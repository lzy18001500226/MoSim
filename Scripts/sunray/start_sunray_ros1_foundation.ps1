param(
    [switch]$Gui,
    [switch]$Review,
    [switch]$CleanExisting,
    [switch]$NoBuildLivox,
    [string]$RunId = ("sunray_ros1_foundation_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
)

$ErrorActionPreference = "Stop"
$ProjectRootWin = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$ProjectRootWsl = (& wsl.exe -d Ubuntu-20.04 --exec wslpath -a $ProjectRootWin).Trim()
if ([string]::IsNullOrWhiteSpace($ProjectRootWsl)) {
    throw "Unable to convert the project root to a WSL path."
}

$ResultDirWin = Join-Path $ProjectRootWin ("Results\sunray_ros1\" + $RunId)
New-Item -ItemType Directory -Force -Path $ResultDirWin | Out-Null
$ResultDirWsl = (& wsl.exe -d Ubuntu-20.04 --exec wslpath -a $ResultDirWin).Trim()

$foundationArgs = @()
if ($Review) { $foundationArgs += "--review" }
if ($Gui) { $foundationArgs += "--gui" }
if ($CleanExisting) { $foundationArgs += "--clean-existing" }
if ($NoBuildLivox) { $foundationArgs += "--no-build-livox" }
$argumentText = $foundationArgs -join " "

$command = "cd '$ProjectRootWsl' && PROJECT_ROOT='$ProjectRootWsl' RUN_ID='$RunId' RESULT_DIR='$ResultDirWsl' bash Scripts/sunray/run_sunray_ros1_foundation_gate.sh $argumentText"
Write-Host "Starting Sunray ROS1 foundation run: $RunId"
Write-Host "Result directory: $ResultDirWin"
Write-Host "No flight control is enabled."

& wsl.exe -d Ubuntu-20.04 --exec bash -lc $command
$exitCode = $LASTEXITCODE

$statusPath = Join-Path $ResultDirWin "STATUS.md"
if (Test-Path -LiteralPath $statusPath) {
    Write-Host ""
    Get-Content -LiteralPath $statusPath
}
if ($exitCode -ne 0) {
    $excerptPath = Join-Path $ResultDirWin "failure_excerpt.txt"
    if (Test-Path -LiteralPath $excerptPath) {
        Write-Host ""
        Write-Host "Failure excerpt:"
        Get-Content -LiteralPath $excerptPath
    }
}
exit $exitCode
