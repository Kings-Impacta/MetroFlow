"""Interface demonstrativa do MetroFlow baseada nos prototipos exportados."""

import reflex as rx

from MetroFlow.auth.presentation.state import (
    AuthState,
    LOGOUT_SCRIPT,
)


BLUE = "#0957cf"
INK = "#10233f"
BG = "#f5f7ff"
PALE = "#eaf1ff"
GREEN = "#087f5b"


def _icon(name: str, color: str = INK, size: int = 20) -> rx.Component:
    return rx.icon(name, color=color, size=size)


def _pill(text: str, color: str = BLUE, background: str = PALE) -> rx.Component:
    return rx.badge(text, color=color, background=background, padding="0.35rem 0.7rem", border_radius="999px")


def _nav_link(label: str, href: str) -> rx.Component:
    return rx.link(label, href=href, color="#3f4756", font_weight="500", _hover={"color": BLUE})


def header() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.link(
                rx.hstack(
                    rx.image(src="/metroflow-logo.svg", width="2.35rem", height="2.35rem"),
                    rx.heading("MetroFlow", size="6", color=INK),
                    _pill("SP LIVE", "#29365b", "#e4e8ff"),
                    spacing="3",
                ),
                href="/",
                text_decoration="none",
            ),
            rx.hstack(
                _nav_link("Início", "/"),
                _nav_link("Buscar trajeto", "/buscar-trajeto"),
                _nav_link("Rotas & Comparação", "/rotas"),
                _nav_link("Sobre", "/sobre"),
                spacing="7",
                display={"base": "none", "md": "flex"},
            ),
            rx.hstack(
                _pill("●  Linhas operando normalmente", GREEN, "#f0f6ff"),
                rx.link("Status da Rede", href="/status", color="#3f4756", display={"base": "none", "lg": "block"}),
                rx.cond(
                    AuthState.auth_status == "authenticated",
                    rx.hstack(
                        rx.text(
                            AuthState.authenticated_email,
                            size="2",
                            color="#475569",
                            display={"base": "none", "xl": "block"},
                        ),
                        rx.button(
                            _icon("log-out", "white", 18),
                            title="Sair",
                            background=BLUE,
                            border_radius="50%",
                            padding="0.55rem",
                            on_click=rx.call_script(
                                LOGOUT_SCRIPT,
                                callback=AuthState.handle_logout_result,
                            ),
                        ),
                        spacing="3",
                    ),
                    rx.link(
                        _icon("circle-user-round", "white", 19),
                        href="/login",
                        background=BLUE,
                        padding="0.55rem",
                        border_radius="50%",
                    ),
                ),
                spacing="4",
            ),
            justify="between",
            align="center",
            width="100%",
            max_width="92rem",
            margin="auto",
            padding="0.85rem 2rem",
        ),
        position="sticky",
        top="0",
        z_index="10",
        background="rgba(255,255,255,.96)",
        border_bottom="1px solid #e8ebf3",
    )


def footer() -> rx.Component:
    return rx.hstack(
        rx.vstack(rx.heading("MetroFlow", size="4", color=INK), rx.text("Monitoramento em tempo real, rotas otimizadas e inteligência de trânsito metropolitano.", color="#647084", size="2"), align="start"),
        rx.hstack(_nav_link("Início", "/"), _nav_link("Buscar trajeto", "/buscar-trajeto"), _nav_link("Rotas", "/rotas"), _nav_link("Status", "/status"), _nav_link("Sobre", "/sobre"), spacing="5", display={"base": "none", "md": "flex"}),
        rx.text("●  Rede 100% monitorada", color=GREEN, font_weight="600"),
        justify="between", align="center", width="100%", padding="2.5rem", background="white", border_top="1px solid #e8ebf3",
    )


def shell(content: rx.Component) -> rx.Component:
    return rx.box(header(), content, footer(), background=BG, color=INK, min_height="100vh", font_family="Inter, Arial, sans-serif")


def _metric(value: str, label: str, icon: str, accent: str = BLUE) -> rx.Component:
    return rx.card(rx.hstack(rx.vstack(rx.text(label.upper(), size="2", font_weight="700", color="#556070"), rx.heading(value, size="7", color=INK), align="start"), rx.spacer(), rx.box(_icon(icon, accent, 27), background=PALE, padding="0.8rem", border_radius="0.8rem"), width="100%", align="center"), padding="1.25rem", width="100%")


