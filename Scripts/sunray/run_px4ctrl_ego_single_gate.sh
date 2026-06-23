#!/usr/bin/env bash
# Run Goal4: EGO single-UAV planner -> traj_server -> original px4ctrl -> PX4/Gazebo.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/opt/mosim_work/sunray_ws/Sunray}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-/opt/mosim_work/sunray_px4}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
GOAL4_EGO_WS="${GOAL4_EGO_WS:-/opt/mosim_work/goal4_ego_ws_px4msg}"
GOAL4_EGOV2_WS="${GOAL4_EGOV2_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/goal4_egov2_ws_px4msg}"
GOAL4_DIFF_PLANNER_WS="${GOAL4_DIFF_PLANNER_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/goal4_diff_planner_ws_px4msg}"
PLANNER_VARIANT="${PLANNER_VARIANT:-ego_v1}"
PLANNER_POSITION_CMD_TOPIC="${PLANNER_POSITION_CMD_TOPIC:-/position_cmd}"
DIFF_RAW_POSITION_CMD_TOPIC="${DIFF_RAW_POSITION_CMD_TOPIC:-/diff_planner/position_cmd_raw}"
DIFF_ENABLE_CMD_SAFETY_ADAPTER="${DIFF_ENABLE_CMD_SAFETY_ADAPTER:-true}"
DIFF_CMD_MIN_Z="${DIFF_CMD_MIN_Z:-0.85}"
DIFF_CMD_MAX_Z="${DIFF_CMD_MAX_Z:-1.35}"
DIFF_CMD_HOLD_RATE_HZ="${DIFF_CMD_HOLD_RATE_HZ:-100.0}"
DIFF_CMD_INPUT_TIMEOUT_S="${DIFF_CMD_INPUT_TIMEOUT_S:-0.30}"
DIFF_CMD_ADAPTER_ENABLE_TOPIC="${DIFF_CMD_ADAPTER_ENABLE_TOPIC:-/mosim/goal4/position_cmd_adapter_enable}"
DIFF_DISABLE_ADAPTER_BEFORE_LAND="${DIFF_DISABLE_ADAPTER_BEFORE_LAND:-true}"
DIFF_POST_ADAPTER_DISABLE_WAIT_S="${DIFF_POST_ADAPTER_DISABLE_WAIT_S:-0.8}"
LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS:-/opt/mosim_work/sunray_livox_plugin_ws}"
RUN_ID="${RUN_ID:-sunray_ros1_goal4_ego_single_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
GUI="${GUI:-false}"
OPEN_RVIZ="${OPEN_RVIZ:-false}"
GRID_RVIZ_CONFIG="${GRID_RVIZ_CONFIG:-${PROJECT_ROOT}/Config/rviz/sunray_ros1_ego_grid_trajectory_review.rviz}"
WORLD_FILE="${WORLD_FILE:-${SUNRAY_WS}/simulation/sunray_simulator/worlds/planning_test.world}"
USE_SIM_TIME="${USE_SIM_TIME:-true}"
SUNRAY_GAZEBO_MAX_STEP_SIZE_S="${SUNRAY_GAZEBO_MAX_STEP_SIZE_S:-0.001}"
SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ="${SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ:-1000}"
MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-60}"
ODOM_BRIDGE_READY_TIMEOUT_S="${ODOM_BRIDGE_READY_TIMEOUT_S:-20}"
MAVROS_STREAM_RATE_HZ="${MAVROS_STREAM_RATE_HZ:-100}"
TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-220}"
TARGET_X="${TARGET_X:-4.0}"
TARGET_Y="${TARGET_Y:-1.0}"
TARGET_Z="${TARGET_Z:-1.0}"
EGO_MAX_VEL="${EGO_MAX_VEL:-0.8}"
EGO_MAX_ACC="${EGO_MAX_ACC:-0.8}"
EGO_MAX_JERK="${EGO_MAX_JERK:-4.0}"
EGO_PLANNING_HORIZON="${EGO_PLANNING_HORIZON:-5.0}"
EGO_GRID_RESOLUTION="${EGO_GRID_RESOLUTION:-0.12}"
EGO_OBSTACLES_INFLATION="${EGO_OBSTACLES_INFLATION:-0.20}"
EGO_OPTIMIZATION_DIST0="${EGO_OPTIMIZATION_DIST0:-0.40}"
EGO_OBSTACLE_CLEARANCE="${EGO_OBSTACLE_CLEARANCE:-0.20}"
EGO_OBSTACLE_CLEARANCE_SOFT="${EGO_OBSTACLE_CLEARANCE_SOFT:-0.40}"
EGO_VIRTUAL_CEIL_HEIGHT="${EGO_VIRTUAL_CEIL_HEIGHT:-1.6}"
EGO_VIRTUAL_GROUND_HEIGHT="${EGO_VIRTUAL_GROUND_HEIGHT:-0.75}"
EGO_VISUALIZATION_TRUNCATE_HEIGHT="${EGO_VISUALIZATION_TRUNCATE_HEIGHT:-1.5}"
RAW_LIDAR_TOPIC="${RAW_LIDAR_TOPIC:-}"
RAW_LIDAR_TOPIC_CANDIDATES="${RAW_LIDAR_TOPIC_CANDIDATES:-/uav1/livox/lidar /livox/lidar /uav1/lidar /livox/lidar/points}"
WORLD_CLOUD_TOPIC="${WORLD_CLOUD_TOPIC:-/uav1/livox_world}"
OCCUPANCY_TOPIC="${OCCUPANCY_TOPIC:-/drone_0_ego_planner_node/grid_map/occupancy_inflate}"
POINTCLOUD_MOUNT_MODE="${POINTCLOUD_MOUNT_MODE:-sensor_to_body}"
POINTCLOUD_MOUNT_XYZ="${POINTCLOUD_MOUNT_XYZ:--0.000005 0.032295 0.050167}"
POINTCLOUD_MOUNT_RPY="${POINTCLOUD_MOUNT_RPY:-0 0 4.712389}"
POINTCLOUD_MIN_SENSOR_RANGE_M="${POINTCLOUD_MIN_SENSOR_RANGE_M:-0.25}"
POINTCLOUD_SELF_FILTER_RADIUS_M="${POINTCLOUD_SELF_FILTER_RADIUS_M:-0.35}"
POINTCLOUD_MIN_WORLD_Z_M="${POINTCLOUD_MIN_WORLD_Z_M:-0.08}"
POINTCLOUD_MAX_WORLD_Z_M="${POINTCLOUD_MAX_WORLD_Z_M:-2.20}"
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

