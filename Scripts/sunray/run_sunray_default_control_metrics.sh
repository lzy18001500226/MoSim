#!/usr/bin/env bash
# Record upstream Sunray demo_id=1 trajectory and compute basic control metrics.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/tmp/mosim_sunray_build_20260620_114615/Sunray}"
RUN_ID="${RUN_ID:-sunray_default_control_metrics_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"

mkdir -p "${RESULT_DIR}"

source /opt/ros/noetic/setup.bash
source "${SUNRAY_WS}/devel/setup.bash"

python3 "${PROJECT_ROOT}/Scripts/sunray/record_sunray_default_demo_metrics.py" \
  --result-dir "${RESULT_DIR}" \
  --duration "${METRICS_DURATION:-45}" \
  --target-x "${TARGET_X:-1.0}" \
  --target-y "${TARGET_Y:-1.0}" \
  --target-z "${TARGET_Z:-1.0}" \
  > "${RESULT_DIR}/metrics_recorder.log" 2>&1 &
REC_PID=$!

sleep 2
timeout "${DEMO_TIMEOUT:-95}s" roslaunch sunray_tutorial run_demo.launch \
  demo_id:=1 uav_id:=1 uav_name:=uav \
  > "${RESULT_DIR}/takeoff_hover_land_demo.log" 2>&1 || true

wait "${REC_PID}"

cat "${RESULT_DIR}/SUNRAY_DEFAULT_CONTROL_METRICS.json"
