param(
    [string]$RunId = ("review_diff_swarm_3uav_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [int]$TotalTimeoutS = 280,
    [switch]$SkipPreflight,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$ProjectRootWin = "C:\Users\HP\Desktop\MoSim"
$ProjectRootWsl = "/mnt/c/Users/HP/Desktop/MoSim"
$ResultDirWin = Join-Path $ProjectRootWin ("Results\sunray_ros1\" + $RunId)
$ResultDirWsl = $ProjectRootWsl + "/Results/sunray_ros1/" + $RunId

$preflight = if ($SkipPreflight) {
    "echo skipped > '$ResultDirWsl/preflight_skipped.txt'"
} else {
    "bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh > '$ResultDirWsl/preflight.log' 2>&1"
}

$command = @"
cd $ProjectRootWsl
mkdir -p '$ResultDirWsl'
date --iso-8601=seconds > '$ResultDirWsl/background_start_marker.txt'
$preflight || { code=`$?; echo `$code > '$ResultDirWsl/preflight_exit_code.txt'; exit 2; }
echo 0 > '$ResultDirWsl/preflight_exit_code.txt'

RUN_ID='$RunId' \
RESULT_DIR='$ResultDirWsl' \
PLANNER_VARIANT=diff_planner \
UAV_NUM=3 \
GUI=false \
KEEP_ALIVE=true \
TOTAL_TIMEOUT_S=$TotalTimeoutS \
POINTCLOUD_MIN_WORLD_Z_M=0.20 \
POINTCLOUD_MAX_WORLD_Z_M=2.20 \
POINTCLOUD_ROTATION_MODE=full \
SUNRAY_MID360_PLUGIN_DOWNSAMPLE=4 \
SUNRAY_MID360_GOAL5_CSV_STRIDE=4 \
MAVROS_STREAM_RATE_HZ=100 \
EGO_MAX_VEL=0.8 \
EGO_MAX_ACC=0.8 \
EGO_MAX_JERK=4.0 \
EGO_CMD_SAFETY_MIN_Z=0.85 \
EGO_CMD_SAFETY_MAX_Z=1.35 \
EGO_CMD_SAFETY_MAX_POSITION_JUMP_M=0.50 \
bash Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh > '$ResultDirWsl/background_launcher.log' 2>&1 &
runner_pid=`$!
echo `$runner_pid > '$ResultDirWsl/background_runner.pid'

for i in `$(seq 1 180); do
  if rostopic list 2>/dev/null | grep -q '/mosim/goal5/uav1/truth_path'; then
    break
  fi
  sleep 1
done

python3 Scripts/sunray/swarm_body_axes_marker_node.py \
  --uav-num 3 \
  --marker-topic /mosim/goal5/body_axes \
  --axis-length-m 0.20 \
  --shaft-m 0.015 \
  --head-diameter-m 0.045 \
  --head-length-m 0.060 \
  > '$ResultDirWsl/swarm_body_axes_marker.log' 2>&1 &
echo `$! > '$ResultDirWsl/swarm_body_axes_marker.pid'

rviz -d '$ProjectRootWsl/Config/rviz/sunray_ros1_goal5_diff_swarm_pointcloud_review.rviz' \
  > '$ResultDirWsl/rviz_diff_swarm_pointcloud_review.log' 2>&1 &
echo `$! > '$ResultDirWsl/rviz_diff_swarm_pointcloud_review.pid'
sleep 1
rviz -d '$ProjectRootWsl/Config/rviz/sunray_ros1_goal5_diff_swarm_grid3d_review.rviz' \
  > '$ResultDirWsl/rviz_diff_swarm_grid3d_review.log' 2>&1 &
echo `$! > '$ResultDirWsl/rviz_diff_swarm_grid3d_review.pid'

wait `$runner_pid
exit_code=`$?
echo `$exit_code > '$ResultDirWsl/background_exit_code.txt'
exit `$exit_code
"@

$wslCommand = "wsl -d Ubuntu-20.04 --exec bash -lc " + '"' + $command.Replace('"', '\"') + '"'

if ($DryRun) {
    Write-Host "Diff swarm review dry run OK."
    Write-Host ("RunId: " + $RunId)
    Write-Host ("Result: " + $ResultDirWin)
    Write-Host ("WslCommandPreview: " + $wslCommand.Substring(0, [Math]::Min($wslCommand.Length, 500)))
    exit 0
}

New-Item -ItemType Directory -Force -Path $ResultDirWin | Out-Null

$encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($wslCommand))
$proc = Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile", "-EncodedCommand", $encoded) -WindowStyle Hidden -PassThru

Write-Host "Started Diff-Planner 3-UAV review."
Write-Host ("RunId: " + $RunId)
Write-Host ("ProcessId: " + $proc.Id)
Write-Host ("Result: " + $ResultDirWin)
Write-Host ""
Write-Host "This opens two RViz windows and keeps Gazebo/ROS/RViz alive for review."
Write-Host "Use 关闭所有RViz窗口.cmd when you only need to close RViz windows."
