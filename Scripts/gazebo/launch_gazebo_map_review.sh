#!/usr/bin/env bash
# Launch the current single-UAV Gazebo visual review world with WSL GPU defaults
# and project-local model lookup only.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
GAZEBO_ENV_SCRIPT="${GAZEBO_ENV_SCRIPT:-${PROJECT_ROOT}/Scripts/gazebo/setup_gazebo_wsl_env.sh}"
if [[ -f "${GAZEBO_ENV_SCRIPT}" ]]; then
  # shellcheck disable=SC1090
  source "${GAZEBO_ENV_SCRIPT}"
fi

WORLD="${WORLD:-Config/gazebo/worlds/yunzong_planning_test_sunray150_assembled.sdf}"
WORLD_NAME="${WORLD_NAME:-yunzong_planning_test_sunray150_assembled}"
RESULT_ROOT="${RESULT_ROOT:-Results/gazebo_ros2}"
RESULT_DIR="${RESULT_DIR:-${RESULT_ROOT}/gazebo_map_review_$(date +%Y%m%d_%H%M%S)}"
GAZEBO_RENDER_ENGINE="${GAZEBO_RENDER_ENGINE:-ogre}"
GAZEBO_VERBOSE="${GAZEBO_VERBOSE:-2}"
START_PAUSED="${START_PAUSED:-1}"
BACKGROUND="${BACKGROUND:-1}"

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_DIR}"

if declare -F mosim_gazebo_apply_resource_paths >/dev/null 2>&1; then
  mosim_gazebo_apply_resource_paths "Config/gazebo/models"
else
  export GZ_SIM_RESOURCE_PATH="${PROJECT_ROOT}/Config/gazebo/models"
  export IGN_GAZEBO_RESOURCE_PATH="${PROJECT_ROOT}/Config/gazebo/models"
fi

if command -v glxinfo >/dev/null 2>&1; then
  glxinfo -B > "${RESULT_DIR}/glx_renderer.txt" 2>&1 || true
fi

run_flags=()
if [[ "${START_PAUSED}" != "1" ]]; then
  run_flags+=("-r")
fi

cat > "${RESULT_DIR}/launch_env.json" <<JSON
{
  "schema": "mosim.gazebo_map_review_launch_env.v1",
  "world": "${WORLD}",
  "world_name": "${WORLD_NAME}",
  "result_dir": "${RESULT_DIR}",
  "gazebo_render_engine": "${GAZEBO_RENDER_ENGINE}",
  "start_paused": $([[ "${START_PAUSED}" == "1" ]] && echo true || echo false),
  "background": $([[ "${BACKGROUND}" == "1" ]] && echo true || echo false),
  "gz_sim_resource_path": "${GZ_SIM_RESOURCE_PATH:-}",
  "ign_gazebo_resource_path": "${IGN_GAZEBO_RESOURCE_PATH:-}",
  "mesa_d3d12_default_adapter_name": "${MESA_D3D12_DEFAULT_ADAPTER_NAME:-}",
  "glx_vendor_library_name": "${__GLX_VENDOR_LIBRARY_NAME:-}",
  "libgl_always_software": "${LIBGL_ALWAYS_SOFTWARE:-}",
  "mosim_gazebo_inherit_resource_paths": "${MOSIM_GAZEBO_INHERIT_RESOURCE_PATHS:-0}",
  "claim_boundary": "GUI review launch evidence only; this does not prove planner_ready, closed_loop, controller performance, or multi-UAV readiness"
}
JSON

gazebo_cmd=(ign gazebo --render-engine "${GAZEBO_RENDER_ENGINE}" -v "${GAZEBO_VERBOSE}" "${run_flags[@]}" "${WORLD}")

if [[ "${BACKGROUND}" == "1" ]]; then
  if command -v setsid >/dev/null 2>&1; then
    setsid nohup "${gazebo_cmd[@]}" \
      > "${RESULT_DIR}/gazebo.stdout.log" \
      2> "${RESULT_DIR}/gazebo.stderr.log" \
      < /dev/null &
  else
    nohup "${gazebo_cmd[@]}" \
      > "${RESULT_DIR}/gazebo.stdout.log" \
      2> "${RESULT_DIR}/gazebo.stderr.log" \
      < /dev/null &
  fi
  gazebo_pid="$!"
  printf '%s\n' "${gazebo_pid}" > "${RESULT_DIR}/gazebo.pid"
  sleep 1
  running_after_1s=false
  if kill -0 "${gazebo_pid}" >/dev/null 2>&1; then
    running_after_1s=true
  fi
  cat > "${RESULT_DIR}/launch_status.json" <<JSON
{
  "schema": "mosim.gazebo_map_review_launch_status.v1",
  "status": "started_background",
  "pid": ${gazebo_pid},
  "running_after_1s": ${running_after_1s},
  "launch_env": "${RESULT_DIR}/launch_env.json",
  "glx_renderer": "${RESULT_DIR}/glx_renderer.txt",
  "stdout": "${RESULT_DIR}/gazebo.stdout.log",
  "stderr": "${RESULT_DIR}/gazebo.stderr.log"
}
JSON
  printf '%s\n' "${RESULT_DIR}"
else
  exec "${gazebo_cmd[@]}"
fi
