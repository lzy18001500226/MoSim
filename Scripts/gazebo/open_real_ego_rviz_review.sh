#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/sunray150_gazebo_ros2_real_ego_rviz_review}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
MOSIM_MSGS_SETUP="${MOSIM_MSGS_SETUP:-${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs_20260615_ego_gate/install/setup.bash}"
EGO_SETUP="${EGO_SETUP:-${PROJECT_ROOT}/Results/tmp/ego_planner_ros2_port_ws/install/setup.bash}"
GAZEBO_ENV_SCRIPT="${GAZEBO_ENV_SCRIPT:-${PROJECT_ROOT}/Scripts/gazebo/setup_gazebo_wsl_env.sh}"
WORLD="${WORLD:-Config/gazebo/worlds/yunzong_planning_test_sunray150_assembled.sdf}"
GAZEBO_MODEL_PATH="${GAZEBO_MODEL_PATH:-${PROJECT_ROOT}/Config/gazebo/models}"
REVIEW_WORLD_HOLD_MODE="${REVIEW_WORLD_HOLD_MODE:-zero_gravity}"
GAZEBO_GUI="${GAZEBO_GUI:-0}"
EGO_LAUNCH="${EGO_LAUNCH:-mosim_gazebo_real_planner_gate.launch.py}"
EGO_DEFAULT_CONFIG="${EGO_DEFAULT_CONFIG:-${PROJECT_ROOT}/Results/tmp/ego_planner_ros2_port_ws/src/plan_manage/config/mosim_gazebo_real_planner_gate.yaml}"
EGO_CONFIG_FILE="${EGO_CONFIG_FILE:-}"
EGO_LONG_AXIS_GOAL_X="${EGO_LONG_AXIS_GOAL_X:-8.0}"
EGO_LONG_AXIS_GOAL_Y="${EGO_LONG_AXIS_GOAL_Y:-0.0}"
EGO_LONG_AXIS_GOAL_Z="${EGO_LONG_AXIS_GOAL_Z:-1.2}"
REVIEW_REFERENCE_START_X="${REVIEW_REFERENCE_START_X:--8.0}"
REVIEW_REFERENCE_START_Y="${REVIEW_REFERENCE_START_Y:-0.0}"
REVIEW_REFERENCE_START_Z="${REVIEW_REFERENCE_START_Z:-1.2}"
REVIEW_REFERENCE_GOAL_X="${REVIEW_REFERENCE_GOAL_X:-${EGO_LONG_AXIS_GOAL_X}}"
REVIEW_REFERENCE_GOAL_Y="${REVIEW_REFERENCE_GOAL_Y:-${EGO_LONG_AXIS_GOAL_Y}}"
REVIEW_REFERENCE_GOAL_Z="${REVIEW_REFERENCE_GOAL_Z:-${EGO_LONG_AXIS_GOAL_Z}}"
WORLD_NAME="${WORLD_NAME:-yunzong_planning_test_sunray150_assembled}"
GZ_TRUTH_TOPIC="${GZ_TRUTH_TOPIC:-/world/${WORLD_NAME}/dynamic_pose/info}"
GAZEBO_TRUTH_MODEL_NAME="${GAZEBO_TRUTH_MODEL_NAME:-sunray150_assembled}"
REVIEW_ACTUAL_PATH_TOPIC="${REVIEW_ACTUAL_PATH_TOPIC:-/mosim/review/actual_path}"
REVIEW_REFERENCE_PATH_TOPIC="${REVIEW_REFERENCE_PATH_TOPIC:-/mosim/review/reference_path}"
REVIEW_PATH_MAX_POINTS="${REVIEW_PATH_MAX_POINTS:-5000}"
STATIC_REVIEW_PATH_SCRIPT="${STATIC_REVIEW_PATH_SCRIPT:-Scripts/ros/publish_static_review_path.py}"
GAZEBO_REVIEW_PATHS_SCRIPT="${GAZEBO_REVIEW_PATHS_SCRIPT:-Scripts/ros/publish_gazebo_review_paths.py}"
RVIZ_LIDAR_CONFIG="${RVIZ_LIDAR_CONFIG:-${PROJECT_ROOT}/Config/rviz2/mosim_real_ego_lidar_cloud_review.rviz}"
RVIZ_GRID_CONFIG="${RVIZ_GRID_CONFIG:-${PROJECT_ROOT}/Config/rviz2/mosim_real_ego_occupancy_grid_review.rviz}"
ODOM_TOPIC="${ODOM_TOPIC:-/mosim/planner/odom}"
CLOUD_TOPIC="${CLOUD_TOPIC:-/mosim/planner/global_points}"
REVIEW_ACCUMULATED_CLOUD_TOPIC="${REVIEW_ACCUMULATED_CLOUD_TOPIC:-/mosim/review/lidar_points_map_accumulated}"
REVIEW_ACCUMULATED_FRAMES="${REVIEW_ACCUMULATED_FRAMES:-5}"
REVIEW_ACCUMULATED_MAX_POINTS="${REVIEW_ACCUMULATED_MAX_POINTS:-100000}"
REVIEW_RECORDER_MAX_POINTS="${REVIEW_RECORDER_MAX_POINTS:-100000}"
REVIEW_OCCUPANCY_TOPIC="${REVIEW_OCCUPANCY_TOPIC:-/mosim/review/occupancy_above_floor}"
REVIEW_OCCUPANCY_INFLATE_TOPIC="${REVIEW_OCCUPANCY_INFLATE_TOPIC:-/mosim/review/occupancy_inflate_above_floor}"
REVIEW_OCCUPANCY_MIN_Z="${REVIEW_OCCUPANCY_MIN_Z:-0.95}"
PLANNER_FILTER_GROUND_MIN_Z="${PLANNER_FILTER_GROUND_MIN_Z:-0.95}"
PLANNER_SELF_FILTER_RADIUS_XY="${PLANNER_SELF_FILTER_RADIUS_XY:-1.0}"
PLANNER_SELF_FILTER_Z_MIN="${PLANNER_SELF_FILTER_Z_MIN:--0.8}"
PLANNER_SELF_FILTER_Z_MAX="${PLANNER_SELF_FILTER_Z_MAX:-0.8}"

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_DIR}"

