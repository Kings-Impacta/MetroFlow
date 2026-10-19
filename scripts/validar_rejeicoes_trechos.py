"""Valida rejeicoes do endpoint de trechos sem criar registros.

O token e solicitado sem eco e permanece apenas na memoria do processo.
"""

from __future__ import annotations

from getpass import getpass
import json
import re

import httpx


ENDPOINT = (
    "https://x8ki-letl-twmt.n7.xano.io/"
    "api:metroflow-planejamento/trechos"
)

BASE = {
    "estacao_origem_id": 1,
    "estacao_destino_id": 2,
    "linha_id": 1,
    "tempo_estimado": 120,
    "ativo": True,
    "tipo": "ferroviario",
    "direcionado": False,
    "servico_id": None,
}


def caso(**alteracoes: object) -> dict[str, object]:
    return BASE | alteracoes


def detalhe_seguro(response: httpx.Response) -> str:
    """Resume somente o corpo da resposta, sem incluir cabecalhos da sessao."""
    try:
        corpo = response.json()
    except ValueError:
        texto = " ".join(response.text.split())
        return texto[:240] or "sem corpo"

    if isinstance(corpo, dict):
        for chave in ("message", "detail", "error"):
            valor = corpo.get(chave)
            if valor:
                return " ".join(str(valor).split())[:240]
    return " ".join(str(corpo).split())[:240]


CASOS = {
    "extremos iguais": caso(estacao_destino_id=1),
    "origem inexistente": caso(estacao_origem_id=999_999),
    "destino inexistente": caso(estacao_destino_id=999_999),
    "linha inexistente": caso(linha_id=999_999),
    "tempo zero": caso(tempo_estimado=0),
    "tempo negativo": caso(tempo_estimado=-1),
    "duplicata direta existente": caso(),
    "duplicata inversa existente": caso(
        estacao_origem_id=2,
        estacao_destino_id=1,
    ),
}


def main() -> int:
    entrada = getpass(
        "Cole o authToken ou a resposta JSON do login (nao sera exibido): "
    ).strip()
    token = entrada
    try:
        resposta = json.loads(entrada)
        if isinstance(resposta, dict):
            token = str(resposta.get("authToken", "")).strip()
    except json.JSONDecodeError:
        encontrado = re.search(
            r'authToken["\s:]+([A-Za-z0-9_.-]+)',
            entrada,
        )
        if encontrado:
            token = encontrado.group(1)
    if not token:
        print("Token ausente.")
        return 2

    falhas: list[str] = []
    headers = {"Authorization": f"Bearer {token}"}

    with httpx.Client(timeout=15.0, headers=headers) as client:
        for nome, payload in CASOS.items():
            response = client.post(ENDPOINT, json=payload)
            if response.status_code in {401, 403}:
                print(f"FALHA DE SESSAO: HTTP {response.status_code}")
                return 2
            if response.is_success:
                falhas.append(nome)
                print(f"FALHOU  {nome}: HTTP {response.status_code}")
            else:
                print(
                    f"OK      {nome}: HTTP {response.status_code} - "
                    f"{detalhe_seguro(response)}"
                )

    if falhas:
        print("Algum caso rejeitado foi persistido; interrompa a validacao.")
        return 1

    print("Todos os casos foram rejeitados sem resposta de sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
