"""Orientacoes: validacao do modelo e associacao as etapas do trajeto."""

import unittest
from datetime import date

from MetroFlow.planning.application.guidance import match_guidance
from MetroFlow.planning.domain.guidance import StationGuidance, normalize_name
from MetroFlow.planning.domain.models import Line, Operator, RouteResult, Segment, Station, Transfer


OPERATOR = Operator(1, "Metro", "M")
L8 = Line(8, "Linha 8 - Diamante", "L8", None, OPERATOR)
L3 = Line(3, "Linha 3 - Vermelha", "L3", None, OPERATOR)
WALK = Line(99, "Integração", "INT", None, OPERATOR)

LAPA = Station(1, "Lapa", "LAP")
BARRA_FUNDA = Station(2, "Palmeiras-Barra Funda", "PBF")
MARECHAL = Station(3, "Marechal Deodoro", "MDE")
SANTA_CECILIA = Station(4, "Santa Cecília", "SCE")


def guidance(**overrides):
    values = {
        "station": "Palmeiras-Barra Funda",
        "line": "Linha 8 - Diamante",
        "direction": "Júlio Prestes",
        "source": "observação em campo",
        "collected_on": date(2026, 10, 25),
        "alighting_side": "esquerdo",
    }
    values.update(overrides)
    return StationGuidance(**values)


def route_with_transfer():
    segments = (
        Segment(1, LAPA, BARRA_FUNDA, L8, 300, direction="Júlio Prestes"),
        Segment(2, BARRA_FUNDA, MARECHAL, L3, 120, direction="Corinthians-Itaquera"),
        Segment(3, MARECHAL, SANTA_CECILIA, L3, 120, direction="Corinthians-Itaquera"),
    )
    return RouteResult(
        LAPA, SANTA_CECILIA, (LAPA, BARRA_FUNDA, MARECHAL, SANTA_CECILIA),
        segments, (Transfer(BARRA_FUNDA, L8, L3),), 1140,
    )


class StationGuidanceTests(unittest.TestCase):
    def test_registro_com_lado_e_observacao_e_aceito(self):
        entry = guidance(note="Desça no carro 6, perto da escada rolante.")
        self.assertEqual((entry.alighting_side, entry.note[:9]), ("esquerdo", "Desça no "))

    def test_registro_so_com_observacao_e_aceito(self):
        self.assertIsNone(guidance(alighting_side=None, note="Siga a passarela").alighting_side)

    def test_campos_obrigatorios_e_valores_invalidos_sao_rejeitados(self):
        invalid = [
            {"source": " "},
            {"station": ""},
            {"alighting_side": "frente"},
            {"note": "  "},
            {"note": "x" * 201},
            {"alighting_side": None},
        ]
        for overrides in invalid:
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                guidance(**overrides)

    def test_observacao_no_limite_e_aceita(self):
        self.assertEqual(len(guidance(note="x" * 200).note), 200)

    def test_normalizacao_ignora_acentos_caixa_e_hifens(self):
        self.assertEqual(normalize_name(" Linha 3 – VERMELHA "), normalize_name("linha 3 - Vermelha"))
        self.assertEqual(normalize_name("Paraíso"), normalize_name("paraiso"))


class MatchGuidanceTests(unittest.TestCase):
    def test_destino_recebe_orientacao_da_estacao_linha_e_sentido(self):
        exit_entry = guidance(
            station="Santa Cecília", line="Linha 3 - Vermelha",
            direction="corinthians itaquera", note="Saída Rua Ana Cintra",
        )
        self.assertEqual(match_guidance(route_with_transfer(), [exit_entry]), {2: exit_entry})

    def test_baldeacao_recebe_orientacao_da_estacao_de_descida(self):
        transfer_entry = guidance(note="Siga as placas da Linha 3 pela passarela")
        self.assertEqual(match_guidance(route_with_transfer(), [transfer_entry]), {0: transfer_entry})

    def test_sentido_oposto_nao_e_associado(self):
        opposite = guidance(direction="Amador Bueno")
        self.assertEqual(match_guidance(route_with_transfer(), [opposite]), {})

    def test_trecho_intermediario_da_mesma_linha_nao_recebe_orientacao(self):
        middle = guidance(station="Marechal Deodoro", line="Linha 3 - Vermelha", direction="Corinthians-Itaquera")
        self.assertEqual(match_guidance(route_with_transfer(), [middle]), {})

    def test_integracao_a_pe_nao_recebe_orientacao(self):
        segments = (
            Segment(1, LAPA, BARRA_FUNDA, L8, 300, direction="Júlio Prestes"),
            Segment(2, BARRA_FUNDA, MARECHAL, WALK, 240, segment_type="transferencia"),
        )
        route = RouteResult(
            LAPA, MARECHAL, (LAPA, BARRA_FUNDA, MARECHAL), segments,
            (Transfer(BARRA_FUNDA, L8, WALK),), 1140,
        )
        walk_entry = guidance(station="Marechal Deodoro", line="Integração", direction="Júlio Prestes")
        alighting = guidance(note="Siga para a integração")
        self.assertEqual(match_guidance(route, [walk_entry, alighting]), {0: alighting})

    def test_sem_cadastro_nao_altera_o_trajeto(self):
        route = route_with_transfer()
        self.assertEqual(match_guidance(route, []), {})
        self.assertEqual(route.total_time_seconds, 1140)


if __name__ == "__main__":
    unittest.main()
