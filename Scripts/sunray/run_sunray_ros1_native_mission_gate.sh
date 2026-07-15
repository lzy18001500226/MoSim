#!/usr/bin/env bash
# Run a ROS1/Sunray native-control mission against the assembled Sunray150+MID360 model.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/opt/mosim_work/sunray_ws/Sunray}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-/opt/mosim_work/sunray_px4}"
FASTLIO="${FASTLIO:-false}"
FASTLIO_WS="${FASTLIO_WS:-/tmp/mosim_sunray_build_20260620_fastlio_3/Sunray}"
FASTLIO_MODE="${FASTLIO_MODE:-pointcloud2}"
FASTLIO_SCAN_RATE_HZ="${FASTLIO_SCAN_RATE_HZ:-20.0}"
EXTERNAL_FUSION_SOURCE="${EXTERNAL_FUSION_SOURCE:-2}"
EXTERNAL_FUSION_POSITION_TOPIC="${EXTERNAL_FUSION_POSITION_TOPIC:-/uav1/mavros/local_position/pose}"
EXTERNAL_FUSION_USE_VISION_POSE="${EXTERNAL_FUSION_USE_VISION_POSE:-true}"
MISSION="${MISSION:-takeoff_hover_land}"
RUN_ID="${RUN_ID:-sunray_ros1_${MISSION}_native_gate_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
GUI="${GUI:-false}"
RVIZ="${RVIZ:-false}"
WORLD_FILE="${WORLD_FILE:-${SUNRAY_WS}/simulation/sunray_simulator/worlds/planning_test.world}"
TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-130}"
CLEAN_START="${CLEAN_START:-true}"
WAIT_NONEMPTY_LIDAR="${WAIT_NONEMPTY_LIDAR:-true}"
REQUIRE_NONEMPTY_LIDAR="${REQUIRE_NONEMPTY_LIDAR:-true}"
LIDAR_READY_TIMEOUT_S="${LIDAR_READY_TIMEOUT_S:-260}"
TOPIC_CONTINUITY_DURATION_S="${TOPIC_CONTINUITY_DURATION_S:-0}"
TIME_TF_AUDIT_DURATION_S="${TIME_TF_AUDIT_DURATION_S:-0}"
USE_SIM_TIME="${USE_SIM_TIME:-true}"
CONTROL_DIAGNOSTICS_DURATION_S="${CONTROL_DIAGNOSTICS_DURATION_S:-90}"
FREQUENCY_AUDIT_DURATION_S="${FREQUENCY_AUDIT_DURATION_S:-12}"
MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-50}"
MAVROS_STREAM_RATE_HZ="${MAVROS_STREAM_RATE_HZ:-0}"
MAVROS_SET_MESSAGE_INTERVALS="${MAVROS_SET_MESSAGE_INTERVALS:-true}"
MAVROS_PATCH_RATE_LIMITS="${MAVROS_PATCH_RATE_LIMITS:-false}"
PX4_PATCH_MAVLINK_STREAMS="${PX4_PATCH_MAVLINK_STREAMS:-true}"
PX4_MAVLINK_STREAM_NAMES="${PX4_MAVLINK_STREAM_NAMES:-HIGHRES_IMU ATTITUDE ATTITUDE_QUATERNION LOCAL_POSITION_NED}"
MAVROS_SET_STREAM_GROUPS="${MAVROS_SET_STREAM_GROUPS:-raw_sensors position extra1 extra2}"
MAVROS_SET_MESSAGE_IDS="${MAVROS_SET_MESSAGE_IDS:-105:HIGHRES_IMU 30:ATTITUDE 32:LOCAL_POSITION_NED}"

mkdir -p "${RESULT_DIR}"

