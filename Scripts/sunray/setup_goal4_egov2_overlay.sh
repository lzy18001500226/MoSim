#!/usr/bin/env bash
# Build a ROS1 Noetic overlay for EGO-Planner-v2 with px4ctrl-compatible messages.

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/opt/mosim_work/sunray_ws/Sunray}"
EGOV2_SRC="${EGOV2_SRC:-${PROJECT_ROOT}/References/Lab/planning_local/EGO-Planner-v2/swarm-playground/main_ws/src}"
EGOV2_WS="${EGOV2_WS:-/opt/mosim_work/goal4_egov2_ws_px4msg}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
PX4CTRL_MSG_SRC="${PX4CTRL_MSG_SRC:-${PROJECT_ROOT}/References/Lab/planning_local/Fast-Drone-250/src/utils/quadrotor_msgs}"
LOG_PATH="${LOG_PATH:-${PROJECT_ROOT}/Results/sunray_ros1/goal4_egov2_overlay_build.log}"

mkdir -p "$(dirname "${LOG_PATH}")"

if [[ ! -d "${EGOV2_SRC}" ]]; then
  echo "EGOV2_SRC missing: ${EGOV2_SRC}" >&2
  exit 2
fi
if [[ ! -d "${PX4CTRL_MSG_SRC}" ]]; then
  echo "PX4CTRL_MSG_SRC missing: ${PX4CTRL_MSG_SRC}" >&2
  exit 2
fi

if [[ ! -d "${EGOV2_WS}" ]]; then
  if [[ -w "$(dirname "${EGOV2_WS}")" ]]; then
    mkdir -p "${EGOV2_WS}/src"
  else
    sudo mkdir -p "${EGOV2_WS}/src"
    sudo chown -R "$(id -u):$(id -g)" "${EGOV2_WS}"
  fi
else
  mkdir -p "${EGOV2_WS}/src"
fi

link_pkg() {
  local name="$1"
  local target="$2"
  if [[ ! -d "${target}" ]]; then
    echo "Package source missing for ${name}: ${target}" >&2
    exit 3
  fi
  if [[ -L "${EGOV2_WS}/src/${name}" ]]; then
    local current
    current="$(readlink "${EGOV2_WS}/src/${name}")"
    if [[ "${current}" != "${target}" ]]; then
      rm -f "${EGOV2_WS}/src/${name}"
      ln -s "${target}" "${EGOV2_WS}/src/${name}"
    fi
  elif [[ ! -e "${EGOV2_WS}/src/${name}" ]]; then
    ln -s "${target}" "${EGOV2_WS}/src/${name}"
  else
    echo "Refusing to replace non-symlink ${EGOV2_WS}/src/${name}" >&2
    exit 4
  fi
}

link_pkg quadrotor_msgs "${PX4CTRL_MSG_SRC}"
link_pkg traj_utils "${EGOV2_SRC}/planner/traj_utils"
link_pkg plan_env "${EGOV2_SRC}/planner/plan_env"
link_pkg path_searching "${EGOV2_SRC}/planner/path_searching"
link_pkg traj_opt "${EGOV2_SRC}/planner/traj_opt"
link_pkg ego_planner "${EGOV2_SRC}/planner/plan_manage"

{
  echo "EGOV2_WS=${EGOV2_WS}"
  echo "EGOV2_SRC=${EGOV2_SRC}"
  echo "PX4CTRL_MSG_SRC=${PX4CTRL_MSG_SRC}"
  echo "linked packages:"
  find "${EGOV2_WS}/src" -maxdepth 1 -type l -printf '%f -> %l\n' | sort
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
  if [[ -f "${PX4CTRL_WS}/devel/setup.bash" ]]; then
    source "${PX4CTRL_WS}/devel/setup.bash"
  fi
  set -u
  cd "${EGOV2_WS}"
  catkin_make --force-cmake -DCMAKE_BUILD_TYPE=Release -DProtobuf_DIR=/usr/lib/x86_64-linux-gnu/cmake/protobuf
} > "${LOG_PATH}" 2>&1

echo "${EGOV2_WS}"
