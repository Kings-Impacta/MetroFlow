"""Contratos HTTP públicos do painel administrativo."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, StrictBool

from MetroFlow.admin.domain.models import AdminIndicators, AdminStation, StationStatus


class StationStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    active: StrictBool


class LineView(BaseModel):
    id: int
    name: str
    code: str
    color: str | None = None


class StationView(BaseModel):
    id: int
    name: str
    code: str
    active: bool
    lines: list[LineView]

    @classmethod
    def from_station(cls, station: AdminStation) -> "StationView":
        return cls(
            id=station.id,
            name=station.name,
            code=station.code,
            active=station.active,
            lines=[
                LineView(id=line.id, name=line.name, code=line.code, color=line.color)
                for line in station.lines
            ],
        )


class StationStatusView(BaseModel):
    id: int
    active: bool

    @classmethod
    def from_status(cls, status: StationStatus) -> "StationStatusView":
        return cls(id=status.id, active=status.active)


class UsageView(BaseModel):
    active_routes: int
    users_travelling: int
    recent_users: int
    enabled_accounts: int


class NetworkView(BaseModel):
    active_stations: int
    inactive_stations: int
    active_lines: int
    active_segments: int


class VolumeView(BaseModel):
    trips_today: int
    trips_last_7_days: int


class RankingItemView(BaseModel):
    id: int
    name: str
    code: str
    uses: int


class CrowdingView(BaseModel):
    crowded_segments: int | None
    minimum_users: int | None
    percentage: float | None


class IndicatorsView(BaseModel):
    computed_at_ms: int
    usage: UsageView
    network: NetworkView
    volume: VolumeView
    ranking: list[RankingItemView]
    crowding: CrowdingView

    @classmethod
    def from_indicators(cls, item: AdminIndicators) -> "IndicatorsView":
        return cls(
            computed_at_ms=item.computed_at_ms,
            usage=UsageView(
                active_routes=item.active_routes,
                users_travelling=item.users_travelling,
                recent_users=item.recent_users,
                enabled_accounts=item.enabled_accounts,
            ),
            network=NetworkView(
                active_stations=item.active_stations,
                inactive_stations=item.inactive_stations,
                active_lines=item.active_lines,
                active_segments=item.active_segments,
            ),
            volume=VolumeView(
                trips_today=item.trips_today,
                trips_last_7_days=item.trips_last_7_days,
            ),
            ranking=[
                RankingItemView(id=usage.id, name=usage.name, code=usage.code, uses=usage.uses)
                for usage in item.ranking
            ],
            crowding=CrowdingView(
                crowded_segments=item.crowding.crowded_segments,
                minimum_users=item.crowding.minimum_users,
                percentage=item.crowding.percentage,
            ),
        )
