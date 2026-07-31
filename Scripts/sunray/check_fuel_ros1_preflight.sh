#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
FUEL_ROOT="${FUEL_ROOT:-${PROJECT_ROOT}/src/planning/fuel}"
STRICT_BUILD=0

fail() {
  echo "FUEL_ROS1_PREFLIGHT=FAIL"
  echo "reason=$1"
  exit 1
}

warn() {
  echo "warning=$1"
}

for arg in "$@"; do
  case "${arg}" in
    --strict-build)
      STRICT_BUILD=1
      ;;
    -h|--help)
      cat <<'EOF'
Usage: bash Scripts/sunray/check_fuel_ros1_preflight.sh [--strict-build]

Checks the local FUEL ROS1/Noetic source and environment without starting
roscore, Gazebo or RViz.

--strict-build  Treat missing build-time dependencies such as LKH and the
                upstream hard-coded /usr/local/lib/libnlopt.so as blockers.
EOF
      exit 0
      ;;
    *)
      fail "unknown_arg:${arg}"
      ;;
  esac
done

echo "FUEL_ROS1_PREFLIGHT=START"
echo "project_root=${PROJECT_ROOT}"
echo "fuel_root=${FUEL_ROOT}"
echo "strict_build=${STRICT_BUILD}"

if ! command -v lsb_release >/dev/null 2>&1; then
  fail "lsb_release_missing"
fi

ubuntu_version="$(lsb_release -rs || true)"
echo "ubuntu_version=${ubuntu_version}"
if [[ "${ubuntu_version}" != "20.04" ]]; then
  fail "wrong_ubuntu_version_expected_20.04"
fi

if [[ ! -f /opt/ros/noetic/setup.bash ]]; then
  fail "ros_noetic_missing"
fi

set +u
source /opt/ros/noetic/setup.bash
set -u
echo "ros_distro=${ROS_DISTRO:-unset}"
if [[ "${ROS_DISTRO:-}" != "noetic" ]]; then
  fail "wrong_ros_distro_expected_noetic"
fi

[[ -d "${PROJECT_ROOT}" ]] || fail "project_root_missing"
[[ -d "${FUEL_ROOT}" ]] || fail "fuel_root_missing"

required_paths=(
  "README.md"
  "fuel_planner/exploration_manager/launch/exploration.launch"
  "fuel_planner/exploration_manager/launch/algorithm.xml"
  "fuel_planner/exploration_manager/launch/rviz.launch"
  "fuel_planner/plan_manage/launch/kino_replan.launch"
  "fuel_planner/bspline/msg/Bspline.msg"
  "uav_simulator/map_generator/package.xml"
  "uav_simulator/local_sensing/package.xml"
  "uav_simulator/Utils/quadrotor_msgs/msg/PositionCommand.msg"
  "fuel_planner/utils/lkh_tsp_solver/CMakeLists.txt"
  "fuel_planner/utils/lkh_tsp_solver/include/lkh_tsp_solver/lkh_interface.h"
)

for rel in "${required_paths[@]}"; do
  if [[ ! -e "${FUEL_ROOT}/${rel}" ]]; then
    fail "missing_fuel_path:${rel}"
  fi
done

required_commands=(cmake make rospack catkin_make pkg-config)
for cmd in "${required_commands[@]}"; do
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    fail "missing_command:${cmd}"
  fi
done

if command -v LKH >/dev/null 2>&1; then
  echo "system_LKH_command=present"
else
  warn "system_LKH_command_missing_but_fuel_builds_repo_local_lkh_tsp_solver"
fi

pkg_config_missing=0
for pkg in armadillo nlopt; do
  if ! pkg-config --exists "${pkg}" >/dev/null 2>&1; then
    warn "pkg_config_missing:${pkg}"
    pkg_config_missing=1
  else
    echo "pkg_config_${pkg}=present"
  fi
done

if [[ "${pkg_config_missing}" -ne 0 ]]; then
  warn "missing_pkg_config_entries_do_not_prove_library_absence_check_apt_or_cmake_when_building"
fi

if [[ "${STRICT_BUILD}" -eq 1 ]]; then
  nlopt_include_candidates=()
  nlopt_lib_candidates=()
  if [[ -n "${NLOPT_ROOT:-}" ]]; then
    nlopt_include_candidates+=("${NLOPT_ROOT}/include/nlopt.hpp" "${NLOPT_ROOT}/include/nlopt.h")
    nlopt_lib_candidates+=("${NLOPT_ROOT}/lib/libnlopt.so" "${NLOPT_ROOT}/lib64/libnlopt.so")
  fi
  nlopt_include_candidates+=(
    "/usr/local/include/nlopt.hpp"
    "/usr/local/include/nlopt.h"
    "/usr/include/nlopt.hpp"
    "/usr/include/nlopt.h"
  )
  nlopt_lib_candidates+=(
    "/usr/local/lib/libnlopt.so"
    "/usr/lib/x86_64-linux-gnu/libnlopt.so"
    "/usr/lib/libnlopt.so"
  )

  nlopt_include_found=0
  for candidate in "${nlopt_include_candidates[@]}"; do
    if [[ -f "${candidate}" ]]; then
      echo "nlopt_include=${candidate}"
      nlopt_include_found=1
      break
    fi
  done
  [[ "${nlopt_include_found}" -eq 1 ]] || fail "missing_nlopt_header_or_cpp_header"

  nlopt_lib_found=0
  for candidate in "${nlopt_lib_candidates[@]}"; do
    if [[ -f "${candidate}" ]]; then
      echo "nlopt_library=${candidate}"
      nlopt_lib_found=1
      break
    fi
  done
  [[ "${nlopt_lib_found}" -eq 1 ]] || fail "missing_nlopt_library"
fi

echo "fuel_readme_present=1"
echo "fuel_exploration_launch=${FUEL_ROOT}/fuel_planner/exploration_manager/launch/exploration.launch"
echo "fuel_algorithm_launch=${FUEL_ROOT}/fuel_planner/exploration_manager/launch/algorithm.xml"
echo "FUEL_ROS1_PREFLIGHT=PASS"
