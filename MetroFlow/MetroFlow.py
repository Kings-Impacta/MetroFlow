"""Aplicacao MetroFlow."""

import reflex as rx

from MetroFlow.auth.presentation.api import auth_api
from MetroFlow.planning.presentation.api import planning_api
from MetroFlow.planning.presentation.state import PlanningState
from MetroFlow.auth.presentation.pages import (
    forgot_password_page,
    login_page,
    resend_verification_page,
    reset_password_page,
    signup_page,
    verify_email_page,
)
from MetroFlow.auth.presentation.state import (
    AuthState,
    RESTORE_SESSION_SCRIPT,
)
from MetroFlow.planning.presentation.pages import (
    about_page,
    compare_page,
    home_page,
    routes_page,
    search_page,
    status_page,
    trip_page,
)


auth_api.include_router(planning_api)
app = rx.App(
    api_transformer=auth_api,
    html_lang="pt-BR",
    html_custom_attrs={
        "translate": "no",
        "class": "notranslate",
    },
    head_components=[
        rx.el.meta(
            name="google",
            content="notranslate",
        ),
    ],
)

restore_session = rx.call_script(
    RESTORE_SESSION_SCRIPT,
    callback=AuthState.handle_session_result,
)
app.add_page(
    home_page,
    route="/",
    title="MetroFlow | Mobilidade inteligente",
    on_load=restore_session,
)
app.add_page(
    search_page,
    route="/buscar-trajeto",
    title="Buscar trajeto | MetroFlow",
    on_load=[restore_session, PlanningState.load_stations],
)
app.add_page(
    routes_page,
    route="/rotas",
    title="Rotas | MetroFlow",
    on_load=[restore_session, PlanningState.load_stations],
)
app.add_page(
    compare_page,
    route="/comparar",
    title="Comparar rotas | MetroFlow",
    on_load=[restore_session, PlanningState.load_stations],
)
app.add_page(
    trip_page,
    route="/trajeto",
    title="Detalhes do trajeto | MetroFlow",
    on_load=[restore_session, PlanningState.load_stations],
)
app.add_page(
    status_page,
    route="/status",
    title="Status da rede | MetroFlow",
    on_load=restore_session,
)
app.add_page(
    about_page,
    route="/sobre",
    title="Sobre | MetroFlow",
    on_load=restore_session,
)
app.add_page(
    login_page,
    route="/login",
    title="Entrar | MetroFlow",
    on_load=AuthState.clear_auth_feedback,
)
app.add_page(
    signup_page,
    route="/cadastro",
    title="Cadastro | MetroFlow",
    on_load=AuthState.clear_auth_feedback,
)
app.add_page(
    forgot_password_page,
    route="/recuperar-senha",
    title="Recuperar senha | MetroFlow",
    on_load=AuthState.clear_auth_feedback,
)
app.add_page(
    reset_password_page,
    route="/redefinir-senha",
    title="Redefinir senha | MetroFlow",
    on_load=AuthState.clear_auth_feedback,
)
app.add_page(
    verify_email_page,
    route="/confirmar-email",
    title="Confirmar e-mail | MetroFlow",
    on_load=AuthState.clear_auth_feedback,
)
app.add_page(
    resend_verification_page,
    route="/reenviar-confirmacao",
    title="Reenviar confirmação | MetroFlow",
    on_load=AuthState.clear_auth_feedback,
)
