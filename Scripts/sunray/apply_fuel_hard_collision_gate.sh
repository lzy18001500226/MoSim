#!/usr/bin/env bash

set -euo pipefail

project_root="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
fuel_source_root="${1:-/opt/mosim_work/sunray_ws/fuel_ext4_sources_20260709/fuel_planner}"
fuel_workspace="${2:-/opt/mosim_work/sunray_ws/fuel_ws_release_20260713}"

if ! grep -q '\[FUEL_HARD_COLLISION_GATE\]' \
  "${fuel_source_root}/plan_manage/src/planner_manager.cpp"; then
  python3 "${project_root}/Scripts/sunray/patch_fuel_hard_collision_gate.py" "${fuel_source_root}"
else
  echo "FUEL hard-collision patch is already present"
fi

if ! grep -q '\[FUEL_COLLISION_RECOVERY_RECORD\]' \
  "${fuel_source_root}/exploration_manager/src/fast_exploration_manager.cpp"; then
  python3 "${project_root}/Scripts/sunray/patch_fuel_collision_recovery.py" "${fuel_source_root}"
else
  echo "FUEL collision-recovery patch is already present"
fi

if ! grep -q '\[FUEL_UNREACHABLE_RECORD\]' \
  "${fuel_source_root}/exploration_manager/src/fast_exploration_manager.cpp"; then
  python3 "${project_root}/Scripts/sunray/patch_fuel_unreachable_frontier_recovery.py" \
    "${fuel_source_root}"
else
  echo "FUEL unreachable-frontier recovery patch is already present"
fi

python3 "${project_root}/Scripts/sunray/patch_fuel_tracking_error_recovery.py" "${fuel_source_root}"

set +u
# Non-interactive Windows-to-WSL shells do not inherit ROS tools in PATH.
source /opt/ros/noetic/setup.bash
set -u

cd "${fuel_workspace}"
catkin_make --pkg plan_manage exploration_manager -DCMAKE_BUILD_TYPE=Release -j2
