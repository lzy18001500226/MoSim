#!/usr/bin/env bash
# Bounded PX4 Offboard adapter live smoke.
#
# Scope:
# - Starts Micro XRCE-DDS Agent and official PX4 SITL Gazebo x500 target.
# - Starts MoSim PX4 Offboard adapter with default safe parameters
#   (auto_arm=false, auto_offboard=false).
# - Publishes one PlannerSetpoint to the adapter input.
# - Verifies /fmu/in/offboard_control_mode and /fmu/in/trajectory_setpoint are
#   observable while /fmu/in/vehicle_command stays absent.
# - Does not arm, switch Offboard, or publish VehicleCommand intentionally.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
PX4_DIR="${PX4_DIR:-${PROJECT_ROOT}/Results/tmp/px4_gitwork/PX4}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/px4_gazebo/px4_offboard_adapter_live_smoke_$(date +%Y%m%d_%H%M%S)}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
PX4_ROS2_INSTALL="${PX4_ROS2_INSTALL:-${PROJECT_ROOT}/Results/ros2_build/px4_offboard_adapter_20260620_rebuild/install/setup.bash}"
STARTUP_TIMEOUT_S="${STARTUP_TIMEOUT_S:-360}"
TOPIC_WAIT_S="${TOPIC_WAIT_S:-120}"
SMOKE_WINDOW_S="${SMOKE_WINDOW_S:-12}"
HEADLESS="${HEADLESS:-1}"
PX4_SIM_SPEED_FACTOR="${PX4_SIM_SPEED_FACTOR:-1}"
SANITIZE_WSL_PATH="${SANITIZE_WSL_PATH:-1}"
ROS_LOG_DIR="${ROS_LOG_DIR:-${PROJECT_ROOT}/Results/tmp/ros_logs/px4_offboard_adapter_live_smoke}"

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

count_records() {
  local path="${1}"
  local marker="${2:-timestamp:}"
  if [[ ! -f "${path}" ]]; then
    printf '0\n'
    return 0
  fi
  grep -c "${marker}" "${path}" 2>/dev/null || true
}

write_summary() {
  local status="${1:-unknown}"
  local offboard_count
  local setpoint_count
  local command_count
  local vehicle_status_topic
  offboard_count="$(count_records "${RESULT_DIR}/offboard_control_mode_echo.txt")"
  setpoint_count="$(count_records "${RESULT_DIR}/trajectory_setpoint_echo.txt")"
  command_count="$(count_records "${RESULT_DIR}/vehicle_command_echo.txt")"
  vehicle_status_topic="$(cat "${RESULT_DIR}/vehicle_status_topic.txt" 2>/dev/null || true)"
  python3 - "${RESULT_DIR}" "${status}" "${offboard_count}" "${setpoint_count}" "${command_count}" "${vehicle_status_topic}" <<'PY'
import json
import pathlib
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
status = sys.argv[2]
offboard_count = int(sys.argv[3] or 0)
setpoint_count = int(sys.argv[4] or 0)
command_count = int(sys.argv[5] or 0)
vehicle_status_topic = sys.argv[6]

def tail(path, n=30):
    p = result_dir / path
    if not p.exists():
        return []
    return p.read_text(encoding="utf-8", errors="replace").splitlines()[-n:]

payload = {
    "schema": "mosim.px4_offboard_adapter_live_smoke.v1",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "status": status,
    "semantic_boundary": "live_px4_xrce_topic_smoke_only_no_arm_no_offboard_mode_switch_no_vehicle_command",
    "vehicle_status_topic": vehicle_status_topic,
    "observed": {
        "offboard_control_mode_count": offboard_count,
        "trajectory_setpoint_count": setpoint_count,
        "vehicle_command_count": command_count,
        "vehicle_command_absent": command_count == 0,
    },
    "defaults_under_test": {
        "auto_arm": False,
        "auto_offboard": False,
        "frame_mode": "enu_to_ned",
        "publish_rate_hz": 20.0,
    },
    "result_dir": str(result_dir),
    "files": {
        "px4_log": str(result_dir / "px4_gz_x500.log"),
        "xrce_agent_log": str(result_dir / "xrce_agent.log"),
        "adapter_log": str(result_dir / "adapter.log"),
        "planner_pub_log": str(result_dir / "planner_setpoint_pub.log"),
        "topic_list": str(result_dir / "ros2_topic_list.txt"),
        "offboard_control_mode_echo": str(result_dir / "offboard_control_mode_echo.txt"),
        "trajectory_setpoint_echo": str(result_dir / "trajectory_setpoint_echo.txt"),
        "vehicle_command_echo": str(result_dir / "vehicle_command_echo.txt"),
    },
    "claim_boundary": [
        "PX4 SITL, Gazebo, uXRCE-DDS, and the MoSim adapter were started.",
        "This smoke intentionally did not arm, switch Offboard, or publish VehicleCommand.",
        "Passing this smoke proves only topic compatibility and default safety behavior, not flight, hover, trajectory tracking, or controller performance.",
    ],
    "adapter_log_tail": tail("adapter.log"),
    "px4_log_tail": tail("px4_gz_x500.log"),
}
(result_dir / "PX4_OFFBOARD_ADAPTER_LIVE_SMOKE.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(payload, ensure_ascii=False, indent=2))
PY
}

agent_cmd="$(find_agent_cmd || true)"
if [[ -z "${agent_cmd}" ]]; then
  write_summary "blocked_missing_micro_xrce_agent"
  exit 2
fi
if [[ ! -d "${PX4_DIR}" ]]; then
  write_summary "blocked_missing_px4_dir"
  exit 2
fi

"${agent_cmd}" udp4 -p 8888 > "${RESULT_DIR}/xrce_agent.log" 2>&1 &
agent_pid="$!"
printf '%s\n' "${agent_pid}" > "${RESULT_DIR}/xrce_agent.pid"
sleep 2
if ! kill -0 "${agent_pid}" >/dev/null 2>&1; then
  write_summary "blocked_xrce_agent_failed_to_start"
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
while [[ "${SECONDS}" -lt "${deadline}" ]]; do
  if ! kill -0 "${px4_pid}" >/dev/null 2>&1; then
    write_summary "blocked_px4_exited_before_topics"
    exit 2
  fi
  timeout 12s ros2 topic list --no-daemon --spin-time 4 -t > "${RESULT_DIR}/ros2_topic_list.txt" 2> "${RESULT_DIR}/ros2_topic_list.err" || true
  vehicle_status_topic="$(
    awk '/^\/fmu\/out\/vehicle_status(_v[0-9]+)?([[:space:]]|$)/ {print $1; exit}' \
      "${RESULT_DIR}/ros2_topic_list.txt" 2>/dev/null || true
  )"
  if [[ -n "${vehicle_status_topic}" ]]; then
    printf '%s\n' "${vehicle_status_topic}" > "${RESULT_DIR}/vehicle_status_topic.txt"
    break
  fi
  sleep 3
