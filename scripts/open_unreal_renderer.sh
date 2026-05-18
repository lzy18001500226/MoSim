#!/usr/bin/env bash
set -euo pipefail

# Open the project-owned Unreal renderer from WSL without editing global config.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/Quadrotor"
UE_EDITOR="${UE_EDITOR:-/mnt/d/Program Files/Epic Games/UE_5.7/Engine/Binaries/Win64/UnrealEditor.exe}"
UPROJECT="${PROJECT_ROOT}/unreal/MworksUnrealRenderer/MworksUnrealRenderer.uproject"

if [[ ! -f "${UE_EDITOR}" ]]; then
  echo "UnrealEditor.exe not found: ${UE_EDITOR}" >&2
  echo "Set UE_EDITOR to the installed UnrealEditor.exe path." >&2
  exit 2
fi

if [[ ! -f "${UPROJECT}" ]]; then
  echo "Unreal project not found: ${UPROJECT}" >&2
  exit 2
fi

cmd.exe /C start "" "$(wslpath -w "${UE_EDITOR}")" "$(wslpath -w "${UPROJECT}")"
