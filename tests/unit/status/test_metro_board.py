"""Quadro HTML: estrutura observada, texto seguro e nenhuma ativação implícita."""
from datetime import datetime
import os
from unittest import TestCase
from unittest.mock import Mock, patch
import httpx
from MetroFlow.status.domain import LineCondition
from MetroFlow.status.metro_board import normalize_metro_board, METRO_BOARD_URL, BRASILIA
from MetroFlow.status.providers import HttpProvider, ProviderFailure
from MetroFlow.status.service import StatusService

NOW = datetime(2026,11,9,17,0,tzinfo=BRASILIA).timestamp()


def row(code="1", label="Operação Normal", description="Sem ocorrência", date="09/11/2026 16:02:03"):
    return f'''<li class="linha list-group-item"><div class="linha-numero">{code}</div>
<div class="linha-situacao">{label}</div><div class="linha-info" data-bs-title="&lt;div class='description'&gt;{description}&lt;/div&gt;&lt;div class='date'&gt;(atualizado em {date})&lt;/div&gt;"></div></li>'''


class BoardTests(TestCase):
    def test_captura_codigo_situacao_descricao_e_data_brasilia(self):
        parsed=normalize_metro_board('<ol>'+row(label="Velocidade Reduzida",description="Falha &amp; circulação parcial")+'</ol>',NOW)[0]
        self.assertEqual(parsed.line_code,"L1")
        self.assertEqual(parsed.situation,"restricted")
        self.assertEqual(parsed.description,"Falha & circulação parcial")
        self.assertEqual(parsed.updated_at,datetime(2026,11,9,16,2,3,tzinfo=BRASILIA).timestamp())
        self.assertIsNone(parsed.verified_at)
        self.assertEqual(parsed.collected_at,NOW)
        self.assertEqual(parsed.aged(NOW).validity,"current")

    def test_data_em_minutos_e_sem_data(self):
        parsed=normalize_metro_board(row("4",date="09/11/2026 16:02"),NOW)[0]
        self.assertEqual(parsed.updated_at,datetime(2026,11,9,16,2,tzinfo=BRASILIA).timestamp())
        minimal='<li class="linha"><div class="linha-numero">2</div><div class="linha-situacao">Operação Normal</div></li>'
        parsed=normalize_metro_board(minimal,NOW)[0]
        self.assertIsNone(parsed.updated_at)
        self.assertEqual(parsed.description,"")

    def test_nao_executa_nem_retorna_html_ou_script(self):
        payload='<script>'+row("2")+'</script>'+row(description="&lt;b&gt;Atenção&lt;/b&gt;&lt;script&gt;segredo&lt;/script&gt;")
        parsed=normalize_metro_board(payload,NOW)
        self.assertEqual(len(parsed),1)
        self.assertEqual(parsed[0].description,"Atenção")
        self.assertNotIn('<',parsed[0].description)

    def test_situacao_desconhecida_nao_vira_normal(self):
        self.assertEqual(normalize_metro_board(row(label="Condição nova"),NOW)[0].situation,"unknown")

    def test_cobertura_limitada_nao_inventa_cptm_ou_servicos(self):
        rows=normalize_metro_board(''.join(row(n) for n in [1,2,3,4,5,6,10,13,15,17]),NOW)
        self.assertEqual([r.line_code for r in rows],["L1","L2","L3","L4","L5","L15","L17"])

    def test_html_incompativel_vazio_duplicado_e_datas_invalidas(self):
        for html in ['','<html>Indisponível</html>',row()+row(),row(label=""),row(date="99/99/2026 16:00"),row(date="10/11/2026 16:00"),row().replace('</li>',''),row().replace('linha-situacao','situacao-nova'),'<p>'+'x'*500001]:
            with self.subTest(html=html[:20]):
                with self.assertRaises(ValueError):normalize_metro_board(html,NOW)

    def test_transporte_html_sem_cabecalho_de_chave(self):
        requests=[]
        def handler(request):
            requests.append(request)
            return httpx.Response(200,text=row())
        provider=HttpProvider(METRO_BOARD_URL,normalize_metro_board,transport=httpx.MockTransport(handler),response_format="html")
        self.assertEqual(provider.fetch(NOW)[0].line_code,"L1")
        self.assertNotIn("Authorization",requests[0].headers)
        self.assertEqual(requests[0].url.host,"www.metro.sp.gov.br")

    def test_falha_html_e_redirect_nao_contorna_origem(self):
        for response in [httpx.Response(200,text="Site em manutenção"),httpx.Response(503),httpx.Response(302,headers={"Location":"https://example.com"})]:
            provider=HttpProvider(METRO_BOARD_URL,normalize_metro_board,transport=httpx.MockTransport(lambda r:response),response_format="html")
            with self.assertRaises(ProviderFailure):provider.fetch(NOW)

    def test_desativado_por_padrao_e_sem_relacao_com_chave_artesp(self):
        with patch.dict(os.environ,{"METROFLOW_ARTESP_API_KEY":"private-key"},clear=True):
            self.assertEqual(StatusService.from_environment().providers,[])
        with patch.dict(os.environ,{"METROFLOW_METRO_QUADRO_AUTORIZADO":"1","METROFLOW_ARTESP_API_KEY":"private-key"},clear=True):
            providers=StatusService.from_environment().providers
        self.assertEqual(len(providers),1)
        self.assertEqual(providers[0][0],"metro_board")
        self.assertEqual(providers[0][2].key,"")

    def test_prioridade_ddt_e_quadro_como_reserva_autorizada(self):
        def condition(code,source,validity="current",state="normal"):
            return LineCondition(line_code=code,source=source,validity=validity,situation=state)
        cache=Mock();cache.read.side_effect=[
            [condition("L4","DDT"),condition("L5","DDT","unavailable")],
            [condition("L4","Quadro",state="restricted"),condition("L5","Quadro"),condition("L1","Quadro")],
            [condition("L10","CPTM")]]
        with self.assertLogs("MetroFlow.status.service",level="INFO"):
            result=StatusService(cache,[("ddt","a",None),("metro_board","m",None),("cptm","b",None)]).conditions()
        rows={r.line_code:r for r in result}
        self.assertEqual(rows["L4"].source,"DDT")
        self.assertEqual(rows["L5"].source,"Quadro")
        self.assertEqual(rows["L1"].source,"Quadro")
        self.assertEqual(rows["L10"].source,"CPTM")
        self.assertEqual(rows["L13"].validity,"unavailable")

    def test_cache_falha_total_preserva_planejamento(self):
        # A mesma fronteira de falha é exercida independentemente do adaptador.
        cache=Mock();cache.read.side_effect=RuntimeError("HTML inválido")
        with self.assertLogs("MetroFlow.status.service",level="WARNING"):
            rows=StatusService(cache,[("metro_board","m",None)]).conditions()
        self.assertTrue(all(r.validity=="unavailable" for r in rows))
