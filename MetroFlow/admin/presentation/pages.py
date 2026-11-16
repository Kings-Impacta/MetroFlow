"""Página do painel administrativo.

Indicadores e controles só aparecem depois que o servidor aceita uma
operação administrativa; até lá a página mostra apenas o estado do acesso.
"""

import reflex as rx

from MetroFlow.admin.presentation.state import AdminState
from MetroFlow.planning.presentation.pages import BLUE, BORDER, INK, MUTED, WHITE, shell


def _card(item: rx.Var) -> rx.Component:
    return rx.box(
        rx.text(item["label"], size="2", color=MUTED, weight="medium"),
        rx.heading(item["value"], size="7", color=INK),
        rx.text(item["hint"], size="1", color=MUTED),
        background=WHITE,
        border=f"1px solid {BORDER}",
        border_radius="12px",
        padding="1rem",
    )


def _card_group(title: str, items: rx.Var) -> rx.Component:
    return rx.vstack(
        rx.heading(title, size="4", color=INK),
        rx.grid(
            rx.foreach(items, _card),
            columns=rx.breakpoints(initial="1", sm="2", md="4"),
            spacing="3",
            width="100%",
        ),
        spacing="2",
        width="100%",
    )


def _crowding() -> rx.Component:
    return rx.box(
        rx.text("Trechos lotados agora", size="2", color=MUTED, weight="medium"),
        rx.heading(AdminState.crowding_value, size="7", color=INK),
        rx.text(AdminState.crowding_hint, size="1", color=MUTED),
        rx.text(
            "Estimativa interna, visível somente para administradores.",
            size="1",
            color=MUTED,
        ),
        background=WHITE,
        border=f"1px solid {BORDER}",
        border_radius="12px",
        padding="1rem",
        width="100%",
    )


def _ranking_row(item: rx.Var) -> rx.Component:
    return rx.hstack(
        rx.text(item["position"], weight="bold", color=BLUE, min_width="2rem"),
        rx.text(item["name"], color=INK, weight="medium"),
        rx.badge(item["code"], variant="soft", color_scheme="gray"),
        rx.spacer(),
        rx.text(item["uses"], color=MUTED, size="2"),
        width="100%",
        align="center",
    )


def _ranking() -> rx.Component:
    return rx.box(
        rx.text(
            "Estações mais usadas como origem ou destino (7 dias)",
            size="2",
            color=MUTED,
            weight="medium",
        ),
        rx.cond(
            AdminState.ranking.length() > 0,
            rx.vstack(rx.foreach(AdminState.ranking, _ranking_row), spacing="2", width="100%"),
            rx.text("Ainda não há dados para o ranking.", color=MUTED, size="2"),
        ),
        background=WHITE,
        border=f"1px solid {BORDER}",
        border_radius="12px",
        padding="1rem",
        width="100%",
    )


def _indicators() -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.vstack(
                rx.heading("Indicadores", size="5", color=INK),
                rx.cond(
                    AdminState.computed_at != "",
                    rx.text("Apurados em ", AdminState.computed_at, size="2", color=MUTED),
                    rx.fragment(),
                ),
                spacing="1",
            ),
            rx.button(
                "Atualizar indicadores",
                on_click=AdminState.refresh_indicators,
                loading=AdminState.indicators_status == "loading",
                disabled=AdminState.indicators_status == "loading",
                variant="soft",
            ),
            justify="between",
            align="center",
            wrap="wrap",
            gap="1rem",
            width="100%",
        ),
        rx.cond(
            AdminState.indicators_status == "error",
            rx.callout(
                AdminState.indicators_message,
                icon="triangle_alert",
                color_scheme="red",
                role="alert",
                width="100%",
            ),
            rx.cond(
                AdminState.computed_at == "",
                rx.hstack(rx.spinner(), rx.text("Apurando indicadores…", color=MUTED), role="status"),
                rx.vstack(
                    _card_group("Uso", AdminState.usage_cards),
                    _card_group("Malha", AdminState.network_cards),
                    _card_group("Volume de viagens", AdminState.volume_cards),
                    rx.grid(
                        _crowding(),
                        _ranking(),
                        columns=rx.breakpoints(initial="1", md="2"),
                        spacing="3",
                        width="100%",
                    ),
                    spacing="5",
                    width="100%",
                ),
            ),
        ),
        spacing="3",
        width="100%",
    )


def _station_row(station: rx.Var) -> rx.Component:
    is_active = station["active"] == "true"
    return rx.table.row(
        rx.table.cell(rx.text(station["name"], weight="medium", color=INK)),
        rx.table.cell(rx.text(station["code"], color=MUTED)),
        rx.table.cell(rx.text(station["lines"], color=MUTED, size="2")),
        rx.table.cell(
            rx.cond(
                is_active,
                rx.badge("Ativa", color_scheme="green", variant="soft"),
                rx.badge("Inativa", color_scheme="gray", variant="soft"),
            )
        ),
        rx.table.cell(
            rx.button(
                rx.cond(is_active, "Inativar", "Ativar"),
                color_scheme=rx.cond(is_active, "red", "green"),
                variant="soft",
                size="1",
                loading=AdminState.updating_id == station["id"],
                disabled=AdminState.updating_id != "",
                on_click=AdminState.request_change(station["id"]),
            )
        ),
        align="center",
    )


