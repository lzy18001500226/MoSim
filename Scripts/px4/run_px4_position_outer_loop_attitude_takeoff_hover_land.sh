#!/usr/bin/env bash
# PX4-native generated position outer-loop attitude takeoff-hover-land gate.
#
# Scope:
# - Starts Micro XRCE-DDS Agent and official PX4 SITL Gazebo x500 target.
# - Starts the MoSim generated C position outer-loop attitude adapter with
#   auto_offboard=true and auto_arm=true.
# - Publishes a continuous PlannerSetpoint trajectory: takeoff, hover, land.
# - Records PX4 status/position/ack topics and evaluates flight quality.
# - Does not write Gazebo motor/actuator topics directly.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
PX4_DIR="${PX4_DIR:-${PROJECT_ROOT}/Results/tmp/px4_gitwork/PX4}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/px4_gazebo/px4_position_outer_loop_attitude_takeoff_hover_land_$(date +%Y%m%d_%H%M%S)}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
PX4_ROS2_INSTALL="${PX4_ROS2_INSTALL:-${PROJECT_ROOT}/Results/ros2_build/px4_attitude_adapter_20260620_006/install/setup.bash}"
STARTUP_TIMEOUT_S="${STARTUP_TIMEOUT_S:-360}"
TOPIC_WAIT_S="${TOPIC_WAIT_S:-150}"
HEADLESS="${HEADLESS:-1}"
PX4_SIM_SPEED_FACTOR="${PX4_SIM_SPEED_FACTOR:-1}"
SANITIZE_WSL_PATH="${SANITIZE_WSL_PATH:-1}"
ROS_LOG_DIR="${ROS_LOG_DIR:-${PROJECT_ROOT}/Results/tmp/ros_logs/px4_position_outer_loop_attitude_takeoff_hover_land}"

TARGET_ALTITUDE_M="${TARGET_ALTITUDE_M:-0.8}"
TAKEOFF_S="${TAKEOFF_S:-10.0}"
HOVER_S="${HOVER_S:-8.0}"
LAND_S="${LAND_S:-10.0}"
POST_LAND_S="${POST_LAND_S:-4.0}"
PUBLISH_RATE_HZ="${PUBLISH_RATE_HZ:-20.0}"
WARMUP_SETPOINT_COUNT="${WARMUP_SETPOINT_COUNT:-30}"
PREFLIGHT_WAIT_S="${PREFLIGHT_WAIT_S:-45}"
STALE_TIMEOUT_S="${STALE_TIMEOUT_S:-1.0}"
RUN_GCS_HEARTBEAT="${RUN_GCS_HEARTBEAT:-1}"
GCS_HEARTBEAT_UDP_PORT="${GCS_HEARTBEAT_UDP_PORT:-18570}"
ADAPTER_HOVER_THRUST="${ADAPTER_HOVER_THRUST:-0.48}"
ADAPTER_THRUST_SCALE="${ADAPTER_THRUST_SCALE:-0.04}"
ADAPTER_MIN_THRUST="${ADAPTER_MIN_THRUST:-0.15}"
ADAPTER_MAX_THRUST="${ADAPTER_MAX_THRUST:-0.65}"
ADAPTER_MAX_TILT_RAD="${ADAPTER_MAX_TILT_RAD:-0.20}"
ADAPTER_X_ERROR_SIGN="${ADAPTER_X_ERROR_SIGN:-1.0}"
ADAPTER_Y_ERROR_SIGN="${ADAPTER_Y_ERROR_SIGN:-1.0}"
ADAPTER_XY_VELOCITY_DAMPING_S="${ADAPTER_XY_VELOCITY_DAMPING_S:-0.0}"
ADAPTER_Z_VELOCITY_DAMPING_S="${ADAPTER_Z_VELOCITY_DAMPING_S:-0.0}"
ADAPTER_ROLL_OUTPUT_SIGN="${ADAPTER_ROLL_OUTPUT_SIGN:--1.0}"
ADAPTER_PITCH_OUTPUT_SIGN="${ADAPTER_PITCH_OUTPUT_SIGN:-1.0}"
ADAPTER_ARM_FIRST="${ADAPTER_ARM_FIRST:-true}"

mkdir -p "${RESULT_DIR}" "${ROS_LOG_DIR}"
export ROS_LOG_DIR

if [[ "${SANITIZE_WSL_PATH}" == "1" ]]; then
  export PATH="$(python3 - <<'PY'
import os
blocked = (
    "/mnt/d/Dev/Anaconda3",
    "/mnt/c/Program Files/NVIDIA GPU Computing Toolkit",
    "/mnt/d/Program Files/MATLAB",
    "/mnt/d/Program Files/MWORKS",
)
parts = []
for part in os.environ.get("PATH", "").split(":"):
    if any(part.startswith(prefix) for prefix in blocked):
        continue
    parts.append(part)
print(":".join(parts))
PY
)"
  unset CPATH C_INCLUDE_PATH CPLUS_INCLUDE_PATH LIBRARY_PATH LD_LIBRARY_PATH PKG_CONFIG_PATH CMAKE_PREFIX_PATH Protobuf_DIR protobuf_DIR
fi

agent_pid=""
px4_pid=""
adapter_pid=""
publisher_pid=""
recorder_pid=""
gcs_pid=""

terminate_process_tree() {
  local pid="${1:-}"
  local grace_seconds="${2:-3}"
  if [[ -z "${pid}" ]] || ! kill -0 "${pid}" >/dev/null 2>&1; then
    return 0
  fi
  local child
  for child in $(pgrep -P "${pid}" 2>/dev/null || true); do
    terminate_process_tree "${child}" "${grace_seconds}"
  done
  kill "${pid}" >/dev/null 2>&1 || true
  local waited=0
  while kill -0 "${pid}" >/dev/null 2>&1 && [[ "${waited}" -lt "${grace_seconds}" ]]; do
    sleep 1
    waited=$((waited + 1))
  done
  if kill -0 "${pid}" >/dev/null 2>&1; then
    kill -KILL "${pid}" >/dev/null 2>&1 || true
  fi
  wait "${pid}" 2>/dev/null || true
}

