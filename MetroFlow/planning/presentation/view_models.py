"""Contrato publico do planejador, independente do formato bruto do Xano."""

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, model_validator

from MetroFlow.planning.domain.guidance import StationGuidance
from MetroFlow.planning.domain.models import (
    MAX_TRIP_SEGMENTS, CalibrationReference, RouteResult, Station, requires_train_change,
)


class RouteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    origin_id: StrictInt = Field(gt=0)
    destination_id: StrictInt = Field(gt=0)


class TripSegmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: StrictInt = Field(gt=0)
    origin_id: StrictInt = Field(gt=0)
    destination_id: StrictInt = Field(gt=0)


class CalibrationReferenceView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: StrictStr = Field(pattern=r"^[a-f0-9]{64}$")
    patterns: list[StrictStr] = Field(min_length=1, max_length=MAX_TRIP_SEGMENTS)

    def reference(self) -> CalibrationReference:
        return CalibrationReference(self.version, tuple(self.patterns))

    @model_validator(mode="after")
    def validate_reference(self):
        self.reference()
        return self


class TripConfirmationRequest(BaseModel):
    """Trechos do trajeto apresentado, na ordem e no sentido percorridos."""

    model_config = ConfigDict(extra="forbid")

    segments: list[TripSegmentRequest] = Field(
        min_length=1,
        max_length=MAX_TRIP_SEGMENTS,
    )
    calculated_at_ms: StrictInt | None = Field(default=None, gt=0)
    calibration: CalibrationReferenceView | None = None

    @model_validator(mode="after")
    def validate_calibration(self):
        if self.calibration is not None and (
            self.calculated_at_ms is None or len(self.calibration.patterns) != len(self.segments)
        ):
            raise ValueError("Referência de calibração incompleta.")
        return self

    def steps(self) -> list[tuple[int, int, int]]:
        return [
            (step.id, step.origin_id, step.destination_id)
            for step in self.segments
        ]


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


class GuidanceView(BaseModel):
    alighting_side: str | None = None
    note: str | None = None

    @classmethod
    def from_guidance(
        cls,
        guidance: StationGuidance,
    ) -> "GuidanceView":
        # Fonte e data ficam no cadastro; a resposta leva so a orientacao.
        return cls(
            alighting_side=guidance.alighting_side,
            note=guidance.note,
        )


class SegmentView(BaseModel):
    # Identificam o trecho e o sentido percorrido na confirmacao da viagem.
    id: int
    origin_id: int
    destination_id: int

    origin: str
    destination: str
    line: str
    operator: str

    # Sentido calculado pelo Xano.
    # Exemplo: Vila Madalena, Vila Prudente,
    # Jabaquara ou Tucuruvi.
    direction: str | None = None
    segment_type: str = "ferroviario"
    directed: bool = False
    service_id: int | None = None

    seconds: int
    wait_seconds: int = Field(default=0, ge=0, exclude_if=lambda value: value == 0)

    # Omitido da resposta quando nao ha orientacao ou a
    # funcionalidade foi desligada com METROFLOW_ORIENTACOES=0.
    guidance: GuidanceView | None = Field(
        default=None,
        exclude_if=lambda value: value is None,
    )


class RouteView(BaseModel):
    origin: str
    destination: str
    stations: list[str]

    seconds: int
    minutes: int

    transfer_count: int

    segments: list[SegmentView]
    transfers: list[str]
    wait_seconds: int = Field(default=0, ge=0, exclude_if=lambda value: value == 0)
    calculated_at_ms: int | None = Field(default=None, exclude_if=lambda value: value is None)
    notices: list[str] = Field(default_factory=list, exclude_if=lambda value: not value)
    calibration: CalibrationReferenceView | None = Field(default=None, exclude_if=lambda value: value is None)

    @model_validator(mode="after")
    def validate_calibration(self):
        if self.calibration is not None and (
            self.calculated_at_ms is None or len(self.calibration.patterns) != len(self.segments)
        ):
            raise ValueError("Referência de calibração incompleta.")
        return self

    @classmethod
    def from_route(
        cls,
        route: RouteResult,
        guidance: Mapping[int, StationGuidance] | None = None,
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
            if requires_train_change(previous, following)
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

            seconds=route.display_seconds,
            wait_seconds=route.waiting_time_seconds,
            calculated_at_ms=route.calculated_at_ms,
            calibration=CalibrationReferenceView(version=route.calibration.version, patterns=list(route.calibration.patterns)) if route.calibration else None,
            notices=list(route.notices),
            minutes=route.display_minutes,

            transfer_count=(
                route.transfer_count
            ),

            segments=[
                SegmentView(
                    id=step.id,
                    origin_id=step.origin.id,
                    destination_id=step.destination.id,
                    origin=step.origin.name,
                    destination=(
                        step.destination.name
                    ),
                    line=step.line.name,
                    operator=(
                        step.line.operator.name
                    ),
                    direction=step.direction,
                    segment_type=step.segment_type,
                    directed=step.directed,
                    service_id=step.service_id,
                    seconds=(
                        step.estimated_time_seconds
                    ),
                    wait_seconds=step.waiting_time_seconds,
                    guidance=(
                        GuidanceView.from_guidance(guidance[index])
                        if guidance and index in guidance
                        else None
                    ),
                )
                for index, step in enumerate(route.segments)
            ],

            transfers=[
                (
                    f"Em {change.station.name}: troque de trem na {change.next_line.name}"
                    if change.previous_line.id == change.next_line.id
                    else (
                        f"Em {change.station.name}: "
                        f"{change.previous_line.name} → "
                        f"{change.next_line.name}"
                    )
                )
                for change in route.transfers
            ],
        )
