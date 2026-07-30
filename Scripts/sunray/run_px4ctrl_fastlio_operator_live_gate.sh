#!/usr/bin/env bash
# Run a source-local no-fault lifecycle with read-only QGC, RViz and UE displays.

set -euo pipefail

if [[ "$#" -gt 1 ]] || { [[ "$#" -eq 1 ]] && [[ "$1" != "takeoff_hover_land" ]]; }; then
  echo "Usage: $0 [takeoff_hover_land]" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
OPERATOR_RUN_ID="${MOSIM_OPERATOR_RUN_ID:-}"
OPERATOR_RUN_DIR="${MOSIM_OPERATOR_RUN_DIR:-}"
OPERATOR_RUN_MANIFEST="${MOSIM_OPERATOR_RUN_MANIFEST:-}"
OPERATOR_RUN_ENABLED=false
RUN_ID="${RUN_ID:-}"

if [[ -n "${OPERATOR_RUN_ID}" || -n "${OPERATOR_RUN_DIR}" || -n "${OPERATOR_RUN_MANIFEST}" ]]; then
  if [[ -z "${OPERATOR_RUN_ID}" || -z "${OPERATOR_RUN_DIR}" || -z "${OPERATOR_RUN_MANIFEST}" ]]; then
    echo "MOSIM_OPERATOR_RUN_ID, MOSIM_OPERATOR_RUN_DIR, and MOSIM_OPERATOR_RUN_MANIFEST must be set together" >&2
    exit 2
  fi
  if [[ -n "${RUN_ID}" && "${RUN_ID}" != "${OPERATOR_RUN_ID}" ]]; then
    echo "RUN_ID must match MOSIM_OPERATOR_RUN_ID when the QGC display bridge is enabled" >&2
    exit 2
  fi
  OPERATOR_RUN_ENABLED=true
  RUN_ID="${OPERATOR_RUN_ID}"
fi
RUN_ID="${RUN_ID:-sunray_ros1_fastlio_operator_live_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
RUNTIME_LOCK_DIR="${PROJECT_ROOT}/Results/sunray_ros1/.sunray_ros1_runtime.lock"
RECORD_ROSBAG="${RECORD_ROSBAG:-true}"
GUI="${GUI:-false}"
REVIEW_OPEN_RVIZ="${REVIEW_OPEN_RVIZ:-true}"
REVIEW_START_CLOUD_NODE="${REVIEW_START_CLOUD_NODE:-true}"
REVIEW_PRESTART_HOLD_S="${REVIEW_PRESTART_HOLD_S:-15}"
MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-180}"
MOSIM_UE_STATE_STREAM="${MOSIM_UE_STATE_STREAM:-true}"
MOSIM_UE_STATE_STREAM_RATE_HZ="${MOSIM_UE_STATE_STREAM_RATE_HZ:-100}"

# This wrapper is the Factory L2 live route, so it must never silently fall
# back to the generic small-voxel settings used by other worlds.  The values
# below are the existing Factory baseline, not a new FAST-LIO tuning.
FACTORY_L2_WORLD_RELATIVE="Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf"
FACTORY_L2_MODELS_RELATIVE="Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/models"
FACTORY_L2_LAUNCH_RELATIVE="Scripts/sunray/factory_l2_sunray_px4_gazebo.launch"
WORLD_FILE="${WORLD_FILE:-${PROJECT_ROOT}/${FACTORY_L2_WORLD_RELATIVE}}"
GAZEBO_MODEL_PATH="${GAZEBO_MODEL_PATH:-${PROJECT_ROOT}/${FACTORY_L2_MODELS_RELATIVE}}"
SUNRAY_GAZEBO_LAUNCH_FILE="${SUNRAY_GAZEBO_LAUNCH_FILE:-${PROJECT_ROOT}/${FACTORY_L2_LAUNCH_RELATIVE}}"
SUNRAY_UAV_INIT_X="${SUNRAY_UAV_INIT_X:--10.575025}"
SUNRAY_UAV_INIT_Y="${SUNRAY_UAV_INIT_Y:--19.36313}"
SUNRAY_UAV_INIT_Z="${SUNRAY_UAV_INIT_Z:-0.2}"
SUNRAY_UAV_INIT_YAW="${SUNRAY_UAV_INIT_YAW:-0}"
FASTLIO_FILTER_SIZE_SURF="${FASTLIO_FILTER_SIZE_SURF:-0.5}"
FASTLIO_FILTER_SIZE_MAP="${FASTLIO_FILTER_SIZE_MAP:-0.5}"
REVIEW_START_OCCUPANCY_NODE="${REVIEW_START_OCCUPANCY_NODE:-true}"

