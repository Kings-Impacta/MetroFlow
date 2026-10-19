"""Valida concorrencia e o default ativo com um registro temporario.

O token permanece apenas na memoria. Este script cria no maximo um trecho
temporario entre as estacoes 1 e 3 da linha 1; remova-o ao concluir o teste.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from getpass import getpass
import json
import re
import threading

import httpx


ENDPOINT = (
    "https://x8ki-letl-twmt.n7.xano.io/"
    "api:metroflow-planejamento/trechos"
)
AUTH_ENDPOINT = (
    "https://x8ki-letl-twmt.n7.xano.io/api:75UptKSb/auth/login"
)
EMAIL_PADRAO = "metroflow.projeto@gmail.com"

PAYLOAD = {
    "estacao_origem_id": 1,
    "estacao_destino_id": 3,
    "linha_id": 1,
    "tempo_estimado": 121,
    # "ativo" e omitido para validar o default true do endpoint.
    "tipo": "ferroviario",
    "direcionado": False,
    # "servico_id" tambem e omitido porque o teste nao usa servico especial.
}


def ler_token() -> str:
    entrada = getpass(
        "Cole um authToken real ou pressione Enter para fazer login seguro: "
    ).strip()
    if not entrada:
        email = input(f"E-mail [{EMAIL_PADRAO}]: ").strip() or EMAIL_PADRAO
        senha = getpass("Senha (nao sera exibida nem salva): ")
        resposta_login = httpx.post(
            AUTH_ENDPOINT,
            json={"email": email, "senha": senha},
            timeout=20.0,
        )
        if not resposta_login.is_success:
            print(f"Falha no login: HTTP {resposta_login.status_code}.")
            return ""
        try:
            corpo_login = resposta_login.json()
        except ValueError:
            print("Falha no login: resposta sem JSON.")
            return ""
        if not isinstance(corpo_login, dict):
            print("Falha no login: resposta inesperada.")
            return ""
        return str(corpo_login.get("authToken", "")).strip()

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
    return token


def resumo(response: httpx.Response) -> str:
    try:
        corpo = response.json()
    except ValueError:
        return " ".join(response.text.split())[:240] or "sem corpo"
    return " ".join(str(corpo).split())[:240]


def enviar(token: str, barreira: threading.Barrier) -> httpx.Response:
    barreira.wait(timeout=10)
    return httpx.post(
        ENDPOINT,
        json=PAYLOAD,
        headers={"Authorization": f"Bearer {token}"},
        timeout=20.0,
    )


def main() -> int:
    token = ler_token()
    if not token:
        print("Token ausente.")
        return 2

    barreira = threading.Barrier(2)
    with ThreadPoolExecutor(max_workers=2) as executor:
        respostas = list(
            executor.map(lambda _: enviar(token, barreira), range(2))
        )

    sucessos = [resposta for resposta in respostas if resposta.is_success]
    for indice, resposta in enumerate(respostas, start=1):
        estado = "SUCESSO" if resposta.is_success else "REJEITADO"
        print(
            f"Tentativa {indice}: {estado} HTTP {resposta.status_code} - "
            f"{resumo(resposta)}"
        )

    if any(
        "Unable to locate auth: versao_sessao" in resposta.text
        for resposta in respostas
    ):
        print(
            "FALHA DE SESSAO: gere um novo authToken pelo endpoint real "
            "auth/login e repita o teste."
        )
        return 2

    if len(sucessos) != 1:
        print(
            "FALHA: eram esperadas exatamente uma criacao e uma rejeicao."
        )
        return 1

    try:
        criado = sucessos[0].json()
    except ValueError:
        print("FALHA: a criacao nao retornou JSON para validar ativo=true.")
        return 1

    if not isinstance(criado, dict) or criado.get("ativo") is not True:
        print("FALHA: o registro criado nao confirmou ativo=true.")
        return 1

    print(
        "OK: uma unica gravacao venceu a concorrencia com ativo=true."
    )
    print(
        "Registro temporario a remover: "
        f"id={criado.get('id')}, origem=1, destino=3, linha=1."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
