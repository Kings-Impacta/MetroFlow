"""Precedência e configuração sem participação no planejamento."""
import hashlib
import logging
import os
from .cache import SharedStatusCache
from .domain import DELEGATED, LINE_CODES, SERVICE_CODES, LineCondition
from .providers import ARTESP_URL, AGGREGATE_URL, HttpProvider, normalize_artesp, normalize_aggregate

logger = logging.getLogger(__name__)


class StatusService:
    def __init__(self, cache, providers):
        self.cache, self.providers = cache, providers

    def conditions(self):
        sources = {}
        for name, key, provider in self.providers:
            try:
                sources[name] = {r.line_code:r for r in self.cache.read(key,provider)}
            except Exception:
                logger.warning("Fonte de status indisponível.")
                sources[name] = {}
        result = []
        for code in (*LINE_CODES, *SERVICE_CODES):
            primary = "artesp" if code in DELEGATED else "aggregate"
            row = sources.get(primary,{}).get(code)
            other = sources.get("aggregate" if primary=="artesp" else "artesp",{}).get(code)
            if row and other and row.situation!=other.situation:
                logger.info("Divergência entre fontes de status para %s.", code)
            result.append(row or LineCondition(line_code=code))
        return result

    @classmethod
    def from_environment(cls):
        providers = []
        key = os.getenv("METROFLOW_ARTESP_API_KEY", "")
        if os.getenv("METROFLOW_ARTESP_ENABLED")=="1" and key:
            fingerprint = hashlib.sha256(("artesp:"+key).encode()).hexdigest()
            providers.append(("artesp",fingerprint,HttpProvider(ARTESP_URL,normalize_artesp,key)))
        if os.getenv("METROFLOW_STATUS_COMPLEMENTAR_AUTORIZADO")=="1":
            providers.append(("aggregate","aggregate-v1",HttpProvider(AGGREGATE_URL,normalize_aggregate)))
        return cls(SharedStatusCache(os.getenv("METROFLOW_STATUS_CACHE_PATH", ".cache/line-status.sqlite3")),providers)
