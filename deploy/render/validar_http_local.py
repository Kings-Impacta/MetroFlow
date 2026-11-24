"""Laboratório em loopback: frontend compilado e fábrica ASGI, sem login real.

Usa Granian incorporado somente no teste Windows, não o inicializador de produção.
Não consulta Xano nem fontes: as APIs são exercidas sem cookie e devem rejeitar.
"""
import asyncio
import base64
import json
import os
from pathlib import Path
import re

import httpx
from deploy.render.environment import configure


async def validate():
    port, origin = configure(local=True)
    if json.loads(Path(".web/render-build.json").read_text(encoding="utf8")) != {
        "origin": origin, "reflex": "0.9.10.post1"
    }:
        raise RuntimeError("Build incompatível com o laboratório.")
    from reflex_base.environment import environment
    environment.REFLEX_SKIP_COMPILE.set(True)
    environment.REFLEX_MOUNT_FRONTEND_COMPILED_APP.set(True)
    from granian._internal import load_target
    from granian.constants import Interfaces
    from granian.server.embed import Server
    from reflex.utils.exec import get_app_instance_from_file
    app = load_target(get_app_instance_from_file())()
    server = Server(target=app, interface=Interfaces.ASGI, address="127.0.0.1",
                    port=port, log_access=False)
    task = asyncio.create_task(server.serve())
    report = {"modo": "Granian incorporado; não é o supervisor multiprocesso de produção"}
    try:
        async with httpx.AsyncClient(base_url=f"http://127.0.0.1:{port}", trust_env=False) as client:
            for _ in range(40):
                if task.done():
                    await task
                try:
                    await client.get("/ping")
                    break
                except httpx.ConnectError:
                    await asyncio.sleep(.1)
            else:
                raise RuntimeError("Servidor de laboratório indisponível.")
            for path in ["/ping", "/", "/buscar-trajeto/", "/admin/", "/status/",
                         "/api/planning/stations", "/api/planning/line-status", "/api/admin/indicators"]:
                response = await client.get(path)
                expected = 401 if path.startswith("/api/") else 200
                assert response.status_code == expected, (path, response.status_code)
                report[path] = response.status_code
            assets = re.findall(r'(?:src|href)="([^\"]*assets/[^\"]+)"', (await client.get("/")).text)
            assert assets and (await client.get(assets[0])).status_code == 200
            report["asset_compilado"] = 200
            response = await client.get("/_event/?EIO=4&transport=websocket", headers={
                "Connection": "Upgrade", "Upgrade": "websocket", "Sec-WebSocket-Version": "13",
                "Sec-WebSocket-Key": base64.b64encode(os.urandom(16)).decode(), "Origin": origin,
            })
            assert response.status_code == 101, response.status_code
            report["websocket_upgrade"] = 101
        Path(".cache/validation/render-http-20261123.json").write_text(json.dumps(report, indent=2), encoding="utf8")
        print(json.dumps(report))
    finally:
        server.stop()
        await task


if __name__ == "__main__":
    asyncio.run(validate())