case "${PLANNER_VARIANT}" in
  ego_v1|ego1|v1)
    PLANNER_VARIANT="ego_v1"
    PLANNER_WS="${GOAL4_EGO_WS}"
    PLANNER_LAUNCH="${PROJECT_ROOT}/Scripts/sunray/ego_single_px4ctrl_goal4.launch"
    PLANNER_TRAJ_TOPIC="/drone_0_planning/bspline"
    PLANNER_POLYTRAJ_TOPIC=""
    PLANNER_GOALSET_TOPIC=""
    PLANNER_GOAL_POSE_TOPIC=""
    PLANNER_NAME="Sunray EGO v1 planner/traj_server minimal overlay"
    ;;
  egov2|ego_v2|v2)
    PLANNER_VARIANT="egov2"
    PLANNER_WS="${GOAL4_EGOV2_WS}"
    PLANNER_LAUNCH="${PROJECT_ROOT}/Scripts/sunray/egov2_single_px4ctrl_goal4.launch"
    PLANNER_TRAJ_TOPIC="/drone_0_planning/bspline"
    PLANNER_POLYTRAJ_TOPIC="/drone_0_planning/trajectory"
    PLANNER_GOALSET_TOPIC="/goal_with_id"
    PLANNER_GOAL_POSE_TOPIC=""
    PLANNER_NAME="EGO-Planner-v2 planner/traj_server minimal overlay"
    ;;
  diff|diff_planner|diff-planner)
    PLANNER_VARIANT="diff_planner"
    PLANNER_WS="${GOAL4_DIFF_PLANNER_WS}"
    PLANNER_LAUNCH="${PROJECT_ROOT}/Scripts/sunray/diff_planner_single_px4ctrl_goal4.launch"
    PLANNER_TRAJ_TOPIC="/drone_0_planning/bspline"
    PLANNER_POLYTRAJ_TOPIC="/drone_0_planning/trajectory"
    PLANNER_GOALSET_TOPIC=""
    PLANNER_GOAL_POSE_TOPIC="/goal_with_id"
    if [[ "${DIFF_ENABLE_CMD_SAFETY_ADAPTER}" == "true" ]]; then
      PLANNER_POSITION_CMD_TOPIC="${DIFF_RAW_POSITION_CMD_TOPIC}"
    fi
    PLANNER_NAME="Diff-Planner planner/traj_server minimal overlay"
    ;;
  *)
    echo "Unsupported PLANNER_VARIANT=${PLANNER_VARIANT}; expected ego_v1, egov2, or diff_planner" >&2
    exit 2
    ;;
