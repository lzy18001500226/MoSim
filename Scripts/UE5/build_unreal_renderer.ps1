param(
    [string]$UnrealEditorRoot = "D:\Program Files\Epic Games\UE_5.7",
    [string]$ProjectPath = "C:\Users\HP\Desktop\MoSim\UE5\MworksUnrealRenderer\MworksUnrealRenderer.uproject",
    [string]$Target = "MworksUnrealRendererEditor",
    [string]$Platform = "Win64",
    [string]$Configuration = "Development"
)

$ErrorActionPreference = "Stop"

$BuildBat = Join-Path $UnrealEditorRoot "Engine\Build\BatchFiles\Build.bat"
$DotNetExe = Join-Path $UnrealEditorRoot "Engine\Binaries\ThirdParty\DotNet\8.0.412\win-x64\dotnet.exe"
$UnrealBuildToolDll = Join-Path $UnrealEditorRoot "Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll"
if (-not (Test-Path $BuildBat)) {
    throw "Build.bat not found: $BuildBat"
}
if (-not (Test-Path $DotNetExe)) {
    throw "dotnet.exe not found: $DotNetExe"
}
if (-not (Test-Path $UnrealBuildToolDll)) {
    throw "UnrealBuildTool.dll not found: $UnrealBuildToolDll"
}
if (-not (Test-Path $ProjectPath)) {
    throw "Unreal project not found: $ProjectPath"
}

$Arguments = @(
    $Target,
    $Platform,
    $Configuration,
    "-Project=`"$ProjectPath`"",
    "-WaitMutex",
    "-NoHotReloadFromIDE"
)

$CommandLine = "`"$DotNetExe`" `"$UnrealBuildToolDll`" " + ($Arguments -join " ")
Write-Host "Running: $CommandLine"
& $DotNetExe $UnrealBuildToolDll @Arguments
exit $LASTEXITCODE
