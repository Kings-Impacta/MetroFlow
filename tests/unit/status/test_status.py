"""Contratos, cache compartilhado e isolamento do planejamento sem rede real."""
from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
from pathlib import Path
from threading import Event
from unittest import TestCase
from unittest.mock import Mock, patch
import json
import os
import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient
from MetroFlow.status.domain import LineCondition, line_code
from MetroFlow.status.providers import HttpProvider, ProviderFailure, normalize_artesp, normalize_aggregate, ARTESP_URL
from MetroFlow.status.cache import SharedStatusCache
from MetroFlow.status.service import StatusService
from MetroFlow.status.api import status_api
from MetroFlow.status.presentation import LineStatusState, status_panel
from MetroFlow.planning.presentation.api import planning_api, authenticated_token
from MetroFlow.planning.presentation.state import PlanningState
from tests.unit.planning import test_api as planning_tests
from tests.unit.planning.test_api import TRIP
from tests.unit.planning.test_state import ROUTE, script_of

NOW=1794247200.0

def payload(label="Operação Normal",code="4",**status):
    return {"empresas":[{"linhas":[{"codigo":code,"ativa":True,"status":dict(situacao=label,operacao_normal=True,**status)}]}]}

def condition(code="L4",now=NOW):
    return LineCondition(line_code=code,situation="normal",label="Operação Normal",collected_at=now,validity="current")


class ProviderTests(TestCase):
    def test_restricao_nao_e_normal_mesmo_com_booleano_true(self):
        self.assertEqual(normalize_artesp(payload("Velocidade Reduzida"),NOW)[0].situation,"restricted")

    def test_catalogo_aberto_e_datas_com_significados_diferentes(self):
        row=normalize_artesp(payload("Situação nova",atualizado_em="2026-01-01T00:00:00-03:00",verificado_em="2026-11-09T15:00:00-03:00"),NOW)[0]
        self.assertEqual(row.situation,"unknown")
        self.assertEqual(row.aged(NOW).validity,"current")
        self.assertLess(row.updated_at,row.verified_at)

    def test_nulos_inativos_codigos_invalidos_e_duplicados(self):
        self.assertEqual(normalize_artesp({"empresas":[{"linhas":[{"ativa":True,"codigo":"4","status":None}]}]},NOW),[])
        self.assertIsNone(line_code(True));self.assertIsNone(line_code("EXP-L10"))
        self.assertEqual(line_code("04"),"L4")
        value=payload();value["empresas"]*=2
        with self.assertRaises(ValueError):normalize_artesp(value,NOW)

    def test_complemento_sem_horario_nao_inventa_data_da_origem(self):
        row=normalize_aggregate({"Data":[{"Code":1,"StatusLabel":"Operação Normal","Description":None}]},NOW)[0]
        self.assertIsNone(row.updated_at);self.assertIsNone(row.verified_at)
        self.assertEqual(row.description,"")

    def test_autorizacao_so_no_backend_e_sem_redirect(self):
        requests=[]
        def handler(request):
            requests.append(request)
            return httpx.Response(200,json=payload())
        provider=HttpProvider(ARTESP_URL,normalize_artesp,"private-key",httpx.MockTransport(handler))
        rows=provider.fetch(NOW)
        self.assertEqual(requests[0].headers["Authorization"],"Api-Key private-key")
        self.assertNotIn("private-key",json.dumps([r.model_dump() for r in rows]))
        self.assertNotIn("private-key",str(requests[0].url))

    def test_timeout_erro_payload_e_limite_sem_excecao_interna(self):
        for response in [httpx.Response(500,text="private-key"),httpx.Response(200,json={}),httpx.Response(200,content=b'x'*500001),httpx.Response(302,headers={"Location":"https://example.com"})]:
            with self.subTest(response=response.status_code):
                provider=HttpProvider(ARTESP_URL,normalize_artesp,transport=httpx.MockTransport(lambda r:response))
                with self.assertRaises(ProviderFailure) as caught:provider.fetch(NOW)
                self.assertNotIn("private-key",str(caught.exception))
        def timeout(request):raise httpx.ReadTimeout("private-key")
        with self.assertRaises(ProviderFailure):
            HttpProvider(ARTESP_URL,normalize_artesp,transport=httpx.MockTransport(timeout)).fetch(NOW)

    def test_429_suspende_uma_hora(self):
        provider=HttpProvider(ARTESP_URL,normalize_artesp,transport=httpx.MockTransport(lambda r:httpx.Response(429)))
        with self.assertRaises(ProviderFailure) as caught:provider.fetch(NOW)
        self.assertEqual(caught.exception.backoff,3600)


