"""Fontes escolhidas: Direto dos Trens e complemento oficial CPTM."""
from contextlib import closing
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import http.client
import json
import re
import time
from urllib.parse import quote
from .domain import LineCondition, line_code, situation, timestamp
from .providers import ProviderFailure, text, unique

DDT_HOST = "www.diretodostrens.com.br"
DDT_PAGE = "https://www.diretodostrens.com.br/"
CPTM_URL = "https://api.cptm.sp.gov.br/AppCPTM/v1/Linhas/ObterStatus"
CPTM_PAGE = "https://www.cptm.sp.gov.br/cptm"
CPTM_CODES = frozenset(("L10", "L11", "L12", "L13"))


class FetchedConditions(list):
    """Metadados de cache privados, sem alterar o contrato público de condições."""
    def __init__(self, rows, *, fresh_for=600, refresh_after=300, cacheable=True):
        super().__init__(rows)
        self.fresh_for = fresh_for
        self.refresh_after = refresh_after
        self.cacheable = cacheable


def cache_policy(rows, headers):
    control = headers.get("cache-control", "").lower()
    parts = {value.strip().split("=", 1)[0] for value in control.split(",")}
    forbidden = bool(parts & {"no-store", "no-cache", "private"})
    match = re.search(r'(?:^|,)\s*s-maxage\s*=\s*"?(\d+)', control)
    if match is None:
        match = re.search(r'(?:^|,)\s*max-age\s*=\s*"?(\d+)', control)
    try:
        age = max(0, int(headers.get("age", "0")))
    except (ValueError, TypeError):
        age = 0
    lifetime = max(0, int(match[1])-age) if match else 600
    return FetchedConditions(rows, fresh_for=lifetime,
        # max-age vencido impede apresentar como atual, mas não proíbe guardar
        # a última observação. no-store/no-cache/private continuam respeitados.
        refresh_after=max(300, lifetime if match else 300), cacheable=not forbidden)


def retry_after(headers, now):
    value = headers.get("retry-after", "")
    try:
        return max(3600, int(value))
    except (ValueError, TypeError):
        try:
            date = parsedate_to_datetime(value)
            return max(3600, int(date.timestamp()-now)) if date.tzinfo is not None else 3600
        except (ValueError, TypeError, OverflowError):
            return 3600


def normalize_ddt(payload, now):
    if not isinstance(payload, list):
        raise ValueError("Contrato Direto dos Trens inválido")
    rows = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("Registro Direto dos Trens inválido")
        code = line_code(item.get("codigo"))
        if not code:
            continue
        label = text(item.get("situacao"), 120).strip()
        if not label or not isinstance(item.get("criado"), str) or type(item.get("id")) is not int or item["id"]<0:
            raise ValueError("Registro Direto dos Trens incompleto")
        changed = timestamp(item.get("modificado")) or timestamp(item.get("criado"))
        if changed is not None and changed>now+60:
            raise ValueError("Data futura Direto dos Trens")
        rows.append(LineCondition(line_code=code, situation=situation(label), label=label,
            description=text(item.get("descricao"),1200), source="Direto dos Trens — agregador independente",
            source_url=DDT_PAGE, collected_at=now, updated_at=changed, verified_at=None,
            validity="current", attribution="Fonte: Direto dos Trens; informações coletadas de canais oficiais"))
    if not rows:
        raise ValueError("Nenhuma linha reconhecida Direto dos Trens")
    return unique(rows)


def normalize_cptm(payload, now):
    if not isinstance(payload, list):
        raise ValueError("Contrato CPTM inválido")
    rows = []
    for item in payload:
        if not isinstance(item, dict) or item.get("tipo")!="C":
            continue
        code = line_code(item.get("linhaId"))
        if code not in CPTM_CODES:
            continue
        label = text(item.get("status"),120).strip()
        if not label:
            raise ValueError("Situação CPTM ausente")
        generated = timestamp(item.get("dataGeracao"))
        if generated is not None and generated>now+60:
            raise ValueError("Data futura CPTM")
        rows.append(LineCondition(line_code=code, situation=situation(label), label=label,
            description=text(item.get("descricao"),1200), source="CPTM — situação das linhas",
            source_url=CPTM_PAGE, collected_at=now, updated_at=None, verified_at=generated,
            validity="current", attribution="Fonte: site oficial CPTM"))
    if not rows:
        raise ValueError("Nenhuma linha reconhecida CPTM")
    return unique(rows)


class DiretoDosTrensProvider:
    """Query de autenticação restrita ao HTTPS interno, sem logger de URLs."""
    def __init__(self, token, connection_factory=http.client.HTTPSConnection):
        if not token or not token.strip():
            raise ValueError("Token obrigatório")
        self._token = token
        self._connection_factory = connection_factory

    def fetch(self, now):
        try:
            started = time.monotonic()
            with closing(self._connection_factory(DDT_HOST, timeout=2.0)) as connection:
                # O fornecedor exige query; não usar httpx, logs de request ou redirecionamentos.
                connection.request("GET", "/api/status?token="+quote(self._token,safe=""),
                    headers={"Accept":"application/json"})
                with closing(connection.getresponse()) as response:
                    headers = {k.lower():v for k,v in response.getheaders()}
                    if response.status==429:
                        raise ProviderFailure(retry_after(headers,now))
                    if response.status!=200:
                        raise ProviderFailure()
                    raw = bytearray()
                    while True:
                        chunk = response.read1(8192)
                        if not chunk:
                            break
                        raw.extend(chunk)
                        if len(raw)>500000 or time.monotonic()-started>4:
                            raise ProviderFailure()
            return cache_policy(normalize_ddt(json.loads(raw),now),headers)
        except ProviderFailure:
            raise
        except (OSError, http.client.HTTPException, ValueError, TypeError, KeyError):
            raise ProviderFailure() from None
