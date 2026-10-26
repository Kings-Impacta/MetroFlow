"""Componentes do resultado do trajeto."""

import unittest

from MetroFlow.planning.presentation.pages import _result


class RouteResultTests(unittest.TestCase):
    def test_resultado_nao_exibe_confirmacao_ou_dados_de_lotacao(self):
        rendered = str(_result().render())

        self.assertNotIn("Confirmar viagem", rendered)
        self.assertNotIn("planning_state.confirm_trip", rendered)
        for forbidden in ("lotação", "lotado", "Lotação", "substituído", "alternativ"):
            self.assertNotIn(forbidden, rendered)
