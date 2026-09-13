"""Portas exigidas pelos casos de uso de planejamento."""

from typing import Protocol

from MetroFlow.planning.domain.models import RouteResult, Station


class PlanningGateway(Protocol):
    def list_active_stations(self, auth_token: str) -> tuple[Station, ...]: ...

    def find_route(
        self,
        origin_id: int,
        destination_id: int,
        auth_token: str,
    ) -> RouteResult | None: ...
