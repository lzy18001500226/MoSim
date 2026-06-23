#!/usr/bin/env bash
# Open the default single-UAV review surface:
# Gazebo full obstacle map + figure-8 animation + fixed follow camera + two RViz
# windows for LiDAR/path and occupancy/path review.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_ROOT="${RESULT_ROOT:-Results/gazebo_ros2}"
RESULT_DIR="${RESULT_DIR:-${RESULT_ROOT}/sunray150_single_uav_figure8_full_review_$(date +%Y%m%d_%H%M%S)}"
SCENARIO="${SCENARIO:-Config/scenarios/system/sunray150_single_uav_competition_light.yaml}"
WORLD="${WORLD:-Config/gazebo/worlds/yunzong_planning_test_sunray150_assembled.sdf}"
WORLD_NAME="${WORLD_NAME:-yunzong_planning_test_sunray150_assembled}"
GAZEBO_TRUTH_TOPIC_OVERRIDE="${GAZEBO_TRUTH_TOPIC_OVERRIDE:-/world/${WORLD_NAME}/dynamic_pose/info}"
RVIZ_LIDAR_CONFIG="${RVIZ_LIDAR_CONFIG:-${PROJECT_ROOT}/Config/rviz2/mosim_real_ego_lidar_cloud_review.rviz}"
RVIZ_GRID_CONFIG="${RVIZ_GRID_CONFIG:-${PROJECT_ROOT}/Config/rviz2/mosim_figure8_local_map_review.rviz}"

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_DIR}"

cat > "${RESULT_DIR}/FULL_REVIEW_REQUEST.json" <<JSON
{
  "schema": "mosim.single_uav_figure8_full_review_request.v1",
  "status": "starting",
  "world": "${WORLD}",
  "world_name": "${WORLD_NAME}",
  "scenario": "${SCENARIO}",
  "vehicle": "sunray150_assembled",
  "gazebo": {
    "purpose": "full obstacle map figure-8 live animation review",
    "camera_follow_default": true,
    "camera_follow_offset_m": [
      ${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M:--0.55},
      ${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M:-0.14},
      ${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M:-0.28}
    ],
    "camera_orbit_default": false
  },
  "rviz": {
    "lidar_window_config": "${RVIZ_LIDAR_CONFIG}",
    "occupancy_window_config": "${RVIZ_GRID_CONFIG}",
    "actual_path_topic": "/mosim/review/actual_path",
    "reference_path_topic": "/mosim/review/reference_path",
    "lidar_topic": "/mosim/review/lidar_points_map_accumulated",
    "occupancy_topics": [
      "/mosim/review/occupancy_above_floor",
      "/mosim/review/occupancy_inflate_above_floor"
    ]
  },
  "claim_boundary": [
    "live visual review entrypoint only",
    "does not claim final controller performance, FAST-LIO localization quality, planner_ready, closed_loop, UE acceptance, or multi-UAV readiness"
  ]
}
JSON

