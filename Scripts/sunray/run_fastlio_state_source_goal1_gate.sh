#!/usr/bin/env bash
# Goal 1 gate: FAST-LIO raw/aligned odom + Gazebo-Z surrogate + UAV axes.
# This script does not arm PX4, publish setpoints, or run a controller mission.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/opt/mosim_work/sunray_ws/Sunray}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-/opt/mosim_work/sunray_px4}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
FASTLIO_WS="${FASTLIO_WS:-/opt/mosim_work/sunray_ws/fastlio_ws}"
RUN_ID="${RUN_ID:-sunray_ros1_fastlio_goal1_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
GUI="${GUI:-false}"
WORLD_FILE="${WORLD_FILE:-${SUNRAY_WS}/simulation/sunray_simulator/worlds/planning_test.world}"
USE_SIM_TIME="${USE_SIM_TIME:-true}"
SUNRAY_UAV_INIT_X="${SUNRAY_UAV_INIT_X:-0.0}"
SUNRAY_UAV_INIT_Y="${SUNRAY_UAV_INIT_Y:-0.0}"
SUNRAY_UAV_INIT_Z="${SUNRAY_UAV_INIT_Z:-0.2}"
SUNRAY_UAV_INIT_YAW="${SUNRAY_UAV_INIT_YAW:-0.0}"
SUNRAY_GAZEBO_MAX_STEP_SIZE_S="${SUNRAY_GAZEBO_MAX_STEP_SIZE_S:-0.001}"
SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ="${SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ:-1000}"
MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-75}"
SENSOR_READY_TIMEOUT_S="${SENSOR_READY_TIMEOUT_S:-90}"
FASTLIO_READY_TIMEOUT_S="${FASTLIO_READY_TIMEOUT_S:-120}"
ALIGNMENT_READY_TIMEOUT_S="${ALIGNMENT_READY_TIMEOUT_S:-30}"
GOAL1_RECORD_DURATION_S="${GOAL1_RECORD_DURATION_S:-25}"
FASTLIO_MODE="${FASTLIO_MODE:-livox_custom}"
FASTLIO_ALIGNMENT_STAMP_SOURCE="${FASTLIO_ALIGNMENT_STAMP_SOURCE:-measurement}"
FASTLIO_MOUNT_XYZ="${FASTLIO_MOUNT_XYZ:--0.000005 0.032295 0.050167}"
FASTLIO_MOUNT_RPY="${FASTLIO_MOUNT_RPY:-0 0 4.712389}"

mkdir -p "${RESULT_DIR}"

PIDS=()
cleanup() {
  set +e
  for pid in "${PIDS[@]:-}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
  sleep 2
  for pid in "${PIDS[@]:-}"; do
    kill -9 "${pid}" >/dev/null 2>&1 || true
  done
  pkill -f "mosim_mavros_pose_velocity_to_odom_bridge" >/dev/null 2>&1 || true
  pkill -f "fastlio_odom_alignment_adapter" >/dev/null 2>&1 || true
  pkill -f "fastlio_uav_axes_marker_node" >/dev/null 2>&1 || true
  pkill -f "mosim_pointcloud2_to_livox_custom_msg" >/dev/null 2>&1 || true
  pkill -f "laserMapping" >/dev/null 2>&1 || true
  pkill -f "mapping_mosim_sunray_livox_custom" >/dev/null 2>&1 || true
  pkill -f "mapping_mosim_sunray_pointcloud2" >/dev/null 2>&1 || true
  pkill -f "roslaunch .*sunray_sim_uav" >/dev/null 2>&1 || true
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
  source /usr/share/gazebo/setup.sh
  source /opt/ros/noetic/setup.bash
  source "${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/setup_gazebo.bash" \
    "${SUNRAY_PX4_DIR}" \
    "${SUNRAY_PX4_DIR}/build/px4_sitl_default"
  source "${SUNRAY_WS}/devel/setup.bash"
  if [[ -f "${FASTLIO_WS}/devel/setup.bash" ]]; then
    source "${FASTLIO_WS}/devel/setup.bash"
  fi

  local sunray_models="${SUNRAY_WS}/simulation/sunray_simulator/models"
  local project_sunray_devel="${PROJECT_ROOT}/References/Sunray/devel"
  export CMAKE_PREFIX_PATH="${PX4CTRL_WS}/devel:${CMAKE_PREFIX_PATH:-}"
  export ROS_PACKAGE_PATH="${PX4CTRL_WS}/src:${SUNRAY_PX4_DIR}:${SUNRAY_WS}:/opt/ros/noetic/share:${ROS_PACKAGE_PATH:-}"
  export PYTHONPATH="${PX4CTRL_WS}/devel/lib/python3/dist-packages:${SUNRAY_WS}/devel/lib/python3/dist-packages:${project_sunray_devel}/lib/python3/dist-packages:${PYTHONPATH:-}"
  export GAZEBO_MODEL_PATH="${sunray_models}/scence_models:${sunray_models}/drone_models:${sunray_models}/sensor_models:${sunray_models}/fake_models:${sunray_models}/ugv_models:${sunray_models}/aws_models:${sunray_models}/aws_vins_models:${GAZEBO_MODEL_PATH:-}"
  export GAZEBO_RESOURCE_PATH="${SUNRAY_WS}/simulation/sunray_simulator:${GAZEBO_RESOURCE_PATH:-}"
  export GAZEBO_PLUGIN_PATH="${SUNRAY_WS}/devel/lib:${project_sunray_devel}/lib:${GAZEBO_PLUGIN_PATH:-}"
  export LD_LIBRARY_PATH="${PX4CTRL_WS}/devel/lib:${SUNRAY_WS}/devel/lib:${project_sunray_devel}/lib:/opt/ros/noetic/lib:${LD_LIBRARY_PATH:-}"
  export CMAKE_PREFIX_PATH="${FASTLIO_WS}/devel:${CMAKE_PREFIX_PATH:-}"
  export ROS_PACKAGE_PATH="${FASTLIO_WS}/src:${ROS_PACKAGE_PATH:-}"
  export PYTHONPATH="${FASTLIO_WS}/devel/lib/python3/dist-packages:${PYTHONPATH:-}"
  export LD_LIBRARY_PATH="${FASTLIO_WS}/devel/lib:${LD_LIBRARY_PATH:-}"
}

