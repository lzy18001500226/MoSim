#!/usr/bin/env bash
# Bounded PX4 + Gazebo x500 baseline probe.
#
# Scope:
# - Starts Micro XRCE-DDS Agent.
# - Starts official PX4 SITL Gazebo x500 target.
# - Records ROS 2 /fmu topic visibility.
# - Does not arm, switch Offboard, or publish setpoints.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
PX4_DIR="${PX4_DIR:-${PROJECT_ROOT}/References/PX4/PX4}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/px4_gazebo/px4_gz_x500_baseline_$(date +%Y%m%d_%H%M%S)}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
PX4_ROS2_INSTALL="${PX4_ROS2_INSTALL:-${PROJECT_ROOT}/Results/ros2_build/px4_offboard_adapter_20260620_rebuild/install/setup.bash}"
STARTUP_TIMEOUT_S="${STARTUP_TIMEOUT_S:-420}"
TOPIC_WAIT_S="${TOPIC_WAIT_S:-90}"
HEADLESS="${HEADLESS:-1}"
PX4_SIM_SPEED_FACTOR="${PX4_SIM_SPEED_FACTOR:-1}"
SANITIZE_WSL_PATH="${SANITIZE_WSL_PATH:-1}"
ROS_LOG_DIR="${ROS_LOG_DIR:-${PROJECT_ROOT}/Results/tmp/ros_logs/px4_gz_x500_baseline}"

mkdir -p "${RESULT_DIR}"
mkdir -p "${ROS_LOG_DIR}"
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

write_summary() {
  local status="${1:-unknown}"
  local fmu_count=0
  local vehicle_status_present=0
  local vehicle_status_topic=""
  if [[ -f "${RESULT_DIR}/ros2_topic_list.txt" ]]; then
    fmu_count="$(grep -c '^/fmu/' "${RESULT_DIR}/ros2_topic_list.txt" 2>/dev/null || true)"
    vehicle_status_topic="$(
      awk '/^\/fmu\/out\/vehicle_status(_v[0-9]+)?([[:space:]]|$)/ {print $1; exit}' \
        "${RESULT_DIR}/ros2_topic_list.txt" 2>/dev/null || true
    )"
    if [[ -n "${vehicle_status_topic}" ]]; then
      vehicle_status_present=1
    fi
  fi
  python3 - "${RESULT_DIR}" "${status}" "${fmu_count}" "${vehicle_status_present}" "${vehicle_status_topic}" <<'PY'
import json
import pathlib
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
status = sys.argv[2]
fmu_count = int(sys.argv[3] or 0)
vehicle_status_present = int(sys.argv[4] or 0) > 0
vehicle_status_topic = sys.argv[5]

def tail(path, n=40):
    p = result_dir / path
    if not p.exists():
        return []
    return p.read_text(encoding="utf-8", errors="replace").splitlines()[-n:]

summary = {
    "schema": "mosim.px4_gz_x500_baseline_probe.v1",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "status": status,
    "semantic_boundary": "baseline_only_no_arm_no_offboard_no_setpoint",
    "fmu_topic_count": fmu_count,
    "vehicle_status_topic_present": vehicle_status_present,
    "vehicle_status_topic": vehicle_status_topic,
    "result_dir": str(result_dir),
    "logs": {
        "agent": str(result_dir / "xrce_agent.log"),
        "px4": str(result_dir / "px4_gz_x500.log"),
        "ros2_topic_list": str(result_dir / "ros2_topic_list.txt"),
        "ros2_topic_list_err": str(result_dir / "ros2_topic_list.err"),
        "ros2_env": str(result_dir / "ros2_env.txt"),
        "vehicle_status_once": str(result_dir / "vehicle_status_once.txt"),
        "vehicle_status_hz": str(result_dir / "vehicle_status_hz.txt"),
    },
    "px4_log_tail": tail("px4_gz_x500.log"),
    "agent_log_tail": tail("xrce_agent.log"),
}
(result_dir / "BASELINE_SUMMARY.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps(summary, ensure_ascii=False, indent=2))
PY
}

{
  echo "schema=mosim.px4_gz_x500_dependency_snapshot.v1"
  date -Is
  echo "PROJECT_ROOT=${PROJECT_ROOT}"
  echo "PX4_DIR=${PX4_DIR}"
  echo "RESULT_DIR=${RESULT_DIR}"
  command -v gz || true
  gz sim --versions 2>/dev/null || true
  command -v ign || true
  ign gazebo --versions 2>/dev/null || true
  find_agent_cmd || true
  command -v ros2 || true
  command -v python3 || true
  command -v ninja || true
} > "${RESULT_DIR}/dependency_snapshot.txt" 2>&1

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

set +eu
if [[ -f "${ROS_SETUP}" ]]; then
  # shellcheck disable=SC1090
  source "${ROS_SETUP}"
fi
if [[ -f "${PX4_ROS2_INSTALL}" ]]; then
  # shellcheck disable=SC1090
  source "${PX4_ROS2_INSTALL}"
fi
set -euo pipefail

{
  echo "ROS_DISTRO=${ROS_DISTRO:-}"
  echo "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-unset}"
  echo "RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-unset}"
  echo "ROS_LOG_DIR=${ROS_LOG_DIR}"
  command -v ros2 || true
  ros2 daemon stop || true
  ros2 daemon status || true
} > "${RESULT_DIR}/ros2_env.txt" 2>&1

topic_seen=0
vehicle_status_topic=""
deadline=$((SECONDS + TOPIC_WAIT_S))
while [[ "${SECONDS}" -lt "${deadline}" ]]; do
  if ! kill -0 "${px4_pid}" >/dev/null 2>&1; then
    break
  fi
  timeout 12s ros2 topic list --no-daemon --spin-time 4 -t > "${RESULT_DIR}/ros2_topic_list.txt" 2> "${RESULT_DIR}/ros2_topic_list.err" || true
  vehicle_status_topic="$(
    awk '/^\/fmu\/out\/vehicle_status(_v[0-9]+)?([[:space:]]|$)/ {print $1; exit}' \
      "${RESULT_DIR}/ros2_topic_list.txt" 2>/dev/null || true
  )"
  if [[ -n "${vehicle_status_topic}" ]]; then
    printf '%s\n' "${vehicle_status_topic}" > "${RESULT_DIR}/vehicle_status_topic.txt"
    topic_seen=1
    break
  fi
  sleep 3
done

if [[ -n "${vehicle_status_topic}" ]]; then
  timeout 10s ros2 topic hz "${vehicle_status_topic}" > "${RESULT_DIR}/vehicle_status_hz.txt" 2>&1 || true
  timeout 10s ros2 topic echo --once "${vehicle_status_topic}" > "${RESULT_DIR}/vehicle_status_once.txt" 2>&1 || true
fi

if [[ "${topic_seen}" == "1" ]]; then
  write_summary "passed"
else
  if ! kill -0 "${px4_pid}" >/dev/null 2>&1; then
    write_summary "blocked_px4_exited_before_vehicle_status_topic"
  else
    write_summary "blocked_no_vehicle_status_topic"
  fi
  exit 2
fi
