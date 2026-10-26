"""Planejador conectado ao backend, com resultados reais e estados explicitos."""

import reflex as rx

from MetroFlow.auth.presentation.state import (
    AuthState,
    LOGOUT_SCRIPT,
)
from MetroFlow.planning.presentation.state import PlanningState


BLUE = "#0957cf"
BLUE_DARK = "#0646a6"
INK = "#10233f"
TEXT = "#334155"
MUTED = "#52627a"
BG = "#f5f7ff"
PALE = "#eaf1ff"
GREEN = "#087f5b"
WHITE = "#ffffff"
BORDER = "#cbd5e1"


def header() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.link(
                rx.hstack(
                    rx.image(
                        src="/metroflow-logo.svg",
                        width="2rem",
                        height="2rem",
                    ),
                    rx.heading(
                        "MetroFlow",
                        size="6",
                        color=INK,
                    ),
                    align="center",
                ),
                href="/",
                text_decoration="none",
            ),
            rx.hstack(
                rx.link(
                    "Buscar trajeto",
                    href="/buscar-trajeto",
                    color=INK,
                    font_weight="500",
                ),
                rx.link(
                    "Sobre",
                    href="/sobre",
                    color=INK,
                    font_weight="500",
                ),
                rx.cond(
                    AuthState.auth_status == "authenticated",
                    rx.button(
                        "Sair",
                        variant="soft",
                        color_scheme="blue",
                        on_click=[
                            PlanningState.clear_planner,
                            rx.call_script(
                                LOGOUT_SCRIPT,
                                callback=AuthState.handle_logout_result,
                            ),
                        ],
                    ),
                    rx.link(
                        "Entrar",
                        href="/login",
                        color=BLUE,
                        font_weight="600",
                    ),
                ),
                spacing="4",
                align="center",
            ),
            justify="between",
            align="center",
            wrap="wrap",
            gap="1rem",
            max_width="72rem",
            margin="auto",
            padding="1rem 1.5rem",
        ),
        background=WHITE,
        border_bottom="1px solid #e0e7ef",
    )


def shell(
    content: rx.Component,
) -> rx.Component:
    return rx.box(
        header(),
        content,
        rx.box(
            rx.text(
                "MetroFlow · Planeje seu trajeto sobre trilhos.",
                size="2",
                color=MUTED,
            ),
            padding="2rem",
            text_align="center",
        ),
        background=BG,
        color=INK,
        min_height="100vh",
        font_family="Inter, Arial, sans-serif",
    )


def home_page() -> rx.Component:
    return shell(
        rx.vstack(
            rx.badge(
                "PLANEJE SUA VIAGEM",
                color_scheme="blue",
                variant="soft",
            ),
            rx.heading(
                "Seu próximo trajeto começa aqui",
                size="9",
                text_align="center",
                color=INK,
            ),
            rx.text(
                (
                    "Escolha as estações e consulte o caminho "
                    "de menor tempo, com as linhas e "
                    "baldeações necessárias."
                ),
                size="5",
                text_align="center",
                color=MUTED,
                max_width="42rem",
            ),
            rx.link(
                rx.button(
                    "Buscar trajeto",
                    size="4",
                    background=BLUE,
                    color=WHITE,
                ),
                href="/buscar-trajeto",
            ),
            rx.text(
                (
                    "A consulta utiliza as estações "
                    "disponíveis na malha cadastrada."
                ),
                size="2",
                color=MUTED,
            ),
            spacing="6",
            align="center",
            max_width="64rem",
            margin="auto",
            padding="5rem 1.5rem",
        )
    )


