[CmdletBinding()]
param(
    [string]$Preflight = "",
    [string]$Executable = "",
    [switch]$PassThru
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
if (-not $Preflight) {
    $Preflight = Join-Path $ProjectRoot "Results/ui_platform/flight_console_windows_toolchain_preflight.json"
}
if (-not $Executable) {
    $Executable = Join-Path $ProjectRoot "build/flight-console-qgc/Release/MoSimFlightConsole.exe"
}

$existing = Get-Process -Name "MoSimFlightConsole" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($existing) {
    Write-Output "Flight Console is already running (PID $($existing.Id))."
    if ($PassThru) { $existing }
    exit 0
}

if (-not (Test-Path -LiteralPath $Preflight)) {
    throw "Flight Console preflight is missing. Run Scripts/ui/build_flight_console.ps1 first."
}
$report = Get-Content -LiteralPath $Preflight -Raw | ConvertFrom-Json
if ($report.status -ne "ready") {
    throw "Flight Console toolchain is not ready. See $Preflight"
}
if (-not (Test-Path -LiteralPath $Executable)) {
    throw "Flight Console executable is missing. Run Scripts/ui/build_flight_console.ps1 first."
}

$QtBin = Join-Path $report.detected.qt_root "bin"
$GStreamerBin = Join-Path $report.detected.gstreamer_root "bin"
foreach ($path in @($QtBin, $GStreamerBin)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Flight Console runtime dependency path is missing: $path"
    }
}

$env:PATH = "$QtBin;$GStreamerBin;$env:PATH"
$process = Start-Process -FilePath (Resolve-Path $Executable).Path `
    -WorkingDirectory (Split-Path -Parent (Resolve-Path $Executable).Path) `
    -PassThru
Write-Output "Started MoSim Flight Console (PID $($process.Id))."
if ($PassThru) { $process }
