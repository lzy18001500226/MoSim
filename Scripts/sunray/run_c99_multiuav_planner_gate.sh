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

die() {
  printf 'BLOCKER %s\n' "$*" >&2
  exit 2
}

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

source "${PROJECT_ROOT}/Scripts/sunray/resolve_local_ros1_runtime.sh"

if [[ -n "${USER_LIVOX_PLUGIN_WS}" ]]; then
  LIVOX_PLUGIN_WS="${USER_LIVOX_PLUGIN_WS}"
else
  LIVOX_PLUGIN_WS="${PROJECT_ROOT}/build/ros1/livox_swarm_ws_c99"
fi

mkdir -p "${RESULT_DIR}"

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
PROJECT_ROOT=${PROJECT_ROOT}
LOCAL_ROS1_WS=${LOCAL_ROS1_WS}
SUNRAY_WS=${SUNRAY_WS}
SUNRAY_PX4_DIR=${SUNRAY_PX4_DIR}
PX4_BUILD_DIR=${PX4_BUILD_DIR}
PX4CTRL_WS=${PX4CTRL_WS}
LIVOX_PLUGIN_WS=${LIVOX_PLUGIN_WS}
PLANNER_WS=${PLANNER_WS}
PX4CTRL_CORE_PROFILE=${PX4CTRL_CORE_PROFILE}
PX4CTRL_EXPECTED_BUILD_BACKEND=${PX4CTRL_EXPECTED_BUILD_BACKEND}
PX4CTRL_BUILD_BACKEND=${PX4CTRL_BUILD_BACKEND}
QGC=disabled
EOF

export RUN_ID RESULT_DIR PLANNER_VARIANT UAV_NUM LIVOX_PLUGIN_WS
export PX4CTRL_CORE_PROFILE PX4CTRL_EXPECTED_BUILD_BACKEND
export GOAL4_DIFF_PLANNER_WS="${GOAL4_DIFF_PLANNER_WS:-${PLANNER_WS}}"
export SWARM_FORMATION_WS="${SWARM_FORMATION_WS:-${PLANNER_WS}}"
export GUI=false
export OPEN_RVIZ=false
export UE_LIVE_MIRROR_ENABLE=false
export KEEP_ALIVE=false
export GOAL5_STARTUP_ATTEMPTS="${GOAL5_STARTUP_ATTEMPTS:-1}"

exec bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh"
