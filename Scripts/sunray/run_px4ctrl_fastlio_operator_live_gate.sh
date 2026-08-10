#!/usr/bin/env bash
# Run a source-local no-fault lifecycle with read-only QGC, RViz and UE displays.

set -euo pipefail

MISSION="${1:-${MISSION:-takeoff_hover_land}}"
if [[ "$#" -gt 1 ]] || { [[ "$#" -eq 1 ]] && [[ "$1" != "takeoff_hover_land" && "$1" != "figure8" ]]; }; then
  echo "Usage: $0 [takeoff_hover_land|figure8]" >&2
  exit 2
fi
if [[ "${MISSION}" != "takeoff_hover_land" && "${MISSION}" != "figure8" ]]; then
  echo "Unsupported operator mission: ${MISSION}" >&2
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
RUNTIME_RESULT_DIR="${RESULT_DIR}"
if [[ "${OPERATOR_RUN_ENABLED}" == "true" ]]; then
  # The prepared operator RunManifest is immutable for the life of this run.
  # Keep the inner PX4CTRL gate's similarly named artifacts below this directory.
  RUNTIME_RESULT_DIR="${RESULT_DIR}/runtime"
fi
RUNTIME_LOCK_DIR="${PROJECT_ROOT}/Results/sunray_ros1/.sunray_ros1_runtime.lock"
RECORD_ROSBAG="${RECORD_ROSBAG:-true}"
GUI="${GUI:-false}"
REVIEW_OPEN_RVIZ="${REVIEW_OPEN_RVIZ:-true}"
REVIEW_START_CLOUD_NODE="${REVIEW_START_CLOUD_NODE:-true}"
REVIEW_PRESTART_HOLD_S="${REVIEW_PRESTART_HOLD_S:-15}"
MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-180}"
TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-600}"
MOSIM_UE_STATE_STREAM="${MOSIM_UE_STATE_STREAM:-true}"
MOSIM_UE_STATE_STREAM_RATE_HZ="${MOSIM_UE_STATE_STREAM_RATE_HZ:-100}"
PX4CTRL_MISSION_EXTRA_ARGS="${PX4CTRL_MISSION_EXTRA_ARGS:-}"

if [[ "${MISSION}" == "figure8" && -z "${PX4CTRL_MISSION_EXTRA_ARGS}" ]]; then
  PX4CTRL_MISSION_EXTRA_ARGS="--initial-hover-s 12 --figure8-period-s 24 --figure8-cycles 1 --figure8-x-amp-m 0.45 --figure8-y-amp-m 0.25 --post-hold-s 3 --land-wait-s 20 --force-disarm-after-land --force-disarm-timeout-s 18 --pre-takeoff-state-stable-s 3 --pre-takeoff-state-timeout-s 60 --pre-takeoff-max-abs-roll-pitch-deg 2 --takeoff-timeout-s 90 --wall-timeout-s 480 --acceptance-mode formal"
fi

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
FASTLIO_ALIGNMENT_ORIGIN_X="${FASTLIO_ALIGNMENT_ORIGIN_X:-${SUNRAY_UAV_INIT_X}}"
FASTLIO_ALIGNMENT_ORIGIN_Y="${FASTLIO_ALIGNMENT_ORIGIN_Y:-${SUNRAY_UAV_INIT_Y}}"
FASTLIO_ALIGNMENT_ORIGIN_Z="${FASTLIO_ALIGNMENT_ORIGIN_Z:-0.035}"
FASTLIO_ALIGNMENT_ORIGIN_XYZ="${FASTLIO_ALIGNMENT_ORIGIN_X} ${FASTLIO_ALIGNMENT_ORIGIN_Y} ${FASTLIO_ALIGNMENT_ORIGIN_Z}"

validate_factory_l2_fastlio_alignment_origin() {
  python3 - \
    "${SUNRAY_UAV_INIT_X}" \
    "${SUNRAY_UAV_INIT_Y}" \
    "${FASTLIO_ALIGNMENT_ORIGIN_X}" \
    "${FASTLIO_ALIGNMENT_ORIGIN_Y}" <<'PY'
import math
import sys

try:
    spawn_x, spawn_y, origin_x, origin_y = (float(value) for value in sys.argv[1:])
except ValueError as exc:
    raise SystemExit(f"Factory L2 FAST-LIO alignment origin is not numeric: {exc}") from exc

if not (
    math.isclose(spawn_x, origin_x, rel_tol=0.0, abs_tol=1e-6)
    and math.isclose(spawn_y, origin_y, rel_tol=0.0, abs_tol=1e-6)
):
    raise SystemExit(
        "Factory L2 FAST-LIO config alignment origin XY must match SUNRAY_UAV_INIT_X/Y "
        f"(spawn=({spawn_x}, {spawn_y}), origin=({origin_x}, {origin_y}))"
    )
PY
}

# The FAST-LIO config reference is expressed in Factory world coordinates.
# Reject a mismatched copy-only invocation before any ROS/PX4 process starts.
validate_factory_l2_fastlio_alignment_origin

