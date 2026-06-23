#!/usr/bin/env bash
# Start the native Sunray ROS1 MID360 Gazebo chain for FAST-LIO/RViz review.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/tmp/mosim_sunray_build_20260620_114615/Sunray}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-/opt/mosim_work/sunray_px4}"
RUN_ID="${RUN_ID:-sunray_mid360_fastlio_review_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
GUI="${GUI:-true}"

mkdir -p "${RESULT_DIR}"

export PATH=/opt/ros/noetic/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib
source /usr/share/gazebo/setup.sh
source /opt/ros/noetic/setup.bash
source "${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/setup_gazebo.bash" \
  "${SUNRAY_PX4_DIR}" \
  "${SUNRAY_PX4_DIR}/build/px4_sitl_default"
source "${SUNRAY_WS}/devel/setup.bash"

sunray_models="${SUNRAY_WS}/simulation/sunray_simulator/models"
export GAZEBO_MODEL_DATABASE_URI="${GAZEBO_MODEL_DATABASE_URI:-http://models.gazebosim.org}"
export ROS_PACKAGE_PATH="${SUNRAY_PX4_DIR}:${SUNRAY_WS}:/opt/ros/noetic/share:${ROS_PACKAGE_PATH:-}"
export GAZEBO_MODEL_PATH="${sunray_models}/scence_models:${sunray_models}/drone_models:${sunray_models}/sensor_models:${sunray_models}/fake_models:${sunray_models}/ugv_models:${sunray_models}/aws_models:${sunray_models}/aws_vins_models:${GAZEBO_MODEL_PATH:-}"
export GAZEBO_RESOURCE_PATH="${SUNRAY_WS}/simulation/sunray_simulator:${GAZEBO_RESOURCE_PATH:-}"
export GAZEBO_PLUGIN_PATH="${SUNRAY_WS}/devel/lib:${GAZEBO_PLUGIN_PATH:-}"
export LD_LIBRARY_PATH="${SUNRAY_WS}/devel/lib:${LD_LIBRARY_PATH:-}"

rm -f /tmp/px4-sock-0 /tmp/px4-sock-1 2>/dev/null || true

nohup roslaunch "${SUNRAY_WS}/simulation/sunray_simulator/launch_uav_demo/sunray_sim_uav_planning.launch" \
  gui:="${GUI}" rviz_enable:=false \
  > "${RESULT_DIR}/sunray_mid360_gazebo.log" 2>&1 &
echo "$!" > "${RESULT_DIR}/sunray_mid360_gazebo.pid"

cat > "${RESULT_DIR}/SESSION.json" <<EOF
{
  "schema": "mosim.sunray_ros1_mid360_fastlio_review_session.v1",
  "status": "starting",
  "result_dir": "${RESULT_DIR}",
  "sunray_ws": "${SUNRAY_WS}",
  "entry": "roslaunch ${SUNRAY_WS}/simulation/sunray_simulator/launch_uav_demo/sunray_sim_uav_planning.launch gui:=${GUI} rviz_enable:=false",
  "vehicle": "sunray150_with_mid360",
  "scope": "native Sunray ROS1 Gazebo MID360 sensor chain for FAST-LIO/RViz review"
}
EOF

echo "${RESULT_DIR}"
