"""Coordenadas das estações usadas para sugerir a origem mais próxima."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


# Região metropolitana de São Paulo com folga; fora dela o registro é descartado.
LATITUDE_RANGE = (-24.1, -23.1)
LONGITUDE_RANGE = (-47.3, -45.9)


@dataclass(frozen=True, slots=True)
class StationCoordinate:
    station: str
    latitude: float
    longitude: float
    source: str
    collected_on: date

    def __post_init__(self) -> None:
        if not self.station.strip():
            raise ValueError("A estação é obrigatória.")
        if not self.source.strip():
            raise ValueError("A fonte é obrigatória.")
        if not LATITUDE_RANGE[0] <= self.latitude <= LATITUDE_RANGE[1]:
            raise ValueError("Latitude fora da região metropolitana.")
        if not LONGITUDE_RANGE[0] <= self.longitude <= LONGITUDE_RANGE[1]:
            raise ValueError("Longitude fora da região metropolitana.")