def home_page() -> rx.Component:
    return shell(rx.box(
        rx.hstack(rx.text("●  REDE METROVIÁRIA ATIVA", color=GREEN, font_weight="700"), rx.spacer(), rx.text("L1 Azul  •  L2 Verde  •  L3 Vermelha  •  L4 Amarela  •  L5 Lilás  •  L15 Prata", color="#475569"), padding="1rem 1.5rem", background="white", border_radius="1rem", box_shadow="0 1px 4px #dfe5f0", width="100%"),
        rx.grid(
            rx.vstack(
                _pill("◉  MOBILIDADE URBANA EM TEMPO REAL", "#24385f", "#dfe7ff"),
                rx.heading("Encontre o melhor caminho pelo metrô", size="9", color=INK, max_width="46rem"),
                rx.text("Compare trajetos, tempo, baldeações e lotação em uma interface simples e moderna.", size="5", color="#5c6575"),
                rx.callout("Atualizações em tempo real com previsão de fluxo e baldeações otimizadas para toda a Grande São Paulo.", icon="zap", color_scheme="blue", width="100%"),
                rx.hstack(rx.link(rx.button("Explorar trajetos", size="3"), href="/buscar-trajeto"), rx.link(rx.button("Ver mapa da rede", variant="outline", size="3"), href="/status"), spacing="4"),
                rx.hstack(_metric("6", "Linhas monitoradas", "train-front"), _metric("99,4%", "Pontualidade", "clock", GREEN), _metric("Ao vivo", "Lotação estimada", "radio", GREEN), width="100%"),
                align="start", spacing="6",
            ),
            rx.card(
                rx.vstack(
                    rx.hstack(rx.box(_icon("train-front", BLUE), background=PALE, padding="0.7rem", border_radius="0.8rem"), rx.vstack(rx.heading("Planeje seu trajeto agora", size="5"), rx.text("Rotas diretas com menos transferências", color="#647084"), align="start"), rx.spacer(), _pill("SP Metrô", GREEN, "#baf7dc"), width="100%"),
                    rx.box(rx.text("ORIGEM", size="2", font_weight="700", color=BLUE), rx.heading("Sé", size="5"), rx.text("L1 Azul  •  L3 Vermelha", color="#566078"), background=PALE, padding="1rem", border_radius="0.8rem", width="100%"),
                    rx.center(_icon("arrow-down-up", BLUE), width="100%"),
                    rx.box(rx.text("DESTINO", size="2", font_weight="700", color="#d82d35"), rx.heading("Faria Lima", size="5"), rx.text("L4 Amarela", color="#7a6200"), background=PALE, padding="1rem", border_radius="0.8rem", width="100%"),
                    rx.hstack(rx.text("Via República (1 baldeação)", font_weight="700"), rx.spacer(), rx.text("~18 min", color=BLUE, font_weight="700"), width="100%"),
                    rx.link(rx.button("Buscar trajeto  →", width="100%", size="3"), href="/buscar-trajeto", width="100%"),
                    spacing="4", width="100%",
                ), padding="1.6rem",
            ),
            columns={"base": "1", "lg": "2"}, spacing="8", align="center", margin_top="2rem",
        ),
        rx.vstack(
            rx.text("INTELIGÊNCIA DE TRÂNSITO", color=BLUE, font_weight="700"),
            rx.heading("Por que usar o MetroFlow", size="8"),
            rx.grid(
                _feature("route", "Compare rotas", "Descubra caminhos alternativos considerando menor tempo, menos trocas e menores caminhadas."),
                _feature("users", "Evite lotação", "Indicadores cromáticos mostram vagões e estações mais vazias para sua viagem."),
                _feature("sliders-horizontal", "Escolha sua prioridade", "Filtre por velocidade, acessibilidade ou trajetos diretos."),
                columns={"base": "1", "md": "3"}, spacing="5", width="100%",
            ),
            align="center", spacing="5", margin_top="7rem",
        ),
        max_width="92rem", margin="auto", padding="2rem",
    ))


