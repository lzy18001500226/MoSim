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

function Test-ManagedDisplayOwnership {
    param($Record, [string]$ExpectedRunId, [string]$ExpectedSessionId)
    $pidValue = 0
    if (-not [int]::TryParse([string]$Record.pid, [ref]$pidValue)) { return $false }
    $process = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
    if ($null -eq $process) { return $false }
    try {
        $commandLine = [string](Get-CimInstance Win32_Process -Filter "ProcessId=$pidValue").CommandLine
    } catch {
        throw "managed_display_ownership_unavailable: kind=$($Record.kind) pid=$pidValue"
    }
    if ($Record.kind -eq "unreal") {
        return $process.ProcessName -eq "UnrealEditor" -and
            $commandLine -like "*MoSimSceneLibrary.uproject*" -and
            $commandLine -like "*-MoSimObservabilityRunId=$ExpectedRunId*"
    }
    if ($Record.kind -eq "unreal_bridge") {
        return $process.ProcessName -in @("wsl", "wslhost") -and
            $commandLine -like "*launch_ros1_display.sh*" -and
            $commandLine -like "*$ExpectedSessionId*"
    }
    if ($Record.kind -in @("rviz_pointcloud", "rviz_gridmap")) {
        return $process.ProcessName -in @("wsl", "wslhost", "rviz") -and
            $commandLine -like "*$ExpectedSessionId*"
    }
    return $false
}

function Stop-ManagedProcessAndWait {
    param([System.Diagnostics.Process]$Process, [string]$Kind)
    Stop-Process -Id $Process.Id -Force -ErrorAction Stop
    if (-not $Process.WaitForExit(10000)) {
        throw "managed_process_survived: kind=$Kind pid=$($Process.Id)"
    }
}

foreach ($process in @(Get-Process -Name "MoSimFlightConsole" -ErrorAction SilentlyContinue)) {
    Stop-ManagedProcessAndWait -Process $process -Kind "flight_console"
}

$sessionDirs = @(Get-ChildItem -Path (Join-Path $runDir "displays") -Directory -ErrorAction SilentlyContinue)
foreach ($sessionDir in $sessionDirs) {
    $records = @()
    $processFile = Join-Path $sessionDir.FullName "DISPLAY_PROCESSES.json"
    $sessionFile = Join-Path $sessionDir.FullName "DISPLAY_SESSION.json"
    if (Test-Path -LiteralPath $processFile) {
        try { $records += @(Get-Content -Raw -LiteralPath $processFile | ConvertFrom-Json) } catch {}
    }
    if (Test-Path -LiteralPath $sessionFile) {
        try {
            $session = Get-Content -Raw -LiteralPath $sessionFile | ConvertFrom-Json
            foreach ($display in @($session.status.displays)) {
                $kind = switch ([string]$display.display) {
                    "unreal" { "unreal" }
                    "unreal_bridge" { "unreal_bridge" }
                    "rviz_pointcloud" { "rviz_pointcloud" }
                    "rviz_gridmap" { "rviz_gridmap" }
                    default { "" }
                }
                if ($kind) { $records += [pscustomobject]@{ kind = $kind; pid = $display.process_id } }
            }
        } catch {}
    }
    $records = @($records | Sort-Object @{ Expression = { [string]$_.kind } }, @{ Expression = { [int]$_.pid } } -Unique)
    foreach ($record in $records) {
        $pidValue = 0
        if (-not [int]::TryParse([string]$record.pid, [ref]$pidValue)) { continue }
        $process = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
        if ($null -eq $process) { continue }
        if (Test-ManagedDisplayOwnership -Record $record -ExpectedRunId $runId -ExpectedSessionId $sessionDir.Name) {
            Stop-ManagedProcessAndWait -Process $process -Kind ([string]$record.kind)
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
