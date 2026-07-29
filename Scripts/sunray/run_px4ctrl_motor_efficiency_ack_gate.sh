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

mkdir -p "${RESULT_DIR}"
PLUGIN_LIB_DIR="${FTC_PLUGIN_WS}/devel/lib"
PLUGIN_LIBRARY="${PLUGIN_LIB_DIR}/libmosim_gazebo_ftc_actuator_plugin.so"
BASIC_PID=""
RUNTIME_LOCK_DIR="${PROJECT_ROOT}/Results/sunray_ros1/.sunray_ros1_runtime.lock"

cleanup() {
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
wait "${BASIC_PID}"
BASIC_EXIT_CODE=$?
set -e
BASIC_PID=""

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