esac

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
  pkill -f "mosim_px4ctrl_ego_single_mission" >/dev/null 2>&1 || true
  pkill -f "mosim_goal4_pointcloud_to_world" >/dev/null 2>&1 || true
  pkill -f "mosim_goal4_position_cmd_safety_adapter" >/dev/null 2>&1 || true
  pkill -f "drone_0_ego_planner_node" >/dev/null 2>&1 || true
  pkill -f "drone_0_diff_planner_node" >/dev/null 2>&1 || true
  pkill -f "drone_0_traj_server" >/dev/null 2>&1 || true
  pkill -f "mosim_mavros_pose_velocity_to_odom_bridge" >/dev/null 2>&1 || true
  pkill -f "px4ctrl_node" >/dev/null 2>&1 || true
  pkill -f "roslaunch .*px4ctrl_mosim.launch" >/dev/null 2>&1 || true
  pkill -f "roslaunch .*ego_single_px4ctrl_goal4.launch" >/dev/null 2>&1 || true
  pkill -f "roslaunch .*egov2_single_px4ctrl_goal4.launch" >/dev/null 2>&1 || true
  pkill -f "roslaunch .*diff_planner_single_px4ctrl_goal4.launch" >/dev/null 2>&1 || true
  pkill -f "rviz.*sunray_ros1_ego_grid_trajectory_review" >/dev/null 2>&1 || true
  pkill -f "roslaunch .*sunray_sim_uav" >/dev/null 2>&1 || true
  pkill -f "roslaunch .*sunray_uav_control.*external_fusion" >/dev/null 2>&1 || true
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
  source "${PLANNER_WS}/devel/setup.bash"
  set -u

  local sunray_models="${SUNRAY_WS}/simulation/sunray_simulator/models"
  export CMAKE_PREFIX_PATH="${PLANNER_WS}/devel:${LIVOX_PLUGIN_WS}/devel:${PX4CTRL_WS}/devel:${SUNRAY_WS}/devel:/opt/ros/noetic:${CMAKE_PREFIX_PATH:-}"
  export ROS_PACKAGE_PATH="${PLANNER_WS}/src:${PX4CTRL_WS}/src:${SUNRAY_PX4_DIR}:${SUNRAY_WS}:/opt/ros/noetic/share:${ROS_PACKAGE_PATH:-}"
  export PYTHONPATH="${PLANNER_WS}/devel/lib/python3/dist-packages:${PX4CTRL_WS}/devel/lib/python3/dist-packages:${SUNRAY_WS}/devel/lib/python3/dist-packages:${PYTHONPATH:-}"
  export GAZEBO_MODEL_PATH="${sunray_models}/scence_models:${sunray_models}/drone_models:${sunray_models}/sensor_models:${sunray_models}/fake_models:${sunray_models}/ugv_models:${sunray_models}/aws_models:${sunray_models}/aws_vins_models:${GAZEBO_MODEL_PATH:-}"
  export GAZEBO_RESOURCE_PATH="${SUNRAY_WS}/simulation/sunray_simulator:${GAZEBO_RESOURCE_PATH:-}"
  export GAZEBO_PLUGIN_PATH="${LIVOX_PLUGIN_WS}/devel/lib:${SUNRAY_WS}/devel/lib:${GAZEBO_PLUGIN_PATH:-}"
  export LD_LIBRARY_PATH="${PLANNER_WS}/devel/lib:${LIVOX_PLUGIN_WS}/devel/lib:${PX4CTRL_WS}/devel/lib:${SUNRAY_WS}/devel/lib:/opt/ros/noetic/lib:${LD_LIBRARY_PATH:-}"
}

topic_file_name() {
  echo "$1" | sed 's#^/##; s#[^A-Za-z0-9_.-]#_#g'
}

