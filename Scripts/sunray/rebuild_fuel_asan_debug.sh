#!/usr/bin/env bash
source /opt/ros/noetic/setup.bash
set -euo pipefail
workspace="${1:-/opt/mosim_work/sunray_ws/fuel_ws_planner_only_debug_20260701_003}"
cd "${workspace}"
catkin_make \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_FLAGS='-O0 -g -fsanitize=address -fno-omit-frame-pointer' \
  -DCMAKE_C_FLAGS='-O0 -g -fsanitize=address -fno-omit-frame-pointer' \
  -DCMAKE_EXE_LINKER_FLAGS='-fsanitize=address' \
  -DCMAKE_SHARED_LINKER_FLAGS='-fsanitize=address' \
  -j2