def _station_search(
    label: str,
    placeholder: str,
    query,
    matches,
    selected_id,
    on_query_change,
    on_select,
) -> rx.Component:
    return rx.vstack(
        rx.text(
            label.upper(),
            font_weight="700",
            size="2",
            color=BLUE_DARK,
        ),
        rx.box(
            rx.input(
                value=query,
                placeholder=placeholder,
                on_change=on_query_change,
                disabled=(
                    (
                        PlanningState.stations_status
                        != "ready"
                    )
                    |
                    (
                        PlanningState.route_status
                        == "loading"
                    )
                ),
                width="100%",
                size="3",
                background=WHITE,
                color=INK,
                border=f"1px solid {BORDER}",
                _placeholder={
                    "color": "#64748b",
                    "opacity": "1",
                },
                _focus={
                    "border_color": BLUE,
                    "box_shadow": (
                        "0 0 0 2px rgba(9,87,207,.18)"
                    ),
                },
                _disabled={
                    "opacity": "1",
                    "background": "#eef2f7",
                    "color": "#475569",
                    "cursor": "not-allowed",
                },
            ),
            rx.cond(
                (query != "")
                & (selected_id == ""),
                rx.box(
                    rx.vstack(
                        rx.foreach(
                            matches,
                            lambda station: rx.button(
                                station["label"],
                                type="button",
                                on_click=on_select(
                                    station["id"],
                                    station["name"],
                                ),
                                variant="ghost",
                                color=INK,
                                background=WHITE,
                                width="100%",
                                justify_content="flex-start",
                                text_align="left",
                                white_space="normal",
                                word_break="break-word",
                                height="auto",
                                min_width="0",
                                padding="0.8rem 1rem",
                                _hover={
                                    "background": PALE,
                                    "color": BLUE_DARK,
                                },
                            ),
                        ),
                        spacing="1",
                        align="stretch",
                        width="100%",
                    ),
                    position="absolute",
                    top="calc(100% + 0.35rem)",
                    left="0",
                    right="0",
                    background=WHITE,
                    border=f"1px solid {BORDER}",
                    border_radius="0.75rem",
                    box_shadow=(
                        "0 10px 30px "
                        "rgba(16,35,63,.16)"
                    ),
                    padding="0.35rem",
                    z_index="30",
                    max_height="18rem",
                    overflow_y="auto",
                    overflow_x="hidden",
                ),
            ),
            position="relative",
            width="100%",
        ),
        spacing="2",
        align="stretch",
        width="100%",
    )


def _instruction_card(
    instruction,
) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.center(
                rx.text(
                    instruction["step"],
                    font_weight="700",
                    color=WHITE,
                ),
                width="2.4rem",
                height="2.4rem",
                min_width="2.4rem",
                border_radius="50%",
                background=BLUE,
            ),
            rx.vstack(
                rx.badge(
                    instruction["kind"],
                    background="#dbeafe",
                    color=BLUE_DARK,
                    font_weight="700",
                ),
                rx.heading(
                    instruction["title"],
                    size="4",
                    color=INK,
                ),
                rx.text(
                    instruction["detail"],
                    color=TEXT,
                    line_height="1.6",
                ),
                rx.text(
                    instruction["meta"],
                    size="2",
                    color=BLUE_DARK,
                    font_weight="600",
                    line_height="1.5",
                ),
                align="start",
                spacing="2",
                width="100%",
            ),
            align="start",
            spacing="4",
            width="100%",
        ),
        padding="1rem",
        background=WHITE,
        border=f"1px solid {BORDER}",
        border_left=f"4px solid {BLUE}",
        border_radius="0.75rem",
        width="100%",
    )


def _confirm_trip_button() -> rx.Component:
    # Sem aviso apos a confirmacao: o botao permanece disponivel.
    return rx.button(
        "Confirmar viagem",
        type="button",
        size="3",
        background=BLUE,
        color=WHITE,
        _hover={
            "background": BLUE_DARK,
        },
        aria_label="Confirmar que vou fazer esta viagem",
        on_click=PlanningState.confirm_trip,
    )


