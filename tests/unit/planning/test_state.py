"""Estado do planejador: selecao, concorrencia, falhas e descarte de resultados."""

import json
import unittest

from MetroFlow.planning.presentation.state import PlanningState


ROUTE = {
    "origin": "Vergueiro", "destination": "Paraiso", "stations": ["Vergueiro", "Paraiso"],
    "seconds": 120, "minutes": 2, "transfer_count": 0,
    "segments": [{
        "id": 7, "origin_id": 1, "destination_id": 2,
        "origin": "Vergueiro", "destination": "Paraiso", "line": "Azul", "operator": "Metro", "seconds": 120,
    }],
    "transfers": [],
}


def script_of(event) -> str:
    return event.args[0][1]._var_value


class PlanningStateTests(unittest.TestCase):
    def setUp(self):
        self.state = PlanningState(_reflex_internal_init=True)
        self.state.stations_status = "ready"
        self.state.stations = [{"id": "1", "label": "Vergueiro"}, {"id": "2", "label": "Paraiso"}]
        self.state.origin_id = "1"
        self.state.destination_id = "2"

    def test_selecao_igual_nao_dispara_consulta(self):
        self.state.destination_id = "1"
        self.assertIsNone(self.state.search({}))
        self.assertEqual(self.state.route_status, "error")

    def test_nova_busca_limpa_resultado_e_impede_duplicata(self):
        self.state.title = "Resultado anterior"
        self.assertIsNotNone(self.state.search({}))
        self.assertEqual(self.state.title, "")
        self.assertEqual(self.state.route_status, "loading")
        self.assertIsNone(self.state.search({}))

    def test_resposta_antiga_nao_sobrescreve_busca(self):
        self.state.search({})
        self.state.receive_route({"request_id": self.state._request_id - 1, "status": 404, "ok": False})
        self.assertEqual(self.state.route_status, "loading")

    def test_sem_rota_limpa_resultado_anterior(self):
        self.state.title = "Resultado anterior"
        self.state.receive_route({"request_id": self.state._request_id, "status": 404, "ok": False})
        self.assertEqual(self.state.route_status, "not_found")
        self.assertEqual(self.state.title, "")

    def test_sessao_expirada_limpa_dados_e_redireciona(self):
        self.state.title = "Resultado anterior"
        events = self.state.receive_route({"request_id": self.state._request_id, "status": 401, "ok": False})
        self.assertEqual(self.state.route_status, "unauthenticated")
        self.assertEqual(self.state.stations, [])
        self.assertEqual(self.state.title, "")
        self.assertEqual(len(events), 2)
        self.assertEqual(events[1].args[0][1]._var_value, "/login")

    def test_resposta_incompleta_vira_erro(self):
        self.state.receive_route({"request_id": self.state._request_id, "status": 200, "ok": True, "data": {}})
        self.assertEqual(self.state.route_status, "error")

    def test_trocar_selecao_limpa_resultado(self):
        self.state.title = "Resultado anterior"
        self.state.route_status = "success"
        self.state.select_origin("2")
        self.assertEqual(self.state.title, "")
        self.assertEqual(self.state.route_status, "idle")

    def test_inverter_rota_troca_ids_e_textos(self):
        self.state.origin_query = "Vergueiro"
        self.state.destination_query = "Paraiso"
        self.state.origin_matches = [{"id": "1", "label": "Vergueiro"}]
        self.state.destination_matches = [{"id": "2", "label": "Paraiso"}]
        self.state.title = "Resultado anterior"
        self.state.route_status = "success"

        self.state.swap_route_selection()

        self.assertEqual(self.state.origin_id, "2")
        self.assertEqual(self.state.destination_id, "1")
        self.assertEqual(self.state.origin_query, "Paraiso")
        self.assertEqual(self.state.destination_query, "Vergueiro")
        self.assertEqual(self.state.origin_matches, [])
        self.assertEqual(self.state.destination_matches, [])
        self.assertEqual(self.state.title, "")
        self.assertEqual(self.state.route_status, "idle")

    def test_inverter_rota_durante_busca_nao_altera_selecao(self):
        self.state.origin_query = "Vergueiro"
        self.state.destination_query = "Paraiso"
        self.state.route_status = "loading"

        self.state.swap_route_selection()

        self.assertEqual(self.state.origin_id, "1")
        self.assertEqual(self.state.destination_id, "2")
        self.assertEqual(self.state.origin_query, "Vergueiro")
        self.assertEqual(self.state.destination_query, "Paraiso")

    def test_lista_vazia_e_erro_de_rede(self):
        self.state.receive_stations({"request_id": self.state._request_id, "status": 200, "ok": True, "data": []})
        self.assertEqual(self.state.stations_status, "empty")
        self.state.receive_stations({"request_id": self.state._request_id, "status": 0, "ok": False})
        self.assertEqual(self.state.stations_status, "error")

    def test_recarregar_lista_invalida_consultas_anteriores(self):
        self.state.title = "Resultado anterior"
        previous_id = self.state._request_id
        self.assertIsNotNone(self.state.load_stations())
        self.assertEqual(self.state.title, "")
        self.assertEqual(self.state.stations_status, "loading")
        self.state.receive_stations({"request_id": previous_id, "status": 200, "ok": True, "data": []})
        self.assertEqual(self.state.stations_status, "loading")

    def test_logout_invalida_callback_em_andamento(self):
        self.state.search({})
        previous_id = self.state._request_id
        self.state.clear_planner()
        self.state.receive_route({"request_id": previous_id, "status": 404, "ok": False})
        self.assertEqual(self.state.route_status, "idle")
        self.assertEqual(self.state.message, "")

    def _receive_success(self):
        self.state.receive_route({"request_id": self.state._request_id, "status": 200, "ok": True, "data": ROUTE})

    def test_resultado_de_sucesso(self):
        self._receive_success()
        self.assertEqual(self.state.route_status, "success")
        self.assertEqual(self.state.minutes, 2)
        self.assertEqual(self.state.segments[0]["line"], "Azul — Metro")

    def test_confirmacao_envia_os_trechos_do_resultado_apresentado(self):
        self._receive_success()
        script = script_of(self.state.confirm_trip())
        self.assertIn('"/api/planning/trip"', script)
        self.assertIn(
            json.dumps(json.dumps({"segments": [{"id": 7, "origin_id": 1, "destination_id": 2}]})),
            script,
        )

    def test_confirmacao_sem_resultado_nao_dispara(self):
        self.assertIsNone(self.state.confirm_trip())
        self._receive_success()
        self.state.select_origin("2")
        self.assertIsNone(self.state.confirm_trip())

    def test_confirmacao_nao_exibe_aviso_e_mantem_botao_disponivel(self):
        self._receive_success()
        for status, ok in [(204, True), (503, False), (0, False)]:
            with self.subTest(status=status):
                event = self.state.confirm_trip()
                self.assertIsNotNone(event)
                self.assertIsNone(self.state.receive_trip_confirmation(
                    {"request_id": self.state._trip_request_id, "status": status, "ok": ok, "data": None}
                ))
                self.assertEqual(self.state.route_status, "success")
                self.assertEqual(self.state.message, "")
                self.assertEqual(self.state.title, "Vergueiro → Paraiso")
        self.assertIsNotNone(self.state.confirm_trip())

    def test_confirmacao_com_sessao_expirada_redireciona(self):
        self._receive_success()
        self.state.confirm_trip()
        events = self.state.receive_trip_confirmation(
            {"request_id": self.state._trip_request_id, "status": 401, "ok": False, "data": None}
        )
        self.assertEqual(self.state.route_status, "unauthenticated")
        self.assertEqual(self.state.title, "")
        self.assertEqual(events[1].args[0][1]._var_value, "/login")
        self.assertIsNone(self.state.confirm_trip())
