#!/usr/bin/env bash
# Run Goal5: EGO-Swarm 2/3 UAVs -> per-UAV original px4ctrl -> PX4/Gazebo.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/opt/mosim_work/sunray_ws/Sunray}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-/opt/mosim_work/sunray_px4}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
GOAL4_EGO_WS="${GOAL4_EGO_WS:-/opt/mosim_work/goal4_ego_ws_px4msg}"
LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS:-/opt/mosim_work/sunray_livox_plugin_ws}"
UAV_NUM="${UAV_NUM:-2}"
RUN_ID="${RUN_ID:-sunray_ros1_goal5_ego_swarm_${UAV_NUM}uav_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
GUI="${GUI:-false}"
WORLD_FILE="${WORLD_FILE:-${SUNRAY_WS}/simulation/sunray_simulator/worlds/planning_test.world}"
USE_SIM_TIME="${USE_SIM_TIME:-true}"
SUNRAY_GAZEBO_MAX_STEP_SIZE_S="${SUNRAY_GAZEBO_MAX_STEP_SIZE_S:-0.001}"
SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ="${SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ:-1000}"
SUNRAY_MID360_PLUGIN_DOWNSAMPLE="${SUNRAY_MID360_PLUGIN_DOWNSAMPLE:-4}"
SUNRAY_LIVOX_PLUGIN_FILENAME="${SUNRAY_LIVOX_PLUGIN_FILENAME:-${LIVOX_PLUGIN_WS}/devel/lib/liblivox_laser_simulation.so}"
SUNRAY_MID360_CSV_FILE_NAME="${SUNRAY_MID360_CSV_FILE_NAME:-mid360-real-centr.csv}"
SUNRAY_MID360_GOAL5_CSV_STRIDE="${SUNRAY_MID360_GOAL5_CSV_STRIDE:-4}"
MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-90}"
ODOM_BRIDGE_READY_TIMEOUT_S="${ODOM_BRIDGE_READY_TIMEOUT_S:-25}"
MAVROS_STREAM_RATE_HZ="${MAVROS_STREAM_RATE_HZ:-100}"
TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-280}"
VEHICLE="${VEHICLE:-sunray150_with_mid360}"
SEQUENTIAL_SPAWN="${SEQUENTIAL_SPAWN:-false}"
PRELOAD_GAZEBO_MODELS="${PRELOAD_GAZEBO_MODELS:-true}"
GOAL5_PRELOADED_INIT_Z="${GOAL5_PRELOADED_INIT_Z:-0.35}"
SUNRAY_STRIP_PX4_MODEL_PATH="${SUNRAY_STRIP_PX4_MODEL_PATH:-true}"
LIDAR_READY_TIMEOUT_S="${LIDAR_READY_TIMEOUT_S:-90}"
SWARM_BASELINE_ONLY="${SWARM_BASELINE_ONLY:-false}"

START1_X="${START1_X:-0.0}"
START1_Y="${START1_Y:--1.0}"
START2_X="${START2_X:-0.0}"
START2_Y="${START2_Y:-1.0}"
START3_X="${START3_X:--1.5}"
START3_Y="${START3_Y:-0.0}"
TARGET1_X="${TARGET1_X:-4.0}"
TARGET1_Y="${TARGET1_Y:--1.0}"
TARGET1_Z="${TARGET1_Z:-1.0}"
TARGET2_X="${TARGET2_X:-4.0}"
TARGET2_Y="${TARGET2_Y:-1.0}"
TARGET2_Z="${TARGET2_Z:-1.0}"
TARGET3_X="${TARGET3_X:-4.0}"
TARGET3_Y="${TARGET3_Y:-0.0}"
TARGET3_Z="${TARGET3_Z:-1.25}"
EGO_MAX_VEL="${EGO_MAX_VEL:-0.8}"
EGO_MAX_ACC="${EGO_MAX_ACC:-0.8}"

PX4CTRL_MASS="${PX4CTRL_MASS:-0.67}"
PX4CTRL_HOVER_PERCENTAGE="${PX4CTRL_HOVER_PERCENTAGE:-0.37}"
PX4CTRL_KP_XY="${PX4CTRL_KP_XY:-10.0}"
PX4CTRL_KP_Z="${PX4CTRL_KP_Z:-3.0}"
PX4CTRL_KV_XY="${PX4CTRL_KV_XY:-5.2}"
PX4CTRL_KV_Z="${PX4CTRL_KV_Z:-3.0}"
PX4CTRL_CTRL_FREQ_MAX="${PX4CTRL_CTRL_FREQ_MAX:-100.0}"
PX4CTRL_USE_BODYRATE_CTRL="${PX4CTRL_USE_BODYRATE_CTRL:-false}"
PX4CTRL_START_EXTERNAL_FUSION="${PX4CTRL_START_EXTERNAL_FUSION:-true}"
PX4CTRL_EXTERNAL_FUSION_USE_VISION_POSE="${PX4CTRL_EXTERNAL_FUSION_USE_VISION_POSE:-true}"

