#!/usr/bin/env bash
set -euo pipefail

# Static contract and future operator wrapper for no-goal FAST-LIO/RViz
# observation. The default path is DRY_RUN=1 and does not source ROS, run ros2,
# launch FAST-LIO, or open RViz2. A later PMO-scoped live task must explicitly
# set ALLOW_LIVE_OBSERVATION=1 before this script can delegate to the ROS2
# replay launcher.
#
# Claim boundary: this script/config contract is observation prep only. It does
# not prove TF/RViz readiness, localization quality, local-map quality,
# planner_ready, controller performance, mission success, runtime ack, or
# closed_loop.

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SCENE_ID="${SCENE_ID:-factoryenvironmentcollect}"
DRY_RUN="${DRY_RUN:-1}"
ALLOW_LIVE_OBSERVATION="${ALLOW_LIVE_OBSERVATION:-0}"
START_RVIZ="${START_RVIZ:-0}"
START_FASTLIO="${START_FASTLIO:-1}"
RVIZ_CONFIG="${RVIZ_CONFIG:-${PROJECT_ROOT}/Config/rviz2/mosim_uav_fastlio_camera_init_output_only.rviz}"
RVIZ_ROUTE_MODE="${RVIZ_ROUTE_MODE:-explicit_rviz_config_pass_through}"
RVIZ_PROFILE="${RVIZ_PROFILE:-fastlio_pointcloud}"
MAX_FRAMES="${MAX_FRAMES:-120}"
LOOP="${LOOP:-0}"
WALL_TIME="${WALL_TIME:-1}"
FPS="${FPS:-21.8}"
SCAN_DURATION_S="${SCAN_DURATION_S:-0.05}"
IMU_SUBSTEPS_PER_FRAME="${IMU_SUBSTEPS_PER_FRAME:-200}"
IMU_SPAN_S="${IMU_SPAN_S:-1.0}"
IMU_LEAD_SLEEP_S="${IMU_LEAD_SLEEP_S:-0.005}"
FASTLIO_LIDAR_TOPIC="${FASTLIO_LIDAR_TOPIC:-/mosim/livox/lidar}"
FASTLIO_POINTCLOUD_TOPIC="${FASTLIO_POINTCLOUD_TOPIC:-/mosim/lidar_points}"
FASTLIO_IMU_TOPIC="${FASTLIO_IMU_TOPIC:-/mosim/forward/imu}"
FASTLIO_LIDAR_FRAME="${FASTLIO_LIDAR_FRAME:-base/mid360_link}"
FASTLIO_IMU_FRAME="${FASTLIO_IMU_FRAME:-base/forward_imu_optical_frame}"
FASTLIO_OUTPUT_FIXED_FRAME="${FASTLIO_OUTPUT_FIXED_FRAME:-camera_init}"
TF_REQUIRED_EDGES="${TF_REQUIRED_EDGES:-camera_init<->base,ue_world<->camera_init,base->base/mid360_link,base->base/forward_imu_optical_frame}"
OBSERVE_TOPICS="${OBSERVE_TOPICS:-/tf,/cloud_registered,/Odometry,/path}"
RAW_LIDAR_DISPLAY_GAP="${RAW_LIDAR_DISPLAY_GAP:-/mosim/livox/lidar is Livox CustomMsg; no displayable raw PointCloud2 topic was proven in 065}"
FORBIDDEN_TOPICS="${FORBIDDEN_TOPICS:-/position_cmd,/mosim/planner/position_cmd,/planning/bspline}"
FORBIDDEN_COMPONENTS="${FORBIDDEN_COMPONENTS:-rviz2_unless_explicit,planner_or_ego,PositionCommand,20Hz_adapter,tf_bridge,goal_sender}"
RUNNER="${PROJECT_ROOT}/Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh"

json_bool() {
  case "$1" in
    1|true|TRUE|yes|YES|on|ON) printf "true" ;;
    *) printf "false" ;;
  esac
}

