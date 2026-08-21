param(
    [string]$RunId = ("factory_l2_highstar_single_exploration_review_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [double]$ExplorationExecuteS = 60.0,
    [double]$EgoTakeoverTimeoutS = 90.0,
    [int]$MissionTotalTimeoutS = 0,
    [int]$ReviewHoldS = 300,
    [double]$TargetZ = 1.2,
    [double]$TakeoffHeight = -1.0,
    [double]$TakeoffTimeoutS = 50.0,
    [double]$StartX = [double]::NaN,
    [double]$StartY = [double]::NaN,
    [double]$StartYaw = 0.0,
    [double]$HighStarWindowXM = 24.0,
    [double]$HighStarWindowYM = 24.0,
    [double]$HighStarMapMinZM = 0.0,
    [double]$HighStarMapMaxZM = 2.0,
    [double]$HighStarCmdMinZM = 0.80,
    [double]$HighStarCmdMaxZM = 1.80,
    [bool]$HighStarViewpointZGateEnable = $false,
    [double]$HighStarViewpointMinZM = 0.80,
    [double]$HighStarViewpointMaxZM = 1.80,
    [double]$HighStarSensorMaxRangeM = 8.0,
    [string]$HighStarSensorInput = "depth",
    [string]$HighStarFrontierSensorType = "Depth_Camera",
    [double]$HighStarFrontierSampleMaxRangeM = 3.0,
    [double]$HighStarFrontierGridScale = 2.0,
    [double]$HighStarFrontierViewpointThresh = 0.8,
    [double]$HighStarFrontierVgainThresh = 0.5,
    [double]$HighStarFrontierObserveThresh = 0.85,
    [double]$HighStarOptMaxVelMps = 1.0,
    [double]$HighStarOptMaxAccMps2 = 1.5,
    [double]$HighStarOptMaxJerMps3 = 8.0,
    [double]$HighStarBridgeMaxVelMps = 0.6,
    [double]$HighStarBridgeMaxAccMps2 = 0.8,
    [bool]$HighStarUseCoverTrajectory = $true,
    [double]$HighStarCmdFixedZM = -1.0,
    [double]$HighStarCmdFixedYawRad = [double]::NaN,
    [bool]$HighStarSeedFromOdomOnEnable = $true,
    [double]$HighStarCmdSmoothMaxSpeedMps = 1.0,
    [double]$HighStarCmdSmoothMaxStepM = 0.0,
    [string]$HighStarWs = "",
    [double]$PointCloudMaxAbsOdomXYM = 700.0,
    [double]$PointCloudTransformMinWorldZM = -0.2,
    [double]$PointCloudReviewMinWorldZM = 0.2,
    [switch]$SkipPreflight,
    [switch]$UnlimitedAccumulation,
    [switch]$NoRviz,
    [switch]$NoKeepAlive
)

$ErrorActionPreference = "Stop"
$ProjectRootWin = "C:\Users\HP\Desktop\MoSim"
$ProjectRootWsl = "/mnt/c/Users/HP/Desktop/MoSim"
$EnvelopePathWin = Join-Path $ProjectRootWin "Config\gazebo\scene_profiles\factory_l2_exploration_envelope.json"
$ResultDirWin = Join-Path $ProjectRootWin ("Results\sunray_ros1\" + $RunId)
$ResultDirWsl = $ProjectRootWsl + "/Results/sunray_ros1/" + $RunId
$FactoryWorldWsl = $ProjectRootWsl + "/Config/gazebo/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf"
$FactoryModelPathWsl = $ProjectRootWsl + "/Config/gazebo/models"
$TotalTimeoutS = if ($MissionTotalTimeoutS -gt 0) {
    $MissionTotalTimeoutS
} else {
    [int]([Math]::Ceiling($ExplorationExecuteS + 180))
}
$PointCloudCap = if ($UnlimitedAccumulation) { 0 } else { 2000000 }
$OccupancyCap = if ($UnlimitedAccumulation) { 0 } else { 1000000 }
$OpenRvizValue = if ($NoRviz) { "false" } else { "true" }
$KeepAliveValue = if ($NoKeepAlive) { "false" } else { "true" }

$envelope = Get-Content -LiteralPath $EnvelopePathWin -Raw | ConvertFrom-Json
$boundary = $envelope.exploration_boundary
if ([double]::IsNaN($StartX)) {
    $StartX = [double]$boundary.center_x_m
}
if ([double]::IsNaN($StartY)) {
    $StartY = [double]$boundary.center_y_m
}
$EffectiveTakeoffHeight = if ($TakeoffHeight -gt 0.0) { $TakeoffHeight } else { $TargetZ }

$HighStarWsWsl = ""
if (-not [string]::IsNullOrWhiteSpace($HighStarWs)) {
    $HighStarWsWsl = $HighStarWs.Replace("\", "/")
    if ($HighStarWsWsl.StartsWith("C:/")) {
        $HighStarWsWsl = "/mnt/c/" + $HighStarWsWsl.Substring(3)
    }
}

New-Item -ItemType Directory -Force -Path $ResultDirWin | Out-Null

$envParts = @(
    "RUN_ID=$RunId",
    "RESULT_DIR=$ResultDirWsl",
    "PLANNER_VARIANT=highstar",
    $(if ([string]::IsNullOrWhiteSpace($HighStarWsWsl)) { $null } else { "HIGHSTAR_WS=$HighStarWsWsl" }),
    "PX4CTRL_CORE_PROFILE=l1_awff",
    "FACTORY_WORLD_MODE=clean",
    "GUI=false",
    "OPEN_RVIZ=$OpenRvizValue",
    "KEEP_ALIVE=$KeepAliveValue",
    "WORLD_FILE=$FactoryWorldWsl",
    "FACTORY_MODEL_PATH=$FactoryModelPathWsl",
    "SUNRAY_GAZEBO_LAUNCH_FILE=$ProjectRootWsl/Scripts/sunray/factory_l2_sunray_px4_gazebo.launch",
    "SUNRAY_STRIP_PX4_MODEL_PATH=true",
    "SUNRAY_MID360_PLUGIN_DOWNSAMPLE=4",
    "SUNRAY_LIVOX_PLUGIN_FILENAME=$ProjectRootWsl/Results/sunray_ros1/workspaces/sunray_livox_plugin_ws/devel/lib/liblivox_laser_simulation.so",
    "SUNRAY_MID360_CSV_FILE_NAME=mid360-real-centr.csv",
    "SUNRAY_MID360_GOAL5_CSV_STRIDE=4",
    "SUNRAY_UAV_INIT_X=$StartX",
    "SUNRAY_UAV_INIT_Y=$StartY",
    "SUNRAY_UAV_INIT_Z=0.2",
    "SUNRAY_UAV_INIT_YAW=$StartYaw",
    "TARGET_X=$StartX",
    "TARGET_Y=$StartY",
    "TARGET_Z=$TargetZ",
    "GOAL4_TAKEOFF_HEIGHT=$EffectiveTakeoffHeight",
    "GOAL4_TAKEOFF_TIMEOUT_S=$TakeoffTimeoutS",
    "GOAL4_EGO_TAKEOVER_TIMEOUT_S=$EgoTakeoverTimeoutS",
    "HIGHSTAR_FACTORY_WINDOW_X_M=$HighStarWindowXM",
    "HIGHSTAR_FACTORY_WINDOW_Y_M=$HighStarWindowYM",
    "HIGHSTAR_MAP_MIN_Z=$HighStarMapMinZM",
    "HIGHSTAR_MAP_MAX_Z=$HighStarMapMaxZM",
    "HIGHSTAR_CMD_MIN_Z=$HighStarCmdMinZM",
    "HIGHSTAR_CMD_MAX_Z=$HighStarCmdMaxZM",
    "HIGHSTAR_FRONTIER_VIEWPOINT_Z_GATE_ENABLE=$($HighStarViewpointZGateEnable.ToString().ToLowerInvariant())",
    "HIGHSTAR_FRONTIER_VIEWPOINT_MIN_Z=$HighStarViewpointMinZM",
    "HIGHSTAR_FRONTIER_VIEWPOINT_MAX_Z=$HighStarViewpointMaxZM",
    "HIGHSTAR_SENSOR_MAX_RANGE=$HighStarSensorMaxRangeM",
    "HIGHSTAR_SENSOR_INPUT=$HighStarSensorInput",
    "HIGHSTAR_FRONTIER_SENSOR_TYPE=$HighStarFrontierSensorType",
    "HIGHSTAR_FRONTIER_SAMPLE_MAX_RANGE=$HighStarFrontierSampleMaxRangeM",
    "HIGHSTAR_FRONTIER_GRID_SCALE=$HighStarFrontierGridScale",
    "HIGHSTAR_FRONTIER_VIEWPOINT_THRESH=$HighStarFrontierViewpointThresh",
    "HIGHSTAR_FRONTIER_VGAIN_THRESH=$HighStarFrontierVgainThresh",
    "HIGHSTAR_FRONTIER_OBSERVE_THRESH=$HighStarFrontierObserveThresh",
    "HIGHSTAR_OPT_MAX_VEL=$HighStarOptMaxVelMps",
    "HIGHSTAR_OPT_MAX_ACC=$HighStarOptMaxAccMps2",
    "HIGHSTAR_OPT_MAX_JER=$HighStarOptMaxJerMps3",
    "HIGHSTAR_EXP_USE_COVER_TRAJECTORY=$($HighStarUseCoverTrajectory.ToString().ToLowerInvariant())",
    "HIGHSTAR_BRIDGE_MAX_V=$HighStarBridgeMaxVelMps",
    "HIGHSTAR_BRIDGE_MAX_A=$HighStarBridgeMaxAccMps2",
    $(if ($HighStarCmdFixedZM -gt 0.0) { "HIGHSTAR_CMD_FIXED_Z=$HighStarCmdFixedZM" } else { $null }),
    $(if (-not [double]::IsNaN($HighStarCmdFixedYawRad)) { "PLANNER_CMD_FIXED_YAW=$HighStarCmdFixedYawRad" } else { $null }),
    "PLANNER_CMD_SEED_FROM_ODOM_ON_ENABLE=$($HighStarSeedFromOdomOnEnable.ToString().ToLowerInvariant())",
    "HIGHSTAR_CMD_SMOOTH_ENABLE=true",
    "HIGHSTAR_CMD_SMOOTH_MAX_SPEED_MPS=$HighStarCmdSmoothMaxSpeedMps",
    "HIGHSTAR_CMD_SMOOTH_MAX_STEP_M=$HighStarCmdSmoothMaxStepM",
    "HIGHSTAR_CMD_SMOOTH_ZERO_DYNAMICS=true",
    "HIGHSTAR_CMD_ZERO_ALL_DYNAMICS=false",
    "HIGHSTAR_RAW_CMD_MAX_POSITION_JUMP_M=0",
    "HIGHSTAR_RAW_CMD_MAX_POSITION_JUMP_SPEED_MPS=3.0",
    "HIGHSTAR_EXPLORATION_EXECUTE_S=$ExplorationExecuteS",
    "HIGHSTAR_MIN_PLANNER_COMMAND_COUNT=1",
    "GOAL4_RECORD_HZ=100",
    "GOAL4_RECORD_CMD_HZ=100",
    "GOAL4_MAX_PATH_POINTS=0",
    "GOAL4_PATH_PUBLISH_HZ=20",
    "GOAL4_REVIEW_HOLD_PATH_PUBLISH_HZ=10",
    "POINTCLOUD_REVIEW_VOXEL_SIZE_M=0.08",
    "POINTCLOUD_MAX_SENSOR_RANGE_M=80.0",
    "POINTCLOUD_MIN_WORLD_Z_M=$PointCloudTransformMinWorldZM",
    "POINTCLOUD_MAX_WORLD_Z_M=4.0",
    "POINTCLOUD_MAX_ABS_ODOM_XY_M=$PointCloudMaxAbsOdomXYM",
    "POINTCLOUD_REVIEW_MIN_WORLD_Z_M=$PointCloudReviewMinWorldZM",
    "POINTCLOUD_REVIEW_MAX_WORLD_Z_M=4.0",
    "POINTCLOUD_REVIEW_MAX_POINTS_PER_CLOUD=50000",
    "POINTCLOUD_REVIEW_MAX_ACCUMULATED_POINTS=$PointCloudCap",
    "POINTCLOUD_REVIEW_PUBLISH_RATE_HZ=2.0",
    "OCCUPANCY_TOPIC=/murder_demo/block_map/voxvis",
    "OCCUPANCY_MSG_TYPE=markerarray",
    "OCCUPANCY_REVIEW_SOURCE_TOPIC=",
    "OCCUPANCY_REVIEW_MIN_Z=0.20",
    "OCCUPANCY_REVIEW_MAX_Z=4.0",
    "OCCUPANCY_REVIEW_VOXEL_SIZE_M=0.12",
    "OCCUPANCY_REVIEW_MAX_POINTS_PER_CLOUD=50000",
    "OCCUPANCY_REVIEW_MAX_ACCUMULATED_POINTS=$OccupancyCap",
    "OCCUPANCY_REVIEW_PUBLISH_RATE_HZ=2.0",
    "OCCUPANCY_REVIEW_QUALITY_ODOM_TOPIC=",
    "ENABLE_OCCUPANCY_REVIEW_ACCUMULATION=false",
    "MAVROS_READY_TIMEOUT_S=120",
    "TOTAL_TIMEOUT_S=$TotalTimeoutS",
    "DIFF_INTERACTIVE_REVIEW_HOLD_S=$ReviewHoldS"
)

$preflight = if ($SkipPreflight) {
    "echo skipped > '$ResultDirWsl/preflight_skipped.txt'"
} else {
    "bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh > '$ResultDirWsl/preflight.log' 2>&1"
}

$bashStatus = '$?'
$bashScriptWin = Join-Path $ResultDirWin "start_factory_highstar_single_exploration_review.sh"
$bashScriptWsl = $ResultDirWsl + "/start_factory_highstar_single_exploration_review.sh"
$command = @"
#!/usr/bin/env bash
set -e
cd $ProjectRootWsl
mkdir -p '$ResultDirWsl'
exec > >(tee -a '$ResultDirWsl/bootstrap.log') 2>&1
date --iso-8601=seconds > '$ResultDirWsl/background_start_marker.txt'
$preflight || { echo $bashStatus > '$ResultDirWsl/preflight_exit_code.txt'; exit 2; }
echo 0 > '$ResultDirWsl/preflight_exit_code.txt'
export GAZEBO_MODEL_PATH='$FactoryModelPathWsl':"`${GAZEBO_MODEL_PATH:-}"
echo "starting run_px4ctrl_ego_single_gate.sh"
set +e
$($envParts -join " ") bash Scripts/sunray/run_px4ctrl_ego_single_gate.sh > '$ResultDirWsl/background_launcher.log' 2>&1
run_exit=$bashStatus
echo `$run_exit > '$ResultDirWsl/background_exit_code.txt'
exit `$run_exit
"@

$command = $command.Replace("`r`n", "`n")
[System.IO.File]::WriteAllText($bashScriptWin, $command, [System.Text.UTF8Encoding]::new($false))
$stdoutLog = Join-Path $ResultDirWin "windows_child_stdout.log"
$stderrLog = Join-Path $ResultDirWin "windows_child_stderr.log"
$proc = Start-Process -FilePath "wsl.exe" -ArgumentList @("-d", "Ubuntu-20.04", "--exec", "bash", $bashScriptWsl) -WindowStyle Hidden -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog -PassThru

[pscustomobject]@{
    RunId = $RunId
    ProcessId = $proc.Id
    ResultDir = $ResultDirWin
    World = $FactoryWorldWsl
    HighStarWindowXM = $HighStarWindowXM
    HighStarWindowYM = $HighStarWindowYM
    HighStarWs = $HighStarWsWsl
    PointCloudAccumulationCap = $PointCloudCap
    OccupancyAccumulationCap = $OccupancyCap
}
