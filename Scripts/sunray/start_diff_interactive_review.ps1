param(
    [string]$RunId = ("review_diff_interactive_guard_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    [int]$ReviewHoldS = 0,
    [switch]$SkipPreflight,
    [switch]$OpenUnrealLiveMirror,
    [int]$UnrealUdpPort = 5005,
    [string]$WorldFileWsl = "",
    [string]$GazeboModelPathPrefixWsl = ""
)

$ErrorActionPreference = "Stop"
$ProjectRootWin = "C:\Users\HP\Desktop\MoSim"
$ProjectRootWsl = "/mnt/c/Users/HP/Desktop/MoSim"
$ResultDirWin = Join-Path $ProjectRootWin ("Results\sunray_ros1\" + $RunId)
$ResultDirWsl = $ProjectRootWsl + "/Results/sunray_ros1/" + $RunId
$TotalTimeoutS = if ($ReviewHoldS -gt 0) { $ReviewHoldS + 180 } else { 0 }

New-Item -ItemType Directory -Force -Path $ResultDirWin | Out-Null

function Start-UnrealLiveMirrorWindow {
    $ue = "D:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe"
    $uproject = Join-Path $ProjectRootWin "UE5\MoSimSceneLibrary\MoSimSceneLibrary.uproject"
    if (!(Test-Path -LiteralPath $ue)) {
        throw "UnrealEditor.exe not found: $ue"
    }
    if (!(Test-Path -LiteralPath $uproject)) {
        throw "Unreal project not found: $uproject"
    }

    Get-CimInstance Win32_Process -Filter "name = 'UnrealEditor.exe'" |
        Where-Object { $_.CommandLine -like '*MoSimSceneLibrary.uproject*' -and $_.CommandLine -like '* -game*' } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2

    $args = @(
        $uproject,
        "-game",
        "-windowed",
        "-ResX=1280",
        "-ResY=720",
        "-NoSplash",
        "/Game/Maps/Demonstration?game=/Script/MoSimSceneLibrary.MoSimSceneLibraryGameMode",
        "-MoSimSimulationReview",
        "-MoSimDayReview",
        "-MoSimReviewSunIntensity=6.0",
        "-MoSimReviewSkyLightIntensity=2.0",
        "-MoSimReviewExposureBias=0.0",
        "-MoSimPlaybackActorCount=1",
        "-MoSimPlaybackBaseUdpPort=$UnrealUdpPort",
        "-MoSimFollowPlaybackCamera",
        "-MoSimFollowCameraBackCm=55",
        "-MoSimFollowCameraRightCm=-14",
        "-MoSimFollowCameraUpCm=28",
        "-MoSimFollowCameraLocationInterpSpeed=0",
        "-MoSimFollowCameraRotationInterpSpeed=0",
        "-MoSimNoReviewCollision"
    )
    Start-Process -FilePath $ue -ArgumentList $args | Out-Null
}

if ($OpenUnrealLiveMirror) {
    Start-UnrealLiveMirrorWindow
}

$envParts = @(
    "RUN_ID=$RunId",
    "RESULT_DIR=$ResultDirWsl",
    "PLANNER_VARIANT=diff_planner",
    "GUI=false",
    "OPEN_RVIZ=true",
    "KEEP_ALIVE=true",
    "DIFF_INTERACTIVE_CLICK_GOAL=true",
    "DIFF_INTERACTIVE_YAW_SCAN_ENABLE=true",
    "DIFF_INTERACTIVE_YAW_SCAN_AFTER_GOAL=true",
    "DIFF_INTERACTIVE_YAW_SCAN_DELTA_RAD=3.141592653589793",
    "DIFF_INTERACTIVE_YAW_SCAN_DURATION_S=6.0",
    "DIFF_INTERACTIVE_YAW_SCAN_SETTLE_S=1.0",
    "DIFF_INTERACTIVE_YAW_SCAN_DISABLE_CMD_ADAPTER=true",
    "DIFF_INTERACTIVE_YAW_SCAN_REENABLE_CMD_ADAPTER=false",
    "DIFF_CLICK_MAX_GOAL_DISTANCE_XY=0",
    "DIFF_ENABLE_CMD_SAFETY_ADAPTER=true",
    "DIFF_CLICK_STATIC_PATH_GUARD=false",
    "DIFF_CMD_INVALID_Z_POLICY=clamp",
    "DIFF_CMD_MIN_Z=0.95",
    "DIFF_CMD_MAX_Z=1.15",
    "DIFF_CMD_SAFETY_MAX_POSITION_JUMP_M=0",
    "DIFF_CMD_SAFETY_MAX_POSITION_JUMP_SPEED_MPS=3.0",
    "EGO_VIRTUAL_CEIL_HEIGHT=1.15",
    "EGO_VISUALIZATION_TRUNCATE_HEIGHT=1.25",
    "GOAL4_RECORD_HZ=100",
    "GOAL4_RECORD_CMD_HZ=100",
    "GOAL4_MAX_PATH_POINTS=0",
    "GOAL4_PATH_PUBLISH_HZ=20",
    "GOAL4_REVIEW_HOLD_PATH_PUBLISH_HZ=10",
    "POINTCLOUD_REVIEW_VOXEL_SIZE_M=0.08",
    "POINTCLOUD_MIN_WORLD_Z_M=0.20",
    "OCCUPANCY_REVIEW_MIN_Z=0.20",
    "UE_LIVE_MIRROR=$($OpenUnrealLiveMirror.ToString().ToLowerInvariant())",
    "UE_LIVE_MIRROR_HOST=auto",
    "UE_LIVE_MIRROR_PORT=$UnrealUdpPort",
    "UE_LIVE_MIRROR_RATE_HZ=30",
    "EGO_MAX_VEL=0.4",
    "EGO_MAX_ACC=0.5",
    "TOTAL_TIMEOUT_S=$TotalTimeoutS",
    "DIFF_INTERACTIVE_REVIEW_HOLD_S=$ReviewHoldS"
)

$preflight = if ($SkipPreflight) {
    "echo skipped > '$ResultDirWsl/preflight_skipped.txt'"
} else {
    "bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh > '$ResultDirWsl/preflight.log' 2>&1"
}

$extraExports = @()
if ($WorldFileWsl -ne "") {
    $extraExports += "export WORLD_FILE='$WorldFileWsl'"
}
if ($GazeboModelPathPrefixWsl -ne "") {
    $extraExports += "export GAZEBO_MODEL_PATH='$GazeboModelPathPrefixWsl':`"${GAZEBO_MODEL_PATH:-}`""
}
$extraExportBlock = $extraExports -join "`n"

$bashStatus = '$?'
$command = @"
cd $ProjectRootWsl
mkdir -p '$ResultDirWsl'
date --iso-8601=seconds > '$ResultDirWsl/background_start_marker.txt'
$preflight || { echo $bashStatus > '$ResultDirWsl/preflight_exit_code.txt'; exit 2; }
echo 0 > '$ResultDirWsl/preflight_exit_code.txt'
$extraExportBlock
$($envParts -join " ") bash Scripts/sunray/run_px4ctrl_ego_single_gate.sh > '$ResultDirWsl/background_launcher.log' 2>&1
echo $bashStatus > '$ResultDirWsl/background_exit_code.txt'
"@

$encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes("wsl -d Ubuntu-20.04 --exec bash -lc " + '"' + $command.Replace('"', '\"') + '"'))
$proc = Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile", "-EncodedCommand", $encoded) -WindowStyle Hidden -PassThru

[pscustomobject]@{
    RunId = $RunId
    ProcessId = $proc.Id
    ResultDir = $ResultDirWin
}
