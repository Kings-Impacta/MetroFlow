"""Estado publico da busca; nenhuma credencial entra no estado Reflex."""

import json
import unicodedata

import reflex as rx
from pydantic import TypeAdapter, ValidationError

from MetroFlow.auth.presentation.state import AuthState
from MetroFlow.planning.presentation.view_models import (
    GuidanceView,
    RouteView,
    StationChoice,
)


ALIGHTING_SIDE_TEXT = {
    "esquerdo": "Desembarque pelo lado esquerdo",
    "direito": "Desembarque pelo lado direito",
    "ambos": "As portas abrem dos dois lados",
}


def guidance_fields(guidance: GuidanceView | None) -> dict[str, str]:
    """Lado de desembarque em destaque e observacao; vazios quando ausentes."""

    if guidance is None:
        return {"side": "", "note": ""}
    return {
        "side": ALIGHTING_SIDE_TEXT.get(guidance.alighting_side or "", ""),
        "note": guidance.note or "",
    }


def request_script(
    endpoint: str,
    request_id: int,
    payload: dict | None = None,
) -> str:
    options = {
        "method": "POST" if payload is not None else "GET",
        "credentials": "include",
        "cache": "no-store",
    }

    if payload is not None:
        options.update(
            headers={"Content-Type": "application/json"},
            body=json.dumps(payload),
        )

    return f"""
(async () => {{
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 35000);

    const apiUrl = new URL({json.dumps(endpoint)}, window.location.origin);

    try {{
        const response = await fetch(apiUrl.toString(), {{
            ...{json.dumps(options)},
            signal: controller.signal
        }});

        const data = await response.json().catch(() => null);

        return {{
            request_id: {request_id},
            ok: response.ok,
            status: response.status,
            data
        }};
    }} catch (_error) {{
        return {{
            request_id: {request_id},
            ok: false,
            status: 0,
            data: null
        }};
    }} finally {{
        clearTimeout(timer);
    }}
}})()
""".strip()


def normalize_search(value: str) -> str:
    """Normaliza a pesquisa ignorando maiusculas, minusculas e acentos."""

    normalized = unicodedata.normalize(
        "NFKD",
        value,
    )

    normalized = "".join(
        char
        for char in normalized
        if not unicodedata.combining(char)
    )

    return normalized.casefold().strip()


