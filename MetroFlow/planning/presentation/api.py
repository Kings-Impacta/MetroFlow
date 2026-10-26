"""Consultas do planejador com token lido exclusivamente do cookie HttpOnly."""

import logging
from typing import Annotated, NoReturn

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from MetroFlow.auth.infrastructure.session_cookie import get_session_token
from MetroFlow.auth.infrastructure.xano_client import (
    XanoAuthClient, XanoAuthError, XanoAuthRejected,
)
from MetroFlow.planning.application.guidance import match_guidance
from MetroFlow.planning.application.services import (
    InvalidRouteSelection, InvalidTripConfirmation, PlanningService,
)
from MetroFlow.planning.domain.guidance import StationGuidance
from MetroFlow.planning.domain.models import RouteResult
from MetroFlow.planning.infrastructure.guidance_csv import cached_guidance, guidance_enabled
from MetroFlow.planning.infrastructure.xano_client import (
    PlanningError, PlanningUnauthorized, PlanningUnavailable, XanoPlanningClient,
)
from MetroFlow.planning.presentation.view_models import (
    RouteRequest, RouteView, StationChoice, TripConfirmationRequest,
)


planning_api = APIRouter(prefix="/api/planning", tags=["planning"])
logger = logging.getLogger(__name__)


def session_token(request: Request, response: Response) -> str:
    response.headers["Cache-Control"] = "no-store"
    token = get_session_token(request)
    if not token:
        raise HTTPException(401, "Entre na sua conta para planejar um trajeto.")
    return token


SessionToken = Annotated[str, Depends(session_token)]


def authenticated_token(token: SessionToken) -> str:
    try:
        with XanoAuthClient.from_environment() as client:
            client.me(token)
    except XanoAuthRejected as error:
        raise HTTPException(401, "Sua sessão expirou. Entre novamente.") from error
    except XanoAuthError as error:
        raise HTTPException(503, "Não foi possível verificar sua sessão. Tente novamente.") from error
    return token


Token = Annotated[str, Depends(authenticated_token)]


def public_error(error: Exception) -> NoReturn:
    if isinstance(error, PlanningUnauthorized):
        raise HTTPException(401, "Sua sessão expirou. Entre novamente.") from error
    if isinstance(error, InvalidRouteSelection):
        raise HTTPException(400, "Selecione estações diferentes para origem e destino.") from error
    if isinstance(error, PlanningUnavailable):
        raise HTTPException(503, "O serviço de trajetos está indisponível. Tente novamente.") from error
    if isinstance(error, PlanningError) and error.status_code in {400, 422}:
        raise HTTPException(400, "Verifique as estações selecionadas e tente novamente.") from error
    raise HTTPException(502, "Não foi possível obter um resultado válido. Tente novamente.") from error


def trip_error(error: Exception) -> NoReturn:
    if isinstance(error, InvalidTripConfirmation) or (
        isinstance(error, PlanningError) and error.status_code in {400, 404, 422}
    ):
        raise HTTPException(400, "Não foi possível confirmar esta viagem. Busque o trajeto novamente.") from error
    public_error(error)


def route_guidance(result: RouteResult) -> dict[int, StationGuidance]:
    """Orientacoes opcionais; qualquer falha devolve o trajeto sem elas."""
    if not guidance_enabled():
        return {}
    try:
        return match_guidance(result, cached_guidance())
    except Exception:
        logger.warning("Orientacoes ignoradas por falha na associacao.")
        return {}


@planning_api.get("/stations", response_model=list[StationChoice])
def stations(token: Token) -> list[StationChoice]:
    try:
        with XanoPlanningClient.from_environment() as client:
            items = PlanningService(client).list_stations(token)
        return [StationChoice.from_station(item)
                for item in sorted(items, key=lambda station: station.name.casefold())]
    except (PlanningError, ValueError) as error:
        public_error(error)


@planning_api.post("/route", response_model=RouteView)
def route(selection: RouteRequest, token: Token) -> RouteView:
    try:
        with XanoPlanningClient.from_environment() as client:
            result = PlanningService(client).plan_route(
                selection.origin_id, selection.destination_id, token,
            )
        if result is None:
            # O contrato atual do Xano tambem usa 404 para estacao inexistente.
            raise HTTPException(404, "Não foi encontrado trajeto para essas estações. Atualize a lista e tente novamente.")
        if (result.origin.id, result.destination.id) != (selection.origin_id, selection.destination_id):
            raise ValueError("Resposta nao corresponde a selecao.")
        return RouteView.from_route(result, route_guidance(result))
    except (PlanningError, ValueError) as error:
        public_error(error)


@planning_api.post("/trip", status_code=204, response_class=Response)
def trip(confirmation: TripConfirmationRequest, token: Token) -> None:
    # A resposta nao tem corpo: nenhum registro de viagem volta ao navegador.
    try:
        with XanoPlanningClient.from_environment() as client:
            PlanningService(client).confirm_trip(confirmation.steps(), token)
    except (PlanningError, ValueError) as error:
        trip_error(error)
