#!/usr/bin/env bash
# Start upstream Sunray ROS1/PX4/Gazebo Classic GUI review session.
# Keeps Gazebo open for human review.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/tmp/mosim_sunray_build_20260620_114615/Sunray}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-/opt/mosim_work/sunray_px4}"
RUN_ID="${RUN_ID:-sunray_ros1_gui_review_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
SUNRAY_LAUNCH_GUI="${SUNRAY_LAUNCH_GUI:-true}"
DETACHED_GZCLIENT="${DETACHED_GZCLIENT:-false}"
SUNRAY_WORLD_FILE="${SUNRAY_WORLD_FILE:-}"
EXTERNAL_FUSION_SOURCE="${EXTERNAL_FUSION_SOURCE:-2}"
EXTERNAL_FUSION_POSITION_TOPIC="${EXTERNAL_FUSION_POSITION_TOPIC:-/uav1/mavros/local_position/pose}"
EXTERNAL_FUSION_USE_VISION_POSE="${EXTERNAL_FUSION_USE_VISION_POSE:-true}"

mkdir -p "${RESULT_DIR}"

source_env() {
  export PATH=/opt/ros/noetic/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib
  source /usr/share/gazebo/setup.sh
  source /opt/ros/noetic/setup.bash
  source "${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/setup_gazebo.bash" \
    "${SUNRAY_PX4_DIR}" \
    "${SUNRAY_PX4_DIR}/build/px4_sitl_default"
  source "${SUNRAY_WS}/devel/setup.bash"

  local sunray_models="${SUNRAY_WS}/simulation/sunray_simulator/models"
  export GAZEBO_MODEL_DATABASE_URI="${GAZEBO_MODEL_DATABASE_URI:-http://models.gazebosim.org}"
  export ROS_PACKAGE_PATH="${SUNRAY_PX4_DIR}:${SUNRAY_WS}:/opt/ros/noetic/share:${ROS_PACKAGE_PATH:-}"
  export GAZEBO_MODEL_PATH="${sunray_models}/scence_models:${sunray_models}/drone_models:${sunray_models}/sensor_models:${sunray_models}/fake_models:${sunray_models}/ugv_models:${sunray_models}/aws_models:${sunray_models}/aws_vins_models:${GAZEBO_MODEL_PATH:-}"
  export GAZEBO_RESOURCE_PATH="${SUNRAY_WS}/simulation/sunray_simulator:${GAZEBO_RESOURCE_PATH:-}"
}

source_env
rm -f /tmp/px4-sock-0 /tmp/px4-sock-1 2>/dev/null || printf "1\n" | sudo -S rm -f /tmp/px4-sock-0 /tmp/px4-sock-1

if [[ -n "${SUNRAY_WORLD_FILE}" ]]; then
  roslaunch sunray_simulator sunray_sim_1uav.launch \
    gui:="${SUNRAY_LAUNCH_GUI}" world:="${SUNRAY_WORLD_FILE}" \
    > "${RESULT_DIR}/sunray_sim_gui.log" 2>&1 &
else
  roslaunch sunray_simulator sunray_sim_1uav.launch \
    gui:="${SUNRAY_LAUNCH_GUI}" \
    > "${RESULT_DIR}/sunray_sim_gui.log" 2>&1 &
fi
echo $! > "${RESULT_DIR}/sunray_sim_gui.pid"

if [[ "${DETACHED_GZCLIENT}" == "true" ]]; then
  # Starting gzclient through gazebo_ros can black-screen under WSLg. Keep the
  # upstream Sunray/PX4 server path and attach a plain Gazebo Classic client.
  sleep 4
  gzclient --verbose > "${RESULT_DIR}/gzclient_detached.log" 2>&1 &
  echo $! > "${RESULT_DIR}/gzclient_detached.pid"
fi

echo "Waiting for MAVROS heartbeat..."
deadline=$((SECONDS + 50))
while (( SECONDS < deadline )); do
  if timeout 2s rostopic echo -n 1 /uav1/mavros/state > "${RESULT_DIR}/mavros_state_first.txt" 2>/dev/null; then
    if grep -q "connected: True" "${RESULT_DIR}/mavros_state_first.txt"; then
      break
    fi
  fi
  sleep 1
done

roslaunch sunray_uav_control external_fusion.launch \
  uav_id:=1 uav_name:=uav external_source:="${EXTERNAL_FUSION_SOURCE}" position_topic:="${EXTERNAL_FUSION_POSITION_TOPIC}" use_vision_pose:="${EXTERNAL_FUSION_USE_VISION_POSE}" \
  > "${RESULT_DIR}/external_fusion.log" 2>&1 &
echo $! > "${RESULT_DIR}/external_fusion.pid"

sleep 2
roslaunch sunray_uav_control sunray_control_node.launch \
  uav_id:=1 uav_name:=uav Takeoff_height:=1.0 Land_speed:=0.25 \
  > "${RESULT_DIR}/uav_control.log" 2>&1 &
echo $! > "${RESULT_DIR}/uav_control.pid"

sleep 4
if [[ "${AUTO_RUN_DEMO:-true}" == "true" ]]; then
  roslaunch sunray_tutorial run_demo.launch demo_id:=1 uav_id:=1 uav_name:=uav \
    > "${RESULT_DIR}/takeoff_hover_land_demo.log" 2>&1 &
  echo $! > "${RESULT_DIR}/takeoff_hover_land_demo.pid"
else
  echo "AUTO_RUN_DEMO=false; waiting for manual demo start." > "${RESULT_DIR}/takeoff_hover_land_demo.deferred"
fi

cat > "${RESULT_DIR}/GUI_REVIEW_SESSION.json" <<EOF
{
  "schema": "mosim.sunray_ros1_gui_review_session.v1",
  "status": "running",
  "result_dir": "${RESULT_DIR}",
  "entry": "roslaunch sunray_simulator sunray_sim_1uav.launch gui:=${SUNRAY_LAUNCH_GUI} + ${DETACHED_GZCLIENT:+detached gzclient + }sunray_uav_control + optional sunray_tutorial demo_id:=1",
  "world_file": "${SUNRAY_WORLD_FILE:-upstream_default}",
  "scope": "upstream Sunray ROS1/PX4/Gazebo default single-UAV GUI review",
  "external_fusion": {
    "source": "${EXTERNAL_FUSION_SOURCE}",
    "position_topic": "${EXTERNAL_FUSION_POSITION_TOPIC}",
    "use_vision_pose": "${EXTERNAL_FUSION_USE_VISION_POSE}"
  },
  "control_feedback_source": "Sunray px4_state from external_fusion_node; default GUI review uses PX4/MAVROS local_position/velocity/imu state unless FAST-LIO/PX4 fusion is separately launched and proven",
  "flight_controller_imu_topic": "/imu -> PX4 -> /uav1/mavros/imu/data",
  "mid360_imu_topic": "/uav1/livox/imu"
}
EOF

echo "${RESULT_DIR}"
echo "Sunray GUI review session is running. Keep this launcher alive to keep ROS/Gazebo alive."

if [[ "${KEEP_ALIVE:-true}" == "true" ]]; then
  while true; do
    sleep 60
  done
fi