GAZEBO_GUI_CAPTURE_REVIEW="${GAZEBO_GUI_CAPTURE_REVIEW:-0}" \
GAZEBO_GUI_CAMERA_FOLLOW="${GAZEBO_GUI_CAMERA_FOLLOW:-1}" \
GAZEBO_GUI_CAMERA_ORBIT="${GAZEBO_GUI_CAMERA_ORBIT:-0}" \
GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M="${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M:--0.55}" \
GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M="${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M:-0.14}" \
GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M="${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M:-0.28}" \
GAZEBO_GUI_CAMERA_FOLLOW_REPEAT="${GAZEBO_GUI_CAMERA_FOLLOW_REPEAT:-240}" \
GAZEBO_GUI_CAMERA_FOLLOW_INTERVAL_S="${GAZEBO_GUI_CAMERA_FOLLOW_INTERVAL_S:-0.4}" \
GAZEBO_GUI_CAMERA_FOLLOW_MIN_DIST_M="${GAZEBO_GUI_CAMERA_FOLLOW_MIN_DIST_M:-0.35}" \
GAZEBO_GUI_CAMERA_FOLLOW_MAX_DIST_M="${GAZEBO_GUI_CAMERA_FOLLOW_MAX_DIST_M:-1.35}" \
GAZEBO_RVIZ_REVIEW_PATHS=1 \
ENABLE_SAME_RUN_MAP_REVIEW=1 \
MAP_REVIEW_DURATION_SECONDS_OVERRIDE="${MAP_REVIEW_DURATION_SECONDS_OVERRIDE:-45}" \
SCENARIO="${SCENARIO}" \
WORLD="${WORLD}" \
WORLD_NAME="${WORLD_NAME}" \
GAZEBO_TRUTH_TOPIC_OVERRIDE="${GAZEBO_TRUTH_TOPIC_OVERRIDE}" \
RESULT_DIR="${RESULT_DIR}" \
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-155}" \
FIGURE_PERIOD_S_OVERRIDE="${FIGURE_PERIOD_S_OVERRIDE:-30}" \
FIGURE_DURATION_S_OVERRIDE="${FIGURE_DURATION_S_OVERRIDE:-78}" \
FIGURE_X_OFFSET_OVERRIDE="${FIGURE_X_OFFSET_OVERRIDE:-0.0}" \
FIGURE_Y_OFFSET_OVERRIDE="${FIGURE_Y_OFFSET_OVERRIDE:-0.0}" \
TRACKER_DURATION_S_OVERRIDE="${TRACKER_DURATION_S_OVERRIDE:-88}" \
FIGURE_LAND_S_OVERRIDE="${FIGURE_LAND_S_OVERRIDE:-10}" \
FIGURE_FINAL_HOLD_S_OVERRIDE="${FIGURE_FINAL_HOLD_S_OVERRIDE:-8}" \
FIGURE_GROUND_ALTITUDE_OVERRIDE="${FIGURE_GROUND_ALTITUDE_OVERRIDE:-0.05}" \
TRACKER_GROUND_MOTOR_COMMAND_OVERRIDE="${TRACKER_GROUND_MOTOR_COMMAND_OVERRIDE:-0.0}" \
TRACKER_ROLL_CONTROL_SIGN_OVERRIDE="${TRACKER_ROLL_CONTROL_SIGN_OVERRIDE:--1.0}" \
TRACKER_PITCH_CONTROL_SIGN_OVERRIDE="${TRACKER_PITCH_CONTROL_SIGN_OVERRIDE:-1.0}" \
TRACKER_XY_CONTROL_SIGN_OVERRIDE="${TRACKER_XY_CONTROL_SIGN_OVERRIDE:-1.0}" \
bash Scripts/gazebo/run_sunray150_figure8_animation_review.sh &
gazebo_pid="$!"

sleep "${RVIZ_START_DELAY_S:-18}"

set +u
source /opt/ros/humble/setup.bash
if [[ -f "${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs/install/setup.bash" ]]; then
  source "${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs/install/setup.bash"
fi
if [[ -f "${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs_20260615_ego_gate/install/setup.bash" ]]; then
  source "${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs_20260615_ego_gate/install/setup.bash"
fi
if [[ -f "${PROJECT_ROOT}/Results/tmp/ego_planner_ros2_port_ws/install/setup.bash" ]]; then
  source "${PROJECT_ROOT}/Results/tmp/ego_planner_ros2_port_ws/install/setup.bash"
fi
set -u

ros2 run tf2_ros static_transform_publisher \
  --x 0 --y 0 --z 1.2 \
  --roll 0 --pitch 0 --yaw 0 \
  --frame-id map \
  --child-frame-id sunray150_assembled/base_link/mid360_lidar \
  > "${RESULT_DIR}/review_static_tf.stdout.log" \
  2> "${RESULT_DIR}/review_static_tf.stderr.log" &
review_static_tf_pid="$!"

