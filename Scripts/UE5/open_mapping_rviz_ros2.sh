#!/usr/bin/env bash
set -euo pipefail

# Open native ROS2/RViz2 map and point-cloud review windows for an accepted UE
# scene. This is the primary Ubuntu 22.04 point-cloud visualization route;
# browser HTML is not part of this workflow.

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
SCENE_ID="${1:-factoryenvironmentcollect}"
OUTPUT_ROOT="${OUTPUT_ROOT:-${PROJECT_ROOT}/Results/unreal_scene_mapping}"
RVIZ_PROFILE="${RVIZ_PROFILE:-overview}"
RVIZ_CONFIG="${RVIZ_CONFIG:-${PROJECT_ROOT}/Config/rviz2/mosim_uav_mapping.rviz}"
RVIZ_GRID_CONFIG="${RVIZ_GRID_CONFIG:-${PROJECT_ROOT}/Config/rviz2/mosim_uav_planning_grid.rviz}"
RVIZ_POINTCLOUD_CONFIG="${RVIZ_POINTCLOUD_CONFIG:-${PROJECT_ROOT}/Config/rviz2/mosim_uav_fastlio_pointcloud.rviz}"
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

case "${RVIZ_PROFILE}" in
  overview)
    RVIZ_CONFIGS=("${RVIZ_CONFIG}")
    ;;
  planning_grid)
    RVIZ_CONFIGS=("${RVIZ_GRID_CONFIG}")
    ;;
  fastlio_pointcloud)
    RVIZ_CONFIGS=("${RVIZ_POINTCLOUD_CONFIG}")
    ;;
  split)
    RVIZ_CONFIGS=("${RVIZ_GRID_CONFIG}" "${RVIZ_POINTCLOUD_CONFIG}")
    ;;
  *)
    echo "Unsupported RVIZ_PROFILE: ${RVIZ_PROFILE}" >&2
    echo "Use overview, planning_grid, fastlio_pointcloud, or split." >&2
    exit 2
    ;;
esac

for required in "${REPLAY_CSV}" "${LOCAL_KNOWN_MAP}" "${LOCAL_PLAN_FRAMES}" "${LIDAR_POINT_FRAMES}" "${RVIZ_CONFIGS[@]}"; do
  if [[ ! -f "${required}" ]]; then
    echo "Missing required RViz2 artifact: ${required}" >&2
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
  RVIZ_CONFIGS_JSON=""
  for config in "${RVIZ_CONFIGS[@]}"; do
    if [[ -n "${RVIZ_CONFIGS_JSON}" ]]; then
      RVIZ_CONFIGS_JSON+=","
    fi
    RVIZ_CONFIGS_JSON+="\"${config}\""
  done
  python3 - <<PY
import json
print(json.dumps({
  "schema": "mosim.rviz2_window_contract_dryrun.v1",
  "scene_id": "${SCENE_ID}",
  "rviz_profile": "${RVIZ_PROFILE}",
  "rviz_configs": [${RVIZ_CONFIGS_JSON}],
  "ros_setup": "${ROS_SETUP}",
}, indent=2))
PY
  python3 Scripts/ros/publish_mosim_mapping_replay_ros2.py "${PUBLISH_ARGS[@]}" --dry-run
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
    echo "Missing ${command_name}. Source/install ROS2 Humble before opening the native point-cloud window." >&2
    exit 4
  fi
done

RVIZ_PIDS=()
cleanup() {
  for pid in "${RVIZ_PIDS[@]:-}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT

for config in "${RVIZ_CONFIGS[@]}"; do
  rviz2 -d "${config}" &
  RVIZ_PIDS+=("$!")
done

python3 Scripts/ros/publish_mosim_mapping_replay_ros2.py "${PUBLISH_ARGS[@]}"

for pid in "${RVIZ_PIDS[@]}"; do
  wait "${pid}" || true
done