mkdir -p "${RESULT_DIR}" "${RUNTIME_RESULT_DIR}"

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
    "${MISSION}" \
    "${basic_exit_code}" \
    "${RECORD_ROSBAG}" \
    "${ROSBAG_FILE}" \
    "${OPERATOR_RUN_ENABLED}" \
    "${RUNTIME_RESULT_DIR}" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
run_id = sys.argv[2]
mission = sys.argv[3]
basic_exit_code = int(sys.argv[4])
record_requested = sys.argv[5].lower() == "true"
rosbag_path = pathlib.Path(sys.argv[6])
operator_display_requested = sys.argv[7].lower() == "true"
runtime_root = pathlib.Path(sys.argv[8])
metrics_path = runtime_root / "PX4CTRL_BASIC_MISSION_METRICS.json"
try:
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    metrics = {}

lifecycle = metrics.get("operational_lifecycle_gate") or {}
checks = lifecycle.get("checks") or {}
sample_counts = metrics.get("sample_counts") or {}
trajectory = metrics.get("trajectory") or {}
rosbag_ready = (not record_requested) or (rosbag_path.is_file() and rosbag_path.stat().st_size > 0)
display_lifecycle_blockers = []
if not checks.get("pre_takeoff_state_ready"):
    display_lifecycle_blockers.append("pre_takeoff_state_not_ready")
if not checks.get("static_odom_ready_before_takeoff"):
    display_lifecycle_blockers.append("static_odom_not_ready")
if not checks.get("physical_takeoff_observed"):
    display_lifecycle_blockers.append("physical_takeoff_not_observed")
if not checks.get("final_state_disarmed"):
    display_lifecycle_blockers.append("final_state_not_disarmed")
if not checks.get("final_truth_available"):
    display_lifecycle_blockers.append("final_truth_missing")
final_z_rel = checks.get("final_z_rel_m")
max_final_z_rel = checks.get("max_final_z_rel_m")
if isinstance(final_z_rel, (int, float)) and isinstance(max_final_z_rel, (int, float)) and final_z_rel > max_final_z_rel:
    display_lifecycle_blockers.append(f"final_z_rel_above_max:{final_z_rel}")

trajectory_required = mission in {"figure8", "spiral", "circle", "step_x", "step_y", "step_z"}
trajectory_blockers = []
if trajectory_required:
    if int(sample_counts.get("reference", 0) or 0) <= 0:
        trajectory_blockers.append("reference_samples_missing")
    if int(sample_counts.get("truth", 0) or 0) <= 0:
        trajectory_blockers.append("truth_samples_missing")
    if int(trajectory.get("matched_samples", 0) or 0) <= 0:
        trajectory_blockers.append("matched_trajectory_samples_missing")

expected_exit_codes = {0} if mission == "takeoff_hover_land" else {0, 2}
display_lifecycle_passed = not display_lifecycle_blockers
trajectory_data_chain_passed = not trajectory_blockers
passed = (
    basic_exit_code in expected_exit_codes
    and display_lifecycle_passed
    and trajectory_data_chain_passed
    and rosbag_ready
)
reasons = []
if basic_exit_code not in expected_exit_codes:
    reasons.append(f"unexpected_basic_gate_exit:{basic_exit_code}")
reasons.extend(f"display_lifecycle:{item}" for item in display_lifecycle_blockers)
reasons.extend(f"trajectory_data_chain:{item}" for item in trajectory_blockers)
if not rosbag_ready:
    reasons.append("rosbag_not_recorded")
