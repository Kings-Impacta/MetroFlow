"""Executa a função de cálculo registrada no XanoScript com malhas controladas."""

import json
from pathlib import Path
import re
import shutil
import subprocess

import pytest


NODE = shutil.which("node")
XANO_SCRIPT = (
    Path(__file__).parents[3]
    / "docs"
    / "xano"
    / "rascunhos"
    / "planejamento"
    / "trajetos_buscar_post.xs"
)
pytestmark = pytest.mark.skipif(
    NODE is None,
    reason="Node.js é necessário para executar a função do XanoScript.",
)

HARNESS = r"""
let source = '';
process.stdin.on('data', chunk => source += chunk);
process.stdin.on('end', () => {
  try {
    const {body, input} = JSON.parse(source);
    const calculate = new Function('$this', body);
    process.stdout.write(JSON.stringify(calculate(input)));
  } catch (error) {
    console.error(error);
    process.exitCode = 1;
  }
});
"""


def _algorithm_body() -> str:
    source = XANO_SCRIPT.read_text(encoding="utf-8-sig")
    match = re.search(r'\|lambda:("(?:\\.|[^"\\])*")', source)
    assert match is not None, "A função lambda do endpoint não foi encontrada."
    return json.loads(match.group(1))


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
    result = subprocess.run(
        [NODE, "-e", HARNESS],
        input=json.dumps({"body": _algorithm_body(), "input": input_data}),
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    decoded = json.loads(result.stdout)
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
