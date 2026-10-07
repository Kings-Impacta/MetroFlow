"""Testes das rotas backend de autenticacao."""

import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from MetroFlow.auth.infrastructure.session_cookie import SESSION_COOKIE_NAME
from MetroFlow.auth.infrastructure.xano_client import (
    AuthSession,
    AuthenticatedUser,
    XanoAuthError,
    XanoAuthRejected,
)
from MetroFlow.auth.presentation.api import auth_api


class AuthApiTests(unittest.TestCase):
    def _xano_client(self) -> MagicMock:
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = None
        return client

    def test_login_define_cookie_sem_retornar_token(self) -> None:
        xano = self._xano_client()
        xano.login.return_value = AuthSession(
            user=AuthenticatedUser(id=20, email="user@example.com"),
            auth_token="token-login-seguro",
        )

        with (
            patch(
                "MetroFlow.auth.presentation.api.XanoAuthClient.from_environment",
                return_value=xano,
            ),
            patch.dict("os.environ", {"METROFLOW_ENV": "development"}),
            TestClient(auth_api) as client,
        ):
            response = client.post(
                "/api/auth/login",
                json={"email": "user@example.com", "senha": "segredo123"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"usuario": {"id": 20, "email": "user@example.com"}},
        )
        self.assertNotIn("token-login-seguro", response.text)

        cookie = response.headers["set-cookie"]
        self.assertIn(f"{SESSION_COOKIE_NAME}=token-login-seguro", cookie)
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=lax", cookie)
        self.assertNotIn("Secure", cookie)

        xano.login.assert_called_once_with(
            "user@example.com",
            "segredo123",
        )

    def test_signup_orienta_confirmacao_sem_criar_sessao(self) -> None:
        xano = self._xano_client()

        with (
            patch(
                "MetroFlow.auth.presentation.api.XanoAuthClient.from_environment",
                return_value=xano,
            ),
            TestClient(auth_api) as client,
        ):
            response = client.post(
                "/api/auth/signup",
                json={"email": "new@example.com", "senha": "segredo123"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"mensagem": "Conta criada. Confira seu e-mail para confirmar o cadastro."},
        )
        self.assertNotIn("set-cookie", response.headers)
        xano.signup.assert_called_once_with("new@example.com", "segredo123")

    def test_signup_duplicado_nao_exibe_erro_de_credenciais(self) -> None:
        xano = self._xano_client()
        xano.signup.side_effect = XanoAuthRejected(
            "E-mail já cadastrado.",
            status_code=401,
        )

        with (
            patch(
                "MetroFlow.auth.presentation.api.XanoAuthClient.from_environment",
                return_value=xano,
            ),
            TestClient(auth_api) as client,
        ):
            response = client.post(
                "/api/auth/signup",
                json={"email": "user@example.com", "senha": "segredo123"},
            )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.json(),
            {
                "detail": (
                    "Não foi possível criar a conta. Se o e-mail já estiver "
                    "cadastrado, entre ou recupere a senha."
                )
            },
        )

    def test_producao_define_cookie_secure(self) -> None:
        xano = self._xano_client()
        xano.login.return_value = AuthSession(
            user=AuthenticatedUser(id=22, email="user@example.com"),
            auth_token="token-producao",
        )

        with (
            patch(
                "MetroFlow.auth.presentation.api.XanoAuthClient.from_environment",
                return_value=xano,
            ),
            patch.dict("os.environ", {"METROFLOW_ENV": "production"}),
            TestClient(auth_api) as client,
        ):
            response = client.post(
                "/api/auth/login",
                json={"email": "user@example.com", "senha": "segredo123"},
            )

        self.assertIn("Secure", response.headers["set-cookie"])

    def test_me_le_token_do_cookie(self) -> None:
        xano = self._xano_client()
        xano.me.return_value = AuthenticatedUser(
            id=23,
            email="user@example.com",
        )

        with (
            patch(
                "MetroFlow.auth.presentation.api.XanoAuthClient.from_environment",
                return_value=xano,
            ),
            TestClient(auth_api) as client,
        ):
            client.cookies.set(SESSION_COOKIE_NAME, "token-cookie")
            response = client.get("/api/auth/me")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"id": 23, "email": "user@example.com"},
        )
        xano.me.assert_called_once_with("token-cookie")

    def test_me_sem_cookie_retorna_401(self) -> None:
        with TestClient(auth_api) as client:
            response = client.get("/api/auth/me")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Sessao ausente."})

    def test_logout_remove_cookie(self) -> None:
        with TestClient(auth_api) as client:
            client.cookies.set(SESSION_COOKIE_NAME, "token-cookie")
            response = client.post("/api/auth/logout")

        self.assertEqual(response.status_code, 204)
        cookie = response.headers["set-cookie"]
        self.assertIn(f"{SESSION_COOKIE_NAME}=", cookie)
        self.assertIn("Max-Age=0", cookie)
        self.assertIn("HttpOnly", cookie)

    def test_erro_nao_expoe_token(self) -> None:
        xano = self._xano_client()
        xano.login.side_effect = XanoAuthRejected(
            "Falha interna com token omitido.",
            status_code=401,
        )

        with (
            patch(
                "MetroFlow.auth.presentation.api.XanoAuthClient.from_environment",
                return_value=xano,
            ),
            TestClient(auth_api) as client,
        ):
            response = client.post(
                "/api/auth/login",
                json={"email": "user@example.com", "senha": "incorreta"},
            )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {"detail": "Credenciais ou sessao invalidas."},
        )

    def test_validacao_nao_devolve_entrada_sensivel(self) -> None:
        for endpoint in ("login", "signup"):
            with self.subTest(endpoint=endpoint), TestClient(auth_api) as client:
                response = client.post(
                    f"/api/auth/{endpoint}",
                    json={
                        "email": "user@example.com",
                        "senha": ["segredo-de-teste"],
                        "campo_extra": "token-de-teste",
                    },
                )

            self.assertEqual(response.status_code, 422)
            self.assertEqual(
                response.json(),
                {"detail": "Dados da requisicao invalidos."},
            )
            self.assertNotIn("segredo-de-teste", response.text)
            self.assertNotIn("token-de-teste", response.text)

    def test_recuperacao_de_senha_tem_resposta_generica(self) -> None:
        for rejected in (False, True):
            with self.subTest(rejected=rejected):
                xano = self._xano_client()
                if rejected:
                    xano.request_password_reset.side_effect = XanoAuthRejected(
                        "Conta inexistente.", status_code=401
                    )

                with (
                    patch(
                        "MetroFlow.auth.presentation.api.XanoAuthClient.from_environment",
                        return_value=xano,
                    ),
                    TestClient(auth_api) as client,
                ):
                    response = client.post(
                        "/api/auth/senha/recuperar",
                        json={"email": "desconhecido@example.com"},
                    )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json(),
                    {
                        "mensagem": (
                            "Se a conta for elegível, enviaremos as instruções "
                            "por e-mail."
                        )
                    },
                )

    def test_reenvio_de_verificacao_tem_resposta_generica(self) -> None:
        xano = self._xano_client()
        xano.request_email_verification.side_effect = XanoAuthRejected(
            "Conta inexistente.", status_code=401
        )

        with (
            patch(
                "MetroFlow.auth.presentation.api.XanoAuthClient.from_environment",
                return_value=xano,
            ),
            TestClient(auth_api) as client,
        ):
            response = client.post(
                "/api/auth/email/reenviar",
                json={"email": "desconhecido@example.com"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "mensagem": (
                    "Se a conta estiver pendente, enviaremos uma nova mensagem."
                )
            },
        )

    def test_redefinicao_nao_devolve_token_ou_senha(self) -> None:
        xano = self._xano_client()

        with (
            patch(
                "MetroFlow.auth.presentation.api.XanoAuthClient.from_environment",
                return_value=xano,
            ),
            TestClient(auth_api) as client,
        ):
            response = client.post(
                "/api/auth/senha/redefinir",
                json={
                    "token": "token-super-secreto-com-mais-de-32-caracteres",
                    "senha": "nova-senha-super-secreta",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            "token-super-secreto-com-mais-de-32-caracteres", response.text
        )
        self.assertNotIn("nova-senha-super-secreta", response.text)
        xano.reset_password.assert_called_once_with(
            "token-super-secreto-com-mais-de-32-caracteres",
            "nova-senha-super-secreta",
        )
        self.assertIn("Max-Age=0", response.headers["set-cookie"])
        self.assertIn("HttpOnly", response.headers["set-cookie"])

    def test_confirmacao_rejeitada_informa_link_invalido(self) -> None:
        xano = self._xano_client()
        xano.confirm_email.side_effect = XanoAuthRejected(
            "Token inválido.", status_code=401
        )

        with (
            patch(
                "MetroFlow.auth.presentation.api.XanoAuthClient.from_environment",
                return_value=xano,
            ),
            TestClient(auth_api) as client,
        ):
            response = client.post(
                "/api/auth/email/confirmar",
                json={"token": "token-invalido-com-mais-de-trinta-e-dois-caracteres"},
            )

        self.assertEqual(response.status_code, 410)
        self.assertEqual(response.json(), {"detail": "Link inválido ou expirado."})

    def test_recuperacao_oculta_rejeicoes_de_validacao(self) -> None:
        xano = self._xano_client()
        xano.request_password_reset.side_effect = XanoAuthError(
            "Conta não elegível.", status_code=404
        )

        with (
            patch(
                "MetroFlow.auth.presentation.api.XanoAuthClient.from_environment",
                return_value=xano,
            ),
            TestClient(auth_api) as client,
        ):
            response = client.post(
                "/api/auth/senha/recuperar",
                json={"email": "desconhecido@example.com"},
            )

        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
