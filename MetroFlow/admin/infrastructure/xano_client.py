"""Cliente backend do grupo `administracao` do Xano."""

from __future__ import annotations

import os
from typing import Any

import httpx

from MetroFlow.admin.domain.models import (
    AdminIndicators,
    AdminLine,
    AdminStation,
    CrowdingIndicator,
    StationStatus,
    StationUsage,
)


XANO_ADMIN_API_BASE_URL_ENV = "XANO_ADMIN_API_BASE_URL"
DEFAULT_XANO_ADMIN_API_BASE_URL = (
    "https://x8ki-letl-twmt.n7.xano.io/api:metroflow-administracao"
)


class AdminError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AdminUnauthorized(AdminError):
    """Sessão ausente, inválida ou expirada (HTTP 401)."""


class AdminForbidden(AdminError):
    """Sessão válida sem concessão de administrador (HTTP 403)."""


class AdminNotFound(AdminError):
    """Estação inexistente."""


class AdminUnavailable(AdminError):
    """Xano indisponível, lento ou com limite de requisições atingido."""


class XanoAdminClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        normalized = base_url.strip().rstrip("/")
        if not normalized:
            raise ValueError("A URL da API administrativa é obrigatória.")
        self._http = httpx.Client(
            base_url=f"{normalized}/",
            timeout=timeout,
            transport=transport,
        )

    @classmethod
    def from_environment(cls, *, timeout: float = 10.0) -> "XanoAdminClient":
        base_url = (
            os.getenv(XANO_ADMIN_API_BASE_URL_ENV, "").strip()
            or DEFAULT_XANO_ADMIN_API_BASE_URL
        )
        return cls(base_url, timeout=timeout)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "XanoAdminClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def indicators(self, auth_token: str) -> AdminIndicators:
        return self._decode_indicators(self._request("GET", "admin/indicadores", auth_token))

    def stations(self, auth_token: str) -> tuple[AdminStation, ...]:
        payload = self._request("GET", "admin/estacoes", auth_token)
        items = payload.get("estacoes")
        if not isinstance(items, list):
            raise AdminError("Lista de estações inválida.")
        return tuple(self._decode_station(item) for item in items)

    def set_station_status(
        self,
        station_id: int,
        active: bool,
        auth_token: str,
    ) -> StationStatus:
        payload = self._request(
            "POST",
            "admin/estacoes/situacao",
            auth_token,
            json={"estacao_id": station_id, "ativa": active},
        )
        try:
            return StationStatus(
                id=self._integer(payload, "id"),
                active=self._boolean(payload, "ativa"),
            )
        except ValueError as exc:
            raise AdminError("Situação da estação inválida.") from exc

    def _request(
        self,
        method: str,
        path: str,
        auth_token: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not auth_token:
            raise AdminUnauthorized("Sessão ausente.", status_code=401)

        try:
            response = self._http.request(
                method,
                path,
                json=json,
                headers={"Authorization": f"Bearer {auth_token}"},
            )
        except httpx.TimeoutException as exc:
            raise AdminUnavailable("O serviço excedeu o tempo de resposta.") from exc
        except httpx.RequestError as exc:
            raise AdminUnavailable("O serviço está indisponível.") from exc

        status = response.status_code
        if status == 401:
            raise AdminUnauthorized("Sessão inválida ou expirada.", status_code=status)
        if status == 403:
            raise AdminForbidden("Acesso restrito.", status_code=status)
        if status == 404:
            raise AdminNotFound("Registro não encontrado.", status_code=status)
        if status == 429 or status >= 500:
            raise AdminUnavailable("O serviço está indisponível.", status_code=status)
        if response.is_error:
            raise AdminError("Falha na consulta administrativa.", status_code=status)

        try:
            payload = response.json()
        except ValueError as exc:
            raise AdminError("Resposta administrativa inválida.") from exc
        if not isinstance(payload, dict):
            raise AdminError("Resposta administrativa inválida.")
        return payload

    @staticmethod
    def _integer(payload: dict[str, Any], key: str) -> int:
        value = payload.get(key)
        if not isinstance(value, int) or isinstance(value, bool):
            raise AdminError(f"Campo inválido: {key}.")
        return value

    @staticmethod
    def _boolean(payload: dict[str, Any], key: str) -> bool:
        value = payload.get(key)
        if not isinstance(value, bool):
            raise AdminError(f"Campo inválido: {key}.")
        return value

    @staticmethod
    def _text(payload: dict[str, Any], key: str) -> str:
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            raise AdminError(f"Campo inválido: {key}.")
        return value.strip()

    @staticmethod
    def _section(payload: dict[str, Any], key: str) -> dict[str, Any]:
        value = payload.get(key)
        if not isinstance(value, dict):
            raise AdminError(f"Seção inválida: {key}.")
        return value

    @classmethod
    def _decode_line(cls, payload: object) -> AdminLine:
        if not isinstance(payload, dict):
            raise AdminError("Linha inválida.")
        color = payload.get("cor")
        if color is not None and not isinstance(color, str):
            raise AdminError("Cor da linha inválida.")
        return AdminLine(
            id=cls._integer(payload, "id"),
            name=cls._text(payload, "nome"),
            code=cls._text(payload, "codigo"),
            color=color.strip() or None if isinstance(color, str) else None,
        )

    @classmethod
    def _decode_station(cls, payload: object) -> AdminStation:
        if not isinstance(payload, dict):
            raise AdminError("Estação inválida.")
        lines = payload.get("linhas", [])
        if not isinstance(lines, list):
            raise AdminError("Linhas da estação inválidas.")
        try:
            return AdminStation(
                id=cls._integer(payload, "id"),
                name=cls._text(payload, "nome"),
                code=cls._text(payload, "codigo"),
                active=cls._boolean(payload, "ativa"),
                lines=tuple(cls._decode_line(line) for line in lines),
            )
        except ValueError as exc:
            raise AdminError("Estação inválida.") from exc

    @classmethod
    def _decode_crowding(cls, payload: dict[str, Any]) -> CrowdingIndicator:
        crowded = payload.get("trechos_lotados")
        minimum = payload.get("minimo_usuarios")
        percentage = payload.get("percentual_lotacao")
        if crowded is not None and (not isinstance(crowded, int) or isinstance(crowded, bool)):
            raise AdminError("Campo inválido: trechos_lotados.")
        if minimum is not None and (not isinstance(minimum, int) or isinstance(minimum, bool)):
            raise AdminError("Campo inválido: minimo_usuarios.")
        if percentage is not None and (
            not isinstance(percentage, int | float) or isinstance(percentage, bool)
        ):
            raise AdminError("Campo inválido: percentual_lotacao.")
        return CrowdingIndicator(
            crowded_segments=crowded,
            minimum_users=minimum,
            percentage=float(percentage) if percentage is not None else None,
        )

    @classmethod
    def _decode_indicators(cls, payload: dict[str, Any]) -> AdminIndicators:
        usage = cls._section(payload, "uso")
        network = cls._section(payload, "malha")
        volume = cls._section(payload, "volume")
        crowding = cls._section(payload, "lotacao")
        ranking_raw = payload.get("ranking_estacoes")
        if not isinstance(ranking_raw, list):
            raise AdminError("Ranking inválido.")

        try:
            ranking = tuple(cls._decode_usage(item) for item in ranking_raw)
            return AdminIndicators(
                computed_at_ms=cls._integer(payload, "apurado_em"),
                active_routes=cls._integer(usage, "rotas_ativas"),
                users_travelling=cls._integer(usage, "usuarios_em_viagem"),
                recent_users=cls._integer(usage, "usuarios_uso_recente"),
                enabled_accounts=cls._integer(usage, "contas_habilitadas"),
                active_stations=cls._integer(network, "estacoes_ativas"),
                inactive_stations=cls._integer(network, "estacoes_inativas"),
                active_lines=cls._integer(network, "linhas_ativas"),
                active_segments=cls._integer(network, "trechos_ativos"),
                trips_today=cls._integer(volume, "viagens_hoje"),
                trips_last_7_days=cls._integer(volume, "viagens_7_dias"),
                ranking=ranking,
                crowding=cls._decode_crowding(crowding),
            )
        except AdminError:
            raise
        except ValueError as exc:
            raise AdminError("Indicadores inválidos.") from exc

    @classmethod
    def _decode_usage(cls, payload: object) -> StationUsage:
        if not isinstance(payload, dict):
            raise AdminError("Item de ranking inválido.")
        return StationUsage(
            id=cls._integer(payload, "id"),
            name=cls._text(payload, "nome"),
            code=cls._text(payload, "codigo"),
            uses=cls._integer(payload, "usos"),
        )
