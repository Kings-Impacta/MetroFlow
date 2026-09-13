"""Politica de cookie da sessao de autenticacao."""

from __future__ import annotations

import os

from starlette.requests import Request
from starlette.responses import Response


SESSION_COOKIE_NAME = "metroflow_session"
SESSION_COOKIE_MAX_AGE = 24 * 60 * 60
APPLICATION_ENV_VAR = "METROFLOW_ENV"
PRODUCTION_ENVIRONMENTS = frozenset({"prod", "production"})


def is_production_environment(environment: str | None = None) -> bool:
    """Informa se cookies devem exigir HTTPS."""

    selected_environment = (
        environment
        if environment is not None
        else os.getenv(APPLICATION_ENV_VAR, "development")
    )
    return selected_environment.strip().lower() in PRODUCTION_ENVIRONMENTS


def set_session_cookie(
    response: Response,
    auth_token: str,
    *,
    secure: bool | None = None,
) -> None:
    """Armazena o token em cookie inacessivel a JavaScript."""

    if not auth_token:
        raise ValueError("O token de autenticacao e obrigatorio.")

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=auth_token,
        max_age=SESSION_COOKIE_MAX_AGE,
        path="/",
        secure=is_production_environment() if secure is None else secure,
        httponly=True,
        samesite="lax",
    )


def clear_session_cookie(
    response: Response,
    *,
    secure: bool | None = None,
) -> None:
    """Remove o cookie usando os mesmos atributos de seguranca."""

    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        secure=is_production_environment() if secure is None else secure,
        httponly=True,
        samesite="lax",
    )


def get_session_token(request: Request) -> str | None:
    """Le o token apenas no backend."""

    auth_token = request.cookies.get(SESSION_COOKIE_NAME)
    return auth_token or None
