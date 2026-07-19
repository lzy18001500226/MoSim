[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "launcher_common.ps1")

Start-MoSimOrchestratorService
$active = Get-MoSimActiveRun
if ($null -eq $active -or -not $active.run_id) {
    Write-Output "No active MoSim run is recorded."
    exit 0
}

$runId = [string]$active.run_id
$runDir = Get-MoSimRunDirectory -RunId $runId
Write-Output "Stopping managed MoSim run: $runId"

Get-Process -Name "MoSimFlightConsole" -ErrorAction SilentlyContinue |
    Stop-Process -Force -ErrorAction SilentlyContinue

$displayFiles = @(Get-ChildItem -Path (Join-Path $runDir "displays") `
    -Recurse -Filter "DISPLAY_PROCESSES.json" -File -ErrorAction SilentlyContinue)
foreach ($file in $displayFiles) {
    try { $records = @(Get-Content -Raw -LiteralPath $file.FullName | ConvertFrom-Json) } catch { continue }
    foreach ($record in $records) {
        $pidValue = 0
        if (-not [int]::TryParse([string]$record.pid, [ref]$pidValue)) { continue }
        $process = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
        if ($null -eq $process) { continue }
        $allowed = switch ([string]$record.kind) {
            "unreal" { $process.ProcessName -eq "UnrealEditor" }
            "unreal_bridge" { $process.ProcessName -in @("wsl", "wslhost") }
            "rviz_pointcloud" { $process.ProcessName -in @("wsl", "wslhost", "rviz") }
            "rviz_gridmap" { $process.ProcessName -in @("wsl", "wslhost", "rviz") }
            default { $false }
        }
        if ($allowed) {
            Stop-Process -Id $pidValue -Force -ErrorAction SilentlyContinue
        }
    }
}

$stopped = Invoke-MoSimOrchestratorClient -Arguments @("stop_run", "--run-id", $runId) -AllowRejected
if (-not $stopped.accepted -and $stopped.reason_code -eq "runtime_process_not_owned") {
    & wsl.exe -d Ubuntu-20.04 -- bash /mnt/c/Users/HP/Desktop/MoSim/Scripts/ui/stop_orchestrated_runtime.sh $runId
    if ($LASTEXITCODE -ne 0) {
        throw "runtime_stop_fallback_failed: inspect $runDir"
    }
} elseif (-not $stopped.accepted -and $stopped.reason_code -ne "run_not_active") {
    throw "runtime_stop_failed: $($stopped.reason_code)"
}

Write-Output "All managed displays and the flight simulation were stopped."
exit 0
