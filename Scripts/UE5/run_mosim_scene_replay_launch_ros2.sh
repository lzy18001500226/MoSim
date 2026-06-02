#!/usr/bin/env bash
set -euo pipefail

# Build/use a generated ROS2 workspace for the project-local
# mosim_scene_replay launch package, then run the native ROS2 launch workflow.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
ROS_LOG_DIR="${ROS_LOG_DIR:-${PROJECT_ROOT}/Results/tmp/ros_logs}"
WORKSPACE_ENV="${WORKSPACE:-}"
SCENE_ID="${1:-factoryenvironmentcollect}"
RVIZ_PROFILE="${RVIZ_PROFILE:-split}"
START_RVIZ="${START_RVIZ:-1}"
START_FASTLIO="${START_FASTLIO:-0}"
FASTLIO_ROS2_LAUNCH_CMD="${FASTLIO_ROS2_LAUNCH_CMD:-}"
FASTLIO_LIDAR_TOPIC="${FASTLIO_LIDAR_TOPIC:-/mosim/livox/lidar}"
FASTLIO_POINTCLOUD_TOPIC="${FASTLIO_POINTCLOUD_TOPIC:-/mosim/lidar_points}"
FASTLIO_IMU_TOPIC="${FASTLIO_IMU_TOPIC:-/mosim/forward/imu}"
FASTLIO_LIDAR_FRAME="${FASTLIO_LIDAR_FRAME:-base/mid360_link}"
FASTLIO_IMU_FRAME="${FASTLIO_IMU_FRAME:-base/forward_imu_optical_frame}"
FPS="${FPS:-10}"
SCAN_DURATION_S="${SCAN_DURATION_S:-0}"
IMU_SUBSTEPS_PER_FRAME="${IMU_SUBSTEPS_PER_FRAME:-10}"
IMU_SPAN_S="${IMU_SPAN_S:-0}"
IMU_LEAD_SLEEP_S="${IMU_LEAD_SLEEP_S:-0.005}"
MAX_FRAMES="${MAX_FRAMES:-0}"
LOOP="${LOOP:-1}"
WALL_TIME="${WALL_TIME:-1}"
DRY_RUN="${DRY_RUN:-0}"

cd "${PROJECT_ROOT}"
mkdir -p "${ROS_LOG_DIR}"
export ROS_LOG_DIR

case "${SCENE_ID}" in
  factoryenvironmentcollect|FactoryEnvironmentCollect|factory)
    SCENE_ID="factoryenvironmentcollect"
    ;;
  derelictcorridormegascans|DerelictCorridorMegascans|derelict)
    SCENE_ID="derelictcorridormegascans"
    ;;
  *)
    echo "Unsupported scene: ${SCENE_ID}" >&2
    echo "Use factoryenvironmentcollect or derelictcorridormegascans." >&2
    exit 2
    ;;
esac

if [[ -n "${WORKSPACE_ENV}" ]]; then
  WORKSPACE="${WORKSPACE_ENV}"
else
  WORKSPACE="${PROJECT_ROOT}/Results/tmp/mosim_scene_replay_ros2_ws_${SCENE_ID}"
fi

if [[ ! -f "${ROS_SETUP}" ]]; then
  echo "Missing ROS2 setup file: ${ROS_SETUP}" >&2
  exit 4
fi
# shellcheck disable=SC1090
set +u
source "${ROS_SETUP}"
set -u

for command_name in ros2 colcon python3; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing ${command_name}. Source/install ROS2 Humble before running the launch workflow." >&2
    exit 4
  fi
done

bool_arg() {
  case "$1" in
    1|true|TRUE|yes|YES|on|ON) printf "true" ;;
    *) printf "false" ;;
  esac
}

LOOP_ARG="$(bool_arg "${LOOP}")"
WALL_TIME_ARG="$(bool_arg "${WALL_TIME}")"
START_RVIZ_ARG="$(bool_arg "${START_RVIZ}")"
START_FASTLIO_ARG="$(bool_arg "${START_FASTLIO}")"

if [[ "${START_FASTLIO_ARG}" == "true" && -z "${FASTLIO_ROS2_LAUNCH_CMD}" ]]; then
  echo "START_FASTLIO=1 requires FASTLIO_ROS2_LAUNCH_CMD for a real ROS2 FAST-LIO package." >&2
  exit 5
