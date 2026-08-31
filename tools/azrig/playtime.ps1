# Measure how long a DLC gallery line ACTUALLY plays.
#
# The question "is this clip cut short?" cannot be answered from the file --
# a clip can decode to a full 5s take and still stop at 3s in-game if the
# player only reads Capcom's original allocation. So measure the speaker.
#
#   playtime.ps1 -x 690 -y 592              one line
#   playtime.ps1 -x 690 -y 592 -Window 8    longer take
#
# Reports first/last audible sample and the span between them. Compare that
# span against the decoded duration of the .mca to decide whether the game
# truncated it.
#
# The DLC pages play looping background music, so an absolute silence floor
# only works when the room happens to be quiet. The floor is therefore derived
# from the audio present BEFORE the touch, and a run must clear that baseline
# to count. Pass -Floor to raise the minimum by hand.
#
# Do not call this in the same PowerShell process as `azrig.ps1 meter`: both
# Add-Type the same audio CLSID under different names and the second cast fails.
# `azrig.ps1 meter` is also system-wide -- use `azrig.ps1 meterpid` for baselines.
param([int]$x, [int]$y, [double]$Window = 6.0, [double]$Delay = 1.2,
      [double]$Floor = 0.004, [int]$StepMs = 30)

$ErrorActionPreference = 'Stop'
$RIG = $PSScriptRoot
# PER-PROCESS meter, not the default endpoint: anything else the machine is
# playing (melonDS for the GK2 project, a browser tab) lands in a system-wide
# peak reading and silently becomes "room tone" that masks a short clip.
Add-Type -TypeDefinition ([IO.File]::ReadAllText("$RIG/meter_pid.cs"))
$AZPID = (Get-Process azahar -ErrorAction Stop | Select-Object -First 1).Id

# fire the touch from a side job so sampling is never blocked by it
$job = Start-Job -ScriptBlock {
  param($rig, $px, $py, $wait)
  Start-Sleep -Milliseconds ([int]($wait * 1000))
  & "$rig\touch.ps1" -x $px -y $py
} -ArgumentList $RIG, $x, $y, $Delay

$t0 = Get-Date
$samples = New-Object System.Collections.Generic.List[object]
while (((Get-Date) - $t0).TotalSeconds -lt $Window) {
  $el = ((Get-Date) - $t0).TotalSeconds
  $samples.Add([pscustomobject]@{ t = $el; v = [MeterPid]::Peak([uint32]$AZPID) })
  Start-Sleep -Milliseconds $StepMs
}
Receive-Job $job -Wait -AutoRemoveJob | Out-Null

# everything before the touch is room tone: music, ambience, a previous clip
$pre = $samples | Where-Object { $_.t -lt ($Delay - 0.1) }
$base = 0.0
if ($pre) { $base = ($pre | Measure-Object -Property v -Maximum).Maximum }
$gate = [math]::Max($Floor, $base * 1.25)

$loud = $samples | Where-Object { $_.t -ge $Delay -and $_.v -gt $gate }
if (-not $loud) {
  "SILENT  -- nothing above {0:N4} after the touch ({1} samples, baseline {2:N4})" -f $gate, $samples.Count, $base
  return
}
$first = $loud[0].t
$last  = $loud[-1].t
$peak  = ($samples | Measure-Object -Property v -Maximum).Maximum

# a gap longer than ~250ms means the tail was cut and something else followed
$gaps = @()
for ($i = 1; $i -lt $loud.Count; $i++) {
  $d = $loud[$i].t - $loud[$i-1].t
  if ($d -gt 0.25) { $gaps += "{0:N2}s..{1:N2}s" -f $loud[$i-1].t, $loud[$i].t }
}

"played {0:N2}s   (audible {1:N2}s -> {2:N2}s after touch at {3:N2}s)" -f ($last - $first), $first, $last, $Delay
"peak   {0:N4}   samples {1}   gate {2:N4} (room tone {3:N4})" -f $peak, $samples.Count, $gate, $base
if ($gaps) { "gaps   " + ($gaps -join ", ") }
