[CmdletBinding()]
param(
    [string]$RunId = ("factory_l2_swarm_formation_manual_" + (Get-Date -Format "yyyyMMdd_HHmmss")),
    # Match the gate's full center-chain plus landing lifecycle watchdog.
    [int]$TotalTimeoutS = 2400,
    [ValidateSet("r6_baseline_v1", "conservative_v1")]
    [string]$DynamicsProfile = "conservative_v1",
    [switch]$KeepAlive,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$Root = "C:\Users\HP\Desktop\MoSim"
$GateScript = Join-Path $Root "Scripts\sunray\run_factory_l2_swarm_formation_obstacle_gate.ps1"
$ResultsRoot = Join-Path $Root "Results\sunray_ros1"
$ResultDir = Join-Path $ResultsRoot $RunId
$ActivePath = Join-Path $ResultsRoot "factory_l2_swarm_formation_active.json"

function Read-MoSimJson {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Set-MoSimProperty {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Object,
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [object]$Value
    )

    if ($Object -is [System.Collections.IDictionary]) {
        $Object[$Name] = $Value
    } else {
        $Object | Add-Member -NotePropertyName $Name -NotePropertyValue $Value -Force
    }
}

function Test-ControlledKeepAliveCompletion {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ExpectedRunId,
        [Parameter(Mandatory = $true)]
        [string]$ExpectedResultDir
    )

    # A nonzero backend exit is accepted only when the completed mission was
    # deliberately stopped through the exact owned-runner stop path.
    $paths = @{
        keep_alive = Join-Path $ExpectedResultDir "KEEP_ALIVE_READY.json"
        operator_stop = Join-Path $ExpectedResultDir "OPERATOR_STOP_REQUESTED.json"
        mission = Join-Path $ExpectedResultDir "EGO_SWARM_METRICS.json"
        manifest = Join-Path $ExpectedResultDir "RUN_MANIFEST.json"
        planner_audit = Join-Path $ExpectedResultDir "planner_runtime_log_audit.json"
        formation = Join-Path $ExpectedResultDir "SWARM_FORMATION_TRACKING_GATE.json"
        clearance = Join-Path $ExpectedResultDir "SWARM_FORMATION_OBSTACLE_CLEARANCE_GATE.json"
    }
    if (@($paths.Values | Where-Object { -not (Test-Path -LiteralPath $_) }).Count -gt 0) {
        return $false
    }

    try {
        $keepAlive = Read-MoSimJson -Path $paths.keep_alive
        $operatorStop = Read-MoSimJson -Path $paths.operator_stop
        $mission = Read-MoSimJson -Path $paths.mission
        $manifest = Read-MoSimJson -Path $paths.manifest
        $plannerAudit = Read-MoSimJson -Path $paths.planner_audit
        $formation = Read-MoSimJson -Path $paths.formation
        $clearance = Read-MoSimJson -Path $paths.clearance

        return (
            [string]$keepAlive.run_id -eq $ExpectedRunId -and
            [string]$keepAlive.status -eq "mission_passed_keep_alive" -and
            [string]$operatorStop.run_id -eq $ExpectedRunId -and
            [string]$operatorStop.status -eq "operator_stop_requested" -and
            [string]$mission.status -eq "passed" -and
            $null -ne $manifest.mission_exit_code -and [int]$manifest.mission_exit_code -eq 0 -and
            [string]$plannerAudit.status -eq "passed" -and
            [string]$formation.status -eq "passed" -and
            [string]$clearance.status -eq "passed"
        )
    } catch {
        Write-Warning "Could not validate controlled KeepAlive completion: $($_.Exception.Message)"
        return $false
    }
}

function Write-RunLifecycleEvidence {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Status,
        [Parameter(Mandatory = $true)]
        [int]$RawGateExitCode,
        [Parameter(Mandatory = $true)]
        [int]$FinalExitCode,
        [Parameter(Mandatory = $true)]
        [bool]$ControlledStopAccepted
    )

    [ordered]@{
        schema = "mosim.factory_l2.swarm_formation.lifecycle.v1"
        run_id = $RunId
        status = $Status
        keep_alive_requested = [bool]$KeepAlive
        controlled_stop_accepted = $ControlledStopAccepted
        raw_gate_exit_code = $RawGateExitCode
        final_exit_code = $FinalExitCode
        recorded_at_utc = [DateTime]::UtcNow.ToString("o")
        claim_boundary = "A controlled stop is successful only after the backend, formation, clearance and planner-log gates have all passed."
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $ResultDir "RUN_LIFECYCLE.json") -Encoding UTF8
}

