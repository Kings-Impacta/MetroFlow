"""Casos de uso de consulta de estacoes, trajeto principal e confirmacao de viagem."""

from collections.abc import Iterable

from MetroFlow.planning.application.ports import PlanningGateway
from MetroFlow.planning.domain.models import (
    RouteResult,
    Station,
    TripConfirmation,
    TripSegment,
)


class InvalidRouteSelection(ValueError):
    """Selecao incompleta ou inconsistente feita pelo usuario."""


class InvalidTripConfirmation(ValueError):
    """Viagem confirmada vazia, longa demais ou com trechos desconexos."""


class PlanningService:
    def __init__(self, gateway: PlanningGateway) -> None:
        self._gateway = gateway

    def list_stations(self, auth_token: str) -> tuple[Station, ...]:
        if not auth_token:
            raise ValueError("A sessao autenticada e obrigatoria.")
        return self._gateway.list_active_stations(auth_token)

    def plan_route(
        self,
        origin_id: int | None,
        destination_id: int | None,
        auth_token: str,
    ) -> RouteResult | None:
        if origin_id is None or destination_id is None:
            raise InvalidRouteSelection("Selecione origem e destino.")
        if origin_id == destination_id:
            raise InvalidRouteSelection(
                "Origem e destino devem ser diferentes."
            )
        if not auth_token:
            raise ValueError("A sessao autenticada e obrigatoria.")

        return self._gateway.find_route(
            origin_id,
            destination_id,
            auth_token,
        )

    def confirm_trip(
        self,
        steps: Iterable[tuple[int, int, int]],
        auth_token: str,
    ) -> None:
        """Registra a viagem; o usuario e identificado pela sessao no Xano."""

        if not auth_token:
            raise ValueError("A sessao autenticada e obrigatoria.")

        try:
            trip = TripConfirmation(
                tuple(TripSegment(*step) for step in steps)
            )
        except ValueError as error:
            raise InvalidTripConfirmation(
                "Viagem confirmada invalida."
            ) from error

        self._gateway.confirm_trip(trip, auth_token)
