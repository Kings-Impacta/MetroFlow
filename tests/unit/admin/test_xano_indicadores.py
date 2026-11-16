"""Executa com Node.js as funções do painel administrativo registradas no XanoScript.

O instante de referência é 16/11/2026 às 15h em São Paulo (18h UTC).
"""

from datetime import datetime, timedelta, timezone

import pytest

from tests.unit.planning.xano_lambda import XANO_DRAFTS, requires_node, run_lambda


DRAFTS = XANO_DRAFTS / "portal-administrativo"
INDICATORS_SCRIPT = DRAFTS / "admin_indicadores_get.xs"
STATIONS_SCRIPT = DRAFTS / "admin_estacoes_get.xs"
pytestmark = requires_node

UTC = timezone.utc
NOW_DT = datetime(2026, 11, 16, 18, 0, tzinfo=UTC)
SP_MIDNIGHT_DT = datetime(2026, 11, 16, 3, 0, tzinfo=UTC)
CONFIG = {"minimo_usuarios": 2, "percentual_lotacao": 50}
STATIONS = [
    {"id": 1, "nome": "Sé", "codigo": "SE", "ativa": True},
    {"id": 2, "nome": "Luz", "codigo": "LUZ", "ativa": True},
    {"id": 3, "nome": "Paraíso", "codigo": "PAR", "ativa": True},
    {"id": 4, "nome": "Brás", "codigo": "BRS", "ativa": False},
]


def ms(moment: datetime) -> int:
    return int(moment.timestamp() * 1000)


NOW = ms(NOW_DT)


def step(
    segment_id: int,
    origin: int,
    destination: int,
    seconds: int,
    *,
    order: int = 1,
    kind: str = "ferroviario",
    service: int | None = None,
    **extra: object,
) -> dict[str, object]:
    return {
        "ordem": order,
        "trecho_id": segment_id,
        "estacao_origem_id": origin,
        "estacao_destino_id": destination,
        "tempo_estimado": seconds,
        "tipo": kind,
        "servico_id": service,
        **extra,
    }