class CacheTests(TestCase):
    def setUp(self):
        Path(".cache/tests").mkdir(parents=True,exist_ok=True)
        self.folder=TemporaryDirectory(dir=".cache/tests");self.addCleanup(self.folder.cleanup)
        self.path=Path(self.folder.name)/"cache.sqlite3"
        self.now=NOW
        self.cache=SharedStatusCache(self.path,lambda:self.now)
        self.provider=Mock();self.provider.fetch.side_effect=lambda now:[condition(now=now)]

    def test_reuso_entre_instancias_e_persistencia(self):
        self.cache.read("key",self.provider)
        SharedStatusCache(self.path,lambda:self.now).read("key",self.provider)
        self.assertEqual(self.provider.fetch.call_count,1)
        self.now+=300;self.cache.read("key",self.provider)
        self.assertEqual(self.provider.fetch.call_count,2)

    def test_falha_mantem_ultimo_dado_com_marcacao_desatualizado(self):
        self.cache.read("key",self.provider);self.now+=300
        self.provider.fetch.side_effect=ProviderFailure()
        self.assertEqual(self.cache.read("key",self.provider)[0].validity,"stale")
        self.assertEqual(self.cache.read("key",self.provider)[0].validity,"stale")
        self.assertEqual(self.provider.fetch.call_count,2)
        self.now+=3601
        last=self.cache.read("key",self.provider)[0]
        self.assertEqual(last.validity,"stale")
        self.assertEqual(last.collected_at,NOW)

    def test_no_maximo_doze_tentativas_inclusive_falhas(self):
        self.provider.fetch.side_effect=ProviderFailure()
        for offset in range(0,3600,30):
            self.now=NOW+offset;self.cache.read("key",self.provider)
        self.assertEqual(self.provider.fetch.call_count,12)

    def test_reserva_entre_consultas_concorrentes(self):
        started,release=Event(),Event()
        def fetch(now):
            started.set();release.wait(5);return [condition(now=now)]
        self.provider.fetch.side_effect=fetch
        with ThreadPoolExecutor(2) as pool:
            first=pool.submit(self.cache.read,"key",self.provider)
            self.assertTrue(started.wait(2))
            second=pool.submit(SharedStatusCache(self.path,lambda:self.now).read,"key",self.provider)
            self.assertEqual(second.result(timeout=2),[])
            release.set();self.assertEqual(first.result(timeout=2)[0].validity,"current")
        self.assertEqual(self.provider.fetch.call_count,1)

    def test_cache_sem_permissao_nao_chama_origem(self):
        with patch("MetroFlow.status.cache.sqlite3.connect",side_effect=OSError()):
            self.assertEqual(self.cache.read("key",self.provider),[])
        self.provider.fetch.assert_not_called()

    def test_datas_velhas_futuras_e_ausentes(self):
        self.assertEqual(condition().aged(NOW+601).validity,"stale")
        self.assertEqual(condition().aged(NOW+3601).validity,"unavailable")
        self.assertEqual(condition(now=NOW+61).aged(NOW).validity,"unavailable")
        self.assertEqual(LineCondition(line_code="L4").aged(NOW).validity,"unavailable")


