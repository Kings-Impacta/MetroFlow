"""Resumo e embarques acompanham as linhas reais, inclusive em alternativas."""
from unittest import TestCase
import json
from tests.unit.planning.test_state import ROUTE
from MetroFlow.planning.presentation.state import PlanningState
from MetroFlow.planning.presentation.pages import _result
from MetroFlow.status.domain import LineCondition
from MetroFlow.status.presentation import LineStatusState, status_panel


class CompactRouteTests(TestCase):
    def route(self, codes):
        state=PlanningState(_reflex_internal_init=True)
        segments=[dict(id=i,origin_id=i,destination_id=i+1,origin=f'Estação {i}',
            destination=f'Estação {i+1}',line=code or 'Integração a pé',line_code=code,
            operator='Metrô',seconds=120,segment_type='ferroviario' if code else 'transferencia')
            for i,code in enumerate(codes,1)]
        state.receive_route(dict(request_id=state._request_id,status=200,ok=True,data=dict(
            origin='Estação 1',destination=f'Estação {len(codes)+1}',
            stations=[f'Estação {i}' for i in range(1,len(codes)+2)],
            seconds=len(codes)*120,minutes=len(codes)*2,transfer_count=max(0,len(codes)-1),
            segments=segments,transfers=[])))
        self.assertEqual(state.route_status,'success')
        return state

    def test_resumo_unico_na_ordem_e_codigo_correto_em_cada_embarque(self):
        for codes,summary,boardings in (
            (['L3','L1'],['L3','L1'],['L3','L1']),
            (['L3','L3','L4',None,'L2','L3'],['L3','L4','L2'],['L3','L4','L2','L3']),
            (['L8'],['L8'],['L8']),
            (['L6','L13'],['L6','L13'],['L6','L13']),
        ):
            with self.subTest(codes=codes):
                state=self.route(codes)
                self.assertEqual(state.route_line_codes,summary)
                self.assertEqual([r['line_code'] for r in state.instructions if r['kind']=='EMBARQUE'],boardings)
                self.assertTrue(all(r['line_code']=='' for r in state.instructions if r['kind']!='EMBARQUE'))

    def test_cor_operacional_e_texto_de_dado_antigo_sem_inventar_normalidade(self):
        state=LineStatusState(_reflex_internal_init=True)
        state.refresh()
        state.receive(dict(request_id=state._request_id,status=200,data=[
            LineCondition(line_code='L3',situation='normal',label='Operação Normal',validity='current').model_dump(),
            LineCondition(line_code='L4',situation='restricted',label='Velocidade Reduzida',validity='stale').model_dump(),
            LineCondition(line_code='L2',situation='interrupted',label='Operação Interrompida',validity='current').model_dump(),
            LineCondition(line_code='L13').model_dump()]))
        indicators=state.indicators
        self.assertEqual(indicators['L3']['color'],'#15803d')
        self.assertEqual(indicators['L2']['color'],'#dc2626')
        self.assertEqual(indicators['L4']['label'],'Velocidade Reduzida')
        self.assertEqual(state.rows[1]['validity'],'Desatualizado')
        self.assertEqual(indicators['L13']['label'],'Status indisponível')
        self.assertEqual(indicators['L13']['color'],'#64748b')

    def test_contrato_legado_sem_codigo_mantem_nome_sem_inferir_status(self):
        state=PlanningState(_reflex_internal_init=True)
        state.receive_route(dict(request_id=state._request_id,status=200,ok=True,data=ROUTE))
        self.assertEqual(state.route_line_codes,['Azul'])
        self.assertEqual([r['line_code'] for r in state.instructions if r['kind']=='EMBARQUE'],['Azul'])

    def test_resultado_compacto_sem_painel_detalhado_e_pagina_geral_preservada(self):
        def text_nodes(value):
            if isinstance(value,dict):
                content=value.get('contents','')
                if content.startswith('"'):
                    yield json.loads(content)
                for child in value.values():
                    yield from text_nodes(child)
            elif isinstance(value,list):
                for child in value:
                    yield from text_nodes(child)
        rendered=list(text_nodes(_result().render()))
        self.assertIn('LINHAS DO TRAJETO',rendered)
        self.assertNotIn('Condições operacionais das linhas',rendered)
        self.assertNotIn('Atualizar condições',rendered)
        self.assertIn('Condições operacionais das linhas',list(text_nodes(status_panel().render())))
