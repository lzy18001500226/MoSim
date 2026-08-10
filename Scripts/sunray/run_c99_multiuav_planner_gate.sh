#!/usr/bin/env bash
# Run a source-local C99 px4ctrl multi-UAV planner gate without QGC.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
PLANNER_VARIANT="${PLANNER_VARIANT:-diff_planner}"
UAV_NUM="${UAV_NUM:-3}"
RUN_ID="${RUN_ID:-sunray_ros1_graphical_c99_${PLANNER_VARIANT}_${UAV_NUM}uav_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
USER_LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS:-}"
# The source-local C99 multi-UAV route uses the preloaded world by default:
# Gazebo's dynamic spawn path only loaded the first Livox sensor reliably in
# the current runtime. Sequential or staggered dynamic spawn remains an
# explicit diagnostic override for callers that need it.
SEQUENTIAL_SPAWN="${SEQUENTIAL_SPAWN:-false}"
STAGGERED_SPAWN="${STAGGERED_SPAWN:-false}"
STAGGERED_SPAWN_INTERVAL_S="${STAGGERED_SPAWN_INTERVAL_S:-20}"
PRELOAD_GAZEBO_MODELS="${PRELOAD_GAZEBO_MODELS:-true}"
# The current preloaded C99 route exposes MAVROS odometry in the common world
# frame. A deployment that resets each PX4 stream at its own takeoff origin
# can explicitly select the local compatibility path, which translates all
# planner inputs and commands together.
C99_DIFF_TARGET_COORDINATE_FRAME="${C99_DIFF_TARGET_COORDINATE_FRAME:-world}"
C99_DIFF_MAVROS_ODOM_FRAME="${C99_DIFF_MAVROS_ODOM_FRAME:-common_world}"
C99_DIFF_TARGET_CONTRACT_FILE="${C99_DIFF_TARGET_CONTRACT_FILE:-${RESULT_DIR}/c99_diff_target_coordinate_contract.json}"
C99_DIFF_PREPARE_ONLY="${C99_DIFF_PREPARE_ONLY:-false}"
# Keep the multi-UAV route on the accepted graphical-C99 Gazebo thrust map.
# The generic swarm gate defaults to 0.37, which makes this controller climb
# above its 1.0 m AUTO_TAKEOFF target before the planner can take over.
PX4CTRL_HOVER_PERCENTAGE="${PX4CTRL_HOVER_PERCENTAGE:-0.456}"
EGO_GATE_TAKEOFF_HEIGHT="${EGO_GATE_TAKEOFF_HEIGHT:-1.0}"
# The accepted Factory single-UAV handoff keeps publishing the fixed hover
# command while px4ctrl completes AUTO_TAKEOFF. Carry that contract into the
# multi-UAV gate so vehicles do not rise briefly and then fall before Diff
# Planner receives the target.
EGO_GATE_PUBLISH_HOVER_DURING_TAKEOFF="${EGO_GATE_PUBLISH_HOVER_DURING_TAKEOFF:-true}"
EGO_GATE_TARGET_HOLD_S="${EGO_GATE_TARGET_HOLD_S:-5.0}"

die() {
  printf 'BLOCKER %s\n' "$*" >&2
  exit 2
}

case "${C99_DIFF_PREPARE_ONLY}" in
  true|false)
    ;;
  *)
    die "C99_DIFF_PREPARE_ONLY=${C99_DIFF_PREPARE_ONLY}; expected true or false"
    ;;
esac

case "${C99_DIFF_MAVROS_ODOM_FRAME}" in
  common_world)
    C99_DIFF_EXPECTED_COMMON_WORLD_BRIDGE=false
    ;;
  local)
    C99_DIFF_EXPECTED_COMMON_WORLD_BRIDGE=true
    ;;
  *)
    die "unsupported C99_DIFF_MAVROS_ODOM_FRAME=${C99_DIFF_MAVROS_ODOM_FRAME}; expected common_world or local"
    ;;
