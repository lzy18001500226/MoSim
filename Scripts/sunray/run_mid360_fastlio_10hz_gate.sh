#!/usr/bin/env bash
# Run the current Sunray ROS1 MID360 -> FAST-LIO localization/map gate.
#
# This gate is intentionally localization-only. It does not feed FAST-LIO
# odometry into PX4/MAVROS or any controller.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/opt/mosim_work/sunray_ws/Sunray}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-/opt/mosim_work/sunray_px4}"
FASTLIO_SRC="${FASTLIO_SRC:-${PROJECT_ROOT}/References/Lab/localization_slam/FAST_LIO}"
LIVOX_COMPAT_SRC="${LIVOX_COMPAT_SRC:-${PROJECT_ROOT}/References/Lab/localization_slam/livox_ros_driver_compat}"
FASTLIO_WS="${FASTLIO_WS:-/opt/mosim_work/sunray_ws/fastlio_ws}"
RUN_ID="${RUN_ID:-sunray_mid360_fastlio_10hz_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
GUI="${GUI:-false}"
OPEN_RVIZ="${OPEN_RVIZ:-true}"
KEEP_ALIVE="${KEEP_ALIVE:-true}"
USE_SIM_TIME="${USE_SIM_TIME:-true}"
WORLD_FILE="${WORLD_FILE:-${SUNRAY_WS}/simulation/sunray_simulator/worlds/planning_test.world}"
SENSOR_START_TIMEOUT_S="${SENSOR_START_TIMEOUT_S:-120}"
FASTLIO_START_TIMEOUT_S="${FASTLIO_START_TIMEOUT_S:-90}"
STATIC_INIT_HOLD_S="${STATIC_INIT_HOLD_S:-10}"
CONTINUITY_DURATION_S="${CONTINUITY_DURATION_S:-90}"
TIME_TF_AUDIT_DURATION_S="${TIME_TF_AUDIT_DURATION_S:-90}"
RVIZ_CONFIG="${RVIZ_CONFIG:-${PROJECT_ROOT}/Config/rviz/sunray_ros1_fastlio_accumulated_map_review.rviz}"
SCAN_RATE_HZ="${SCAN_RATE_HZ:-${FASTLIO_SCAN_RATE_HZ:-20.0}}"
FASTLIO_REVIEW_FILTER_MIN_Z="${FASTLIO_REVIEW_FILTER_MIN_Z:-0.05}"
FASTLIO_MODE="${FASTLIO_MODE:-livox_custom}"
FASTLIO_AXES_MARKER_TOPIC="${FASTLIO_AXES_MARKER_TOPIC:-/mosim/fastlio/uav_axes}"
FASTLIO_AXES_PATH_TOPIC="${FASTLIO_AXES_PATH_TOPIC:-/mosim/fastlio/uav_path}"
FASTLIO_AXES_CHILD_FRAME="${FASTLIO_AXES_CHILD_FRAME:-mosim_fastlio_uav_body}"
FASTLIO_AXES_INPUT_POSE_FRAME="${FASTLIO_AXES_INPUT_POSE_FRAME:-livox}"
FASTLIO_MOUNT_XYZ="${FASTLIO_MOUNT_XYZ:--0.000005 0.032295 0.050167}"
FASTLIO_MOUNT_RPY="${FASTLIO_MOUNT_RPY:-0 0 4.712389}"

mkdir -p "${RESULT_DIR}"

PIDS=()
DIAG_PIDS=()
cleanup() {
  set +e
  if [[ "${KEEP_ALIVE}" == "true" ]]; then
    return
  fi
  for pid in "${PIDS[@]:-}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
  sleep 1
  for pid in "${PIDS[@]:-}"; do
    kill -9 "${pid}" >/dev/null 2>&1 || true
  done
  pkill -f "mosim_pointcloud2_to_livox_custom_msg" >/dev/null 2>&1 || true
  pkill -f "fastlio_uav_axes_marker_node" >/dev/null 2>&1 || true
  pkill -f "laserMapping" >/dev/null 2>&1 || true
  pkill -f "mapping_mosim_sunray_livox_custom" >/dev/null 2>&1 || true
  pkill -f "rviz.*sunray_ros1_mid360_cloud_review" >/dev/null 2>&1 || true
  pkill -f "rviz.*sunray_ros1_fastlio_accumulated_map_review" >/dev/null 2>&1 || true
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
  export ROS_PACKAGE_PATH="${FASTLIO_WS}/src:${SUNRAY_WS}:${SUNRAY_PX4_DIR}:/opt/ros/noetic/share:${ROS_PACKAGE_PATH:-}"
  export GAZEBO_MODEL_PATH="${sunray_models}/scence_models:${sunray_models}/drone_models:${sunray_models}/sensor_models:${sunray_models}/fake_models:${sunray_models}/ugv_models:${sunray_models}/aws_models:${sunray_models}/aws_vins_models:${GAZEBO_MODEL_PATH:-}"
  export GAZEBO_RESOURCE_PATH="${SUNRAY_WS}/simulation/sunray_simulator:${GAZEBO_RESOURCE_PATH:-}"
  export GAZEBO_PLUGIN_PATH="${SUNRAY_WS}/devel/lib:${project_sunray_devel}/lib:${GAZEBO_PLUGIN_PATH:-}"
  export LD_LIBRARY_PATH="${FASTLIO_WS}/devel/lib:${SUNRAY_WS}/devel/lib:${project_sunray_devel}/lib:/opt/ros/noetic/lib:${LD_LIBRARY_PATH:-}"
}

