"""Cadastro local de coordenadas das estações e interruptor da localização."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from MetroFlow.planning.domain.guidance import normalize_name
from MetroFlow.planning.infrastructure.coordinates_csv import (
    CSV_COLUMNS, DEFAULT_COORDINATES_PATH, load_coordinates, location_enabled,
    station_coordinates,
)


HEADER = ",".join(CSV_COLUMNS)
PARAISO = "Paraíso,-23.575386,-46.640960,OpenStreetMap node/1 (ODbL),2026-11-16"
COVERAGE = Path(DEFAULT_COORDINATES_PATH).parent / "tempos" / "cobertura" / "cobertura-deslocamentos.json"


class CoordinatesCsvTests(unittest.TestCase):
    def write(self, *lines, header=HEADER):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "coordenadas.csv"
        path.write_text("\n".join([header, *lines]) + "\n", encoding="utf-8")
        return path

    def test_registro_valido_e_carregado(self):
        result = load_coordinates(self.write(PARAISO))
        self.assertEqual(result.problems, ())
        entry = result.entries[normalize_name("Paraíso")]
        self.assertEqual((entry.latitude, entry.longitude), (-23.575386, -46.64096))

    def test_registros_invalidos_sao_descartados_sem_afetar_os_demais(self):
        result = load_coordinates(self.write(
            PARAISO,
            "Fora,-22.9,-43.2,fonte,2026-11-16",
            "Sem fonte,-23.5,-46.6,,2026-11-16",
            "Sem data,-23.5,-46.6,fonte,",
            "Texto,abc,-46.6,fonte,2026-11-16",
            "Infinito,nan,-46.6,fonte,2026-11-16",
            ",-23.5,-46.6,fonte,2026-11-16",
            "Colunas,-23.5,-46.6,fonte,2026-11-16,extra",
        ))
        self.assertEqual(list(result.entries), [normalize_name("Paraíso")])
        self.assertEqual([line for line, _ in result.problems], [3, 4, 5, 6, 7, 8, 9])

    def test_estacao_repetida_descarta_todas_as_ocorrencias(self):
        result = load_coordinates(self.write(
            PARAISO, "PARAISO,-23.57,-46.64,outra fonte,2026-11-16"))
        self.assertEqual(result.entries, {})
        self.assertEqual([reason for _, reason in result.problems], ["Estação repetida."] * 2)

    def test_arquivo_ausente_ou_cabecalho_diferente_vira_cadastro_vazio(self):
        missing = load_coordinates(Path(tempfile.gettempdir()) / "nao-existe-metroflow.csv")
        self.assertEqual(missing.entries, {})
        other = load_coordinates(self.write(PARAISO, header="nome,lat,lon,fonte,data"))
        self.assertEqual(other.entries, {})

    def test_interruptor_ligado_por_padrao_e_desligado_com_zero(self):
        self.assertTrue(location_enabled({}))
        self.assertTrue(location_enabled({"METROFLOW_LOCALIZACAO": "1"}))
        self.assertFalse(location_enabled({"METROFLOW_LOCALIZACAO": " 0 "}))

    def test_associacao_por_nome_normalizado_e_desligamento(self):
        entries = load_coordinates(self.write(PARAISO)).entries
        with patch("MetroFlow.planning.infrastructure.coordinates_csv.cached_coordinates",
                   return_value=entries):
            matched = station_coordinates(["PARAISO", "Vergueiro"], {})
            self.assertEqual(list(matched), ["PARAISO"])
            self.assertEqual(station_coordinates(["Paraíso"], {"METROFLOW_LOCALIZACAO": "0"}), {})

    def test_falha_na_leitura_nao_bloqueia(self):
        with patch("MetroFlow.planning.infrastructure.coordinates_csv.cached_coordinates",
                   side_effect=RuntimeError("falha simulada")):
            self.assertEqual(station_coordinates(["Paraíso"], {}), {})


class CoordinatesFileTests(unittest.TestCase):
    def test_arquivo_versionado_e_valido_e_cobre_a_malha(self):
        result = load_coordinates(DEFAULT_COORDINATES_PATH)
        self.assertEqual(result.problems, ())
        coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
        names = {item[key] for item in coverage for key in ("origem", "destino")}
        missing = sorted(name for name in names if normalize_name(name) not in result.entries)
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
