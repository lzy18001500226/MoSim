#!/usr/bin/env bash
set -euo pipefail

# Build the project-owned Unreal renderer editor target from WSL.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
UE_ROOT="${UE_ROOT:-/mnt/d/Program Files/Epic Games/UE_5.7}"
DOTNET_EXE="${UE_ROOT}/Engine/Binaries/ThirdParty/DotNet/8.0.412/win-x64/dotnet.exe"
UBT_DLL="${UE_ROOT}/Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll"
UPROJECT_WIN="$(wslpath -w "${PROJECT_ROOT}/UE5/MworksUnrealRenderer/MworksUnrealRenderer.uproject")"

if [[ ! -f "${DOTNET_EXE}" ]]; then
  echo "dotnet.exe not found: ${DOTNET_EXE}" >&2
  exit 2
fi

if [[ ! -f "${UBT_DLL}" ]]; then
  echo "UnrealBuildTool.dll not found: ${UBT_DLL}" >&2
  exit 2
fi

UBT_WIN="$(wslpath -w "${UBT_DLL}")"

export PATHEXT="${PATHEXT:-.COM;.EXE;.BAT;.CMD}"
export DOTNET_CLI_TELEMETRY_OPTOUT="${DOTNET_CLI_TELEMETRY_OPTOUT:-1}"

"${DOTNET_EXE}" "${UBT_WIN}" \
  MworksUnrealRendererEditor Win64 Development \
  "-Project=${UPROJECT_WIN}" \
  -WaitMutex \
  -NoHotReloadFromIDE \
  "$@"