pkill -f "mosim_pointcloud2_to_livox_custom_msg" >/dev/null 2>&1 || true
pkill -f "fastlio_uav_axes_marker_node" >/dev/null 2>&1 || true
pkill -f "laserMapping" >/dev/null 2>&1 || true
pkill -f "mapping_mosim_sunray_livox_custom" >/dev/null 2>&1 || true
pkill -f "rviz.*sunray_ros1_mid360_cloud_review" >/dev/null 2>&1 || true
pkill -f "rviz.*sunray_ros1_fastlio_accumulated_map_review" >/dev/null 2>&1 || true
pkill -f "roslaunch .*sunray_sim_uav" >/dev/null 2>&1 || true
pkill -f "gzserver" >/dev/null 2>&1 || true
pkill -f "gzclient" >/dev/null 2>&1 || true
pkill -f "mavros_node" >/dev/null 2>&1 || true
pkill -f "/opt/mosim_work/sunray_px4.*/px4" >/dev/null 2>&1 || true
pkill -f "rosmaster" >/dev/null 2>&1 || true
pkill -f "rosout" >/dev/null 2>&1 || true
sleep 2

source_env

if [[ ! -d "${FASTLIO_SRC}" || ! -d "${LIVOX_COMPAT_SRC}" ]]; then
  echo "Missing FAST-LIO or livox_ros_driver compatibility source." >&2
  exit 2
fi

mkdir -p "${FASTLIO_WS}/src"
ln -sfn "${FASTLIO_SRC}" "${FASTLIO_WS}/src/FAST_LIO"
ln -sfn "${LIVOX_COMPAT_SRC}" "${FASTLIO_WS}/src/livox_ros_driver_compat"

{
  echo "SUNRAY_WS=${SUNRAY_WS}"
  echo "FASTLIO_WS=${FASTLIO_WS}"
  echo "FASTLIO_SRC=${FASTLIO_SRC}"
  echo "LIVOX_COMPAT_SRC=${LIVOX_COMPAT_SRC}"
  cd "${FASTLIO_WS}"
  catkin_make --only-pkg-with-deps livox_ros_driver fast_lio
} > "${RESULT_DIR}/fastlio_build.log" 2>&1

source_env
rospack profile > "${RESULT_DIR}/rospack_profile.log" 2>&1 || true

{
  echo "rospack find livox_ros_driver"
  rospack find livox_ros_driver
  echo "rospack find fast_lio"
  rospack find fast_lio
  echo "rosmsg show livox_ros_driver/CustomMsg"
  rosmsg show livox_ros_driver/CustomMsg
} > "${RESULT_DIR}/fastlio_package_audit.txt" 2>&1

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

deadline=$((SECONDS + SENSOR_START_TIMEOUT_S))
while (( SECONDS < deadline )); do
  if timeout 5s rostopic echo -n 1 /uav1/livox/lidar > "${RESULT_DIR}/livox_lidar_first.txt" 2>&1 &&
     timeout 5s rostopic echo -n 1 /uav1/livox/imu > "${RESULT_DIR}/livox_imu_first.txt" 2>&1; then
    break
  fi
  sleep 2
done

if [[ ! -s "${RESULT_DIR}/livox_lidar_first.txt" || ! -s "${RESULT_DIR}/livox_imu_first.txt" ]]; then
  echo "MID360 LiDAR/IMU did not publish before timeout." >&2
  exit 3
fi

