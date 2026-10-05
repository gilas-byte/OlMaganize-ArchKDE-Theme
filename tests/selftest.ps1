# Windows selftest (PHASE-WindowsOnly.md §3): render, dry-run, idempotence, backup and restore
# for _selftest-win and the W1 targets that can run sandboxed.
#
# Nothing real is touched:
#   - %LOCALAPPDATA% and %USERPROFILE% point to a temp folder (fragments, YASB, fonts, state);
#   - GIBI_REGISTRY_REDIRECT moves every HKCU key the targets write under a throwaway
#     HKCU\Software\gibi-selftest-<random> key, deleted at the end;
#   - the real accent/theme/font keys are read before and after and must be identical.
# win-fonts (real archives, ~40 MB) only runs as dry-run; its code path is covered by the
# fake font of _selftest-win.
#
# Uso: powershell -ExecutionPolicy Bypass -File tests\selftest.ps1
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
[Console]::OutputEncoding = [Text.Encoding]::UTF8

function Pass($msg) { Write-Host "PASSOU: $msg" }
function Fail($msg) { Write-Host "FALHOU: $msg" -ForegroundColor Red; throw "selftest falhou: $msg" }

# --- sandbox -------------------------------------------------------------------------------
$tmp = Join-Path ([IO.Path]::GetTempPath()) ("gibi-selftest-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
$redirect = "Software\gibi-selftest-" + [guid]::NewGuid().ToString('N').Substring(0, 8)
$saved = @{ LOCALAPPDATA = $env:LOCALAPPDATA; USERPROFILE = $env:USERPROFILE; YASB_CONFIG_HOME = $env:YASB_CONFIG_HOME
            GIBI_REGISTRY_REDIRECT = $env:GIBI_REGISTRY_REDIRECT }
$realKeys = @(
    @('HKCU:\Software\Microsoft\Windows\DWM', 'AccentColor'),
    @('HKCU:\Software\Microsoft\Windows\DWM', 'ColorPrevalence'),
    @('HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Accent', 'AccentPalette'),
    @('HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize', 'AppsUseLightTheme')
)
function Read-Real {
    $realFonts = (Get-Item 'HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts').GetValueNames() -join '|'
    $vals = foreach ($k in $realKeys) {
        $v = (Get-Item $k[0]).GetValue($k[1], $null)
        if ($v -is [byte[]]) { [BitConverter]::ToString($v) } else { "$v" }
    }
    ($vals -join ';') + '#' + $realFonts
}
$realBefore = Read-Real

# Resolve Python before the sandbox hides %LOCALAPPDATA%\Programs\Python.
. (Join-Path $repo 'tooling\find-python.ps1')
$python = Find-GibiPython
if (-not $python) { Fail "Python >= 3.11 não encontrado" }
$pyArgs = @($python | Select-Object -Skip 1)
$pyExe = (& $python[0] @pyArgs -c "import sys; print(sys.executable)").Trim()
$saved.GIBI_PYTHON = $env:GIBI_PYTHON
$env:GIBI_PYTHON = $pyExe

# powershell.exe creates %USERPROFILE%\AppData\Roaming on startup; create it up front.
New-Item -ItemType Directory -Force "$tmp\local", "$tmp\home\AppData\Roaming" | Out-Null
$env:LOCALAPPDATA = "$tmp\local"
$env:USERPROFILE = "$tmp\home"
Remove-Item Env:\YASB_CONFIG_HOME -ErrorAction SilentlyContinue
$env:GIBI_REGISTRY_REDIRECT = $redirect
$regRoot = "HKCU:\$redirect"

$id = (Get-Content "$repo\palette.toml" | Select-String '^id = "(.+)"').Matches[0].Groups[1].Value
$dir = "$tmp\local\$id-selftest"
$yasb = "$tmp\home\.config\yasb"
$state = "$tmp\local\$id\state"
$targets = '_selftest-win,win-colors,windows-terminal,yasb,brave,stylus'

function Invoke-Gibi($script, [string[]]$extra) {
    $ErrorActionPreference = 'Continue'
    $out = & powershell -NoProfile -ExecutionPolicy Bypass -File "$repo\$script" @extra 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) { Write-Host $out; Fail "$script $($extra -join ' ') saiu com $LASTEXITCODE" }
    return $out
}