PIDS=()
cleanup() {
  set +e
  if [[ "${KEEP_ALIVE:-false}" == "true" ]]; then
    return
  fi
  for pid in "${PIDS[@]:-}"; do
    if kill -0 "${pid}" >/dev/null 2>&1; then
      kill "${pid}" >/dev/null 2>&1 || true
    fi
  done
  sleep 2
  for pid in "${PIDS[@]:-}"; do
    if kill -0 "${pid}" >/dev/null 2>&1; then
      kill -9 "${pid}" >/dev/null 2>&1 || true
    fi
  done
  pkill -f "roslaunch .*sunray_sim_uav_planning.launch" >/dev/null 2>&1 || true
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

  local sunray_models="${SUNRAY_WS}/simulation/sunray_simulator/models"
  export ROS_PACKAGE_PATH="${SUNRAY_PX4_DIR}:${SUNRAY_WS}:/opt/ros/noetic/share:${ROS_PACKAGE_PATH:-}"
  export GAZEBO_MODEL_PATH="${sunray_models}/scence_models:${sunray_models}/drone_models:${sunray_models}/sensor_models:${sunray_models}/fake_models:${sunray_models}/ugv_models:${sunray_models}/aws_models:${sunray_models}/aws_vins_models:${GAZEBO_MODEL_PATH:-}"
  export GAZEBO_RESOURCE_PATH="${SUNRAY_WS}/simulation/sunray_simulator:${GAZEBO_RESOURCE_PATH:-}"
  export GAZEBO_PLUGIN_PATH="${SUNRAY_WS}/devel/lib:${SUNRAY_WS}/devel/lib:${GAZEBO_PLUGIN_PATH:-}"
  export LD_LIBRARY_PATH="${SUNRAY_WS}/devel/lib:${LD_LIBRARY_PATH:-}"
}

if [[ ! -d "${SUNRAY_WS}" ]]; then
  echo "SUNRAY_WS missing: ${SUNRAY_WS}" >&2
  exit 2
fi
if [[ ! -d "${SUNRAY_PX4_DIR}" ]]; then
  echo "SUNRAY_PX4_DIR missing: ${SUNRAY_PX4_DIR}" >&2
  exit 2
fi

if [[ "${CLEAN_START}" == "true" ]]; then
  pkill -f "roslaunch .*sunray_sim_uav" >/dev/null 2>&1 || true
  pkill -f "roslaunch .*sunray_uav_control" >/dev/null 2>&1 || true
  pkill -f "roslaunch .*sunray_tutorial" >/dev/null 2>&1 || true
  pkill -f "roslaunch .*mapping_mosim_sunray_pointcloud2.launch" >/dev/null 2>&1 || true
  pkill -f "fast_lio.*/fastlio_mapping" >/dev/null 2>&1 || true
  pkill -f "pointcloud2_to_livox_custom_msg.py" >/dev/null 2>&1 || true
  pkill -f "mosim_sunray_ros1_native_mission_node" >/dev/null 2>&1 || true
  pkill -f "rviz -d .*sunray_ros1_" >/dev/null 2>&1 || true
  pkill -f "gzserver" >/dev/null 2>&1 || true
  pkill -f "gzclient" >/dev/null 2>&1 || true
  pkill -f "mavros_node" >/dev/null 2>&1 || true
  pkill -f "/opt/mosim_work/sunray_px4.*/px4" >/dev/null 2>&1 || true
  pkill -f "rosmaster" >/dev/null 2>&1 || true
  pkill -f "rosout" >/dev/null 2>&1 || true
  sleep 3
fi

source_env

patch_mavros_rate_limits() {
  local rate_hz="$1"
  if [[ "${MAVROS_PATCH_RATE_LIMITS}" != "true" || "${rate_hz}" == "0" || "${rate_hz}" == "0.0" ]]; then
    return
  fi
  local config_path="${SUNRAY_WS}/simulation/sunray_simulator/config/px4_config.yaml"
  local backup_path="${config_path}.bak_mosim_mavros_rate_$(date +%Y%m%d_%H%M%S)"
  cp "${config_path}" "${backup_path}"
  python3 - "${config_path}" "${rate_hz}" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
rate = float(sys.argv[2])
text = path.read_text(encoding="utf-8")

# MAVROS px4_config rate_limit entries cap several high-rate plugin outputs.
# Keep the patch intentionally narrow and auditable for this frequency gate.
text = re.sub(r"rate_limit:\s*(50\.0|10\.0)", f"rate_limit: {rate:.1f}", text)
path.write_text(text, encoding="utf-8")
PY
  cp "${config_path}" "${RESULT_DIR}/px4_config_rate_patched.yaml"
  {
    echo "MAVROS_PATCH_RATE_LIMITS=true"
    echo "rate_hz=${rate_hz}"
    echo "config_path=${config_path}"
    echo "backup_path=${backup_path}"
    grep -n "rate_limit" "${config_path}" || true
  } > "${RESULT_DIR}/mavros_rate_limit_patch.txt"
}