if ($RunId -notmatch '^[A-Za-z0-9_.-]+$') {
    throw "RunId may contain only letters, digits, dot, underscore, and hyphen."
}
if ($TotalTimeoutS -lt 60) {
    throw "TotalTimeoutS must be at least 60 seconds."
}
if (-not (Test-Path -LiteralPath $GateScript)) {
    throw "Missing three-UAV backend launcher: $GateScript"
}

if ($DryRun) {
    Write-Host "[MoSim] Dry run: validating the three-UAV backend without changing the active run pointer."
    & $GateScript -RunId $RunId -TotalTimeoutS $TotalTimeoutS -DynamicsProfile $DynamicsProfile -KeepAlive:$KeepAlive -DryRun
    exit $LASTEXITCODE
}

New-Item -ItemType Directory -Force -Path $ResultsRoot | Out-Null
$active = [ordered]@{
    schema = "mosim.factory_l2.swarm_formation.manual_session.v1"
    run_id = $RunId
    result_dir = $ResultDir
    status = "launch_requested"
    dynamics_profile = $DynamicsProfile
    keep_alive = [bool]$KeepAlive
    created_at_utc = [DateTime]::UtcNow.ToString("o")
    launcher = $GateScript
    claim_boundary = "Three-UAV fixed Swarm-Formation obstacle-crossing backend. This is not autonomous exploration or a 4-9 UAV claim."
}
$active | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ActivePath -Encoding UTF8

Write-Host "[MoSim] Starting the three-UAV Swarm-Formation backend in this terminal."
Write-Host "[MoSim] RunId: $RunId"
Write-Host "[MoSim] The three-UAV Windows wrappers are archived and require a separate revalidation before use."
Write-Host "[MoSim] Do not treat this historical route as the current C99 baseline."

$exitCode = 1
$rawGateExitCode = 1
$controlledStopAccepted = $false
try {
    Set-MoSimProperty -Object $active -Name "status" -Value "running"
    Set-MoSimProperty -Object $active -Name "started_at_utc" -Value ([DateTime]::UtcNow.ToString("o"))
    $active | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ActivePath -Encoding UTF8
    & $GateScript -RunId $RunId -TotalTimeoutS $TotalTimeoutS -DynamicsProfile $DynamicsProfile -KeepAlive:$KeepAlive
    $exitCode = $LASTEXITCODE
} finally {
    $rawGateExitCode = $exitCode
    if ($KeepAlive.IsPresent -and $rawGateExitCode -ne 0) {
        $controlledStopAccepted = Test-ControlledKeepAliveCompletion -ExpectedRunId $RunId -ExpectedResultDir $ResultDir
        if ($controlledStopAccepted) {
            $exitCode = 0
        }
    }

    # The stop helper may have appended its request marker while the backend
    # was unwinding. Re-read the same run pointer before recording the result.
    if (Test-Path -LiteralPath $ActivePath) {
        try {
            $latestActive = Read-MoSimJson -Path $ActivePath
            if ([string]$latestActive.run_id -eq $RunId) {
                $active = $latestActive
            }
        } catch {
            Write-Warning "Could not refresh the active run pointer: $($_.Exception.Message)"
        }
    }

    $finalStatus = if ($controlledStopAccepted) { "finished_after_operator_stop" } elseif ($exitCode -eq 0) { "finished" } else { "stopped_or_failed" }
    Set-MoSimProperty -Object $active -Name "status" -Value $finalStatus
    Set-MoSimProperty -Object $active -Name "finished_at_utc" -Value ([DateTime]::UtcNow.ToString("o"))
    Set-MoSimProperty -Object $active -Name "raw_gate_exit_code" -Value $rawGateExitCode
    Set-MoSimProperty -Object $active -Name "exit_code" -Value $exitCode
    Set-MoSimProperty -Object $active -Name "controlled_stop_accepted" -Value $controlledStopAccepted
    $active | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ActivePath -Encoding UTF8
    Write-RunLifecycleEvidence -Status $finalStatus -RawGateExitCode $rawGateExitCode -FinalExitCode $exitCode -ControlledStopAccepted $controlledStopAccepted
}

exit $exitCode
