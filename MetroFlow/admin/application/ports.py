"""Contrato entre os casos de uso administrativos e o Xano."""

from __future__ import annotations

from typing import Protocol

from MetroFlow.admin.domain.models import AdminIndicators, AdminStation, StationStatus


class AdminGateway(Protocol):
    def indicators(self, auth_token: str) -> AdminIndicators: ...

    def stations(self, auth_token: str) -> tuple[AdminStation, ...]: ...

    def set_station_status(
        self,
        station_id: int,
        active: bool,
        auth_token: str,
    ) -> StationStatus: ...
