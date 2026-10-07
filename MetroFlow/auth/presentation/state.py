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


def build_email_action_script(form_id: str, endpoint: str, loading_label: str) -> str:
    """Envia somente o e-mail e mantém a resposta pública genérica."""

    return f"""
(async () => {{
    const form = document.getElementById({json.dumps(form_id)});
    const button = form?.querySelector('button[type="submit"]');
    if (!form || !button) return {{ok: false, status: 0, data: {{}}}};
    const originalLabel = button.textContent || "";
    button.disabled = true;
    button.textContent = {json.dumps(loading_label)};
    const email = String(new FormData(form).get("email") || "").trim();
    const apiUrl = new URL({json.dumps(endpoint)}, window.location.origin);
    try {{
        const response = await fetch(apiUrl.toString(), {{
            method: "POST", credentials: "include",
            headers: {{"Content-Type": "application/json"}},
            body: JSON.stringify({{email}})
        }});
        const data = await response.json().catch(() => ({{}}));
        return {{ok: response.ok, status: response.status, data}};
    }} catch (_error) {{
        return {{ok: false, status: 0, data: {{}}}};
    }} finally {{
        button.disabled = false;
        button.textContent = originalLabel;
    }}
}})()
""".strip()


def build_token_capture_script(form_id: str) -> str:
    """Retira o token da URL e o mantém somente no elemento do formulário."""

    return f"""
(() => {{
    const form = document.getElementById({json.dumps(form_id)});
    if (!form) return;
    const fragment = new URLSearchParams(window.location.hash.slice(1));
    const token = fragment.get("token");
    if (token) form._metroflowActionToken = token;
    window.history.replaceState(null, "", window.location.pathname);
}})()
""".strip()


def build_token_action_script(
    form_id: str, endpoint: str, *, include_password: bool
) -> str:
    """Envia o token no corpo e permite repetir falhas recuperáveis."""

    password = (
        ', senha: String(formData.get("senha") || "")'
        if include_password
        else ""
    )
    return f"""
(async () => {{
    {build_token_capture_script(form_id)};
    const form = document.getElementById({json.dumps(form_id)});
    if (!form) return {{ok: false, status: 0, data: {{}}}};
    if (form._metroflowActionPending) return {{ignored: true}};
    const token = String(form._metroflowActionToken || "");
    if (!token) return {{ok: false, status: 400, data: {{detail: "Link inválido ou expirado."}}}};
    const formData = new FormData(form);
    const payload = {{token{password}}};
    if ("senha" in payload && (payload.senha.length < 8 || payload.senha.length > 256)) {{
        return {{ok: false, status: 422, data: {{detail: "A senha deve ter entre 8 e 256 caracteres."}}}};
    }}
    const apiUrl = new URL({json.dumps(endpoint)}, window.location.origin);
    const button = form.querySelector('button[type="submit"]');
    form._metroflowActionPending = true;
    if (button) button.disabled = true;
    try {{
        const response = await fetch(apiUrl.toString(), {{
            method: "POST", credentials: "include",
            headers: {{"Content-Type": "application/json"}},
            body: JSON.stringify(payload)
        }});
        const data = await response.json().catch(() => ({{}}));
        if (response.ok || [401, 403, 410].includes(response.status)) {{
            delete form._metroflowActionToken;
        }}
        if (response.ok) form.reset();
        return {{ok: response.ok, status: response.status, data}};
    }} catch (_error) {{
        return {{ok: false, status: 0, data: {{}}}};
    }} finally {{
        form._metroflowActionPending = false;
        if (button) button.disabled = false;
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
    def clear_auth_feedback(self) -> None:
        self.auth_status = "idle"
        self.auth_message = ""

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
    def handle_signup_result(self, result: dict[str, Any]) -> None:
        data = result.get("data") if isinstance(result, dict) else None
        message = data.get("mensagem") if isinstance(data, dict) else None
        detail = data.get("detail") if isinstance(data, dict) else None

        if isinstance(result, dict) and result.get("ok") is True:
            self.auth_status = "success"
            self.authenticated_email = ""
            self.auth_message = (
                message
                if isinstance(message, str)
                else "Conta criada. Confira seu e-mail."
            )
            return

        self.auth_status = "error"
        self.authenticated_email = ""
        self.auth_message = (
            detail if isinstance(detail, str) else "Não foi possível criar a conta."
        )

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

    @rx.event
    def handle_action_result(self, result: dict[str, Any]) -> None:
        if isinstance(result, dict) and result.get("ignored") is True:
            return
        data = result.get("data") if isinstance(result, dict) else None
        message = data.get("mensagem") if isinstance(data, dict) else None
        detail = data.get("detail") if isinstance(data, dict) else None
        if isinstance(result, dict) and result.get("ok") is True:
            self.auth_status = "success"
            self.auth_message = message if isinstance(message, str) else "Solicitação concluída."
            return
        self.auth_status = "error"
        self.auth_message = detail if isinstance(detail, str) else "Não foi possível concluir."

    @rx.event
    def handle_reset_result(self, result: dict[str, Any]):
        """Encerra o fluxo de redefinição no login após remover a sessão."""

        if isinstance(result, dict) and result.get("ignored") is True:
            return

        data = result.get("data") if isinstance(result, dict) else None
        detail = data.get("detail") if isinstance(data, dict) else None
        if isinstance(result, dict) and result.get("ok") is True:
            self.auth_status = "idle"
            self.auth_message = ""
            self.authenticated_email = ""
            return rx.redirect("/login")

        self.auth_status = "error"
        self.auth_message = detail if isinstance(detail, str) else "Não foi possível concluir."