fi

LAUNCH_ARGS=(
  "scene:=${SCENE_ID}"
  "rviz_profile:=${RVIZ_PROFILE}"
  "start_rviz:=${START_RVIZ_ARG}"
  "start_fastlio:=${START_FASTLIO_ARG}"
  "fps:=${FPS}"
  "scan_duration_s:=${SCAN_DURATION_S}"
  "imu_substeps_per_frame:=${IMU_SUBSTEPS_PER_FRAME}"
  "imu_span_s:=${IMU_SPAN_S}"
  "imu_lead_sleep_s:=${IMU_LEAD_SLEEP_S}"
  "max_frames:=${MAX_FRAMES}"
  "loop:=${LOOP_ARG}"
  "wall_time:=${WALL_TIME_ARG}"
  "fastlio_lidar_topic:=${FASTLIO_LIDAR_TOPIC}"
  "fastlio_pointcloud_topic:=${FASTLIO_POINTCLOUD_TOPIC}"
  "fastlio_imu_topic:=${FASTLIO_IMU_TOPIC}"
  "fastlio_lidar_frame:=${FASTLIO_LIDAR_FRAME}"
  "fastlio_imu_frame:=${FASTLIO_IMU_FRAME}"
)
if [[ -n "${FASTLIO_ROS2_LAUNCH_CMD}" ]]; then
  LAUNCH_ARGS+=("fastlio_launch_cmd:=${FASTLIO_ROS2_LAUNCH_CMD}")
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  START_RVIZ_JSON="false"
  START_FASTLIO_JSON="false"
  [[ "${START_RVIZ_ARG}" == "true" ]] && START_RVIZ_JSON="true"
  [[ "${START_FASTLIO_ARG}" == "true" ]] && START_FASTLIO_JSON="true"
  python3 - <<PY
import json
print(json.dumps({
  "schema": "mosim.ros2_launch_workflow_dryrun.v1",
  "workspace": "${WORKSPACE}",
  "package": "mosim_scene_replay",
  "launch_file": "mosim_scene_replay.launch.py",
  "scene_id": "${SCENE_ID}",
  "rviz_profile": "${RVIZ_PROFILE}",
  "start_rviz": "${START_RVIZ_JSON}" == "true",
  "start_fastlio": "${START_FASTLIO_JSON}" == "true",
  "fastlio_lidar_topic": "${FASTLIO_LIDAR_TOPIC}",
  "fastlio_pointcloud_topic": "${FASTLIO_POINTCLOUD_TOPIC}",
  "fastlio_imu_topic": "${FASTLIO_IMU_TOPIC}",
  "fastlio_lidar_frame": "${FASTLIO_LIDAR_FRAME}",
  "fastlio_imu_frame": "${FASTLIO_IMU_FRAME}",
  "imu_substeps_per_frame": ${IMU_SUBSTEPS_PER_FRAME},
  "scan_duration_s": ${SCAN_DURATION_S},
  "imu_span_s": ${IMU_SPAN_S},
  "imu_lead_sleep_s": ${IMU_LEAD_SLEEP_S},
  "claim": "dry-run only; no workspace files were created and no ROS2 process was launched"
}, indent=2))
PY
  ros2 launch "${PROJECT_ROOT}/Scripts/ros/mosim_scene_replay/launch/mosim_scene_replay.launch.py" --show-args
  exit 0
fi

mkdir -p "${WORKSPACE}/src"
ln -sfn "${PROJECT_ROOT}/Scripts/ros/mosim_scene_replay" "${WORKSPACE}/src/mosim_scene_replay"
rm -rf \
  "${WORKSPACE}/build/mosim_scene_replay" \
  "${WORKSPACE}/install/mosim_scene_replay" \
  "${WORKSPACE}/log/latest_build/mosim_scene_replay" \
  "${WORKSPACE}/log/latest/mosim_scene_replay"
colcon --log-base "${WORKSPACE}/log" build --base-paths "${WORKSPACE}/src/mosim_scene_replay" --build-base "${WORKSPACE}/build" --install-base "${WORKSPACE}/install" --packages-select mosim_scene_replay
# shellcheck disable=SC1091
set +u
source "${WORKSPACE}/install/setup.bash"
set -u

ros2 launch mosim_scene_replay mosim_scene_replay.launch.py "${LAUNCH_ARGS[@]}"
