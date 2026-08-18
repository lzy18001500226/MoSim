#!/usr/bin/env bash
# Launch one bounded, headless Factory L2 real-time A/B case.

set -eo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 {control|physics400|ray1x1} RUN_ID" >&2
  exit 2
fi

CASE_NAME="$1"
RUN_ID="$2"
case "${CASE_NAME}" in
  control)
    MAX_STEP_SIZE_S=0.001
    REAL_TIME_UPDATE_RATE_HZ=1000
    OUTER_RAY_HORIZONTAL_SAMPLES=100
    OUTER_RAY_VERTICAL_SAMPLES=50
    ;;
  physics400)
    MAX_STEP_SIZE_S=0.0025
    REAL_TIME_UPDATE_RATE_HZ=400
    OUTER_RAY_HORIZONTAL_SAMPLES=100
    OUTER_RAY_VERTICAL_SAMPLES=50
    ;;
  ray1x1)
    MAX_STEP_SIZE_S=0.001
    REAL_TIME_UPDATE_RATE_HZ=1000
    OUTER_RAY_HORIZONTAL_SAMPLES=1
    OUTER_RAY_VERTICAL_SAMPLES=1
    ;;
  *)
    echo "Unknown A/B case: ${CASE_NAME}; expected control, physics400, or ray1x1" >&2
    exit 2
    ;;
esac

if [[ ! "${RUN_ID}" =~ ^qgc-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$ ]]; then
  echo "RUN_ID must match qgc-[A-Za-z0-9][A-Za-z0-9._-]{0,95}" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
COLLISION_OVERLAY="${PROJECT_ROOT}/Results/sunray_ros1/performance_overlays/factory_l2_collision_lite_10pct/models"

if [[ ! -d "${COLLISION_OVERLAY}" ]]; then
  echo "Collision overlay is missing: ${COLLISION_OVERLAY}" >&2
  exit 2
fi

# ROS Noetic's generated catkin hooks reference optional environment variables.
# Enable nounset only after those hooks have initialized the ROS environment.
source /opt/ros/noetic/setup.bash
set -u

# All A/B cases reuse this one task-local plugin workspace. Only the outer ray
# grid and the explicitly selected world physics values may differ between
# cases, including the loaded shared-object binary.
AB_LIVOX_PLUGIN_WS="${PROJECT_ROOT}/Results/sunray_ros1/workspaces/factory_l2_ab_livox_plugin_ws"
export LIVOX_PLUGIN_WS="${AB_LIVOX_PLUGIN_WS}"
export SUNRAY_LIVOX_PLUGIN_FILENAME="${LIVOX_PLUGIN_WS}/devel/lib/liblivox_laser_simulation.so"
CASE_RESULT_DIR="${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}"
mkdir -p "${CASE_RESULT_DIR}"
PLUGIN_SOURCE_DIR="${PROJECT_ROOT}/src/simulation/gazebo/plugins/sunray/livox_laser_simulation"
PLUGIN_SOURCE_FINGERPRINT_PATH="${LIVOX_PLUGIN_WS}/.mosim_factory_l2_ab_plugin_source.sha256"
PLUGIN_SOURCE_SHA256="$(
  find "${PLUGIN_SOURCE_DIR}" -type f -print0 \
    | sort -z \
    | xargs -0 sha256sum \
    | sha256sum \
    | awk '{print $1}'
)"

if [[ ! -f "${SUNRAY_LIVOX_PLUGIN_FILENAME}" || ! -f "${PLUGIN_SOURCE_FINGERPRINT_PATH}" \
  || "$(cat "${PLUGIN_SOURCE_FINGERPRINT_PATH}")" != "${PLUGIN_SOURCE_SHA256}" ]]; then
  LOG_PATH="${CASE_RESULT_DIR}/sunray_livox_plugin_build.log" \
    LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS}" \
    bash "${PROJECT_ROOT}/Scripts/sunray/setup_sunray_livox_gazebo_plugin.sh"
  printf '%s\n' "${PLUGIN_SOURCE_SHA256}" > "${PLUGIN_SOURCE_FINGERPRINT_PATH}"
else
  printf 'reused plugin source sha256=%s\n' "${PLUGIN_SOURCE_SHA256}" \
    > "${CASE_RESULT_DIR}/sunray_livox_plugin_build.log"
fi
printf '%s\n' "${PLUGIN_SOURCE_SHA256}" > "${CASE_RESULT_DIR}/sunray_livox_plugin_source.sha256"
sha256sum "${SUNRAY_LIVOX_PLUGIN_FILENAME}" > "${CASE_RESULT_DIR}/sunray_livox_plugin.sha256"

export SUNRAY_GAZEBO_MAX_STEP_SIZE_S="${MAX_STEP_SIZE_S}"
export SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ="${REAL_TIME_UPDATE_RATE_HZ}"
export SUNRAY_MID360_OUTER_RAY_HORIZONTAL_SAMPLES="${OUTER_RAY_HORIZONTAL_SAMPLES}"
export SUNRAY_MID360_OUTER_RAY_VERTICAL_SAMPLES="${OUTER_RAY_VERTICAL_SAMPLES}"
export SUNRAY_FACTORY_WORLD_RUNTIME_OVERLAY=true
export QGC_DIFF_GAZEBO_MODEL_OVERLAY="${COLLISION_OVERLAY}"
export GOAL4_DATA_PLANE_OBSERVATION_MODE=continuous
export MOSIM_OPERATOR_RUN_ID="${RUN_ID}"
export MOSIM_OPERATOR_RUN_DIR="${PROJECT_ROOT}/Results/runs/${RUN_ID}"
export MOSIM_OPERATOR_RUN_MANIFEST="${MOSIM_OPERATOR_RUN_DIR}/RUN_MANIFEST.json"
export GUI=false

python3 "${PROJECT_ROOT}/Scripts/ui/prepare_operator_run.py" \
  --profile-id px4ctrl_graphical_c99_factory_qgc_realtime_goal_v1 \
  --runtime-profile-id sunray_ros1_factory_l2_graphical_px4ctrl_c99_qgc_realtime_goal_v1 \
  --run-id "${RUN_ID}" \
  --prepared-by "qgc_visible_terminal"

printf 'Starting %s: step=%s s, update_rate=%s Hz, outer_ray=%sx%s, run_id=%s\n' \
  "${CASE_NAME}" "${MAX_STEP_SIZE_S}" "${REAL_TIME_UPDATE_RATE_HZ}" \
  "${OUTER_RAY_HORIZONTAL_SAMPLES}" "${OUTER_RAY_VERTICAL_SAMPLES}" "${RUN_ID}"
exec bash "${PROJECT_ROOT}/Scripts/sunray/run_qgc_diff_realtime_goal_gate.sh" qgc_realtime_goal
