#!/usr/bin/env bash
# Run a bounded source-local Diff-Planner ROS-interface fixture without Gazebo, QGC, or UE.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
WORKSPACE="${GOAL4_DIFF_PLANNER_WS:-${PROJECT_ROOT}/build/ros1/diff_planner_ws_c99}"
RUN_ID="${RUN_ID:-diff_planner_single_core_fixture_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
ROS_PORT="${ROS_PORT:-11391}"
TIMEOUT_S="${TIMEOUT_S:-20}"

die() {
  printf 'BLOCKER %s\n' "$*" >&2
  exit 2
}

[[ -f /opt/ros/noetic/setup.bash ]] || die "ROS Noetic setup is missing"
[[ -f "${WORKSPACE}/devel/setup.bash" ]] || die "Diff-Planner workspace is not built: ${WORKSPACE}/devel/setup.bash"

mkdir -p "${RESULT_DIR}/ros_home"
export ROS_MASTER_URI="http://127.0.0.1:${ROS_PORT}"
export ROS_HOME="${RESULT_DIR}/ros_home"
export ROS_LOG_DIR="${RESULT_DIR}/ros_logs"
export PROJECT_ROOT

# ROS Noetic's setup hook reads ROS_DISTRO before assigning it, so source it
# with nounset temporarily disabled and restore the wrapper's strict mode.
set +u
source /opt/ros/noetic/setup.bash
source "${WORKSPACE}/devel/setup.bash"
set -u

pids=()
cleanup() {
  local pid
  for pid in "${pids[@]:-}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
  wait >/dev/null 2>&1 || true
}
trap cleanup EXIT

roscore -p "${ROS_PORT}" > "${RESULT_DIR}/roscore.log" 2>&1 &
pids+=("$!")
for _ in $(seq 1 100); do
  if rosparam get /rosversion >/dev/null 2>&1; then
    break
  fi
  sleep 0.1
done
rosparam get /rosversion >/dev/null 2>&1 || die "roscore did not become ready"

roslaunch "${PROJECT_ROOT}/Scripts/sunray/diff_planner_single_px4ctrl_goal4.launch" \
  use_multipoint:=false \
  flight_type:=1 \
  > "${RESULT_DIR}/diff_planner_launch.log" 2>&1 &
pids+=("$!")

python3 "${PROJECT_ROOT}/Scripts/sunray/probe_diff_planner_single_core_fixture.py" \
  --output "${RESULT_DIR}/DIFF_PLANNER_SINGLE_CORE_FIXTURE.json" \
  --timeout-s "${TIMEOUT_S}"