function Snapshot {
    # The state dir (and its parent %LOCALAPPDATA%\<id>, created with it) stays after uninstall.
    # The child powershell.exe also writes its own caches under %LOCALAPPDATA%\Microsoft\Windows\PowerShell.
    $files = Get-ChildItem $tmp -Recurse -Force |
        Where-Object { $_.FullName -notlike "$state*" -and $_.FullName -ne "$tmp\local\$id" -and
                       $_.FullName -notlike "$tmp\local\Microsoft\Windows\PowerShell*" -and
                       $_.FullName -ne "$tmp\local\Microsoft\Windows" -and $_.FullName -ne "$tmp\local\Microsoft" } |
        Sort-Object FullName |
        ForEach-Object {
            $rel = $_.FullName.Substring($tmp.Length)
            if ($_.PSIsContainer) { "$rel/" } else { "$rel " + (Get-FileHash $_.FullName -Algorithm SHA256).Hash }
        }
    $reg = if (Test-Path $regRoot) {
        Get-ChildItem $regRoot -Recurse | Sort-Object Name | ForEach-Object {
            $k = $_
            $k.Name + ' {' + (($k.GetValueNames() | Sort-Object | ForEach-Object {
                $v = $k.GetValue($_, $null, 'DoNotExpandEnvironmentNames')
                if ($v -is [byte[]]) { $v = [BitConverter]::ToString($v) }
                "$_=$v"
            }) -join ',') + '}'
        }
    }
    (@($files) + @($reg)) -join "`n"
}

