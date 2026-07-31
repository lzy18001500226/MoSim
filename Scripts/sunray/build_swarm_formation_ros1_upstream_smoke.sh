#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SWARM_FORMATION_ROOT="${SWARM_FORMATION_ROOT:-${PROJECT_ROOT}/src/planning/fixed_formation}"
SWARM_FORMATION_BUILD_TYPE="${SWARM_FORMATION_BUILD_TYPE:-Release}"
SWARM_FORMATION_BUILD_JOBS="${SWARM_FORMATION_BUILD_JOBS:-2}"
SWARM_FORMATION_BUILD_TIMEOUT_S="${SWARM_FORMATION_BUILD_TIMEOUT_S:-300}"
SWARM_FORMATION_TARGET_TIMEOUT_S="${SWARM_FORMATION_TARGET_TIMEOUT_S:-180}"
SWARM_FORMATION_RUN_LAUNCH_SMOKE="${SWARM_FORMATION_RUN_LAUNCH_SMOKE:-false}"
SWARM_FORMATION_LAUNCH_SMOKE_TIMEOUT_S="${SWARM_FORMATION_LAUNCH_SMOKE_TIMEOUT_S:-75}"
SWARM_FORMATION_WS_NAME="${SWARM_FORMATION_WS_NAME:-swarm_formation_ws_d1_$(date +%Y%m%d_%H%M%S)}"
SWARM_FORMATION_WS="${SWARM_FORMATION_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/${SWARM_FORMATION_WS_NAME}}"

fail() {
  echo "SWARM_FORMATION_D1=FAIL"
  echo "reason=$1"
  exit 1
}

check_executable() {
  local rel="$1"
  [[ -x "${SWARM_FORMATION_WS}/devel/lib/${rel}" ]] || fail "missing_executable:${rel}"
}

copy_pkg() {
  local src_rel="$1"
  local dst_rel="$2"
  local src="${SWARM_FORMATION_ROOT}/src/${src_rel}"
  local dst="${SWARM_FORMATION_WS}/src/${dst_rel}"
  [[ -d "${src}" ]] || fail "source_package_missing:${src_rel}"
  if [[ -e "${dst}" ]]; then
    fail "workspace_destination_exists:${dst}"
  fi
  mkdir -p "$(dirname "${dst}")"
  cp -a "${src}" "${dst}"
}

patch_workspace_for_smoke() {
  python3 - "${SWARM_FORMATION_WS}" <<'PY'
from __future__ import annotations

import sys
from pathlib import Path

ws = Path(sys.argv[1])
for cmake in ws.glob("src/**/CMakeLists.txt"):
    if cmake.is_symlink():
        continue
    text = cmake.read_text(encoding="utf-8", errors="replace")
    text = text.replace('set(CMAKE_BUILD_TYPE "Release")', 'set(CMAKE_BUILD_TYPE "Debug")')
    text = text.replace('SET(CMAKE_BUILD_TYPE Release)', 'SET(CMAKE_BUILD_TYPE Debug)')
    text = text.replace('SET(CMAKE_BUILD_TYPE Release) # Release, RelWithDebInfo', 'SET(CMAKE_BUILD_TYPE Debug) # MoSim D1 smoke build')
    text = text.replace('set(CMAKE_CXX_FLAGS_RELEASE "-O3 -Wall -g")', 'set(CMAKE_CXX_FLAGS_RELEASE "-O0 -g0")')
    if "CMAKE_CXX_FLAGS_DEBUG" not in text:
        text += '\nset(CMAKE_CXX_FLAGS_DEBUG "-O0 -g0")\n'
    cmake.write_text(text, encoding="utf-8")
PY
}

run_build_step() {
  local mode="$1"
  local name="$2"
  shift 2

  echo "build_step=${name}"
  set +e
  timeout --kill-after=10s "$@"
  local code=$?
  set -e

  if [[ "${code}" -eq 0 ]]; then
    echo "build_step_${name}=PASS"
    return 0
  fi

  if [[ "${code}" -eq 124 && "${mode}" == "allow_timeout" ]]; then
    echo "build_step_${name}=TIMEOUT_CONTINUE"
    return 0
  fi

  fail "build_step_failed:${name}:exit_${code}"
}

