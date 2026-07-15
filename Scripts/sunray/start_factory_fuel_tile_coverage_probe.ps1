param(
    [string]$RunId = ("factory_l2_fuel_tile_coverage_probe_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [ValidateSet("center3", "line5", "grid9")]
    [string]$TileSet = "center3",
    [int]$MaxTiles = 3,
    [string]$TileCsv = "",
    [double]$ExplorationExecuteS = 120.0,
    [double]$EgoTakeoverTimeoutS = 140.0,
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
    [double]$CmdMinZM = 0.90,
    [double]$CmdMaxZM = 1.60,
    [double]$TileSpacingXM = 45.0,
    [double]$TileSpacingYM = 20.0,
    [double]$CoverageGridResolutionM = 2.0,
    [double]$CoverageSensorRadiusM = 8.0,
    [double]$MinSensorCoverageRatio = 0.80,
    [int]$PollSeconds = 5,
    [int]$PerTileExtraTimeoutS = 180,
    [int]$RuntimeQuietTimeoutS = 30,
    [switch]$ContinueOnTileFailure,
    [switch]$DryRun,
    [switch]$SkipPreflight,
    [switch]$NoUnlimitedAccumulation
)

$ErrorActionPreference = "Stop"

$ProjectRootWin = "C:\Users\HP\Desktop\MoSim"
$EnvelopePath = Join-Path $ProjectRootWin "Config\gazebo\scene_profiles\factory_l2_exploration_envelope.json"
$SingleRunScript = Join-Path $ProjectRootWin "Scripts\sunray\start_factory_fuel_single_exploration_review.ps1"
$SummaryRoot = Join-Path $ProjectRootWin ("Results\sunray_ros1\" + $RunId)
$ManifestPath = Join-Path $SummaryRoot "FACTORY_L2_FUEL_TILE_COVERAGE_PROBE.json"

function Get-Number($Value, [double]$Default) {
    if ($null -eq $Value) {
        return $Default
    }
    try {
        return [double]$Value
    } catch {
        return $Default
    }
}

function Clamp-Value([double]$Value, [double]$Min, [double]$Max) {
    return [Math]::Min([Math]::Max($Value, $Min), $Max)
}

function New-Tile([string]$Id, [double]$X, [double]$Y, [double]$Yaw) {
    [pscustomobject]@{
        tile_id = $Id
        x = [Math]::Round($X, 6)
        y = [Math]::Round($Y, 6)
        yaw = [Math]::Round($Yaw, 6)
    }
}

function Get-DefaultTiles($Boundary, [string]$SetName) {
    $minX = Get-Number $Boundary.min_x_m 0.0
    $maxX = Get-Number $Boundary.max_x_m 0.0
    $minY = Get-Number $Boundary.min_y_m 0.0
    $maxY = Get-Number $Boundary.max_y_m 0.0
    $centerX = Get-Number $Boundary.center_x_m (($minX + $maxX) * 0.5)
    $centerY = Get-Number $Boundary.center_y_m (($minY + $maxY) * 0.5)
    $marginX = [Math]::Max($FuelWindowXYM * 0.5, 8.0)
    $marginY = [Math]::Max($FuelWindowXYM * 0.5, 8.0)

    $westX = Clamp-Value ($centerX - $TileSpacingXM) ($minX + $marginX) ($maxX - $marginX)
    $eastX = Clamp-Value ($centerX + $TileSpacingXM) ($minX + $marginX) ($maxX - $marginX)
    $southY = Clamp-Value ($centerY - $TileSpacingYM) ($minY + $marginY) ($maxY - $marginY)
    $northY = Clamp-Value ($centerY + $TileSpacingYM) ($minY + $marginY) ($maxY - $marginY)

    $tiles = New-Object System.Collections.Generic.List[object]
    $tiles.Add((New-Tile "center" $centerX $centerY 0.0)) | Out-Null
    $tiles.Add((New-Tile "west" $westX $centerY 0.0)) | Out-Null
    $tiles.Add((New-Tile "east" $eastX $centerY 3.141593)) | Out-Null

    if ($SetName -eq "line5" -or $SetName -eq "grid9") {
        $tiles.Add((New-Tile "south" $centerX $southY 1.570796)) | Out-Null
        $tiles.Add((New-Tile "north" $centerX $northY -1.570796)) | Out-Null
    }

    if ($SetName -eq "grid9") {
        $tiles.Add((New-Tile "west_south" $westX $southY 0.785398)) | Out-Null
        $tiles.Add((New-Tile "west_north" $westX $northY -0.785398)) | Out-Null
        $tiles.Add((New-Tile "east_south" $eastX $southY 2.356194)) | Out-Null
        $tiles.Add((New-Tile "east_north" $eastX $northY -2.356194)) | Out-Null
    }
    return $tiles.ToArray()
}

function Read-TilesFromCsv([string]$Path) {
    $resolved = Resolve-Path -LiteralPath $Path
    $rows = Import-Csv -LiteralPath $resolved
    $tiles = New-Object System.Collections.Generic.List[object]
    foreach ($row in $rows) {
        $id = if ($row.tile_id) { [string]$row.tile_id } else { "tile" + ($tiles.Count + 1) }
        $tiles.Add((New-Tile $id (Get-Number $row.x 0.0) (Get-Number $row.y 0.0) (Get-Number $row.yaw 0.0))) | Out-Null
    }
    return $tiles.ToArray()
}

function ConvertTo-WslPath([string]$Path) {
    $full = [System.IO.Path]::GetFullPath($Path)
    $drive = $full.Substring(0, 1).ToLowerInvariant()
    $rest = $full.Substring(2).Replace("\", "/")
    return "/mnt/$drive$rest"
}

function Invoke-RuntimeCleanup([string]$LogDir, [string]$Reason) {
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
    $logDirWsl = ConvertTo-WslPath $LogDir
    $safeReason = ($Reason -replace '[^A-Za-z0-9_.-]', '_')
    $script = @'
set +e
mkdir -p '__LOG_DIR__'
stamp=$(date +%Y%m%d_%H%M%S)
before="__LOG_DIR__/runtime_cleanup___REASON___${stamp}_before.txt"
after="__LOG_DIR__/runtime_cleanup___REASON___${stamp}_after.txt"
ps -eo pid,ppid,stat,etime,cmd | grep -E 'run_px4ctrl_ego_single_gate|fuel_native_traj_server|fuel_compat_traj_server|exploration_node|fuel_.*bridge|goal4_.*node|position_cmd_safety_adapter|accumulate_pointcloud_review|roslaunch|gzserver|gzclient|mavros_node|px4 |rosmaster|rosout' | grep -v grep > "$before" || true
patterns=(
  'run_px4ctrl_ego_single_gate.sh'
  'mosim_px4ctrl_ego_single_mission'
  'fuel_native_traj_server'
  'fuel_compat_traj_server'
  'exploration_node'
  'fuel_trigger_path_adapter.py'
  'fuel_bspline_bridge.py'
  'fuel_position_cmd_compat_bridge.py'
  'goal4_pointcloud_to_world_node.py'
  'goal4_position_cmd_safety_adapter.py'
  'accumulate_pointcloud_review.py'
  'mosim_mavros_pose_velocity_to_odom_bridge'
  'px4ctrl_node'
  'roslaunch .*px4ctrl_mosim.launch'
  'roslaunch .*fuel_single_px4ctrl_goal4.launch'
  'roslaunch .*sunray_sim_uav'
  'roslaunch .*sunray_uav_control.*external_fusion'
  'gzserver'
  'gzclient'
  'mavros_node'
  '/opt/mosim_work/sunray_px4.*/px4'
  'px4_ros1_runtime_overlay_.*px4'
  'rosmaster'
  'rosout'
)
for pat in "${patterns[@]}"; do pkill -f "$pat" >/dev/null 2>&1 || true; done
sleep 2
for pat in "${patterns[@]}"; do pkill -9 -f "$pat" >/dev/null 2>&1 || true; done
sleep 1
ps -eo pid,ppid,stat,etime,cmd | grep -E 'run_px4ctrl_ego_single_gate|fuel_native_traj_server|fuel_compat_traj_server|exploration_node|fuel_.*bridge|goal4_.*node|position_cmd_safety_adapter|accumulate_pointcloud_review|roslaunch|gzserver|gzclient|mavros_node|px4 |rosmaster|rosout' | grep -v grep > "$after" || true
'@
    $script = $script.Replace("__LOG_DIR__", $logDirWsl).Replace("__REASON__", $safeReason)
    & wsl -d Ubuntu-20.04 --exec bash -lc $script | Out-Null
}

function Wait-RuntimeQuiet([string]$LogDir, [string]$Reason, [int]$TimeoutS) {
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
    $deadline = (Get-Date).AddSeconds($TimeoutS)
    $lastOutput = @()
    do {
        $output = & wsl -d Ubuntu-20.04 --exec bash -lc "ps -eo pid,ppid,stat,etime,cmd | grep -E 'run_px4ctrl_ego_single_gate|fuel_native_traj_server|fuel_compat_traj_server|exploration_node|fuel_.*bridge|goal4_.*node|position_cmd_safety_adapter|accumulate_pointcloud_review|roslaunch|gzserver|gzclient|mavros_node|px4 |rosmaster|rosout' | grep -v grep || true"
        $lastOutput = @($output | Where-Object { $_ -and $_.Trim() -ne "" })
        if ($lastOutput.Count -eq 0) {
            return $true
        }
        Start-Sleep -Seconds 2
    } while ((Get-Date) -lt $deadline)

    $safeReason = ($Reason -replace '[^A-Za-z0-9_.-]', '_')
    $lastOutput | Out-File -FilePath (Join-Path $LogDir ("runtime_quiet_timeout_" + $safeReason + ".txt")) -Encoding utf8
    return $false
}

function Get-MetricsSummary([string]$RunDir) {
    $metricsPath = Join-Path $RunDir "EGO_SINGLE_METRICS.json"
    if (-not (Test-Path -LiteralPath $metricsPath)) {
        return [pscustomobject]@{
            metrics_present = $false
            status = $null
            blockers = @("missing_EGO_SINGLE_METRICS")
        }
    }
    $metrics = Get-Content -LiteralPath $metricsPath -Raw | ConvertFrom-Json
    return [pscustomobject]@{
        metrics_present = $true
        status = $metrics.status
        blockers = @($metrics.blockers)
    }
}

if (-not (Test-Path -LiteralPath $EnvelopePath)) {
    throw "missing envelope: $EnvelopePath"
}
if (-not (Test-Path -LiteralPath $SingleRunScript)) {
    throw "missing single-run script: $SingleRunScript"
}

New-Item -ItemType Directory -Force -Path $SummaryRoot | Out-Null

$envelope = Get-Content -LiteralPath $EnvelopePath -Raw | ConvertFrom-Json
$tiles = if ($TileCsv -ne "") {
    Read-TilesFromCsv $TileCsv
} else {
    Get-DefaultTiles $envelope.exploration_boundary $TileSet
}
if ($MaxTiles -gt 0) {
    $tiles = @($tiles | Select-Object -First $MaxTiles)
}

$results = New-Object System.Collections.Generic.List[object]
$plannedCommands = New-Object System.Collections.Generic.List[object]
$sequenceStopped = $false
$stopReason = $null

foreach ($tile in $tiles) {
    $tileRunId = "{0}_{1}" -f $RunId, $tile.tile_id
    $tileRunDir = Join-Path $ProjectRootWin ("Results\sunray_ros1\" + $tileRunId)
    $singleArgs = @{
        RunId = $tileRunId
        ExplorationExecuteS = $ExplorationExecuteS
        EgoTakeoverTimeoutS = $EgoTakeoverTimeoutS
        MissionTotalTimeoutS = $MissionTotalTimeoutS
        ReviewHoldS = 0
        StartX = [double]$tile.x
        StartY = [double]$tile.y
        StartYaw = [double]$tile.yaw
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
        CmdMinZM = $CmdMinZM
        CmdMaxZM = $CmdMaxZM
        NoRviz = $true
        NoKeepAlive = $true
    }
    if ($SkipPreflight) {
        $singleArgs.SkipPreflight = $true
    }
    if (-not $NoUnlimitedAccumulation) {
        $singleArgs.UnlimitedAccumulation = $true
    }

    $plannedCommands.Add([pscustomobject]@{
        tile_id = $tile.tile_id
        run_id = $tileRunId
        run_dir = $tileRunDir
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$SingleRunScript`" " + (($singleArgs.GetEnumerator() | Sort-Object Name | ForEach-Object {
            if ($_.Value -is [bool]) {
                if ($_.Value) { "-$($_.Name)" } else { "" }
            } else {
                "-$($_.Name) $($_.Value)"
            }
        } | Where-Object { $_ -ne "" }) -join " ")
    }) | Out-Null

    if ($DryRun) {
        $results.Add([pscustomobject]@{
            tile_id = $tile.tile_id
            run_id = $tileRunId
            run_dir = $tileRunDir
            status = "dry_run_planned"
            exit_code = $null
            metrics = $null
        }) | Out-Null
        continue
    }

    Invoke-RuntimeCleanup $SummaryRoot ("before_" + $tile.tile_id)
    $quietBefore = Wait-RuntimeQuiet $SummaryRoot ("before_" + $tile.tile_id) $RuntimeQuietTimeoutS
    if (-not $quietBefore) {
        $results.Add([pscustomobject]@{
            tile_id = $tile.tile_id
            run_id = $tileRunId
            run_dir = $tileRunDir
            status = "blocked_runtime_not_quiet_before_tile"
            exit_code = $null
            metrics = Get-MetricsSummary $tileRunDir
        }) | Out-Null
        $sequenceStopped = $true
        $stopReason = "runtime_not_quiet_before_tile"
        break
    }

    & $SingleRunScript @singleArgs | Out-File -FilePath (Join-Path $SummaryRoot ("launch_" + $tile.tile_id + ".txt")) -Encoding utf8

    $exitFile = Join-Path $tileRunDir "background_exit_code.txt"
    $deadline = (Get-Date).AddSeconds([Math]::Ceiling($ExplorationExecuteS + $EgoTakeoverTimeoutS + $PerTileExtraTimeoutS))
    while ((Get-Date) -lt $deadline -and -not (Test-Path -LiteralPath $exitFile)) {
        Start-Sleep -Seconds $PollSeconds
    }

    if (-not (Test-Path -LiteralPath $exitFile)) {
        Invoke-RuntimeCleanup $SummaryRoot ("timeout_" + $tile.tile_id)
        $quietAfterTimeout = Wait-RuntimeQuiet $SummaryRoot ("timeout_" + $tile.tile_id) $RuntimeQuietTimeoutS
        $results.Add([pscustomobject]@{
            tile_id = $tile.tile_id
            run_id = $tileRunId
            run_dir = $tileRunDir
            status = "blocked_timeout_killed_waiting_for_background_exit_code"
            exit_code = $null
            metrics = Get-MetricsSummary $tileRunDir
            runtime_quiet_after_cleanup = $quietAfterTimeout
        }) | Out-Null
        $sequenceStopped = $true
        $stopReason = "tile_timeout_waiting_for_background_exit_code"
        if (-not $ContinueOnTileFailure) {
            break
        }
        continue
    }

    $exitCodeText = (Get-Content -LiteralPath $exitFile -Raw).Trim()
    $exitCode = Get-Number $exitCodeText -9999
    $metricsSummary = Get-MetricsSummary $tileRunDir
    $tileStatus = if ($exitCode -eq 0 -and $metricsSummary.status -eq "passed" -and @($metricsSummary.blockers).Count -eq 0) { "passed" } else { "blocked_or_failed" }
    Invoke-RuntimeCleanup $SummaryRoot ("after_" + $tile.tile_id)
    $quietAfter = Wait-RuntimeQuiet $SummaryRoot ("after_" + $tile.tile_id) $RuntimeQuietTimeoutS
    $results.Add([pscustomobject]@{
        tile_id = $tile.tile_id
        run_id = $tileRunId
        run_dir = $tileRunDir
        status = $tileStatus
        exit_code = $exitCode
        metrics = $metricsSummary
        runtime_quiet_after_cleanup = $quietAfter
    }) | Out-Null
    if ($tileStatus -ne "passed") {
        $sequenceStopped = $true
        $stopReason = "tile_blocked_or_failed"
        if (-not $ContinueOnTileFailure) {
            break
        }
    }
}

$coverageDir = Join-Path $SummaryRoot "coverage_packet"
$coverageExitCode = $null
$coveragePacket = $null
if (-not $DryRun) {
    $runDirs = @($results | Where-Object { Test-Path -LiteralPath $_.run_dir } | ForEach-Object { $_.run_dir })
    if ($runDirs.Count -gt 0) {
        $coverageArgs = @(
            "Scripts\sunray\build_factory_l2_indoor_coverage_packet.py",
            "--output-dir", $coverageDir,
            "--grid-resolution-m", ([string]$CoverageGridResolutionM),
            "--sensor-radius-m", ([string]$CoverageSensorRadiusM),
            "--min-sensor-coverage-ratio", ([string]$MinSensorCoverageRatio)
        )
        foreach ($dir in $runDirs) {
            $coverageArgs += "--run"
            $coverageArgs += $dir
        }
        Push-Location $ProjectRootWin
        try {
            & python @coverageArgs | Out-File -FilePath (Join-Path $SummaryRoot "coverage_builder_stdout.log") -Encoding utf8
            $coverageExitCode = $LASTEXITCODE
        } finally {
            Pop-Location
        }
        $packetPath = Join-Path $coverageDir "FACTORY_L2_INDOOR_COVERAGE_PACKET.json"
        if (Test-Path -LiteralPath $packetPath) {
            $coveragePacket = $packetPath
        }
    }
}

$manifest = [pscustomobject]@{
    schema = "mosim.factory_l2_fuel_tile_coverage_probe.v1"
    status = if ($DryRun) { "dry_run_planned" } elseif ($coverageExitCode -eq 0) { "passed" } else { "review_required_or_blocked" }
    generated_at = (Get-Date).ToString("o")
    run_id = $RunId
    envelope = $EnvelopePath
    parameters = [pscustomobject]@{
        tile_set = $TileSet
        max_tiles = $MaxTiles
        exploration_execute_s = $ExplorationExecuteS
        ego_takeover_timeout_s = $EgoTakeoverTimeoutS
        mission_total_timeout_s = $MissionTotalTimeoutS
        target_z = $TargetZ
        takeoff_timeout_s = $TakeoffTimeoutS
        fuel_window_xy_m = $FuelWindowXYM
        fuel_window_z_m = $FuelWindowZM
        fuel_box_min_z_m = $FuelBoxMinZM
        fuel_box_max_z_m = $FuelBoxMaxZM
        fuel_virtual_ceil_height_m = $FuelVirtualCeilHeightM
        fuel_planner_max_vel_mps = $FuelPlannerMaxVelMps
        fuel_planner_max_acc_mps2 = $FuelPlannerMaxAccMps2
        fuel_cmd_smooth_max_speed_mps = $FuelCmdSmoothMaxSpeedMps
        fuel_cmd_smooth_max_step_m = $FuelCmdSmoothMaxStepM
        command_min_z_m = $CmdMinZM
        command_max_z_m = $CmdMaxZM
        coverage_grid_resolution_m = $CoverageGridResolutionM
        coverage_sensor_radius_m = $CoverageSensorRadiusM
        min_sensor_coverage_ratio = $MinSensorCoverageRatio
        per_tile_extra_timeout_s = $PerTileExtraTimeoutS
        runtime_quiet_timeout_s = $RuntimeQuietTimeoutS
        continue_on_tile_failure = [bool]$ContinueOnTileFailure
        dry_run = [bool]$DryRun
    }
    sequence = [pscustomobject]@{
        stopped = [bool]$sequenceStopped
        stop_reason = $stopReason
    }
    tiles = $tiles
    planned_commands = $plannedCommands
    results = $results
    coverage = [pscustomobject]@{
        output_dir = $coverageDir
        packet = $coveragePacket
        exit_code = $coverageExitCode
    }
    claim_boundary = @(
        "This wrapper runs bounded FUEL local windows serially and then builds one merged coverage packet.",
        "Only backend-passed runs count toward merged coverage in build_factory_l2_indoor_coverage_packet.py.",
        "A dry-run manifest proves planned tile centers and commands only; it is not runtime evidence.",
        "This is still a FUEL coverage-strategy probe, not proof that FUEL is the final full-map autonomous exploration algorithm."
    )
}

$manifest | ConvertTo-Json -Depth 8 | Out-File -FilePath $ManifestPath -Encoding utf8
[pscustomobject]@{
    Status = $manifest.status
    RunId = $RunId
    Manifest = $ManifestPath
    CoveragePacket = $coveragePacket
}
