"""Executa as funções propostas de confirmação e lotação com viagens controladas.

Malha usada nos testes:

    1 --(trecho 1, L1, 100 s)--> 2 --(trecho 2, L1, 100 s)--> 4
    1 --(trecho 3, L2, 150 s)--> 3 --(trecho 4, L2, 150 s)--> 4
                                 3 --(trecho 5, L1, 50 s)---> 2

O trajeto principal de 1 a 4 é 1-2-4 (200 s); a alternativa direta é 1-3-4.
"""

import pytest

from tests.unit.planning.xano_lambda import XANO_DRAFTS, requires_node, run_lambda


DRAFTS = XANO_DRAFTS / "concorrencia-rotas"
SEARCH_SCRIPT = DRAFTS / "trajetos_buscar_post.xs"
CONFIRM_SCRIPT = DRAFTS / "viagens_confirmar_post.xs"
pytestmark = requires_node

T0 = 1_760_000_000_000
SEARCHER = 99
PRIMARY = [1, 2, 4]
ALTERNATIVE = [1, 3, 4]
CONFIG = {"minimo_usuarios": 1, "percentual_lotacao": 50}


def _segment(
    identifier: int,
    origin: int,
    destination: int,
    line: int,
    seconds: int,
    *,
    kind: str = "ferroviario",
    service: int | None = None,
    directed: bool = False,
) -> dict[str, object]:
    return {
        "id": identifier,
        "estacao_origem_id": origin,
        "estacao_destino_id": destination,
        "linha_id": line,
        "tempo_estimado": seconds,
        "tipo": kind,
        "direcionado": directed,
        "servico_id": service,
    }


def _segments(**overrides: dict[str, object]) -> list[dict[str, object]]:
    segments = [
        _segment(1, 1, 2, 1, 100),
        _segment(2, 2, 4, 1, 100),
        _segment(3, 1, 3, 2, 150),
        _segment(4, 3, 4, 2, 150),
        _segment(5, 3, 2, 1, 50),
    ]
    for segment in segments:
        segment.update(overrides.get(f"t{segment['id']}", {}))
    return segments


def _line(identifier: int) -> dict[str, object]:
    return {
        "id": identifier,
        "nome": f"Linha {identifier}",
        "codigo": f"L{identifier}",
        "cor": None,
        "operador_id": 1,
        "operador_nome": "Operador de teste",
        "operador_codigo": "TESTE",
        "sentido_ordem_crescente": None,
        "sentido_ordem_decrescente": None,
    }


def _confirm(
    steps: list[object],
    *,
    now: int = T0,
    segments: list[dict[str, object]] | None = None,
) -> dict[str, object] | None:
    requested = [
        {"id": step[0], "estacao_origem_id": step[1], "estacao_destino_id": step[2]}
        if isinstance(step, tuple)
        else step
        for step in steps
    ]
    result = run_lambda(
        CONFIRM_SCRIPT,
        {
            "agora": now,
            "trechos_confirmados": requested,
            "trechos": segments or _segments(),
        },
    )
    assert result is None or isinstance(result, dict)
    return result