emit_contract_json() {
  python3 - "$@" <<'PY'
import json
import os
import sys

payload = {
    "schema": "mosim.ros2_runtime.fastlio_rviz_replay_static_contract.v1",
    "mode": "dry_run_static_contract",
    "live_graph_started": False,
    "ros_setup_sourced": False,
    "ros2_command_executed": False,
    "project_root": os.environ.get("PROJECT_ROOT", "/mnt/c/Users/HP/Desktop/MoSim"),
    "scene_id": os.environ.get("SCENE_ID", "factoryenvironmentcollect"),
    "runner": os.environ.get("RUNNER"),
    "rviz_config": os.environ.get("RVIZ_CONFIG"),
    "rviz_route_mode": os.environ.get("RVIZ_ROUTE_MODE"),
    "rviz_profile_for_existing_launch": os.environ.get("RVIZ_PROFILE"),
    "start_rviz_default": os.environ.get("START_RVIZ", "0") in {"1", "true", "TRUE", "yes", "YES", "on", "ON"},
    "start_fastlio_default": os.environ.get("START_FASTLIO", "1") in {"1", "true", "TRUE", "yes", "YES", "on", "ON"},
    "max_frames": int(float(os.environ.get("MAX_FRAMES", "120"))),
    "loop": os.environ.get("LOOP", "0") in {"1", "true", "TRUE", "yes", "YES", "on", "ON"},
    "wall_time": os.environ.get("WALL_TIME", "1") in {"1", "true", "TRUE", "yes", "YES", "on", "ON"},
    "fps": float(os.environ.get("FPS", "21.8")),
    "scan_duration_s": float(os.environ.get("SCAN_DURATION_S", "0.05")),
    "fastlio_input_topics": {
        "lidar": os.environ.get("FASTLIO_LIDAR_TOPIC", "/mosim/livox/lidar"),
        "imu": os.environ.get("FASTLIO_IMU_TOPIC", "/mosim/forward/imu"),
        "optional_pointcloud2_raw": os.environ.get("FASTLIO_POINTCLOUD_TOPIC", "/mosim/lidar_points"),
    },
    "fastlio_input_frames": {
        "lidar": os.environ.get("FASTLIO_LIDAR_FRAME", "base/mid360_link"),
        "imu": os.environ.get("FASTLIO_IMU_FRAME", "base/forward_imu_optical_frame"),
    },
    "fastlio_output_review": {
        "fixed_frame": os.environ.get("FASTLIO_OUTPUT_FIXED_FRAME", "camera_init"),
        "output_only_config_path": os.environ.get("RVIZ_CONFIG"),
        "launch_profile_gap_resolved": True,
        "launch_route_repair": "RVIZ_CONFIG is passed to run_mosim_scene_replay_launch_ros2.sh; that wrapper disables its older profile RViz path and opens rviz2 -d RVIZ_CONFIG only when START_RVIZ is explicitly enabled in a future authorized live task",
        "display_topics": [topic for topic in os.environ.get("OBSERVE_TOPICS", "/tf,/cloud_registered,/Odometry,/path").split(",") if topic],
    },
    "tf_edges_to_record_in_future_live_observation": [
        edge for edge in os.environ.get("TF_REQUIRED_EDGES", "").split(",") if edge
    ],
    "raw_lidar_display_gap": os.environ.get("RAW_LIDAR_DISPLAY_GAP"),
    "forbidden_topics": [topic for topic in os.environ.get("FORBIDDEN_TOPICS", "").split(",") if topic],
    "forbidden_components_to_keep_out_of_scope": [
        item for item in os.environ.get("FORBIDDEN_COMPONENTS", "").split(",") if item
    ],
    "claim_boundary": [
        "static observation contract only",
        "no TF/RViz readiness claim",
        "no localization or local-map quality claim",
        "no planner_ready, controller performance, mission success, runtime ack, or closed_loop claim",
        "raw LiDAR display is unresolved unless a real PointCloud2 source/conversion is separately proven",
    ],
}
print(json.dumps(payload, indent=2, ensure_ascii=False))
PY
}

if [[ "${DRY_RUN}" == "1" ]]; then
  export PROJECT_ROOT SCENE_ID RUNNER RVIZ_CONFIG RVIZ_ROUTE_MODE RVIZ_PROFILE START_RVIZ START_FASTLIO
  export MAX_FRAMES LOOP WALL_TIME FPS SCAN_DURATION_S FASTLIO_LIDAR_TOPIC
  export FASTLIO_POINTCLOUD_TOPIC FASTLIO_IMU_TOPIC FASTLIO_LIDAR_FRAME FASTLIO_IMU_FRAME
  export FASTLIO_OUTPUT_FIXED_FRAME OBSERVE_TOPICS TF_REQUIRED_EDGES RAW_LIDAR_DISPLAY_GAP
  export FORBIDDEN_TOPICS FORBIDDEN_COMPONENTS
  emit_contract_json
  exit 0
fi

if [[ "${ALLOW_LIVE_OBSERVATION}" != "1" ]]; then
  echo "Refusing live observation: set DRY_RUN=1 for static contract output or ALLOW_LIVE_OBSERVATION=1 in a separately authorized PMO live task." >&2
  exit 10
fi

if [[ ! -f "${RUNNER}" ]]; then
  echo "Missing replay runner: ${RUNNER}" >&2
  exit 11
fi

if [[ ! -f "${RVIZ_CONFIG}" ]]; then
  echo "Missing output-only RViz config: ${RVIZ_CONFIG}" >&2
  exit 12
fi

export RVIZ_CONFIG RVIZ_ROUTE_MODE RVIZ_PROFILE START_RVIZ START_FASTLIO MAX_FRAMES LOOP WALL_TIME FPS
export SCAN_DURATION_S IMU_SUBSTEPS_PER_FRAME IMU_SPAN_S IMU_LEAD_SLEEP_S
export FASTLIO_LIDAR_TOPIC FASTLIO_POINTCLOUD_TOPIC FASTLIO_IMU_TOPIC
export FASTLIO_LIDAR_FRAME FASTLIO_IMU_FRAME

exec bash "${RUNNER}" "${SCENE_ID}"
