"""Envia o último retorno persistível do coletor local; nunca consulta as fontes.

Uso exclusivo no terminal do responsável, com sessão administrativa temporária.
Credenciais não são salvas. Não executar este processo no servidor de trajetos.
"""
import argparse
import getpass
import json
from pathlib import Path
import sqlite3
import time
from urllib.parse import urlsplit

import httpx
from MetroFlow.auth.infrastructure.xano_client import XanoAuthClient
from .domain import LineCondition
from .xano_snapshot import CODES

KEYS = {"cptm": "cptm-v1", "metro": "metro-board-v1", "motiva": "motiva-board-v1"}


def saved_conditions(path, source):
    """Somente payloads já aceitos pelo cache; no-store nunca entrou neste banco."""
    with sqlite3.connect(Path(path).resolve().as_uri()+"?mode=ro", uri=True, timeout=0.2) as db:
        row = db.execute("SELECT payload FROM status_cache WHERE key=?", (KEYS[source],)).fetchone()
    if not row:
        return []
    items = [LineCondition.model_validate(raw) for raw in json.loads(row[0])]
    if len(items) > 17 or len({r.line_code for r in items}) != len(items):
        raise ValueError("Cache inválido.")
    if any(r.line_code not in CODES[source] or r.collected_at is None for r in items):
        raise ValueError("Cache incompatível com a fonte.")
    # O servidor calcula a validade com as datas originais; não as renova no envio.
    return [r.model_copy(update={"validity": "current"}).model_dump() for r in items]


def send(client, source, items):
    response = client.post("controle", json={"fonte": source, "pedido": {"acao": "reserve"}})
    response.raise_for_status()
    lease = response.json()
    if not lease.get("granted"):
        return False
    response = client.post("controle", json={"fonte": source, "pedido": {
        "acao": "publish", "generation": lease["generation"], "conditions": items,
        "cacheable": True, "refresh_after": 300, "fresh_for": 600,
    }})
    response.raise_for_status()
    return response.json().get("stored", 0) > 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Base HTTPS do grupo exclusivo de status.")
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--sources", nargs="+", required=True, choices=tuple(KEYS))
    parser.add_argument("--loop", action="store_true")
    args = parser.parse_args()
    url = urlsplit(args.url)
    if url.scheme != "https" or not url.hostname or url.username or url.password or url.query or url.fragment:
        parser.error("Informe uma base HTTPS sem credenciais.")
    with XanoAuthClient.from_environment() as auth:
        session = auth.login(input("E-mail administrativo: ").strip(), getpass.getpass("Senha (não será salva): "))
        user = auth.me(session.auth_token)
    if not user.is_admin:
        raise SystemExit("A conta não possui acesso administrativo.")
    sent = {}
    with httpx.Client(base_url=args.url.rstrip("/")+"/", timeout=10, follow_redirects=False,
                      headers={"Authorization": "Bearer "+session.auth_token}) as client:
        while True:
            for source in dict.fromkeys(args.sources):
                try:
                    items = saved_conditions(args.cache, source)
                    fingerprint = json.dumps(items, sort_keys=True)
                    if items and fingerprint != sent.get(source):
                        if send(client, source, items):
                            sent[source] = fingerprint
                            print(f"{source}: último retorno gravado; datas preservadas.", flush=True)
                except httpx.HTTPStatusError as error:
                    if error.response.status_code in (401, 403):
                        raise SystemExit("Sessão encerrada ou acesso recusado; entre novamente.") from None
                    if error.response.status_code == 429:
                        print("Limite do Xano; aguardando uma hora sem repetir pedidos.", flush=True)
                        if not args.loop:
                            raise SystemExit(1)
                        time.sleep(3600)
                    else:
                        print(f"{source}: envio recusado; último retorno remoto preservado.", flush=True)
                except (httpx.HTTPError, sqlite3.Error, OSError, ValueError, TypeError):
                    print(f"{source}: cache ou envio indisponível; último retorno remoto preservado.", flush=True)
                if args.loop:
                    # Um ciclo de três fontes leva cinco minutos, sem rajada no Xano.
                    time.sleep(300 / len(set(args.sources)))
            if not args.loop:
                break


if __name__ == "__main__":
    main()
