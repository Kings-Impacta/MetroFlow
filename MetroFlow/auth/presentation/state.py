"""Estado e chamadas client-side dos formularios de autenticacao."""

from __future__ import annotations

import json
from typing import Any

import reflex as rx


def build_auth_script(
    form_id: str,
    endpoint: str,
    loading_label: str,
) -> str:
    """Cria o fetch que permite ao backend definir o cookie HttpOnly."""

    return f"""
(async () => {{
    const form = document.getElementById({json.dumps(form_id)});
    const button = form?.querySelector('button[type="submit"]');

    if (!form || !button) {{
        return {{
            ok: false,
            status: 0,
            data: {{detail: "Formulario indisponivel."}}
        }};
    }}

    const originalLabel = button.textContent || "";
    button.disabled = true;
    button.setAttribute("aria-busy", "true");
    button.textContent = {json.dumps(loading_label)};

    const formData = new FormData(form);
    const payload = {{
        email: String(formData.get("email") || ""),
        senha: String(formData.get("senha") || "")
    }};

    if (!payload.email || !payload.email.includes("@")) {{
        button.disabled = false;
        button.removeAttribute("aria-busy");
        button.textContent = originalLabel;
        return {{
            ok: false,
            status: 422,
            data: {{detail: "Informe um e-mail valido."}}
        }};
    }}

    if (payload.senha.length < 8) {{
        button.disabled = false;
        button.removeAttribute("aria-busy");
        button.textContent = originalLabel;
        return {{
            ok: false,
            status: 422,
            data: {{detail: "A senha deve ter pelo menos 8 caracteres."}}
        }};
    }}

    const apiUrl = new URL({json.dumps(endpoint)}, window.location.origin);
    if (["localhost", "127.0.0.1"].includes(window.location.hostname)
            && window.location.port === "3000") {{
        apiUrl.port = "8000";
    }}

    try {{
        const response = await fetch(apiUrl.toString(), {{
            method: "POST",
            credentials: "include",
            headers: {{"Content-Type": "application/json"}},
            body: JSON.stringify(payload)
        }});

        const data = await response.json().catch(() => ({{}}));

        return {{
            ok: response.ok,
            status: response.status,
            data
        }};
    }} catch (_error) {{
        return {{
            ok: false,
            status: 0,
            data: {{detail: "Servico de autenticacao indisponivel."}}
        }};
    }} finally {{
        button.disabled = false;
        button.removeAttribute("aria-busy");
        button.textContent = originalLabel;
    }}
}})()
""".strip()


def interpret_auth_result(
    result: object,
) -> tuple[str, str, str]:
    """Converte a resposta publica em estado seguro para a interface."""

    if not isinstance(result, dict):
        return "error", "Resposta de autenticacao invalida.", ""

    data = result.get("data")
    data = data if isinstance(data, dict) else {}

    if result.get("ok") is True:
        user = data.get("usuario")
        if (
            isinstance(user, dict)
            and isinstance(user.get("email"), str)
            and user["email"]
        ):
            return (
                "success",
                "Autenticacao concluida com sucesso.",
                user["email"],
            )

        return "error", "Resposta de autenticacao invalida.", ""

    status_code = result.get("status")
    detail = data.get("detail")

    if status_code == 401:
        return "error", "Credenciais invalidas.", ""

    if status_code in {400, 409, 422}:
        return (
            "error",
            detail if isinstance(detail, str) else "Dados invalidos.",
            "",
        )

    return "error", "Servico de autenticacao indisponivel.", ""


def build_session_script(endpoint: str, method: str = "GET") -> str:
    """Cria uma chamada sem acesso JavaScript ao cookie HttpOnly."""

    return f"""
(async () => {{
    const apiUrl = new URL({json.dumps(endpoint)}, window.location.origin);
    if (["localhost", "127.0.0.1"].includes(window.location.hostname)
            && window.location.port === "3000") {{
        apiUrl.port = "8000";
    }}

    try {{
        const response = await fetch(apiUrl.toString(), {{
            method: {json.dumps(method)},
            credentials: "include"
        }});
        const data = response.status === 204
            ? {{}}
            : await response.json().catch(() => ({{}}));
        return {{ok: response.ok, status: response.status, data}};
    }} catch (_error) {{
        return {{ok: false, status: 0, data: {{}}}};
    }}
}})()
""".strip()


def interpret_session_result(result: object) -> tuple[str, str]:
    """Interpreta a resposta publica da consulta da sessao."""

    if not isinstance(result, dict) or result.get("ok") is not True:
        return "unauthenticated", ""

    data = result.get("data")
    if not isinstance(data, dict):
        return "unauthenticated", ""

    email = data.get("email")
    if not isinstance(email, str) or not email:
        return "unauthenticated", ""

    return "authenticated", email


RESTORE_SESSION_SCRIPT = build_session_script("/api/auth/me")
LOGOUT_SCRIPT = build_session_script("/api/auth/logout", "POST")


class AuthState(rx.State):
    """Estado publico da experiencia de autenticacao."""

    auth_status: str = "idle"
    auth_message: str = ""
    authenticated_email: str = ""

    @rx.event
    def begin_auth(self) -> None:
        self.auth_status = "loading"
        self.auth_message = ""
        self.authenticated_email = ""

    @rx.event
    def handle_auth_result(self, result: dict[str, Any]):
        status_value, message, email = interpret_auth_result(result)
        self.auth_status = (
            "authenticated" if status_value == "success" else status_value
        )
        self.auth_message = message
        self.authenticated_email = email

        if status_value == "success":
            return rx.redirect("/")

    @rx.event
    def handle_session_result(self, result: dict[str, Any]) -> None:
        status_value, email = interpret_session_result(result)
        self.auth_status = status_value
        self.authenticated_email = email
        self.auth_message = ""

    @rx.event
    def handle_protected_session_result(self, result: dict[str, Any]):
        status_value, email = interpret_session_result(result)
        self.auth_status = status_value
        self.authenticated_email = email
        self.auth_message = ""

        if status_value != "authenticated":
            return rx.redirect("/login")

    @rx.event
    def handle_logout_result(self, result: dict[str, Any]):
        if result.get("ok") is True:
            self.auth_status = "unauthenticated"
            self.authenticated_email = ""
            self.auth_message = ""
            return rx.redirect("/login")

        self.auth_message = "Nao foi possivel encerrar a sessao."
