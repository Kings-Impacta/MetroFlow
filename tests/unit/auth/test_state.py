"""Testes dos estados publicos de autenticacao."""

import unittest

from MetroFlow.auth.presentation.state import (
    AuthState,
    build_auth_script,
    build_email_action_script,
    build_session_script,
    build_token_action_script,
    interpret_auth_result,
    interpret_session_result,
)


class AuthStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = AuthState(_reflex_internal_init=True)

    def test_script_usa_cookie_sem_token_no_estado(self) -> None:
        script = build_auth_script(
            "login-form",
            "/api/auth/login",
            "Entrando...",
        )

        self.assertIn('credentials: "include"', script)
        self.assertIn("/api/auth/login", script)
        self.assertIn("aria-busy", script)
        self.assertIn("payload.senha.length < 8", script)
        self.assertIn(
            "A senha deve ter pelo menos 8 caracteres.",
            script,
        )
        self.assertNotIn("localStorage", script)
        self.assertNotIn("authToken", script)

    def test_resultado_de_sucesso(self) -> None:
        result = interpret_auth_result(
            {
                "ok": True,
                "status": 200,
                "data": {
                    "usuario": {
                        "id": 30,
                        "email": "user@example.com",
                    }
                },
            }
        )

        self.assertEqual(
            result,
            (
                "success",
                "Autenticacao concluida com sucesso.",
                "user@example.com",
            ),
        )

    def test_script_de_sessao_usa_cookie_http_only(self) -> None:
        script = build_session_script("/api/auth/me")

        self.assertIn("/api/auth/me", script)
        self.assertIn('credentials: "include"', script)
        self.assertNotIn("localStorage", script)

    def test_restaura_sessao_autenticada(self) -> None:
        result = interpret_session_result(
            {
                "ok": True,
                "status": 200,
                "data": {"id": 30, "email": "user@example.com"},
            }
        )

        self.assertEqual(result, ("authenticated", "user@example.com"))

    def test_sessao_ausente_fica_nao_autenticada(self) -> None:
        result = interpret_session_result(
            {"ok": False, "status": 401, "data": {}}
        )

        self.assertEqual(result, ("unauthenticated", ""))

    def test_credenciais_invalidas(self) -> None:
        result = interpret_auth_result(
            {
                "ok": False,
                "status": 401,
                "data": {"detail": "Mensagem interna ignorada."},
            }
        )

        self.assertEqual(result, ("error", "Credenciais invalidas.", ""))

    def test_campos_invalidos(self) -> None:
        result = interpret_auth_result(
            {
                "ok": False,
                "status": 400,
                "data": {"detail": "Dados de autenticacao invalidos."},
            }
        )

        self.assertEqual(
            result,
            ("error", "Dados de autenticacao invalidos.", ""),
        )

    def test_servico_indisponivel(self) -> None:
        result = interpret_auth_result(
            {
                "ok": False,
                "status": 0,
                "data": {},
            }
        )

        self.assertEqual(
            result,
            ("error", "Servico de autenticacao indisponivel.", ""),
        )

    def test_cadastro_concluido_nao_autentica_e_orienta_confirmacao(self) -> None:
        result = self.state.handle_signup_result(
            {
                "ok": True,
                "status": 200,
                "data": {"mensagem": "Confira seu e-mail para confirmar o cadastro."},
            }
        )

        self.assertIsNone(result)
        self.assertEqual(self.state.auth_status, "success")
        self.assertEqual(self.state.authenticated_email, "")
        self.assertEqual(
            self.state.auth_message,
            "Confira seu e-mail para confirmar o cadastro.",
        )

    def test_recuperacao_envia_email_no_corpo(self) -> None:
        script = build_email_action_script(
            "recovery-form", "/api/auth/senha/recuperar", "Enviando..."
        )

        self.assertIn('body: JSON.stringify({email})', script)
        self.assertIn("/api/auth/senha/recuperar", script)
        self.assertNotIn("localStorage", script)

    def test_token_vem_do_fragmento_e_url_e_limpa(self) -> None:
        script = build_token_action_script(
            "reset-form",
            "/api/auth/senha/redefinir",
            include_password=True,
        )

        self.assertIn("window.location.hash.slice(1)", script)
        self.assertIn("window.history.replaceState", script)
        self.assertIn("JSON.stringify(payload)", script)
        self.assertNotIn("window.location.search", script)
        self.assertNotIn("localStorage", script)

    def test_redefinicao_concluida_volta_ao_login(self) -> None:
        result = self.state.handle_reset_result(
            {"ok": True, "status": 200, "data": {"mensagem": "Senha redefinida."}}
        )

        self.assertIsNotNone(result)
        self.assertIn("/login", str(result))
        self.assertEqual(self.state.auth_status, "idle")
        self.assertEqual(self.state.authenticated_email, "")


if __name__ == "__main__":
    unittest.main()