if [[ "${FASTLIO_MODE}" == "livox_custom" ]]; then
  python3 "${PROJECT_ROOT}/Scripts/sunray/pointcloud2_to_livox_custom_msg.py" \
    --input-topic /uav1/livox/lidar \
    --output-topic /mosim/fastlio/livox/lidar \
    --imu-topic /uav1/livox/imu \
    --stamp-source imu \
    --frame-id uav1/base_link \
    --scan-rate-hz "${SCAN_RATE_HZ}" \
    --scan-lines 4 \
    --stride 1 \
    --points-per-scan-hint 20000 \
    > "${RESULT_DIR}/pointcloud2_to_livox_custom_msg.log" 2>&1 &
  PIDS+=("$!")

  deadline=$((SECONDS + 30))
  while (( SECONDS < deadline )); do
    if timeout 5s rostopic echo -n 1 /mosim/fastlio/livox/lidar > "${RESULT_DIR}/fastlio_livox_custom_first.txt" 2>&1; then
      break
    fi
    sleep 1
  done

  if [[ ! -s "${RESULT_DIR}/fastlio_livox_custom_first.txt" ]]; then
    echo "FAST-LIO Livox CustomMsg bridge did not publish before timeout." >&2
    exit 4
  fi

  FASTLIO_LAUNCH="mapping_mosim_sunray_livox_custom.launch"
elif [[ "${FASTLIO_MODE}" == "pointcloud2" ]]; then
  FASTLIO_LAUNCH="mapping_mosim_sunray_pointcloud2.launch"
else
  echo "unsupported FASTLIO_MODE=${FASTLIO_MODE}" >&2
  exit 4
fi

roslaunch fast_lio "${FASTLIO_LAUNCH}" rviz:=false \
  > "${RESULT_DIR}/fastlio_mapping.log" 2>&1 &
PIDS+=("$!")

python3 "${PROJECT_ROOT}/Scripts/sunray/fastlio_uav_axes_marker_node.py" \
  --odom-topic /Odometry \
  --marker-topic "${FASTLIO_AXES_MARKER_TOPIC}" \
  --path-topic "${FASTLIO_AXES_PATH_TOPIC}" \
  --child-frame-id "${FASTLIO_AXES_CHILD_FRAME}" \
  --input-pose-frame "${FASTLIO_AXES_INPUT_POSE_FRAME}" \
  --mount-xyz "${FASTLIO_MOUNT_XYZ}" \
  --mount-rpy "${FASTLIO_MOUNT_RPY}" \
  > "${RESULT_DIR}/fastlio_uav_axes_marker_node.log" 2>&1 &
PIDS+=("$!")

python3 "${PROJECT_ROOT}/Scripts/ros/filter_pointcloud_by_z.py" \
  --input-topic /Laser_map \
  --output-topic /mosim/fastlio/laser_map_obstacles \
  --min-z "${FASTLIO_REVIEW_FILTER_MIN_Z}" \
  --output-json "${RESULT_DIR}/fastlio_laser_map_obstacle_filter.json" \
  > "${RESULT_DIR}/fastlio_laser_map_obstacle_filter.log" 2>&1 &
PIDS+=("$!")

{
  echo "STATIC_INIT_HOLD_S=${STATIC_INIT_HOLD_S}"
  echo "Holding vehicle static while FAST-LIO initializes."
  date --iso-8601=seconds
} > "${RESULT_DIR}/fastlio_static_init_hold.txt"
sleep "${STATIC_INIT_HOLD_S}"

deadline=$((SECONDS + FASTLIO_START_TIMEOUT_S))
while (( SECONDS < deadline )); do
  if timeout 5s rostopic echo -n 1 /cloud_registered > "${RESULT_DIR}/cloud_registered_first.txt" 2>&1 &&
     timeout 5s rostopic echo -n 1 /Odometry > "${RESULT_DIR}/Odometry_first.txt" 2>&1 &&
     timeout 5s rostopic echo -n 1 /path > "${RESULT_DIR}/path_first.txt" 2>&1; then
    break
  fi
  sleep 2
done

python3 "${PROJECT_ROOT}/Scripts/sunray/record_ros1_topic_continuity.py" \
  --duration-s "${CONTINUITY_DURATION_S}" \
  --out "${RESULT_DIR}/fastlio_topic_continuity.json" \
  > "${RESULT_DIR}/fastlio_topic_continuity_stdout.txt" 2>&1 &
PIDS+=("$!")
DIAG_PIDS+=("$!")

python3 "${PROJECT_ROOT}/Scripts/sunray/record_ros1_time_tf_audit.py" \
  --duration-s "${TIME_TF_AUDIT_DURATION_S}" \
  --out "${RESULT_DIR}/fastlio_time_tf_audit.json" \
  --log-glob "${RESULT_DIR}/*.log" \
  --log-glob "${RESULT_DIR}/*.txt" \
  > "${RESULT_DIR}/fastlio_time_tf_audit_stdout.txt" 2>&1 &
