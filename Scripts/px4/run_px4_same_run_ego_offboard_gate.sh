#!/usr/bin/env bash
# Same-run EGO -> PX4 Offboard gate.
#
# Scope:
# - Starts Micro XRCE-DDS Agent and official PX4 SITL Gazebo x500 target.
# - Bridges PX4 fused local position to planner odometry.
# - Publishes a deterministic planner cloud fixture for the first same-run
#   transport gate. This is not MID360 / FAST-LIO evidence.
# - Starts EGO planner, traj_server_ros2_node, PositionCommand conversion,
#   setpoint adapter, and PX4 Offboard adapter.
# - Records EGO / PlannerSetpoint / PX4 flight topics and evaluates whether the
#   planner output actually drove PX4/Gazebo in the same run.
# - Does not write Gazebo motor/actuator topics directly.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
PX4_DIR="${PX4_DIR:-${PROJECT_ROOT}/Results/tmp/px4_gitwork/PX4}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/px4_gazebo/px4_same_run_ego_offboard_gate_$(date +%Y%m%d_%H%M%S)}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
MOSIM_MSGS_SETUP="${MOSIM_MSGS_SETUP:-${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs_20260615_ego_gate/install/setup.bash}"
SETPOINT_ADAPTER_SETUP="${SETPOINT_ADAPTER_SETUP:-${MOSIM_MSGS_SETUP}}"
PX4_ROS2_INSTALL="${PX4_ROS2_INSTALL:-${PROJECT_ROOT}/Results/ros2_build/px4_offboard_adapter_20260620_rebuild/install/setup.bash}"
EGO_SETUP="${EGO_SETUP:-${PROJECT_ROOT}/Results/tmp/ego_planner_ros2_port_ws/install/setup.bash}"
STARTUP_TIMEOUT_S="${STARTUP_TIMEOUT_S:-360}"
TOPIC_WAIT_S="${TOPIC_WAIT_S:-150}"
RUN_DURATION_S="${RUN_DURATION_S:-75}"
RECORD_DURATION_S="${RECORD_DURATION_S:-70}"
HEADLESS="${HEADLESS:-1}"
PX4_SIM_SPEED_FACTOR="${PX4_SIM_SPEED_FACTOR:-1}"
SANITIZE_WSL_PATH="${SANITIZE_WSL_PATH:-1}"
ROS_LOG_DIR="${ROS_LOG_DIR:-${PROJECT_ROOT}/Results/tmp/ros_logs/px4_same_run_ego_offboard_gate}"

PUBLISH_RATE_HZ="${PUBLISH_RATE_HZ:-20.0}"
WARMUP_SETPOINT_COUNT="${WARMUP_SETPOINT_COUNT:-30}"
STALE_TIMEOUT_S="${STALE_TIMEOUT_S:-1.0}"
RUN_GCS_HEARTBEAT="${RUN_GCS_HEARTBEAT:-1}"
GCS_HEARTBEAT_UDP_PORT="${GCS_HEARTBEAT_UDP_PORT:-18570}"
BOOTSTRAP_TAKEOFF_S="${BOOTSTRAP_TAKEOFF_S:-14.0}"
BOOTSTRAP_TARGET_ALTITUDE_M="${BOOTSTRAP_TARGET_ALTITUDE_M:-1.2}"

ODOM_TOPIC="${ODOM_TOPIC:-/mosim/planner/odom}"
CLOUD_TOPIC="${CLOUD_TOPIC:-/mosim/planner/global_points}"
EGO_LAUNCH="${EGO_LAUNCH:-mosim_gazebo_real_planner_gate.launch.py}"
EGO_GOAL_X="${EGO_GOAL_X:-2.0}"
EGO_GOAL_Y="${EGO_GOAL_Y:-0.0}"
EGO_GOAL_Z="${EGO_GOAL_Z:-1.2}"
TRAJ_SERVER_PATH_FOLLOW="${TRAJ_SERVER_PATH_FOLLOW:-true}"
TRAJ_SERVER_OUTPUT_SHAPING="${TRAJ_SERVER_OUTPUT_SHAPING:-true}"
TRAJ_SERVER_MAX_SPEED_MPS="${TRAJ_SERVER_MAX_SPEED_MPS:-0.8}"
TRAJ_SERVER_MAX_Z_SPEED_MPS="${TRAJ_SERVER_MAX_Z_SPEED_MPS:-0.5}"
POSITION_CMD_MIN_Z_M="${POSITION_CMD_MIN_Z_M:-0.0}"

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
gcs_pid=""
odom_bridge_pid=""
cloud_pid=""
bootstrap_pid=""
ego_pid=""
traj_server_pid=""
position_adapter_pid=""
setpoint_adapter_pid=""
px4_adapter_pid=""
flight_recorder_pid=""
ego_recorder_pid=""

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
  terminate_process_tree "${ego_recorder_pid}" 2
  terminate_process_tree "${flight_recorder_pid}" 2
  terminate_process_tree "${px4_adapter_pid}" 3
  terminate_process_tree "${bootstrap_pid}" 2
  terminate_process_tree "${setpoint_adapter_pid}" 3
  terminate_process_tree "${position_adapter_pid}" 3
  terminate_process_tree "${traj_server_pid}" 3
  terminate_process_tree "${ego_pid}" 4
  terminate_process_tree "${cloud_pid}" 2
  terminate_process_tree "${odom_bridge_pid}" 2
  terminate_process_tree "${gcs_pid}" 2
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

