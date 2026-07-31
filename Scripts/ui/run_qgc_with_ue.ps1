[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "launcher_common.ps1")

$qgcLauncher = Join-Path $script:MoSimProjectRoot "Scripts/ui/run_flight_console.ps1"
$displayHelper = Join-Path $script:MoSimProjectRoot "Scripts/ui/attach_orchestrated_displays.ps1"

if (Get-Process -Name "MoSimGroundControl" -ErrorAction SilentlyContinue) {
    throw "qgc_already_running: close MoSim Ground Control first"
}

function Start-FlightConsoleConfigurationMode {
    param([string]$Reason)

    Write-Output "Starting MoSim Ground Control in task configuration mode ($Reason)."
    Write-Output "Select a task, validate its Profile, then start it from QGC."
    Write-Output "Gazebo/PX4/MAVROS and the managed UE viewport will start for that run_id."
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $qgcLauncher
    if ($LASTEXITCODE -ne 0) {
        throw "qgc_start_failed: run_flight_console.ps1 exited with $LASTEXITCODE"
    }
    Write-Output "MoSim ground station started in task configuration mode."
}

function Test-ProcessHasUsableWindow {
    param([int]$ProcessId)
    if ($ProcessId -le 0) { return $false }
    $probe = @"
using System;
using System.Runtime.InteropServices;
public static class MoSimGroundWindowProbe {
    public delegate bool Callback(IntPtr h, IntPtr p);
    [StructLayout(LayoutKind.Sequential)] public struct Rect { public int Left, Top, Right, Bottom; }
    [DllImport("user32.dll")] public static extern bool EnumWindows(Callback callback, IntPtr parameter);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint processId);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out Rect rect);
    public static bool HasUsableWindow(uint target) {
        bool found = false;
        EnumWindows((h, p) => {
            uint owner; GetWindowThreadProcessId(h, out owner);
            Rect rect;
            if (owner == target && GetWindowRect(h, out rect) && (rect.Right - rect.Left) * (rect.Bottom - rect.Top) > 10000) {
                found = true; return false;
            }
            return true;
        }, IntPtr.Zero);
        return found;
    }
}
"@
    if ($null -eq ("MoSimGroundWindowProbe" -as [type])) { Add-Type $probe }
    return [MoSimGroundWindowProbe]::HasUsableWindow([uint32]$ProcessId)
}

function Get-TrackedDisplayRecords {
    param([string]$ProcessFile, [string]$SessionFile)
    $records = @()
    if (Test-Path -LiteralPath $ProcessFile) {
        try {
            $parsedRecords = Get-Content -Raw -LiteralPath $ProcessFile | ConvertFrom-Json
            foreach ($record in $parsedRecords) { $records += $record }
        } catch {}
    }
    if (Test-Path -LiteralPath $SessionFile) {
        try {
            $session = Get-Content -Raw -LiteralPath $SessionFile | ConvertFrom-Json
            foreach ($display in @($session.status.displays)) {
                $kind = switch ([string]$display.display) {
                    "unreal" { "unreal" }
                    "unreal_bridge" { "unreal_bridge" }
                    default { "" }
                }
                if ($kind) {
                    $records += [pscustomobject]@{ kind = $kind; pid = $display.process_id }
                }
            }
        } catch {}
    }
    return @($records | Sort-Object @{ Expression = { [string]$_.kind } }, @{ Expression = { [int]$_.pid } } -Unique)
}

function Test-TrackedDisplayOwnership {
    param($Record, [string]$RunId, [string]$SessionId)
    $pidValue = 0
    if (-not [int]::TryParse([string]$Record.pid, [ref]$pidValue)) { return $false }
    $process = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
    if ($null -eq $process) { return $false }
    try {
        $commandLine = [string](Get-CimInstance Win32_Process -Filter "ProcessId=$pidValue").CommandLine
    } catch {
        return $false
    }
    if ($Record.kind -eq "unreal") {
        return $process.ProcessName -eq "UnrealEditor" -and
            $commandLine -like "*MoSimSceneLibrary.uproject*" -and
            $commandLine -like "*-MoSimObservabilityRunId=$RunId*"
    }
    if ($Record.kind -eq "unreal_bridge") {
        return $process.ProcessName -in @("wsl", "wslhost") -and
            $commandLine -like "*launch_ros1_display.sh*" -and
            $commandLine -like "*$SessionId*"
    }
    return $false
}

function Stop-StaleDisplayProcesses {
    param(
        [string]$ProcessFile,
        [string]$SessionFile,
        [string]$RunId,
        [string]$SessionId,
        [int[]]$PreserveProcessIds = @()
    )
    $records = @(Get-TrackedDisplayRecords -ProcessFile $ProcessFile -SessionFile $SessionFile)
    foreach ($record in $records) {
        $pidValue = 0
        if (-not [int]::TryParse([string]$record.pid, [ref]$pidValue)) { continue }
        if ($pidValue -in $PreserveProcessIds) { continue }
        $process = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
        if ($null -eq $process) { continue }
        if (Test-TrackedDisplayOwnership -Record $record -RunId $RunId -SessionId $SessionId) {
            Stop-Process -Id $pidValue -Force -ErrorAction Stop
            if (-not $process.WaitForExit(5000)) {
                throw "stale_display_process_survived: kind=$($record.kind) pid=$pidValue"
            }
        }
    }
}

