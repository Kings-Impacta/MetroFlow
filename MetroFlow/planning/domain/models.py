"""Modelos normalizados independentes do contrato bruto do Xano."""

from __future__ import annotations

from dataclasses import dataclass


TRANSFER_TIME_SECONDS = 600
MAX_TRIP_SEGMENTS = 200


@dataclass(frozen=True, slots=True)
class Operator:
    id: int
    name: str
    code: str


@dataclass(frozen=True, slots=True)
class Line:
    id: int
    name: str
    code: str
    color: str | None
    operator: Operator


@dataclass(frozen=True, slots=True)
class Station:
    id: int
    name: str
    code: str
    lines: tuple[Line, ...] = ()


@dataclass(frozen=True, slots=True)
class Segment:
    id: int
    origin: Station
    destination: Station
    line: Line
    estimated_time_seconds: int

    # Sentido real calculado pelo backend.
    # Exemplo: "Vila Madalena", "Vila Prudente",
    # "Jabaquara" ou "Tucuruvi".
    direction: str | None = None
    segment_type: str = "ferroviario"
    directed: bool = False
    service_id: int | None = None

    def __post_init__(self) -> None:
        if self.estimated_time_seconds <= 0:
            raise ValueError(
                "O tempo estimado deve ser positivo."
            )

        if self.origin.id == self.destination.id:
            raise ValueError(
                "Um trecho deve ligar estacoes diferentes."
            )

        if (
            self.direction is not None
            and not self.direction.strip()
        ):
            raise ValueError(
                "O sentido do trecho nao pode ser vazio."
            )

        if not self.segment_type.strip():
            raise ValueError("O tipo do trecho nao pode ser vazio.")


@dataclass(frozen=True, slots=True)
class Transfer:
    station: Station
    previous_line: Line
    next_line: Line


@dataclass(frozen=True, slots=True)
class RouteResult:
    origin: Station
    destination: Station
    stations: tuple[Station, ...]
    segments: tuple[Segment, ...]
    transfers: tuple[Transfer, ...]
    total_time_seconds: int

    def __post_init__(self) -> None:
        if self.origin.id == self.destination.id:
            raise ValueError(
                "Origem e destino devem ser diferentes."
            )

        if self.total_time_seconds <= 0:
            raise ValueError(
                "O tempo total deve ser positivo."
            )

        segment_total = sum(
            segment.estimated_time_seconds
            for segment in self.segments
        )

        expected_total = (
            segment_total
            + len(self.transfers) * TRANSFER_TIME_SECONDS
        )

        if expected_total != self.total_time_seconds:
            raise ValueError(
                "O tempo total deve incluir os trechos e as baldeacoes."
            )

    @property
    def transfer_count(self) -> int:
        return len(self.transfers)

    @property
    def display_minutes(self) -> int:
        return (
            self.total_time_seconds + 59
        ) // 60


@dataclass(frozen=True, slots=True)
class TripSegment:
    """Trecho de uma viagem confirmada, no sentido em que foi percorrido."""

    segment_id: int
    origin_id: int
    destination_id: int

    def __post_init__(self) -> None:
        if min(
            self.segment_id,
            self.origin_id,
            self.destination_id,
        ) <= 0:
            raise ValueError(
                "Os identificadores do trecho devem ser positivos."
            )

        if self.origin_id == self.destination_id:
            raise ValueError(
                "Um trecho deve ligar estacoes diferentes."
            )


@dataclass(frozen=True, slots=True)
class TripConfirmation:
    """Viagem apresentada que o usuario confirmou que vai fazer."""

    segments: tuple[TripSegment, ...]

    def __post_init__(self) -> None:
        if not self.segments:
            raise ValueError(
                "A viagem deve ter ao menos um trecho."
            )

        if len(self.segments) > MAX_TRIP_SEGMENTS:
            raise ValueError(
                "A viagem possui trechos demais."
            )

        for previous, following in zip(
            self.segments,
            self.segments[1:],
        ):
            if previous.destination_id != following.origin_id:
                raise ValueError(
                    "Os trechos da viagem devem ser consecutivos."
                )
