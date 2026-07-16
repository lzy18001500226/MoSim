#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
OPERATION_ID="${1:-}"
RUN_ID="${2:-}"

if [[ ! "${RUN_ID}" =~ ^run-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$ ]]; then
  echo "invalid run_id" >&2
  exit 2
fi

ORCHESTRATOR_RUN_DIR="${PROJECT_ROOT}/Results/ui_platform/orchestrator_runs/${RUN_ID}"
mkdir -p -- "${ORCHESTRATOR_RUN_DIR}"
printf '%s\n' "$$" > "${ORCHESTRATOR_RUN_DIR}/runtime_linux_pid.txt"

SIDECAR_PID=""
RUNTIME_CHILD_PID=""
cleanup() {
  set +e
  if [[ -n "${SIDECAR_PID}" ]]; then
    kill -TERM "${SIDECAR_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${RUNTIME_CHILD_PID}" ]]; then
    kill -TERM "${RUNTIME_CHILD_PID}" >/dev/null 2>&1 || true
  fi
  wait "${SIDECAR_PID}" >/dev/null 2>&1 || true
  wait "${RUNTIME_CHILD_PID}" >/dev/null 2>&1 || true
}
trap cleanup EXIT TERM INT

assert_no_conflicting_runtime() {
  local conflicts=()
  pgrep -x gzserver >/dev/null 2>&1 && conflicts+=("gzserver")
  pgrep -f '[r]osmaster --core' >/dev/null 2>&1 && conflicts+=("rosmaster")
  pgrep -f '/bin/[p]x4 ' >/dev/null 2>&1 && conflicts+=("px4")
  pgrep -f '[m]avros/mavros_node' >/dev/null 2>&1 && conflicts+=("mavros")
  pgrep -f '[r]un_px4ctrl_(basic|ego_swarm)_gate\.sh' >/dev/null 2>&1 && conflicts+=("sunray_gate")
  if (( ${#conflicts[@]} > 0 )); then
    printf 'Sunray ROS1 runtime process conflict: %s\n' "$(IFS=,; echo "${conflicts[*]}")" >&2
    return 11
  fi
}

start_sidecar() {
  local vehicle_count="${1:-1}"
  set +u
  source /opt/ros/noetic/setup.bash
  [[ -f /opt/mosim_work/sunray_ws/Sunray/devel/setup.bash ]] && source /opt/mosim_work/sunray_ws/Sunray/devel/setup.bash
  [[ -f "${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash" ]] && \
    source "${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash"
  set -u
  python3 -u "${PROJECT_ROOT}/Scripts/ui/runtime_sidecar.py" \
    --run-dir "${ORCHESTRATOR_RUN_DIR}" \
    --manifest "${ORCHESTRATOR_RUN_DIR}/RUN_MANIFEST.json" \
    --contract "${PROJECT_ROOT}/Config/control_platform/factory_injection_contract.json" \
    --vehicle-count "${vehicle_count}" \
    --body-name "uav1::base_link" \
    > "${ORCHESTRATOR_RUN_DIR}/runtime_sidecar.log" 2>&1 &
  SIDECAR_PID="$!"
  printf '%s\n' "${SIDECAR_PID}" > "${ORCHESTRATOR_RUN_DIR}/runtime_sidecar_pid.txt"
}

run_basic_gate() {
  local controller_profile="$1"
  assert_no_conflicting_runtime
  local plugin_ws="${PROJECT_ROOT}/Results/control_platform/p7_ftc_gazebo_plugin_ws_v2"
  local plugin_library="${plugin_ws}/devel/lib/libmosim_gazebo_ftc_actuator_plugin.so"
  if [[ ! -f "${plugin_library}" ]]; then
    FTC_PLUGIN_WS="${plugin_ws}" bash "${PROJECT_ROOT}/Scripts/sunray/build_p7_ftc_actuator_plugin.sh" \
      > "${ORCHESTRATOR_RUN_DIR}/ftc_plugin_build.log" 2>&1
  fi
  local factory_root="${PROJECT_ROOT}/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean"
  export RUN_ID="${RUN_ID}"
  export RESULT_DIR="${ORCHESTRATOR_RUN_DIR}/runtime"
  export PX4CTRL_CORE_PROFILE="${controller_profile}"
  export GUI="false"
  export KEEP_ALIVE="false"
  export WORLD_FILE="${factory_root}/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf"
  export SUNRAY_GAZEBO_LAUNCH_FILE="${PROJECT_ROOT}/Scripts/sunray/factory_l2_sunray_px4_gazebo.launch"
  export GAZEBO_MODEL_PATH="${factory_root}/models:${GAZEBO_MODEL_PATH:-}"
  export SUNRAY_UAV_INIT_X="-10.575025"
  export SUNRAY_UAV_INIT_Y="-19.36313"
  export SUNRAY_UAV_INIT_Z="0.2"
  export MOSIM_ENABLE_FTC_ACTUATOR_PLUGIN="true"
  export GAZEBO_PLUGIN_PATH="${plugin_ws}/devel/lib:${GAZEBO_PLUGIN_PATH:-}"
  export LD_LIBRARY_PATH="${plugin_ws}/devel/lib:${LD_LIBRARY_PATH:-}"
  start_sidecar 1
  bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" figure8 &
  RUNTIME_CHILD_PID="$!"
  set +e
  wait "${RUNTIME_CHILD_PID}"
  local exit_code="$?"
  set -e
  RUNTIME_CHILD_PID=""
  return "${exit_code}"
}

run_swarm_formation_gate() {
  assert_no_conflicting_runtime
  local plugin_ws="${PROJECT_ROOT}/Results/control_platform/p7_ftc_gazebo_plugin_ws_v2"
  local plugin_library="${plugin_ws}/devel/lib/libmosim_gazebo_ftc_actuator_plugin.so"
  if [[ ! -f "${plugin_library}" ]]; then
    FTC_PLUGIN_WS="${plugin_ws}" bash "${PROJECT_ROOT}/Scripts/sunray/build_p7_ftc_actuator_plugin.sh" \
      > "${ORCHESTRATOR_RUN_DIR}/ftc_plugin_build.log" 2>&1
  fi
  local factory_root="${PROJECT_ROOT}/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean"
  export RUN_ID="${RUN_ID}"
  export RESULT_DIR="${ORCHESTRATOR_RUN_DIR}/runtime"
  export PLANNER_VARIANT="swarm_formation"
  export UAV_NUM="3"
  export GUI="false"
  export KEEP_ALIVE="false"
  export WORLD_FILE="${factory_root}/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf"
  export GAZEBO_MODEL_PATH="${factory_root}/models:${GAZEBO_MODEL_PATH:-}"
  export MOSIM_ENABLE_FTC_ACTUATOR_PLUGIN="true"
  export GAZEBO_PLUGIN_PATH="${plugin_ws}/devel/lib:${GAZEBO_PLUGIN_PATH:-}"
  export LD_LIBRARY_PATH="${plugin_ws}/devel/lib:${LD_LIBRARY_PATH:-}"
  export TOTAL_TIMEOUT_S="600"
  export EGO_GATE_EGO_TAKEOVER_TIMEOUT_S="120"
  export EGO_GATE_EXECUTE_TIMEOUT_S="420"
  export SWARM_FORMATION_D3_CENTER_X="-16.679266719908025"
  export SWARM_FORMATION_D3_CENTER_Y="-8.0868185505691"
  export SWARM_FORMATION_D3_CENTER_Z="1.2"
  export SWARM_FORMATION_D3_SWARM_SCALE="0.75"
  export SWARM_FORMATION_D3_SWARM_CLEARANCE="1.0"
  export SWARM_FORMATION_D3_MIN_TRAJ_Z="0.90"
  export SWARM_FORMATION_D3_MAX_TRAJ_Z="1.60"
  export SWARM_FORMATION_D3_WEIGHT_HEIGHT="50000.0"
  export SWARM_FORMATION_D3_MAP_SIZE_X="64.0"
  export SWARM_FORMATION_D3_MAP_SIZE_Y="64.0"
  export SWARM_FORMATION_D3_MAP_SIZE_Z="3.0"
  export SWARM_FORMATION_D3_GRID_RESOLUTION="0.20"
  export SWARM_FORMATION_D3_OBSTACLES_INFLATION="0.20"
  export SWARM_FORMATION_D3_LOCAL_UPDATE_RANGE_XY="8.0"
  export SWARM_FORMATION_D3_LEADER_FOLLOWER_COMMANDS="true"
  start_sidecar 3
  bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh" &
  RUNTIME_CHILD_PID="$!"
  set +e
  wait "${RUNTIME_CHILD_PID}"
  local exit_code="$?"
  set -e
  RUNTIME_CHILD_PID=""
  return "${exit_code}"
}

case "${OPERATION_ID}" in
  px4ctrl_figure8_single)
    run_basic_gate original
    ;;
  cascade_pid_figure8_single)
    run_basic_gate cascade_pid
    ;;
  factory_l2_three_uav_swarm_formation)
    run_swarm_formation_gate
    ;;
  *)
    echo "operation is not allowlisted: ${OPERATION_ID}" >&2
    exit 2
    ;;
esac