payload = {
    "schema": "mosim.sunray_ros1.fastlio_operator_live_status.v1",
    "run_id": run_id,
    "mission": mission,
    "status": "passed" if passed else "blocked",
    "reason": None if passed else ";".join(reasons),
    "functional_lifecycle": lifecycle,
    "operator_display_lifecycle": {
        "status": "passed" if display_lifecycle_passed else "blocked",
        "blockers": display_lifecycle_blockers,
        "checks": checks,
        "claim_boundary": "This is a display/reproducibility lifecycle check; it does not replace the controller performance gate.",
    },
    "trajectory_data_chain": {
        "status": "passed" if trajectory_data_chain_passed else "blocked",
        "blockers": trajectory_blockers,
        "required": trajectory_required,
        "reference_samples": int(sample_counts.get("reference", 0) or 0),
        "truth_samples": int(sample_counts.get("truth", 0) or 0),
        "matched_samples": int(trajectory.get("matched_samples", 0) or 0),
        "claim_boundary": "Trajectory samples prove that live reference/truth data were published and recorded; they do not prove tracking performance.",
    },
    "underlying_controller_gate": {
        "status": metrics.get("status"),
        "exit_code": basic_exit_code,
        "formal_performance_gate": metrics.get("formal_performance_gate"),
        "note": "The operator display gate never upgrades a blocked formal controller-performance result.",
    },
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
            "/gazebo/model_states",
            "/Laser_map",
            "/cloud_registered",
            "/Odometry",
            "/path",
            "/mosim/fastlio/laser_map_obstacles",
            "/mosim/fastlio/occupancy_object_review",
            "/mosim/fastlio/uav_path",
            "/mosim/fastlio/uav_axes",
            "/uav1/livox/lidar",
            "/uav1/livox/imu",
            "/tf",
            "/tf_static",
        ],
    },
    "display": {
        "qgc_read_only_requested": operator_display_requested,
        "ue_state_stream_metrics": str(root / "ue_sender_metrics.json"),
        "rviz_requested": True,
        "trajectory_topics": ["/mosim/px4ctrl/reference_path", "/mosim/px4ctrl/truth_path", "/mosim/fastlio/uav_path"],
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
  echo "operation_selector=factory_l2_${MISSION}"
  echo "mission=${MISSION}"
  echo "run_id=${RUN_ID}"
  echo "result_dir=${RESULT_DIR}"
  echo "runtime_result_dir=${RUNTIME_RESULT_DIR}"
  echo "controller_authority=px4ctrl_only"
  echo "state_chain=fastlio_to_px4_ekf_to_mavros_local_odom"
  echo "fastlio_alignment_origin_xyz=${FASTLIO_ALIGNMENT_ORIGIN_XYZ}"
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

run_inner_gate() {
  export PROJECT_ROOT RUN_ID GUI REVIEW_OPEN_RVIZ REVIEW_START_CLOUD_NODE
  export REVIEW_PRESTART_HOLD_S MAVROS_READY_TIMEOUT_S TOTAL_TIMEOUT_S WORLD_FILE GAZEBO_MODEL_PATH
  export SUNRAY_GAZEBO_LAUNCH_FILE SUNRAY_UAV_INIT_X SUNRAY_UAV_INIT_Y
  export SUNRAY_UAV_INIT_Z SUNRAY_UAV_INIT_YAW FASTLIO_FILTER_SIZE_SURF
  export FASTLIO_FILTER_SIZE_MAP REVIEW_START_OCCUPANCY_NODE
  export FASTLIO_ALIGNMENT_ORIGIN_XYZ
  export SUNRAY_GPS_SENSOR_MODE=removed
  export PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=true
  export PX4CTRL_START_EXTERNAL_FUSION=true
  export PX4CTRL_ODOM_SOURCE=mavros_local
  export PX4CTRL_ODOM_TOPIC=/uav1/mavros/local_position/odom
  export FASTLIO_ALIGNMENT_Z_SOURCE=truth
  export FASTLIO_ALIGNMENT_REFERENCE=config
  export FASTLIO_ALIGNMENT_REQUIRED=true
  export REVIEW_START_FASTLIO=true
  export PX4CTRL_HOVER_PERCENTAGE="${PX4CTRL_HOVER_PERCENTAGE:-0.456}"
  export PX4CTRL_SUNRAY150_IMU_CALIBRATION_ENABLED=false
  if [[ "${PX4CTRL_CORE_PROFILE:-}" == "graphical_c99" ]]; then
    export PX4CTRL_EXPECTED_BUILD_BACKEND=graphical_px4ctrl_c99
  fi
  if [[ "${MISSION}" == "takeoff_hover_land" ]]; then
    export PX4CTRL_ACCEPTANCE_MODE=operational_lifecycle
    RESULT_DIR="${RUNTIME_RESULT_DIR}" exec bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_fastlio_hover_gate.sh" takeoff_hover_land
  fi
  export PX4CTRL_MISSION_EXTRA_ARGS
  RESULT_DIR="${RUNTIME_RESULT_DIR}" exec bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" "${MISSION}"
}

run_inner_gate > "${RESULT_DIR}/basic_gate_runner.log" 2>&1 &
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
  finalize_operator_run "blocked" "factory_l2_${MISSION}_runtime_not_ready"
  exit 4
fi

if [[ "${OPERATOR_RUN_ENABLED}" == "true" ]]; then
  QGC_SIDECAR_READINESS_ARGS=()
  case "${ORCHESTRATOR_REQUIRE_ACTUATOR_TELEMETRY:-true}" in
    true) ;;
    false) QGC_SIDECAR_READINESS_ARGS+=(--skip-actuator-telemetry-readiness) ;;
    *)
      echo "ORCHESTRATOR_REQUIRE_ACTUATOR_TELEMETRY must be true or false" >&2
      exit 2
      ;;
  esac
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
    "${QGC_SIDECAR_READINESS_ARGS[@]}" \
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
    /gazebo/model_states \
    /position_cmd \
    /mosim/px4ctrl/reference_path \
    /mosim/px4ctrl/truth_path \
    /Laser_map \
    /cloud_registered \
    /Odometry \
    /path \
    /mosim/fastlio/laser_map_obstacles \
    /mosim/fastlio/occupancy_object_review \
    /mosim/fastlio/uav_path \
    /mosim/fastlio/uav_axes \
    /uav1/livox/lidar \
    /uav1/livox/imu \
    /tf \
    /tf_static \
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
  finalize_operator_run "completed" "factory_l2_${MISSION}_completed"
else
  finalize_operator_run "blocked" "factory_l2_${MISSION}_blocked"
fi
stop_process QGC_SIDECAR_PID

if [[ "${TERMINAL_STATE}" != "completed" ]]; then
  exit 1
fi
