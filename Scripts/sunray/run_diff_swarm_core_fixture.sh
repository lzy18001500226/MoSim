#!/usr/bin/env bash
# Run a bounded source-local Diff-Swarm ROS-interface fixture without Gazebo, PX4, QGC, or UE.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
WORKSPACE="${GOAL4_DIFF_PLANNER_WS:-${PROJECT_ROOT}/build/ros1/diff_planner_ws_c99}"
RUN_ID="${RUN_ID:-diff_swarm_core_fixture_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
ROS_PORT="${ROS_PORT:-11392}"
TIMEOUT_S="${TIMEOUT_S:-25}"

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

roslaunch "${PROJECT_ROOT}/Scripts/sunray/diff_swarm_px4ctrl_goal5.launch" \
  uav_num:=3 \
  use_multipoint:=false \
  flight_type:=1 \
  target1_x:=2.0 target1_y:=-1.0 target1_z:=1.0 \
  target2_x:=2.0 target2_y:=1.0 target2_z:=1.0 \
  target3_x:=0.5 target3_y:=0.0 target3_z:=1.0 \
  uav1_odom_topic:=/uav1/mosim/diff_swarm/planner_odom_world \
  uav2_odom_topic:=/uav2/mosim/diff_swarm/planner_odom_world \
  uav3_odom_topic:=/uav3/mosim/diff_swarm/planner_odom_world \
  uav1_global_pointcloud_topic:=/uav1/mosim/diff_swarm/planner_cloud_world \
  uav2_global_pointcloud_topic:=/uav2/mosim/diff_swarm/planner_cloud_world \
  uav3_global_pointcloud_topic:=/uav3/mosim/diff_swarm/planner_cloud_world \
  uav1_goal_topic:=/uav1/mosim/diff_swarm/planner_goal_world \
  uav2_goal_topic:=/uav2/mosim/diff_swarm/planner_goal_world \
  uav3_goal_topic:=/uav3/mosim/diff_swarm/planner_goal_world \
  uav1_position_cmd_topic:=/uav1/mosim/diff_swarm/planner_position_cmd_world \
  uav2_position_cmd_topic:=/uav2/mosim/diff_swarm/planner_position_cmd_world \
  uav3_position_cmd_topic:=/uav3/mosim/diff_swarm/planner_position_cmd_world \
  > "${RESULT_DIR}/diff_swarm_launch.log" 2>&1 &
pids+=("$!")

python3 "${PROJECT_ROOT}/Scripts/sunray/probe_diff_swarm_core_fixture.py" \
  --output "${RESULT_DIR}/DIFF_SWARM_CORE_FIXTURE.json" \
  --timeout-s "${TIMEOUT_S}"
