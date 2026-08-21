param(
    [string]$RunId = ("factory_l2_diff_lawnmower_coverage_probe_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [ValidateSet("lawnmower", "clearance_route")]
    [string]$RouteMode = "clearance_route",
    [int]$MaxWaypoints = 4,
    [int]$MaxCoverageTargets = 0,
    [double]$StripSpacingM = 12.0,
    [double]$SegmentLengthM = 5.0,
    [double]$MarginM = 8.0,
    [double]$ClearanceGridStepM = 5.0,
    [double]$ClearanceMarginM = 1.0,
    [double]$BoundaryMarginM = 2.0,
    [double]$FloorEdgeMarginM = 0.5,
    [double]$RouteStartX = [double]::NaN,
    [double]$RouteStartY = [double]::NaN,
    [ValidateSet("nearest_neighbor", "ordered_targets", "astar_connected")]
    [string]$ClearanceRoutePolicy = "nearest_neighbor",
    [double]$MinStartTargetDistanceM = 4.0,
    [switch]$IncludeCenterStart,
    [double]$TargetZ = 1.2,
    [double]$PlannerMaxVelMps = 0.6,
    [double]$PlannerMaxAccMps2 = 0.6,
    [double]$DiffMultipointNextDistanceM = 1.0,
    [int]$CoverageExecuteS = 120,
    [int]$LandTimeoutS = 25,
    [int]$RuntimeTimeoutS = 240,
    [int]$OuterWaitTimeoutS = 330,
    [double]$CoverageGridResolutionM = 2.0,
    [double]$CoverageSensorRadiusM = 8.0,
    [double]$MinSensorCoverageRatio = 0.80,
    [switch]$DryRun,
    [switch]$SkipPreflight,
    [switch]$WithRviz,
    [switch]$NoUnlimitedAccumulation
)

$ErrorActionPreference = "Stop"

$ProjectRootWin = "C:\Users\HP\Desktop\MoSim"
$ProjectRootWsl = "/mnt/c/Users/HP/Desktop/MoSim"
$ResultDirWin = Join-Path $ProjectRootWin ("Results\sunray_ros1\" + $RunId)
$ResultDirWsl = $ProjectRootWsl + "/Results/sunray_ros1/" + $RunId
$EnvelopeWin = Join-Path $ProjectRootWin "Config\gazebo\scene_profiles\factory_l2_exploration_envelope.json"
$FactoryWorldWsl = $ProjectRootWsl + "/Config/gazebo/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf"
$FactoryModelPathWsl = $ProjectRootWsl + "/Config/gazebo/models"
$WaypointStem = if ($RouteMode -eq "clearance_route") { "factory_l2_clearance_route_waypoints" } else { "factory_l2_lawnmower_waypoints" }
$WaypointYamlWin = Join-Path $ResultDirWin ($WaypointStem + ".yaml")
$WaypointJsonWin = Join-Path $ResultDirWin ($WaypointStem + ".json")
$WaypointYamlWsl = $ResultDirWsl + "/" + $WaypointStem + ".yaml"
$ManifestPath = Join-Path $ResultDirWin "FACTORY_L2_DIFF_LAWNMOWER_COVERAGE_PROBE.json"

function Get-Number($Value, [double]$Default) {
    if ($null -eq $Value) { return $Default }
    try { return [double]$Value } catch { return $Default }
}

New-Item -ItemType Directory -Force -Path $ResultDirWin | Out-Null
$routeStartArgs = @()
if (-not [double]::IsNaN($RouteStartX)) {
    $routeStartArgs += @("--start-x-m", $RouteStartX)
}
if (-not [double]::IsNaN($RouteStartY)) {
    $routeStartArgs += @("--start-y-m", $RouteStartY)
}

if ($RouteMode -eq "clearance_route") {
    $generator = Join-Path $ProjectRootWin "Scripts\sunray\generate_factory_l2_clearance_route_waypoints.py"
    $centerStartArg = if ($IncludeCenterStart) { "--include-center-start" } else { "--no-include-center-start" }
    python $generator `
        --envelope $EnvelopeWin `
        --output-yaml $WaypointYamlWin `
        --output-json $WaypointJsonWin `
        --section test1 `
        --z-m $TargetZ `
        --grid-step-m $ClearanceGridStepM `
        --boundary-margin-m $BoundaryMarginM `
        --floor-edge-margin-m $FloorEdgeMarginM `
        --clearance-margin-m $ClearanceMarginM `
        --route-policy $ClearanceRoutePolicy `
        $routeStartArgs `
        $centerStartArg `
        --min-start-target-distance-m $MinStartTargetDistanceM `
        --max-coverage-targets $MaxCoverageTargets `
        --max-waypoints $MaxWaypoints `
        --coverage-resolution-m $CoverageGridResolutionM `
        --sensor-radius-m $CoverageSensorRadiusM | Out-Null
} else {
    $generator = Join-Path $ProjectRootWin "Scripts\sunray\generate_factory_l2_lawnmower_waypoints.py"
    python $generator `
        --envelope $EnvelopeWin `
        --output-yaml $WaypointYamlWin `
        --output-json $WaypointJsonWin `
        --section test1 `
        --z-m $TargetZ `
        --margin-m $MarginM `
        --strip-spacing-m $StripSpacingM `
        --segment-length-m $SegmentLengthM `
        --max-waypoints $MaxWaypoints `
        --coverage-resolution-m $CoverageGridResolutionM `
        --sensor-radius-m $CoverageSensorRadiusM `
        --include-center-start | Out-Null
}

$waypointPacket = Get-Content -LiteralPath $WaypointJsonWin -Raw | ConvertFrom-Json
$first = $waypointPacket.first_waypoint
$boundary = $waypointPacket.boundary
$centerX = Get-Number $boundary.center_x_m 0.0
$centerY = Get-Number $boundary.center_y_m 0.0
$minX = Get-Number $boundary.min_x_m 0.0
$maxX = Get-Number $boundary.max_x_m 0.0
$minY = Get-Number $boundary.min_y_m 0.0
$maxY = Get-Number $boundary.max_y_m 0.0
$spawnX = if ([double]::IsNaN($RouteStartX)) { $centerX } else { $RouteStartX }
$spawnY = if ([double]::IsNaN($RouteStartY)) { $centerY } else { $RouteStartY }
$mapSizeX = [Math]::Max(1.0, $maxX - $minX)
$mapSizeY = [Math]::Max(1.0, $maxY - $minY)
$openRvizValue = if ($WithRviz) { "true" } else { "false" }
$keepAliveValue = if ($WithRviz) { "true" } else { "false" }
$pointCloudCap = if ($NoUnlimitedAccumulation) { 2000000 } else { 0 }
$occupancyCap = if ($NoUnlimitedAccumulation) { 1000000 } else { 0 }

if ($DryRun) {
    $manifest = [pscustomobject]@{
        schema = "mosim.factory_l2_diff_lawnmower_coverage_probe.v1"
        status = "dry_run_planned"
        generated_at = (Get-Date).ToString("o")
        run_id = $RunId
        result_dir = $ResultDirWin
        route_mode = $RouteMode
        waypoint_packet = $WaypointJsonWin
        waypoint_yaml = $WaypointYamlWin
        waypoint_count = $waypointPacket.waypoint_count
        planned_coverage_proxy = $waypointPacket.planned_coverage_proxy
    }
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8
    $manifest
    exit 0
}

$envParts = @(
    "RUN_ID=$RunId",
    "RESULT_DIR=$ResultDirWsl",
    "PLANNER_VARIANT=diff_planner",
    "PX4CTRL_CORE_PROFILE=l1_awff",
    "GUI=false",
    "OPEN_RVIZ=$openRvizValue",
    "KEEP_ALIVE=$keepAliveValue",
    "WORLD_FILE=$FactoryWorldWsl",
    "FACTORY_MODEL_PATH=$FactoryModelPathWsl",
    "SUNRAY_GAZEBO_LAUNCH_FILE=$ProjectRootWsl/Scripts/sunray/factory_l2_sunray_px4_gazebo.launch",
    "SUNRAY_STRIP_PX4_MODEL_PATH=true",
    "SUNRAY_MID360_PLUGIN_DOWNSAMPLE=4",
    "SUNRAY_LIVOX_PLUGIN_FILENAME=$ProjectRootWsl/Results/sunray_ros1/workspaces/sunray_livox_plugin_ws/devel/lib/liblivox_laser_simulation.so",
    "SUNRAY_MID360_CSV_FILE_NAME=mid360-real-centr.csv",
    "SUNRAY_MID360_GOAL5_CSV_STRIDE=4",
    "SUNRAY_UAV_INIT_X=$spawnX",
    "SUNRAY_UAV_INIT_Y=$spawnY",
    "SUNRAY_UAV_INIT_Z=0.2",
    "SUNRAY_UAV_INIT_YAW=0.0",
    "TARGET_X=$($first[0])",
    "TARGET_Y=$($first[1])",
    "TARGET_Z=$TargetZ",
    "PLANNER_MISSION_MODE=exploration_stream",
    "PLANNER_EXPLORATION_EXECUTE_S=$CoverageExecuteS",
    "DIFF_USE_MULTIPOINT=true",
    "DIFF_MULTIPOINT_YAML=$WaypointYamlWsl",
    "DIFF_WAYPOINT_AUDIT_SECTION=test1",
    "DIFF_MULTIPOINT_NEXT_DISTANCE=$DiffMultipointNextDistanceM",
    "DIFF_MULTIPOINT_FLIGHT_TYPE=1",
    "DIFF_ENABLE_CMD_SAFETY_ADAPTER=true",
    "DIFF_CMD_INVALID_Z_POLICY=clamp",
    "DIFF_CMD_MIN_Z=0.90",
    "DIFF_CMD_MAX_Z=1.60",
    "DIFF_CMD_SAFETY_MAX_POSITION_JUMP_M=0",
    "DIFF_CMD_SAFETY_MAX_POSITION_JUMP_SPEED_MPS=3.0",
    "DIFF_AUDIT_MAX_FINAL_TARGET_ERROR_M=1.0",
    "DIFF_WAYPOINT_AUDIT_MAX_STATE_XYZ_ERROR_M=1.2",
    "DIFF_WAYPOINT_AUDIT_MAX_STATE_Z_ERROR_M=0.25",
    "DIFF_WAYPOINT_AUDIT_MAX_CMD_XYZ_ERROR_M=0.8",
    "DIFF_WAYPOINT_AUDIT_MAX_CMD_Z_ERROR_M=0.20",
    "EGO_MAX_VEL=$PlannerMaxVelMps",
    "EGO_MAX_ACC=$PlannerMaxAccMps2",
    "EGO_PLANNING_HORIZON=7.0",
    "EGO_GRID_RESOLUTION=0.20",
    "EGO_OBSTACLES_INFLATION=0.25",
    "EGO_OBSTACLE_CLEARANCE=0.25",
    "EGO_OBSTACLE_CLEARANCE_SOFT=0.45",
    "EGO_VIRTUAL_CEIL_HEIGHT=1.60",
    "EGO_VISUALIZATION_TRUNCATE_HEIGHT=1.80",
    "EGO_GRID_INIT_X=$centerX",
    "EGO_GRID_INIT_Y=$centerY",
    "EGO_GRID_INIT_Z=0.0",
    "FUEL_MAP_SIZE_X=$mapSizeX",
    "FUEL_MAP_SIZE_Y=$mapSizeY",
    "FUEL_MAP_SIZE_Z=3.0",
    "FUEL_BOX_MIN_X=$minX",
    "FUEL_BOX_MAX_X=$maxX",
    "FUEL_BOX_MIN_Y=$minY",
    "FUEL_BOX_MAX_Y=$maxY",
    "FUEL_BOX_MIN_Z=0.90",
    "FUEL_BOX_MAX_Z=1.60",
    "FACTORY_INDOOR_BOUNDARY_MIN_X=$minX",
    "FACTORY_INDOOR_BOUNDARY_MAX_X=$maxX",
    "FACTORY_INDOOR_BOUNDARY_MIN_Y=$minY",
    "FACTORY_INDOOR_BOUNDARY_MAX_Y=$maxY",
    "GOAL4_TAKEOFF_HEIGHT=$TargetZ",
    "GOAL4_TAKEOFF_TIMEOUT_S=60",
    "GOAL4_LAND_TIMEOUT_S=$LandTimeoutS",
    "GOAL4_EGO_TAKEOVER_TIMEOUT_S=120",
    "MAVROS_READY_TIMEOUT_S=120",
    "GOAL4_RECORD_HZ=100",
    "GOAL4_RECORD_CMD_HZ=100",
    "GOAL4_MAX_PATH_POINTS=0",
    "GOAL4_PATH_PUBLISH_HZ=20",
    "GOAL4_REVIEW_HOLD_PATH_PUBLISH_HZ=10",
    "POINTCLOUD_REVIEW_VOXEL_SIZE_M=0.08",
    "POINTCLOUD_MIN_WORLD_Z_M=-0.2",
    "POINTCLOUD_REVIEW_MIN_WORLD_Z_M=0.2",
    "POINTCLOUD_REVIEW_MAX_WORLD_Z_M=4.0",
    "POINTCLOUD_REVIEW_MAX_POINTS_PER_CLOUD=50000",
    "POINTCLOUD_REVIEW_MAX_ACCUMULATED_POINTS=$pointCloudCap",
    "POINTCLOUD_REVIEW_PUBLISH_RATE_HZ=2.0",
    "OCCUPANCY_REVIEW_SOURCE_TOPIC=/drone_0_ego_planner_node/grid_map/occupancy",
    "OCCUPANCY_REVIEW_MIN_Z=0.20",
    "OCCUPANCY_REVIEW_MAX_Z=4.0",
    "OCCUPANCY_REVIEW_VOXEL_SIZE_M=0.12",
    "OCCUPANCY_REVIEW_MAX_POINTS_PER_CLOUD=50000",
    "OCCUPANCY_REVIEW_MAX_ACCUMULATED_POINTS=$occupancyCap",
    "OCCUPANCY_REVIEW_PUBLISH_RATE_HZ=2.0",
    "ENABLE_OCCUPANCY_REVIEW_ACCUMULATION=true",
    "TOTAL_TIMEOUT_S=$RuntimeTimeoutS",
    "DIFF_INTERACTIVE_REVIEW_HOLD_S=0"
)

$preflight = if ($SkipPreflight) {
    "echo skipped > '$ResultDirWsl/preflight_skipped.txt'"
} else {
    "bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh > '$ResultDirWsl/preflight.log' 2>&1"
}

$bashStatus = '$?'
$bashScriptWin = Join-Path $ResultDirWin "start_factory_diff_lawnmower_coverage_probe.sh"
$bashScriptWsl = $ResultDirWsl + "/start_factory_diff_lawnmower_coverage_probe.sh"
$command = @"
#!/usr/bin/env bash
set -e
cd $ProjectRootWsl
mkdir -p '$ResultDirWsl'
exec > >(tee -a '$ResultDirWsl/bootstrap.log') 2>&1
date --iso-8601=seconds > '$ResultDirWsl/background_start_marker.txt'
$preflight || { echo $bashStatus > '$ResultDirWsl/preflight_exit_code.txt'; exit 2; }
echo 0 > '$ResultDirWsl/preflight_exit_code.txt'
export GAZEBO_MODEL_PATH='$FactoryModelPathWsl':"`$`{GAZEBO_MODEL_PATH:-`}"
set +e
$($envParts -join " ") bash Scripts/sunray/run_px4ctrl_ego_single_gate.sh > '$ResultDirWsl/background_launcher.log' 2>&1
run_exit=$bashStatus
echo `$run_exit > '$ResultDirWsl/background_exit_code.txt'
exit `$run_exit
"@

[System.IO.File]::WriteAllText($bashScriptWin, $command, [System.Text.UTF8Encoding]::new($false))
$stdoutLog = Join-Path $ResultDirWin "windows_child_stdout.log"
$stderrLog = Join-Path $ResultDirWin "windows_child_stderr.log"
$proc = Start-Process -FilePath "wsl.exe" -ArgumentList @("-d", "Ubuntu-20.04", "--exec", "bash", $bashScriptWsl) -WindowStyle Hidden -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog -PassThru

$deadline = (Get-Date).AddSeconds($OuterWaitTimeoutS)
while (-not $proc.HasExited) {
    if ((Get-Date) -gt $deadline) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        "124" | Set-Content -LiteralPath (Join-Path $ResultDirWin "background_exit_code.txt") -Encoding ASCII
        break
    }
    Start-Sleep -Seconds 2
    $proc.Refresh()
}

$backendExit = 124
$exitPath = Join-Path $ResultDirWin "background_exit_code.txt"
if (Test-Path -LiteralPath $exitPath) {
    $backendExit = [int]((Get-Content -LiteralPath $exitPath -Raw).Trim())
}

$coverageDir = Join-Path $ResultDirWin "coverage_packet"
$coverageScript = Join-Path $ProjectRootWin "Scripts\sunray\build_factory_l2_indoor_coverage_packet.py"
python $coverageScript `
    --run $ResultDirWin `
    --output-dir $coverageDir `
    --grid-resolution-m $CoverageGridResolutionM `
    --sensor-radius-m $CoverageSensorRadiusM `
    --min-sensor-coverage-ratio $MinSensorCoverageRatio | Out-File -FilePath (Join-Path $ResultDirWin "coverage_packet_builder_stdout.txt") -Encoding UTF8

$coveragePacketPath = Join-Path $coverageDir "FACTORY_L2_INDOOR_COVERAGE_PACKET.json"
$coverageStatus = "missing"
if (Test-Path -LiteralPath $coveragePacketPath) {
    $coverageStatus = (Get-Content -LiteralPath $coveragePacketPath -Raw | ConvertFrom-Json).status
}
$metricsPath = Join-Path $ResultDirWin "EGO_SINGLE_METRICS.json"
$metricsStatus = "missing"
$metricsBlockerCount = $null
if (Test-Path -LiteralPath $metricsPath) {
    $metrics = Get-Content -LiteralPath $metricsPath -Raw | ConvertFrom-Json
    $metricsStatus = [string]$metrics.status
    $metricsBlockerCount = @($metrics.blockers).Count
}

$manifestStatus = if ($metricsStatus -eq "passed" -and $coverageStatus -eq "passed") {
    "passed"
} elseif ($metricsStatus -eq "passed") {
    "review_required_coverage_below_threshold_or_packet_blocked"
} else {
    "blocked_backend_failed_or_timeout"
}

$manifest = [pscustomobject]@{
    schema = "mosim.factory_l2_diff_lawnmower_coverage_probe.v1"
    status = $manifestStatus
    generated_at = (Get-Date).ToString("o")
    run_id = $RunId
    result_dir = $ResultDirWin
    backend_exit_code = $backendExit
    waypoint_packet = $WaypointJsonWin
    waypoint_yaml = $WaypointYamlWin
    route_mode = $RouteMode
    waypoint_count = $waypointPacket.waypoint_count
    metrics_status = $metricsStatus
    metrics_blocker_count = $metricsBlockerCount
    coverage_packet_status = $coverageStatus
    coverage_packet = $coveragePacketPath
    parameters = [pscustomobject]@{
        max_waypoints = $MaxWaypoints
        max_coverage_targets = $MaxCoverageTargets
        route_mode = $RouteMode
        strip_spacing_m = $StripSpacingM
        segment_length_m = $SegmentLengthM
        margin_m = $MarginM
        clearance_grid_step_m = $ClearanceGridStepM
        clearance_margin_m = $ClearanceMarginM
        boundary_margin_m = $BoundaryMarginM
        floor_edge_margin_m = $FloorEdgeMarginM
        route_start_x_m = if ([double]::IsNaN($RouteStartX)) { $null } else { $RouteStartX }
        route_start_y_m = if ([double]::IsNaN($RouteStartY)) { $null } else { $RouteStartY }
        clearance_route_policy = $ClearanceRoutePolicy
        min_start_target_distance_m = $MinStartTargetDistanceM
        include_center_start = [bool]$IncludeCenterStart
        target_z_m = $TargetZ
        planner_max_vel_mps = $PlannerMaxVelMps
        planner_max_acc_mps2 = $PlannerMaxAccMps2
        diff_multipoint_next_distance_m = $DiffMultipointNextDistanceM
        coverage_execute_s = $CoverageExecuteS
        land_timeout_s = $LandTimeoutS
        runtime_timeout_s = $RuntimeTimeoutS
        outer_wait_timeout_s = $OuterWaitTimeoutS
        with_rviz = [bool]$WithRviz
        unlimited_accumulation = -not [bool]$NoUnlimitedAccumulation
    }
    claim_boundary = @(
        "This is a same-flight scripted coverage route through Diff-Planner multipoint, not FUEL native autonomous exploration.",
        "It validates whether one UAV can keep moving through a coverage route in the clean Factory ROS1/Sunray/PX4/MAVROS/px4ctrl runtime.",
        "Full-map coverage is accepted only if FACTORY_L2_INDOOR_COVERAGE_PACKET.json passes the configured threshold."
    )
}
$manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8
$manifest
exit $(if ($manifestStatus -eq "passed") { 0 } else { 1 })