if [[ "${UAV_NUM}" != "2" && "${UAV_NUM}" != "3" ]]; then
  echo "UAV_NUM must be 2 or 3, got ${UAV_NUM}" >&2
  exit 2
fi

mkdir -p "${RESULT_DIR}"

PIDS=()
cleanup() {
  set +e
  if [[ "${KEEP_ALIVE:-false}" == "true" ]]; then
    return
  fi
  for pid in "${PIDS[@]:-}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
  sleep 2
  for pid in "${PIDS[@]:-}"; do
    kill -9 "${pid}" >/dev/null 2>&1 || true
  done
  pkill -f "mosim_px4ctrl_ego_swarm_mission" >/dev/null 2>&1 || true
  pkill -f "mosim_goal4_pointcloud_to_world" >/dev/null 2>&1 || true
  pkill -f "mosim_mavros_pose_velocity_to_odom_bridge" >/dev/null 2>&1 || true
  pkill -f "drone_[0-9]_ego_planner_node" >/dev/null 2>&1 || true
  pkill -f "drone_[0-9]_traj_server" >/dev/null 2>&1 || true
  pkill -f "px4ctrl_node" >/dev/null 2>&1 || true
  pkill -f "external_fusion_node" >/dev/null 2>&1 || true
  pkill -f "roslaunch .*goal5_swarm_px4_gazebo" >/dev/null 2>&1 || true
  pkill -f "roslaunch .*ego_swarm_px4ctrl_goal5" >/dev/null 2>&1 || true
  pkill -f "gzserver" >/dev/null 2>&1 || true
  pkill -f "gzclient" >/dev/null 2>&1 || true
  pkill -f "mavros_node" >/dev/null 2>&1 || true
  pkill -f "/opt/mosim_work/sunray_px4.*/px4" >/dev/null 2>&1 || true
  pkill -f "rosmaster" >/dev/null 2>&1 || true
  pkill -f "rosout" >/dev/null 2>&1 || true
}
trap cleanup EXIT

source_env() {
  export PATH=/opt/ros/noetic/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib
  set +u
  source /usr/share/gazebo/setup.sh
  source /opt/ros/noetic/setup.bash
  source "${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/setup_gazebo.bash" \
    "${SUNRAY_PX4_DIR}" \
    "${SUNRAY_PX4_DIR}/build/px4_sitl_default"
  source "${SUNRAY_WS}/devel/setup.bash"
  if [[ -f "${LIVOX_PLUGIN_WS}/devel/setup.bash" ]]; then
    source "${LIVOX_PLUGIN_WS}/devel/setup.bash"
  fi
  source "${GOAL4_EGO_WS}/devel/setup.bash"
  set -u

  local sunray_models="${SUNRAY_WS}/simulation/sunray_simulator/models"
  local px4_gazebo_models="${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/sitl_gazebo-classic/models"
  if [[ "${SUNRAY_STRIP_PX4_MODEL_PATH}" == "true" ]]; then
    GAZEBO_MODEL_PATH="$(
      python3 - "${GAZEBO_MODEL_PATH:-}" "${px4_gazebo_models}" <<'PY'
import sys
value, remove = sys.argv[1], sys.argv[2]
print(":".join(part for part in value.split(":") if part and part != remove))
PY
    )"
  fi
  export PROJECT_ROOT
  export CMAKE_PREFIX_PATH="${GOAL4_EGO_WS}/devel:${LIVOX_PLUGIN_WS}/devel:${PX4CTRL_WS}/devel:${SUNRAY_WS}/devel:/opt/ros/noetic:${CMAKE_PREFIX_PATH:-}"
  export ROS_PACKAGE_PATH="${GOAL4_EGO_WS}/src:${PX4CTRL_WS}/src:${SUNRAY_PX4_DIR}:${SUNRAY_WS}:/opt/ros/noetic/share:${ROS_PACKAGE_PATH:-}"
  export PYTHONPATH="${GOAL4_EGO_WS}/devel/lib/python3/dist-packages:${PX4CTRL_WS}/devel/lib/python3/dist-packages:${SUNRAY_WS}/devel/lib/python3/dist-packages:${PYTHONPATH:-}"
  export GAZEBO_MODEL_PATH="${sunray_models}/scence_models:${sunray_models}/drone_models:${sunray_models}/sensor_models:${sunray_models}/fake_models:${sunray_models}/ugv_models:${sunray_models}/aws_models:${sunray_models}/aws_vins_models:${GAZEBO_MODEL_PATH:-}"
  export GAZEBO_RESOURCE_PATH="${SUNRAY_WS}/simulation/sunray_simulator:${GAZEBO_RESOURCE_PATH:-}"
  export GAZEBO_PLUGIN_PATH="${LIVOX_PLUGIN_WS}/devel/lib:${SUNRAY_WS}/devel/lib:${GAZEBO_PLUGIN_PATH:-}"
  export LD_LIBRARY_PATH="${GOAL4_EGO_WS}/devel/lib:${LIVOX_PLUGIN_WS}/devel/lib:${PX4CTRL_WS}/devel/lib:${SUNRAY_WS}/devel/lib:/opt/ros/noetic/lib:${LD_LIBRARY_PATH:-}"
}

