"""Fronteira HTTP: autenticacao, entradas e contrato publico do planejador."""

import unittest
from datetime import date
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from MetroFlow.auth.infrastructure.session_cookie import SESSION_COOKIE_NAME
from MetroFlow.auth.infrastructure.xano_client import XanoAuthRejected
from MetroFlow.planning.domain.guidance import StationGuidance
from MetroFlow.planning.domain.models import Line, Operator, RouteResult, Segment, Station, Transfer
from MetroFlow.planning.domain.models import TripConfirmation, TripSegment
from MetroFlow.planning.infrastructure.xano_client import PlanningError, PlanningUnauthorized, PlanningUnavailable
from MetroFlow.planning.presentation.api import planning_api

TRIP = {"segments": [
    {"id": 10, "origin_id": 1, "destination_id": 3},
    {"id": 11, "origin_id": 3, "destination_id": 2},
]}


class PlanningApiTests(unittest.TestCase):
    def setUp(self):
        app = FastAPI()
        app.include_router(planning_api)
        self.browser = TestClient(app)
        self.addCleanup(self.browser.close)
        self.browser.cookies.set(SESSION_COOKIE_NAME, "private-test-token")
        self.auth = MagicMock()
        self.auth.__enter__.return_value = self.auth
        self.gateway = MagicMock()
        self.gateway.__enter__.return_value = self.gateway
        for name, client in [("XanoAuthClient", self.auth), ("XanoPlanningClient", self.gateway)]:
            mocked = patch(f"MetroFlow.planning.presentation.api.{name}.from_environment", return_value=client)
            mocked.start()
            self.addCleanup(mocked.stop)
        line = Line(1, "Linha Azul", "L1", "#00f", Operator(1, "Metro", "M"))
        self.origin = Station(1, "Vergueiro", "VER", (line,))
        self.destination = Station(2, "Paraiso", "PAR", (line,))
        self.gateway.list_active_stations.return_value = (self.origin, self.destination)
        self.gateway.find_route.return_value = RouteResult(
            self.origin, self.destination, (self.origin, self.destination),
            (Segment(1, self.origin, self.destination, line, 120),), (), 120,
        )

    def test_estacoes_ordenadas_e_operador_no_rotulo(self):
        response = self.browser.get("/api/planning/stations")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["name"] for item in response.json()], ["Paraiso", "Vergueiro"])
        self.assertIn("Metro", response.json()[0]["label"])
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertNotIn("private-test-token", response.text)
        self.auth.me.assert_called_once_with("private-test-token")

    def test_sem_cookie_nao_consulta_xano(self):
        self.browser.cookies.clear()
        response = self.browser.get("/api/planning/stations")
        self.assertEqual(response.status_code, 401)
        self.auth.me.assert_not_called()
        self.gateway.list_active_stations.assert_not_called()

    def test_rota_sem_cookie_nao_consulta_xano(self):
        self.browser.cookies.clear()
        response = self.browser.post(
            "/api/planning/route",
            json={"origin_id": 1, "destination_id": 2},
        )
        self.assertEqual(response.status_code, 401)
        self.auth.me.assert_not_called()
        self.gateway.find_route.assert_not_called()

    def test_sessao_expirada_e_rejeitada_pelo_endpoint_de_planejamento(self):
        self.auth.me.side_effect = XanoAuthRejected("expired", 401)
        response = self.browser.post("/api/planning/route", json={"origin_id": 1, "destination_id": 2})
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("private-test-token", response.text)
        self.auth.me.assert_called_once_with("private-test-token")
        self.gateway.find_route.assert_not_called()

    def test_rota_retorna_tempo_operador_e_estacoes(self):
        response = self.browser.post("/api/planning/route", json={"origin_id": 1, "destination_id": 2})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["stations"], ["Vergueiro", "Paraiso"])
        self.assertEqual((body["seconds"], body["minutes"], body["transfer_count"]), (120, 2, 0))
        self.assertEqual(body["segments"][0]["operator"], "Metro")
        self.assertEqual(
            (body["segments"][0]["id"], body["segments"][0]["origin_id"], body["segments"][0]["destination_id"]),
            (1, 1, 2),
        )
        self.assertNotIn("private-test-token", response.text)
        self.auth.me.assert_called_once_with("private-test-token")
        self.gateway.find_route.assert_called_once_with(1, 2, "private-test-token")

    def test_extremos_iguais_rejeitados_antes_da_busca(self):
        response = self.browser.post("/api/planning/route", json={"origin_id": 1, "destination_id": 1})
        self.assertEqual(response.status_code, 400)
        self.gateway.find_route.assert_not_called()

    def test_ids_invalidos_rejeitados(self):
        for invalid in [None, 0, -1, True, "1", 1.5]:
            with self.subTest(value=invalid):
                response = self.browser.post("/api/planning/route", json={"origin_id": invalid, "destination_id": 2})
                self.assertEqual(response.status_code, 422)
        self.gateway.find_route.assert_not_called()

    def test_sem_rota_retorna_404(self):
        self.gateway.find_route.return_value = None
        response = self.browser.post("/api/planning/route", json={"origin_id": 1, "destination_id": 2})
        self.assertEqual(response.status_code, 404)

    def test_falha_de_servico_nao_expoe_mensagem_interna(self):
        self.gateway.find_route.side_effect = PlanningUnavailable("internal-secret")
        response = self.browser.post("/api/planning/route", json={"origin_id": 1, "destination_id": 2})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("internal-secret", response.text)

    def test_contrato_invalido_retorna_502(self):
        self.gateway.find_route.side_effect = ValueError("internal-payload")
        response = self.browser.post("/api/planning/route", json={"origin_id": 1, "destination_id": 2})
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("internal-payload", response.text)

    def test_rota_com_baldeacao_e_operadores(self):
        other_line = Line(2, "Linha Verde", "L2", None, Operator(2, "Outro operador", "O"))
        middle = Station(3, "Intermediaria", "INT")
        first_line = self.origin.lines[0]
        self.gateway.find_route.return_value = RouteResult(
            self.origin, self.destination, (self.origin, middle, self.destination),
            (Segment(1, self.origin, middle, first_line, 120), Segment(2, middle, self.destination, other_line, 120)),
            (Transfer(middle, first_line, other_line),), 840,
        )
        response = self.browser.post("/api/planning/route", json={"origin_id": 1, "destination_id": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["seconds"], 840)
        self.assertEqual(response.json()["transfer_count"], 1)
        self.assertEqual(response.json()["segments"][1]["operator"], "Outro operador")
        self.assertIn("Intermediaria", response.json()["transfers"][0])

    def test_sequencia_inconsistente_nao_e_exibida(self):
        from dataclasses import replace
        self.gateway.find_route.return_value = replace(self.gateway.find_route.return_value,
            stations=(self.destination, self.origin))
        response = self.browser.post("/api/planning/route", json={"origin_id": 1, "destination_id": 2})
        self.assertEqual(response.status_code, 502)

    def test_rota_de_outra_selecao_nao_e_exibida(self):
        response = self.browser.post("/api/planning/route", json={"origin_id": 2, "destination_id": 1})
        self.assertEqual(response.status_code, 502)

    def test_rota_nao_expoe_dados_de_lotacao(self):
        response = self.browser.post("/api/planning/route", json={"origin_id": 1, "destination_id": 2})
        body = response.json()
        public_keys = set(body) | {key for segment in body["segments"] for key in segment}
        for forbidden in ("lotac", "ocupac", "substitu", "viage", "crowd", "occupancy", "replaced"):
            self.assertFalse(any(forbidden in key for key in public_keys), forbidden)

    def test_confirmacao_registra_viagem_sem_devolver_registros(self):
        response = self.browser.post("/api/planning/trip", json=TRIP)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.auth.me.assert_called_once_with("private-test-token")
        self.gateway.confirm_trip.assert_called_once_with(
            TripConfirmation((TripSegment(10, 1, 3), TripSegment(11, 3, 2))),
            "private-test-token",
        )

    def test_confirmacao_sem_cookie_nao_registra(self):
        self.browser.cookies.clear()
        response = self.browser.post("/api/planning/trip", json=TRIP)
        self.assertEqual(response.status_code, 401)
        self.auth.me.assert_not_called()
        self.gateway.confirm_trip.assert_not_called()

    def test_confirmacao_com_sessao_expirada_nao_registra(self):
        self.auth.me.side_effect = XanoAuthRejected("expired", 401)
        response = self.browser.post("/api/planning/trip", json=TRIP)
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("private-test-token", response.text)
        self.gateway.confirm_trip.assert_not_called()

    def test_confirmacao_rejeitada_pela_sessao_do_xano(self):
        self.gateway.confirm_trip.side_effect = PlanningUnauthorized("internal-secret", 403)
        response = self.browser.post("/api/planning/trip", json=TRIP)
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("internal-secret", response.text)

    def test_confirmacao_nao_aceita_usuario_ou_tempo_do_navegador(self):
        invalid_bodies = [
            {**TRIP, "usuario_id": 7},
            {"segments": [{**TRIP["segments"][0], "tempo_estimado": 1}]},
            {"segments": []},
            {"segments": [{"id": 10, "origin_id": 1, "destination_id": 3}] * 201},
            {"segments": [{"id": True, "origin_id": 1, "destination_id": 3}]},
            {"segments": [{"id": 10, "origin_id": 0, "destination_id": 3}]},
            {"segments": [{"id": "10", "origin_id": 1, "destination_id": 3}]},
        ]
        for body in invalid_bodies:
            with self.subTest(body=body):
                response = self.browser.post("/api/planning/trip", json=body)
                self.assertEqual(response.status_code, 422)
        self.gateway.confirm_trip.assert_not_called()

    def test_confirmacao_de_trechos_desconexos_e_rejeitada(self):
        for segments in [
            [{"id": 10, "origin_id": 1, "destination_id": 3}, {"id": 11, "origin_id": 2, "destination_id": 4}],
            [{"id": 10, "origin_id": 1, "destination_id": 1}],
        ]:
            with self.subTest(segments=segments):
                response = self.browser.post("/api/planning/trip", json={"segments": segments})
                self.assertEqual(response.status_code, 400)
        self.gateway.confirm_trip.assert_not_called()

    def test_confirmacao_recusada_pelo_xano_nao_expoe_mensagem_interna(self):
        self.gateway.confirm_trip.side_effect = PlanningError("internal-payload", 400)
        response = self.browser.post("/api/planning/trip", json=TRIP)
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("internal-payload", response.text)

    def test_confirmacao_com_xano_indisponivel(self):
        self.gateway.confirm_trip.side_effect = PlanningUnavailable("internal-secret")
        response = self.browser.post("/api/planning/trip", json=TRIP)
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("internal-secret", response.text)

class PlanningApiGuidanceTests(unittest.TestCase):
    def setUp(self):
        PlanningApiTests.setUp(self)
        line = self.origin.lines[0]
        self.gateway.find_route.return_value = RouteResult(
            self.origin, self.destination, (self.origin, self.destination),
            (Segment(1, self.origin, self.destination, line, 120, direction="Jabaquara"),), (), 120,
        )
        self.entry = StationGuidance(
            station="Paraíso", line="linha azul", direction="Jabaquara",
            source="observação em campo", collected_on=date(2026, 10, 25),
            alighting_side="esquerdo", note="Carro 4, perto da escada rolante",
        )

    def post_route(self, enabled, entries=None, error=None):
        loader = MagicMock(return_value=entries if entries is not None else (self.entry,))
        if error is not None:
            loader.side_effect = error
        environ = {"METROFLOW_ORIENTACOES": "1" if enabled else "0"}
        with patch.dict("os.environ", environ), \
                patch("MetroFlow.planning.presentation.api.cached_guidance", loader):
            response = self.browser.post("/api/planning/route", json={"origin_id": 1, "destination_id": 2})
        return response, loader

    def test_ligada_por_padrao_sem_variavel(self):
        loader = MagicMock(return_value=(self.entry,))
        with patch("MetroFlow.planning.infrastructure.guidance_csv.os.environ", {}),                 patch("MetroFlow.planning.presentation.api.cached_guidance", loader):
            response = self.browser.post("/api/planning/route", json={"origin_id": 1, "destination_id": 2})
        self.assertEqual(response.json()["segments"][0]["guidance"]["alighting_side"], "esquerdo")

    def test_desligada_resposta_sem_campo_novo_e_sem_leitura(self):
        response, loader = self.post_route(enabled=False)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("guidance", response.json()["segments"][0])
        loader.assert_not_called()

    def test_ligada_inclui_somente_campos_publicos(self):
        response, _ = self.post_route(enabled=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["segments"][0]["guidance"], {
            "alighting_side": "esquerdo", "note": "Carro 4, perto da escada rolante",
        })
        self.assertNotIn("observação em campo", response.text)
        self.assertNotIn("private-test-token", response.text)

    def test_ligada_sem_cadastro_mantem_resposta_atual(self):
        enabled, _ = self.post_route(enabled=True, entries=())
        disabled, _ = self.post_route(enabled=False)
        self.assertEqual(enabled.json(), disabled.json())

    def test_falha_nas_orientacoes_nao_bloqueia_o_trajeto(self):
        response, _ = self.post_route(enabled=True, error=RuntimeError("internal-guidance"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("guidance", response.json()["segments"][0])
        self.assertNotIn("internal-guidance", response.text)

    def test_orientacoes_nao_alteram_tempo_nem_trechos(self):
        enabled, _ = self.post_route(enabled=True)
        disabled, _ = self.post_route(enabled=False)
        for key in ["seconds", "minutes", "stations", "transfers", "transfer_count"]:
            self.assertEqual(enabled.json()[key], disabled.json()[key])