write_status() {
  local status="${1}"
  local message="${2}"
  python3 - "${RESULT_DIR}" "${status}" "${message}" <<'PY'
import json
import pathlib
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
payload = {
    "schema": "mosim.px4_same_run_ego_offboard_gate.v1",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "status": sys.argv[2],
    "message": sys.argv[3],
    "semantic_boundary": "same_run_ego_to_px4_offboard_no_direct_gazebo_actuator_control",
    "result_dir": str(result_dir),
}
(result_dir / "PX4_SAME_RUN_EGO_OFFBOARD_GATE.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(payload, ensure_ascii=False, indent=2))
PY
}

agent_cmd="$(find_agent_cmd || true)"
if [[ -z "${agent_cmd}" ]]; then
  write_status "blocked_missing_micro_xrce_agent" "Micro XRCE-DDS Agent was not found"
  exit 2
fi
if [[ ! -d "${PX4_DIR}" ]]; then
  write_status "blocked_missing_px4_dir" "PX4_DIR does not exist: ${PX4_DIR}"
  exit 2
fi

"${agent_cmd}" udp4 -p 8888 > "${RESULT_DIR}/xrce_agent.log" 2>&1 &
agent_pid="$!"
printf '%s\n' "${agent_pid}" > "${RESULT_DIR}/xrce_agent.pid"
sleep 2
if ! kill -0 "${agent_pid}" >/dev/null 2>&1; then
  write_status "blocked_xrce_agent_failed_to_start" "Micro XRCE-DDS Agent exited before PX4 start"
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
if [[ -f "${MOSIM_MSGS_SETUP}" ]]; then
  # shellcheck disable=SC1090
  source "${MOSIM_MSGS_SETUP}"
fi
if [[ -f "${SETPOINT_ADAPTER_SETUP}" && "${SETPOINT_ADAPTER_SETUP}" != "${MOSIM_MSGS_SETUP}" ]]; then
  # shellcheck disable=SC1090
  source "${SETPOINT_ADAPTER_SETUP}"
fi
if [[ -f "${PX4_ROS2_INSTALL}" ]]; then
  # shellcheck disable=SC1090
  source "${PX4_ROS2_INSTALL}"
fi
if [[ -f "${EGO_SETUP}" ]]; then
  # shellcheck disable=SC1090
  source "${EGO_SETUP}"
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
  ros2 pkg executables mosim_px4_offboard_adapter || true
  ros2 pkg executables mosim_setpoint_adapter || true
  ros2 pkg executables ego_planner || true
} > "${RESULT_DIR}/ros2_env.txt" 2>&1

deadline=$((SECONDS + TOPIC_WAIT_S))
vehicle_status_topic=""
local_position_topic=""
command_ack_topic=""
land_detected_topic=""
while [[ "${SECONDS}" -lt "${deadline}" ]]; do
  if ! kill -0 "${px4_pid}" >/dev/null 2>&1; then
    write_status "blocked_px4_exited_before_topics" "PX4 exited before required ROS2 topics appeared"
    exit 2
  fi
  timeout 12s ros2 topic list --no-daemon --spin-time 4 -t > "${RESULT_DIR}/ros2_topic_list.txt" 2> "${RESULT_DIR}/ros2_topic_list.err" || true
  vehicle_status_topic="$(awk '/^\/fmu\/out\/vehicle_status(_v[0-9]+)?([[:space:]]|$)/ {print $1; exit}' "${RESULT_DIR}/ros2_topic_list.txt" 2>/dev/null || true)"
  local_position_topic="$(awk '/^\/fmu\/out\/vehicle_local_position(_v[0-9]+)?([[:space:]]|$)/ {print $1; exit}' "${RESULT_DIR}/ros2_topic_list.txt" 2>/dev/null || true)"
  command_ack_topic="$(awk '/^\/fmu\/out\/vehicle_command_ack(_v[0-9]+)?([[:space:]]|$)/ {print $1; exit}' "${RESULT_DIR}/ros2_topic_list.txt" 2>/dev/null || true)"
  land_detected_topic="$(awk '/^\/fmu\/out\/vehicle_land_detected(_v[0-9]+)?([[:space:]]|$)/ {print $1; exit}' "${RESULT_DIR}/ros2_topic_list.txt" 2>/dev/null || true)"
  if [[ -n "${vehicle_status_topic}" && -n "${local_position_topic}" && -n "${command_ack_topic}" && -n "${land_detected_topic}" ]]; then
    break
  fi
  sleep 3
