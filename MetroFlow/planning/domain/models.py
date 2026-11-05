"""Modelos normalizados independentes do contrato bruto do Xano."""

from __future__ import annotations

from dataclasses import dataclass
import re


TRANSFER_TIME_SECONDS = 600
MAX_TRIP_SEGMENTS = 200


@dataclass(frozen=True, slots=True)
class CalibrationReference:
    """Identifica regras e padrões, sem aceitar tempos fornecidos pelo cliente."""

    version: str
    patterns: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.version, str) or not re.fullmatch(r"[a-f0-9]{64}", self.version):
            raise ValueError("Versão de calibração inválida.")
        if not isinstance(self.patterns, tuple) or not 1 <= len(self.patterns) <= MAX_TRIP_SEGMENTS or any(
            not isinstance(p, str) or not 1 <= len(p) <= 160
            or any(ord(c) < 32 or ord(c) == 127 for c in p) for p in self.patterns
        ):
            raise ValueError("Padrões de trem inválidos.")


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
    waiting_time_seconds: int = 0
    train_pattern: str | None = None
    transfer_before_seconds: int | None = None

    def __post_init__(self) -> None:
        if self.transfer_before_seconds is not None and (
            type(self.transfer_before_seconds) is not int or self.transfer_before_seconds < 0
        ):
            raise ValueError("Tempo de troca inválido.")
        if self.waiting_time_seconds < 0:
            raise ValueError("A espera estimada não pode ser negativa.")
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


def requires_train_change(previous: Segment, following: Segment) -> bool:
    """Reconhece também as trocas em Brooklin Paulista e na extensão de Itapevi."""
    if previous.line.id != following.line.id:
        return True
    # O corredor pode usar a identificação da linha de destino. Seu padrão
    # técnico difere do trem, sem criar outra baldeação na mesma linha.
    if previous.segment_type == "transferencia" or following.segment_type == "transferencia":
        return False
    if previous.train_pattern is not None and following.train_pattern is not None:
        return previous.train_pattern != following.train_pattern
    return bool(
        previous.line.code in {"L8", "L17"}
        and previous.direction
        and following.direction
        and previous.direction != following.direction
    )


@dataclass(frozen=True, slots=True)
class RouteResult:
    origin: Station
    destination: Station
    stations: tuple[Station, ...]
    segments: tuple[Segment, ...]
    transfers: tuple[Transfer, ...]
    total_time_seconds: int
    calculated_at_ms: int | None = None
    notices: tuple[str, ...] = ()
    calibration: CalibrationReference | None = None
    public_estimate_seconds: int | None = None

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

        transfer_total = len(self.transfers) * TRANSFER_TIME_SECONDS
        if self.calibration is not None:
            if self.calculated_at_ms is None or len(self.calibration.patterns) != len(self.segments):
                raise ValueError("Referência de calibração incompleta.")
            if tuple(s.train_pattern for s in self.segments) != self.calibration.patterns or any(
                s.transfer_before_seconds is None for s in self.segments
            ):
                raise ValueError("Cronologia calibrada incompleta.")
            if self.segments[0].transfer_before_seconds != 0:
                raise ValueError("Não há baldeação antes da origem.")
            for a, b in zip(self.segments, self.segments[1:]):
                if not requires_train_change(a, b) and b.transfer_before_seconds != 0:
                    raise ValueError("Troca sem mudança de trem.")
            transfer_total = sum(s.transfer_before_seconds for s in self.segments)
        elif any(s.transfer_before_seconds is not None or s.train_pattern is not None for s in self.segments):
            raise ValueError("Tempos calibrados exigem versão.")
        expected_total = (
            segment_total
            + transfer_total
            + self.waiting_time_seconds
        )

        if expected_total != self.total_time_seconds:
            raise ValueError(
                "O tempo total deve incluir os trechos e as baldeacoes."
            )
        if self.public_estimate_seconds is not None and self.public_estimate_seconds != expected_total + 60:
            raise ValueError("A estimativa pública deve incluir exatamente 60 segundos de margem.")

    @property
    def display_seconds(self) -> int:
        return self.total_time_seconds if self.public_estimate_seconds is None else self.public_estimate_seconds

    @property
    def waiting_time_seconds(self) -> int:
        return sum(segment.waiting_time_seconds for segment in self.segments)

    @property
    def transfer_count(self) -> int:
        return len(self.transfers)

    @property
    def display_minutes(self) -> int:
        return (
            self.display_seconds + 59
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
    calculated_at_ms: int | None = None
    calibration: CalibrationReference | None = None

    def __post_init__(self) -> None:
        if self.calibration is not None and (
            self.calculated_at_ms is None or len(self.calibration.patterns) != len(self.segments)
        ):
            raise ValueError("Referência da viagem incompleta.")
        if self.calculated_at_ms is not None and (
            isinstance(self.calculated_at_ms, bool)
            or not isinstance(self.calculated_at_ms, int)
            or self.calculated_at_ms <= 0
        ):
            raise ValueError("Instante da busca inválido.")
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
