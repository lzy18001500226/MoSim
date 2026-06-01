#!/usr/bin/env bash
set -euo pipefail

# Run the native ROS1/RViz + FAST-LIO replay path for an accepted UE scene.
# This script does not open browser HTML. It starts/checks only ROS-native
# processes and exits early when ROS1/Catkin/FAST-LIO runtime is unavailable.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
SCENE_ID="${1:-factoryenvironmentcollect}"
OUTPUT_ROOT="${OUTPUT_ROOT:-${PROJECT_ROOT}/Results/unreal_scene_mapping}"
FAST_LIO_LAUNCH="${FAST_LIO_LAUNCH:-fast_lio mapping_velodyne.launch rviz:=false}"
RVIZ_CONFIG="${RVIZ_CONFIG:-${PROJECT_ROOT}/Config/rviz/mosim_uav_mapping.rviz}"
RVIZ_PROFILE="${RVIZ_PROFILE:-fastlio_pointcloud}"
RVIZ_GRID_CONFIG="${RVIZ_GRID_CONFIG:-${PROJECT_ROOT}/Config/rviz/mosim_uav_planning_grid.rviz}"
RVIZ_POINTCLOUD_CONFIG="${RVIZ_POINTCLOUD_CONFIG:-${PROJECT_ROOT}/Config/rviz/mosim_uav_fastlio_pointcloud.rviz}"
FPS="${FPS:-10}"
MAX_FRAMES="${MAX_FRAMES:-0}"
LOOP="${LOOP:-1}"
START_RVIZ="${START_RVIZ:-1}"
START_FASTLIO="${START_FASTLIO:-1}"
RECORD_FASTLIO="${RECORD_FASTLIO:-1}"
RECORD_DURATION_SECONDS="${RECORD_DURATION_SECONDS:-20}"
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
    echo "Missing required replay artifact: ${required}" >&2
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
  python3 Scripts/UE5/publish_fastlio_replay_ros1.py "${FASTLIO_ARGS[@]}" --dry-run
  python3 Scripts/ros/publish_mosim_mapping_replay_ros1.py "${MAPPING_ARGS[@]}" --dry-run
  echo "DRY_RUN=1: no ROS process was launched."
  exit 0
fi

for command_name in roscore rostopic roslaunch rviz python3; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing ${command_name}. Source/install ROS1 before running the native replay loop." >&2
    exit 4
  fi
done

PIDS=()
cleanup() {
  for pid in "${PIDS[@]:-}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT

if ! rostopic list >/dev/null 2>&1; then
  mkdir -p "${PROJECT_ROOT}/Results/tmp"
  roscore >"${PROJECT_ROOT}/Results/tmp/mosim_roscore.log" 2>&1 &
  PIDS+=("$!")
  sleep 3
fi

if [[ "${START_FASTLIO}" == "1" ]]; then
  # shellcheck disable=SC2086
  roslaunch ${FAST_LIO_LAUNCH} &
  PIDS+=("$!")
  sleep 3
fi

if [[ "${START_RVIZ}" == "1" ]]; then
  case "${RVIZ_PROFILE}" in
    overview)
      rviz -d "${RVIZ_CONFIG}" &
      PIDS+=("$!")
      ;;
    planning_grid)
      rviz -d "${RVIZ_GRID_CONFIG}" &
      PIDS+=("$!")
      ;;
    fastlio_pointcloud)
      rviz -d "${RVIZ_POINTCLOUD_CONFIG}" &
      PIDS+=("$!")
      ;;
    split)
      rviz -d "${RVIZ_GRID_CONFIG}" &
      PIDS+=("$!")
      rviz -d "${RVIZ_POINTCLOUD_CONFIG}" &
      PIDS+=("$!")
      ;;
    *)
      echo "Unsupported RVIZ_PROFILE: ${RVIZ_PROFILE}" >&2
      exit 2
      ;;
  esac
fi

if [[ "${RECORD_FASTLIO}" == "1" ]]; then
  python3 Scripts/UE5/record_fastlio_ros1_runtime.py \
    --scene-id "${SCENE_ID}" \
    --output-dir "${SCENE_DIR}/fastlio_runtime" \
    --duration-seconds "${RECORD_DURATION_SECONDS}" &
  PIDS+=("$!")
fi

python3 Scripts/ros/publish_mosim_mapping_replay_ros1.py "${MAPPING_ARGS[@]}" &
PIDS+=("$!")
python3 Scripts/UE5/publish_fastlio_replay_ros1.py "${FASTLIO_ARGS[@]}"
