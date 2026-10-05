# Shared by install.ps1 and uninstall.ps1: finds a Python >= 3.11 without relying on PATH.
# The `python` on PATH is often just the Microsoft Store alias, and per-user installs from
# python.org do not always add themselves to PATH (docs/SPIKE-S0.md).

function Find-GibiPython {
    $candidates = [System.Collections.Generic.List[object]]::new()
    foreach ($py in @((Get-Command py -ErrorAction SilentlyContinue).Source,
                      "$env:LOCALAPPDATA\Programs\Python\Launcher\py.exe")) {
        if ($py -and (Test-Path $py)) { $candidates.Add(@($py, '-3')) }
    }
    $onPath = (Get-Command python -ErrorAction SilentlyContinue).Source
    if ($onPath) { $candidates.Add(@($onPath)) }
    $installs = Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe", `
                              "$env:ProgramFiles\Python3*\python.exe" -ErrorAction SilentlyContinue |
        Sort-Object { [int]($_.Directory.Name -replace '\D', '') } -Descending
    foreach ($exe in $installs) { $candidates.Add(@($exe.FullName)) }

    foreach ($cmd in $candidates) {
        $exe = $cmd[0]
        $rest = @($cmd | Select-Object -Skip 1)
        try {
            $ok = & $exe @rest -c "import sys; print(sys.version_info >= (3, 11))" 2>$null
        } catch {
            continue
        }
        if ($LASTEXITCODE -eq 0 -and "$ok".Trim() -eq 'True') { return , $cmd }
    }
    return $null
}
