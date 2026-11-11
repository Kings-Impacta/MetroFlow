"""Contrato de duas fontes, cache de origem e proteção do token."""
from io import BytesIO
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch
from MetroFlow.status.cache import SharedStatusCache
from MetroFlow.status.domain import LineCondition
from MetroFlow.status.feeds import (
    DiretoDosTrensProvider, normalize_ddt, normalize_cptm, cache_policy, retry_after,
)
from MetroFlow.status.providers import ProviderFailure
from MetroFlow.status.service import StatusService
from tests.unit.status.test_status import NOW


def ddt(code=6, **extra):
    return dict(codigo=code,id=123,criado="2026-11-09T12:00:00-03:00",situacao="Operação Normal",**extra)


class Response(BytesIO):
    def __init__(self, body, status=200, headers=None):
        super().__init__(body)
        self.status=status
        self.headers=headers or {}
    def getheaders(self):return list(self.headers.items())


class FeedsTests(TestCase):
    def test_ddt_cobre_linhas_pendentes_sem_inventar_verificacao(self):
        rows=normalize_ddt([ddt(6),ddt(7),ddt(13)],NOW)
        self.assertEqual([r.line_code for r in rows],["L6","L7","L13"])
        self.assertTrue(all(r.verified_at is None for r in rows))
        self.assertTrue(all(r.updated_at is not None for r in rows))

    def test_ddt_opcionais_situacao_nova_e_datas_naive(self):
        record=ddt(descricao=None,modificado="2026-11-09T14:00:00-03:00")
        record["situacao"]="Condição não catalogada"
        row=normalize_ddt([record],NOW)[0]
        self.assertEqual(row.description,"")
        self.assertEqual(row.situation,"unknown")
        record["criado"]="2026-11-09T12:00:00";record.pop("modificado")
        self.assertIsNone(normalize_ddt([record],NOW)[0].updated_at)

    def test_ddt_invalidos_duplicados_e_data_futura(self):
        for payload in [{},[],[None],[ddt(),ddt()],[dict(ddt(),situacao="")],[dict(ddt(),id=True)],[dict(ddt(),criado="2026-11-10T12:00:00-03:00")]]:
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):normalize_ddt(payload,NOW)

    def test_cptm_filtro_e_nao_inventa_fuso_ou_mudanca(self):
        row=dict(linhaId=10,tipo="C",status="Velocidade Reduzida",dataGeracao="2026-11-09T14:00:00",descricao=None)
        rows=normalize_cptm([row,dict(row,linhaId=11),dict(row,linhaId=12),dict(row,linhaId=1,tipo="M")],NOW)
        self.assertEqual([r.line_code for r in rows],["L10","L11","L12"])
        self.assertEqual(rows[0].situation,"restricted")
        self.assertIsNone(rows[0].verified_at)
        self.assertIsNone(rows[0].updated_at)
        row["dataGeracao"]="2026-11-09T14:00:00-03:00"
        self.assertIsNotNone(normalize_cptm([row],NOW)[0].verified_at)

    def test_cptm_resposta_vazia_e_invalida_nao_vira_normal(self):
        for payload in [{},[],[dict(linhaId=10,tipo="C",status="")]]:
            with self.assertRaises(ValueError):normalize_cptm(payload,NOW)

    def test_principal_complemento_e_reserva_por_atualidade(self):
        def condition(source,validity):
            return LineCondition(line_code="L10",source=source,validity=validity)
        for principal,complement,expected in [("current","current","DDT"),("stale","current","CPTM"),("unavailable","current","CPTM"),("stale","stale","DDT")]:
            with self.subTest(principal=principal,complement=complement):
                cache=Mock();cache.read.side_effect=[[condition("DDT",principal)],[condition("CPTM",complement)]]
                result=StatusService(cache,[("ddt","d",None),("cptm","c",None)]).conditions()
                self.assertEqual(next(r for r in result if r.line_code=="L10").source,expected)

    def test_sem_token_sem_ativacao_e_flags_antigas_ignoradas(self):
        for env in [{},{"METROFLOW_DDT_ENABLED":"1"},{"METROFLOW_DDT_TOKEN":"secret"},{"METROFLOW_ARTESP_ENABLED":"1","METROFLOW_ARTESP_API_KEY":"secret","METROFLOW_STATUS_COMPLEMENTAR_AUTORIZADO":"1"}]:
            with patch.dict(os.environ,env,clear=True):
                self.assertFalse(StatusService.from_environment().providers)
        with patch.dict(os.environ,{"METROFLOW_DDT_ENABLED":"1","METROFLOW_DDT_TOKEN":"secret","METROFLOW_CPTM_ENABLED":"1"},clear=True):
            providers=StatusService.from_environment().providers
        self.assertEqual([p[0] for p in providers],["ddt","cptm"])
        self.assertNotIn("secret",providers[0][1])

    def test_token_restrito_ao_transporte_https_sem_logs_ou_redirecionamento(self):
        response=Response(json.dumps([ddt()]).encode(),headers={"Cache-Control":"max-age=60"})
        connection=Mock();connection.getresponse.return_value=response
        factory=Mock(return_value=connection)
        token="private-token/with?chars"
        with self.assertNoLogs("httpx",level="DEBUG"):
            rows=DiretoDosTrensProvider(token,factory).fetch(NOW)
        factory.assert_called_once_with("www.diretodostrens.com.br",timeout=2.0)
        path=connection.request.call_args.args[1]
        self.assertIn("private-token%2Fwith%3Fchars",path)
        self.assertNotIn(token,json.dumps([r.model_dump() for r in rows]))
        connection.close.assert_called_once()
        self.assertEqual(rows.fresh_for,60)

    def test_erro_de_transporte_nao_expoe_credencial(self):
        connection=Mock();connection.request.side_effect=OSError("private-token")
        with self.assertRaises(ProviderFailure) as caught:
            DiretoDosTrensProvider("private-token",Mock(return_value=connection)).fetch(NOW)
        self.assertNotIn("private-token",str(caught.exception))
        connection.close.assert_called_once()

    def test_erro_http_redirect_429_payload_e_tamanho(self):
        for body,status in [(b'{}',200),(b'x'*500001,200),(b'',302),(b'',401),(b'',500),(b'',429)]:
            response=Response(body,status,{"Retry-After":"7200"})
            connection=Mock();connection.getresponse.return_value=response
            with self.assertRaises(ProviderFailure) as caught:
                DiretoDosTrensProvider("token",Mock(return_value=connection)).fetch(NOW)
            if status==429:self.assertEqual(caught.exception.backoff,7200)
            self.assertEqual(connection.request.call_count,1)

    def test_cache_control_limita_validade_respeita_age_e_no_store(self):
        rows=normalize_ddt([ddt()],NOW)
        result=cache_policy(rows,{"cache-control":"max-age=100, s-maxage=60","age":"20"})
        self.assertEqual(result.fresh_for,40)
        for directive in ["no-store","no-cache","private"]:
            self.assertFalse(cache_policy(rows,{"cache-control":directive}).cacheable)
        expired=cache_policy(rows,{"cache-control":"max-age=0"})
        self.assertTrue(expired.cacheable)
        self.assertEqual(expired.fresh_for,0)
        self.assertEqual(cache_policy(rows,{"cache-control":"max-age=900"}).refresh_after,900)
        self.assertEqual(retry_after({"retry-after":"7200"},NOW),7200)

    def test_cache_compatibilidade_expiracao_e_no_store_sem_refetch(self):
        Path(".cache/tests").mkdir(parents=True,exist_ok=True)
        with TemporaryDirectory(dir=".cache/tests") as directory:
            clock=[NOW];cache=SharedStatusCache(Path(directory)/"cache.sqlite3",lambda:clock[0])
            provider=Mock();provider.fetch.side_effect=lambda now:cache_policy(normalize_ddt([ddt()],now),{"cache-control":"max-age=60"})
            self.assertEqual(cache.read("d",provider)[0].validity,"current")
            clock[0]+=61
            self.assertEqual(cache.read("d",provider)[0].validity,"stale")
            self.assertEqual(provider.fetch.call_count,1)
            provider.fetch.side_effect=lambda now:cache_policy(normalize_ddt([ddt()],now),{"cache-control":"no-store"})
            self.assertEqual(cache.read("private",provider)[0].validity,"current")
            self.assertEqual(cache.read("private",provider),[])
            self.assertEqual(provider.fetch.call_count,2)
