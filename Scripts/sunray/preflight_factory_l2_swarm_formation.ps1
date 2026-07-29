[CmdletBinding()]
param(
    [int]$WslTimeoutS = 45,
    [int]$MaxVmmemWorkingSetMB = 8192,
    [int]$MaxWslHostProcessCount = 40
)

$ErrorActionPreference = "Stop"

if ($WslTimeoutS -lt 10 -or $WslTimeoutS -gt 120) {
    throw "WslTimeoutS must be between 10 and 120 seconds."
}
if ($MaxVmmemWorkingSetMB -lt 1024) {
    throw "MaxVmmemWorkingSetMB must be at least 1024."
}

$Root = "C:\Users\HP\Desktop\MoSim"
$RootWsl = "/mnt/c/Users/HP/Desktop/MoSim"
$ResultsRoot = Join-Path $Root "Results\sunray_ros1"
$ActivePath = Join-Path $ResultsRoot "factory_l2_swarm_formation_active.json"
. (Join-Path $PSScriptRoot "Invoke-SunrayWslBounded.ps1")

$runtimeCommand = @"
cd '$RootWsl'
export PROJECT_ROOT='$RootWsl'
bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh
"@
$runtime = Invoke-SunrayWslBash -Script $runtimeCommand -TimeoutS $WslTimeoutS -AllowNonZero

$runnerCommand = @"
pgrep -af '[r]un_px4ctrl_ego_swarm_gate\.sh' || true
"@
$runner = Invoke-SunrayWslBash -Script $runnerCommand -TimeoutS 8 -AllowNonZero
$runnerProbeFailed = $runner.ExitCode -ne 0
$activeRunnerLines = if ($runnerProbeFailed) {
    @()
} else {
    @($runner.StdOut -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}

$wslProcesses = @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
    $_.ProcessName -match '^(vmmemWSL|wsl|wslhost)$'
})
$vmmem = @($wslProcesses | Where-Object { $_.ProcessName -eq "vmmemWSL" } | Select-Object -First 1)
$vmmemMb = if ($vmmem) { [math]::Round($vmmem.WorkingSet64 / 1MB, 1) } else { 0.0 }
$activePointer = $null
if (Test-Path -LiteralPath $ActivePath) {
    try {
        $activePointer = Get-Content -LiteralPath $ActivePath -Raw | ConvertFrom-Json
    } catch {
        $activePointer = [pscustomobject]@{ status = "unreadable"; parse_error = $_.Exception.Message }
    }
}

$memoryWarning = $vmmemMb -gt $MaxVmmemWorkingSetMB
$processWarning = $wslProcesses.Count -gt $MaxWslHostProcessCount
$recommendation = if ($runtime.ExitCode -ne 0) {
    "runtime_preflight_failed_inspect_evidence"
} elseif ($runnerProbeFailed) {
    "runner_probe_failed_inspect_evidence"
} elseif ($activeRunnerLines.Count -gt 0) {
    "active_runner_present_do_not_restart_wsl"
} elseif ($memoryWarning -or $processWarning) {
    "manual_wsl_restart_recommended_after_confirming_no_run_is_active"
} else {
    "no_global_wsl_restart_requested"
}
$status = if ($runtime.ExitCode -ne 0 -or $runnerProbeFailed) {
    "blocked"
} elseif ($activeRunnerLines.Count -gt 0) {
    "busy"
} else {
    "passed"
}

$outputDir = Join-Path $ResultsRoot ("factory_l2_swarm_formation_preflight_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
$outputPath = Join-Path $outputDir "PREFLIGHT.json"
$packet = [ordered]@{
    schema = "mosim.factory_l2.swarm_formation.preflight.v1"
    status = $status
    created_at_utc = [DateTime]::UtcNow.ToString("o")
    runtime_preflight = [ordered]@{
        exit_code = $runtime.ExitCode
        stdout = $runtime.StdOut.Trim()
        stderr = $runtime.StdErr.Trim()
    }
    active_runner = [ordered]@{
        probe_exit_code = $runner.ExitCode
        probe_failed = $runnerProbeFailed
        probe_stdout = $runner.StdOut.Trim()
        probe_stderr = $runner.StdErr.Trim()
        count = $activeRunnerLines.Count
        lines = $activeRunnerLines
    }
    active_pointer = $activePointer
    host_wsl = [ordered]@{
        vmmem_working_set_mb = $vmmemMb
        wsl_host_process_count = $wslProcesses.Count
        max_vmmem_working_set_mb = $MaxVmmemWorkingSetMB
        max_wsl_host_process_count = $MaxWslHostProcessCount
        memory_warning = $memoryWarning
        process_count_warning = $processWarning
    }
    recommendation = $recommendation
    manual_restart_command = if ($recommendation -eq "manual_wsl_restart_recommended_after_confirming_no_run_is_active") {
        "wsl --shutdown"
    } else {
        ""
    }
    claim_boundary = "Read-only preflight. It never starts or stops Gazebo, PX4, MAVROS, RViz, or WSL. A WSL restart is reported for manual operator decision only."
}
$packet | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $outputPath -Encoding UTF8

Write-Host "[MoSim] Factory three-UAV preflight: $status"
Write-Host "[MoSim] WSL host processes: $($wslProcesses.Count), vmmemWSL working set: $vmmemMb MB"
Write-Host "[MoSim] Active three-UAV runner count: $($activeRunnerLines.Count)"
Write-Host "[MoSim] Recommendation: $recommendation"
Write-Host "[MoSim] Evidence: $outputPath"
exit $(if ($status -eq "passed") { 0 } else { 1 })
