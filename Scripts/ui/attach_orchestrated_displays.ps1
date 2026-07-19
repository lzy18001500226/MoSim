param(
    [Parameter(Mandatory = $true)][string]$RunId,
    [Parameter(Mandatory = $true)][string]$SessionId,
    [string]$DisplayCsv = "",
    [switch]$Detach,
    [switch]$CloseRvizOnly
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

if ($null -eq ('MoSim.NativeWindow' -as [type])) {
    Add-Type @'
using System;
using System.Runtime.InteropServices;

namespace MoSim {
    [StructLayout(LayoutKind.Sequential)]
    public struct Rect {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    public static class NativeWindow {
        public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
        [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc callback, IntPtr lParam);
        [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr parent, EnumWindowsProc callback, IntPtr lParam);
        [DllImport("user32.dll")] public static extern IntPtr GetDesktopWindow();
        [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
        [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
        [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out Rect rect);
        [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int command);
        public const int SW_HIDE = 0;
    }
}
'@
}

function Test-ProcessHasUsableWindow {
    param([int]$ProcessId)
    $script:mosimTargetWindowProcessId = [uint32]$ProcessId
    $script:mosimUsableWindowFound = $false
    $callback = [MoSim.NativeWindow+EnumWindowsProc] {
        param([IntPtr]$Window, [IntPtr]$Unused)
        [uint32]$windowProcessId = 0
        [MoSim.NativeWindow]::GetWindowThreadProcessId($Window, [ref]$windowProcessId) | Out-Null
        if ($windowProcessId -eq $script:mosimTargetWindowProcessId) {
            $rect = New-Object MoSim.Rect
            if ([MoSim.NativeWindow]::GetWindowRect($Window, [ref]$rect)) {
                $area = ($rect.Right - $rect.Left) * ($rect.Bottom - $rect.Top)
                if ($area -gt 10000) {
                    $script:mosimUsableWindowFound = $true
                    return $false
                }
            }
        }
        return $true
    }
    [MoSim.NativeWindow]::EnumWindows($callback, [IntPtr]::Zero) | Out-Null
    if (-not $script:mosimUsableWindowFound) {
        [MoSim.NativeWindow]::EnumChildWindows([MoSim.NativeWindow]::GetDesktopWindow(), $callback, [IntPtr]::Zero) | Out-Null
    }
    return $script:mosimUsableWindowFound
}

function Hide-ProcessWindows {
    param([int]$ProcessId)
    $script:mosimHiddenWindowCount = 0
    $callback = [MoSim.NativeWindow+EnumWindowsProc] {
        param([IntPtr]$Window, [IntPtr]$Unused)
        [uint32]$windowProcessId = 0
        [MoSim.NativeWindow]::GetWindowThreadProcessId($Window, [ref]$windowProcessId) | Out-Null
        if ($windowProcessId -eq [uint32]$ProcessId -and [MoSim.NativeWindow]::IsWindowVisible($Window)) {
            [MoSim.NativeWindow]::ShowWindow($Window, [MoSim.NativeWindow]::SW_HIDE) | Out-Null
            $script:mosimHiddenWindowCount = $script:mosimHiddenWindowCount + 1
        }
        return $true
    }
    [MoSim.NativeWindow]::EnumWindows($callback, [IntPtr]::Zero) | Out-Null
    return $script:mosimHiddenWindowCount
}

function Wait-AndHide-ProcessWindows {
    param([System.Diagnostics.Process]$Process, [int]$TimeoutSeconds = 45)
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    $hiddenAny = $false
    $windowFound = $false
    $lastHiddenAt = $null
    do {
        $Process.Refresh()
        $hiddenNow = [int](Hide-ProcessWindows -ProcessId $Process.Id)
        if ($hiddenNow -gt 0) {
            $hiddenAny = $true
            $lastHiddenAt = [DateTime]::UtcNow
        }
        # Unreal may create its game window hidden. Count a real client area as
        # readiness even when it has never been visible on the desktop.
        $windowFound = Test-ProcessHasUsableWindow -ProcessId $Process.Id
        # Keep the window hidden briefly after the first appearance so UE's
        # startup resize/show pass cannot flash a standalone desktop window.
        if ($windowFound -and (($hiddenAny -and $lastHiddenAt -and ([DateTime]::UtcNow - $lastHiddenAt).TotalSeconds -ge 2) -or -not $hiddenAny)) {
            break
        }
        Start-Sleep -Milliseconds 100
    } while ([DateTime]::UtcNow -lt $deadline -and -not $Process.HasExited)
    return $windowFound
}

if ($CloseRvizOnly) {
    $stopped = @()
    & wsl.exe -d Ubuntu-20.04 -- bash $DisplayHelper "rviz_stop" $SessionId 2>$null
    $wslStopExitCode = $LASTEXITCODE
    if (Test-Path -LiteralPath $ProcessFile) {
        $records = @(Get-Content -Raw -LiteralPath $ProcessFile | ConvertFrom-Json)
        foreach ($record in @($records | Where-Object { $_.kind -in @("rviz_pointcloud", "rviz_gridmap") })) {
            $process = Get-Process -Id ([int]$record.pid) -ErrorAction SilentlyContinue
            if ($null -ne $process) {
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
                $stopped += $process.Id
            }
        }
    }
    Start-Sleep -Milliseconds 250
    $residual = @()
    if (Test-Path -LiteralPath $ProcessFile) {
        $records = @(Get-Content -Raw -LiteralPath $ProcessFile | ConvertFrom-Json)
        foreach ($record in @($records | Where-Object { $_.kind -in @("rviz_pointcloud", "rviz_gridmap") })) {
            if ($null -ne (Get-Process -Id ([int]$record.pid) -ErrorAction SilentlyContinue)) {
                $residual += [int]$record.pid
            }
        }
    }
    [pscustomobject]@{
        schema = "mosim.rviz_cleanup.status.v1"
        run_id = $RunId
        session_id = $SessionId
        state = if ($residual.Count -eq 0 -and $wslStopExitCode -eq 0) { "closed" } else { "blocked" }
        stopped_process_ids = $stopped
        residual_process_ids = $residual
        wsl_stop_exit_code = $wslStopExitCode
        updated_at = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() / 1000.0
    } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $SessionDir "RVIZ_CLEANUP_STATUS.json") -Encoding utf8
    if ($residual.Count -gt 0 -or $wslStopExitCode -ne 0) { exit 4 }
    exit 0
}

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
function Save-ProcessRecords {
    @($script:records) | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ProcessFile -Encoding utf8
}

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
        # Unreal's game viewport can fail to create a native window when the
        # parent process is launched with CREATE_NO_WINDOW/hidden startup
        # flags. Start it normally, then hide every created window immediately
        # and keep it hidden until QGC reparents it.
        $windowStyle = "Normal"
        $process = Start-Process -FilePath $Executable -ArgumentList $Arguments -PassThru `
            -WindowStyle $windowStyle -RedirectStandardOutput $stdout -RedirectStandardError $stderr
        $startupVisibility = "normal"
if ($Kind -eq "unreal") {
            $startupVisibility = "hidden_until_qgc_embed"
            $script:records += [pscustomobject]@{ kind = $Kind; pid = $process.Id; executable = $Executable; startup_visibility = $startupVisibility }
            Save-ProcessRecords
            $windowReady = Wait-AndHide-ProcessWindows -Process $process -TimeoutSeconds 180
            if (-not $windowReady) {
                throw "unreal_window_startup_timeout_pid_$($process.Id)"
            }
        } else {
            $script:records += [pscustomobject]@{ kind = $Kind; pid = $process.Id; executable = $Executable; startup_visibility = $startupVisibility }
            Save-ProcessRecords
        }
        $script:results += [pscustomobject]@{
            display = $Kind
            state = "launch_requested"
            process_id = $process.Id
            readiness_path = $ReadinessPath
            startup_visibility = $startupVisibility
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
        "rviz_pointcloud", $PlannerProfile, $readinessWsl, $SessionId
    ) "rviz_pointcloud" $readiness
}
if ($Display -contains "rviz_gridmap") {
    $readiness = Join-Path $SessionDir "rviz_gridmap.readiness.json"
    $readinessWsl = "$RootWsl/Results/ui_platform/orchestrator_runs/$RunId/displays/$SessionId/rviz_gridmap.readiness.json"
    Start-TrackedProcess "rviz_gridmap" "wsl.exe" @(
        "-d", "Ubuntu-20.04", "--", "bash", $DisplayHelper,
        "rviz_gridmap", $PlannerProfile, $readinessWsl, $SessionId
    ) "rviz_gridmap" $readiness
}
if ($Display -contains "unreal") {
    $route = & wsl.exe -d Ubuntu-20.04 -- ip route show default
    $match = [regex]::Match(($route -join "`n"), '(?m)^default\s+via\s+(\S+)')
    if (-not $match.Success) {
        $results += [pscustomobject]@{ display = "unreal"; state = "blocked"; reason = "windows_host_address_unavailable" }
    } else {
        $hostAddress = $match.Groups[1].Value
        $ueMetricsWsl = "$RootWsl/Results/ui_platform/orchestrator_runs/$RunId/observability/gazebo_ue_sender.json"
        $ueReceiverMetrics = Join-Path $RunDir "observability\gazebo_ue_receiver.json"
        $ueFrameMetrics = Join-Path $RunDir "observability\ue_frame_timing.json"
        Start-TrackedProcess "unreal_bridge" "wsl.exe" @(
            "-d", "Ubuntu-20.04", "--", "bash", $DisplayHelper, "unreal_bridge", $hostAddress, $SessionId,
            $RunId, $ueMetricsWsl
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
                "-MoSimFollowCameraRotationInterpSpeed=0", "-MoSimNoReviewCollision",
                "-MoSimEmbeddedViewport", "-MoSimObservabilityRunId=$RunId",
                "-MoSimUeReceiverMetrics=$ueReceiverMetrics", "-MoSimUeFrameMetrics=$ueFrameMetrics"
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
        state = "blocked"
        reason = "mworks_result_requires_model_studio_live_session"
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

Save-ProcessRecords
$blockedResults = @($results | Where-Object { $_.state -eq "blocked" })
$readyResults = @($results | Where-Object { $_.state -in @("ready", "running") })
$state = if ($blockedResults.Count -gt 0) { "blocked" } elseif ($readyResults.Count -gt 0) { "attached" } else { "blocked" }
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