if [[ -f "${GAZEBO_ENV_SCRIPT}" ]]; then
  # shellcheck disable=SC1090
  source "${GAZEBO_ENV_SCRIPT}"
fi

set +u
# shellcheck disable=SC1090
source "${ROS_SETUP}"
# shellcheck disable=SC1090
source "${MOSIM_MSGS_SETUP}"
# shellcheck disable=SC1090
source "${EGO_SETUP}"
set -u

export ROS_LOG_DIR="${PROJECT_ROOT}/Results/tmp/ros_logs"
mkdir -p "${ROS_LOG_DIR}"
export GZ_SIM_RESOURCE_PATH="${GAZEBO_MODEL_PATH}"
export IGN_GAZEBO_RESOURCE_PATH="${GAZEBO_MODEL_PATH}"

WORLD_TO_RUN="${WORLD}"
if [[ "${REVIEW_WORLD_HOLD_MODE}" == "zero_gravity" ]]; then
  WORLD_TO_RUN="${RESULT_DIR}/review_world_zero_gravity.sdf"
  python3 - "${WORLD}" "${WORLD_TO_RUN}" <<'PY'
from pathlib import Path
import sys

source = Path(sys.argv[1])
target = Path(sys.argv[2])
text = source.read_text(encoding="utf-8")
text = text.replace("<gravity>0 0 -9.8066</gravity>", "<gravity>0 0 0</gravity>", 1)
target.write_text(text, encoding="utf-8")
PY
fi

