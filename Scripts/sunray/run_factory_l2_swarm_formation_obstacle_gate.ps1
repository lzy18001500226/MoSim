param(
    [string]$RunId = ("factory_l2_swarm_formation_obstacle_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$Root = "C:\Users\HP\Desktop\MoSim"
$RootWsl = "/mnt/c/Users/HP/Desktop/MoSim"
$ScenarioPath = Join-Path $Root "Config\scenarios\formation\factory_l2_three_uav_obstacle_crossing.json"
$ResultDir = Join-Path $Root ("Results\sunray_ros1\" + $RunId)
$ResultDirWsl = $RootWsl + "/Results/sunray_ros1/" + $RunId

python (Join-Path $Root "Scripts\sunray\build_factory_l2_formation_obstacle_scenario.py")
$scenario = Get-Content -Raw -LiteralPath $ScenarioPath | ConvertFrom-Json
$formation = $scenario.formation
$start = $formation.start_positions_xy_m
$center = $formation.target_center_xy_m

$environment = @(
    "RUN_ID=$RunId",
    "RESULT_DIR=$ResultDirWsl",
    "PLANNER_VARIANT=swarm_formation",
    "UAV_NUM=3",
    "WORLD_FILE=$RootWsl/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf",
    "FACTORY_L2_MODEL_PATH=$RootWsl/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/models",
    "SUNRAY_GAZEBO_LAUNCH_FILE=$RootWsl/Scripts/sunray/factory_l2_sunray_px4_gazebo.launch",
    "PRELOAD_GAZEBO_MODELS=false",
    "STAGGERED_SPAWN=true",
    "STAGGERED_SPAWN_INTERVAL_S=12",
    "GOAL5_STARTUP_ATTEMPTS=1",
    "MAVROS_READY_TIMEOUT_S=150",
    "START1_X=$($start.'1'[0])", "START1_Y=$($start.'1'[1])",
    "START2_X=$($start.'2'[0])", "START2_Y=$($start.'2'[1])",
    "START3_X=$($start.'3'[0])", "START3_Y=$($start.'3'[1])",
    "SWARM_FORMATION_D3_CENTER_X=$($center[0])",
    "SWARM_FORMATION_D3_CENTER_Y=$($center[1])",
    "SWARM_FORMATION_D3_CENTER_Z=$($formation.z_m)",
    "SWARM_FORMATION_D3_RELATIVE_Z=0.0",
    "SWARM_FORMATION_D3_SWARM_SCALE=$($formation.scale)",
    "SWARM_FORMATION_D3_MAP_SIZE_X=64.0",
    "SWARM_FORMATION_D3_MAP_SIZE_Y=64.0",
    "SWARM_FORMATION_D3_MAP_SIZE_Z=3.0",
    "SWARM_FORMATION_D3_GRID_RESOLUTION=0.20",
    "SWARM_FORMATION_D3_OBSTACLES_INFLATION=0.20",
    "SWARM_FORMATION_D3_LOCAL_UPDATE_RANGE_XY=8.0",
    "EGO_MAX_VEL=0.8",
    "EGO_MAX_ACC=0.8",
    "EGO_PLANNING_HORIZON=8.0",
    "EGO_GATE_MIN_INTER_UAV_DISTANCE=1.0",
    "EGO_GATE_INTER_UAV_EMERGENCY_HOLD_ENABLE=true",
    "EGO_GATE_TAKEOFF_HEIGHT=1.0",
    "EGO_GATE_EXECUTE_TIMEOUT_S=420",
    "EGO_GATE_EGO_TAKEOVER_TIMEOUT_S=120",
    "EGO_GATE_TAKEOFF_WALL_TIMEOUT_S=300",
    "EGO_GATE_LAND_WALL_TIMEOUT_S=300",
    "EGO_CMD_SAFETY_MIN_Z=0.90",
    "EGO_CMD_SAFETY_MAX_Z=1.60",
    "EGO_CMD_SAFETY_MOTION_TIME_BASIS=ros_sim_time",
    "EGO_CMD_SAFETY_RECOMPUTE_VELOCITY_FROM_POSITION=true",
    "EGO_CMD_SAFETY_MAX_VELOCITY_MPS=1.0",
    "EGO_CMD_SAFETY_MAX_ACCELERATION_MPS2=1.2",
    "EGO_CMD_SAFETY_MAX_LATERAL_ACCELERATION_MPS2=1.2",
    "EGO_CMD_SAFETY_MAX_JERK_MPS3=6.0",
    "TOTAL_TIMEOUT_S=600"
)

$command = "cd $RootWsl && env " + ($environment -join " ") + " bash Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh"
New-Item -ItemType Directory -Force -Path $ResultDir | Out-Null
$manifest = [pscustomobject]@{
    schema = "mosim.factory_l2_swarm_formation_obstacle_gate.v1"
    status = if ($DryRun) { "dry_run" } else { "runtime_pending" }
    run_id = $RunId
    scenario = $ScenarioPath
    command = $command
    acceptance = [pscustomobject]@{
        backend_mission_status = "passed"
        minimum_inter_uav_distance_m = 1.0
        maximum_roll_pitch_deg = 45.0
        formation_rmse_m = 0.35
        formation_peak_error_m = 0.80
    }
    claim_boundary = "Swarm-Formation known-target obstacle-crossing gate; not autonomous exploration or unknown-map coverage."
}
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $ResultDir "FORMATION_OBSTACLE_GATE.json") -Encoding utf8
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
} else {
    $formationExit = 2
}
if ($backendExit -ne 0 -or $formationExit -ne 0) {
    exit 1
}