class PlanningState(rx.State):
    stations: list[dict[str, str]] = []

    origin_id: str = ""
    destination_id: str = ""

    origin_query: str = ""
    destination_query: str = ""

    origin_matches: list[dict[str, str]] = []
    destination_matches: list[dict[str, str]] = []

    stations_status: str = "idle"
    route_status: str = "idle"

    message: str = ""

    title: str = ""
    station_names: list[str] = []

    segments: list[dict[str, str]] = []

    instructions: list[dict[str, str]] = []

    transfers: list[str] = []

    minutes: int = 0
    seconds: int = 0
    transfer_count: int = 0
    has_walking_integration: bool = False

    _request_id: int = 0

    # Trechos do resultado apresentado, enviados ao confirmar a viagem.
    _trip_segments: list[dict[str, int]] = []
    _trip_request_id: int = 0

    def _clear_result(self) -> None:
        self.title = ""
        self.station_names = []

        self.segments = []
        self.instructions = []
        self.transfers = []

        self.minutes = 0
        self.seconds = 0
        self.transfer_count = 0
        self.has_walking_integration = False

        self._trip_segments = []

    def _filter_stations(
        self,
        query: str,
    ) -> list[dict[str, str]]:
        """Filtra as estacoes carregadas pelo texto digitado."""

        search = normalize_search(query)

        if not search:
            return []

        return [
            station
            for station in self.stations
            if search
            in normalize_search(
                station["label"]
            )
        ][:8]

    def _build_instructions(
        self,
        route: RouteView,
    ) -> list[dict[str, str]]:
        """
        Transforma os segmentos tecnicos em instrucoes
        amigaveis para o passageiro.

        Segmentos consecutivos na mesma linha,
        operador e sentido sao agrupados.
        """

        if not route.segments:
            return []

        groups: list[dict[str, object]] = []

        first_segment = route.segments[0]

        current_group: dict[str, object] = {
            "origin": first_segment.origin,
            "destination": first_segment.destination,
            "line": first_segment.line,
            "operator": first_segment.operator,
            "direction": first_segment.direction,
            "segment_type": first_segment.segment_type,
            "service_id": first_segment.service_id,
            "stops": 1,
            "seconds": first_segment.seconds,
            "guidance": first_segment.guidance,
        }

        for segment in route.segments[1:]:
            direction_compatible = (
                segment.direction is None
                or current_group["direction"] is None
                or segment.direction
                == current_group["direction"]
            )

            same_service = (
                segment.line
                == current_group["line"]
                and segment.operator
                == current_group["operator"]
                and direction_compatible
                and segment.segment_type
                == current_group["segment_type"]
                and segment.service_id
                == current_group["service_id"]
            )

            if same_service:
                current_group["destination"] = (
                    segment.destination
                )

                current_group["guidance"] = segment.guidance

                if current_group["direction"] is None:
                    current_group["direction"] = segment.direction

                current_group["stops"] = (
                    int(
                        current_group["stops"]
                    )
                    + 1
                )

                current_group["seconds"] = (
                    int(
                        current_group["seconds"]
                    )
                    + segment.seconds
                )

            else:
                groups.append(
                    current_group
                )

                current_group = {
                    "origin": segment.origin,
                    "destination": (
                        segment.destination
                    ),
                    "line": segment.line,
                    "operator": (
                        segment.operator
                    ),
                    "direction": (
                        segment.direction
                    ),
                    "segment_type": (
                        segment.segment_type
                    ),
                    "service_id": (
                        segment.service_id
                    ),
                    "stops": 1,
                    "seconds": (
                        segment.seconds
                    ),
                    "guidance": segment.guidance,
                }

        groups.append(
            current_group
        )

        instructions: list[
            dict[str, str]
        ] = []

        step_number = 1

        first_group = groups[0]

        if first_group["segment_type"] != "transferencia":
            first_direction = first_group["direction"]

            if first_direction:
                boarding_meta = f"Sentido {first_direction}."
            else:
                boarding_meta = (
                    "Confirme o sentido na sinalização da estação."
                )

            instructions.append(
                {
                    "step": str(step_number),
                    "kind": "EMBARQUE",
                    "title": f"Embarque em {first_group['origin']}",
                    "detail": (
                        f"Use a {first_group['line']}, operada por "
                        f"{first_group['operator']}."
                    ),
                    "meta": boarding_meta,
                    **guidance_fields(None),
                }
            )
            step_number += 1

        for index, group in enumerate(
            groups
        ):
            stops = int(
                group["stops"]
            )

            group_seconds = int(
                group["seconds"]
            )

            group_minutes = max(
                1,
                (
                    group_seconds
                    + 59
                )
                // 60,
            )

            trecho_text = (
                "trecho"
                if stops == 1
                else "trechos"
            )

            direction = (
                group["direction"]
            )

            if direction:
                direction_text = (
                    f" no sentido "
                    f"{direction}"
                )
            else:
                direction_text = ""

            is_transfer = group["segment_type"] == "transferencia"

            if is_transfer:
                instructions.append(
                    {
                        "step": str(step_number),
                        "kind": "INTEGRAÇÃO",
                        "title": (
                            "Faça a integração a pé de "
                            f"{group['origin']} até {group['destination']}"
                        ),
                        "detail": (
                            "Siga a sinalização da estação pela passagem "
                            "de integração entre as linhas."
                        ),
                        "meta": (
                            "Caminhada de aproximadamente "
                            f"{group_minutes} min."
                        ),
                        **guidance_fields(
                            groups[index - 1]["guidance"]
                            if index > 0
                            else None
                        ),
                    }
                )
            else:
                instructions.append(
                    {
                        "step": str(step_number),
                        "kind": "SIGA",
                        "title": f"Siga pela {group['line']}",
                        "detail": (
                            "Permaneça nesta linha"
                            f"{direction_text} de {group['origin']} "
                            f"até {group['destination']}."
                        ),
                        "meta": (
                            f"{stops} {trecho_text} · aproximadamente "
                            f"{group_minutes} min · {group['operator']}"
                        ),
                        **guidance_fields(None),
                    }
                )

            step_number += 1

            if index < len(groups) - 1:
                next_group = (
                    groups[
                        index + 1
                    ]
                )

                next_direction = (
                    next_group[
                        "direction"
                    ]
                )

                next_is_transfer = (
                    next_group["segment_type"] == "transferencia"
                )

                if next_is_transfer:
                    continue

                if next_direction:
                    transfer_meta = (
                        "Após a troca, siga pela "
                        f"{next_group['line']} "
                        "no sentido "
                        f"{next_direction}."
                    )
                else:
                    transfer_meta = (
                        "Após a troca, siga pela "
                        f"{next_group['line']}."
                    )

                if not is_transfer:
                    instructions.append(
                        {
                            "step": str(step_number),
                            "kind": "BALDEAÇÃO",
                            "title": (
                                "Faça baldeação em "
                                f"{group['destination']}"
                            ),
                            "detail": (
                                f"Troque da {group['line']} para a "
                                f"{next_group['line']}."
                            ),
                            "meta": transfer_meta,
                            **guidance_fields(group["guidance"]),
                        }
                    )
                    step_number += 1

                instructions.append(
                    {
                        "step": str(
                            step_number
                        ),
                        "kind": (
                            "EMBARQUE"
                        ),
                        "title": (
                            "Embarque na "
                            f"{next_group['line']}"
                        ),
                        "detail": (
                            "Na estação "
                            f"{next_group['origin']}, "
                            "continue pela "
                            f"{next_group['line']}."
                        ),
                        "meta": (
                            (
                                "Sentido "
                                f"{next_direction}."
                            )
                            if next_direction
                            else (
                                "Confirme o sentido "
                                "na sinalização "
                                "da estação."
                            )
                        ),
                        **guidance_fields(None),
                    }
                )

                step_number += 1

        arrived_on_foot = (
            groups[-1]["segment_type"] == "transferencia"
        )

        instructions.append(
            {
                "step": str(
                    step_number
                ),
                "kind": "CHEGADA" if arrived_on_foot else "DESEMBARQUE",
                "title": (
                    ("Chegue a " if arrived_on_foot else "Desembarque em ")
                    + f"{route.destination}"
                ),
                "detail": (
                    "Você chegou ao destino "
                    "selecionado."
                ),
                "meta": (
                    "Finalize sua viagem "
                    "nesta estação."
                ),
                **guidance_fields(
                    None
                    if arrived_on_foot
                    else groups[-1]["guidance"]
                ),
            }
        )

        return instructions

    @rx.event
    def clear_planner(
        self,
    ) -> None:
        self._request_id += 1

        self.stations = []

        self.origin_id = ""
        self.destination_id = ""

        self.origin_query = ""
        self.destination_query = ""

        self.origin_matches = []
        self.destination_matches = []

        self.stations_status = "idle"
        self.route_status = "idle"

        self.message = ""

        self._clear_result()

    @rx.event
    def load_stations(
        self,
    ):
        self.clear_planner()

        self.stations_status = (
            "loading"
        )

        return rx.call_script(
            request_script(
                "/api/planning/stations",
                self._request_id,
            ),
            callback=(
                PlanningState.receive_stations
            ),
        )

    def _unauthenticated(
        self,
    ):
        self.clear_planner()

        self.stations_status = (
            "unauthenticated"
        )

        self.route_status = (
            "unauthenticated"
        )

        return [
            AuthState.handle_session_result(
                {"ok": False}
            ),
            rx.redirect(
                "/login"
            ),
        ]

    @rx.event
    def receive_stations(
        self,
        result: dict,
    ):
        if (
            result.get(
                "request_id"
            )
            != self._request_id
        ):
            return

        if (
            result.get(
                "status"
            )
            == 401
        ):
            return (
                self._unauthenticated()
            )

        if (
            result.get(
                "ok"
            )
            is not True
        ):
            self.stations_status = (
                "error"
            )

            self.message = (
                "Não foi possível carregar "
                "as estações. "
                "Tente novamente."
            )

            return

        try:
            choices = TypeAdapter(
                list[
                    StationChoice
                ]
            ).validate_python(
                result.get(
                    "data"
                )
            )

        except ValidationError:
            self.stations_status = (
                "error"
            )

            self.message = (
                "A lista de estações "
                "recebida é inválida. "
                "Tente novamente."
            )

            return

        self.stations = [
            {
                "id": str(
                    item.id
                ),
                "name": item.name,
                "label": (
                    item.label
                ),
            }
            for item in choices
        ]

        self.stations_status = (
            "ready"
            if choices
            else "empty"
        )

        self.message = (
            ""
            if choices
            else (
                "Nenhuma estação "
                "disponível para consulta."
            )
        )

    @rx.event
    def update_origin_query(
        self,
        value: str,
    ) -> None:
        if (
            self.route_status
            == "loading"
        ):
            return

        self.origin_query = value
        self.origin_id = ""

        self.origin_matches = (
            self._filter_stations(
                value
            )
        )

        self._clear_result()

        self.route_status = "idle"
        self.message = ""

    @rx.event
    def update_destination_query(
        self,
        value: str,
    ) -> None:
        if (
            self.route_status
            == "loading"
        ):
            return

        self.destination_query = (
            value
        )

        self.destination_id = ""

        self.destination_matches = (
            self._filter_stations(
                value
            )
        )

        self._clear_result()

        self.route_status = "idle"
        self.message = ""

    @rx.event
    def choose_origin(
        self,
        station_id: str,
        label: str,
    ) -> None:
        if (
            self.route_status
            == "loading"
        ):
            return

        self.origin_id = (
            station_id
        )

        self.origin_query = (
            label
        )

        self.origin_matches = []

        self._clear_result()

        self.route_status = "idle"
        self.message = ""

    @rx.event
    def choose_destination(
        self,
        station_id: str,
        label: str,
    ) -> None:
        if (
            self.route_status
            == "loading"
        ):
            return

        self.destination_id = (
            station_id
        )

        self.destination_query = (
            label
        )

        self.destination_matches = []

        self._clear_result()

        self.route_status = "idle"
        self.message = ""

    @rx.event
    def swap_route_selection(self) -> None:
        if (
            self.route_status == "loading"
            or self.stations_status != "ready"
        ):
            return

        (
            self.origin_id,
            self.destination_id,
        ) = (
            self.destination_id,
            self.origin_id,
        )

        (
            self.origin_query,
            self.destination_query,
        ) = (
            self.destination_query,
            self.origin_query,
        )

        self.origin_matches = []
        self.destination_matches = []

        self._clear_result()

        self.route_status = "idle"
        self.message = ""

    @rx.event
    def select_origin(
        self,
        value: str,
    ) -> None:
        if (
            self.route_status
            == "loading"
        ):
            return

        self.origin_id = value

        self._clear_result()

        self.route_status = "idle"
        self.message = ""

    @rx.event
    def select_destination(
        self,
        value: str,
    ) -> None:
        if (
            self.route_status
            == "loading"
        ):
            return

        self.destination_id = (
            value
        )

        self._clear_result()

        self.route_status = "idle"
        self.message = ""

    @rx.event
    def search(
        self,
        _form_data: dict,
    ):
        if (
            self.route_status
            == "loading"
            or self.stations_status
            != "ready"
        ):
            return

        self._clear_result()

        available = {
            station["id"]
            for station
            in self.stations
        }

        if (
            self.origin_id
            not in available
            or self.destination_id
            not in available
        ):
            self.route_status = (
                "error"
            )

            self.message = (
                "Selecione origem e destino "
                "na lista de estações."
            )

            return

        if (
            self.origin_id
            == self.destination_id
        ):
            self.route_status = (
                "error"
            )

            self.message = (
                "Origem e destino "
                "devem ser diferentes."
            )

            return

        self._request_id += 1

        self.route_status = (
            "loading"
        )

        self.message = ""

        return rx.call_script(
            request_script(
                "/api/planning/route",
                self._request_id,
                {
                    "origin_id": int(
                        self.origin_id
                    ),
                    "destination_id": int(
                        self.destination_id
                    ),
                },
            ),
            callback=(
                PlanningState.receive_route
            ),
        )

    @rx.event
    def receive_route(
        self,
        result: dict,
    ):
        if (
            result.get(
                "request_id"
            )
            != self._request_id
        ):
            return

        self._clear_result()

        if (
            result.get(
                "status"
            )
            == 401
        ):
            return (
                self._unauthenticated()
            )

        if (
            result.get(
                "ok"
            )
            is not True
        ):
            self.route_status = (
                "not_found"
                if result.get(
                    "status"
                )
                == 404
                else "error"
            )

            self.message = {
                400: (
                    "Verifique as estações "
                    "selecionadas e "
                    "tente novamente."
                ),
                422: (
                    "Selecione uma origem "
                    "e um destino válidos."
                ),
                404: (
                    "Nenhum trajeto encontrado "
                    "para essas estações. "
                    "Atualize a lista ou "
                    "escolha outro destino."
                ),
            }.get(
                result.get(
                    "status"
                ),
                (
                    "Não foi possível "
                    "consultar o trajeto. "
                    "Tente novamente."
                ),
            )

            return

        try:
            route = (
                RouteView.model_validate(
                    result.get(
                        "data"
                    )
                )
            )

        except ValidationError:
            self.route_status = (
                "error"
            )

            self.message = (
                "O resultado recebido "
                "é inválido. "
                "Tente novamente."
            )

            return

        self.title = (
            f"{route.origin} "
            "→ "
            f"{route.destination}"
        )

        self.station_names = (
            route.stations
        )

        self.minutes = (
            route.minutes
        )

        self.seconds = (
            route.seconds
        )

        self.transfer_count = (
            route.transfer_count
        )

        self.has_walking_integration = any(
            step.segment_type == "transferencia"
            for step in route.segments
        )

        self.transfers = (
            route.transfers
        )

        self.segments = [
            {
                "path": (
                    f"{step.origin} "
                    "→ "
                    f"{step.destination}"
                ),
                "line": (
                    "Integração a pé"
                    if step.segment_type == "transferencia"
                    else f"{step.line} — {step.operator}"
                ),
                "time": (
                    f"{step.seconds} s"
                ),
            }
            for step
            in route.segments
        ]

        self.instructions = (
            self._build_instructions(
                route
            )
        )

        self._trip_segments = [
            {
                "id": step.id,
                "origin_id": step.origin_id,
                "destination_id": step.destination_id,
            }
            for step
            in route.segments
        ]

        self.route_status = (
            "success"
        )

        self.message = ""

    @rx.event
    def confirm_trip(
        self,
    ):
        """Confirma a viagem apresentada; o botao continua disponivel."""

        if (
            self.route_status
            != "success"
            or not self._trip_segments
        ):
            return

        self._trip_request_id += 1

        return rx.call_script(
            request_script(
                "/api/planning/trip",
                self._trip_request_id,
                {
                    "segments": (
                        self._trip_segments
                    ),
                },
            ),
            callback=(
                PlanningState.receive_trip_confirmation
            ),
        )

    @rx.event
    def receive_trip_confirmation(
        self,
        result: dict,
    ):
        # A interface nao exibe aviso apos a confirmacao. Somente a sessao
        # expirada muda a tela, conduzindo ao login.
        if (
            result.get(
                "status"
            )
            == 401
        ):
            return (
                self._unauthenticated()
            )
