"""Executado dentro do contêiner Linux sem rede externa e sem credenciais."""
import base64
import json
import os
from pathlib import Path
import platform
import re
import time

import httpx


def main():
    assert platform.system() == "Linux"
    report = {"sistema": "Linux", "python": platform.python_version(), "http": {}}
    # --network none ainda permite loopback; nenhum endpoint de produção é usado.
    for key in ("XANO_AUTH_API_BASE_URL", "XANO_PLANNING_API_BASE_URL", "XANO_ADMIN_API_BASE_URL"):
        assert os.environ[key] == "https://127.0.0.1:9"
    for key in ("METROFLOW_DDT_ENABLED", "METROFLOW_CPTM_ENABLED",
                "METROFLOW_METRO_QUADRO_AUTORIZADO", "METROFLOW_MOTIVA_QUADRO_ENABLED"):
        assert os.environ[key] == "0"
    with httpx.Client(base_url="http://127.0.0.1:10000", trust_env=False, timeout=5) as client:
        deadline = time.monotonic()+120
        while True:
            try:
                response = client.get("/ping")
                response.raise_for_status()
                break
            except httpx.HTTPError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(.5)
        for route in ("/ping", "/", "/login/", "/buscar-trajeto/", "/admin/", "/status/",
                      "/api/planning/stations", "/api/planning/line-status", "/api/admin/indicators"):
            response = client.get(route)
            expected = 401 if route.startswith("/api/") else 200
            assert response.status_code == expected, (route, response.status_code)
            report["http"][route] = response.status_code
        assets = re.findall(r'(?:src|href)="([^\"]*assets/[^\"]+)"', client.get("/").text)
        assert assets and client.get(assets[0]).status_code == 200
        report["asset"] = 200
        response = client.get("/_event/?EIO=4&transport=websocket", headers={
            "Connection": "Upgrade", "Upgrade": "websocket", "Sec-WebSocket-Version": "13",
            "Sec-WebSocket-Key": base64.b64encode(os.urandom(16)).decode(),
            "Origin": "https://metroflow.invalid",
        })
        assert response.status_code == 101, response.status_code
        report["websocket_upgrade"] = 101
    report["memoria_cgroup_bytes"] = (
        Path("/sys/fs/cgroup/memory.current").read_text().strip()
        if Path("/sys/fs/cgroup/memory.current").exists() else "indisponível"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
