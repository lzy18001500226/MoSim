#!/usr/bin/env bash
set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RACER_WS="${RACER_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/racer_ws_d1_optimized_20260701_084307}"

source /opt/ros/noetic/setup.bash
set -u
cmake --build "${RACER_WS}/build" --target exploration_node -- -j2
