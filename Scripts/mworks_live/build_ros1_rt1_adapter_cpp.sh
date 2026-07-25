#!/usr/bin/env bash
set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SOURCE="${PROJECT_ROOT}/Scripts/mworks_live/ros1_rt1_adapter_cpp.cpp"
OUTPUT_DIR="${MWORKS_LIVE_CPP_BUILD_DIR:-${PROJECT_ROOT}/Results/control_platform/mworks_live_rt1_cpp}"
OUTPUT="${OUTPUT_DIR}/bin/ros1_rt1_adapter_cpp"
CUSTOM_SETUP="${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash"

source /opt/ros/noetic/setup.bash
[[ -f /opt/mosim_work/sunray_ws/Sunray/devel/setup.bash ]] && source /opt/mosim_work/sunray_ws/Sunray/devel/setup.bash
[[ -f "${CUSTOM_SETUP}" ]] && source "${CUSTOM_SETUP}"
set -u

QUADROTOR_MSGS_DIR="$(rospack find quadrotor_msgs)"
CUSTOM_DEVEL="$(dirname "$(dirname "${QUADROTOR_MSGS_DIR}")")/devel"
if [[ -x "${OUTPUT}" && "${OUTPUT}" -nt "${SOURCE}" ]]; then
  printf '%s\n' "${OUTPUT}"
  exit 0
fi

mkdir -p "$(dirname "${OUTPUT}")"
read -r -a ROSCPP_FLAGS <<< "$(pkg-config --cflags --libs roscpp)"
read -r -a GAZEBO_FLAGS <<< "$(pkg-config --cflags --libs gazebo)"
g++ -std=c++17 -O2 -DNDEBUG -pthread \
  "${SOURCE}" -o "${OUTPUT}" \
  -I/opt/ros/noetic/include -I"${CUSTOM_DEVEL}/include" \
  "${ROSCPP_FLAGS[@]}" "${GAZEBO_FLAGS[@]}"
printf '%s\n' "${OUTPUT}"
