"""Contrato opcional: alcance parcial, soma e bloqueio de envio remoto."""
from dataclasses import replace
import json

import httpx
import pytest
from pydantic import ValidationError

from MetroFlow.planning.domain.models import (
    CalibrationReference, Line, Operator, RouteResult, Segment, Station, Transfer, TripConfirmation, TripSegment,
)
from MetroFlow.planning.infrastructure.xano_client import PlanningError, XanoPlanningClient
from MetroFlow.planning.presentation.view_models import RouteView, TripConfirmationRequest
from MetroFlow.planning.presentation.state import PlanningState


def route():
    line = Line(9, 'Linha 10', 'L10', None, Operator(1, 'CPTM', 'CPTM'))
    a, b, c = [Station(i, str(i), str(i)) for i in [1, 2, 3]]
    patterns = ('l10:tronco:1', 'l10:integral:1')
    steps = (Segment(1, a, b, line, 120, waiting_time_seconds=180, train_pattern=patterns[0], transfer_before_seconds=0),
        Segment(2, b, c, line, 150, waiting_time_seconds=360, train_pattern=patterns[1], transfer_before_seconds=300))
    return RouteResult(a, c, (a, b, c), steps, (Transfer(b, line, line),), 1110, calculated_at_ms=1793791800000,
        calibration=CalibrationReference('a'*64, patterns))


def test_parcial_muda_trem_sem_mudar_linha_e_valida_soma():
    r = route(); v = RouteView.from_route(r)
    assert v.transfer_count == 1 and v.seconds == 1110
    assert v.calibration.patterns == ['l10:tronco:1', 'l10:integral:1']
    assert v.transfers == ['Em 2: troque de trem na Linha 10']
    with pytest.raises(ValueError): replace(r, total_time_seconds=1170)
    with pytest.raises(ValueError): replace(r, calibration=None)


def test_caminhada_pode_cobrir_troca_sem_penalidade_duplicada():
    r = route(); s = replace(r.segments[1], transfer_before_seconds=0)
    v = replace(r, segments=(r.segments[0], s), total_time_seconds=810)
    assert RouteView.from_route(v).transfer_count == 1


def test_margem_altera_somente_estimativa_publica():
    original = route()
    adjusted = replace(original, public_estimate_seconds=1170)
    assert adjusted.total_time_seconds == 1110
    assert adjusted.segments == original.segments
    assert adjusted.calibration == original.calibration
    assert RouteView.from_route(adjusted).seconds == 1170
    assert adjusted.display_minutes == original.display_minutes + 1
    with pytest.raises(ValueError):
        replace(original, public_estimate_seconds=1230)


@pytest.mark.parametrize('change', [
    dict(calculated_at_ms=None), dict(calibration=CalibrationReference('a'*64, ('um',))),
    dict(segments=(replace(route().segments[0], transfer_before_seconds=1), route().segments[1])),
])
def test_cronologia_incompleta_rejeitada(change):
    with pytest.raises(ValueError): replace(route(), **change)


@pytest.mark.parametrize('host', ['https://example.xano.io/api:planejamento', 'http://localhost.example.com', 'http://192.168.1.2'])
def test_calibracao_experimental_exige_loopback(host):
    with pytest.raises(ValueError): XanoPlanningClient(host, calibration_enabled=True)


def test_cliente_padrao_nao_envia_registro_calibrado():
    calls = []
    trip = TripConfirmation((TripSegment(1, 1, 2),), 1793791800000, CalibrationReference('a'*64, ('um',)))
    with XanoPlanningClient('https://example.xano.io/api', transport=httpx.MockTransport(lambda q: calls.append(q))) as client:
        with pytest.raises(PlanningError): client.confirm_trip(trip, 'token-simulado')
    assert calls == []


def test_cliente_oficial_negocia_calibracao_sem_alterar_sessao():
    calls = []

    def transport(request):
        calls.append(request)
        if request.method == "GET":
            return httpx.Response(200, json={"estacoes": []})
        if request.url.path.endswith("/buscar"):
            return httpx.Response(404, json={})
        return httpx.Response(200, json={"confirmada": True})

    trip = TripConfirmation((TripSegment(1, 1, 2),), 1793791800000, CalibrationReference("a"*64, ("um",)))
    with XanoPlanningClient(
        "https://x8ki-letl-twmt.n7.xano.io/api:metroflow-planejamento",
        calibration_enabled=True,
        transport=httpx.MockTransport(transport),
    ) as client:
        assert client.list_active_stations("sessao-simulada") == ()
        assert client.find_route(1, 2, "sessao-simulada") is None
        client.confirm_trip(trip, "sessao-simulada")

    assert calls[0].url.params["suporta_calibracao"] == "true"
    assert json.loads(calls[1].content)["suporta_calibracao"] is True
    assert json.loads(calls[2].content)["versao_calibracao"] == "a"*64
    assert all(r.headers["Authorization"] == "Bearer sessao-simulada" for r in calls)


def test_cliente_local_envia_referencia_sem_tempos_ou_usuario():
    calls = []
    def transport(q):
        calls.append(json.loads(q.content)); return httpx.Response(200, json={'confirmada': True})
    trip = TripConfirmation((TripSegment(1, 1, 2),), 1793791800000, CalibrationReference('a'*64, ('um',)))
    with XanoPlanningClient('http://127.0.0.1/api', calibration_enabled=True, transport=httpx.MockTransport(transport)) as client:
        client.confirm_trip(trip, 'token-simulado')
    assert calls == [dict(trechos=[dict(id=1, estacao_origem_id=1, estacao_destino_id=2)], calculado_em=1793791800000, versao_calibracao='a'*64, padroes_experimentais=['um'])]


def test_pedido_publico_rejeita_tempo_e_referencia_desconexa():
    base = dict(segments=[dict(id=1, origin_id=1, destination_id=2)], calculated_at_ms=1793791800000,
        calibration=dict(version='a'*64, patterns=['um']))
    assert TripConfirmationRequest.model_validate(base).calibration.reference().version == 'a'*64
    for extra in [dict(tempo_total_segundos=1), dict(calculated_at_ms=None), dict(calibration=dict(version='a'*64, patterns=['um', 'dois']))]:
        with pytest.raises(ValidationError): TripConfirmationRequest.model_validate(dict(base, **extra))


def test_estado_transporta_referencia_sem_exibir_identificador():
    v = RouteView.from_route(route()); state = PlanningState(_reflex_internal_init=True)
    state.origin_id = '1'; state.destination_id = '3'
    event = state.receive_route(dict(request_id=state._request_id, status=200, ok=True, data=v.model_dump()))
    script = event.args[0][1]._var_value
    assert 'calibration' in script and 'a'*64 in script
    assert 'a'*64 not in str(state.instructions)
    assert state.route_status == 'success'


def test_corredor_e_trem_com_mesma_linha_nao_criam_troca_duplicada():
    line=Line(4,'Amarela','L4',None,Operator(1,'Motiva','M'))
    a,b,c=[Station(i,str(i),str(i)) for i in [1,2,3]]
    patterns=('walk:4','regular:4')
    steps=(Segment(1,a,b,line,300,segment_type='transferencia',train_pattern=patterns[0],transfer_before_seconds=0),
        Segment(2,b,c,line,100,waiting_time_seconds=120,train_pattern=patterns[1],transfer_before_seconds=0))
    r=RouteResult(a,c,(a,b,c),steps,(),520,calculated_at_ms=1793791800000,calibration=CalibrationReference('a'*64,patterns))
    assert RouteView.from_route(r).transfer_count==0
