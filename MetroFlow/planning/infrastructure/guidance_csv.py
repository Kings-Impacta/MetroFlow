"""Leitura do cadastro local de orientacoes, ligado por padrao."""

from __future__ import annotations

import csv
import logging
import os
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path

from MetroFlow.planning.domain.guidance import StationGuidance


logger = logging.getLogger(__name__)

GUIDANCE_ENV = "METROFLOW_ORIENTACOES"

DEFAULT_GUIDANCE_PATH = (
    Path(__file__).resolve().parents[3] / "docs" / "dados" / "orientacoes-estacoes.csv"
)

CSV_COLUMNS = (
    "estacao",
    "linha",
    "sentido",
    "lado_desembarque",
    "observacao",
    "fonte",
    "data_coleta",
)

GUIDANCE_COLUMNS = (
    "lado_desembarque",
    "observacao",
)


@dataclass(frozen=True, slots=True)
class GuidanceLoad:
    entries: tuple[StationGuidance, ...]
    # Linhas sem nenhum campo de orientacao: aguardam a coleta.
    pending: int
    # Linha do arquivo e motivo, sem reproduzir o conteudo.
    problems: tuple[tuple[int, str], ...]


def guidance_enabled(environ: Mapping[str, str] | None = None) -> bool:
    # Ligado por padrao; METROFLOW_ORIENTACOES=0 desliga sem mudar codigo.
    if environ is None:
        environ = os.environ
    return environ.get(GUIDANCE_ENV, "").strip() != "0"


def _optional(row: Mapping[str, str | None], column: str) -> str | None:
    value = (row.get(column) or "").strip()
    return value or None


def _parse_row(row: Mapping[str, str | None]) -> StationGuidance:
    collected = _optional(row, "data_coleta")
    if collected is None:
        raise ValueError("A data de coleta e obrigatoria.")

    side = _optional(row, "lado_desembarque")

    return StationGuidance(
        station=_optional(row, "estacao") or "",
        line=_optional(row, "linha") or "",
        direction=_optional(row, "sentido") or "",
        alighting_side=side.casefold() if side else None,
        note=_optional(row, "observacao"),
        source=_optional(row, "fonte") or "",
        collected_on=date.fromisoformat(collected),
    )


def load_guidance(path: Path) -> GuidanceLoad:
    """Le o CSV descartando linhas invalidas; arquivo ausente vira cadastro vazio."""

    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != CSV_COLUMNS:
                return GuidanceLoad((), 0, ((1, "Cabecalho diferente do esperado."),))
            rows = [(reader.line_num, row) for row in reader]
    except (OSError, UnicodeDecodeError, csv.Error):
        return GuidanceLoad((), 0, ((0, "Arquivo ausente ou ilegivel."),))

    parsed: list[tuple[int, StationGuidance]] = []
    problems: list[tuple[int, str]] = []
    pending = 0

    for line_number, row in rows:
        if None in row:
            problems.append((line_number, "Quantidade de colunas invalida."))
            continue
        if not any(_optional(row, column) for column in GUIDANCE_COLUMNS):
            pending += 1
            continue
        try:
            parsed.append((line_number, _parse_row(row)))
        except ValueError as error:
            problems.append((line_number, str(error)))

    counts = Counter(entry.key for _, entry in parsed)
    entries: list[StationGuidance] = []
    for line_number, entry in parsed:
        if counts[entry.key] > 1:
            problems.append((line_number, "Registro duplicado."))
        else:
            entries.append(entry)

    return GuidanceLoad(tuple(entries), pending, tuple(sorted(problems)))


@lru_cache(maxsize=1)
def cached_guidance() -> tuple[StationGuidance, ...]:
    """Le o arquivo uma vez por processo; reinicie o servidor para recarregar."""

    result = load_guidance(DEFAULT_GUIDANCE_PATH)
    logger.info(
        "Orientacoes carregadas: %d validas, %d pendentes, %d descartadas.",
        len(result.entries),
        result.pending,
        len(result.problems),
    )
    return result.entries