prepare_px4_mavlink_stream_override() {
  local rate_hz="$1"
  if [[ "${PX4_PATCH_MAVLINK_STREAMS}" != "true" || "${rate_hz}" == "0" || "${rate_hz}" == "0.0" ]]; then
    return
  fi
  local original="${SUNRAY_PX4_DIR}/build/px4_sitl_default/etc/init.d-posix/px4-rc.mavlink"
  local override_dir="${RESULT_DIR}/px4_mavlink_path_override"
  local override="${override_dir}/px4-rc.mavlink"
  mkdir -p "${override_dir}"
  cp "${original}" "${override}"
  {
    cat <<EOF

# MoSim frequency experiment override for the MAVROS/API offboard link.
# PX4 rcS sources px4-rc.mavlink through PATH, so the launcher prepends this
# result-directory copy without mutating the PX4 installation.
if [ "\${udp_offboard_port_local}" != "" ]; then
EOF
    for stream_name in ${PX4_MAVLINK_STREAM_NAMES}; do
      printf '\tmavlink stream -r %s -s %s -u ${udp_offboard_port_local}\n' "${rate_hz}" "${stream_name}"
    done
    cat <<'EOF'
fi
EOF
  } >> "${override}"
  export PATH="${override_dir}:${PATH}"
  {
    echo "PX4_PATCH_MAVLINK_STREAMS=true"
    echo "rate_hz=${rate_hz}"
    echo "PX4_MAVLINK_STREAM_NAMES=${PX4_MAVLINK_STREAM_NAMES}"
    echo "original=${original}"
    echo "override=${override}"
    echo "PATH_HEAD=${override_dir}"
    tail -n $((8 + $(echo "${PX4_MAVLINK_STREAM_NAMES}" | wc -w))) "${override}"
  } > "${RESULT_DIR}/px4_mavlink_stream_override.txt"
}

patch_mavros_rate_limits "${MAVROS_STREAM_RATE_HZ}"
prepare_px4_mavlink_stream_override "${MAVROS_STREAM_RATE_HZ}"

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

deadline=$((SECONDS + MAVROS_READY_TIMEOUT_S))
while (( SECONDS < deadline )); do
  if ! kill -0 "${PIDS[0]}" >/dev/null 2>&1; then
    echo "sunray gazebo launch exited before MAVROS ready" >&2
    exit 3
  fi
  if timeout 3s rostopic echo -n 1 /uav1/mavros/state > "${RESULT_DIR}/mavros_state_first.txt" 2>/dev/null; then
    if grep -q "connected: True" "${RESULT_DIR}/mavros_state_first.txt"; then
      break
    fi
  fi
  sleep 1
done

if ! grep -q "connected: True" "${RESULT_DIR}/mavros_state_first.txt" 2>/dev/null; then
  echo "MAVROS did not connect" >&2
  exit 4
fi

configure_mavros_stream_rates() {
  local rate_hz="$1"
  if [[ "${rate_hz}" == "0" || "${rate_hz}" == "0.0" ]]; then
    return
  fi
  {
    echo "MAVROS_STREAM_RATE_HZ=${rate_hz}"
    echo "MAVROS_SET_STREAM_GROUPS=${MAVROS_SET_STREAM_GROUPS}"
    for group in ${MAVROS_SET_STREAM_GROUPS}; do
      case "${group}" in
        raw_sensors) stream_id=1 ;;
        position) stream_id=6 ;;
        extra1) stream_id=10 ;;
        extra2) stream_id=11 ;;
        *) echo "skip_unknown_stream_group ${group}"; continue ;;
      esac
      echo "set_stream_rate ${group}"
      timeout 8s rosservice call /uav1/mavros/set_stream_rate \
        "stream_id: ${stream_id}