sample_pointcloud_topic() {
  local topic="$1"
  local safe
  safe="$(topic_file_name "${topic}")"
  {
    echo "TOPIC ${topic}"
    echo "TYPE"
    timeout 5s rostopic type "${topic}" || true
    echo "INFO"
    timeout 5s rostopic info "${topic}" || true
    echo "SAMPLE"
    timeout 8s rostopic echo -n 1 --noarr "${topic}" || true
  } > "${RESULT_DIR}/topic_audit_${safe}.txt" 2>&1
}

discover_nonempty_pointcloud_topic() {
  local topic safe sample_file topic_type
  rostopic list | sort > "${RESULT_DIR}/topic_list_before_goal4_nodes.txt" 2>/dev/null || true
  grep -Ei "livox|cloud|point|scan|imu|mavros|gazebo" "${RESULT_DIR}/topic_list_before_goal4_nodes.txt" \
    > "${RESULT_DIR}/topic_list_before_goal4_nodes_filtered.txt" 2>/dev/null || true

  for topic in ${RAW_LIDAR_TOPIC:-} ${RAW_LIDAR_TOPIC_CANDIDATES}; do
    [[ -n "${topic}" ]] || continue
    sample_pointcloud_topic "${topic}"
    safe="$(topic_file_name "${topic}")"
    sample_file="${RESULT_DIR}/topic_audit_${safe}.txt"
    topic_type="$(timeout 5s rostopic type "${topic}" 2>/dev/null || true)"
    if [[ "${topic_type}" != "sensor_msgs/PointCloud2" ]]; then
      continue
    fi
    if grep -q "^width:" "${sample_file}" \
      && ! grep -q "^width: 0" "${sample_file}" \
      && ! grep -q "data: \\[\\]" "${sample_file}"; then
      echo "${topic}"
      return 0
    fi
  done
  return 1
}

if [[ ! -d "${PX4CTRL_WS}/devel" ]]; then
  echo "PX4CTRL_WS devel missing: ${PX4CTRL_WS}/devel" >&2
  exit 2
fi
if [[ ! -d "${PLANNER_WS}/devel" ]]; then
  echo "Planner workspace devel missing: ${PLANNER_WS}/devel; run the matching setup_goal4_ego*_overlay.sh" >&2
  exit 2
fi
if [[ ! -f "${LIVOX_PLUGIN_WS}/devel/lib/liblivox_laser_simulation.so" ]]; then
  LOG_PATH="${RESULT_DIR}/sunray_livox_plugin_build.log" \
    SUNRAY_WS="${SUNRAY_WS}" \
    LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS}" \
    bash "${PROJECT_ROOT}/Scripts/sunray/setup_sunray_livox_gazebo_plugin.sh" \
    > "${RESULT_DIR}/sunray_livox_plugin_setup_stdout.txt" 2>&1
fi

cleanup
sleep 3
source_env

{
  echo "ROS_ENV_SNAPSHOT"
  env | grep -E '^(ROS_PACKAGE_PATH|PYTHONPATH|CMAKE_PREFIX_PATH|LD_LIBRARY_PATH)=' || true
  rospack profile || true
  for pkg in px4ctrl quadrotor_msgs ego_planner traj_utils plan_env sunray_msgs; do
    echo "rospack find ${pkg}"
    rospack find "${pkg}"
  done
  python3 -c "import sunray_msgs.msg, quadrotor_msgs.msg, traj_utils.msg; print('python message imports ok')"
} > "${RESULT_DIR}/ros_env_snapshot.txt" 2>&1 || {
  echo "ROS environment missing required Goal4 packages; see ${RESULT_DIR}/ros_env_snapshot.txt" >&2
  exit 6
}

export SUNRAY_GAZEBO_MAX_STEP_SIZE_S
export SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ

python3 "${PROJECT_ROOT}/Scripts/sunray/sync_assembled_model_into_sunray_ros1.py" \
  --project-root "${PROJECT_ROOT}" \
  --sunray-ws "${SUNRAY_WS}" \
  --manifest "${RESULT_DIR}/assembled_model_sync.json" \
  > "${RESULT_DIR}/assembled_model_sync.log" 2>&1

rm -f /tmp/px4-sock-0 /tmp/px4-sock-1 2>/dev/null || true

roslaunch "${SUNRAY_WS}/simulation/sunray_simulator/launch_uav_demo/sunray_sim_uav_planning.launch" \
  gui:="${GUI}" rviz_enable:=false world:="${WORLD_FILE}" use_sim_time:="${USE_SIM_TIME}" \
  > "${RESULT_DIR}/sunray_gazebo.log" 2>&1 &
