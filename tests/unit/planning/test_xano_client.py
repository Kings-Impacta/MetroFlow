"""Testes do adaptador Xano de planejamento."""

import json
import unittest

import httpx

from MetroFlow.planning.infrastructure.xano_client import (
    PlanningUnauthorized,
    XanoPlanningClient,
)


BASE_URL = "https://example.xano.io/api:planning"


def operator() -> dict[str, object]:
    return {"id": 1, "nome": "Metro SP", "codigo": "METRO"}


def line() -> dict[str, object]:
    return {
        "id": 2,
        "nome": "Linha 2 - Verde",
        "codigo": "L2",
        "cor": "#008061",
        "operador": operator(),
    }


def station(identifier: int, name: str, code: str) -> dict[str, object]:
    return {
        "id": identifier,
        "nome": name,
        "codigo": code,
        "linhas": [line()],
    }


class XanoPlanningClientTests(unittest.TestCase):
    def test_lista_estacoes_autenticada(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/api:planning/estacoes")
            self.assertEqual(request.headers["Authorization"], "Bearer token")
            return httpx.Response(
                200,
                json={"estacoes": [station(10, "Paraiso", "PAR")]},
            )

        with XanoPlanningClient(
            BASE_URL,
            transport=httpx.MockTransport(handler),
        ) as client:
            stations = client.list_active_stations("token")

        self.assertEqual(stations[0].name, "Paraiso")
        self.assertEqual(stations[0].lines[0].operator.name, "Metro SP")

    def test_busca_trajeto_normaliza_resposta(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/api:planning/trajetos/buscar")
            self.assertEqual(
                json.loads(request.content),
                {"estacao_origem_id": 10, "estacao_destino_id": 11},
            )
            return httpx.Response(
                200,
                json={
                    "estacao_origem_id": 10,
                    "estacao_destino_id": 11,
                    "estacoes": [
                        station(10, "Paraiso", "PAR"),
                        station(11, "Brigadeiro", "BRI"),
                    ],
                    "trechos": [
                        {
                            "id": 20,
                            "estacao_origem_id": 10,
                            "estacao_destino_id": 11,
                            "linha": line(),
                            "tempo_estimado": 120,
                        }
                    ],
                    "baldeacoes": [],
                    "tempo_total_segundos": 120,
                    "quantidade_baldeacoes": 0,
                },
            )

        with XanoPlanningClient(
            BASE_URL,
            transport=httpx.MockTransport(handler),
        ) as client:
            route = client.find_route(10, 11, "token")

        self.assertIsNotNone(route)
        assert route is not None
        self.assertEqual(route.total_time_seconds, 120)
        self.assertEqual(route.display_minutes, 2)

    def test_ausencia_de_trajeto_retorna_none(self) -> None:
        transport = httpx.MockTransport(
            lambda _: httpx.Response(404, json={"detail": "not found"})
        )
        with XanoPlanningClient(BASE_URL, transport=transport) as client:
            self.assertIsNone(client.find_route(10, 11, "token"))

    def test_sessao_invalida_e_diferenciada(self) -> None:
        transport = httpx.MockTransport(
            lambda _: httpx.Response(401, json={"detail": "unauthorized"})
        )
        with XanoPlanningClient(BASE_URL, transport=transport) as client:
            with self.assertRaises(PlanningUnauthorized):
                client.list_active_stations("token-invalido")


if __name__ == "__main__":
    unittest.main()
