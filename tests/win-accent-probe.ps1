# Spike S0 probe (docs/SPIKE-S0.md §2): does Windows pick up an accent color written only to
# the registry + WM_SETTINGCHANGE, without logoff? TOUCHES THE REAL HKCU KEYS, so it is never
# run by the selftest. Run it by hand:
#
#   .\tests\win-accent-probe.ps1 backup    # saves the current values to %TEMP%\gibi-accent-probe.json
#   .\tests\win-accent-probe.ps1 apply     # writes #FFEA00 and prints the effective accent
#   .\tests\win-accent-probe.ps1 restore   # puts the saved values back and prints the accent again
#   .\tests\win-accent-probe.ps1 read      # just prints the effective accent
#
# "Effective accent" is what WinRT UISettings reports, read in a fresh process.
param([Parameter(Mandatory)][ValidateSet('backup', 'apply', 'restore', 'read')][string]$Action)
$ErrorActionPreference = 'Stop'
$backup = Join-Path $env:TEMP 'gibi-accent-probe.json'
$keys = @(
    @{ Path = 'HKCU:\Software\Microsoft\Windows\DWM'; Names = 'AccentColor', 'ColorizationColor', 'ColorizationAfterglow' },
    @{ Path = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Accent'; Names = 'AccentPalette', 'StartColorMenu', 'AccentColorMenu' }
)

Add-Type -Namespace GibiProbe -Name Native -MemberDefinition @'
[DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
public static extern System.IntPtr SendMessageTimeout(System.IntPtr hWnd, uint Msg, System.UIntPtr wParam,
    string lParam, uint fuFlags, uint uTimeout, out System.UIntPtr lpdwResult);
'@ -ErrorAction SilentlyContinue

# PowerShell 5.1 parses 0xFF00EAFF as a negative Int32 already; DWORD values must be Int32.
function Dword($u) { if ($u -is [int]) { return $u }; [BitConverter]::ToInt32([BitConverter]::GetBytes([uint32]$u), 0) }

function Send-ColorChange {
    $r = [UIntPtr]::Zero
    [void][GibiProbe.Native]::SendMessageTimeout([IntPtr]0xffff, 0x1A, [UIntPtr]::Zero, 'ImmersiveColorSet', 2, 2000, [ref]$r)
}

function Show-Accent {
    powershell -NoProfile -Command {
        [void][Windows.UI.ViewManagement.UISettings, Windows.UI.ViewManagement, ContentType = WindowsRuntime]
        $ui = New-Object Windows.UI.ViewManagement.UISettings
        foreach ($t in 'Accent', 'AccentLight2', 'AccentDark1') {
            $c = $ui.GetColorValue([Windows.UI.ViewManagement.UIColorType]::$t)
            '{0,-13} #{1:X2}{2:X2}{3:X2}' -f $t, $c.R, $c.G, $c.B
        }
    }
}

switch ($Action) {
    'read' { Show-Accent }
    'backup' {
        if (Test-Path $backup) { throw "backup already exists, restore or delete it first: $backup" }
        $data = foreach ($k in $keys) {
            $item = Get-Item $k.Path
            foreach ($n in $k.Names) {
                $v = $item.GetValue($n, $null)
                [pscustomobject]@{
                    Path = $k.Path; Name = $n; Exists = ($null -ne $v)
                    Kind = $(if ($null -ne $v) { $item.GetValueKind($n).ToString() })
                    Value = $(if ($v -is [byte[]]) { [Convert]::ToBase64String($v) } else { $v })
                }
            }
        }
        $data | ConvertTo-Json | Set-Content -Encoding UTF8 $backup
        "saved $backup"
    }
    'apply' {
        if (-not (Test-Path $backup)) { throw "run 'backup' first" }
        # #FFEA00 and the shade ramp win-colors computes (L3 L2 L1 accent D1 D2 D3 D3).
        $palette = [byte[]](0xFF, 0xF3, 0x73, 0, 0xFF, 0xF0, 0x4C, 0, 0xFF, 0xED, 0x26, 0, 0xFF, 0xEA, 0x00, 0,
            0xD9, 0xC7, 0x00, 0, 0x99, 0x8C, 0x00, 0, 0x59, 0x52, 0x00, 0, 0x59, 0x52, 0x00, 0)
        $accent = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Accent'
        $dwm = 'HKCU:\Software\Microsoft\Windows\DWM'
        New-ItemProperty $accent -Name AccentPalette -Value $palette -PropertyType Binary -Force | Out-Null
        New-ItemProperty $accent -Name AccentColorMenu -Value (Dword 0xFF00EAFF) -PropertyType DWord -Force | Out-Null
        New-ItemProperty $accent -Name StartColorMenu -Value (Dword 0xFF00C7D9) -PropertyType DWord -Force | Out-Null
        New-ItemProperty $dwm -Name AccentColor -Value (Dword 0xFF00EAFF) -PropertyType DWord -Force | Out-Null
        New-ItemProperty $dwm -Name ColorizationColor -Value (Dword 0xC4FFEA00) -PropertyType DWord -Force | Out-Null
        New-ItemProperty $dwm -Name ColorizationAfterglow -Value (Dword 0xC4FFEA00) -PropertyType DWord -Force | Out-Null
        Send-ColorChange
        Start-Sleep -Milliseconds 800
        Show-Accent
    }
    'restore' {
        foreach ($e in (Get-Content $backup -Raw | ConvertFrom-Json)) {
            if ($e.Exists) {
                $v = if ($e.Kind -eq 'Binary') { [Convert]::FromBase64String($e.Value) } else { Dword $e.Value }
                New-ItemProperty $e.Path -Name $e.Name -Value $v -PropertyType $e.Kind -Force | Out-Null
            } else {
                Remove-ItemProperty $e.Path -Name $e.Name -ErrorAction SilentlyContinue
            }
        }
        Send-ColorChange
        Remove-Item $backup
        Start-Sleep -Milliseconds 800
        Show-Accent
    }
}