message_rate: ${rate_hz}
on_off: true" || true
    done
    if [[ "${MAVROS_SET_MESSAGE_INTERVALS}" == "true" ]]; then
      local interval_us
      interval_us="$(python3 - <<PY
rate = float("${rate_hz}")
print(int(round(1000000.0 / rate)))
PY
)"
      echo "MAVROS_SET_MESSAGE_IDS=${MAVROS_SET_MESSAGE_IDS}"
      for spec in ${MAVROS_SET_MESSAGE_IDS}; do
        local msg_id msg_name
        msg_id="${spec%%:*}"
        msg_name="${spec#*:}"
        echo "set_message_interval ${msg_name}(${msg_id}) ${interval_us}us"
        timeout 8s rosservice call /uav1/mavros/cmd/command \
          "broadcast: false
command: 511
confirmation: 0
param1: ${msg_id}
param2: ${interval_us}
param3: 0
param4: 0
param5: 0
param6: 0
param7: 0" || true
      done
    fi
  } > "${RESULT_DIR}/mavros_stream_rate_request.txt" 2>&1
}

configure_mavros_stream_rates "${MAVROS_STREAM_RATE_HZ}"

roslaunch sunray_uav_control external_fusion.launch \
  uav_id:=1 uav_name:=uav external_source:="${EXTERNAL_FUSION_SOURCE}" position_topic:="${EXTERNAL_FUSION_POSITION_TOPIC}" use_vision_pose:="${EXTERNAL_FUSION_USE_VISION_POSE}" \
  > "${RESULT_DIR}/external_fusion.log" 2>&1 &
PIDS+=("$!")
sleep 2

roslaunch sunray_uav_control sunray_control_node.launch \
  uav_id:=1 uav_name:=uav \
  Takeoff_height:="${SUNRAY_TAKEOFF_HEIGHT:-1.0}" \
  Land_speed:="${SUNRAY_LAND_SPEED:-0.25}" \
  control_loop_hz:="${SUNRAY_CTRL_CONTROL_LOOP_HZ:-200.0}" \
  quad_mass:="${SUNRAY_CTRL_QUAD_MASS:-1.0}" \
  hov_percent:="${SUNRAY_CTRL_HOV_PERCENT:-0.37}" \
  thrust_norm_compensation:="${SUNRAY_CTRL_THRUST_NORM_COMPENSATION:-false}" \
  pxy_int_max:="${SUNRAY_CTRL_PXY_INT_MAX:-10.0}" \
  pz_int_max:="${SUNRAY_CTRL_PZ_INT_MAX:-10.0}" \
  Kp_xy:="${SUNRAY_CTRL_KP_XY:-3.0}" \
  Kp_z:="${SUNRAY_CTRL_KP_Z:-3.0}" \
  Kv_xy:="${SUNRAY_CTRL_KV_XY:-3.0}" \
  Kv_z:="${SUNRAY_CTRL_KV_Z:-3.0}" \
  Kvi_xy:="${SUNRAY_CTRL_KVI_XY:-0.3}" \
  Kvi_z:="${SUNRAY_CTRL_KVI_Z:-0.3}" \
  tilt_angle_max:="${SUNRAY_CTRL_TILT_ANGLE_MAX:-20.0}" \
  > "${RESULT_DIR}/sunray_control_node.log" 2>&1 &
PIDS+=("$!")
sleep 5

if [[ "${WAIT_NONEMPTY_LIDAR}" == "true" ]]; then
  deadline=$((SECONDS + LIDAR_READY_TIMEOUT_S))
  lidar_ready=false
  while (( SECONDS < deadline )); do
    if timeout 8s rostopic echo -n 1 /uav1/livox/lidar > "${RESULT_DIR}/livox_lidar_ready_sample.txt" 2>/dev/null; then
      if grep -q "width:" "${RESULT_DIR}/livox_lidar_ready_sample.txt" \
        && ! grep -q "width: 0" "${RESULT_DIR}/livox_lidar_ready_sample.txt" \
        && ! grep -q "data: \\[\\]" "${RESULT_DIR}/livox_lidar_ready_sample.txt"; then
        lidar_ready=true
        break
      fi
    fi
    sleep 5
  done
  if [[ "${lidar_ready}" != "true" ]]; then
    echo "MID360 lidar did not publish a nonempty PointCloud2 before mission start" >&2
    exit 5
  fi
