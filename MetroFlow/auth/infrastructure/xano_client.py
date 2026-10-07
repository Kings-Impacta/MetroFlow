"""Cliente backend para os endpoints de autenticacao do Xano."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import httpx


XANO_AUTH_API_BASE_URL_ENV = "XANO_AUTH_API_BASE_URL"
DEFAULT_XANO_AUTH_API_BASE_URL = (
    "https://x8ki-letl-twmt.n7.xano.io/api:75UptKSb"
)


class XanoAuthError(RuntimeError):
    """Erro controlado durante uma operacao de autenticacao."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class XanoAuthRejected(XanoAuthError):
    """Credenciais ou sessao rejeitadas pelo Xano."""


class XanoAuthUnavailable(XanoAuthError):
    """Xano indisponivel ou inacessivel."""


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    """Dados publicos do usuario autenticado."""

    id: int
    email: str


@dataclass(frozen=True, slots=True)
class AuthSession:
    """Sessao emitida pelo Xano sem expor o token em representacoes."""

    user: AuthenticatedUser
    auth_token: str = field(repr=False)


class XanoAuthClient:
    """Cliente sincrono usado exclusivamente pelo backend Reflex."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        normalized_base_url = base_url.strip().rstrip("/")

        if not normalized_base_url:
            raise ValueError("A URL base da API de autenticacao e obrigatoria.")

        self._http = httpx.Client(
            base_url=f"{normalized_base_url}/",
            timeout=timeout,
            transport=transport,
        )

    @classmethod
    def from_environment(cls, *, timeout: float = 10.0) -> "XanoAuthClient":
        """Cria o cliente sem manter configuracao sensivel no codigo."""

        base_url = (
            os.getenv(XANO_AUTH_API_BASE_URL_ENV, "").strip()
            or DEFAULT_XANO_AUTH_API_BASE_URL
        )

        return cls(base_url, timeout=timeout)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "XanoAuthClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def signup(self, email: str, password: str) -> None:
        self._request(
            "POST",
            "auth/signup",
            json={"email": email, "senha": password},
        )

    def login(self, email: str, password: str) -> AuthSession:
        payload = self._request(
            "POST",
            "auth/login",
            json={"email": email, "senha": password},
        )
        return self._decode_session(payload)

    def me(self, auth_token: str) -> AuthenticatedUser:
        payload = self._request(
            "GET",
            "auth/me",
            auth_token=auth_token,
        )
        return self._decode_user(payload)

    def request_email_verification(self, email: str) -> None:
        self._request(
            "POST",
            "email/reenviar",
            json={"email": email},
        )

    def confirm_email(self, token: str) -> None:
        self._request(
            "POST",
            "email/confirmar",
            json={"token": token},
        )

    def request_password_reset(self, email: str) -> None:
        self._request(
            "POST",
            "senha/recuperar",
            json={"email": email},
        )

    def reset_password(self, token: str, password: str) -> None:
        self._request(
            "POST",
            "senha/redefinir",
            json={"token": token, "password": password},
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, str] | None = None,
        auth_token: str | None = None,
    ) -> dict[str, Any]:
        headers: dict[str, str] = {}

        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        try:
            response = self._http.request(
                method,
                path,
                json=json,
                headers=headers,
            )
        except httpx.TimeoutException as exc:
            raise XanoAuthUnavailable(
                "O servico de autenticacao excedeu o tempo de resposta."
            ) from exc
        except httpx.RequestError as exc:
            raise XanoAuthUnavailable(
                "O servico de autenticacao esta indisponivel."
            ) from exc

        if response.status_code in {401, 403}:
            raise XanoAuthRejected(
                "Credenciais ou sessao invalidas.",
                status_code=response.status_code,
            )

        if response.is_error:
            raise XanoAuthError(
                "Falha na solicitacao de autenticacao.",
                status_code=response.status_code,
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise XanoAuthError(
                "Resposta invalida do servico de autenticacao.",
                status_code=response.status_code,
            ) from exc

        if not isinstance(payload, dict):
            raise XanoAuthError(
                "Resposta invalida do servico de autenticacao.",
                status_code=response.status_code,
            )

        return payload

    @staticmethod
    def _decode_user(payload: dict[str, Any]) -> AuthenticatedUser:
        user_id = payload.get("id")
        email = payload.get("email")

        if (
            not isinstance(user_id, int)
            or isinstance(user_id, bool)
            or not isinstance(email, str)
            or not email
        ):
            raise XanoAuthError("Resposta de usuario invalida.")

        return AuthenticatedUser(id=user_id, email=email)

    @classmethod
    def _decode_session(cls, payload: dict[str, Any]) -> AuthSession:
        auth_token = payload.get("authToken")
        user_payload = payload.get("usuario")

        if not isinstance(auth_token, str) or not auth_token:
            raise XanoAuthError("Resposta de sessao invalida.")

        if not isinstance(user_payload, dict):
            raise XanoAuthError("Resposta de sessao invalida.")

        return AuthSession(
            user=cls._decode_user(user_payload),
            auth_token=auth_token,
        )