wait_topic_sample() {
  local topic="$1"
  local output="$2"
  local timeout_s="$3"
  local deadline=$((SECONDS + timeout_s))
  while (( SECONDS < deadline )); do
    if timeout 3s rostopic echo -n 1 "${topic}" > "${output}" 2>/dev/null; then
      return 0
    fi
    sleep 1
  done
  return 1
}

wait_mavros_connected() {
  local uid="$1"
  local output="${RESULT_DIR}/uav${uid}_mavros_state_first.txt"
  local deadline=$((SECONDS + MAVROS_READY_TIMEOUT_S))
  while (( SECONDS < deadline )); do
    if timeout 3s rostopic echo -n 1 "/uav${uid}/mavros/state" > "${output}" 2>/dev/null; then
      if grep -q "connected: True" "${output}"; then
        return 0
      fi
    fi
    sleep 1
  done
  return 1
}

request_stream_rate() {
  local uid="$1"
  if [[ "${MAVROS_STREAM_RATE_HZ}" == "0" || "${MAVROS_STREAM_RATE_HZ}" == "0.0" ]]; then
    return 0
  fi
  {
    echo "MAVROS_STREAM_RATE_HZ=${MAVROS_STREAM_RATE_HZ}"
    timeout 8s rosservice call "/uav${uid}/mavros/set_stream_rate" "stream_id: 6
message_rate: ${MAVROS_STREAM_RATE_HZ}
on_off: true" || true
    timeout 8s rosservice call "/uav${uid}/mavros/cmd/command" "broadcast: false
command: 511
confirmation: 0
param1: 32
param2: $((1000000 / MAVROS_STREAM_RATE_HZ))
param3: 0
param4: 0
param5: 0
param6: 0
param7: 0" || true
  } > "${RESULT_DIR}/uav${uid}_mavros_stream_rate_request.txt" 2>&1
}

prepare_goal5_mid360_csv() {
  local scan_dir="${LIVOX_PLUGIN_WS}/src/livox_laser_simulation/scan_mode"
  local source_csv="${scan_dir}/mid360-real-centr.csv"
  local target_csv="${scan_dir}/${SUNRAY_MID360_CSV_FILE_NAME}"
  if [[ "${SUNRAY_MID360_CSV_FILE_NAME}" == "mid360-real-centr.csv" ]]; then
    return 0
  fi
  if [[ ! -f "${source_csv}" ]]; then
    echo "MID360 source csv missing: ${source_csv}" >&2
    exit 8
  fi
  awk -F',' -v stride="${SUNRAY_MID360_GOAL5_CSV_STRIDE}" 'NR == 1 || ((NR - 2) % stride == 0)' "${source_csv}" > "${target_csv}"
}

start_gazebo_world() {
  roslaunch gazebo_ros empty_world.launch \
    gui:="${GUI}" world_name:="${WORLD_FILE}" debug:=false verbose:=false paused:=false use_sim_time:="${USE_SIM_TIME}" \
    > "${RESULT_DIR}/sunray_goal5_gazebo_world.log" 2>&1 &
  PIDS+=("$!")
  echo "${PIDS[-1]}" > "${RESULT_DIR}/sunray_goal5_gazebo_world.pid"
  sleep 8
}

