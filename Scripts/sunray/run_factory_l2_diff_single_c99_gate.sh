#!/usr/bin/env bash
# Factory L2 C99 single-UAV Diff fixed-goal gate.
#
# This is deliberately a thin Factory contract around the generic interactive
# Diff gate. Keep the generic entry available for planning_test diagnostics;
# evidence produced here must load the reviewed Factory static SDF.

set -euo pipefail

case "${1:-}" in
  "")
    ;;
  -h|--help)
    cat <<'EOF'
Usage: bash Scripts/sunray/run_factory_l2_diff_single_c99_gate.sh

Runs the Factory L2 single-UAV graphical-C99 Diff fixed-goal gate.
The gate pins the clean Factory SDF, spawn pose, fixed target, and 5-second
target/final-hover holds. Set RUN_ID or RESULT_DIR before invoking it to
choose the output location.
EOF
    exit 0
    ;;
  *)
    printf 'Unexpected argument: %s\n' "$1" >&2
    exit 2
    ;;
esac

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RUN_ID="${RUN_ID:-factory_l2_diff_single_c99_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"

FACTORY_WORLD_FILE="${PROJECT_ROOT}/Config/gazebo/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf"
FACTORY_MODEL_PATH="${PROJECT_ROOT}/Config/gazebo/models"
FACTORY_GAZEBO_LAUNCH="${PROJECT_ROOT}/Scripts/sunray/factory_l2_sunray_px4_gazebo.launch"

# This scene-specific mapping is evidenced by the C99 Factory fixed-hover
# retest. It is not a replacement for the project-wide MWORKS calibration or
# another runtime profile's hover setting.
PX4CTRL_HOVER_PERCENTAGE="${PX4CTRL_HOVER_PERCENTAGE:-0.294}"

exec env \
  PROJECT_ROOT="${PROJECT_ROOT}" \
  RUN_ID="${RUN_ID}" \
  RESULT_DIR="${RESULT_DIR}" \
  FACTORY_WORLD_MODE=clean \
  WORLD_FILE="${FACTORY_WORLD_FILE}" \
  FACTORY_MODEL_PATH="${FACTORY_MODEL_PATH}" \
  SUNRAY_GAZEBO_LAUNCH_FILE="${FACTORY_GAZEBO_LAUNCH}" \
  SUNRAY_UAV_INIT_X=0.0 \
  SUNRAY_UAV_INIT_Y=120.0 \
  SUNRAY_UAV_INIT_Z=0.2 \
  SUNRAY_UAV_INIT_YAW=0.0 \
  GOALS=-4.0,118.0,1.0 \
  TARGET_X=-4.0 \
  TARGET_Y=118.0 \
  TARGET_Z=1.0 \
  DIFF_INTERACTIVE_AUTO_PASS_GOAL_COUNT=1 \
  DIFF_INTERACTIVE_TARGET_HOLD_S=5.0 \
  DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S=5.0 \
  PX4CTRL_HOVER_PERCENTAGE="${PX4CTRL_HOVER_PERCENTAGE}" \
  bash "${PROJECT_ROOT}/Scripts/sunray/run_diff_single_auto123_gate.sh"
