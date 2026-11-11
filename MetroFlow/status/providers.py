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
    def __init__(self, backoff=300, *, kind="unavailable"):
        super().__init__("Fonte de status indisponível")
        self.backoff = backoff
        self.kind = kind


class HttpProvider:
    def __init__(self, url, normalizer, key="", transport=None, response_format="json", respect_cache=False,
                 timeout=2.0, total_timeout=4.0, local_address=None, read_timeout=None):
        self.timeout, self.total_timeout = timeout, total_timeout
        self.local_address = local_address
        self.read_timeout = timeout if read_timeout is None else read_timeout
        self.respect_cache = respect_cache
        if response_format not in {"json", "html"}:
            raise ValueError("Formato de resposta inválido")
        self.response_format = response_format
        self.url, self.normalizer, self.key, self.transport = url, normalizer, key, transport

    def fetch(self, now):
        try:
            headers = {"Authorization":f"Api-Key {self.key}"} if self.key else {}
            started = time.monotonic()
            transport = self.transport
            if transport is None and self.local_address is not None:
                transport = httpx.HTTPTransport(local_address=self.local_address, trust_env=False, verify=True)
            with httpx.Client(timeout=httpx.Timeout(self.timeout,read=self.read_timeout), follow_redirects=False,
                              transport=transport, trust_env=False) as client:
                with client.stream("GET", self.url, headers=headers) as response:
                    response_headers = dict(response.headers)
                    if response.status_code == 429:
                        from .feeds import retry_after
                        raise ProviderFailure(retry_after(response_headers, now))
                    response.raise_for_status()
                    raw = bytearray()
                    for chunk in response.iter_bytes():
                        raw.extend(chunk)
                        if len(raw)>500000 or time.monotonic()-started>self.total_timeout:
                            raise ProviderFailure(kind="response_limit")
            payload = raw.decode("utf-8") if self.response_format == "html" else json.loads(raw)
            rows = self.normalizer(payload, now)
            if self.respect_cache:
                from .feeds import cache_policy
                return cache_policy(rows, response_headers)
            return rows
        except ProviderFailure:
            raise
        except httpx.TimeoutException as error:
            kind = "connect_timeout" if isinstance(error,httpx.ConnectTimeout) else (
                "read_timeout" if isinstance(error,httpx.ReadTimeout) else "timeout")
            raise ProviderFailure(kind=kind) from None
        except httpx.HTTPStatusError:
            raise ProviderFailure(kind="http_status") from None
        except (httpx.HTTPError, ValueError, TypeError, KeyError):
            raise ProviderFailure(kind="invalid_response") from None