def _stations() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.heading("Estações", size="5", color=INK),
            rx.cond(
                AdminState.stations_status == "ready",
                rx.text(AdminState.stations_summary, size="2", color=MUTED),
                rx.fragment(),
            ),
            spacing="1",
        ),
        rx.flex(
            rx.input(
                value=AdminState.query,
                on_change=AdminState.set_query,
                placeholder="Pesquisar por nome ou código",
                aria_label="Pesquisar estação por nome ou código",
                max_length=100,
                flex="1",
                min_width="14rem",
            ),
            rx.select.root(
                rx.select.trigger(aria_label="Filtrar por situação"),
                rx.select.content(
                    rx.select.item("Todas", value="todas"),
                    rx.select.item("Ativas", value="ativas"),
                    rx.select.item("Inativas", value="inativas"),
                ),
                value=AdminState.status_filter,
                on_change=AdminState.set_status_filter,
            ),
            gap="0.75rem",
            wrap="wrap",
            width="100%",
        ),
        rx.match(
            AdminState.stations_status,
            (
                "error",
                rx.callout(
                    AdminState.stations_message,
                    icon="triangle_alert",
                    color_scheme="red",
                    role="alert",
                    width="100%",
                ),
            ),
            (
                "ready",
                rx.cond(
                    AdminState.visible_stations.length() > 0,
                    rx.box(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Estação"),
                                    rx.table.column_header_cell("Código"),
                                    rx.table.column_header_cell("Linhas"),
                                    rx.table.column_header_cell("Situação"),
                                    rx.table.column_header_cell("Ação"),
                                )
                            ),
                            rx.table.body(rx.foreach(AdminState.visible_stations, _station_row)),
                            width="100%",
                            variant="surface",
                        ),
                        overflow_x="auto",
                        width="100%",
                    ),
                    rx.text("Nenhuma estação encontrada.", color=MUTED),
                ),
            ),
            rx.hstack(rx.spinner(), rx.text("Carregando estações…", color=MUTED), role="status"),
        ),
        spacing="3",
        width="100%",
    )


def _confirmation() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Inativar estação?"),
            rx.alert_dialog.description(
                rx.text(
                    rx.text.strong(AdminState.pending_name),
                    " (",
                    AdminState.pending_lines,
                    ") deixará de aparecer na seleção de origem e destino, e nenhum "
                    "trajeto passará por ela. As linhas que a atendem ficarão "
                    "interrompidas neste ponto até a estação ser ativada novamente.",
                ),
                rx.text(
                    "Viagens já em andamento não são encerradas.",
                    size="2",
                    color=MUTED,
                    margin_top="0.5rem",
                ),
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button("Cancelar", variant="soft", color_scheme="gray", on_click=AdminState.cancel_change),
                ),
                rx.alert_dialog.action(
                    rx.button("Inativar estação", color_scheme="red", on_click=AdminState.confirm_change),
                ),
                gap="0.75rem",
                justify="end",
                margin_top="1rem",
            ),
        ),
        open=AdminState.confirm_open,
        on_open_change=AdminState.handle_dialog_open,
    )


def _feedback() -> rx.Component:
    return rx.cond(
        AdminState.feedback != "",
        rx.callout(
            AdminState.feedback,
            icon="info",
            color_scheme=rx.cond(AdminState.feedback_kind == "success", "green", "red"),
            role="status",
            width="100%",
        ),
        rx.fragment(),
    )


def _authorized() -> rx.Component:
    return rx.vstack(
        _feedback(),
        _indicators(),
        rx.divider(),
        _stations(),
        _confirmation(),
        spacing="6",
        width="100%",
    )


def _restricted() -> rx.Component:
    return rx.callout(
        "O acesso a este painel é restrito a administradores.",
        icon="lock",
        color_scheme="amber",
        role="alert",
        width="100%",
    )


def _access_error() -> rx.Component:
    return rx.vstack(
        rx.callout(
            "Não foi possível verificar o acesso ao painel. Tente novamente.",
            icon="triangle_alert",
            color_scheme="red",
            role="alert",
            width="100%",
        ),
        rx.button("Tentar novamente", on_click=AdminState.load_panel, variant="soft"),
        spacing="3",
        width="100%",
    )


def admin_page() -> rx.Component:
    return shell(
        rx.box(
            rx.vstack(
                rx.vstack(
                    rx.badge("ADMINISTRAÇÃO", color_scheme="blue", variant="soft"),
                    rx.heading("Painel administrativo", size="8", color=INK),
                    rx.text(
                        "Acompanhe o uso do MetroFlow e gerencie a situação das estações.",
                        color=MUTED,
                    ),
                    spacing="2",
                ),
                rx.match(
                    AdminState.access,
                    ("authorized", _authorized()),
                    ("restricted", _restricted()),
                    ("error", _access_error()),
                    rx.hstack(rx.spinner(), rx.text("Verificando acesso…", color=MUTED), role="status"),
                ),
                spacing="6",
                width="100%",
            ),
            max_width="72rem",
            margin="auto",
            padding="2rem 1.5rem",
        )
    )
