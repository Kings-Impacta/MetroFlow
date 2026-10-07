$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "O uv não está instalado. Consulte https://docs.astral.sh/uv/getting-started/installation/ e execute novamente."
}

Write-Host "Preparando o ambiente do MetroFlow..." -ForegroundColor Cyan
uv sync --frozen --group dev --python 3.12
if ($LASTEXITCODE -ne 0) {
    throw "Não foi possível preparar o ambiente do projeto."
}

if (-not $env:XANO_AUTH_API_BASE_URL) {
    $env:XANO_AUTH_API_BASE_URL = "https://x8ki-letl-twmt.n7.xano.io/api:75UptKSb"
}

if (-not $env:XANO_PLANNING_API_BASE_URL) {
    $env:XANO_PLANNING_API_BASE_URL = "https://x8ki-letl-twmt.n7.xano.io/api:metroflow-planejamento"
}

Write-Host "Iniciando o MetroFlow. Abra o endereço exibido abaixo e mantenha este terminal aberto." -ForegroundColor Green
& .\.venv\Scripts\python.exe -m reflex run --env prod --single-port 2>&1 |
    Tee-Object -FilePath reflex.log
