"""Componentes do resultado do trajeto."""

import unittest

from MetroFlow.planning.presentation.pages import _confirm_trip_button, _result


class ConfirmTripButtonTests(unittest.TestCase):
    def test_botao_confirma_viagem_e_permanece_disponivel(self):
        rendered = _confirm_trip_button().render()
        props = " ".join(rendered["props"])

        self.assertEqual(rendered["children"], [{"contents": '"Confirmar viagem"'}])
        self.assertIn("planning_state.confirm_trip", props)
        for blocked in ("disabled", "loading"):
            self.assertNotIn(blocked, props)

    def test_resultado_inclui_botao_sem_dados_de_lotacao(self):
        rendered = str(_result().render())

        self.assertIn("planning_state.confirm_trip", rendered)
        for forbidden in ("lotação", "lotado", "Lotação", "substituído", "alternativ"):
            self.assertNotIn(forbidden, rendered)