Start-MoSimOrchestratorService
$active = Get-MoSimActiveRun
if ($null -eq $active -or -not $active.run_id) {
    Start-FlightConsoleConfigurationMode -Reason "no active flight simulation"
    exit 0
}
$runId = [string]$active.run_id
$runState = Invoke-MoSimOrchestratorClient -Arguments @("get_run_state", "--run-id", $runId) -AllowRejected
if (-not $runState.accepted -or $runState.manifest.lifecycle_state -notin @("starting", "running")) {
    $stateLabel = if ($runState.accepted) { [string]$runState.manifest.lifecycle_state } else { "unavailable" }
    Start-FlightConsoleConfigurationMode -Reason "active run state: $stateLabel"
    exit 0
}

$display = Invoke-MoSimOrchestratorClient -Arguments @(
    "prepare_display_session", "--run-id", $runId, "--display", "unreal"
)
$sessionId = [string]$display.session.session_id
$runDir = Get-MoSimRunDirectory -RunId $runId
$sessionDir = Join-Path $runDir "displays/$sessionId"
$processFile = Join-Path $sessionDir "DISPLAY_PROCESSES.json"
$sessionFile = Join-Path $sessionDir "DISPLAY_SESSION.json"
$statusFile = Join-Path $sessionDir "DISPLAY_STATUS.json"

$unrealReady = $false
$preservedProcessIds = @()
if (Test-Path -LiteralPath $processFile) {
    try {
        $records = @(Get-Content -Raw -LiteralPath $processFile | ConvertFrom-Json)
        $unrealRecord = @($records | Where-Object { $_.kind -eq "unreal" }) | Select-Object -First 1
        if ($null -ne $unrealRecord) {
            $unrealProcess = Get-Process -Id ([int]$unrealRecord.pid) -ErrorAction SilentlyContinue
            $unrealReady = $null -ne $unrealProcess -and (Test-ProcessHasUsableWindow -ProcessId $unrealProcess.Id)
            if ($unrealReady) { $preservedProcessIds += $unrealProcess.Id }
        }
        $bridgeRecord = @($records | Where-Object { $_.kind -eq "unreal_bridge" }) | Select-Object -First 1
        if ($null -ne $bridgeRecord -and $null -ne (Get-Process -Id ([int]$bridgeRecord.pid) -ErrorAction SilentlyContinue)) {
            $preservedProcessIds += [int]$bridgeRecord.pid
        }
    } catch { $unrealReady = $false }
}

# DISPLAY_SESSION.json is written when the display is first attached, while
# DISPLAY_PROCESSES.json can be replaced by a later launch. Reconcile both so a
# stale UE instance cannot keep consuming the same run/UDP stream.
Stop-StaleDisplayProcesses -ProcessFile $processFile -SessionFile $sessionFile `
    -RunId $runId -SessionId $sessionId -PreserveProcessIds $preservedProcessIds

if (-not $unrealReady) {
    Write-Output "Starting the managed UE display for run $runId..."
    Stop-StaleDisplayProcesses -ProcessFile $processFile -SessionFile $sessionFile `
        -RunId $runId -SessionId $sessionId
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $displayHelper `
        -RunId $runId -SessionId $sessionId -DisplayCsv "unreal"
    if ($LASTEXITCODE -ne 0) {
        throw "ue_display_start_failed: inspect $sessionDir"
    }
} elseif ($display.session.state -eq "prepared") {
    $null = Invoke-MoSimOrchestratorClient -Arguments @("attach_display", "--session-id", $sessionId)
}

$deadline = [DateTime]::UtcNow.AddSeconds(195)
do {
    $status = $null
    if (Test-Path -LiteralPath $statusFile) {
        try { $status = Get-Content -Raw -LiteralPath $statusFile | ConvertFrom-Json } catch { $status = $null }
    }
    $unreal = if ($null -ne $status) {
        @($status.displays | Where-Object { $_.display -eq "unreal" }) | Select-Object -First 1
    } else { $null }
    if ($null -ne $status -and $status.state -eq "attached" -and $unreal.state -in @("ready", "running")) {
        break
    }
    Write-Output "Waiting for UE viewport..."
    Start-Sleep -Seconds 2
} while ([DateTime]::UtcNow -lt $deadline)

if ($null -eq $status -or $status.state -ne "attached") {
    throw "ue_display_readiness_timeout: inspect $statusFile"
}

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $qgcLauncher
if ($LASTEXITCODE -ne 0) {
    throw "qgc_start_failed: run_flight_console.ps1 exited with $LASTEXITCODE"
}

Write-Output "MoSim ground station started for run $runId."
exit 0