done

if [[ -z "${vehicle_status_topic}" || -z "${local_position_topic}" || -z "${command_ack_topic}" || -z "${land_detected_topic}" ]]; then
  write_status "blocked_missing_required_px4_topics" "Required PX4 output topics did not appear"
  exit 2
fi

cat > "${RESULT_DIR}/selected_topics.env" <<EOF
vehicle_status_topic=${vehicle_status_topic}
local_position_topic=${local_position_topic}
command_ack_topic=${command_ack_topic}
land_detected_topic=${land_detected_topic}
odom_topic=${ODOM_TOPIC}
cloud_topic=${CLOUD_TOPIC}
EOF

if [[ "${RUN_GCS_HEARTBEAT}" == "1" ]]; then
  python3 - "${RESULT_DIR}" "${GCS_HEARTBEAT_UDP_PORT}" <<'PY' > "${RESULT_DIR}/gcs_heartbeat.log" 2>&1 &
import json
import pathlib
import sys
import time

result_dir = pathlib.Path(sys.argv[1])
port = int(sys.argv[2])
from pymavlink import mavutil

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
    write_status "blocked_gcs_heartbeat_failed_to_start" "Headless GCS heartbeat process exited"
    exit 2
  fi
fi

python3 "${PROJECT_ROOT}/Scripts/ros/px4_local_position_to_planner_odom.py" \
  --input-topic "${local_position_topic}" \
  --odom-topic "${ODOM_TOPIC}" \
  --mirror-odom-topic /grid_map/odom \
  --map-frame map \
  --child-frame px4/base_link \
  --output-json "${RESULT_DIR}/px4_local_position_to_planner_odom.json" \
  --trace-jsonl "${RESULT_DIR}/px4_planner_odom_trace.jsonl" \
  > "${RESULT_DIR}/px4_local_position_to_planner_odom.stdout.log" \
  2> "${RESULT_DIR}/px4_local_position_to_planner_odom.stderr.log" &
odom_bridge_pid="$!"
printf '%s\n' "${odom_bridge_pid}" > "${RESULT_DIR}/odom_bridge.pid"

python3 "${PROJECT_ROOT}/Scripts/ros/publish_static_planner_cloud.py" \
  --topic "${CLOUD_TOPIC}" \
  --mirror-topic /uav1/global_points \
  --frame-id map \
  --rate-hz 5.0 \
  --ground-z -5.0 \
  --obstacle 4.0,0.0,0.2,0.25,1.8 \
  --output-json "${RESULT_DIR}/static_planner_cloud.json" \
  > "${RESULT_DIR}/static_planner_cloud.stdout.log" \
  2> "${RESULT_DIR}/static_planner_cloud.stderr.log" &
cloud_pid="$!"
printf '%s\n' "${cloud_pid}" > "${RESULT_DIR}/static_cloud.pid"

sleep 4
if ! kill -0 "${odom_bridge_pid}" >/dev/null 2>&1; then
  write_status "blocked_odom_bridge_failed_to_start" "PX4 local-position to planner odom bridge exited"
  exit 2
fi
if ! kill -0 "${cloud_pid}" >/dev/null 2>&1; then
  write_status "blocked_static_cloud_failed_to_start" "Static planner cloud publisher exited"
  exit 2
fi

ros2 run mosim_px4_offboard_adapter planner_setpoint_to_px4_offboard_node \
  --ros-args \
  -p input_topic:=/mosim/planner/setpoint \
  -p auto_arm:=true \
  -p auto_offboard:=true \
  -p frame_mode:=enu_to_ned \
  -p expected_frame:=map \
  -p publish_rate_hz:="${PUBLISH_RATE_HZ}" \
  -p stale_timeout_s:="${STALE_TIMEOUT_S}" \
  -p warmup_setpoint_count:="${WARMUP_SETPOINT_COUNT}" \
  > "${RESULT_DIR}/px4_offboard_adapter.stdout.log" \
  2> "${RESULT_DIR}/px4_offboard_adapter.stderr.log" &
