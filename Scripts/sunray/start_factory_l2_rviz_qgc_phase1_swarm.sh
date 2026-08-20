#!/usr/bin/env bash
# Start the published Factory L2 Phase 1 three-UAV RViz-to-QGC display run.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REQUESTED_RUN_ID="${1:-}"
PROFILE_ID="px4ctrl_graphical_c99_factory_rviz_qgc_display_phase1_swarm_v1"
RUNTIME_PROFILE_ID="sunray_ros1_factory_l2_graphical_px4ctrl_c99_rviz_qgc_display_phase1_swarm_v1"
READY_TOPIC="/mosim/diff_swarm/interactive_goal_ready"
ROS_MASTER_URI="${ROS_MASTER_URI:-http://127.0.0.1:11311}"
export ROS_MASTER_URI

if [[ "$#" -gt 1 ]]; then
  echo "Usage: $0 [run-id]" >&2
  exit 2
fi
if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
  echo "BLOCKER RViz GUI display is unavailable: DISPLAY and WAYLAND_DISPLAY are both unset." >&2
  exit 2
fi
for rviz_config in \
  "${PROJECT_ROOT}/Config/rviz/sunray_ros1_goal5_diff_swarm_pointcloud_review.rviz" \
  "${PROJECT_ROOT}/Config/rviz/sunray_ros1_goal5_diff_swarm_grid3d_review.rviz"; do
  if [[ ! -f "${rviz_config}" ]]; then
    echo "BLOCKER RViz configuration missing: ${rviz_config}" >&2
    exit 2
  fi
done

export PROJECT_ROOT
export UAV_NUM=3
export PLANNER_VARIANT=diff_planner
export DIFF_SWARM_INTERACTIVE_GOAL_REVIEW=true
export DIFF_GOAL5_COMMON_WORLD_FRAME=true
export DIFF_GOAL5_FASTLIO_INPUT_ENABLED="${DIFF_GOAL5_FASTLIO_INPUT_ENABLED:-true}"
export FASTLIO_WS="${FASTLIO_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/fastlio_ws}"
export DIFF_SWARM_GOAL_INPUT_TOPIC="${DIFF_SWARM_GOAL_INPUT_TOPIC:-/move_base_simple/goal}"
export DIFF_SWARM_GOAL_READY_TOPIC="${DIFF_SWARM_GOAL_READY_TOPIC:-${READY_TOPIC}}"
export DIFF_SWARM_GOAL_INPUT_FRAME="${DIFF_SWARM_GOAL_INPUT_FRAME:-world}"
export DIFF_SWARM_GOAL_OUTPUT_FRAME="${DIFF_SWARM_GOAL_OUTPUT_FRAME:-local}"
export DIFF_SWARM_INTERACTIVE_GOAL_TIMEOUT_S="${DIFF_SWARM_INTERACTIVE_GOAL_TIMEOUT_S:-900}"
export DIFF_SWARM_INTERACTIVE_GOAL_IDLE_TIMEOUT_S="${DIFF_SWARM_INTERACTIVE_GOAL_IDLE_TIMEOUT_S:-10}"
export TOTAL_TIMEOUT_S="${PHASE1_SWARM_TOTAL_TIMEOUT_S:-1800}"
export QGC_TERMINAL_ROLE=backend
export GUI=false
export DISABLE_ROS1_EOL_WARNINGS="${DISABLE_ROS1_EOL_WARNINGS:-1}"
export SUNRAY_MID360_RAY_BACKEND="${SUNRAY_MID360_RAY_BACKEND:-ode}"
if [[ "${SUNRAY_MID360_RAY_BACKEND}" == "gpu" ]]; then
  export GPU_LIVOX_PLUGIN_WS="${GPU_LIVOX_PLUGIN_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/gpu_livox_pointcloud_ws}"
  export SUNRAY_LIVOX_PLUGIN_FILENAME="${SUNRAY_LIVOX_PLUGIN_FILENAME:-${GPU_LIVOX_PLUGIN_WS}/devel/lib/libmosim_gpu_livox_pointcloud.so}"
else
  export LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS:-${PROJECT_ROOT}/build/ros1/local_source_ws}"
fi

if ! PROJECT_ROOT="${PROJECT_ROOT}" \
  LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS:-}" \
  GPU_LIVOX_PLUGIN_WS="${GPU_LIVOX_PLUGIN_WS:-}" \
  SUNRAY_LIVOX_PLUGIN_FILENAME="${SUNRAY_LIVOX_PLUGIN_FILENAME:-}" \
  SUNRAY_MID360_RAY_BACKEND="${SUNRAY_MID360_RAY_BACKEND}" \
  bash "${PROJECT_ROOT}/Scripts/sunray/check_sunray_ros1_runtime_preflight.sh"; then
  echo "BLOCKER MID360 sensor preflight failed; Phase 1 swarm was not created." >&2
  exit 2
