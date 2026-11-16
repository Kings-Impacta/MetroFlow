"""Casos de uso do painel administrativo."""

from __future__ import annotations

import unicodedata

from MetroFlow.admin.application.ports import AdminGateway
from MetroFlow.admin.domain.models import AdminIndicators, AdminStation, StationStatus


class InvalidStationChange(ValueError):
    """Alteração de situação com dados inválidos."""


def alphabetical_key(name: str) -> str:
    """Ordena por nome sem distinguir maiúsculas e acentos."""

    decomposed = unicodedata.normalize("NFKD", name)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).casefold()


class AdminService:
    def __init__(self, gateway: AdminGateway) -> None:
        self._gateway = gateway

    def indicators(self, auth_token: str) -> AdminIndicators:
        return self._gateway.indicators(auth_token)

    def stations(self, auth_token: str) -> tuple[AdminStation, ...]:
        items = self._gateway.stations(auth_token)
        return tuple(sorted(items, key=lambda station: (alphabetical_key(station.name), station.id)))

    def change_station_status(
        self,
        station_id: int,
        active: bool,
        auth_token: str,
    ) -> StationStatus:
        if isinstance(station_id, bool) or not isinstance(station_id, int) or station_id <= 0:
            raise InvalidStationChange("Estação inválida.")
        if not isinstance(active, bool):
            raise InvalidStationChange("Situação inválida.")

        status = self._gateway.set_station_status(station_id, active, auth_token)
        if status.id != station_id:
            raise ValueError("Resposta não corresponde à estação alterada.")
        return status
