"""Leitura do cadastro local de orientacoes e interruptor de ativacao."""

import tempfile
import unittest
from pathlib import Path

from MetroFlow.planning.infrastructure.guidance_csv import (
    CSV_COLUMNS, guidance_enabled, load_guidance,
)


HEADER = ",".join(CSV_COLUMNS)
VALID = 'Paraíso,Linha 1 - Azul,Jabaquara,Esquerdo,"Carro 4, perto da escada",campo,2026-10-25'


class GuidanceCsvTests(unittest.TestCase):
    def write(self, *lines, header=HEADER):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "orientacoes.csv"
        path.write_text("\n".join([header, *lines]) + "\n", encoding="utf-8")
        return path

    def test_registro_valido_e_carregado(self):
        result = load_guidance(self.write(VALID))
        self.assertEqual(result.problems, ())
        self.assertEqual(len(result.entries), 1)
        entry = result.entries[0]
        self.assertEqual((entry.alighting_side, entry.note), ("esquerdo", "Carro 4, perto da escada"))

    def test_registro_so_com_observacao_e_carregado(self):
        result = load_guidance(self.write("Sé,Linha 3 - Vermelha,Corinthians-Itaquera,,Siga a passarela,campo,2026-10-25"))
        self.assertEqual(result.problems, ())
        self.assertIsNone(result.entries[0].alighting_side)

    def test_linha_sem_orientacao_fica_pendente(self):
        result = load_guidance(self.write("Paraíso,Linha 1 - Azul,Jabaquara,,,,"))
        self.assertEqual((result.entries, result.pending, result.problems), ((), 1, ()))

    def test_linhas_invalidas_sao_descartadas_sem_afetar_as_demais(self):
        invalid = [
            "Sé,Linha 3 - Vermelha,Corinthians-Itaquera,frente,,campo,2026-10-25",
            f"Sé,Linha 3 - Vermelha,Palmeiras-Barra Funda,,{'x' * 201},campo,2026-10-25",
            "Sé,Linha 1 - Azul,Tucuruvi,direito,,,2026-10-25",
            "Luz,Linha 1 - Azul,Tucuruvi,direito,,campo,",
            "Luz,Linha 1 - Azul,Jabaquara,direito,,campo,25/10/2026",
            "Luz,Linha 1 - Azul,Jabaquara,direito,,campo,2026-10-25,extra",
        ]
        result = load_guidance(self.write(VALID, *invalid))
        self.assertEqual(len(result.entries), 1)
        self.assertEqual([line for line, _ in result.problems], list(range(3, 9)))

    def test_duplicatas_sao_descartadas_por_inteiro(self):
        duplicate = "paraiso,LINHA 1 - AZUL,jabaquara,direito,,campo,2026-10-26"
        result = load_guidance(self.write(VALID, duplicate))
        self.assertEqual(result.entries, ())
        self.assertEqual([reason for _, reason in result.problems], ["Registro duplicado."] * 2)

    def test_mesma_estacao_em_sentidos_diferentes_nao_e_duplicata(self):
        other_direction = "Paraíso,Linha 1 - Azul,Tucuruvi,direito,,campo,2026-10-25"
        self.assertEqual(len(load_guidance(self.write(VALID, other_direction)).entries), 2)

    def test_arquivo_ausente_ou_cabecalho_errado_vira_cadastro_vazio(self):
        missing = load_guidance(Path(tempfile.gettempdir()) / "nao-existe-metroflow.csv")
        self.assertEqual(missing.entries, ())
        wrong_header = load_guidance(self.write(VALID, header="estacao,linha"))
        self.assertEqual(wrong_header.entries, ())
        self.assertEqual(len(wrong_header.problems), 1)

    def test_interruptor_ligado_por_padrao_e_desligado_com_zero(self):
        self.assertTrue(guidance_enabled({}))
        for value in ["1", "true", ""]:
            with self.subTest(value=value):
                self.assertTrue(guidance_enabled({"METROFLOW_ORIENTACOES": value}))
        for value in ["0", " 0 "]:
            with self.subTest(value=value):
                self.assertFalse(guidance_enabled({"METROFLOW_ORIENTACOES": value}))


if __name__ == "__main__":
    unittest.main()