PIDS+=("$!")
echo "${PIDS[-1]}" > "${RESULT_DIR}/sunray_gazebo.pid"

if ! kill -0 "${PIDS[0]}" >/dev/null 2>&1; then
  echo "sunray gazebo launch exited before MAVROS ready" >&2
  exit 3
fi

if ! python3 "${PROJECT_ROOT}/Scripts/sunray/wait_for_mavros_state.py" \
  --topic /uav1/mavros/state \
  --timeout-s "${MAVROS_READY_TIMEOUT_S}" \
  --output "${RESULT_DIR}/mavros_state_first.txt"; then
  echo "MAVROS did not connect" >&2
  exit 4
fi

if [[ "${MAVROS_STREAM_RATE_HZ}" != "0" && "${MAVROS_STREAM_RATE_HZ}" != "0.0" ]]; then
  {
    echo "MAVROS_STREAM_RATE_HZ=${MAVROS_STREAM_RATE_HZ}"
    timeout 8s rosservice call /uav1/mavros/set_stream_rate "stream_id: 6
message_rate: ${MAVROS_STREAM_RATE_HZ}
on_off: true" || true
    timeout 8s rosservice call /uav1/mavros/cmd/command "broadcast: false
command: 511
confirmation: 0
param1: 32
param2: $((1000000 / MAVROS_STREAM_RATE_HZ))
param3: 0
param4: 0
param5: 0
param6: 0
param7: 0" || true
  } > "${RESULT_DIR}/mavros_stream_rate_request.txt" 2>&1
fi

if [[ "${PX4CTRL_START_EXTERNAL_FUSION}" == "true" ]]; then
  roslaunch sunray_uav_control external_fusion.launch \
    uav_id:=1 uav_name:=uav external_source:=2 position_topic:=/uav1/mavros/local_position/pose use_vision_pose:="${PX4CTRL_EXTERNAL_FUSION_USE_VISION_POSE}" \
    > "${RESULT_DIR}/external_fusion.log" 2>&1 &
  PIDS+=("$!")
  sleep 3
fi

python3 "${PROJECT_ROOT}/Scripts/sunray/mavros_pose_velocity_to_odom_bridge.py" \
  --pose-topic /uav1/mavros/local_position/pose \
  --velocity-topic /uav1/mavros/local_position/velocity_local \
  --output-topic /uav1/mavros/local_position/odom \
  --frame-id world \
  --child-frame-id uav1/base_link \
  > "${RESULT_DIR}/odom_bridge.log" 2>&1 &
PIDS+=("$!")

deadline=$((SECONDS + ODOM_BRIDGE_READY_TIMEOUT_S))
while (( SECONDS < deadline )); do
  if timeout 3s rostopic echo -n 1 /uav1/mavros/local_position/odom > "${RESULT_DIR}/odom_first.txt" 2>/dev/null; then
    break
  fi
  sleep 1
done

if [[ ! -s "${RESULT_DIR}/odom_first.txt" ]]; then
  echo "No odometry on /uav1/mavros/local_position/odom" >&2
  exit 5
fi

if ! DISCOVERED_RAW_LIDAR_TOPIC="$(discover_nonempty_pointcloud_topic)"; then
  echo "No nonempty raw MID360 PointCloud2 topic found; see ${RESULT_DIR}/topic_list_before_goal4_nodes*.txt and topic_audit_*.txt" >&2
  exit 7
fi
RAW_LIDAR_TOPIC="${DISCOVERED_RAW_LIDAR_TOPIC}"
echo "${RAW_LIDAR_TOPIC}" > "${RESULT_DIR}/raw_lidar_topic_selected.txt"

