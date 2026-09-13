"""Testes dos casos de uso de planejamento."""

import unittest
from unittest.mock import MagicMock

from MetroFlow.planning.application.services import (
    InvalidRouteSelection,
    PlanningService,
)


class PlanningServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gateway = MagicMock()
        self.service = PlanningService(self.gateway)

    def test_rejeita_selecao_incompleta_sem_consultar_xano(self) -> None:
        with self.assertRaises(InvalidRouteSelection):
            self.service.plan_route(None, 2, "token")

        self.gateway.find_route.assert_not_called()

    def test_rejeita_origem_igual_ao_destino(self) -> None:
        with self.assertRaisesRegex(
            InvalidRouteSelection,
            "devem ser diferentes",
        ):
            self.service.plan_route(2, 2, "token")

        self.gateway.find_route.assert_not_called()

    def test_encaminha_consulta_valida(self) -> None:
        expected = object()
        self.gateway.find_route.return_value = expected

        result = self.service.plan_route(1, 2, "token")

        self.assertIs(result, expected)
        self.gateway.find_route.assert_called_once_with(1, 2, "token")


if __name__ == "__main__":
    unittest.main()
