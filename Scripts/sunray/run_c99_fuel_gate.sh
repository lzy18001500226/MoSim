#!/usr/bin/env bash
# Run the source-local FUEL gate on the graphical C99 px4ctrl backend.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
EXECUTE_S="${1:-45}"
RUN_ID="${RUN_ID:-sunray_ros1_graphical_c99_fuel_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
GOAL4_FUEL_WS="${GOAL4_FUEL_WS:-${PROJECT_ROOT}/build/ros1/fuel_ws_c99}"
# Keep FAST-LIO in a dedicated generated Catkin workspace.  The controller
# workspace already owns the source-local packages below `perception/`; adding
# legacy top-level aliases there makes Catkin discover each package twice.
FASTLIO_WS="${FUEL_FASTLIO_WS:-${PROJECT_ROOT}/build/ros1/fastlio_fuel_c99_ws}"
FASTLIO_SRC="${FASTLIO_SRC:-${PROJECT_ROOT}/src/perception/fast_lio}"
LIVOX_COMPAT_SRC="${LIVOX_COMPAT_SRC:-${PROJECT_ROOT}/src/perception/livox_ros_driver_compat}"

die() {
  printf 'BLOCKER %s\n' "$*" >&2
  exit 2
}

source "${PROJECT_ROOT}/Scripts/sunray/resolve_local_ros1_runtime.sh"
# Do not allow the generic runtime gate to fall back to the historical audit
# workspace. The C99 route must launch the controller built from this source
# tree, and the selected workspace must remain visible in the run contract.
PX4CTRL_WS="${PX4CTRL_WS:-${LOCAL_ROS1_WS}}"
export PX4CTRL_WS
mkdir -p "${RESULT_DIR}"

prepare_source_local_fastlio_workspace() {
  local local_src="${LOCAL_ROS1_WS}/src"
  local catkin_toplevel="/opt/ros/noetic/share/catkin/cmake/toplevel.cmake"
  local catkin_link="${FASTLIO_WS}/src/CMakeLists.txt"
  local legacy_link

  [[ -f "${FASTLIO_SRC}/package.xml" ]] || die "FAST-LIO source is missing: ${FASTLIO_SRC}"
  [[ -f "${LIVOX_COMPAT_SRC}/package.xml" ]] || die "Livox compatibility source is missing: ${LIVOX_COMPAT_SRC}"
  [[ -f "${catkin_toplevel}" ]] || die "Catkin toplevel is missing: ${catkin_toplevel}"

  {
    echo "LOCAL_ROS1_WS=${LOCAL_ROS1_WS}"
    echo "FASTLIO_WS=${FASTLIO_WS}"
    echo "FASTLIO_SRC=${FASTLIO_SRC}"
    echo "LIVOX_COMPAT_SRC=${LIVOX_COMPAT_SRC}"
    for legacy_link in FAST_LIO livox_ros_driver_compat; do
      local legacy_path="${local_src}/${legacy_link}"
      if [[ -L "${legacy_path}" ]]; then
        echo "removed_stale_generated_link=${legacy_path}->$(readlink -f "${legacy_path}")"
        rm -f "${legacy_path}"
      elif [[ -e "${legacy_path}" ]]; then
        echo "unexpected_nonlink=${legacy_path}"
        return 2
      else
        echo "no_stale_generated_link=${legacy_path}"
      fi
    done

    mkdir -p "${FASTLIO_WS}/src"
    if [[ -L "${catkin_link}" ]]; then
      [[ "$(readlink -f "${catkin_link}")" == "$(readlink -f "${catkin_toplevel}")" ]] || return 2
      echo "reused_fastlio_catkin_link=${catkin_link}"
    elif [[ -e "${catkin_link}" ]]; then
      echo "unexpected_fastlio_catkin_file=${catkin_link}"
      return 2
    else
      ln -s "${catkin_toplevel}" "${catkin_link}"
      echo "created_fastlio_catkin_link=${catkin_link}"
    fi
  } > "${RESULT_DIR}/fastlio_workspace_source_guard.txt"
}

prepare_source_local_fastlio_workspace || die "FAST-LIO generated workspace guard failed"