fi

if [[ "${RVIZ}" == "true" ]]; then
  rviz -d "${PROJECT_ROOT}/Config/rviz/sunray_ros1_trajectory_review.rviz" \
    > "${RESULT_DIR}/rviz_trajectory.log" 2>&1 &
  PIDS+=("$!")
  rviz -d "${PROJECT_ROOT}/Config/rviz/sunray_ros1_mid360_cloud_review.rviz" \
    > "${RESULT_DIR}/rviz_mid360.log" 2>&1 &
  PIDS+=("$!")
fi

if [[ "${FASTLIO}" == "true" ]]; then
  if [[ ! -d "${FASTLIO_WS}/devel" ]]; then
    echo "FASTLIO_WS devel missing: ${FASTLIO_WS}/devel" >&2
    exit 6
  fi
  if [[ "${FASTLIO_MODE}" == "livox_custom" ]]; then
    source "${FASTLIO_WS}/devel/setup.bash"
    python3 "${PROJECT_ROOT}/Scripts/sunray/pointcloud2_to_livox_custom_msg.py" \
      --input-topic /uav1/livox/lidar \
      --output-topic /mosim/fastlio/livox/lidar \
      --imu-topic /uav1/livox/imu \
      --stamp-source imu \
      --frame-id uav1/base_link \
      --scan-rate-hz "${FASTLIO_SCAN_RATE_HZ}" \
      --scan-lines 4 \
      --blind 0.4 \
      > "${RESULT_DIR}/pointcloud2_to_livox_custom.log" 2>&1 &
    PIDS+=("$!")
    sleep 2
  fi
  source "${FASTLIO_WS}/devel/setup.bash"
  if [[ "${FASTLIO_MODE}" == "livox_custom" ]]; then
    FASTLIO_LAUNCH="mapping_mosim_sunray_livox_custom.launch"
  else
    FASTLIO_LAUNCH="mapping_mosim_sunray_pointcloud2.launch"
  fi
  roslaunch fast_lio "${FASTLIO_LAUNCH}" rviz:=false \
    > "${RESULT_DIR}/fastlio_mapping.log" 2>&1 &
  PIDS+=("$!")
  sleep 5
  source "${SUNRAY_WS}/devel/setup.bash"
  (
    sleep "${FASTLIO_RECORD_DELAY_S:-8}"
    {
      echo "TOPICS"
      rostopic list 2>/dev/null | grep -E "cloud_registered|Odometry|/path|livox|imu" || true
      echo "TYPES"
      for topic in /cloud_registered /cloud_registered_body /Odometry /path /mosim/fastlio/livox/lidar /uav1/livox/lidar /uav1/livox/imu; do
        printf "%s " "${topic}"
        timeout 5s rostopic type "${topic}" || true
      done
    } > "${RESULT_DIR}/fastlio_topic_summary_live.txt" 2>&1
    timeout 12s rostopic echo -n 1 /cloud_registered > "${RESULT_DIR}/fastlio_cloud_registered_first_live.txt" 2>&1 || true
    timeout 12s rostopic echo -n 1 /Odometry > "${RESULT_DIR}/fastlio_odometry_first_live.txt" 2>&1 || true
    timeout 12s rostopic echo -n 1 /path > "${RESULT_DIR}/fastlio_path_first_live.txt" 2>&1 || true
    timeout 12s rostopic hz /cloud_registered -w 20 > "${RESULT_DIR}/fastlio_cloud_registered_hz_live.txt" 2>&1 || true
    timeout 12s rostopic hz /Odometry -w 20 > "${RESULT_DIR}/fastlio_odometry_hz_live.txt" 2>&1 || true
    timeout 12s rostopic hz /path -w 20 > "${RESULT_DIR}/fastlio_path_hz_live.txt" 2>&1 || true
  ) &
  PIDS+=("$!")

  if [[ "${TOPIC_CONTINUITY_DURATION_S}" != "0" ]]; then
    source "${FASTLIO_WS}/devel/setup.bash"
    python3 "${PROJECT_ROOT}/Scripts/sunray/record_ros1_topic_continuity.py" \
      --duration-s "${TOPIC_CONTINUITY_DURATION_S}" \
      --out "${RESULT_DIR}/topic_continuity_summary.json" \
      > "${RESULT_DIR}/topic_continuity_stdout.txt" 2>&1 &
    PIDS+=("$!")
    source "${SUNRAY_WS}/devel/setup.bash"
  fi
