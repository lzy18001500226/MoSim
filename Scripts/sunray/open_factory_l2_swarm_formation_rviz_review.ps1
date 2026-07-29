[CmdletBinding()]
param(
    [string]$ReviewRunId = ("factory_l2_swarm_formation_rviz_manual_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [int]$StartupTimeoutS = 300,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$Root = "C:\Users\HP\Desktop\MoSim"
$ReviewScript = Join-Path $Root "Scripts\sunray\start_factory_l2_swarm_formation_review.ps1"

if ($ReviewRunId -notmatch '^[A-Za-z0-9_.-]+$') {
    throw "ReviewRunId may contain only letters, digits, dot, underscore, and hyphen."
}
if ($StartupTimeoutS -lt 30) {
    throw "StartupTimeoutS must be at least 30 seconds."
}
if (-not (Test-Path -LiteralPath $ReviewScript)) {
    throw "Missing Swarm-Formation RViz review launcher: $ReviewScript"
}

Write-Host "[MoSim] Attaching RViz to the active three-UAV backend. UE and QGC are intentionally not started."
& $ReviewScript -RunId $ReviewRunId -AttachOnly -NoUnreal -StartupTimeoutS $StartupTimeoutS -DryRun:$DryRun
exit $LASTEXITCODE
