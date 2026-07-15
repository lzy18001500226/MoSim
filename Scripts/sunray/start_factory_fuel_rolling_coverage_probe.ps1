param(
    [string]$RunId = ("factory_l2_fuel_rolling_coverage_probe_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [int]$MaxWindows = 2,
    [ValidateSet("forward_strip", "lawnmower")]
    [string]$CoveragePattern = "forward_strip",
    [double]$StepXM = 10.0,
    [double]$StepYM = 10.0,
    [double]$ExplorationExecuteS = 90.0,
    [double]$EgoTakeoverTimeoutS = 120.0,
    [int]$MissionTotalTimeoutS = 0,
    [double]$TargetZ = 1.2,
    [double]$TakeoffTimeoutS = 50.0,
    [double]$FuelWindowXYM = 16.0,
    [double]$FuelWindowZM = 3.0,
    [double]$FuelBoxMinZM = 0.90,
    [double]$FuelBoxMaxZM = 1.60,
    [double]$FuelVirtualCeilHeightM = 1.60,
    [double]$FuelPlannerMaxVelMps = 0.8,
    [double]$FuelPlannerMaxAccMps2 = 0.8,
    [double]$FuelCmdSmoothMaxSpeedMps = 0.8,
    [double]$FuelCmdSmoothMaxStepM = 0.0,
    [double]$CoverageGridResolutionM = 2.0,
    [double]$CoverageSensorRadiusM = 8.0,
    [double]$MinSensorCoverageRatio = 0.80,
    [string]$TileCsv = "",
    [switch]$DryRun,
    [switch]$SkipPreflight,
    [switch]$NoUnlimitedAccumulation
)

$ErrorActionPreference = "Stop"

$ProjectRootWin = "C:\Users\HP\Desktop\MoSim"
$EnvelopePath = Join-Path $ProjectRootWin "Config\gazebo\scene_profiles\factory_l2_exploration_envelope.json"
$TileProbeScript = Join-Path $ProjectRootWin "Scripts\sunray\start_factory_fuel_tile_coverage_probe.ps1"
$SummaryRoot = Join-Path $ProjectRootWin ("Results\sunray_ros1\" + $RunId)
$TileCsvPath = Join-Path $SummaryRoot "rolling_windows.csv"
$ManifestPath = Join-Path $SummaryRoot "FACTORY_L2_FUEL_ROLLING_COVERAGE_PROBE.json"

function Get-Number($Value, [double]$Default) {
    if ($null -eq $Value) { return $Default }
    try { return [double]$Value } catch { return $Default }
}

function Clamp-Value([double]$Value, [double]$Min, [double]$Max) {
    return [Math]::Min([Math]::Max($Value, $Min), $Max)
}

function Add-Window($List, [string]$Id, [double]$X, [double]$Y, [double]$Yaw) {
    $exists = $false
    foreach ($item in $List) {
        if ([Math]::Abs($item.x - $X) -lt 0.001 -and [Math]::Abs($item.y - $Y) -lt 0.001) {
            $exists = $true
            break
        }
    }
    if (-not $exists) {
        $List.Add([pscustomobject]@{
            tile_id = $Id
            x = [Math]::Round($X, 6)
            y = [Math]::Round($Y, 6)
            yaw = [Math]::Round($Yaw, 6)
        }) | Out-Null
    }
}

function Read-WindowsFromCsv([string]$Path) {
    $resolved = Resolve-Path -LiteralPath $Path
    $rows = Import-Csv -LiteralPath $resolved
    $items = New-Object System.Collections.Generic.List[object]
    foreach ($row in $rows) {
        $id = if ($row.tile_id) { [string]$row.tile_id } else { "win{0:D2}" -f ($items.Count + 1) }
        Add-Window $items $id (Get-Number $row.x 0.0) (Get-Number $row.y 0.0) (Get-Number $row.yaw 0.0)
    }
    return $items
}

if (-not (Test-Path -LiteralPath $EnvelopePath)) {
    throw "missing envelope: $EnvelopePath"
}
if (-not (Test-Path -LiteralPath $TileProbeScript)) {
    throw "missing tile probe script: $TileProbeScript"
}

New-Item -ItemType Directory -Force -Path $SummaryRoot | Out-Null

$envelope = Get-Content -LiteralPath $EnvelopePath -Raw | ConvertFrom-Json
$boundary = $envelope.exploration_boundary
$minX = Get-Number $boundary.min_x_m 0.0
$maxX = Get-Number $boundary.max_x_m 0.0
$minY = Get-Number $boundary.min_y_m 0.0
$maxY = Get-Number $boundary.max_y_m 0.0
$centerX = Get-Number $boundary.center_x_m (($minX + $maxX) * 0.5)
$centerY = Get-Number $boundary.center_y_m (($minY + $maxY) * 0.5)
$half = [Math]::Max($FuelWindowXYM * 0.5, 1.0)
$safeMinX = $minX + $half
$safeMaxX = $maxX - $half
$safeMinY = $minY + $half
$safeMaxY = $maxY - $half

if ($safeMinX -gt $safeMaxX -or $safeMinY -gt $safeMaxY) {
    throw "fuel window too large for boundary: window=$FuelWindowXYM boundary=[$minX,$maxX]x[$minY,$maxY]"
}

$windows = if ($TileCsv -ne "") {
    Read-WindowsFromCsv $TileCsv
} else {
    $generated = New-Object System.Collections.Generic.List[object]
    $rowOffsets = @(0.0, $StepYM, -$StepYM, (2.0 * $StepYM), (-2.0 * $StepYM), (3.0 * $StepYM), (-3.0 * $StepYM))

    if ($CoveragePattern -eq "lawnmower") {
        $rowIndex = 0
        foreach ($rowOffset in $rowOffsets) {
            if ($generated.Count -ge $MaxWindows) { break }
            $y = Clamp-Value ($centerY + $rowOffset) $safeMinY $safeMaxY
            $direction = if (($rowIndex % 2) -eq 0) { 1.0 } else { -1.0 }
            $x = if ($direction -gt 0) { $safeMinX } else { $safeMaxX }
            while ($generated.Count -lt $MaxWindows) {
                $yaw = if ($direction -gt 0) { 0.0 } else { 3.141593 }
                Add-Window $generated ("win{0:D2}" -f ($generated.Count + 1)) $x $y $yaw
                $nextX = $x + ($direction * $StepXM)
                if (($direction -gt 0 -and $nextX -gt $safeMaxX) -or ($direction -lt 0 -and $nextX -lt $safeMinX)) {
                    break
                }
                $x = $nextX
            }
            $rowIndex += 1
        }
    } else {
        $rowIndex = 0
        foreach ($rowOffset in $rowOffsets) {
            if ($generated.Count -ge $MaxWindows) { break }
            $y = Clamp-Value ($centerY + $rowOffset) $safeMinY $safeMaxY
            $direction = if (($rowIndex % 2) -eq 0) { 1.0 } else { -1.0 }
            $x = $centerX
            while ($generated.Count -lt $MaxWindows) {
                $clampedX = Clamp-Value $x $safeMinX $safeMaxX
                $yaw = if ($direction -gt 0) { 0.0 } else { 3.141593 }
                Add-Window $generated ("win{0:D2}" -f ($generated.Count + 1)) $clampedX $y $yaw
                $nextX = $x + ($direction * $StepXM)
                if (($direction -gt 0 -and $nextX -gt $safeMaxX) -or ($direction -lt 0 -and $nextX -lt $safeMinX)) {
                    break
                }
                $x = $nextX
            }
            $rowIndex += 1
        }
    }
    $generated
}

if ($MaxWindows -gt 0 -and $windows.Count -gt $MaxWindows) {
    $trimmed = New-Object System.Collections.Generic.List[object]
    foreach ($window in @($windows | Select-Object -First $MaxWindows)) {
        $trimmed.Add($window) | Out-Null
    }
    $windows = $trimmed
}

if ($windows.Count -eq 0) {
    throw "no rolling windows generated"
}

$windows |
    Select-Object tile_id,x,y,yaw |
    Export-Csv -LiteralPath $TileCsvPath -NoTypeInformation -Encoding UTF8

$tileArgs = @{
    RunId = $RunId
    TileCsv = $TileCsvPath
    MaxTiles = $MaxWindows
    ExplorationExecuteS = $ExplorationExecuteS
    EgoTakeoverTimeoutS = $EgoTakeoverTimeoutS
    MissionTotalTimeoutS = $MissionTotalTimeoutS
    TargetZ = $TargetZ
    TakeoffTimeoutS = $TakeoffTimeoutS
    FuelWindowXYM = $FuelWindowXYM
    FuelWindowZM = $FuelWindowZM
    FuelBoxMinZM = $FuelBoxMinZM
    FuelBoxMaxZM = $FuelBoxMaxZM
    FuelVirtualCeilHeightM = $FuelVirtualCeilHeightM
    FuelPlannerMaxVelMps = $FuelPlannerMaxVelMps
    FuelPlannerMaxAccMps2 = $FuelPlannerMaxAccMps2
    FuelCmdSmoothMaxSpeedMps = $FuelCmdSmoothMaxSpeedMps
    FuelCmdSmoothMaxStepM = $FuelCmdSmoothMaxStepM
    CoverageGridResolutionM = $CoverageGridResolutionM
    CoverageSensorRadiusM = $CoverageSensorRadiusM
    MinSensorCoverageRatio = $MinSensorCoverageRatio
}
if ($DryRun) { $tileArgs.DryRun = $true }
if ($SkipPreflight) { $tileArgs.SkipPreflight = $true }
if ($NoUnlimitedAccumulation) { $tileArgs.NoUnlimitedAccumulation = $true }

$tileResult = & $TileProbeScript @tileArgs

$manifest = [pscustomobject]@{
    schema = "mosim.factory_l2_fuel_rolling_coverage_probe.v1"
    status = if ($DryRun) { "dry_run_planned" } else { "executed_review_tile_probe_result" }
    generated_at = (Get-Date).ToString("o")
    run_id = $RunId
    envelope = $EnvelopePath
    tile_csv = $TileCsvPath
    windows = $windows
    parameters = [pscustomobject]@{
        max_windows = $MaxWindows
        coverage_pattern = $CoveragePattern
        input_tile_csv = $TileCsv
        step_x_m = $StepXM
        step_y_m = $StepYM
        exploration_execute_s = $ExplorationExecuteS
        ego_takeover_timeout_s = $EgoTakeoverTimeoutS
        mission_total_timeout_s = $MissionTotalTimeoutS
        target_z_m = $TargetZ
        takeoff_timeout_s = $TakeoffTimeoutS
        fuel_window_xy_m = $FuelWindowXYM
        fuel_window_z_m = $FuelWindowZM
        fuel_planner_max_vel_mps = $FuelPlannerMaxVelMps
        fuel_cmd_smooth_max_speed_mps = $FuelCmdSmoothMaxSpeedMps
        dry_run = [bool]$DryRun
    }
    tile_probe_result = $tileResult
    claim_boundary = @(
        "This is a bounded rolling-window coverage strategy probe for FUEL.",
        "Current execution reuses the existing single-run FUEL launch per window, so it validates window selection and merged coverage, not same-flight runtime box migration.",
        "Do not treat this as direct constant-velocity forward flight; each window still routes through FUEL/traj_server/px4ctrl/PX4/Gazebo.",
        "Promotion to same-flight rolling supervisor requires a separate gate because FUEL's sdf_map box is launch-time configuration."
    )
}

$manifest | ConvertTo-Json -Depth 8 | Out-File -FilePath $ManifestPath -Encoding utf8
[pscustomobject]@{
    Status = $manifest.status
    RunId = $RunId
    Manifest = $ManifestPath
    TileCsv = $TileCsvPath
    TileProbeResult = $tileResult
}