start_uav_instance() {
  local uid="$1"
  local x="$2"
  local y="$3"
  local z="$4"
  local yaw="$5"
  roslaunch sunray_simulator sunray_px4_basic.launch \
    uav_id:="${uid}" vehicle:="${VEHICLE}" \
    uav_init_x:="${x}" uav_init_y:="${y}" uav_init_z:="${z}" uav_init_yaw:="${yaw}" \
    > "${RESULT_DIR}/uav${uid}_sunray_px4_basic.log" 2>&1 &
  PIDS+=("$!")
  echo "${PIDS[-1]}" > "${RESULT_DIR}/uav${uid}_sunray_px4_basic.pid"
}

write_px4ctrl_launch() {
  local launch_path="${RESULT_DIR}/px4ctrl_swarm_mosim.launch"
  local config
  config="$(rospack find px4ctrl)/config/ctrl_param_fpv.yaml"
  {
    echo "<launch>"
    for uid in $(seq 1 "${UAV_NUM}"); do
      cat <<EOF
  <node pkg="px4ctrl" type="px4ctrl_node" name="px4ctrl_uav${uid}" output="screen">
    <remap from="~odom" to="/uav${uid}/mavros/local_position/odom" />
    <remap from="~cmd" to="/uav${uid}/position_cmd" />
    <remap from="~takeoff_land" to="/uav${uid}/px4ctrl/takeoff_land" />
    <remap from="/mavros/state" to="/uav${uid}/mavros/state" />
    <remap from="/mavros/extended_state" to="/uav${uid}/mavros/extended_state" />
    <remap from="/mavros/imu/data" to="/uav${uid}/mavros/imu/data" />
    <remap from="/mavros/rc/in" to="/uav${uid}/mavros/rc/in" />
    <remap from="/mavros/battery" to="/uav${uid}/mavros/battery" />
    <remap from="/mavros/setpoint_raw/attitude" to="/uav${uid}/mavros/setpoint_raw/attitude" />
    <remap from="/mavros/setpoint_raw/target_attitude" to="/uav${uid}/mavros/setpoint_raw/target_attitude" />
    <remap from="/mavros/set_mode" to="/uav${uid}/mavros/set_mode" />
    <remap from="/mavros/cmd/arming" to="/uav${uid}/mavros/cmd/arming" />
    <remap from="/mavros/cmd/command" to="/uav${uid}/mavros/cmd/command" />
    <remap from="/debugPx4ctrl" to="/uav${uid}/debugPx4ctrl" />
    <rosparam command="load" file="${config}" />
    <param name="mass" value="${PX4CTRL_MASS}" />
    <param name="ctrl_freq_max" value="${PX4CTRL_CTRL_FREQ_MAX}" />
    <param name="use_bodyrate_ctrl" value="${PX4CTRL_USE_BODYRATE_CTRL}" />
    <param name="mosim_generated_core_mode" value="original" />
    <param name="auto_takeoff_land/enable" value="true" />
    <param name="auto_takeoff_land/enable_auto_arm" value="true" />
    <param name="auto_takeoff_land/no_RC" value="true" />
    <param name="auto_takeoff_land/takeoff_height" value="1.0" />
    <param name="auto_takeoff_land/takeoff_land_speed" value="0.25" />
    <param name="thrust_model/hover_percentage" value="${PX4CTRL_HOVER_PERCENTAGE}" />
    <param name="gain/Kp0" value="${PX4CTRL_KP_XY}" />
    <param name="gain/Kp1" value="${PX4CTRL_KP_XY}" />
    <param name="gain/Kp2" value="${PX4CTRL_KP_Z}" />
    <param name="gain/Kv0" value="${PX4CTRL_KV_XY}" />
    <param name="gain/Kv1" value="${PX4CTRL_KV_XY}" />
    <param name="gain/Kv2" value="${PX4CTRL_KV_Z}" />
  </node>
EOF
    done
    echo "</launch>"
  } > "${launch_path}"
  echo "${launch_path}"
}

if [[ ! -d "${PX4CTRL_WS}/devel" ]]; then
  echo "PX4CTRL_WS devel missing: ${PX4CTRL_WS}/devel" >&2
  exit 2
fi
if [[ ! -d "${GOAL4_EGO_WS}/devel" ]]; then
  echo "GOAL4_EGO_WS devel missing: ${GOAL4_EGO_WS}/devel; run Scripts/sunray/setup_goal4_ego_overlay.sh" >&2
  exit 2
