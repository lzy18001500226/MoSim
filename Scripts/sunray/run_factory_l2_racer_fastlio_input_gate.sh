#!/usr/bin/env bash
# Run the bounded Factory L2 RACER MID360/FAST-LIO input-only gate.

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
STAMP="$(date +%Y%m%d_%H%M%S)"
RUN_ID="${RUN_ID:-factory_l2_racer_fastlio_input_${STAMP}}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
mkdir -p "${RESULT_DIR}"

export PROJECT_ROOT RUN_ID RESULT_DIR
export PLANNER_VARIANT=racer
export RACER_SENSOR_SOURCE=fastlio
export RACER_INPUT_GATE_ONLY=true
export GUI=false
export KEEP_ALIVE=false
export WORLD_FILE="${WORLD_FILE:-${PROJECT_ROOT}/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf}"
export SUNRAY_GAZEBO_LAUNCH_FILE="${SUNRAY_GAZEBO_LAUNCH_FILE:-${PROJECT_ROOT}/Scripts/sunray/factory_l2_sunray_px4_gazebo.launch}"
export START1_X="${START1_X:--10.575025}"
export START1_Y="${START1_Y:--19.36313}"
export START2_X="${START2_X:--8.575025}"
export START2_Y="${START2_Y:--19.36313}"
export START3_X="${START3_X:--10.575025}"
export START3_Y="${START3_Y:--17.36313}"
export RACER_FRAME_BRIDGE_ENABLED=true
export RACER_FRAME_OFFSET_X="${RACER_FRAME_OFFSET_X:--10.575025}"
export RACER_FRAME_OFFSET_Y="${RACER_FRAME_OFFSET_Y:--19.36313}"
export RACER_FRAME_OFFSET_Z="${RACER_FRAME_OFFSET_Z:-0.0}"
export RACER_FASTLIO_ALIGNMENT_Z_SOURCE="${RACER_FASTLIO_ALIGNMENT_Z_SOURCE:-truth}"
export RACER_FASTLIO_FILTER_SIZE_SURF="${RACER_FASTLIO_FILTER_SIZE_SURF:-0.5}"
export RACER_FASTLIO_FILTER_SIZE_MAP="${RACER_FASTLIO_FILTER_SIZE_MAP:-0.5}"
export RACER_FASTLIO_SCAN_RATE_HZ="${RACER_FASTLIO_SCAN_RATE_HZ:-20}"
export RACER_FASTLIO_READY_TIMEOUT_S="${RACER_FASTLIO_READY_TIMEOUT_S:-90}"
export MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-120}"
export LIDAR_READY_TIMEOUT_S="${LIDAR_READY_TIMEOUT_S:-120}"
export GOAL5_STARTUP_ATTEMPTS=1
export STAGGERED_SPAWN="${STAGGERED_SPAWN:-true}"
export STAGGERED_SPAWN_INTERVAL_S="${STAGGERED_SPAWN_INTERVAL_S:-8}"
export TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-240}"
export PX4CTRL_START_EXTERNAL_FUSION=false

timeout --kill-after=15s "$((TOTAL_TIMEOUT_S + 30))s" \
  bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh"