class ServiceTests(TestCase):
    def test_fontes_desabilitadas_por_padrao(self):
        with patch.dict(os.environ,{},clear=True):
            service=StatusService.from_environment()
        self.assertFalse(service.providers)
        self.assertIn("EXP-AER",[r.line_code for r in service.conditions()])
        self.assertTrue(all(r.validity=="unavailable" for r in service.conditions()))

    def test_chave_sem_ativacao_nao_consulta(self):
        with patch.dict(os.environ,{"METROFLOW_ARTESP_API_KEY":"private-key"},clear=True):
            self.assertFalse(StatusService.from_environment().providers)

    def test_ativacao_explicita_e_identificador_de_cache_sem_chave(self):
        with patch.dict(os.environ,{"METROFLOW_DDT_ENABLED":"1","METROFLOW_DDT_TOKEN":"private-key"},clear=True):
            service=StatusService.from_environment()
        self.assertEqual(len(service.providers),1)
        self.assertNotIn("private-key",service.providers[0][1])

    def test_precedencia_divergencia_ausencia_e_falha_total(self):
        cache=Mock();cache.read.side_effect=[[condition()],[condition().model_copy(update={"situation":"restricted"}),condition("L1")]]
        with self.assertLogs("MetroFlow.status.service",level="INFO"):
            rows=StatusService(cache,[("ddt","a",None),("cptm","b",None)]).conditions()
        self.assertEqual(next(r for r in rows if r.line_code=="L4").situation,"normal")
        self.assertEqual(next(r for r in rows if r.line_code=="L1").validity,"current")
        self.assertEqual(next(r for r in rows if r.line_code=="L2").validity,"unavailable")
        cache.read.side_effect=RuntimeError("private-key")
        with self.assertLogs("MetroFlow.status.service",level="WARNING") as logs:
            self.assertTrue(all(r.validity=="unavailable" for r in StatusService(cache,[("ddt","a",None)]).conditions()))
        self.assertNotIn("private-key",str(logs.output))


class StatusApiTests(TestCase):
    def setUp(self):
        app=FastAPI();app.include_router(status_api)
        self.app=app;self.browser=TestClient(app);self.addCleanup(self.browser.close)

    def test_sem_sessao_bloqueado_sem_cache_publico(self):
        response=self.browser.get("/api/planning/line-status")
        self.assertEqual(response.status_code,401)

    def test_falha_interna_nao_expoe_detalhes_nem_interrompe_status(self):
        self.app.dependency_overrides[authenticated_token]=lambda:"session"
        with patch("MetroFlow.status.api.StatusService.from_environment",side_effect=RuntimeError("private-key")):
            response=self.browser.get("/api/planning/line-status")
        self.assertEqual(response.status_code,200)
        self.assertTrue(all(r["validity"]=="unavailable" for r in response.json()))
        self.assertNotIn("private-key",response.text)


class PlanningIsolationTests(TestCase):
    setUp = planning_tests.PlanningApiTests.setUp
    def test_status_falha_busca_e_confirmacao_continuam(self):
        self.browser.app.include_router(status_api)
        with patch("MetroFlow.status.api.StatusService.from_environment",side_effect=RuntimeError("private-key")):
            self.assertEqual(self.browser.get("/api/planning/line-status").status_code,200)
            route=self.browser.post("/api/planning/route",json={"origin_id":1,"destination_id":2})
            self.assertEqual(route.status_code,200)
            self.assertEqual(self.browser.post("/api/planning/trip",json=TRIP).status_code,204)
            self.gateway.confirm_trip.assert_called_once()
            self.assertEqual(route.json()["segments"][0]["line_code"],"L1")


class PresentationTests(TestCase):
    def test_resultado_antigo_descartado_e_erro_independente(self):
        state=LineStatusState(_reflex_internal_init=True)
        state.refresh();state.refresh()
        state.receive({"request_id":1,"status":200,"data":[condition().model_dump()]})
        self.assertEqual(state.rows,[])
        state.receive({"request_id":2,"status":500,"data":None})
        self.assertIn("continuar buscando",state.message)
        self.assertEqual(state.rows,[])

    def test_interface_compila_e_desatualizado_tem_rotulo(self):
        state=LineStatusState(_reflex_internal_init=True);state.refresh()
        state.receive({"request_id":1,"status":200,"data":[condition().model_copy(update={"validity":"stale"}).model_dump()]})
        self.assertEqual(state.rows[0]["validity"],"Desatualizado")
        self.assertIsNotNone(status_panel(for_route=True))

    def test_consulta_status_nao_substitui_confirmacao_automatica(self):
        state=PlanningState(_reflex_internal_init=True)
        state._request_id=1
        route=json.loads(json.dumps(ROUTE));route["segments"][0]["line_code"]="L1"
        event=state.receive_route({"request_id":1,"status":200,"ok":True,"data":route})
        self.assertIn("/api/planning/trip",script_of(event))
        self.assertNotIn("/line-status",script_of(event))
        self.assertEqual(state.route_line_codes,["L1"])
        state._clear_result()
        self.assertEqual(state.route_line_codes,[])
