"""Compila a interface no build, antes de iniciar o serviço gratuito."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from deploy.render.environment import configure


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()
    _, origin = configure(local=args.local)
    subprocess.run([sys.executable, "-m", "reflex", "export", "--no-zip", "--env", "prod"], check=True)
    if not Path(".web/build/client/index.html").is_file():
        raise RuntimeError("Exportação não produziu a página inicial compilada.")
    Path(".web/render-build.json").write_text(json.dumps({"origin": origin, "reflex": "0.9.10.post1"}), encoding="utf-8")

if __name__ == "__main__":
    main()
