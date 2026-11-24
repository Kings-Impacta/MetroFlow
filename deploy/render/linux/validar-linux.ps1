#requires -Version 5.1
param([switch]$ManterContainer)
$ErrorActionPreference = 'Stop'
$project = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../../..')).Path
$reportDir = Join-Path $project '.cache\linux-validation-20261123'
New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
$runtimeImage = 'metroflow-linux-lab:20261123'
$testsImage = 'metroflow-linux-tests:20261123'
$container = 'metroflow-linux-validation-20261123'
$created = $false

function Invoke-DockerChecked {
    param([string[]]$DockerArguments, [string]$LogName, [switch]$Capture)
    $saved = $ErrorActionPreference
    try {
        # Windows PowerShell 5 trata stderr nativo como erro: conferir o exit code.
        $ErrorActionPreference = 'Continue'
        $lines = @(& docker @DockerArguments 2>&1 | ForEach-Object { $_.ToString() })
        $code = $LASTEXITCODE
    } finally { $ErrorActionPreference = $saved }
    $text = $lines -join [Environment]::NewLine
    if ($LogName) { $text | Set-Content -LiteralPath (Join-Path $reportDir $LogName) -Encoding UTF8 }
    if ($code -ne 0) { throw "Docker falhou ($code). Consulte $LogName em $reportDir. $text" }
    if ($Capture) { return $text }
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw 'Docker Desktop nao instalado.' }
$system = Invoke-DockerChecked -DockerArguments @('info','--format','{{.OSType}}') -LogName 'docker-info.log' -Capture
if ($system.Trim() -ne 'linux') { throw 'O motor Docker precisa estar em Linux.' }
$existing = Invoke-DockerChecked -DockerArguments @('ps','-a','--filter',"name=^/$container$",'--format','{{.ID}}') -Capture
if ($existing.Trim()) { throw "Ja existe $container. Nada sera removido ou substituido." }

Push-Location -LiteralPath $project
try {
    Write-Host '1/5: Instalacao limpa, build de producao e suite Python em Linux. Pode demorar alguns minutos.'
    Invoke-DockerChecked -DockerArguments @('build','--progress=plain','--target','tests','-t',$testsImage,
        '-f','deploy/render/linux/Dockerfile','.') -LogName 'build-tests.log'
    Write-Host '2/5: Preparando a imagem de runtime sem dependencias de teste.'
    Invoke-DockerChecked -DockerArguments @('build','--progress=plain','--target','lab','-t',$runtimeImage,
        '-f','deploy/render/linux/Dockerfile','.') -LogName 'build-runtime.log'
    Write-Host '3/5: Iniciando o supervisor de producao, sem rede externa, com 512 MB e 0,1 CPU.'
    Invoke-DockerChecked -DockerArguments @('run','-d','--name',$container,'--network','none',
        '--memory','512m','--memory-swap','512m','--cpus','0.1',$runtimeImage) -LogName 'container-id.log'
    $created = $true
    $network = Invoke-DockerChecked -DockerArguments @('inspect','--format','{{.HostConfig.NetworkMode}}',$container) -Capture
    if ($network.Trim() -ne 'none') { throw 'Rede do laboratorio diferente da esperada.' }
    Write-Host '4/5: Conferindo paginas, assets, APIs sem sessao e upgrade WebSocket.'
    Invoke-DockerChecked -DockerArguments @('exec',$container,'.venv/bin/python','-m','deploy.render.linux.check_runtime') -LogName 'runtime-primeira.json'
    Invoke-DockerChecked -DockerArguments @('stats','--no-stream','--format','{{json .}}',$container) -LogName 'runtime-stats.json'
    Write-Host '5/5: Reiniciando o mesmo container e repetindo a verificacao.'
    Invoke-DockerChecked -DockerArguments @('restart',$container) -LogName 'restart.log'
    Invoke-DockerChecked -DockerArguments @('exec',$container,'.venv/bin/python','-m','deploy.render.linux.check_runtime') -LogName 'runtime-reinicio.json'
    $stateJson = Invoke-DockerChecked -DockerArguments @('inspect','--format','{{json .State}}',$container) -LogName 'runtime-state.json' -Capture
    $state = $stateJson | ConvertFrom-Json
    if ($state.OOMKilled -or -not $state.Running) { throw 'Runtime nao permaneceu ativo ou houve encerramento por memoria.' }
    Write-Host "Validacao Linux concluida. Evidencias: $reportDir"
    Write-Host 'Nenhuma publicacao. Fontes desligadas; Xano de producao inacessivel no runtime.'
} finally {
    if ($created) {
        try { Invoke-DockerChecked -DockerArguments @('logs',$container) -LogName 'runtime-server.log' } catch { Write-Warning $_.Exception.Message }
        if (-not $ManterContainer) {
            # Somente o container criado por esta execucao; nunca volumes ou outros containers.
            try { Invoke-DockerChecked -DockerArguments @('stop',$container) -LogName 'stop.log' } catch { Write-Warning $_.Exception.Message }
        }
    }
    Pop-Location
}
