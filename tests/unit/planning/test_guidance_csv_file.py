"""Valida o cadastro versionado em docs/dados antes de usa-lo na aplicacao."""

import csv
import unittest

from MetroFlow.planning.infrastructure.guidance_csv import (
    CSV_COLUMNS, DEFAULT_GUIDANCE_PATH, load_guidance,
)


class GuidanceFileTests(unittest.TestCase):
    def test_cabecalho_do_arquivo_versionado(self):
        with DEFAULT_GUIDANCE_PATH.open(encoding="utf-8-sig", newline="") as handle:
            self.assertEqual(tuple(next(csv.reader(handle))), CSV_COLUMNS)

    def test_registros_preenchidos_sao_validos_e_unicos(self):
        result = load_guidance(DEFAULT_GUIDANCE_PATH)
        # Cada problema indica a linha do CSV e o motivo da recusa.
        self.assertEqual(result.problems, ())
        self.assertGreater(len(result.entries) + result.pending, 0)


if __name__ == "__main__":
    unittest.main()