def _result() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.badge(
                "TRAJETO ENCONTRADO",
                background="#dcfce7",
                color="#166534",
                font_weight="700",
            ),

            rx.heading(
                PlanningState.title,
                size="7",
                color=INK,
            ),

            rx.flex(
                rx.box(
                    rx.text(
                        "TEMPO ESTIMADO",
                        size="1",
                        font_weight="700",
                        color=MUTED,
                    ),
                    rx.text(
                        PlanningState.minutes,
                        " min",
                        weight="bold",
                        size="6",
                        color=INK,
                    ),
                ),
                rx.box(
                    rx.text(
                        "BALDEAÇÕES",
                        size="1",
                        font_weight="700",
                        color=MUTED,
                    ),
                    rx.text(
                        PlanningState.transfer_count,
                        weight="bold",
                        size="6",
                        color=INK,
                    ),
                ),
                rx.box(
                    rx.text(
                        "ESTAÇÕES",
                        size="1",
                        font_weight="700",
                        color=MUTED,
                    ),
                    rx.text(
                        PlanningState.station_names.length(),
                        weight="bold",
                        size="6",
                        color=INK,
                    ),
                ),
                gap="2rem",
                align="center",
                wrap="wrap",
                width="100%",
            ),

            rx.text(
                "Tempo calculado: ",
                PlanningState.seconds,
                (
                    " segundos. O cálculo considera os tempos dos trechos "
                    "e uma estimativa de 10 minutos por baldeação."
                ),
                size="2",
                color=MUTED,
            ),

            _confirm_trip_button(),

            rx.divider(),

            rx.vstack(
                rx.text(
                    "INSTRUÇÕES DE VIAGEM",
                    color=BLUE_DARK,
                    font_weight="700",
                    size="2",
                ),
                rx.heading(
                    "Como chegar",
                    size="6",
                    color=INK,
                ),
                rx.text(
                    (
                        "Siga as etapas abaixo na ordem "
                        "apresentada."
                    ),
                    color=MUTED,
                ),
                align="start",
                spacing="2",
                width="100%",
            ),

            rx.vstack(
                rx.foreach(
                    PlanningState.instructions,
                    _instruction_card,
                ),
                spacing="3",
                width="100%",
            ),

            rx.divider(),

            rx.heading(
                "Estações do percurso",
                size="4",
                color=INK,
            ),

            rx.flex(
                rx.foreach(
                    PlanningState.station_names,
                    lambda name: rx.badge(
                        name,
                        background="#dbeafe",
                        color=BLUE_DARK,
                        font_weight="600",
                    ),
                ),
                wrap="wrap",
                gap="0.5rem",
            ),

            rx.heading(
                "Trechos usados no cálculo",
                size="4",
                color=INK,
            ),

            rx.foreach(
                PlanningState.segments,
                lambda segment: rx.box(
                    rx.text(
                        segment["path"],
                        weight="bold",
                        color=INK,
                    ),
                    rx.text(
                        segment["line"],
                        size="2",
                        color=TEXT,
                    ),
                    rx.text(
                        segment["time"],
                        size="2",
                        color=INK,
                    ),
                    padding="1rem",
                    border_left=f"4px solid {BLUE}",
                    background=PALE,
                    border_radius="0.5rem",
                    width="100%",
                ),
            ),

            rx.heading(
                "Baldeações",
                size="4",
                color=INK,
            ),

            rx.cond(
                PlanningState.transfer_count == 0,
                rx.cond(
                    PlanningState.has_walking_integration,
                    rx.text(
                        (
                            "A rota inclui uma integração a pé. "
                            "Siga a sinalização da estação."
                        ),
                        color=TEXT,
                    ),
                    rx.text(
                        (
                            "Não é necessário trocar de linha. "
                            "Permaneça na mesma linha até "
                            "o ponto indicado para desembarque."
                        ),
                        color=TEXT,
                    ),
                ),
                rx.foreach(
                    PlanningState.transfers,
                    lambda transfer: rx.text(
                        transfer,
                        color=TEXT,
                    ),
                ),
            ),

            align="start",
            spacing="5",
            width="100%",
        ),
        padding="1.5rem",
        width="100%",
        role="status",
        aria_live="polite",
        background="#f8fafc",
    )


