"""Testes dos casos de uso de planejamento."""

import unittest
from unittest.mock import MagicMock

from MetroFlow.planning.application.services import (
    InvalidRouteSelection,
    InvalidTripConfirmation,
    PlanningService,
)
from MetroFlow.planning.domain.models import TripConfirmation, TripSegment


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

    def test_confirma_viagem_com_trechos_consecutivos(self) -> None:
        self.service.confirm_trip([(10, 1, 3), (11, 3, 2)], "token")

        self.gateway.confirm_trip.assert_called_once_with(
            TripConfirmation((TripSegment(10, 1, 3), TripSegment(11, 3, 2))),
            "token",
        )

    def test_rejeita_viagem_invalida_sem_consultar_xano(self) -> None:
        for steps in [
            [],
            [(10, 1, 3), (11, 2, 4)],
            [(10, 1, 1)],
            [(0, 1, 3)],
            [(10, 1, 3), (11, 3, 1)] * 101,
        ]:
            with self.subTest(steps=steps[:2]):
                with self.assertRaises(InvalidTripConfirmation):
                    self.service.confirm_trip(steps, "token")

        self.gateway.confirm_trip.assert_not_called()

    def test_confirmacao_exige_sessao(self) -> None:
        with self.assertRaises(ValueError):
            self.service.confirm_trip([(10, 1, 3)], "")

        self.gateway.confirm_trip.assert_not_called()


if __name__ == "__main__":
    unittest.main()