px4_adapter_pid="$!"
printf '%s\n' "${px4_adapter_pid}" > "${RESULT_DIR}/px4_adapter.pid"
sleep 2
if ! kill -0 "${px4_adapter_pid}" >/dev/null 2>&1; then
  write_status "blocked_px4_adapter_failed_to_start" "PX4 Offboard adapter exited during bootstrap"
  exit 2
fi

python3 - "${RESULT_DIR}" "${BOOTSTRAP_TAKEOFF_S}" "${BOOTSTRAP_TARGET_ALTITUDE_M}" "${PUBLISH_RATE_HZ}" <<'PY' > "${RESULT_DIR}/bootstrap_takeoff_setpoints.stdout.log" 2> "${RESULT_DIR}/bootstrap_takeoff_setpoints.stderr.log" &
import json
import pathlib
import sys
import time
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
duration_s = float(sys.argv[2])
target_altitude = float(sys.argv[3])
rate_hz = float(sys.argv[4])

import rclpy
from mosim_msgs.msg import PlannerSetpoint

def smoothstep(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3.0 - 2.0 * u)

rclpy.init()
node = rclpy.create_node("mosim_px4_same_run_ego_bootstrap_takeoff")
publisher = node.create_publisher(PlannerSetpoint, "/mosim/planner/setpoint", 10)
trace = (result_dir / "bootstrap_takeoff_setpoint_trace.jsonl").open("w", encoding="utf-8")
dt = 1.0 / rate_hz
takeoff_s = min(max(6.0, duration_s * 0.6), duration_s)
start = time.monotonic()
sequence = 1
try:
    while rclpy.ok() and time.monotonic() - start < duration_s:
        elapsed = time.monotonic() - start
        u = min(1.0, elapsed / takeoff_s)
        z = target_altitude * smoothstep(u)
        msg = PlannerSetpoint()
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.header.frame_id = "map"
        msg.sequence = sequence
        msg.frame_id = "map"
        msg.position_m = [0.0, 0.0, float(z)]
        msg.velocity_mps = [0.0, 0.0, 0.0]
        msg.acceleration_mps2 = [0.0, 0.0, 0.0]
        msg.yaw_rad = 0.0
        msg.yaw_rate_radps = 0.0
        msg.trajectory_status = 1
        msg.planner_id = "px4_same_run_ego_bootstrap_takeoff"
        publisher.publish(msg)
        trace.write(json.dumps({
            "wall_time_utc": datetime.now(timezone.utc).isoformat(),
            "elapsed_s": elapsed,
            "sequence": sequence,
            "phase": "bootstrap_takeoff" if u < 1.0 else "bootstrap_hover",
            "position_m": [0.0, 0.0, z],
        }, ensure_ascii=False, separators=(",", ":")) + "\n")
        trace.flush()
        sequence += 1
        rclpy.spin_once(node, timeout_sec=0.0)
        time.sleep(dt)
finally:
    trace.close()
    node.destroy_node()
    rclpy.shutdown()
PY
bootstrap_pid="$!"
printf '%s\n' "${bootstrap_pid}" > "${RESULT_DIR}/bootstrap_takeoff.pid"
if wait "${bootstrap_pid}"; then
  printf '0\n' > "${RESULT_DIR}/bootstrap_takeoff.rc"
else
  printf '%s\n' "$?" > "${RESULT_DIR}/bootstrap_takeoff.rc"
  write_status "blocked_bootstrap_takeoff_failed" "Bootstrap takeoff setpoint publisher failed"
  exit 2
fi
bootstrap_pid=""
sleep 1

ros2 launch ego_planner "${EGO_LAUNCH}" \
  odom_topic:="${ODOM_TOPIC}" \
  cloud_topic:="${CLOUD_TOPIC}" \
  > "${RESULT_DIR}/ego_planner.stdout.log" \
  2> "${RESULT_DIR}/ego_planner.stderr.log" &
ego_pid="$!"
printf '%s\n' "${ego_pid}" > "${RESULT_DIR}/ego_planner.pid"

ros2 run ego_planner traj_server_ros2_node \
  --ros-args \
  -p publish_enabled:=true \
  -p output_topic:=/position_cmd \
  -p bspline_topic:=/planning/bspline \
  -p odom_topic:="${ODOM_TOPIC}" \
  -p command_rate_hz:="${PUBLISH_RATE_HZ}" \
  -p path_follow_mode:="${TRAJ_SERVER_PATH_FOLLOW}" \
  -p output_shaping_enabled:="${TRAJ_SERVER_OUTPUT_SHAPING}" \
  -p output_max_speed_mps:="${TRAJ_SERVER_MAX_SPEED_MPS}" \
  -p output_max_z_speed_mps:="${TRAJ_SERVER_MAX_Z_SPEED_MPS}" \
  > "${RESULT_DIR}/traj_server.stdout.log" \
  2> "${RESULT_DIR}/traj_server.stderr.log" &