fi
if [[ ! -f "${LIVOX_PLUGIN_WS}/devel/lib/liblivox_laser_simulation.so" || ! -f "${LIVOX_PLUGIN_WS}/.mosim_multiuav_livox_patch_v1" ]]; then
  LOG_PATH="${RESULT_DIR}/sunray_livox_plugin_build.log" \
    SUNRAY_WS="${SUNRAY_WS}" \
    LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS}" \
    PROJECT_ROOT="${PROJECT_ROOT}" \
    bash "${PROJECT_ROOT}/Scripts/sunray/setup_sunray_livox_gazebo_plugin.sh" \
    > "${RESULT_DIR}/sunray_livox_plugin_setup_stdout.txt" 2>&1
fi
prepare_goal5_mid360_csv

cleanup
sleep 3
source_env

{
  echo "ROS_ENV_SNAPSHOT"
  env | grep -E '^(ROS_PACKAGE_PATH|PYTHONPATH|CMAKE_PREFIX_PATH|LD_LIBRARY_PATH|PROJECT_ROOT|GAZEBO_MODEL_PATH|GAZEBO_PLUGIN_PATH|GAZEBO_RESOURCE_PATH)=' || true
  echo "SUNRAY_STRIP_PX4_MODEL_PATH=${SUNRAY_STRIP_PX4_MODEL_PATH}"
  echo "SUNRAY_PX4_DIR=${SUNRAY_PX4_DIR}"
  echo "PX4_GAZEBO_MODEL_PATH=${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/sitl_gazebo-classic/models"
  if [[ "${GAZEBO_MODEL_PATH:-}" == *"${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/sitl_gazebo-classic/models"* ]]; then
    echo "PX4_MODEL_PATH_PRESENT=true"
  else
    echo "PX4_MODEL_PATH_PRESENT=false"
  fi
  rospack profile || true
  for pkg in px4ctrl quadrotor_msgs ego_planner traj_utils plan_env sunray_msgs sunray_uav_control; do
    echo "rospack find ${pkg}"
    rospack find "${pkg}"
  done
  python3 -c "import sunray_msgs.msg, quadrotor_msgs.msg, traj_utils.msg; print('python message imports ok')"
} > "${RESULT_DIR}/ros_env_snapshot.txt" 2>&1 || {
  echo "ROS environment missing required Goal5 packages; see ${RESULT_DIR}/ros_env_snapshot.txt" >&2
  exit 6
}

export SUNRAY_GAZEBO_MAX_STEP_SIZE_S
export SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ
export SUNRAY_MID360_PLUGIN_DOWNSAMPLE
export SUNRAY_LIVOX_PLUGIN_FILENAME
export SUNRAY_MID360_CSV_FILE_NAME

python3 "${PROJECT_ROOT}/Scripts/sunray/sync_assembled_model_into_sunray_ros1.py" \
  --project-root "${PROJECT_ROOT}" \
  --sunray-ws "${SUNRAY_WS}" \
  --manifest "${RESULT_DIR}/assembled_model_sync.json" \
  > "${RESULT_DIR}/assembled_model_sync.log" 2>&1

rm -f /tmp/px4-sock-* 2>/dev/null || true

if [[ "${SEQUENTIAL_SPAWN}" == "true" ]]; then
  start_gazebo_world
  start_uav_instance 1 "${START1_X}" "${START1_Y}" "0.2" "0.0"
  if ! wait_mavros_connected 1; then
    echo "MAVROS did not connect for uav1" >&2
    exit 4
  fi
  request_stream_rate 1
  if ! wait_topic_sample "/uav1/livox/lidar" "${RESULT_DIR}/uav1_raw_lidar_first.txt" 35; then
    echo "No raw MID360 point cloud on /uav1/livox/lidar" >&2
    exit 7
  fi

  start_uav_instance 2 "${START2_X}" "${START2_Y}" "0.2" "0.0"
  if ! wait_mavros_connected 2; then
    echo "MAVROS did not connect for uav2" >&2
    exit 4
  fi
  request_stream_rate 2
  if ! wait_topic_sample "/uav2/livox/lidar" "${RESULT_DIR}/uav2_raw_lidar_first.txt" 35; then
    echo "No raw MID360 point cloud on /uav2/livox/lidar" >&2
    exit 7
  fi

  if [[ "${UAV_NUM}" == "3" ]]; then
    start_uav_instance 3 "${START3_X}" "${START3_Y}" "0.2" "0.0"
    if ! wait_mavros_connected 3; then
      echo "MAVROS did not connect for uav3" >&2
      exit 4
    fi
    request_stream_rate 3
    if ! wait_topic_sample "/uav3/livox/lidar" "${RESULT_DIR}/uav3_raw_lidar_first.txt" 35; then
      echo "No raw MID360 point cloud on /uav3/livox/lidar" >&2
      exit 7
    fi
  fi