def _feature(icon: str, title: str, text: str) -> rx.Component:
    return rx.card(rx.vstack(rx.box(_icon(icon, BLUE, 28), background=PALE, padding="0.8rem", border_radius="0.8rem"), rx.heading(title, size="6"), rx.text(text, color="#5d6675", line_height="1.7"), align="start", spacing="4"), padding="1.7rem", min_height="16rem")


def search_page() -> rx.Component:
    return shell(rx.vstack(
        _pill("⌁  Navegador Inteligente SP Live"), rx.heading("Buscar trajeto", size="9"), rx.text("Calcule a melhor rota entre estações com estimativas de tempo, baldeações e nível de lotação em tempo real.", size="5", color="#5d6675", text_align="center"),
        rx.card(rx.vstack(
            rx.hstack(rx.button("◷  Partir agora", variant="outline"), rx.button("Definir horário de partida", variant="soft")),
            _station_input("Origem", "Estação Paraíso", "L1 Azul  •  L2 Verde", BLUE),
            rx.center(_icon("arrow-down-up", BLUE), width="100%"),
            _station_input("Destino", "Estação Faria Lima", "L4 Amarela", "#d39a00"),
            rx.text("CRITÉRIO DE OTIMIZAÇÃO", font_weight="700", size="2"),
            rx.grid(rx.button("⚡ Mais rápido"), rx.button("Menor lotação", variant="soft"), rx.button("Menos baldeações", variant="soft"), rx.button("Acessibilidade", variant="soft"), columns={"base":"2","md":"4"}, spacing="3", width="100%"),
            rx.link(rx.button("Buscar rotas disponíveis  →", width="100%", size="3"), href="/rotas", width="100%"), spacing="4", width="100%"
        ), padding="2rem", width="100%", max_width="60rem"),
        rx.callout("Dica de Fluxo MetroFlow: entre 17:30 e 19:30, rotas via Linha 2-Verde apresentam menor aglomeração.", icon="info", width="100%", max_width="60rem"),
        rx.card(rx.vstack(rx.heading("Mapa Esquemático Rápido", size="5"), rx.text("Jabaquara ━━━ Paraíso ━━━ Sé ━━━ Tatuapé", color=BLUE, font_weight="700", text_align="center", padding="4rem 1rem", background=PALE, border_radius="0.8rem", width="100%"), align="start"), width="100%", max_width="60rem", padding="1.5rem"),
        padding="3rem 1.5rem 7rem", spacing="5", align="center", min_height="80vh"
    ))


def _station_input(label: str, station: str, lines: str, color: str) -> rx.Component:
    return rx.box(rx.text(label.upper(), font_weight="700", size="2", color=color), rx.hstack(rx.heading(station, size="5"), rx.spacer(), _pill(lines, color), width="100%"), background=PALE, padding="1rem", border_radius="0.8rem", width="100%")


def _route_card(label: str, time: str, transfers: str, occupancy: str, recommended: bool = False) -> rx.Component:
    return rx.card(rx.vstack(
        rx.hstack(_pill(label, "white" if recommended else INK, BLUE if recommended else PALE), rx.spacer(), _pill(occupancy, GREEN, "#baf7dc"), width="100%"),
        rx.hstack(rx.heading(time, size="8"), rx.text(transfers, color="#566078"), spacing="5", align="end"),
        rx.text("Paraíso  →  Consolação  →  Paulista  →  Faria Lima", font_weight="600"),
        rx.text("Tarifa integrada: R$ 5,00  •  Próximo trem em 2 min", color="#5d6675"),
        rx.link(rx.button("Ver detalhes do trajeto  →", width="100%", variant="solid" if recommended else "soft"), href="/trajeto", width="100%"),
        align="start", spacing="4"
    ), padding="1.5rem", border_top=f"4px solid {BLUE}" if recommended else "none")