esac
if [[ -n "${DIFF_GOAL5_COMMON_WORLD_FRAME+x}" && "${DIFF_GOAL5_COMMON_WORLD_FRAME}" != "${C99_DIFF_EXPECTED_COMMON_WORLD_BRIDGE}" ]]; then
  die "DIFF_GOAL5_COMMON_WORLD_FRAME=${DIFF_GOAL5_COMMON_WORLD_FRAME} conflicts with C99_DIFF_MAVROS_ODOM_FRAME=${C99_DIFF_MAVROS_ODOM_FRAME}"
fi
DIFF_GOAL5_COMMON_WORLD_FRAME="${DIFF_GOAL5_COMMON_WORLD_FRAME:-${C99_DIFF_EXPECTED_COMMON_WORLD_BRIDGE}}"

case "${PLANNER_VARIANT}" in
  diff|diff_planner|diff-swarm)
    PLANNER_VARIANT="diff_planner"
    PLANNER_WS="${GOAL4_DIFF_PLANNER_WS:-${PROJECT_ROOT}/build/ros1/diff_planner_ws_c99}"
    PLANNER_PROFILE="diff_planner"
    ;;
  swarm_formation|swarm-formation|formation)
    PLANNER_VARIANT="swarm_formation"
    PLANNER_WS="${SWARM_FORMATION_WS:-${PROJECT_ROOT}/build/ros1/fixed_formation_ws_c99_v3}"
    PLANNER_PROFILE="fixed_formation"
    ;;
  *)
    die "unsupported PLANNER_VARIANT=${PLANNER_VARIANT}; expected diff_planner or swarm_formation"
    ;;
esac

mkdir -p "${RESULT_DIR}"
if ! bash "${PROJECT_ROOT}/Scripts/sunray/check_sunray_ros1_runtime_preflight.sh" \
  > "${RESULT_DIR}/runtime_preflight.log" 2>&1; then
  die "Sunray ROS1 runtime preflight failed; inspect ${RESULT_DIR}/runtime_preflight.log and launch through wsl -d Ubuntu-20.04"
fi

if [[ "${PLANNER_VARIANT}" == "diff_planner" ]]; then
  START1_X="${START1_X:-0.0}"
  START1_Y="${START1_Y:--1.0}"
  START2_X="${START2_X:-0.0}"
  START2_Y="${START2_Y:-1.0}"
  START3_X="${START3_X:--1.5}"
  START3_Y="${START3_Y:-0.0}"
  TARGET1_X="${TARGET1_X:-1.0}"
  TARGET1_Y="${TARGET1_Y:--1.0}"
  TARGET1_Z="${TARGET1_Z:-1.0}"
  TARGET2_X="${TARGET2_X:-1.0}"
  TARGET2_Y="${TARGET2_Y:-1.0}"
  TARGET2_Z="${TARGET2_Z:-1.0}"
  TARGET3_X="${TARGET3_X:-1.0}"
  TARGET3_Y="${TARGET3_Y:-0.0}"
  TARGET3_Z="${TARGET3_Z:-1.0}"
  case "${C99_DIFF_TARGET_COORDINATE_FRAME}" in
    world|local) ;;
    *) die "unsupported C99_DIFF_TARGET_COORDINATE_FRAME=${C99_DIFF_TARGET_COORDINATE_FRAME}; expected world or local" ;;
  esac

  # Keep the original world targets in the contract. The helper selects either
  # identity common-world routing or the legacy local-to-world translation;
  # it does not touch map/sensor parameters or alter the requested destination.
  read -r TARGET1_X TARGET1_Y TARGET1_Z TARGET2_X TARGET2_Y TARGET2_Z TARGET3_X TARGET3_Y TARGET3_Z < <(
    python3 "${PROJECT_ROOT}/Scripts/sunray/write_c99_diff_target_coordinate_contract.py" \
      --source-frame "${C99_DIFF_TARGET_COORDINATE_FRAME}" \
      --mavros-frame "${C99_DIFF_MAVROS_ODOM_FRAME}" \
      --output "${C99_DIFF_TARGET_CONTRACT_FILE}" \
      --starts "${START1_X}" "${START1_Y}" "${START2_X}" "${START2_Y}" "${START3_X}" "${START3_Y}" \
      --targets "${TARGET1_X}" "${TARGET1_Y}" "${TARGET1_Z}" \
      "${TARGET2_X}" "${TARGET2_Y}" "${TARGET2_Z}" \
      "${TARGET3_X}" "${TARGET3_Y}" "${TARGET3_Z}"
  )

  # The shared mission gate is executed in a new Bash process. Re-export the
  # resolved targets and declared frame so it cannot restore incompatible
  # bridge defaults.
  export START1_X START1_Y START2_X START2_Y START3_X START3_Y
  export TARGET1_X TARGET1_Y TARGET1_Z TARGET2_X TARGET2_Y TARGET2_Z TARGET3_X TARGET3_Y TARGET3_Z
