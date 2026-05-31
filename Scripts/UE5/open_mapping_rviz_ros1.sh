#!/usr/bin/env bash
set -euo pipefail

# Open the native ROS/RViz map and point-cloud review window for an accepted UE
# scene. This is the primary point-cloud visualization route; browser HTML is
# not part of this workflow.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
SCENE_ID="${1:-factoryenvironmentcollect}"
OUTPUT_ROOT="${OUTPUT_ROOT:-${PROJECT_ROOT}/Results/unreal_scene_mapping}"
RVIZ_CONFIG="${RVIZ_CONFIG:-${PROJECT_ROOT}/Config/rviz/mosim_uav_mapping.rviz}"
FPS="${FPS:-10}"
MAX_FRAMES="${MAX_FRAMES:-0}"
LOOP="${LOOP:-1}"
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
REPLAY_CSV="${SCENE_DIR}/render_replay.csv"
LOCAL_KNOWN_MAP="${SCENE_DIR}/local_known_map_frames.jsonl"
LOCAL_PLAN_FRAMES="${SCENE_DIR}/local_plan_frames.jsonl"
LIDAR_POINT_FRAMES="${SCENE_DIR}/lidar_point_frames.jsonl"

for required in "${REPLAY_CSV}" "${LOCAL_KNOWN_MAP}" "${LOCAL_PLAN_FRAMES}" "${LIDAR_POINT_FRAMES}" "${RVIZ_CONFIG}"; do
  if [[ ! -f "${required}" ]]; then
    echo "Missing required RViz artifact: ${required}" >&2
    exit 3
  fi
done

PUBLISH_ARGS=(
  --render-replay-csv "${REPLAY_CSV}"
  --local-known-map-jsonl "${LOCAL_KNOWN_MAP}"
  --local-plan-jsonl "${LOCAL_PLAN_FRAMES}"
  --lidar-point-frames-jsonl "${LIDAR_POINT_FRAMES}"
  --fps "${FPS}"
)

if [[ "${MAX_FRAMES}" != "0" ]]; then
  PUBLISH_ARGS+=(--max-frames "${MAX_FRAMES}")
fi
if [[ "${LOOP}" == "1" ]]; then
  PUBLISH_ARGS+=(--loop)
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  python3 Scripts/ros/publish_mosim_mapping_replay_ros1.py "${PUBLISH_ARGS[@]}" --dry-run
  exit 0
fi

for command_name in roscore rviz python3; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing ${command_name}. Source/install ROS1 before opening the native point-cloud window." >&2
    exit 4
  fi
done

ROSCORE_STARTED=0
if ! rostopic list >/dev/null 2>&1; then
  mkdir -p "${PROJECT_ROOT}/Results/tmp"
  roscore >"${PROJECT_ROOT}/Results/tmp/mosim_roscore.log" 2>&1 &
  ROSCORE_PID=$!
  ROSCORE_STARTED=1
  sleep 3
fi

rviz -d "${RVIZ_CONFIG}" &
RVIZ_PID=$!
python3 Scripts/ros/publish_mosim_mapping_replay_ros1.py "${PUBLISH_ARGS[@]}"

wait "${RVIZ_PID}" || true
if [[ "${ROSCORE_STARTED}" == "1" ]]; then
  kill "${ROSCORE_PID}" >/dev/null 2>&1 || true
fi