wait_topic() {
  local topic="$1"
  local timeout_s="$2"
  local out="$3"
  local deadline=$((SECONDS + timeout_s))
  while (( SECONDS < deadline )); do
    if timeout 4s rostopic echo -n 1 "${topic}" > "${out}" 2>&1; then
      return 0
    fi
    sleep 1
  done
  return 1
}

pkill -f "roslaunch .*sunray_sim_uav" >/dev/null 2>&1 || true
pkill -f "fastlio_odom_alignment_adapter" >/dev/null 2>&1 || true
pkill -f "fastlio_uav_axes_marker_node" >/dev/null 2>&1 || true
pkill -f "laserMapping" >/dev/null 2>&1 || true
pkill -f "mapping_mosim_sunray_pointcloud2" >/dev/null 2>&1 || true
pkill -f "gzserver" >/dev/null 2>&1 || true
pkill -f "gzclient" >/dev/null 2>&1 || true
pkill -f "mavros_node" >/dev/null 2>&1 || true
pkill -f "/opt/mosim_work/sunray_px4.*/px4" >/dev/null 2>&1 || true
pkill -f "rosmaster" >/dev/null 2>&1 || true
pkill -f "rosout" >/dev/null 2>&1 || true
sleep 3

source_env
{
  echo "GOAL1_FASTLIO_STATE_SOURCE_GATE"
  date --iso-8601=seconds
  echo "PROJECT_ROOT=${PROJECT_ROOT}"
  echo "SUNRAY_WS=${SUNRAY_WS}"
  echo "FASTLIO_WS=${FASTLIO_WS}"
  echo "USE_SIM_TIME=${USE_SIM_TIME}"
  echo "WORLD_FILE=${WORLD_FILE}"
  echo "FASTLIO_MODE=${FASTLIO_MODE}"
  echo "FASTLIO_ALIGNMENT_STAMP_SOURCE=${FASTLIO_ALIGNMENT_STAMP_SOURCE}"
  echo "No arming, no setpoint publication, no px4ctrl mission."
} > "${RESULT_DIR}/run_command_context.txt"

python3 "${PROJECT_ROOT}/Scripts/sunray/sync_assembled_model_into_sunray_ros1.py" \
  --project-root "${PROJECT_ROOT}" \
  --sunray-ws "${SUNRAY_WS}" \
  --manifest "${RESULT_DIR}/assembled_model_sync.json" \
  > "${RESULT_DIR}/assembled_model_sync.log" 2>&1

rm -f /tmp/px4-sock-0 /tmp/px4-sock-1 2>/dev/null || true

roslaunch "${SUNRAY_WS}/simulation/sunray_simulator/launch_uav_demo/sunray_sim_uav_planning.launch" \
  gui:="${GUI}" rviz_enable:=false world:="${WORLD_FILE}" use_sim_time:="${USE_SIM_TIME}" \
  uav_init_x:="${SUNRAY_UAV_INIT_X}" uav_init_y:="${SUNRAY_UAV_INIT_Y}" \
  uav_init_yaw:="${SUNRAY_UAV_INIT_YAW}" \
  > "${RESULT_DIR}/sunray_gazebo.log" 2>&1 &