fi

source "${PROJECT_ROOT}/Scripts/sunray/resolve_local_ros1_runtime.sh"

if [[ -n "${USER_LIVOX_PLUGIN_WS}" ]]; then
  LIVOX_PLUGIN_WS="${USER_LIVOX_PLUGIN_WS}"
else
  LIVOX_PLUGIN_WS="${PROJECT_ROOT}/build/ros1/livox_swarm_ws_c99"
fi
SUNRAY_LIVOX_PLUGIN_FILENAME="${SUNRAY_LIVOX_PLUGIN_FILENAME:-${LIVOX_PLUGIN_WS}/devel/lib/liblivox_laser_simulation.so}"

bash "${PROJECT_ROOT}/Scripts/sunray/prepare_local_ros1_workspace.sh" \
  --profile "${PLANNER_PROFILE}" \
  --workspace "${PLANNER_WS}" \
  --verify \
  > "${RESULT_DIR}/planner_workspace_verify.log" 2>&1

[[ -f "${PLANNER_WS}/devel/setup.bash" ]] || die "planner workspace is not built: ${PLANNER_WS}/devel/setup.bash"
[[ -f "${LOCAL_ROS1_WS}/devel/setup.bash" ]] || die "local controller workspace is not built: ${LOCAL_ROS1_WS}/devel/setup.bash"

LIVOX_PLUGIN_SOURCE_DIR="${PROJECT_ROOT}/src/simulation/gazebo/plugins/sunray/livox_laser_simulation"
LIVOX_PLUGIN_BINARY="${LIVOX_PLUGIN_WS}/devel/lib/liblivox_laser_simulation.so"
LIVOX_BUILD_ARGS=(--profile foundation --workspace "${LIVOX_PLUGIN_WS}")
if [[ ! -f "${LIVOX_PLUGIN_BINARY}" ]] || find "${LIVOX_PLUGIN_SOURCE_DIR}" -type f -newer "${LIVOX_PLUGIN_BINARY}" -print -quit | grep -q .; then
  LIVOX_BUILD_ARGS+=(--build)
fi
bash "${PROJECT_ROOT}/Scripts/sunray/prepare_local_ros1_workspace.sh" \
  "${LIVOX_BUILD_ARGS[@]}" \
  > "${RESULT_DIR}/livox_workspace_prepare.log" 2>&1

[[ -f "${LIVOX_PLUGIN_BINARY}" ]] \
  || die "project-local Livox plugin binary missing after local foundation preparation: ${LIVOX_PLUGIN_BINARY}"

bash "${PROJECT_ROOT}/Scripts/sunray/prepare_local_ros1_runtime_overlay.sh" \
  --workspace "${SUNRAY_WS}" \
  > "${RESULT_DIR}/local_runtime_overlay.log" 2>&1

if [[ -L "${SUNRAY_WS}/devel" ]]; then
  [[ "$(readlink -f "${SUNRAY_WS}/devel")" == "$(readlink -f "${LOCAL_ROS1_WS}/devel")" ]] \
    || die "runtime overlay devel link targets another workspace: ${SUNRAY_WS}/devel"
elif [[ ! -e "${SUNRAY_WS}/devel" ]]; then
  ln -s "${LOCAL_ROS1_WS}/devel" "${SUNRAY_WS}/devel"
