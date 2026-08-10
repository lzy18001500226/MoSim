[CmdletBinding()]
param(
    [string]$Preflight = "",
    [string]$Executable = "",
    [switch]$PassThru,
    [switch]$ResolveOnly,
    [switch]$AuditInstance,
    [ValidateRange(1, 60)]
    [int]$StartupTimeoutSeconds = 15
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
if (-not $Preflight) {
    $Preflight = Join-Path $ProjectRoot "Results/ui_platform/flight_console_windows_toolchain_preflight.json"
}
$ExecutableWasSpecified = [bool]$Executable
$FormalExecutable = Join-Path $ProjectRoot "build/flight-console-qgc/Release/MoSimGroundControl.exe"
$CandidateExecutable = Join-Path $ProjectRoot "build/flight-console-qgc-candidate/Release/MoSimGroundControl.exe"
$AuditExecutable = Join-Path $ProjectRoot "build/flight-console-qgc-audit/Release/MoSimGroundControlAudit.exe"

if ($AuditInstance) {
    if (-not $ExecutableWasSpecified) {
        $Executable = $AuditExecutable
    } elseif (-not [String]::Equals([IO.Path]::GetFullPath($Executable), [IO.Path]::GetFullPath($AuditExecutable), [StringComparison]::OrdinalIgnoreCase)) {
        throw "-AuditInstance is restricted to $AuditExecutable"
    }
} elseif (-not $ExecutableWasSpecified) {
    $Executable = $FormalExecutable
    if (Test-Path -LiteralPath $CandidateExecutable) {
        $candidateItem = Get-Item -LiteralPath $CandidateExecutable
        $formalItem = if (Test-Path -LiteralPath $FormalExecutable) {
            Get-Item -LiteralPath $FormalExecutable
        } else {
            $null
        }
        if ($null -eq $formalItem -or $candidateItem.LastWriteTimeUtc -gt $formalItem.LastWriteTimeUtc) {
            $Executable = $CandidateExecutable
            Write-Output "Using newer MoSim Ground Control candidate build: $Executable"
        }
    }
}

if ($ResolveOnly) {
    if (-not (Test-Path -LiteralPath $Executable)) {
        throw "MoSim Ground Control executable is missing: $Executable"
    }
    Write-Output (Resolve-Path $Executable).Path
    exit 0
}

$existing = if ($AuditInstance) {
    Get-Process -Name "MoSimGroundControlAudit" -ErrorAction SilentlyContinue | Select-Object -First 1
} else {
    Get-Process -Name "MoSimGroundControl" -ErrorAction SilentlyContinue | Select-Object -First 1
}
if ($existing) {
    Write-Output "MoSim Ground Control is already running (PID $($existing.Id))."
    if ($PassThru) { $existing }
    exit 0
}

if (-not (Test-Path -LiteralPath $Preflight)) {
    throw "MoSim Ground Control preflight is missing. Run Scripts/ui/build_flight_console.ps1 first."
}
$report = Get-Content -LiteralPath $Preflight -Raw | ConvertFrom-Json
if ($report.status -ne "ready") {
    throw "MoSim Ground Control toolchain is not ready. See $Preflight"
}
if (-not (Test-Path -LiteralPath $Executable)) {
    throw "MoSim Ground Control executable is missing. Run Scripts/ui/build_flight_console.ps1 first."
}

$QtBin = Join-Path $report.detected.qt_root "bin"
$GStreamerBin = Join-Path $report.detected.gstreamer_root "bin"
foreach ($path in @($QtBin, $GStreamerBin)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "MoSim Ground Control runtime dependency path is missing: $path"
    }
}

$env:PATH = "$QtBin;$GStreamerBin;$env:PATH"
$process = Start-Process -FilePath (Resolve-Path $Executable).Path `
    -WorkingDirectory (Split-Path -Parent (Resolve-Path $Executable).Path) `
    -PassThru
$deadline = [DateTime]::UtcNow.AddSeconds($StartupTimeoutSeconds)
$windowReady = $false
while ([DateTime]::UtcNow -lt $deadline) {
    Start-Sleep -Milliseconds 250
    $process.Refresh()
    if ($process.HasExited) {
        throw "MoSim Ground Control exited during startup (PID $($process.Id), exit code $($process.ExitCode))."
    }
    if ($process.MainWindowHandle -ne [IntPtr]::Zero) {
        $windowReady = $true
        break
    }
}

if (-not $windowReady) {
    $process.Refresh()
    if ($process.HasExited) {
        throw "MoSim Ground Control exited during startup (PID $($process.Id), exit code $($process.ExitCode))."
    }
    throw "MoSim Ground Control did not create a main window within $StartupTimeoutSeconds seconds (PID $($process.Id))."
}

Write-Output "Started MoSim Ground Control (PID $($process.Id), main window ready)."
Write-Output "MoSim Ground Control executable: $((Resolve-Path $Executable).Path)"
if ($PassThru) { $process }
