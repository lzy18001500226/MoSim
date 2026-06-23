#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/sunray150_gazebo_ros2_real_lidar_only_rviz_review}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
MOSIM_MSGS_SETUP="${MOSIM_MSGS_SETUP:-${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs_20260615_ego_gate/install/setup.bash}"
GAZEBO_ENV_SCRIPT="${GAZEBO_ENV_SCRIPT:-${PROJECT_ROOT}/Scripts/gazebo/setup_gazebo_wsl_env.sh}"
WORLD="${WORLD:-Config/gazebo/worlds/yunzong_planning_test_sunray150_assembled.sdf}"
GAZEBO_MODEL_PATH="${GAZEBO_MODEL_PATH:-${PROJECT_ROOT}/Config/gazebo/models}"
REVIEW_WORLD_HOLD_MODE="${REVIEW_WORLD_HOLD_MODE:-zero_gravity}"
RVIZ_LIDAR_CONFIG="${RVIZ_LIDAR_CONFIG:-${PROJECT_ROOT}/Config/rviz2/mosim_real_ego_lidar_cloud_review.rviz}"
CLOUD_TOPIC="${CLOUD_TOPIC:-/mosim/planner/global_points}"
REVIEW_ACCUMULATED_CLOUD_TOPIC="${REVIEW_ACCUMULATED_CLOUD_TOPIC:-/mosim/review/lidar_points_map_accumulated}"

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

ign gazebo -s --headless-rendering --render-engine-server ogre -r "${WORLD_TO_RUN}" \
  > "${RESULT_DIR}/gazebo.stdout.log" \
  2> "${RESULT_DIR}/gazebo.stderr.log" &
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
  --review-accumulated-frames 15 \
  --review-accumulated-max-points 150000 \
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
  --output-json "${RESULT_DIR}/fastlio_planner_input_adapter.json" \
  --trace-jsonl "${RESULT_DIR}/fastlio_planner_input_adapter.trace.jsonl" \
  --disable-spark-livox-custom-output \
  --disable-imu-output \
  > "${RESULT_DIR}/fastlio_planner_input_adapter.stdout.log" \
  2> "${RESULT_DIR}/fastlio_planner_input_adapter.stderr.log" &
PIDS+=("$!")

sleep 8

python3 Scripts/ros/record_real_ego_rviz_review_topics.py \
  --output-json "${RESULT_DIR}/REAL_LIDAR_ONLY_RVIZ_REVIEW_TOPICS.json" \
  --duration-seconds 45 \
  --raw-lidar-topic /mosim/gazebo/lidar_points/points \
  --planner-cloud-topic "${CLOUD_TOPIC}" \
  --review-cloud-topic /mosim/review/lidar_points_map \
  --review-accumulated-cloud-topic "${REVIEW_ACCUMULATED_CLOUD_TOPIC}" \
  --skip-ego-topics \
  > "${RESULT_DIR}/real_lidar_only_rviz_review_topics.stdout.log" \
  2> "${RESULT_DIR}/real_lidar_only_rviz_review_topics.stderr.log" &
PIDS+=("$!")

sleep 2

rviz2 -d "${RVIZ_LIDAR_CONFIG}" \
  > "${RESULT_DIR}/rviz2_lidar.stdout.log" \
  2> "${RESULT_DIR}/rviz2_lidar.stderr.log" &
PIDS+=("$!")

wait "${PIDS[-1]}"
