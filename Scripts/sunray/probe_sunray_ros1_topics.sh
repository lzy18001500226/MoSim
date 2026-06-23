#!/usr/bin/env bash
# Probe Sunray ROS1/Gazebo topics with the assembled Sunray150+MID360 model.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/tmp/mosim_sunray_build_20260620_114615/Sunray}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-/opt/mosim_work/sunray_px4}"
RUN_ID="${RUN_ID:-sunray_ros1_topic_probe_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
GUI="${GUI:-false}"
WORLD_FILE="${WORLD_FILE:-${SUNRAY_WS}/simulation/sunray_simulator/worlds/planning_test.world}"
PROBE_WAIT_S="${PROBE_WAIT_S:-35}"

mkdir -p "${RESULT_DIR}"

cleanup() {
  set +e
  if [[ -n "${LAUNCH_PID:-}" ]] && kill -0 "${LAUNCH_PID}" >/dev/null 2>&1; then
    kill "${LAUNCH_PID}" >/dev/null 2>&1 || true
  fi
  pkill -f "[r]oslaunch .*sunray_sim_uav" >/dev/null 2>&1 || true
  pkill -f "[g]zserver" >/dev/null 2>&1 || true
  pkill -f "[g]zclient" >/dev/null 2>&1 || true
  pkill -f "[m]avros_node" >/dev/null 2>&1 || true
  pkill -f "/opt/mosim_work/sunray_px4.*/[p]x4" >/dev/null 2>&1 || true
  pkill -f "[r]osmaster" >/dev/null 2>&1 || true
  pkill -f "[r]osout" >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup
sleep 2

export PATH=/opt/ros/noetic/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib
source /usr/share/gazebo/setup.sh
source /opt/ros/noetic/setup.bash
source "${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/setup_gazebo.bash" \
  "${SUNRAY_PX4_DIR}" \
  "${SUNRAY_PX4_DIR}/build/px4_sitl_default"
source "${SUNRAY_WS}/devel/setup.bash"

sunray_models="${SUNRAY_WS}/simulation/sunray_simulator/models"
export ROS_PACKAGE_PATH="${SUNRAY_PX4_DIR}:${SUNRAY_WS}:/opt/ros/noetic/share:${ROS_PACKAGE_PATH:-}"
export GAZEBO_MODEL_PATH="${sunray_models}/scence_models:${sunray_models}/drone_models:${sunray_models}/sensor_models:${sunray_models}/fake_models:${sunray_models}/ugv_models:${sunray_models}/aws_models:${sunray_models}/aws_vins_models:${GAZEBO_MODEL_PATH:-}"
export GAZEBO_RESOURCE_PATH="${SUNRAY_WS}/simulation/sunray_simulator:${GAZEBO_RESOURCE_PATH:-}"
export GAZEBO_PLUGIN_PATH="${SUNRAY_WS}/devel/lib:${GAZEBO_PLUGIN_PATH:-}"
export LD_LIBRARY_PATH="${SUNRAY_WS}/devel/lib:${LD_LIBRARY_PATH:-}"

python3 "${PROJECT_ROOT}/Scripts/sunray/sync_assembled_model_into_sunray_ros1.py" \
  --project-root "${PROJECT_ROOT}" \
  --sunray-ws "${SUNRAY_WS}" \
  --manifest "${RESULT_DIR}/assembled_model_sync.json" \
  > "${RESULT_DIR}/assembled_model_sync.log" 2>&1

rm -f /tmp/px4-sock-0 /tmp/px4-sock-1 2>/dev/null || true

roslaunch "${SUNRAY_WS}/simulation/sunray_simulator/launch_uav_demo/sunray_sim_uav_planning.launch" \
  gui:="${GUI}" rviz_enable:=false world:="${WORLD_FILE}" \
  > "${RESULT_DIR}/gazebo.log" 2>&1 &
LAUNCH_PID=$!
echo "${LAUNCH_PID}" > "${RESULT_DIR}/launch.pid"

sleep "${PROBE_WAIT_S}"

rostopic list | sort > "${RESULT_DIR}/topics.txt" || true
grep -E "livox|cloud|scan|point|imu|gazebo|sunray|mavros" "${RESULT_DIR}/topics.txt" \
  > "${RESULT_DIR}/topics_filtered.txt" || true

: > "${RESULT_DIR}/topic_samples.txt"
for topic in /uav1/livox/lidar /livox/lidar /uav1/livox/imu /livox/imu /gazebo/model_states; do
  {
    echo "==== ${topic}"
    timeout 5s rostopic info "${topic}" 2>&1 || true
    timeout 8s rostopic echo -n 1 "${topic}" 2>&1 | head -80 || true
  } >> "${RESULT_DIR}/topic_samples.txt"
done

cat > "${RESULT_DIR}/TOPIC_PROBE.json" <<EOF
{
  "schema": "mosim.sunray_ros1_topic_probe.v1",
  "status": "completed",
  "result_dir": "${RESULT_DIR}",
  "topics": "${RESULT_DIR}/topics.txt",
  "topics_filtered": "${RESULT_DIR}/topics_filtered.txt",
  "topic_samples": "${RESULT_DIR}/topic_samples.txt"
}
EOF

cat "${RESULT_DIR}/topics_filtered.txt"
cat "${RESULT_DIR}/TOPIC_PROBE.json"
