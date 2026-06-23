#!/usr/bin/env bash
# PX4-native Offboard replay gate for a recorded MoSim PlannerSetpoint trace.
#
# Scope:
# - Starts Micro XRCE-DDS Agent and official PX4 SITL Gazebo x500 target.
# - Starts the MoSim PX4 Offboard adapter with auto_offboard=true and auto_arm=true.
# - Replays a recorded PlannerSetpoint JSONL trace onto /mosim/planner/setpoint.
# - Records PX4 status/position/ack topics and evaluates flight quality.
# - Does not write Gazebo motor/actuator topics directly.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
PX4_DIR="${PX4_DIR:-${PROJECT_ROOT}/Results/tmp/px4_gitwork/PX4}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/px4_gazebo/px4_offboard_replay_trace_$(date +%Y%m%d_%H%M%S)}"
TRACE_JSONL="${TRACE_JSONL:?TRACE_JSONL is required}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
PX4_ROS2_INSTALL="${PX4_ROS2_INSTALL:-${PROJECT_ROOT}/Results/ros2_build/px4_offboard_adapter_20260620_rebuild/install/setup.bash}"
STARTUP_TIMEOUT_S="${STARTUP_TIMEOUT_S:-360}"
TOPIC_WAIT_S="${TOPIC_WAIT_S:-150}"
HEADLESS="${HEADLESS:-1}"
PX4_SIM_SPEED_FACTOR="${PX4_SIM_SPEED_FACTOR:-1}"
SANITIZE_WSL_PATH="${SANITIZE_WSL_PATH:-1}"
ROS_LOG_DIR="${ROS_LOG_DIR:-${PROJECT_ROOT}/Results/tmp/ros_logs/px4_offboard_replay_trace}"

REPLAY_RATE_LIMIT_HZ="${REPLAY_RATE_LIMIT_HZ:-20.0}"
REPLAY_RATE_LIMIT_HZ="$(python3 - "${REPLAY_RATE_LIMIT_HZ}" <<'PY'
import sys
print(f"{float(sys.argv[1]):.6f}")
PY
)"
REPLAY_TIME_SCALE="${REPLAY_TIME_SCALE:-1.0}"
REPLAY_FORCE_FRAME_ID="${REPLAY_FORCE_FRAME_ID:-map}"
REPLAY_FORCE_ALTITUDE_M="${REPLAY_FORCE_ALTITUDE_M:-}"
REPLAY_PREPEND_TAKEOFF_S="${REPLAY_PREPEND_TAKEOFF_S:-8.0}"
REPLAY_APPEND_LAND_S="${REPLAY_APPEND_LAND_S:-8.0}"
REPLAY_POST_LAND_S="${REPLAY_POST_LAND_S:-4.0}"
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