PX4CTRL_LAUNCH="${RESULT_DIR}/px4ctrl_mosim.launch"
PX4CTRL_CONFIG="$(rospack find px4ctrl)/config/ctrl_param_fpv.yaml"
cat > "${PX4CTRL_LAUNCH}" <<EOF
<launch>
  <node pkg="px4ctrl" type="px4ctrl_node" name="px4ctrl" output="screen">
    <remap from="~odom" to="/uav1/mavros/local_position/odom" />
    <remap from="~cmd" to="/position_cmd" />
    <remap from="/mavros/state" to="/uav1/mavros/state" />
    <remap from="/mavros/extended_state" to="/uav1/mavros/extended_state" />
    <remap from="/mavros/imu/data" to="/uav1/mavros/imu/data" />
    <remap from="/mavros/rc/in" to="/uav1/mavros/rc/in" />
    <remap from="/mavros/battery" to="/uav1/mavros/battery" />
    <remap from="/mavros/setpoint_raw/attitude" to="/uav1/mavros/setpoint_raw/attitude" />
    <remap from="/mavros/set_mode" to="/uav1/mavros/set_mode" />
    <remap from="/mavros/cmd/arming" to="/uav1/mavros/cmd/arming" />
    <remap from="/mavros/cmd/command" to="/uav1/mavros/cmd/command" />
    <rosparam command="load" file="${PX4CTRL_CONFIG}" />
    <param name="mass" value="${PX4CTRL_MASS}" />
    <param name="ctrl_freq_max" value="${PX4CTRL_CTRL_FREQ_MAX}" />
    <param name="use_bodyrate_ctrl" value="${PX4CTRL_USE_BODYRATE_CTRL}" />
    <param name="mosim_generated_core_mode" value="original" />
    <param name="auto_takeoff_land/enable" value="true" />
    <param name="auto_takeoff_land/enable_auto_arm" value="true" />
    <param name="auto_takeoff_land/no_RC" value="true" />
    <param name="auto_takeoff_land/takeoff_height" value="1.0" />
    <param name="auto_takeoff_land/takeoff_land_speed" value="0.12" />
    <param name="thrust_model/hover_percentage" value="${PX4CTRL_HOVER_PERCENTAGE}" />
    <param name="gain/Kp0" value="${PX4CTRL_KP_XY}" />
    <param name="gain/Kp1" value="${PX4CTRL_KP_XY}" />
    <param name="gain/Kp2" value="${PX4CTRL_KP_Z}" />
    <param name="gain/Kv0" value="${PX4CTRL_KV_XY}" />
    <param name="gain/Kv1" value="${PX4CTRL_KV_XY}" />
    <param name="gain/Kv2" value="${PX4CTRL_KV_Z}" />
  </node>
</launch>
EOF

roslaunch "${PX4CTRL_LAUNCH}" > "${RESULT_DIR}/px4ctrl.log" 2>&1 &
PIDS+=("$!")
sleep 5

python3 "${PROJECT_ROOT}/Scripts/sunray/goal4_pointcloud_to_world_node.py" \
  _input_point_topic:="${RAW_LIDAR_TOPIC}" \
  _output_point_topic:="${WORLD_CLOUD_TOPIC}" \
  _odom_topic:=/uav1/mavros/local_position/odom \
  _frame_id:=world \
  _mount_mode:="${POINTCLOUD_MOUNT_MODE}" \
  _mount_xyz:="${POINTCLOUD_MOUNT_XYZ}" \
  _mount_rpy:="${POINTCLOUD_MOUNT_RPY}" \
  _min_sensor_range_m:="${POINTCLOUD_MIN_SENSOR_RANGE_M}" \
  _self_filter_radius_m:="${POINTCLOUD_SELF_FILTER_RADIUS_M}" \
  _min_world_z_m:="${POINTCLOUD_MIN_WORLD_Z_M}" \
  _max_world_z_m:="${POINTCLOUD_MAX_WORLD_Z_M}" \
  _diagnostics_path:="${RESULT_DIR}/pointcloud_to_world_stats.json" \
  > "${RESULT_DIR}/pointcloud_to_world.log" 2>&1 &
PIDS+=("$!")
sleep 2

PLANNER_EXTRA_LAUNCH_ARGS=()
if [[ "${PLANNER_VARIANT}" == "diff_planner" ]]; then
  PLANNER_EXTRA_LAUNCH_ARGS+=(virtual_ground_height:="${EGO_VIRTUAL_GROUND_HEIGHT}")
fi