PIDS+=("$!")
DIAG_PIDS+=("$!")

python3 "${PROJECT_ROOT}/Scripts/sunray/record_fastlio_truth_alignment.py" \
  --out-dir "${RESULT_DIR}" \
  --duration-s "${CONTINUITY_DURATION_S}" \
  --fastlio-topic /Odometry \
  --truth-topic /uav1/sunray/gazebo_pose \
  --fastlio-pose-frame livox \
  --mount-xyz "${FASTLIO_MOUNT_XYZ}" \
  --mount-rpy "${FASTLIO_MOUNT_RPY}" \
  > "${RESULT_DIR}/fastlio_truth_alignment_stdout.txt" 2>&1 &
PIDS+=("$!")
DIAG_PIDS+=("$!")

(
  for topic in \
    /uav1/livox/lidar \
    /uav1/livox/imu \
    /mosim/fastlio/livox/lidar \
    /Laser_map \
    /cloud_registered \
    /Odometry \
    /path; do
    safe_name="$(echo "${topic}" | sed 's#^/##; s#/#_#g')"
    timeout 25s rostopic hz -w 80 "${topic}" \
      > "${RESULT_DIR}/${safe_name}_hz.txt" 2>&1 || true
  done
) &
PIDS+=("$!")
DIAG_PIDS+=("$!")

if [[ "${OPEN_RVIZ}" == "true" ]]; then
  rviz -d "${RVIZ_CONFIG}" > "${RESULT_DIR}/rviz_fastlio.log" 2>&1 &
  PIDS+=("$!")
fi

cat > "${RESULT_DIR}/RUN_MANIFEST.json" <<EOF
{
  "schema": "mosim.sunray_ros1.mid360_fastlio_gate_manifest.v2",
  "status": "review_running",
  "result_dir": "${RESULT_DIR}",
  "scope": "Sunray ROS1 MID360 raw PointCloud2 plus MID360 IMU bridged to local FAST-LIO; localization/map review only; no controller state-source switch",
  "sunray_ws": "${SUNRAY_WS}",
  "fastlio_ws": "${FASTLIO_WS}",
  "fastlio_source": "${FASTLIO_SRC}",
  "livox_ros_driver_compat_source": "${LIVOX_COMPAT_SRC}",
  "vehicle": "sunray150_with_mid360",
  "use_sim_time": "${USE_SIM_TIME}",
  "scan_rate_hz": ${SCAN_RATE_HZ},
  "fastlio_mode": "${FASTLIO_MODE}",
  "fastlio_launch": "${FASTLIO_LAUNCH}",
  "topics": {
    "raw_lidar": "/uav1/livox/lidar",
    "raw_mid360_imu": "/uav1/livox/imu",
    "fastlio_livox_custom": "/mosim/fastlio/livox/lidar",
    "fastlio_accumulated_map": "/Laser_map",
    "fastlio_cloud_registered": "/cloud_registered",
    "fastlio_odometry": "/Odometry",
    "fastlio_path": "/path"
  },
  "claim_boundary": "Does not claim FAST-LIO-backed control, EGO readiness, or final closed-loop performance; reported scan_rate_hz must be verified by topic-rate artifacts."
}
EOF

if [[ ! -s "${RESULT_DIR}/cloud_registered_first.txt" ||
      ! -s "${RESULT_DIR}/Odometry_first.txt" ||
      ! -s "${RESULT_DIR}/path_first.txt" ]]; then
  echo "FAST-LIO outputs were not all observed before timeout; see ${RESULT_DIR}/fastlio_mapping.log" >&2
  exit 5
fi

echo "${RESULT_DIR}"

if [[ "${KEEP_ALIVE}" == "true" ]]; then
  echo "KEEP_ALIVE=true; holding Gazebo/FAST-LIO/RViz for review." > "${RESULT_DIR}/keep_alive_status.txt"
  while true; do
    alive=0
    for pid in "${PIDS[@]:-}"; do
      if kill -0 "${pid}" >/dev/null 2>&1; then
        alive=1
      fi
    done
    if [[ "${alive}" -eq 0 ]]; then
      echo "all child processes exited" >> "${RESULT_DIR}/keep_alive_status.txt"
      exit 0
    fi
    sleep 5
  done
fi

for pid in "${DIAG_PIDS[@]:-}"; do
  wait "${pid}" >/dev/null 2>&1 || true
done
