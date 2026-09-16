"""Modelos normalizados independentes do contrato bruto do Xano."""

from __future__ import annotations

from dataclasses import dataclass


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

        if segment_total != self.total_time_seconds:
            raise ValueError(
                "O tempo total deve ser a soma dos trechos."
            )

    @property
    def transfer_count(self) -> int:
        return len(self.transfers)

    @property
    def display_minutes(self) -> int:
        return (
            self.total_time_seconds + 59
        ) // 60