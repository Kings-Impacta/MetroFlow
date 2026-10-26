"""Orientacoes de desembarque por estacao, linha e sentido de chegada."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date


ALIGHTING_SIDES = frozenset({"esquerdo", "direito", "ambos"})
NOTE_MAX_LENGTH = 200


def normalize_name(value: str) -> str:
    """Compara nomes sem acentos, caixa ou variacoes de espacos e hifens."""

    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    unified = re.sub(r"[\s\-–—]+", " ", without_accents)
    return unified.strip().casefold()


@dataclass(frozen=True, slots=True)
class StationGuidance:
    station: str
    line: str
    direction: str
    source: str
    collected_on: date

    # Informacao principal.
    alighting_side: str | None = None
    # Qualquer outra dica relevante ao descer nesta estacao.
    note: str | None = None

    def __post_init__(self) -> None:
        for name in ("station", "line", "direction", "source"):
            if not getattr(self, name).strip():
                raise ValueError(f"O campo {name} e obrigatorio.")

        if (
            self.alighting_side is not None
            and self.alighting_side not in ALIGHTING_SIDES
        ):
            raise ValueError("Lado de desembarque invalido.")

        if self.note is not None:
            if not self.note.strip():
                raise ValueError("A observacao nao pode ser vazia.")
            if len(self.note) > NOTE_MAX_LENGTH:
                raise ValueError(
                    f"A observacao deve ter ate {NOTE_MAX_LENGTH} caracteres."
                )

        if self.alighting_side is None and self.note is None:
            raise ValueError("Informe o lado de desembarque ou a observacao.")

    @property
    def key(self) -> tuple[str, str, str]:
        return (
            normalize_name(self.station),
            normalize_name(self.line),
            normalize_name(self.direction),
        )