echo "SWARM_FORMATION_D1=START"
echo "project_root=${PROJECT_ROOT}"
echo "swarm_formation_root=${SWARM_FORMATION_ROOT}"
echo "swarm_formation_ws=${SWARM_FORMATION_WS}"
echo "build_type=${SWARM_FORMATION_BUILD_TYPE}"
echo "build_jobs=${SWARM_FORMATION_BUILD_JOBS}"
echo "build_timeout_s=${SWARM_FORMATION_BUILD_TIMEOUT_S}"
echo "target_timeout_s=${SWARM_FORMATION_TARGET_TIMEOUT_S}"
echo "run_launch_smoke=${SWARM_FORMATION_RUN_LAUNCH_SMOKE}"

[[ -d "${PROJECT_ROOT}" ]] || fail "project_root_missing"
[[ -d "${SWARM_FORMATION_ROOT}" ]] || fail "swarm_formation_root_missing"
[[ -d "${SWARM_FORMATION_ROOT}/src" ]] || fail "swarm_formation_src_missing"
[[ ! -e "${SWARM_FORMATION_WS}" ]] || fail "workspace_already_exists:${SWARM_FORMATION_WS}"

set +u
source /opt/ros/noetic/setup.bash
set -u

mkdir -p "${SWARM_FORMATION_WS}/src"
ln -s /opt/ros/noetic/share/catkin/cmake/toplevel.cmake "${SWARM_FORMATION_WS}/src/CMakeLists.txt"

copy_pkg "Utils/quadrotor_msgs" "Utils/quadrotor_msgs"
copy_pkg "Utils/pose_utils" "Utils/pose_utils"
copy_pkg "Utils/odom_visualization" "Utils/odom_visualization"
copy_pkg "planner/traj_utils" "planner/traj_utils"
copy_pkg "planner/traj_opt" "planner/traj_opt"
copy_pkg "planner/path_searching" "planner/path_searching"
copy_pkg "planner/plan_env" "planner/plan_env"
copy_pkg "planner/swarm_graph" "planner/swarm_graph"
copy_pkg "planner/swarm_bridge" "planner/swarm_bridge"
copy_pkg "planner/plan_manage" "planner/plan_manage"
copy_pkg "uav_simulator/map_generator" "uav_simulator/map_generator"
copy_pkg "uav_simulator/fake_drone" "uav_simulator/fake_drone"
copy_pkg "uav_simulator/local_sensing" "uav_simulator/local_sensing"

patch_workspace_for_smoke

set +e
timeout --kill-after=10s "${SWARM_FORMATION_BUILD_TIMEOUT_S}" \
  catkin_make -C "${SWARM_FORMATION_WS}" \
    -j"${SWARM_FORMATION_BUILD_JOBS}" \
    -DCMAKE_BUILD_TYPE="${SWARM_FORMATION_BUILD_TYPE}" \
    -DCMAKE_CXX_FLAGS_DEBUG="-O0 -g0" \
    >"${SWARM_FORMATION_WS}/catkin_make.log" 2>&1
build_code=$?
set -e

if [[ "${build_code}" -eq 0 ]]; then
  echo "catkin_make=PASS"
elif [[ "${build_code}" -eq 124 && -f "${SWARM_FORMATION_WS}/build/Makefile" ]]; then
  echo "catkin_make=TIMEOUT_CONTINUE"
else
  echo "catkin_make_exit_code=${build_code}"
  tail -120 "${SWARM_FORMATION_WS}/catkin_make.log" || true
  fail "catkin_make_failed_or_timed_out"
fi

run_build_step required bridge_node \
  "${SWARM_FORMATION_TARGET_TIMEOUT_S}" make -C "${SWARM_FORMATION_WS}/build" -j"${SWARM_FORMATION_BUILD_JOBS}" bridge_node
run_build_step required poscmd_2_odom \
  "${SWARM_FORMATION_TARGET_TIMEOUT_S}" make -C "${SWARM_FORMATION_WS}/build" -j"${SWARM_FORMATION_BUILD_JOBS}" poscmd_2_odom
