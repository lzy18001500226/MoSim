#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
GAZEBO_ENV_SCRIPT="${GAZEBO_ENV_SCRIPT:-${PROJECT_ROOT}/Scripts/gazebo/setup_gazebo_wsl_env.sh}"
if [[ -f "${GAZEBO_ENV_SCRIPT}" ]]; then
  # shellcheck disable=SC1090
  source "${GAZEBO_ENV_SCRIPT}"
fi
WORLD="${WORLD:-Config/gazebo/worlds/factory_minimal.sdf}"
WORLD_NAME="${WORLD_NAME:-mosim_factory_minimal}"
RESULT_ROOT="${RESULT_ROOT:-Results/gazebo_ros2}"
GAZEBO_RENDER_ENGINE_SERVER="${GAZEBO_RENDER_ENGINE_SERVER:-ogre}"

cd "${PROJECT_ROOT}"

timestamp="$(date +%Y%m%d_%H%M%S)"
result_dir="${RESULT_ROOT}/paused_control_probe_${timestamp}"
mkdir -p "${result_dir}"

if declare -F mosim_gazebo_apply_resource_paths >/dev/null 2>&1; then
  mosim_gazebo_apply_resource_paths
else
  export GZ_SIM_RESOURCE_PATH="${PROJECT_ROOT}/Config/gazebo/models"
  export IGN_GAZEBO_RESOURCE_PATH="${PROJECT_ROOT}/Config/gazebo/models"
fi

ign gazebo -s --headless-rendering --render-engine-server "${GAZEBO_RENDER_ENGINE_SERVER}" "${WORLD}" \
  > "${result_dir}/gazebo.stdout.log" \
  2> "${result_dir}/gazebo.stderr.log" &
gazebo_pid="$!"

cleanup() {
  if kill -0 "${gazebo_pid}" >/dev/null 2>&1; then
    kill "${gazebo_pid}" >/dev/null 2>&1 || true
    wait "${gazebo_pid}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

sleep 3

ign service -l > "${result_dir}/services.txt"
grep -E "/world/.*/control|${WORLD_NAME}" "${result_dir}/services.txt" \
  > "${result_dir}/services_control_subset.txt" || true

ign service -i -s "/world/${WORLD_NAME}/control" \
  > "${result_dir}/control_info.txt" \
  2> "${result_dir}/control_info.stderr.txt" || true

ign service \
  -s "/world/${WORLD_NAME}/control" \
  --reqtype ignition.msgs.WorldControl \
  --reptype ignition.msgs.Boolean \
  --timeout 1000 \
  --req "pause: false" \
  > "${result_dir}/unpause_response.txt" \
  2> "${result_dir}/unpause_response.stderr.txt" || true

printf '%s\n' "${result_dir}"
