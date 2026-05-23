#!/usr/bin/env bash
set -euo pipefail

# Open the project-owned Unreal renderer from WSL without editing global config.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/Quadrotor"
UE_EDITOR="${UE_EDITOR:-/mnt/d/Program Files/Epic Games/UE_5.7/Engine/Binaries/Win64/UnrealEditor.exe}"
UPROJECT="${PROJECT_ROOT}/unreal/MworksUnrealRenderer/MworksUnrealRenderer.uproject"
MODE="${1:-editor}"
RESTART_UNREAL_GAME="${RESTART_UNREAL_GAME:-0}"

if [[ ! -f "${UE_EDITOR}" ]]; then
  echo "UnrealEditor.exe not found: ${UE_EDITOR}" >&2
  echo "Set UE_EDITOR to the installed UnrealEditor.exe path." >&2
  exit 2
fi

if [[ ! -f "${UPROJECT}" ]]; then
  echo "Unreal project not found: ${UPROJECT}" >&2
  exit 2
fi

if [[ "${MODE}" == "editor" ]] && powershell.exe -NoProfile -Command \
  "Get-CimInstance Win32_Process -Filter \"name = 'UnrealEditor.exe'\" | Where-Object { \$_.CommandLine -like '*MworksUnrealRenderer.uproject*' } | Select-Object -First 1 | ForEach-Object { exit 0 }; exit 1" >/dev/null 2>&1; then
  echo "MworksUnrealRenderer UnrealEditor is already running."
  exit 0
fi

if [[ "${MODE}" == "game" ]] && powershell.exe -NoProfile -Command \
  "Get-CimInstance Win32_Process -Filter \"name = 'UnrealEditor.exe'\" | Where-Object { \$_.CommandLine -like '*MworksUnrealRenderer.uproject*' -and \$_.CommandLine -like '* -game*' } | Select-Object -First 1 | ForEach-Object { exit 0 }; exit 1" >/dev/null 2>&1; then
  if [[ "${RESTART_UNREAL_GAME}" == "1" ]]; then
    echo "Restarting existing MworksUnrealRenderer game window."
    powershell.exe -NoProfile -Command \
      "Get-CimInstance Win32_Process -Filter \"name = 'UnrealEditor.exe'\" | Where-Object { \$_.CommandLine -like '*MworksUnrealRenderer.uproject*' -and \$_.CommandLine -like '* -game*' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }" >/dev/null
    sleep 2
  else
    echo "MworksUnrealRenderer game window is already running."
    exit 0
  fi
fi

case "${MODE}" in
  editor)
    EXTRA_ARGS=()
    ;;
  game)
    EXTRA_ARGS=("-game" "-windowed" "-ResX=1280" "-ResY=720" "-log")
    ;;
  *)
    echo "Usage: $0 [editor|game]" >&2
    exit 2
    ;;
esac

UE_WIN="$(wslpath -w "${UE_EDITOR}")"
UPROJECT_WIN="$(wslpath -w "${UPROJECT}")"
if [[ "${#EXTRA_ARGS[@]}" -eq 0 ]]; then
  powershell.exe -NoProfile -Command \
    "Start-Process -FilePath '${UE_WIN}' -ArgumentList @('${UPROJECT_WIN}') | Out-Null"
else
  powershell.exe -NoProfile -Command \
    "Start-Process -FilePath '${UE_WIN}' -ArgumentList @('${UPROJECT_WIN}', '-game', '-windowed', '-ResX=1280', '-ResY=720', '-log') | Out-Null"
fi
