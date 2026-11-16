"""Modelos do painel administrativo e suas invariantes."""

from __future__ import annotations

from dataclasses import dataclass


RANKING_LIMIT = 5


def _require_non_negative(**values: int) -> None:
    for name, value in values.items():
        if value < 0:
            raise ValueError(f"Contagem negativa: {name}.")


@dataclass(frozen=True, slots=True)
class AdminLine:
    """Linha ativa que atende uma estação."""

    id: int
    name: str
    code: str
    color: str | None = None


@dataclass(frozen=True, slots=True)
class AdminStation:
    """Estação cadastrada, ativa ou inativa, com as linhas que a atendem."""

    id: int
    name: str
    code: str
    active: bool
    lines: tuple[AdminLine, ...] = ()

    def __post_init__(self) -> None:
        if self.id <= 0:
            raise ValueError("Identificador de estação inválido.")
        if not self.name.strip() or not self.code.strip():
            raise ValueError("Estação sem nome ou código.")


@dataclass(frozen=True, slots=True)
class StationStatus:
    """Situação vigente de uma estação após uma alteração."""

    id: int
    active: bool

    def __post_init__(self) -> None:
        if self.id <= 0:
            raise ValueError("Identificador de estação inválido.")


@dataclass(frozen=True, slots=True)
class StationUsage:
    """Estação do ranking com a quantidade de usos como origem ou destino."""

    id: int
    name: str
    code: str
    uses: int

    def __post_init__(self) -> None:
        if self.uses < 1:
            raise ValueError("Estação do ranking sem uso.")


@dataclass(frozen=True, slots=True)
class CrowdingIndicator:
    """Trechos lotados no instante da apuração, com o critério vigente.

    Sem configuração válida, os três campos são ``None``: o indicador fica
    indisponível, e não zero.
    """

    crowded_segments: int | None
    minimum_users: int | None
    percentage: float | None

    @property
    def available(self) -> bool:
        return self.crowded_segments is not None

    def __post_init__(self) -> None:
        values = (self.crowded_segments, self.minimum_users, self.percentage)
        if all(value is None for value in values):
            return
        if any(value is None for value in values):
            raise ValueError("Indicador de lotação incompleto.")
        _require_non_negative(crowded_segments=self.crowded_segments)
        if self.minimum_users < 1:
            raise ValueError("Mínimo de usuários inválido.")
        if not 0 < self.percentage <= 100:
            raise ValueError("Percentual de lotação inválido.")


@dataclass(frozen=True, slots=True)
class AdminIndicators:
    """Indicadores agregados; não contêm dados de usuários nem de viagens."""

    computed_at_ms: int
    active_routes: int
    users_travelling: int
    recent_users: int
    enabled_accounts: int
    active_stations: int
    inactive_stations: int
    active_lines: int
    active_segments: int
    trips_today: int
    trips_last_7_days: int
    ranking: tuple[StationUsage, ...]
    crowding: CrowdingIndicator

    def __post_init__(self) -> None:
        if self.computed_at_ms <= 0:
            raise ValueError("Momento da apuração inválido.")
        _require_non_negative(
            active_routes=self.active_routes,
            users_travelling=self.users_travelling,
            recent_users=self.recent_users,
            enabled_accounts=self.enabled_accounts,
            active_stations=self.active_stations,
            inactive_stations=self.inactive_stations,
            active_lines=self.active_lines,
            active_segments=self.active_segments,
            trips_today=self.trips_today,
            trips_last_7_days=self.trips_last_7_days,
        )
        if self.trips_today > self.trips_last_7_days:
            raise ValueError("Volume do dia maior que o dos últimos 7 dias.")
        if len(self.ranking) > RANKING_LIMIT:
            raise ValueError("Ranking com mais de cinco estações.")
        uses = [item.uses for item in self.ranking]
        if uses != sorted(uses, reverse=True):
            raise ValueError("Ranking fora de ordem.")
