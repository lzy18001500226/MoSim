#!/usr/bin/env bash
# Run the source-local single-UAV video demo without changing controller authority.

set -euo pipefail

if [[ "$#" -gt 1 ]] || { [[ "$#" -eq 1 ]] && [[ "$1" != "--factory-l2-fault-demo" ]]; }; then
  echo "Usage: $0 [--factory-l2-fault-demo]" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
RUN_ID="${RUN_ID:-sunray_ros1_fastlio_fault_demo_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
FTC_PLUGIN_WS="${FTC_PLUGIN_WS:-${PROJECT_ROOT}/build/ros1/ftc_actuator_plugin_ws}"
ROTOR_INDEX="${MOTOR_EFFICIENCY_ROTOR_INDEX:-1}"
EFFECTIVENESS="${MOTOR_EFFICIENCY_EFFECTIVENESS:-0.85}"
DURATION_S="${MOTOR_EFFICIENCY_DURATION_S:-4}"
MINIMUM_ALTITUDE_M="${MOTOR_EFFICIENCY_MINIMUM_ALTITUDE_M:-0.95}"
AIRBORNE_TIMEOUT_S="${MOTOR_EFFICIENCY_AIRBORNE_TIMEOUT_S:-90}"
RESET_HOLD_S="${MOTOR_EFFICIENCY_RESET_HOLD_S:-2}"
MISSION_START_TIMEOUT_S="${MOTOR_EFFICIENCY_MISSION_START_TIMEOUT_S:-180}"
RECORD_ROSBAG="${RECORD_ROSBAG:-true}"
# Gazebo is the headless physics backend. UE is the only rendered flight view.
GUI="${GUI:-false}"
REVIEW_OPEN_RVIZ="${REVIEW_OPEN_RVIZ:-true}"
REVIEW_START_CLOUD_NODE="${REVIEW_START_CLOUD_NODE:-true}"
REVIEW_START_OCCUPANCY_NODE="${REVIEW_START_OCCUPANCY_NODE:-true}"
REVIEW_PRESTART_HOLD_S="${REVIEW_PRESTART_HOLD_S:-5}"
MOSIM_UE_STATE_STREAM="${MOSIM_UE_STATE_STREAM:-true}"
MOSIM_UE_STATE_STREAM_RATE_HZ="${MOSIM_UE_STATE_STREAM_RATE_HZ:-100}"
# Factory L2 loads a large static collision scene before the Sunray model
# exposes its MAVLink TCP endpoint. Keep this local to the Factory demo so the
# generic basic gate retains its shorter diagnostic timeout.
MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-180}"
FACTORY_L2_WORLD_RELATIVE="Config/gazebo/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf"
FACTORY_L2_MODELS_RELATIVE="Config/gazebo/models"
FACTORY_L2_LAUNCH_RELATIVE="Scripts/sunray/factory_l2_sunray_px4_gazebo.launch"
WORLD_FILE="${WORLD_FILE:-${PROJECT_ROOT}/${FACTORY_L2_WORLD_RELATIVE}}"
GAZEBO_MODEL_PATH="${GAZEBO_MODEL_PATH:-${PROJECT_ROOT}/${FACTORY_L2_MODELS_RELATIVE}}"
SUNRAY_GAZEBO_LAUNCH_FILE="${SUNRAY_GAZEBO_LAUNCH_FILE:-${PROJECT_ROOT}/${FACTORY_L2_LAUNCH_RELATIVE}}"
SUNRAY_UAV_INIT_X="${SUNRAY_UAV_INIT_X:--10.575025}"
SUNRAY_UAV_INIT_Y="${SUNRAY_UAV_INIT_Y:--19.36313}"
SUNRAY_UAV_INIT_Z="${SUNRAY_UAV_INIT_Z:-0.2}"
SUNRAY_UAV_INIT_YAW="${SUNRAY_UAV_INIT_YAW:-0}"
# Preserve the already accepted Factory L2 map baseline. These are not tuning
# knobs for this wrapper and must not fall back to the generic small-world values.
FASTLIO_FILTER_SIZE_SURF="${FASTLIO_FILTER_SIZE_SURF:-0.5}"
FASTLIO_FILTER_SIZE_MAP="${FASTLIO_FILTER_SIZE_MAP:-0.5}"
RUNTIME_LOCK_DIR="${PROJECT_ROOT}/Results/sunray_ros1/.sunray_ros1_runtime.lock"
OPERATOR_RUN_ID="${MOSIM_OPERATOR_RUN_ID:-}"
OPERATOR_RUN_DIR="${MOSIM_OPERATOR_RUN_DIR:-}"
OPERATOR_RUN_MANIFEST="${MOSIM_OPERATOR_RUN_MANIFEST:-}"
OPERATOR_RUN_ENABLED=false
QGC_SIDECAR_PID=""
UE_STREAM_PID=""

