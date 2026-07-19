[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "launcher_common.ps1")

$qgcLauncher = Join-Path $script:MoSimProjectRoot "Scripts/ui/run_flight_console.ps1"
$displayHelper = Join-Path $script:MoSimProjectRoot "Scripts/ui/attach_orchestrated_displays.ps1"

if (Get-Process -Name "MoSimFlightConsole" -ErrorAction SilentlyContinue) {
    throw "qgc_already_running: close the existing Flight Console first"
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

function Stop-StaleDisplayProcesses {
    param([string]$ProcessFile)
    if (-not (Test-Path -LiteralPath $ProcessFile)) { return }
    try { $records = @(Get-Content -Raw -LiteralPath $ProcessFile | ConvertFrom-Json) } catch { return }
    foreach ($record in $records) {
        $pidValue = 0
        if (-not [int]::TryParse([string]$record.pid, [ref]$pidValue)) { continue }
        $process = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
        if ($null -eq $process) { continue }
        if (($record.kind -eq "unreal" -and $process.ProcessName -eq "UnrealEditor") -or
            ($record.kind -eq "unreal_bridge" -and $process.ProcessName -in @("wsl", "wslhost"))) {
            Stop-Process -Id $pidValue -Force -ErrorAction SilentlyContinue
        }
    }
}

Start-MoSimOrchestratorService
$active = Get-MoSimActiveRun
if ($null -eq $active -or -not $active.run_id) {
    throw "flight_simulation_not_started: run the Gazebo flight simulation launcher first"
}
$runId = [string]$active.run_id
$runState = Invoke-MoSimOrchestratorClient -Arguments @("get_run_state", "--run-id", $runId) -AllowRejected
if (-not $runState.accepted -or $runState.manifest.lifecycle_state -notin @("starting", "running")) {
    throw "flight_simulation_not_active: run the Gazebo flight simulation launcher first"
}

$display = Invoke-MoSimOrchestratorClient -Arguments @(
    "prepare_display_session", "--run-id", $runId, "--display", "unreal"
)
$sessionId = [string]$display.session.session_id
$runDir = Get-MoSimRunDirectory -RunId $runId
$sessionDir = Join-Path $runDir "displays/$sessionId"
$processFile = Join-Path $sessionDir "DISPLAY_PROCESSES.json"
$statusFile = Join-Path $sessionDir "DISPLAY_STATUS.json"

$unrealReady = $false
if (Test-Path -LiteralPath $processFile) {
    try {
        $records = @(Get-Content -Raw -LiteralPath $processFile | ConvertFrom-Json)
        $unrealRecord = @($records | Where-Object { $_.kind -eq "unreal" }) | Select-Object -First 1
        if ($null -ne $unrealRecord) {
            $unrealProcess = Get-Process -Id ([int]$unrealRecord.pid) -ErrorAction SilentlyContinue
            $unrealReady = $null -ne $unrealProcess -and (Test-ProcessHasUsableWindow -ProcessId $unrealProcess.Id)
        }
    } catch { $unrealReady = $false }
}

if (-not $unrealReady) {
    Write-Output "Starting the managed UE display for run $runId..."
    Stop-StaleDisplayProcesses -ProcessFile $processFile
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