else
  die "runtime overlay devel path is not a generated link: ${SUNRAY_WS}/devel"
fi

PX4CTRL_CORE_PROFILE="graphical_c99"
PX4CTRL_EXPECTED_BUILD_BACKEND="graphical_px4ctrl_c99"
PX4CTRL_CACHE="${LOCAL_ROS1_WS}/build/CMakeCache.txt"
[[ -f "${PX4CTRL_CACHE}" ]] || die "px4ctrl CMake cache is missing: ${PX4CTRL_CACHE}"
PX4CTRL_BUILD_BACKEND="$(sed -n 's/^MOSIM_PX4CTRL_GENERATED_BACKEND:STRING=//p' "${PX4CTRL_CACHE}" | tail -n 1)"
[[ "${PX4CTRL_BUILD_BACKEND}" == "${PX4CTRL_EXPECTED_BUILD_BACKEND}" ]] \
  || die "px4ctrl build backend mismatch: expected ${PX4CTRL_EXPECTED_BUILD_BACKEND}, got ${PX4CTRL_BUILD_BACKEND:-missing}"

cat > "${RESULT_DIR}/c99_multiuav_contract.env" <<EOF
RUN_ID=${RUN_ID}
RESULT_DIR=${RESULT_DIR}
PLANNER_VARIANT=${PLANNER_VARIANT}
UAV_NUM=${UAV_NUM}
C99_DIFF_PREPARE_ONLY=${C99_DIFF_PREPARE_ONLY}
PROJECT_ROOT=${PROJECT_ROOT}
LOCAL_ROS1_WS=${LOCAL_ROS1_WS}
SUNRAY_WS=${SUNRAY_WS}
SUNRAY_PX4_DIR=${SUNRAY_PX4_DIR}
PX4_BUILD_DIR=${PX4_BUILD_DIR}
PX4CTRL_WS=${PX4CTRL_WS}
LIVOX_PLUGIN_WS=${LIVOX_PLUGIN_WS}
PLANNER_WS=${PLANNER_WS}
START1_X=${START1_X:-}
START1_Y=${START1_Y:-}
START2_X=${START2_X:-}
START2_Y=${START2_Y:-}
START3_X=${START3_X:-}
START3_Y=${START3_Y:-}
TARGET1_X=${TARGET1_X:-}
TARGET1_Y=${TARGET1_Y:-}
TARGET1_Z=${TARGET1_Z:-}
TARGET2_X=${TARGET2_X:-}
TARGET2_Y=${TARGET2_Y:-}
TARGET2_Z=${TARGET2_Z:-}
TARGET3_X=${TARGET3_X:-}
TARGET3_Y=${TARGET3_Y:-}
TARGET3_Z=${TARGET3_Z:-}
C99_DIFF_TARGET_COORDINATE_FRAME=${C99_DIFF_TARGET_COORDINATE_FRAME}
C99_DIFF_MAVROS_ODOM_FRAME=${C99_DIFF_MAVROS_ODOM_FRAME}
C99_DIFF_TARGET_CONTRACT_FILE=${C99_DIFF_TARGET_CONTRACT_FILE}
DIFF_GOAL5_COMMON_WORLD_FRAME=${DIFF_GOAL5_COMMON_WORLD_FRAME}
SEQUENTIAL_SPAWN=${SEQUENTIAL_SPAWN}
STAGGERED_SPAWN=${STAGGERED_SPAWN}
STAGGERED_SPAWN_INTERVAL_S=${STAGGERED_SPAWN_INTERVAL_S}
PRELOAD_GAZEBO_MODELS=${PRELOAD_GAZEBO_MODELS}
SUNRAY_LIVOX_PLUGIN_FILENAME=${SUNRAY_LIVOX_PLUGIN_FILENAME}
PX4CTRL_CORE_PROFILE=${PX4CTRL_CORE_PROFILE}
PX4CTRL_EXPECTED_BUILD_BACKEND=${PX4CTRL_EXPECTED_BUILD_BACKEND}
PX4CTRL_BUILD_BACKEND=${PX4CTRL_BUILD_BACKEND}
PX4CTRL_HOVER_PERCENTAGE=${PX4CTRL_HOVER_PERCENTAGE}
EGO_GATE_TAKEOFF_HEIGHT=${EGO_GATE_TAKEOFF_HEIGHT}
EGO_GATE_PUBLISH_HOVER_DURING_TAKEOFF=${EGO_GATE_PUBLISH_HOVER_DURING_TAKEOFF}
EGO_GATE_TARGET_HOLD_S=${EGO_GATE_TARGET_HOLD_S}
WORLD_FILE=${WORLD_FILE:-}
SUNRAY_GAZEBO_LAUNCH_FILE=${SUNRAY_GAZEBO_LAUNCH_FILE:-}
FACTORY_L2_MODEL_PATH=${FACTORY_L2_MODEL_PATH:-}
FACTORY_L2_CONFIG_MODEL_PATH=${FACTORY_L2_CONFIG_MODEL_PATH:-}
GOAL5_FACTORY_MODEL_PATH_MODE=${GOAL5_FACTORY_MODEL_PATH_MODE:-}
GAZEBO_MODEL_PATH=${GAZEBO_MODEL_PATH:-}
QGC=disabled
EOF