python3 Scripts/ros/gazebo_fastlio_planner_input_adapter.py \
  --lidar-input-topic /mosim/gazebo/lidar_points/points \
  --imu-input-topic /mosim/gazebo/imu \
  --fastlio-lidar-topic /mosim/fastlio/livox/lidar \
  --fastlio-imu-topic /mosim/fastlio/livox/imu \
  --spark-livox-custom-topic /mosim/spark_fastlio/livox/lidar \
  --sunray-lidar-topic /uav1/livox/lidar \
  --sunray-imu-topic /uav1/livox/imu \
  --planner-global-points-topic /uav1/global_points \
  --mosim-planner-global-points-topic /mosim/planner/global_points \
  --review-map-cloud-topic /mosim/review/lidar_points_map \
  --review-accumulated-cloud-topic /mosim/review/lidar_points_map_accumulated \
  --review-accumulated-frames "${REVIEW_ACCUMULATED_FRAMES:-5}" \
  --review-accumulated-max-points "${REVIEW_ACCUMULATED_MAX_POINTS:-100000}" \
  --review-accumulated-intensity-policy z \
  --planner-odom-topic /uav1/sunray/gazebo_pose \
  --mosim-planner-odom-topic /mosim/planner/odom \
  --map-frame map \
  --global-frame map \
  --sensor-frame sunray150_assembled/base_link/mid360_lidar \
  --imu-frame sunray150_assembled/base_link/forward_imu \
  --odom-child-frame uav1/base_link \
  --tf-lookup-timeout-s 0.2 \
  --spark-livox-scan-lines 4 \
  --spark-livox-scan-rate-hz 10 \
  --odom-rate-hz 20 \
  --planner-filter-ground-min-z "${PLANNER_FILTER_GROUND_MIN_Z:-0.95}" \
  --planner-self-filter-radius-xy "${PLANNER_SELF_FILTER_RADIUS_XY:-1.0}" \
  --planner-self-filter-z-min "${PLANNER_SELF_FILTER_Z_MIN:--0.8}" \
  --planner-self-filter-z-max "${PLANNER_SELF_FILTER_Z_MAX:-0.8}" \
  --output-json "${RESULT_DIR}/review_fastlio_planner_input_adapter.json" \
  --trace-jsonl "${RESULT_DIR}/review_fastlio_planner_input_adapter.trace.jsonl" \
  --disable-spark-livox-custom-output \
  --disable-imu-output \
  > "${RESULT_DIR}/review_fastlio_planner_input_adapter.stdout.log" \
  2> "${RESULT_DIR}/review_fastlio_planner_input_adapter.stderr.log" &
review_fastlio_adapter_pid="$!"

sleep 4

rviz2 -d "${RVIZ_LIDAR_CONFIG}" \
  > "${RESULT_DIR}/rviz2_lidar.stdout.log" \
  2> "${RESULT_DIR}/rviz2_lidar.stderr.log" &
rviz_lidar_pid="$!"

rviz2 -d "${RVIZ_GRID_CONFIG}" \
  > "${RESULT_DIR}/rviz2_grid.stdout.log" \
  2> "${RESULT_DIR}/rviz2_grid.stderr.log" &
rviz_grid_pid="$!"

python3 - <<PY
import json
from pathlib import Path
path = Path("${RESULT_DIR}/FULL_REVIEW_REQUEST.json")
payload = json.loads(path.read_text(encoding="utf-8"))
payload.update({
    "status": "running_for_manual_review",
    "gazebo_pid": int("${gazebo_pid}"),
    "review_static_tf_pid": int("${review_static_tf_pid}"),
    "review_fastlio_adapter_pid": int("${review_fastlio_adapter_pid}"),
    "rviz_lidar_pid": int("${rviz_lidar_pid}"),
    "rviz_grid_pid": int("${rviz_grid_pid}"),
})
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(path.parent)
PY

wait "${gazebo_pid}" || true
wait "${rviz_lidar_pid}" "${rviz_grid_pid}" || true