fi

if [[ "${TIME_TF_AUDIT_DURATION_S}" != "0" ]]; then
  python3 "${PROJECT_ROOT}/Scripts/sunray/record_ros1_time_tf_audit.py" \
    --duration-s "${TIME_TF_AUDIT_DURATION_S}" \
    --out "${RESULT_DIR}/time_tf_audit.json" \
    --log-glob "${RESULT_DIR}/*.log" \
    --log-glob "${RESULT_DIR}/*.txt" \
    > "${RESULT_DIR}/time_tf_audit_stdout.txt" 2>&1 &
  PIDS+=("$!")
fi

if [[ "${FREQUENCY_AUDIT_DURATION_S}" != "0" ]]; then
  (
    sleep "${FREQUENCY_AUDIT_DELAY_S:-8}"
    for topic in \
      /imu \
      /uav1/mavros/imu/data \
      /uav1/mavros/local_position/pose \
      /uav1/mavros/local_position/velocity_local \
      /uav1/livox/imu; do
      safe_name="$(echo "${topic}" | sed 's#^/##; s#/#_#g')"
      timeout "${FREQUENCY_AUDIT_DURATION_S}"s rostopic hz -w 80 "${topic}" \
        > "${RESULT_DIR}/${safe_name}_hz.txt" 2>&1 || true
    done
  ) &
  PIDS+=("$!")
fi

if [[ "${CONTROL_DIAGNOSTICS_DURATION_S}" != "0" ]]; then
  python3 "${PROJECT_ROOT}/Scripts/sunray/record_sunray_ros1_control_diagnostics.py" \
    --duration-s "${CONTROL_DIAGNOSTICS_DURATION_S}" \
    --out-dir "${RESULT_DIR}" \
    > "${RESULT_DIR}/control_diagnostics_stdout.txt" 2>&1 &
  PIDS+=("$!")
fi

{
  echo "PX4 PARAM SNAPSHOT"
  for param in \
    MPC_XY_P MPC_Z_P MPC_XY_VEL_P_ACC MPC_XY_VEL_I_ACC MPC_XY_VEL_D_ACC \
    MPC_Z_VEL_P_ACC MPC_Z_VEL_I_ACC MPC_Z_VEL_D_ACC MPC_THR_HOVER \
    MPC_XY_VEL_MAX MPC_Z_VEL_MAX_UP MPC_Z_VEL_MAX_DN MPC_TILTMAX_AIR \
    EKF2_HGT_REF EKF2_AID_MASK EKF2_EV_CTRL EKF2_EV_POS_X EKF2_EV_POS_Y EKF2_EV_POS_Z
  do
    printf "%s\n" "${param}"
    timeout 5s rosservice call /uav1/mavros/param/get "param_id: '${param}'" 2>&1 || true
  done
} > "${RESULT_DIR}/px4_param_snapshot_before_mission.txt" 2>&1 &
PIDS+=("$!")

MISSION_REVIEW_HOLD_ARGS=()
if [[ "${KEEP_ALIVE:-false}" == "true" && "${MISSION_REVIEW_HOLD_S:-}" == "" ]]; then
  MISSION_REVIEW_HOLD_ARGS=(--review-hold-s 36000)
elif [[ "${MISSION_REVIEW_HOLD_S:-}" != "" ]]; then
  MISSION_REVIEW_HOLD_ARGS=(--review-hold-s "${MISSION_REVIEW_HOLD_S}")
fi

MISSION_LIDAR_ARGS=()
if [[ "${REQUIRE_NONEMPTY_LIDAR}" == "true" ]]; then
  MISSION_LIDAR_ARGS=(--require-nonempty-lidar)
