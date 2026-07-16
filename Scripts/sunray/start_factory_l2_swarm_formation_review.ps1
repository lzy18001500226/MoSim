param(
    [string]$RunId = ("factory_l2_swarm_formation_review_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [string]$AcceptedRunId = "factory_l2_swarm_formation_obstacle_runtime_r34_20260716",
    [int]$StartupTimeoutS = 240,
    [int]$ReviewTotalTimeoutS = 1200,
    [switch]$AttachOnly,
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

foreach ($gatePath in @($AcceptedBackendGate, $AcceptedFormationGate)) {
    if (-not (Test-Path -LiteralPath $gatePath)) {
        throw "RViz review is closed because accepted gate evidence is missing: $gatePath"
    }
    $gatePacket = Get-Content -Raw -LiteralPath $gatePath | ConvertFrom-Json
    if ($gatePacket.status -ne "passed" -or @($gatePacket.blockers).Count -ne 0) {
        throw "RViz review is closed because accepted gate evidence did not pass: $gatePath"
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
        throw "Swarm-Formation gate exited before RViz topics became ready (exit $($gate.ExitCode))."
    }
    & wsl -d Ubuntu-20.04 -- bash -lc "source /opt/ros/noetic/setup.bash && rostopic list 2>/dev/null | grep -q '^/mosim/goal5/uav1/truth_path$'"
    if ($LASTEXITCODE -eq 0) {
        $ready = $true
        break
    }
    Start-Sleep -Seconds 2
}
if (-not $ready) {
    throw "Timed out after ${StartupTimeoutS}s waiting for the Swarm-Formation review topics."
}

$reviewCommand = @"
cd '$RootWsl'
source /opt/ros/noetic/setup.bash
python3 Scripts/sunray/swarm_body_axes_marker_node.py \
  --uav-num 3 \
  --marker-topic /mosim/goal5/body_axes \
  --axis-length-m 0.60 \
  --shaft-m 0.04 \
  --head-diameter-m 0.12 \
  --head-length-m 0.16 \
  > '$ResultDirWsl/swarm_body_axes_marker.log' 2>&1 &
echo `$! > '$ResultDirWsl/swarm_body_axes_marker.pid'
rviz -d '$RootWsl/Config/rviz/sunray_ros1_goal5_diff_swarm_pointcloud_review.rviz' \
  > '$ResultDirWsl/rviz_swarm_formation_pointcloud_review.log' 2>&1 &
echo `$! > '$ResultDirWsl/rviz_swarm_formation_pointcloud_review.pid'
sleep 1
rviz -d '$RootWsl/Config/rviz/sunray_ros1_goal5_diff_swarm_grid3d_review.rviz' \
  > '$ResultDirWsl/rviz_swarm_formation_grid3d_review.log' 2>&1 &
echo `$! > '$ResultDirWsl/rviz_swarm_formation_grid3d_review.pid'
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
Write-Host ("RViz host process: " + $review.Id)
Write-Host ("Result: " + $ResultDir)
