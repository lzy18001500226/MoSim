[CmdletBinding()]
param(
    [int]$WaitS = 20,
    [int]$InterruptGraceS = 5
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "Invoke-SunrayWslBounded.ps1")

$Root = "C:\Users\HP\Desktop\MoSim"
$ResultsRoot = Join-Path $Root "Results\sunray_ros1"
$ActivePath = Join-Path $ResultsRoot "factory_l2_swarm_formation_active.json"

if ($WaitS -lt 5 -or $WaitS -gt 60) {
    throw "WaitS must be between 5 and 60 seconds."
}
if ($InterruptGraceS -lt 1 -or $InterruptGraceS -gt 30) {
    throw "InterruptGraceS must be between 1 and 30 seconds."
}

$runnerPattern = '[r]un_px4ctrl_ego_swarm_gate\.sh'
$WslCommandTimeoutS = 20
$findCommand = @"
pgrep -f '$runnerPattern' || true
"@

function Get-ActiveRunnerIds {
    $query = Invoke-SunrayWslBash -Script $findCommand -TimeoutS $WslCommandTimeoutS -AllowNonZero
    $ids = @()
    foreach ($line in @($query.StdOut -split "\r?\n")) {
        if ($line -match '^\s*(\d+)\s*$') {
            $ids += [int]$Matches[1]
        }
    }
    return $ids
}

function Get-RunnerProcessSnapshot {
    param(
        [Parameter(Mandatory = $true)]
        [int[]]$RunnerIds
    )

    if ($RunnerIds.Count -eq 0) {
        return @()
    }

    $pidList = $RunnerIds -join " "
    # The WSL snapshot validates /proc/$runner_pid/cmdline before walking only
    # descendants of the exact three-UAV runner. Each record carries Linux
    # starttime so a reused PID cannot be signalled later.
    $snapshotCommand = @'
python3 - __MOSIM_RUNNER_IDS__ <<'PY'
import os
import sys


def stat(pid):
    try:
        raw = open(f"/proc/{pid}/stat", "r", encoding="utf-8", errors="replace").read()
        tail = raw[raw.rfind(")") + 1 :].split()
        return int(tail[1]), int(tail[19])
    except (FileNotFoundError, IndexError, OSError, ValueError):
        return None


def cmdline(pid):
    try:
        return open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ").decode("utf-8", "replace")
    except OSError:
        return ""


roots = []
for value in sys.argv[1:]:
    try:
        pid = int(value)
    except ValueError:
        continue
    if "run_px4ctrl_ego_swarm_gate.sh" in cmdline(pid) and stat(pid) is not None:
        roots.append(pid)

children = {}
starts = {}
for name in os.listdir("/proc"):
    if not name.isdigit():
        continue
    pid = int(name)
    info = stat(pid)
    if info is None:
        continue
    ppid, starttime = info
    starts[pid] = starttime
    children.setdefault(ppid, []).append(pid)

seen = set()
pending = list(roots)
while pending:
    pid = pending.pop()
    if pid in seen or pid not in starts:
        continue
    seen.add(pid)
    pending.extend(children.get(pid, []))

for pid in sorted(seen, reverse=True):
    print(f"{pid}:{starts[pid]}")
PY
'@
    $snapshotCommand = $snapshotCommand.Replace("__MOSIM_RUNNER_IDS__", $pidList)
    $query = Invoke-SunrayWslBash -Script $snapshotCommand -TimeoutS $WslCommandTimeoutS -AllowNonZero
    $records = @()
    foreach ($line in @($query.StdOut -split "\r?\n")) {
        if ($line -match '^\s*(\d+):(\d+)\s*$') {
            $records += ("{0}:{1}" -f $Matches[1], $Matches[2])
        }
    }
    return $records
}

function Test-ProcessSnapshotAlive {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$ProcessSnapshot
    )

    if ($ProcessSnapshot.Count -eq 0) {
        return @()
    }

    $records = $ProcessSnapshot -join " "
    $aliveCommand = @'
python3 - __MOSIM_SNAPSHOT__ <<'PY'
import os
import sys


def starttime(pid):
    try:
        raw = open(f"/proc/{pid}/stat", "r", encoding="utf-8", errors="replace").read()
        return int(raw[raw.rfind(")") + 1 :].split()[19])
    except (FileNotFoundError, IndexError, OSError, ValueError):
        return None