else
  if [[ "${PRELOAD_GAZEBO_MODELS}" == "true" ]]; then
    PRELOADED_WORLD_FILE="${RESULT_DIR}/goal5_preloaded_${UAV_NUM}uav.world"
    python3 "${PROJECT_ROOT}/Scripts/sunray/create_goal5_preloaded_swarm_world.py" \
      --sunray-ws "${SUNRAY_WS}" \
      --base-world "${WORLD_FILE}" \
      --output-world "${PRELOADED_WORLD_FILE}" \
      --vehicle "${VEHICLE}" \
      --uav-num "${UAV_NUM}" \
      --uav1 "${START1_X}" "${START1_Y}" "${GOAL5_PRELOADED_INIT_Z}" "0.0" \
      --uav2 "${START2_X}" "${START2_Y}" "${GOAL5_PRELOADED_INIT_Z}" "0.0" \
      --uav3 "${START3_X}" "${START3_Y}" "${GOAL5_PRELOADED_INIT_Z}" "0.0" \
      > "${RESULT_DIR}/goal5_preloaded_world_generation.log" 2>&1
    GOAL5_GAZEBO_LAUNCH="${PROJECT_ROOT}/Scripts/sunray/goal5_swarm_px4_preloaded_gazebo.launch"
    GOAL5_WORLD_FILE="${PRELOADED_WORLD_FILE}"
  else
    GOAL5_GAZEBO_LAUNCH="${PROJECT_ROOT}/Scripts/sunray/goal5_swarm_px4_gazebo.launch"
    GOAL5_WORLD_FILE="${WORLD_FILE}"
  fi

  roslaunch "${GOAL5_GAZEBO_LAUNCH}" \
    uav_num:="${UAV_NUM}" vehicle:="${VEHICLE}" gui:="${GUI}" world:="${GOAL5_WORLD_FILE}" use_sim_time:="${USE_SIM_TIME}" \
    uav1_init_x:="${START1_X}" uav1_init_y:="${START1_Y}" \
    uav2_init_x:="${START2_X}" uav2_init_y:="${START2_Y}" \
    uav3_init_x:="${START3_X}" uav3_init_y:="${START3_Y}" \
    > "${RESULT_DIR}/sunray_goal5_swarm_gazebo.log" 2>&1 &
  PIDS+=("$!")
  echo "${PIDS[-1]}" > "${RESULT_DIR}/sunray_goal5_swarm_gazebo.pid"

  for uid in $(seq 1 "${UAV_NUM}"); do
    if ! wait_mavros_connected "${uid}"; then
      echo "MAVROS did not connect for uav${uid}" >&2
      exit 4
    fi
    request_stream_rate "${uid}"
  done
fi

if [[ "${PX4CTRL_START_EXTERNAL_FUSION}" == "true" ]]; then
  for uid in $(seq 1 "${UAV_NUM}"); do
    rosrun sunray_uav_control external_fusion_node \
      __name:="external_fusion_uav${uid}" \
      _uav_id:="${uid}" _external_source:=2 _uav_name:=uav \
      _position_topic:="/uav${uid}/mavros/local_position/pose" \
      _use_vision_pose:="${PX4CTRL_EXTERNAL_FUSION_USE_VISION_POSE}" \
      > "${RESULT_DIR}/uav${uid}_external_fusion.log" 2>&1 &
    PIDS+=("$!")
  done
  sleep 3
fi

for uid in $(seq 1 "${UAV_NUM}"); do
  python3 "${PROJECT_ROOT}/Scripts/sunray/mavros_pose_velocity_to_odom_bridge.py" \
    --pose-topic "/uav${uid}/mavros/local_position/pose" \
    --velocity-topic "/uav${uid}/mavros/local_position/velocity_local" \
    --output-topic "/uav${uid}/mavros/local_position/odom" \
    --frame-id world \
    --child-frame-id "uav${uid}/base_link" \
    > "${RESULT_DIR}/uav${uid}_odom_bridge.log" 2>&1 &
  PIDS+=("$!")
done

