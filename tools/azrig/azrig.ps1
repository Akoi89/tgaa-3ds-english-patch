# Azahar driving rig: capture without focus, keys without focus, audio metering.
# Usage: azrig.ps1 launch | cap <name> | key <name> [holdMs] | keys <a,b,down,...> | meter <seconds> | stop
param([string]$action, [string]$arg1, [string]$arg2)

$ErrorActionPreference = 'Stop'
$RIG = $PSScriptRoot
$CAPS = Join-Path $RIG "caps"
New-Item -ItemType Directory -Force $CAPS | Out-Null

Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class Az {
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
  public struct RECT { public int L, T, R, B; }
}
"@

# DS/3DS buttons -> the user's default Azahar keyboard profile (VK codes)
$VK = @{ a=65; b=83; x=90; y=88; up=84; down=71; left=70; right=72; l=81; r=87; start=77; select=78 }

function Get-Az {
  $p = Get-Process azahar -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
  if (-not $p) { throw "azahar not running" }
  return $p
}

function Cap([string]$name) {
  $p = Get-Az; $h = $p.MainWindowHandle
  $r = New-Object Az+RECT; [Az]::GetWindowRect($h, [ref]$r) | Out-Null
  # window rect is logical units; PrintWindow renders physical pixels at the window DPI
  $scale = [Az]::GetDpiForWindow($h) / 96.0
  $bmp = New-Object System.Drawing.Bitmap([int](($r.R - $r.L) * $scale), [int](($r.B - $r.T) * $scale))
  $g = [System.Drawing.Graphics]::FromImage($bmp); $dc = $g.GetHdc()
  [Az]::PrintWindow($h, $dc, 2) | Out-Null
  $g.ReleaseHdc($dc)
  $path = Join-Path $CAPS "$name.png"
  $bmp.Save($path); $g.Dispose(); $bmp.Dispose()
  Write-Output "cap -> $path"
}

function Key([string]$name, [int]$hold = 120) {
  $vk = $VK[$name.ToLower()]
  if (-not $vk) { throw "unknown button $name" }
  $p = Get-Az; $h = $p.MainWindowHandle
  [Az]::PostMessage($h, 0x100, [IntPtr]$vk, [IntPtr]1) | Out-Null
  Start-Sleep -Milliseconds $hold
  [Az]::PostMessage($h, 0x101, [IntPtr]$vk, [IntPtr]([long]0xC0000001)) | Out-Null
}

switch ($action) {
  'launch' {
    # azrig.ps1 launch          -> TGAA1 (default)
    # azrig.ps1 launch tgaa2    -> TGAA2
    # the two games do not use the same content id for index 0 -- TGAA1 is
    # 00000000.app, TGAA2 is 00000003.app -- so pick the largest .app present
    $tid = switch ("$arg1".ToLower()) {
      'tgaa2' { '001ae200' }
      'dgs2'  { '001ae200' }
      default { '0014ad00' }
    }
    $dir = "$env:APPDATA\AzaharPlus\sdmc\Nintendo 3DS\00000000000000000000000000000000\00000000000000000000000000000000\title\00040000\$tid\content"
    if (-not (Test-Path $dir)) { throw "no installed title at $dir" }
    $app = (Get-ChildItem "$dir\*.app" | Sort-Object Length -Descending | Select-Object -First 1).FullName
    if (-not $app) { throw "no .app in $dir" }
    Start-Process -FilePath $(if ($env:AZAHAR) { $env:AZAHAR } else { "azahar.exe" }) -ArgumentList "`"$app`""
    Write-Output "launched $tid"
  }
  'cap'  { Cap $arg1 }
  'key'  { Key $arg1 $(if ($arg2) { [int]$arg2 } else { 120 }); Write-Output "key $arg1" }
  'keys' {
    foreach ($k in $arg1.Split(',')) { Key $k.Trim(); Start-Sleep -Milliseconds $(if ($arg2) { [int]$arg2 } else { 700 }) }
    Write-Output "keys $arg1"
  }
  'meter' {
    Add-Type @"
using System; using System.Runtime.InteropServices;
[Guid("C02216F6-8C67-4B5B-9D00-D008E73E0064"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioMeterInformation {
  int GetPeakValue(out float peak);
}
[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDeviceEnumerator {
  int NotImpl1();
  int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice dev);
}
[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDevice {
  int Activate(ref Guid iid, int clsCtx, IntPtr pars, [MarshalAs(UnmanagedType.IUnknown)] out object o);
}
[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
public class MMDeviceEnumerator {}
public class Meter {
  public static float Peak() {
    var en = (IMMDeviceEnumerator)(new MMDeviceEnumerator());
    IMMDevice dev; en.GetDefaultAudioEndpoint(0, 0, out dev);
    var iid = typeof(IAudioMeterInformation).GUID; object o;
    dev.Activate(ref iid, 1, IntPtr.Zero, out o);
    float p; ((IAudioMeterInformation)o).GetPeakValue(out p);
    return p;
  }
}
"@
    $secs = if ($arg1) { [double]$arg1 } else { 3 }
    $n = [int]($secs * 20); $max = 0.0; $sum = 0.0
    for ($i = 0; $i -lt $n; $i++) {
      $v = [Meter]::Peak(); if ($v -gt $max) { $max = $v }; $sum += $v
      Start-Sleep -Milliseconds 50
    }
    "peak_max={0:N4} peak_avg={1:N4} over {2}s" -f $max, ($sum / $n), $secs
  }
  'meterlog' {
    Add-Type -TypeDefinition ([IO.File]::ReadAllText("$PSScriptRoot/meter.cs"))
    $secs = if ($arg1) { [double]$arg1 } else { 10 }
    $t0 = Get-Date; $last = -1
    while (((Get-Date) - $t0).TotalSeconds -lt $secs) {
      $el = ((Get-Date) - $t0).TotalSeconds
      $slot = [math]::Floor($el * 2)
      $v = [Meter2]::Peak()
      if ($slot -ne $last) { "{0,6:N2}s  {1:N4}" -f $el, $v; $last = $slot }
      Start-Sleep -Milliseconds 100
    }
  }
  'meterpid' {
    Add-Type -TypeDefinition ([IO.File]::ReadAllText("$PSScriptRoot/meter_pid.cs"))
    $az = (Get-Process azahar | Select-Object -First 1).Id
    $secs = if ($arg1) { [double]$arg1 } else { 5 }
    $t0 = Get-Date; $last = -1
    while (((Get-Date) - $t0).TotalSeconds -lt $secs) {
      $el = ((Get-Date) - $t0).TotalSeconds
      $slot = [math]::Floor($el * 2)
      $v = [MeterPid]::Peak([uint32]$az)
      if ($slot -ne $last) { "{0,6:N2}s  {1:N4}" -f $el, $v; $last = $slot }
      Start-Sleep -Milliseconds 100
    }
  }
  'stop' { Get-Process azahar -ErrorAction SilentlyContinue | Stop-Process; Write-Output "stopped" }
  default { Write-Output "actions: launch cap key keys meter stop" }
}
