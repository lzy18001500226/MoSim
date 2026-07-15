#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
FUEL_ROOT="${FUEL_ROOT:-${PROJECT_ROOT}/References/Lab/exploration_coverage/FUEL}"
FUEL_DEPS_ROOT="${FUEL_DEPS_ROOT:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/fuel_deps}"
NLOPT_VERSION="${NLOPT_VERSION:-v2.7.1}"
NLOPT_ROOT="${NLOPT_ROOT:-${FUEL_DEPS_ROOT}/install/nlopt-${NLOPT_VERSION}}"
FUEL_BUILD_TYPE="${FUEL_BUILD_TYPE:-Debug}"
FUEL_BUILD_JOBS="${FUEL_BUILD_JOBS:-2}"
FUEL_BUILD_TEST_TOOLS="${FUEL_BUILD_TEST_TOOLS:-OFF}"
FUEL_BUILD_SCOPE="${FUEL_BUILD_SCOPE:-planner_only}"
FUEL_WS_NAME="${FUEL_WS_NAME:-fuel_ws_smoke_debug_notools}"
FUEL_WS="${FUEL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/${FUEL_WS_NAME}}"

fail() {
  echo "FUEL_UPSTREAM_BUILD=FAIL"
  echo "reason=$1"
  exit 1
}

echo "FUEL_UPSTREAM_BUILD=START"
echo "project_root=${PROJECT_ROOT}"
echo "fuel_root=${FUEL_ROOT}"
echo "fuel_ws=${FUEL_WS}"
echo "nlopt_root=${NLOPT_ROOT}"
echo "fuel_build_type=${FUEL_BUILD_TYPE}"
echo "fuel_build_jobs=${FUEL_BUILD_JOBS}"
echo "fuel_build_test_tools=${FUEL_BUILD_TEST_TOOLS}"
echo "fuel_build_scope=${FUEL_BUILD_SCOPE}"

[[ -d "${PROJECT_ROOT}" ]] || fail "project_root_missing"
[[ -d "${FUEL_ROOT}" ]] || fail "fuel_root_missing"
[[ -f "${NLOPT_ROOT}/include/nlopt.hpp" || -f "${NLOPT_ROOT}/include/nlopt.h" ]] \
  || fail "nlopt_header_missing_run_setup_fuel_ros1_dependencies_first"
[[ -f "${NLOPT_ROOT}/lib/libnlopt.so" || -f "${NLOPT_ROOT}/lib64/libnlopt.so" ]] \
  || fail "nlopt_library_missing_run_setup_fuel_ros1_dependencies_first"

set +u
source /opt/ros/noetic/setup.bash
set -u
NLOPT_ROOT="${NLOPT_ROOT}" bash "${PROJECT_ROOT}/Scripts/sunray/check_fuel_ros1_preflight.sh" --strict-build

mkdir -p "${FUEL_WS}/src"

link_or_refresh() {
  local src="$1"
  local dst="$2"
  if [[ -L "${dst}" ]]; then
    unlink "${dst}"
  elif [[ -e "${dst}" ]]; then
    fail "workspace_path_exists_not_symlink:${dst}"
  fi
  ln -s "${src}" "${dst}"
}

link_or_refresh "${FUEL_ROOT}/fuel_planner" "${FUEL_WS}/src/fuel_planner"
case "${FUEL_BUILD_SCOPE}" in
  planner_only)
    link_or_refresh "${FUEL_ROOT}/uav_simulator/Utils/quadrotor_msgs" "${FUEL_WS}/src/quadrotor_msgs"
    ;;
  full)
    link_or_refresh "${FUEL_ROOT}/uav_simulator" "${FUEL_WS}/src/uav_simulator"
    ;;
  *)
    fail "unknown_fuel_build_scope:${FUEL_BUILD_SCOPE}"
    ;;
esac

catkin_make -C "${FUEL_WS}" \
  -j"${FUEL_BUILD_JOBS}" \
  -DCMAKE_BUILD_TYPE="${FUEL_BUILD_TYPE}" \
  -DNLOPT_ROOT="${NLOPT_ROOT}" \
  -DFUEL_BUILD_TEST_TOOLS="${FUEL_BUILD_TEST_TOOLS}"

set +u
source "${FUEL_WS}/devel/setup.bash"
set -u
rospack find exploration_manager >/dev/null
rospack find lkh_tsp_solver >/dev/null
rospack find bspline_opt >/dev/null
rospack find plan_manage >/dev/null

[[ -x "${FUEL_WS}/devel/lib/exploration_manager/exploration_node" ]] \
  || fail "exploration_node_not_built"
[[ -x "${FUEL_WS}/devel/lib/plan_manage/traj_server" ]] \
  || fail "traj_server_not_built"

echo "fuel_exploration_manager=$(rospack find exploration_manager)"
echo "fuel_lkh_tsp_solver=$(rospack find lkh_tsp_solver)"
echo "fuel_plan_manage=$(rospack find plan_manage)"
echo "FUEL_UPSTREAM_BUILD=PASS"