for record in sys.argv[1:]:
    try:
        pid_text, expected_text = record.split(":", 1)
        pid = int(pid_text)
        expected = int(expected_text)
    except ValueError:
        continue
    if starttime(pid) == expected:
        print(record)
PY
'@
    $aliveCommand = $aliveCommand.Replace("__MOSIM_SNAPSHOT__", $records)
    $query = Invoke-SunrayWslBash -Script $aliveCommand -TimeoutS $WslCommandTimeoutS -AllowNonZero
    $alive = @()
    foreach ($line in @($query.StdOut -split "\r?\n")) {
        if ($line -match '^\s*\d+:\d+\s*$') {
            $alive += $line.Trim()
        }
    }
    return $alive
}

function Send-ProcessSnapshotSignal {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("INT", "TERM", "KILL")]
        [string]$Signal,
        [Parameter(Mandatory = $true)]
        [string[]]$ProcessSnapshot
    )

    if ($ProcessSnapshot.Count -eq 0) {
        return
    }

    $records = $ProcessSnapshot -join " "
    $signalCommand = @'
python3 - "__MOSIM_SIGNAL__" __MOSIM_SNAPSHOT__ <<'PY'
import os
import signal
import sys


def starttime(pid):
    try:
        raw = open(f"/proc/{pid}/stat", "r", encoding="utf-8", errors="replace").read()
        return int(raw[raw.rfind(")") + 1 :].split()[19])
    except (FileNotFoundError, IndexError, OSError, ValueError):
        return None


signal_value = getattr(signal, "SIG" + sys.argv[1])
for record in sys.argv[2:]:
    try:
        pid_text, expected_text = record.split(":", 1)
        pid = int(pid_text)
        expected = int(expected_text)
    except ValueError:
        continue
    if starttime(pid) != expected:
        continue
    try:
        os.kill(pid, signal_value)
    except OSError:
        pass
PY
'@
    $signalCommand = $signalCommand.Replace("__MOSIM_SIGNAL__", $Signal).Replace("__MOSIM_SNAPSHOT__", $records)
    Invoke-SunrayWslBash -Script $signalCommand -TimeoutS $WslCommandTimeoutS -AllowNonZero | Out-Null
}

function Wait-ForProcessSnapshotExit {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$ProcessSnapshot,
        [Parameter(Mandatory = $true)]
        [int]$DurationS
    )

    $deadline = [DateTime]::UtcNow.AddSeconds($DurationS)
    while ([DateTime]::UtcNow -lt $deadline) {
        if (@(Test-ProcessSnapshotAlive -ProcessSnapshot $ProcessSnapshot).Count -eq 0) {
            return $true
        }
        Start-Sleep -Milliseconds 500
    }
    return (@(Test-ProcessSnapshotAlive -ProcessSnapshot $ProcessSnapshot).Count -eq 0)
}

