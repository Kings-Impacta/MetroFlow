"""Leitor de status agregado, independente de busca e registro.

Lê somente o snapshot agregado. Nenhum método grava ou coleta fontes externas.
Uma única instância deve ser compartilhada pelo servidor, não por passageiro.
"""
from threading import Lock
from email.utils import parsedate_to_datetime
import math
import time
from urllib.parse import urlsplit
import httpx
from .domain import LineCondition

CODES = {
    "cptm": {"L10", "L11", "L12", "L13"},
    "metro": {"L1", "L2", "L3", "L4", "L5", "L15", "L17"},
    "motiva": {"L8", "L9"},
    "ddt": {f"L{n}" for n in (1,2,3,4,5,6,7,8,9,10,11,12,13,15,17)},
}


class XanoStatusSnapshotReader:
    def __init__(self, base_url, *, transport=None, clock=time.time):
        parts = urlsplit(base_url)
        if (parts.scheme != "https" or not parts.hostname or parts.username or parts.password
                or parts.query or parts.fragment):
            raise ValueError("O snapshot exige uma URL HTTPS sem credenciais.")
        self.client = httpx.Client(base_url=base_url.rstrip("/")+"/", timeout=2.0,
                                   transport=transport, follow_redirects=False)
        self.clock = clock
        self.lock = Lock()
        self.rows = []
        self.next_read = 0.0
        self.failed = False

    def close(self):
        self.client.close()

    def conditions(self):
        now = self.clock()
        if self.lock.acquire(blocking=False):
            try:
                if now >= self.next_read:
                    self.next_read = now+60
                    try:
                        with self.client.stream("GET", "snapshot") as response:
                            response.raise_for_status()
                            data = bytearray()
                            for part in response.iter_bytes():
                                data.extend(part)
                                if len(data) > 131072:
                                    raise ValueError("Snapshot acima do limite.")
                            import json
                            body = json.loads(data)
                        if (body.get("version") != 1 or not isinstance(body.get("sources"), list)
                                or len(body["sources"]) > len(CODES)):
                            raise ValueError("Contrato inválido.")
                        sources, rows = set(), []
                        for source in sorted(body["sources"], key=lambda s: ["ddt", "cptm", "metro", "motiva"].index(s["source"]) if s.get("source") in CODES else 99):
                            code = source["source"]
                            if (code not in CODES or code in sources or not isinstance(source.get("conditions"), list)
                                    or len(source["conditions"]) > 17):
                                raise ValueError("Fonte inválida.")
                            sources.add(code)
                            seen = set()
                            for raw in source["conditions"]:
                                item = LineCondition.model_validate(raw)
                                if (item.line_code not in CODES[code] or item.line_code in seen
                                        or item.collected_at is None or any(
                                            not math.isfinite(t) or t <= 0 or t > now+60
                                            for t in (item.collected_at, item.verified_at, item.updated_at)
                                            if t is not None)
                                        or (item.verified_at is not None and item.verified_at > now+60)):
                                    raise ValueError("Condição inválida.")
                                seen.add(item.line_code)
                                rows.append(item)
                        self.rows, self.failed = rows, False
                    except (httpx.HTTPError, ValueError, TypeError, KeyError, AttributeError) as error:
                        self.failed = True
                        backoff = 300
                        if isinstance(error, httpx.HTTPStatusError):
                            if error.response.status_code == 429:
                                backoff = 3600
                            retry = error.response.headers.get("Retry-After", "")
                            try:
                                seconds = float(retry) if retry.isascii() and retry.isdecimal() else parsedate_to_datetime(retry).timestamp()-now
                                if math.isfinite(seconds):
                                    backoff = max(backoff, seconds)
                            except (ValueError, TypeError, OverflowError):
                                pass
                        self.next_read = now+backoff
                        # Não renovar datas, repetir GET ou propagar falha ao planejador.
            finally:
                self.lock.release()
        return [row.aged(now, self.failed, keep_last=True) for row in self.rows]