for uid in $(seq 1 "${UAV_NUM}"); do
  if ! wait_topic_sample "/uav${uid}/mavros/local_position/odom" "${RESULT_DIR}/uav${uid}_odom_first.txt" "${ODOM_BRIDGE_READY_TIMEOUT_S}"; then
    echo "No odometry on /uav${uid}/mavros/local_position/odom" >&2
    exit 5
  fi
done

for uid in $(seq 1 "${UAV_NUM}"); do
  if [[ ! -s "${RESULT_DIR}/uav${uid}_raw_lidar_first.txt" ]]; then
    if ! wait_topic_sample "/uav${uid}/livox/lidar" "${RESULT_DIR}/uav${uid}_raw_lidar_first.txt" "${LIDAR_READY_TIMEOUT_S}"; then
      echo "No raw MID360 point cloud on /uav${uid}/livox/lidar" >&2
      exit 7
    fi
  fi
done

PX4CTRL_LAUNCH="$(write_px4ctrl_launch)"
roslaunch "${PX4CTRL_LAUNCH}" > "${RESULT_DIR}/px4ctrl_swarm.log" 2>&1 &
PIDS+=("$!")
sleep 5

for uid in $(seq 1 "${UAV_NUM}"); do
  python3 "${PROJECT_ROOT}/Scripts/sunray/goal4_pointcloud_to_world_node.py" \
    _input_point_topic:="/uav${uid}/livox/lidar" \
    _output_point_topic:="/uav${uid}/livox_world" \
    _odom_topic:="/uav${uid}/mavros/local_position/odom" \
    _frame_id:=world \
    > "${RESULT_DIR}/uav${uid}_pointcloud_to_world.log" 2>&1 &
  PIDS+=("$!")
done
sleep 2

if [[ "${SWARM_BASELINE_ONLY}" == "true" ]]; then
  set +e
  timeout "${TOTAL_TIMEOUT_S}s" python3 "${PROJECT_ROOT}/Scripts/sunray/px4ctrl_swarm_basic_mission_node.py" \
    --result-dir "${RESULT_DIR}" \
    --uav-num "${UAV_NUM}" \
    --start1-x "${START1_X}" --start1-y "${START1_Y}" \
    --start2-x "${START2_X}" --start2-y "${START2_Y}" \
    --start3-x "${START3_X}" --start3-y "${START3_Y}" \
    > "${RESULT_DIR}/px4ctrl_swarm_basic_mission.log" 2>&1
  MISSION_EXIT_CODE=$?
  set -e

  cat > "${RESULT_DIR}/RUN_MANIFEST.json" <<EOF
{
  "schema": "mosim.sunray_ros1.goal5_swarm_baseline_manifest.v1",
  "result_dir": "${RESULT_DIR}",
  "uav_num": ${UAV_NUM},
  "baseline_only": true,
  "controller": "original Fast-Drone-250 px4ctrl, one instance per UAV",
  "planner": "not launched; this gate isolates multi-UAV PX4/Gazebo/px4ctrl before EGO-Swarm",
  "spawn_mode": "${SEQUENTIAL_SPAWN}",
  "world_file": "${WORLD_FILE}",
  "use_sim_time": "${USE_SIM_TIME}",
  "topics": {
    "raw_lidar": ["/uav1/livox/lidar", "/uav2/livox/lidar", "/uav3/livox/lidar"],
    "world_cloud": ["/uav1/livox_world", "/uav2/livox_world", "/uav3/livox_world"],
    "target_attitude": ["/uav1/mavros/setpoint_raw/target_attitude", "/uav2/mavros/setpoint_raw/target_attitude", "/uav3/mavros/setpoint_raw/target_attitude"]
  },
  "px4ctrl": {
    "mass": ${PX4CTRL_MASS},
    "hover_percentage": ${PX4CTRL_HOVER_PERCENTAGE},
    "Kp_xy": ${PX4CTRL_KP_XY},
    "Kp_z": ${PX4CTRL_KP_Z},
    "Kv_xy": ${PX4CTRL_KV_XY},
    "Kv_z": ${PX4CTRL_KV_Z},
    "ctrl_freq_max": ${PX4CTRL_CTRL_FREQ_MAX},
    "use_bodyrate_ctrl": ${PX4CTRL_USE_BODYRATE_CTRL}
  },
  "mission_exit_code": ${MISSION_EXIT_CODE},
  "claim_boundary": "Multi-UAV original px4ctrl/PX4/Gazebo takeoff-hover-land baseline only; no EGO-Swarm planning success claim."
}
EOF

  echo "${RESULT_DIR}"
  exit "${MISSION_EXIT_CODE}"
