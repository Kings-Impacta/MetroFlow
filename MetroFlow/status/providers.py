"""Adaptadores limitados a campos públicos dos contratos externos."""
import json
import time
import httpx
from .domain import LineCondition, line_code, situation, timestamp

ARTESP_URL = "https://ccm.artesp.sp.gov.br/metroferroviario/api/status/"
AGGREGATE_URL = "https://apim-proximotrem-prd-brazilsouth-001.azure-api.net/api/v1/lines"


def text(value: object, limit: int) -> str:
    return value[:limit] if isinstance(value, str) else ""


def unique(rows):
    if len({r.line_code for r in rows}) != len(rows):
        raise ValueError("Linhas duplicadas na fonte")
    return rows


def normalize_artesp(payload, now):
    if not isinstance(payload, dict) or not isinstance(payload.get("empresas"), list):
        raise ValueError("Contrato de status inválido")
    result = []
    for company in payload["empresas"]:
        if not isinstance(company, dict) or not isinstance(company.get("linhas"), list):
            continue
        for row in company["linhas"]:
            if not isinstance(row, dict) or row.get("ativa") is not True:
                continue
            code, status = line_code(row.get("codigo")), row.get("status")
            if not code or not isinstance(status, dict):
                continue
            label = text(status.get("situacao"), 120)
            if not label.strip():
                continue
            result.append(LineCondition(line_code=code, situation=situation(label), label=label,
                description=text(status.get("descricao"),1200), source="ARTESP — API Trilhos",
                source_url="https://ccm.artesp.sp.gov.br/metroferroviario/status-linhas/",
                collected_at=now, updated_at=timestamp(status.get("atualizado_em")),
                verified_at=timestamp(status.get("verificado_em")), validity="current",
                attribution="ARTESP — dados CC BY-NC 4.0"))
    return unique(result)


def normalize_aggregate(payload, now):
    if not isinstance(payload, dict) or not isinstance(payload.get("Data"), list):
        raise ValueError("Contrato de status inválido")
    result = []
    for row in payload["Data"]:
        if not isinstance(row, dict):
            continue
        code, label = line_code(row.get("Code")), text(row.get("StatusLabel"),120)
        if code and label.strip():
            result.append(LineCondition(line_code=code, situation=situation(label), label=label,
                description=text(row.get("Description"),1200), source="Canal oficial agregado",
                source_url="https://www.metro.sp.gov.br/sua-viagem/direto-metro/",
                collected_at=now, validity="current"))
    return unique(result)


class ProviderFailure(Exception):
    def __init__(self, backoff=300):
        super().__init__("Fonte de status indisponível")
        self.backoff = backoff


class HttpProvider:
    def __init__(self, url, normalizer, key="", transport=None):
        self.url, self.normalizer, self.key, self.transport = url, normalizer, key, transport

    def fetch(self, now):
        try:
            headers = {"Authorization":f"Api-Key {self.key}"} if self.key else {}
            started = time.monotonic()
            with httpx.Client(timeout=httpx.Timeout(2.0), follow_redirects=False,
                              transport=self.transport, trust_env=False) as client:
                with client.stream("GET", self.url, headers=headers) as response:
                    if response.status_code == 429:
                        raise ProviderFailure(3600)
                    response.raise_for_status()
                    raw = bytearray()
                    for chunk in response.iter_bytes():
                        raw.extend(chunk)
                        if len(raw)>500000 or time.monotonic()-started>4:
                            raise ProviderFailure()
            return self.normalizer(json.loads(raw), now)
        except ProviderFailure:
            raise
        except (httpx.HTTPError, ValueError, TypeError, KeyError):
            raise ProviderFailure() from None
