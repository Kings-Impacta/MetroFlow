"""Consulta protegida, sem chamadas de status na busca ou confirmação."""
from fastapi import APIRouter
from MetroFlow.planning.presentation.api import Token
from .domain import LINE_CODES, SERVICE_CODES, LineCondition
from .service import StatusService

status_api = APIRouter(prefix="/api/planning", tags=["status"])


@status_api.get("/line-status", response_model=list[LineCondition])
def line_status(token: Token):
    try:
        return StatusService.from_environment().conditions()
    except Exception:
        return [LineCondition(line_code=code) for code in (*LINE_CODES, *SERVICE_CODES)]
