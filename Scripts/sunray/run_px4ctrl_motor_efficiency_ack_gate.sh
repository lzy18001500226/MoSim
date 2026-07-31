#!/usr/bin/env bash
# Verify bounded Gazebo motor-efficiency fault acknowledgement without taking control from px4ctrl.

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RUN_ID="${RUN_ID:-sunray_ros1_p3_motor_efficiency_ack_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
FTC_PLUGIN_WS="${FTC_PLUGIN_WS:-${PROJECT_ROOT}/build/ros1/ftc_actuator_plugin_ws}"
ROTOR_INDEX="${MOTOR_EFFICIENCY_ROTOR_INDEX:-1}"
EFFECTIVENESS="${MOTOR_EFFICIENCY_EFFECTIVENESS:-0.85}"
DURATION_S="${MOTOR_EFFICIENCY_DURATION_S:-4}"
MINIMUM_ALTITUDE_M="${MOTOR_EFFICIENCY_MINIMUM_ALTITUDE_M:-0.95}"
AIRBORNE_TIMEOUT_S="${MOTOR_EFFICIENCY_AIRBORNE_TIMEOUT_S:-90}"
OPERATOR_RUN_ID="${MOSIM_OPERATOR_RUN_ID:-}"
OPERATOR_RUN_DIR="${MOSIM_OPERATOR_RUN_DIR:-}"
OPERATOR_RUN_MANIFEST="${MOSIM_OPERATOR_RUN_MANIFEST:-}"
OPERATOR_RUN_ENABLED=false
QGC_SIDECAR_PID=""

if [[ -n "${OPERATOR_RUN_ID}" || -n "${OPERATOR_RUN_DIR}" || -n "${OPERATOR_RUN_MANIFEST}" ]]; then
  if [[ -z "${OPERATOR_RUN_ID}" || -z "${OPERATOR_RUN_DIR}" || -z "${OPERATOR_RUN_MANIFEST}" ]]; then
    echo "MOSIM_OPERATOR_RUN_ID, MOSIM_OPERATOR_RUN_DIR, and MOSIM_OPERATOR_RUN_MANIFEST must be set together" >&2
    exit 2
  fi
  if [[ -z "${WORLD_FILE:-}" || -z "${SUNRAY_GAZEBO_LAUNCH_FILE:-}" ]]; then
    echo "WORLD_FILE and SUNRAY_GAZEBO_LAUNCH_FILE are required when QGC display is enabled" >&2
    exit 2
  fi
  OPERATOR_RUN_ENABLED=true
fi

mkdir -p "${RESULT_DIR}"
PLUGIN_LIB_DIR="${FTC_PLUGIN_WS}/devel/lib"
PLUGIN_LIBRARY="${PLUGIN_LIB_DIR}/libmosim_gazebo_ftc_actuator_plugin.so"
BASIC_PID=""
RUNTIME_LOCK_DIR="${PROJECT_ROOT}/Results/sunray_ros1/.sunray_ros1_runtime.lock"

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