fi

MISSION_TIMEOUT_S="${TOTAL_TIMEOUT_S}"
if [[ "${KEEP_ALIVE:-false}" == "true" ]]; then
  MISSION_TIMEOUT_S=$((TOTAL_TIMEOUT_S + ${MISSION_REVIEW_HOLD_TIMEOUT_PADDING_S:-36000}))
fi

set +e
timeout "${MISSION_TIMEOUT_S}s" python3 "${PROJECT_ROOT}/Scripts/sunray/sunray_ros1_mission_node.py" \
  --result-dir "${RESULT_DIR}" \
  --mission "${MISSION}" \
  --external-fusion-source "${EXTERNAL_FUSION_SOURCE}" \
  --external-fusion-position-topic "${EXTERNAL_FUSION_POSITION_TOPIC}" \
  --external-fusion-use-vision-pose "${EXTERNAL_FUSION_USE_VISION_POSE}" \
  --fastlio-enabled "${FASTLIO}" \
  "${MISSION_LIDAR_ARGS[@]}" \
  "${MISSION_REVIEW_HOLD_ARGS[@]}" \
  ${MISSION_NODE_ARGS:-} \
  > "${RESULT_DIR}/mission_node.log" 2>&1
MISSION_STATUS=$?
set -e

if [[ "${FASTLIO}" == "true" ]]; then
  {
    echo "TOPICS"
    rostopic list 2>/dev/null | grep -E "cloud_registered|Odometry|/path|livox|imu" || true
    echo "TYPES"
    for topic in /cloud_registered /cloud_registered_body /Odometry /path /mosim/fastlio/livox/lidar /uav1/livox/lidar /uav1/livox/imu; do
      printf "%s " "${topic}"
      timeout 5s rostopic type "${topic}" || true
    done
  } > "${RESULT_DIR}/fastlio_topic_summary.txt" 2>&1
  timeout 8s rostopic echo -n 1 /cloud_registered > "${RESULT_DIR}/fastlio_cloud_registered_first.txt" 2>&1 || true
  timeout 8s rostopic echo -n 1 /Odometry > "${RESULT_DIR}/fastlio_odometry_first.txt" 2>&1 || true
  timeout 8s rostopic echo -n 1 /path > "${RESULT_DIR}/fastlio_path_first.txt" 2>&1 || true
  timeout 8s rostopic hz /cloud_registered -w 20 > "${RESULT_DIR}/fastlio_cloud_registered_hz.txt" 2>&1 || true
  timeout 8s rostopic hz /Odometry -w 20 > "${RESULT_DIR}/fastlio_odometry_hz.txt" 2>&1 || true
  timeout 8s rostopic hz /path -w 20 > "${RESULT_DIR}/fastlio_path_hz.txt" 2>&1 || true
fi

for pid in "${PIDS[@]:-}"; do
  if kill -0 "${pid}" >/dev/null 2>&1; then
    cmdline="$(tr '\0' ' ' < "/proc/${pid}/cmdline" 2>/dev/null || true)"
    case "${cmdline}" in
      *record_sunray_ros1_control_diagnostics.py*|*rostopic\ hz*)
        wait "${pid}" >/dev/null 2>&1 || true
        ;;
    esac
  fi
done