fi

prepare_args=(
  --profile-id "${PROFILE_ID}"
  --runtime-profile-id "${RUNTIME_PROFILE_ID}"
  --prepared-by "terminal_rviz_qgc_display_phase1"
  --print-run-id
)
if [[ -n "${REQUESTED_RUN_ID}" ]]; then
  prepare_args+=(--run-id "${REQUESTED_RUN_ID}")
fi
RUN_ID="$(python3 "${PROJECT_ROOT}/Scripts/ui/prepare_operator_run.py" "${prepare_args[@]}")"
export RUN_ID
export MOSIM_OPERATOR_RUN_ID="${RUN_ID}"
export MOSIM_OPERATOR_RUN_DIR="${PROJECT_ROOT}/Results/runs/${RUN_ID}"
export MOSIM_OPERATOR_RUN_MANIFEST="${MOSIM_OPERATOR_RUN_DIR}/RUN_MANIFEST.json"
RESULT_DIR="${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}"
STATUS_FILE="${RESULT_DIR}/RVIZ_QGC_DISPLAY_PHASE1_SWARM_RUNTIME_STATUS.json"
mkdir -p "${RESULT_DIR}"

write_runtime_status() {
  local state="$1"
  local reason_code="$2"
  local exit_code="${3:-0}"
  python3 - "${STATUS_FILE}" "${RUN_ID}" "${state}" "${reason_code}" "${exit_code}" <<'PY'
import json
import pathlib
import sys
import time

output, run_id, state, reason_code, exit_code = sys.argv[1:]
payload = {
    "schema": "mosim.rviz_qgc_display_phase1_swarm_runtime_status.v1",
    "run_id": run_id,
    "state": state,
    "reason_code": reason_code,
    "exit_code": int(exit_code),
    "vehicle_count": 3,
    "transport": {
        "rviz_goal_topic": "/move_base_simple/goal",
        "planner_goal_topic_template": "/uav{uid}/goal_with_id",
        "interactive_ready_topic": "/mosim/diff_swarm/interactive_goal_ready",
        "operator_telemetry_path": f"Results/runs/{run_id}/telemetry.json",
        "planner_cloud_topic_template": "/uav{uid}/livox_world",
        "fastlio_aligned_cloud_topic_template": "/uav{uid}/mosim/diff_swarm/fastlio/aligned_cloud",
        "fastlio_aligned_odom_topic_template": "/uav{uid}/mosim/diff_swarm/fastlio/aligned_odom",
        "fastlio_xy_role": "planner_input_when_enabled_after_alignment_gate",
    },
    "claim_boundary": (
        "This status records the Phase 1 multi-UAV RViz input and QGC display readiness surfaces. "
        "It does not prove human QGC observation, global collision-aware planning, flight, "
        "controller acceptance, or FAST-LIO XY as a planner or PX4/EKF input."
    ),
    "updated_at_unix_s": time.time(),
}
path = pathlib.Path(output)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
PY
}

# The generic swarm gate is also used by legacy callers, so bind this
# published Phase 1 entrypoint to a fresh project-local runtime overlay before
# handing control to it. This keeps model sync, PX4 resolution, and Gazebo
# assets on the same source-local runtime contract.
export LOCAL_ROS1_WS="${PROJECT_ROOT}/build/ros1/local_source_ws"
export SUNRAY_PX4_DIR="${PROJECT_ROOT}/src/flight_stack/px4/PX4-Autopilot"
export PX4_BUILD_DIR="${PROJECT_ROOT}/build/px4/px4_sitl_default"
export LIVOX_PLUGIN_WS="${LOCAL_ROS1_WS}"
RUNTIME_OVERLAY_WORKSPACE="${PROJECT_ROOT}/build/ros1/runtime_overlays/${RUN_ID}"
if ! bash "${PROJECT_ROOT}/Scripts/sunray/prepare_local_ros1_runtime_overlay.sh" \
  --workspace "${RUNTIME_OVERLAY_WORKSPACE}" \
  > "${RESULT_DIR}/local_runtime_overlay.log" 2>&1; then
  write_runtime_status blocked rviz_qgc_display_phase1_swarm_runtime_overlay_prepare_failed 3
  exit 3
fi
LOCAL_ROS1_DEVEL="${LOCAL_ROS1_WS}/devel"
if [[ ! -f "${LOCAL_ROS1_DEVEL}/setup.bash" ]]; then
  write_runtime_status blocked rviz_qgc_display_phase1_swarm_local_ros1_setup_missing 3
  exit 3
fi
if [[ -L "${RUNTIME_OVERLAY_WORKSPACE}/devel" ]]; then
  if [[ "$(readlink -f "${RUNTIME_OVERLAY_WORKSPACE}/devel")" != "$(readlink -f "${LOCAL_ROS1_DEVEL}")" ]]; then
    write_runtime_status blocked rviz_qgc_display_phase1_swarm_runtime_overlay_devel_link_mismatch 3
    exit 3
  fi
