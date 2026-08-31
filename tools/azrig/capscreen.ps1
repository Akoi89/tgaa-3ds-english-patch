# Capture the Azahar window by grabbing its rectangle from the SCREEN.
# Fallback for when PrintWindow returns black (GL child not redirected).
param([string]$name = 'screen')
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class ScrCap {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
}
"@
[ScrCap]::SetProcessDPIAware() | Out-Null
$p = Get-Process azahar | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $p) { throw "azahar not running" }
[ScrCap]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
[ScrCap]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 700
$r = New-Object ScrCap+RECT
[ScrCap]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
$w = $r.R - $r.L; $h = $r.B - $r.T
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.L, $r.T, 0, 0, (New-Object System.Drawing.Size($w, $h)))
$dir = Join-Path $PSScriptRoot 'caps'
if (-not (Test-Path $dir)) { New-Item -ItemType Directory $dir | Out-Null }
$out = Join-Path $dir "$name.png"
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output "cap -> $out ($w x $h)"
