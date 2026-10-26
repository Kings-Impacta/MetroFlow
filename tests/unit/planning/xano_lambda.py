"""Executa com Node.js as funções lambda registradas nos rascunhos XanoScript."""

import json
from pathlib import Path
import re
import shutil
import subprocess

import pytest


NODE = shutil.which("node")
XANO_DRAFTS = Path(__file__).parents[3] / "docs" / "xano" / "rascunhos"
requires_node = pytest.mark.skipif(
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


def lambda_body(script: Path) -> str:
    source = script.read_text(encoding="utf-8-sig")
    match = re.search(r'\|lambda:("(?:\\.|[^"\\])*")', source)
    assert match is not None, "A função lambda do endpoint não foi encontrada."
    return json.loads(match.group(1))


def run_lambda(script: Path, input_data: dict[str, object]) -> object:
    assert NODE is not None
    result = subprocess.run(
        [NODE, "-e", HARNESS],
        input=json.dumps({"body": lambda_body(script), "input": input_data}),
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)
