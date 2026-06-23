#!/usr/bin/env bash
# Probe native Sunray ROS1 MID360/FAST-LIO review topics.

set -eo pipefail

RESULT_DIR="${1:?usage: probe_mid360_fastlio_topics.sh RESULT_DIR}"
SUNRAY_WS="${SUNRAY_WS:-/tmp/mosim_sunray_build_20260620_114615/Sunray}"

mkdir -p "${RESULT_DIR}"

export PATH=/opt/ros/noetic/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib
source /opt/ros/noetic/setup.bash
source "${SUNRAY_WS}/devel/setup.bash"

deadline=$((SECONDS + 80))
while (( SECONDS < deadline )); do
  rostopic list > "${RESULT_DIR}/topics_after_gazebo.txt" 2>&1 || true
  if grep -q "/uav1/livox/lidar" "${RESULT_DIR}/topics_after_gazebo.txt" &&
     grep -q "/uav1/livox/imu" "${RESULT_DIR}/topics_after_gazebo.txt"; then
    break
  fi
  sleep 2
done

{
  echo "TOPICS"
  grep -Ei "livox|mid360|cloud|odom|path|gazebo_pose|imu" "${RESULT_DIR}/topics_after_gazebo.txt" || true
  echo "TYPES"
  for topic in \
    /uav1/livox/lidar \
    /uav1/livox/imu \
    /uav1/sunray/gazebo_pose \
    /uav1/mavros/local_position/pose; do
    printf "%s " "${topic}"
    timeout 5s rostopic type "${topic}" || true
  done
} | tee "${RESULT_DIR}/topic_probe_summary.txt"

timeout 8s rostopic echo -n 1 /uav1/livox/lidar > "${RESULT_DIR}/livox_lidar_first.txt" 2>&1 || true
timeout 8s rostopic echo -n 1 /uav1/livox/imu > "${RESULT_DIR}/livox_imu_first.txt" 2>&1 || true
timeout 8s rostopic hz /uav1/livox/lidar -w 20 > "${RESULT_DIR}/livox_lidar_hz.txt" 2>&1 || true
timeout 8s rostopic hz /uav1/livox/imu -w 50 > "${RESULT_DIR}/livox_imu_hz.txt" 2>&1 || true

echo "LIDAR_SAMPLE"
sed -n '1,80p' "${RESULT_DIR}/livox_lidar_first.txt"
echo "IMU_SAMPLE"
sed -n '1,60p' "${RESULT_DIR}/livox_imu_first.txt"
