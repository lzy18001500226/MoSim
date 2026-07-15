param(
    [string]$RunId = ("factory_l2_fast_autocover_review_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [int]$MaxWaypoints = 80,
    [int]$MaxInteractiveGoals = 80,
    [double]$SpeedMps = 1.5,
    [double]$AccelerationMps2 = 1.5,
    [double]$TargetReachedXYM = 0.45,
    [double]$TargetHoldS = 0.05,
    [switch]$WithRviz,
    [switch]$DryRun,
    [switch]$SkipPreflight
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$entry = Join-Path $PSScriptRoot "start_factory_diff_interactive_coverage_probe.ps1"

$argsList = @(
    "-File", $entry,
    "-RunId", $RunId,
    "-MaxWaypoints", $MaxWaypoints,
    "-MaxInteractiveGoals", $MaxInteractiveGoals,
    "-TargetZ", "4.0",
    "-TakeoffHeight", "4.0",
    "-TakeoffSpeedMps", "0.4",
    "-TakeoffZTolM", "0.35",
    "-PreGoalStableTimeoutS", "180",
    "-PreGoalTargetZ", "4.0",
    "-PreGoalMinZM", "3.4",
    "-PreGoalZTolM", "0.35",
    "-ClickReadyZTolM", "0.35",
    "-CommandMinZ", "3.4",
    "-CommandMaxZ", "4.5",
    "-CommandAuditMaxZ", "4.5",
    "-CommandEndZTolM", "0.35",
    "-PlannerMinZ", "3.4",
    "-PlannerMaxZ", "4.5",
    "-VirtualCeilHeight", "4.5",
    "-MapSizeZ", "6.0",
    "-ReviewMaxZ", "4.8",
    "-PlannerMaxVelMps", $SpeedMps,
    "-PlannerMaxAccMps2", $AccelerationMps2,
    "-InteractiveTargetReachedXYM", $TargetReachedXYM,
    "-InteractiveTargetReachedZM", "0.25",
    "-InteractiveTargetHoldS", $TargetHoldS,
    "-InteractiveTargetHoldMaxSpeedMps", ([Math]::Max($SpeedMps + 0.2, 0.5)),
    "-InteractiveTargetHoldMaxVzMps", "0.8",
    "-DropImmediateBacktracks",
    "-PointCloudReviewMaxAccumRollPitchDeg", "25",
    "-PointCloudReviewMaxAccumYawRateDegS", "60",
    "-PointCloudReviewMaxAccumSpeedXYMps", ([Math]::Max($SpeedMps + 0.5, 1.0)),
    "-PointCloudReviewMaxAccumSpeedZMps", "1.0",
    "-OccupancyReviewSourceTopic", "/uav1/livox_world",
    "-OccupancyReviewVoxelSizeM", "0.16",
    "-RuntimeTimeoutS", "1800",
    "-OuterWaitTimeoutS", "1900",
    "-CoverageExecuteS", "1200"
)

if ($WithRviz) {
    $argsList += "-WithRviz"
}
if ($DryRun) {
    $argsList += "-DryRun"
}
if ($SkipPreflight) {
    $argsList += "-SkipPreflight"
}

& powershell -ExecutionPolicy Bypass @argsList
