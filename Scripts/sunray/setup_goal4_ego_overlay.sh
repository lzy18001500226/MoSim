#!/usr/bin/env bash
# Build a minimal ROS1 Noetic overlay for Goal4 EGO single-UAV integration.

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/opt/mosim_work/sunray_ws/Sunray}"
GOAL4_EGO_WS="${GOAL4_EGO_WS:-/opt/mosim_work/goal4_ego_ws_px4msg}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
LOG_PATH="${LOG_PATH:-${PROJECT_ROOT}/Results/sunray_ros1/goal4_ego_overlay_build.log}"

mkdir -p "$(dirname "${LOG_PATH}")"

if [[ ! -d "${SUNRAY_WS}" ]]; then
  echo "SUNRAY_WS missing: ${SUNRAY_WS}" >&2
  exit 2
fi

if [[ ! -d "${GOAL4_EGO_WS}" ]]; then
  if [[ -w "$(dirname "${GOAL4_EGO_WS}")" ]]; then
    mkdir -p "${GOAL4_EGO_WS}/src"
  else
    sudo mkdir -p "${GOAL4_EGO_WS}/src"
    sudo chown -R "$(id -u):$(id -g)" "${GOAL4_EGO_WS}"
  fi
else
  mkdir -p "${GOAL4_EGO_WS}/src"
fi

link_pkg() {
  local name="$1"
  local target="$2"
  if [[ ! -d "${target}" ]]; then
    echo "Package source missing for ${name}: ${target}" >&2
    exit 3
  fi
  if [[ ! -e "${GOAL4_EGO_WS}/src/${name}" ]]; then
    ln -s "${target}" "${GOAL4_EGO_WS}/src/${name}"
  fi
}

link_pkg cmake_utils "${SUNRAY_WS}/External_Module/ego-planner-swarm/src/uav_simulator/Utils/cmake_utils"
link_pkg pose_utils "${SUNRAY_WS}/External_Module/ego-planner-swarm/src/uav_simulator/Utils/pose_utils"
link_pkg uav_utils "${SUNRAY_WS}/External_Module/ego-planner-swarm/src/uav_simulator/Utils/uav_utils"
link_pkg quadrotor_msgs "${PX4CTRL_WS}/src/quadrotor_msgs"
link_pkg traj_utils "${SUNRAY_WS}/External_Module/ego-planner-swarm/src/planner/traj_utils"
link_pkg plan_env "${SUNRAY_WS}/External_Module/ego-planner-swarm/src/planner/plan_env"
link_pkg path_searching "${SUNRAY_WS}/External_Module/ego-planner-swarm/src/planner/path_searching"
link_pkg bspline_opt "${SUNRAY_WS}/External_Module/ego-planner-swarm/src/planner/bspline_opt"
link_pkg ego_planner "${SUNRAY_WS}/External_Module/ego-planner-swarm/src/planner/plan_manage"

{
  echo "GOAL4_EGO_WS=${GOAL4_EGO_WS}"
  echo "SUNRAY_WS=${SUNRAY_WS}"
  echo "linked packages:"
  find "${GOAL4_EGO_WS}/src" -maxdepth 1 -type l -printf '%f -> %l\n' | sort
  export PATH=/opt/ros/noetic/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib
  unset CMAKE_PREFIX_PATH
  unset Protobuf_DIR
  unset protobuf_DIR
  unset Protobuf_ROOT
  set +u
  source /usr/share/gazebo/setup.sh
  source /opt/ros/noetic/setup.bash
  if [[ -f "${SUNRAY_WS}/devel/setup.bash" ]]; then
    source "${SUNRAY_WS}/devel/setup.bash"
  fi
  set -u
  cd "${GOAL4_EGO_WS}"
  catkin_make --force-cmake -DCMAKE_BUILD_TYPE=Release -DProtobuf_DIR=/usr/lib/x86_64-linux-gnu/cmake/protobuf
} > "${LOG_PATH}" 2>&1

echo "${GOAL4_EGO_WS}"