mkdir -p "${RESULT_DIR}"

BASIC_PID=""
QGC_SIDECAR_PID=""
UE_STREAM_PID=""
ROSBAG_PID=""
ROSBAG_BASE="${RESULT_DIR}/rosbag/${RUN_ID}"
ROSBAG_FILE="${ROSBAG_BASE}.bag"

stop_process() {
  local variable_name="$1"
  local pid="${!variable_name:-}"
  if [[ -z "${pid}" ]] || ! kill -0 "${pid}" 2>/dev/null; then
    printf -v "${variable_name}" '%s' ""
    return
  fi
  kill -INT "${pid}" 2>/dev/null || true
  for _ in $(seq 1 20); do
    if ! kill -0 "${pid}" 2>/dev/null; then
      break
    fi
    sleep 0.25
  done
  if kill -0 "${pid}" 2>/dev/null; then
    kill -TERM "${pid}" 2>/dev/null || true
  fi
  wait "${pid}" 2>/dev/null || true
  printf -v "${variable_name}" '%s' ""
}

finalize_operator_run() {
  local terminal_state="$1"
  local reason_code="$2"
  if [[ "${OPERATOR_RUN_ENABLED}" != "true" ]]; then
    return
  fi
  python3 "${PROJECT_ROOT}/Scripts/ui/prepare_operator_run.py" \
    --finalize-active \
    --expected-run-id "${OPERATOR_RUN_ID}" \
    --terminal-state "${terminal_state}" \
    --reason-code "${reason_code}" \
    --terminal-source "terminal_fastlio_operator_live_gate" \
    > "${RESULT_DIR}/qgc_operator_run_finalize.log" 2>&1
}

