[CmdletBinding()]
param(
    [string]$RunId = ""
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$existingAudit = Get-Process -Name "MoSimGroundControlAudit" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($existingAudit) {
    throw "An isolated QGC online-waypoint audit is already running (PID $($existingAudit.Id)). Close it before starting a new audit pointer."
}
if ([string]::IsNullOrWhiteSpace($RunId)) {
    $RunId = "qgc-online-waypoint-audit-" + (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")
}

$prepareScript = Join-Path $projectRoot "Scripts\ui\prepare_qgc_online_waypoint_audit.py"
$prepareResult = & python $prepareScript --run-id $RunId
if ($LASTEXITCODE -ne 0) {
    throw "Failed to prepare QGC online-waypoint audit run."
}
$prepared = $prepareResult | ConvertFrom-Json
$auditManifestPath = Join-Path $projectRoot "Results\ui_platform\qgc_online_waypoint_audits\$RunId\ONLINE_WAYPOINT_DISPLAY_AUDIT.json"
$audit = Get-Content -LiteralPath $auditManifestPath -Raw | ConvertFrom-Json

$qgcExe = Join-Path $projectRoot "build\flight-console-qgc-audit\Release\MoSimGroundControlAudit.exe"
if (-not (Test-Path -LiteralPath $qgcExe -PathType Leaf)) {
    throw "Isolated QGC audit executable is missing: $qgcExe"
}
$runtimeLauncher = Join-Path $projectRoot "Scripts\ui\run_flight_console.ps1"
if (-not (Test-Path -LiteralPath $runtimeLauncher -PathType Leaf)) {
    throw "MoSim Ground Control runtime launcher is missing: $runtimeLauncher"
}

$wslProjectRoot = (wsl.exe -d Ubuntu-20.04 --exec wslpath -u $projectRoot).Trim()
$wslRunDirectory = (wsl.exe -d Ubuntu-20.04 --exec wslpath -u (Join-Path $projectRoot $audit.run_directory)).Trim()
$wslManifest = (wsl.exe -d Ubuntu-20.04 --exec wslpath -u (Join-Path $projectRoot "$($audit.run_directory)\RUN_MANIFEST.json")).Trim()
$wslEvidence = (wsl.exe -d Ubuntu-20.04 --exec wslpath -u (Join-Path $projectRoot $audit.coordinate_fixture_path)).Trim()
$fixtureCommand = "cd '$wslProjectRoot' && bash Scripts/ui/run_qgc_online_waypoint_fixture.sh --run-dir '$wslRunDirectory' --manifest '$wslManifest' --coordinate-evidence '$wslEvidence'"
# Start-Process flattens ArgumentList. Preserve the complete shell command as
# the single argument required by `bash -lc`, including its spaces and `&&`.
$quotedFixtureCommand = '"' + $fixtureCommand.Replace('"', '\"') + '"'

$previousProjectRoot = $env:MOSIM_PROJECT_ROOT
$previousPointer = $env:MOSIM_QGC_ACTIVE_RUN_POINTER
try {
    $env:MOSIM_PROJECT_ROOT = $projectRoot
    $env:MOSIM_QGC_ACTIVE_RUN_POINTER = $audit.pointer_relative_path
    & $runtimeLauncher -Executable $qgcExe -AuditInstance -StartupTimeoutSeconds 15
}
finally {
    $env:MOSIM_PROJECT_ROOT = $previousProjectRoot
    $env:MOSIM_QGC_ACTIVE_RUN_POINTER = $previousPointer
}

Start-Process -FilePath "wsl.exe" -ArgumentList @("-d", "Ubuntu-20.04", "--exec", "bash", "-lc", $quotedFixtureCommand)

Write-Output "QGC online-waypoint audit started in an isolated instance for $RunId"
Write-Output "Audit manifest: $auditManifestPath"
Write-Output "The ROS1 fixture terminal is display-only; close it or press Ctrl+C after review."
