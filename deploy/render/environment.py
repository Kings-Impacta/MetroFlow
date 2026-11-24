"""Configuração exclusiva do pacote Render; não modifica a aplicação local."""
import os
from pathlib import Path
from urllib.parse import urlsplit

STATUS_FLAGS = (
    "METROFLOW_DDT_ENABLED", "METROFLOW_CPTM_ENABLED",
    "METROFLOW_METRO_QUADRO_AUTORIZADO", "METROFLOW_MOTIVA_QUADRO_ENABLED",
)

def configure(*, local=False):
    if any(os.environ.get(key, "0") != "0" for key in STATUS_FLAGS):
        raise ValueError("Ativação pública dos status pendente; todas as fontes devem estar em 0.")
    for key in STATUS_FLAGS:
        os.environ[key] = "0"
    raw_port = os.environ.get("PORT", "10000")
    if not raw_port.isascii() or not raw_port.isdecimal() or not 1024 <= int(raw_port) <= 65535:
        raise ValueError("PORT deve ser um inteiro entre 1024 e 65535.")
    port = int(raw_port)
    url = os.environ.get("METROFLOW_PUBLIC_URL") or os.environ.get("RENDER_EXTERNAL_URL", "")
    if any(c.isspace() for c in url):
        raise ValueError("Origem não pode conter espaços.")
    parts = urlsplit(url)
    _ = parts.port
    if (not parts.hostname or parts.username or parts.password or parts.query or parts.fragment
            or parts.path not in ("", "/")
            or not (parts.scheme == "https" or
                    (local and parts.scheme == "http" and parts.hostname in ("localhost", "127.0.0.1")))):
        raise ValueError("Informe a origem HTTPS em METROFLOW_PUBLIC_URL ou RENDER_EXTERNAL_URL.")
    origin = url.rstrip("/")
    os.environ.update({
        "METROFLOW_ENV": "production", "REFLEX_ENV_MODE": "prod",
        "REFLEX_API_URL": origin, "REFLEX_DEPLOY_URL": origin,
        "REFLEX_BACKEND_PORT": str(port), "REFLEX_FRONTEND_PORT": str(port),
        "REFLEX_BACKEND_HOST": "0.0.0.0", "GRANIAN_WORKERS": "1",
        "REFLEX_TELEMETRY_ENABLED": "false", "REFLEX_USE_NPM": "true", "npm_config_save_exact": "true",
    })
    reflex_dir = Path(os.environ.get("REFLEX_DIR", ".cache/reflex")).resolve()
    reflex_dir.mkdir(parents=True, exist_ok=True)
    os.environ["REFLEX_DIR"] = str(reflex_dir)
    # Cache efêmero, exclusivo deste servidor; fontes permanecem desligadas.
    os.environ.setdefault("METROFLOW_STATUS_CACHE_PATH", ".cache/render-line-status.sqlite3")
    return port, origin
