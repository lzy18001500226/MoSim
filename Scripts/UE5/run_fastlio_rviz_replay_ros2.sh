#!/usr/bin/env bash
set -euo pipefail

# Run the native ROS2/RViz2 replay path for an accepted UE scene. This script
# publishes MoSim LiDAR/IMU/local-map topics and optionally starts an external
# ROS2 FAST-LIO-family launch command supplied by FASTLIO_ROS2_LAUNCH_CMD.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
SCENE_ID="${1:-factoryenvironmentcollect}"
OUTPUT_ROOT="${OUTPUT_ROOT:-${PROJECT_ROOT}/Results/unreal_scene_mapping}"
RVIZ_CONFIG="${RVIZ_CONFIG:-${PROJECT_ROOT}/Config/rviz2/mosim_uav_mapping.rviz}"
RVIZ_PROFILE="${RVIZ_PROFILE:-fastlio_pointcloud}"
RVIZ_GRID_CONFIG="${RVIZ_GRID_CONFIG:-${PROJECT_ROOT}/Config/rviz2/mosim_uav_planning_grid.rviz}"
RVIZ_POINTCLOUD_CONFIG="${RVIZ_POINTCLOUD_CONFIG:-${PROJECT_ROOT}/Config/rviz2/mosim_uav_fastlio_pointcloud.rviz}"
FPS="${FPS:-10}"
MAX_FRAMES="${MAX_FRAMES:-0}"
LOOP="${LOOP:-1}"
START_RVIZ="${START_RVIZ:-1}"
START_FASTLIO="${START_FASTLIO:-0}"
FASTLIO_ROS2_LAUNCH_CMD="${FASTLIO_ROS2_LAUNCH_CMD:-}"
DRY_RUN="${DRY_RUN:-0}"

cd "${PROJECT_ROOT}"

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

SCENE_DIR="${OUTPUT_ROOT}/${SCENE_ID}"
DATASET="${SCENE_DIR}/fastlio_replay_dataset.jsonl"
RENDER_REPLAY="${SCENE_DIR}/render_replay.csv"
LOCAL_KNOWN_MAP="${SCENE_DIR}/local_known_map_frames.jsonl"
LOCAL_PLAN_FRAMES="${SCENE_DIR}/local_plan_frames.jsonl"
LIDAR_POINT_FRAMES="${SCENE_DIR}/lidar_point_frames.jsonl"

for required in \
  "${DATASET}" \
  "${RENDER_REPLAY}" \
  "${LOCAL_KNOWN_MAP}" \
  "${LOCAL_PLAN_FRAMES}" \
  "${LIDAR_POINT_FRAMES}" \
  "${RVIZ_CONFIG}" \
  "${RVIZ_GRID_CONFIG}" \
  "${RVIZ_POINTCLOUD_CONFIG}"
do
  if [[ ! -f "${required}" ]]; then
    echo "Missing required ROS2 replay artifact: ${required}" >&2
    exit 3
  fi
done

FASTLIO_ARGS=(--dataset "${DATASET}" --fps "${FPS}" --wall-time)
MAPPING_ARGS=(
  --render-replay-csv "${RENDER_REPLAY}"
  --local-known-map-jsonl "${LOCAL_KNOWN_MAP}"
  --local-plan-jsonl "${LOCAL_PLAN_FRAMES}"
  --lidar-point-frames-jsonl "${LIDAR_POINT_FRAMES}"
  --fps "${FPS}"
)
if [[ "${MAX_FRAMES}" != "0" ]]; then
  FASTLIO_ARGS+=(--max-frames "${MAX_FRAMES}")
  MAPPING_ARGS+=(--max-frames "${MAX_FRAMES}")
fi
if [[ "${LOOP}" == "1" ]]; then
  FASTLIO_ARGS+=(--loop)
  MAPPING_ARGS+=(--loop)
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "RVIZ_PROFILE=${RVIZ_PROFILE}"
  echo "START_FASTLIO=${START_FASTLIO}"
  if [[ "${START_FASTLIO}" == "1" && -z "${FASTLIO_ROS2_LAUNCH_CMD}" ]]; then
    echo "FASTLIO_ROS2_LAUNCH_CMD is not set; ROS2 FAST-LIO runtime remains degraded."
  fi
  python3 Scripts/UE5/publish_fastlio_replay_ros2.py "${FASTLIO_ARGS[@]}" --dry-run
  python3 Scripts/ros/publish_mosim_mapping_replay_ros2.py "${MAPPING_ARGS[@]}" --dry-run
  echo "DRY_RUN=1: no ROS2 process was launched."
  exit 0
fi

if [[ ! -f "${ROS_SETUP}" ]]; then
  echo "Missing ROS2 setup file: ${ROS_SETUP}" >&2
  exit 4
fi
# shellcheck disable=SC1090
set +u
source "${ROS_SETUP}"
set -u

for command_name in ros2 rviz2 python3; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing ${command_name}. Source/install ROS2 Humble before running the native replay loop." >&2
    exit 4
  fi
done

if [[ "${START_FASTLIO}" == "1" && -z "${FASTLIO_ROS2_LAUNCH_CMD}" ]]; then
  echo "START_FASTLIO=1 requires FASTLIO_ROS2_LAUNCH_CMD for a real ROS2 FAST-LIO package." >&2
  exit 5
fi

PIDS=()
cleanup() {
  for pid in "${PIDS[@]:-}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT

if [[ "${START_FASTLIO}" == "1" ]]; then
  bash -lc "${FASTLIO_ROS2_LAUNCH_CMD}" &
  PIDS+=("$!")
  sleep 3
fi

if [[ "${START_RVIZ}" == "1" ]]; then
  case "${RVIZ_PROFILE}" in
    overview)
      rviz2 -d "${RVIZ_CONFIG}" &
      PIDS+=("$!")
      ;;
    planning_grid)
      rviz2 -d "${RVIZ_GRID_CONFIG}" &
      PIDS+=("$!")
      ;;
    fastlio_pointcloud)
      rviz2 -d "${RVIZ_POINTCLOUD_CONFIG}" &
      PIDS+=("$!")
      ;;
    split)
      rviz2 -d "${RVIZ_GRID_CONFIG}" &
      PIDS+=("$!")
      rviz2 -d "${RVIZ_POINTCLOUD_CONFIG}" &
      PIDS+=("$!")
      ;;
    *)
      echo "Unsupported RVIZ_PROFILE: ${RVIZ_PROFILE}" >&2
      exit 2
      ;;
  esac
fi

python3 Scripts/ros/publish_mosim_mapping_replay_ros2.py "${MAPPING_ARGS[@]}" &
PIDS+=("$!")
python3 Scripts/UE5/publish_fastlio_replay_ros2.py "${FASTLIO_ARGS[@]}"
