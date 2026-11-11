"""Compatibilidade IPv4 somente no quadro Metrô, preservando limites e TLS."""
import os
from unittest import TestCase
from unittest.mock import patch
import httpx
from MetroFlow.status.service import StatusService
from MetroFlow.status.providers import HttpProvider,ProviderFailure
from MetroFlow.status.metro_board import METRO_BOARD_URL,normalize_metro_board
from tests.unit.status.test_metro_board import row,NOW


class MetroTransportTests(TestCase):
    def test_fabrica_isola_ipv4_no_metro_sem_alterar_demais_fontes(self):
        with patch.dict(os.environ,{'METROFLOW_CPTM_ENABLED':'1',
                'METROFLOW_METRO_QUADRO_AUTORIZADO':'1','METROFLOW_MOTIVA_QUADRO_ENABLED':'1'},clear=True):
            providers={name:provider for name,_,provider in StatusService.from_environment().providers}
        self.assertEqual(providers['metro_board'].local_address,'0.0.0.0')
        self.assertIsNone(providers['cptm'].local_address)
        self.assertIsNone(providers['motiva_board'].local_address)
        self.assertEqual(providers['metro_board'].timeout,5)
        self.assertEqual(providers['metro_board'].read_timeout,15)
        self.assertEqual(providers['cptm'].read_timeout,2)
        self.assertEqual(providers['motiva_board'].read_timeout,5)

    def test_transporte_restrito_preserva_https_certificado_e_quadro_valido(self):
        requests=[]
        def handler(request):
            requests.append(request)
            self.assertEqual(request.extensions['timeout']['connect'],5)
            self.assertEqual(request.extensions['timeout']['read'],15)
            return httpx.Response(200,text='<ol>'+''.join(row(str(code)) for code in (1,2,3,4,5,15,17))+'</ol>')
        transport=httpx.MockTransport(handler)
        provider=HttpProvider(METRO_BOARD_URL,normalize_metro_board,response_format='html',
            local_address='0.0.0.0',timeout=5,read_timeout=15,total_timeout=20)
        with patch('MetroFlow.status.providers.httpx.HTTPTransport',return_value=transport) as factory:
            result=provider.fetch(NOW)
        factory.assert_called_once_with(local_address='0.0.0.0',trust_env=False,verify=True)
        self.assertEqual([r.line_code for r in result],['L1','L2','L3','L4','L5','L15','L17'])
        self.assertEqual(len(requests),1)
        self.assertEqual(requests[0].url.scheme,'https')
        self.assertEqual(requests[0].url.host,'www.metro.sp.gov.br')
        self.assertNotIn('Authorization',requests[0].headers)

    def test_timeout_identifica_etapa_sem_expor_mensagem_nem_repetir_get(self):
        for error,kind in ((httpx.ConnectTimeout,'connect_timeout'),(httpx.ReadTimeout,'read_timeout')):
            calls=[]
            def handler(request):
                calls.append(request)
                raise error('segredo-nao-deve-aparecer')
            provider=HttpProvider(METRO_BOARD_URL,normalize_metro_board,response_format='html',
                local_address='0.0.0.0',transport=httpx.MockTransport(handler))
            with patch('MetroFlow.status.providers.httpx.HTTPTransport') as transport_factory:
                with self.assertRaises(ProviderFailure) as caught:
                    provider.fetch(NOW)
            transport_factory.assert_not_called()
            self.assertEqual(caught.exception.kind,kind)
            self.assertNotIn('segredo',str(caught.exception))
            self.assertEqual(len(calls),1)
