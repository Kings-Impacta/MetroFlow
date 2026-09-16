"""Contrato publico do planejador, independente do formato bruto do Xano."""

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from MetroFlow.planning.domain.models import RouteResult, Station


class RouteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    origin_id: StrictInt = Field(gt=0)
    destination_id: StrictInt = Field(gt=0)


class StationChoice(BaseModel):
    id: int
    name: str
    label: str

    @classmethod
    def from_station(
        cls,
        station: Station,
    ) -> "StationChoice":
        lines = " / ".join(
            (
                f"{line.name} — "
                f"{line.operator.name}"
            )
            for line in station.lines
        )

        return cls(
            id=station.id,
            name=station.name,
            label=(
                f"{station.name} · {lines}"
                if lines
                else station.name
            ),
        )


class SegmentView(BaseModel):
    origin: str
    destination: str
    line: str
    operator: str

    # Sentido calculado pelo Xano.
    # Exemplo: Vila Madalena, Vila Prudente,
    # Jabaquara ou Tucuruvi.
    direction: str | None = None

    seconds: int


class RouteView(BaseModel):
    origin: str
    destination: str
    stations: list[str]

    seconds: int
    minutes: int

    transfer_count: int

    segments: list[SegmentView]
    transfers: list[str]

    @classmethod
    def from_route(
        cls,
        route: RouteResult,
    ) -> "RouteView":
        if (
            not route.stations
            or not route.segments
            or route.stations[0].id
            != route.origin.id
            or route.stations[-1].id
            != route.destination.id
        ):
            raise ValueError(
                "Extremos da rota inconsistentes."
            )

        expected_steps = [
            (a.id, b.id)
            for a, b in zip(
                route.stations,
                route.stations[1:],
            )
        ]

        if [
            (
                step.origin.id,
                step.destination.id,
            )
            for step in route.segments
        ] != expected_steps:
            raise ValueError(
                "Sequencia de trechos inconsistente."
            )

        expected_transfers = [
            (
                previous.destination.id,
                previous.line.id,
                following.line.id,
            )
            for previous, following in zip(
                route.segments,
                route.segments[1:],
            )
            if previous.line.id
            != following.line.id
        ]

        if [
            (
                change.station.id,
                change.previous_line.id,
                change.next_line.id,
            )
            for change in route.transfers
        ] != expected_transfers:
            raise ValueError(
                "Baldeacoes inconsistentes."
            )

        return cls(
            origin=route.origin.name,
            destination=route.destination.name,

            stations=[
                station.name
                for station in route.stations
            ],

            seconds=route.total_time_seconds,
            minutes=route.display_minutes,

            transfer_count=(
                route.transfer_count
            ),

            segments=[
                SegmentView(
                    origin=step.origin.name,
                    destination=(
                        step.destination.name
                    ),
                    line=step.line.name,
                    operator=(
                        step.line.operator.name
                    ),
                    direction=step.direction,
                    seconds=(
                        step.estimated_time_seconds
                    ),
                )
                for step in route.segments
            ],

            transfers=[
                (
                    f"Em {change.station.name}: "
                    f"{change.previous_line.name} → "
                    f"{change.next_line.name}"
                )
                for change in route.transfers
            ],
        )