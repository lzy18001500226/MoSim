[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRootWin = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$ProjectRootWsl = (& wsl.exe -d Ubuntu-20.04 --exec wslpath -a $ProjectRootWin).Trim()
if ([string]::IsNullOrWhiteSpace($ProjectRootWsl)) {
    throw "Unable to convert the project root to a WSL path."
}

$command = "cd '$ProjectRootWsl' && PROJECT_ROOT='$ProjectRootWsl' bash Scripts/sunray/stop_sunray_ros1_foundation.sh"
& wsl.exe -d Ubuntu-20.04 --exec bash -lc $command
exit $LASTEXITCODE
