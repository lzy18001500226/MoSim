param(
    [string]$RunId = ("factory_l2_diff_interactive_coverage_probe_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [int]$MaxWaypoints = 0,
    [int]$MaxCoverageTargets = 0,
    [int]$MaxInteractiveGoals = 0,
    [string]$WaypointJsonOverride = "",
    [string]$WaypointYamlOverride = "",
    [switch]$UseMultipointRoute,
    [double]$DiffMultipointNextDistanceM = 1.0,
    [double]$ClearanceGridStepM = 6.0,
    [double]$TransitGridStepM = 1.5,
    [double]$ClearanceMarginM = 0.6,
    [double]$BoundaryMarginM = 2.0,
    [double]$FloorEdgeMarginM = 0.5,
    [double]$RouteStartX = -72.404960,
    [double]$RouteStartY = 1.637090,
    [double]$UavInitX = [double]::NaN,
    [double]$UavInitY = [double]::NaN,
    [string]$ControllerCoreProfile = "l1_awff",
    [ValidateSet("nearest_neighbor", "nearest_neighbor_transit", "coverage_gain_transit", "ordered_targets", "astar_connected")]
    [string]$ClearanceRoutePolicy = "coverage_gain_transit",
    [ValidateSet("topdown", "bottomup", "start_outward")]
    [string]$CoverageOrder = "topdown",
    [double]$MinStartTargetDistanceM = 4.0,
    [double]$MaxSegmentM = 6.0,
    [switch]$DropImmediateBacktracks,
    [double]$TargetZ = 3.0,
    [double]$FlightObstacleMinZM = 2.5,
    [double]$FlightObstacleMaxZM = 3.5,
    [double]$ObstacleZInflationM = 0.0,
    [double]$OverheadObstacleMaxMinZM = 5.5,
    [double]$CommandMinZ = 2.40,
    [double]$CommandMaxZ = 3.20,
    [double]$CommandAuditMaxZ = -1.0,
    [double]$CommandEndZTolM = 0.35,
    [double]$CommandFixedZ = -1.0,
    [switch]$RawCmdZWarningsOnly,
    [switch]$ZeroAllCommandDynamics,
    [double]$PlannerMinZ = 2.40,
    [double]$PlannerMaxZ = 3.20,
    [double]$VirtualCeilHeight = 3.20,
    [double]$MapSizeZ = 5.0,
    [double]$ReviewMaxZ = 4.0,
    [double]$PlannerMaxVelMps = 0.30,
    [double]$PlannerMaxAccMps2 = 0.30,
    [double]$PlannerLocalUpdateRangeXYM = 12.0,
    [double]$PlannerLocalUpdateRangeZM = 3.0,
    [int]$CoverageExecuteS = 7800,
    [int]$GoalTimeoutS = 90,
    [int]$ProbeReadyTimeoutS = 300,
    [int]$PreGoalStableTimeoutS = 120,
    [double]$PreGoalMaxSpeedMps = 0.35,
    [double]$PreGoalMaxVzMps = 0.20,
    [ValidateSet("adapter_hold", "direct_hover")]
    [string]$InteractiveHandoffMode = "direct_hover",
    [double]$InteractiveTargetReachedXYM = 0.45,
    [double]$InteractiveTargetReachedZM = 0.15,
    [double]$InteractiveTargetHoldS = 1.5,
    [double]$InteractiveTargetHoldMaxSpeedMps = 0.45,
    [double]$InteractiveTargetHoldMaxVzMps = 0.25,
    [double]$InteractiveTargetHoldMaxRollPitchDeg = 12.0,
    [double]$TakeoffHeight = [double]::NaN,
    [double]$TakeoffZTolM = 0.12,
    [double]$TakeoffSpeedMps = 0.12,
    [double]$PreGoalTargetZ = [double]::NaN,
    [double]$PreGoalMinZM = [double]::NaN,
    [double]$PreGoalZTolM = 0.20,
    [double]$ClickReadyZTolM = 0.15,
    [int]$Goal4TakeoffTimeoutS = 60,
    [int]$MavrosReadyTimeoutS = 240,
    [double]$PublishHoverDuringTakeoffDelayS = 0.3,
    [int]$LandTimeoutS = 60,
    [int]$RuntimeTimeoutS = 9000,
    [int]$OuterWaitTimeoutS = 9600,
    [double]$CoverageGridResolutionM = 2.0,
    [double]$CoverageSensorRadiusM = 8.0,
    [double]$MinSensorCoverageRatio = 0.80,
    [int]$CoverageTargetMinNewCells = 15,
    [double]$CoverageTargetStopRatio = 0.82,
    [double]$DiffMapPaddingM = 2.0,
    [switch]$AllowRuntimeSkippedGoals,
    [switch]$AllowRequestedGoalOnForwardedTimeout,
    [double]$RuntimeSkipMaxXYErrorM = 3.00,
    [switch]$AllowCoverageSoftWaypoints,
    [double]$CoverageSoftXYRadiusM = 2.0,
    [switch]$EnableRouteRejoin,
    [switch]$RouteRejoinAfterSoftWaypoint,
    [switch]$AllowRouteRejoinOnStableFailure,
    [double]$RouteRejoinLocalHorizonM = 5.0,
    [int]$RouteRejoinSearchCount = 80,
    [double]$RouteRejoinMinImprovementM = 0.50,
    [double]$RouteRejoinStableFailureMaxXYErrorM = 12.0,
    [double]$RouteRejoinStableFailureMaxSpeedMps = 0.08,
    [double]$RouteRejoinStableFailureMaxRollPitchDeg = 8.0,
    [string]$Px4Ekf2EvCtrlOverride = "",
    [string]$Px4Ekf2HgtRefOverride = "",
    [string]$Px4ExtraParamOverrides = "",
    [int]$RouteSliceStartIndex = 0,
    [int]$RouteSliceCount = 0,
    [switch]$AttitudeStuckGate,
    [double]$AttitudeStuckMinElapsedS = 8.0,
    [double]$AttitudeStuckHoldS = 2.0,
    [double]$AttitudeStuckMinXYErrorM = 2.0,
    [double]$AttitudeStuckMaxSpeedMps = 0.08,
    [double]$AttitudeStuckMaxVzMps = 0.05,
    [double]$AttitudeStuckMinRollPitchDeg = 18.0,
    [double]$PointCloudReviewMaxAccumRollPitchDeg = 5.0,
    [double]$PointCloudReviewMaxAccumYawRateDegS = 30.0,
    [double]$PointCloudReviewMaxAccumSpeedXYMps = 0.45,
    [double]$PointCloudReviewMaxAccumSpeedZMps = 0.30,
    [double]$OccupancyReviewMaxAccumRollPitchDeg = -1.0,
    [double]$OccupancyReviewMaxAccumYawRateDegS = -1.0,
    [double]$OccupancyReviewMaxAccumSpeedXYMps = -1.0,
    [double]$OccupancyReviewMaxAccumSpeedZMps = -1.0,
    [string]$OccupancyReviewSourceTopic = "/uav1/livox_world",
    [double]$OccupancyReviewVoxelSizeM = 0.20,
    [double]$BodyAxisLengthM = 0.60,
    [double]$BodyAxisShaftM = 0.035,
    [double]$BodyAxisHeadDiameterM = 0.10,
    [double]$BodyAxisHeadLengthM = 0.14,
    [switch]$AllowEmptyFinalOccupancy,
    [switch]$AllowDiscontinuousRawPlannerPositionCmd,
    [switch]$SkipLandAfterExploration,
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
$FactoryWorldWsl = $ProjectRootWsl + "/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf"
$FactoryModelPathWsl = $ProjectRootWsl + "/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/models"
$WaypointJsonWin = Join-Path $ResultDirWin "factory_l2_clearance_route_waypoints.json"
$WaypointYamlWin = Join-Path $ResultDirWin "factory_l2_clearance_route_waypoints.yaml"
$WaypointJsonWsl = $ResultDirWsl + "/factory_l2_clearance_route_waypoints.json"
$WaypointYamlWsl = $ResultDirWsl + "/factory_l2_clearance_route_waypoints.yaml"
$ManifestPath = Join-Path $ResultDirWin "FACTORY_L2_DIFF_INTERACTIVE_COVERAGE_PROBE.json"

function Get-Number($Value, [double]$Default) {
    if ($null -eq $Value) { return $Default }
    try { return [double]$Value } catch { return $Default }
}

New-Item -ItemType Directory -Force -Path $ResultDirWin | Out-Null

if ($WaypointJsonOverride -or $WaypointYamlOverride) {
    if (-not ($WaypointJsonOverride -and $WaypointYamlOverride)) {
        throw "WaypointJsonOverride and WaypointYamlOverride must be provided together."
    }
    if (-not (Test-Path -LiteralPath $WaypointJsonOverride)) {
        throw "WaypointJsonOverride not found: $WaypointJsonOverride"
    }
    if (-not (Test-Path -LiteralPath $WaypointYamlOverride)) {
        throw "WaypointYamlOverride not found: $WaypointYamlOverride"
    }
    Copy-Item -LiteralPath $WaypointJsonOverride -Destination $WaypointJsonWin -Force
    Copy-Item -LiteralPath $WaypointYamlOverride -Destination $WaypointYamlWin -Force
} else {
    $generator = Join-Path $ProjectRootWin "Scripts\sunray\generate_factory_l2_clearance_route_waypoints.py"
    python $generator `
        --envelope $EnvelopeWin `
        --output-yaml $WaypointYamlWin `
        --output-json $WaypointJsonWin `
        --section test1 `
        --z-m $TargetZ `
        --grid-step-m $ClearanceGridStepM `
        --transit-grid-step-m $TransitGridStepM `
        --boundary-margin-m $BoundaryMarginM `
        --floor-edge-margin-m $FloorEdgeMarginM `
        --clearance-margin-m $ClearanceMarginM `
        --flight-obstacle-min-z-m $FlightObstacleMinZM `
        --flight-obstacle-max-z-m $FlightObstacleMaxZM `
        --obstacle-z-inflation-m $ObstacleZInflationM `
        --overhead-obstacle-max-min-z-m $OverheadObstacleMaxMinZM `
        --route-policy $ClearanceRoutePolicy `
        --coverage-order $CoverageOrder `
        --start-x-m $RouteStartX `
        --start-y-m $RouteStartY `
        --no-include-center-start `
        --min-start-target-distance-m $MinStartTargetDistanceM `
        --max-coverage-targets $MaxCoverageTargets `
        --max-waypoints $MaxWaypoints `
        --max-segment-m $MaxSegmentM `
        $(if ($DropImmediateBacktracks) { "--drop-immediate-backtracks" }) `
        --coverage-resolution-m $CoverageGridResolutionM `
        --sensor-radius-m $CoverageSensorRadiusM `
        --coverage-target-min-new-cells $CoverageTargetMinNewCells `
        --coverage-target-stop-ratio $CoverageTargetStopRatio | Out-Null
}

if ($RouteSliceStartIndex -gt 0 -or $RouteSliceCount -gt 0) {
    $sliceStart = if ($RouteSliceStartIndex -gt 0) { $RouteSliceStartIndex } else { 1 }
    $slicer = Join-Path $ProjectRootWin "Scripts\sunray\slice_factory_route_waypoints.py"
    python $slicer `
        --input-json $WaypointJsonWin `
        --output-json $WaypointJsonWin `
        --output-yaml $WaypointYamlWin `
        --section test1 `
        --start-index $sliceStart `
        --count $RouteSliceCount | Out-Null
}

$waypointPacket = Get-Content -LiteralPath $WaypointJsonWin -Raw | ConvertFrom-Json
$boundary = $waypointPacket.boundary
$centerX = Get-Number $boundary.center_x_m 0.0
$centerY = Get-Number $boundary.center_y_m 0.0
$minX = Get-Number $boundary.min_x_m 0.0
$maxX = Get-Number $boundary.max_x_m 0.0
$minY = Get-Number $boundary.min_y_m 0.0
$maxY = Get-Number $boundary.max_y_m 0.0
$mapSizeX = [Math]::Max(1.0, $maxX - $minX)
$mapSizeY = [Math]::Max(1.0, $maxY - $minY)
$diffMapInitX = $minX - $DiffMapPaddingM
$diffMapInitY = $minY - $DiffMapPaddingM
$diffMapInitZ = 0.0
$diffMapSizeX = $mapSizeX + (2.0 * $DiffMapPaddingM)
$diffMapSizeY = $mapSizeY + (2.0 * $DiffMapPaddingM)
$diffMapSizeZ = $MapSizeZ
$effectiveTakeoffHeight = if ([double]::IsNaN($TakeoffHeight)) { $TargetZ } else { $TakeoffHeight }
$effectivePreGoalTargetZ = if ([double]::IsNaN($PreGoalTargetZ)) { $TargetZ } else { $PreGoalTargetZ }
$effectivePreGoalMinZ = if ([double]::IsNaN($PreGoalMinZM)) { $CommandMinZ } else { $PreGoalMinZM }
$interactiveGoalCount = [int]$waypointPacket.waypoint_count
if ($MaxInteractiveGoals -gt 0) {
    $interactiveGoalCount = [Math]::Min($interactiveGoalCount, $MaxInteractiveGoals)
}
$openRvizValue = if ($WithRviz) { "true" } else { "false" }
$keepAliveValue = if ($WithRviz) { "true" } else { "false" }
$pointCloudCap = if ($NoUnlimitedAccumulation) { 2000000 } else { 0 }
$occupancyCap = if ($NoUnlimitedAccumulation) { 1000000 } else { 0 }
$diffUseMultipointValue = if ($UseMultipointRoute) { "true" } else { "false" }
$diffInteractiveClickGoalValue = if ($UseMultipointRoute) { "false" } else { "true" }
$diffMultipointEnvParts = if ($UseMultipointRoute) {
    @(
        "DIFF_MULTIPOINT_YAML=$WaypointYamlWsl",
        "DIFF_WAYPOINT_AUDIT_SECTION=test1",
        "DIFF_MULTIPOINT_NEXT_DISTANCE=$DiffMultipointNextDistanceM",
        "DIFF_MULTIPOINT_FLIGHT_TYPE=1"
    )
} else {
    @()
}
$effectiveOccupancyAccumRollPitch = if ($OccupancyReviewMaxAccumRollPitchDeg -ge 0.0) { $OccupancyReviewMaxAccumRollPitchDeg } else { $PointCloudReviewMaxAccumRollPitchDeg }
$effectiveOccupancyAccumYawRate = if ($OccupancyReviewMaxAccumYawRateDegS -ge 0.0) { $OccupancyReviewMaxAccumYawRateDegS } else { $PointCloudReviewMaxAccumYawRateDegS }
$effectiveOccupancyAccumSpeedXY = if ($OccupancyReviewMaxAccumSpeedXYMps -ge 0.0) { $OccupancyReviewMaxAccumSpeedXYMps } else { $PointCloudReviewMaxAccumSpeedXYMps }
$effectiveOccupancyAccumSpeedZ = if ($OccupancyReviewMaxAccumSpeedZMps -ge 0.0) { $OccupancyReviewMaxAccumSpeedZMps } else { $PointCloudReviewMaxAccumSpeedZMps }
$allowRuntimeSkipArg = if ($AllowRuntimeSkippedGoals) { "--allow-runtime-skipped-goals" } else { "" }
$allowRequestedOnForwardTimeoutArg = if ($AllowRequestedGoalOnForwardedTimeout) { "--allow-requested-goal-on-forwarded-timeout" } else { "" }
$allowCoverageSoftArg = if ($AllowCoverageSoftWaypoints) { "--allow-coverage-soft-waypoints" } else { "" }
$rawCmdZWarningsOnlyArg = if ($RawCmdZWarningsOnly) { "--raw-cmd-z-warnings-only" } else { "" }
$allowInitialCmdZBelowArg = if ($RawCmdZWarningsOnly) { "--allow-initial-cmd-z-below-gate" } else { "" }
$enableRouteRejoinArg = if ($EnableRouteRejoin) { "--enable-route-rejoin" } else { "" }
$routeRejoinAfterSoftArg = if ($RouteRejoinAfterSoftWaypoint) { "--route-rejoin-after-soft-waypoint" } else { "" }
$allowRouteRejoinOnStableFailureArg = if ($AllowRouteRejoinOnStableFailure) { "--allow-route-rejoin-on-stable-failure" } else { "" }
$attitudeStuckGateArg = if ($AttitudeStuckGate) { "--attitude-stuck-gate" } else { "" }
$effectiveCommandAuditMaxZ = if ($CommandAuditMaxZ -gt 0.0) { $CommandAuditMaxZ } else { $CommandMaxZ }
$effectiveCommandFixedZ = if ($CommandFixedZ -gt 0.0) { "$CommandFixedZ" } else { "" }
$effectiveUavInitX = if ([double]::IsNaN($UavInitX)) { $RouteStartX } else { $UavInitX }
$effectiveUavInitY = if ([double]::IsNaN($UavInitY)) { $RouteStartY } else { $UavInitY }
$zeroAllCommandDynamicsValue = if ($ZeroAllCommandDynamics) { "true" } else { "false" }
$allowEmptyFinalOccupancyValue = if ($AllowEmptyFinalOccupancy) { "true" } else { "false" }
$allowDiscontinuousRawPlannerPositionCmdValue = if ($AllowDiscontinuousRawPlannerPositionCmd) { "true" } else { "false" }
$skipLandAfterExplorationValue = if ($SkipLandAfterExploration) { "true" } else { "false" }

if ($DryRun) {
    $manifest = [pscustomobject]@{
        schema = "mosim.factory_l2_diff_interactive_coverage_probe.v1"
        status = "dry_run_planned"
        generated_at = (Get-Date).ToString("o")
        run_id = $RunId
        result_dir = $ResultDirWin
        waypoint_packet = $WaypointJsonWin
        waypoint_yaml = $WaypointYamlWin
        waypoint_count = $waypointPacket.waypoint_count
        interactive_goal_count = $interactiveGoalCount
        diff_map_origin = [pscustomobject]@{ x = $diffMapInitX; y = $diffMapInitY; z = $diffMapInitZ }
        diff_map_size = [pscustomobject]@{ x = $diffMapSizeX; y = $diffMapSizeY; z = $diffMapSizeZ }
        diff_map_padding_m = $DiffMapPaddingM
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
    "PX4CTRL_CORE_PROFILE=$ControllerCoreProfile",
    "PX4CTRL_EKF2_EV_CTRL_OVERRIDE=$Px4Ekf2EvCtrlOverride",
    "PX4CTRL_EKF2_HGT_REF_OVERRIDE=$Px4Ekf2HgtRefOverride",
    "PX4CTRL_EXTRA_PARAM_OVERRIDES=$Px4ExtraParamOverrides",
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
    "SUNRAY_UAV_INIT_X=$effectiveUavInitX",
    "SUNRAY_UAV_INIT_Y=$effectiveUavInitY",
    "SUNRAY_UAV_INIT_Z=0.2",
    "SUNRAY_UAV_INIT_YAW=0.0",
    "TARGET_X=$($waypointPacket.first_waypoint[0])",
    "TARGET_Y=$($waypointPacket.first_waypoint[1])",
    "TARGET_Z=$TargetZ",
    "PLANNER_MISSION_MODE=exploration_stream",
    "PLANNER_EXPLORATION_EXECUTE_S=$CoverageExecuteS",
    "EGO_ALLOW_EMPTY_FINAL_OCCUPANCY=$allowEmptyFinalOccupancyValue",
    "EGO_ALLOW_DISCONTINUOUS_RAW_PLANNER_POSITION_CMD=$allowDiscontinuousRawPlannerPositionCmdValue",
    "EGO_SKIP_LAND_AFTER_EXPLORATION=$skipLandAfterExplorationValue",
    "DIFF_USE_MULTIPOINT=$diffUseMultipointValue",
    $diffMultipointEnvParts,
    "DIFF_INTERACTIVE_CLICK_GOAL=$diffInteractiveClickGoalValue",
    "DIFF_AUTO_GOAL_IN_INTERACTIVE_REVIEW=false",
    "DIFF_INTERACTIVE_AUTO_PASS_GOAL_COUNT=$interactiveGoalCount",
    "DIFF_INTERACTIVE_REVIEW_HOLD_S=$CoverageExecuteS",
    "DIFF_ENABLE_Z_AUDIT=false",
    "DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S=3.0",
    "DIFF_INTERACTIVE_TARGET_REACHED_XY_M=$InteractiveTargetReachedXYM",
    "DIFF_INTERACTIVE_TARGET_REACHED_Z_M=$InteractiveTargetReachedZM",
    "DIFF_INTERACTIVE_TARGET_HOLD_S=$InteractiveTargetHoldS",
    "DIFF_INTERACTIVE_TARGET_HOLD_MAX_SPEED_MPS=$InteractiveTargetHoldMaxSpeedMps",
    "DIFF_INTERACTIVE_TARGET_HOLD_MAX_VZ_MPS=$InteractiveTargetHoldMaxVzMps",
    "DIFF_INTERACTIVE_TARGET_HOLD_MAX_ROLL_PITCH_DEG=$InteractiveTargetHoldMaxRollPitchDeg",
    "DIFF_INTERACTIVE_HANDOFF_MODE=$InteractiveHandoffMode",
    "DIFF_ENABLE_CMD_SAFETY_ADAPTER=true",
    "DIFF_CMD_INVALID_Z_POLICY=clamp",
    "DIFF_CMD_MIN_Z=$CommandMinZ",
    "DIFF_CMD_MAX_Z=$CommandMaxZ",
    "PLANNER_CMD_FIXED_Z=$effectiveCommandFixedZ",
    "PLANNER_CMD_ZERO_ALL_DYNAMICS=$zeroAllCommandDynamicsValue",
    "DIFF_CMD_SAFETY_MAX_POSITION_JUMP_M=0.50",
    "DIFF_CMD_SAFETY_MAX_POSITION_JUMP_SPEED_MPS=3.0",
    "EGO_MAX_VEL=$PlannerMaxVelMps",
    "EGO_MAX_ACC=$PlannerMaxAccMps2",
    "EGO_PLANNING_HORIZON=7.0",
    "EGO_GRID_RESOLUTION=0.20",
    "EGO_OBSTACLES_INFLATION=0.25",
    "EGO_OBSTACLE_CLEARANCE=0.25",
    "EGO_OBSTACLE_CLEARANCE_SOFT=0.45",
    "EGO_VIRTUAL_CEIL_HEIGHT=$VirtualCeilHeight",
    "EGO_VISUALIZATION_TRUNCATE_HEIGHT=$ReviewMaxZ",
    "EGO_GRID_INIT_X=$diffMapInitX",
    "EGO_GRID_INIT_Y=$diffMapInitY",
    "EGO_GRID_INIT_Z=$diffMapInitZ",
    "EGO_MAP_SIZE_X=$diffMapSizeX",
    "EGO_MAP_SIZE_Y=$diffMapSizeY",
    "EGO_MAP_SIZE_Z=$diffMapSizeZ",
    "EGO_LOCAL_UPDATE_RANGE_X=$PlannerLocalUpdateRangeXYM",
    "EGO_LOCAL_UPDATE_RANGE_Y=$PlannerLocalUpdateRangeXYM",
    "EGO_LOCAL_UPDATE_RANGE_Z=$PlannerLocalUpdateRangeZM",
    "FUEL_MAP_SIZE_X=$mapSizeX",
    "FUEL_MAP_SIZE_Y=$mapSizeY",
    "FUEL_MAP_SIZE_Z=$MapSizeZ",
    "FUEL_BOX_MIN_X=$minX",
    "FUEL_BOX_MAX_X=$maxX",
    "FUEL_BOX_MIN_Y=$minY",
    "FUEL_BOX_MAX_Y=$maxY",
    "FUEL_BOX_MIN_Z=$PlannerMinZ",
    "FUEL_BOX_MAX_Z=$PlannerMaxZ",
    "FACTORY_INDOOR_BOUNDARY_MIN_X=$minX",
    "FACTORY_INDOOR_BOUNDARY_MAX_X=$maxX",
    "FACTORY_INDOOR_BOUNDARY_MIN_Y=$minY",
    "FACTORY_INDOOR_BOUNDARY_MAX_Y=$maxY",
    "GOAL4_TAKEOFF_HEIGHT=$effectiveTakeoffHeight",
    "GOAL4_TAKEOFF_Z_TOL=$TakeoffZTolM",
    "GOAL4_TAKEOFF_TIMEOUT_S=$Goal4TakeoffTimeoutS",
    "PX4CTRL_AUTO_TAKEOFF_SPEED=$TakeoffSpeedMps",
    "GOAL4_LAND_TIMEOUT_S=$LandTimeoutS",
    "GOAL4_EGO_TAKEOVER_TIMEOUT_S=120",
    "DIFF_PUBLISH_HOVER_DURING_TAKEOFF=true",
    "DIFF_PUBLISH_HOVER_DURING_TAKEOFF_DELAY_S=$PublishHoverDuringTakeoffDelayS",
    "MAVROS_READY_TIMEOUT_S=$MavrosReadyTimeoutS",
    "GOAL4_RECORD_HZ=100",
    "GOAL4_RECORD_CMD_HZ=100",
    "GOAL4_MAX_PATH_POINTS=0",
    "GOAL4_PATH_PUBLISH_HZ=20",
    "GOAL4_REVIEW_HOLD_PATH_PUBLISH_HZ=10",
    "DIFF_INTERACTIVE_YAW_SCAN_AFTER_GOAL=false",
    "DIFF_INTERACTIVE_YAW_SCAN_DISABLE_CMD_ADAPTER=false",
    "DIFF_PRE_MAX_Z_ERROR_M=$PreGoalZTolM",
    "DIFF_PRE_MAX_SPEED_MPS=$PreGoalMaxSpeedMps",
    "DIFF_PRE_MAX_VZ_MPS=$PreGoalMaxVzMps",
    "DIFF_CLICK_READY_Z_TOL=$ClickReadyZTolM",
    "POINTCLOUD_REVIEW_VOXEL_SIZE_M=0.08",
    "POINTCLOUD_MIN_WORLD_Z_M=-0.2",
    "POINTCLOUD_REVIEW_MIN_WORLD_Z_M=0.2",
    "POINTCLOUD_REVIEW_MAX_WORLD_Z_M=$ReviewMaxZ",
    "POINTCLOUD_REVIEW_MAX_POINTS_PER_CLOUD=50000",
    "POINTCLOUD_REVIEW_MAX_ACCUMULATED_POINTS=$pointCloudCap",
    "POINTCLOUD_REVIEW_PUBLISH_RATE_HZ=2.0",
    "POINTCLOUD_REVIEW_MAX_ACCUM_ROLL_PITCH_DEG=$PointCloudReviewMaxAccumRollPitchDeg",
    "POINTCLOUD_REVIEW_MAX_ACCUM_YAW_RATE_DEG_S=$PointCloudReviewMaxAccumYawRateDegS",
    "POINTCLOUD_REVIEW_MAX_ACCUM_SPEED_XY_MPS=$PointCloudReviewMaxAccumSpeedXYMps",
    "POINTCLOUD_REVIEW_MAX_ACCUM_SPEED_Z_MPS=$PointCloudReviewMaxAccumSpeedZMps",
    "OCCUPANCY_REVIEW_SOURCE_TOPIC=$OccupancyReviewSourceTopic",
    "OCCUPANCY_REVIEW_MIN_Z=0.20",
    "OCCUPANCY_REVIEW_MAX_Z=$ReviewMaxZ",
    "OCCUPANCY_REVIEW_VOXEL_SIZE_M=$OccupancyReviewVoxelSizeM",
    "OCCUPANCY_REVIEW_MAX_POINTS_PER_CLOUD=50000",
    "OCCUPANCY_REVIEW_MAX_ACCUMULATED_POINTS=$occupancyCap",
    "OCCUPANCY_REVIEW_PUBLISH_RATE_HZ=2.0",
    "OCCUPANCY_REVIEW_MAX_ACCUM_ROLL_PITCH_DEG=$effectiveOccupancyAccumRollPitch",
    "OCCUPANCY_REVIEW_MAX_ACCUM_YAW_RATE_DEG_S=$effectiveOccupancyAccumYawRate",
    "OCCUPANCY_REVIEW_MAX_ACCUM_SPEED_XY_MPS=$effectiveOccupancyAccumSpeedXY",
    "OCCUPANCY_REVIEW_MAX_ACCUM_SPEED_Z_MPS=$effectiveOccupancyAccumSpeedZ",
    "ENABLE_OCCUPANCY_REVIEW_ACCUMULATION=true",
    "GOAL4_BODY_AXIS_LENGTH_M=$BodyAxisLengthM",
    "GOAL4_BODY_AXIS_SHAFT_M=$BodyAxisShaftM",
    "GOAL4_BODY_AXIS_HEAD_DIAMETER_M=$BodyAxisHeadDiameterM",
    "GOAL4_BODY_AXIS_HEAD_LENGTH_M=$BodyAxisHeadLengthM",
    "TOTAL_TIMEOUT_S=$RuntimeTimeoutS"
)
$envParts = @($envParts | ForEach-Object { $_ })

$preflight = if ($SkipPreflight) {
    "echo skipped > '$ResultDirWsl/preflight_skipped.txt'"
} else {
    "bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh > '$ResultDirWsl/preflight.log' 2>&1"
}

$bashStatus = '$?'
$bashScriptWin = Join-Path $ResultDirWin "start_factory_diff_interactive_coverage_probe.sh"
$bashScriptWsl = $ResultDirWsl + "/start_factory_diff_interactive_coverage_probe.sh"
$command = @"
#!/usr/bin/env bash
set -uo pipefail
cd $ProjectRootWsl || exit 97
mkdir -p '$ResultDirWsl'
exec > >(tee -a '$ResultDirWsl/bootstrap.log') 2>&1
date --iso-8601=seconds > '$ResultDirWsl/background_start_marker.txt'
$preflight || { echo $bashStatus > '$ResultDirWsl/preflight_exit_code.txt'; exit 2; }
echo 0 > '$ResultDirWsl/preflight_exit_code.txt'
export GAZEBO_MODEL_PATH='$FactoryModelPathWsl':"`$`{GAZEBO_MODEL_PATH:-`}"

set +e
$($envParts -join " ") bash Scripts/sunray/run_px4ctrl_ego_single_gate.sh > '$ResultDirWsl/background_launcher.log' 2>&1 &
runner_pid=`$!
echo `$runner_pid > '$ResultDirWsl/runner_pid.txt'

set +u
source /opt/ros/noetic/setup.bash
source /opt/mosim_work/sunray_ws/Sunray/devel/setup.bash
source '$ProjectRootWsl/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash'
source '$ProjectRootWsl/Results/sunray_ros1/workspaces/goal4_diff_planner_ws_px4msg/devel/setup.bash'
set -u

if [[ "$diffUseMultipointValue" == "true" ]]; then
  wait "`$runner_pid"
  runner_exit=$bashStatus
  echo "PROBE_EXIT=0" > '$ResultDirWsl/outer_status.txt'
  echo "RUNNER_EXIT=`$runner_exit" >> '$ResultDirWsl/outer_status.txt'
  date --iso-8601=seconds > '$ResultDirWsl/interactive_coverage_end.txt'
  echo `$runner_exit > '$ResultDirWsl/background_exit_code.txt'
  exit "`$runner_exit"
fi

python3 Scripts/sunray/probe_diff_interactive_goal_switch_chain.py \
  --result-dir '$ResultDirWsl' \
  --output-json DIFF_INTERACTIVE_COVERAGE_GOAL_CHAIN_PROBE.json \
  --partial-output-json DIFF_INTERACTIVE_COVERAGE_GOAL_CHAIN_PROBE.partial.json \
  --goals-file '$WaypointJsonWsl' \
  --max-goals $interactiveGoalCount \
  --ready-timeout-s $ProbeReadyTimeoutS \
  --pre-goal-stable-timeout-s $PreGoalStableTimeoutS \
  --pre-goal-stable-s 1.0 \
  --pre-goal-target-z $effectivePreGoalTargetZ \
  --pre-goal-min-z-m $effectivePreGoalMinZ \
  --pre-goal-z-tol-m $PreGoalZTolM \
  --pre-goal-max-speed-mps $PreGoalMaxSpeedMps \
  --pre-goal-max-vz-mps $PreGoalMaxVzMps \
  --reach-xy-radius-m $InteractiveTargetReachedXYM \
  --reach-z-tol-m $InteractiveTargetReachedZM \
  --reach-max-speed-mps $InteractiveTargetHoldMaxSpeedMps \
  --reach-max-vz-mps $InteractiveTargetHoldMaxVzMps \
  --reach-hold-s $InteractiveTargetHoldS \
  --min-cmd-z-m $CommandMinZ \
  --max-cmd-z-m $effectiveCommandAuditMaxZ \
  --cmd-end-z-tol-m $CommandEndZTolM \
  $rawCmdZWarningsOnlyArg \
  $allowInitialCmdZBelowArg \
  $allowRequestedOnForwardTimeoutArg \
  --goal-timeout-s $GoalTimeoutS \
  $allowRuntimeSkipArg \
  --runtime-skip-max-xy-error-m $RuntimeSkipMaxXYErrorM \
  $allowCoverageSoftArg \
  --coverage-soft-xy-radius-m $CoverageSoftXYRadiusM \
  $enableRouteRejoinArg \
  $routeRejoinAfterSoftArg \
  $allowRouteRejoinOnStableFailureArg \
  --route-rejoin-local-horizon-m $RouteRejoinLocalHorizonM \
  --route-rejoin-search-count $RouteRejoinSearchCount \
  --route-rejoin-min-improvement-m $RouteRejoinMinImprovementM \
  --route-rejoin-stable-failure-max-xy-error-m $RouteRejoinStableFailureMaxXYErrorM \
  --route-rejoin-stable-failure-max-speed-mps $RouteRejoinStableFailureMaxSpeedMps \
  --route-rejoin-stable-failure-max-roll-pitch-deg $RouteRejoinStableFailureMaxRollPitchDeg \
  $attitudeStuckGateArg \
  --attitude-stuck-min-elapsed-s $AttitudeStuckMinElapsedS \
  --attitude-stuck-hold-s $AttitudeStuckHoldS \
  --attitude-stuck-min-xy-error-m $AttitudeStuckMinXYErrorM \
  --attitude-stuck-max-speed-mps $AttitudeStuckMaxSpeedMps \
  --attitude-stuck-max-vz-mps $AttitudeStuckMaxVzMps \
  --attitude-stuck-min-roll-pitch-deg $AttitudeStuckMinRollPitchDeg \
  --stop-on-first-failure \
  > '$ResultDirWsl/probe_stdout.txt' 2> '$ResultDirWsl/probe_stderr.txt'
probe_exit=$bashStatus
echo "PROBE_EXIT=`$probe_exit" > '$ResultDirWsl/outer_status.txt'
if [[ "`$probe_exit" -ne 0 ]]; then
  kill "`$runner_pid" >/dev/null 2>&1 || true
fi
wait "`$runner_pid"
runner_exit=$bashStatus
echo "RUNNER_EXIT=`$runner_exit" >> '$ResultDirWsl/outer_status.txt'
date --iso-8601=seconds > '$ResultDirWsl/interactive_coverage_end.txt'
if [[ "`$probe_exit" -ne 0 ]]; then
  echo `$probe_exit > '$ResultDirWsl/background_exit_code.txt'
  exit "`$probe_exit"
fi
echo `$runner_exit > '$ResultDirWsl/background_exit_code.txt'
exit "`$runner_exit"
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

$metricsPath = Join-Path $ResultDirWin "EGO_SINGLE_METRICS.json"
$metricsDeadline = (Get-Date).AddSeconds(90)
while (-not (Test-Path -LiteralPath $metricsPath)) {
    if ((Get-Date) -gt $metricsDeadline) {
        break
    }
    Start-Sleep -Seconds 2
}

$coverageDir = Join-Path $ResultDirWin "coverage_packet"
$coverageScript = Join-Path $ProjectRootWin "Scripts\sunray\build_factory_l2_indoor_coverage_packet.py"
python $coverageScript `
    --run $ResultDirWin `
    --output-dir $coverageDir `
    --grid-resolution-m $CoverageGridResolutionM `
    --sensor-radius-m $CoverageSensorRadiusM `
    --z-min-m $CommandMinZ `
    --z-max-m $CommandMaxZ `
    --min-sensor-coverage-ratio $MinSensorCoverageRatio | Out-File -FilePath (Join-Path $ResultDirWin "coverage_packet_builder_stdout.txt") -Encoding UTF8

$coveragePacketPath = Join-Path $coverageDir "FACTORY_L2_INDOOR_COVERAGE_PACKET.json"
$coverageStatus = "missing"
if (Test-Path -LiteralPath $coveragePacketPath) {
    $coverageStatus = (Get-Content -LiteralPath $coveragePacketPath -Raw | ConvertFrom-Json).status
}
$metricsStatus = "missing"
$metricsBlockerCount = $null
if (Test-Path -LiteralPath $metricsPath) {
    $metrics = Get-Content -LiteralPath $metricsPath -Raw | ConvertFrom-Json
    $metricsStatus = [string]$metrics.status
    $metricsBlockerCount = @($metrics.blockers).Count
}
$probePath = Join-Path $ResultDirWin "DIFF_INTERACTIVE_COVERAGE_GOAL_CHAIN_PROBE.json"
$probeStatus = "missing"
$probeBlockerCount = $null
if (Test-Path -LiteralPath $probePath) {
    $probe = Get-Content -LiteralPath $probePath -Raw | ConvertFrom-Json
    $probeStatus = [string]$probe.status
    $probeBlockerCount = @($probe.blockers).Count
}

$isPartialGoalProbe = ($MaxInteractiveGoals -gt 0 -and $MaxInteractiveGoals -lt [int]$waypointPacket.waypoint_count)
$multipointEvidencePassed = ($UseMultipointRoute -and $metricsStatus -eq "passed" -and $coverageStatus -eq "passed")
$manifestStatus = if ($multipointEvidencePassed) {
    "passed"
} elseif ($UseMultipointRoute -and $backendExit -eq 0 -and $metricsStatus -eq "passed") {
    "review_required_multipoint_metrics_passed_coverage_below_threshold_or_packet_blocked"
} elseif ($UseMultipointRoute) {
    "blocked_multipoint_backend_or_metrics_failed"
} elseif ($probeStatus -eq "passed" -and $isPartialGoalProbe) {
    "review_required_partial_goal_chain_passed"
} elseif ($probeStatus -eq "passed" -and $metricsStatus -eq "passed" -and $coverageStatus -eq "passed") {
    "passed"
} elseif ($probeStatus -eq "passed" -and $metricsStatus -eq "passed") {
    "review_required_coverage_below_threshold_or_packet_blocked"
} elseif ($probeStatus -eq "passed") {
    "review_required_goal_chain_passed_metrics_or_coverage_incomplete"
} else {
    "blocked_backend_or_goal_chain_failed"
}

$manifest = [pscustomobject]@{
    schema = "mosim.factory_l2_diff_interactive_coverage_probe.v1"
    status = $manifestStatus
    generated_at = (Get-Date).ToString("o")
    run_id = $RunId
    result_dir = $ResultDirWin
    backend_exit_code = $backendExit
    waypoint_packet = $WaypointJsonWin
    waypoint_yaml = $WaypointYamlWin
    waypoint_count = $waypointPacket.waypoint_count
    interactive_goal_count = $interactiveGoalCount
    goal_chain_probe_status = $probeStatus
    goal_chain_probe_blocker_count = $probeBlockerCount
    goal_chain_probe = $probePath
    metrics_status = $metricsStatus
    metrics_blocker_count = $metricsBlockerCount
    coverage_packet_status = $coverageStatus
    coverage_packet = $coveragePacketPath
    parameters = [pscustomobject]@{
        max_waypoints = $MaxWaypoints
        max_coverage_targets = $MaxCoverageTargets
        max_interactive_goals = $MaxInteractiveGoals
        use_multipoint_route = [bool]$UseMultipointRoute
        diff_multipoint_next_distance_m = $DiffMultipointNextDistanceM
        clearance_grid_step_m = $ClearanceGridStepM
        transit_grid_step_m = $TransitGridStepM
        clearance_margin_m = $ClearanceMarginM
        boundary_margin_m = $BoundaryMarginM
        floor_edge_margin_m = $FloorEdgeMarginM
        route_start_x_m = $RouteStartX
        route_start_y_m = $RouteStartY
        uav_init_x_m = $effectiveUavInitX
        uav_init_y_m = $effectiveUavInitY
        controller_core_profile = $ControllerCoreProfile
        clearance_route_policy = $ClearanceRoutePolicy
        min_start_target_distance_m = $MinStartTargetDistanceM
        max_segment_m = $MaxSegmentM
        drop_immediate_backtracks = [bool]$DropImmediateBacktracks
        target_z_m = $TargetZ
        flight_obstacle_min_z_m = $FlightObstacleMinZM
        flight_obstacle_max_z_m = $FlightObstacleMaxZM
        obstacle_z_inflation_m = $ObstacleZInflationM
        overhead_obstacle_max_min_z_m = $OverheadObstacleMaxMinZM
        allow_runtime_skipped_goals = [bool]$AllowRuntimeSkippedGoals
        allow_requested_goal_on_forwarded_timeout = [bool]$AllowRequestedGoalOnForwardedTimeout
        runtime_skip_max_xy_error_m = $RuntimeSkipMaxXYErrorM
        allow_coverage_soft_waypoints = [bool]$AllowCoverageSoftWaypoints
        coverage_soft_xy_radius_m = $CoverageSoftXYRadiusM
        enable_route_rejoin = [bool]$EnableRouteRejoin
        route_rejoin_after_soft_waypoint = [bool]$RouteRejoinAfterSoftWaypoint
        allow_route_rejoin_on_stable_failure = [bool]$AllowRouteRejoinOnStableFailure
        route_rejoin_local_horizon_m = $RouteRejoinLocalHorizonM
        route_rejoin_search_count = $RouteRejoinSearchCount
        route_rejoin_min_improvement_m = $RouteRejoinMinImprovementM
        route_rejoin_stable_failure_max_xy_error_m = $RouteRejoinStableFailureMaxXYErrorM
        route_rejoin_stable_failure_max_speed_mps = $RouteRejoinStableFailureMaxSpeedMps
        route_rejoin_stable_failure_max_roll_pitch_deg = $RouteRejoinStableFailureMaxRollPitchDeg
        route_slice_start_index = $RouteSliceStartIndex
        route_slice_count = $RouteSliceCount
        attitude_stuck_gate = [bool]$AttitudeStuckGate
        attitude_stuck_min_elapsed_s = $AttitudeStuckMinElapsedS
        attitude_stuck_hold_s = $AttitudeStuckHoldS
        attitude_stuck_min_xy_error_m = $AttitudeStuckMinXYErrorM
        attitude_stuck_max_speed_mps = $AttitudeStuckMaxSpeedMps
        attitude_stuck_max_vz_mps = $AttitudeStuckMaxVzMps
        attitude_stuck_min_roll_pitch_deg = $AttitudeStuckMinRollPitchDeg
        command_min_z_m = $CommandMinZ
        command_max_z_m = $CommandMaxZ
        command_audit_max_z_m = $effectiveCommandAuditMaxZ
        command_end_z_tol_m = $CommandEndZTolM
        command_fixed_z_m = $effectiveCommandFixedZ
        zero_all_command_dynamics = [bool]$ZeroAllCommandDynamics
        raw_cmd_z_warnings_only = [bool]$RawCmdZWarningsOnly
        planner_min_z_m = $PlannerMinZ
        planner_max_z_m = $PlannerMaxZ
        virtual_ceil_height_m = $VirtualCeilHeight
        map_size_z_m = $MapSizeZ
        review_max_z_m = $ReviewMaxZ
        diff_map_origin_x_m = $diffMapInitX
        diff_map_origin_y_m = $diffMapInitY
        diff_map_origin_z_m = $diffMapInitZ
        diff_map_size_x_m = $diffMapSizeX
        diff_map_size_y_m = $diffMapSizeY
        diff_map_size_z_m = $diffMapSizeZ
        diff_map_padding_m = $DiffMapPaddingM
        planner_max_vel_mps = $PlannerMaxVelMps
        planner_max_acc_mps2 = $PlannerMaxAccMps2
        planner_local_update_range_xy_m = $PlannerLocalUpdateRangeXYM
        planner_local_update_range_z_m = $PlannerLocalUpdateRangeZM
        coverage_execute_s = $CoverageExecuteS
        goal_timeout_s = $GoalTimeoutS
        pre_goal_stable_timeout_s = $PreGoalStableTimeoutS
        pre_goal_max_speed_mps = $PreGoalMaxSpeedMps
        pre_goal_max_vz_mps = $PreGoalMaxVzMps
        goal4_takeoff_timeout_s = $Goal4TakeoffTimeoutS
        mavros_ready_timeout_s = $MavrosReadyTimeoutS
        publish_hover_during_takeoff_delay_s = $PublishHoverDuringTakeoffDelayS
        takeoff_height_m = $effectiveTakeoffHeight
        takeoff_z_tol_m = $TakeoffZTolM
        takeoff_speed_mps = $TakeoffSpeedMps
        pre_goal_target_z_m = $effectivePreGoalTargetZ
        pre_goal_min_z_m = $effectivePreGoalMinZ
        pre_goal_z_tol_m = $PreGoalZTolM
        click_ready_z_tol_m = $ClickReadyZTolM
        land_timeout_s = $LandTimeoutS
        runtime_timeout_s = $RuntimeTimeoutS
        outer_wait_timeout_s = $OuterWaitTimeoutS
        with_rviz = [bool]$WithRviz
        unlimited_accumulation = -not [bool]$NoUnlimitedAccumulation
        pointcloud_review_max_accum_roll_pitch_deg = $PointCloudReviewMaxAccumRollPitchDeg
        pointcloud_review_max_accum_yaw_rate_deg_s = $PointCloudReviewMaxAccumYawRateDegS
        pointcloud_review_max_accum_speed_xy_mps = $PointCloudReviewMaxAccumSpeedXYMps
        pointcloud_review_max_accum_speed_z_mps = $PointCloudReviewMaxAccumSpeedZMps
        occupancy_review_max_accum_roll_pitch_deg = $effectiveOccupancyAccumRollPitch
        occupancy_review_max_accum_yaw_rate_deg_s = $effectiveOccupancyAccumYawRate
        occupancy_review_max_accum_speed_xy_mps = $effectiveOccupancyAccumSpeedXY
        occupancy_review_max_accum_speed_z_mps = $effectiveOccupancyAccumSpeedZ
        occupancy_review_source_topic = $OccupancyReviewSourceTopic
        occupancy_review_voxel_size_m = $OccupancyReviewVoxelSizeM
        allow_empty_final_occupancy = [bool]$AllowEmptyFinalOccupancy
        allow_discontinuous_raw_planner_position_cmd = [bool]$AllowDiscontinuousRawPlannerPositionCmd
        skip_land_after_exploration = [bool]$SkipLandAfterExploration
    }
    claim_boundary = @(
        "This is a same-flight supervised interactive-goal coverage route, not reset-window map stitching.",
        "The route uses the clean Factory ROS1/Sunray/PX4/MAVROS/px4ctrl runtime and waits for stable arrival before publishing the next target.",
        "Full-map coverage is accepted only if the goal chain, EGO_SINGLE_METRICS.json, and FACTORY_L2_INDOOR_COVERAGE_PACKET.json pass."
    )
}
$manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8
$manifest
exit $(if ($manifestStatus -eq "passed") { 0 } else { 1 })
