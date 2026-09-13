"""Testes dos modelos normalizados de planejamento."""

import unittest

from MetroFlow.planning.domain.models import (
    Line,
    Operator,
    RouteResult,
    Segment,
    Station,
)


class PlanningModelsTests(unittest.TestCase):
    def setUp(self) -> None:
        operator = Operator(id=1, name="Metro SP", code="METRO")
        self.line = Line(
            id=2,
            name="Linha 2 - Verde",
            code="L2",
            color="#008061",
            operator=operator,
        )
        self.origin = Station(id=10, name="Paraiso", code="PAR")
        self.destination = Station(id=11, name="Brigadeiro", code="BRI")

    def test_tempo_total_e_soma_dos_trechos(self) -> None:
        segment = Segment(
            id=20,
            origin=self.origin,
            destination=self.destination,
            line=self.line,
            estimated_time_seconds=120,
        )

        route = RouteResult(
            origin=self.origin,
            destination=self.destination,
            stations=(self.origin, self.destination),
            segments=(segment,),
            transfers=(),
            total_time_seconds=120,
        )

        self.assertEqual(route.display_minutes, 2)
        self.assertEqual(route.transfer_count, 0)

    def test_rejeita_tempo_total_diferente_da_soma(self) -> None:
        segment = Segment(
            id=20,
            origin=self.origin,
            destination=self.destination,
            line=self.line,
            estimated_time_seconds=120,
        )

        with self.assertRaises(ValueError):
            RouteResult(
                origin=self.origin,
                destination=self.destination,
                stations=(self.origin, self.destination),
                segments=(segment,),
                transfers=(),
                total_time_seconds=60,
            )


if __name__ == "__main__":
    unittest.main()
