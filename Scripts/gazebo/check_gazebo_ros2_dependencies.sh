#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/dependency_check}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_DIR}"

if [[ -f "${ROS_SETUP}" ]]; then
  # shellcheck disable=SC1090
  set +u
  source "${ROS_SETUP}"
  set -u
fi

json_string() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip(), ensure_ascii=False))'
}

command_path() {
  local name="$1"
  if command -v "${name}" >/dev/null 2>&1; then
    command -v "${name}"
  else
    true
  fi
}

apt_candidate() {
  local package="$1"
  apt-cache policy "${package}" 2>/dev/null | awk '/Candidate:/ {print $2; exit}' || true
}

ros_pkg_prefix() {
  local name="$1"
  if command -v ros2 >/dev/null 2>&1; then
    ros2 pkg prefix "${name}" 2>/dev/null || true
  fi
}

ros_pkg_has_executable() {
  local package="$1"
  local executable="$2"
  if command -v ros2 >/dev/null 2>&1; then
    ros2 pkg executables "${package}" 2>/dev/null | awk '{print $2}' | grep -Fx "${executable}" >/dev/null 2>&1
  else
    return 1
  fi
}

ros2_path="$(command_path ros2)"
colcon_path="$(command_path colcon)"
gz_path="$(command_path gz)"
ign_path="$(command_path ign)"
gazebo_path="$(command_path gazebo)"
ros_gz_bridge_prefix="$(ros_pkg_prefix ros_gz_bridge)"
tf2_ros_prefix="$(ros_pkg_prefix tf2_ros)"
gz_fortress_candidate="$(apt_candidate gz-fortress)"
gz_tools_candidate="$(apt_candidate gz-tools)"
ignition_fortress_candidate="$(apt_candidate ignition-fortress)"
ignition_tools_candidate="$(apt_candidate ignition-tools)"
ros_gz_bridge_candidate="$(apt_candidate ros-humble-ros-gz-bridge)"
ros_ign_bridge_candidate="$(apt_candidate ros-humble-ros-ign-bridge)"
gazebo_candidate="$(apt_candidate gazebo)"
gz_sim_candidate="$(apt_candidate gz-sim)"
gz_harmonic_candidate="$(apt_candidate gz-harmonic)"

gazebo_sim_cli_path=""
gazebo_sim_cli_command=""
gazebo_sim_cli_kind=""
if [[ -n "${gz_path}" ]]; then
  gazebo_sim_cli_path="${gz_path}"
  gazebo_sim_cli_command="gz sim"
  gazebo_sim_cli_kind="gz"
elif [[ -n "${ign_path}" ]]; then
  gazebo_sim_cli_path="${ign_path}"
  gazebo_sim_cli_command="ign gazebo"
  gazebo_sim_cli_kind="ign"
fi

parameter_bridge_available=false
if ros_pkg_has_executable ros_gz_bridge parameter_bridge; then
  parameter_bridge_available=true
fi

static_tf_available=false
if ros_pkg_has_executable tf2_ros static_transform_publisher; then
  static_tf_available=true
fi

osrf_sources="$(grep -R "packages.osrfoundation\|gazebo" /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null || true)"

blockers=()
[[ -f "${ROS_SETUP}" ]] || blockers+=("missing_ros_setup:${ROS_SETUP}")
[[ -n "${ros2_path}" ]] || blockers+=("missing_command:ros2")
[[ -n "${colcon_path}" ]] || blockers+=("missing_command:colcon")
[[ -n "${gazebo_sim_cli_path}" ]] || blockers+=("missing_command:gazebo_sim_cli(gz_or_ign)")
[[ -n "${ros_gz_bridge_prefix}" ]] || blockers+=("missing_ros2_package:ros_gz_bridge")
[[ "${parameter_bridge_available}" == true ]] || blockers+=("missing_ros2_executable:ros_gz_bridge/parameter_bridge")

blockers_json="$(printf '%s\n' "${blockers[@]:-}" | python3 -c 'import json,sys; print(json.dumps([line.strip() for line in sys.stdin if line.strip()], ensure_ascii=False))')"
osrf_sources_json="$(printf '%s' "${osrf_sources}" | json_string)"

cat > "${RESULT_DIR}/DEPENDENCY_STATUS.json" <<JSON
{
  "schema": "mosim.gazebo_ros2_dependency_status.v1",
  "status": "$([[ "${#blockers[@]}" -eq 0 ]] && echo ready || echo blocked)",
  "ros_setup": "${ROS_SETUP}",
  "commands": {
    "ros2": "${ros2_path}",
    "colcon": "${colcon_path}",
    "gz": "${gz_path}",
    "ign": "${ign_path}",
    "gazebo": "${gazebo_path}",
    "gazebo_sim_cli_path": "${gazebo_sim_cli_path}",
    "gazebo_sim_cli_command": "${gazebo_sim_cli_command}",
    "gazebo_sim_cli_kind": "${gazebo_sim_cli_kind}"
  },
  "ros2_packages": {
    "ros_gz_bridge_prefix": "${ros_gz_bridge_prefix}",
    "parameter_bridge_available": ${parameter_bridge_available},
    "tf2_ros_prefix": "${tf2_ros_prefix}",
    "static_transform_publisher_available": ${static_tf_available}
  },
  "apt_candidates": {
    "gz-fortress": "${gz_fortress_candidate}",
    "gz-tools": "${gz_tools_candidate}",
    "ignition-fortress": "${ignition_fortress_candidate}",
    "ignition-tools": "${ignition_tools_candidate}",
    "ros-humble-ros-gz-bridge": "${ros_gz_bridge_candidate}",
    "ros-humble-ros-ign-bridge": "${ros_ign_bridge_candidate}",
    "gazebo": "${gazebo_candidate}",
    "gz-sim": "${gz_sim_candidate}",
    "gz-harmonic": "${gz_harmonic_candidate}"
  },
  "apt_sources": {
    "osrf_or_gazebo_entries": ${osrf_sources_json}
  },
  "blockers": ${blockers_json},
  "recommended_manual_unblock": [
    "Install or source Gazebo Sim so either 'gz sim' or Fortress 'ign gazebo' is available in WSL.",
    "Install ros-humble-ros-gz-bridge so the ros_gz_bridge parameter_bridge executable is available.",
    "Rerun Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh with RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_ACTUATOR_BRIDGE=1 RUN_LOCAL_MAP=1 RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=1 RUN_STATIC_TF=1 RUN_TF_CHECK=1."
  ],
  "safety": "This script is read-only and does not perform package installation, Gazebo launch, ROS2 node launch, or RViz launch."
}
JSON

cat "${RESULT_DIR}/DEPENDENCY_STATUS.json"