EGO_CONFIG_TO_RUN="${EGO_CONFIG_FILE}"
if [[ -z "${EGO_CONFIG_TO_RUN}" ]]; then
  EGO_CONFIG_TO_RUN="${RESULT_DIR}/ego_long_axis_config.yaml"
  python3 - "${EGO_DEFAULT_CONFIG}" "${EGO_CONFIG_TO_RUN}" \
    "${EGO_LONG_AXIS_GOAL_X}" "${EGO_LONG_AXIS_GOAL_Y}" "${EGO_LONG_AXIS_GOAL_Z}" <<'PY'
from pathlib import Path
import re
import sys

source = Path(sys.argv[1])
target = Path(sys.argv[2])
goal_x, goal_y, goal_z = sys.argv[3:6]
text = source.read_text(encoding="utf-8")
replacements = {
    r"(\bfsm\.waypoint0_x:\s*)[-+0-9.eE]+": rf"\g<1>{goal_x}",
    r"(\bfsm\.waypoint0_y:\s*)[-+0-9.eE]+": rf"\g<1>{goal_y}",
    r"(\bfsm\.waypoint0_z:\s*)[-+0-9.eE]+": rf"\g<1>{goal_z}",
}
for pattern, replacement in replacements.items():
    text, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise SystemExit(f"failed to patch EGO config pattern: {pattern}")
target.write_text(text, encoding="utf-8")
PY
fi

