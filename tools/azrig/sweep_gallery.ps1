# Measure how long each requested line of one DLC voice gallery actually plays.
#
#   sweep_gallery.ps1 -Rows 2,4,5,6
#
# The game must ALREADY be on the DLC list page of the issue you want, with the
# Audio tile at -AudioX/-AudioY. Issues do not all carry the same tiles (issue 8
# has Editor's Notes and no Audio at all), so the tile position is a parameter,
# not an assumption -- and this script deliberately does not press B to navigate,
# because B on the DLC list opens "return to title screen?".
#
# Rows 1-4 are visible without scrolling; 5+ need two taps of the down arrow,
# after which the visible window is rows 3-6.
param([int[]]$Rows, [double]$Window = 10.0, [int]$AudioX = 511, [int]$AudioY = 785)

$ErrorActionPreference = 'Stop'
$RIG = $PSScriptRoot
$ROWY = @(592, 676, 760, 842)          # y of the four visible rows
$DOWN = @{ x = 684; y = 920 }

function Tap($x, $y, $wait = 2) { & "$RIG\touch.ps1" -x $x -y $y | Out-Null; Start-Sleep -Seconds $wait }

Tap $AudioX $AudioY 5

$scrolled = $false
foreach ($r in ($Rows | Sort-Object)) {
  if ($r -gt 4 -and -not $scrolled) {
    Tap $DOWN.x $DOWN.y 2; Tap $DOWN.x $DOWN.y 3
    $scrolled = $true
  }
  $y = if ($r -le 4) { $ROWY[$r - 1] } else { $ROWY[$r - 3] }   # after scroll, window is rows 3-6
  "row $r :"
  & "$RIG\playtime.ps1" -x 690 -y $y -Window $Window
  Start-Sleep -Seconds 2
}
& "$RIG\azrig.ps1" key b | Out-Null      # leaves the gallery, back to the DLC list
Start-Sleep -Seconds 3
