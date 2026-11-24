# Laboratório local; não é o método de publicação nem cria recursos no Render.
FROM node:22.22.0-bookworm-slim AS node
FROM ghcr.io/astral-sh/uv:0.12.23 AS uv
FROM python:3.12.14-slim-bookworm AS runtime

COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=uv /uv /uvx /usr/local/bin/
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
    && apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates openssl libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    REFLEX_TELEMETRY_ENABLED=false \
    METROFLOW_PUBLIC_URL=https://metroflow.invalid \
    METROFLOW_ENV=production \
    PORT=10000 \
    METROFLOW_DDT_ENABLED=0 \
    METROFLOW_CPTM_ENABLED=0 \
    METROFLOW_METRO_QUADRO_AUTORIZADO=0 \
    METROFLOW_MOTIVA_QUADRO_ENABLED=0 \
    XANO_AUTH_API_BASE_URL=https://127.0.0.1:9 \
    XANO_PLANNING_API_BASE_URL=https://127.0.0.1:9 \
    XANO_ADMIN_API_BASE_URL=https://127.0.0.1:9 \
    STATUS_XANO_ESCRITA_HABILITADA=0 \
    UV_CACHE_DIR=/app/.cache/uv

COPY . .
# Mesmo procedimento do Blueprint: lock congelado, instalação nova, exportação real.
RUN uv sync --frozen --no-dev \
    && uv run --no-sync python -m deploy.render.build
RUN useradd --create-home --uid 10001 metroflow \
    && chown -R metroflow:metroflow /app
USER metroflow
CMD ["uv", "run", "--no-sync", "python", "-m", "deploy.render.serve"]

# Alvo opcional para a suíte; não faz parte da imagem de runtime.
FROM runtime AS tests
RUN uv sync --frozen --group dev \
    && uv run --no-sync python -B -m pytest -q -p no:cacheprovider

FROM runtime AS lab