traj_server_pid="$!"
printf '%s\n' "${traj_server_pid}" > "${RESULT_DIR}/traj_server.pid"

ros2 run mosim_setpoint_adapter position_command_to_planner_setpoint_node \
  --ros-args \
  -p input_topic:=/position_cmd \
  -p output_topic:=/mosim/planner/position_cmd \
  -p expected_frame:=map \
  -p source_frame_alias:=world \
  -p min_position_z_m:="${POSITION_CMD_MIN_Z_M}" \
  > "${RESULT_DIR}/position_command_to_planner_setpoint.stdout.log" \
  2> "${RESULT_DIR}/position_command_to_planner_setpoint.stderr.log" &
position_adapter_pid="$!"
printf '%s\n' "${position_adapter_pid}" > "${RESULT_DIR}/position_adapter.pid"

ros2 run mosim_setpoint_adapter planner_setpoint_adapter_node \
  --ros-args \
  -p input_topic:=/mosim/planner/position_cmd \
  -p output_topic:=/mosim/planner/setpoint \
  -p status_topic:=/mosim/planner/setpoint_adapter_status \
  -p expected_frame:=map \
  -p rate_hz:="${PUBLISH_RATE_HZ}" \
  -p stale_timeout_s:=0.20 \
  > "${RESULT_DIR}/planner_setpoint_adapter.stdout.log" \
  2> "${RESULT_DIR}/planner_setpoint_adapter.stderr.log" &
setpoint_adapter_pid="$!"
printf '%s\n' "${setpoint_adapter_pid}" > "${RESULT_DIR}/setpoint_adapter.pid"

sleep 5
for pair in \
  "ego_planner:${ego_pid}" \
  "traj_server:${traj_server_pid}" \
  "position_adapter:${position_adapter_pid}" \
  "setpoint_adapter:${setpoint_adapter_pid}" \
  "px4_adapter:${px4_adapter_pid}"; do
  name="${pair%%:*}"
  pid="${pair#*:}"
  if ! kill -0 "${pid}" >/dev/null 2>&1; then
    write_status "blocked_${name}_failed_to_start" "${name} process exited"
    exit 2
  fi
done

python3 - "${RESULT_DIR}" "${vehicle_status_topic}" "${local_position_topic}" "${command_ack_topic}" "${land_detected_topic}" "${RECORD_DURATION_S}" <<'PY' &
import json
import pathlib
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
vehicle_status_topic, local_position_topic, command_ack_topic, land_detected_topic = sys.argv[2:6]
record_duration_s = float(sys.argv[6])

import rclpy
from px4_msgs.msg import VehicleCommandAck, VehicleLandDetected, VehicleLocalPosition, VehicleStatus

def scrub_message(msg):
    if isinstance(msg, VehicleStatus):
        return {
            "recorded_wall_time_utc": datetime.now(timezone.utc).isoformat(),
            "timestamp_us": int(msg.timestamp),
            "arming_state": int(msg.arming_state),
            "nav_state": int(msg.nav_state),
            "failsafe": bool(msg.failsafe),
            "accepts_offboard_setpoints": bool(msg.accepts_offboard_setpoints),
            "pre_flight_checks_pass": bool(msg.pre_flight_checks_pass),
        }
    if isinstance(msg, VehicleLocalPosition):
        return {
            "recorded_wall_time_utc": datetime.now(timezone.utc).isoformat(),
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
            "recorded_wall_time_utc": datetime.now(timezone.utc).isoformat(),
            "timestamp_us": int(msg.timestamp),
            "command": int(msg.command),
            "result": int(msg.result),
            "from_external": bool(msg.from_external),
        }
    if isinstance(msg, VehicleLandDetected):
        fields = {"recorded_wall_time_utc": datetime.now(timezone.utc).isoformat(), "timestamp_us": int(msg.timestamp)}
        for name in ("landed", "maybe_landed", "ground_contact", "freefall"):
            if hasattr(msg, name):
                fields[name] = bool(getattr(msg, name))
        return fields
    return {}

rclpy.init()
node = rclpy.create_node("mosim_px4_same_run_ego_flight_recorder")
qos = rclpy.qos.QoSProfile(depth=200, reliability=rclpy.qos.ReliabilityPolicy.BEST_EFFORT)
files = {
    "vehicle_status": result_dir / "vehicle_status.jsonl",
    "local_position": result_dir / "vehicle_local_position.jsonl",
    "command_ack": result_dir / "vehicle_command_ack.jsonl",
    "land_detected": result_dir / "vehicle_land_detected.jsonl",
}
handles = {key: path.open("w", encoding="utf-8") for key, path in files.items()}

