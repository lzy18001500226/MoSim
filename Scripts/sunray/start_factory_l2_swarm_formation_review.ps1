param(
    [string]$RunId = ("factory_l2_swarm_formation_review_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [string]$AcceptedRunId = "factory_l2_swarm_formation_maporigin_r54_runtime_20260722",
    [int]$StartupTimeoutS = 300,
    [int]$AirborneTimeoutS = 300,
    [double]$AirborneMinZ = 0.8,
    [int]$ReviewTotalTimeoutS = 1200,
    [int]$UnrealUdpBasePort = 5005,
    [double]$UnrealStateRateHz = 100.0,
    [int]$UnrealMaxFps = 30,
    [switch]$AttachOnly,
    [switch]$NoUnreal,
    [switch]$NoRviz,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$Root = "C:\Users\HP\Desktop\MoSim"
$RootWsl = "/mnt/c/Users/HP/Desktop/MoSim"
$ResultDir = Join-Path $Root ("Results\sunray_ros1\" + $RunId)
$ResultDirWsl = $RootWsl + "/Results/sunray_ros1/" + $RunId
$GateScript = Join-Path $Root "Scripts\sunray\run_factory_l2_swarm_formation_obstacle_gate.ps1"
$AcceptedResultDir = Join-Path $Root ("Results\sunray_ros1\" + $AcceptedRunId)
$AcceptedBackendGate = Join-Path $AcceptedResultDir "EGO_SWARM_METRICS.json"
$AcceptedFormationGate = Join-Path $AcceptedResultDir "SWARM_FORMATION_TRACKING_GATE.json"
$AcceptedObstacleClearanceGate = Join-Path $AcceptedResultDir "SWARM_FORMATION_OBSTACLE_CLEARANCE_GATE.json"
$UnrealEditor = "D:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe"
$UnrealProject = Join-Path $Root "UE5\MoSimSceneLibrary\MoSimSceneLibrary.uproject"

foreach ($gatePath in @($AcceptedBackendGate, $AcceptedFormationGate, $AcceptedObstacleClearanceGate)) {
    if (-not (Test-Path -LiteralPath $gatePath)) {
        throw "Swarm-Formation review is closed because accepted gate evidence is missing: $gatePath"
    }
    $gatePacket = Get-Content -Raw -LiteralPath $gatePath | ConvertFrom-Json
    if ($gatePacket.status -ne "passed" -or @($gatePacket.blockers).Count -ne 0) {
        throw "Swarm-Formation review is closed because accepted gate evidence did not pass: $gatePath"
    }
}

if ($DryRun) {
    & $GateScript -RunId $RunId -TotalTimeoutS $ReviewTotalTimeoutS -KeepAlive -DryRun
    Write-Host "Factory L2 Swarm-Formation review dry run OK."
    Write-Host ("RunId: " + $RunId)
    exit 0
}

New-Item -ItemType Directory -Force -Path $ResultDir | Out-Null

$gate = $null
if (-not $AttachOnly) {
    $gate = Start-Process -FilePath "powershell.exe" -ArgumentList @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", $GateScript,
        "-RunId", $RunId,
        "-TotalTimeoutS", $ReviewTotalTimeoutS,
        "-KeepAlive"
    ) -WindowStyle Hidden -PassThru
    $gate.Id | Set-Content -LiteralPath (Join-Path $ResultDir "review_gate_windows_pid.txt") -Encoding ascii
}

$ready = $false
$deadline = [DateTime]::UtcNow.AddSeconds($StartupTimeoutS)
while ([DateTime]::UtcNow -lt $deadline) {
    if ($null -ne $gate -and $gate.HasExited) {
        throw "Swarm-Formation gate exited before live review inputs became ready (exit $($gate.ExitCode))."
    }
    & wsl -d Ubuntu-20.04 -- bash -lc "source /opt/ros/noetic/setup.bash && timeout 4 rostopic echo -n 1 /uav1/sunray/gazebo_pose >/dev/null 2>&1 && timeout 4 rostopic echo -n 1 /uav2/sunray/gazebo_pose >/dev/null 2>&1 && timeout 4 rostopic echo -n 1 /uav3/sunray/gazebo_pose >/dev/null 2>&1 && timeout 4 rostopic echo -n 1 /uav1/mavros/state 2>/dev/null | grep -q 'connected: True' && timeout 4 rostopic echo -n 1 /uav2/mavros/state 2>/dev/null | grep -q 'connected: True' && timeout 4 rostopic echo -n 1 /uav3/mavros/state 2>/dev/null | grep -q 'connected: True'"
    if ($LASTEXITCODE -eq 0) {
        $ready = $true
        break
    }
    Start-Sleep -Seconds 2
}
if (-not $ready) {
    throw "Timed out after ${StartupTimeoutS}s waiting for all three Gazebo-truth UE review topics."
}

& wsl -d Ubuntu-20.04 -- bash -lc "source /opt/ros/noetic/setup.bash && rostopic list > '$ResultDirWsl/ros_topic_list.txt'"
if ($LASTEXITCODE -ne 0) {
    throw "Unable to save the ROS topic snapshot for the Swarm-Formation review."
}

if (-not $NoUnreal) {
    if ($null -ne $gate -and $gate.HasExited) {
        throw "Swarm-Formation gate exited before all three UAVs became airborne (exit $($gate.ExitCode))."
    }
    & wsl -d Ubuntu-20.04 -- bash -lc "cd '$RootWsl' && source /opt/ros/noetic/setup.bash && python3 Scripts/sunray/wait_for_swarm_airborne.py --uav-num 3 --min-z $AirborneMinZ --timeout-s $AirborneTimeoutS"
    if ($LASTEXITCODE -ne 0) {
        throw "Timed out after ${AirborneTimeoutS}s waiting for all three UAVs to be armed above ${AirborneMinZ}m before opening UE."
    }
}

$DefaultRoute = & wsl -d Ubuntu-20.04 -- ip route show default
$GatewayMatch = [regex]::Match(($DefaultRoute -join "`n"), '(?m)^default\s+via\s+(\S+)')
$UnrealHost = if ($GatewayMatch.Success) { $GatewayMatch.Groups[1].Value } else { "" }
if (-not $NoUnreal -and [string]::IsNullOrWhiteSpace($UnrealHost)) {
    throw "Unable to resolve the Windows host address for the UE UDP mirror."
}

$unrealProcess = $null
if (-not $NoUnreal) {
    if (-not (Test-Path -LiteralPath $UnrealEditor)) {
        throw "UnrealEditor.exe not found: $UnrealEditor"
    }
    if (-not (Test-Path -LiteralPath $UnrealProject)) {
        throw "Unreal project not found: $UnrealProject"
    }

    Get-CimInstance Win32_Process -Filter "name = 'UnrealEditor.exe'" |
        Where-Object { $_.CommandLine -like '*MoSimSceneLibrary.uproject*' -and $_.CommandLine -like '* -game*' } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2

    $unrealArgs = @(
        $UnrealProject,
        "-game",
        "-windowed",
        "-ResX=1440",
        "-ResY=810",
        "-NoSplash",
        "/Game/Maps/Demonstration?game=/Script/MoSimSceneLibrary.MoSimSceneLibraryGameMode",
        "-MoSimSimulationReview",
        "-MoSimDayReview",
        "-MoSimReviewSunIntensity=6.0",
        "-MoSimReviewSkyLightIntensity=2.0",
        "-MoSimReviewExposureBias=0.0",
        "-MoSimPlaybackActorCount=3",
        "-MoSimPlaybackBaseUdpPort=$UnrealUdpBasePort",
        "-MoSimFollowPlaybackCamera",
        "-MoSimFollowCameraBackCm=231.25",
        "-MoSimFollowCameraRightCm=0",
        "-MoSimFollowCameraUpCm=95",
        "-MoSimFollowCameraLocationInterpSpeed=0",
        "-MoSimFollowCameraRotationInterpSpeed=0",
        "-ExecCmds=`"t.MaxFPS $UnrealMaxFps`"",
        "-MoSimNoReviewCollision"
    )
    $unrealProcess = Start-Process -FilePath $UnrealEditor -ArgumentList $unrealArgs -PassThru
    try {
        $unrealProcess.PriorityClass = "BelowNormal"
    } catch {
        Write-Warning "Unable to lower UE review process priority: $($_.Exception.Message)"
    }
    $unrealProcess.Id | Set-Content -LiteralPath (Join-Path $ResultDir "ue_game_pid.txt") -Encoding ascii
    [pscustomobject]@{
        schema = "mosim.factory_l2.swarm_formation.ue_review.v1"
        process_id = $unrealProcess.Id
        map = "/Game/Maps/Demonstration"
        actor_count = 3
        udp_ports = @($UnrealUdpBasePort, ($UnrealUdpBasePort + 1), ($UnrealUdpBasePort + 2))
        state_rate_hz = $UnrealStateRateHz
        max_render_fps = $UnrealMaxFps
        process_priority = "BelowNormal"
        camera = "formation_centroid_orbit_q_cycle"
        follow_offset_cm = @(0, 231.25, 95)
        pose_authority = "Gazebo truth"
        trajectory_overlay = "disabled"
        startup_gate = "three_truth_samples_three_mavros_connected_and_three_uavs_airborne"
    } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $ResultDir "ue_swarm_review_launch.json") -Encoding UTF8
}

$reviewCommand = @"
cd '$RootWsl'
source /opt/ros/noetic/setup.bash
source '$RootWsl/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash'
source '$RootWsl/Results/sunray_ros1/workspaces/swarm_formation_ws_d1_20260701_173306/devel/setup.bash'
export DISABLE_ROS1_EOL_WARNINGS=1
$(if (-not $NoUnreal) { @"
python3 -u Scripts/UE5/stream_ros1_state_to_ue_udp.py --odom-topic /uav1/sunray/gazebo_pose --position-cmd-topic /uav1/position_cmd --link-states-topic /gazebo/link_states --mavros-state-topic /uav1/mavros/state --host '$UnrealHost' --port $UnrealUdpBasePort --rate-hz $UnrealStateRateHz --vehicle-id uav1 --scene-id factory --map-id local_factoryenvironmentcollect --controller-profile px4ctrl --planner-profile swarm_formation > '$ResultDirWsl/ue_uav1_live_mirror.log' 2>&1 &
echo `$! > '$ResultDirWsl/ue_uav1_live_mirror.pid'
python3 -u Scripts/UE5/stream_ros1_state_to_ue_udp.py --odom-topic /uav2/sunray/gazebo_pose --position-cmd-topic /uav2/position_cmd --link-states-topic /gazebo/link_states --mavros-state-topic /uav2/mavros/state --host '$UnrealHost' --port $($UnrealUdpBasePort + 1) --rate-hz $UnrealStateRateHz --vehicle-id uav2 --scene-id factory --map-id local_factoryenvironmentcollect --controller-profile px4ctrl --planner-profile swarm_formation > '$ResultDirWsl/ue_uav2_live_mirror.log' 2>&1 &
echo `$! > '$ResultDirWsl/ue_uav2_live_mirror.pid'
python3 -u Scripts/UE5/stream_ros1_state_to_ue_udp.py --odom-topic /uav3/sunray/gazebo_pose --position-cmd-topic /uav3/position_cmd --link-states-topic /gazebo/link_states --mavros-state-topic /uav3/mavros/state --host '$UnrealHost' --port $($UnrealUdpBasePort + 2) --rate-hz $UnrealStateRateHz --vehicle-id uav3 --scene-id factory --map-id local_factoryenvironmentcollect --controller-profile px4ctrl --planner-profile swarm_formation > '$ResultDirWsl/ue_uav3_live_mirror.log' 2>&1 &
echo `$! > '$ResultDirWsl/ue_uav3_live_mirror.pid'
"@ })
$(if (-not $NoRviz) { @"
python3 Scripts/sunray/swarm_body_axes_marker_node.py \
  --uav-num 3 \
  --marker-topic /mosim/swarm_formation/body_axes \
  --axis-length-m 0.60 \
  --shaft-m 0.04 \
  --head-diameter-m 0.12 \
  --head-length-m 0.16 \
  > '$ResultDirWsl/swarm_body_axes_marker.log' 2>&1 &
echo `$! > '$ResultDirWsl/swarm_body_axes_marker.pid'
python3 Scripts/sunray/px4ctrl_pointcloud_review_node.py \
  --node-name mosim_swarm_formation_uav1_pointcloud_review \
  --result-dir '$ResultDirWsl' \
  --input-topic /uav1/livox/lidar \
  --odom-topic /uav1/sunray/gazebo_pose \
  --output-topic /mosim/swarm_formation/uav1/livox_world_accumulated \
  --frame-id world \
  > '$ResultDirWsl/uav1_pointcloud_review.log' 2>&1 &
echo `$! > '$ResultDirWsl/uav1_pointcloud_review.pid'
python3 Scripts/sunray/px4ctrl_pointcloud_review_node.py \
  --node-name mosim_swarm_formation_uav2_pointcloud_review \
  --result-dir '$ResultDirWsl' \
  --input-topic /uav2/livox/lidar \
  --odom-topic /uav2/sunray/gazebo_pose \
  --output-topic /mosim/swarm_formation/uav2/livox_world_accumulated \
  --frame-id world \
  > '$ResultDirWsl/uav2_pointcloud_review.log' 2>&1 &
echo `$! > '$ResultDirWsl/uav2_pointcloud_review.pid'
python3 Scripts/sunray/px4ctrl_pointcloud_review_node.py \
  --node-name mosim_swarm_formation_uav3_pointcloud_review \
  --result-dir '$ResultDirWsl' \
  --input-topic /uav3/livox/lidar \
  --odom-topic /uav3/sunray/gazebo_pose \
  --output-topic /mosim/swarm_formation/uav3/livox_world_accumulated \
  --frame-id world \
  > '$ResultDirWsl/uav3_pointcloud_review.log' 2>&1 &
echo `$! > '$ResultDirWsl/uav3_pointcloud_review.pid'
rviz -d '$RootWsl/Config/rviz/sunray_ros1_swarm_formation_pointcloud_review.rviz' \
  > '$ResultDirWsl/rviz_swarm_formation_pointcloud_review.log' 2>&1 &
echo `$! > '$ResultDirWsl/rviz_swarm_formation_pointcloud_review.pid'
sleep 1
rviz -d '$RootWsl/Config/rviz/sunray_ros1_swarm_formation_grid3d_review.rviz' \
  > '$ResultDirWsl/rviz_swarm_formation_grid3d_review.log' 2>&1 &
echo `$! > '$ResultDirWsl/rviz_swarm_formation_grid3d_review.pid'
"@ })
wait
"@
$encodedReview = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes(
    "wsl -d Ubuntu-20.04 --exec bash -lc `"$($reviewCommand.Replace('`"', '\`"'))`""
))
$review = Start-Process -FilePath "powershell.exe" -ArgumentList @(
    "-NoProfile", "-EncodedCommand", $encodedReview
) -WindowStyle Hidden -PassThru
$review.Id | Set-Content -LiteralPath (Join-Path $ResultDir "review_windows_host_pid.txt") -Encoding ascii

Write-Host "Factory L2 Swarm-Formation review started."
Write-Host ("RunId: " + $RunId)
if ($null -ne $gate) {
    Write-Host ("Gate process: " + $gate.Id)
} else {
    Write-Host "Gate process: attached to existing runtime"
}
if ($null -ne $unrealProcess) {
    Write-Host ("UE process: " + $unrealProcess.Id)
    Write-Host "UE controls: arrow keys orbit; Q cycles formation overview, uav1, uav2, uav3."
}
Write-Host ("Review host process: " + $review.Id)
Write-Host ("RViz enabled: " + (-not $NoRviz))
Write-Host ("Result: " + $ResultDir)
