"""Adaptador backend para os futuros endpoints de planejamento do Xano."""

from __future__ import annotations

import os
from urllib.parse import urlsplit
from typing import Any

import httpx

from MetroFlow.planning.domain.models import (
    CalibrationReference,
    Line,
    Operator,
    RouteResult,
    Segment,
    Station,
    Transfer,
    TripConfirmation,
)


XANO_PLANNING_API_BASE_URL_ENV = "XANO_PLANNING_API_BASE_URL"
DEFAULT_XANO_PLANNING_API_BASE_URL = (
    "https://x8ki-letl-twmt.n7.xano.io/api:metroflow-planejamento"
)


class PlanningError(RuntimeError):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code


class PlanningUnauthorized(PlanningError):
    """Sessao ausente, invalida ou expirada."""


class PlanningUnavailable(PlanningError):
    """Servico externo indisponivel."""


class XanoPlanningClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
        calibration_enabled: bool = False,
    ) -> None:
        normalized = base_url.strip().rstrip("/")

        if not normalized:
            raise ValueError(
                "A URL da API de planejamento e obrigatoria."
            )
        if (
            calibration_enabled
            and normalized != DEFAULT_XANO_PLANNING_API_BASE_URL
            and urlsplit(normalized).hostname not in {"localhost", "127.0.0.1", "::1"}
        ):
            raise ValueError("A calibração exige a API oficial ou uma API local.")
        self._calibration_enabled = calibration_enabled

        self._http = httpx.Client(
            base_url=f"{normalized}/",
            timeout=timeout,
            transport=transport,
        )

    @classmethod
    def from_environment(
        cls,
        *,
        timeout: float = 10.0,
    ) -> "XanoPlanningClient":
        base_url = (
            os.getenv(XANO_PLANNING_API_BASE_URL_ENV, "").strip()
            or DEFAULT_XANO_PLANNING_API_BASE_URL
        )

        return cls(
            base_url,
            timeout=timeout,
            calibration_enabled=(
                base_url.rstrip("/") == DEFAULT_XANO_PLANNING_API_BASE_URL
                or os.getenv("METROFLOW_CALIBRACAO_LOCAL", "") == "1"
            ),
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "XanoPlanningClient":
        return self

    def __exit__(
        self,
        *_: object,
    ) -> None:
        self.close()

    def list_active_stations(
        self,
        auth_token: str,
    ) -> tuple[Station, ...]:
        payload = self._request(
            "GET",
            "estacoes",
            auth_token=auth_token,
            params={"suporta_calibracao": "true"} if self._calibration_enabled else None,
        )

        items = payload.get(
            "estacoes"
        )

        if not isinstance(items, list):
            raise PlanningError(
                "Resposta de estacoes invalida."
            )

        return tuple(
            self._decode_station(item)
            for item in items
        )

    def find_route(
        self,
        origin_id: int,
        destination_id: int,
        auth_token: str,
    ) -> RouteResult | None:
        payload = self._request(
            "POST",
            "trajetos/buscar",
            auth_token=auth_token,
            json={
                "estacao_origem_id": origin_id,
                "estacao_destino_id": destination_id,
                "suporta_troca_mesma_linha": True,
                "suporta_espera_partidas": True,
                "suporta_extensao_linha8": True,
                **({"suporta_calibracao": True} if self._calibration_enabled else {}),
            },
            allow_not_found=True,
        )

        if payload is None:
            return None

        if payload.get("versao_calibracao") is not None and not self._calibration_enabled:
            raise PlanningError("Contrato de calibração local não habilitado.")
        return self._decode_route(payload)

    def confirm_trip(
        self,
        trip: TripConfirmation,
        auth_token: str,
    ) -> None:
        # O Xano obtem o usuario pela sessao e le o tempo dos trechos cadastrados.
        if trip.calibration is not None and not self._calibration_enabled:
            raise PlanningError("Contrato de calibração local não habilitado.")
        payload = self._request(
            "POST",
            "viagens/confirmar",
            auth_token=auth_token,
            json={
                "trechos": [
                    {
                        "id": step.segment_id,
                        "estacao_origem_id": step.origin_id,
                        "estacao_destino_id": step.destination_id,
                    }
                    for step in trip.segments
                ],
                **({"calculado_em": trip.calculated_at_ms} if trip.calculated_at_ms is not None else {}),
                **({"versao_calibracao": trip.calibration.version,
                    "padroes_experimentais": list(trip.calibration.patterns)} if trip.calibration is not None else {}),
            },
        )

        if payload is None or payload.get("confirmada") is not True:
            raise PlanningError(
                "Resposta de confirmacao invalida."
            )

    def _request(
        self,
        method: str,
        path: str,
        *,
        auth_token: str,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        allow_not_found: bool = False,
    ) -> dict[str, Any] | None:
        if not auth_token:
            raise PlanningUnauthorized(
                "Sessao ausente.",
                status_code=401,
            )

        try:
            response = self._http.request(
                method,
                path,
                json=json,
                params=params,
                headers={
                    "Authorization": (
                        f"Bearer {auth_token}"
                    )
                },
            )

        except httpx.TimeoutException as exc:
            raise PlanningUnavailable(
                "O servico excedeu o tempo de resposta."
            ) from exc

        except httpx.RequestError as exc:
            raise PlanningUnavailable(
                "O servico esta indisponivel."
            ) from exc

        if response.status_code in {
            401,
            403,
        }:
            raise PlanningUnauthorized(
                "Sessao invalida ou expirada.",
                status_code=response.status_code,
            )

        if (
            allow_not_found
            and response.status_code == 404
        ):
            return None

        if response.is_error:
            raise PlanningError(
                "Falha na consulta de planejamento.",
                status_code=response.status_code,
            )

        try:
            payload = response.json()

        except ValueError as exc:
            raise PlanningError(
                "Resposta de planejamento invalida."
            ) from exc

        if not isinstance(payload, dict):
            raise PlanningError(
                "Resposta de planejamento invalida."
            )

        return payload

    @staticmethod
    def _integer(
        payload: dict[str, Any],
        key: str,
    ) -> int:
        value = payload.get(key)

        if (
            not isinstance(value, int)
            or isinstance(value, bool)
        ):
            raise PlanningError(
                f"Campo invalido: {key}."
            )

        return value

    @staticmethod
    def _text(
        payload: dict[str, Any],
        key: str,
    ) -> str:
        value = payload.get(key)

        if (
            not isinstance(value, str)
            or not value.strip()
        ):
            raise PlanningError(
                f"Campo invalido: {key}."
            )

        return value.strip()

    @staticmethod
    def _optional_text(
        payload: dict[str, Any],
        key: str,
    ) -> str | None:
        """
        Le um texto opcional.

        O Xano pode retornar null enquanto uma linha ainda
        nao tiver o sentido configurado.
        """

        value = payload.get(key)

        if value is None:
            return None

        if not isinstance(value, str):
            raise PlanningError(
                f"Campo invalido: {key}."
            )

        normalized = value.strip()

        if not normalized:
            return None

        return normalized

    @classmethod
    def _decode_operator(
        cls,
        payload: object,
    ) -> Operator:
        if not isinstance(payload, dict):
            raise PlanningError(
                "Operador invalido."
            )

        return Operator(
            id=cls._integer(
                payload,
                "id",
            ),
            name=cls._text(
                payload,
                "nome",
            ),
            code=cls._text(
                payload,
                "codigo",
            ),
        )

    @classmethod
    def _decode_line(
        cls,
        payload: object,
    ) -> Line:
        if not isinstance(payload, dict):
            raise PlanningError(
                "Linha invalida."
            )

        color = payload.get("cor")

        if (
            color is not None
            and not isinstance(color, str)
        ):
            raise PlanningError(
                "Cor da linha invalida."
            )

        return Line(
            id=cls._integer(
                payload,
                "id",
            ),
            name=cls._text(
                payload,
                "nome",
            ),
            code=cls._text(
                payload,
                "codigo",
            ),
            color=color,
            operator=cls._decode_operator(
                payload.get("operador")
            ),
        )

    @classmethod
    def _decode_station(
        cls,
        payload: object,
    ) -> Station:
        if not isinstance(payload, dict):
            raise PlanningError(
                "Estacao invalida."
            )

        lines = payload.get(
            "linhas",
            [],
        )

        if not isinstance(lines, list):
            raise PlanningError(
                "Linhas da estacao invalidas."
            )

        return Station(
            id=cls._integer(
                payload,
                "id",
            ),
            name=cls._text(
                payload,
                "nome",
            ),
            code=cls._text(
                payload,
                "codigo",
            ),
            lines=tuple(
                cls._decode_line(line)
                for line in lines
            ),
        )

    @classmethod
    def _decode_route(
        cls,
        payload: dict[str, Any],
    ) -> RouteResult:
        stations_raw = payload.get(
            "estacoes"
        )

        segments_raw = payload.get(
            "trechos"
        )

        transfers_raw = payload.get(
            "baldeacoes",
            [],
        )

        if (
            not isinstance(stations_raw, list)
            or not isinstance(segments_raw, list)
        ):
            raise PlanningError(
                "Trajeto incompleto."
            )

        if not isinstance(
            transfers_raw,
            list,
        ):
            raise PlanningError(
                "Baldeacoes invalidas."
            )

        stations = tuple(
            cls._decode_station(item)
            for item in stations_raw
        )

        by_id = {
            station.id: station
            for station in stations
        }

        def station(
            station_id: int,
        ) -> Station:
            try:
                return by_id[
                    station_id
                ]

            except KeyError as exc:
                raise PlanningError(
                    (
                        "Referencia de estacao "
                        "invalida."
                    )
                ) from exc

        segments: list[Segment] = []
        calibration = None
        if payload.get("versao_calibracao") is not None:
            patterns = payload.get("padroes_experimentais")
            if not isinstance(patterns, list) or len(patterns) != len(segments_raw):
                raise PlanningError("Padrões de calibração incompletos.")
            calibration = CalibrationReference(payload["versao_calibracao"], tuple(patterns))

        for index, item in enumerate(segments_raw):
            if not isinstance(
                item,
                dict,
            ):
                raise PlanningError(
                    "Trecho invalido."
                )

            segments.append(
                Segment(
                    id=cls._integer(
                        item,
                        "id",
                    ),
                    origin=station(
                        cls._integer(
                            item,
                            "estacao_origem_id",
                        )
                    ),
                    destination=station(
                        cls._integer(
                            item,
                            "estacao_destino_id",
                        )
                    ),
                    line=cls._decode_line(
                        item.get(
                            "linha"
                        )
                    ),
                    estimated_time_seconds=(
                        cls._integer(
                            item,
                            "tempo_estimado",
                        )
                    ),
                    direction=cls._optional_text(
                        item,
                        "sentido",
                    ),
                    segment_type=(
                        cls._optional_text(item, "tipo")
                        or "ferroviario"
                    ),
                    directed=bool(
                        item.get("direcionado", False)
                    ),
                    service_id=(
                        cls._integer(item, "servico_id")
                        if item.get("servico_id") is not None
                        else None
                    ),
                    waiting_time_seconds=(
                        cls._integer(item, "espera_estimada_segundos")
                        if item.get("espera_estimada_segundos") is not None else 0
                    ),
                    train_pattern=calibration.patterns[index] if calibration else None,
                    transfer_before_seconds=cls._integer(item, "baldeacao_antes_segundos") if calibration else None,
                )
            )

        if payload.get("tempo_espera_segundos") is not None and (
            cls._integer(payload, "tempo_espera_segundos")
            != sum(segment.waiting_time_seconds for segment in segments)
        ):
            raise PlanningError("Espera total inconsistente.")

        transfers: list[Transfer] = []

        for item in transfers_raw:
            if not isinstance(
                item,
                dict,
            ):
                raise PlanningError(
                    "Baldeacao invalida."
                )

            transfers.append(
                Transfer(
                    station=station(
                        cls._integer(
                            item,
                            "estacao_id",
                        )
                    ),
                    previous_line=(
                        cls._decode_line(
                            item.get(
                                "linha_anterior"
                            )
                        )
                    ),
                    next_line=(
                        cls._decode_line(
                            item.get(
                                "linha_seguinte"
                            )
                        )
                    ),
                )
            )

        origin = station(
            cls._integer(
                payload,
                "estacao_origem_id",
            )
        )

        destination = station(
            cls._integer(
                payload,
                "estacao_destino_id",
            )
        )

        notices = payload.get("avisos", [])
        if not isinstance(notices, list) or any(not isinstance(note, str) or not note.strip() or len(note) > 500 for note in notices):
            raise PlanningError("Avisos do trajeto inválidos.")

        return RouteResult(
            origin=origin,
            destination=destination,
            stations=stations,
            segments=tuple(
                segments
            ),
            transfers=tuple(
                transfers
            ),
            total_time_seconds=(
                cls._integer(
                    payload,
                    "tempo_total_segundos",
                )
            ),
            calculated_at_ms=(
                cls._integer(payload, "calculado_em")
                if payload.get("calculado_em") is not None else None
            ),
            notices=tuple(notices),
            calibration=calibration,
            public_estimate_seconds=(
                cls._integer(payload, "tempo_estimado_total_segundos")
                if "tempo_estimado_total_segundos" in payload else None
            ),
        )
