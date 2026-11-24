"""Precedência e configuração sem participação no planejamento."""
import hashlib
import logging
import os
from functools import lru_cache
from .cache import SharedStatusCache
from .metro_board import METRO_BOARD_URL, normalize_metro_board
from .domain import LINE_CODES, SERVICE_CODES, LineCondition
from .providers import HttpProvider
from .feeds import CPTM_URL, DiretoDosTrensProvider, normalize_cptm
from .motiva_board import MOTIVA_URL, normalize_motiva_board

logger = logging.getLogger(__name__)


@lru_cache(maxsize=4)
def snapshot_service(url):
    from .xano_snapshot import XanoStatusSnapshotReader
    return SnapshotStatusService(XanoStatusSnapshotReader(url))


class SnapshotStatusService:
    """Uma leitura agregada por servidor; falhas preservam o último retorno."""
    def __init__(self, reader):
        self.reader = reader

    def conditions(self):
        candidates = self.reader.conditions()
        result = []
        for code in (*LINE_CODES, *SERVICE_CODES):
            rows = [r for r in candidates if r.line_code == code and r.validity != "unavailable"]
            result.append(next((r for r in rows if r.validity == "current"),
                               rows[0] if rows else LineCondition(line_code=code)))
        return result


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
            priorities = ("ddt", "cptm", "metro_board", "motiva_board")
            candidates = [sources.get(name, {}).get(code) for name in priorities]
            usable = [row for row in candidates if row and row.validity != "unavailable"]
            row = next((item for item in usable if item.validity == "current"), usable[0] if usable else None)
            if row and any(other.situation != row.situation for other in usable):
                logger.info("Divergência entre fontes de status para %s.", code)
            result.append(row or LineCondition(line_code=code))
        return result

    @classmethod
    def from_environment(cls):
        url = os.getenv("METROFLOW_STATUS_XANO_URL", "").strip()
        if url:
            # O modo remoto não consulta as fontes nem abre o banco local.
            return snapshot_service(url)
        providers = []
        token = os.getenv("METROFLOW_DDT_TOKEN", "")
        if os.getenv("METROFLOW_DDT_ENABLED") == "1" and token.strip():
            fingerprint = hashlib.sha256(("ddt:"+token).encode()).hexdigest()
            providers.append(("ddt",fingerprint,DiretoDosTrensProvider(token)))
        if os.getenv("METROFLOW_CPTM_ENABLED") == "1":
            providers.append(("cptm","cptm-v1",HttpProvider(CPTM_URL,normalize_cptm,respect_cache=True)))
        if os.getenv("METROFLOW_METRO_QUADRO_AUTORIZADO") == "1":
            providers.append(("metro_board", "metro-board-v1", HttpProvider(
                METRO_BOARD_URL, normalize_metro_board, response_format="html", timeout=5.0,
                total_timeout=20.0, local_address="0.0.0.0",read_timeout=15.0)))
        if os.getenv("METROFLOW_MOTIVA_QUADRO_ENABLED") == "1":
            providers.append(("motiva_board", "motiva-board-v1", HttpProvider(
                MOTIVA_URL, normalize_motiva_board, response_format="html", respect_cache=True,
                timeout=5.0, total_timeout=10.0)))
        return cls(SharedStatusCache(os.getenv("METROFLOW_STATUS_CACHE_PATH", ".cache/line-status.sqlite3")),providers)
