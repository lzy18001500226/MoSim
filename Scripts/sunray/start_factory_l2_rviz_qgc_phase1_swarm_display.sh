#!/usr/bin/env bash
# Attach the Phase 1 three-UAV Display/RViz terminal to an existing run.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ACTIVE_POINTER="${PROJECT_ROOT}/Results/ui_platform/qgc_active_run.json"
REQUESTED_RUN_ID="${1:-}"
PROFILE_ID="px4ctrl_graphical_c99_factory_rviz_qgc_display_phase1_swarm_v1"
RUNTIME_PROFILE_ID="sunray_ros1_factory_l2_graphical_px4ctrl_c99_rviz_qgc_display_phase1_swarm_v1"
POINTCLOUD_RVIZ_CONFIG="${PROJECT_ROOT}/Config/rviz/sunray_ros1_goal5_diff_swarm_pointcloud_review.rviz"
GRID_RVIZ_CONFIG="${PROJECT_ROOT}/Config/rviz/sunray_ros1_goal5_diff_swarm_grid3d_review.rviz"
ROS_MASTER_URI="${ROS_MASTER_URI:-http://127.0.0.1:11311}"
WAIT_TIMEOUT_S="${PHASE1_SWARM_DISPLAY_WAIT_TIMEOUT_S:-900}"
export ROS_MASTER_URI

if [[ "$#" -gt 1 ]]; then
  echo "Usage: $0 [run-id]" >&2
  exit 2
fi
if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
  echo "BLOCKER RViz GUI display is unavailable: DISPLAY and WAYLAND_DISPLAY are both unset." >&2
  exit 2
fi
for config in "${POINTCLOUD_RVIZ_CONFIG}" "${GRID_RVIZ_CONFIG}"; do
  [[ -f "${config}" ]] || { echo "BLOCKER RViz configuration missing: ${config}" >&2; exit 2; }
done

read_pointer_value() {
  local key="$1"
  python3 - "${ACTIVE_POINTER}" "${key}" <<'PY'
import json
import pathlib
import sys

try:
    value = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    value = {}
result = value.get(sys.argv[2], "") if isinstance(value, dict) else ""
print(result if isinstance(result, str) else "")
PY
}

run_id="${REQUESTED_RUN_ID}"
deadline=$((SECONDS + WAIT_TIMEOUT_S))
while [[ -z "${run_id}" && SECONDS -lt deadline ]]; do
  run_id="$(read_pointer_value run_id)"
  [[ -n "${run_id}" ]] || sleep 1
done
if [[ ! "${run_id}" =~ ^qgc-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$ ]]; then
  echo "No operator run appeared within ${WAIT_TIMEOUT_S} seconds." >&2
  exit 2
fi

RUN_DIR="${PROJECT_ROOT}/Results/runs/${run_id}"
RESULT_DIR="${PROJECT_ROOT}/Results/sunray_ros1/${run_id}"
STATUS_FILE="${RESULT_DIR}/RVIZ_QGC_DISPLAY_PHASE1_SWARM_RUNTIME_STATUS.json"
COORDINATE_EVIDENCE="${RUN_DIR}/OPERATOR_MAP_COORDINATE_EVIDENCE.json"
MANUAL_PACKET_FILE="${RESULT_DIR}/RVIZ_QGC_DISPLAY_PHASE1_SWARM_MANUAL_TEST.json"
ACCEPTANCE_FILE="${RESULT_DIR}/RVIZ_QGC_DISPLAY_PHASE1_SWARM_ACCEPTANCE.json"
RUNTIME_RESULT_DIR="${RESULT_DIR}/runtime"
mkdir -p "${RUNTIME_RESULT_DIR}"

verify_manifest() {
  python3 - "${RUN_DIR}/RUN_MANIFEST.json" "${run_id}" <<'PY'
import json
import pathlib
import sys

payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
if payload.get("run_id") != sys.argv[2]:
    raise SystemExit("phase1_swarm_display_run_id_mismatch")
if payload.get("experiment_profile_id") != "px4ctrl_graphical_c99_factory_rviz_qgc_display_phase1_swarm_v1":
    raise SystemExit("phase1_swarm_display_profile_mismatch")
if payload.get("runtime_profile_id") != "sunray_ros1_factory_l2_graphical_px4ctrl_c99_rviz_qgc_display_phase1_swarm_v1":
    raise SystemExit("phase1_swarm_display_runtime_profile_mismatch")
if payload.get("vehicle_count") != 3:
    raise SystemExit("phase1_swarm_display_vehicle_count_mismatch")
PY
}

verify_manifest
[[ -f "${COORDINATE_EVIDENCE}" ]] || { echo "Coordinate evidence is missing: ${COORDINATE_EVIDENCE}" >&2; exit 3; }

ready=false
deadline=$((SECONDS + WAIT_TIMEOUT_S))
while (( SECONDS < deadline )); do
  status_reason="$(python3 - "${STATUS_FILE}" <<'PY'
import json
import pathlib
import sys

try:
    value = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    value = {}
