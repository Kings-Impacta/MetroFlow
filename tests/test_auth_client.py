"""Testes do cliente backend de autenticacao do Xano."""

import json
import unittest
from unittest.mock import patch

import httpx

from MetroFlow.auth_client import (
    AuthenticatedUser,
    XanoAuthClient,
    XanoAuthError,
    XanoAuthRejected,
)


BASE_URL = "https://example.xano.io/api:test"


class XanoAuthClientTests(unittest.TestCase):
    def test_signup_envia_credenciais_no_corpo(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.method, "POST")
            self.assertEqual(request.url.path, "/api:test/auth/signup")
            self.assertEqual(request.url.query, b"")
            self.assertEqual(
                json.loads(request.content),
                {"email": "user@example.com", "senha": "segredo123"},
            )
            return httpx.Response(
                200,
                json={
                    "authToken": "token-cadastro",
                    "usuario": {"id": 10, "email": "user@example.com"},
                },
            )

        with XanoAuthClient(
            BASE_URL,
            transport=httpx.MockTransport(handler),
        ) as client:
            session = client.signup("user@example.com", "segredo123")

        self.assertEqual(session.user.id, 10)
        self.assertEqual(session.user.email, "user@example.com")
        self.assertNotIn("token-cadastro", repr(session))

    def test_login_usa_endpoint_correto(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.method, "POST")
            self.assertEqual(request.url.path, "/api:test/auth/login")
            self.assertEqual(request.url.query, b"")
            self.assertEqual(
                json.loads(request.content),
                {"email": "user@example.com", "senha": "segredo123"},
            )
            return httpx.Response(
                200,
                json={
                    "authToken": "token-login",
                    "usuario": {"id": 11, "email": "user@example.com"},
                },
            )

        with XanoAuthClient(
            BASE_URL,
            transport=httpx.MockTransport(handler),
        ) as client:
            session = client.login("user@example.com", "segredo123")

        self.assertEqual(session.auth_token, "token-login")

    def test_me_envia_token_somente_no_cabecalho(self) -> None:
        auth_token = "token-sensivel"

        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.method, "GET")
            self.assertEqual(request.url.path, "/api:test/auth/me")
            self.assertEqual(request.url.query, b"")
            self.assertNotIn(auth_token, str(request.url))
            self.assertEqual(
                request.headers["Authorization"],
                f"Bearer {auth_token}",
            )
            return httpx.Response(
                200,
                json={"id": 12, "email": "user@example.com"},
            )

        with self.assertLogs("httpx", level="INFO") as captured_logs:
            with XanoAuthClient(
                BASE_URL,
                transport=httpx.MockTransport(handler),
            ) as client:
                user = client.me(auth_token)

        self.assertEqual(
            user,
            AuthenticatedUser(id=12, email="user@example.com"),
        )

        self.assertNotIn(
            auth_token,
            "\n".join(captured_logs.output),
        )
    def test_rejeicao_nao_expoe_token(self) -> None:
        auth_token = "token-que-nao-pode-vazar"

        transport = httpx.MockTransport(
            lambda _: httpx.Response(401, json={"message": "Unauthorized"})
        )

        with XanoAuthClient(BASE_URL, transport=transport) as client:
            with self.assertRaises(XanoAuthRejected) as captured:
                client.me(auth_token)

        self.assertEqual(captured.exception.status_code, 401)
        self.assertNotIn(auth_token, str(captured.exception))

    def test_resposta_invalida_e_rejeitada(self) -> None:
        transport = httpx.MockTransport(
            lambda _: httpx.Response(
                200,
                json={"authToken": "token", "usuario": {"id": 1}},
            )
        )

        with XanoAuthClient(BASE_URL, transport=transport) as client:
            with self.assertRaises(XanoAuthError):
                client.login("user@example.com", "segredo123")

    def test_configuracao_por_variavel_de_ambiente(self) -> None:
        with patch.dict(
            "os.environ",
            {"XANO_AUTH_API_BASE_URL": BASE_URL},
            clear=False,
        ):
            client = XanoAuthClient.from_environment()
            client.close()


if __name__ == "__main__":
    unittest.main()
