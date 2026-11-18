"""Cliente do grupo `administracao` do Xano com transporte simulado."""

import json
from unittest.mock import patch

import httpx
import pytest

from MetroFlow.admin.infrastructure.xano_client import (
    DEFAULT_XANO_ADMIN_API_BASE_URL,
    AdminError,
    AdminForbidden,
    AdminNotFound,
    AdminUnauthorized,
    AdminUnavailable,
    XanoAdminClient,
)


BASE_URL = "https://example.xano.io/api:admin"
TOKEN = "token-administrativo-sensivel"
INDICATORS = {
    "apurado_em": 1_763_316_000_000,
    "uso": {"rotas_ativas": 2, "usuarios_em_viagem": 2, "usuarios_uso_recente": 5, "contas_habilitadas": 9},
    "malha": {"estacoes_ativas": 180, "estacoes_inativas": 2, "linhas_ativas": 16, "trechos_ativos": 207},
    "volume": {"viagens_hoje": 3, "viagens_7_dias": 20},
    "ranking_estacoes": [{"id": 1, "nome": "Sé", "codigo": "SE", "usos": 6}],
    "lotacao": {"trechos_lotados": 1, "minimo_usuarios": 2, "percentual_lotacao": 50},
}


def client_for(handler) -> XanoAdminClient:
    return XanoAdminClient(BASE_URL, transport=httpx.MockTransport(handler))


def respond(status: int, payload: object = None):
    return lambda _request: httpx.Response(status, json=payload)


def test_indicadores_enviam_token_somente_no_cabecalho_e_decodificam_a_resposta() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api:admin/admin/indicadores"
        assert TOKEN not in str(request.url)
        assert request.headers["Authorization"] == f"Bearer {TOKEN}"
        return httpx.Response(200, json=INDICATORS)

    with client_for(handler) as client:
        result = client.indicators(TOKEN)

    assert result.active_routes == 2
    assert result.inactive_stations == 2
    assert result.ranking[0].name == "Sé"
    assert result.crowding.percentage == 50.0


def test_lotacao_indisponivel_e_decodificada_como_vazia() -> None:
    payload = {**INDICATORS, "lotacao": {"trechos_lotados": None, "minimo_usuarios": None, "percentual_lotacao": None}}

    with client_for(respond(200, payload)) as client:
        result = client.indicators(TOKEN)

    assert result.crowding.available is False


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({**INDICATORS, "uso": None}, id="secao-ausente"),
        pytest.param({**INDICATORS, "uso": {**INDICATORS["uso"], "rotas_ativas": "2"}}, id="texto"),
        pytest.param({**INDICATORS, "uso": {**INDICATORS["uso"], "rotas_ativas": True}}, id="booleano"),
        pytest.param({**INDICATORS, "uso": {**INDICATORS["uso"], "rotas_ativas": -1}}, id="negativo"),
        pytest.param({**INDICATORS, "ranking_estacoes": ["Sé"]}, id="ranking-invalido"),
        pytest.param({**INDICATORS, "lotacao": {"trechos_lotados": 1, "minimo_usuarios": None, "percentual_lotacao": None}}, id="lotacao-incompleta"),
        pytest.param([], id="lista"),
    ],
)
def test_indicadores_fora_do_contrato_sao_rejeitados(payload) -> None:
    with client_for(respond(200, payload)) as client, pytest.raises(AdminError):
        client.indicators(TOKEN)


def test_estacoes_incluem_inativas_e_linhas() -> None:
    payload = {
        "estacoes": [
            {"id": 4, "nome": "Brás", "codigo": "BRS", "ativa": False, "linhas": [{"id": 3, "nome": "Vermelha", "codigo": "L3", "cor": None}]},
            {"id": 1, "nome": "Sé", "codigo": "SE", "ativa": True, "linhas": []},
        ]
    }

    with client_for(respond(200, payload)) as client:
        stations = client.stations(TOKEN)

    assert [(item.id, item.active) for item in stations] == [(4, False), (1, True)]
    assert stations[0].lines[0].code == "L3"


@pytest.mark.parametrize(
    "station",
    [
        {"id": 1, "nome": "Sé", "codigo": "SE", "ativa": None, "linhas": []},
        {"id": 1, "nome": "", "codigo": "SE", "ativa": True, "linhas": []},
        {"id": 0, "nome": "Sé", "codigo": "SE", "ativa": True, "linhas": []},
        {"id": 1, "nome": "Sé", "codigo": "SE", "ativa": True, "linhas": "L1"},
    ],
)
def test_estacao_fora_do_contrato_e_rejeitada(station) -> None:
    with client_for(respond(200, {"estacoes": [station]})) as client, pytest.raises(AdminError):
        client.stations(TOKEN)


