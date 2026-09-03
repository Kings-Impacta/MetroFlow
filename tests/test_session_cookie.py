"""Testes da politica de cookie da sessao."""

import unittest
from unittest.mock import patch

from starlette.requests import Request
from starlette.responses import Response

from MetroFlow.session_cookie import (
    SESSION_COOKIE_MAX_AGE,
    SESSION_COOKIE_NAME,
    clear_session_cookie,
    get_session_token,
    set_session_cookie,
)


class SessionCookieTests(unittest.TestCase):
    def test_cookie_local_e_httponly(self) -> None:
        response = Response()

        with patch.dict("os.environ", {"METROFLOW_ENV": "development"}):
            set_session_cookie(response, "token-local")

        header = response.headers["set-cookie"]

        self.assertIn(f"{SESSION_COOKIE_NAME}=token-local", header)
        self.assertIn("HttpOnly", header)
        self.assertIn("SameSite=lax", header)
        self.assertIn("Path=/", header)
        self.assertIn(f"Max-Age={SESSION_COOKIE_MAX_AGE}", header)
        self.assertNotIn("Secure", header)

    def test_cookie_de_producao_exige_https(self) -> None:
        response = Response()

        with patch.dict("os.environ", {"METROFLOW_ENV": "production"}):
            set_session_cookie(response, "token-producao")

        header = response.headers["set-cookie"]

        self.assertIn("HttpOnly", header)
        self.assertIn("SameSite=lax", header)
        self.assertIn("Secure", header)

    def test_token_e_lido_do_cookie_no_backend(self) -> None:
        request = Request(
            {
                "type": "http",
                "headers": [
                    (
                        b"cookie",
                        f"{SESSION_COOKIE_NAME}=token-backend".encode(),
                    )
                ],
            }
        )

        self.assertEqual(get_session_token(request), "token-backend")

    def test_cookie_ausente_retorna_none(self) -> None:
        request = Request({"type": "http", "headers": []})

        self.assertIsNone(get_session_token(request))

    def test_logout_expira_cookie_com_mesma_politica(self) -> None:
        response = Response()

        clear_session_cookie(response, secure=True)

        header = response.headers["set-cookie"]

        self.assertIn(f"{SESSION_COOKIE_NAME}=", header)
        self.assertIn("Max-Age=0", header)
        self.assertIn("HttpOnly", header)
        self.assertIn("SameSite=lax", header)
        self.assertIn("Secure", header)


if __name__ == "__main__":
    unittest.main()