print(value.get("reason_code", "") if isinstance(value, dict) else "")
PY
)"
  if [[ "${status_reason}" == "rviz_qgc_display_phase1_swarm_runtime_ready_for_display" ]]; then
    ready=true
    break
  fi
  state="$(read_pointer_value state)"
  if [[ "${state}" == "completed" || "${state}" == "blocked" || "${state}" == "failed" ]]; then
    echo "Phase 1 swarm runtime ended before Display/RViz became ready: ${state}" >&2
    exit 3
  fi
  sleep 1
done
[[ "${ready}" == true ]] || { echo "Phase 1 swarm Display/RViz readiness timed out." >&2; exit 3; }

source /opt/ros/noetic/setup.bash
GOAL4_DIFF_PLANNER_WS="${GOAL4_DIFF_PLANNER_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/goal4_diff_planner_ws_px4msg}"
if [[ -f "${GOAL4_DIFF_PLANNER_WS}/devel/setup.bash" ]]; then
  source "${GOAL4_DIFF_PLANNER_WS}/devel/setup.bash"
fi

RVIZ_POINTCLOUD_PID=""
RVIZ_GRID_PID=""
SIDECAR_PID=""
cleanup() {
  local exit_code=$?
  set +e
  for pid in "${SIDECAR_PID}" "${RVIZ_POINTCLOUD_PID}" "${RVIZ_GRID_PID}"; do
    if [[ "${pid}" =~ ^[0-9]+$ ]] && kill -0 "${pid}" 2>/dev/null; then
      kill -INT "${pid}" 2>/dev/null || true
      sleep 0.2
      kill -TERM "${pid}" 2>/dev/null || true
    fi
  done
  trap - EXIT INT TERM
  exit "${exit_code}"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

python3 "${PROJECT_ROOT}/Scripts/sunray/rviz_qgc_display_phase1_swarm.py" manual-packet \
  --run-id "${run_id}" \
  --profile-id "${PROFILE_ID}" \
  --runtime-profile-id "${RUNTIME_PROFILE_ID}" \
  --pointcloud-rviz-config "${POINTCLOUD_RVIZ_CONFIG}" \
  --grid-rviz-config "${GRID_RVIZ_CONFIG}" \
  --result-directory "${RESULT_DIR}" \
  --operator-run-directory "${RUN_DIR}" \
  --output "${MANUAL_PACKET_FILE}"

rviz -d "${POINTCLOUD_RVIZ_CONFIG}" > "${RUNTIME_RESULT_DIR}/rviz_phase1_swarm_pointcloud.log" 2>&1 &
RVIZ_POINTCLOUD_PID=$!
rviz -d "${GRID_RVIZ_CONFIG}" > "${RUNTIME_RESULT_DIR}/rviz_phase1_swarm_grid3d.log" 2>&1 &
RVIZ_GRID_PID=$!
(
  exec python3 "${PROJECT_ROOT}/Scripts/ui/runtime_sidecar.py" \
    --run-dir "${RUN_DIR}" \
    --manifest "${RUN_DIR}/RUN_MANIFEST.json" \
    --contract "${PROJECT_ROOT}/Config/control_platform/factory_injection_contract.json" \
    --vehicle-count 3 \
    --rate-hz 20 \
    --max-track-points 1200 \
    --odom-topic-template /uav{uid}/mosim/diff_swarm/planner_odom_world \
    --expected-path-topic /mosim/goal5/target_path \
    --future-polytraj-topic-template /drone_{drone_id}_planning/trajectory \
    --future-polytraj-frame-id world \
    --future-polytraj-sample-period-s 0.01 \
    --future-polytraj-max-points 2400 \
    --actual-track-min-distance-m 0.02 \
    --coordinate-evidence "${COORDINATE_EVIDENCE}" \
    --skip-controller-command-readiness \
    --skip-actuator-telemetry-readiness \
    --read-only
) > "${RESULT_DIR}/qgc_swarm_runtime_sidecar.log" 2>&1 &
SIDECAR_PID=$!

echo "Phase 1 swarm Display/RViz terminal is ready. Use RViz 2D Nav Goal for one or more waypoints, then observe all tracks in QGC."
while true; do
  if ! kill -0 "${SIDECAR_PID}" 2>/dev/null; then
    echo "The QGC runtime sidecar exited; inspect ${RESULT_DIR}/qgc_swarm_runtime_sidecar.log" >&2
    exit 5
  fi
  state="$(read_pointer_value state)"
  if [[ "${state}" == "completed" || "${state}" == "blocked" || "${state}" == "failed" ]]; then
    break
  fi
  sleep 2
done

if [[ -f "${RESULT_DIR}/EGO_SWARM_METRICS.json" && -f "${RESULT_DIR}/DIFF_SWARM_RVIZ_GOAL_ROUTER.json" && -f "${RUN_DIR}/telemetry.json" ]]; then
  python3 "${PROJECT_ROOT}/Scripts/sunray/rviz_qgc_display_phase1_swarm.py" evaluate \
    --run-id "${run_id}" \
    --metrics "${RESULT_DIR}/EGO_SWARM_METRICS.json" \
    --router "${RESULT_DIR}/DIFF_SWARM_RVIZ_GOAL_ROUTER.json" \
    --telemetry "${RUN_DIR}/telemetry.json" \
    --output "${ACCEPTANCE_FILE}" \
    --schema mosim.rviz_qgc_display_phase1_swarm_acceptance.v1 || true
fi
echo "Phase 1 swarm Display/RViz evidence was written for run ${run_id}."
