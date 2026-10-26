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

    def test_busca_confirma_automaticamente_os_trechos_apresentados(self):
        event = self.state.receive_route({
            "request_id": self.state._request_id,
            "status": 200,
            "ok": True,
            "data": ROUTE,
        })
        script = script_of(event)
        self.assertIn('"/api/planning/trip"', script)
        self.assertIn(
            json.dumps(json.dumps({"segments": [{"id": 7, "origin_id": 1, "destination_id": 2}]})),
            script,
        )

    def test_confirmacao_automatica_nao_apaga_resultado(self):
        self._receive_success()
        for status, ok in [(204, True), (503, False), (0, False)]:
            with self.subTest(status=status):
                self.assertIsNone(self.state.receive_trip_confirmation(
                    {"request_id": self.state._trip_request_id, "status": status, "ok": ok, "data": None}
                ))
                self.assertEqual(self.state.route_status, "success")
                self.assertEqual(self.state.message, "")
                self.assertEqual(self.state.title, "Vergueiro → Paraiso")

    def test_confirmacao_com_sessao_expirada_redireciona(self):
        self._receive_success()
        events = self.state.receive_trip_confirmation(
            {"request_id": self.state._trip_request_id, "status": 401, "ok": False, "data": None}
        )
        self.assertEqual(self.state.route_status, "unauthenticated")
        self.assertEqual(self.state.title, "")
        self.assertEqual(events[1].args[0][1]._var_value, "/login")

    def test_confirmacao_antiga_e_descartada(self):
        self._receive_success()
        previous_id = self.state._trip_request_id
        self._receive_success()

        self.assertIsNone(self.state.receive_trip_confirmation({
            "request_id": previous_id,
            "status": 401,
            "ok": False,
            "data": None,
        }))
        self.assertEqual(self.state.route_status, "success")

    def receive_segments(self, segments, destination):
        # Identificadores exigidos pelo contrato da confirmacao de viagem.
        segments = [
            {"id": index, "origin_id": index, "destination_id": index + 1, **item}
            for index, item in enumerate(segments, 1)
        ]
        self.state.receive_route({"request_id": self.state._request_id, "status": 200, "ok": True, "data": {
            "origin": segments[0]["origin"], "destination": destination,
            "stations": [segments[0]["origin"], *[item["destination"] for item in segments]],
            "seconds": 1000, "minutes": 17, "transfer_count": len(segments) - 1,
            "segments": segments, "transfers": [],
        }})
        return self.state.instructions

    def test_cartoes_sem_orientacao_tem_campos_vazios(self):
        instructions = self.receive_segments([
            {"origin": "Vergueiro", "destination": "Paraiso", "line": "Azul", "operator": "Metro", "seconds": 120},
        ], "Paraiso")
        self.assertEqual({(item["side"], item["note"]) for item in instructions}, {("", "")})

    def test_orientacoes_aparecem_na_baldeacao_e_no_desembarque(self):
        instructions = self.receive_segments([
            {"origin": "Lapa", "destination": "Barra Funda", "line": "Linha 8", "operator": "Via",
             "direction": "Júlio Prestes", "seconds": 300,
             "guidance": {"alighting_side": "direito", "note": "Siga pela passarela"}},
            {"origin": "Barra Funda", "destination": "Sé", "line": "Linha 3", "operator": "Metro",
             "direction": "Corinthians-Itaquera", "seconds": 600,
             "guidance": {"alighting_side": "ambos", "note": None}},
        ], "Sé")
        by_kind = {}
        for item in instructions:
            by_kind.setdefault(item["kind"], []).append((item["side"], item["note"]))
        self.assertEqual(by_kind["BALDEAÇÃO"], [("Desembarque pelo lado direito", "Siga pela passarela")])
        self.assertEqual(by_kind["DESEMBARQUE"], [("As portas abrem dos dois lados", "")])
        # Embarque e trajeto no trem nao repetem a orientacao de descida.
        self.assertEqual(set(by_kind["EMBARQUE"] + by_kind["SIGA"]), {("", "")})

    def test_integracao_a_pe_recebe_orientacao_da_descida_anterior(self):
        instructions = self.receive_segments([
            {"origin": "Consolação", "destination": "Paulista", "line": "Linha 2", "operator": "Metro",
             "direction": "Vila Prudente", "seconds": 120,
             "guidance": {"alighting_side": None, "note": "Siga as placas da Linha 4"}},
            {"origin": "Paulista", "destination": "Consolação", "line": "Integração", "operator": "Metro",
             "segment_type": "transferencia", "seconds": 240},
        ], "Consolação")
        walk = next(item for item in instructions if item["kind"] == "INTEGRAÇÃO")
        self.assertEqual((walk["side"], walk["note"]), ("", "Siga as placas da Linha 4"))