write_demo_status() {
  local basic_exit_code="$1"
  python3 - \
    "${RESULT_DIR}" \
    "${RUN_ID}" \
    "${basic_exit_code}" \
    "${RECORD_ROSBAG}" \
    "${ROSBAG_FILE}" \
    "${OPERATOR_RUN_ENABLED}" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
run_id = sys.argv[2]
basic_exit_code = int(sys.argv[3])
record_requested = sys.argv[4].lower() == "true"
rosbag_path = pathlib.Path(sys.argv[5])
operator_display_requested = sys.argv[6].lower() == "true"
metrics_path = root / "PX4CTRL_BASIC_MISSION_METRICS.json"
try:
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    metrics = {}

lifecycle = metrics.get("operational_lifecycle_gate") or {}
rosbag_ready = (not record_requested) or (rosbag_path.is_file() and rosbag_path.stat().st_size > 0)
passed = basic_exit_code == 0 and lifecycle.get("status") == "passed" and rosbag_ready
payload = {
    "schema": "mosim.sunray_ros1.fastlio_operator_live_status.v1",
    "run_id": run_id,
    "status": "passed" if passed else "blocked",
    "reason": None if passed else (
        lifecycle.get("reason")
        or ("rosbag_not_recorded" if not rosbag_ready else f"basic_gate_exit:{basic_exit_code}")
    ),
    "functional_lifecycle": lifecycle,
    "quality_observation": {
        "formal_performance_gate": metrics.get("formal_performance_gate"),
        "policy": "Formal tracking performance remains an observation and is not replaced by this operational lifecycle gate.",
    },
    "recording": {
        "requested": record_requested,
        "status": "passed" if rosbag_ready else "blocked",
        "rosbag": str(rosbag_path) if record_requested else "",
        "rosbag_bytes": rosbag_path.stat().st_size if rosbag_path.is_file() else 0,
        "topics": [
            "/uav1/mavros/state",
            "/uav1/mavros/local_position/odom",
            "/uav1/sunray/gazebo_pose",
            "/position_cmd",
            "/mosim/px4ctrl/reference_path",
            "/mosim/px4ctrl/truth_path",
        ],
    },
    "display": {
        "qgc_read_only_requested": operator_display_requested,
        "ue_state_stream_metrics": str(root / "ue_sender_metrics.json"),
        "rviz_requested": True,
        "claim_boundary": "QGC, UE and RViz are display surfaces only. Gazebo, PX4, MAVROS and the recorded ROS topics remain runtime evidence.",
    },
    "claim_boundary": "This gate proves only a no-fault source-local lifecycle and display/recording path. It is not a controller-performance, fault-tolerance, planner or UE-control claim.",
}
(root / "DEMO_STATUS.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
}

cleanup() {
  local exit_code=$?
  set +e
  stop_process UE_STREAM_PID
  stop_process ROSBAG_PID
  stop_process QGC_SIDECAR_PID
  if [[ -n "${BASIC_PID}" ]] && kill -0 "${BASIC_PID}" 2>/dev/null; then
    kill -TERM "${BASIC_PID}" 2>/dev/null || true
    wait "${BASIC_PID}" 2>/dev/null || true
  fi
  return "${exit_code}"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

{
  echo "schema=mosim.sunray_ros1.fastlio_operator_live_command.v1"
  echo "operation_selector=factory_l2_takeoff_hover_land"
  echo "run_id=${RUN_ID}"
  echo "result_dir=${RESULT_DIR}"
  echo "controller_authority=px4ctrl_only"
  echo "state_chain=fastlio_to_px4_ekf_to_mavros_local_odom"
  echo "fault_mode=none"
  echo "record_rosbag=${RECORD_ROSBAG}"
  echo "qgc_display_bridge=${OPERATOR_RUN_ENABLED}"
  echo "ue_state_stream=${MOSIM_UE_STATE_STREAM}"
} > "${RESULT_DIR}/DEMO_COMMAND.txt"

set +u
source /opt/ros/noetic/setup.bash
source "${PROJECT_ROOT}/Scripts/sunray/resolve_local_ros1_runtime.sh"
source "${LOCAL_ROS1_WS}/devel/setup.bash"
set -u

env \
  RUN_ID="${RUN_ID}" \
  RESULT_DIR="${RESULT_DIR}" \
  GUI="${GUI}" \
  REVIEW_OPEN_RVIZ="${REVIEW_OPEN_RVIZ}" \
  REVIEW_START_CLOUD_NODE="${REVIEW_START_CLOUD_NODE}" \
  REVIEW_PRESTART_HOLD_S="${REVIEW_PRESTART_HOLD_S}" \
  MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S}" \
  WORLD_FILE="${WORLD_FILE}" \
  GAZEBO_MODEL_PATH="${GAZEBO_MODEL_PATH}" \
  SUNRAY_GAZEBO_LAUNCH_FILE="${SUNRAY_GAZEBO_LAUNCH_FILE}" \
  SUNRAY_UAV_INIT_X="${SUNRAY_UAV_INIT_X}" \
  SUNRAY_UAV_INIT_Y="${SUNRAY_UAV_INIT_Y}" \
  SUNRAY_UAV_INIT_Z="${SUNRAY_UAV_INIT_Z}" \
  SUNRAY_UAV_INIT_YAW="${SUNRAY_UAV_INIT_YAW}" \
  FASTLIO_FILTER_SIZE_SURF="${FASTLIO_FILTER_SIZE_SURF}" \
  FASTLIO_FILTER_SIZE_MAP="${FASTLIO_FILTER_SIZE_MAP}" \
  REVIEW_START_OCCUPANCY_NODE="${REVIEW_START_OCCUPANCY_NODE}" \
  PX4CTRL_ACCEPTANCE_MODE="operational_lifecycle" \
  bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_fastlio_hover_gate.sh" takeoff_hover_land \
  > "${RESULT_DIR}/basic_gate_runner.log" 2>&1 &
BASIC_PID=$!

MASTER_READY=false
for _ in $(seq 1 360); do
  if ! kill -0 "${BASIC_PID}" 2>/dev/null; then
    break
  fi
  if [[ -f "${RUNTIME_LOCK_DIR}/run_id" && "$(<"${RUNTIME_LOCK_DIR}/run_id")" == "${RUN_ID}" ]] \
      && rosparam get /rosversion >/dev/null 2>&1; then
    MASTER_READY=true
    break
  fi
  sleep 0.5
done

if [[ "${MASTER_READY}" != "true" ]]; then
  set +e
  wait "${BASIC_PID}"
  BASIC_EXIT_CODE=$?
  set -e
  BASIC_PID=""
  write_demo_status "${BASIC_EXIT_CODE}"
  finalize_operator_run "blocked" "factory_l2_takeoff_hover_land_runtime_not_ready"
  exit 4
fi

if [[ "${OPERATOR_RUN_ENABLED}" == "true" ]]; then
  python3 "${PROJECT_ROOT}/Scripts/ui/prepare_factory_live_operator_map.py" \
    --run-dir "${OPERATOR_RUN_DIR}" \
    --manifest "${OPERATOR_RUN_MANIFEST}" \
    --world-file "${WORLD_FILE}" \
    --gazebo-launch-file "${SUNRAY_GAZEBO_LAUNCH_FILE}" \
    > "${RESULT_DIR}/qgc_factory_map_prepare.log" 2>&1
  python3 "${PROJECT_ROOT}/Scripts/ui/runtime_sidecar.py" \
    --run-dir "${OPERATOR_RUN_DIR}" \
    --manifest "${OPERATOR_RUN_MANIFEST}" \
    --contract "${PROJECT_ROOT}/Config/control_platform/factory_injection_contract.json" \
    --vehicle-count 1 \
    --odom-topic /uav1/sunray/gazebo_pose \
    --expected-path-topic /mosim/px4ctrl/reference_path \
    --coordinate-evidence "${OPERATOR_RUN_DIR}/OPERATOR_MAP_COORDINATE_EVIDENCE.json" \
    --read-only \
    > "${RESULT_DIR}/qgc_runtime_sidecar.log" 2>&1 &
  QGC_SIDECAR_PID=$!
  sleep 0.5
  if ! kill -0 "${QGC_SIDECAR_PID}" 2>/dev/null; then
    wait "${QGC_SIDECAR_PID}" 2>/dev/null || true
    QGC_SIDECAR_PID=""
    echo "QGC read-only telemetry sidecar exited during startup" >&2
    exit 7
  fi
fi

if [[ "${MOSIM_UE_STATE_STREAM}" == "true" ]]; then
  UE_HOST="${MOSIM_UE_HOST:-}"
  if [[ -z "${UE_HOST}" ]]; then
    UE_HOST="$(ip route show default 2>/dev/null | awk '/default/ {print $3; exit}')"
  fi
  UE_HOST="${UE_HOST:-127.0.0.1}"
  python3 -u "${PROJECT_ROOT}/Scripts/UE5/stream_ros1_state_to_ue_udp.py" \
    --odom-topic /uav1/sunray/gazebo_pose \
    --position-cmd-topic /position_cmd \
    --link-states-topic /gazebo/link_states \
    --mavros-state-topic /uav1/mavros/state \
    --host "${UE_HOST}" \
    --port 5005 \
    --rate-hz "${MOSIM_UE_STATE_STREAM_RATE_HZ}" \
    --stream-id "${RUN_ID}-ue" \
    --run-id "${RUN_ID}" \
    --metrics-output "${RESULT_DIR}/ue_sender_metrics.json" \
    --vehicle-id uav1 \
    --scene-id factoryenvironmentcollect \
    --map-id factory_l2 \
    --controller-profile px4ctrl \
    --planner-profile none \
    > "${RESULT_DIR}/ue_state_stream.log" 2>&1 &
  UE_STREAM_PID=$!
  sleep 0.5
  if ! kill -0 "${UE_STREAM_PID}" 2>/dev/null; then
    wait "${UE_STREAM_PID}" 2>/dev/null || true
    UE_STREAM_PID=""
    echo "UE state stream exited during startup" >&2
    exit 8
  fi
fi

if [[ "${RECORD_ROSBAG}" == "true" ]]; then
  mkdir -p "${RESULT_DIR}/rosbag"
  rosbag record --lz4 -O "${ROSBAG_BASE}" \
    /uav1/mavros/state \
    /uav1/mavros/local_position/odom \
    /uav1/sunray/gazebo_pose \
    /position_cmd \
    /mosim/px4ctrl/reference_path \
    /mosim/px4ctrl/truth_path \
    > "${RESULT_DIR}/rosbag_record.log" 2>&1 &
  ROSBAG_PID=$!
fi

set +e
wait "${BASIC_PID}"
BASIC_EXIT_CODE=$?
set -e
BASIC_PID=""
stop_process UE_STREAM_PID
stop_process ROSBAG_PID
write_demo_status "${BASIC_EXIT_CODE}"

TERMINAL_STATE="$(python3 - "${RESULT_DIR}/DEMO_STATUS.json" <<'PY'
import json
import pathlib
import sys

status = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")).get("status")
print("completed" if status == "passed" else "blocked")
PY
)"
if [[ "${TERMINAL_STATE}" == "completed" ]]; then
  finalize_operator_run "completed" "factory_l2_takeoff_hover_land_completed"
else
  finalize_operator_run "blocked" "factory_l2_takeoff_hover_land_blocked"
fi
stop_process QGC_SIDECAR_PID

if [[ "${TERMINAL_STATE}" != "completed" ]]; then
  exit 1
fi