function Write-OperatorStopRequest {
    param(
        [Parameter(Mandatory = $true)]
        [int[]]$RunnerIds
    )

    if (-not (Test-Path -LiteralPath $ActivePath)) {
        Write-Warning "No active-run pointer was found; stop evidence will not be promoted to a successful completion."
        return $null
    }

    try {
        $active = Get-Content -Raw -LiteralPath $ActivePath | ConvertFrom-Json
        $runId = [string]$active.run_id
        $resultDir = [IO.Path]::GetFullPath([string]$active.result_dir)
        $resultsPrefix = [IO.Path]::GetFullPath($ResultsRoot).TrimEnd('\') + '\'
        if ($runId -notmatch '^[A-Za-z0-9_.-]+$' -or -not $resultDir.StartsWith($resultsPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            Write-Warning "The active-run pointer is not safe for a controlled-stop marker; preserving the nonzero backend result."
            return $null
        }

        $markerPath = Join-Path $resultDir "OPERATOR_STOP_REQUESTED.json"
        [ordered]@{
            schema = "mosim.factory_l2.swarm_formation.operator_stop_request.v1"
            run_id = $runId
            status = "operator_stop_requested"
            requested_at_utc = [DateTime]::UtcNow.ToString("o")
            runner_pids = @($RunnerIds)
            source = "cmd/06_停止Factory三机编队.cmd"
            claim_boundary = "This marker records an operator-requested stop. It is insufficient by itself to promote a stopped run to passed."
        } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $markerPath -Encoding UTF8

        $active | Add-Member -NotePropertyName "status" -NotePropertyValue "stop_requested" -Force
        $active | Add-Member -NotePropertyName "operator_stop_requested_at_utc" -NotePropertyValue ([DateTime]::UtcNow.ToString("o")) -Force
        $active | Add-Member -NotePropertyName "operator_stop_marker" -NotePropertyValue $markerPath -Force
        $active | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ActivePath -Encoding UTF8
        return $markerPath
    } catch {
        Write-Warning "Could not write the controlled-stop marker: $($_.Exception.Message)"
        return $null
    }
}

$initialRunnerIds = @(Get-ActiveRunnerIds)
$hasActiveRunner = $initialRunnerIds.Count -gt 0

$reviewStopCommand = @"
pkill -TERM -f 'sunray_ros1_swarm_formation_(pointcloud|grid3d)_review\.rviz' || true
pkill -TERM -f 'mosim_swarm_formation_uav[123]_pointcloud_review' || true
pkill -TERM -f 'swarm_body_axes_marker_node.py.*mosim/swarm_formation/body_axes' || true
"@

if ($hasActiveRunner) {
    $initialSnapshot = @(Get-RunnerProcessSnapshot -RunnerIds $initialRunnerIds)
    if ($initialSnapshot.Count -eq 0) {
        throw "An active three-UAV runner was found but its owned process tree could not be snapshotted. Refusing a broad stop."
    }
    $stopMarker = Write-OperatorStopRequest -RunnerIds $initialRunnerIds
    if ($null -ne $stopMarker) {
        Write-Host "[MoSim] Recorded the controlled-stop request: $stopMarker"
    }
    Write-Host ("[MoSim] Sending SIGINT to the exact three-UAV runner process tree (" + $initialSnapshot.Count + " processes).")
    Send-ProcessSnapshotSignal -Signal "INT" -ProcessSnapshot $initialSnapshot
} else {
    Write-Host "[MoSim] No active three-UAV swarm gate runner was found. Closing only its owned RViz review processes."
}

Invoke-SunrayWslBash -Script $reviewStopCommand -TimeoutS $WslCommandTimeoutS -AllowNonZero | Out-Null

if (-not $hasActiveRunner) {
    Write-Host "[MoSim] No backend was active; the owned RViz review cleanup request has completed."
    exit 0
}

$intWaitS = [Math]::Min($InterruptGraceS, [Math]::Max(1, $WaitS - 1))
if (Wait-ForProcessSnapshotExit -ProcessSnapshot $initialSnapshot -DurationS $intWaitS) {
    Write-Host "[MoSim] The exact three-UAV process tree exited after SIGINT."
    exit 0
}

$remainingSnapshot = @(Test-ProcessSnapshotAlive -ProcessSnapshot $initialSnapshot)
Write-Host ("[MoSim] " + $remainingSnapshot.Count + " owned process(es) remain after " + $intWaitS + "s; escalating only those snapshot entries to SIGTERM.")
Send-ProcessSnapshotSignal -Signal "TERM" -ProcessSnapshot $remainingSnapshot

$termWaitS = $WaitS - $intWaitS
if (Wait-ForProcessSnapshotExit -ProcessSnapshot $initialSnapshot -DurationS $termWaitS) {
    Write-Host "[MoSim] The exact three-UAV process tree exited after SIGTERM."
    exit 0
}

$survivors = @(Test-ProcessSnapshotAlive -ProcessSnapshot $initialSnapshot)
Write-Host ("[MoSim] " + $survivors.Count + " owned process(es) remain after SIGTERM; sending SIGKILL only to the original snapshot.")
Send-ProcessSnapshotSignal -Signal "KILL" -ProcessSnapshot $survivors
if (Wait-ForProcessSnapshotExit -ProcessSnapshot $initialSnapshot -DurationS 3) {
    Write-Host "[MoSim] The exact three-UAV process tree exited after SIGKILL escalation."
    exit 0
}

throw ("The exact three-UAV process tree did not exit within " + ($WaitS + 3) + "s after SIGINT, SIGTERM and SIGKILL. Do not start another run; inspect its terminal and Results\\sunray_ros1 first.")