write_status() {
  local status="${1}"
  local message="${2}"
  python3 - "${RESULT_DIR}" "${status}" "${message}" "${TRACE_JSONL}" <<'PY'
import json
import pathlib
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
payload = {
    "schema": "mosim.px4_offboard_replay_planner_setpoint_trace.v1",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "status": sys.argv[2],
    "message": sys.argv[3],
    "semantic_boundary": "px4_native_offboard_replay_no_direct_gazebo_actuator_control",
    "trace_jsonl": sys.argv[4],
    "result_dir": str(result_dir),
}
(result_dir / "PX4_OFFBOARD_REPLAY_TRACE_GATE.json").write_text(
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
if [[ ! -f "${TRACE_JSONL}" ]]; then
  write_status "blocked_missing_trace" "TRACE_JSONL does not exist: ${TRACE_JSONL}"
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
  write_status "blocked_missing_required_topics" "Required PX4 output topics did not appear"
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

ros2 run mosim_px4_offboard_adapter planner_setpoint_to_px4_offboard_node \
  --ros-args \
  -p auto_arm:=true \
  -p auto_offboard:=true \
  -p frame_mode:=enu_to_ned \
  -p expected_frame:=map \
  -p publish_rate_hz:="${REPLAY_RATE_LIMIT_HZ}" \
  -p stale_timeout_s:="${STALE_TIMEOUT_S}" \
  -p warmup_setpoint_count:="${WARMUP_SETPOINT_COUNT}" \
  > "${RESULT_DIR}/adapter.log" 2>&1 &
adapter_pid="$!"
printf '%s\n' "${adapter_pid}" > "${RESULT_DIR}/adapter.pid"
sleep 2
if ! kill -0 "${adapter_pid}" >/dev/null 2>&1; then
  write_status "blocked_adapter_failed_to_start" "MoSim PX4 Offboard adapter exited"
  exit 2
fi

python3 - "${RESULT_DIR}" "${vehicle_status_topic}" "${local_position_topic}" "${command_ack_topic}" "${land_detected_topic}" <<'PY' &
import json
import pathlib
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
vehicle_status_topic, local_position_topic, command_ack_topic, land_detected_topic = sys.argv[2:6]

import rclpy
from px4_msgs.msg import VehicleCommandAck, VehicleLandDetected, VehicleLocalPosition, VehicleStatus

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
node = rclpy.create_node("mosim_px4_offboard_replay_trace_recorder")
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

python3 - "${RESULT_DIR}" "${TRACE_JSONL}" "${REPLAY_RATE_LIMIT_HZ}" "${REPLAY_TIME_SCALE}" "${REPLAY_FORCE_FRAME_ID}" "${REPLAY_FORCE_ALTITUDE_M}" "${REPLAY_PREPEND_TAKEOFF_S}" "${REPLAY_APPEND_LAND_S}" "${REPLAY_POST_LAND_S}" <<'PY' > "${RESULT_DIR}/planner_setpoint_replay.log" 2>&1 &
import json
import math
import pathlib
import sys
import time
from datetime import datetime, timezone

import rclpy
from mosim_msgs.msg import PlannerSetpoint

result_dir = pathlib.Path(sys.argv[1])
trace_path = pathlib.Path(sys.argv[2])
rate_hz = float(sys.argv[3])
time_scale = float(sys.argv[4])
force_frame = sys.argv[5]
force_alt_raw = sys.argv[6]
prepend_takeoff_s = float(sys.argv[7])
append_land_s = float(sys.argv[8])
post_land_s = float(sys.argv[9])
force_altitude = float(force_alt_raw) if force_alt_raw.strip() else None

def finite_xyz(raw):
    if not isinstance(raw, list) or len(raw) != 3:
        return None
    try:
        values = [float(raw[0]), float(raw[1]), float(raw[2])]
    except Exception:
        return None
    return values if all(math.isfinite(item) for item in values) else None

rows = []
for line in trace_path.read_text(encoding="utf-8", errors="replace").splitlines():
    if not line.strip():
        continue
    try:
        row = json.loads(line)
    except json.JSONDecodeError:
        continue
    pos = finite_xyz(row.get("position_m"))
    if pos is None:
        continue
    vel = finite_xyz(row.get("velocity_mps")) or [0.0, 0.0, 0.0]
    acc = finite_xyz(row.get("acceleration_mps2")) or [0.0, 0.0, 0.0]
    if force_altitude is not None:
        pos[2] = force_altitude
        vel[2] = 0.0
        acc[2] = 0.0
    rows.append({
        "position_m": pos,
        "velocity_mps": vel,
        "acceleration_mps2": acc,
        "yaw_rad": float(row.get("yaw_rad", 0.0) or 0.0),
        "yaw_rate_radps": float(row.get("yaw_rate_radps", 0.0) or 0.0),
        "frame_id": force_frame or str(row.get("frame_id", "map") or "map"),
        "planner_id": str(row.get("planner_id", "recorded_trace") or "recorded_trace"),
    })

if not rows:
    raise SystemExit(f"no finite PlannerSetpoint rows found in {trace_path}")

target_altitude = rows[0]["position_m"][2]
dt = 1.0 / max(rate_hz, 1.0)
publish_rows = []

def smoothstep(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3.0 - 2.0 * u)

takeoff_steps = int(max(prepend_takeoff_s, 0.0) * rate_hz)
for idx in range(takeoff_steps):
    u = (idx + 1) / max(takeoff_steps, 1)
    z = target_altitude * smoothstep(u)
    zdot = target_altitude * (6.0 * u * (1.0 - u)) / max(prepend_takeoff_s, dt)
    publish_rows.append({
        "phase": "takeoff",
        "position_m": [0.0, 0.0, z],
        "velocity_mps": [0.0, 0.0, zdot],
        "acceleration_mps2": [0.0, 0.0, 0.0],
        "yaw_rad": 0.0,
        "yaw_rate_radps": 0.0,
        "frame_id": force_frame or "map",
        "planner_id": "trace_replay_takeoff",
    })

for row in rows:
    item = dict(row)
    item["phase"] = "trace"
    publish_rows.append(item)

land_steps = int(max(append_land_s, 0.0) * rate_hz)
land_start_xy = publish_rows[-1]["position_m"][:2]
land_start_z = publish_rows[-1]["position_m"][2]
for idx in range(land_steps):
    u = (idx + 1) / max(land_steps, 1)
    z = land_start_z * (1.0 - smoothstep(u))
    zdot = -land_start_z * (6.0 * u * (1.0 - u)) / max(append_land_s, dt)
    publish_rows.append({
        "phase": "land",
        "position_m": [land_start_xy[0], land_start_xy[1], z],
        "velocity_mps": [0.0, 0.0, zdot],
        "acceleration_mps2": [0.0, 0.0, 0.0],
        "yaw_rad": publish_rows[-1]["yaw_rad"],
        "yaw_rate_radps": 0.0,
        "frame_id": force_frame or "map",
        "planner_id": "trace_replay_land",
    })

post_land_steps = int(max(post_land_s, 0.0) * rate_hz)
for _ in range(post_land_steps):
    publish_rows.append({
        "phase": "post_land_hold",
        "position_m": [land_start_xy[0], land_start_xy[1], 0.0],
        "velocity_mps": [0.0, 0.0, 0.0],
        "acceleration_mps2": [0.0, 0.0, 0.0],
        "yaw_rad": publish_rows[-1]["yaw_rad"],
        "yaw_rate_radps": 0.0,
        "frame_id": force_frame or "map",
        "planner_id": "trace_replay_post_land",
    })

rclpy.init()
node = rclpy.create_node("mosim_px4_offboard_replay_setpoint_publisher")
publisher = node.create_publisher(PlannerSetpoint, "/mosim/planner/setpoint", 10)
trace = (result_dir / "planner_setpoint_trace.jsonl").open("w", encoding="utf-8")
start = time.monotonic()
try:
    for sequence, row in enumerate(publish_rows):
        if not rclpy.ok():
            break
        msg = PlannerSetpoint()
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.header.frame_id = row["frame_id"]
        msg.sequence = sequence
        msg.frame_id = row["frame_id"]
        msg.position_m = [float(item) for item in row["position_m"]]
        msg.velocity_mps = [float(item) for item in row["velocity_mps"]]
        msg.acceleration_mps2 = [float(item) for item in row["acceleration_mps2"]]
        msg.yaw_rad = float(row["yaw_rad"])
        msg.yaw_rate_radps = float(row["yaw_rate_radps"])
        msg.trajectory_status = 1
        msg.planner_id = str(row["planner_id"])
        publisher.publish(msg)
        elapsed = time.monotonic() - start
        trace.write(json.dumps({
            "wall_time_utc": datetime.now(timezone.utc).isoformat(),
            "elapsed_s": round(elapsed, 6),
            "sequence": sequence,
            "phase": row["phase"],
            "position_m": [float(item) for item in msg.position_m],
            "velocity_mps": [float(item) for item in msg.velocity_mps],
            "yaw_rad": msg.yaw_rad,
        }, ensure_ascii=False, separators=(",", ":")) + "\n")
        trace.flush()
        rclpy.spin_once(node, timeout_sec=0.0)
        time.sleep(dt / max(time_scale, 1e-6))
finally:
    trace.close()
    node.destroy_node()
    rclpy.shutdown()
PY
publisher_pid="$!"
printf '%s\n' "${publisher_pid}" > "${RESULT_DIR}/publisher.pid"

wait "${publisher_pid}" || true
sleep 3

python3 - "${RESULT_DIR}" "${TRACE_JSONL}" <<'PY'
import json
import math
import pathlib
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
input_trace = pathlib.Path(sys.argv[2])

def read_jsonl(path):
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
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
        "timestamp_us": int(row.get("timestamp_us", 0) or 0),
        "wall_ts_s": parse_wall_time(row.get("recorded_wall_time_utc")),
        "x_east": float(row.get("y", math.nan)),
        "y_north": float(row.get("x", math.nan)),
        "z_up": -float(row.get("z", math.nan)),
        "heading": float(row.get("heading", math.nan)),
        "valid": bool(row.get("xy_valid")) and bool(row.get("z_valid")),
    }

positions = [ned_to_enu(row) for row in read_jsonl(result_dir / "vehicle_local_position.jsonl")]
positions = [row for row in positions if row["valid"] and math.isfinite(row["wall_ts_s"])]
status_rows = read_jsonl(result_dir / "vehicle_status.jsonl")
ack_rows = read_jsonl(result_dir / "vehicle_command_ack.jsonl")
land_rows = read_jsonl(result_dir / "vehicle_land_detected.jsonl")
setpoints = read_jsonl(result_dir / "planner_setpoint_trace.jsonl")
for row in setpoints:
    row["wall_ts_s"] = parse_wall_time(row.get("wall_time_utc"))
positions.sort(key=lambda row: row["wall_ts_s"])
setpoints = [row for row in setpoints if math.isfinite(row.get("wall_ts_s", math.nan))]
position_times = [row["wall_ts_s"] for row in positions]

def nearest(target, start_index=0):
    import bisect
    if not positions:
        return None, start_index, math.nan
    index = bisect.bisect_left(position_times, target, lo=max(0, start_index - 4))
    candidates = []
    for idx in (index - 1, index, index + 1):
        if 0 <= idx < len(positions):
            candidates.append((abs(positions[idx]["wall_ts_s"] - target), idx))
    if not candidates:
        return None, start_index, math.nan
    dt, idx = min(candidates, key=lambda item: item[0])
    return positions[idx], idx, dt

aligned = []
cursor = 0
for sp in setpoints:
    pos, cursor, dt = nearest(sp["wall_ts_s"], cursor)
    if pos is None or dt > 0.30:
        continue
    ref = sp.get("position_m") or [math.nan, math.nan, math.nan]
    dx = pos["x_east"] - float(ref[0])
    dy = pos["y_north"] - float(ref[1])
    dz = pos["z_up"] - float(ref[2])
    aligned.append({
        "phase": sp.get("phase", ""),
        "actual": [pos["x_east"], pos["y_north"], pos["z_up"]],
        "reference": [float(ref[0]), float(ref[1]), float(ref[2])],
        "xy_error_m": math.hypot(dx, dy),
        "z_error_m": abs(dz),
        "time_delta_s": dt,
    })

def phase(name):
    return [row for row in aligned if row.get("phase") == name]

def stats(rows):
    if not rows:
        return {"sample_count": 0}
    return {
        "sample_count": len(rows),
        "xy_rmse_m": math.sqrt(sum(row["xy_error_m"] ** 2 for row in rows) / len(rows)),
        "xy_max_error_m": max(row["xy_error_m"] for row in rows),
        "z_rmse_m": math.sqrt(sum(row["z_error_m"] ** 2 for row in rows) / len(rows)),
        "z_max_error_m": max(row["z_error_m"] for row in rows),
    }

all_positions = [[row["x_east"], row["y_north"], row["z_up"]] for row in positions]
final = all_positions[-1] if all_positions else None
trace_phase = phase("trace")
land_phase = phase("land") + phase("post_land_hold")
trace_stats = stats(trace_phase)
land_stats = stats(land_phase)
max_alt = max((row[2] for row in all_positions), default=math.nan)
final_alt = final[2] if final else math.nan
post_land_xy_span = math.nan
if len(land_phase) >= 2:
    tail = land_phase[-min(80, len(land_phase)):]
    xs = [row["actual"][0] for row in tail]
    ys = [row["actual"][1] for row in tail]
    post_land_xy_span = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
nav_states = sorted({int(row.get("nav_state", -1)) for row in status_rows if "nav_state" in row})
arming_states = sorted({int(row.get("arming_state", -1)) for row in status_rows if "arming_state" in row})
failsafe_seen = any(bool(row.get("failsafe")) for row in status_rows)
blockers = []
if len(positions) < 50:
    blockers.append(f"local_position_samples_below_min:{len(positions)}<50")
if 14 not in nav_states:
    blockers.append("offboard_nav_state_not_seen")
if 2 not in arming_states:
    blockers.append("armed_state_not_seen")
if failsafe_seen:
    blockers.append("failsafe_seen")
if not math.isfinite(max_alt) or max_alt < 0.8:
    blockers.append(f"max_altitude_low:{max_alt}")
if trace_stats.get("sample_count", 0) < 20:
    blockers.append(f"trace_aligned_samples_below_min:{trace_stats.get('sample_count', 0)}<20")
if trace_stats.get("xy_rmse_m", math.inf) > 1.5:
    blockers.append(f"trace_xy_rmse_above_max:{trace_stats.get('xy_rmse_m')}>1.5")
if math.isfinite(final_alt) and final_alt > 0.25:
    blockers.append(f"landing_not_completed:final_altitude={final_alt}>0.25")
if math.isfinite(post_land_xy_span) and post_land_xy_span > 0.25:
    blockers.append(f"post_land_xy_span_above_max:{post_land_xy_span}>0.25")

payload = {
    "schema": "mosim.px4_offboard_replay_planner_setpoint_trace.v1",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "status": "passed" if not blockers else "runtime_gate_blocked",
    "gate_passed": not blockers,
    "semantic_boundary": "px4_native_offboard_replay_no_direct_gazebo_actuator_control",
    "input_trace_jsonl": str(input_trace),
    "result_dir": str(result_dir),
    "counts": {
        "input_trace_rows": sum(1 for _ in input_trace.open("r", encoding="utf-8", errors="replace")),
        "replayed_setpoints": len(setpoints),
        "local_position": len(positions),
        "vehicle_status": len(status_rows),
        "command_ack": len(ack_rows),
        "land_detected": len(land_rows),
    },
    "state": {
        "nav_states": nav_states,
        "arming_states": arming_states,
        "offboard_seen": 14 in nav_states,
        "armed_seen": 2 in arming_states,
        "failsafe_seen": failsafe_seen,
    },
    "metrics": {
        "max_altitude_m": round(max_alt, 6) if math.isfinite(max_alt) else None,
        "final_altitude_m": round(final_alt, 6) if math.isfinite(final_alt) else None,
        "trace_phase": {key: round(value, 6) if isinstance(value, float) and math.isfinite(value) else value for key, value in trace_stats.items()},
        "land_phase": {key: round(value, 6) if isinstance(value, float) and math.isfinite(value) else value for key, value in land_stats.items()},
        "post_land_xy_span_m": round(post_land_xy_span, 6) if math.isfinite(post_land_xy_span) else None,
        "final_position_m": [round(item, 6) for item in final] if final else None,
    },
    "blockers": blockers,
    "claim_boundary": [
        "This gate replays a recorded PlannerSetpoint trace through PX4 Offboard TrajectorySetpoint.",
        "It does not write Gazebo actuator or motor topics directly.",
        "Passing proves only PX4 can execute this recorded trajectory shape; it is not same-run EGO replanning or MWORKS generated-controller deployment.",
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
(result_dir / "PX4_OFFBOARD_REPLAY_TRACE_GATE.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))
raise SystemExit(0 if not blockers else 1)
PY

cat > "${RESULT_DIR}/RUN_MANIFEST.json" <<EOF
{
  "schema": "mosim.px4_offboard_replay_run_manifest.v1",
  "trace_jsonl": "${TRACE_JSONL}",
  "result_dir": "${RESULT_DIR}",
  "claim_boundary": "PX4-native Offboard replay only; no direct Gazebo actuator writes"
}
EOF