roslaunch "${PLANNER_LAUNCH}" \
  target_x:="${TARGET_X}" target_y:="${TARGET_Y}" target_z:="${TARGET_Z}" \
  max_vel:="${EGO_MAX_VEL}" max_acc:="${EGO_MAX_ACC}" max_jer:="${EGO_MAX_JERK}" planning_horizon:="${EGO_PLANNING_HORIZON}" \
  grid_resolution:="${EGO_GRID_RESOLUTION}" obstacles_inflation:="${EGO_OBSTACLES_INFLATION}" \
  optimization_dist0:="${EGO_OPTIMIZATION_DIST0}" obstacle_clearance:="${EGO_OBSTACLE_CLEARANCE}" obstacle_clearance_soft:="${EGO_OBSTACLE_CLEARANCE_SOFT}" \
  virtual_ceil_height:="${EGO_VIRTUAL_CEIL_HEIGHT}" visualization_truncate_height:="${EGO_VISUALIZATION_TRUNCATE_HEIGHT}" \
  odom_topic:=/uav1/mavros/local_position/odom global_pointcloud_topic:="${WORLD_CLOUD_TOPIC}" \
  position_cmd_topic:="${PLANNER_POSITION_CMD_TOPIC}" \
  "${PLANNER_EXTRA_LAUNCH_ARGS[@]}" \
  > "${RESULT_DIR}/ego_single_px4ctrl_goal4.log" 2>&1 &
PIDS+=("$!")
sleep 3

if [[ "${PLANNER_VARIANT}" == "diff_planner" && "${DIFF_ENABLE_CMD_SAFETY_ADAPTER}" == "true" ]]; then
  python3 "${PROJECT_ROOT}/Scripts/sunray/goal4_position_cmd_safety_adapter.py" \
    _input_topic:="${DIFF_RAW_POSITION_CMD_TOPIC}" \
    _output_topic:=/position_cmd \
    _enable_topic:="${DIFF_CMD_ADAPTER_ENABLE_TOPIC}" \
    _initial_enabled:=true \
    _rate_hz:="${DIFF_CMD_HOLD_RATE_HZ}" \
    _min_z:="${DIFF_CMD_MIN_Z}" \
    _max_z:="${DIFF_CMD_MAX_Z}" \
    _input_timeout_s:="${DIFF_CMD_INPUT_TIMEOUT_S}" \
    _diagnostics_path:="${RESULT_DIR}/position_cmd_safety_adapter.json" \
    > "${RESULT_DIR}/position_cmd_safety_adapter.log" 2>&1 &
  PIDS+=("$!")
  sleep 1
fi

if [[ "${OPEN_RVIZ}" == "true" ]]; then
  rviz -d "${GRID_RVIZ_CONFIG}" > "${RESULT_DIR}/rviz_ego_grid_trajectory.log" 2>&1 &
  PIDS+=("$!")
fi

MISSION_ADAPTER_ARGS=()
if [[ "${PLANNER_VARIANT}" == "diff_planner" && "${DIFF_ENABLE_CMD_SAFETY_ADAPTER}" == "true" && "${DIFF_DISABLE_ADAPTER_BEFORE_LAND}" == "true" ]]; then
  MISSION_ADAPTER_ARGS+=(--disable-cmd-adapter-before-land)
fi

set +e
timeout "${TOTAL_TIMEOUT_S}s" python3 "${PROJECT_ROOT}/Scripts/sunray/px4ctrl_ego_single_mission_node.py" \
  --result-dir "${RESULT_DIR}" \
  --target-x "${TARGET_X}" --target-y "${TARGET_Y}" --target-z "${TARGET_Z}" \
  --raw-lidar-topic "${RAW_LIDAR_TOPIC}" \
  --world-cloud-topic "${WORLD_CLOUD_TOPIC}" \
  --occupancy-topic "${OCCUPANCY_TOPIC}" \
  --bspline-topic "${PLANNER_TRAJ_TOPIC}" \
  --polytraj-topic "${PLANNER_POLYTRAJ_TOPIC}" \
  --goalset-topic "${PLANNER_GOALSET_TOPIC}" \
  --goal-pose-topic "${PLANNER_GOAL_POSE_TOPIC}" \
  --cmd-adapter-enable-topic "${DIFF_CMD_ADAPTER_ENABLE_TOPIC}" \
  --post-adapter-disable-wait-s "${DIFF_POST_ADAPTER_DISABLE_WAIT_S}" \
  "${MISSION_ADAPTER_ARGS[@]}" \
  > "${RESULT_DIR}/px4ctrl_ego_single_mission.log" 2>&1
MISSION_EXIT_CODE=$?
set -e

