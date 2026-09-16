"""Aplicacao MetroFlow."""

import reflex as rx

from MetroFlow.auth.presentation.api import auth_api
from MetroFlow.planning.presentation.api import planning_api
from MetroFlow.planning.presentation.state import PlanningState
from MetroFlow.auth.presentation.pages import login_page, signup_page
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
app = rx.App(api_transformer=auth_api)

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
app.add_page(login_page, route="/login", title="Entrar | MetroFlow")
app.add_page(signup_page, route="/cadastro", title="Cadastro | MetroFlow")