def make_cb(key):
    def callback(msg):
        handles[key].write(json.dumps(scrub_message(msg), ensure_ascii=False, separators=(",", ":")) + "\n")
        handles[key].flush()
    return callback

node.create_subscription(VehicleStatus, vehicle_status_topic, make_cb("vehicle_status"), qos)
node.create_subscription(VehicleLocalPosition, local_position_topic, make_cb("local_position"), qos)
node.create_subscription(VehicleCommandAck, command_ack_topic, make_cb("command_ack"), qos)
node.create_subscription(VehicleLandDetected, land_detected_topic, make_cb("land_detected"), qos)
deadline = node.get_clock().now().nanoseconds + int(10**9 * record_duration_s)
try:
    while rclpy.ok() and node.get_clock().now().nanoseconds < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)
finally:
    for handle in handles.values():
        handle.close()
    node.destroy_node()
    rclpy.shutdown()
PY
flight_recorder_pid="$!"
printf '%s\n' "${flight_recorder_pid}" > "${RESULT_DIR}/flight_recorder.pid"

python3 "${PROJECT_ROOT}/Scripts/ros/record_real_ego_rviz_review_topics.py" \
  --output-json "${RESULT_DIR}/same_run_ego_topic_recorder.json" \
  --duration-seconds "${RECORD_DURATION_S}" \
  --raw-lidar-topic "${CLOUD_TOPIC}" \
  --planner-cloud-topic "${CLOUD_TOPIC}" \
  --review-cloud-topic "${CLOUD_TOPIC}" \
  --review-accumulated-cloud-topic "${CLOUD_TOPIC}" \
  --position-command-trace-jsonl "${RESULT_DIR}/position_cmd.trace.jsonl" \
  --planner-setpoint-trace-jsonl "${RESULT_DIR}/planner_setpoint.trace.jsonl" \
  --controller-output-trace-jsonl "${RESULT_DIR}/controller_output.trace.jsonl" \
  --skip-ego-topics \
  > "${RESULT_DIR}/same_run_ego_topic_recorder.stdout.log" \
  2> "${RESULT_DIR}/same_run_ego_topic_recorder.stderr.log" &
ego_recorder_pid="$!"
printf '%s\n' "${ego_recorder_pid}" > "${RESULT_DIR}/ego_recorder.pid"

sleep "${RUN_DURATION_S}"

if wait "${flight_recorder_pid}"; then
  printf '0\n' > "${RESULT_DIR}/flight_recorder.rc"
else
  printf '%s\n' "$?" > "${RESULT_DIR}/flight_recorder.rc"
fi
if wait "${ego_recorder_pid}"; then
  printf '0\n' > "${RESULT_DIR}/ego_recorder.rc"
else
  printf '%s\n' "$?" > "${RESULT_DIR}/ego_recorder.rc"
fi

ros2 topic list > "${RESULT_DIR}/ros2_topic_list_final.txt" 2> "${RESULT_DIR}/ros2_topic_list_final.err" || true

terminate_process_tree "${px4_adapter_pid}" 3
px4_adapter_pid=""
terminate_process_tree "${setpoint_adapter_pid}" 3
setpoint_adapter_pid=""
terminate_process_tree "${position_adapter_pid}" 3
position_adapter_pid=""
terminate_process_tree "${traj_server_pid}" 3
traj_server_pid=""
terminate_process_tree "${ego_pid}" 4
ego_pid=""
terminate_process_tree "${cloud_pid}" 2
cloud_pid=""
terminate_process_tree "${odom_bridge_pid}" 2
odom_bridge_pid=""

python3 - "${RESULT_DIR}" "${EGO_GOAL_X}" "${EGO_GOAL_Y}" "${EGO_GOAL_Z}" <<'PY'
import json
import math
import pathlib
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
goal = [float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])]

def read_jsonl(path):
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return rows

def parse_wall_time(value):
    if not value:
        return math.nan
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except Exception:
        return math.nan

def ned_to_enu(row):
    return {
        "wall_ts_s": parse_wall_time(row.get("recorded_wall_time_utc")),
        "timestamp_us": int(row.get("timestamp_us", 0) or 0),
        "x": float(row.get("y", math.nan)),
        "y": float(row.get("x", math.nan)),
        "z": -float(row.get("z", math.nan)),
        "vx": float(row.get("vy", math.nan)),
        "vy": float(row.get("vx", math.nan)),
        "vz": -float(row.get("vz", math.nan)),
        "heading": float(row.get("heading", math.nan)),
        "valid": bool(row.get("xy_valid")) and bool(row.get("z_valid")),
    }

