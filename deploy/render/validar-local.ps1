#requires -Version 5.1
$ErrorActionPreference = 'Stop'
$project = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location -LiteralPath $project
$names = @('UV_CACHE_DIR','TEMP','TMP','npm_config_cache','METROFLOW_PUBLIC_URL','PORT')
$saved = @{}
foreach ($name in $names) { $saved[$name] = [Environment]::GetEnvironmentVariable($name,'Process') }
try {
    $env:UV_CACHE_DIR = Join-Path $project '.uv-cache'
    $env:TEMP = Join-Path $project '.cache/tmp'
    $env:TMP = $env:TEMP
    New-Item -ItemType Directory -Force -Path $env:TEMP > $null
    $env:npm_config_cache = Join-Path $project '.cache/npm'
    $env:METROFLOW_PUBLIC_URL = 'http://localhost:10000'
    $env:PORT = '10000'
    uv sync --frozen --group dev --python 3.12
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao preparar dependencias.' }
    uv run --no-sync python -B -m pytest -q -p no:cacheprovider
    if ($LASTEXITCODE -ne 0) { throw 'Testes falharam; build nao iniciado.' }
    uv run --no-sync python -m deploy.render.build --local
    if ($LASTEXITCODE -ne 0) { throw 'Build incompleto; servidor nao iniciado.' }
    Write-Host 'Build e testes aprovados. Servidor local em http://localhost:10000; Ctrl+C para parar.'
    Write-Host 'Fontes de status desligadas. Nenhuma publicacao sera executada.'
    uv run --no-sync python -m deploy.render.serve --local
    if ($LASTEXITCODE -ne 0) { throw 'Servidor local encerrou com erro.' }
} finally {
    foreach ($name in $names) { [Environment]::SetEnvironmentVariable($name,$saved[$name],'Process') }
    Pop-Location
}