if [[ -n "${OPERATOR_RUN_ID}" || -n "${OPERATOR_RUN_DIR}" || -n "${OPERATOR_RUN_MANIFEST}" ]]; then
  if [[ -z "${OPERATOR_RUN_ID}" || -z "${OPERATOR_RUN_DIR}" || -z "${OPERATOR_RUN_MANIFEST}" ]]; then
    echo "MOSIM_OPERATOR_RUN_ID, MOSIM_OPERATOR_RUN_DIR, and MOSIM_OPERATOR_RUN_MANIFEST must be set together" >&2
    exit 2
  fi
  OPERATOR_RUN_ENABLED=true
fi

mkdir -p "${RESULT_DIR}"

BASIC_PID=""
ROSBAG_PID=""
ROSBAG_BASE="${RESULT_DIR}/rosbag/${RUN_ID}"
ROSBAG_FILE="${ROSBAG_BASE}.bag"

stop_qgc_sidecar() {
  if [[ -z "${QGC_SIDECAR_PID}" ]]; then
    return
  fi
  if ! kill -0 "${QGC_SIDECAR_PID}" 2>/dev/null; then
    wait "${QGC_SIDECAR_PID}" 2>/dev/null || true
    QGC_SIDECAR_PID=""
    return
  fi
  kill -INT "${QGC_SIDECAR_PID}" 2>/dev/null || true
  for _ in $(seq 1 10); do
    if ! kill -0 "${QGC_SIDECAR_PID}" 2>/dev/null; then
      break
    fi
    sleep 0.2
  done
  if kill -0 "${QGC_SIDECAR_PID}" 2>/dev/null; then
    kill -TERM "${QGC_SIDECAR_PID}" 2>/dev/null || true
  fi
  wait "${QGC_SIDECAR_PID}" 2>/dev/null || true
  QGC_SIDECAR_PID=""
}

stop_rosbag() {
  if [[ -z "${ROSBAG_PID}" ]] || ! kill -0 "${ROSBAG_PID}" 2>/dev/null; then
    return
  fi
  kill -INT "${ROSBAG_PID}" 2>/dev/null || true
  for _ in $(seq 1 20); do
    if ! kill -0 "${ROSBAG_PID}" 2>/dev/null; then
      break
    fi
    sleep 0.5
  done
  if kill -0 "${ROSBAG_PID}" 2>/dev/null; then
    kill -TERM "${ROSBAG_PID}" 2>/dev/null || true
  fi
  wait "${ROSBAG_PID}" 2>/dev/null || true
  ROSBAG_PID=""
}

stop_ue_stream() {
  if [[ -z "${UE_STREAM_PID}" ]]; then
    return
  fi
  if ! kill -0 "${UE_STREAM_PID}" 2>/dev/null; then
    wait "${UE_STREAM_PID}" 2>/dev/null || true
    UE_STREAM_PID=""
    return
  fi
  kill -INT "${UE_STREAM_PID}" 2>/dev/null || true
  for _ in $(seq 1 20); do
    if ! kill -0 "${UE_STREAM_PID}" 2>/dev/null; then
      break
    fi
    sleep 0.25
  done
  if kill -0 "${UE_STREAM_PID}" 2>/dev/null; then
    kill -TERM "${UE_STREAM_PID}" 2>/dev/null || true
  fi
  wait "${UE_STREAM_PID}" 2>/dev/null || true
  UE_STREAM_PID=""
}

cleanup() {
  local exit_code=$?
  set +e
  stop_ue_stream
  stop_qgc_sidecar
  stop_rosbag
  if [[ -n "${BASIC_PID}" ]] && kill -0 "${BASIC_PID}" 2>/dev/null; then
    kill -TERM "${BASIC_PID}" 2>/dev/null || true
    wait "${BASIC_PID}" 2>/dev/null || true
  fi
  return "${exit_code}"
}