def _trip(
    identifier: int,
    user: int,
    steps: list[tuple[int, int, int]],
    *,
    start: int = T0,
    replaced: bool = False,
    segments: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    confirmed = _confirm(steps, now=start, segments=segments)
    assert confirmed is not None
    return {
        "id": identifier,
        "usuario_id": user,
        "confirmada_em": start,
        "fim_janela": confirmed["fim_janela"],
        "substituida": replaced,
        "trechos": confirmed["trechos"],
    }


def _search(
    trips: list[dict[str, object]],
    now: int,
    *,
    config: dict[str, object] | None = CONFIG,
    user: int = SEARCHER,
    origin: int = 1,
    destination: int = 4,
    segments: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    result = run_lambda(
        SEARCH_SCRIPT,
        {
            "origem_id": origin,
            "destino_id": destination,
            "estacoes": [
                {"id": 1, "nome": "Origem", "codigo": "O"},
                {"id": 2, "nome": "Caminho A", "codigo": "A"},
                {"id": 3, "nome": "Caminho B", "codigo": "B"},
                {"id": 4, "nome": "Destino", "codigo": "D"},
            ],
            "linhas": [_line(1), _line(2)],
            "estacoes_linhas": [],
            "trechos": segments or _segments(),
            "agora": now,
            "usuario_id": user,
            "viagens": trips,
            "configuracao": config,
        },
    )
    assert isinstance(result, dict)
    return result


def _path(result: dict[str, object]) -> list[int]:
    return [station["id"] for station in result["estacoes"]]


def _seconds(value: int) -> int:
    return T0 + value * 1000


ON_PRIMARY = [(1, 1, 2), (2, 2, 4)]
ELSEWHERE = [(4, 4, 3)]


# Confirmação e janela da viagem


def test_janela_soma_os_trechos_sem_penalidade_de_baldeacao() -> None:
    confirmed = _confirm([(3, 1, 3), (5, 3, 2), (2, 2, 4)])

    assert confirmed is not None
    assert confirmed["fim_janela"] == _seconds(300)
    assert [step["tempo_estimado"] for step in confirmed["trechos"]] == [150, 50, 100]
    assert [step["ordem"] for step in confirmed["trechos"]] == [1, 2, 3]


def test_confirmacao_usa_tempo_cadastrado_e_sentido_percorrido() -> None:
    confirmed = _confirm(
        [
            {"id": 2, "estacao_origem_id": 4, "estacao_destino_id": 2, "tempo_estimado": 1},
            (1, 2, 1),
        ]
    )

    assert confirmed is not None
    assert [
        (step["trecho_id"], step["estacao_origem_id"], step["estacao_destino_id"], step["tempo_estimado"])
        for step in confirmed["trechos"]
    ] == [(2, 4, 2, 100), (1, 2, 1, 100)]
    assert confirmed["fim_janela"] == _seconds(200)


@pytest.mark.parametrize(
    "steps",
    [
        pytest.param([], id="sem-trechos"),
        pytest.param([(1, 1, 2), (4, 3, 4)], id="trechos-nao-consecutivos"),
        pytest.param([(99, 1, 2)], id="trecho-inexistente-ou-inativo"),
        pytest.param([(1, 1, 3)], id="estacoes-diferentes-do-cadastro"),
        pytest.param([(1, 1, 1)], id="extremos-iguais"),
        pytest.param([{"id": "1", "estacao_origem_id": 1, "estacao_destino_id": 2}], id="id-nao-inteiro"),
        pytest.param([(0, 1, 2)], id="id-nao-positivo"),
        pytest.param([(1, 1, 2), (1, 2, 1)] * 101, id="mais-de-200-trechos"),
    ],
)
def test_confirmacao_rejeita_trajeto_invalido(steps: list[object]) -> None:
    assert _confirm(steps) is None


def test_confirmacao_rejeita_sentido_inverso_de_trecho_direcionado() -> None:
    segments = _segments(t1={"direcionado": True})

    assert _confirm([(1, 1, 2)], segments=segments) is not None
    assert _confirm([(1, 2, 1)], segments=segments) is None


# Intervalo estimado em cada trecho


def test_intervalo_do_trecho_ignora_penalidade_de_baldeacao() -> None:
    # A viagem muda de linha em 3; o trecho 2 é ocupado entre 200 e 300 s.
    trip = _trip(1, 1, [(3, 1, 3), (5, 3, 2), (2, 2, 4)])

    assert _path(_search([trip], _seconds(250))) == ALTERNATIVE
    assert _path(_search([trip], _seconds(150))) == PRIMARY


def test_trecho_ainda_nao_alcancado_nao_conta() -> None:
    # Percorre 3 -> 1 (150 s) antes de ocupar 1 -> 2 entre 150 e 250 s.
    trip = _trip(1, 1, [(3, 3, 1), (1, 1, 2)])

    assert _path(_search([trip], _seconds(100), destination=2)) == [1, 2]
    assert _path(_search([trip], _seconds(200), destination=2)) == [1, 3, 2]


def test_trecho_ja_percorrido_nao_conta() -> None:
    trip = _trip(1, 1, ON_PRIMARY)

    assert _path(_search([trip], _seconds(50), destination=2)) == [1, 3, 2]
    assert _path(_search([trip], _seconds(150), destination=2)) == [1, 2]


def test_viagem_deixa_de_contar_no_fim_da_janela() -> None:
    trip = _trip(1, 1, ON_PRIMARY)

    assert trip["fim_janela"] == _seconds(200)
    assert _path(_search([trip], _seconds(200) - 1)) == ALTERNATIVE
    assert _path(_search([trip], _seconds(200))) == PRIMARY


# Uma viagem ativa por usuário


def test_viagem_substituida_deixa_de_contar_imediatamente() -> None:
    active = _trip(1, 1, ON_PRIMARY)
    replaced = _trip(1, 1, ON_PRIMARY, replaced=True)

    assert _path(_search([active], _seconds(50))) == ALTERNATIVE
    assert _path(_search([replaced], _seconds(50))) == PRIMARY


def test_somente_a_viagem_mais_recente_do_usuario_conta() -> None:
    # Duas confirmações concorrentes ainda não marcadas como substituídas.
    older = _trip(1, 1, ON_PRIMARY)
    newer = _trip(2, 1, [(3, 1, 3), (4, 3, 4)], start=_seconds(10))

    assert _path(_search([older, newer], _seconds(50))) == PRIMARY


def test_reconfirmar_o_mesmo_trajeto_reinicia_a_janela() -> None:
    first = _trip(1, 1, ON_PRIMARY, replaced=True)
    second = _trip(2, 1, ON_PRIMARY, start=_seconds(150))

    assert second["fim_janela"] == _seconds(350)
    assert second["fim_janela"] > first["fim_janela"]
    # A primeira janela já terminou; a nova ocupa o trecho 1 entre 150 e 250 s.
    assert _path(_search([first, second], _seconds(210), destination=2)) == [1, 3, 2]


# Critério de lotação


@pytest.mark.parametrize(
    ("on_primary", "elsewhere", "minimum", "expected"),
    [
        pytest.param(2, 2, 2, ALTERNATIVE, id="minimo-e-percentual-iguais-aos-parametros"),
        pytest.param(3, 1, 2, ALTERNATIVE, id="minimo-e-percentual-superados"),
        pytest.param(1, 0, 2, PRIMARY, id="percentual-sem-minimo"),
        pytest.param(2, 3, 2, PRIMARY, id="minimo-sem-percentual"),
        pytest.param(2, 2, 3, PRIMARY, id="minimo-alterado-na-configuracao"),
    ],
)
def test_lotacao_exige_minimo_e_percentual(
    on_primary: int,
    elsewhere: int,
    minimum: int,
    expected: list[int],
) -> None:
    trips = [_trip(user, user, ON_PRIMARY) for user in range(1, on_primary + 1)]
    trips += [
        _trip(user, user, ELSEWHERE)
        for user in range(on_primary + 1, on_primary + elsewhere + 1)
    ]
    config = {"minimo_usuarios": minimum, "percentual_lotacao": 50}

    assert _path(_search(trips, _seconds(50), config=config)) == expected


def test_sentidos_do_mesmo_trecho_sao_avaliados_separadamente() -> None:
    trips = [_trip(user, user, [(1, 2, 1)]) for user in (1, 2, 3)]

    assert _path(_search(trips, _seconds(50))) == PRIMARY
    assert _path(_search(trips, _seconds(50), origin=2, destination=1)) == [2, 3, 1]


@pytest.mark.parametrize(
    "config",
    [
        pytest.param(None, id="sem-configuracao"),
        pytest.param({"minimo_usuarios": 0, "percentual_lotacao": 50}, id="minimo-zero"),
        pytest.param({"minimo_usuarios": 1, "percentual_lotacao": 0}, id="percentual-zero"),
        pytest.param({"minimo_usuarios": 1, "percentual_lotacao": 150}, id="percentual-acima-de-100"),
    ],
)
def test_configuracao_ausente_ou_invalida_nao_marca_lotacao(config: object) -> None:
    trip = _trip(1, 1, ON_PRIMARY)

    assert _path(_search([trip], _seconds(50), config=config)) == PRIMARY


# Trechos considerados na lotação


@pytest.mark.parametrize(
    "override",
    [
        pytest.param({"tipo": "transferencia"}, id="integracao-a-pe"),
        pytest.param({"servico_id": 7}, id="servico-especial"),
    ],
)
def test_trecho_nao_ferroviario_nunca_fica_lotado(override: dict[str, object]) -> None:
    segments = _segments(t1=override)
    trips = [_trip(user, user, ON_PRIMARY, segments=segments) for user in (1, 2, 3)]

    assert trips[0]["trechos"][0]["tipo"] == override.get("tipo", "ferroviario")
    assert _path(_search(trips, _seconds(50), segments=segments)) == PRIMARY


def test_tempo_da_integracao_a_pe_conta_na_janela_e_nos_intervalos() -> None:
    segments = _segments(t3={"tipo": "transferencia"})
    trip = _trip(1, 1, [(3, 1, 3), (5, 3, 2), (2, 2, 4)], segments=segments)

    assert trip["fim_janela"] == _seconds(300)
    # Sem os 150 s da caminhada, o trecho 2 estaria ocupado entre 50 e 150 s.
    assert _path(_search([trip], _seconds(100), segments=segments)) == PRIMARY
    assert _path(_search([trip], _seconds(250), segments=segments)) == ALTERNATIVE


# Viagem ativa de quem busca


def test_viagem_de_quem_busca_nao_entra_na_ocupacao() -> None:
    trips = [_trip(1, SEARCHER, ON_PRIMARY), _trip(2, 1, ON_PRIMARY)]
    config = {"minimo_usuarios": 2, "percentual_lotacao": 50}

    assert _path(_search(trips, _seconds(50), config=config)) == PRIMARY
    assert _path(_search(trips, _seconds(50), config=config, user=77)) == ALTERNATIVE


def test_viagem_de_quem_busca_nao_entra_no_total() -> None:
    trips = [_trip(1, 1, ON_PRIMARY), _trip(2, SEARCHER, ELSEWHERE)]
    config = {"minimo_usuarios": 1, "percentual_lotacao": 60}

    assert _path(_search(trips, _seconds(50), config=config)) == ALTERNATIVE
    assert _path(_search(trips, _seconds(50), config=config, user=77)) == PRIMARY


# Substituição do trajeto por lotação


def test_sem_trecho_lotado_apresenta_o_trajeto_principal() -> None:
    result = _search([], _seconds(50))

    assert _path(result) == PRIMARY
    assert result["tempo_total_segundos"] == 200


def test_alternativa_disponivel_substitui_o_principal() -> None:
    result = _search([_trip(1, 1, ON_PRIMARY)], _seconds(50))

    assert _path(result) == ALTERNATIVE
    assert [step["id"] for step in result["trechos"]] == [3, 4]
    assert result["tempo_total_segundos"] == 300
    assert result["quantidade_baldeacoes"] == 0


def test_alternativa_evita_todos_os_trechos_lotados() -> None:
    trips = [_trip(1, 1, ON_PRIMARY), _trip(2, 2, [(4, 3, 4)])]

    result = _search(trips, _seconds(50))

    assert _path(result) == [1, 3, 2, 4]
    assert result["tempo_total_segundos"] == 900


def test_alternativa_indisponivel_mantem_o_principal() -> None:
    trips = [_trip(1, 1, ON_PRIMARY), _trip(2, 2, [(3, 1, 3)])]

    assert _path(_search(trips, _seconds(50))) == PRIMARY


# Lotação de uso interno


def test_resultado_substituido_tem_a_forma_do_principal() -> None:
    principal = _search([], _seconds(50))
    replaced = _search([_trip(1, 1, ON_PRIMARY)], _seconds(50))

    assert replaced.keys() == principal.keys()
    assert {
        key for step in replaced["trechos"] for key in step
    } == {key for step in principal["trechos"] for key in step}
    for forbidden in ("lotac", "ocupac", "substitu", "viage", "usuario", "configurac"):
        assert not any(forbidden in key for key in replaced)
