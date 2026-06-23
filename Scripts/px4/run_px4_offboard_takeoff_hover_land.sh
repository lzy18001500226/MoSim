#!/usr/bin/env bash
# PX4-native Offboard takeoff-hover-land gate.
#
# Scope:
# - Starts Micro XRCE-DDS Agent and official PX4 SITL Gazebo x500 target.
# - Starts the MoSim PX4 Offboard adapter with auto_offboard=true and auto_arm=true.
# - Publishes a continuous PlannerSetpoint trajectory: takeoff, hover, land.
# - Records PX4 status/position/ack topics and evaluates flight quality.
# - Does not write Gazebo motor/actuator topics directly.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
PX4_DIR="${PX4_DIR:-${PROJECT_ROOT}/Results/tmp/px4_gitwork/PX4}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/px4_gazebo/px4_offboard_takeoff_hover_land_$(date +%Y%m%d_%H%M%S)}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
PX4_ROS2_INSTALL="${PX4_ROS2_INSTALL:-${PROJECT_ROOT}/Results/ros2_build/px4_offboard_adapter_20260620_rebuild/install/setup.bash}"
STARTUP_TIMEOUT_S="${STARTUP_TIMEOUT_S:-360}"
TOPIC_WAIT_S="${TOPIC_WAIT_S:-150}"
HEADLESS="${HEADLESS:-1}"
PX4_SIM_SPEED_FACTOR="${PX4_SIM_SPEED_FACTOR:-1}"
SANITIZE_WSL_PATH="${SANITIZE_WSL_PATH:-1}"
ROS_LOG_DIR="${ROS_LOG_DIR:-${PROJECT_ROOT}/Results/tmp/ros_logs/px4_offboard_takeoff_hover_land}"

