# Iniciador local com as três fontes públicas validadas, sem chave ou token.
$ErrorActionPreference = 'Stop'
$previous = Get-Location
$settings = @{
    METROFLOW_DDT_ENABLED = '0'
    METROFLOW_CPTM_ENABLED = '1'
    METROFLOW_METRO_QUADRO_AUTORIZADO = '1'
    METROFLOW_MOTIVA_QUADRO_ENABLED = '1'
}
$saved = @{}
foreach ($name in $settings.Keys) {
    $saved[$name] = [Environment]::GetEnvironmentVariable($name,'Process')
}
try {
    foreach ($name in $settings.Keys) {
        [Environment]::SetEnvironmentVariable($name,$settings[$name],'Process')
    }
    Write-Host 'Status local: Metrô, CPTM e Motiva. Linhas 6, 7 e 13 sem cobertura por enquanto.'
    Write-Host 'Pare o servidor anterior com Ctrl+C antes de iniciar esta versão.'
    & (Join-Path $PSScriptRoot 'iniciar-metroflow.ps1')
} finally {
    foreach ($name in $settings.Keys) {
        [Environment]::SetEnvironmentVariable($name,$saved[$name],'Process')
    }
    Set-Location -LiteralPath $previous
}