cat > "${RESULT_DIR}/SESSION.json" <<EOF
{
  "schema": "mosim.sunray_ros1_native_mission_session.v1",
  "status": "mission_exited",
  "mission_exit_code": ${MISSION_STATUS},
  "mission": "${MISSION}",
  "result_dir": "${RESULT_DIR}",
  "sunray_ws": "${SUNRAY_WS}",
  "world_file": "${WORLD_FILE}",
  "use_sim_time": "${USE_SIM_TIME}",
  "gui": "${GUI}",
  "rviz": "${RVIZ}",
  "fastlio": "${FASTLIO}",
  "fastlio_ws": "${FASTLIO_WS}",
  "fastlio_mode": "${FASTLIO_MODE}",
  "fastlio_scan_rate_hz": ${FASTLIO_SCAN_RATE_HZ},
  "vehicle": "sunray150_with_mid360",
  "control_backend": "Sunray native control node -> PX4 SITL -> Gazebo Classic",
  "external_fusion": {
    "source": "${EXTERNAL_FUSION_SOURCE}",
    "position_topic": "${EXTERNAL_FUSION_POSITION_TOPIC}",
    "use_vision_pose": "${EXTERNAL_FUSION_USE_VISION_POSE}"
  },
  "control_feedback_source": "Sunray px4_state from external_fusion_node; current state fields are populated from MAVROS local_position/velocity/imu topics unless PX4 fusion of the configured external_fusion source is separately proven",
  "flight_controller_imu_topic": "/imu -> PX4 -> /uav1/mavros/imu/data",
  "mid360_imu_topic": "/uav1/livox/imu",
  "frequency_gate": {
    "gazebo_physics_target_hz": "${SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ:-400}",
    "flight_controller_imu_world_update_target_hz": "${SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ:-400}",
    "mavros_stream_rate_requested_hz": "${MAVROS_STREAM_RATE_HZ}",
    "mavros_set_message_intervals": "${MAVROS_SET_MESSAGE_INTERVALS}",
    "mavros_set_stream_groups": "${MAVROS_SET_STREAM_GROUPS}",
    "mavros_set_message_ids": "${MAVROS_SET_MESSAGE_IDS}",
    "mavros_rate_limits_patched": "${MAVROS_PATCH_RATE_LIMITS}",
    "px4_mavlink_streams_patched": "${PX4_PATCH_MAVLINK_STREAMS}",
    "px4_mavlink_stream_names": "${PX4_MAVLINK_STREAM_NAMES}",
    "mavros_imu_output_target_hz": "${MAVROS_STREAM_RATE_HZ:-50}",
    "frequency_audit_duration_s": "${FREQUENCY_AUDIT_DURATION_S}",
    "artifacts": [
      "mavros_rate_limit_patch.txt",
      "px4_mavlink_stream_override.txt",
      "mavros_stream_rate_request.txt",
      "imu_hz.txt",
      "uav1_mavros_imu_data_hz.txt",
      "uav1_mavros_local_position_pose_hz.txt",
      "uav1_mavros_local_position_velocity_local_hz.txt",
      "uav1_livox_imu_hz.txt"
    ]
  },
  "sunray_pid_params": {
    "quad_mass": "${SUNRAY_CTRL_QUAD_MASS:-1.0}",
    "hov_percent": "${SUNRAY_CTRL_HOV_PERCENT:-0.37}",
    "thrust_norm_compensation": "${SUNRAY_CTRL_THRUST_NORM_COMPENSATION:-false}",
    "Kp_xy": "${SUNRAY_CTRL_KP_XY:-3.0}",
    "Kp_z": "${SUNRAY_CTRL_KP_Z:-3.0}",
    "Kv_xy": "${SUNRAY_CTRL_KV_XY:-3.0}",
    "Kv_z": "${SUNRAY_CTRL_KV_Z:-3.0}",
    "Kvi_xy": "${SUNRAY_CTRL_KVI_XY:-0.3}",
    "Kvi_z": "${SUNRAY_CTRL_KVI_Z:-0.3}",
    "tilt_angle_max_deg": "${SUNRAY_CTRL_TILT_ANGLE_MAX:-20.0}",
    "takeoff_height": "${SUNRAY_TAKEOFF_HEIGHT:-1.0}",
    "land_speed": "${SUNRAY_LAND_SPEED:-0.25}",
    "control_loop_hz": "${SUNRAY_CTRL_CONTROL_LOOP_HZ:-200.0}"
  },
  "fastlio_feedback_into_control": "unproven_by_this_launcher"
}
EOF

cat "${RESULT_DIR}/SUNRAY_ROS1_NATIVE_MISSION_GATE.json"
if [[ "${KEEP_ALIVE:-false}" == "true" ]]; then
  echo "KEEP_ALIVE=true; Gazebo/RViz/FAST-LIO processes remain active for review. Press Ctrl-C or kill this launcher to stop." >&2
  while true; do
    sleep 3600
  done
fi
exit "${MISSION_STATUS}"
