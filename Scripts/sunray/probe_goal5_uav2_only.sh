#!/usr/bin/env bash
# Narrow Goal5 diagnostic: start one UAV and check its MID360 topic.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/opt/mosim_work/sunray_ws/Sunray}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-/opt/mosim_work/sunray_px4}"
LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS:-/opt/mosim_work/sunray_livox_plugin_ws}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/goal5_probe_uav2_only_$(date +%Y%m%d_%H%M%S)}"
WORLD_FILE="${WORLD_FILE:-${SUNRAY_WS}/simulation/sunray_simulator/worlds/planning_test.world}"
SUNRAY_MID360_PLUGIN_DOWNSAMPLE="${SUNRAY_MID360_PLUGIN_DOWNSAMPLE:-4}"
SUNRAY_LIVOX_PLUGIN_FILENAME="${SUNRAY_LIVOX_PLUGIN_FILENAME:-${LIVOX_PLUGIN_WS}/devel/lib/liblivox_laser_simulation.so}"
SUNRAY_MID360_CSV_FILE_NAME="${SUNRAY_MID360_CSV_FILE_NAME:-mid360-real-centr.csv}"
SUNRAY_MID360_GOAL5_CSV_STRIDE="${SUNRAY_MID360_GOAL5_CSV_STRIDE:-4}"
UAV_ID="${UAV_ID:-2}"
UAV_INIT_Y="${UAV_INIT_Y:-1}"

mkdir -p "${RESULT_DIR}"

cleanup() {
  set +e
  pkill -f "roslaunch .*sunray_px4_basic" >/dev/null 2>&1 || true
  pkill -f "roslaunch .*empty_world" >/dev/null 2>&1 || true
  pkill -f "gzserver" >/dev/null 2>&1 || true
  pkill -f "gzclient" >/dev/null 2>&1 || true
  pkill -f "mavros_node" >/dev/null 2>&1 || true
  pkill -f "/opt/mosim_work/sunray_px4.*/px4" >/dev/null 2>&1 || true
  pkill -f "rosmaster" >/dev/null 2>&1 || true
  pkill -f "rosout" >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup
sleep 2

source /usr/share/gazebo/setup.sh
source /opt/ros/noetic/setup.bash
source "${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/setup_gazebo.bash" \
  "${SUNRAY_PX4_DIR}" \
  "${SUNRAY_PX4_DIR}/build/px4_sitl_default"
source "${SUNRAY_WS}/devel/setup.bash"
source "${LIVOX_PLUGIN_WS}/devel/setup.bash"

export GAZEBO_MODEL_PATH="${SUNRAY_WS}/simulation/sunray_simulator/models/scence_models:${SUNRAY_WS}/simulation/sunray_simulator/models/drone_models:${SUNRAY_WS}/simulation/sunray_simulator/models/sensor_models:${SUNRAY_WS}/simulation/sunray_simulator/models/fake_models:${GAZEBO_MODEL_PATH:-}"
export GAZEBO_PLUGIN_PATH="${LIVOX_PLUGIN_WS}/devel/lib:${SUNRAY_WS}/devel/lib:${GAZEBO_PLUGIN_PATH:-}"
export LD_LIBRARY_PATH="${LIVOX_PLUGIN_WS}/devel/lib:${SUNRAY_WS}/devel/lib:/opt/ros/noetic/lib:${LD_LIBRARY_PATH:-}"
export ROS_PACKAGE_PATH="${SUNRAY_PX4_DIR}:${SUNRAY_WS}:/opt/ros/noetic/share:${ROS_PACKAGE_PATH:-}"
export SUNRAY_MID360_PLUGIN_DOWNSAMPLE
export SUNRAY_LIVOX_PLUGIN_FILENAME
export SUNRAY_MID360_CSV_FILE_NAME

if [[ ! -f "${LIVOX_PLUGIN_WS}/devel/lib/liblivox_laser_simulation.so" || ! -f "${LIVOX_PLUGIN_WS}/.mosim_multiuav_livox_patch_v1" ]]; then
  LOG_PATH="${RESULT_DIR}/sunray_livox_plugin_build.log" \
    SUNRAY_WS="${SUNRAY_WS}" \
    LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS}" \
    PROJECT_ROOT="${PROJECT_ROOT}" \
    bash "${PROJECT_ROOT}/Scripts/sunray/setup_sunray_livox_gazebo_plugin.sh" \
    > "${RESULT_DIR}/sunray_livox_plugin_setup_stdout.txt" 2>&1
fi

scan_dir="${LIVOX_PLUGIN_WS}/src/livox_laser_simulation/scan_mode"
source_csv="${scan_dir}/mid360-real-centr.csv"
target_csv="${scan_dir}/${SUNRAY_MID360_CSV_FILE_NAME}"
if [[ "${SUNRAY_MID360_CSV_FILE_NAME}" != "mid360-real-centr.csv" ]]; then
  awk -F',' -v stride="${SUNRAY_MID360_GOAL5_CSV_STRIDE}" 'NR == 1 || ((NR - 2) % stride == 0)' "${source_csv}" > "${target_csv}"
fi

python3 "${PROJECT_ROOT}/Scripts/sunray/sync_assembled_model_into_sunray_ros1.py" \
  --project-root "${PROJECT_ROOT}" \
  --sunray-ws "${SUNRAY_WS}" \
  --manifest "${RESULT_DIR}/sync.json" \
  > "${RESULT_DIR}/sync.log" 2>&1

roslaunch gazebo_ros empty_world.launch \
  gui:=false world_name:="${WORLD_FILE}" use_sim_time:=true \
  > "${RESULT_DIR}/world.log" 2>&1 &
sleep 8

roslaunch sunray_simulator sunray_px4_basic.launch \
  uav_id:="${UAV_ID}" vehicle:=sunray150_with_mid360 \
  uav_init_x:=0 uav_init_y:="${UAV_INIT_Y}" uav_init_z:=0.2 \
  > "${RESULT_DIR}/uav${UAV_ID}.log" 2>&1 &

for _ in $(seq 1 70); do
  if timeout 2s rostopic echo -n 1 "/uav${UAV_ID}/livox/lidar" > "${RESULT_DIR}/uav${UAV_ID}_lidar.txt" 2>/dev/null; then
    echo "PASS:${RESULT_DIR}"
    exit 0
  fi
  sleep 1
done

echo "FAIL:${RESULT_DIR}"
exit 7