def routes_page() -> rx.Component:
    return shell(rx.box(
        rx.card(rx.hstack(rx.heading("Estação Paraíso  →  Estação Faria Lima", size="5"), rx.spacer(), rx.link(rx.button("Editar busca", variant="soft"), href="/buscar-trajeto"), width="100%"), padding="1.5rem"),
        rx.grid(
            rx.vstack(_route_card("★ RECOMENDADO", "18 min", "1 baldeação • 5 estações", "Baixa lotação (32%)", True), _route_card("⚡ MAIS RÁPIDO", "15 min", "2 baldeações • 4 estações", "Lotação moderada (58%)"), _route_card("TRAJETO MAIS TRANQUILO", "23 min", "0 baldeações", "Baixa lotação (25%)"), spacing="5"),
            rx.vstack(rx.card(rx.vstack(rx.heading("Visão Espacial da Rota", size="5"), rx.center(_icon("map", BLUE, 48), rx.text("Mapa da região central de São Paulo", color="#5d6675"), direction="column", background=PALE, min_height="16rem", width="100%", border_radius="0.8rem"), align="start"), padding="1.5rem", width="100%"), rx.card(rx.vstack(rx.heading("Status das Linhas da Rota", size="5"), rx.text("● Linha 2 - Verde     Operação normal", color=GREEN), rx.text("● Linha 4 - Amarela   Operação normal", color="#8a6900"), align="start"), padding="1.5rem", width="100%"), spacing="5"),
            columns={"base":"1","lg":"3"}, spacing="6", margin_top="1.5rem"
        ), max_width="92rem", margin="auto", padding="2rem", min_height="80vh"
    ))


def trip_page() -> rx.Component:
    steps = [("Estação Paraíso", "Embarque na Linha 2-Verde • Plataforma 2", GREEN), ("Consolação → Paulista", "Baldeação obrigatória • 3 min de caminhada", "#6d35d8"), ("Estação Paulista", "Linha 4-Amarela • sentido Vila Sônia", "#d39a00"), ("Estação Faria Lima", "Destino • chegada prevista 14:53", BLUE)]
    return shell(rx.box(
        rx.link("← Voltar para todos os trajetos", href="/rotas", color="#556070"),
        rx.hstack(rx.heading("Paraíso  →  Faria Lima", size="8"), _pill("ROTA RECOMENDADA"), margin="1rem 0 1.5rem"),
        rx.grid(_metric("18 minutos", "Tempo total", "clock"), _metric("1 transferência", "Baldeações", "arrow-right-left", "#6d35d8"), _metric("5 estações", "Total de paradas", "train-front"), _metric("Baixa lotação", "Lotação média", "accessibility", GREEN), columns={"base":"1","md":"4"}, spacing="4"),
        rx.grid(
            rx.card(rx.vstack(rx.heading("Passo a passo do trajeto", size="6"), *[rx.box(rx.heading(title, size="5"), rx.text(desc, color="#5d6675"), border_left=f"5px solid {color}", background=PALE, padding="1.3rem", border_radius="0.7rem", width="100%") for title, desc, color in steps], spacing="4", align="start"), padding="1.5rem"),
            rx.vstack(rx.card(rx.vstack(rx.heading("Resumo da Viagem", size="6"), rx.text("Tarifa integrada                         R$ 5,00"), rx.text("CO₂ economizado                           1,4 kg", color=GREEN), rx.callout("Acessibilidade total nas estações do percurso.", icon="accessibility", color_scheme="blue"), rx.button("Compartilhar itinerário", width="100%"), align="start", spacing="4"), padding="1.5rem", width="100%"), spacing="4"),
            columns={"base":"1","lg":"3"}, spacing="6", margin_top="1.5rem"
        ), max_width="92rem", margin="auto", padding="2rem", min_height="80vh"
    ))


def compare_page() -> rx.Component:
    return shell(rx.vstack(
        rx.box(_pill("ANÁLISE MULTIMODAL EM TEMPO REAL"), rx.heading("Comparar rotas", size="8"), rx.text("Avalie lado a lado tempo total, lotação, baldeações e esforço de caminhada para Paraíso → Faria Lima.", color="#5d6675", size="4"), width="100%"),
        rx.grid(_route_card("★ Melhor custo-benefício", "18 min", "1 troca • 280m caminhada", "Baixa (32%)", True), _route_card("⚡ Mais rápido", "15 min", "2 trocas • 490m caminhada", "Moderada (58%)"), _route_card("Mais conforto", "23 min", "0 trocas • 60m caminhada", "Muito baixa (21%)"), columns={"base":"1","lg":"3"}, spacing="5", width="100%"),
        rx.card(rx.vstack(rx.heading("Detalhamento de critérios lado a lado", size="7"), rx.grid(rx.text("Critério de viagem", font_weight="700"), rx.text("Rota 1", color=BLUE, font_weight="700"), rx.text("Rota 2", color=GREEN, font_weight="700"), rx.text("Rota 3", color="#6d35d8", font_weight="700"), rx.text("Tempo porta a porta"), rx.text("18 min"), rx.text("15 min"), rx.text("23 min"), rx.text("Baldeações & esforço"), rx.text("1 troca • 280m"), rx.text("2 trocas • 490m"), rx.text("0 trocas • 60m"), columns="4", spacing="4", width="100%"), align="start"), padding="1.5rem", width="100%"),
        max_width="92rem", margin="auto", padding="3rem 2rem 7rem", spacing="6", min_height="80vh"
    ))


