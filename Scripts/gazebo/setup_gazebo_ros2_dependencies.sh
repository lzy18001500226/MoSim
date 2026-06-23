#!/usr/bin/env bash
set -euo pipefail

# Default is non-mutating. To install packages, run with:
#   EXECUTE=1 MOSIM_ALLOW_WSL_PACKAGE_INSTALL=1 bash Scripts/gazebo/setup_gazebo_ros2_dependencies.sh

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/dependency_check}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
EXECUTE="${EXECUTE:-0}"
MOSIM_ALLOW_WSL_PACKAGE_INSTALL="${MOSIM_ALLOW_WSL_PACKAGE_INSTALL:-0}"
SKIP_APT_UPDATE="${SKIP_APT_UPDATE:-0}"
PACKAGE_LIST=(
  gz-fortress
  ros-humble-ros-gz-bridge
  ros-humble-ros-gz-sim
)

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_DIR}"

json_array() {
  python3 -c 'import json,sys; print(json.dumps([line.strip() for line in sys.stdin if line.strip()], ensure_ascii=False))'
}

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

write_plan() {
  local mode="$1"
  local status="$2"
  local reason="$3"
  local packages_json
  local candidates_json
  local commands_json
  packages_json="$(printf '%s\n' "${PACKAGE_LIST[@]}" | json_array)"
  candidates_json="$(
    python3 - "$@" <<'PY'
import json
import os
import subprocess

packages = os.environ["PACKAGES"].split(":")
payload = {}
for package in packages:
    proc = subprocess.run(
        ["apt-cache", "policy", package],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    candidate = ""
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("Candidate:"):
            candidate = line.split(":", 1)[1].strip()
            break
    payload[package] = candidate
print(json.dumps(payload, ensure_ascii=False, indent=2))
PY
  )"
  commands_json="$(
    {
      echo "sudo apt-get update"
      printf 'sudo apt-get install -y'
      printf ' %q' "${PACKAGE_LIST[@]}"
      printf '\n'
      echo "bash Scripts/gazebo/check_gazebo_ros2_dependencies.sh"
      echo "RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_LOCAL_MAP=1 RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=1 RUN_STATIC_TF=1 RUN_TF_CHECK=1 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh"
    } | json_array
  )"
  cat > "${RESULT_DIR}/DEPENDENCY_SETUP_PLAN.json" <<JSON
{
  "schema": "mosim.gazebo_ros2_dependency_setup_plan.v1",
  "mode": "${mode}",
  "status": "${status}",
  "reason": "${reason}",
  "packages": ${packages_json},
  "apt_candidates": ${candidates_json},
  "commands": ${commands_json},
  "guards": {
    "execute_required": "EXECUTE=1",
    "install_authorization_required": "MOSIM_ALLOW_WSL_PACKAGE_INSTALL=1",
    "default_is_plan_only": true
  },
  "claim_boundary": [
    "setup only changes WSL packages when both guards are set",
    "setup success does not prove Gazebo runtime or ROS2 topic evidence",
    "runtime evidence still requires RUNTIME_STATUS.json gate_passed=true"
  ]
}
JSON
}

export PACKAGES="$(IFS=:; echo "${PACKAGE_LIST[*]}")"

if [[ "${EXECUTE}" != "1" || "${MOSIM_ALLOW_WSL_PACKAGE_INSTALL}" != "1" ]]; then
  write_plan "plan_only" "not_executed" "missing_execute_or_install_authorization_guard"
  cat "${RESULT_DIR}/DEPENDENCY_SETUP_PLAN.json"
  exit 0
fi

write_plan "execute_requested" "starting" "both_guards_present"

if [[ "${SKIP_APT_UPDATE}" != "1" ]]; then
  sudo apt-get update | tee "${RESULT_DIR}/apt_update.log"
fi

sudo apt-get install -y "${PACKAGE_LIST[@]}" | tee "${RESULT_DIR}/apt_install.log"

if [[ -f "${ROS_SETUP}" ]]; then
  # shellcheck disable=SC1090
  set +u
  source "${ROS_SETUP}"
  set -u
fi

post_blockers=()
gz_after_install="$(command_path gz)"
ign_after_install="$(command_path ign)"
gazebo_sim_cli_path=""
gazebo_sim_cli_command=""
gazebo_sim_cli_kind=""
if [[ -n "${gz_after_install}" ]]; then
  gazebo_sim_cli_path="${gz_after_install}"
  gazebo_sim_cli_command="gz sim"
  gazebo_sim_cli_kind="gz"
elif [[ -n "${ign_after_install}" ]]; then
  gazebo_sim_cli_path="${ign_after_install}"
  gazebo_sim_cli_command="ign gazebo"
  gazebo_sim_cli_kind="ign"
fi
[[ -n "${gazebo_sim_cli_path}" ]] || post_blockers+=("missing_command:gazebo_sim_cli(gz_or_ign)_after_install")
[[ -n "$(command_path ros2)" ]] || post_blockers+=("missing_command:ros2_after_install")
if ! ros2 pkg executables ros_gz_bridge 2>/dev/null | awk '{print $2}' | grep -Fx parameter_bridge >/dev/null 2>&1; then
  post_blockers+=("missing_ros2_executable:ros_gz_bridge/parameter_bridge_after_install")
fi

post_blockers_json="$(printf '%s\n' "${post_blockers[@]:-}" | json_array)"
if [[ "${gazebo_sim_cli_kind}" == "gz" ]]; then
  gazebo_cli_version="$("${gazebo_sim_cli_path}" --version 2>&1 || true)"
elif [[ "${gazebo_sim_cli_kind}" == "ign" ]]; then
  gazebo_cli_version="$("${gazebo_sim_cli_path}" gazebo --versions 2>&1 || "${gazebo_sim_cli_path}" --versions 2>&1 || true)"
else
  gazebo_cli_version=""
fi
ros2_gz_prefix="$(ros2 pkg prefix ros_gz_bridge 2>/dev/null || true)"

cat > "${RESULT_DIR}/DEPENDENCY_SETUP_RESULT.json" <<JSON
{
  "schema": "mosim.gazebo_ros2_dependency_setup_result.v1",
  "status": "$([[ "${#post_blockers[@]}" -eq 0 ]] && echo ready || echo blocked)",
  "packages": $(printf '%s\n' "${PACKAGE_LIST[@]}" | json_array),
  "commands": {
    "gz": "${gz_after_install}",
    "ign": "${ign_after_install}",
    "ros2": "$(command_path ros2)",
    "gazebo_sim_cli_path": "${gazebo_sim_cli_path}",
    "gazebo_sim_cli_command": "${gazebo_sim_cli_command}",
    "gazebo_sim_cli_kind": "${gazebo_sim_cli_kind}"
  },
  "gazebo_cli_version": $(printf '%s' "${gazebo_cli_version}" | json_string),
  "ros_gz_bridge_prefix": "${ros2_gz_prefix}",
  "blockers": ${post_blockers_json},
  "next_check": "bash Scripts/gazebo/check_gazebo_ros2_dependencies.sh",
  "next_runtime_gate": "RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_LOCAL_MAP=1 RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=1 RUN_STATIC_TF=1 RUN_TF_CHECK=1 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh"
}
JSON

cat "${RESULT_DIR}/DEPENDENCY_SETUP_RESULT.json"