if [[ "${C99_DIFF_PREPARE_ONLY}" == "true" ]]; then
  python3 - "${RESULT_DIR}/C99_DIFF_PREPARE_STATUS.json" \
    "${RUN_ID}" "${RESULT_DIR}" "${PLANNER_VARIANT}" "${UAV_NUM}" \
    "${C99_DIFF_TARGET_CONTRACT_FILE}" "${PLANNER_WS}" "${PX4CTRL_BUILD_BACKEND}" <<'PY'
import json
import sys
from pathlib import Path

output = Path(sys.argv[1])
packet = {
    "schema": "mosim.sunray_ros1.c99_diff_prepare_status.v1",
    "status": "passed",
    "run_id": sys.argv[2],
    "result_dir": sys.argv[3],
    "planner_variant": sys.argv[4],
    "uav_num": int(sys.argv[5]),
    "target_coordinate_contract": sys.argv[6],
    "planner_workspace": sys.argv[7],
    "px4ctrl_build_backend": sys.argv[8],
    "claim_boundary": "Preparation only: runtime lane preflight, local workspaces, overlay, controller backend, and coordinate contract passed. No Gazebo, PX4, MAVROS, planner, mission, or RViz runtime is claimed.",
}
output.write_text(json.dumps(packet, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
PY
  echo "${RESULT_DIR}"
  exit 0
fi

export RUN_ID RESULT_DIR PLANNER_VARIANT UAV_NUM LIVOX_PLUGIN_WS SUNRAY_LIVOX_PLUGIN_FILENAME
export SEQUENTIAL_SPAWN STAGGERED_SPAWN STAGGERED_SPAWN_INTERVAL_S
export PRELOAD_GAZEBO_MODELS
export C99_DIFF_TARGET_COORDINATE_FRAME C99_DIFF_TARGET_CONTRACT_FILE
export C99_DIFF_MAVROS_ODOM_FRAME
export DIFF_GOAL5_COMMON_WORLD_FRAME
export PX4CTRL_CORE_PROFILE PX4CTRL_EXPECTED_BUILD_BACKEND
export PX4CTRL_HOVER_PERCENTAGE EGO_GATE_TAKEOFF_HEIGHT
export EGO_GATE_PUBLISH_HOVER_DURING_TAKEOFF EGO_GATE_TARGET_HOLD_S
export GOAL4_DIFF_PLANNER_WS="${GOAL4_DIFF_PLANNER_WS:-${PLANNER_WS}}"
export SWARM_FORMATION_WS="${SWARM_FORMATION_WS:-${PLANNER_WS}}"
export GUI=false
export OPEN_RVIZ=false
export UE_LIVE_MIRROR_ENABLE=false
export KEEP_ALIVE=false
export GOAL5_STARTUP_ATTEMPTS="${GOAL5_STARTUP_ATTEMPTS:-1}"

exec bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh"
