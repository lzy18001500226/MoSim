[CmdletBinding()]
param(
    [string]$ProfilePath = "Config/profiles/experiments/px4ctrl_ground_standby_v1.json",
    [string]$ControllerId = "px4ctrl",
    [int]$VehicleCount = 1
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "launcher_common.ps1")

function Show-Stage {
    param([string]$Message)
    Write-Host ("[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $Message)
}

Start-MoSimOrchestratorService

$active = Get-MoSimActiveRun
$state = $null
if ($null -ne $active -and $active.run_id) {
    $state = Invoke-MoSimOrchestratorClient -Arguments @(
        "get_run_state", "--run-id", [string]$active.run_id
    ) -AllowRejected
}

if ($null -ne $state -and $state.accepted -and $state.manifest.lifecycle_state -in @("starting", "running")) {
    $runId = [string]$state.run_id
    Show-Stage "Reusing active flight simulation: $runId"
} else {
    if (-not (Test-Path -LiteralPath (Join-Path $script:MoSimProjectRoot $ProfilePath))) {
        throw "profile_missing: $ProfilePath"
    }
    Show-Stage "Preparing Gazebo/PX4/MAVROS flight simulation..."
    $prepared = Invoke-MoSimOrchestratorClient -Arguments @(
        "prepare_run", "--profile-path", $ProfilePath,
        "--controller-id", $ControllerId, "--vehicle-count", [string]$VehicleCount
    )
    $runId = [string]$prepared.run_id
    $started = Invoke-MoSimOrchestratorClient -Arguments @("start_run", "--run-id", $runId)
    Show-Stage "Runtime launch accepted: $($started.reason_code)"
}

$runDir = Get-MoSimRunDirectory -RunId $runId
$runtimeStatusPath = Join-Path $runDir "RUNTIME_STATUS.json"
$preflightPath = Join-Path $runDir "runtime/px4_ekf_global_origin.txt"
$mavlinkPath = Join-Path $runDir "observability/mavlink_qgc.json"

Write-Host ""
Write-Host "MoSim flight simulation terminal"
Write-Host "Run ID : $runId"
Write-Host "Logs   : $runDir"
Write-Host "Keep this window open while testing. Closing it does not stop the simulation."
Write-Host "Use the Stop All MoSim Simulation launcher to stop the managed run."
Write-Host ""

$lastLine = ""
while ($true) {
    $status = $null
    if (Test-Path -LiteralPath $runtimeStatusPath) {
        try { $status = Get-Content -Raw -LiteralPath $runtimeStatusPath | ConvertFrom-Json } catch { $status = $null }
    }
    $preflightReady = (Test-Path -LiteralPath $preflightPath) -and
        ((Get-Content -Raw -LiteralPath $preflightPath -ErrorAction SilentlyContinue) -match '(?m)^preflight_ready=true$')
    $qgcLinks = 0
    if (Test-Path -LiteralPath $mavlinkPath) {
        try {
            $mavlink = Get-Content -Raw -LiteralPath $mavlinkPath | ConvertFrom-Json
            $qgcLinks = [int]$mavlink.connected_link_count
        } catch { $qgcLinks = 0 }
    }
    $statusName = if ($null -ne $status) { [string]$status.status } else { "starting" }
    $reason = if ($null -ne $status) { [string]$status.reason_code } else { "runtime_status_pending" }
    $missing = if ($null -ne $status) { @($status.missing_readiness) -join "," } else { "status_file" }
    if (-not $missing) { $missing = "none" }
    $line = "state=$statusName reason=$reason preflight=$preflightReady qgc_links=$qgcLinks missing=$missing"
    if ($line -ne $lastLine) {
        Show-Stage $line
        $lastLine = $line
    }
    if ($statusName -in @("blocked", "failed", "stopped", "completed")) {
        break
    }
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "Flight simulation ended. Review logs at: $runDir"
pause
