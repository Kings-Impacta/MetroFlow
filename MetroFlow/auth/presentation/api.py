"""Rotas backend de autenticacao usadas pela interface Reflex."""

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field
from starlette.responses import JSONResponse

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


class EmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3, max_length=254)


class TokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=32, max_length=1024)


class ResetPasswordRequest(TokenRequest):
    senha: str = Field(min_length=8, max_length=256)


class MessageResponse(BaseModel):
    mensagem: str


auth_api = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@auth_api.exception_handler(RequestValidationError)
def validation_error(_request: Request, _error: RequestValidationError) -> JSONResponse:
    """Nao devolve valores de entrada presentes nos erros do Pydantic."""

    return JSONResponse(
        status_code=422,
        content={"detail": "Dados da requisicao invalidos."},
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
        detail="Serviço de autenticação indisponível.",
    ) from error


def _raise_action_token_error(error: XanoAuthError) -> None:
    """Distingue um link rejeitado de uma indisponibilidade do serviço."""

    if isinstance(error, XanoAuthRejected) or error.status_code in {
        400,
        404,
        409,
        410,
        422,
    }:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Link inválido ou expirado.",
        ) from error

    _raise_public_error(error)


def _raise_signup_error(error: XanoAuthError) -> None:
    """Orienta o usuário sem tratar duplicidade como falha de login."""

    if isinstance(error, XanoAuthRejected) or error.status_code in {
        400,
        409,
        422,
    }:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Não foi possível criar a conta. Se o e-mail já estiver "
                "cadastrado, entre ou recupere a senha."
            ),
        ) from error

    _raise_public_error(error)


def _is_generic_request_rejection(error: XanoAuthError) -> bool:
    """Oculta diferenças esperadas entre contas elegíveis e não elegíveis."""

    return isinstance(error, XanoAuthRejected) or error.status_code in {
        400,
        404,
        409,
        410,
        422,
    }


def _auth_response(response: Response, session: AuthSession) -> AuthResponse:
    set_session_cookie(response, session.auth_token)
    return AuthResponse(usuario=_public_user(session.user))


@auth_api.post("/api/auth/signup", response_model=MessageResponse)
def signup(credentials: CredentialsRequest) -> MessageResponse:
    try:
        with XanoAuthClient.from_environment() as client:
            client.signup(credentials.email, credentials.senha)
    except XanoAuthError as error:
        _raise_signup_error(error)

    return MessageResponse(
        mensagem="Conta criada. Confira seu e-mail para confirmar o cadastro."
    )


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


@auth_api.post(
    "/api/auth/email/reenviar",
    response_model=MessageResponse,
)
def resend_email_verification(request: EmailRequest) -> MessageResponse:
    try:
        with XanoAuthClient.from_environment() as client:
            client.request_email_verification(request.email)
    except XanoAuthError as error:
        if not _is_generic_request_rejection(error):
            _raise_public_error(error)

    return MessageResponse(
        mensagem="Se a conta estiver pendente, enviaremos uma nova mensagem."
    )


@auth_api.post(
    "/api/auth/email/confirmar",
    response_model=MessageResponse,
)
def confirm_email(request: TokenRequest) -> MessageResponse:
    try:
        with XanoAuthClient.from_environment() as client:
            client.confirm_email(request.token)
    except XanoAuthError as error:
        _raise_action_token_error(error)

    return MessageResponse(mensagem="E-mail confirmado. Agora você pode entrar.")


@auth_api.post(
    "/api/auth/senha/recuperar",
    response_model=MessageResponse,
)
def request_password_reset(request: EmailRequest) -> MessageResponse:
    try:
        with XanoAuthClient.from_environment() as client:
            client.request_password_reset(request.email)
    except XanoAuthError as error:
        if not _is_generic_request_rejection(error):
            _raise_public_error(error)

    return MessageResponse(
        mensagem="Se a conta for elegível, enviaremos as instruções por e-mail."
    )


@auth_api.post(
    "/api/auth/senha/redefinir",
    response_model=MessageResponse,
)
def reset_password(request: ResetPasswordRequest, response: Response) -> MessageResponse:
    try:
        with XanoAuthClient.from_environment() as client:
            client.reset_password(request.token, request.senha)
    except XanoAuthError as error:
        _raise_action_token_error(error)

    clear_session_cookie(response)
    return MessageResponse(
        mensagem="Senha redefinida. Entre novamente em todos os dispositivos."
    )
