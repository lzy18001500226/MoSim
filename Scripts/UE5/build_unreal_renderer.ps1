param(
    [string]$UnrealEditorRoot = "",
    [string]$ProjectPath = "C:\Users\HP\Desktop\MoSim\UE5\MoSimSceneLibrary\MoSimSceneLibrary.uproject",
    [string]$Target = "MoSimSceneLibraryEditor",
    [string]$Platform = "Win64",
    [string]$Configuration = "Development"
)

$ErrorActionPreference = "Stop"

if (-not $UnrealEditorRoot) {
    $ProjectJson = Get-Content $ProjectPath -Raw | ConvertFrom-Json
    $Association = $ProjectJson.EngineAssociation
    $Candidates = @()
    if ($Association) {
        $Candidates += "D:\Program Files\Epic Games\UE_$Association"
    }
    $Candidates += @(
        "D:\Program Files\Epic Games\UE_5.5",
        "D:\Program Files\Epic Games\UE_5.7",
        "D:\Program Files\Epic Games\UE_5.4",
        "D:\Program Files\Epic Games\UE_4.27"
    )
    foreach ($Candidate in $Candidates) {
        if (Test-Path (Join-Path $Candidate "Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll")) {
            $UnrealEditorRoot = $Candidate
            break
        }
    }
}

$BuildBat = Join-Path $UnrealEditorRoot "Engine\Build\BatchFiles\Build.bat"
$DotNetCandidates = Get-ChildItem -Path (Join-Path $UnrealEditorRoot "Engine\Binaries\ThirdParty\DotNet") -Filter dotnet.exe -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -like "*\win-x64\dotnet.exe" } |
    Sort-Object FullName
$DotNetExe = if ($DotNetCandidates) { $DotNetCandidates[-1].FullName } else { "" }
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
    "-Project=$ProjectPath",
    "-WaitMutex",
    "-NoHotReloadFromIDE"
)

$CommandLine = "`"$DotNetExe`" `"$UnrealBuildToolDll`" " + ($Arguments -join " ")
Write-Host "Running: $CommandLine"
& $DotNetExe $UnrealBuildToolDll @Arguments
exit $LASTEXITCODE
