[CmdletBinding()]
param(
    [string]$QtDir = "",
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Release",
    [switch]$ConfigureOnly
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$VendorRoot = Join-Path $ProjectRoot "apps/flight_console/vendor/qgroundcontrol"
$BuildRoot = Join-Path $ProjectRoot "build/flight-console-qgc"
$Preflight = Join-Path $ProjectRoot "Results/ui_platform/flight_console_windows_toolchain_preflight.json"

# This entrypoint is intentionally non-installing. System dependencies require
# a separately authorized infrastructure action.
$preflightArgs = @((Join-Path $ProjectRoot "Scripts/ui/check_qgc_windows_toolchain.py"), "--output", $Preflight)
if ($QtDir) { $preflightArgs += @("--qt-dir", $QtDir) }
& python @preflightArgs
if ($LASTEXITCODE -ne 0) {
    throw "Flight Console toolchain preflight failed. See $Preflight"
}

$report = Get-Content -LiteralPath $Preflight -Raw | ConvertFrom-Json
$QtRoot = $report.detected.qt_root
$VsDevCmd = Join-Path $report.detected.visual_studio_installation "Common7/Tools/VsDevCmd.bat"

& python (Join-Path $ProjectRoot "Scripts/ui/materialize_qgc_custom_overlay.py")
if ($LASTEXITCODE -ne 0) { throw "Failed to materialize the MoSim QGC custom overlay" }
& python (Join-Path $ProjectRoot "Scripts/ui/generate_qgc_vendor_manifest.py") --verify
if ($LASTEXITCODE -ne 0) { throw "Frozen QGroundControl source verification failed" }

$configure = "call `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul && " +
    "set `"QTDIR=$QtRoot`" && set `"CMAKE_PREFIX_PATH=$QtRoot`" && " +
    "set `"GSTREAMER_1_0_ROOT_MSVC_X86_64=$($report.detected.gstreamer_root)`" && " +
    "cmake -S `"$VendorRoot`" -B `"$BuildRoot`" -G `"Ninja Multi-Config`""
& cmd.exe /d /s /c $configure
if ($LASTEXITCODE -ne 0) { throw "Flight Console CMake configure failed" }
if (-not $ConfigureOnly) {
    $build = "call `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul && " +
        "set `"QTDIR=$QtRoot`" && set `"CMAKE_PREFIX_PATH=$QtRoot`" && " +
        "set `"GSTREAMER_1_0_ROOT_MSVC_X86_64=$($report.detected.gstreamer_root)`" && " +
        "cmake --build `"$BuildRoot`" --config $Configuration --parallel"
    & cmd.exe /d /s /c $build
    if ($LASTEXITCODE -ne 0) { throw "Flight Console build failed" }
}