cleanup() {
  stop_qgc_sidecar
  if [[ -n "${BASIC_PID}" ]] && kill -0 "${BASIC_PID}" 2>/dev/null; then
    kill "${BASIC_PID}" 2>/dev/null || true
    wait "${BASIC_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

{
  echo "schema=mosim.sunray_ros1.motor_efficiency_ack_command.v1"
  echo "run_id=${RUN_ID}"
  echo "rotor_index=${ROTOR_INDEX}"
  echo "effectiveness=${EFFECTIVENESS}"
  echo "duration_s=${DURATION_S}"
  echo "minimum_altitude_m=${MINIMUM_ALTITUDE_M}"
  echo "controller_authority=px4ctrl_only"
  echo "fault_mode=physical_gazebo_actuator_efficiency"
} > "${RESULT_DIR}/fault_ack_command.txt"

bash "${PROJECT_ROOT}/Scripts/sunray/build_p7_ftc_actuator_plugin.sh" \
  > "${RESULT_DIR}/ftc_plugin_build.log" 2>&1
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
  SUNRAY_GPS_SENSOR_MODE=nested \
  PX4CTRL_BOOT_PARAM_OVERRIDES=EKF2_GPS_CTRL=7,EKF2_HGT_REF=1,EKF2_EV_CTRL=0 \
  PX4CTRL_CORE_PROFILE=original \
  PX4CTRL_START_EXTERNAL_FUSION=false \
  PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=false \
  PX4CTRL_SET_EKF_GLOBAL_ORIGIN=false \
  PX4CTRL_ODOM_SOURCE=mavros_local \
  PX4CTRL_HOVER_PERCENTAGE=0.37 \
  PX4CTRL_THRUST_ESTIMATE_ENABLE=false \
  PX4CTRL_SUNRAY150_IMU_CALIBRATION_ENABLED=false \
  MAVROS_STREAM_RATE_HZ=100 \
  MAVROS_SET_MESSAGE_INTERVALS=true \
  FREQUENCY_AUDIT_DURATION_S=0 \
  CONTROL_DIAGNOSTICS_DURATION_S=0 \
  TIME_TF_AUDIT_DURATION_S=0 \
  TOTAL_TIMEOUT_S=180 \
  bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" takeoff_hover_land \
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
  python3 - "${RESULT_DIR}" "${BASIC_EXIT_CODE}" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
payload = {
    "schema": "mosim.sunray_ros1.motor_efficiency_ack_gate.v1",
    "status": "blocked",
    "reason": "ros_master_not_ready_before_fault_injection",
    "basic_gate_exit_code": int(sys.argv[2]),
    "claim_boundary": "No fault command was published because the Gazebo/PX4/MAVROS runtime did not become ready.",
}
(root / "MOTOR_EFFICIENCY_ACK_STATUS.json").write_text(
    json.dumps(payload, indent=2) + "\n", encoding="utf-8")
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

set +e
python3 "${PROJECT_ROOT}/Scripts/sunray/apply_motor_efficiency_fault.py" \
  --result-dir "${RESULT_DIR}" \
  --rotor-index "${ROTOR_INDEX}" \
  --effectiveness "${EFFECTIVENESS}" \
  --duration-s "${DURATION_S}" \
  --minimum-altitude-m "${MINIMUM_ALTITUDE_M}" \
  --airborne-timeout-s "${AIRBORNE_TIMEOUT_S}" \
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
import sys
import time

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
    "source": "terminal_motor_efficiency_ack_gate",
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
stop_qgc_sidecar

python3 - "${RESULT_DIR}" "${BASIC_EXIT_CODE}" "${INJECTOR_EXIT_CODE}" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
basic_exit_code, injector_exit_code = map(int, sys.argv[2:])
injection_path = root / "MOTOR_EFFICIENCY_INJECTION_EVIDENCE.json"
mission_path = root / "PX4CTRL_BASIC_MISSION_METRICS.json"
injection = json.loads(injection_path.read_text(encoding="utf-8")) if injection_path.exists() else {}
mission = json.loads(mission_path.read_text(encoding="utf-8")) if mission_path.exists() else {}
ack_passed = injector_exit_code == 0 and injection.get("status") == "passed"
payload = {
    "schema": "mosim.sunray_ros1.motor_efficiency_ack_gate.v1",
    "status": "passed" if ack_passed else "blocked",
    "fault_ack_status": injection.get("status", "missing"),
    "basic_mission_status": mission.get("status", "missing"),
    "basic_gate_exit_code": basic_exit_code,
    "injector_exit_code": injector_exit_code,
    "injection_evidence": str(injection_path),
    "mission_metrics": str(mission_path),
    "controller_override_observed": injection.get("controller_override_observed"),
    "reset_to_nominal_commanded": injection.get("reset_to_nominal_commanded"),
    "claim_boundary": (
        "This gate proves only same-run Gazebo actuator-plugin acknowledgement of a bounded rotor-efficiency command and its nominal reset. "
        "px4ctrl remains the only controller authority. Mission-quality acceptance remains governed separately by PX4CTRL_BASIC_MISSION_METRICS.json."
    ),
}
(root / "MOTOR_EFFICIENCY_ACK_STATUS.json").write_text(
    json.dumps(payload, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if ack_passed else 1)
PY