on_signal() {
  exit 130
}

trap cleanup EXIT
trap on_signal INT TERM

{
  echo "schema=mosim.sunray_ros1.fastlio_fault_demo_command.v1"
  echo "operation_selector=factory_l2_fault_demo"
  echo "run_id=${RUN_ID}"
  echo "result_dir=${RESULT_DIR}"
  echo "controller_authority=px4ctrl_only"
  echo "state_chain=fastlio_to_px4_ekf_to_mavros_local_odom"
  echo "fault_mode=physical_gazebo_actuator_efficiency"
  echo "rotor_index=${ROTOR_INDEX}"
  echo "effectiveness=${EFFECTIVENESS}"
  echo "duration_s=${DURATION_S}"
  echo "mission_start_timeout_s=${MISSION_START_TIMEOUT_S}"
  echo "record_rosbag=${RECORD_ROSBAG}"
  echo "gui=${GUI}"
  echo "rviz=${REVIEW_OPEN_RVIZ}"
  echo "occupancy_review=${REVIEW_START_OCCUPANCY_NODE}"
  echo "fastlio_filter_size_surf_m=${FASTLIO_FILTER_SIZE_SURF}"
  echo "fastlio_filter_size_map_m=${FASTLIO_FILTER_SIZE_MAP}"
  echo "ue_state_stream=${MOSIM_UE_STATE_STREAM}"
  echo "mavros_ready_timeout_s=${MAVROS_READY_TIMEOUT_S}"
  echo "qgc_display_bridge=${OPERATOR_RUN_ENABLED}"
} > "${RESULT_DIR}/DEMO_COMMAND.txt"

bash "${PROJECT_ROOT}/Scripts/sunray/build_p7_ftc_actuator_plugin.sh" \
  > "${RESULT_DIR}/ftc_plugin_build.log" 2>&1
PLUGIN_LIB_DIR="${FTC_PLUGIN_WS}/devel/lib"
PLUGIN_LIBRARY="${PLUGIN_LIB_DIR}/libmosim_gazebo_ftc_actuator_plugin.so"
if [[ ! -f "${PLUGIN_LIBRARY}" ]]; then
  echo "FTC actuator plugin was not built: ${PLUGIN_LIBRARY}" >&2
  exit 3
fi

set +u
source /opt/ros/noetic/setup.bash
source "${PROJECT_ROOT}/Scripts/sunray/resolve_local_ros1_runtime.sh"
source "${LOCAL_ROS1_WS}/devel/setup.bash"
set -u

env \
  RUN_ID="${RUN_ID}" \
  RESULT_DIR="${RESULT_DIR}" \
  FTC_PLUGIN_WS="${FTC_PLUGIN_WS}" \
  MOSIM_ENABLE_FTC_ACTUATOR_PLUGIN=true \
  GAZEBO_PLUGIN_PATH="${PLUGIN_LIB_DIR}:${GAZEBO_PLUGIN_PATH:-}" \
  LD_LIBRARY_PATH="${PLUGIN_LIB_DIR}:${LD_LIBRARY_PATH:-}" \
  GUI="${GUI}" \
  REVIEW_OPEN_RVIZ="${REVIEW_OPEN_RVIZ}" \
  REVIEW_START_CLOUD_NODE="${REVIEW_START_CLOUD_NODE}" \
  REVIEW_START_OCCUPANCY_NODE="${REVIEW_START_OCCUPANCY_NODE}" \
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
  PX4CTRL_ACCEPTANCE_MODE="operational_lifecycle" \
  bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_fastlio_hover_gate.sh" \
  > "${RESULT_DIR}/basic_gate_runner.log" 2>&1 &
BASIC_PID=$!

MASTER_READY=false
for _ in $(seq 1 180); do
  if ! kill -0 "${BASIC_PID}" 2>/dev/null; then
    break
  fi
  if [[ -f "${RUNTIME_LOCK_DIR}/run_id" && "$(<"${RUNTIME_LOCK_DIR}/run_id")" == "${RUN_ID}" ]] && \
      rosparam get /rosversion >/dev/null 2>&1; then
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
  python3 - "${RESULT_DIR}" "${RUN_ID}" "${BASIC_EXIT_CODE}" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