def search_page() -> rx.Component:
    return shell(
        rx.vstack(
            rx.heading(
                "Buscar trajeto",
                size="8",
                color=INK,
            ),

            rx.text(
                (
                    "Menor tempo de viagem; "
                    "em caso de empate, menos baldeações."
                ),
                color=MUTED,
            ),

            rx.cond(
                PlanningState.stations_status
                == "loading",
                rx.hstack(
                    rx.spinner(),
                    rx.text(
                        "Carregando estações…",
                        color=TEXT,
                    ),
                    role="status",
                ),
            ),

            rx.card(
                rx.form.root(
                    rx.vstack(
                        _station_search(
                            "Origem",
                            "Digite a estação de origem",
                            PlanningState.origin_query,
                            PlanningState.origin_matches,
                            PlanningState.origin_id,
                            PlanningState.update_origin_query,
                            PlanningState.choose_origin,
                        ),

                        rx.center(
                            rx.button(
                                rx.icon(
                                    "arrow-down-up",
                                    size=24,
                                ),
                                type="button",
                                variant="ghost",
                                color=BLUE,
                                aria_label=(
                                    "Inverter origem e destino"
                                ),
                                title=(
                                    "Inverter origem e destino"
                                ),
                                on_click=(
                                    PlanningState
                                    .swap_route_selection
                                ),
                                disabled=(
                                    (
                                        PlanningState.stations_status
                                        != "ready"
                                    )
                                    |
                                    (
                                        PlanningState.route_status
                                        == "loading"
                                    )
                                ),
                            ),
                            width="100%",
                        ),

                        _station_search(
                            "Destino",
                            "Digite a estação de destino",
                            PlanningState.destination_query,
                            PlanningState.destination_matches,
                            PlanningState.destination_id,
                            PlanningState.update_destination_query,
                            PlanningState.choose_destination,
                        ),

                        rx.button(
                            rx.cond(
                                PlanningState.route_status
                                == "loading",
                                "Buscando trajeto…",
                                "Buscar trajeto",
                            ),
                            type="submit",
                            size="3",
                            width="100%",
                            background=BLUE,
                            color=WHITE,
                            _hover={
                                "background": BLUE_DARK,
                            },
                            loading=(
                                PlanningState.route_status
                                == "loading"
                            ),
                            disabled=(
                                (
                                    PlanningState.stations_status
                                    != "ready"
                                )
                                |
                                (
                                    PlanningState.route_status
                                    == "loading"
                                )
                            ),
                        ),

                        spacing="4",
                        width="100%",
                    ),
                    on_submit=PlanningState.search,
                    width="100%",
                ),
                padding="1.5rem",
                width="100%",
                background="#f8fafc",
                border=f"1px solid {BORDER}",
            ),

            rx.cond(
                PlanningState.message != "",
                rx.callout(
                    PlanningState.message,
                    icon="info",
                    background="#fef3c7",
                    color="#78350f",
                    border="1px solid #f59e0b",
                    role="alert",
                    width="100%",
                ),
            ),

            rx.cond(
                (
                    (
                        PlanningState.stations_status
                        == "error"
                    )
                    |
                    (
                        PlanningState.stations_status
                        == "empty"
                    )
                    |
                    (
                        PlanningState.route_status
                        == "not_found"
                    )
                ),
                rx.button(
                    "Atualizar estações",
                    variant="outline",
                    color=BLUE_DARK,
                    border_color=BLUE,
                    on_click=PlanningState.load_stations,
                ),
            ),

            rx.cond(
                PlanningState.route_status
                == "loading",
                rx.hstack(
                    rx.spinner(),
                    rx.text(
                        "Consultando o melhor caminho…",
                        color=TEXT,
                    ),
                    role="status",
                ),
            ),

            rx.cond(
                PlanningState.route_status
                == "success",
                _result(),
            ),

            align="stretch",
            spacing="5",
            max_width="52rem",
            margin="auto",
            padding="3rem 1.5rem",
        )
    )


def routes_page() -> rx.Component:
    return search_page()


def trip_page() -> rx.Component:
    return search_page()


def compare_page() -> rx.Component:
    return search_page()


def about_page() -> rx.Component:
    return shell(
        rx.vstack(
            rx.heading(
                "Sobre o MetroFlow",
                size="8",
                color=INK,
            ),

            rx.text(
                (
                    "O MetroFlow ajuda a consultar trajetos "
                    "na malha ferroviária cadastrada, "
                    "mostrando estações, linhas, "
                    "operadores e baldeações."
                ),
                color=TEXT,
            ),

            rx.text(
                (
                    "O tempo estimado soma os trechos "
                    "do caminho. Neste MVP, não inclui "
                    "espera, caminhada ou tempo adicional "
                    "de transferência."
                ),
                color=TEXT,
            ),

            rx.link(
                "Planejar uma viagem",
                href="/buscar-trajeto",
                color=BLUE,
                font_weight="600",
            ),

            align="start",
            spacing="5",
            max_width="52rem",
            margin="auto",
            padding="4rem 1.5rem",
        )
    )


def status_page() -> rx.Component:
    return shell(
        rx.vstack(
            rx.heading(
                "Status da rede",
                size="8",
                color=INK,
            ),

            rx.text(
                (
                    "O MetroFlow ainda não recebe informações "
                    "operacionais em tempo real. Consulte os "
                    "canais oficiais dos operadores antes "
                    "de viajar."
                ),
                color=TEXT,
            ),

            rx.link(
                "Voltar ao planejador",
                href="/buscar-trajeto",
                color=BLUE,
                font_weight="600",
            ),

            align="start",
            spacing="5",
            max_width="52rem",
            margin="auto",
            padding="4rem 1.5rem",
        )
    )
