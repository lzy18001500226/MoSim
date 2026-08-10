param(
    [string]$RunId = ("factory_l2_diff_swarm_target_chain_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [ValidateRange(1, 3)]
    [int]$UavNum = 3,
    [int]$MaxGoalsPerUav = 3,
    [int]$PartitionWindowGoalsPerUav = 0,
    [ValidateSet("contiguous", "contiguous_swap_23", "round_robin", "spatial_y_bands", "spatial_x_bands")]
    [string]$PartitionPolicy = "contiguous",
    [int]$PartitionStartIndex = 0,
    [string]$WaypointJsonOverride = "",
    [double]$ClearanceGridStepM = 6.0,
    [double]$TransitGridStepM = 1.5,
    [double]$ClearanceMarginM = 0.6,
    [double]$BoundaryMarginM = 2.0,
    [double]$FloorEdgeMarginM = 0.5,
    [double]$RouteStartX = -72.404960,
    [double]$RouteStartY = 1.637090,
    [ValidateSet("nearest_neighbor", "nearest_neighbor_transit", "coverage_gain_transit", "ordered_targets", "astar_connected")]
    [string]$ClearanceRoutePolicy = "coverage_gain_transit",
    [ValidateSet("topdown", "bottomup", "start_outward")]
    [string]$CoverageOrder = "topdown",
    [double]$TargetZ = 3.0,
    [double]$FlightObstacleMinZM = 2.5,
    [double]$FlightObstacleMaxZM = 3.5,
    [double]$OverheadObstacleMaxMinZM = 5.5,
    [double]$PlannerMaxVelMps = 0.30,
    [double]$PlannerMaxAccMps2 = 0.30,
    [ValidateSet("goal", "trigger")]
    [string]$DiffPlannerTargetMode = "goal",
    [ValidateSet(1, 2)]
    [int]$DiffFlightType = 1,
    [double]$PlannerLocalUpdateRangeXYM = 12.0,
    [double]$PlannerLocalUpdateRangeZM = 3.0,
    [double]$CommandMinZ = 2.40,
    [double]$CommandMaxZ = 3.20,
    [double]$VirtualCeilHeight = 4.50,
    [double]$MapSizeZ = 5.0,
    [double]$ReviewMaxZ = 4.0,
    [double]$TakeoffLandSpeedMps = 0.60,
    [double]$DiffMapPaddingM = 2.0,
    [int]$TargetChainGoalTimeoutS = 90,
    [double]$TargetStableSkipRadiusM = 0.0,
    [double]$TargetStableSkipS = 2.0,
    [double]$TargetStableSkipMaxSpeedMps = 0.08,
    [double]$TargetStableSkipMaxVzMps = 0.08,
    [int]$RuntimeTimeoutS = 420,
    [int]$OuterWaitTimeoutS = 520,
    [int]$TakeoffTimeoutS = 120,
    [double]$TakeoffUavStaggerS = 2.0,
    [int]$TakeoffRetryRepeats = 3,
    [int]$TakeoffRetryMax = 2,
    [switch]$PublishHoverDuringTakeoff,
    [double]$CoverageGridResolutionM = 2.0,
    [double]$CoverageSensorRadiusM = 8.0,
    [int]$CoverageTargetMinNewCells = 15,
    [double]$MinSensorCoverageRatio = 0.80,
    [double]$CoverageTargetStopRatio = 0.82,
    [double]$MinSameRoundTargetDistanceM = 4.0,
    [string]$ControllerCoreProfile = "l1_awff",
    [string]$Px4Ekf2EvCtrlOverride = "",
    [string]$Px4Ekf2HgtRefOverride = "",
    [string]$Px4ExtraParamOverrides = "",
    [switch]$SkipPx4ParamSnapshot,
    [switch]$StartupOnly,
    [int]$StartupAttempts = 1,
    [int]$OdomReadyTimeoutS = 40,
    [double]$StaggeredSpawnIntervalS = 20.0,
    [ValidateSet("PartitionRoute", "AcceptedSafe")]
    [string]$SpawnStartMode = "PartitionRoute",
    [ValidateSet("LShape", "XLine")]
    [string]$AcceptedSafeLayout = "LShape",
    [double]$AcceptedSafeSpacingM = 2.0,
    [switch]$PrependStartTransition,
    [double]$StartTransitionStepM = 6.0,
    [double]$StartTransitionMinDistanceM = 2.0,
    [switch]$UseNearStartSmokeTargets,
    [double]$NearStartSmokeDxM = 3.0,
    [switch]$SequentialSpawn,
    [switch]$DisableStaggeredSpawn,
    [switch]$PreloadGazeboModels,
    [switch]$DryRun,
    [switch]$SkipPreflight,
    [switch]$WithRviz,
    [switch]$KeepAlive
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
$PartitionDirWin = Join-Path $ResultDirWin "swarm_partitions"
$PartitionDirWsl = $ResultDirWsl + "/swarm_partitions"
$ManifestPath = Join-Path $ResultDirWin "FACTORY_L2_DIFF_SWARM_COVERAGE_PROBE.json"

function Get-Number($Value, [double]$Default) {
    if ($null -eq $Value) { return $Default }
    try { return [double]$Value } catch { return $Default }
}

function Get-FirstWaypoint($Path, $Fallback) {
    if (-not (Test-Path -LiteralPath $Path)) {
        return @([double]$Fallback[0], [double]$Fallback[1], [double]$Fallback[2])
    }
    $packet = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    if ($null -eq $packet.first_waypoint -or $packet.first_waypoint.Count -lt 3) {
        return @([double]$Fallback[0], [double]$Fallback[1], [double]$Fallback[2])
    }
    return @([double]$packet.first_waypoint[0], [double]$packet.first_waypoint[1], [double]$packet.first_waypoint[2])
}

function Write-SingleWaypointChain($Path, [int]$UavId, $Waypoint, $Boundary, $SourcePacket) {
    $packet = [pscustomobject]@{
        schema = "mosim.factory_l2_swarm_partitioned_waypoints.v1"
        source_packet = $SourcePacket
        uav_id = $UavId
        boundary = $Boundary
        waypoint_count = 1
        first_waypoint = @([double]$Waypoint[0], [double]$Waypoint[1], [double]$Waypoint[2])
        last_waypoint = @([double]$Waypoint[0], [double]$Waypoint[1], [double]$Waypoint[2])
        route_length_m = 0.0
        waypoints = @(, @([double]$Waypoint[0], [double]$Waypoint[1], [double]$Waypoint[2]))
        claim_boundary = "Near-start nonzero smoke target chain for verifying three-UAV Diff-Planner trigger takeover before full Factory L2 coverage."
    }
    $json = $packet | ConvertTo-Json -Depth 8
    [System.IO.File]::WriteAllText($Path, $json, [System.Text.UTF8Encoding]::new($false))
}

function Write-TransitionWaypointChain($InputPath, $OutputPath, [int]$UavId, $Start, [double]$StepM, [double]$MinDistanceM) {
    if (-not (Test-Path -LiteralPath $InputPath)) {
        throw "missing chain file for transition: $InputPath"
    }
    $packet = Get-Content -LiteralPath $InputPath -Raw | ConvertFrom-Json
    $rawWaypoints = @($packet.waypoints)
    if ($rawWaypoints.Count -lt 1) {
        throw "empty chain file for transition: $InputPath"
    }

    $first = @([double]$rawWaypoints[0][0], [double]$rawWaypoints[0][1], [double]$rawWaypoints[0][2])
    $sx = [double]$Start[0]
    $sy = [double]$Start[1]
    $sz = [double]$Start[2]
    $dx = $first[0] - $sx
    $dy = $first[1] - $sy
    $dz = $first[2] - $sz
    $distance = [Math]::Sqrt(($dx * $dx) + ($dy * $dy) + ($dz * $dz))

    $transition = [System.Collections.ArrayList]::new()
    if ($distance -gt $MinDistanceM) {
        $segments = [Math]::Max(1, [int][Math]::Ceiling($distance / [Math]::Max(0.1, $StepM)))
        for ($i = 1; $i -lt $segments; $i++) {
            $ratio = [double]$i / [double]$segments
            $px = $sx + ($dx * $ratio)
            $py = $sy + ($dy * $ratio)
            $pz = $sz + ($dz * $ratio)
            [void]$transition.Add(@($px, $py, $pz))
        }
    }

    $newWaypoints = [System.Collections.ArrayList]::new()
    foreach ($wp in $transition) {
        [void]$newWaypoints.Add(@([double]$wp[0], [double]$wp[1], [double]$wp[2]))
    }
    foreach ($wp in $rawWaypoints) {
        [void]$newWaypoints.Add(@([double]$wp[0], [double]$wp[1], [double]$wp[2]))
    }

    $routeLength = 0.0
    for ($i = 1; $i -lt $newWaypoints.Count; $i++) {
        $a = $newWaypoints[$i - 1]
        $b = $newWaypoints[$i]
        $routeLength += [Math]::Sqrt(
            [Math]::Pow(([double]$b[0] - [double]$a[0]), 2) +
            [Math]::Pow(([double]$b[1] - [double]$a[1]), 2) +
            [Math]::Pow(([double]$b[2] - [double]$a[2]), 2)
        )
    }

    $out = [pscustomobject]@{
        schema = "mosim.factory_l2_swarm_partitioned_waypoints.v1"
        source_packet = $packet.source_packet
        source_chain_file = $InputPath
        uav_id = $UavId
        boundary = $packet.boundary
        planned_coverage_proxy = $packet.planned_coverage_proxy
        waypoint_count = $newWaypoints.Count
        transition_waypoint_count = $transition.Count
        transition_step_m = $StepM
        transition_min_distance_m = $MinDistanceM
        start_for_transition = @($sx, $sy, $sz)
        first_waypoint = $newWaypoints[0]
        last_waypoint = $newWaypoints[$newWaypoints.Count - 1]
        route_length_m = $routeLength
        waypoints = $newWaypoints
        claim_boundary = "Per-UAV known-scene target chain with prepended transition waypoints from an accepted safe spawn; not autonomous task allocation."
    }
    $json = $out | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText($OutputPath, $json, [System.Text.UTF8Encoding]::new($false))
}

New-Item -ItemType Directory -Force -Path $ResultDirWin | Out-Null
$effectiveCoverageTargetStopRatio = if ($StartupOnly -and $MaxGoalsPerUav -gt 0 -and $MaxGoalsPerUav -le 3) { 0.04 } else { $CoverageTargetStopRatio }

$generator = Join-Path $ProjectRootWin "Scripts\sunray\generate_factory_l2_clearance_route_waypoints.py"
if ($WaypointJsonOverride) {
    $overridePath = [System.IO.Path]::GetFullPath($WaypointJsonOverride)
    if (-not $overridePath.StartsWith($ProjectRootWin, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "WaypointJsonOverride must stay inside MoSim: $overridePath"
    }
    if (-not (Test-Path -LiteralPath $overridePath)) {
        throw "WaypointJsonOverride does not exist: $overridePath"
    }
    Copy-Item -LiteralPath $overridePath -Destination $WaypointJsonWin -Force
} else {
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
    --overhead-obstacle-max-min-z-m $OverheadObstacleMaxMinZM `
    --route-policy $ClearanceRoutePolicy `
    --coverage-order $CoverageOrder `
    --start-x-m $RouteStartX `
    --start-y-m $RouteStartY `
    --no-include-center-start `
    --min-start-target-distance-m 4.0 `
    --coverage-resolution-m $CoverageGridResolutionM `
    --sensor-radius-m $CoverageSensorRadiusM `
    --coverage-target-min-new-cells $CoverageTargetMinNewCells `
    --coverage-target-stop-ratio $effectiveCoverageTargetStopRatio | Out-Null
}

$partitioner = Join-Path $ProjectRootWin "Scripts\sunray\partition_factory_l2_swarm_waypoints.py"
python $partitioner `
    --input-json $WaypointJsonWin `
    --output-dir $PartitionDirWin `
    --uav-num $UavNum `
    --policy $PartitionPolicy `
    --start-index $PartitionStartIndex `
    --max-goals-per-uav $MaxGoalsPerUav `
    $(if ($PartitionWindowGoalsPerUav -gt 0) { @("--partition-window-goals-per-uav", "$PartitionWindowGoalsPerUav") } else { @() }) `
    --min-same-round-target-distance-m $MinSameRoundTargetDistanceM `
    --prefix factory_l2_swarm | Out-File -FilePath (Join-Path $ResultDirWin "partition_stdout.txt") -Encoding UTF8

$PartitionSummaryPath = Join-Path $PartitionDirWin "factory_l2_swarm_partition_summary.json"
if (Test-Path -LiteralPath $PartitionSummaryPath) {
    $partitionSummary = Get-Content -LiteralPath $PartitionSummaryPath -Raw | ConvertFrom-Json
    $unresolvedRounds = @($partitionSummary.same_round_conflict_resolution.unresolved_rounds)
    if ($unresolvedRounds.Count -gt 0) {
        $blockedManifest = [pscustomobject]@{
            schema = "mosim.factory_l2_diff_swarm_coverage_probe.v1"
            status = "blocked_partition_conflict"
            generated_at = (Get-Date).ToString("o")
            run_id = $RunId
            result_dir = $ResultDirWin
            startup_only = [bool]$StartupOnly
            uav_num = $UavNum
            partition_policy = $PartitionPolicy
            partition_start_index = $PartitionStartIndex
            max_goals_per_uav = $MaxGoalsPerUav
            partition_window_goals_per_uav = $PartitionWindowGoalsPerUav
            min_same_round_target_distance_m = $MinSameRoundTargetDistanceM
            partition_summary = $PartitionSummaryPath
            blocker = "partition_unresolved_same_round_conflicts"
            unresolved_round_count = $unresolvedRounds.Count
            unresolved_rounds = $unresolvedRounds
            claim_boundary = "Live Gazebo/PX4 run was not started because the known-route partition still assigns conflicting same-round UAV targets."
        }
        $blockedManifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8
        $blockedManifest
        exit 14
    }
}

$waypointPacket = Get-Content -LiteralPath $WaypointJsonWin -Raw | ConvertFrom-Json
$boundary = $waypointPacket.boundary
$minX = Get-Number $boundary.min_x_m 0.0
$maxX = Get-Number $boundary.max_x_m 0.0
$minY = Get-Number $boundary.min_y_m 0.0
$maxY = Get-Number $boundary.max_y_m 0.0
$mapSizeX = [Math]::Max(1.0, $maxX - $minX)
$mapSizeY = [Math]::Max(1.0, $maxY - $minY)
$diffMapInitX = ($minX + $maxX) / 2.0
$diffMapInitY = ($minY + $maxY) / 2.0
$diffMapInitZ = $MapSizeZ / 2.0
$diffMapSizeX = $mapSizeX + (2.0 * $DiffMapPaddingM)
$diffMapSizeY = $mapSizeY + (2.0 * $DiffMapPaddingM)
$diffMapSizeZ = $MapSizeZ

$uav1ChainWin = Join-Path $PartitionDirWin "factory_l2_swarm_uav1_waypoints.json"
$uav2ChainWin = Join-Path $PartitionDirWin "factory_l2_swarm_uav2_waypoints.json"
$uav3ChainWin = Join-Path $PartitionDirWin "factory_l2_swarm_uav3_waypoints.json"
$fallback1 = @($RouteStartX, $RouteStartY, $TargetZ)
$fallback2 = @($RouteStartX, ($RouteStartY + 3.0), $TargetZ)
$fallback3 = @($RouteStartX, ($RouteStartY - 3.0), $TargetZ)
$uav1Start = Get-FirstWaypoint $uav1ChainWin $fallback1
$uav2Start = Get-FirstWaypoint $uav2ChainWin $fallback2
$uav3Start = Get-FirstWaypoint $uav3ChainWin $fallback3
if ($SpawnStartMode -eq "AcceptedSafe") {
    # Diagnostic-only startup layout: keep all three vehicles near a previously
    # accepted Factory indoor start so instance health can be separated from
    # partition-route terrain or local collision effects.
    $safeAnchorX = -10.575025
    $safeAnchorY = -19.363130
    $safeSpacing = [Math]::Max(2.0, [double]$AcceptedSafeSpacingM)
    if ($AcceptedSafeLayout -eq "XLine") {
        $uav1Start = @($safeAnchorX, $safeAnchorY, $TargetZ)
        $uav2Start = @(($safeAnchorX + $safeSpacing), $safeAnchorY, $TargetZ)
        $uav3Start = @(($safeAnchorX + (2.0 * $safeSpacing)), $safeAnchorY, $TargetZ)
    } else {
        $uav1Start = @($safeAnchorX, $safeAnchorY, $TargetZ)
        $uav2Start = @(($safeAnchorX + $safeSpacing), $safeAnchorY, $TargetZ)
        $uav3Start = @($safeAnchorX, ($safeAnchorY + $safeSpacing), $TargetZ)
    }
}

$effectiveUav1ChainWin = $uav1ChainWin
$effectiveUav2ChainWin = $uav2ChainWin
$effectiveUav3ChainWin = $uav3ChainWin
if ($UseNearStartSmokeTargets) {
    $effectiveUav1ChainWin = Join-Path $PartitionDirWin "factory_l2_swarm_uav1_near_start_smoke.json"
    $effectiveUav2ChainWin = Join-Path $PartitionDirWin "factory_l2_swarm_uav2_near_start_smoke.json"
    $effectiveUav3ChainWin = Join-Path $PartitionDirWin "factory_l2_swarm_uav3_near_start_smoke.json"
    Write-SingleWaypointChain $effectiveUav1ChainWin 1 @(([double]$uav1Start[0] + $NearStartSmokeDxM), [double]$uav1Start[1], $TargetZ) $boundary $WaypointJsonWin
    Write-SingleWaypointChain $effectiveUav2ChainWin 2 @(([double]$uav2Start[0] + $NearStartSmokeDxM), [double]$uav2Start[1], $TargetZ) $boundary $WaypointJsonWin
    Write-SingleWaypointChain $effectiveUav3ChainWin 3 @(([double]$uav3Start[0] + $NearStartSmokeDxM), [double]$uav3Start[1], $TargetZ) $boundary $WaypointJsonWin
} elseif ($PrependStartTransition) {
    $effectiveUav1ChainWin = Join-Path $PartitionDirWin "factory_l2_swarm_uav1_transition_waypoints.json"
    $effectiveUav2ChainWin = Join-Path $PartitionDirWin "factory_l2_swarm_uav2_transition_waypoints.json"
    $effectiveUav3ChainWin = Join-Path $PartitionDirWin "factory_l2_swarm_uav3_transition_waypoints.json"
    Write-TransitionWaypointChain $uav1ChainWin $effectiveUav1ChainWin 1 $uav1Start $StartTransitionStepM $StartTransitionMinDistanceM
    Write-TransitionWaypointChain $uav2ChainWin $effectiveUav2ChainWin 2 $uav2Start $StartTransitionStepM $StartTransitionMinDistanceM
    Write-TransitionWaypointChain $uav3ChainWin $effectiveUav3ChainWin 3 $uav3Start $StartTransitionStepM $StartTransitionMinDistanceM
}

$uav1InitialTarget = Get-FirstWaypoint $effectiveUav1ChainWin $fallback1
$uav2InitialTarget = Get-FirstWaypoint $effectiveUav2ChainWin $fallback2
$uav3InitialTarget = Get-FirstWaypoint $effectiveUav3ChainWin $fallback3

$openRvizValue = if ($WithRviz) { "true" } else { "false" }
$keepAliveValue = if ($KeepAlive -or $WithRviz) { "true" } else { "false" }
$sequentialSpawnValue = if ($SequentialSpawn) { "true" } else { "false" }
$c99PreloadedDefault = ($ControllerCoreProfile -eq "graphical_c99") -and (-not $SequentialSpawn)
$staggeredSpawnValue = if ($c99PreloadedDefault) { "false" } elseif ((-not $DisableStaggeredSpawn) -and (-not $SequentialSpawn)) { "true" } else { "false" }
$preloadGazeboModelsValue = if ($c99PreloadedDefault -or $PreloadGazeboModels) { "true" } else { "false" }

$dryManifest = [pscustomobject]@{
    schema = "mosim.factory_l2_diff_swarm_coverage_probe.v1"
    status = if ($DryRun) { "dry_run_planned" } else { "planned" }
    generated_at = (Get-Date).ToString("o")
    run_id = $RunId
    result_dir = $ResultDirWin
    startup_only = [bool]$StartupOnly
    uav_num = $UavNum
    source_waypoint_packet = $WaypointJsonWin
    partition_policy = $PartitionPolicy
    partition_start_index = $PartitionStartIndex
    spawn_start_mode = $SpawnStartMode
    accepted_safe_layout = $AcceptedSafeLayout
    accepted_safe_spacing_m = $AcceptedSafeSpacingM
    prepend_start_transition = [bool]$PrependStartTransition
    start_transition_step_m = $StartTransitionStepM
    start_transition_min_distance_m = $StartTransitionMinDistanceM
    near_start_smoke_targets = [bool]$UseNearStartSmokeTargets
    max_goals_per_uav = $MaxGoalsPerUav
    partition_window_goals_per_uav = $PartitionWindowGoalsPerUav
    target_stable_skip = [pscustomobject]@{
        radius_m = $TargetStableSkipRadiusM
        stable_s = $TargetStableSkipS
        max_speed_mps = $TargetStableSkipMaxSpeedMps
        max_vz_mps = $TargetStableSkipMaxVzMps
    }
    min_same_round_target_distance_m = $MinSameRoundTargetDistanceM
    diff_planner_target_mode = $DiffPlannerTargetMode
    diff_flight_type = $DiffFlightType
    takeoff_timeout_s = $TakeoffTimeoutS
    publish_hover_during_takeoff = [bool]$PublishHoverDuringTakeoff
    coverage_target_stop_ratio = $effectiveCoverageTargetStopRatio
    coverage_target_min_new_cells = $CoverageTargetMinNewCells
    uav_starts = [pscustomobject]@{
        uav1 = $uav1Start
        uav2 = $uav2Start
        uav3 = $uav3Start
    }
    initial_targets = [pscustomobject]@{
        uav1 = $uav1InitialTarget
        uav2 = $uav2InitialTarget
        uav3 = $uav3InitialTarget
    }
    chain_files = [pscustomobject]@{
        uav1 = $effectiveUav1ChainWin
        uav2 = $effectiveUav2ChainWin
        uav3 = $effectiveUav3ChainWin
    }
    diff_map_origin = [pscustomobject]@{ x = $diffMapInitX; y = $diffMapInitY; z = $diffMapInitZ }
    diff_map_size = [pscustomobject]@{ x = $diffMapSizeX; y = $diffMapSizeY; z = $diffMapSizeZ }
    claim_boundary = "Known-scene three-UAV target-chain map-building coverage attempt on Factory L2; not unknown autonomous task allocation."
}

if ($DryRun) {
    $dryManifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8
    $dryManifest
    exit 0
}

$livoxPluginWsWsl = if ($ControllerCoreProfile -eq "graphical_c99") {
    "$ProjectRootWsl/build/ros1/livox_swarm_ws_c99"
} else {
    "$ProjectRootWsl/Results/sunray_ros1/workspaces/sunray_livox_plugin_ws"
}
$livoxPluginFilenameWsl = "$livoxPluginWsWsl/devel/lib/liblivox_laser_simulation.so"
$livoxPluginWsEnv = if ($ControllerCoreProfile -eq "graphical_c99") { $livoxPluginWsWsl } else { $null }
$px4HoverPercentageEnv = if ($ControllerCoreProfile -eq "graphical_c99") { "0.456" } else { "0.37" }

$envParts = @(
    "RUN_ID=$RunId",
    "RESULT_DIR=$ResultDirWsl",
    "UAV_NUM=$UavNum",
    "PLANNER_VARIANT=diff_planner",
    "GOAL5_STARTUP_ONLY=$($StartupOnly.ToString().ToLowerInvariant())",
    "GOAL5_STARTUP_ATTEMPTS=$StartupAttempts",
    "SEQUENTIAL_SPAWN=$sequentialSpawnValue",
    "STAGGERED_SPAWN=$staggeredSpawnValue",
    "STAGGERED_SPAWN_INTERVAL_S=$StaggeredSpawnIntervalS",
    "PRELOAD_GAZEBO_MODELS=$preloadGazeboModelsValue",
    "PX4CTRL_CORE_PROFILE=$ControllerCoreProfile",
    "PX4CTRL_HOVER_PERCENTAGE=$px4HoverPercentageEnv",
    "PX4CTRL_EKF2_EV_CTRL_OVERRIDE=$Px4Ekf2EvCtrlOverride",
    "PX4CTRL_EKF2_HGT_REF_OVERRIDE=$Px4Ekf2HgtRefOverride",
    "PX4CTRL_EXTRA_PARAM_OVERRIDES=$Px4ExtraParamOverrides",
    "PX4CTRL_SKIP_PARAM_SNAPSHOT=$($SkipPx4ParamSnapshot.ToString().ToLowerInvariant())",
    "GUI=false",
    "OPEN_RVIZ=$openRvizValue",
    "KEEP_ALIVE=$keepAliveValue",
    "WORLD_FILE=$FactoryWorldWsl",
    "FACTORY_MODEL_PATH=$FactoryModelPathWsl",
    "SUNRAY_GAZEBO_LAUNCH_FILE=$ProjectRootWsl/Scripts/sunray/factory_l2_sunray_px4_gazebo.launch",
    "SUNRAY_STRIP_PX4_MODEL_PATH=true",
    "SUNRAY_MID360_PLUGIN_DOWNSAMPLE=4",
    "SUNRAY_LIVOX_PLUGIN_FILENAME=$livoxPluginFilenameWsl",
    "LIVOX_PLUGIN_WS=$livoxPluginWsEnv",
    "SUNRAY_MID360_CSV_FILE_NAME=mid360-real-centr.csv",
    "SUNRAY_MID360_GOAL5_CSV_STRIDE=4",
    "START1_X=$($uav1Start[0])",
    "START1_Y=$($uav1Start[1])",
    "START2_X=$($uav2Start[0])",
    "START2_Y=$($uav2Start[1])",
    "START3_X=$($uav3Start[0])",
    "START3_Y=$($uav3Start[1])",
    "TARGET1_X=$($uav1InitialTarget[0])",
    "TARGET1_Y=$($uav1InitialTarget[1])",
    "TARGET1_Z=$TargetZ",
    "TARGET2_X=$($uav2InitialTarget[0])",
    "TARGET2_Y=$($uav2InitialTarget[1])",
    "TARGET2_Z=$TargetZ",
    "TARGET3_X=$($uav3InitialTarget[0])",
    "TARGET3_Y=$($uav3InitialTarget[1])",
    "TARGET3_Z=$TargetZ",
    "TARGET1_CHAIN_FILE=$($effectiveUav1ChainWin.Replace($ProjectRootWin, $ProjectRootWsl).Replace('\', '/'))",
    "TARGET2_CHAIN_FILE=$($effectiveUav2ChainWin.Replace($ProjectRootWin, $ProjectRootWsl).Replace('\', '/'))",
    "TARGET3_CHAIN_FILE=$($effectiveUav3ChainWin.Replace($ProjectRootWin, $ProjectRootWsl).Replace('\', '/'))",
    "TARGET_CHAIN_MAX_GOALS=0",
    "TARGET_CHAIN_GOAL_TIMEOUT_S=$TargetChainGoalTimeoutS",
    "EGO_GATE_TARGET_STABLE_SKIP_RADIUS_M=$TargetStableSkipRadiusM",
    "EGO_GATE_TARGET_STABLE_SKIP_S=$TargetStableSkipS",
    "EGO_GATE_TARGET_STABLE_SKIP_MAX_SPEED_MPS=$TargetStableSkipMaxSpeedMps",
    "EGO_GATE_TARGET_STABLE_SKIP_MAX_VZ_MPS=$TargetStableSkipMaxVzMps",
    "DIFF_GOAL5_PLANNER_TARGET_MODE=$DiffPlannerTargetMode",
    "DIFF_GOAL5_FLIGHT_TYPE=$DiffFlightType",
    "DIFF_GOAL5_GRID_INIT_X=$diffMapInitX",
    "DIFF_GOAL5_GRID_INIT_Y=$diffMapInitY",
    "DIFF_GOAL5_GRID_INIT_Z=$diffMapInitZ",
    "DIFF_GOAL5_MAP_SIZE_X=$diffMapSizeX",
    "DIFF_GOAL5_MAP_SIZE_Y=$diffMapSizeY",
    "DIFF_GOAL5_MAP_SIZE_Z=$diffMapSizeZ",
    "DIFF_GOAL5_LOCAL_UPDATE_RANGE_X=$PlannerLocalUpdateRangeXYM",
    "DIFF_GOAL5_LOCAL_UPDATE_RANGE_Y=$PlannerLocalUpdateRangeXYM",
    "DIFF_GOAL5_LOCAL_UPDATE_RANGE_Z=$PlannerLocalUpdateRangeZM",
    "EGO_MAX_VEL=$PlannerMaxVelMps",
    "EGO_MAX_ACC=$PlannerMaxAccMps2",
    "EGO_MAX_JERK=4.0",
    "EGO_PLANNING_HORIZON=7.0",
    "EGO_GRID_RESOLUTION=0.20",
    "EGO_OBSTACLES_INFLATION=0.25",
    "EGO_OBSTACLE_CLEARANCE=0.25",
    "EGO_OBSTACLE_CLEARANCE_SOFT=0.45",
    "EGO_VIRTUAL_CEIL_HEIGHT=$VirtualCeilHeight",
    "EGO_VIRTUAL_GROUND_HEIGHT=0.05",
    "EGO_VISUALIZATION_TRUNCATE_HEIGHT=$ReviewMaxZ",
    "EGO_CMD_SAFETY_ENABLE=true",
    "EGO_CMD_INVALID_Z_POLICY=clamp",
    "EGO_CMD_SAFETY_MIN_Z=$CommandMinZ",
    "EGO_CMD_SAFETY_MAX_Z=$CommandMaxZ",
    "EGO_CMD_SAFETY_MAX_POSITION_JUMP_M=0.80",
    "EGO_CMD_SAFETY_MAX_POSITION_JUMP_SPEED_MPS=0.0",
    "EGO_GATE_TAKEOFF_HEIGHT=$TargetZ",
    "EGO_GATE_TAKEOFF_LAND_SPEED=$TakeoffLandSpeedMps",
    "EGO_GATE_TAKEOFF_TIMEOUT_S=$TakeoffTimeoutS",
    "EGO_GATE_TAKEOFF_UAV_STAGGER_S=$TakeoffUavStaggerS",
    "EGO_GATE_TAKEOFF_RETRY_REPEATS=$TakeoffRetryRepeats",
    "EGO_GATE_TAKEOFF_RETRY_MAX=$TakeoffRetryMax",
    "EGO_GATE_PUBLISH_HOVER_DURING_TAKEOFF=$($PublishHoverDuringTakeoff.ToString().ToLowerInvariant())",
    "EGO_GATE_EGO_TAKEOVER_TIMEOUT_S=120",
    "EGO_GATE_EXECUTE_TIMEOUT_S=$RuntimeTimeoutS",
    "EGO_GATE_LAND_TIMEOUT_S=60",
    "EGO_GATE_PRE_LAND_HOVER_S=1.5",
    "EGO_GATE_PRE_LAND_NO_CMD_S=4.0",
    "EGO_GATE_LANDED_Z_MAX=0.40",
    "EGO_GATE_TARGET_HOLD_MAX_SPEED_MPS=0.45",
    "EGO_GATE_TARGET_HOLD_MAX_VZ_MPS=0.25",
    "EGO_GATE_MIN_OCCUPANCY_COUNT=2",
    "EGO_GATE_MIN_OCCUPANCY_POINTS=0",
    "MAVROS_READY_TIMEOUT_S=240",
    "ODOM_BRIDGE_READY_TIMEOUT_S=$OdomReadyTimeoutS",
    "LIDAR_READY_TIMEOUT_S=120",
    "POINTCLOUD_MIN_WORLD_Z_M=-0.2",
    "POINTCLOUD_MAX_WORLD_Z_M=$ReviewMaxZ",
    "TOTAL_TIMEOUT_S=$RuntimeTimeoutS"
)

$preflight = if ($SkipPreflight) {
    "echo skipped > '$ResultDirWsl/preflight_skipped.txt'"
} else {
    "bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh > '$ResultDirWsl/preflight.log' 2>&1"
}

$bashStatus = '$?'
$bashScriptWin = Join-Path $ResultDirWin "start_factory_diff_swarm_coverage_probe.sh"
$bashScriptWsl = $ResultDirWsl + "/start_factory_diff_swarm_coverage_probe.sh"
$runnerScript = if ($ControllerCoreProfile -eq "graphical_c99") {
    "Scripts/sunray/run_c99_multiuav_planner_gate.sh"
} else {
    "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh"
}
$runnerCommand = "$($envParts -join " " ) bash $runnerScript > '$ResultDirWsl/background_launcher.log' 2>&1"
$runtimeBlock = if ($WithRviz) {
@"
$runnerCommand &
runner_pid=`$!
echo "`$runner_pid" > '$ResultDirWsl/background_runner.pid'

source /opt/ros/noetic/setup.bash
for _ in `$(seq 1 300); do
  if rostopic list 2>/dev/null | grep -q '/mosim/goal5/uav1/truth_path'; then
    break
  fi
  if ! kill -0 "`$runner_pid" 2>/dev/null; then
    break
  fi
  sleep 1
done

if kill -0 "`$runner_pid" 2>/dev/null && rostopic list 2>/dev/null | grep -q '/mosim/goal5/uav1/truth_path'; then
  for uid in 1 2 3; do
    python3 Scripts/ros/accumulate_pointcloud_review.py \
      --input-topic "/uav`$`{uid`}/livox_world" \
      --output-topic "/mosim/goal5/uav`$`{uid`}/livox_world_accumulated" \
      --frame-id world \
      --voxel-size-m 0.08 \
      --min-z -0.2 \
      --max-z $ReviewMaxZ \
      --max-accumulated-points 0 \
      --publish-rate-hz 2 \
      --max-runtime-s 0 \
      --output-json "$ResultDirWsl/uav`$`{uid`}_pointcloud_accumulated_review.json" \
      > "$ResultDirWsl/uav`$`{uid`}_pointcloud_accumulated_review.log" 2>&1 &
    echo `$! > "$ResultDirWsl/uav`$`{uid`}_pointcloud_accumulated_review.pid"

    python3 Scripts/ros/accumulate_pointcloud_review.py \
      --input-topic "/uav`$`{uid`}/livox_world" \
      --output-topic "/mosim/goal5/uav`$`{uid`}/occupancy_accumulated" \
      --frame-id world \
      --voxel-size-m 0.20 \
      --min-z -0.2 \
      --max-z $ReviewMaxZ \
      --max-accumulated-points 0 \
      --publish-rate-hz 2 \
      --max-runtime-s 0 \
      --output-json "$ResultDirWsl/uav`$`{uid`}_occupancy_accumulated_review.json" \
      > "$ResultDirWsl/uav`$`{uid`}_occupancy_accumulated_review.log" 2>&1 &
    echo `$! > "$ResultDirWsl/uav`$`{uid`}_occupancy_accumulated_review.pid"
  done

  python3 Scripts/sunray/swarm_body_axes_marker_node.py \
    --uav-num 3 \
    --marker-topic /mosim/goal5/body_axes \
    --axis-length-m 0.60 \
    --shaft-m 0.035 \
    --head-diameter-m 0.10 \
    --head-length-m 0.14 \
    > '$ResultDirWsl/swarm_body_axes_marker.log' 2>&1 &
  echo `$! > '$ResultDirWsl/swarm_body_axes_marker.pid'

  rviz -d '$ProjectRootWsl/Config/rviz/sunray_ros1_goal5_diff_swarm_pointcloud_review.rviz' \
    > '$ResultDirWsl/rviz_diff_swarm_pointcloud_review.log' 2>&1 &
  echo `$! > '$ResultDirWsl/rviz_diff_swarm_pointcloud_review.pid'
  sleep 1
  rviz -d '$ProjectRootWsl/Config/rviz/sunray_ros1_goal5_diff_swarm_grid3d_review.rviz' \
    > '$ResultDirWsl/rviz_diff_swarm_grid3d_review.log' 2>&1 &
  echo `$! > '$ResultDirWsl/rviz_diff_swarm_grid3d_review.pid'
else
  echo 'review topics did not become ready' > '$ResultDirWsl/rviz_review_start_blocker.txt'
fi

wait "`$runner_pid"
runner_exit=$bashStatus
"@
} else {
@"
$runnerCommand
runner_exit=$bashStatus
"@
}
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
$runtimeBlock
echo "`$runner_exit" > '$ResultDirWsl/background_exit_code.txt'
date --iso-8601=seconds > '$ResultDirWsl/swarm_coverage_end.txt'
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
    $rawExit = (Get-Content -LiteralPath $exitPath -Raw).Trim()
    if ($rawExit -match "^-?\d+$") { $backendExit = [int]$rawExit }
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
$coverageRatio = $null
if (Test-Path -LiteralPath $coveragePacketPath) {
    $coveragePacket = Get-Content -LiteralPath $coveragePacketPath -Raw | ConvertFrom-Json
    $coverageStatus = [string]$coveragePacket.status
    $coverageRatio = $coveragePacket.acceptance.merged_sensor_footprint_coverage_ratio
}
$metricsPath = Join-Path $ResultDirWin "EGO_SWARM_METRICS.json"
$metricsStatus = "missing"
$metricsBlockerCount = $null
if (Test-Path -LiteralPath $metricsPath) {
    $metrics = Get-Content -LiteralPath $metricsPath -Raw | ConvertFrom-Json
    $metricsStatus = [string]$metrics.status
    $metricsBlockerCount = @($metrics.blockers).Count
}
$chainPath = Join-Path $ResultDirWin "SWARM_TARGET_CHAIN_PROBE.json"
$chainStatus = "missing"
$chainBlockerCount = $null
if (Test-Path -LiteralPath $chainPath) {
    $chain = Get-Content -LiteralPath $chainPath -Raw | ConvertFrom-Json
    $chainStatus = [string]$chain.status
    $chainBlockerCount = @($chain.blockers).Count
}

