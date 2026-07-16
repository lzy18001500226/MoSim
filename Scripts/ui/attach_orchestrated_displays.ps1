param(
    [Parameter(Mandatory = $true)][string]$RunId,
    [Parameter(Mandatory = $true)][string]$SessionId,
    [string]$DisplayCsv = "",
    [switch]$Detach
)

$ErrorActionPreference = "Stop"
$Root = "C:\Users\HP\Desktop\MoSim"
if ($RunId -notmatch '^run-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$') { throw "invalid run id" }
if ($SessionId -notmatch '^display-[A-Za-z0-9]{10}$') { throw "invalid display session id" }
$RunDir = Join-Path $Root "Results\ui_platform\orchestrator_runs\$RunId"
$SessionDir = Join-Path $RunDir "displays\$SessionId"
$ProcessFile = Join-Path $SessionDir "DISPLAY_PROCESSES.json"
$StatusFile = Join-Path $SessionDir "DISPLAY_STATUS.json"
New-Item -ItemType Directory -Force -Path $SessionDir | Out-Null

if ($Detach) {
    $stopped = @()
    if (Test-Path -LiteralPath $ProcessFile) {
        $records = @(Get-Content -Raw -LiteralPath $ProcessFile | ConvertFrom-Json)
        foreach ($record in $records) {
            $process = Get-Process -Id ([int]$record.pid) -ErrorAction SilentlyContinue
            if ($null -ne $process) {
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
                $stopped += $process.Id
            }
        }
    }
    [pscustomobject]@{
        schema = "mosim.display_session.status.v1"
        run_id = $RunId
        session_id = $SessionId
        state = "detached"
        stopped_process_ids = $stopped
        updated_at = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() / 1000.0
    } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $StatusFile -Encoding utf8
    exit 0
}

$Display = @($DisplayCsv.Split(',', [System.StringSplitOptions]::RemoveEmptyEntries))
$Allowed = @("rviz_pointcloud", "rviz_gridmap", "unreal", "mworks_result")
foreach ($item in $Display) {
    if ($item -notin $Allowed) { throw "unsupported display: $item" }
}

$records = @()
$results = @()
function Start-TrackedProcess {
    param([string]$Kind, [string]$Executable, [string[]]$Arguments, [string]$LogName)
    try {
        $stdout = Join-Path $SessionDir ($LogName + ".stdout.log")
        $stderr = Join-Path $SessionDir ($LogName + ".stderr.log")
        $process = Start-Process -FilePath $Executable -ArgumentList $Arguments -PassThru `
            -RedirectStandardOutput $stdout -RedirectStandardError $stderr
        $script:records += [pscustomobject]@{ kind = $Kind; pid = $process.Id; executable = $Executable }
        $script:results += [pscustomobject]@{ display = $Kind; state = "launch_requested"; process_id = $process.Id }
    } catch {
        $script:results += [pscustomobject]@{ display = $Kind; state = "blocked"; reason = $_.Exception.Message }
    }
}

$RootWsl = "/mnt/c/Users/HP/Desktop/MoSim"
if ($Display -contains "rviz_pointcloud") {
    $command = "source /opt/ros/noetic/setup.bash && rviz -d '$RootWsl/Config/rviz/sunray_ros1_mid360_cloud_review.rviz'"
    Start-TrackedProcess "rviz_pointcloud" "wsl.exe" @("-d", "Ubuntu-20.04", "--", "bash", "-lc", $command) "rviz_pointcloud"
}
if ($Display -contains "rviz_gridmap") {
    $command = "source /opt/ros/noetic/setup.bash && rviz -d '$RootWsl/Config/rviz/sunray_ros1_ego_grid_trajectory_review.rviz'"
    Start-TrackedProcess "rviz_gridmap" "wsl.exe" @("-d", "Ubuntu-20.04", "--", "bash", "-lc", $command) "rviz_gridmap"
}
if ($Display -contains "unreal") {
    $route = & wsl.exe -d Ubuntu-20.04 -- ip route show default
    $match = [regex]::Match(($route -join "`n"), '(?m)^default\s+via\s+(\S+)')
    if (-not $match.Success) {
        $results += [pscustomobject]@{ display = "unreal"; state = "blocked"; reason = "windows_host_address_unavailable" }
    } else {
        $hostAddress = $match.Groups[1].Value
        $bridge = "cd '$RootWsl' && source /opt/ros/noetic/setup.bash && python3 -u Scripts/UE5/stream_ros1_state_to_ue_udp.py --odom-topic /uav1/sunray/gazebo_pose --position-cmd-topic /position_cmd --link-states-topic /gazebo/link_states --mavros-state-topic /uav1/mavros/state --host '$hostAddress' --port 5005 --rate-hz 100 --vehicle-id uav1 --scene-id factory --map-id local_factoryenvironmentcollect --controller-profile orchestrated --planner-profile none"
        Start-TrackedProcess "unreal_bridge" "wsl.exe" @("-d", "Ubuntu-20.04", "--", "bash", "-lc", $bridge) "unreal_bridge"
        $editor = "D:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe"
        $project = Join-Path $Root "UE5\MoSimSceneLibrary\MoSimSceneLibrary.uproject"
        if ((Test-Path -LiteralPath $editor) -and (Test-Path -LiteralPath $project)) {
            $ueArgs = @(
                $project, "-game", "-windowed", "-ResX=1440", "-ResY=810", "-NoSplash",
                "/Game/Maps/Demonstration?game=/Script/MoSimSceneLibrary.MoSimSceneLibraryGameMode",
                "-MoSimSimulationReview", "-MoSimDayReview", "-MoSimPlaybackActorCount=1",
                "-MoSimPlaybackBaseUdpPort=5005", "-MoSimFollowPlaybackCamera",
                "-MoSimFollowCameraBackCm=231.25", "-MoSimFollowCameraRightCm=0",
                "-MoSimFollowCameraUpCm=95", "-MoSimFollowCameraLocationInterpSpeed=0",
                "-MoSimFollowCameraRotationInterpSpeed=0", "-MoSimNoReviewCollision"
            )
            Start-TrackedProcess "unreal" $editor $ueArgs "unreal"
        } else {
            $results += [pscustomobject]@{ display = "unreal"; state = "blocked"; reason = "unreal_runtime_missing" }
        }
    }
}
if ($Display -contains "mworks_result") {
    $results += [pscustomobject]@{
        display = "mworks_result"
        state = "prepared"
        reason = "opened_by_model_studio_after_result_packet"
    }
}

@($records) | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ProcessFile -Encoding utf8
$state = if (@($results | Where-Object state -eq "launch_requested").Count -gt 0) { "attached" } else { "blocked" }
[pscustomobject]@{
    schema = "mosim.display_session.status.v1"
    run_id = $RunId
    session_id = $SessionId
    state = $state
    displays = $results
    updated_at = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() / 1000.0
    claim_boundary = "Process launch evidence only; RViz and UE visual correctness require same-run review."
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $StatusFile -Encoding utf8
exit 0
