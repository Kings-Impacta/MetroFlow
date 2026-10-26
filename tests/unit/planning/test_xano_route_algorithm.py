"""Executa a função de cálculo registrada no XanoScript com malhas controladas."""

from tests.unit.planning.xano_lambda import XANO_DRAFTS, requires_node, run_lambda


XANO_SCRIPT = XANO_DRAFTS / "planejamento" / "trajetos_buscar_post.xs"
pytestmark = requires_node


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


def _segment(
    identifier: int,
    origin: int,
    destination: int,
    line: int,
    seconds: int,
) -> dict[str, object]:
    return {
        "id": identifier,
        "estacao_origem_id": origin,
        "estacao_destino_id": destination,
        "linha_id": line,
        "tempo_estimado": seconds,
        "tipo": "ferroviario",
        "direcionado": False,
        "servico_id": None,
    }


def _mesh(segments: list[dict[str, object]]) -> dict[str, object]:
    return {
        "origem_id": 1,
        "destino_id": 4,
        "estacoes": [
            {"id": 1, "nome": "Origem", "codigo": "O"},
            {"id": 2, "nome": "Caminho A", "codigo": "A"},
            {"id": 3, "nome": "Caminho B", "codigo": "B"},
            {"id": 4, "nome": "Destino", "codigo": "D"},
        ],
        "linhas": [_line(1), _line(2)],
        "estacoes_linhas": [],
        "trechos": segments,
    }


def _calculate(input_data: dict[str, object]) -> dict[str, object]:
    decoded = run_lambda(XANO_SCRIPT, input_data)
    assert isinstance(decoded, dict)
    return decoded


def test_escolhe_o_caminho_de_menor_tempo_total() -> None:
    result = _calculate(
        _mesh(
            [
                _segment(1, 1, 2, 1, 100),
                _segment(2, 2, 4, 1, 100),
                _segment(3, 1, 3, 2, 150),
                _segment(4, 3, 4, 2, 150),
            ]
        )
    )

    assert [station["id"] for station in result["estacoes"]] == [1, 2, 4]
    assert result["tempo_total_segundos"] == 200
    assert result["quantidade_baldeacoes"] == 0


def test_desempata_o_tempo_total_por_menos_baldeacoes() -> None:
    result = _calculate(
        _mesh(
            [
                _segment(1, 1, 2, 1, 400),
                _segment(2, 2, 4, 1, 400),
                _segment(3, 1, 3, 1, 100),
                _segment(4, 3, 4, 2, 100),
            ]
        )
    )

    assert [station["id"] for station in result["estacoes"]] == [1, 2, 4]
    assert result["tempo_total_segundos"] == 800
    assert result["quantidade_baldeacoes"] == 0