$isPartialGoalProbe = ($MaxGoalsPerUav -gt 0)
$manifestStatus = if ($StartupOnly -and $backendExit -eq 0) {
    "passed_startup_only"
} elseif ($StartupOnly) {
    "blocked_startup_only"
} elseif ($chainStatus -eq "passed" -and $metricsStatus -eq "passed" -and $isPartialGoalProbe) {
    "review_required_partial_swarm_chain_passed"
} elseif ($chainStatus -eq "passed" -and $metricsStatus -eq "passed" -and $coverageStatus -eq "passed") {
    "passed"
} elseif ($chainStatus -eq "passed" -and $metricsStatus -eq "passed") {
    "review_required_swarm_chain_passed_coverage_below_threshold"
} else {
    "blocked_backend_or_swarm_chain_failed"
}

$manifest = [pscustomobject]@{
    schema = "mosim.factory_l2_diff_swarm_coverage_probe.v1"
    status = $manifestStatus
    generated_at = (Get-Date).ToString("o")
    run_id = $RunId
    result_dir = $ResultDirWin
    backend_exit_code = $backendExit
    startup_only = [bool]$StartupOnly
    uav_num = $UavNum
    metrics_status = $metricsStatus
    metrics_blocker_count = $metricsBlockerCount
    chain_status = $chainStatus
    chain_blocker_count = $chainBlockerCount
    coverage_status = $coverageStatus
    merged_sensor_footprint_coverage_ratio = $coverageRatio
    is_partial_goal_probe = $isPartialGoalProbe
    source_waypoint_packet = $WaypointJsonWin
    spawn_start_mode = $SpawnStartMode
    accepted_safe_layout = $AcceptedSafeLayout
    accepted_safe_spacing_m = $AcceptedSafeSpacingM
    prepend_start_transition = [bool]$PrependStartTransition
    start_transition_step_m = $StartTransitionStepM
    start_transition_min_distance_m = $StartTransitionMinDistanceM
    takeoff_timeout_s = $TakeoffTimeoutS
    publish_hover_during_takeoff = [bool]$PublishHoverDuringTakeoff
    partition_summary = (Join-Path $PartitionDirWin "factory_l2_swarm_partition_summary.json")
    coverage_packet = $coveragePacketPath
    uav_starts = [pscustomobject]@{
        uav1 = $uav1Start
        uav2 = $uav2Start
        uav3 = $uav3Start
    }
    initial_targets = [pscustomobject]@{
        uav1 = $uav1InitialTarget
        uav2 = $uav2InitialTarget
        uav3 = $uav3InitialTarget
    }
    near_start_smoke_targets = [bool]$UseNearStartSmokeTargets
    claim_boundary = if ($StartupOnly) { "Startup-only Factory L2 multi-UAV gate; no planner, mission, coverage, or RViz success is claimed." } else { "Known-scene three-UAV target-chain map-building coverage attempt on Factory L2; backend metrics and coverage packet are the evidence surface." }
}
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8
$manifest
exit $backendExit
