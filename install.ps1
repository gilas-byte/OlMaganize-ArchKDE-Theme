# Uso: .\install.ps1 [-DryRun] [-Only alvo[,alvo]] [-List]
# Windows: entrada fina para `python -m tooling apply` (PHASE-WindowsOnly.md §6). Sem admin.
param(
    [switch]$DryRun,
    [string[]]$Only,
    [switch]$List
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'tooling\find-python.ps1')

$python = Find-GibiPython
if (-not $python) {
    Write-Error "Python >= 3.11 não encontrado. Instale por usuário, sem admin: winget install --id Python.Python.3.13 --scope user"
    exit 1
}

$tooling = @('-m', 'tooling', 'apply')
if ($DryRun) { $tooling += '--dry-run' }
if ($List) { $tooling += '--list' }
if ($Only) { $tooling += @('--only', ($Only -join ',')) }

# Templates and user files are UTF-8; Python on Windows defaults to the ANSI code page.
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
