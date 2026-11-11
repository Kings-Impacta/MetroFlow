from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, patch
import os
from MetroFlow.status.service import StatusService
from MetroFlow.status.providers import ProviderFailure
from MetroFlow.status.domain import LineCondition
from MetroFlow.status.metro_board import BRASILIA
from MetroFlow.status.motiva_board import normalize_motiva_board

NOW = datetime(2026,11,9,23,0,tzinfo=BRASILIA).timestamp()


def post(date='09/11/2026 às 16:21:37',label='Operação Normal',description=''):
    return f'<div class="block-post-list-container__post-item"><p class="post-time">{date}</p><h2 class="post-title">{label}</h2><div class="post-description"><p>{description}</p></div></div>'


def board(first=None, second=None):
    return ('<li role="tab" id="a">8 - Diamante</li><li role="tab" id="b">9 - Esmeralda</li>'
            f'<div role="tabpanel" aria-labelledby="b">{second or post()}</div>'
            f'<div role="tabpanel" aria-labelledby="a">{first or post()}</div>')


class MotivaBoardTests(TestCase):
    def test_ativacao_explicita_e_falha_isolada_preservam_cobertura_das_outras_fontes(self):
        with patch.dict(os.environ,{},clear=True):
            self.assertEqual(StatusService.from_environment().providers,[])
        with patch.dict(os.environ,{'METROFLOW_MOTIVA_QUADRO_ENABLED':'1'},clear=True):
            providers=StatusService.from_environment().providers
        self.assertEqual([p[0] for p in providers],['motiva_board'])
        cache=Mock()
        cache.read.side_effect=[
            [LineCondition(line_code='L1',label='Operação Normal',validity='current')],
            [LineCondition(line_code='L10',label='Operação Normal',validity='current')],
            ProviderFailure()]
        with self.assertLogs('MetroFlow.status.service',level='WARNING'):
            result={r.line_code:r for r in StatusService(cache,[('metro_board','m',None),
                ('cptm','c',None),('motiva_board','v',None)]).conditions()}
        self.assertEqual(result['L1'].validity,'current')
        self.assertEqual(result['L10'].validity,'current')
        self.assertTrue(all(result[code].validity=='unavailable' for code in ('L6','L7','L8','L9','L13')))

    def test_linha_vem_da_aba_e_ultima_ocorrencia_da_data_nao_ordem(self):
        rows={r.line_code:r for r in normalize_motiva_board(board(
            post('09/11/2026 às 10:00:00','Atividade Programada','Manutenção antiga')+post(),
            post(label='Operação Parcial',description='Trecho &amp; intervalo')),NOW)}
        self.assertEqual(rows['L8'].situation,'normal')
        self.assertEqual(rows['L8'].description,'')
        self.assertEqual(rows['L9'].situation,'restricted')
        self.assertEqual(rows['L9'].description,'Trecho & intervalo')
        self.assertEqual(rows['L8'].updated_at,datetime(2026,11,9,16,21,37,tzinfo=BRASILIA).timestamp())
        self.assertEqual(rows['L8'].collected_at,NOW)

    def test_mudanca_antiga_nao_significa_coleta_antiga(self):
        row=normalize_motiva_board(board(post('01/11/2026 às 04:00:00')),NOW)[1]
        self.assertEqual(row.aged(NOW).validity,'current')
        self.assertEqual(row.aged(NOW+601).validity,'stale')
        self.assertEqual(row.aged(NOW,True).validity,'stale')

    def test_estrutura_incompleta_datas_futuras_e_empates_conflitantes_falham(self):
        for payload in ('',board().replace('9 - Esmeralda','7 - Rubi'),
                        board().replace('9 - Esmeralda','9 - Diamante'),
                        board().replace('aria-labelledby="a"','aria-labelledby="b"'),
                        board(post('10/11/2026 às 04:00:00')),
                        board(post()+post(label='Operação Parcial')),
                        board().replace('post-title','titulo-desconhecido')):
            with self.subTest(payload=payload[:100]),self.assertRaises(ValueError):
                normalize_motiva_board(payload,NOW)