local = [ned_to_enu(row) for row in read_jsonl(result_dir / "vehicle_local_position.jsonl")]
local = [row for row in local if row["valid"] and math.isfinite(row["x"]) and math.isfinite(row["y"]) and math.isfinite(row["z"])]
status_rows = read_jsonl(result_dir / "vehicle_status.jsonl")
ack_rows = read_jsonl(result_dir / "vehicle_command_ack.jsonl")
land_rows = read_jsonl(result_dir / "vehicle_land_detected.jsonl")
setpoints = read_jsonl(result_dir / "planner_setpoint.trace.jsonl")
position_cmd = read_jsonl(result_dir / "position_cmd.trace.jsonl")
ego_report = {}
ego_report_path = result_dir / "same_run_ego_topic_recorder.json"
if ego_report_path.exists():
    try:
        ego_report = json.loads(ego_report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        ego_report = {}
ego_log = ""
for name in ("ego_planner.stdout.log", "ego_planner.stderr.log"):
    path = result_dir / name
    if path.exists():
        ego_log += path.read_text(encoding="utf-8", errors="replace")[-200000:] + "\n"

first_ts = local[0]["timestamp_us"] if local else 0
for row in local:
    row["t_s"] = (row["timestamp_us"] - first_ts) / 1e6 if first_ts else 0.0

positions_with_time = [row for row in local if math.isfinite(row["wall_ts_s"])]
position_wall_times = [row["wall_ts_s"] for row in positions_with_time]
setpoints_with_time = [row for row in setpoints if math.isfinite(parse_wall_time((row.get("stamp") or {}).get("iso") if isinstance(row.get("stamp"), dict) else None))]

# record_real_ego_rviz_review_topics stores ROS stamp, not wall time. Use latest
# sample metrics for command counts and evaluate coarse flight motion in this
# first same-run gate.
duration_s = local[-1]["t_s"] if local else 0.0
max_altitude = max((row["z"] for row in local), default=math.nan)
final_position = [local[-1]["x"], local[-1]["y"], local[-1]["z"]] if local else [math.nan, math.nan, math.nan]
max_xy = max((math.hypot(row["x"], row["y"]) for row in local), default=math.nan)
goal_distance_final = math.dist(final_position, goal) if all(math.isfinite(v) for v in final_position) else math.nan
goal_xy_distance_final = math.hypot(final_position[0] - goal[0], final_position[1] - goal[1]) if all(math.isfinite(v) for v in final_position[:2]) else math.nan
max_x = max((row["x"] for row in local), default=math.nan)
min_x = min((row["x"] for row in local), default=math.nan)
max_y = max((row["y"] for row in local), default=math.nan)
min_y = min((row["y"] for row in local), default=math.nan)
xy_span = math.hypot(max_x - min_x, max_y - min_y) if all(math.isfinite(v) for v in (max_x, min_x, max_y, min_y)) else math.nan
z_span = max_altitude - min((row["z"] for row in local), default=math.nan) if math.isfinite(max_altitude) else math.nan

nav_states = sorted({row.get("nav_state") for row in status_rows if row.get("nav_state") is not None})
arming_states = sorted({row.get("arming_state") for row in status_rows if row.get("arming_state") is not None})
offboard_seen = any(row.get("nav_state") == 14 for row in status_rows)
armed_seen = any(row.get("arming_state") == 2 for row in status_rows)
failsafe_seen = any(row.get("failsafe") for row in status_rows)
landed_seen = any(row.get("landed") for row in land_rows)

message_counts = ego_report.get("message_counts", {}) if isinstance(ego_report, dict) else {}
command_counts = ego_report.get("command_message_counts", {}) if isinstance(ego_report, dict) else {}
samples = ego_report.get("samples", {}) if isinstance(ego_report, dict) else {}
planner_cloud_finite = int(samples.get("planner_cloud_map_frame", {}).get("finite_point_count", 0) or 0) if isinstance(samples, dict) else 0
bspline_count = int(message_counts.get("ego_global", 0) or 0) + int(message_counts.get("ego_optimal", 0) or 0)

checks = {
    "has_local_position_samples": len(local) >= 100,
    "has_status_samples": len(status_rows) >= 10,
    "ego_recorder_ready_or_partial": (ego_report.get("status") in {"ready", "blocked"}) if isinstance(ego_report, dict) else False,
    "planner_cloud_sampled": planner_cloud_finite > 0,
    "position_cmd_published": int(command_counts.get("position_cmd", 0) or 0) >= 20,
    "planner_setpoint_published": int(command_counts.get("planner_setpoint", 0) or 0) >= 20,
    "offboard_seen": offboard_seen,
    "armed_seen": armed_seen,
    "failsafe_not_seen": not failsafe_seen,
    "vehicle_moved": math.isfinite(xy_span) and xy_span >= 0.5,
    "vehicle_climbed": math.isfinite(max_altitude) and max_altitude >= 0.7,
    "goal_xy_reached_loose": math.isfinite(goal_xy_distance_final) and goal_xy_distance_final <= 1.25,
    "ego_not_in_emergency_stop_loop": "drone is in obstacle" not in ego_log[-80000:],
}
blockers = [name for name, passed in checks.items() if not passed]

def clean(value):
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clean(item) for item in value]
    return value

