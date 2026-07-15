#!/usr/bin/env bash
# Headless Goal4 Diff-Planner single-UAV 1-2-3 interactive-goal gate.
#
# This wrapper keeps the runner and the standalone goal-chain probe in one WSL
# process so bash status variables such as $! and $? are not mangled by Windows
# command quoting. It is intended for metrics/evidence runs, not RViz review.

set -uo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RUN_ID="${RUN_ID:-diff_single_auto123_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"

GOALS="${GOALS:-1.0,0.0,1.0;2.0,0.0,1.0;3.0,0.5,1.0}"
GOAL_COUNT="${DIFF_INTERACTIVE_AUTO_PASS_GOAL_COUNT:-$(printf '%s\n' "${GOALS}" | awk -F';' '{count=0; for (i=1; i<=NF; i++) if ($i != "") count++; print count}')}"
TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-320}"
DIFF_INTERACTIVE_REVIEW_HOLD_S="${DIFF_INTERACTIVE_REVIEW_HOLD_S:-240}"
DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S="${DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S:-3.0}"

mkdir -p "${RESULT_DIR}"
date --iso-8601=seconds > "${RESULT_DIR}/auto123_gate_start.txt"

cat > "${RESULT_DIR}/auto123_gate_command.env" <<EOF
RUN_ID=${RUN_ID}
RESULT_DIR=${RESULT_DIR}
GOALS=${GOALS}
TOTAL_TIMEOUT_S=${TOTAL_TIMEOUT_S}
DIFF_INTERACTIVE_REVIEW_HOLD_S=${DIFF_INTERACTIVE_REVIEW_HOLD_S}
DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S=${DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S}
DIFF_INTERACTIVE_AUTO_PASS_GOAL_COUNT=${GOAL_COUNT}
DIFF_CMD_INVALID_Z_POLICY=clamp
DIFF_CMD_MIN_Z=0.95
DIFF_CMD_MAX_Z=1.15
EGO_VIRTUAL_CEIL_HEIGHT=1.15
EGO_VISUALIZATION_TRUNCATE_HEIGHT=1.25
EOF

(
  cd "${PROJECT_ROOT}" || exit 97
  RUN_ID="${RUN_ID}" \
  RESULT_DIR="${RESULT_DIR}" \
  PLANNER_VARIANT=diff_planner \
  GUI=false \
  OPEN_RVIZ=false \
  KEEP_ALIVE=false \
  DIFF_INTERACTIVE_CLICK_GOAL=true \
  DIFF_AUTO_GOAL_IN_INTERACTIVE_REVIEW=false \
  DIFF_INTERACTIVE_AUTO_PASS_GOAL_COUNT="${GOAL_COUNT}" \
  DIFF_INTERACTIVE_REVIEW_HOLD_S="${DIFF_INTERACTIVE_REVIEW_HOLD_S}" \
  DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S="${DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S}" \
  DIFF_INTERACTIVE_TARGET_REACHED_XY_M=0.35 \
  DIFF_INTERACTIVE_TARGET_REACHED_Z_M=0.12 \
  DIFF_INTERACTIVE_TARGET_HOLD_S=1.0 \
  DIFF_INTERACTIVE_TARGET_HOLD_MAX_SPEED_MPS=0.45 \
  DIFF_INTERACTIVE_TARGET_HOLD_MAX_VZ_MPS=0.25 \
  DIFF_INTERACTIVE_HANDOFF_MODE=adapter_hold \
  DIFF_ENABLE_CMD_SAFETY_ADAPTER=true \
  DIFF_CMD_INVALID_Z_POLICY=clamp \
  DIFF_CMD_MIN_Z=0.95 \
  DIFF_CMD_MAX_Z=1.15 \
  DIFF_CMD_SAFETY_MAX_POSITION_JUMP_M=0.50 \
  DIFF_CMD_SAFETY_MAX_POSITION_JUMP_SPEED_MPS=3.0 \
  EGO_VIRTUAL_CEIL_HEIGHT=1.15 \
  EGO_VISUALIZATION_TRUNCATE_HEIGHT=1.25 \
  EGO_MAX_VEL=0.4 \
  EGO_MAX_ACC=0.5 \
  TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S}" \
  POINTCLOUD_ROTATION_MODE=full \
  POINTCLOUD_MIN_WORLD_Z_M=0.50 \
  POINTCLOUD_REVIEW_VOXEL_SIZE_M=0.08 \
  bash Scripts/sunray/run_px4ctrl_ego_single_gate.sh
) > "${RESULT_DIR}/runner_outer.log" 2>&1 &
runner_pid=$!
echo "${runner_pid}" > "${RESULT_DIR}/runner_pid.txt"

set +u
source /opt/ros/noetic/setup.bash
source /opt/mosim_work/sunray_ws/Sunray/devel/setup.bash
source "${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash"
source "${PROJECT_ROOT}/Results/sunray_ros1/workspaces/goal4_diff_planner_ws_px4msg/devel/setup.bash"
set -u

cd "${PROJECT_ROOT}" || exit 97
python3 Scripts/sunray/probe_diff_interactive_goal_switch_chain.py \
  --result-dir "${RESULT_DIR}" \
  --output-json DIFF_INTERACTIVE_GOAL_SWITCH_CHAIN_PROBE.json \
  --goals "${GOALS}" \
  --ready-timeout-s 120 \
  --pre-goal-stable-timeout-s 120 \
  --pre-goal-stable-s 1.0 \
  --reach-xy-radius-m 0.35 \
  --reach-z-tol-m 0.12 \
  --reach-max-speed-mps 0.45 \
  --reach-max-vz-mps 0.25 \
  --reach-hold-s 1.0 \
  --min-cmd-z-m 0.95 \
  --max-cmd-z-m 1.15 \
  --cmd-end-z-tol-m 0.12 \
  --goal-timeout-s 55 \
  > "${RESULT_DIR}/probe_stdout.txt" 2> "${RESULT_DIR}/probe_stderr.txt"
probe_exit=$?

echo "PROBE_EXIT=${probe_exit}" > "${RESULT_DIR}/outer_status.txt"
wait "${runner_pid}"
runner_exit=$?
echo "RUNNER_EXIT=${runner_exit}" >> "${RESULT_DIR}/outer_status.txt"
date --iso-8601=seconds > "${RESULT_DIR}/auto123_gate_end.txt"

if [[ "${probe_exit}" -ne 0 ]]; then
  exit "${probe_exit}"
fi
exit "${runner_exit}"
