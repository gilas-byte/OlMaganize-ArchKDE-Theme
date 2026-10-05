# Uso: .\uninstall.ps1 [-DryRun] [-Only alvo[,alvo]]
# Windows: entrada fina para `python -m tooling restore`.
param(
    [switch]$DryRun,
    [string[]]$Only
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'tooling\find-python.ps1')

$python = Find-GibiPython
if (-not $python) {
    Write-Error "Python >= 3.11 não encontrado."
    exit 1
}

$tooling = @('-m', 'tooling', 'restore')
if ($DryRun) { $tooling += '--dry-run' }
if ($Only) { $tooling += @('--only', ($Only -join ',')) }

$oldUtf8 = $env:PYTHONUTF8
$env:PYTHONUTF8 = '1'
$exe = $python[0]
$rest = @($python | Select-Object -Skip 1)
# tooling resolves paths from the repo root; Push/Pop keeps the caller's location.
Push-Location -LiteralPath $PSScriptRoot
try {
    & $exe @rest @tooling
    $code = $LASTEXITCODE
} finally {
    Pop-Location
    $env:PYTHONUTF8 = $oldUtf8
}
exit $code
