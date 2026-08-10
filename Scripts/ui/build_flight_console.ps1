[CmdletBinding()]
param(
    [string]$ToolRoot = "",
    [string]$QtDir = "",
    [string]$NinjaPath = "",
    [string]$GStreamerDir = "",
    [string]$BuildRoot = "",
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Release",
    [switch]$AuditInstance,
    [switch]$ConfigureOnly,
    [switch]$Incremental
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$QgcRoot = Join-Path $ProjectRoot "src/ground_station/qgc/qgroundcontrol"
$QgcManifest = Join-Path $ProjectRoot "src/ground_station/qgc/qgroundcontrol.SHA256SUMS"
$DefaultBuildDirectory = if ($AuditInstance) {
    "build/flight-console-qgc-audit"
} else {
    "build/flight-console-qgc"
}
$DefaultBuildRoot = Join-Path $ProjectRoot $DefaultBuildDirectory
if (-not $BuildRoot) {
    $BuildRoot = $DefaultBuildRoot
} elseif (-not [IO.Path]::IsPathRooted($BuildRoot)) {
    $BuildRoot = Join-Path $ProjectRoot $BuildRoot
}
$BuildRoot = [IO.Path]::GetFullPath($BuildRoot)
$ProjectBuildRoot = [IO.Path]::GetFullPath((Join-Path $ProjectRoot "build"))
if (-not $BuildRoot.StartsWith($ProjectBuildRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw "QGC build root must remain under $ProjectBuildRoot"
}
if ($AuditInstance -and $Configuration -ne "Release") {
    throw "The isolated QGC audit build must use the Release configuration."
}
$Preflight = Join-Path $ProjectRoot "Results/ui_platform/flight_console_windows_toolchain_preflight.json"
if (-not $ToolRoot) { $ToolRoot = Join-Path $ProjectRoot ".tools/flight-console" }

# This entrypoint is intentionally non-installing. System dependencies require
# a separately authorized infrastructure action.
$preflightArgs = @(
    (Join-Path $ProjectRoot "Scripts/ui/check_qgc_windows_toolchain.py"),
    "--output", $Preflight,
    "--tool-root", $ToolRoot
)
if ($QtDir) { $preflightArgs += @("--qt-dir", $QtDir) }
if ($NinjaPath) { $preflightArgs += @("--ninja-path", $NinjaPath) }
if ($GStreamerDir) { $preflightArgs += @("--gstreamer-dir", $GStreamerDir) }
& python @preflightArgs
if ($LASTEXITCODE -ne 0) {
    throw "MoSim Ground Control toolchain preflight failed. See $Preflight"
}

$report = Get-Content -LiteralPath $Preflight -Raw | ConvertFrom-Json
$QtRoot = $report.detected.qt_root
$NinjaDir = Split-Path -Parent $report.detected.ninja
$GStreamerRoot = $report.detected.gstreamer_root
$VsDevCmd = Join-Path $report.detected.visual_studio_installation "Common7/Tools/VsDevCmd.bat"

& python (Join-Path $ProjectRoot "Scripts/ui/materialize_qgc_custom_overlay.py")
if ($LASTEXITCODE -ne 0) { throw "Failed to materialize the MoSim QGC custom overlay" }
& python (Join-Path $ProjectRoot "Scripts/ui/generate_qgc_vendor_manifest.py") --vendor $QgcRoot --manifest $QgcManifest --verify
if ($LASTEXITCODE -ne 0) { throw "Canonical QGroundControl source verification failed" }

# The materializer preserves source timestamps. Refresh the resource manifest
# so Qt RCC rescans copied QML assets during an incremental build.
$CustomResource = Join-Path $QgcRoot "custom/custom.qrc"
& ([string]$report.detected.cmake) -E touch $CustomResource
if ($LASTEXITCODE -ne 0) { throw "Failed to refresh the MoSim Ground Control custom resource manifest" }

$freshArgument = if ($Incremental) { "" } else { "--fresh " }
$auditIdentityArgument = if ($AuditInstance) { " -DMOSIM_QGC_AUDIT_APP_NAME=MoSimGroundControlAudit" } else { "" }
$auditCpmCacheArgument = ""
$auditGeographicLibArgument = ""
if ($AuditInstance) {
    $FormalCpmCache = Join-Path $ProjectRoot "build/flight-console-qgc/cpm_modules"
    if (-not (Test-Path -LiteralPath $FormalCpmCache -PathType Container)) {
        throw "The verified QGC dependency cache is missing: $FormalCpmCache"
    }
    $FormalCmakeCache = Join-Path $ProjectRoot "build/flight-console-qgc/CMakeCache.txt"
    if (-not (Test-Path -LiteralPath $FormalCmakeCache -PathType Leaf)) {
        throw "The formal QGC CMake cache is missing: $FormalCmakeCache"
    }
    $FormalGeographicLibSourceLine = Select-String -LiteralPath $FormalCmakeCache -Pattern '^GeographicLib_SOURCE_DIR:STATIC=(.+)$' | Select-Object -First 1
    $FormalGeographicLibVersionLine = Select-String -LiteralPath $FormalCmakeCache -Pattern '^CPM_PACKAGE_geographiclib_VERSION:INTERNAL=2\.5$' | Select-Object -First 1
    if ($null -eq $FormalGeographicLibSourceLine -or $null -eq $FormalGeographicLibVersionLine) {
        throw "The formal QGC build does not expose the expected GeographicLib 2.5 source."
    }
    $FormalGeographicLibSource = [IO.Path]::GetFullPath($FormalGeographicLibSourceLine.Matches[0].Groups[1].Value).Replace('\', '/')
    if (-not (Test-Path -LiteralPath (Join-Path $FormalGeographicLibSource "CMakeLists.txt") -PathType Leaf)) {
        throw "The formal QGC GeographicLib source is incomplete: $FormalGeographicLibSource"
    }
    $FormalGeographicLibSource = $FormalGeographicLibSource.Replace([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    $AuditCmakeCache = Join-Path $BuildRoot "CMakeCache.txt"
    $AuditGeographicLibSource = ""
    $AuditGeographicLibSourceCreated = $false
    if ($Incremental -and (Test-Path -LiteralPath $AuditCmakeCache -PathType Leaf)) {
        $AuditGeographicLibSourceLine = Select-String -LiteralPath $AuditCmakeCache -Pattern '^CPM_PACKAGE_geographiclib_SOURCE_DIR:INTERNAL=(.+)$' | Select-Object -First 1
        if ($null -ne $AuditGeographicLibSourceLine) {
            $candidate = [IO.Path]::GetFullPath($AuditGeographicLibSourceLine.Matches[0].Groups[1].Value).Replace([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
            if (Test-Path -LiteralPath (Join-Path $candidate "CMakeLists.txt") -PathType Leaf) {
                $AuditGeographicLibSource = $candidate
            }
        }
    }
    if (-not $AuditGeographicLibSource) {
        $AuditSourceRoot = Join-Path $ProjectBuildRoot "flight-console-qgc-audit-sources"
        New-Item -ItemType Directory -Path $AuditSourceRoot -Force | Out-Null
        $AuditGeographicLibSource = Join-Path $AuditSourceRoot ("geographiclib-r2.5-" + [Guid]::NewGuid().ToString("N"))
        & git clone --no-checkout --local $FormalGeographicLibSource $AuditGeographicLibSource
        if ($LASTEXITCODE -ne 0) { throw "Failed to create an isolated GeographicLib source for the QGC audit build." }
        & git -C $AuditGeographicLibSource checkout --detach r2.5
        if ($LASTEXITCODE -ne 0) { throw "Failed to check out GeographicLib r2.5 for the QGC audit build." }
        $AuditGeographicLibSource = [IO.Path]::GetFullPath($AuditGeographicLibSource).Replace([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
        $AuditGeographicLibSourceCreated = $true
    }
    if ($AuditGeographicLibSourceCreated) {
        $GeographicLibPatch = Join-Path $QgcRoot "src/Utilities/Geo/geographiclib.patch"
        & git -C $AuditGeographicLibSource apply --check $GeographicLibPatch
        if ($LASTEXITCODE -ne 0) { throw "The isolated GeographicLib source cannot accept the required QGC patch." }
    }
    $auditCpmCacheArgument = " -DQGC_CPM_SOURCE_CACHE=`"$FormalCpmCache`""
    # Reuse the formal build's pinned source to keep the isolated audit build
    # offline-compatible and avoid competing network clones in its shared cache.
    $auditGeographicLibArgument = " -DCPM_geographiclib_SOURCE=`"$AuditGeographicLibSource`" -DFETCHCONTENT_SOURCE_DIR_GEOGRAPHICLIB="
}
$configure = "set `"PATH=$NinjaDir;$QtRoot\bin;$GStreamerRoot\bin;%PATH%`" && " +
    "call `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul && " +
    "set `"QTDIR=$QtRoot`" && set `"CMAKE_PREFIX_PATH=$QtRoot`" && " +
    "set `"GSTREAMER_1_0_ROOT_MSVC_X86_64=$GStreamerRoot`" && " +
    "cmake $freshArgument-S `"$QgcRoot`" -B `"$BuildRoot`" -G `"Ninja Multi-Config`" -DQGC_APP_VERSION_OVERRIDE=0.0.0 -DQGC_SOURCE_SNAPSHOT_ID=mosim-source-snapshot$auditIdentityArgument$auditCpmCacheArgument$auditGeographicLibArgument"
& cmd.exe /d /s /c $configure
if ($LASTEXITCODE -ne 0) { throw "MoSim Ground Control CMake configure failed" }
if (-not $ConfigureOnly) {
    $build = "set `"PATH=$NinjaDir;$QtRoot\bin;$GStreamerRoot\bin;%PATH%`" && " +
        "call `"$VsDevCmd`" -arch=x64 -host_arch=x64 >nul && " +
        "set `"QTDIR=$QtRoot`" && set `"CMAKE_PREFIX_PATH=$QtRoot`" && " +
        "set `"GSTREAMER_1_0_ROOT_MSVC_X86_64=$GStreamerRoot`" && " +
        "cmake --build `"$BuildRoot`" --config $Configuration --parallel"
    & cmd.exe /d /s /c $build
    if ($LASTEXITCODE -ne 0) { throw "MoSim Ground Control build failed" }
}