elif [[ ! -e "${RUNTIME_OVERLAY_WORKSPACE}/devel" ]]; then
  ln -s "${LOCAL_ROS1_DEVEL}" "${RUNTIME_OVERLAY_WORKSPACE}/devel"
else
  write_runtime_status blocked rviz_qgc_display_phase1_swarm_runtime_overlay_devel_path_invalid 3
  exit 3
fi
export MOSIM_RUNTIME_OVERLAY_ID="${RUN_ID}"
source "${PROJECT_ROOT}/Scripts/sunray/resolve_local_ros1_runtime.sh"

write_runtime_status launch_prepared rviz_qgc_display_phase1_swarm_runtime_starting

GATE_PID=""
cleanup() {
  local exit_code=$?
  set +e
  if [[ "${GATE_PID}" =~ ^[0-9]+$ ]] && kill -0 "${GATE_PID}" 2>/dev/null; then
    kill -INT "${GATE_PID}" 2>/dev/null || true
    wait "${GATE_PID}" 2>/dev/null || true
  fi
  trap - EXIT INT TERM
  exit "${exit_code}"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

(
  export RUN_ID RESULT_DIR PROJECT_ROOT MOSIM_OPERATOR_RUN_ID MOSIM_OPERATOR_RUN_DIR MOSIM_OPERATOR_RUN_MANIFEST
  export UAV_NUM PLANNER_VARIANT DIFF_SWARM_INTERACTIVE_GOAL_REVIEW DIFF_GOAL5_COMMON_WORLD_FRAME
  export DIFF_SWARM_GOAL_INPUT_TOPIC DIFF_SWARM_GOAL_READY_TOPIC DIFF_SWARM_GOAL_INPUT_FRAME DIFF_SWARM_GOAL_OUTPUT_FRAME
  bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh"
) > "${RESULT_DIR}/swarm_runtime_gate.log" 2>&1 &
GATE_PID=$!

set +u
source /opt/ros/noetic/setup.bash
set -u
ready=false
deadline=$((SECONDS + ${PHASE1_SWARM_READY_TIMEOUT_S:-900}))
while (( SECONDS < deadline )); do
  if ! kill -0 "${GATE_PID}" 2>/dev/null; then
    break
  fi
  if timeout 5s rostopic echo -n 1 "${READY_TOPIC}" 2>/dev/null | grep -q "data: true"; then
    ready=true
    break
  fi
  sleep 1
done

if [[ "${ready}" == true ]]; then
  python3 "${PROJECT_ROOT}/Scripts/ui/prepare_operator_run.py" \
    --activate-active \
    --expected-run-id "${RUN_ID}" \
    --activation-source terminal_rviz_qgc_display_phase1_swarm
  write_runtime_status running rviz_qgc_display_phase1_swarm_runtime_ready_for_display
  echo "Phase 1 swarm runtime is ready. Start the separate swarm Display/RViz terminal now; click one or more RViz 2D Nav Goals."
else
  write_runtime_status blocked rviz_qgc_display_phase1_swarm_runtime_ready_timeout 124
  echo "Phase 1 swarm runtime did not publish ${READY_TOPIC}; inspect ${RESULT_DIR}/swarm_runtime_gate.log" >&2
  set +e
  wait "${GATE_PID}"
  set -e
  python3 "${PROJECT_ROOT}/Scripts/ui/prepare_operator_run.py" \
    --finalize-active \
    --expected-run-id "${RUN_ID}" \
    --terminal-state blocked \
    --reason-code rviz_qgc_display_phase1_swarm_runtime_ready_timeout \
    --terminal-source terminal_rviz_qgc_display_phase1_swarm
  exit 3
fi

set +e
wait "${GATE_PID}"
GATE_EXIT_CODE=$?
set -e
if [[ "${GATE_EXIT_CODE}" -eq 0 ]]; then
  write_runtime_status completed rviz_qgc_display_phase1_swarm_runtime_completed "${GATE_EXIT_CODE}"
  TERMINAL_STATE=completed
  TERMINAL_REASON=rviz_qgc_display_phase1_swarm_runtime_completed
else
  write_runtime_status blocked rviz_qgc_display_phase1_swarm_runtime_blocked "${GATE_EXIT_CODE}"
  TERMINAL_STATE=blocked
  TERMINAL_REASON=rviz_qgc_display_phase1_swarm_runtime_blocked
fi
python3 "${PROJECT_ROOT}/Scripts/ui/prepare_operator_run.py" \
  --finalize-active \
  --expected-run-id "${RUN_ID}" \
  --terminal-state "${TERMINAL_STATE}" \
  --reason-code "${TERMINAL_REASON}" \
  --terminal-source terminal_rviz_qgc_display_phase1_swarm
exit "${GATE_EXIT_CODE}"
