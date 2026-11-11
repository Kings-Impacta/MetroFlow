"""Último retorno permanece visível até uma nova observação válida por linha."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from MetroFlow.status.cache import SharedStatusCache
from MetroFlow.status.domain import LineCondition
from MetroFlow.status.feeds import cache_policy
from MetroFlow.status.presentation import LineStatusState
from MetroFlow.status.providers import ProviderFailure
from tests.unit.status.test_status import NOW, condition


def observed(code='L8',now=NOW,label='Operação Normal'):
    return condition(code,now).model_copy(update={'source':'Fonte oficial','label':label})


class LastKnownCacheTests(TestCase):
    def setUp(self):
        Path('.cache/tests').mkdir(parents=True,exist_ok=True)
        self.folder=TemporaryDirectory(dir='.cache/tests');self.addCleanup(self.folder.cleanup)
        self.path=Path(self.folder.name)/'status.sqlite3'
        self.now=NOW
        self.cache=SharedStatusCache(self.path,lambda:self.now)
        self.provider=Mock()
        self.provider.fetch.side_effect=lambda now:[observed(now=now)]

    def test_cache_cdn_vencido_permanece_entre_pedidos_e_reinicio(self):
        self.provider.fetch.side_effect=lambda now:cache_policy([observed(now=now)],
            {'cache-control':'max-age=600, stale-while-revalidate=600','age':'700'})
        first=self.cache.read('motiva',self.provider)[0]
        second=SharedStatusCache(self.path,lambda:self.now).read('motiva',self.provider)[0]
        self.assertEqual(first,second)
        self.assertEqual(second.validity,'stale')
        self.assertEqual(second.label,'Operação Normal')
        self.assertEqual(self.provider.fetch.call_count,1)

    def test_falha_prolongada_nao_apaga_data_e_recuperacao_substitui(self):
        self.cache.read('metro',self.provider)
        self.now+=86400
        self.provider.fetch.side_effect=ProviderFailure()
        last=SharedStatusCache(self.path,lambda:self.now).read('metro',self.provider)[0]
        self.assertEqual(last.collected_at,NOW)
        self.assertEqual(last.validity,'stale')
        self.now+=300
        self.provider.fetch.side_effect=lambda now:[observed(now=now,label='Operação Parcial')]
        recovered=self.cache.read('metro',self.provider)[0]
        self.assertEqual(recovered.label,'Operação Parcial')
        self.assertEqual(recovered.collected_at,self.now)
        self.assertEqual(recovered.validity,'current')

    def test_vazio_duplicado_futuro_e_payload_invalido_nao_substituem(self):
        self.cache.read('metro',self.provider)
        for value in ([],[observed(),observed()],['inválido'],[observed(now=NOW+99999)]):
            self.now+=300
            self.provider.fetch.side_effect=None;self.provider.fetch.return_value=value
            row=self.cache.read('metro',self.provider)[0]
            self.assertEqual(row.label,'Operação Normal')
            self.assertEqual(row.collected_at,NOW)
            self.assertEqual(row.validity,'stale')

    def test_resposta_parcial_substitui_somente_linha_que_retornou(self):
        self.provider.fetch.side_effect=lambda now:[observed('L8',now),observed('L9',now)]
        self.cache.read('motiva',self.provider);self.now+=300
        self.provider.fetch.side_effect=lambda now:[observed('L8',now,'Atividade Programada')]
        rows={r.line_code:r for r in self.cache.read('motiva',self.provider)}
        self.assertEqual(rows['L8'].label,'Atividade Programada')
        self.assertEqual(rows['L8'].validity,'current')
        self.assertEqual(rows['L9'].collected_at,NOW)
        self.assertEqual(rows['L9'].validity,'stale')

    def test_no_store_nao_grava_nova_observacao_e_nao_apaga_anterior_permitida(self):
        self.cache.read('fonte',self.provider);self.now+=300
        self.provider.fetch.side_effect=lambda now:cache_policy(
            [observed(now=now,label='Operação Parcial')],{'cache-control':'no-store'})
        self.assertEqual(self.cache.read('fonte',self.provider)[0].label,'Operação Parcial')
        previous=SharedStatusCache(self.path,lambda:self.now).read('fonte',self.provider)[0]
        self.assertEqual(previous.label,'Operação Normal')
        self.assertEqual(previous.collected_at,NOW)
        self.assertEqual(previous.validity,'stale')

    def test_consultas_simultaneas_mantem_ultimo_retorno_durante_atualizacao(self):
        self.cache.read('metro',self.provider);self.now+=300
        entered,release=Event(),Event()
        def delayed(now):
            entered.set()
            if not release.wait(3):
                raise ProviderFailure()
            return [observed(now=now,label='Operação Parcial')]
        self.provider.fetch.side_effect=delayed
        with ThreadPoolExecutor(2) as pool:
            updating=pool.submit(self.cache.read,'metro',self.provider)
            try:
                self.assertTrue(entered.wait(2))
                during=SharedStatusCache(self.path,lambda:self.now).read('metro',self.provider)[0]
                self.assertEqual(during.label,'Operação Normal')
                self.assertEqual(during.collected_at,NOW)
            finally:
                release.set()
            self.assertEqual(updating.result(timeout=2)[0].label,'Operação Parcial')
        self.assertEqual(self.provider.fetch.call_count,2)


class LastKnownScreenTests(TestCase):
    def setUp(self):
        self.state=LineStatusState(_reflex_internal_init=True)
        self.state.start()
        self.state.receive(dict(request_id=self.state._request_id,status=200,
            data=[observed().model_dump(),LineCondition(line_code='L6').model_dump()]))

    def test_consulta_em_andamento_preserva_cartoes_e_resposta_antiga_ignorada(self):
        before=[dict(r) for r in self.state.rows]
        old_id=self.state._request_id
        self.state.refresh()
        self.assertEqual(self.state.rows,before)
        self.state.receive(dict(request_id=old_id,status=200,data=[]))
        self.assertEqual(self.state.rows,before)

    def test_erros_vazio_e_indisponivel_preservam_ultimo_retorno_e_repeticao(self):
        original=self.state.rows[0]['collected']
        for status,data in ((503,None),(200,{'inválido':True}),(200,[]),
                            (200,[LineCondition(line_code='L8').model_dump()])):
            self.state.refresh()
            timer=self.state.receive(dict(request_id=self.state._request_id,status=status,data=data))
            self.assertIsNotNone(timer)
            rows={r['code']:r for r in self.state.rows}
            self.assertEqual(rows['L8']['label'],'Operação Normal')
            self.assertEqual(rows['L8']['collected'],original)
            self.assertEqual(rows['L8']['validity'],'Desatualizado')
            self.assertEqual(rows['L6']['validity'],'Indisponível')

    def test_novo_retorno_valido_substitui_sem_mudar_linhas_ausentes(self):
        self.state.refresh()
        self.state.receive(dict(request_id=self.state._request_id,status=200,
            data=[observed(now=NOW+300,label='Operação Parcial').model_dump()]))
        rows={r['code']:r for r in self.state.rows}
        self.assertEqual(rows['L8']['label'],'Operação Parcial')
        self.assertEqual(rows['L8']['validity'],'Atual na consulta')
        self.assertEqual(rows['L6']['validity'],'Indisponível')
