#!/usr/bin/env bash
set -euo pipefail

# Open a Windows-native WPF point-cloud/local-map preview fallback. This is not
# the official FAST-LIO/RViz runtime evidence path and does not use browser HTML.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
SCENE_ID="${1:-factoryenvironmentcollect}"
MAX_FRAMES="${MAX_FRAMES:-8}"
MAX_POINTS_PER_FRAME="${MAX_POINTS_PER_FRAME:-900}"
DRY_RUN="${DRY_RUN:-0}"

cd "${PROJECT_ROOT}"

if ! command -v powershell.exe >/dev/null 2>&1; then
  echo "Missing powershell.exe. This native preview fallback requires Windows PowerShell from WSL." >&2
  exit 4
fi

WIN_PROJECT_ROOT="$(wslpath -w "${PROJECT_ROOT}")"
ARGS=(
  -NoProfile
  -ExecutionPolicy Bypass
  -File "${WIN_PROJECT_ROOT}\\Scripts\\UE5\\open_native_pointcloud_preview.ps1"
  -SceneId "${SCENE_ID}"
  -ProjectRoot "${WIN_PROJECT_ROOT}"
  -MaxFrames "${MAX_FRAMES}"
  -MaxPointsPerFrame "${MAX_POINTS_PER_FRAME}"
)

if [[ "${DRY_RUN}" == "1" ]]; then
  ARGS+=(-DryRun)
fi

powershell.exe "${ARGS[@]}"
