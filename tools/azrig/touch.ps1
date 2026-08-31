# Touch-click Azahar's bottom screen. Coords are in CAPTURE-image pixels
# (what capchild.ps1 saves); this converts to the child window's logical
# client coords using the window DPI, so it matches what you see.
param([int]$x, [int]$y)
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Text;
public class AzT {
  public delegate bool EnumProc(IntPtr h, IntPtr p);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr h, EnumProc cb, IntPtr p);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
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
$proc = Get-Process azahar | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
$h = [AzT]::Gl($proc.MainWindowHandle)
$s = [AzT]::GetDpiForWindow($h)/96.0
$lx = [int]($x / $s); $ly = [int]($y / $s)
$lp = [IntPtr](($ly -shl 16) -bor $lx)
[AzT]::PostMessage($h, 0x200, [IntPtr]0, $lp) | Out-Null   # WM_MOUSEMOVE
Start-Sleep -Milliseconds 60
[AzT]::PostMessage($h, 0x201, [IntPtr]1, $lp) | Out-Null   # WM_LBUTTONDOWN
Start-Sleep -Milliseconds 90
[AzT]::PostMessage($h, 0x202, [IntPtr]0, $lp) | Out-Null   # WM_LBUTTONUP
Write-Output "touch img($x,$y) -> logical($lx,$ly)"
