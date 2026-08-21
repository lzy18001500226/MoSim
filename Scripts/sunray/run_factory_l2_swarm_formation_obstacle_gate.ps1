param(
    [string]$RunId = ("factory_l2_swarm_formation_obstacle_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    # r8 reached five center-chain waypoints safely but used about 847 s of
    # wall time before the sixth. This is only the outer lifecycle watchdog;
    # the per-goal, motion, clearance, and emergency gates remain unchanged.
    [int]$TotalTimeoutS = 2400,
    [ValidateSet("leader_follower", "native_per_uav")]
    [string]$CommandMode = "leader_follower",
    [ValidateSet("r6_baseline_v1", "conservative_v1")]
    [string]$DynamicsProfile = "conservative_v1",
    # C99 and the accepted original formation run both complete takeoff before
    # the mission starts publishing the final hover command. Keep the
    # historical early-publish behavior opt-in for diagnosis only.
    [switch]$PublishHoverDuringTakeoff,
    [switch]$KeepAlive,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$Root = "C:\Users\HP\Desktop\MoSim"
$RootWsl = "/mnt/c/Users/HP/Desktop/MoSim"
$ScenarioPath = Join-Path $Root "Config\scenarios\formation\factory_l2_three_uav_obstacle_crossing.json"
$ResultDir = Join-Path $Root ("Results\sunray_ros1\" + $RunId)
$ResultDirWsl = $RootWsl + "/Results/sunray_ros1/" + $RunId

python (Join-Path $Root "Scripts\sunray\build_factory_l2_formation_obstacle_scenario.py")
if ($LASTEXITCODE -ne 0) {
    throw "Unable to generate a rigid-formation-safe obstacle-crossing scenario. The previous scenario file will not be reused."
}
$scenario = Get-Content -Raw -LiteralPath $ScenarioPath | ConvertFrom-Json
$rigidPath = $scenario.rigid_center_path_contract
if ($null -eq $rigidPath -or $rigidPath.status -ne "passed") {
    throw "The generated scenario does not contain a passed rigid-center path contract."
}
$plannerObstacleClearanceM = [double]$rigidPath.clearance_margin_m
if ($plannerObstacleClearanceM -le 0.0) {
    throw "The passed rigid-center path contract must provide a positive clearance_margin_m."
}
# The post-flight gate remains at the scenario's 1.70 m AABB-clearance
# contract.  r62 passed all mission and formation gates but UAV1 reached only
# 1.6156 m on that axis-aligned metric, so add one full 0.20 m grid cell to
# the live planner inflation instead of weakening the evidence threshold.
$runtimePlannerObstacleInflationM = [math]::Round($plannerObstacleClearanceM + 0.20, 2)
$runtimeContract = $scenario.runtime_contract
if ($null -eq $runtimeContract) {
    throw "The generated scenario is missing runtime_contract. Regenerate it with build_factory_l2_formation_obstacle_scenario.py."
}
$swarmTrajectoryReceiverTimeToleranceS = [double]$runtimeContract.swarm_trajectory_receiver_time_tolerance_s
$r52ObservedMaxReceiveAgeS = [double]$runtimeContract.r52_observed_max_receive_age_s
$receiverAgeSafetyMarginS = [double]$runtimeContract.receiver_age_safety_margin_s
if ($swarmTrajectoryReceiverTimeToleranceS -le 0 -or $r52ObservedMaxReceiveAgeS -le 0 -or $receiverAgeSafetyMarginS -le 0) {
    throw "The Factory L2 trajectory receiver timing contract must contain positive tolerance, observed age and safety margin."
}
$missionTargetContract = $scenario.mission_target_contract
if ($null -eq $missionTargetContract) {
    throw "The generated scenario is missing mission_target_contract. Regenerate it with build_factory_l2_formation_obstacle_scenario.py."
}
$targetReachedRadiusM = [double]$missionTargetContract.target_reached_radius_m
$targetHoldS = [double]$missionTargetContract.target_hold_s
if ($targetReachedRadiusM -le 0.0 -or $targetHoldS -le 0.0) {
    throw "The Factory L2 mission target contract must provide positive target_reached_radius_m and target_hold_s."
}
$formation = $scenario.formation
$start = $formation.start_positions_xy_m
$center = $formation.target_center_xy_m
$relative = $formation.relative_positions_unit
$mapSizeX = 64.0
$mapSizeY = 64.0
$mapSizeZ = 3.0
$mapOriginX = [double]$center[0] - ($mapSizeX / 2.0)
$mapOriginY = [double]$center[1] - ($mapSizeY / 2.0)
$dynamicsProfiles = @{
    "r6_baseline_v1" = [ordered]@{
        ego_max_vel_mps = 0.80
        ego_max_acc_mps2 = 0.80
        command_speed_mps = 0.60
        command_acceleration_mps2 = 0.40
        command_lateral_acceleration_mps2 = 0.40
        command_jerk_mps3 = 2.00
        predictive_braking_deceleration_mps2 = 1.20
    }
    "conservative_v1" = [ordered]@{
        ego_max_vel_mps = 0.45
        ego_max_acc_mps2 = 0.35
        command_speed_mps = 0.35
        command_acceleration_mps2 = 0.25
        command_lateral_acceleration_mps2 = 0.25
        command_jerk_mps3 = 0.75
        predictive_braking_deceleration_mps2 = 0.25
    }
}
$dynamics = $dynamicsProfiles[$DynamicsProfile]
if ($null -eq $dynamics) {
    throw "Unknown DynamicsProfile: $DynamicsProfile"
}
if ($null -eq $relative) {
    throw "Formation scenario is missing relative_positions_unit. Regenerate it with build_factory_l2_formation_obstacle_scenario.py."
}
New-Item -ItemType Directory -Force -Path $ResultDir | Out-Null

# The upstream Swarm-Formation planner consumes one global center target. The
# member chains below are only synchronized acceptance targets; publishing them
# to the shared topic would collapse the formation semantics.
$centerWaypoints = @($rigidPath.center_waypoints_xy_m)
if ($centerWaypoints.Count -lt 2) {
    throw "The passed rigid-center path must contain a spawn point plus at least one traversal waypoint."
}
$startCenter = @([double]($formation.start_center_xy_m[0]), [double]($formation.start_center_xy_m[1]))
$firstCenter = $centerWaypoints[0]
if ($null -eq $firstCenter -or $firstCenter.Count -lt 2 -or
    [math]::Abs([double]($firstCenter[0]) - $startCenter[0]) -gt 0.001 -or
    [math]::Abs([double]($firstCenter[1]) - $startCenter[1]) -gt 0.001) {
    throw "The rigid-center path first waypoint must match formation.start_center_xy_m before it can be skipped."
}
$formationCenterWaypoints = @()
for ($index = 1; $index -lt $centerWaypoints.Count; $index++) {
    $point = $centerWaypoints[$index]
    if ($null -eq $point -or $point.Count -lt 2) {
        throw "The rigid-center path contains an invalid traversal waypoint at index $index."
    }
    $formationCenterWaypoints += ,@([double]($point[0]), [double]($point[1]), [double]$formation.z_m)
}
if ($formationCenterWaypoints.Count -eq 0) {
    throw "The rigid-center path has no traversal waypoint after the spawn point."
}

$formationCenterChainPath = Join-Path $ResultDir "formation_center_chain.json"
$formationCenterChainWsl = "$ResultDirWsl/formation_center_chain.json"
$formationCenterPayload = [ordered]@{
    schema = "mosim.factory_l2_swarm_formation_center_chain.v1"
    target_transport = "single_global_formation_center"
    source = "rigid_center_path_contract.center_waypoints_xy_m"
    skipped_spawn_waypoint = $true
    source_center_waypoint_count = $centerWaypoints.Count
    waypoints = $formationCenterWaypoints
}
$formationCenterPayload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $formationCenterChainPath -Encoding utf8

$memberChainPaths = @{}
$memberChainPathsWsl = @{}
$memberOffsets = @{}
foreach ($uid in 1..3) {
    $offset = $relative.PSObject.Properties[[string]$uid].Value
    if ($null -eq $offset -or $offset.Count -lt 2) {
        throw "Formation scenario is missing a two-dimensional relative offset for UAV$uid."
    }
    $offsetScale = [double]($formation.scale)
    $offsetX = [double]($offset[0])
    $offsetY = [double]($offset[1])
    $offsetXY = @(
        ($offsetX * $offsetScale),
        ($offsetY * $offsetScale)
    )
    $memberOffsets[$uid] = $offsetXY
    $memberWaypoints = @()
    foreach ($centerWaypoint in $formationCenterWaypoints) {
        $memberX = [double]($centerWaypoint[0]) + [double]($offsetXY[0])
        $memberY = [double]($centerWaypoint[1]) + [double]($offsetXY[1])
        $memberZ = [double]($centerWaypoint[2])
        $memberWaypoints += ,@($memberX, $memberY, $memberZ)
    }
    $memberChainPath = Join-Path $ResultDir ("uav{0}_formation_acceptance_chain.json" -f $uid)
    $memberChainPayload = [ordered]@{
        schema = "mosim.factory_l2_swarm_formation_member_acceptance_chain.v1"
        uav_id = $uid
        target_transport = "acceptance_only_member_target_chain"
        formation_center_chain_file = $formationCenterChainWsl
        relative_offset_xy_m = $offsetXY
        waypoints = $memberWaypoints
    }
    $memberChainPayload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $memberChainPath -Encoding utf8
    $memberChainPaths[$uid] = $memberChainPath
    $memberChainPathsWsl[$uid] = "$ResultDirWsl/uav$($uid)_formation_acceptance_chain.json"
}
$leaderFollowerCommands = $CommandMode -eq "leader_follower"
$rigidLeaderFollowerMode = $leaderFollowerCommands
$plannerCommandProducerUavIds = [System.Collections.ArrayList]::new()
if ($leaderFollowerCommands) {
    [void]$plannerCommandProducerUavIds.Add(1)
} else {
    foreach ($uid in 1..3) {
        [void]$plannerCommandProducerUavIds.Add($uid)
    }
}
$followerFinalCommandSource = if ($leaderFollowerCommands) {
    "uav1_position_cmd_plus_spawn_relative_offset"
} else {
    "per_uav_planner_position_cmd"
}

$environment = @(
    "RUN_ID=$RunId",
    "RESULT_DIR=$ResultDirWsl",
    "DISABLE_ROS1_EOL_WARNINGS=1",
    "PLANNER_VARIANT=swarm_formation",
    "PX4CTRL_CORE_PROFILE=graphical_c99",
    "PX4CTRL_HOVER_PERCENTAGE=0.456",
    "EGO_GATE_TAKEOFF_LAND_SPEED=0.12",
    "UAV_NUM=3",
    "KEEP_ALIVE=$($KeepAlive.IsPresent.ToString().ToLowerInvariant())",
    "WORLD_FILE=$RootWsl/Config/gazebo/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf",
    "FACTORY_L2_MODEL_PATH=$RootWsl/Config/gazebo/models",
    "SUNRAY_GAZEBO_LAUNCH_FILE=$RootWsl/Scripts/sunray/factory_l2_sunray_px4_gazebo.launch",
    # The C99 route uses a preloaded world so every UAV retains its Livox
    # sensor plugin. Dynamic staggered spawn remains available through the
    # lower-level diagnostic gate, but is not the formation default.
    "PRELOAD_GAZEBO_MODELS=true",
    "STAGGERED_SPAWN=false",
    "STAGGERED_SPAWN_INTERVAL_S=12",
    "GOAL5_STARTUP_ATTEMPTS=1",
    "MAVROS_READY_TIMEOUT_S=150",
    "START1_X=$($start.'1'[0])", "START1_Y=$($start.'1'[1])",
    "START2_X=$($start.'2'[0])", "START2_Y=$($start.'2'[1])",
    "START3_X=$($start.'3'[0])", "START3_Y=$($start.'3'[1])",
    "TARGET1_CHAIN_FILE=$($memberChainPathsWsl[1])",
    "TARGET2_CHAIN_FILE=$($memberChainPathsWsl[2])",
    "TARGET3_CHAIN_FILE=$($memberChainPathsWsl[3])",
    "FORMATION_CENTER_CHAIN_FILE=$formationCenterChainWsl",
    "TARGET_CHAIN_MAX_GOALS=0",
    "TARGET_CHAIN_GOAL_TIMEOUT_S=120",
    "TARGET_CHAIN_GOAL_WALL_TIMEOUT_S=900",
    "EGO_GATE_TARGET_REACHED_RADIUS_M=$targetReachedRadiusM",
    "EGO_GATE_TARGET_HOLD_S=$targetHoldS",
    "EGO_GATE_TARGET_STABLE_SKIP_RADIUS_M=0.0",
    "SWARM_FORMATION_D3_CENTER_X=$($center[0])",
    "SWARM_FORMATION_D3_CENTER_Y=$($center[1])",
    "SWARM_FORMATION_D3_CENTER_Z=$($formation.z_m)",
    "SWARM_FORMATION_D3_RELATIVE_Z=0.0",
    "SWARM_FORMATION_D3_SWARM_SCALE=$($formation.scale)",
    "SWARM_FORMATION_D3_RELATIVE_POS_0_X=$($relative.'1'[0])",
    "SWARM_FORMATION_D3_RELATIVE_POS_0_Y=$($relative.'1'[1])",
    "SWARM_FORMATION_D3_RELATIVE_POS_1_X=$($relative.'2'[0])",
    "SWARM_FORMATION_D3_RELATIVE_POS_1_Y=$($relative.'2'[1])",
    "SWARM_FORMATION_D3_RELATIVE_POS_2_X=$($relative.'3'[0])",
    "SWARM_FORMATION_D3_RELATIVE_POS_2_Y=$($relative.'3'[1])",
    "SWARM_FORMATION_D3_MAP_SIZE_X=$mapSizeX",
    "SWARM_FORMATION_D3_MAP_SIZE_Y=$mapSizeY",
    "SWARM_FORMATION_D3_MAP_SIZE_Z=$mapSizeZ",
    "SWARM_FORMATION_D3_USE_MAP_ORIGIN_OVERRIDE=true",
    "SWARM_FORMATION_D3_MAP_ORIGIN_X=$mapOriginX",
    "SWARM_FORMATION_D3_MAP_ORIGIN_Y=$mapOriginY",
    "SWARM_FORMATION_D3_GRID_RESOLUTION=0.20",
    "SWARM_FORMATION_D3_LOCAL_UPDATE_RANGE_XY=8.0",
    # r62 reached every target but passed the container with only 1.6156 m of
    # axis-aligned post-flight clearance. Increase live map inflation by one
    # 0.20 m grid cell while the independent post-flight gate remains 1.70 m.
    "SWARM_FORMATION_D3_OBSTACLES_INFLATION=$runtimePlannerObstacleInflationM",
    # A wide rigid footprint can need a longer one-shot initialization search.
    # This does not change the collision or flight-safety gates.
    "SWARM_FORMATION_D3_ASTAR_SEARCH_TIMEOUT_S=1.00",
    "SWARM_FORMATION_D3_ASTAR_PLANAR_SEARCH=true",
    "SWARM_FORMATION_D3_SWARM_TRAJ_TIME_TOLERANCE_S=$swarmTrajectoryReceiverTimeToleranceS",
    "SWARM_FORMATION_D3_LEADER_FOLLOWER_COMMANDS=$($leaderFollowerCommands.ToString().ToLowerInvariant())",
    "SWARM_FORMATION_D3_RIGID_LEADER_FOLLOWER_MODE=$($rigidLeaderFollowerMode.ToString().ToLowerInvariant())",
    "SWARM_POINTCLOUD_PEER_FILTER_RADIUS_XY_M=0.45",
    "SWARM_POINTCLOUD_PEER_FILTER_Z_MIN_M=-0.30",
    "SWARM_POINTCLOUD_PEER_FILTER_Z_MAX_M=0.30",
    "SWARM_POINTCLOUD_PEER_ODOM_MAX_AGE_S=0.50",
    # Keep low floor returns out of the live inflated occupancy field.
    "POINTCLOUD_MIN_WORLD_Z_M=0.50",
    "SWARM_FORMATION_D3_RELAY_RETIME_FUTURE_S=0.0",
    "SWARM_FORMATION_D3_MIN_TRAJ_Z=0.90",
    "SWARM_FORMATION_D3_MAX_TRAJ_Z=1.35",
    "SWARM_FORMATION_D3_VIRTUAL_CEIL_HEIGHT=1.45",
    "SWARM_FORMATION_D3_WEIGHT_HEIGHT=50000.0",
    "EGO_MAX_VEL=$($dynamics['ego_max_vel_mps'])",
    "EGO_MAX_ACC=$($dynamics['ego_max_acc_mps2'])",
    "EGO_PLANNING_HORIZON=8.0",
    "EGO_GATE_MIN_INTER_UAV_DISTANCE=1.0",
    "EGO_GATE_INTER_UAV_EMERGENCY_HOLD_ENABLE=true",
    "EGO_GATE_INTER_UAV_EMERGENCY_DECELERATION_MPS2=$($dynamics['predictive_braking_deceleration_mps2'])",
    # r54 proved that the generic 0.20 m predictive buffer trips at nominal
    # formation spacing although the 1.0 m hard separation gate is satisfied.
    # Keep the hard gate and braking prediction enabled; narrow only this
    # scenario's extra buffer to the evidence-backed 0.10 m value.
    "EGO_GATE_INTER_UAV_EMERGENCY_MARGIN_M=0.10",
    "EGO_GATE_INTER_UAV_EMERGENCY_MIN_CLOSING_SPEED_MPS=0.05",
    "EGO_GATE_TAKEOFF_HEIGHT=1.0",
    # px4ctrl changes from AUTO_TAKEOFF to AUTO_HOVER after the target height.
    # Do not publish the final mission hover command before that transition;
    # this matches the passing C99 single-aircraft and original formation
    # contracts. The switch above keeps the old behavior available for a
    # controlled comparison.
    "EGO_GATE_PUBLISH_HOVER_DURING_TAKEOFF=$($PublishHoverDuringTakeoff.ToString().ToLowerInvariant())",
    "EGO_GATE_EXECUTE_TIMEOUT_S=420",
    "EGO_GATE_EXECUTE_WALL_TIMEOUT_S=900",
    "EGO_GATE_EGO_TAKEOVER_TIMEOUT_S=120",
    "EGO_GATE_TAKEOFF_WALL_TIMEOUT_S=300",
    "EGO_GATE_LAND_WALL_TIMEOUT_S=300",
    "EGO_CMD_SAFETY_MIN_Z=0.90",
    "EGO_CMD_SAFETY_MAX_Z=1.35",
    "EGO_CMD_SAFETY_MOTION_TIME_BASIS=ros_sim_time",
    "EGO_CMD_SAFETY_SMOOTHING_MAX_SPEED_MPS=$($dynamics['command_speed_mps'])",
    "EGO_CMD_SAFETY_RECOMPUTE_VELOCITY_FROM_POSITION=true",
    "EGO_CMD_SAFETY_MAX_VELOCITY_MPS=$($dynamics['command_speed_mps'])",
    "EGO_CMD_SAFETY_MAX_ACCELERATION_MPS2=$($dynamics['command_acceleration_mps2'])",
    "EGO_CMD_SAFETY_MAX_LATERAL_ACCELERATION_MPS2=$($dynamics['command_lateral_acceleration_mps2'])",
    "EGO_CMD_SAFETY_MAX_JERK_MPS3=$($dynamics['command_jerk_mps3'])",
    "TOTAL_TIMEOUT_S=$TotalTimeoutS"
)

# Route the Factory C99 gate through the source-local multi-UAV wrapper. That
# wrapper resolves PX4CTRL_WS, planner workspaces, the Livox plugin workspace,
# and the generated runtime overlay under build/ros1 before starting the
# shared mission gate. Calling the shared gate directly would fall back to
# historical Results workspaces when those variables are not supplied.
$command = "cd $RootWsl && env " + ($environment -join " ") + " bash Scripts/sunray/run_c99_multiuav_planner_gate.sh"
$manifest = [pscustomobject]@{
    schema = "mosim.factory_l2_swarm_formation_obstacle_gate.v1"
    status = if ($DryRun) { "dry_run" } else { "runtime_pending" }
    run_id = $RunId
    scenario = $ScenarioPath
    command = $command
    dynamics_profile = [pscustomobject]@{
        name = $DynamicsProfile
        ego_max_vel_mps = $dynamics['ego_max_vel_mps']
        ego_max_acc_mps2 = $dynamics['ego_max_acc_mps2']
        command_speed_mps = $dynamics['command_speed_mps']
        command_acceleration_mps2 = $dynamics['command_acceleration_mps2']
        command_lateral_acceleration_mps2 = $dynamics['command_lateral_acceleration_mps2']
        command_jerk_mps3 = $dynamics['command_jerk_mps3']
        predictive_braking_deceleration_mps2 = $dynamics['predictive_braking_deceleration_mps2']
        minimum_inter_uav_distance_m = 1.0
        predictive_margin_m = 0.10
    }
    publish_hover_during_takeoff = [bool]$PublishHoverDuringTakeoff
    acceptance = [pscustomobject]@{
        backend_mission_status = "passed"
        minimum_inter_uav_distance_m = 1.0
        inter_uav_emergency_prediction_margin_m = 0.10
        maximum_roll_pitch_deg = 45.0
        formation_rmse_m = 0.35
        formation_peak_error_m = 0.80
        planner_obstacle_clearance_m = $plannerObstacleClearanceM
        runtime_planner_obstacle_inflation_m = $runtimePlannerObstacleInflationM
        formation_envelope_radius_m = 1.50
        actual_formation_footprint_radius_m = $formation.rigid_footprint_radius_m
        formation_envelope_obstacle_inflation_m = 1.70
        astar_search_timeout_s = 1.00
        astar_planar_search = $true
        swarm_trajectory_receiver_time_tolerance_s = $swarmTrajectoryReceiverTimeToleranceS
        r52_observed_max_receive_age_s = $r52ObservedMaxReceiveAgeS
        receiver_age_safety_margin_s = $receiverAgeSafetyMarginS
        receiver_time_semantics = $runtimeContract.semantics
        local_map_size_xy_m = $mapSizeX
        local_grid_resolution_m = 0.20
        map_origin_override = [pscustomobject]@{
            enabled = $true
            x_m = $mapOriginX
            y_m = $mapOriginY
            min_x_m = $mapOriginX
            max_x_m = $mapOriginX + $mapSizeX
            min_y_m = $mapOriginY
            max_y_m = $mapOriginY + $mapSizeY
            center_source = "formation.target_center_xy_m"
        }
        planner_min_traj_z_m = 0.90
        planner_max_traj_z_m = 1.35
        virtual_ceil_height_m = 1.45
        command_safety_max_z_m = 1.35
    }
    target_chain_contract = [pscustomobject]@{
        transport = "single_global_formation_center"
        source = "rigid_center_path_contract.center_waypoints_xy_m"
        skipped_spawn_waypoint = $true
        target_reached_radius_m = $targetReachedRadiusM
        target_hold_s = $targetHoldS
        center_chain_file = $formationCenterChainPath
        center_chain_waypoint_count = $formationCenterWaypoints.Count
        member_acceptance_chain_files = [pscustomobject]@{
            uav1 = $memberChainPaths[1]
            uav2 = $memberChainPaths[2]
            uav3 = $memberChainPaths[3]
        }
        member_offsets_xy_m = [pscustomobject]@{
            uav1 = $memberOffsets[1]
            uav2 = $memberOffsets[2]
            uav3 = $memberOffsets[3]
        }
        semantics = "Only formation_center_chain.json may be published to /move_base_simple/goal. Per-UAV chains are synchronized target-hold acceptance references and must never be published sequentially to the shared formation-center topic."
    }
    command_mode = $CommandMode
    command_topology = [pscustomobject]@{
        leader_follower_commands = $leaderFollowerCommands
        rigid_leader_follower_mode = $rigidLeaderFollowerMode
        planner_command_producer_uav_ids = $plannerCommandProducerUavIds
        follower_final_command_source = $followerFinalCommandSource
        semantics = "In rigid leader-follower mode, only UAV1 produces executable Swarm-Formation trajectories. UAV2/UAV3 retain MID360 and grid diagnostics but execute the safety-adapted UAV1 command plus their spawn-relative offsets."
    }
    claim_boundary = "Swarm-Formation known-target obstacle-crossing gate; not autonomous exploration or unknown-map coverage. leader_follower forwards UAV1 raw commands to UAV2/UAV3 with spawn-relative offsets; native_per_uav forwards each planner's own raw command."
}
$manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $ResultDir "FORMATION_OBSTACLE_GATE.json") -Encoding utf8
if ($DryRun) {
    Write-Output $ResultDir
    exit 0
}

& wsl -d Ubuntu-20.04 -- bash -lc $command
$backendExit = $LASTEXITCODE
if (Test-Path -LiteralPath (Join-Path $ResultDir "EGO_SWARM_METRICS.json")) {
    python (Join-Path $Root "Scripts\sunray\analyze_swarm_formation_tracking.py") `
        --run $ResultDir `
        --scenario $ScenarioPath `
        --max-rmse-m 0.35 `
        --max-peak-error-m 0.80 `
        --min-inter-uav-distance-m 1.0 `
        --max-roll-pitch-deg 45.0
    $formationExit = $LASTEXITCODE
    python (Join-Path $Root "Scripts\sunray\analyze_swarm_formation_obstacle_clearance.py") `
        --run $ResultDir `
        --scenario $ScenarioPath `
        --planner-clearance-m $plannerObstacleClearanceM
    $obstacleExit = $LASTEXITCODE
} else {
    $formationExit = 2
    $obstacleExit = 2
}
function Get-GateStatus {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return "missing"
    }
    try {
        $payload = Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
        if ($null -eq $payload -or [string]::IsNullOrWhiteSpace([string]$payload.status)) {
            return "invalid_status"
        }
        return [string]$payload.status
    } catch {
        return "invalid_json"
    }
}

$metricsStatus = Get-GateStatus (Join-Path $ResultDir "EGO_SWARM_METRICS.json")
$trackingStatus = Get-GateStatus (Join-Path $ResultDir "SWARM_FORMATION_TRACKING_GATE.json")
$plannerAuditStatus = Get-GateStatus (Join-Path $ResultDir "planner_runtime_log_audit.json")
$clearanceStatus = Get-GateStatus (Join-Path $ResultDir "SWARM_FORMATION_OBSTACLE_CLEARANCE_GATE.json")
$allGatesPassed = $backendExit -eq 0 -and $formationExit -eq 0 -and $obstacleExit -eq 0 -and `
    $metricsStatus -eq "passed" -and $trackingStatus -eq "passed" -and `
    $plannerAuditStatus -eq "passed" -and $clearanceStatus -eq "passed"
$manifest.status = if ($allGatesPassed) { "passed" } else { "blocked" }
$manifest | Add-Member -NotePropertyName exit_codes -NotePropertyValue ([pscustomobject]@{
    backend = $backendExit
    formation_tracking = $formationExit
    obstacle_clearance = $obstacleExit
}) -Force
$manifest | Add-Member -NotePropertyName gate_results -NotePropertyValue ([pscustomobject]@{
    mission_metrics = $metricsStatus
    formation_tracking = $trackingStatus
    planner_runtime_log_audit = $plannerAuditStatus
    obstacle_clearance = $clearanceStatus
}) -Force
$manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $ResultDir "FORMATION_OBSTACLE_GATE.json") -Encoding utf8
if (-not $allGatesPassed) {
    exit 1
}
Write-Output $ResultDir