def about_page() -> rx.Component:
    return shell(rx.vstack(
        rx.grid(rx.vstack(_pill("Tecnologia para mobilidade humana", GREEN), rx.text("INSTITUCIONAL", font_weight="700", color="#6b7280"), rx.heading("Sobre o MetroFlow", size="9"), rx.heading("Conectando pessoas e otimizando deslocamentos diários através de inteligência de tráfego metroviário em tempo real.", size="6", color=BLUE), rx.text("O MetroFlow nasceu para transformar a experiência de transporte coletivo sobre trilhos. Cruzamos dados operacionais ao vivo, sensores de densidade de plataforma e mapas esquemáticos intuitivos para oferecer a melhor rota.", size="4", color="#5d6675", line_height="1.8"), align="start", spacing="4"), rx.card(rx.vstack(rx.heading("Malha SP Conectada", size="5"), rx.center(rx.text("━━●━━━●━━\n      ●", white_space="pre", color=BLUE, font_size="2rem"), min_height="14rem", background=PALE, width="100%", border_radius="0.8rem"), rx.hstack(_metric("+35%", "Eficiência", "clock"), _metric("-180t", "Impacto urbano", "leaf", GREEN), width="100%"), align="start"), padding="1.5rem"), columns={"base":"1","lg":"2"}, spacing="7", width="100%"),
        rx.grid(_feature("network", "Como funciona", "Sensores em estações e composições transmitem telemetria contínua para estimar tempo e fluxo."), _feature("leaf", "Benefícios diretos", "Redução de tempo em percursos e rotas com acessibilidade garantida."), _feature("flag", "Nosso propósito", "Democratizar o acesso à informação de trânsito público com transparência e precisão."), columns={"base":"1","md":"3"}, spacing="5", width="100%"),
        rx.callout("Fontes oficiais e dados abertos: CPTM, Metrô SP e ViaQuatro.", icon="globe", width="100%"),
        max_width="72rem", margin="auto", padding="3rem 2rem 7rem", spacing="7", min_height="80vh"
    ))


def status_page() -> rx.Component:
    lines = [("Linha 1 - Azul", "Operação normal", BLUE), ("Linha 2 - Verde", "Operação normal", GREEN), ("Linha 3 - Vermelha", "Operação normal", "#d62f3a"), ("Linha 4 - Amarela", "Operação normal", "#d39a00"), ("Linha 5 - Lilás", "Operação normal", "#7137a8"), ("Linha 15 - Prata", "Operação normal", "#8a96a3")]
    return shell(rx.vstack(
        _pill("DIAGNÓSTICO & RESILIÊNCIA DO SISTEMA"), rx.heading("Status da Rede", size="9"), rx.text("Acompanhe em tempo real a operação das principais linhas metropolitanas.", size="5", color="#5d6675"),
        rx.callout("Todas as linhas monitoradas estão operando normalmente.", icon="circle-check", color_scheme="green", width="100%"),
        rx.grid(*[rx.card(rx.hstack(rx.box(width="0.8rem", height="3.2rem", background=color, border_radius="1rem"), rx.vstack(rx.heading(name, size="5"), rx.text(status, color=GREEN), align="start"), rx.spacer(), _pill("AO VIVO", GREEN, "#e1f8ee"), width="100%", align="center"), padding="1.3rem") for name, status, color in lines], columns={"base":"1","md":"2"}, spacing="4", width="100%"),
        max_width="72rem", margin="auto", padding="3rem 2rem 7rem", spacing="5", min_height="80vh"
    ))