payload = {
    "schema": "mosim.px4_same_run_ego_offboard_gate.v1",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "status": "passed_same_run_ego_to_px4_transport_flight" if not blockers else "blocked",
    "gate_passed": not blockers,
    "semantic_boundary": "same_run_ego_to_px4_offboard_no_direct_gazebo_actuator_control",
    "goal_m": goal,
    "counts": {
        "local_position": len(local),
        "vehicle_status": len(status_rows),
        "vehicle_command_ack": len(ack_rows),
        "vehicle_land_detected": len(land_rows),
        "position_cmd_trace": len(position_cmd),
        "planner_setpoint_trace": len(setpoints),
    },
    "ego_recorder": {
        "status": ego_report.get("status") if isinstance(ego_report, dict) else None,
        "message_counts": message_counts,
        "command_message_counts": command_counts,
        "measured_rates_hz": ego_report.get("measured_rates_hz", {}) if isinstance(ego_report, dict) else {},
        "command_rates_hz": ego_report.get("command_rates_hz", {}) if isinstance(ego_report, dict) else {},
        "blockers": ego_report.get("blockers", []) if isinstance(ego_report, dict) else [],
        "warnings": ego_report.get("warnings", []) if isinstance(ego_report, dict) else [],
        "planner_cloud_finite_points": planner_cloud_finite,
        "marker_count_proxy": bspline_count,
        "ego_log_markers": {
            "final_plan_success_true": "final_plan_success=1" in ego_log or "final_plan_success=true" in ego_log,
            "drone_in_obstacle": "drone is in obstacle" in ego_log,
            "emergency_stop": "EMERGENCY_STOP" in ego_log,
        },
    },
    "state": {
        "nav_states": nav_states,
        "arming_states": arming_states,
        "offboard_seen": offboard_seen,
        "armed_seen": armed_seen,
        "failsafe_seen": failsafe_seen,
        "landed_seen": landed_seen,
    },
    "metrics": {
        "duration_s": round(duration_s, 3),
        "max_altitude_m": max_altitude,
        "max_xy_distance_from_origin_m": max_xy,
        "xy_span_m": xy_span,
        "z_span_m": z_span,
        "final_position_m": final_position,
        "final_goal_distance_m": goal_distance_final,
        "final_goal_xy_distance_m": goal_xy_distance_final,
    },
    "checks": checks,
    "blockers": blockers,
    "claim_boundary": [
        "EGO, traj_server, PositionCommand adapter, PlannerSetpoint adapter, and PX4 Offboard adapter ran in the same ROS2/PX4 session.",
        "This first same-run gate uses a deterministic planner-cloud fixture; it is not MID360, FAST-LIO, or final obstacle-avoidance evidence.",
        "The gate does not write Gazebo actuator or motor topics directly.",
        "Passing proves same-run EGO-to-PX4 transport plus bounded PX4/Gazebo motion only; it does not certify generated MWORKS controller deployment or final competition controller performance.",
    ],
    "files": {
        "vehicle_local_position": str(result_dir / "vehicle_local_position.jsonl"),
        "vehicle_status": str(result_dir / "vehicle_status.jsonl"),
        "position_cmd_trace": str(result_dir / "position_cmd.trace.jsonl"),
        "planner_setpoint_trace": str(result_dir / "planner_setpoint.trace.jsonl"),
        "ego_topic_recorder": str(result_dir / "same_run_ego_topic_recorder.json"),
        "odom_bridge": str(result_dir / "px4_local_position_to_planner_odom.json"),
        "static_planner_cloud": str(result_dir / "static_planner_cloud.json"),
        "px4_log": str(result_dir / "px4_gz_x500.log"),
    },
}
(result_dir / "PX4_SAME_RUN_EGO_OFFBOARD_GATE.json").write_text(
    json.dumps(clean(payload), ensure_ascii=False, indent=2, allow_nan=False) + "\n",
    encoding="utf-8",
)
print(json.dumps(clean(payload), ensure_ascii=False, indent=2, allow_nan=False))
PY

status="$(python3 -c "import json; print(json.load(open('${RESULT_DIR}/PX4_SAME_RUN_EGO_OFFBOARD_GATE.json', encoding='utf-8')).get('status','unknown'))")"
if [[ "${status}" != "passed_same_run_ego_to_px4_transport_flight" ]]; then
  exit 2
fi
