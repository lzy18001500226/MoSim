#!/usr/bin/env bash
set -euo pipefail

# Build the project-owned Unreal renderer editor target from WSL.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
UPROJECT="${PROJECT_ROOT}/UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject"

engine_association() {
  python3 - <<'PY'
import json
from pathlib import Path
project = Path("/mnt/c/Users/HP/Desktop/MoSim/UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject")
try:
    print(json.loads(project.read_text(encoding="utf-8")).get("EngineAssociation", ""))
except Exception:
    print("")
PY
}

resolve_ue_root() {
  if [[ -n "${UE_ROOT:-}" ]]; then
    printf '%s\n' "${UE_ROOT}"
    return
  fi
  local association
  association="$(engine_association)"
  local candidates=()
  if [[ -n "${association}" ]]; then
    candidates+=("/mnt/d/Program Files/Epic Games/UE_${association}")
  fi
  candidates+=(
    "/mnt/d/Program Files/Epic Games/UE_5.5"
    "/mnt/d/Program Files/Epic Games/UE_5.7"
    "/mnt/d/Program Files/Epic Games/UE_5.4"
    "/mnt/d/Program Files/Epic Games/UE_4.27"
  )
  local candidate
  for candidate in "${candidates[@]}"; do
    if [[ -f "${candidate}/Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll" ]]; then
      printf '%s\n' "${candidate}"
      return
    fi
  done
  return 1
}

UE_ROOT="$(resolve_ue_root || true)"
DOTNET_EXE="${DOTNET_EXE:-}"
if [[ -z "${DOTNET_EXE}" ]]; then
  DOTNET_EXE="$(find "${UE_ROOT}/Engine/Binaries/ThirdParty/DotNet" -path '*/win-x64/dotnet.exe' -print | sort -V | tail -n 1)"
fi
UBT_DLL="${UE_ROOT}/Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll"
UPROJECT_WIN="$(wslpath -w "${UPROJECT}")"

if [[ ! -f "${DOTNET_EXE}" ]]; then
  echo "dotnet.exe not found: ${DOTNET_EXE}" >&2
  exit 2
fi

if [[ ! -f "${UBT_DLL}" ]]; then
  echo "UnrealBuildTool.dll not found: ${UBT_DLL}" >&2
  exit 2
fi

if [[ ! -f "${UPROJECT}" ]]; then
  echo "Unreal project not found: ${UPROJECT}" >&2
  exit 2
fi

UBT_WIN="$(wslpath -w "${UBT_DLL}")"

export PATHEXT="${PATHEXT:-.COM;.EXE;.BAT;.CMD}"
export DOTNET_CLI_TELEMETRY_OPTOUT="${DOTNET_CLI_TELEMETRY_OPTOUT:-1}"

"${DOTNET_EXE}" "${UBT_WIN}" \
  MoSimSceneLibraryEditor Win64 Development \
  "-Project=${UPROJECT_WIN}" \
  -WaitMutex \
  -NoHotReloadFromIDE \
  "$@"