PIDS+=("$!")

if ! timeout "${MAVROS_READY_TIMEOUT_S}s" python3 - <<'PY' > "${RESULT_DIR}/mavros_state_first.txt" 2>&1
import sys
import rospy
from mavros_msgs.msg import State

connected = None

def cb(msg):
    global connected
    if msg.connected:
        connected = msg
        rospy.signal_shutdown("connected")

rospy.init_node("mosim_goal1_wait_mavros_connected", anonymous=True)
rospy.Subscriber("/uav1/mavros/state", State, cb, queue_size=5)
rate = rospy.Rate(20)
while not rospy.is_shutdown() and connected is None:
    rate.sleep()
if connected is None:
    print("connected: False")
    sys.exit(1)
print(f"connected: {connected.connected}")
print(f"armed: {connected.armed}")
print(f"guided: {connected.guided}")
print(f"mode: {connected.mode}")
PY
then
  echo "MAVROS did not connect for Goal 1 state-source gate" >&2
  exit 4
fi

python3 "${PROJECT_ROOT}/Scripts/sunray/mavros_pose_velocity_to_odom_bridge.py" \
  --output-topic /uav1/mavros/local_position/odom \
  > "${RESULT_DIR}/mavros_pose_velocity_to_odom_bridge.log" 2>&1 &
PIDS+=("$!")

wait_topic /uav1/mavros/local_position/odom "${SENSOR_READY_TIMEOUT_S}" "${RESULT_DIR}/mavros_local_odom_first.txt" || {
  echo "No /uav1/mavros/local_position/odom sample" >&2
  exit 5
}
wait_topic /uav1/livox/lidar "${SENSOR_READY_TIMEOUT_S}" "${RESULT_DIR}/livox_lidar_first.txt" || {
  echo "No /uav1/livox/lidar sample" >&2
  exit 6
}
wait_topic /uav1/livox/imu "${SENSOR_READY_TIMEOUT_S}" "${RESULT_DIR}/livox_imu_first.txt" || {
  echo "No /uav1/livox/imu sample" >&2
  exit 7
}
wait_topic /uav1/sunray/gazebo_pose "${SENSOR_READY_TIMEOUT_S}" "${RESULT_DIR}/gazebo_pose_first.txt" || {
  echo "No /uav1/sunray/gazebo_pose sample" >&2
  exit 8
}

FASTLIO_LAUNCH="mapping_mosim_sunray_pointcloud2.launch"
if [[ "${FASTLIO_MODE}" == "livox_custom" ]]; then
  python3 "${PROJECT_ROOT}/Scripts/sunray/pointcloud2_to_livox_custom_msg.py" \
    --input-topic /uav1/livox/lidar \
    --output-topic /mosim/fastlio/livox/lidar \
    --imu-topic /uav1/livox/imu \
    --stamp-source imu \
    --frame-id uav1/base_link \
    --scan-rate-hz 10 \
    --scan-lines 4 \
    --stride 1 \
    --points-per-scan-hint 20000 \
    > "${RESULT_DIR}/pointcloud2_to_livox_custom_msg.log" 2>&1 &
  PIDS+=("$!")
  wait_topic /mosim/fastlio/livox/lidar 30 "${RESULT_DIR}/fastlio_livox_custom_first.txt" || {
    echo "No /mosim/fastlio/livox/lidar sample" >&2
    exit 9
  }
  FASTLIO_LAUNCH="mapping_mosim_sunray_livox_custom.launch"
elif [[ "${FASTLIO_MODE}" != "pointcloud2" ]]; then
  echo "unsupported FASTLIO_MODE=${FASTLIO_MODE}" >&2
  exit 9
fi

roslaunch fast_lio "${FASTLIO_LAUNCH}" rviz:=false \
  > "${RESULT_DIR}/fastlio_mapping.log" 2>&1 &
PIDS+=("$!")

wait_topic /Odometry "${FASTLIO_READY_TIMEOUT_S}" "${RESULT_DIR}/fastlio_raw_odom_first.txt" || {
  echo "No FAST-LIO /Odometry sample" >&2
  exit 9
}

