"""Estado do painel administrativo; nenhuma credencial entra no estado Reflex.

As chamadas partem do navegador com o cookie HttpOnly. Indicadores e estações
são carregados separadamente, e cada resposta traz o identificador da
requisição para que respostas antigas sejam descartadas.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import reflex as rx
from pydantic import TypeAdapter, ValidationError

from MetroFlow.admin.presentation.view_models import (
    IndicatorsView,
    StationStatusView,
    StationView,
)
from MetroFlow.auth.presentation.state import AuthState
from MetroFlow.planning.presentation.state import normalize_search, request_script


INDICATORS_ENDPOINT = "/api/admin/indicators"
STATIONS_ENDPOINT = "/api/admin/stations"
STATUS_FILTERS = ("todas", "ativas", "inativas")
# Deslocamento fixo de São Paulo, sem horário de verão desde 2019.
SAO_PAULO = timezone(timedelta(hours=-3))


def status_endpoint(station_id: int) -> str:
    return f"/api/admin/stations/{station_id}/status"


def format_count(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def format_percentage(value: float) -> str:
    return f"{value:g}".replace(".", ",")


def format_moment(milliseconds: int) -> str:
    moment = datetime.fromtimestamp(milliseconds / 1000, SAO_PAULO)
    return moment.strftime("%d/%m/%Y às %H:%M:%S")


def plural(count: int, singular: str, plural_form: str) -> str:
    return f"{format_count(count)} {singular if count == 1 else plural_form}"


def card(label: str, value: int, hint: str) -> dict[str, str]:
    return {"label": label, "value": format_count(value), "hint": hint}


class AdminState(rx.State):
    # checking: aguardando a primeira resposta; authorized: alguma resposta
    # administrativa foi aceita; restricted: 403; error: nenhuma resposta válida.
    access: str = "checking"

    indicators_status: str = "idle"
    indicators_message: str = ""
    computed_at: str = ""
    usage_cards: list[dict[str, str]] = []
    network_cards: list[dict[str, str]] = []
    volume_cards: list[dict[str, str]] = []
    ranking: list[dict[str, str]] = []
    crowding_value: str = ""
    crowding_hint: str = ""

    stations_status: str = "idle"
    stations_message: str = ""
    stations: list[dict[str, str]] = []
    query: str = ""
    status_filter: str = "todas"

    confirm_open: bool = False
    pending_id: str = ""
    pending_name: str = ""
    pending_lines: str = ""
    updating_id: str = ""
    feedback: str = ""
    feedback_kind: str = ""

    _indicators_request: int = 0
    _stations_request: int = 0
    _change_request: int = 0

    @rx.var
    def visible_stations(self) -> list[dict[str, str]]:
        term = normalize_search(self.query)
        return [
            station
            for station in self.stations
            if (
                self.status_filter == "todas"
                or (self.status_filter == "ativas") == (station["active"] == "true")
            )
            and (not term or term in station["search"])
        ]

    @rx.var
    def stations_summary(self) -> str:
        inactive = sum(1 for station in self.stations if station["active"] != "true")
        return (
            f"{plural(len(self.stations), 'estação cadastrada', 'estações cadastradas')}"
            f" · {plural(inactive, 'inativa', 'inativas')}"
        )

    def _clear_indicators(self) -> None:
        self.computed_at = ""
        self.usage_cards = []
        self.network_cards = []
        self.volume_cards = []
        self.ranking = []
        self.crowding_value = ""
        self.crowding_hint = ""

    def _clear_pending(self) -> None:
        self.confirm_open = False
        self.pending_id = ""
        self.pending_name = ""
        self.pending_lines = ""

    def _reset_panel(self) -> None:
        # Invalida qualquer resposta ainda em trânsito.
        self._indicators_request += 1
        self._stations_request += 1
        self._change_request += 1
        self.access = "checking"
        self.indicators_status = "idle"
        self.indicators_message = ""
        self._clear_indicators()
        self.stations_status = "idle"
        self.stations_message = ""
        self.stations = []
        self.query = ""
        self.status_filter = "todas"
        self._clear_pending()
        self.updating_id = ""
        self.feedback = ""
        self.feedback_kind = ""

    @rx.event
    def clear_panel(self) -> None:
        self._reset_panel()

    def _indicators_call(self):
        return rx.call_script(
            request_script(INDICATORS_ENDPOINT, self._indicators_request),
            callback=AdminState.receive_indicators,
        )

    @rx.event
    def load_panel(self):
        self._reset_panel()
        self.indicators_status = "loading"
        self.stations_status = "loading"
        return [
            self._indicators_call(),
            rx.call_script(
                request_script(STATIONS_ENDPOINT, self._stations_request),
                callback=AdminState.receive_stations,
            ),
        ]

    @rx.event
    def refresh_indicators(self):
        if self.access != "authorized":
            return None
        self._indicators_request += 1
        self.indicators_status = "loading"
        self.indicators_message = ""
        return self._indicators_call()

    def _auth_failure(self, status: object):
        """Trata 401 e 403; devolve ``None`` para os demais códigos."""

        if status == 401:
            self._reset_panel()
            return [AuthState.handle_session_result({"ok": False}), rx.redirect("/login")]
        if status == 403:
            self._reset_panel()
            self.access = "restricted"
            return []
        return None

    def _section_failed(self) -> None:
        if self.access == "checking" and "error" == self.indicators_status == self.stations_status:
            self.access = "error"

    def _indicators_failed(self, message: str) -> None:
        # Valores anteriores não podem continuar parecendo atuais.
        self._clear_indicators()
        self.indicators_status = "error"
        self.indicators_message = message
        self._section_failed()

    @rx.event
    def receive_indicators(self, result: dict):
        if result.get("request_id") != self._indicators_request:
            return None
        handled = self._auth_failure(result.get("status"))
        if handled is not None:
            return handled
        if result.get("ok") is not True:
            self._indicators_failed("Não foi possível apurar os indicadores. Tente novamente.")
            return None
        try:
            view = IndicatorsView.model_validate(result.get("data"))
        except ValidationError:
            self._indicators_failed("Os indicadores recebidos são inválidos. Tente novamente.")
            return None

        self.access = "authorized"
        self._apply_indicators(view)
        self.indicators_status = "ready"
        self.indicators_message = ""
        return None

    def _apply_indicators(self, view: IndicatorsView) -> None:
        usage, network, volume = view.usage, view.network, view.volume
        self.computed_at = format_moment(view.computed_at_ms)
        self.usage_cards = [
            card("Rotas ativas", usage.active_routes, "Viagens em andamento agora"),
            card("Usuários em viagem agora", usage.users_travelling, "Usuários distintos com viagem em andamento"),
            card("Uso recente", usage.recent_users, "Usuários com viagem nos últimos 7 dias"),
            card("Contas habilitadas", usage.enabled_accounts, "Contas ativas com e-mail verificado"),
        ]
        self.network_cards = [
            card("Estações ativas", network.active_stations, "Disponíveis para busca"),
            card("Estações inativas", network.inactive_stations, "Fora da seleção e dos trajetos"),
            card("Linhas ativas", network.active_lines, "Linha e operador ativos"),
            card("Trechos ativos", network.active_segments, "Trecho, linha e operador ativos"),
        ]
        self.volume_cards = [
            card("Viagens registradas hoje", volume.trips_today, "Desde 00h no horário de São Paulo, incluindo substituídas"),
            card("Viagens nos últimos 7 dias", volume.trips_last_7_days, "Inclui viagens substituídas"),
        ]
        self.ranking = [
            {
                "position": f"{position}º",
                "name": item.name,
                "code": item.code,
                "uses": plural(item.uses, "uso", "usos"),
            }
            for position, item in enumerate(view.ranking, start=1)
        ]
        crowding = view.crowding
        if crowding.crowded_segments is None or crowding.minimum_users is None or crowding.percentage is None:
            self.crowding_value = "Indisponível"
            self.crowding_hint = "A configuração de lotação está ausente ou inválida."
        else:
            self.crowding_value = format_count(crowding.crowded_segments)
            self.crowding_hint = (
                f"Critério: no mínimo {plural(crowding.minimum_users, 'usuário', 'usuários')} "
                f"e {format_percentage(crowding.percentage)}% das viagens ativas no trecho e sentido."
            )

    def _stations_failed(self, message: str) -> None:
        self.stations = []
        self.stations_status = "error"
        self.stations_message = message
        self._section_failed()

    @rx.event
    def receive_stations(self, result: dict):
        if result.get("request_id") != self._stations_request:
            return None
        handled = self._auth_failure(result.get("status"))
        if handled is not None:
            return handled
        if result.get("ok") is not True:
            self._stations_failed("Não foi possível carregar as estações. Tente novamente.")
            return None
        try:
            views = TypeAdapter(list[StationView]).validate_python(result.get("data"))
        except ValidationError:
            self._stations_failed("A lista de estações recebida é inválida. Tente novamente.")
            return None

        self.access = "authorized"
        self.stations = [
            {
                "id": str(item.id),
                "name": item.name,
                "code": item.code,
                "active": "true" if item.active else "false",
                "lines": " · ".join(f"{line.code} {line.name}" for line in item.lines),
                "search": normalize_search(f"{item.name} {item.code}"),
            }
            for item in views
        ]
        self.stations_status = "ready"
        self.stations_message = ""
        return None

    @rx.event
    def set_query(self, value: str) -> None:
        self.query = value[:100]

    @rx.event
    def set_status_filter(self, value: str) -> None:
        self.status_filter = value if value in STATUS_FILTERS else "todas"

    def _station(self, station_id: str) -> dict[str, str] | None:
        return next((item for item in self.stations if item["id"] == station_id), None)

    @rx.event
    def request_change(self, station_id: str):
        if self.access != "authorized" or self.updating_id:
            return None
        station = self._station(station_id)
        if station is None:
            return None
        self.feedback = ""
        self.feedback_kind = ""
        if station["active"] == "true":
            # Inativar interrompe linhas: exige confirmação explícita.
            self.pending_id = station_id
            self.pending_name = station["name"]
            self.pending_lines = station["lines"] or "nenhuma linha ativa"
            self.confirm_open = True
            return None
        return self._send_change(station, True)

    @rx.event
    def cancel_change(self) -> None:
        self._clear_pending()

    @rx.event
    def handle_dialog_open(self, value: bool) -> None:
        if not value:
            self._clear_pending()

    @rx.event
    def confirm_change(self):
        station = self._station(self.pending_id) if self.pending_id else None
        self._clear_pending()
        if station is None or self.updating_id or station["active"] != "true":
            return None
        return self._send_change(station, False)

    def _send_change(self, station: dict[str, str], active: bool):
        self._change_request += 1
        self.updating_id = station["id"]
        return rx.call_script(
            request_script(
                status_endpoint(int(station["id"])),
                self._change_request,
                {"active": active},
            ),
            callback=AdminState.receive_change,
        )

    @rx.event
    def receive_change(self, result: dict):
        if result.get("request_id") != self._change_request:
            return None
        station_id = self.updating_id
        self.updating_id = ""
        handled = self._auth_failure(result.get("status"))
        if handled is not None:
            return handled

        station = self._station(station_id)
        name = station["name"] if station else "a estação"
        if result.get("ok") is not True:
            self.feedback_kind = "error"
            self.feedback = (
                "Estação não encontrada. Atualize o painel e tente novamente."
                if result.get("status") == 404
                else f"Não foi possível confirmar a alteração de {name}. "
                "A situação exibida é a última confirmada pelo sistema."
            )
            return None
        try:
            view = StationStatusView.model_validate(result.get("data"))
        except ValidationError:
            view = None
        if view is None or station is None or str(view.id) != station_id:
            self.feedback_kind = "error"
            self.feedback = (
                f"Não foi possível confirmar a alteração de {name}. "
                "A situação exibida é a última confirmada pelo sistema."
            )
            return None

        self.stations = [
            {**item, "active": "true" if view.active else "false"} if item["id"] == station_id else item
            for item in self.stations
        ]
        self.feedback_kind = "success"
        self.feedback = f"{name} {'ativada' if view.active else 'inativada'}."
        return AdminState.refresh_indicators
