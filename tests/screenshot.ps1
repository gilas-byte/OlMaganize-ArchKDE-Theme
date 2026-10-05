# Screenshot for the visual checklists (docs/CHECKLIST-W1.md), the Windows counterpart of
# `spectacle -b -f -n -o ~/gibi-check-<app>.png`. Saves %USERPROFILE%\gibi-check-<Name>.png.
#
# Uso:
#   .\tests\screenshot.ps1 -Name terminal            # tela inteira (todos os monitores) em 3 s
#   .\tests\screenshot.ps1 -Name terminal -Window    # só a janela em foco quando o tempo acabar
#   .\tests\screenshot.ps1 -Name yasb -Delay 0
param(
    [Parameter(Mandatory)][string]$Name,
    [int]$Delay = 3,
    [switch]$Window
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing, System.Windows.Forms
Add-Type -Namespace GibiShot -Name Native -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
[DllImport("user32.dll")] public static extern System.IntPtr GetForegroundWindow();
[DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(System.IntPtr hwnd, int attr, out RECT rect, int size);
[System.Runtime.InteropServices.StructLayout(System.Runtime.InteropServices.LayoutKind.Sequential)]
public struct RECT { public int Left, Top, Right, Bottom; }
'@
# Physical pixels, not the scaled ones (the colors are what matters, but the size should be real).
[void][GibiShot.Native]::SetProcessDPIAware()

if ($Delay -gt 0) {
    Write-Host "Capturando em $Delay s$(if ($Window) { ' (deixe a janela em foco)' })..."
    Start-Sleep -Seconds $Delay
}

if ($Window) {
    $rect = New-Object GibiShot.Native+RECT
    # DWMWA_EXTENDED_FRAME_BOUNDS (9): the visible frame, without the invisible resize border.
    $hr = [GibiShot.Native]::DwmGetWindowAttribute([GibiShot.Native]::GetForegroundWindow(), 9, [ref]$rect,
        [Runtime.InteropServices.Marshal]::SizeOf($rect))
    if ($hr -ne 0) { throw "não consegui ler a janela em foco (HRESULT $hr)" }
    $bounds = [Drawing.Rectangle]::FromLTRB($rect.Left, $rect.Top, $rect.Right, $rect.Bottom)
} else {
    $bounds = [Windows.Forms.SystemInformation]::VirtualScreen
}

$bmp = New-Object Drawing.Bitmap $bounds.Width, $bounds.Height
$g = [Drawing.Graphics]::FromImage($bmp)
try {
    $g.CopyFromScreen($bounds.Location, [Drawing.Point]::Empty, $bounds.Size)
    $out = Join-Path $env:USERPROFILE "gibi-check-$Name.png"
    $bmp.Save($out, [Drawing.Imaging.ImageFormat]::Png)
    Write-Host "Salvo: $out ($($bounds.Width)x$($bounds.Height))"
} finally {
    $g.Dispose()
    $bmp.Dispose()
}
