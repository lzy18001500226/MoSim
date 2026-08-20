#!/usr/bin/env bash
# Run the deterministic Diff-Planner obstacle-wall fixture without Gazebo/PX4.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
WORKSPACE="${GOAL4_DIFF_PLANNER_WS:-${PROJECT_ROOT}/build/ros1/diff_planner_ws_c99}"
RUN_ID="${RUN_ID:-diff_planner_obstacle_fixture_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
ROS_PORT="${ROS_PORT:-11392}"

[[ -f /opt/ros/noetic/setup.bash ]] || { echo "BLOCKER ROS Noetic setup is missing" >&2; exit 2; }
[[ -f "${WORKSPACE}/devel/setup.bash" ]] || { echo "BLOCKER Diff-Planner workspace is not built: ${WORKSPACE}" >&2; exit 2; }

mkdir -p "${RESULT_DIR}/ros_home"
export ROS_MASTER_URI="http://127.0.0.1:${ROS_PORT}"
export ROS_HOME="${RESULT_DIR}/ros_home"
export ROS_LOG_DIR="${RESULT_DIR}/ros_logs"

set +u
source /opt/ros/noetic/setup.bash
source "${WORKSPACE}/devel/setup.bash"
set -u

# Keep old generated package copies in place for inspection, but make Catkin
# ignore them while this workspace is used as a runtime source. They are not
# the project-owned source links used by the current build.
if [[ -d "${WORKSPACE}/src/planning" && ! -e "${WORKSPACE}/src/planning/CATKIN_IGNORE" ]]; then
  printf 'generated stale package tree; use direct Diff package links instead\n' > "${WORKSPACE}/src/planning/CATKIN_IGNORE"
fi
if [[ -d "${WORKSPACE}/src/Utils/quadrotor_msgs" && -d "${WORKSPACE}/src/quadrotor_msgs" \
  && ! -e "${WORKSPACE}/src/Utils/CATKIN_IGNORE" ]]; then
  printf 'generated duplicate quadrotor_msgs tree; use direct Diff message link instead\n' > "${WORKSPACE}/src/Utils/CATKIN_IGNORE"
fi

# The generated Diff workspace may retain an older nested `src/planning`
# directory. Exposing the whole workspace source root makes roslaunch scan
# that residue and reject the run for duplicate package names. Keep this
# fixture bound to the current package links only.
ROS_PACKAGE_PATHS=()
for package in diff_planner multipoint path_searching plan_env traj_opt traj_utils quadrotor_msgs; do
  if [[ -d "${WORKSPACE}/src/${package}" ]]; then
    ROS_PACKAGE_PATHS+=("${WORKSPACE}/src/${package}")
  fi
done
if [[ ! -d "${WORKSPACE}/src/quadrotor_msgs" && -d "${WORKSPACE}/src/Utils" ]]; then
  ROS_PACKAGE_PATHS+=("${WORKSPACE}/src/Utils")
fi
if [[ "${#ROS_PACKAGE_PATHS[@]}" -eq 0 ]]; then
  echo "BLOCKER no direct Diff package roots found under ${WORKSPACE}/src" >&2
  exit 2
fi
export ROS_PACKAGE_PATH="$(IFS=:; printf '%s' "${ROS_PACKAGE_PATHS[*]}"):/opt/ros/noetic/share"
rospack profile >/dev/null 2>&1 || true

pids=()
cleanup() {
  for pid in "${pids[@]:-}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
  wait >/dev/null 2>&1 || true
}
trap cleanup EXIT

roscore -p "${ROS_PORT}" > "${RESULT_DIR}/roscore.log" 2>&1 &
pids+=("$!")
for _ in $(seq 1 100); do
  if rosparam get /rosversion >/dev/null 2>&1; then break; fi
  sleep 0.1
done
rosparam get /rosversion >/dev/null 2>&1 || { echo "BLOCKER roscore did not become ready" >&2; exit 2; }

roslaunch "${PROJECT_ROOT}/Scripts/sunray/diff_planner_single_px4ctrl_goal4.launch" \
  use_multipoint:=false \
  flight_type:=1 \
  target_x:=2.0 target_y:=0.0 target_z:=1.0 \
  grid_resolution:=0.12 obstacles_inflation:=0.20 \
  obstacle_clearance:=0.20 obstacle_clearance_soft:=0.40 \
  visualization_forward_only:=false \
  > "${RESULT_DIR}/diff_planner_launch.log" 2>&1 &
pids+=("$!")

python3 "${PROJECT_ROOT}/Scripts/sunray/probe_diff_planner_obstacle_fixture.py" \
  --output "${RESULT_DIR}/DIFF_PLANNER_OBSTACLE_FIXTURE.json" \
  --timeout-s "${TIMEOUT_S:-20}"