bash "${PROJECT_ROOT}/Scripts/sunray/prepare_local_ros1_workspace.sh" \
  --profile fuel \
  --workspace "${GOAL4_FUEL_WS}" \
  --verify \
  > "${RESULT_DIR}/fuel_workspace_verify.log" 2>&1

[[ -f "${GOAL4_FUEL_WS}/devel/setup.bash" ]] || die "FUEL workspace is not built: ${GOAL4_FUEL_WS}/devel/setup.bash"
[[ -f "${LOCAL_ROS1_WS}/devel/setup.bash" ]] || die "local controller workspace is not built: ${LOCAL_ROS1_WS}/devel/setup.bash"

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
# Freeze the source-local C99 FUEL launch to the historical FUEL flight
# baseline. These are controller/startup settings only; planner and perception
# parameters remain owned by the existing FUEL configuration.
PX4CTRL_HOVER_PERCENTAGE="${PX4CTRL_HOVER_PERCENTAGE:-0.456}"
PX4CTRL_AUTO_TAKEOFF_HEIGHT="${PX4CTRL_AUTO_TAKEOFF_HEIGHT:-1.0}"
PX4CTRL_KP_XY="${PX4CTRL_KP_XY:-11}"
PX4CTRL_KP_Z="${PX4CTRL_KP_Z:-4}"
PX4CTRL_KV_XY="${PX4CTRL_KV_XY:-6.5}"
PX4CTRL_KV_Z="${PX4CTRL_KV_Z:-4}"
PX4CTRL_START_EXTERNAL_FUSION="${PX4CTRL_START_EXTERNAL_FUSION:-true}"
PX4CTRL_ENABLE_FASTLIO_EKF_FUSION="${PX4CTRL_ENABLE_FASTLIO_EKF_FUSION:-false}"
PX4CTRL_FASTLIO_ODOMETRY_FUSION_ENABLED="${PX4CTRL_FASTLIO_ODOMETRY_FUSION_ENABLED:-false}"
PX4CTRL_FASTLIO_VELOCITY_FUSION_ENABLED="${PX4CTRL_FASTLIO_VELOCITY_FUSION_ENABLED:-false}"
# The accepted original FUEL run did not add top-level EKF overrides. Preserve
# an explicit caller override, but otherwise keep this C99 FUEL route empty.
PX4CTRL_EKF2_EV_CTRL_OVERRIDE="${PX4CTRL_EKF2_EV_CTRL_OVERRIDE-}"
PX4CTRL_EKF2_HGT_REF_OVERRIDE="${PX4CTRL_EKF2_HGT_REF_OVERRIDE-}"
# The historical Factory FUEL baseline uses the Mid-360 simulator downsample
# of eight. This only bounds Gazebo sensor generation; FAST-LIO and planner
# configuration remain unchanged.
SUNRAY_MID360_PLUGIN_DOWNSAMPLE="${SUNRAY_MID360_PLUGIN_DOWNSAMPLE:-8}"
SUNRAY_MID360_GOAL5_CSV_STRIDE="${SUNRAY_MID360_GOAL5_CSV_STRIDE:-4}"
PX4CTRL_CACHE="${LOCAL_ROS1_WS}/build/CMakeCache.txt"
[[ -f "${PX4CTRL_CACHE}" ]] || die "px4ctrl CMake cache is missing: ${PX4CTRL_CACHE}"
PX4CTRL_BUILD_BACKEND="$(sed -n 's/^MOSIM_PX4CTRL_GENERATED_BACKEND:STRING=//p' "${PX4CTRL_CACHE}" | tail -n 1)"
[[ "${PX4CTRL_BUILD_BACKEND}" == "${PX4CTRL_EXPECTED_BUILD_BACKEND}" ]] \
  || die "px4ctrl build backend mismatch: expected ${PX4CTRL_EXPECTED_BUILD_BACKEND}, got ${PX4CTRL_BUILD_BACKEND:-missing}"