fi

roslaunch "${PROJECT_ROOT}/Scripts/sunray/ego_swarm_px4ctrl_goal5.launch" \
  uav_num:="${UAV_NUM}" \
  target1_x:="${TARGET1_X}" target1_y:="${TARGET1_Y}" target1_z:="${TARGET1_Z}" \
  target2_x:="${TARGET2_X}" target2_y:="${TARGET2_Y}" target2_z:="${TARGET2_Z}" \
  target3_x:="${TARGET3_X}" target3_y:="${TARGET3_Y}" target3_z:="${TARGET3_Z}" \
  max_vel:="${EGO_MAX_VEL}" max_acc:="${EGO_MAX_ACC}" \
  > "${RESULT_DIR}/ego_swarm_px4ctrl_goal5.log" 2>&1 &
PIDS+=("$!")
sleep 4

set +e
timeout "${TOTAL_TIMEOUT_S}s" python3 "${PROJECT_ROOT}/Scripts/sunray/px4ctrl_ego_swarm_mission_node.py" \
  --result-dir "${RESULT_DIR}" \
  --uav-num "${UAV_NUM}" \
  --start1-x "${START1_X}" --start1-y "${START1_Y}" \
  --start2-x "${START2_X}" --start2-y "${START2_Y}" \
  --start3-x "${START3_X}" --start3-y "${START3_Y}" \
  --target1-x "${TARGET1_X}" --target1-y "${TARGET1_Y}" --target1-z "${TARGET1_Z}" \
  --target2-x "${TARGET2_X}" --target2-y "${TARGET2_Y}" --target2-z "${TARGET2_Z}" \
  --target3-x "${TARGET3_X}" --target3-y "${TARGET3_Y}" --target3-z "${TARGET3_Z}" \
  > "${RESULT_DIR}/px4ctrl_ego_swarm_mission.log" 2>&1
MISSION_EXIT_CODE=$?
set -e

cat > "${RESULT_DIR}/RUN_MANIFEST.json" <<EOF
{
  "schema": "mosim.sunray_ros1.goal5_ego_swarm_manifest.v1",
  "result_dir": "${RESULT_DIR}",
  "uav_num": ${UAV_NUM},
  "baseline_only": false,
  "controller": "original Fast-Drone-250 px4ctrl, one instance per UAV",
  "planner": "EGO-Swarm official planner/traj_server, per-UAV command isolation",
  "spawn_mode": "${SEQUENTIAL_SPAWN}",
  "world_file": "${WORLD_FILE}",
  "use_sim_time": "${USE_SIM_TIME}",
  "lidar_ready_timeout_s": ${LIDAR_READY_TIMEOUT_S},
  "mid360_plugin_downsample": ${SUNRAY_MID360_PLUGIN_DOWNSAMPLE},
  "mid360_csv_file_name": "${SUNRAY_MID360_CSV_FILE_NAME}",
  "mid360_goal5_csv_stride": ${SUNRAY_MID360_GOAL5_CSV_STRIDE},
  "topics": {
    "position_cmd": ["/uav1/position_cmd", "/uav2/position_cmd", "/uav3/position_cmd"],
    "bspline": ["/drone_0_planning/bspline", "/drone_1_planning/bspline", "/drone_2_planning/bspline"],
    "raw_lidar": ["/uav1/livox/lidar", "/uav2/livox/lidar", "/uav3/livox/lidar"],
    "world_cloud": ["/uav1/livox_world", "/uav2/livox_world", "/uav3/livox_world"]
  },
  "px4ctrl": {
    "mass": ${PX4CTRL_MASS},
    "hover_percentage": ${PX4CTRL_HOVER_PERCENTAGE},
    "Kp_xy": ${PX4CTRL_KP_XY},
    "Kp_z": ${PX4CTRL_KP_Z},
    "Kv_xy": ${PX4CTRL_KV_XY},
    "Kv_z": ${PX4CTRL_KV_Z},
    "ctrl_freq_max": ${PX4CTRL_CTRL_FREQ_MAX},
    "use_bodyrate_ctrl": ${PX4CTRL_USE_BODYRATE_CTRL}
  },
  "mission_exit_code": ${MISSION_EXIT_CODE},
  "claim_boundary": "Goal5 EGO-Swarm official planning baseline through original px4ctrl/MAVROS/PX4/Gazebo; no fake_drone and no ROS2/x500."
}
EOF

echo "${RESULT_DIR}"
exit "${MISSION_EXIT_CODE}"
