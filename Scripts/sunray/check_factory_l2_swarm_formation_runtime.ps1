[CmdletBinding()]
param(
    [string]$RunId = "",
    [int]$TimeoutS = 12
)

$ErrorActionPreference = "Stop"

$Root = "C:\Users\HP\Desktop\MoSim"
$RootWsl = "/mnt/c/Users/HP/Desktop/MoSim"
$ResultsRoot = Join-Path $Root "Results\sunray_ros1"
$ActivePath = Join-Path $ResultsRoot "factory_l2_swarm_formation_active.json"
$ProbeScript = Join-Path $Root "Scripts\sunray\probe_swarm_formation_runtime.py"
. (Join-Path $PSScriptRoot "Invoke-SunrayWslBounded.ps1")

if ($TimeoutS -lt 1 -or $TimeoutS -gt 60) {
    throw "TimeoutS must be between 1 and 60 seconds."
}
if (-not (Test-Path -LiteralPath $ProbeScript)) {
    throw "Missing three-UAV runtime probe: $ProbeScript"
}

if ([string]::IsNullOrWhiteSpace($RunId) -and (Test-Path -LiteralPath $ActivePath)) {
    try {
        $active = Get-Content -Raw -LiteralPath $ActivePath | ConvertFrom-Json
        if ([string]$active.status -in @("launch_requested", "running")) {
            $RunId = [string]$active.run_id
        } else {
            Write-Host "[MoSim] The active pointer is not running; writing a standalone health snapshot."
        }
    } catch {
        Write-Warning "Could not read the active run pointer. A standalone health snapshot will be used."
    }
}
if (-not [string]::IsNullOrWhiteSpace($RunId) -and $RunId -notmatch '^[A-Za-z0-9_.-]+$') {
    throw "RunId may contain only letters, digits, dot, underscore, and hyphen."
}

$OutputDir = if ([string]::IsNullOrWhiteSpace($RunId)) {
    Join-Path $ResultsRoot ("factory_l2_swarm_formation_runtime_check_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
} else {
    Join-Path $ResultsRoot $RunId
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$OutputPath = Join-Path $OutputDir "SWARM_RUNTIME_STATUS.json"
$OutputPathWsl = $RootWsl + "/Results/sunray_ros1/" + (Split-Path -Leaf $OutputDir) + "/SWARM_RUNTIME_STATUS.json"

$command = @"
cd '$RootWsl'
source /opt/ros/noetic/setup.bash
export DISABLE_ROS1_EOL_WARNINGS=1
python3 Scripts/sunray/probe_swarm_formation_runtime.py --timeout-s $TimeoutS --output '$OutputPathWsl'
"@

$probe = Invoke-SunrayWslBash -Script $command -TimeoutS ($TimeoutS + 10) -AllowNonZero
$exitCode = $probe.ExitCode
if (-not (Test-Path -LiteralPath $OutputPath)) {
    throw "The ROS runtime probe did not create $OutputPath. Exit code: $exitCode"
}

$packet = Get-Content -Raw -LiteralPath $OutputPath | ConvertFrom-Json
Write-Host ("[MoSim] Three-UAV runtime status: " + $packet.status + " (" + $packet.reason_code + ")")
Write-Host ("[MoSim] Sensor/grid readiness: " + $packet.sensor_grid_readiness.status + " (" + $packet.sensor_grid_readiness.ready_topic_count + "/" + $packet.sensor_grid_readiness.required_topic_count + ")")
Write-Host ("[MoSim] Flight-link readiness: " + $packet.flight_link_readiness.status + " (" + $packet.flight_link_readiness.ready_link_count + "/" + $packet.flight_link_readiness.required_link_count + ")")
Write-Host ("[MoSim] RViz accumulated-map readiness: " + $packet.rviz_map_readiness.status + " (" + $packet.rviz_map_readiness.ready_topic_count + "/" + $packet.rviz_map_readiness.required_topic_count + ")")
foreach ($entry in $packet.clouds.PSObject.Properties) {
    $sample = $entry.Value
    Write-Host ("  " + $entry.Name + ": " + $sample.nonempty + ", points=" + $sample.point_count)
}
foreach ($entry in $packet.review_accumulated_clouds.PSObject.Properties) {
    $sample = $entry.Value
    Write-Host ("  review_" + $entry.Name + ": " + $sample.nonempty + ", points=" + $sample.point_count)
}
foreach ($entry in $packet.mavros_states.PSObject.Properties) {
    $sample = $entry.Value
    Write-Host ("  " + $entry.Name + ": connected=" + $sample.connected + ", armed=" + $sample.armed + ", mode=" + $sample.mode)
}
Write-Host ("[MoSim] Evidence: " + $OutputPath)

exit $exitCode