PIDS=()
cleanup() {
  local pid
  for pid in "${PIDS[@]}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
  sleep 1
  for pid in "${PIDS[@]}"; do
    kill -KILL "${pid}" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT

if [[ "${GAZEBO_GUI}" == "1" ]]; then
  ign gazebo --render-engine ogre -r "${WORLD_TO_RUN}" \
    > "${RESULT_DIR}/gazebo.stdout.log" \
    2> "${RESULT_DIR}/gazebo.stderr.log" &
else
  ign gazebo -s --headless-rendering --render-engine-server ogre -r "${WORLD_TO_RUN}" \
    > "${RESULT_DIR}/gazebo.stdout.log" \
    2> "${RESULT_DIR}/gazebo.stderr.log" &
fi
PIDS+=("$!")
sleep 4

ros2 run ros_gz_bridge parameter_bridge \
  /mosim/gazebo/imu@sensor_msgs/msg/Imu@gz.msgs.IMU \
  /mosim/gazebo/lidar_points/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked \
  > "${RESULT_DIR}/ros_gz_bridge.stdout.log" \
  2> "${RESULT_DIR}/ros_gz_bridge.stderr.log" &
PIDS+=("$!")

ros2 run tf2_ros static_transform_publisher \
  --x 0 --y 0 --z 1.2 --roll 0 --pitch 0 --yaw 0 \
  --frame-id map \
  --child-frame-id sunray150_assembled/base_link/mid360_lidar \
  > "${RESULT_DIR}/static_tf.stdout.log" \
  2> "${RESULT_DIR}/static_tf.stderr.log" &
PIDS+=("$!")
sleep 2

python3 Scripts/ros/gazebo_fastlio_imu_passthrough.py \
  --imu-input-topic /mosim/gazebo/imu \
  --fastlio-imu-topic /mosim/fastlio/livox/imu \
  --sunray-imu-topic /uav1/livox/imu \
  --imu-frame sunray150_assembled/base_link/forward_imu \
  --output-json "${RESULT_DIR}/fastlio_imu_passthrough.json" \
  --trace-jsonl "${RESULT_DIR}/fastlio_imu_passthrough.trace.jsonl" \
  > "${RESULT_DIR}/fastlio_imu_passthrough.stdout.log" \
  2> "${RESULT_DIR}/fastlio_imu_passthrough.stderr.log" &
PIDS+=("$!")

python3 Scripts/ros/gazebo_fastlio_planner_input_adapter.py \
  --lidar-input-topic /mosim/gazebo/lidar_points/points \
  --imu-input-topic /mosim/gazebo/imu \
  --fastlio-lidar-topic /mosim/fastlio/livox/lidar \
  --fastlio-imu-topic /mosim/fastlio/livox/imu \
  --spark-livox-custom-topic /mosim/spark_fastlio/livox/lidar \
  --sunray-lidar-topic /uav1/livox/lidar \
  --sunray-imu-topic /uav1/livox/imu \
  --planner-global-points-topic /uav1/global_points \
  --mosim-planner-global-points-topic "${CLOUD_TOPIC}" \
  --review-map-cloud-topic /mosim/review/lidar_points_map \
  --review-accumulated-cloud-topic "${REVIEW_ACCUMULATED_CLOUD_TOPIC}" \
  --review-accumulated-frames "${REVIEW_ACCUMULATED_FRAMES}" \
  --review-accumulated-max-points "${REVIEW_ACCUMULATED_MAX_POINTS}" \
  --review-accumulated-intensity-policy z \
  --planner-odom-topic /uav1/sunray/gazebo_pose \
  --mosim-planner-odom-topic "${ODOM_TOPIC}" \
  --map-frame map \
  --global-frame map \
  --sensor-frame sunray150_assembled/base_link/mid360_lidar \
  --imu-frame sunray150_assembled/base_link/forward_imu \
  --odom-child-frame uav1/base_link \
  --tf-lookup-timeout-s 0.2 \
  --spark-livox-scan-lines 4 \
  --spark-livox-scan-rate-hz 10 \
  --odom-rate-hz 20 \
  --planner-filter-ground-min-z "${PLANNER_FILTER_GROUND_MIN_Z}" \
  --planner-self-filter-radius-xy "${PLANNER_SELF_FILTER_RADIUS_XY}" \
  --planner-self-filter-z-min "${PLANNER_SELF_FILTER_Z_MIN}" \
  --planner-self-filter-z-max "${PLANNER_SELF_FILTER_Z_MAX}" \
  --output-json "${RESULT_DIR}/fastlio_planner_input_adapter.json" \
  --trace-jsonl "${RESULT_DIR}/fastlio_planner_input_adapter.trace.jsonl" \
  --disable-spark-livox-custom-output \
  --disable-imu-output \
  > "${RESULT_DIR}/fastlio_planner_input_adapter.stdout.log" \
  2> "${RESULT_DIR}/fastlio_planner_input_adapter.stderr.log" &
PIDS+=("$!")

sleep 8

python3 "${GAZEBO_REVIEW_PATHS_SCRIPT}" \
  --gz-truth-topic "${GZ_TRUTH_TOPIC}" \
  --model-name "${GAZEBO_TRUTH_MODEL_NAME}" \
  --reference-topic "" \
  --truth-path-topic "${REVIEW_ACTUAL_PATH_TOPIC}" \
  --reference-path-topic "${REVIEW_REFERENCE_PATH_TOPIC}" \
  --frame-id map \
  --max-points "${REVIEW_PATH_MAX_POINTS}" \
  --summary-json "${RESULT_DIR}/gazebo_review_paths.json" \
  > "${RESULT_DIR}/gazebo_review_paths.stdout.log" \
  2> "${RESULT_DIR}/gazebo_review_paths.stderr.log" &
PIDS+=("$!")

python3 "${STATIC_REVIEW_PATH_SCRIPT}" \
  --path-topic "${REVIEW_REFERENCE_PATH_TOPIC}" \
  --frame-id map \
  --start-x "${REVIEW_REFERENCE_START_X}" \
  --start-y "${REVIEW_REFERENCE_START_Y}" \
  --start-z "${REVIEW_REFERENCE_START_Z}" \
  --goal-x "${REVIEW_REFERENCE_GOAL_X}" \
  --goal-y "${REVIEW_REFERENCE_GOAL_Y}" \
  --goal-z "${REVIEW_REFERENCE_GOAL_Z}" \
  --summary-json "${RESULT_DIR}/static_reference_path.json" \
  > "${RESULT_DIR}/static_reference_path.stdout.log" \
  2> "${RESULT_DIR}/static_reference_path.stderr.log" &
PIDS+=("$!")

sleep 2

ros2 launch ego_planner "${EGO_LAUNCH}" \
  config_file:="${EGO_CONFIG_TO_RUN}" \
  odom_topic:="${ODOM_TOPIC}" \
  cloud_topic:="${CLOUD_TOPIC}" \
  > "${RESULT_DIR}/ego_planner.stdout.log" \
  2> "${RESULT_DIR}/ego_planner.stderr.log" &
PIDS+=("$!")

sleep 8

python3 Scripts/ros/filter_pointcloud_by_z.py \
  --input-topic /grid_map/occupancy \
  --output-topic "${REVIEW_OCCUPANCY_TOPIC}" \
  --min-z "${REVIEW_OCCUPANCY_MIN_Z}" \
  --output-json "${RESULT_DIR}/review_occupancy_above_floor.json" \
  > "${RESULT_DIR}/review_occupancy_above_floor.stdout.log" \
  2> "${RESULT_DIR}/review_occupancy_above_floor.stderr.log" &
PIDS+=("$!")

python3 Scripts/ros/filter_pointcloud_by_z.py \
  --input-topic /grid_map/occupancy_inflate \
  --output-topic "${REVIEW_OCCUPANCY_INFLATE_TOPIC}" \
  --min-z "${REVIEW_OCCUPANCY_MIN_Z}" \
  --output-json "${RESULT_DIR}/review_occupancy_inflate_above_floor.json" \
  > "${RESULT_DIR}/review_occupancy_inflate_above_floor.stdout.log" \
  2> "${RESULT_DIR}/review_occupancy_inflate_above_floor.stderr.log" &
PIDS+=("$!")

sleep 2

python3 Scripts/ros/record_real_ego_rviz_review_topics.py \
  --output-json "${RESULT_DIR}/REAL_EGO_RVIZ_REVIEW_TOPICS.json" \
  --duration-seconds 45 \
  --max-points "${REVIEW_RECORDER_MAX_POINTS}" \
  --raw-lidar-topic /mosim/gazebo/lidar_points/points \
  --planner-cloud-topic "${CLOUD_TOPIC}" \
  --review-cloud-topic /mosim/review/lidar_points_map \
  --review-accumulated-cloud-topic "${REVIEW_ACCUMULATED_CLOUD_TOPIC}" \
  --ego-occupancy-topic "${REVIEW_OCCUPANCY_TOPIC}" \
  --ego-inflate-topic "${REVIEW_OCCUPANCY_INFLATE_TOPIC}" \
  > "${RESULT_DIR}/real_ego_rviz_review_topics.stdout.log" \
  2> "${RESULT_DIR}/real_ego_rviz_review_topics.stderr.log" &
PIDS+=("$!")

sleep 2

rviz2 -d "${RVIZ_LIDAR_CONFIG}" \
  > "${RESULT_DIR}/rviz2_lidar.stdout.log" \
  2> "${RESULT_DIR}/rviz2_lidar.stderr.log" &
RVIZ_LIDAR_PID="$!"
PIDS+=("${RVIZ_LIDAR_PID}")

rviz2 -d "${RVIZ_GRID_CONFIG}" \
  > "${RESULT_DIR}/rviz2_grid.stdout.log" \
  2> "${RESULT_DIR}/rviz2_grid.stderr.log" &
RVIZ_GRID_PID="$!"
PIDS+=("${RVIZ_GRID_PID}")

# Keep Gazebo, bridges, adapters, and EGO alive until both review windows close.
# Waiting for only the last RViz process made the LiDAR review window fragile:
# closing the grid window could tear down the point-cloud publishers.
wait "${RVIZ_LIDAR_PID}" "${RVIZ_GRID_PID}"