done

if [[ -z "${vehicle_status_topic}" ]]; then
  write_summary "blocked_no_vehicle_status_topic"
  exit 2
fi

ros2 run mosim_px4_offboard_adapter planner_setpoint_to_px4_offboard_node \
  --ros-args \
  -p auto_arm:=false \
  -p auto_offboard:=false \
  -p frame_mode:=enu_to_ned \
  -p expected_frame:=map \
  -p publish_rate_hz:=20.0 \
  -p stale_timeout_s:=2.0 \
  > "${RESULT_DIR}/adapter.log" 2>&1 &
adapter_pid="$!"
printf '%s\n' "${adapter_pid}" > "${RESULT_DIR}/adapter.pid"
sleep 2
if ! kill -0 "${adapter_pid}" >/dev/null 2>&1; then
  write_summary "blocked_adapter_failed_to_start"
  exit 2
fi

timeout "${SMOKE_WINDOW_S}s" ros2 topic echo /fmu/in/offboard_control_mode > "${RESULT_DIR}/offboard_control_mode_echo.txt" 2>&1 &
offboard_echo_pid="$!"
timeout "${SMOKE_WINDOW_S}s" ros2 topic echo /fmu/in/trajectory_setpoint > "${RESULT_DIR}/trajectory_setpoint_echo.txt" 2>&1 &
setpoint_echo_pid="$!"
timeout "${SMOKE_WINDOW_S}s" ros2 topic echo /fmu/in/vehicle_command > "${RESULT_DIR}/vehicle_command_echo.txt" 2>&1 &
command_echo_pid="$!"

sleep 1
timeout 5s ros2 topic pub --once /mosim/planner/setpoint mosim_msgs/msg/PlannerSetpoint \
  "{header: {frame_id: 'map'}, sequence: 1, frame_id: 'map', position_m: [0.0, 0.0, 1.0], velocity_mps: [0.0, 0.0, 0.0], acceleration_mps2: [0.0, 0.0, 0.0], yaw_rad: 0.0, yaw_rate_radps: 0.0, trajectory_status: 1, planner_id: 'live_smoke'}" \
  > "${RESULT_DIR}/planner_setpoint_pub.log" 2>&1 || true

wait "${offboard_echo_pid}" 2>/dev/null || true
wait "${setpoint_echo_pid}" 2>/dev/null || true
wait "${command_echo_pid}" 2>/dev/null || true

offboard_count="$(count_records "${RESULT_DIR}/offboard_control_mode_echo.txt")"
setpoint_count="$(count_records "${RESULT_DIR}/trajectory_setpoint_echo.txt")"
command_count="$(count_records "${RESULT_DIR}/vehicle_command_echo.txt")"

if [[ "${offboard_count}" -gt 0 && "${setpoint_count}" -gt 0 && "${command_count}" -eq 0 ]]; then
  write_summary "passed"
else
  write_summary "failed_topic_contract"
  exit 2
fi
