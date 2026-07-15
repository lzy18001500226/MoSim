#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
FUEL_WS="${FUEL_WS:-/opt/mosim_work/sunray_ws/fuel_ws_planner_only_debug_20260701_003}"
PATCH_FILE="${PROJECT_ROOT}/Scripts/sunray/patches/fuel_hard_dynamic_feasibility.patch"
SOURCE_ROOT="${FUEL_WS}/src/fuel_planner"

if [[ ! -d "${SOURCE_ROOT}/plan_manage" ]]; then
  echo "FUEL source root not found: ${SOURCE_ROOT}" >&2
  exit 2
fi

if git -C "${SOURCE_ROOT}" apply --reverse --check "${PATCH_FILE}" >/dev/null 2>&1; then
  echo "FUEL dynamic-feasibility patch already applied"
elif git -C "${SOURCE_ROOT}" apply --check "${PATCH_FILE}"; then
  git -C "${SOURCE_ROOT}" apply "${PATCH_FILE}"
  echo "Applied FUEL dynamic-feasibility patch"
else
  echo "Patch does not apply cleanly; source drift must be reviewed" >&2
  exit 3
fi

if [[ "${BUILD_FUEL_AFTER_PATCH:-true}" == "true" ]]; then
  cd "${FUEL_WS}"
  source /opt/ros/noetic/setup.bash
  catkin_make --pkg plan_manage exploration_manager -DCMAKE_BUILD_TYPE=Release
fi
