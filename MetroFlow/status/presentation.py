"""Informação operacional carregada separadamente do trajeto e de seu registro."""
from datetime import datetime, timedelta, timezone
import reflex as rx
from pydantic import TypeAdapter, ValidationError
from MetroFlow.planning.presentation.state import PlanningState, request_script
from .domain import LineCondition

LINE_NAMES = {f"L{number}":f"{number} · {name}" for number,name in (
    (1,"Azul"),(2,"Verde"),(3,"Vermelha"),(4,"Amarela"),(5,"Lilás"),(6,"Laranja"),
    (7,"Rubi"),(8,"Diamante"),(9,"Esmeralda"),(10,"Turquesa"),(11,"Coral"),
    (12,"Safira"),(13,"Jade"),(15,"Prata"),(17,"Ouro"))}
LINE_NAMES.update({"EXP-AER":"Expresso Aeroporto","EXP-L10":"Expresso Linha 10"})
STATUS_COLORS = {"normal":"#15803d","restricted":"#a16207","interrupted":"#dc2626",
                 "closed":"#64748b","unknown":"#64748b"}
EMPTY_INDICATOR = {"label":"Status indisponível","color":"#64748b",
                   "details":"Aguardando uma informação válida da fonte."}


class LineStatusState(rx.State):
    rows: list[dict[str,str]] = []
    message: str = "As condições operacionais ainda não foram consultadas."
    _request_id: int = 0
    _polling: bool = False

    @rx.var
    def indicators(self) -> dict[str,dict[str,str]]:
        result = {}
        for row in self.rows:
            unavailable = row["validity"] == "Indisponível"
            result[row["code"]] = dict(
                label="Status indisponível" if unavailable else row["label"],
                color=STATUS_COLORS.get(row.get("situation","unknown"),"#64748b") if not unavailable else "#64748b",
                details=" · ".join(value for value in (row.get("source",""),row.get("collected",""),
                    row.get("description","")) if value))
        return result

    @rx.event
    def start(self):
        self._polling = True
        return self.refresh()

    @rx.event
    def stop(self):
        self._polling = False
        self._request_id += 1

    def _schedule(self):
        if self._polling:
            return rx.call_script(
                f"new Promise(resolve => setTimeout(() => resolve({self._request_id}), 60000))",
                callback=LineStatusState.repeat,
            )

    @rx.event
    def repeat(self, request_id: int):
        if self._polling and request_id == self._request_id:
            return self.refresh()

    @rx.event
    def refresh(self):
        self._request_id += 1
        self.message = "Atualizando condições; mantendo o último retorno…" if self.rows else "Consultando condições operacionais…"
        return rx.call_script(request_script("/api/planning/line-status",self._request_id),callback=LineStatusState.receive)

    @rx.event
    def receive(self, result: dict):
        if result.get("request_id") != self._request_id:
            return
        if result.get("status") != 200:
            self._retain_previous()
            return self._schedule()
        try:
            conditions = TypeAdapter(list[LineCondition]).validate_python(result.get("data"))
        except ValidationError:
            self._retain_previous()
            return self._schedule()
        if not conditions:
            self._retain_previous()
            return self._schedule()
        def date(value):
            return datetime.fromtimestamp(value,timezone(timedelta(hours=-3))).strftime("%d/%m %H:%M") if value is not None else "Não informada"
        previous = {row["code"]:row for row in self.rows}
        incoming = [dict(code=r.line_code,label=r.label,situation=r.situation,description=r.description,
            source=r.source,source_url=r.source_url,attribution=r.attribution,
            validity={"current":"Atual na consulta","stale":"Desatualizado","unavailable":"Indisponível"}[r.validity],
            collected="Coleta: "+date(r.collected_at),updated="Última mudança: "+date(r.updated_at),
            verified="Verificação da fonte: "+date(r.verified_at)) for r in conditions]
        merged = {code:(dict(row,validity="Desatualizado") if row.get("source") else row)
                  for code,row in previous.items()}
        for row in incoming:
            if row["validity"]=="Indisponível" and previous.get(row["code"],{}).get("source"):
                continue
            merged[row["code"]] = row
        self.rows = list(merged.values())
        self.message = "Informação complementar: não altera o trajeto nem representa lotação dos trens. A tela consulta novamente a cada minuto. Em falhas, mantém o último retorno como desatualizado; confira o horário de coleta."
        return self._schedule()

    def _retain_previous(self):
        self.rows = [dict(row,validity="Desatualizado") if row.get("source") else row for row in self.rows]
        self.message = ("Não foi possível atualizar. Mantendo o último retorno disponível. "
                        "Você pode continuar buscando trajetos." if self.rows else
                        "Status indisponível. Você pode continuar buscando trajetos.")


def condition_card(row):
    return rx.card(rx.vstack(
        rx.hstack(rx.text(row["code"],weight="bold"),rx.badge(row["validity"])),
        rx.text(row["label"]),rx.text(row["description"]),
        rx.text(row["collected"],size="1"),rx.text(row["updated"],size="1"),rx.text(row["verified"],size="1"),
        rx.cond(row["source"]!="",rx.link(row["source"],href=row["source_url"],is_external=True)),
        rx.text(row["attribution"],size="1"),align="start"),width="100%")


def line_status_indicator(code):
    """Mesmo dado no resumo e no embarque; não dispara outra consulta."""
    row = LineStatusState.indicators.get(code,EMPTY_INDICATOR).to(dict[str,str])
    name = rx.Var.create(LINE_NAMES).get(code,code)
    return rx.tooltip(rx.hstack(
        rx.box(width="0.55rem",height="0.55rem",min_width="0.55rem",
               border_radius="50%",background=row["color"],aria_hidden=True),
        rx.text(name,size="2",weight="bold",color="#334155"),
        rx.text(row["label"],size="2",color=row["color"]),
        spacing="2",align="center",wrap="wrap",tab_index=0,
        aria_label=name+": "+row["label"],
    ),content=row["details"])


def route_status_summary():
    return rx.vstack(
        rx.text("LINHAS DO TRAJETO",size="1",weight="bold",color="#52627a"),
        rx.foreach(PlanningState.route_line_codes,line_status_indicator),
        spacing="2",align="start",justify_self="end",width="auto",
        on_mount=LineStatusState.start,on_unmount=LineStatusState.stop,
    )


def status_panel(for_route: bool = False):
    def card(row):
        if for_route:
            return rx.cond(PlanningState.route_line_codes.contains(row["code"]),condition_card(row))
        return condition_card(row)
    return rx.vstack(rx.heading("Condições operacionais das linhas",size="5"),
        rx.text(LineStatusState.message),
        rx.button("Atualizar condições",on_click=LineStatusState.refresh),
        rx.foreach(LineStatusState.rows,card),align="start",width="100%",on_mount=LineStatusState.start,on_unmount=LineStatusState.stop)
