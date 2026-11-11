"""Leitura experimental do quadro público; ativação depende de condições de uso."""
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
import re
from .domain import LineCondition, line_code, situation
from .providers import unique

METRO_BOARD_URL = "https://www.metro.sp.gov.br/wp-content/themes/metrosp/direto-metro.php?embed=1"
METRO_BOARD_PAGE = "https://www.metro.sp.gov.br/sua-viagem/direto-metro/"
BOARD_CODES = frozenset(("L1", "L2", "L3", "L4", "L5", "L15", "L17"))
BRASILIA = timezone(timedelta(hours=-3))


class FieldsParser(HTMLParser):
    """Extrai texto de classes conhecidas sem executar ou renderizar marcação."""
    def __init__(self, names):
        super().__init__(convert_charrefs=True)
        self.names = set(names)
        self.fields = {}
        self.stack = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set(attrs.get("class", "").split())
        field = next(iter(classes & self.names), None)
        ignored = tag in {"script", "style"} or bool(self.stack and self.stack[-1][2])
        if tag not in {"br", "img", "hr", "input", "meta", "link", "wbr", "source", "area", "embed", "param", "track", "col", "base"}:
            self.stack.append((tag, field, ignored))
        if field and not ignored:
            if field in self.fields:
                raise ValueError("Campo duplicado no quadro")
            self.fields[field] = []

    def handle_startendtag(self, tag, attrs):
        # Elementos vazios não criam nível de captura.
        return

    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.stack and self.stack[-1][2]:
            return
        for _, field, ignored in self.stack:
            if field and not ignored:
                self.fields[field].append(data)

    def value(self, field, limit):
        return " ".join(" ".join(self.fields.get(field, [])).split())[:limit]


class BoardParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.parts = None
        self.tooltip = None
        self.li_depth = 0
        self.ignored = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        classes = set(attrs_dict.get("class", "").split())
        if tag in {"script", "style"}:
            self.ignored += 1
        if self.ignored:
            return
        if tag == "li":
            if self.parts is not None:
                self.li_depth += 1
            elif "linha" in classes:
                self.parts, self.li_depth = [], 1
        if self.parts is not None:
            self.parts.append(self.get_starttag_text())
            if "linha-info" in classes:
                if self.tooltip is not None:
                    raise ValueError("Tooltip duplicado")
                self.tooltip = attrs_dict.get("data-bs-title") or ""

    def handle_startendtag(self, tag, attrs):
        if self.parts is not None and not self.ignored:
            self.parts.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.ignored:
            self.ignored -= 1
            return
        if self.ignored or self.parts is None:
            return
        self.parts.append(f"</{tag}>")
        if tag == "li":
            self.li_depth -= 1
            if self.li_depth == 0:
                self.rows.append(("".join(self.parts), self.tooltip or ""))
                self.parts, self.tooltip = None, None

    def handle_data(self, data):
        if self.parts is not None and not self.ignored:
            # Reescapar texto evita que um &lt;script&gt; textual vire estrutura.
            from html import escape
            self.parts.append(escape(data))


def changed_at(value):
    if not value:
        return None
    match = re.search(r"atualizado em\s+(\d{2}/\d{2}/\d{4} \d{2}:\d{2}(?::\d{2})?)", value, re.I)
    if not match:
        raise ValueError("Data do quadro incompatível")
    date = match[1]
    pattern = "%d/%m/%Y %H:%M:%S" if len(date) == 19 else "%d/%m/%Y %H:%M"
    return datetime.strptime(date, pattern).replace(tzinfo=BRASILIA).timestamp()


def normalize_metro_board(payload, now):
    if not isinstance(payload, str) or len(payload) > 500000:
        raise ValueError("HTML do quadro inválido")
    board = BoardParser()
    board.feed(payload)
    board.close()
    if not board.rows or board.parts is not None or board.ignored:
        raise ValueError("Estrutura do quadro incompatível")
    result = []
    for markup, tooltip in board.rows:
        fields = FieldsParser(("linha-numero", "linha-situacao"))
        fields.feed(markup)
        code = line_code(fields.value("linha-numero", 20))
        if code not in BOARD_CODES:
            continue
        label = fields.value("linha-situacao", 120)
        if not label:
            raise ValueError("Situação ausente no quadro")
        detail = FieldsParser(("description", "date"))
        detail.feed(tooltip)
        changed = changed_at(detail.value("date", 100))
        if changed is not None and changed > now + 60:
            raise ValueError("Data futura no quadro")
        result.append(LineCondition(line_code=code, situation=situation(label), label=label,
            description=detail.value("description", 1200), source="Metrô — quadro Direto do Metrô",
            source_url=METRO_BOARD_PAGE, collected_at=now, updated_at=changed,
            verified_at=None, validity="current", attribution="Fonte: Direto do Metrô — Metrô de São Paulo"))
    if not result:
        raise ValueError("Nenhuma linha reconhecida no quadro")
    return unique(result)