TARGET_ALTITUDE_M="${TARGET_ALTITUDE_M:-1.2}"
TAKEOFF_S="${TAKEOFF_S:-8.0}"
HOVER_S="${HOVER_S:-10.0}"
LAND_S="${LAND_S:-8.0}"
POST_LAND_S="${POST_LAND_S:-4.0}"
PUBLISH_RATE_HZ="${PUBLISH_RATE_HZ:-20.0}"
WARMUP_SETPOINT_COUNT="${WARMUP_SETPOINT_COUNT:-30}"
STALE_TIMEOUT_S="${STALE_TIMEOUT_S:-1.0}"
RUN_GCS_HEARTBEAT="${RUN_GCS_HEARTBEAT:-1}"
GCS_HEARTBEAT_UDP_PORT="${GCS_HEARTBEAT_UDP_PORT:-18570}"

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
    "schema": "mosim.px4_offboard_takeoff_hover_land.v1",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "status": sys.argv[2],
    "message": sys.argv[3],
    "semantic_boundary": "px4_native_offboard_takeoff_hover_land_no_direct_gazebo_actuator_control",
    "result_dir": str(result_dir),
}
(result_dir / "PX4_OFFBOARD_TAKEOFF_HOVER_LAND.json").write_text(
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
  if [[ -n "${vehicle_status_topic}" && -n "${local_position_topic}" && -n "${command_ack_topic}" && -n "${land_detected_topic}" ]]; then
    break
  fi
  sleep 3
done

if [[ -z "${vehicle_status_topic}" || -z "${local_position_topic}" || -z "${command_ack_topic}" || -z "${land_detected_topic}" ]]; then
  write_blocker "blocked_missing_required_topics" "Required PX4 output topics did not appear"
  exit 2
fi

cat > "${RESULT_DIR}/selected_topics.env" <<EOF
vehicle_status_topic=${vehicle_status_topic}
local_position_topic=${local_position_topic}
command_ack_topic=${command_ack_topic}
land_detected_topic=${land_detected_topic}
EOF

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

ros2 run mosim_px4_offboard_adapter planner_setpoint_to_px4_offboard_node \
  --ros-args \
  -p auto_arm:=true \
  -p auto_offboard:=true \
  -p frame_mode:=enu_to_ned \
  -p expected_frame:=map \
  -p publish_rate_hz:="${PUBLISH_RATE_HZ}" \
  -p stale_timeout_s:="${STALE_TIMEOUT_S}" \
  -p warmup_setpoint_count:="${WARMUP_SETPOINT_COUNT}" \
  > "${RESULT_DIR}/adapter.log" 2>&1 &
adapter_pid="$!"
printf '%s\n' "${adapter_pid}" > "${RESULT_DIR}/adapter.pid"
sleep 2
if ! kill -0 "${adapter_pid}" >/dev/null 2>&1; then
  write_blocker "blocked_adapter_failed_to_start" "MoSim PX4 Offboard adapter exited"
  exit 2
fi

python3 - "${RESULT_DIR}" "${vehicle_status_topic}" "${local_position_topic}" "${command_ack_topic}" "${land_detected_topic}" <<'PY' &
import json
import pathlib
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
vehicle_status_topic, local_position_topic, command_ack_topic, land_detected_topic = sys.argv[2:6]

try:
    import rclpy
    from px4_msgs.msg import VehicleCommandAck, VehicleLandDetected, VehicleLocalPosition, VehicleStatus
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
    if isinstance(msg, VehicleLandDetected):
        fields = {"timestamp_us": int(msg.timestamp)}
        for name in ("landed", "maybe_landed", "ground_contact", "freefall"):
            if hasattr(msg, name):
                fields[name] = bool(getattr(msg, name))
        return fields
    return {}

rclpy.init()
node = rclpy.create_node("mosim_px4_offboard_takeoff_hover_land_recorder")
paths = {
    "vehicle_status": result_dir / "vehicle_status.jsonl",
    "local_position": result_dir / "vehicle_local_position.jsonl",
    "command_ack": result_dir / "vehicle_command_ack.jsonl",
    "land_detected": result_dir / "vehicle_land_detected.jsonl",
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
node = rclpy.create_node("mosim_px4_offboard_takeoff_hover_land_setpoint_publisher")
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
        msg.planner_id = "px4_native_takeoff_hover_land_gate"
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

python3 - "${RESULT_DIR}" "${TARGET_ALTITUDE_M}" <<'PY'
import json
import math
import pathlib
import statistics
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
target_altitude = float(sys.argv[2])

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
}

status = "passed" if all(checks.values()) else "failed_metrics"
payload = {
    "schema": "mosim.px4_offboard_takeoff_hover_land.v1",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "status": status,
    "semantic_boundary": "px4_native_offboard_takeoff_hover_land_no_direct_gazebo_actuator_control",
    "result_dir": str(result_dir),
    "inputs": {
        "target_altitude_m": target_altitude,
        "source": "continuous PlannerSetpoint via MoSim PX4 Offboard adapter",
        "headless_gcs_heartbeat": (result_dir / "gcs_heartbeat_manifest.json").exists(),
    },
    "counts": {
        "planner_setpoints": len(setpoint_rows),
        "local_position": len(local_rows),
        "vehicle_status": len(status_rows),
        "command_ack": len(ack_rows),
        "land_detected": len(land_rows),
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
    },
    "checks": checks,
    "claim_boundary": [
        "This is a PX4-native Offboard takeoff-hover-land gate.",
        "It does not write Gazebo actuator or motor topics directly.",
        "Passing this gate proves baseline PX4/Gazebo Offboard flight quality only, not generated MWORKS controller deployment.",
    ],
    "files": {
        "planner_setpoint_trace": str(result_dir / "planner_setpoint_trace.jsonl"),
        "vehicle_local_position": str(result_dir / "vehicle_local_position.jsonl"),
        "vehicle_status": str(result_dir / "vehicle_status.jsonl"),
        "vehicle_command_ack": str(result_dir / "vehicle_command_ack.jsonl"),
        "vehicle_land_detected": str(result_dir / "vehicle_land_detected.jsonl"),
        "adapter_log": str(result_dir / "adapter.log"),
        "px4_log": str(result_dir / "px4_gz_x500.log"),
    },
}
(result_dir / "PX4_OFFBOARD_TAKEOFF_HOVER_LAND.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False, indent=2))
PY

status="$(python3 -c "import json,sys; print(json.load(open('${RESULT_DIR}/PX4_OFFBOARD_TAKEOFF_HOVER_LAND.json', encoding='utf-8')).get('status','unknown'))")"
if [[ "${status}" != "passed" ]]; then
  exit 2
fi