payload = {
    "schema": "mosim.sunray_ros1.fastlio_fault_demo_status.v1",
    "run_id": sys.argv[2],
    "status": "blocked",
    "reason": "ros_master_not_ready_before_recording_and_fault_injection",
    "basic_gate_exit_code": int(sys.argv[3]),
    "claim_boundary": "No rosbag or fault command was started because the source-local Gazebo/PX4/MAVROS runtime did not become ready.",
}
(root / "DEMO_STATUS.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY
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
  sidecar_state="$(ps -o stat= -p "${QGC_SIDECAR_PID}" 2>/dev/null | tr -d '[:space:]')"
  if ! kill -0 "${QGC_SIDECAR_PID}" 2>/dev/null || [[ -z "${sidecar_state}" ]] || [[ "${sidecar_state:0:1}" == "Z" ]]; then
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
  if ! command -v rosbag >/dev/null 2>&1; then
    echo "rosbag is required when RECORD_ROSBAG=true" >&2
    exit 5
  fi
  {
    echo "rosbag record --lz4 -O ${ROSBAG_BASE}"
    printf '%s\n' \
      /uav1/mavros/state \
      /uav1/mavros/local_position/odom \
      /uav1/sunray/gazebo_pose \
      /position_cmd \
      /mosim/px4ctrl/reference_path \
      /mosim/px4ctrl/truth_path \
      /uav1/mosim/ftc_actuator_telemetry
  } > "${RESULT_DIR}/rosbag_command.txt"
  rosbag record --lz4 -O "${ROSBAG_BASE}" \
    /uav1/mavros/state \
    /uav1/mavros/local_position/odom \
    /uav1/sunray/gazebo_pose \
    /position_cmd \
    /mosim/px4ctrl/reference_path \
    /mosim/px4ctrl/truth_path \
    /uav1/mosim/ftc_actuator_telemetry \
    > "${RESULT_DIR}/rosbag_record.log" 2>&1 &
  ROSBAG_PID=$!
fi

# The FAST-LIO startup contract completes its estimator and state checks before
# it launches the existing mission node.  Start the airborne fault timer only
# after that node exists so initialization time cannot consume it.
MISSION_NODE_STARTED=false
mission_start_deadline=$((SECONDS + MISSION_START_TIMEOUT_S))
while (( SECONDS < mission_start_deadline )); do
  if [[ -f "${RESULT_DIR}/px4ctrl_basic_mission.log" ]]; then
    MISSION_NODE_STARTED=true
    break
  fi
  if ! kill -0 "${BASIC_PID}" 2>/dev/null; then
    break
  fi
  sleep 0.5
done

if [[ "${MISSION_NODE_STARTED}" != "true" ]]; then
  set +e
  wait "${BASIC_PID}"
  BASIC_EXIT_CODE=$?
  set -e
  BASIC_PID=""
  stop_ue_stream
  stop_rosbag
  python3 - "${RESULT_DIR}" "${RUN_ID}" "${BASIC_EXIT_CODE}" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
payload = {
    "schema": "mosim.sunray_ros1.fastlio_fault_demo_status.v1",
    "run_id": sys.argv[2],
    "status": "blocked",
    "reason": "mission_node_not_started_before_fault_injection",
    "basic_gate_exit_code": int(sys.argv[3]),
    "claim_boundary": "No fault command was published because the existing source-local mission node did not start within its bounded initialization window.",
}
(root / "DEMO_STATUS.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY
  exit 6
fi

set +e
python3 "${PROJECT_ROOT}/Scripts/sunray/apply_motor_efficiency_fault.py" \
  --result-dir "${RESULT_DIR}" \
  --rotor-index "${ROTOR_INDEX}" \
  --effectiveness "${EFFECTIVENESS}" \
  --duration-s "${DURATION_S}" \
  --minimum-altitude-m "${MINIMUM_ALTITUDE_M}" \
  --airborne-timeout-s "${AIRBORNE_TIMEOUT_S}" \
  --reset-hold-s "${RESET_HOLD_S}" \
  > "${RESULT_DIR}/motor_efficiency_injector.log" 2>&1
INJECTOR_EXIT_CODE=$?
if [[ "${OPERATOR_RUN_ENABLED}" == "true" ]]; then
  python3 - \
    "${RESULT_DIR}" \
    "${OPERATOR_RUN_DIR}" \
    "${OPERATOR_RUN_ID}" \
    "${ROTOR_INDEX}" \
    "${EFFECTIVENESS}" <<'PY'
import json
import os
import pathlib
import time
import sys

result_dir = pathlib.Path(sys.argv[1])
operator_run_dir = pathlib.Path(sys.argv[2])
operator_run_id = sys.argv[3]
rotor_index = int(sys.argv[4])
effectiveness = float(sys.argv[5])
source = result_dir / "MOTOR_EFFICIENCY_INJECTION_EVIDENCE.json"
try:
    injection = json.loads(source.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    injection = {}

accepted = injection.get("status") == "passed"
observed = int(injection.get("fault_effectiveness_observed_samples") or 0)
recovery_commanded = injection.get("reset_to_nominal_commanded") is True
reason = "terminal_fault_observed_and_nominal_restore_commanded"
if not accepted:
    reason = "terminal_fault_injection_not_accepted"
elif not recovery_commanded:
    reason = "terminal_fault_observed_restore_not_confirmed"

payload = {
    "schema": "mosim.runtime_injection_ack.v1",
    "command_id": "terminal-motor-efficiency-{}-{}".format(rotor_index, int(time.time() * 1000)),
    "run_id": operator_run_id,
    "vehicle_id": "uav1",
    "target": "motor_effectiveness",
    "rotor_index": rotor_index,
    "apply_mode": "set",
    "source": "terminal_fastlio_fault_demo_gate",
    "accepted": accepted,
    "reason_code": reason,
    "requested_value": effectiveness,
    "applied_value": effectiveness if accepted else None,
    "applied_at": time.time(),
    "observed_fault_samples": observed,
    "recovery": {
        "requested_effectiveness": 1.0,
        "reset_to_nominal_commanded": recovery_commanded,
        "evidence": str(source),
    },
}
ack_dir = operator_run_dir / "injection_acks"
ack_dir.mkdir(parents=True, exist_ok=True)
target = ack_dir / (payload["command_id"] + ".json")
temporary = target.with_name(target.name + ".{}.tmp".format(os.getpid()))
with temporary.open("w", encoding="utf-8", newline="\n") as stream:
    json.dump(payload, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
temporary.replace(target)
PY
fi
wait "${BASIC_PID}"
BASIC_EXIT_CODE=$?
set -e
BASIC_PID=""
stop_ue_stream
stop_rosbag
stop_qgc_sidecar

python3 - \
  "${RESULT_DIR}" \
  "${RUN_ID}" \
  "${BASIC_EXIT_CODE}" \
  "${INJECTOR_EXIT_CODE}" \
  "${RECORD_ROSBAG}" \
  "${ROSBAG_FILE}" \
  "${OPERATOR_RUN_ENABLED}" \
  "${OPERATOR_RUN_ID}" \
  "${OPERATOR_RUN_DIR}" \
  "${MOSIM_UE_STATE_STREAM}" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
run_id = sys.argv[2]
basic_exit_code = int(sys.argv[3])
injector_exit_code = int(sys.argv[4])
record_rosbag = sys.argv[5].lower() == "true"
rosbag_path = pathlib.Path(sys.argv[6])
operator_run_enabled = sys.argv[7].lower() == "true"
operator_run_id = sys.argv[8]
operator_run_dir = sys.argv[9]
ue_stream_requested = sys.argv[10].lower() == "true"
injection_path = root / "MOTOR_EFFICIENCY_INJECTION_EVIDENCE.json"
mission_path = root / "PX4CTRL_BASIC_MISSION_METRICS.json"
ue_metrics_path = root / "ue_sender_metrics.json"
injection = json.loads(injection_path.read_text(encoding="utf-8")) if injection_path.exists() else {}
mission = json.loads(mission_path.read_text(encoding="utf-8")) if mission_path.exists() else {}
landing = mission.get("landing_disarm") if isinstance(mission.get("landing_disarm"), dict) else {}
functional_lifecycle = bool(mission.get("takeoff_reached_altitude")) and bool(landing.get("success"))
physical_fault_ack = (
    injector_exit_code == 0
    and injection.get("status") == "passed"
    and injection.get("controller_override_observed") is False
    and injection.get("reset_to_nominal_commanded") is True
)
rosbag_ready = (not record_rosbag) or (rosbag_path.is_file() and rosbag_path.stat().st_size > 0)
status = "passed" if functional_lifecycle and physical_fault_ack and rosbag_ready else "blocked"
payload = {
    "schema": "mosim.sunray_ros1.fastlio_fault_demo_status.v1",
    "run_id": run_id,
    "status": status,
    "functional_lifecycle": {
        "status": "passed" if functional_lifecycle else "blocked",
        "takeoff_reached_altitude": mission.get("takeoff_reached_altitude"),
        "landing_disarm_success": landing.get("success"),
        "basic_gate_exit_code": basic_exit_code,
    },
    "physical_motor_fault": {
        "status": "passed" if physical_fault_ack else "blocked",
        "injector_exit_code": injector_exit_code,
        "rotor_index": injection.get("rotor_index"),
        "effectiveness": injection.get("effectiveness"),
        "observed_samples": injection.get("fault_effectiveness_observed_samples"),
        "controller_override_observed": injection.get("controller_override_observed"),
        "reset_to_nominal_commanded": injection.get("reset_to_nominal_commanded"),
        "evidence": str(injection_path),
    },
    "recording": {
        "requested": record_rosbag,
        "status": "passed" if rosbag_ready else "blocked",
        "rosbag": str(rosbag_path) if record_rosbag else "",
        "rosbag_bytes": rosbag_path.stat().st_size if rosbag_path.is_file() else 0,
        "topics": [
            "/uav1/mavros/state",
            "/uav1/mavros/local_position/odom",
            "/uav1/sunray/gazebo_pose",
            "/position_cmd",
            "/mosim/px4ctrl/reference_path",
            "/mosim/px4ctrl/truth_path",
            "/uav1/mosim/ftc_actuator_telemetry",
        ],
    },
    "quality_observation": {
        "status": mission.get("status", "missing"),
        "reason": mission.get("reason"),
        "metrics": str(mission_path),
        "policy": "Preserved as an observation. It does not override the functional lifecycle or physical fault acknowledgement in this video-demo gate.",
    },
    "qgc_display_bridge": {
        "requested": operator_run_enabled,
        "operator_run_id": operator_run_id if operator_run_enabled else "",
        "operator_run_dir": operator_run_dir if operator_run_enabled else "",
        "coordinate_evidence": (
            str(pathlib.Path(operator_run_dir) / "OPERATOR_MAP_COORDINATE_EVIDENCE.json")
            if operator_run_enabled else ""
        ),
        "telemetry": str(pathlib.Path(operator_run_dir) / "telemetry.json") if operator_run_enabled else "",
        "mode": "read_only_display" if operator_run_enabled else "not_requested",
    },
    "ue_display_bridge": {
        "requested": ue_stream_requested,
        "sender_metrics": str(ue_metrics_path),
        "sender_metrics_available": ue_metrics_path.is_file(),
        "claim_boundary": "Sender-side UDP metrics prove only that ROS state was emitted toward UE. They do not prove UE reception, rendering, or frame rate.",
    },
    "claim_boundary": (
        "This gate proves a source-local px4ctrl lifecycle and bounded physical Gazebo rotor-efficiency fault/recovery acknowledgement. "
        "px4ctrl remains the sole controller authority. It does not prove fault tolerance, controller robustness, or final tracking performance."
    ),
}
(root / "DEMO_STATUS.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if status == "passed" else 1)
PY

if [[ "${OPERATOR_RUN_ENABLED}" == "true" ]]; then
  terminal_state="$(python3 - "${RESULT_DIR}/DEMO_STATUS.json" <<'PY'
import json
import pathlib
import sys

status = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")).get("status")
print("completed" if status == "passed" else "blocked")
PY
)"
  terminal_reason="factory_l2_fault_demo_completed"
  if [[ "${terminal_state}" != "completed" ]]; then
    terminal_reason="factory_l2_fault_demo_blocked"
  fi
  python3 "${PROJECT_ROOT}/Scripts/ui/prepare_operator_run.py" \
    --finalize-active \
    --expected-run-id "${OPERATOR_RUN_ID}" \
    --terminal-state "${terminal_state}" \
    --reason-code "${terminal_reason}" \
    --terminal-source "terminal_fastlio_fault_demo_gate" \
    > "${RESULT_DIR}/qgc_operator_run_finalize.log" 2>&1
fi
