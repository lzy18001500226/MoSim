param(
    [Parameter(Mandatory = $true)][string]$RunId,
    [Parameter(Mandatory = $true)][string]$SessionId,
    [string]$DisplayCsv = "",
    [switch]$Detach
)

$ErrorActionPreference = "Stop"
$Root = "C:\Users\HP\Desktop\MoSim"
$RootWsl = "/mnt/c/Users/HP/Desktop/MoSim"
$DisplayHelper = "$RootWsl/Scripts/ui/launch_ros1_display.sh"
if ($RunId -notmatch '^run-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$') { throw "invalid run id" }
if ($SessionId -notmatch '^display-[A-Za-z0-9]{10}$') { throw "invalid display session id" }
$RunDir = Join-Path $Root "Results\ui_platform\orchestrator_runs\$RunId"
$SessionDir = Join-Path $RunDir "displays\$SessionId"
$ProcessFile = Join-Path $SessionDir "DISPLAY_PROCESSES.json"
$StatusFile = Join-Path $SessionDir "DISPLAY_STATUS.json"
New-Item -ItemType Directory -Force -Path $SessionDir | Out-Null

$PlannerProfile = "unknown"
$ManifestFile = Join-Path $RunDir "RUN_MANIFEST.json"
if (Test-Path -LiteralPath $ManifestFile) {
    $manifest = Get-Content -Raw -LiteralPath $ManifestFile | ConvertFrom-Json
    if ($manifest.profile_path) {
        $profileFile = Join-Path $Root ([string]$manifest.profile_path)
        if (Test-Path -LiteralPath $profileFile) {
            $profile = Get-Content -Raw -LiteralPath $profileFile | ConvertFrom-Json
            if ($profile.experiment_profile.planner_profile) {
                $PlannerProfile = [string]$profile.experiment_profile.planner_profile
            }
        }
    }
}

if ($Detach) {
    $stopped = @()
    & wsl.exe -d Ubuntu-20.04 -- bash $DisplayHelper "unreal_bridge_stop" $SessionId 2>$null
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
    param(
        [string]$Kind,
        [string]$Executable,
        [string[]]$Arguments,
        [string]$LogName,
        [string]$ReadinessPath = ""
    )
    try {
        $stdout = Join-Path $SessionDir ($LogName + ".stdout.log")
        $stderr = Join-Path $SessionDir ($LogName + ".stderr.log")
        $process = Start-Process -FilePath $Executable -ArgumentList $Arguments -PassThru `
            -RedirectStandardOutput $stdout -RedirectStandardError $stderr
        $script:records += [pscustomobject]@{ kind = $Kind; pid = $process.Id; executable = $Executable }
        $script:results += [pscustomobject]@{
            display = $Kind
            state = "launch_requested"
            process_id = $process.Id
            readiness_path = $ReadinessPath
        }
    } catch {
        $script:results += [pscustomobject]@{ display = $Kind; state = "blocked"; reason = $_.Exception.Message }
    }
}

if ($Display -contains "rviz_pointcloud") {
    $readiness = Join-Path $SessionDir "rviz_pointcloud.readiness.json"
    $readinessWsl = "$RootWsl/Results/ui_platform/orchestrator_runs/$RunId/displays/$SessionId/rviz_pointcloud.readiness.json"
    Start-TrackedProcess "rviz_pointcloud" "wsl.exe" @(
        "-d", "Ubuntu-20.04", "--", "bash", $DisplayHelper,
        "rviz_pointcloud", $PlannerProfile, $readinessWsl
    ) "rviz_pointcloud" $readiness
}
if ($Display -contains "rviz_gridmap") {
    $readiness = Join-Path $SessionDir "rviz_gridmap.readiness.json"
    $readinessWsl = "$RootWsl/Results/ui_platform/orchestrator_runs/$RunId/displays/$SessionId/rviz_gridmap.readiness.json"
    Start-TrackedProcess "rviz_gridmap" "wsl.exe" @(
        "-d", "Ubuntu-20.04", "--", "bash", $DisplayHelper,
        "rviz_gridmap", $PlannerProfile, $readinessWsl
    ) "rviz_gridmap" $readiness
}
if ($Display -contains "unreal") {
    $route = & wsl.exe -d Ubuntu-20.04 -- ip route show default
    $match = [regex]::Match(($route -join "`n"), '(?m)^default\s+via\s+(\S+)')
    if (-not $match.Success) {
        $results += [pscustomobject]@{ display = "unreal"; state = "blocked"; reason = "windows_host_address_unavailable" }
    } else {
        $hostAddress = $match.Groups[1].Value
        Start-TrackedProcess "unreal_bridge" "wsl.exe" @(
            "-d", "Ubuntu-20.04", "--", "bash", $DisplayHelper, "unreal_bridge", $hostAddress, $SessionId
        ) "unreal_bridge"
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

if (@($results | Where-Object state -eq "launch_requested").Count -gt 0) {
    $deadline = [DateTime]::UtcNow.AddSeconds(70)
    do {
        $pendingReadiness = @($results | Where-Object {
            $_.state -eq "launch_requested" -and $_.readiness_path -and
            -not (Test-Path -LiteralPath $_.readiness_path)
        })
        if ($pendingReadiness.Count -eq 0) { break }
        Start-Sleep -Milliseconds 500
    } while ([DateTime]::UtcNow -lt $deadline)

    foreach ($result in @($results | Where-Object state -eq "launch_requested")) {
        $process = Get-Process -Id ([int]$result.process_id) -ErrorAction SilentlyContinue
        if ($result.readiness_path -and (Test-Path -LiteralPath $result.readiness_path)) {
            $readiness = Get-Content -Raw -LiteralPath $result.readiness_path | ConvertFrom-Json
            if ($readiness.status -eq "ready") {
                $result.state = "ready"
                $result | Add-Member -NotePropertyName fixed_frame -NotePropertyValue $readiness.fixed_frame -Force
                $result | Add-Member -NotePropertyName rviz_config -NotePropertyValue $readiness.rviz_config -Force
                $result | Add-Member -NotePropertyName required_topics -NotePropertyValue $readiness.required_topics -Force
            } else {
                $result.state = "blocked"
                $result | Add-Member -NotePropertyName reason -NotePropertyValue $readiness.reason_code -Force
            }
        } elseif ($result.readiness_path) {
            $result.state = "blocked"
            $result | Add-Member -NotePropertyName reason -NotePropertyValue "display_readiness_timeout" -Force
        } elseif ($null -eq $process) {
            $result.state = "blocked"
            $result | Add-Member -NotePropertyName reason -NotePropertyValue "process_exited_during_startup" -Force
        } else {
            $result.state = "running"
        }
    }
}

@($records) | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ProcessFile -Encoding utf8
$state = if (@($results | Where-Object { $_.state -in @("ready", "running") }).Count -gt 0) { "attached" } else { "blocked" }
[pscustomobject]@{
    schema = "mosim.display_session.status.v1"
    run_id = $RunId
    session_id = $SessionId
    state = $state
    planner_profile = $PlannerProfile
    displays = $results
    updated_at = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() / 1000.0
    claim_boundary = "RViz ready means same-run topic samples and fixed-frame agreement passed; visual correctness still requires manual review."
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $StatusFile -Encoding utf8
exit 0
