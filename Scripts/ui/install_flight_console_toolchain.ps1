[CmdletBinding()]
param(
    [string]$ToolRoot = "",
    [switch]$SkipQt,
    [switch]$SkipGStreamer
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
if (-not $ToolRoot) { $ToolRoot = Join-Path $ProjectRoot ".tools/flight-console" }
$ToolRoot = [IO.Path]::GetFullPath($ToolRoot)
if (-not $ToolRoot.StartsWith($ProjectRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw "ToolRoot must stay inside the MoSim repository: $ToolRoot"
}

$PythonRoot = Join-Path $ToolRoot "python"
$QtBase = Join-Path $ToolRoot "qt"
$QtRoot = Join-Path $QtBase "6.8.3/msvc2022_64"
$DownloadRoot = Join-Path $ToolRoot "downloads"
$GStreamerImage = Join-Path $ToolRoot "gstreamer"
$SourceRoot = Join-Path $ToolRoot "sources"
New-Item -ItemType Directory -Force -Path $ToolRoot, $DownloadRoot | Out-Null

if (-not (Test-Path (Join-Path $PythonRoot "Scripts/python.exe"))) {
    python -m venv $PythonRoot
}
$PrivatePython = Join-Path $PythonRoot "Scripts/python.exe"
& $PrivatePython -m pip install --disable-pip-version-check "aqtinstall==3.3.0" "ninja==1.13.0"
if ($LASTEXITCODE -ne 0) { throw "Failed to install private aqtinstall/Ninja" }

if (-not $SkipQt -and -not (Test-Path (Join-Path $QtRoot "bin/qtpaths6.exe"))) {
    $AqtArgs = @(
        "-m", "aqt", "install-qt", "windows", "desktop", "6.8.3",
        "win64_msvc2022_64", "-O", $QtBase, "-m",
        "qtcharts", "qtlocation", "qtpositioning", "qtspeech", "qt5compat",
        "qtmultimedia", "qtserialport", "qtimageformats", "qtshadertools",
        "qtconnectivity", "qtquick3d", "qtsensors"
    )
    & $PrivatePython @AqtArgs
    if ($LASTEXITCODE -ne 0) { throw "Failed to install private Qt 6.8.3" }
}

$GpsSha = "8fdef3bc0cb7820119abdb7320ad3992af2e440f"
$GpsArchiveSha256 = "1437DC5D2FE7F3C6F9F24396DBAEB55C79A4F9E0F95D8EF559AD14ADB0237FAF"
$GpsArchive = Join-Path $DownloadRoot "px4-gpsdrivers-$GpsSha.tar.gz"
$GpsSource = Join-Path $SourceRoot "PX4-GPSDrivers-$GpsSha"
if (-not (Test-Path (Join-Path $GpsSource "src/ubx.h"))) {
    if (-not (Test-Path $GpsArchive)) {
        Invoke-WebRequest -UseBasicParsing -Uri "https://codeload.github.com/PX4/PX4-GPSDrivers/tar.gz/$GpsSha" -OutFile $GpsArchive
    }
    $ActualHash = (Get-FileHash -LiteralPath $GpsArchive -Algorithm SHA256).Hash
    if ($ActualHash -ne $GpsArchiveSha256) {
        throw "PX4-GPSDrivers archive hash mismatch: $ActualHash"
    }
    New-Item -ItemType Directory -Force -Path $SourceRoot | Out-Null
    & tar -xf $GpsArchive -C $SourceRoot
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path (Join-Path $GpsSource "src/ubx.h"))) {
        throw "Failed to extract pinned PX4-GPSDrivers source"
    }
}

if (-not $SkipGStreamer) {
    $Version = "1.22.12"
    $BaseUrl = "https://gstreamer.freedesktop.org/data/pkg/windows/$Version/msvc"
    $Packages = @(
        "gstreamer-1.0-msvc-x86_64-$Version.msi",
        "gstreamer-1.0-devel-msvc-x86_64-$Version.msi"
    )
    foreach ($Package in $Packages) {
        $Msi = Join-Path $DownloadRoot $Package
        if (-not (Test-Path $Msi)) {
            Invoke-WebRequest -Uri "$BaseUrl/$Package" -OutFile $Msi
        }
        $MsiArgs = "/a `"$Msi`" /qn TARGETDIR=`"$GStreamerImage`""
        $Process = Start-Process msiexec.exe -ArgumentList $MsiArgs -Wait -PassThru -WindowStyle Hidden
        if ($Process.ExitCode -ne 0) {
            throw "GStreamer administrative extraction failed for $Package (exit $($Process.ExitCode))"
        }
    }
}

& $PrivatePython (Join-Path $ProjectRoot "Scripts/ui/check_qgc_windows_toolchain.py") --tool-root $ToolRoot
if ($LASTEXITCODE -ne 0) { throw "Private Flight Console toolchain preflight failed" }

Write-Host "Flight Console private toolchain is ready at $ToolRoot"
