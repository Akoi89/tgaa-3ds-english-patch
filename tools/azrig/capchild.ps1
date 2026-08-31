# A BLACK CAPTURE IS NOT EVIDENCE OF A BROKEN GAME.
# PrintWindow returns the Qt chrome but can come back all-black for the GL
# surface -- seen after force-killing Azahar, and after a second instance has
# existed. The game keeps running at 60 FPS with audio throughout.
# Before concluding anything from a black frame, prove liveness another way:
#   azrig.ps1 meterpid 4        -> is it making sound?
#   playtime.ps1 -x .. -y ..    -> does a known clip still play?
# Both worked while every screenshot was pure black, and a clean CIA install
# was briefly mistaken for a boot failure because of it.
# Capture Azahar's OpenGL child surface (QWindowOwnDC) - position independent.
param([string]$name = "cap")
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Collections.Generic; using System.Runtime.InteropServices; using System.Text;
public class AzC {
  public delegate bool EnumProc(IntPtr h, IntPtr p);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr h, EnumProc cb, IntPtr p);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
  public struct RECT { public int L,T,R,B; }
  public static IntPtr Gl(IntPtr main) {
    IntPtr found = IntPtr.Zero;
    EnumChildWindows(main, (h,p) => {
      var sb = new StringBuilder(256); GetClassName(h, sb, 256);
      if (sb.ToString().Contains("OwnDC") && IsWindowVisible(h)) { found = h; return false; }
      return true;
    }, IntPtr.Zero);
    return found;
  }
}
"@
$proc = Get-Process azahar -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $proc) { throw "azahar not running" }
$h = [AzC]::Gl($proc.MainWindowHandle)
if ($h -eq [IntPtr]::Zero) { throw "no OwnDC GL child window found" }
$r = New-Object AzC+RECT; [AzC]::GetWindowRect($h,[ref]$r) | Out-Null
$s = [AzC]::GetDpiForWindow($h)/96.0
$bmp = New-Object System.Drawing.Bitmap([int](($r.R-$r.L)*$s), [int](($r.B-$r.T)*$s))
$g = [System.Drawing.Graphics]::FromImage($bmp); $dc = $g.GetHdc()
[AzC]::PrintWindow($h,$dc,2) | Out-Null
$g.ReleaseHdc($dc)
$dir = (Join-Path $PSScriptRoot "caps")
$out = Join-Path $dir "$name.png"
$bmp.Save($out); $g.Dispose(); $bmp.Dispose()
Write-Output "cap -> $out"