try {
    # Pre-existing user content that must survive (LF, like the real styles.css).
    New-Item -ItemType Directory -Force $dir, $yasb, "$tmp\local\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe" | Out-Null
    [IO.File]::WriteAllText("$dir\host.conf", "linha do usuario = 1`n")
    [IO.File]::WriteAllText("$dir\host.css", "@import 'colors.css';`n.user { color: red; }`n")
    [IO.File]::WriteAllText("$yasb\styles.css", ":root { --bar_bg: #000000; }`n.yasb-bar { background-color: var(--bar_bg); }`n")
    [IO.File]::WriteAllText("$yasb\config.yaml", "watch_stylesheet: true`n")
    New-Item "$regRoot\Software\gibi-selftest\Values" -Force | Out-Null
    New-ItemProperty "$regRoot\Software\gibi-selftest\Values" -Name Dword -Value 7 -PropertyType DWord | Out-Null
    New-ItemProperty "$regRoot\Software\gibi-selftest\Values" -Name Obsolete -Value 'x' -PropertyType String | Out-Null
    New-Item "$regRoot\Software\Microsoft\Windows\DWM" -Force | Out-Null
    New-ItemProperty "$regRoot\Software\Microsoft\Windows\DWM" -Name AccentColor -Value 0x1234 -PropertyType DWord | Out-Null
    $before = Snapshot

    # --- dry-run ---------------------------------------------------------------------------
    $out = Invoke-Gibi 'install.ps1' @('-Only', $targets, '-DryRun')
    $now = Snapshot
    if ($now -ne $before) {
        Compare-Object ($before -split "`n") ($now -split "`n") | Format-Table -AutoSize | Out-String | Write-Host
        Fail "dry-run alterou arquivos ou registro"
    }
    if (Test-Path $state) { Fail "dry-run criou estado/backup" }
    if ($out -notmatch 'mudaria') { Write-Host $out; Fail "dry-run não listou mudanças" }
    $fonts = Invoke-Gibi 'install.ps1' @('-Only', 'win-fonts', '-DryRun')
    if ($fonts -notmatch 'baixar https://github.com/rsms/inter') { Write-Host $fonts; Fail "dry-run do win-fonts" }
    Pass "dry-run não altera nada"

    # --- install ---------------------------------------------------------------------------
    $out = Invoke-Gibi 'install.ps1' @('-Only', $targets)
    $afterFirst = Snapshot
    if ($afterFirst -eq $before) { Fail "install não mudou nada" }
    if ($out -match 'erro:') { Write-Host $out; Fail "install reportou erro" }
    $sample = Get-Content "$dir\sample.conf" -Raw
    if ($sample -notmatch 'background = #') { Fail "render de cor" }
    if ($sample -notmatch 'dollar = \$literal') { Fail "escape de `$`$" }
    if ((Get-Item "$dir\sample.conf").LinkType) { Fail "symlink no Windows (devia ser cópia)" }
    if ((Get-Content "$dir\sample.svg" -Raw) -notmatch 'rx="7"') { Fail "svg copiado" }
    $host_ = [IO.File]::ReadAllText("$dir\host.conf")
    if ($host_ -notmatch "linha do usuario = 1") { Fail "managed-block apagou conteúdo do usuário" }
    if ($host_ -match "`r`n") { Fail "managed-block converteu LF em CRLF" }
    $css = [IO.File]::ReadAllText("$dir\host.css")
    if (-not $css.StartsWith("@import 'colors.css';")) { Fail "bloco no fim, não no topo" }
    if ($css.TrimEnd() -notmatch '<<< ' + $id + ' <<< \*/$') { Fail "position = bottom" }
    $v = Get-Item "$regRoot\Software\gibi-selftest\Values"
    if ($v.GetValue('Dword') -ne 0) { Fail "registry dword" }
    if (('{0:X8}' -f $v.GetValue('Accent')) -ne 'FF00EAFF') { Fail "registry abgr" }
    if ($v.GetValue('Name') -ne 'Gibi') { Fail "registry string" }
    if ($v.GetValue('Palette').Length -ne 32) { Fail "registry accent-palette" }
    if ($null -ne $v.GetValue('Obsolete')) { Fail "registry delete" }
    if ((Get-Item "$regRoot\Software\gibi-selftest\Created\Deep").GetValue('Value') -ne $id) { Fail "registry em chave nova" }
    $fontsKey = Get-Item "$regRoot\Software\Microsoft\Windows NT\CurrentVersion\Fonts"
    if ($fontsKey.GetValue('Gibi Selftest Regular (TrueType)') -ne "$tmp\local\Microsoft\Windows\Fonts\GibiSelftest-Regular.ttf") { Fail "fonte registrada" }
    if (-not (Test-Path "$tmp\local\Microsoft\Windows\Fonts\GibiSelftest-Bold.ttf")) { Fail "fonte copiada" }
    if (Test-Path "$tmp\local\Microsoft\Windows\Fonts\README.txt") { Fail "glob de fontes pegou arquivo que não é fonte" }
    $dwm = Get-Item "$regRoot\Software\Microsoft\Windows\DWM"
    if (('{0:X8}' -f $dwm.GetValue('AccentColor')) -ne 'FF00EAFF') { Fail "win-colors AccentColor (redirecionado)" }
    if ($dwm.GetValue('ColorPrevalence') -ne 0) { Fail "win-colors ColorPrevalence" }
    $frag = "$tmp\local\Microsoft\Windows Terminal\Fragments\$id\$id.json"
    $json = Get-Content $frag -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($json.schemes[0].background -ne '#2E261F' -or $json.profiles.Count -ne 2) { Fail "fragmento do Windows Terminal" }
    $styles = [IO.File]::ReadAllText("$yasb\styles.css")
    if (-not $styles.StartsWith(":root { --bar_bg: #000000; }")) { Fail "yasb: styles.css do usuário alterado" }
    if ($styles -notmatch '@import "' + $id + '.css";') { Fail "yasb: @import ausente" }
    if ($styles -match "`r`n") { Fail "yasb: LF virou CRLF" }
    if ((Get-Content "$yasb\config.yaml" -Raw) -ne "watch_stylesheet: true`n") { Fail "yasb: config.yaml tocado" }
    if ((Get-Content "$yasb\$id.css" -Raw) -match '\$\{') { Fail "yasb: placeholder sobrando" }
    if (-not (Test-Path "$tmp\local\$id\brave-theme\manifest.json")) { Fail "brave em %LOCALAPPDATA%\$id" }
    if (Test-Path "$repo\vendor\catppuccin-userstyles\styles") {
        $null = Get-Content "$tmp\local\$id\stylus\import.json" -Raw -Encoding UTF8 | ConvertFrom-Json
    } else { Write-Host "PULADO: stylus (submodule vazio)" }
    $backups = @(Get-ChildItem "$state\backups" -Recurse -Filter manifest.json)
    if ($backups.Count -ne 1) { Fail "esperado 1 backup, achei $($backups.Count)" }
    Pass "install aplica copy, managed-block, registry, fontes, fragmento, yasb, brave e stylus"

    # --- idempotence -----------------------------------------------------------------------
    $out = Invoke-Gibi 'install.ps1' @('-Only', $targets)
    if ((Snapshot) -ne $afterFirst) { Fail "segunda execução alterou arquivos ou registro" }
    if ($out -match 'mudança\(s\)') { Write-Host $out; Fail "segunda execução reportou mudanças" }
    if (@(Get-ChildItem "$state\backups" -Recurse -Filter manifest.json).Count -ne 1) { Fail "segunda execução criou backup" }
    Pass "idempotente"

    # --- restore ---------------------------------------------------------------------------
    $null = Invoke-Gibi 'uninstall.ps1' @('-DryRun')
    if ((Snapshot) -ne $afterFirst) { Fail "uninstall -DryRun alterou algo" }
    $null = Invoke-Gibi 'uninstall.ps1' @()
    $after = Snapshot
    if ($after -ne $before) {
        Compare-Object ($before -split "`n") ($after -split "`n") | Format-Table -AutoSize | Out-String | Write-Host
        Fail "uninstall não voltou ao estado original"
    }
    Pass "uninstall restaura arquivos e registro byte a byte"
    $out = Invoke-Gibi 'uninstall.ps1' @()
    if ($out -notmatch 'Nada para restaurar') { Fail "uninstall repetido" }
    Pass "uninstall repetido é seguro"
} finally {
    foreach ($k in $saved.Keys) {
        if ($null -eq $saved[$k]) { Remove-Item "Env:\$k" -ErrorAction SilentlyContinue } else { Set-Item "Env:\$k" $saved[$k] }
    }
    if (Test-Path $regRoot) { Remove-Item $regRoot -Recurse -Force }
    if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
}

if ((Read-Real) -ne $realBefore) { Fail "AS CHAVES REAIS MUDARAM (cor/tema/fontes)" }
Pass "chaves reais de cor, tema e fontes intactas"
Write-Host "Selftest Windows OK."