python3 "${PROJECT_ROOT}/Scripts/sunray/fastlio_odom_alignment_adapter.py" \
  --fastlio-topic /Odometry \
  --local-topic /uav1/mavros/local_position/odom \
  --output-topic /mosim/fastlio/odom_aligned \
  --path-topic /mosim/fastlio/odom_aligned_path \
  --z-source truth_delta \
  --truth-topic /uav1/sunray/gazebo_pose \
  --output-frame world \
  --child-frame base_link \
  --stamp-source "${FASTLIO_ALIGNMENT_STAMP_SOURCE}" \
  --input-pose-frame livox \
  --mount-xyz "${FASTLIO_MOUNT_XYZ}" \
  --mount-rpy "${FASTLIO_MOUNT_RPY}" \
  > "${RESULT_DIR}/fastlio_odom_alignment_adapter.log" 2>&1 &
PIDS+=("$!")

python3 "${PROJECT_ROOT}/Scripts/sunray/fastlio_uav_axes_marker_node.py" \
  --odom-topic /Odometry \
  --marker-topic /mosim/fastlio/uav_axes \
  --path-topic /mosim/fastlio/uav_path \
  --child-frame-id mosim_fastlio_uav_body \
  --input-pose-frame livox \
  --mount-xyz "${FASTLIO_MOUNT_XYZ}" \
  --mount-rpy "${FASTLIO_MOUNT_RPY}" \
  > "${RESULT_DIR}/fastlio_uav_axes_marker_node.log" 2>&1 &
PIDS+=("$!")

wait_topic /mosim/fastlio/odom_aligned "${ALIGNMENT_READY_TIMEOUT_S}" "${RESULT_DIR}/fastlio_aligned_odom_first.txt" || {
  echo "No /mosim/fastlio/odom_aligned sample" >&2
  exit 10
}
wait_topic /mosim/fastlio/uav_axes "${ALIGNMENT_READY_TIMEOUT_S}" "${RESULT_DIR}/fastlio_uav_axes_first.txt" || {
  echo "No /mosim/fastlio/uav_axes sample" >&2
  exit 11
}

set +e
python3 "${PROJECT_ROOT}/Scripts/sunray/record_fastlio_state_source_goal1.py" \
  --duration-s "${GOAL1_RECORD_DURATION_S}" \
  --out "${RESULT_DIR}/GOAL1_FASTLIO_STATE_SOURCE_GATE.json" \
  --mount-xyz "${FASTLIO_MOUNT_XYZ}" \
  --mount-rpy "${FASTLIO_MOUNT_RPY}" \
  > "${RESULT_DIR}/goal1_recorder_stdout.json" 2>&1
RECORDER_EXIT=$?
set -e

(
  for topic in \
    /uav1/livox/lidar \
    /uav1/livox/imu \
    /uav1/mavros/local_position/odom \
    /uav1/sunray/gazebo_pose \
    /Odometry \
    /Laser_map \
    /mosim/fastlio/odom_aligned \
    /mosim/fastlio/odom_aligned_delay \
    /mosim/fastlio/uav_axes; do
    safe_name="$(echo "${topic}" | sed 's#^/##; s#/#_#g')"
    timeout 10s rostopic hz -w 50 "${topic}" > "${RESULT_DIR}/${safe_name}_hz.txt" 2>&1 || true
  done
) &
PIDS+=("$!")
wait "${PIDS[-1]}" || true

cat > "${RESULT_DIR}/RUN_MANIFEST.json" <<EOF
{
  "schema": "mosim.sunray_ros1.fastlio_goal1_gate_manifest.v1",
  "result_dir": "${RESULT_DIR}",
  "claim_boundary": "FAST-LIO raw/aligned odometry, Gazebo rangefinder surrogate Z, and UAV base axes only; no arming, no setpoint publication, no controller mission.",
  "controller_state_source": "/uav1/mavros/local_position/odom",
  "fastlio_mode": "${FASTLIO_MODE}",
  "fastlio_launch": "${FASTLIO_LAUNCH}",
  "fastlio_livox_custom_topic": "/mosim/fastlio/livox/lidar",
  "fastlio_raw_odom": "/Odometry",
  "fastlio_aligned_odom_candidate": "/mosim/fastlio/odom_aligned",
  "fastlio_aligned_delay_topic": "/mosim/fastlio/odom_aligned_delay",
  "fastlio_alignment_stamp_source": "${FASTLIO_ALIGNMENT_STAMP_SOURCE}",
  "z_source_first_version": "gazebo_rangefinder_surrogate",
  "gazebo_truth_control_input_allowed": false,
  "setpoint_publication_allowed": false,
  "use_sim_time": "${USE_SIM_TIME}",
  "fastlio_mount_xyz_m": "${FASTLIO_MOUNT_XYZ}",
  "fastlio_mount_rpy_rad": "${FASTLIO_MOUNT_RPY}",
  "recorder_exit_code": ${RECORDER_EXIT}
}
EOF

echo "${RESULT_DIR}"
exit "${RECORDER_EXIT}"
