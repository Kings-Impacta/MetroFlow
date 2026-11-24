"""Serve o build existente e a API Reflex na mesma porta, sem recompilar."""
import argparse
import json
from pathlib import Path
from deploy.render.environment import configure


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()
    port, origin = configure(local=args.local)
    if not Path(".web/build/client/index.html").is_file():
        raise RuntimeError("Build ausente. Execute python -m deploy.render.build antes de iniciar.")
    manifest = json.loads(Path(".web/render-build.json").read_text(encoding="utf-8"))
    if manifest != {"origin": origin, "reflex": "0.9.10.post1"}:
        raise RuntimeError("Origem ou versão diferente do build; recompile antes de iniciar.")
    from reflex_base.environment import environment
    environment.REFLEX_SKIP_COMPILE.set(True)
    environment.REFLEX_MOUNT_FRONTEND_COMPILED_APP.set(True)
    # Equivale ao servidor de produção do Reflex 0.9.10.post1, com build separado.
    from granian.constants import Interfaces
    from granian.server import Server
    from reflex.utils.exec import get_app_instance_from_file
    Server(target=get_app_instance_from_file(), factory=True, interface=Interfaces.ASGI,
           address="0.0.0.0", port=port, workers=1, log_access=False).serve()

if __name__ == "__main__":
    main()