run_build_step required random_forest \
  "${SWARM_FORMATION_TARGET_TIMEOUT_S}" make -C "${SWARM_FORMATION_WS}/build" -j"${SWARM_FORMATION_BUILD_JOBS}" random_forest
run_build_step required pcl_render_node \
  "${SWARM_FORMATION_TARGET_TIMEOUT_S}" make -C "${SWARM_FORMATION_WS}/build" -j"${SWARM_FORMATION_BUILD_JOBS}" pcl_render_node
run_build_step required traj_opt \
  "${SWARM_FORMATION_TARGET_TIMEOUT_S}" make -C "${SWARM_FORMATION_WS}/build" -j"${SWARM_FORMATION_BUILD_JOBS}" traj_opt
run_build_step required ego_planner_node \
  "${SWARM_FORMATION_TARGET_TIMEOUT_S}" make -C "${SWARM_FORMATION_WS}/build" -j"${SWARM_FORMATION_BUILD_JOBS}" ego_planner_node
run_build_step required traj_server \
  "${SWARM_FORMATION_TARGET_TIMEOUT_S}" make -C "${SWARM_FORMATION_WS}/build" -j"${SWARM_FORMATION_BUILD_JOBS}" traj_server

set +u
source "${SWARM_FORMATION_WS}/devel/setup.bash"
set -u

for pkg in \
  ego_planner swarm_bridge traj_utils traj_opt plan_env path_searching swarm_graph \
  quadrotor_msgs pose_utils map_generator local_sensing_node poscmd_2_odom odom_visualization
do
  rospack find "${pkg}" >/dev/null
  echo "rospack_${pkg}=$(rospack find "${pkg}")"
done

check_executable "ego_planner/ego_planner_node"
check_executable "ego_planner/traj_server"
check_executable "swarm_bridge/bridge_node"
check_executable "map_generator/random_forest"
check_executable "poscmd_2_odom/poscmd_2_odom"
check_executable "local_sensing_node/pcl_render_node"

roslaunch ego_planner normal_hexagon.launch --nodes >"${SWARM_FORMATION_WS}/normal_hexagon_nodes.txt"
echo "launch_nodes_normal_hexagon=PASS"

roslaunch ego_planner run_in_sim.launch \
  map_size_x:=10 map_size_y:=10 map_size_z:=3 \
  init_x:=0 init_y:=0 init_z:=0.5 \
  target_x:=2 target_y:=0 target_z:=0.5 \
  drone_id:=0 formation_type:=1 \
  weight_obstacle:=50000 weight_swarm:=50000 weight_feasibility:=10000 \
  weight_sqrvariance:=10000 weight_time:=80 weight_formation:=15000 \
  obstacle_clearance:=0.5 swarm_clearance:=0.5 replan_trajectory_time:=0.1 \
  odom_topic:=visual_slam/odom \
  --nodes >"${SWARM_FORMATION_WS}/run_in_sim_nodes.txt"
echo "launch_nodes_run_in_sim=PASS"

if [[ "${SWARM_FORMATION_RUN_LAUNCH_SMOKE}" == "true" ]]; then
  set +e
  timeout --kill-after=10s "${SWARM_FORMATION_LAUNCH_SMOKE_TIMEOUT_S}" \
    roslaunch ego_planner normal_hexagon.launch \
    >"${SWARM_FORMATION_WS}/normal_hexagon_launch_smoke.log" 2>&1
  smoke_code=$?
  set -e
  echo "launch_smoke_exit_code=${smoke_code}"
  if [[ "${smoke_code}" -ne 124 && "${smoke_code}" -ne 0 ]]; then
    tail -120 "${SWARM_FORMATION_WS}/normal_hexagon_launch_smoke.log" || true
    fail "launch_smoke_failed"
  fi
  echo "launch_smoke=TIMEOUT_EXPECTED_OR_PASS"
else
  echo "launch_smoke=SKIPPED_build_and_parse_only"
fi

echo "SWARM_FORMATION_WS=${SWARM_FORMATION_WS}"
echo "SWARM_FORMATION_D1=PASS"