cleanup() {
  terminate_process_tree "${publisher_pid}" 2
  terminate_process_tree "${recorder_pid}" 2
  terminate_process_tree "${gcs_pid}" 2
  terminate_process_tree "${adapter_pid}" 3
  terminate_process_tree "${px4_pid}" 5
  terminate_process_tree "${agent_pid}" 3
}
trap cleanup EXIT

find_agent_cmd() {
  if command -v MicroXRCEAgent >/dev/null 2>&1; then
    command -v MicroXRCEAgent
    return 0
  fi
  if command -v micro-xrce-dds-agent >/dev/null 2>&1; then
    command -v micro-xrce-dds-agent
    return 0
  fi
  if [[ -x /snap/bin/micro-xrce-dds-agent ]]; then
    printf '%s\n' /snap/bin/micro-xrce-dds-agent
    return 0
  fi
  return 1
}

write_blocker() {
  local status="${1}"
  local message="${2}"
  python3 - "${RESULT_DIR}" "${status}" "${message}" <<'PY'
import json
import pathlib
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
payload = {
    "schema": "mosim.px4_position_outer_loop_attitude_takeoff_hover_land.v1",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "status": sys.argv[2],
    "message": sys.argv[3],
    "semantic_boundary": "px4_native_generated_mworks_position_outer_loop_attitude_takeoff_hover_land",
    "result_dir": str(result_dir),
}
(result_dir / "PX4_POSITION_OUTER_LOOP_ATTITUDE_TAKEOFF_HOVER_LAND.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(payload, ensure_ascii=False, indent=2))
PY
}

agent_cmd="$(find_agent_cmd || true)"
if [[ -z "${agent_cmd}" ]]; then
  write_blocker "blocked_missing_micro_xrce_agent" "Micro XRCE-DDS Agent was not found"
  exit 2
fi
if [[ ! -d "${PX4_DIR}" ]]; then
  write_blocker "blocked_missing_px4_dir" "PX4_DIR does not exist: ${PX4_DIR}"
  exit 2
fi

"${agent_cmd}" udp4 -p 8888 > "${RESULT_DIR}/xrce_agent.log" 2>&1 &
agent_pid="$!"
printf '%s\n' "${agent_pid}" > "${RESULT_DIR}/xrce_agent.pid"
sleep 2
if ! kill -0 "${agent_pid}" >/dev/null 2>&1; then
  write_blocker "blocked_xrce_agent_failed_to_start" "Micro XRCE-DDS Agent exited before PX4 start"
  exit 2
fi

(
  cd "${PX4_DIR}"
  HEADLESS="${HEADLESS}" PX4_SIM_SPEED_FACTOR="${PX4_SIM_SPEED_FACTOR}" \
    timeout "${STARTUP_TIMEOUT_S}s" make px4_sitl gz_x500
) > "${RESULT_DIR}/px4_gz_x500.log" 2>&1 &
px4_pid="$!"
printf '%s\n' "${px4_pid}" > "${RESULT_DIR}/px4_make.pid"

set +u
if [[ -f "${ROS_SETUP}" ]]; then
  # shellcheck disable=SC1090
  source "${ROS_SETUP}"
fi
if [[ -f "${PX4_ROS2_INSTALL}" ]]; then
  # shellcheck disable=SC1090
  source "${PX4_ROS2_INSTALL}"
fi
set -u

{
  echo "ROS_DISTRO=${ROS_DISTRO:-}"
  echo "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-unset}"
  echo "RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-unset}"
  echo "ROS_LOG_DIR=${ROS_LOG_DIR}"
  command -v ros2 || true
  ros2 daemon stop || true
  ros2 daemon status || true
} > "${RESULT_DIR}/ros2_env.txt" 2>&1

deadline=$((SECONDS + TOPIC_WAIT_S))
vehicle_status_topic=""
local_position_topic=""
command_ack_topic=""
land_detected_topic=""
vehicle_control_mode_topic=""
actuator_motors_topic=""
attitude_setpoint_input_topic=""
while [[ "${SECONDS}" -lt "${deadline}" ]]; do
  if ! kill -0 "${px4_pid}" >/dev/null 2>&1; then
    write_blocker "blocked_px4_exited_before_topics" "PX4 exited before required ROS2 topics appeared"
    exit 2
  fi
  timeout 12s ros2 topic list --no-daemon --spin-time 4 -t > "${RESULT_DIR}/ros2_topic_list.txt" 2> "${RESULT_DIR}/ros2_topic_list.err" || true
  vehicle_status_topic="$(awk '/^\/fmu\/out\/vehicle_status(_v[0-9]+)?([[:space:]]|$)/ {print $1; exit}' "${RESULT_DIR}/ros2_topic_list.txt" 2>/dev/null || true)"
  local_position_topic="$(awk '/^\/fmu\/out\/vehicle_local_position(_v[0-9]+)?([[:space:]]|$)/ {print $1; exit}' "${RESULT_DIR}/ros2_topic_list.txt" 2>/dev/null || true)"
  command_ack_topic="$(awk '/^\/fmu\/out\/vehicle_command_ack(_v[0-9]+)?([[:space:]]|$)/ {print $1; exit}' "${RESULT_DIR}/ros2_topic_list.txt" 2>/dev/null || true)"
  land_detected_topic="$(awk '/^\/fmu\/out\/vehicle_land_detected(_v[0-9]+)?([[:space:]]|$)/ {print $1; exit}' "${RESULT_DIR}/ros2_topic_list.txt" 2>/dev/null || true)"
  vehicle_control_mode_topic="$(awk '/^\/fmu\/out\/vehicle_control_mode(_v[0-9]+)?([[:space:]]|$)/ {print $1; exit}' "${RESULT_DIR}/ros2_topic_list.txt" 2>/dev/null || true)"
  actuator_motors_topic="$(awk '/^\/fmu\/out\/actuator_motors(_v[0-9]+)?([[:space:]]|$)/ {print $1; exit}' "${RESULT_DIR}/ros2_topic_list.txt" 2>/dev/null || true)"
  attitude_setpoint_input_topic="$(awk '/^\/fmu\/in\/vehicle_attitude_setpoint(_v[0-9]+)?([[:space:]]|$)/ {print $1; exit}' "${RESULT_DIR}/ros2_topic_list.txt" 2>/dev/null || true)"
  if [[ -n "${vehicle_status_topic}" && -n "${local_position_topic}" && -n "${command_ack_topic}" && -n "${land_detected_topic}" ]]; then
    break
  fi
  sleep 3
done

if [[ -z "${vehicle_status_topic}" || -z "${local_position_topic}" || -z "${command_ack_topic}" || -z "${land_detected_topic}" ]]; then
  write_blocker "blocked_missing_required_topics" "Required PX4 output topics did not appear"
  exit 2
fi
if [[ -z "${attitude_setpoint_input_topic}" ]]; then
  write_blocker "blocked_missing_attitude_setpoint_input_topic" "PX4 did not expose /fmu/in/vehicle_attitude_setpoint or a versioned equivalent"
  exit 2
fi

cat > "${RESULT_DIR}/selected_topics.env" <<EOF
vehicle_status_topic=${vehicle_status_topic}
local_position_topic=${local_position_topic}
command_ack_topic=${command_ack_topic}
land_detected_topic=${land_detected_topic}
vehicle_control_mode_topic=${vehicle_control_mode_topic}
actuator_motors_topic=${actuator_motors_topic}
attitude_setpoint_input_topic=${attitude_setpoint_input_topic}
EOF

python3 - "${RESULT_DIR}" "${vehicle_status_topic}" "${local_position_topic}" "${command_ack_topic}" "${land_detected_topic}" "${vehicle_control_mode_topic}" "${actuator_motors_topic}" "${attitude_setpoint_input_topic}" <<'PY' &
import json
import pathlib
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
vehicle_status_topic, local_position_topic, command_ack_topic, land_detected_topic, vehicle_control_mode_topic, actuator_motors_topic, attitude_setpoint_input_topic = sys.argv[2:9]

try:
    import rclpy
    from px4_msgs.msg import (
        OffboardControlMode,
        ActuatorMotors,
        VehicleAttitudeSetpoint,
        VehicleCommandAck,
        VehicleControlMode,
        VehicleLandDetected,
        VehicleLocalPosition,
        VehicleStatus,
    )
except Exception as exc:
    (result_dir / "recorder_blocker.json").write_text(json.dumps({"status": "blocked_import_error", "error": str(exc)}), encoding="utf-8")
    raise

def scrub_message(msg):
    if isinstance(msg, VehicleStatus):
        return {
            "timestamp_us": int(msg.timestamp),
            "arming_state": int(msg.arming_state),
            "nav_state": int(msg.nav_state),
            "failsafe": bool(msg.failsafe),
            "accepts_offboard_setpoints": bool(msg.accepts_offboard_setpoints),
            "pre_flight_checks_pass": bool(msg.pre_flight_checks_pass),
        }
    if isinstance(msg, VehicleLocalPosition):
        return {
            "timestamp_us": int(msg.timestamp),
            "xy_valid": bool(msg.xy_valid),
            "z_valid": bool(msg.z_valid),
            "v_xy_valid": bool(msg.v_xy_valid),
            "v_z_valid": bool(msg.v_z_valid),
            "x": float(msg.x),
            "y": float(msg.y),
            "z": float(msg.z),
            "vx": float(msg.vx),
            "vy": float(msg.vy),
            "vz": float(msg.vz),
            "heading": float(msg.heading),
            "heading_good_for_control": bool(msg.heading_good_for_control),
            "dead_reckoning": bool(msg.dead_reckoning),
        }
    if isinstance(msg, VehicleCommandAck):
        return {
            "timestamp_us": int(msg.timestamp),
            "command": int(msg.command),
            "result": int(msg.result),
            "from_external": bool(msg.from_external),
        }
    if isinstance(msg, OffboardControlMode):
        return {
            "timestamp_us": int(msg.timestamp),
            "position": bool(msg.position),
            "velocity": bool(msg.velocity),
            "acceleration": bool(msg.acceleration),
            "attitude": bool(msg.attitude),
            "body_rate": bool(msg.body_rate),
            "thrust_and_torque": bool(getattr(msg, "thrust_and_torque", False)),
            "direct_actuator": bool(getattr(msg, "direct_actuator", False)),
        }
    if isinstance(msg, VehicleAttitudeSetpoint):
        return {
            "timestamp_us": int(msg.timestamp),
            "yaw_sp_move_rate": float(msg.yaw_sp_move_rate),
            "q_d": [float(value) for value in msg.q_d],
            "thrust_body": [float(value) for value in msg.thrust_body],
        }
    if isinstance(msg, VehicleLandDetected):
        fields = {"timestamp_us": int(msg.timestamp)}
        for name in ("landed", "maybe_landed", "ground_contact", "freefall"):
            if hasattr(msg, name):
                fields[name] = bool(getattr(msg, name))
        return fields
    if isinstance(msg, VehicleControlMode):
        fields = {"timestamp_us": int(msg.timestamp)}
        for name in (
            "flag_armed",
            "flag_multicopter_position_control_enabled",
            "flag_control_offboard_enabled",
            "flag_control_manual_enabled",
            "flag_control_attitude_enabled",
            "flag_control_rates_enabled",
            "flag_control_allocation_enabled",
        ):
            if hasattr(msg, name):
                fields[name] = bool(getattr(msg, name))
        return fields
    if isinstance(msg, ActuatorMotors):
        return {
            "timestamp_us": int(msg.timestamp),
            "timestamp_sample_us": int(getattr(msg, "timestamp_sample", 0)),
            "control": [float(value) for value in msg.control],
            "reversible_flags": int(getattr(msg, "reversible_flags", 0)),
        }
    return {}

rclpy.init()
node = rclpy.create_node("mosim_px4_position_outer_loop_attitude_takeoff_hover_land_recorder")
paths = {
    "vehicle_status": result_dir / "vehicle_status.jsonl",
    "local_position": result_dir / "vehicle_local_position.jsonl",
    "command_ack": result_dir / "vehicle_command_ack.jsonl",
    "land_detected": result_dir / "vehicle_land_detected.jsonl",
    "offboard_control_mode": result_dir / "offboard_control_mode.jsonl",
    "attitude_setpoint": result_dir / "vehicle_attitude_setpoint.jsonl",
    "vehicle_control_mode": result_dir / "vehicle_control_mode.jsonl",
    "actuator_motors": result_dir / "actuator_motors.jsonl",
}
handles = {key: path.open("w", encoding="utf-8") for key, path in paths.items()}

def write(kind, msg):
    payload = scrub_message(msg)
    payload["schema"] = f"mosim.px4.{kind}.sample.v1"
    payload["recorded_wall_time_utc"] = datetime.now(timezone.utc).isoformat()
    handles[kind].write(json.dumps(payload, ensure_ascii=False) + "\n")
    handles[kind].flush()

qos = rclpy.qos.QoSProfile(depth=100, reliability=rclpy.qos.ReliabilityPolicy.BEST_EFFORT)
node.create_subscription(VehicleStatus, vehicle_status_topic, lambda msg: write("vehicle_status", msg), qos)
node.create_subscription(VehicleLocalPosition, local_position_topic, lambda msg: write("local_position", msg), qos)
node.create_subscription(VehicleCommandAck, command_ack_topic, lambda msg: write("command_ack", msg), qos)
node.create_subscription(VehicleLandDetected, land_detected_topic, lambda msg: write("land_detected", msg), qos)
node.create_subscription(OffboardControlMode, "/fmu/in/offboard_control_mode", lambda msg: write("offboard_control_mode", msg), qos)
node.create_subscription(VehicleAttitudeSetpoint, attitude_setpoint_input_topic, lambda msg: write("attitude_setpoint", msg), qos)
if vehicle_control_mode_topic:
    node.create_subscription(VehicleControlMode, vehicle_control_mode_topic, lambda msg: write("vehicle_control_mode", msg), qos)
if actuator_motors_topic:
    node.create_subscription(ActuatorMotors, actuator_motors_topic, lambda msg: write("actuator_motors", msg), qos)

try:
    rclpy.spin(node)
except BaseException:
    pass
finally:
    for handle in handles.values():
        handle.close()
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()
PY
recorder_pid="$!"
printf '%s\n' "${recorder_pid}" > "${RESULT_DIR}/recorder.pid"
sleep 2
if ! kill -0 "${recorder_pid}" >/dev/null 2>&1; then
  write_blocker "blocked_recorder_failed_to_start" "PX4 topic recorder exited before adapter start"
  exit 2
fi

preflight_deadline=$((SECONDS + PREFLIGHT_WAIT_S))
preflight_ready=0
while [[ "${SECONDS}" -lt "${preflight_deadline}" ]]; do
  if [[ -s "${RESULT_DIR}/vehicle_status.jsonl" ]] && python3 - "${RESULT_DIR}/vehicle_status.jsonl" <<'PY'
import json
import sys
from pathlib import Path
rows = []
for line in Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines()[-10:]:
    try:
        rows.append(json.loads(line))
    except Exception:
        pass
ok = any(row.get("pre_flight_checks_pass") is True for row in rows)
raise SystemExit(0 if ok else 1)
PY
  then
    preflight_ready=1
    break
  fi
  sleep 1
done
python3 - "${RESULT_DIR}" "${preflight_ready}" "${PREFLIGHT_WAIT_S}" <<'PY'
import json
import pathlib
import sys
from datetime import datetime, timezone
payload = {
    "schema": "mosim.px4_preflight_wait.v1",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "status": "ready" if sys.argv[2] == "1" else "timeout_continue",
    "wait_s": float(sys.argv[3]),
    "note": "Adapter starts after this wait; timeout_continue preserves diagnostics instead of hiding PX4 health failures.",
}
(pathlib.Path(sys.argv[1]) / "preflight_wait.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

if [[ "${RUN_GCS_HEARTBEAT}" == "1" ]]; then
  python3 - "${RESULT_DIR}" "${GCS_HEARTBEAT_UDP_PORT}" <<'PY' > "${RESULT_DIR}/gcs_heartbeat.log" 2>&1 &
import json
import pathlib
import sys
import time

result_dir = pathlib.Path(sys.argv[1])
port = int(sys.argv[2])
try:
    from pymavlink import mavutil
except Exception as exc:
    (result_dir / "gcs_heartbeat_blocker.json").write_text(
        json.dumps({"status": "blocked_missing_pymavlink", "error": str(exc)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    raise

connection = mavutil.mavlink_connection(f"udpout:127.0.0.1:{port}", source_system=255, source_component=190)
(result_dir / "gcs_heartbeat_manifest.json").write_text(
    json.dumps(
        {
            "schema": "mosim.px4_headless_gcs_heartbeat.v1",
            "status": "running",
            "udp_target": f"127.0.0.1:{port}",
            "purpose": "headless SITL GCS heartbeat only; no control commands",
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
while True:
    connection.mav.heartbeat_send(
        mavutil.mavlink.MAV_TYPE_GCS,
        mavutil.mavlink.MAV_AUTOPILOT_INVALID,
        0,
        0,
        mavutil.mavlink.MAV_STATE_ACTIVE,
    )
    time.sleep(1.0)
PY
  gcs_pid="$!"
  printf '%s\n' "${gcs_pid}" > "${RESULT_DIR}/gcs_heartbeat.pid"
  sleep 2
  if ! kill -0 "${gcs_pid}" >/dev/null 2>&1; then
    write_blocker "blocked_gcs_heartbeat_failed_to_start" "Headless GCS heartbeat process exited"
    exit 2
  fi
fi

ros2 run mosim_px4_offboard_adapter position_outer_loop_to_px4_attitude_node \
  --ros-args \
  -p auto_arm:=true \
  -p auto_offboard:=true \
  -p arm_first:="${ADAPTER_ARM_FIRST}" \
  -p expected_frame:=map \
  -p local_position_topic:="${local_position_topic}" \
  -p attitude_setpoint_topic:="${attitude_setpoint_input_topic:-/fmu/in/vehicle_attitude_setpoint_v1}" \
  -p publish_rate_hz:="${PUBLISH_RATE_HZ}" \
  -p stale_timeout_s:="${STALE_TIMEOUT_S}" \
  -p warmup_setpoint_count:="${WARMUP_SETPOINT_COUNT}" \
  -p hover_thrust:="${ADAPTER_HOVER_THRUST}" \
  -p thrust_scale:="${ADAPTER_THRUST_SCALE}" \
  -p min_thrust:="${ADAPTER_MIN_THRUST}" \
  -p max_thrust:="${ADAPTER_MAX_THRUST}" \
  -p max_tilt_rad:="${ADAPTER_MAX_TILT_RAD}" \
  -p x_error_sign:="${ADAPTER_X_ERROR_SIGN}" \
  -p y_error_sign:="${ADAPTER_Y_ERROR_SIGN}" \
  -p xy_velocity_damping_s:="${ADAPTER_XY_VELOCITY_DAMPING_S}" \
  -p z_velocity_damping_s:="${ADAPTER_Z_VELOCITY_DAMPING_S}" \
  -p roll_output_sign:="${ADAPTER_ROLL_OUTPUT_SIGN}" \
  -p pitch_output_sign:="${ADAPTER_PITCH_OUTPUT_SIGN}" \
  > "${RESULT_DIR}/adapter.log" 2>&1 &
adapter_pid="$!"
printf '%s\n' "${adapter_pid}" > "${RESULT_DIR}/adapter.pid"
sleep 2
if ! kill -0 "${adapter_pid}" >/dev/null 2>&1; then
  write_blocker "blocked_adapter_failed_to_start" "MoSim generated position outer-loop attitude adapter exited"
  exit 2
fi

python3 - "${RESULT_DIR}" "${TARGET_ALTITUDE_M}" "${TAKEOFF_S}" "${HOVER_S}" "${LAND_S}" "${POST_LAND_S}" "${PUBLISH_RATE_HZ}" <<'PY' > "${RESULT_DIR}/planner_setpoint_publisher.log" 2>&1 &
import math
import pathlib
import sys
import time

import rclpy
from mosim_msgs.msg import PlannerSetpoint

result_dir = pathlib.Path(sys.argv[1])
target_altitude = float(sys.argv[2])
takeoff_s = float(sys.argv[3])
hover_s = float(sys.argv[4])
land_s = float(sys.argv[5])
post_land_s = float(sys.argv[6])
rate_hz = float(sys.argv[7])

total_s = takeoff_s + hover_s + land_s + post_land_s
dt = 1.0 / rate_hz

rclpy.init()
node = rclpy.create_node("mosim_px4_position_outer_loop_attitude_takeoff_hover_land_setpoint_publisher")
publisher = node.create_publisher(PlannerSetpoint, "/mosim/planner/setpoint", 10)
trace = (result_dir / "planner_setpoint_trace.jsonl").open("w", encoding="utf-8")

def smoothstep(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3.0 - 2.0 * u)

start = time.monotonic()
sequence = 0
try:
    while rclpy.ok():
        elapsed = time.monotonic() - start
        if elapsed > total_s:
            break
        if elapsed < takeoff_s:
            phase = "takeoff"
            u = elapsed / takeoff_s
            z = target_altitude * smoothstep(u)
            zdot = target_altitude * (6.0 * u * (1.0 - u)) / takeoff_s
        elif elapsed < takeoff_s + hover_s:
            phase = "hover"
            z = target_altitude
            zdot = 0.0
        elif elapsed < takeoff_s + hover_s + land_s:
            phase = "land"
            u = (elapsed - takeoff_s - hover_s) / land_s
            z = target_altitude * (1.0 - smoothstep(u))
            zdot = -target_altitude * (6.0 * u * (1.0 - u)) / land_s
        else:
            phase = "post_land_hold"
            z = 0.0
            zdot = 0.0

        msg = PlannerSetpoint()
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.header.frame_id = "map"
        msg.sequence = sequence
        msg.frame_id = "map"
        msg.position_m = [0.0, 0.0, float(z)]
        msg.velocity_mps = [0.0, 0.0, float(zdot)]
        msg.acceleration_mps2 = [0.0, 0.0, 0.0]
        msg.yaw_rad = 0.0
        msg.yaw_rate_radps = 0.0
        msg.trajectory_status = 1
        msg.planner_id = "mworks_position_outer_loop_attitude_gate"
        publisher.publish(msg)
        trace.write(
            f'{{"elapsed_s":{elapsed:.6f},"sequence":{sequence},"phase":"{phase}","position_m":[0.0,0.0,{z:.6f}],"velocity_mps":[0.0,0.0,{zdot:.6f}],"yaw_rad":0.0}}\n'
        )
        trace.flush()
        sequence += 1
        rclpy.spin_once(node, timeout_sec=0.0)
        time.sleep(dt)
finally:
    trace.close()
    node.destroy_node()
    rclpy.shutdown()
PY
publisher_pid="$!"
printf '%s\n' "${publisher_pid}" > "${RESULT_DIR}/publisher.pid"

wait "${publisher_pid}" || true
sleep 3

python3 - "${RESULT_DIR}" "${TARGET_ALTITUDE_M}" "${ADAPTER_HOVER_THRUST}" "${ADAPTER_THRUST_SCALE}" "${ADAPTER_MIN_THRUST}" "${ADAPTER_MAX_THRUST}" "${ADAPTER_MAX_TILT_RAD}" "${ADAPTER_X_ERROR_SIGN}" "${ADAPTER_Y_ERROR_SIGN}" "${ADAPTER_XY_VELOCITY_DAMPING_S}" "${ADAPTER_Z_VELOCITY_DAMPING_S}" "${ADAPTER_ROLL_OUTPUT_SIGN}" "${ADAPTER_PITCH_OUTPUT_SIGN}" "${ADAPTER_ARM_FIRST}" <<'PY'
import json
import math
import pathlib
import statistics
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
target_altitude = float(sys.argv[2])
adapter_params = {
    "hover_thrust": float(sys.argv[3]),
    "thrust_scale": float(sys.argv[4]),
    "min_thrust": float(sys.argv[5]),
    "max_thrust": float(sys.argv[6]),
    "max_tilt_rad": float(sys.argv[7]),
    "x_error_sign": float(sys.argv[8]),
    "y_error_sign": float(sys.argv[9]),
    "xy_velocity_damping_s": float(sys.argv[10]),
    "z_velocity_damping_s": float(sys.argv[11]),
    "roll_output_sign": float(sys.argv[12]),
    "pitch_output_sign": float(sys.argv[13]),
    "arm_first": sys.argv[14],
    "preflight_wait_file": str(result_dir / "preflight_wait.json"),
}

def read_jsonl(path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return rows

local_rows = read_jsonl(result_dir / "vehicle_local_position.jsonl")
status_rows = read_jsonl(result_dir / "vehicle_status.jsonl")
ack_rows = read_jsonl(result_dir / "vehicle_command_ack.jsonl")
land_rows = read_jsonl(result_dir / "vehicle_land_detected.jsonl")
setpoint_rows = read_jsonl(result_dir / "planner_setpoint_trace.jsonl")
offboard_rows = read_jsonl(result_dir / "offboard_control_mode.jsonl")
attitude_rows = read_jsonl(result_dir / "vehicle_attitude_setpoint.jsonl")
vehicle_control_mode_rows = read_jsonl(result_dir / "vehicle_control_mode.jsonl")
actuator_motors_rows = read_jsonl(result_dir / "actuator_motors.jsonl")

def ned_to_enu(row):
    return {
        "timestamp_us": row.get("timestamp_us", 0),
        "x_east": float(row.get("y", math.nan)),
        "y_north": float(row.get("x", math.nan)),
        "z_up": -float(row.get("z", math.nan)),
        "vx_east": float(row.get("vy", math.nan)),
        "vy_north": float(row.get("vx", math.nan)),
        "vz_up": -float(row.get("vz", math.nan)),
        "heading": float(row.get("heading", math.nan)),
        "valid": bool(row.get("xy_valid")) and bool(row.get("z_valid")),
    }

enu_rows = [ned_to_enu(row) for row in local_rows if row.get("xy_valid") and row.get("z_valid")]
first_t = enu_rows[0]["timestamp_us"] if enu_rows else 0
for row in enu_rows:
    row["t_s"] = (row["timestamp_us"] - first_t) / 1e6 if first_t else 0.0

duration_s = enu_rows[-1]["t_s"] if enu_rows else 0.0
max_alt = max((row["z_up"] for row in enu_rows), default=math.nan)
final_alt = enu_rows[-1]["z_up"] if enu_rows else math.nan
max_xy = max((math.hypot(row["x_east"], row["y_north"]) for row in enu_rows), default=math.nan)

hover_candidate_rows = [row for row in enu_rows if abs(row["z_up"] - target_altitude) <= 0.15 and abs(row["vz_up"]) <= 0.15]
hover_start_s = None
hover_end_s = None
if hover_candidate_rows:
    hover_start_s = hover_candidate_rows[0]["t_s"]
    hover_end_s = hover_candidate_rows[-1]["t_s"]
hover_rows = hover_candidate_rows
hover_z_errors = [abs(row["z_up"] - target_altitude) for row in hover_rows]
hover_xy = [math.hypot(row["x_east"], row["y_north"]) for row in hover_rows]
hover_vxy = [math.hypot(row["vx_east"], row["vy_north"]) for row in hover_rows]
hover_z_rmse = math.sqrt(statistics.fmean([e * e for e in hover_z_errors])) if hover_z_errors else math.nan
hover_xy_max = max(hover_xy, default=math.nan)
hover_vxy_max = max(hover_vxy, default=math.nan)
hover_duration_s = (hover_end_s - hover_start_s) if hover_start_s is not None and hover_end_s is not None else 0.0

post_land_rows = [row for row in enu_rows if row["t_s"] >= max(0.0, duration_s - 3.0)]
post_land_xy_span = 0.0
post_land_heading_span = 0.0
if len(post_land_rows) >= 2:
    xs = [row["x_east"] for row in post_land_rows]
    ys = [row["y_north"] for row in post_land_rows]
    hs = [row["heading"] for row in post_land_rows if math.isfinite(row["heading"])]
    post_land_xy_span = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
    if hs:
        post_land_heading_span = max(hs) - min(hs)

accepted_acks = [row for row in ack_rows if row.get("result") == 0]
rejected_acks = [row for row in ack_rows if row.get("result") not in (0, None)]
nav_states = sorted({row.get("nav_state") for row in status_rows if row.get("nav_state") is not None})
arming_states = sorted({row.get("arming_state") for row in status_rows if row.get("arming_state") is not None})
failsafe_seen = any(row.get("failsafe") for row in status_rows)
offboard_seen = any(row.get("nav_state") == 14 for row in status_rows)
armed_seen = any(row.get("arming_state") == 2 for row in status_rows)
landed_seen = any(row.get("landed") for row in land_rows)

def topic_rate_stats(rows):
    times = [int(row.get("timestamp_us", 0)) for row in rows if int(row.get("timestamp_us", 0)) > 0]
    if len(times) < 2:
        return {"count": len(rows), "duration_s": 0.0, "mean_rate_hz": 0.0, "max_gap_s": math.nan}
    times.sort()
    gaps = [(b - a) / 1e6 for a, b in zip(times, times[1:]) if b > a]
    duration = (times[-1] - times[0]) / 1e6
    return {
        "count": len(rows),
        "duration_s": duration,
        "mean_rate_hz": (len(times) - 1) / duration if duration > 0 else 0.0,
        "max_gap_s": max(gaps) if gaps else math.nan,
    }

attitude_rate = topic_rate_stats(attitude_rows)
offboard_rate = topic_rate_stats(offboard_rows)
thrust_z_values = [
    float(row.get("thrust_body", [math.nan, math.nan, math.nan])[2])
    for row in attitude_rows
    if isinstance(row.get("thrust_body"), list) and len(row.get("thrust_body")) >= 3
]
q_norms = []
for row in attitude_rows:
    q = row.get("q_d")
    if isinstance(q, list) and len(q) == 4:
        q_norms.append(math.sqrt(sum(float(value) * float(value) for value in q)))

attitude_summary = {
    "rate": attitude_rate,
    "thrust_body_z_min": min(thrust_z_values, default=math.nan),
    "thrust_body_z_max": max(thrust_z_values, default=math.nan),
    "thrust_body_z_mean": statistics.fmean(thrust_z_values) if thrust_z_values else math.nan,
    "q_norm_min": min(q_norms, default=math.nan),
    "q_norm_max": max(q_norms, default=math.nan),
    "first_sample": attitude_rows[0] if attitude_rows else None,
    "last_sample": attitude_rows[-1] if attitude_rows else None,
}
offboard_summary = {
    "rate": offboard_rate,
    "attitude_mode_count": sum(1 for row in offboard_rows if row.get("attitude") is True),
    "position_mode_count": sum(1 for row in offboard_rows if row.get("position") is True),
    "velocity_mode_count": sum(1 for row in offboard_rows if row.get("velocity") is True),
    "first_sample": offboard_rows[0] if offboard_rows else None,
    "last_sample": offboard_rows[-1] if offboard_rows else None,
}
vehicle_control_mode_summary = {
    "rate": topic_rate_stats(vehicle_control_mode_rows),
    "armed_count": sum(1 for row in vehicle_control_mode_rows if row.get("flag_armed") is True),
    "offboard_enabled_count": sum(1 for row in vehicle_control_mode_rows if row.get("flag_control_offboard_enabled") is True),
    "attitude_enabled_count": sum(1 for row in vehicle_control_mode_rows if row.get("flag_control_attitude_enabled") is True),
    "rates_enabled_count": sum(1 for row in vehicle_control_mode_rows if row.get("flag_control_rates_enabled") is True),
    "allocation_enabled_count": sum(1 for row in vehicle_control_mode_rows if row.get("flag_control_allocation_enabled") is True),
    "first_sample": vehicle_control_mode_rows[0] if vehicle_control_mode_rows else None,
    "last_sample": vehicle_control_mode_rows[-1] if vehicle_control_mode_rows else None,
}
motor_values = []
for row in actuator_motors_rows:
    control = row.get("control")
    if isinstance(control, list):
        motor_values.extend(float(value) for value in control if math.isfinite(float(value)))
actuator_motors_summary = {
    "rate": topic_rate_stats(actuator_motors_rows),
    "control_min": min(motor_values, default=math.nan),
    "control_max": max(motor_values, default=math.nan),
    "control_mean": statistics.fmean(motor_values) if motor_values else math.nan,
    "first_sample": actuator_motors_rows[0] if actuator_motors_rows else None,
    "last_sample": actuator_motors_rows[-1] if actuator_motors_rows else None,
}

checks = {
    "has_local_position_samples": len(enu_rows) >= 50,
    "has_status_samples": len(status_rows) >= 10,
    "armed_seen": armed_seen,
    "offboard_seen": offboard_seen,
    "failsafe_not_seen": not failsafe_seen,
    "max_altitude_reached": math.isfinite(max_alt) and max_alt >= 0.8 * target_altitude,
    "hover_duration_ok": hover_duration_s >= 4.0,
    "hover_z_rmse_ok": math.isfinite(hover_z_rmse) and hover_z_rmse <= 0.35,
    "hover_xy_max_ok": math.isfinite(hover_xy_max) and hover_xy_max <= 0.75,
    "hover_vxy_max_ok": math.isfinite(hover_vxy_max) and hover_vxy_max <= 1.0,
    "final_altitude_near_ground": math.isfinite(final_alt) and final_alt <= 0.35,
    "post_land_xy_span_ok": post_land_xy_span <= 0.25,
    "post_land_heading_span_ok": post_land_heading_span <= 0.75,
    "attitude_setpoints_recorded": len(attitude_rows) >= 50,
    "offboard_heartbeat_recorded": len(offboard_rows) >= 50,
    "attitude_setpoint_rate_ok": attitude_rate.get("mean_rate_hz", 0.0) >= 10.0,
    "attitude_setpoint_gap_ok": math.isfinite(attitude_rate.get("max_gap_s", math.nan)) and attitude_rate["max_gap_s"] <= 0.5,
    "attitude_quaternion_norm_ok": bool(q_norms) and min(q_norms) >= 0.99 and max(q_norms) <= 1.01,
    "attitude_thrust_command_present": bool(thrust_z_values) and min(thrust_z_values) < -0.2,
    "vehicle_control_mode_recorded": len(vehicle_control_mode_rows) >= 10,
    "actuator_motors_recorded": len(actuator_motors_rows) >= 10,
    "actuator_motors_nonzero": bool(motor_values) and max(motor_values) > 0.05,
}

status = "passed" if all(checks.values()) else "failed_metrics"
payload = {
    "schema": "mosim.px4_position_outer_loop_attitude_takeoff_hover_land.v1",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "status": status,
    "semantic_boundary": "px4_native_generated_mworks_position_outer_loop_attitude_takeoff_hover_land",
    "result_dir": str(result_dir),
    "inputs": {
        "target_altitude_m": target_altitude,
        "adapter_params": adapter_params,
        "source": "continuous PlannerSetpoint plus generated MWORKS position outer-loop attitude adapter",
        "headless_gcs_heartbeat": (result_dir / "gcs_heartbeat_manifest.json").exists(),
    },
    "counts": {
        "planner_setpoints": len(setpoint_rows),
        "local_position": len(local_rows),
        "vehicle_status": len(status_rows),
        "command_ack": len(ack_rows),
        "land_detected": len(land_rows),
        "offboard_control_mode": len(offboard_rows),
        "attitude_setpoint": len(attitude_rows),
        "vehicle_control_mode": len(vehicle_control_mode_rows),
        "actuator_motors": len(actuator_motors_rows),
    },
    "state": {
        "nav_states": nav_states,
        "arming_states": arming_states,
        "offboard_seen": offboard_seen,
        "armed_seen": armed_seen,
        "failsafe_seen": failsafe_seen,
        "landed_seen": landed_seen,
        "accepted_ack_count": len(accepted_acks),
        "rejected_ack_count": len(rejected_acks),
        "rejected_acks": rejected_acks[-10:],
    },
    "metrics": {
        "duration_s": round(duration_s, 3),
        "max_altitude_m": max_alt,
        "final_altitude_m": final_alt,
        "max_xy_distance_m": max_xy,
        "hover_z_rmse_m": hover_z_rmse,
        "hover_duration_s": hover_duration_s,
        "hover_window_s": [hover_start_s, hover_end_s],
        "hover_xy_max_m": hover_xy_max,
        "hover_vxy_max_mps": hover_vxy_max,
        "post_land_xy_span_m": post_land_xy_span,
        "post_land_heading_span_rad": post_land_heading_span,
        "offboard_control_mode_summary": offboard_summary,
        "attitude_setpoint_summary": attitude_summary,
        "vehicle_control_mode_summary": vehicle_control_mode_summary,
        "actuator_motors_summary": actuator_motors_summary,
    },
    "checks": checks,
    "claim_boundary": [
        "This is a PX4-native generated MWORKS position outer-loop attitude takeoff-hover-land gate.",
        "It does not write Gazebo actuator or motor topics directly.",
        "Passing this gate proves only the exported position outer-loop C code can participate in a bounded PX4 attitude Offboard loop; it does not certify the full MWORKS controller or 8字 performance.",
    ],
    "files": {
        "planner_setpoint_trace": str(result_dir / "planner_setpoint_trace.jsonl"),
        "vehicle_local_position": str(result_dir / "vehicle_local_position.jsonl"),
        "vehicle_status": str(result_dir / "vehicle_status.jsonl"),
        "vehicle_command_ack": str(result_dir / "vehicle_command_ack.jsonl"),
        "vehicle_land_detected": str(result_dir / "vehicle_land_detected.jsonl"),
        "offboard_control_mode": str(result_dir / "offboard_control_mode.jsonl"),
        "vehicle_attitude_setpoint": str(result_dir / "vehicle_attitude_setpoint.jsonl"),
        "vehicle_control_mode": str(result_dir / "vehicle_control_mode.jsonl"),
        "actuator_motors": str(result_dir / "actuator_motors.jsonl"),
        "adapter_log": str(result_dir / "adapter.log"),
        "px4_log": str(result_dir / "px4_gz_x500.log"),
    },
}
(result_dir / "PX4_POSITION_OUTER_LOOP_ATTITUDE_TAKEOFF_HOVER_LAND.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False, indent=2))
PY

status="$(python3 -c "import json,sys; print(json.load(open('${RESULT_DIR}/PX4_POSITION_OUTER_LOOP_ATTITUDE_TAKEOFF_HOVER_LAND.json', encoding='utf-8')).get('status','unknown'))")"
if [[ "${status}" != "passed" ]]; then
  exit 2
fi
