"""Estado do painel: acesso, cargas separadas, filtros e alteração de estações."""

import json
import unittest

from MetroFlow.admin.presentation.state import AdminState, format_moment


INDICATORS = {
    "computed_at_ms": 1_763_316_000_000,
    "usage": {"active_routes": 2, "users_travelling": 2, "recent_users": 1234, "enabled_accounts": 9},
    "network": {"active_stations": 180, "inactive_stations": 2, "active_lines": 16, "active_segments": 207},
    "volume": {"trips_today": 3, "trips_last_7_days": 20},
    "ranking": [
        {"id": 1, "name": "Sé", "code": "SE", "uses": 6},
        {"id": 2, "name": "Luz", "code": "LUZ", "uses": 1},
    ],
    "crowding": {"crowded_segments": 1, "minimum_users": 2, "percentage": 12.5},
}
STATIONS = [
    {"id": 4, "name": "Brás", "code": "BRS", "active": False, "lines": [{"id": 3, "name": "Vermelha", "code": "L3", "color": None}]},
    {"id": 1, "name": "Sé", "code": "SE", "active": True, "lines": [
        {"id": 1, "name": "Azul", "code": "L1", "color": "#0455A1"},
        {"id": 3, "name": "Vermelha", "code": "L3", "color": None},
    ]},
    {"id": 2, "name": "Luz", "code": "LUZ", "active": True, "lines": []},
]


def script_of(event) -> str:
    return event.args[0][1]._var_value


def ok(request_id: int, data) -> dict:
    return {"request_id": request_id, "ok": True, "status": 200, "data": data}


def failed(request_id: int, status: int) -> dict:
    return {"request_id": request_id, "ok": False, "status": status, "data": {"detail": "x"}}


class AdminStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = AdminState(_reflex_internal_init=True)
        self.events = self.state.load_panel()

    def authorize(self) -> None:
        self.state.receive_indicators(ok(self.state._indicators_request, INDICATORS))
        self.state.receive_stations(ok(self.state._stations_request, STATIONS))

    def test_abertura_dispara_duas_cargas_sem_dados_ate_a_autorizacao(self) -> None:
        self.assertEqual(len(self.events), 2)
        self.assertIn("/api/admin/indicators", script_of(self.events[0]))
        self.assertIn("/api/admin/stations", script_of(self.events[1]))
        self.assertIn('"credentials": "include"', script_of(self.events[0]))
        self.assertEqual(self.state.access, "checking")
        self.assertEqual(self.state.usage_cards, [])
        self.assertEqual(self.state.stations, [])

    def test_respostas_aceitas_autorizam_e_preenchem_o_painel(self) -> None:
        self.authorize()

        self.assertEqual(self.state.access, "authorized")
        self.assertEqual(self.state.indicators_status, "ready")
        self.assertEqual(self.state.usage_cards[0], {
            "label": "Rotas ativas", "value": "2", "hint": "Viagens em andamento agora",
        })
        self.assertEqual(self.state.usage_cards[2]["value"], "1.234")
        self.assertEqual(self.state.ranking[0], {"position": "1º", "name": "Sé", "code": "SE", "uses": "6 usos"})
        self.assertEqual(self.state.ranking[1]["uses"], "1 uso")
        self.assertEqual(self.state.crowding_value, "1")
        self.assertIn("2 usuários e 12,5%", self.state.crowding_hint)
        self.assertEqual(self.state.computed_at, format_moment(INDICATORS["computed_at_ms"]))
        self.assertEqual(self.state.stations_summary, "3 estações cadastradas · 1 inativa")
        self.assertEqual(self.state.stations[1]["lines"], "L1 Azul · L3 Vermelha")

    def test_momento_da_apuracao_no_horario_de_sao_paulo(self) -> None:
        # 16/11/2025 18:00 UTC = 15:00 em São Paulo.
        self.assertEqual(format_moment(1_763_316_000_000), "16/11/2025 às 15:00:00")

    def test_lotacao_indisponivel(self) -> None:
        data = {**INDICATORS, "crowding": {"crowded_segments": None, "minimum_users": None, "percentage": None}}

        self.state.receive_indicators(ok(self.state._indicators_request, data))

        self.assertEqual(self.state.crowding_value, "Indisponível")
        self.assertIn("ausente ou inválida", self.state.crowding_hint)

    def test_401_descarta_dados_e_redireciona_ao_login(self) -> None:
        self.authorize()
        self.state.refresh_indicators()

        events = self.state.receive_indicators(failed(self.state._indicators_request, 401))

        self.assertEqual(self.state.access, "checking")
        self.assertEqual(self.state.stations, [])
        self.assertEqual(self.state.usage_cards, [])
        self.assertEqual(script_of(events[1]), "/login")

    def test_403_mostra_acesso_restrito_sem_dados_e_sem_encerrar_a_sessao(self) -> None:
        events = self.state.receive_stations(failed(self.state._stations_request, 403))

        self.assertEqual(self.state.access, "restricted")
        self.assertEqual(events, [])
        self.assertEqual(self.state.stations, [])
        # A outra carga, já invalidada, não reabre o painel.
        self.state.receive_indicators(ok(self.state._indicators_request - 1, INDICATORS))
        self.assertEqual(self.state.access, "restricted")
        self.assertEqual(self.state.usage_cards, [])

    def test_falha_nos_indicadores_nao_bloqueia_as_estacoes(self) -> None:
        self.state.receive_indicators(failed(self.state._indicators_request, 503))
        self.state.receive_stations(ok(self.state._stations_request, STATIONS))

        self.assertEqual(self.state.access, "authorized")
        self.assertEqual(self.state.indicators_status, "error")
        self.assertEqual(self.state.stations_status, "ready")
        self.assertEqual(len(self.state.visible_stations), 3)

    def test_falha_apos_atualizacao_nao_mantem_valores_antigos(self) -> None:
        self.authorize()
        self.state.refresh_indicators()

        self.state.receive_indicators(failed(self.state._indicators_request, 503))

        self.assertEqual(self.state.indicators_status, "error")
        self.assertEqual(self.state.usage_cards, [])
        self.assertEqual(self.state.computed_at, "")
        self.assertEqual(self.state.crowding_value, "")

    def test_falha_nas_duas_cargas_indica_erro_de_acesso(self) -> None:
        self.state.receive_indicators(failed(self.state._indicators_request, 503))
        self.assertEqual(self.state.access, "checking")

        self.state.receive_stations(failed(self.state._stations_request, 0))

        self.assertEqual(self.state.access, "error")

    def test_resposta_antiga_e_descartada(self) -> None:
        old = self.state._indicators_request
        self.authorize()
        self.state.refresh_indicators()

        self.state.receive_indicators(ok(old, {**INDICATORS, "usage": {**INDICATORS["usage"], "active_routes": 99}}))

        self.assertEqual(self.state.usage_cards[0]["value"], "2")
        self.assertEqual(self.state.indicators_status, "loading")

    def test_contrato_invalido_vira_erro(self) -> None:
        self.state.receive_indicators(ok(self.state._indicators_request, {"usage": {}}))
        self.state.receive_stations(ok(self.state._stations_request, [{"id": "x"}]))

        self.assertEqual(self.state.indicators_status, "error")
        self.assertEqual(self.state.stations_status, "error")
        self.assertEqual(self.state.access, "error")

    def test_atualizacao_manual_so_depois_da_autorizacao(self) -> None:
        self.assertIsNone(self.state.refresh_indicators())

        self.authorize()
        event = self.state.refresh_indicators()

        self.assertIn("/api/admin/indicators", script_of(event))
        self.assertEqual(self.state.indicators_status, "loading")

    # Pesquisa e filtro

    def test_pesquisa_sem_acento_e_por_codigo(self) -> None:
        self.authorize()

        self.state.set_query("se")
        self.assertEqual([item["name"] for item in self.state.visible_stations], ["Sé"])

        self.state.set_query("BRS")
        self.assertEqual([item["name"] for item in self.state.visible_stations], ["Brás"])

    def test_filtro_por_situacao(self) -> None:
        self.authorize()

        self.state.set_status_filter("inativas")
        self.assertEqual([item["name"] for item in self.state.visible_stations], ["Brás"])

        self.state.set_status_filter("ativas")
        self.assertEqual([item["name"] for item in self.state.visible_stations], ["Sé", "Luz"])

        self.state.set_status_filter("qualquer")
        self.assertEqual(self.state.status_filter, "todas")

    def test_pesquisa_sem_resultado(self) -> None:
        self.authorize()

        self.state.set_query("inexistente")

        self.assertEqual(self.state.visible_stations, [])

    # Alteração

    def test_inativar_abre_confirmacao_com_nome_e_linhas_sem_enviar(self) -> None:
        self.authorize()

        result = self.state.request_change("1")

        self.assertIsNone(result)
        self.assertTrue(self.state.confirm_open)
        self.assertEqual(self.state.pending_name, "Sé")
        self.assertEqual(self.state.pending_lines, "L1 Azul · L3 Vermelha")
        self.assertEqual(self.state.updating_id, "")

    def test_cancelar_nao_envia_requisicao(self) -> None:
        self.authorize()
        self.state.request_change("1")
        request = self.state._change_request

        self.state.cancel_change()

        self.assertFalse(self.state.confirm_open)
        self.assertEqual(self.state.pending_id, "")
        self.assertEqual(self.state._change_request, request)
        self.assertEqual(self.state.stations[1]["active"], "true")

    def test_fechar_o_dialogo_cancela(self) -> None:
        self.authorize()
        self.state.request_change("1")

        self.state.handle_dialog_open(False)

        self.assertFalse(self.state.confirm_open)
        self.assertEqual(self.state.pending_id, "")

    def test_confirmar_envia_inativacao(self) -> None:
        self.authorize()
        self.state.request_change("1")

        event = self.state.confirm_change()

        script = script_of(event)
        self.assertIn("/api/admin/stations/1/status", script)
        self.assertIn(json.dumps(json.dumps({"active": False})), script)
        self.assertEqual(self.state.updating_id, "1")
        self.assertFalse(self.state.confirm_open)

    def test_ativar_nao_pede_confirmacao(self) -> None:
        self.authorize()

        event = self.state.request_change("4")

        self.assertFalse(self.state.confirm_open)
        self.assertIn("/api/admin/stations/4/status", script_of(event))
        self.assertIn(json.dumps(json.dumps({"active": True})), script_of(event))

    def test_sucesso_usa_a_situacao_devolvida_e_reapura_os_indicadores(self) -> None:
        self.authorize()
        self.state.request_change("4")

        follow_up = self.state.receive_change(ok(self.state._change_request, {"id": 4, "active": True}))

        self.assertEqual(self.state.stations[0]["active"], "true")
        self.assertEqual(self.state.updating_id, "")
        self.assertEqual(self.state.feedback_kind, "success")
        self.assertEqual(self.state.feedback, "Brás ativada.")
        self.assertEqual(follow_up, AdminState.refresh_indicators)

    def test_situacao_ja_aplicada_mostra_a_situacao_vigente(self) -> None:
        self.authorize()
        self.state.request_change("1")
        self.state.confirm_change()

        # Outro administrador já havia reativado: o servidor devolve a vigente.
        self.state.receive_change(ok(self.state._change_request, {"id": 1, "active": True}))

        self.assertEqual(self.state.stations[1]["active"], "true")
        self.assertEqual(self.state.feedback, "Sé ativada.")

    def test_falha_preserva_a_situacao_anterior(self) -> None:
        self.authorize()
        self.state.request_change("4")

        follow_up = self.state.receive_change(failed(self.state._change_request, 503))

        self.assertIsNone(follow_up)
        self.assertEqual(self.state.stations[0]["active"], "false")
        self.assertEqual(self.state.feedback_kind, "error")
        self.assertIn("última confirmada", self.state.feedback)

    def test_estacao_inexistente(self) -> None:
        self.authorize()
        self.state.request_change("4")

        self.state.receive_change(failed(self.state._change_request, 404))

        self.assertIn("Estação não encontrada", self.state.feedback)
        self.assertEqual(self.state.stations[0]["active"], "false")

    def test_resposta_de_outra_estacao_e_rejeitada(self) -> None:
        self.authorize()
        self.state.request_change("4")

        self.state.receive_change(ok(self.state._change_request, {"id": 2, "active": False}))

        self.assertEqual(self.state.feedback_kind, "error")
        self.assertEqual(self.state.stations[2]["active"], "true")

    def test_uma_alteracao_por_vez(self) -> None:
        self.authorize()
        self.state.request_change("4")

        self.assertIsNone(self.state.request_change("1"))
        self.assertFalse(self.state.confirm_open)

    def test_sessao_expirada_na_alteracao_redireciona(self) -> None:
        self.authorize()
        self.state.request_change("4")

        events = self.state.receive_change(failed(self.state._change_request, 401))

        self.assertEqual(script_of(events[1]), "/login")
        self.assertEqual(self.state.stations, [])

    def test_controles_bloqueados_sem_autorizacao(self) -> None:
        self.state.stations = [{"id": "1", "name": "Sé", "code": "SE", "active": "true", "lines": "", "search": "se se"}]

        self.assertIsNone(self.state.request_change("1"))
        self.assertFalse(self.state.confirm_open)

    def test_limpar_painel_descarta_dados(self) -> None:
        self.authorize()

        self.state.clear_panel()

        self.assertEqual(self.state.access, "checking")
        self.assertEqual(self.state.stations, [])
        self.assertEqual(self.state.ranking, [])