cat > "${RESULT_DIR}/RUN_MANIFEST.json" <<EOF
{
  "schema": "mosim.sunray_ros1.goal4_ego_single_manifest.v1",
  "result_dir": "${RESULT_DIR}",
  "controller": "original Fast-Drone-250 px4ctrl",
  "planner": "${PLANNER_NAME}",
  "planner_variant": "${PLANNER_VARIANT}",
  "goal4_ego_ws": "${PLANNER_WS}",
  "world_file": "${WORLD_FILE}",
  "use_sim_time": "${USE_SIM_TIME}",
  "target": {"x": ${TARGET_X}, "y": ${TARGET_Y}, "z": ${TARGET_Z}},
  "ego": {
    "max_vel": ${EGO_MAX_VEL},
    "max_acc": ${EGO_MAX_ACC},
    "max_jer": ${EGO_MAX_JERK},
    "planning_horizon": ${EGO_PLANNING_HORIZON},
    "grid_resolution": ${EGO_GRID_RESOLUTION},
    "obstacles_inflation": ${EGO_OBSTACLES_INFLATION},
    "optimization_dist0": ${EGO_OPTIMIZATION_DIST0},
    "obstacle_clearance": ${EGO_OBSTACLE_CLEARANCE},
    "obstacle_clearance_soft": ${EGO_OBSTACLE_CLEARANCE_SOFT},
    "virtual_ceil_height": ${EGO_VIRTUAL_CEIL_HEIGHT},
    "virtual_ground_height": ${EGO_VIRTUAL_GROUND_HEIGHT},
    "visualization_truncate_height": ${EGO_VISUALIZATION_TRUNCATE_HEIGHT}
  },
  "gazebo": {
    "max_step_size_s": ${SUNRAY_GAZEBO_MAX_STEP_SIZE_S},
    "real_time_update_rate_hz": ${SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ}
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
  "topics": {
    "raw_lidar": "${RAW_LIDAR_TOPIC}",
    "ego_cloud": "${WORLD_CLOUD_TOPIC}",
    "ego_bspline": "${PLANNER_TRAJ_TOPIC}",
    "ego_polytraj": "${PLANNER_POLYTRAJ_TOPIC}",
    "goalset": "${PLANNER_GOALSET_TOPIC}",
    "goal_pose": "${PLANNER_GOAL_POSE_TOPIC}",
    "position_cmd": "/position_cmd",
    "planner_position_cmd": "${PLANNER_POSITION_CMD_TOPIC}",
    "diff_raw_position_cmd": "${DIFF_RAW_POSITION_CMD_TOPIC}",
    "occupancy_inflate": "${OCCUPANCY_TOPIC}"
  },
  "position_cmd_safety_adapter": {
    "enabled": "${DIFF_ENABLE_CMD_SAFETY_ADAPTER}",
    "min_z": ${DIFF_CMD_MIN_Z},
    "max_z": ${DIFF_CMD_MAX_Z},
    "rate_hz": ${DIFF_CMD_HOLD_RATE_HZ},
    "input_timeout_s": ${DIFF_CMD_INPUT_TIMEOUT_S},
    "enable_topic": "${DIFF_CMD_ADAPTER_ENABLE_TOPIC}",
    "disable_before_land": "${DIFF_DISABLE_ADAPTER_BEFORE_LAND}",
    "post_disable_wait_s": ${DIFF_POST_ADAPTER_DISABLE_WAIT_S}
  },
  "pointcloud_to_world": {
    "mount_mode": "${POINTCLOUD_MOUNT_MODE}",
    "mount_xyz": "${POINTCLOUD_MOUNT_XYZ}",
    "mount_rpy": "${POINTCLOUD_MOUNT_RPY}",
    "min_sensor_range_m": ${POINTCLOUD_MIN_SENSOR_RANGE_M},
    "self_filter_radius_m": ${POINTCLOUD_SELF_FILTER_RADIUS_M},
    "min_world_z_m": ${POINTCLOUD_MIN_WORLD_Z_M},
    "max_world_z_m": ${POINTCLOUD_MAX_WORLD_Z_M}
  },
  "mission_exit_code": ${MISSION_EXIT_CODE},
  "claim_boundary": "Goal4 EGO single-UAV planner closed-loop through original px4ctrl/MAVROS/PX4/Gazebo; no Sunray native controller and no FAST-LIO state-source replacement."
}
EOF

echo "${RESULT_DIR}"
exit "${MISSION_EXIT_CODE}"
