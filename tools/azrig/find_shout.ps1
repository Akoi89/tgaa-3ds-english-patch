# Advance a scene with A presses until a character shout fires, then capture it.
#
# Shouts cannot be spotted by peak level alone -- background music already sits
# near full scale. The signature is the BGM CUTTING OUT for a beat and then a
# loud burst, which is what the game does for an Objection. So watch for a drop
# below -Quiet held briefly, followed by a rise above -Loud.
#
#   find_shout.ps1 -Presses 200
#
# Uses the per-process meter: a system-wide reading would include anything else
# the machine is playing.
param([int]$Presses = 200, [double]$Quiet = 0.04, [double]$Loud = 0.60,
      [int]$GapMs = 320, [string]$Tag = 'shout')

$ErrorActionPreference = 'Stop'
$RIG = $PSScriptRoot
Add-Type -TypeDefinition ([IO.File]::ReadAllText("$RIG/meter_pid.cs"))
$pid_ = (Get-Process azahar -ErrorAction Stop | Select-Object -First 1).Id

$quietRun = 0
$hits = 0
for ($i = 1; $i -le $Presses; $i++) {
  & "$RIG\azrig.ps1" key a | Out-Null
  Start-Sleep -Milliseconds $GapMs
  $v = [MeterPid]::Peak([uint32]$pid_)
  if ($v -lt $Quiet) { $quietRun++ }
  elseif ($quietRun -ge 2 -and $v -gt $Loud) {
    $hits++
    & "$RIG\capchild.ps1" "$Tag$hits" | Out-Null
    "press {0,4}: silence then {1:N3} -> probable shout, captured as $Tag$hits" -f $i, $v
    # let it play out and measure the whole burst
    $peak = $v; $t0 = Get-Date; $last = 0.0
    while (((Get-Date) - $t0).TotalSeconds -lt 6) {
      $s = [MeterPid]::Peak([uint32]$pid_)
      if ($s -gt $peak) { $peak = $s }
      if ($s -gt 0.02) { $last = ((Get-Date) - $t0).TotalSeconds }
      Start-Sleep -Milliseconds 40
    }
    "            burst ran {0:N2}s, peak {1:N3}" -f $last, $peak
    $quietRun = 0
    if ($hits -ge 3) { break }
  }
  else { $quietRun = 0 }
}
if ($hits -eq 0) { "no shout detected in $Presses presses" }
