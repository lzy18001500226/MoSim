[CmdletBinding()]
param(
    [string]$ProfilePath = "Config/profiles/experiments/px4ctrl_ground_standby_v1.json",
    [string]$ControllerId = "px4ctrl",
    [int]$VehicleCount = 1
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$Client = Join-Path $ProjectRoot "Scripts/ui/orchestrator_client.py"
$Service = Join-Path $ProjectRoot "Scripts/ui/orchestrator_service.py"
$QgcLauncher = Join-Path $ProjectRoot "Scripts/ui/run_flight_console.ps1"
$LogDir = Join-Path $ProjectRoot "Results/ui_platform/startup"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

if (Get-Process -Name "MoSimFlightConsole" -ErrorAction SilentlyContinue) {
    throw "qgc_already_running: close the existing Flight Console, then run Start_MoSim_QGC.cmd again"
}

function Get-OrchestratorService {
    return @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine -like "*Scripts*orchestrator_service.py*" })
}

if ((Get-OrchestratorService).Count -eq 0) {
    $serviceOut = Join-Path $LogDir "orchestrator.stdout.log"
    $serviceErr = Join-Path $LogDir "orchestrator.stderr.log"
    Start-Process -FilePath "python.exe" -WorkingDirectory $ProjectRoot `
        -ArgumentList @($Service) -WindowStyle Hidden -RedirectStandardOutput $serviceOut `
        -RedirectStandardError $serviceErr | Out-Null
    Start-Sleep -Milliseconds 750
}

function Invoke-OrchestratorClient {
    param([string[]]$Arguments)
    $raw = & python.exe $Client @Arguments --format json --timeout-s 5 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0 -and $raw -notmatch '"accepted"\s*:\s*true') {
        throw "orchestrator_request_failed: $raw"
    }
    try {
        return ($raw | ConvertFrom-Json)
    } catch {
        throw "orchestrator_response_invalid: $raw"
    }
}

function Stop-StaleManagedUnreal {
    $records = Get-ChildItem -Path (Join-Path $ProjectRoot "Results/ui_platform/orchestrator_runs") `
        -Recurse -Filter "DISPLAY_PROCESSES.json" -File -ErrorAction SilentlyContinue
    foreach ($file in $records) {
        try { $entries = Get-Content -Raw -LiteralPath $file.FullName | ConvertFrom-Json } catch { continue }
        foreach ($entry in $entries) {
            if ([string]$entry.kind -ne "unreal") { continue }
            [int]$managedPid = 0
            if (-not [int]::TryParse([string]$entry.pid, [ref]$managedPid) -or $managedPid -le 0) { continue }
            $process = Get-Process -Id $managedPid -ErrorAction SilentlyContinue
            if ($null -ne $process -and $process.ProcessName -eq "UnrealEditor") {
                Write-Output "Stopping stale managed UE process PID $($process.Id)..."
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot $ProfilePath))) {
    throw "default_profile_missing: $ProfilePath"
}

Stop-StaleManagedUnreal

$prepared = Invoke-OrchestratorClient -Arguments @(
    "prepare_run", "--profile-path", $ProfilePath,
    "--controller-id", $ControllerId, "--vehicle-count", [string]$VehicleCount
)
if (-not $prepared.accepted) {
    throw "prepare_run_blocked: $($prepared.reason_code)"
}
$runId = [string]$prepared.run_id

$started = Invoke-OrchestratorClient -Arguments @(
    "start_run", "--run-id", $runId
)
if (-not $started.accepted) {
    throw "start_run_blocked: $($started.reason_code)"
}

$display = Invoke-OrchestratorClient -Arguments @(
    "prepare_display_session", "--run-id", $runId, "--display", "unreal"
)
if (-not $display.accepted) {
    throw "prepare_display_blocked: $($display.reason_code)"
}
$sessionId = [string]$display.session.session_id

$attached = Invoke-OrchestratorClient -Arguments @(
    "attach_display", "--session-id", $sessionId
)
if (-not $attached.accepted) {
    throw "attach_display_blocked: $($attached.reason_code)"
}

$displayStatus = Join-Path $ProjectRoot "Results/ui_platform/orchestrator_runs/$runId/displays/$sessionId/DISPLAY_STATUS.json"
$readyDeadline = [DateTime]::UtcNow.AddSeconds(195)
do {
    if (Test-Path -LiteralPath $displayStatus) {
        try {
            $status = Get-Content -Raw -LiteralPath $displayStatus | ConvertFrom-Json
            $unreal = @($status.displays | Where-Object { $_.display -eq "unreal" }) | Select-Object -First 1
            if ($status.state -eq "attached" -and $unreal.state -in @("ready", "running")) {
                Write-Output "UE display is ready for run $runId. Starting QGC..."
                break
            }
            if ($status.state -eq "blocked") {
                throw "ue_display_start_blocked: $($unreal.reason)"
            }
        } catch {
            if ($_.Exception.Message -like "ue_display_start_blocked:*") { throw }
        }
    }
    Write-Output "Waiting for UE viewport... ($([int]([Math]::Max(0, ($readyDeadline - [DateTime]::UtcNow).TotalSeconds)))s remaining)"
    Start-Sleep -Seconds 2
} while ([DateTime]::UtcNow -lt $readyDeadline)

if (-not $status -or $status.state -ne "attached") {
    throw "ue_display_readiness_timeout: inspect $displayStatus and the display logs"
}

# Put the operator surface on screen as soon as UE is ready. Runtime readiness
# is reported inside QGC and must not leave the user staring at a standalone UE
# window when PX4/MAVROS startup is delayed or blocked.
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $QgcLauncher
if ($LASTEXITCODE -ne 0) {
    throw "qgc_start_failed: run_flight_console.ps1 exited with $LASTEXITCODE"
}

$runtimeStatus = Join-Path $ProjectRoot "Results/ui_platform/orchestrator_runs/$runId/RUNTIME_STATUS.json"
$preflightStatus = Join-Path $ProjectRoot "Results/ui_platform/orchestrator_runs/$runId/runtime/px4_ekf_global_origin.txt"
$runtimeDeadline = [DateTime]::UtcNow.AddSeconds(240)
$runtimeReady = $false
do {
    if (Test-Path -LiteralPath $runtimeStatus) {
        try {
            $runtime = Get-Content -Raw -LiteralPath $runtimeStatus | ConvertFrom-Json
            $preflightReady = (Test-Path -LiteralPath $preflightStatus) -and
                ((Get-Content -Raw -LiteralPath $preflightStatus) -match '(?m)^preflight_ready=true$')
            if ($runtime.status -eq "running" -and @($runtime.missing_readiness).Count -eq 0 -and $preflightReady) {
                Write-Output "PX4/MAVROS ground standby is ready for run $runId."
                $runtimeReady = $true
                break
            }
            if ($runtime.status -in @("blocked", "failed", "stopped")) {
                throw "runtime_start_blocked: $($runtime.reason_code)"
            }
        } catch {
            if ($_.Exception.Message -like "runtime_start_blocked:*") { throw }
        }
    }
    Write-Output "Waiting for PX4/MAVROS ground standby... ($([int]([Math]::Max(0, ($runtimeDeadline - [DateTime]::UtcNow).TotalSeconds)))s remaining)"
    Start-Sleep -Seconds 2
} while ([DateTime]::UtcNow -lt $runtimeDeadline)

if (-not $runtimeReady) {
    throw "runtime_readiness_timeout: inspect $runtimeStatus, $preflightStatus, and the runtime logs"
}

Write-Output "PX4/MAVROS runtime is ready for QGC operation."
exit 0
