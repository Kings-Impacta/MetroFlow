"""Testes dos modelos normalizados de planejamento."""

import unittest

from MetroFlow.planning.domain.models import (
    Line,
    Operator,
    RouteResult,
    Segment,
    Station,
    Transfer,
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

    def test_tempo_total_inclui_baldeacao(self) -> None:
        interchange = Station(id=12, name="Se", code="SE")
        next_line = Line(
            id=3,
            name="Linha 3 - Vermelha",
            code="L3",
            color="#EE3338",
            operator=self.line.operator,
        )
        segments = (
            Segment(
                id=20,
                origin=self.origin,
                destination=interchange,
                line=self.line,
                estimated_time_seconds=120,
            ),
            Segment(
                id=21,
                origin=interchange,
                destination=self.destination,
                line=next_line,
                estimated_time_seconds=120,
            ),
        )
        transfer = Transfer(
            station=interchange,
            previous_line=self.line,
            next_line=next_line,
        )

        route = RouteResult(
            origin=self.origin,
            destination=self.destination,
            stations=(self.origin, interchange, self.destination),
            segments=segments,
            transfers=(transfer,),
            total_time_seconds=840,
        )

        self.assertEqual(route.display_minutes, 14)
        self.assertEqual(route.transfer_count, 1)


if __name__ == "__main__":
    unittest.main()