cat > "${RESULT_DIR}/c99_fuel_contract.env" <<EOF
RUN_ID=${RUN_ID}
RESULT_DIR=${RESULT_DIR}
EXECUTE_S=${EXECUTE_S}
PROJECT_ROOT=${PROJECT_ROOT}
LOCAL_ROS1_WS=${LOCAL_ROS1_WS}
SUNRAY_WS=${SUNRAY_WS}
SUNRAY_PX4_DIR=${SUNRAY_PX4_DIR}
PX4_BUILD_DIR=${PX4_BUILD_DIR}
PX4CTRL_WS=${PX4CTRL_WS}
LIVOX_PLUGIN_WS=${LIVOX_PLUGIN_WS}
GOAL4_FUEL_WS=${GOAL4_FUEL_WS}
FASTLIO_WS=${FASTLIO_WS}
FASTLIO_SRC=${FASTLIO_SRC}
LIVOX_COMPAT_SRC=${LIVOX_COMPAT_SRC}
PX4CTRL_CORE_PROFILE=${PX4CTRL_CORE_PROFILE}
PX4CTRL_EXPECTED_BUILD_BACKEND=${PX4CTRL_EXPECTED_BUILD_BACKEND}
PX4CTRL_BUILD_BACKEND=${PX4CTRL_BUILD_BACKEND}
PX4CTRL_HOVER_PERCENTAGE=${PX4CTRL_HOVER_PERCENTAGE}
PX4CTRL_AUTO_TAKEOFF_HEIGHT=${PX4CTRL_AUTO_TAKEOFF_HEIGHT}
PX4CTRL_KP_XY=${PX4CTRL_KP_XY}
PX4CTRL_KP_Z=${PX4CTRL_KP_Z}
PX4CTRL_KV_XY=${PX4CTRL_KV_XY}
PX4CTRL_KV_Z=${PX4CTRL_KV_Z}
PX4CTRL_START_EXTERNAL_FUSION=${PX4CTRL_START_EXTERNAL_FUSION}
PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=${PX4CTRL_ENABLE_FASTLIO_EKF_FUSION}
PX4CTRL_FASTLIO_ODOMETRY_FUSION_ENABLED=${PX4CTRL_FASTLIO_ODOMETRY_FUSION_ENABLED}
PX4CTRL_FASTLIO_VELOCITY_FUSION_ENABLED=${PX4CTRL_FASTLIO_VELOCITY_FUSION_ENABLED}
PX4CTRL_EKF2_EV_CTRL_OVERRIDE=${PX4CTRL_EKF2_EV_CTRL_OVERRIDE}
PX4CTRL_EKF2_HGT_REF_OVERRIDE=${PX4CTRL_EKF2_HGT_REF_OVERRIDE}
SUNRAY_MID360_PLUGIN_DOWNSAMPLE=${SUNRAY_MID360_PLUGIN_DOWNSAMPLE}
SUNRAY_MID360_GOAL5_CSV_STRIDE=${SUNRAY_MID360_GOAL5_CSV_STRIDE}
QGC=disabled
EOF

export RUN_ID RESULT_DIR GOAL4_FUEL_WS FASTLIO_WS FASTLIO_SRC LIVOX_COMPAT_SRC
export PX4CTRL_CORE_PROFILE PX4CTRL_EXPECTED_BUILD_BACKEND PX4CTRL_HOVER_PERCENTAGE PX4CTRL_AUTO_TAKEOFF_HEIGHT
export PX4CTRL_KP_XY PX4CTRL_KP_Z PX4CTRL_KV_XY PX4CTRL_KV_Z
export PX4CTRL_START_EXTERNAL_FUSION PX4CTRL_ENABLE_FASTLIO_EKF_FUSION
export PX4CTRL_FASTLIO_ODOMETRY_FUSION_ENABLED PX4CTRL_FASTLIO_VELOCITY_FUSION_ENABLED
export PX4CTRL_EKF2_EV_CTRL_OVERRIDE PX4CTRL_EKF2_HGT_REF_OVERRIDE
export SUNRAY_MID360_PLUGIN_DOWNSAMPLE SUNRAY_MID360_GOAL5_CSV_STRIDE
export GUI=false
export OPEN_RVIZ=false
export UE_LIVE_MIRROR_ENABLE=false
export KEEP_ALIVE=false

exec bash "${PROJECT_ROOT}/Scripts/sunray/run_factory_l2_fuel_speed_gate.sh" "${EXECUTE_S}" "${RESULT_DIR}"
