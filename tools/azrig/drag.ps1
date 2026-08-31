# Drag on Azahar's touch screen. Coords in CAPTURE-image pixels.
param([int]$x1,[int]$y1,[int]$x2,[int]$y2,[int]$steps=14)
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Text;
public class AzD {
  public delegate bool EnumProc(IntPtr h, IntPtr p);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr h, EnumProc cb, IntPtr p);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
  public static IntPtr Gl(IntPtr main) {
    IntPtr f = IntPtr.Zero;
    EnumChildWindows(main, (h,p) => {
      var sb = new StringBuilder(256); GetClassName(h, sb, 256);
      if (sb.ToString().Contains("OwnDC") && IsWindowVisible(h)) { f = h; return false; }
      return true; }, IntPtr.Zero);
    return f; }
}
"@
$p = Get-Process azahar | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
$h = [AzD]::Gl($p.MainWindowHandle)
$s = [AzD]::GetDpiForWindow($h)/96.0
function LP([int]$x,[int]$y){ [IntPtr]((([int]($y/$s)) -shl 16) -bor ([int]($x/$s))) }
[AzD]::PostMessage($h,0x200,[IntPtr]0,(LP $x1 $y1)) | Out-Null
Start-Sleep -Milliseconds 60
[AzD]::PostMessage($h,0x201,[IntPtr]1,(LP $x1 $y1)) | Out-Null
for($i=1;$i -le $steps;$i++){
  $cx=[int]($x1+($x2-$x1)*$i/$steps); $cy=[int]($y1+($y2-$y1)*$i/$steps)
  [AzD]::PostMessage($h,0x200,[IntPtr]1,(LP $cx $cy)) | Out-Null
  Start-Sleep -Milliseconds 25
}
[AzD]::PostMessage($h,0x202,[IntPtr]0,(LP $x2 $y2)) | Out-Null
Write-Output "drag ($x1,$y1)->($x2,$y2)"
