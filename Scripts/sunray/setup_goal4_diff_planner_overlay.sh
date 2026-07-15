#!/usr/bin/env bash
# Build a ROS1 Noetic overlay for Diff-Planner with px4ctrl-compatible messages.

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/opt/mosim_work/sunray_ws/Sunray}"
DIFF_SRC="${DIFF_SRC:-${PROJECT_ROOT}/References/Lab/planning_local/Diff-Planner/src}"
DIFF_WS="${DIFF_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/goal4_diff_planner_ws_px4msg}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
PX4CTRL_MSG_SRC="${PX4CTRL_MSG_SRC:-${PROJECT_ROOT}/References/Lab/planning_local/Fast-Drone-250/src/utils/quadrotor_msgs}"
DIFF_MSG_SRC="${DIFF_MSG_SRC:-${DIFF_SRC}/Utils/quadrotor_msgs}"
OVERLAY_MSG_SRC="${DIFF_WS}/generated_src/quadrotor_msgs_mosim_diff_overlay"
LOG_PATH="${LOG_PATH:-${PROJECT_ROOT}/Results/sunray_ros1/goal4_diff_planner_overlay_build.log}"

mkdir -p "$(dirname "${LOG_PATH}")"

if [[ ! -d "${DIFF_SRC}" ]]; then
  echo "DIFF_SRC missing: ${DIFF_SRC}" >&2
  exit 2
fi
if [[ ! -d "${PX4CTRL_MSG_SRC}" ]]; then
  echo "PX4CTRL_MSG_SRC missing: ${PX4CTRL_MSG_SRC}" >&2
  exit 2
fi
if [[ ! -f "${DIFF_MSG_SRC}/msg/Px4ctrlState.msg" ]]; then
  echo "DIFF Px4ctrlState.msg missing: ${DIFF_MSG_SRC}/msg/Px4ctrlState.msg" >&2
  exit 2
fi

mkdir -p "${DIFF_WS}/src"

prepare_quadrotor_msgs_overlay() {
  mkdir -p "${OVERLAY_MSG_SRC}"
  cp -a "${PX4CTRL_MSG_SRC}/." "${OVERLAY_MSG_SRC}/"
  cp "${DIFF_MSG_SRC}/msg/Px4ctrlState.msg" "${OVERLAY_MSG_SRC}/msg/Px4ctrlState.msg"
  if ! grep -q 'Px4ctrlState.msg' "${OVERLAY_MSG_SRC}/CMakeLists.txt"; then
    sed -i '/Px4ctrlDebug.msg/a\  Px4ctrlState.msg' "${OVERLAY_MSG_SRC}/CMakeLists.txt"
  fi
}

link_pkg() {
  local name="$1"
  local target="$2"
  if [[ ! -d "${target}" ]]; then
    echo "Package source missing for ${name}: ${target}" >&2
    exit 3
  fi
  if [[ -L "${DIFF_WS}/src/${name}" ]]; then
    local current
    current="$(readlink "${DIFF_WS}/src/${name}")"
    if [[ "${current}" != "${target}" ]]; then
      rm -f "${DIFF_WS}/src/${name}"
      ln -s "${target}" "${DIFF_WS}/src/${name}"
    fi
  elif [[ ! -e "${DIFF_WS}/src/${name}" ]]; then
    ln -s "${target}" "${DIFF_WS}/src/${name}"
  else
    echo "Refusing to replace non-symlink ${DIFF_WS}/src/${name}" >&2
    exit 4
  fi
}

prepare_quadrotor_msgs_overlay
link_pkg quadrotor_msgs "${OVERLAY_MSG_SRC}"
link_pkg traj_utils "${DIFF_SRC}/diff_planner/traj_utils"
link_pkg plan_env "${DIFF_SRC}/diff_planner/plan_env"
link_pkg path_searching "${DIFF_SRC}/diff_planner/path_searching"
link_pkg traj_opt "${DIFF_SRC}/diff_planner/traj_opt"
link_pkg diff_planner "${DIFF_SRC}/diff_planner/plan_manage"
link_pkg multipoint "${DIFF_SRC}/user_command/multipoint"

{
  echo "DIFF_WS=${DIFF_WS}"
  echo "DIFF_SRC=${DIFF_SRC}"
  echo "PX4CTRL_MSG_SRC=${PX4CTRL_MSG_SRC}"
  echo "DIFF_MSG_SRC=${DIFF_MSG_SRC}"
  echo "OVERLAY_MSG_SRC=${OVERLAY_MSG_SRC}"
  echo "linked packages:"
  find "${DIFF_WS}/src" -maxdepth 1 -type l -printf '%f -> %l\n' | sort
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
  cd "${DIFF_WS}"
  catkin_make --force-cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS="-I/usr/include/eigen3" \
    -DProtobuf_DIR=/usr/lib/x86_64-linux-gnu/cmake/protobuf
} > "${LOG_PATH}" 2>&1

echo "${DIFF_WS}"