def test_alteracao_envia_somente_estacao_e_situacao() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api:admin/admin/estacoes/situacao"
        assert json.loads(request.content) == {"estacao_id": 7, "ativa": False}
        return httpx.Response(200, json={"id": 7, "ativa": False})

    with client_for(handler) as client:
        status = client.set_station_status(7, False, TOKEN)

    assert (status.id, status.active) == (7, False)


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (401, AdminUnauthorized),
        (403, AdminForbidden),
        (404, AdminNotFound),
        (429, AdminUnavailable),
        (500, AdminUnavailable),
        (400, AdminError),
    ],
)
def test_codigos_http_sao_distinguidos(status: int, expected: type[Exception]) -> None:
    with client_for(respond(status, {"message": "detalhe interno"})) as client:
        with pytest.raises(expected) as raised:
            client.set_station_status(7, True, TOKEN)

    assert "detalhe interno" not in str(raised.value)
    assert TOKEN not in str(raised.value)


def test_401_e_403_nao_se_confundem() -> None:
    assert not issubclass(AdminForbidden, AdminUnauthorized)
    assert not issubclass(AdminUnauthorized, AdminForbidden)


def test_indisponibilidade_de_rede() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("falha", request=request)

    with client_for(handler) as client, pytest.raises(AdminUnavailable):
        client.indicators(TOKEN)


def test_resposta_que_nao_e_json_e_rejeitada() -> None:
    with client_for(lambda _request: httpx.Response(200, text="<html>")) as client:
        with pytest.raises(AdminError):
            client.stations(TOKEN)


def test_sem_token_nao_chama_o_xano() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        raise AssertionError("O Xano não deveria ser chamado.")

    with client_for(handler) as client, pytest.raises(AdminUnauthorized):
        client.indicators("")


def test_configuracao_por_variavel_de_ambiente() -> None:
    with patch.dict("os.environ", {"XANO_ADMIN_API_BASE_URL": "https://outro.xano.io/api:x/"}):
        with XanoAdminClient.from_environment() as client:
            assert str(client._http.base_url) == "https://outro.xano.io/api:x/"

    with patch.dict("os.environ", {"XANO_ADMIN_API_BASE_URL": ""}):
        with XanoAdminClient.from_environment() as client:
            assert str(client._http.base_url) == f"{DEFAULT_XANO_ADMIN_API_BASE_URL}/"


@pytest.mark.parametrize("first", ["timeout", "network", "protocol", 502, 503, 504])
def test_get_recupera_uma_falha_transitoria_sem_expor_credencial(first):
    calls = []
    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            errors = {"timeout": httpx.ReadTimeout, "network": httpx.ConnectError,
                      "protocol": httpx.RemoteProtocolError}
            if first in errors:
                raise errors[first](TOKEN, request=request)
            return httpx.Response(first)
        return httpx.Response(200, json=INDICATORS)
    with patch("MetroFlow.admin.infrastructure.xano_client.time.sleep") as pause:
        with client_for(handler) as client:
            assert client.indicators(TOKEN).active_routes == 2
    assert len(calls) == 2
    pause.assert_called_once_with(1.0)
    assert all(TOKEN not in str(r.url) for r in calls)


def test_get_persistente_para_apos_duas_tentativas():
    calls = []
    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout(TOKEN, request=request)
    with patch("MetroFlow.admin.infrastructure.xano_client.time.sleep"):
        with client_for(handler) as client, pytest.raises(AdminUnavailable) as error:
            client.indicators(TOKEN)
    assert len(calls) == 2
    assert TOKEN not in str(error.value)


@pytest.mark.parametrize("status, headers, error", [
    (401, {}, AdminUnauthorized), (403, {}, AdminForbidden),
    (429, {"Retry-After": "60"}, AdminUnavailable),
    (503, {"Retry-After": "30"}, AdminUnavailable),
    (200, {}, AdminError),
])
def test_get_nao_repete_rejeicao_limite_retry_after_ou_contrato(status, headers, error):
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(status, json={}, headers=headers)
    with patch("MetroFlow.admin.infrastructure.xano_client.time.sleep") as pause:
        with client_for(handler) as client, pytest.raises(error):
            client.indicators(TOKEN)
    assert len(calls) == 1
    pause.assert_not_called()


def test_revogacao_na_segunda_tentativa_bloqueia_acesso():
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(503 if len(calls) == 1 else 403)
    with patch("MetroFlow.admin.infrastructure.xano_client.time.sleep"):
        with client_for(handler) as client, pytest.raises(AdminForbidden):
            client.indicators(TOKEN)
    assert len(calls) == 2


@pytest.mark.parametrize("failure", ["timeout", 503])
def test_post_nunca_e_repetido_automaticamente(failure):
    calls = []
    def handler(request):
        calls.append(request)
        if failure == "timeout":
            raise httpx.ReadTimeout(TOKEN, request=request)
        return httpx.Response(failure)
    with patch("MetroFlow.admin.infrastructure.xano_client.time.sleep") as pause:
        with client_for(handler) as client, pytest.raises(AdminUnavailable):
            client.set_station_status(7, False, TOKEN)
    assert len(calls) == 1
    pause.assert_not_called()