def trip(
    identifier: int,
    user: int,
    confirmed: datetime,
    *,
    duration: timedelta = timedelta(minutes=30),
    replaced: bool = False,
    steps: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {
        "id": identifier,
        "usuario_id": user,
        "confirmada_em": ms(confirmed),
        "fim_janela": ms(confirmed + duration),
        "substituida": replaced,
        "trechos": steps if steps is not None else [step(10, 1, 2, 120)],
    }


def indicators(
    trips: list[dict[str, object]] | None = None,
    *,
    accounts: int = 0,
    stations: list[dict[str, object]] | None = None,
    lines: int = 0,
    segments: int = 0,
    config: dict[str, object] | None = CONFIG,
) -> dict[str, object]:
    result = run_lambda(
        INDICATORS_SCRIPT,
        {
            "agora": NOW,
            "viagens": trips or [],
            "contas": [{"id": i} for i in range(accounts)],
            "estacoes": STATIONS if stations is None else stations,
            "linhas_ativas": [{"id": i} for i in range(lines)],
            "trechos_ativos": [{"id": i} for i in range(segments)],
            "configuracao": config,
        },
    )
    assert isinstance(result, dict)
    return result


# Indicadores de uso


def test_viagem_dentro_da_janela_conta_em_rotas_ativas() -> None:
    result = indicators([trip(1, 501, NOW_DT - timedelta(minutes=5))])

    assert result["apurado_em"] == NOW
    assert result["uso"]["rotas_ativas"] == 1
    assert result["uso"]["usuarios_em_viagem"] == 1


def test_viagem_encerrada_substituida_ou_futura_nao_conta() -> None:
    result = indicators(
        [
            trip(1, 501, NOW_DT - timedelta(minutes=40)),
            trip(2, 502, NOW_DT - timedelta(minutes=5), replaced=True),
            trip(3, 503, NOW_DT - timedelta(minutes=30)),  # fim_janela == agora
            trip(4, 504, NOW_DT + timedelta(minutes=1)),
        ]
    )

    assert result["uso"]["rotas_ativas"] == 0
    assert result["uso"]["usuarios_em_viagem"] == 0


def test_duas_viagens_ativas_do_mesmo_usuario_contam_uma() -> None:
    result = indicators(
        [
            trip(1, 501, NOW_DT - timedelta(minutes=10)),
            trip(2, 501, NOW_DT - timedelta(minutes=5)),
            trip(3, 502, NOW_DT - timedelta(minutes=5)),
        ]
    )

    assert result["uso"]["rotas_ativas"] == 2
    assert result["uso"]["usuarios_em_viagem"] == 2


def test_uso_recente_conta_cada_usuario_uma_vez_nos_ultimos_7_dias() -> None:
    result = indicators(
        [
            trip(1, 501, NOW_DT - timedelta(days=1)),
            trip(2, 501, NOW_DT - timedelta(days=2)),
            trip(3, 501, NOW_DT - timedelta(hours=1), replaced=True),
            trip(4, 502, NOW_DT - timedelta(days=7)),
            trip(5, 503, NOW_DT - timedelta(days=7, seconds=1)),
        ]
    )

    assert result["uso"]["usuarios_uso_recente"] == 2


def test_contas_habilitadas_usa_a_contagem_filtrada() -> None:
    assert indicators(accounts=7)["uso"]["contas_habilitadas"] == 7


# Indicadores da malha e volume


def test_indicadores_da_malha() -> None:
    result = indicators(lines=16, segments=207)

    assert result["malha"] == {
        "estacoes_ativas": 3,
        "estacoes_inativas": 1,
        "linhas_ativas": 16,
        "trechos_ativos": 207,
    }


def test_estacao_sem_situacao_booleana_nao_conta_como_ativa() -> None:
    stations = [{"id": 1, "nome": "Sé", "codigo": "SE", "ativa": None}]

    assert indicators(stations=stations)["malha"]["estacoes_ativas"] == 0
    assert indicators(stations=stations)["malha"]["estacoes_inativas"] == 1


def test_volume_inclui_substituidas_e_respeita_a_virada_do_dia() -> None:
    result = indicators(
        [
            trip(1, 501, SP_MIDNIGHT_DT),
            trip(2, 501, SP_MIDNIGHT_DT + timedelta(hours=2), replaced=True),
            trip(3, 502, SP_MIDNIGHT_DT - timedelta(minutes=1)),
            trip(4, 503, NOW_DT - timedelta(days=6)),
            trip(5, 504, NOW_DT - timedelta(days=8)),
        ]
    )

    assert result["volume"] == {"viagens_hoje": 2, "viagens_7_dias": 4}


# Ranking de estações


def test_ranking_conta_origem_e_destino_sem_estacoes_intermediarias() -> None:
    steps = [step(10, 1, 4, 100, order=1), step(11, 4, 2, 100, order=2)]
    result = indicators([trip(1, 501, NOW_DT - timedelta(hours=2), steps=steps)])

    assert result["ranking_estacoes"] == [
        {"id": 2, "nome": "Luz", "codigo": "LUZ", "usos": 1},
        {"id": 1, "nome": "Sé", "codigo": "SE", "usos": 1},
    ]


def test_ranking_ordena_por_usos_desempata_por_nome_e_limita_a_cinco() -> None:
    stations = [
        {"id": index, "nome": name, "codigo": f"C{index}", "ativa": index != 6}
        for index, name in enumerate(
            ["Zona Norte", "Ána Rosa", "Butantã", "Consolação", "Itaquera", "Barra Funda", "Morumbi"],
            start=1,
        )
    ]
    trips = [
        trip(1, 501, NOW_DT - timedelta(hours=3), steps=[step(10, 1, 7, 100)]),
        trip(2, 502, NOW_DT - timedelta(hours=3), steps=[step(11, 1, 2, 100)]),
        trip(3, 503, NOW_DT - timedelta(hours=3), steps=[step(12, 3, 4, 100)]),
        trip(4, 504, NOW_DT - timedelta(hours=3), steps=[step(13, 5, 6, 100)]),
    ]

    ranking = indicators(trips, stations=stations)["ranking_estacoes"]

    assert [item["nome"] for item in ranking] == [
        "Zona Norte",
        "Ána Rosa",
        "Barra Funda",
        "Butantã",
        "Consolação",
    ]
    assert ranking[0]["usos"] == 2


def test_ranking_vazio_sem_viagens_no_periodo() -> None:
    result = indicators([trip(1, 501, NOW_DT - timedelta(days=9))])

    assert result["ranking_estacoes"] == []


# Trechos lotados


def _on_segment(identifier: int, user: int, origin: int = 1, destination: int = 2) -> dict[str, object]:
    return trip(
        identifier,
        user,
        NOW_DT - timedelta(seconds=30),
        steps=[step(10, origin, destination, 120)],
    )


def test_trecho_lotado_nos_dois_sentidos_conta_duas_ocorrencias() -> None:
    trips = [
        _on_segment(1, 501),
        _on_segment(2, 502),
        _on_segment(3, 503, 2, 1),
        _on_segment(4, 504, 2, 1),
    ]

    result = indicators(trips)

    assert result["lotacao"] == {
        "trechos_lotados": 2,
        "minimo_usuarios": 2,
        "percentual_lotacao": 50,
    }


def test_nenhum_trecho_lotado_apresenta_zero_e_o_criterio() -> None:
    result = indicators([_on_segment(1, 501)])

    assert result["lotacao"] == {
        "trechos_lotados": 0,
        "minimo_usuarios": 2,
        "percentual_lotacao": 50,
    }


def test_percentual_e_calculado_sobre_todas_as_viagens_ativas() -> None:
    trips = [_on_segment(1, 501), _on_segment(2, 502)] + [
        trip(10 + index, 600 + index, NOW_DT - timedelta(minutes=1), steps=[step(20, 3, 4, 300)])
        for index in range(3)
    ]

    # 2 de 5 viagens ativas no trecho 10 (40%) e 3 de 5 no trecho 20 (60%).
    assert indicators(trips)["lotacao"]["trechos_lotados"] == 1


def test_usuario_com_duas_viagens_ativas_conta_uma_vez_na_ocupacao() -> None:
    trips = [_on_segment(1, 501), _on_segment(2, 501)]

    assert indicators(trips)["lotacao"]["trechos_lotados"] == 0


@pytest.mark.parametrize(
    "config",
    [
        pytest.param(None, id="ausente"),
        pytest.param({"minimo_usuarios": 0, "percentual_lotacao": 50}, id="minimo-zero"),
        pytest.param({"minimo_usuarios": 1, "percentual_lotacao": 0}, id="percentual-zero"),
        pytest.param({"minimo_usuarios": 1, "percentual_lotacao": 150}, id="percentual-acima-de-100"),
    ],
)
def test_configuracao_ausente_ou_invalida_torna_o_indicador_indisponivel(config) -> None:
    trips = [_on_segment(1, 501), _on_segment(2, 502)]

    assert indicators(trips, config=config)["lotacao"] == {
        "trechos_lotados": None,
        "minimo_usuarios": None,
        "percentual_lotacao": None,
    }


def test_integracao_a_pe_e_servico_especial_nunca_lotam() -> None:
    walking = [step(30, 1, 2, 120, kind="transferencia")]
    special = [step(31, 2, 3, 120, service=7)]
    trips = [
        trip(1, 501, NOW_DT - timedelta(seconds=30), steps=walking),
        trip(2, 502, NOW_DT - timedelta(seconds=30), steps=walking),
        trip(3, 503, NOW_DT - timedelta(seconds=30), steps=special),
        trip(4, 504, NOW_DT - timedelta(seconds=30), steps=special),
    ]

    assert indicators(trips)["lotacao"]["trechos_lotados"] == 0


def test_cronograma_calibrado_define_o_intervalo_de_passagem() -> None:
    passing = [step(10, 1, 2, 120, inicio_previsto_em=NOW - 60_000)]
    later = [step(10, 1, 2, 120, inicio_previsto_em=NOW + 60_000)]
    trips = [
        trip(1, 501, NOW_DT - timedelta(minutes=5), steps=passing),
        trip(2, 502, NOW_DT - timedelta(minutes=5), steps=passing),
        trip(3, 503, NOW_DT - timedelta(minutes=5), steps=later),
    ]

    # Duas passam agora pelo trecho; a terceira só passará depois.
    assert indicators(trips)["lotacao"]["trechos_lotados"] == 1
    assert indicators(trips[1:])["lotacao"]["trechos_lotados"] == 0


def test_registro_antigo_soma_trechos_esperas_e_baldeacoes_anteriores() -> None:
    def legacy(identifier: int, user: int) -> dict[str, object]:
        # Começa há 300 s: 100 s no trecho 40 e 60 s de espera + 120 s de
        # baldeação antes do trecho 41, que vai de 280 s a 400 s.
        return trip(
            identifier,
            user,
            NOW_DT - timedelta(seconds=300),
            steps=[
                step(40, 1, 2, 100, order=1),
                step(
                    41,
                    2,
                    3,
                    120,
                    order=2,
                    espera_estimada_segundos=60,
                    baldeacao_antes_segundos=120,
                ),
            ],
        )

    assert indicators([legacy(1, 501), legacy(2, 502)])["lotacao"]["trechos_lotados"] == 1


# Somente agregados


def _keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {key for item in value.values() for key in _keys(item)}
    if isinstance(value, list):
        return {key for item in value for key in _keys(item)}
    return set()


def _values(value: object) -> list[object]:
    if isinstance(value, dict):
        return [item for nested in value.values() for item in _values(nested)]
    if isinstance(value, list):
        return [item for nested in value for item in _values(nested)]
    return [value]


def test_resposta_dos_indicadores_nao_contem_dados_de_usuarios_ou_viagens() -> None:
    trips = [
        trip(1, 987_654, NOW_DT - timedelta(minutes=5)),
        trip(2, 876_543, NOW_DT - timedelta(hours=5)),
    ]

    result = indicators(trips, accounts=3)

    assert not _keys(result) & {
        "usuario_id",
        "usuario",
        "email",
        "trechos",
        "viagens",
        "confirmada_em",
        "fim_janela",
    }
    assert 987_654 not in _values(result)
    assert 876_543 not in _values(result)


# Listagem de estações


def test_listagem_inclui_estacoes_inativas_com_linhas_sem_repeticao() -> None:
    result = run_lambda(
        STATIONS_SCRIPT,
        {
            "estacoes": [
                {"id": 1, "nome": "Sé", "codigo": "SE", "ativa": True},
                {"id": 4, "nome": "Brás", "codigo": "BRS", "ativa": False},
                {"id": 5, "nome": "Nova", "codigo": "NOV", "ativa": None},
            ],
            "vinculos": [
                {"estacao_id": 1, "linha_id": 1, "linha_nome": "Azul", "linha_codigo": "L1", "linha_cor": "#0455A1"},
                {"estacao_id": 1, "linha_id": 3, "linha_nome": "Vermelha", "linha_codigo": "L3", "linha_cor": None},
                {"estacao_id": 1, "linha_id": 1, "linha_nome": "Azul", "linha_codigo": "L1", "linha_cor": "#0455A1"},
                {"estacao_id": 4, "linha_id": 3, "linha_nome": "Vermelha", "linha_codigo": "L3", "linha_cor": None},
            ],
        },
    )

    assert result == {
        "estacoes": [
            {
                "id": 1,
                "nome": "Sé",
                "codigo": "SE",
                "ativa": True,
                "linhas": [
                    {"id": 1, "nome": "Azul", "codigo": "L1", "cor": "#0455A1"},
                    {"id": 3, "nome": "Vermelha", "codigo": "L3", "cor": None},
                ],
            },
            {
                "id": 4,
                "nome": "Brás",
                "codigo": "BRS",
                "ativa": False,
                "linhas": [{"id": 3, "nome": "Vermelha", "codigo": "L3", "cor": None}],
            },
            {"id": 5, "nome": "Nova", "codigo": "NOV", "ativa": False, "linhas": []},
        ]
    }
