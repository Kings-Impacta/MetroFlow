"""Leitura do cadastro local de coordenadas das estações, ligado por padrão."""

from __future__ import annotations

import csv
import logging
import math
import os
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path

from MetroFlow.planning.domain.guidance import normalize_name
from MetroFlow.planning.domain.location import StationCoordinate


logger = logging.getLogger(__name__)

LOCATION_ENV = "METROFLOW_LOCALIZACAO"

DEFAULT_COORDINATES_PATH = (
    Path(__file__).resolve().parents[3] / "docs" / "dados" / "coordenadas-estacoes.csv"
)

CSV_COLUMNS = ("estacao", "latitude", "longitude", "fonte", "data_coleta")


@dataclass(frozen=True, slots=True)
class CoordinatesLoad:
    # Chave: nome normalizado da estação.
    entries: Mapping[str, StationCoordinate]
    # Linha do arquivo e motivo, sem reproduzir o conteúdo.
    problems: tuple[tuple[int, str], ...]


def location_enabled(environ: Mapping[str, str] | None = None) -> bool:
    # Ligado por padrão; METROFLOW_LOCALIZACAO=0 desliga sem mudar código.
    if environ is None:
        environ = os.environ
    return environ.get(LOCATION_ENV, "").strip() != "0"


def _parse_row(row: Mapping[str, str | None]) -> StationCoordinate:
    def text(column: str) -> str:
        return (row.get(column) or "").strip()

    collected = text("data_coleta")
    if not collected:
        raise ValueError("A data de coleta é obrigatória.")
    try:
        latitude = float(text("latitude"))
        longitude = float(text("longitude"))
    except ValueError:
        raise ValueError("Latitude ou longitude inválida.") from None
    if not (math.isfinite(latitude) and math.isfinite(longitude)):
        raise ValueError("Latitude ou longitude inválida.")

    return StationCoordinate(
        station=text("estacao"),
        latitude=latitude,
        longitude=longitude,
        source=text("fonte"),
        collected_on=date.fromisoformat(collected),
    )


def load_coordinates(path: Path) -> CoordinatesLoad:
    """Lê o CSV descartando linhas inválidas; arquivo ausente vira cadastro vazio."""

    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != CSV_COLUMNS:
                return CoordinatesLoad({}, ((1, "Cabeçalho diferente do esperado."),))
            rows = [(reader.line_num, row) for row in reader]
    except (OSError, UnicodeDecodeError, csv.Error):
        return CoordinatesLoad({}, ((0, "Arquivo ausente ou ilegível."),))

    parsed: list[tuple[int, StationCoordinate]] = []
    problems: list[tuple[int, str]] = []
    for line_number, row in rows:
        if None in row:
            problems.append((line_number, "Quantidade de colunas inválida."))
            continue
        try:
            parsed.append((line_number, _parse_row(row)))
        except ValueError as error:
            problems.append((line_number, str(error)))

    # Estação repetida descarta todas as ocorrências para não sugerir posição ambígua.
    counts = Counter(normalize_name(entry.station) for _, entry in parsed)
    entries: dict[str, StationCoordinate] = {}
    for line_number, entry in parsed:
        key = normalize_name(entry.station)
        if counts[key] > 1:
            problems.append((line_number, "Estação repetida."))
        else:
            entries[key] = entry

    return CoordinatesLoad(entries, tuple(sorted(problems)))


@lru_cache(maxsize=1)
def cached_coordinates() -> Mapping[str, StationCoordinate]:
    """Lê o arquivo uma vez por processo; reinicie o servidor para recarregar."""

    result = load_coordinates(DEFAULT_COORDINATES_PATH)
    logger.info(
        "Coordenadas carregadas: %d válidas, %d descartadas.",
        len(result.entries),
        len(result.problems),
    )
    return result.entries


def station_coordinates(
    names: Iterable[str],
    environ: Mapping[str, str] | None = None,
) -> dict[str, StationCoordinate]:
    """Associa as estações da malha às coordenadas, por nome normalizado."""

    if not location_enabled(environ):
        return {}
    try:
        registry = cached_coordinates()
    except Exception:  # Falha nas coordenadas nunca bloqueia o planejamento.
        logger.warning("Coordenadas indisponíveis; lista segue sem localização.")
        return {}

    matched = {name: registry[normalize_name(name)]
               for name in names if normalize_name(name) in registry}
    unmatched = len(registry) - len({normalize_name(name) for name in matched})
    if unmatched:
        logger.info("Coordenadas sem estação correspondente: %d.", unmatched)
    return matched
