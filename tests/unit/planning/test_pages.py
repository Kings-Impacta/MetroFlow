"""Componentes do resultado do trajeto."""

import unittest

from MetroFlow.planning.presentation.pages import _confirm_trip_button, _result


def _find(node, predicate):
    """Primeiro componente renderizado que satisfaz o predicado, inclusive em ramos de rx.cond."""
    if isinstance(node, dict) and predicate(node):
        return node
    children = node.values() if isinstance(node, dict) else node if isinstance(node, list) else []
    for child in children:
        found = _find(child, predicate)
        if found is not None:
            return found
    return None


class ConfirmTripButtonTests(unittest.TestCase):
    def setUp(self):
        self.rendered = _confirm_trip_button().render()
        self.button = _find(
            self.rendered, lambda node: "planning_state.confirm_trip" in " ".join(node.get("props", []))
        )

    def test_botao_alterna_entre_confirmar_e_viagem_confirmada(self):
        self.assertIsNotNone(self.button)
        text = str(self.button)
        for expected in ('"Confirmar viagem"', '"Viagem confirmada"', "trip_status"):
            self.assertIn(expected, text)

    def test_botao_desativa_durante_envio_e_apos_confirmar(self):
        props = " ".join(self.button["props"])
        for prop in ("disabled:", "loading:"):
            self.assertIn(prop, props)
        self.assertIn('"loading"', props)
        self.assertIn('"confirmed"', props)

    def test_falha_exibe_mensagem_de_erro(self):
        alert = _find(self.rendered, lambda node: 'role:"alert"' in " ".join(node.get("props", [])))
        self.assertIsNotNone(alert)
        self.assertIn("trip_message", str(alert))

    def test_resultado_inclui_botao_sem_dados_de_lotacao(self):
        rendered = str(_result().render())

        self.assertIn("planning_state.confirm_trip", rendered)
        for forbidden in ("lotação", "lotado", "Lotação", "substituído", "alternativ"):
            self.assertNotIn(forbidden, rendered)
