"""Rotas do painel administrativo, com token lido somente do cookie HttpOnly.

A autorização é verificada pelo Xano em cada endpoint administrativo; este
módulo não consulta `auth/me` antes, para gastar uma única requisição.
"""

from typing import Annotated, NoReturn

from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response

from MetroFlow.admin.application.services import AdminService, InvalidStationChange
from MetroFlow.admin.infrastructure.xano_client import (
    AdminError,
    AdminForbidden,
    AdminNotFound,
    AdminUnauthorized,
    AdminUnavailable,
    XanoAdminClient,
)
from MetroFlow.admin.presentation.view_models import (
    IndicatorsView,
    StationStatusRequest,
    StationStatusView,
    StationView,
)
from MetroFlow.auth.infrastructure.session_cookie import get_session_token


admin_api = APIRouter(prefix="/api/admin", tags=["admin"])
NO_STORE = {"Cache-Control": "no-store"}


def _fail(status_code: int, detail: str) -> HTTPException:
    # Respostas de erro também não podem ser guardadas em cache.
    return HTTPException(status_code, detail, headers=NO_STORE)


def admin_session_token(request: Request, response: Response) -> str:
    response.headers.update(NO_STORE)
    token = get_session_token(request)
    if not token:
        raise _fail(401, "Entre na sua conta para acessar o painel.")
    return token


Token = Annotated[str, Depends(admin_session_token)]


def public_error(error: Exception) -> NoReturn:
    """Converte falhas em mensagens genéricas, sem conteúdo do Xano."""

    if isinstance(error, AdminUnauthorized):
        raise _fail(401, "Sua sessão expirou. Entre novamente.") from error
    if isinstance(error, AdminForbidden):
        raise _fail(403, "Acesso restrito a administradores.") from error
    if isinstance(error, AdminNotFound):
        raise _fail(404, "Estação não encontrada. Atualize a lista e tente novamente.") from error
    if isinstance(error, InvalidStationChange) or (
        isinstance(error, AdminError) and error.status_code in {400, 422}
    ):
        raise _fail(400, "Verifique a estação selecionada e tente novamente.") from error
    if isinstance(error, AdminUnavailable):
        raise _fail(503, "O serviço administrativo está indisponível. Tente novamente.") from error
    raise _fail(502, "Não foi possível obter um resultado válido. Tente novamente.") from error


@admin_api.get("/indicators", response_model=IndicatorsView)
def indicators(token: Token) -> IndicatorsView:
    try:
        with XanoAdminClient.from_environment() as client:
            result = AdminService(client).indicators(token)
        return IndicatorsView.from_indicators(result)
    except (AdminError, ValueError) as error:
        public_error(error)


@admin_api.get("/stations", response_model=list[StationView])
def stations(token: Token) -> list[StationView]:
    try:
        with XanoAdminClient.from_environment() as client:
            items = AdminService(client).stations(token)
        return [StationView.from_station(item) for item in items]
    except (AdminError, ValueError) as error:
        public_error(error)


@admin_api.post("/stations/{station_id}/status", response_model=StationStatusView)
def change_station_status(
    change: StationStatusRequest,
    token: Token,
    station_id: Annotated[int, Path(gt=0, le=2_147_483_647)],
) -> StationStatusView:
    try:
        with XanoAdminClient.from_environment() as client:
            status = AdminService(client).change_station_status(station_id, change.active, token)
        return StationStatusView.from_status(status)
    except (AdminError, ValueError) as error:
        public_error(error)
