"""Paginas dos formularios de autenticacao."""

import reflex as rx

from MetroFlow.auth.presentation.state import (
    AuthState,
    build_auth_script,
    build_email_action_script,
    build_token_action_script,
    build_token_capture_script,
)


LOGIN_SCRIPT = build_auth_script(
    "login-form",
    "/api/auth/login",
    "Entrando...",
)

SIGNUP_SCRIPT = build_auth_script(
    "signup-form",
    "/api/auth/signup",
    "Criando conta...",
)

RECOVERY_SCRIPT = build_email_action_script(
    "recovery-form", "/api/auth/senha/recuperar", "Enviando..."
)
RESEND_SCRIPT = build_email_action_script(
    "resend-form", "/api/auth/email/reenviar", "Enviando..."
)
RESET_SCRIPT = build_token_action_script(
    "reset-form", "/api/auth/senha/redefinir", include_password=True
)
VERIFY_SCRIPT = build_token_action_script(
    "verify-form", "/api/auth/email/confirmar", include_password=False
)


def _feedback() -> rx.Component:
    return rx.cond(
        AuthState.auth_message != "",
        rx.callout(
            AuthState.auth_message,
            color_scheme=rx.cond(
                (AuthState.auth_status == "authenticated")
                | (AuthState.auth_status == "success"),
                "green",
                "red",
            ),
            width="100%",
        ),
    )


def _email_field() -> rx.Component:
    return rx.form.field(
        rx.form.label("E-mail"),
        rx.form.control(
            rx.input(
                name="email",
                type="email",
                placeholder="voce@exemplo.com",
                required=True,
                width="100%",
            ),
            as_child=True,
        ),
        rx.form.message(
            "Informe seu e-mail.",
            match="valueMissing",
            color="red",
            opacity="1",
        ),
        rx.form.message(
            "Informe um e-mail válido.",
            match="typeMismatch",
            color="red",
            opacity="1",
        ),
        name="email",
        width="100%",
    )


def _password_field(placeholder: str) -> rx.Component:
    return rx.form.field(
        rx.form.label("Senha"),
        rx.form.control(
            rx.input(
                name="senha",
                type="password",
                placeholder=placeholder,
                required=True,
                min_length=8,
                width="100%",
            ),
            as_child=True,
        ),
        rx.form.message(
            "Informe sua senha.",
            match="valueMissing",
            color="red",
            opacity="1",
        ),
        rx.form.message(
            "A senha deve ter pelo menos 8 caracteres.",
            match="tooShort",
            color="red",
            opacity="1",
        ),
        name="senha",
        width="100%",
    )


def _auth_layout(
    title: str,
    description: str,
    form: rx.Component,
    footer: rx.Component,
) -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading(title, size="7"),
                rx.text(description, color_scheme="gray"),
                _feedback(),
                form,
                footer,
                spacing="5",
                width="100%",
            ),
            width="100%",
            max_width="28rem",
            padding="2rem",
        ),
        min_height="100vh",
        padding="1rem",
    )


def login_page() -> rx.Component:
    return _auth_layout(
        "Entrar",
        "Acesse sua conta para planejar seus trajetos.",
        rx.form.root(
            rx.vstack(
                _email_field(),
                _password_field("Sua senha"),
                rx.button(
                    "Entrar",
                    type="submit",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            id="login-form",
            on_submit=rx.call_script(
                LOGIN_SCRIPT,
                callback=AuthState.handle_auth_result,
            ),
            no_validate=True,
            width="100%",
        ),
        rx.vstack(
            rx.text(
                "Ainda não possui conta? ",
                rx.link("Cadastre-se", href="/cadastro"),
            ),
            rx.link("Esqueci minha senha", href="/recuperar-senha"),
            spacing="2",
        ),
    )


def signup_page() -> rx.Component:
    return _auth_layout(
        "Criar conta",
        "Cadastre-se com seu e-mail e uma senha segura.",
        rx.form.root(
            rx.vstack(
                _email_field(),
                _password_field("Mínimo de 8 caracteres"),
                rx.button(
                    "Criar conta",
                    type="submit",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            id="signup-form",
            on_submit=rx.call_script(
                SIGNUP_SCRIPT,
                callback=AuthState.handle_signup_result,
            ),
            no_validate=True,
            width="100%",
        ),
        rx.text(
            "Já possui conta? ",
            rx.link("Entrar", href="/login"),
        ),
    )


def _email_action_page(
    title: str,
    description: str,
    form_id: str,
    button_label: str,
    script: str,
) -> rx.Component:
    return _auth_layout(
        title,
        description,
        rx.form.root(
            rx.vstack(
                _email_field(),
                rx.button(button_label, type="submit", width="100%"),
                spacing="3",
                width="100%",
            ),
            id=form_id,
            on_submit=rx.call_script(script, callback=AuthState.handle_action_result),
            no_validate=True,
            width="100%",
        ),
        rx.link("Voltar para o login", href="/login"),
    )


def forgot_password_page() -> rx.Component:
    return _email_action_page(
        "Recuperar senha",
        "Informe seu e-mail para receber as instruções.",
        "recovery-form",
        "Enviar instruções",
        RECOVERY_SCRIPT,
    )


def resend_verification_page() -> rx.Component:
    return _email_action_page(
        "Reenviar confirmação",
        "Informe o e-mail usado no cadastro.",
        "resend-form",
        "Reenviar mensagem",
        RESEND_SCRIPT,
    )


def reset_password_page() -> rx.Component:
    return _auth_layout(
        "Definir nova senha",
        "Escolha uma nova senha com pelo menos oito caracteres.",
        rx.form.root(
            rx.vstack(
                _password_field("Nova senha"),
                rx.button("Redefinir senha", type="submit", width="100%"),
                spacing="3",
                width="100%",
            ),
            id="reset-form",
            on_mount=rx.call_script(build_token_capture_script("reset-form")),
            on_submit=rx.call_script(RESET_SCRIPT, callback=AuthState.handle_reset_result),
            no_validate=True,
            width="100%",
        ),
        rx.link("Voltar para o login", href="/login"),
    )


def verify_email_page() -> rx.Component:
    return _auth_layout(
        "Confirmar e-mail",
        "Confirme o endereço para ativar sua conta.",
        rx.form.root(
            rx.button("Confirmar e-mail", type="submit", width="100%"),
            id="verify-form",
            on_mount=rx.call_script(build_token_capture_script("verify-form")),
            on_submit=rx.call_script(VERIFY_SCRIPT, callback=AuthState.handle_action_result),
            width="100%",
        ),
        rx.link("Reenviar mensagem", href="/reenviar-confirmacao"),
    )
