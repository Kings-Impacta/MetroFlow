"""Rotas backend de autenticacao usadas pela interface Reflex."""

from fastapi import FastAPI, HTTPException, Request, Response, status
from pydantic import BaseModel, ConfigDict

from MetroFlow.auth.infrastructure.xano_client import (
    AuthSession,
    AuthenticatedUser,
    XanoAuthClient,
    XanoAuthError,
    XanoAuthRejected,
)
from MetroFlow.auth.infrastructure.session_cookie import (
    clear_session_cookie,
    get_session_token,
    set_session_cookie,
)


class CredentialsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    senha: str


class PublicUserResponse(BaseModel):
    id: int
    email: str


class AuthResponse(BaseModel):
    usuario: PublicUserResponse


auth_api = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


def _public_user(user: AuthenticatedUser) -> PublicUserResponse:
    return PublicUserResponse(id=user.id, email=user.email)


def _raise_public_error(error: XanoAuthError) -> None:
    if isinstance(error, XanoAuthRejected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais ou sessao invalidas.",
        ) from error

    if error.status_code in {400, 409, 422}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dados de autenticacao invalidos.",
        ) from error

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Servico de autenticacao indisponivel.",
    ) from error


def _auth_response(response: Response, session: AuthSession) -> AuthResponse:
    set_session_cookie(response, session.auth_token)
    return AuthResponse(usuario=_public_user(session.user))


@auth_api.post("/api/auth/signup", response_model=AuthResponse)
def signup(credentials: CredentialsRequest, response: Response) -> AuthResponse:
    try:
        with XanoAuthClient.from_environment() as client:
            session = client.signup(credentials.email, credentials.senha)
    except XanoAuthError as error:
        _raise_public_error(error)

    return _auth_response(response, session)


@auth_api.post("/api/auth/login", response_model=AuthResponse)
def login(credentials: CredentialsRequest, response: Response) -> AuthResponse:
    try:
        with XanoAuthClient.from_environment() as client:
            session = client.login(credentials.email, credentials.senha)
    except XanoAuthError as error:
        _raise_public_error(error)

    return _auth_response(response, session)


@auth_api.get("/api/auth/me", response_model=PublicUserResponse)
def me(request: Request) -> PublicUserResponse:
    auth_token = get_session_token(request)

    if auth_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessao ausente.",
        )

    try:
        with XanoAuthClient.from_environment() as client:
            user = client.me(auth_token)
    except XanoAuthError as error:
        _raise_public_error(error)

    return _public_user(user)


@auth_api.post("/api/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    """Encerra a sessao no navegador sem expor o token."""

    clear_session_cookie(response)
