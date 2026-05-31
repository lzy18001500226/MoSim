#!/usr/bin/env bash
set -euo pipefail

# Open the project-owned Unreal renderer from WSL without editing global config.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
UPROJECT="${PROJECT_ROOT}/UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject"
MODE="${1:-editor}"
RESTART_UNREAL_GAME="${RESTART_UNREAL_GAME:-0}"
UNREAL_EXTRA_ARGS="${UNREAL_EXTRA_ARGS:-}"

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

resolve_unreal_editor() {
  if [[ -n "${UE_EDITOR:-}" ]]; then
    printf '%s\n' "${UE_EDITOR}"
    return
  fi
  local association
  association="$(engine_association)"
  local candidates=()
  if [[ -n "${association}" ]]; then
    candidates+=("/mnt/d/Program Files/Epic Games/UE_${association}/Engine/Binaries/Win64/UnrealEditor.exe")
    candidates+=("/mnt/d/Program Files/Epic Games/UE_${association}/Engine/Binaries/Win64/UE4Editor.exe")
  fi
  candidates+=(
    "/mnt/d/Program Files/Epic Games/UE_5.5/Engine/Binaries/Win64/UnrealEditor.exe"
    "/mnt/d/Program Files/Epic Games/UE_5.7/Engine/Binaries/Win64/UnrealEditor.exe"
    "/mnt/d/Program Files/Epic Games/UE_5.4/Engine/Binaries/Win64/UnrealEditor.exe"
    "/mnt/d/Program Files/Epic Games/UE_4.27/Engine/Binaries/Win64/UE4Editor.exe"
  )
  local candidate
  for candidate in "${candidates[@]}"; do
    if [[ -f "${candidate}" ]]; then
      printf '%s\n' "${candidate}"
      return
    fi
  done
  return 1
}

UE_EDITOR="$(resolve_unreal_editor || true)"

if [[ ! -f "${UE_EDITOR}" ]]; then
  echo "Unreal editor executable not found for ${UPROJECT}." >&2
  echo "Set UE_EDITOR to the installed UnrealEditor.exe or UE4Editor.exe path." >&2
  exit 2
fi

if [[ ! -f "${UPROJECT}" ]]; then
  echo "Unreal project not found: ${UPROJECT}" >&2
  exit 2
fi

focus_game_window() {
  powershell.exe -NoProfile -Command \
    "Add-Type @'
using System;
using System.Runtime.InteropServices;
public class WinApi {
  [DllImport(\"user32.dll\")] public static extern bool SetForegroundWindow(IntPtr hWnd);
}
'@;
\$game = Get-CimInstance Win32_Process -Filter \"name = 'UnrealEditor.exe'\" | Where-Object { \$_.CommandLine -like '*MoSimSceneLibrary.uproject*' -and \$_.CommandLine -like '* -game*' } | Select-Object -First 1;
if (\$game) {
  \$proc = Get-Process -Id \$game.ProcessId -ErrorAction SilentlyContinue;
  if (\$proc -and \$proc.MainWindowHandle -ne 0) { [WinApi]::SetForegroundWindow(\$proc.MainWindowHandle) | Out-Null }
}" >/dev/null 2>&1 || true
}

if [[ "${MODE}" == "editor" ]] && powershell.exe -NoProfile -Command \
  "Get-CimInstance Win32_Process -Filter \"name = 'UnrealEditor.exe'\" | Where-Object { \$_.CommandLine -like '*MoSimSceneLibrary.uproject*' -and \$_.CommandLine -notlike '* -game*' } | Select-Object -First 1 | ForEach-Object { exit 0 }; exit 1" >/dev/null 2>&1; then
  echo "MoSimSceneLibrary UnrealEditor is already running."
  exit 0
fi

if [[ "${MODE}" == "game" ]] && powershell.exe -NoProfile -Command \
  "Get-CimInstance Win32_Process -Filter \"name = 'UnrealEditor.exe'\" | Where-Object { \$_.CommandLine -like '*MoSimSceneLibrary.uproject*' -and \$_.CommandLine -like '* -game*' } | Select-Object -First 1 | ForEach-Object { exit 0 }; exit 1" >/dev/null 2>&1; then
  if [[ "${RESTART_UNREAL_GAME}" == "1" ]]; then
    echo "Restarting existing MoSimSceneLibrary game window."
    powershell.exe -NoProfile -Command \
      "Get-CimInstance Win32_Process -Filter \"name = 'UnrealEditor.exe'\" | Where-Object { \$_.CommandLine -like '*MoSimSceneLibrary.uproject*' -and \$_.CommandLine -like '* -game*' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }" >/dev/null
    sleep 2
  else
    echo "MoSimSceneLibrary game window is already running."
    focus_game_window
    exit 0
  fi
fi

case "${MODE}" in
  editor)
    EXTRA_ARGS=()
    ;;
  game)
    EXTRA_ARGS=("-game" "-windowed" "-ResX=1280" "-ResY=720")
    ;;
  review-scene)
    EXTRA_ARGS=("-game" "-windowed" "-ResX=1280" "-ResY=720" "-MoSimSceneReview")
    ;;
  *)
    echo "Usage: $0 [editor|game|review-scene]" >&2
    exit 2
    ;;
esac

UE_WIN="$(wslpath -w "${UE_EDITOR}")"
UPROJECT_WIN="$(wslpath -w "${UPROJECT}")"
if [[ "${#EXTRA_ARGS[@]}" -eq 0 ]]; then
  powershell.exe -NoProfile -Command \
    "Start-Process -FilePath '${UE_WIN}' -ArgumentList @('${UPROJECT_WIN}') | Out-Null"
else
  EXTRA_ARGS_WIN=()
  if [[ -n "${UNREAL_EXTRA_ARGS}" ]]; then
    # shellcheck disable=SC2206
    EXTRA_ARGS_WIN=(${UNREAL_EXTRA_ARGS})
  fi
  ARG_LIST="'${UPROJECT_WIN}'"
  for Arg in "${EXTRA_ARGS[@]}" "${EXTRA_ARGS_WIN[@]}"; do
    ARG_LIST="${ARG_LIST}, '${Arg}'"
  done
  powershell.exe -NoProfile -Command \
    "Start-Process -FilePath '${UE_WIN}' -ArgumentList @(${ARG_LIST}) | Out-Null"
  sleep 5
  focus_game_window
fi
