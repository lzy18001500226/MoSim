#!/usr/bin/env bash
# Run Fast-Drone-250 px4ctrl against the current Sunray ROS1/PX4/Gazebo plant.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/opt/mosim_work/sunray_ws/Sunray}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-/opt/mosim_work/sunray_px4}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/sunray_livox_plugin_ws}"
MISSION="${1:-${MISSION:-takeoff_hover_land}}"
RUN_ID="${RUN_ID:-sunray_ros1_px4ctrl_${MISSION}_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
GUI="${GUI:-false}"
WORLD_FILE="${WORLD_FILE:-${SUNRAY_WS}/simulation/sunray_simulator/worlds/planning_test.world}"
SUNRAY_GAZEBO_LAUNCH_FILE="${SUNRAY_GAZEBO_LAUNCH_FILE:-${SUNRAY_WS}/simulation/sunray_simulator/launch_uav_demo/sunray_sim_uav_planning.launch}"
VEHICLE="${VEHICLE:-sunray150_with_mid360}"
SUNRAY_UAV_INIT_X="${SUNRAY_UAV_INIT_X:-0.0}"
SUNRAY_UAV_INIT_Y="${SUNRAY_UAV_INIT_Y:-0.0}"
SUNRAY_UAV_INIT_Z="${SUNRAY_UAV_INIT_Z:-0.2}"
SUNRAY_UAV_INIT_YAW="${SUNRAY_UAV_INIT_YAW:-0.0}"
USE_SIM_TIME="${USE_SIM_TIME:-true}"
SUNRAY_GAZEBO_MAX_STEP_SIZE_S="${SUNRAY_GAZEBO_MAX_STEP_SIZE_S:-0.001}"
SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ="${SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ:-1000}"
SUNRAY_STRIP_PX4_MODEL_PATH="${SUNRAY_STRIP_PX4_MODEL_PATH:-true}"
SUNRAY_MID360_PLUGIN_DOWNSAMPLE="${SUNRAY_MID360_PLUGIN_DOWNSAMPLE:-4}"
SUNRAY_LIVOX_PLUGIN_FILENAME="${SUNRAY_LIVOX_PLUGIN_FILENAME:-${LIVOX_PLUGIN_WS}/devel/lib/liblivox_laser_simulation.so}"
SUNRAY_MID360_CSV_FILE_NAME="${SUNRAY_MID360_CSV_FILE_NAME:-mid360-real-centr.csv}"
SUNRAY_MID360_GOAL5_CSV_STRIDE="${SUNRAY_MID360_GOAL5_CSV_STRIDE:-4}"
TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-180}"
MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-60}"
MAVROS_STREAM_RATE_HZ="${MAVROS_STREAM_RATE_HZ:-100}"
MAVROS_SET_STREAM_GROUPS="${MAVROS_SET_STREAM_GROUPS:-raw_sensors position extra1 extra2}"
MAVROS_SET_MESSAGE_INTERVALS="${MAVROS_SET_MESSAGE_INTERVALS:-false}"
MAVROS_SET_MESSAGE_IDS="${MAVROS_SET_MESSAGE_IDS:-105:HIGHRES_IMU 30:ATTITUDE 31:ATTITUDE_QUATERNION 32:LOCAL_POSITION_NED}"
FREQUENCY_AUDIT_DURATION_S="${FREQUENCY_AUDIT_DURATION_S:-25}"
FREQUENCY_AUDIT_DELAY_S="${FREQUENCY_AUDIT_DELAY_S:-8}"
CONTROL_DIAGNOSTICS_DURATION_S="${CONTROL_DIAGNOSTICS_DURATION_S:-75}"
TIME_TF_AUDIT_DURATION_S="${TIME_TF_AUDIT_DURATION_S:-75}"
POST_MISSION_DIAGNOSTIC_GRACE_S="${POST_MISSION_DIAGNOSTIC_GRACE_S:-8}"
ODOM_BRIDGE_READY_TIMEOUT_S="${ODOM_BRIDGE_READY_TIMEOUT_S:-20}"
MAVROS_ODOM_BRIDGE_MODE="${MAVROS_ODOM_BRIDGE_MODE:-auto}"
PX4CTRL_MASS="${PX4CTRL_MASS:-0.67}"
PX4CTRL_HOVER_PERCENTAGE="${PX4CTRL_HOVER_PERCENTAGE:-0.294}"
PX4CTRL_THRUST_ESTIMATE_ENABLE="${PX4CTRL_THRUST_ESTIMATE_ENABLE:-false}"
PX4CTRL_KP_XY="${PX4CTRL_KP_XY:-11}"
PX4CTRL_KP_Z="${PX4CTRL_KP_Z:-4}"
PX4CTRL_KV_XY="${PX4CTRL_KV_XY:-6.5}"
PX4CTRL_KV_Z="${PX4CTRL_KV_Z:-4}"
PX4CTRL_KI_XY="${PX4CTRL_KI_XY:-0.0}"
PX4CTRL_KI_Z="${PX4CTRL_KI_Z:-0.0}"
PX4CTRL_SMC_LAMBDA_XY="${PX4CTRL_SMC_LAMBDA_XY:-2.0}"
PX4CTRL_SMC_LAMBDA_Z="${PX4CTRL_SMC_LAMBDA_Z:-2.0}"
PX4CTRL_SMC_ETA_XY="${PX4CTRL_SMC_ETA_XY:-0.1}"
PX4CTRL_SMC_ETA_Z="${PX4CTRL_SMC_ETA_Z:-0.05}"
PX4CTRL_SMC_PHI_XY="${PX4CTRL_SMC_PHI_XY:-0.4}"
PX4CTRL_SMC_PHI_Z="${PX4CTRL_SMC_PHI_Z:-0.35}"
PX4CTRL_SMC_SURFACE_LIMIT_XY="${PX4CTRL_SMC_SURFACE_LIMIT_XY:-3.0}"
PX4CTRL_SMC_SURFACE_LIMIT_Z="${PX4CTRL_SMC_SURFACE_LIMIT_Z:-2.5}"
PX4CTRL_INDI_GAIN_XY="${PX4CTRL_INDI_GAIN_XY:-0.12}"
PX4CTRL_INDI_GAIN_Z="${PX4CTRL_INDI_GAIN_Z:-0.08}"
PX4CTRL_INDI_INCREMENT_LIMIT_XY="${PX4CTRL_INDI_INCREMENT_LIMIT_XY:-0.35}"
PX4CTRL_INDI_INCREMENT_LIMIT_Z="${PX4CTRL_INDI_INCREMENT_LIMIT_Z:-0.20}"
PX4CTRL_INDI_MEASURED_ACCEL_LIMIT_XY="${PX4CTRL_INDI_MEASURED_ACCEL_LIMIT_XY:-6.0}"
PX4CTRL_INDI_MEASURED_ACCEL_LIMIT_Z="${PX4CTRL_INDI_MEASURED_ACCEL_LIMIT_Z:-4.0}"
PX4CTRL_INDI_ACCEL_LPF_ALPHA="${PX4CTRL_INDI_ACCEL_LPF_ALPHA:-0.25}"
PX4CTRL_NMPC_HORIZON_S="${PX4CTRL_NMPC_HORIZON_S:-0.25}"
PX4CTRL_NMPC_POSITION_WEIGHT_XY="${PX4CTRL_NMPC_POSITION_WEIGHT_XY:-1.0}"
PX4CTRL_NMPC_POSITION_WEIGHT_Z="${PX4CTRL_NMPC_POSITION_WEIGHT_Z:-1.0}"
PX4CTRL_NMPC_VELOCITY_WEIGHT_XY="${PX4CTRL_NMPC_VELOCITY_WEIGHT_XY:-0.05}"
PX4CTRL_NMPC_VELOCITY_WEIGHT_Z="${PX4CTRL_NMPC_VELOCITY_WEIGHT_Z:-0.05}"
PX4CTRL_NMPC_CONTROL_WEIGHT_XY="${PX4CTRL_NMPC_CONTROL_WEIGHT_XY:-0.001}"
PX4CTRL_NMPC_CONTROL_WEIGHT_Z="${PX4CTRL_NMPC_CONTROL_WEIGHT_Z:-0.001}"
PX4CTRL_NMPC_ACCEL_LIMIT_XY="${PX4CTRL_NMPC_ACCEL_LIMIT_XY:-4.0}"
PX4CTRL_NMPC_ACCEL_LIMIT_Z="${PX4CTRL_NMPC_ACCEL_LIMIT_Z:-2.5}"
PX4CTRL_NMPC_INCREMENT_LIMIT_XY="${PX4CTRL_NMPC_INCREMENT_LIMIT_XY:-4.0}"
PX4CTRL_NMPC_INCREMENT_LIMIT_Z="${PX4CTRL_NMPC_INCREMENT_LIMIT_Z:-2.5}"
PX4CTRL_CTRL_FREQ_MAX="${PX4CTRL_CTRL_FREQ_MAX:-100.0}"
PX4CTRL_USE_BODYRATE_CTRL="${PX4CTRL_USE_BODYRATE_CTRL:-false}"
PX4CTRL_BODYRATE_ATTITUDE_GAIN_XY="${PX4CTRL_BODYRATE_ATTITUDE_GAIN_XY:-3.0}"
PX4CTRL_BODYRATE_ATTITUDE_GAIN_Z="${PX4CTRL_BODYRATE_ATTITUDE_GAIN_Z:-1.5}"
PX4CTRL_HIGH_ORDER_BODY_RATE_LIMIT_XY="${PX4CTRL_HIGH_ORDER_BODY_RATE_LIMIT_XY:-6.0}"
PX4CTRL_HIGH_ORDER_BODY_RATE_LIMIT_Z="${PX4CTRL_HIGH_ORDER_BODY_RATE_LIMIT_Z:-3.0}"
PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_GAIN_XY="${PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_GAIN_XY:-1.2}"
PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_GAIN_Z="${PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_GAIN_Z:-1.0}"
PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_BOUND_XY="${PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_BOUND_XY:-1.5}"
PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_BOUND_Z="${PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_BOUND_Z:-1.0}"
PX4CTRL_DFBC_ROBUST_DISTURBANCE_OBSERVER_GAIN_XY="${PX4CTRL_DFBC_ROBUST_DISTURBANCE_OBSERVER_GAIN_XY:-0.4}"
PX4CTRL_DFBC_ROBUST_DISTURBANCE_OBSERVER_GAIN_Z="${PX4CTRL_DFBC_ROBUST_DISTURBANCE_OBSERVER_GAIN_Z:-0.3}"
PX4CTRL_DFBC_ROBUST_DISTURBANCE_COMPENSATION_LIMIT_XY="${PX4CTRL_DFBC_ROBUST_DISTURBANCE_COMPENSATION_LIMIT_XY:-1.0}"
PX4CTRL_DFBC_ROBUST_DISTURBANCE_COMPENSATION_LIMIT_Z="${PX4CTRL_DFBC_ROBUST_DISTURBANCE_COMPENSATION_LIMIT_Z:-0.8}"
PX4CTRL_L1_AWFF_MODEL_DECAY="${PX4CTRL_L1_AWFF_MODEL_DECAY:-1.25}"
PX4CTRL_L1_AWFF_FILTER_T="${PX4CTRL_L1_AWFF_FILTER_T:-0.20}"
PX4CTRL_L1_AWFF_GAIN_XY="${PX4CTRL_L1_AWFF_GAIN_XY:-0.32}"
PX4CTRL_L1_AWFF_GAIN_Z="${PX4CTRL_L1_AWFF_GAIN_Z:-0.35}"
PX4CTRL_L1_AWFF_COMP_LIMIT_XY="${PX4CTRL_L1_AWFF_COMP_LIMIT_XY:-2.0}"
PX4CTRL_L1_AWFF_COMP_LIMIT_Z="${PX4CTRL_L1_AWFF_COMP_LIMIT_Z:-2.0}"
PX4CTRL_L1_AWFF_DRAG_FEEDFORWARD_GAIN_XY="${PX4CTRL_L1_AWFF_DRAG_FEEDFORWARD_GAIN_XY:-0.0}"
PX4CTRL_L1_AWFF_DRAG_FEEDFORWARD_GAIN_Z="${PX4CTRL_L1_AWFF_DRAG_FEEDFORWARD_GAIN_Z:-0.0}"
PX4CTRL_SAFETY_FILTER_ACCEL_LIMIT_XY="${PX4CTRL_SAFETY_FILTER_ACCEL_LIMIT_XY:-50.0}"
PX4CTRL_SAFETY_FILTER_ACCEL_LIMIT_Z="${PX4CTRL_SAFETY_FILTER_ACCEL_LIMIT_Z:-50.0}"
PX4CTRL_FAULT_ALLOCATION_ROTOR1_EFFICIENCY="${PX4CTRL_FAULT_ALLOCATION_ROTOR1_EFFICIENCY:-1.0}"
PX4CTRL_FAULT_ALLOCATION_ROTOR2_EFFICIENCY="${PX4CTRL_FAULT_ALLOCATION_ROTOR2_EFFICIENCY:-1.0}"
PX4CTRL_FAULT_ALLOCATION_ROTOR3_EFFICIENCY="${PX4CTRL_FAULT_ALLOCATION_ROTOR3_EFFICIENCY:-1.0}"
PX4CTRL_FAULT_ALLOCATION_ROTOR4_EFFICIENCY="${PX4CTRL_FAULT_ALLOCATION_ROTOR4_EFFICIENCY:-1.0}"
PX4CTRL_FAULT_ALLOCATION_BLEND="${PX4CTRL_FAULT_ALLOCATION_BLEND:-0.52}"
PX4CTRL_FAULT_ALLOCATION_MIN_EFFICIENCY="${PX4CTRL_FAULT_ALLOCATION_MIN_EFFICIENCY:-0.50}"
PX4CTRL_FAULT_ALLOCATION_THRUST_COMP_LIMIT="${PX4CTRL_FAULT_ALLOCATION_THRUST_COMP_LIMIT:-0.25}"
PX4CTRL_ODOM_VELOCITY_FRAME="${PX4CTRL_ODOM_VELOCITY_FRAME:-body}"
PX4CTRL_TAKEOFF_HEIGHT="${PX4CTRL_TAKEOFF_HEIGHT:-1.0}"
PX4CTRL_TAKEOFF_LAND_SPEED="${PX4CTRL_TAKEOFF_LAND_SPEED:-0.12}"
PX4CTRL_CORE_PROFILE="${PX4CTRL_CORE_PROFILE:-original}"
PX4CTRL_START_EXTERNAL_FUSION="${PX4CTRL_START_EXTERNAL_FUSION:-true}"
PX4CTRL_EXTERNAL_FUSION_USE_VISION_POSE="${PX4CTRL_EXTERNAL_FUSION_USE_VISION_POSE:-true}"
PX4CTRL_ENABLE_FASTLIO_EKF_FUSION="${PX4CTRL_ENABLE_FASTLIO_EKF_FUSION:-false}"
PX4CTRL_ODOM_SOURCE="${PX4CTRL_ODOM_SOURCE:-mavros_local}"
PX4CTRL_ODOM_TOPIC="${PX4CTRL_ODOM_TOPIC:-/uav1/mavros/local_position/odom}"
PX4CTRL_MISSION_EXTRA_ARGS="${PX4CTRL_MISSION_EXTRA_ARGS:-}"
PX4CTRL_TAKEOFF_HOVER_DEFAULT_ARGS="${PX4CTRL_TAKEOFF_HOVER_DEFAULT_ARGS:---initial-hover-s 20 --steady-hover-tail-s 8 --land-wait-s 25 --force-disarm-after-land --force-disarm-timeout-s 18 --command-x-bias-m -0.006 --command-y-bias-m -0.004 --command-z-bias-m 0.0 --pre-takeoff-state-stable-s 3.0}"
PX4CTRL_TRAJECTORY_DEFAULT_ARGS="${PX4CTRL_TRAJECTORY_DEFAULT_ARGS:---force-disarm-after-land --force-disarm-timeout-s 18 --pre-takeoff-state-stable-s 3.0}"
PX4CTRL_SKIP_MISSION="${PX4CTRL_SKIP_MISSION:-false}"
PX4CTRL_PARAM_PULL_BEFORE_OVERRIDE="${PX4CTRL_PARAM_PULL_BEFORE_OVERRIDE:-true}"
PX4CTRL_EKF2_EV_CTRL_OVERRIDE="${PX4CTRL_EKF2_EV_CTRL_OVERRIDE:-}"
PX4CTRL_EKF2_HGT_REF_OVERRIDE="${PX4CTRL_EKF2_HGT_REF_OVERRIDE:-}"
PX4CTRL_EXTRA_PARAM_OVERRIDES="${PX4CTRL_EXTRA_PARAM_OVERRIDES:-}"
FASTLIO_ALIGNED_ODOM_TOPIC="${FASTLIO_ALIGNED_ODOM_TOPIC:-/mosim/fastlio/odom_aligned}"
FASTLIO_ALIGNED_PATH_TOPIC="${FASTLIO_ALIGNED_PATH_TOPIC:-/mosim/fastlio/odom_aligned_path}"
FASTLIO_ALIGNMENT_Z_SOURCE_WAS_SET="${FASTLIO_ALIGNMENT_Z_SOURCE+x}"
FASTLIO_ALIGNMENT_Z_SOURCE="${FASTLIO_ALIGNMENT_Z_SOURCE:-fastlio}"
FASTLIO_ALIGNMENT_TRUTH_TOPIC="${FASTLIO_ALIGNMENT_TRUTH_TOPIC:-/uav1/sunray/gazebo_pose}"
FASTLIO_ALIGNMENT_REQUIRED="${FASTLIO_ALIGNMENT_REQUIRED:-auto}"
FASTLIO_ALIGNMENT_STAMP_SOURCE="${FASTLIO_ALIGNMENT_STAMP_SOURCE:-measurement}"
FASTLIO_ALIGNMENT_REFERENCE="${FASTLIO_ALIGNMENT_REFERENCE:-local}"
FASTLIO_ALIGNMENT_ORIGIN_XYZ="${FASTLIO_ALIGNMENT_ORIGIN_XYZ:-0 0 0.035}"
FASTLIO_ALIGNMENT_ORIGIN_RPY="${FASTLIO_ALIGNMENT_ORIGIN_RPY:-0 0 0}"
FASTLIO_ALIGNMENT_REPUBLISH_LATEST="${FASTLIO_ALIGNMENT_REPUBLISH_LATEST:-false}"
GOAL3_FUSION_AUDIT_DURATION_S="${GOAL3_FUSION_AUDIT_DURATION_S:-120}"
NO_FLIGHT_DIAGNOSTIC_HOLD_S="${NO_FLIGHT_DIAGNOSTIC_HOLD_S:-auto}"
REVIEW_OPEN_RVIZ="${REVIEW_OPEN_RVIZ:-false}"
REVIEW_START_CLOUD_NODE="${REVIEW_START_CLOUD_NODE:-false}"
REVIEW_START_FASTLIO="${REVIEW_START_FASTLIO:-${REVIEW_OPEN_RVIZ}}"
REVIEW_START_FASTLIO_ALIGNMENT="${REVIEW_START_FASTLIO_ALIGNMENT:-false}"
FASTLIO_WS="${FASTLIO_WS:-/opt/mosim_work/sunray_ws/fastlio_ws}"
FASTLIO_MODE="${FASTLIO_MODE:-livox_custom}"
FASTLIO_SCAN_RATE_HZ="${FASTLIO_SCAN_RATE_HZ:-20.0}"
FASTLIO_SENSOR_START_TIMEOUT_S="${FASTLIO_SENSOR_START_TIMEOUT_S:-120}"
FASTLIO_START_TIMEOUT_S="${FASTLIO_START_TIMEOUT_S:-90}"
FASTLIO_REVIEW_FILTER_MIN_Z="${FASTLIO_REVIEW_FILTER_MIN_Z:-0.05}"
FASTLIO_AXES_MARKER_TOPIC="${FASTLIO_AXES_MARKER_TOPIC:-/mosim/fastlio/uav_axes}"
FASTLIO_AXES_PATH_TOPIC="${FASTLIO_AXES_PATH_TOPIC:-/mosim/fastlio/uav_path}"
FASTLIO_AXES_CHILD_FRAME="${FASTLIO_AXES_CHILD_FRAME:-mosim_fastlio_uav_body}"
FASTLIO_AXES_ODOM_TOPIC="${FASTLIO_AXES_ODOM_TOPIC:-/Odometry}"
FASTLIO_ODOM_INPUT_POSE_FRAME="${FASTLIO_ODOM_INPUT_POSE_FRAME:-livox}"
FASTLIO_AXES_INPUT_POSE_FRAME="${FASTLIO_AXES_INPUT_POSE_FRAME:-${FASTLIO_ODOM_INPUT_POSE_FRAME}}"
FASTLIO_MOUNT_XYZ="${FASTLIO_MOUNT_XYZ:--0.000005 0.032295 0.050167}"
FASTLIO_MOUNT_RPY="${FASTLIO_MOUNT_RPY:-0 0 4.712389}"
if [[ "${PX4CTRL_ENABLE_FASTLIO_EKF_FUSION}" == "true" ]]; then
  if [[ "${PX4CTRL_ODOM_SOURCE}" != "mavros_local" ]]; then
    echo "PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=true requires PX4CTRL_ODOM_SOURCE=mavros_local; FAST-LIO must feed PX4 EKF, not px4ctrl directly." >&2
    exit 2
  fi
  REVIEW_START_FASTLIO=true
  PX4CTRL_START_EXTERNAL_FUSION=true
  if [[ -z "${FASTLIO_ALIGNMENT_Z_SOURCE_WAS_SET}" ]]; then
    FASTLIO_ALIGNMENT_Z_SOURCE="truth"
  fi
fi
if [[ "${PX4CTRL_ODOM_SOURCE}" == "fastlio" || "${PX4CTRL_ODOM_SOURCE}" == "fastlio_aligned" ]]; then
  REVIEW_START_FASTLIO=true
  if [[ "${PX4CTRL_ODOM_SOURCE}" == "fastlio_aligned" ]]; then
    PX4CTRL_ODOM_TOPIC="${FASTLIO_ALIGNED_ODOM_TOPIC}"
    FASTLIO_AXES_ODOM_TOPIC="${FASTLIO_ALIGNED_ODOM_TOPIC}"
    FASTLIO_AXES_INPUT_POSE_FRAME="base"
  else
    PX4CTRL_ODOM_TOPIC="/Odometry"
  fi
fi
if [[ -z "${PX4CTRL_PATH_FRAME:-}" ]]; then
  if [[ "${PX4CTRL_ODOM_SOURCE}" == "fastlio" ]]; then
    PX4CTRL_PATH_FRAME="camera_init"
  elif [[ "${PX4CTRL_ODOM_SOURCE}" == "fastlio_aligned" ]]; then
    PX4CTRL_PATH_FRAME="world"
  elif [[ "${PX4CTRL_ENABLE_FASTLIO_EKF_FUSION}" == "true" ]]; then
    PX4CTRL_PATH_FRAME="world"
  elif [[ "${REVIEW_START_FASTLIO}" == "true" || "${REVIEW_OPEN_RVIZ}" == "true" ]]; then
    PX4CTRL_PATH_FRAME="camera_init"
  else
    PX4CTRL_PATH_FRAME="map"
  fi
fi
REVIEW_PRESTART_HOLD_S="${REVIEW_PRESTART_HOLD_S:-0}"
REVIEW_TRAJECTORY_RVIZ_CONFIG="${REVIEW_TRAJECTORY_RVIZ_CONFIG:-${PROJECT_ROOT}/Config/rviz/sunray_ros1_trajectory_review.rviz}"
REVIEW_CLOUD_RVIZ_CONFIG="${REVIEW_CLOUD_RVIZ_CONFIG:-${PROJECT_ROOT}/Config/rviz/sunray_ros1_fastlio_accumulated_map_review.rviz}"

case "${PX4CTRL_CORE_PROFILE}" in
  original|mworks_generated|generated_c|mworks_generated_c|official_pid|se3_basic|dfbc_basic|smc_boundary_layer|pid_indi|nmpc_outer|dfbc_high_order|dfbc_jerk_snap|dfbc_smooth_robust|dfbc_smooth_robust_dob|dfbc_wind_robust|dfbc_smooth_robust_indi|l1_awff|l1_residual|awff_l1|safety_filter|fault_allocation)
    ;;
  *)
    echo "Unsupported PX4CTRL_CORE_PROFILE=${PX4CTRL_CORE_PROFILE}" >&2
    exit 2
    ;;
esac

case "${PX4CTRL_ODOM_SOURCE}" in
  mavros_local)
    PX4CTRL_ODOM_TOPIC="/uav1/mavros/local_position/odom"
    ;;
  sunray_truth)
    PX4CTRL_ODOM_TOPIC="/uav1/sunray/gazebo_pose"
    ;;
  fastlio)
    PX4CTRL_ODOM_TOPIC="/Odometry"
    ;;
  fastlio_aligned)
    PX4CTRL_ODOM_TOPIC="${FASTLIO_ALIGNED_ODOM_TOPIC}"
    ;;
  custom)
    if [[ -z "${PX4CTRL_ODOM_TOPIC}" ]]; then
      echo "PX4CTRL_ODOM_SOURCE=custom requires PX4CTRL_ODOM_TOPIC" >&2
      exit 2
    fi
    ;;
  *)
    echo "Unsupported PX4CTRL_ODOM_SOURCE=${PX4CTRL_ODOM_SOURCE}" >&2
    exit 2
    ;;
esac

mkdir -p "${RESULT_DIR}"

if [[ "${SUNRAY_LIVOX_PLUGIN_FILENAME}" == */* && ! -f "${SUNRAY_LIVOX_PLUGIN_FILENAME}" ]]; then
  echo "Livox plugin overlay missing: ${SUNRAY_LIVOX_PLUGIN_FILENAME}; run check_sunray_ros1_runtime_preflight.sh --build-livox first" >&2
  exit 2
fi

PIDS=()
cleanup() {
  set +e
  if [[ "${KEEP_ALIVE:-false}" == "true" ]]; then
    return
  fi
  for pid in "${PIDS[@]:-}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
  for pid in "${PIDS[@]:-}"; do
    wait "${pid}" >/dev/null 2>&1 || true
  done
  sleep 2
  for pid in "${PIDS[@]:-}"; do
    kill -9 "${pid}" >/dev/null 2>&1 || true
  done
  for pid in "${PIDS[@]:-}"; do
    wait "${pid}" >/dev/null 2>&1 || true
  done
  pkill -f "mosim_px4ctrl_basic_mission" >/dev/null 2>&1 || true
  pkill -f "mosim_mavros_pose_velocity_to_odom_bridge" >/dev/null 2>&1 || true
  pkill -f "mosim_px4ctrl_pointcloud_review" >/dev/null 2>&1 || true
  pkill -f "mosim_pointcloud2_to_livox_custom_msg" >/dev/null 2>&1 || true
  pkill -f "fastlio_odom_alignment_adapter" >/dev/null 2>&1 || true
  pkill -f "fastlio_uav_axes_marker_node" >/dev/null 2>&1 || true
  pkill -f "laserMapping" >/dev/null 2>&1 || true
  pkill -f "mapping_mosim_sunray_livox_custom" >/dev/null 2>&1 || true
  pkill -f "mapping_mosim_sunray_pointcloud2" >/dev/null 2>&1 || true
  pkill -f "px4ctrl_node" >/dev/null 2>&1 || true
  pkill -f "rviz.*sunray_ros1_trajectory_review" >/dev/null 2>&1 || true
  pkill -f "rviz.*sunray_ros1_mid360_cloud_review" >/dev/null 2>&1 || true
  pkill -f "rviz.*sunray_ros1_fastlio_accumulated_map_review" >/dev/null 2>&1 || true
  pkill -f "roslaunch .*px4ctrl_mosim.launch" >/dev/null 2>&1 || true
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
  source /usr/share/gazebo/setup.sh
  source /opt/ros/noetic/setup.bash
  source "${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/setup_gazebo.bash" \
    "${SUNRAY_PX4_DIR}" \
    "${SUNRAY_PX4_DIR}/build/px4_sitl_default"
  source "${SUNRAY_WS}/devel/setup.bash"
  if [[ -f "${LIVOX_PLUGIN_WS}/devel/setup.bash" ]]; then
    source "${LIVOX_PLUGIN_WS}/devel/setup.bash"
  fi
  if [[ -f "${FASTLIO_WS}/devel/setup.bash" ]]; then
    source "${FASTLIO_WS}/devel/setup.bash"
  fi

  local sunray_models="${SUNRAY_WS}/simulation/sunray_simulator/models"
  local project_sunray_devel="${PROJECT_ROOT}/References/Sunray/devel"
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
  # The px4ctrl audit workspace was built as a separate catkin workspace whose
  # setup.bash overwrites other overlays. FAST-LIO is also a separate catkin
  # workspace. Merge the runtime paths explicitly after all setup.bash calls so
  # Sunray nodes/messages, Fast-Drone-250 px4ctrl, and Livox FAST-LIO messages
  # remain visible together.
  export CMAKE_PREFIX_PATH="${PX4CTRL_WS}/devel:${project_sunray_devel}:${CMAKE_PREFIX_PATH:-}"
  export ROS_PACKAGE_PATH="${PX4CTRL_WS}/src:${SUNRAY_PX4_DIR}:${SUNRAY_WS}:/opt/ros/noetic/share:${ROS_PACKAGE_PATH:-}"
  export PYTHONPATH="${PX4CTRL_WS}/devel/lib/python3/dist-packages:${SUNRAY_WS}/devel/lib/python3/dist-packages:${project_sunray_devel}/lib/python3/dist-packages:${PYTHONPATH:-}"
  export GAZEBO_MODEL_PATH="${PROJECT_ROOT}/Config/gazebo/models:${sunray_models}/scence_models:${sunray_models}/drone_models:${sunray_models}/sensor_models:${sunray_models}/fake_models:${sunray_models}/ugv_models:${sunray_models}/aws_models:${sunray_models}/aws_vins_models:${GAZEBO_MODEL_PATH:-}"
  export GAZEBO_RESOURCE_PATH="${SUNRAY_WS}/simulation/sunray_simulator:${GAZEBO_RESOURCE_PATH:-}"
  export GAZEBO_PLUGIN_PATH="${LIVOX_PLUGIN_WS}/devel/lib:${SUNRAY_WS}/devel/lib:${project_sunray_devel}/lib:${GAZEBO_PLUGIN_PATH:-}"
  export LD_LIBRARY_PATH="${PX4CTRL_WS}/devel/lib:${LIVOX_PLUGIN_WS}/devel/lib:${SUNRAY_WS}/devel/lib:${project_sunray_devel}/lib:/opt/ros/noetic/lib:${LD_LIBRARY_PATH:-}"
  if [[ -f "${FASTLIO_WS}/devel/setup.bash" ]]; then
    export CMAKE_PREFIX_PATH="${FASTLIO_WS}/devel:${CMAKE_PREFIX_PATH:-}"
    export ROS_PACKAGE_PATH="${FASTLIO_WS}/src:${ROS_PACKAGE_PATH:-}"
    export PYTHONPATH="${FASTLIO_WS}/devel/lib/python3/dist-packages:${PYTHONPATH:-}"
    export LD_LIBRARY_PATH="${FASTLIO_WS}/devel/lib:${LD_LIBRARY_PATH:-}"
  fi
}

FASTLIO_STACK_STARTED=false
FASTLIO_ALIGNMENT_STARTED=false
MAVROS_ODOM_BRIDGE_STARTED=false
start_mavros_local_odom_bridge() {
  if [[ "${MAVROS_ODOM_BRIDGE_STARTED}" == "true" ]]; then
    return
  fi
  if [[ "${MAVROS_ODOM_BRIDGE_MODE}" == "native" ]]; then
    echo "MAVROS_ODOM_BRIDGE_MODE=native; using existing /uav1/mavros/local_position/odom" \
      > "${RESULT_DIR}/odom_bridge.log"
    return
  fi
  if [[ "${MAVROS_ODOM_BRIDGE_MODE}" == "auto" ]]; then
    if python3 "${PROJECT_ROOT}/Scripts/sunray/wait_for_topic_sample.py" --topic /uav1/mavros/local_position/odom --timeout-s 5 --output "${RESULT_DIR}/native_odom_probe.txt" >/dev/null 2>&1; then
      echo "MAVROS_ODOM_BRIDGE_MODE=auto; native /uav1/mavros/local_position/odom is present, bridge not started" \
        > "${RESULT_DIR}/odom_bridge.log"
      return
    fi
  fi
  python3 "${PROJECT_ROOT}/Scripts/sunray/mavros_pose_velocity_to_odom_bridge.py" \
    --pose-topic /uav1/mavros/local_position/pose \
    --velocity-topic /uav1/mavros/local_position/velocity_local \
    --output-topic /uav1/mavros/local_position/odom \
    --frame-id map \
    --child-frame-id uav1/base_link \
    > "${RESULT_DIR}/odom_bridge.log" 2>&1 &
  PIDS+=("$!")
  MAVROS_ODOM_BRIDGE_STARTED=true
}

start_fastlio_stack() {
  if [[ "${FASTLIO_STACK_STARTED}" == "true" ]]; then
    return
  fi
  if [[ ! -d "${FASTLIO_WS}/devel" ]]; then
    echo "FASTLIO_WS devel missing: ${FASTLIO_WS}/devel" >&2
    exit 8
  fi
  source_env

  local deadline
  local livox_ready=false
  deadline=$((SECONDS + FASTLIO_SENSOR_START_TIMEOUT_S))
  while (( SECONDS < deadline )); do
    if python3 "${PROJECT_ROOT}/Scripts/sunray/wait_for_topic_sample.py" --topic /uav1/livox/lidar --timeout-s 5 --output "${RESULT_DIR}/livox_lidar_first.txt" &&
       python3 "${PROJECT_ROOT}/Scripts/sunray/wait_for_topic_sample.py" --topic /uav1/livox/imu --timeout-s 5 --output "${RESULT_DIR}/livox_imu_first.txt"; then
      livox_ready=true
      break
    fi
    sleep 2
  done

  if [[ "${livox_ready}" != "true" ]]; then
    echo "MID360 LiDAR/IMU did not publish before FAST-LIO startup timeout." >&2
    exit 8
  fi

  local fastlio_launch
  if [[ "${FASTLIO_MODE}" == "livox_custom" ]]; then
    python3 "${PROJECT_ROOT}/Scripts/sunray/pointcloud2_to_livox_custom_msg.py" \
      --input-topic /uav1/livox/lidar \
      --output-topic /mosim/fastlio/livox/lidar \
      --imu-topic /uav1/livox/imu \
      --stamp-source imu \
      --frame-id uav1/base_link \
      --scan-rate-hz "${FASTLIO_SCAN_RATE_HZ}" \
      --scan-lines 4 \
      --stride 1 \
      --points-per-scan-hint 20000 \
      > "${RESULT_DIR}/pointcloud2_to_livox_custom.log" 2>&1 &
    PIDS+=("$!")
    sleep 2
    fastlio_launch="mapping_mosim_sunray_livox_custom.launch"
  elif [[ "${FASTLIO_MODE}" == "pointcloud2" ]]; then
    fastlio_launch="mapping_mosim_sunray_pointcloud2.launch"
  else
    echo "unsupported FASTLIO_MODE=${FASTLIO_MODE}" >&2
    exit 8
  fi

  roslaunch fast_lio "${fastlio_launch}" rviz:=false \
    > "${RESULT_DIR}/fastlio_mapping.log" 2>&1 &
  PIDS+=("$!")

  python3 "${PROJECT_ROOT}/Scripts/ros/filter_pointcloud_by_z.py" \
    --input-topic /Laser_map \
    --output-topic /mosim/fastlio/laser_map_obstacles \
    --min-z "${FASTLIO_REVIEW_FILTER_MIN_Z}" \
    --output-json "${RESULT_DIR}/fastlio_laser_map_obstacle_filter.json" \
    > "${RESULT_DIR}/fastlio_laser_map_obstacle_filter.log" 2>&1 &
  PIDS+=("$!")

  python3 "${PROJECT_ROOT}/Scripts/sunray/fastlio_uav_axes_marker_node.py" \
    --odom-topic "${FASTLIO_AXES_ODOM_TOPIC}" \
    --marker-topic "${FASTLIO_AXES_MARKER_TOPIC}" \
    --path-topic "${FASTLIO_AXES_PATH_TOPIC}" \
    --child-frame-id "${FASTLIO_AXES_CHILD_FRAME}" \
    --input-pose-frame "${FASTLIO_AXES_INPUT_POSE_FRAME}" \
    --mount-xyz "${FASTLIO_MOUNT_XYZ}" \
    --mount-rpy "${FASTLIO_MOUNT_RPY}" \
    > "${RESULT_DIR}/fastlio_uav_axes_marker_node.log" 2>&1 &
  PIDS+=("$!")

  local fastlio_ready=false
  deadline=$((SECONDS + FASTLIO_START_TIMEOUT_S))
  while (( SECONDS < deadline )); do
    if python3 "${PROJECT_ROOT}/Scripts/sunray/wait_for_topic_sample.py" --topic /Odometry --timeout-s 5 --output "${RESULT_DIR}/fastlio_odometry_first_live.txt" &&
       python3 "${PROJECT_ROOT}/Scripts/sunray/wait_for_topic_sample.py" --topic /path --timeout-s 5 --output "${RESULT_DIR}/fastlio_path_first_live.txt"; then
      fastlio_ready=true
      break
    fi
    sleep 2
  done

  if [[ "${PX4CTRL_ODOM_SOURCE}" == "fastlio" || "${PX4CTRL_ODOM_SOURCE}" == "fastlio_aligned" ]] && [[ "${fastlio_ready}" != "true" ]]; then
    echo "FAST-LIO /Odometry did not publish before controller odometry timeout." >&2
    exit 8
  fi

  (
    sleep 8
    {
      echo "TOPICS"
      rostopic list 2>/dev/null | grep -E "Laser_map|cloud_registered|Odometry|/path|livox|imu|fastlio/uav" || true
      echo "TYPES"
      for topic in /Laser_map /cloud_registered /Odometry /path "${FASTLIO_AXES_MARKER_TOPIC}" "${FASTLIO_AXES_PATH_TOPIC}" /mosim/fastlio/livox/lidar /uav1/livox/lidar /uav1/livox/imu; do
        printf "%s " "${topic}"
        timeout 5s rostopic type "${topic}" || true
      done
    } > "${RESULT_DIR}/fastlio_topic_summary_live.txt" 2>&1
    python3 "${PROJECT_ROOT}/Scripts/sunray/wait_for_topic_sample.py" --topic /Laser_map --timeout-s 12 --output "${RESULT_DIR}/fastlio_laser_map_first_live.txt" || true
    python3 "${PROJECT_ROOT}/Scripts/sunray/wait_for_topic_sample.py" --topic /cloud_registered --timeout-s 12 --output "${RESULT_DIR}/fastlio_cloud_registered_first_live.txt" || true
    python3 "${PROJECT_ROOT}/Scripts/sunray/wait_for_topic_sample.py" --topic "${FASTLIO_AXES_MARKER_TOPIC}" --timeout-s 12 --output "${RESULT_DIR}/fastlio_uav_axes_first_live.txt" || true
    timeout 12s rostopic hz /Laser_map -w 20 > "${RESULT_DIR}/fastlio_laser_map_hz_live.txt" 2>&1 || true
    timeout 12s rostopic hz /cloud_registered -w 20 > "${RESULT_DIR}/fastlio_cloud_registered_hz_live.txt" 2>&1 || true
  ) &
  PIDS+=("$!")

  FASTLIO_STACK_STARTED=true
}

start_fastlio_alignment_adapter() {
  if [[ "${FASTLIO_ALIGNMENT_STARTED}" == "true" ]]; then
    return
  fi
  start_fastlio_stack
  local republish_args=()
  if [[ "${FASTLIO_ALIGNMENT_REPUBLISH_LATEST}" == "true" ]]; then
    republish_args+=(--republish-latest)
  fi

  python3 "${PROJECT_ROOT}/Scripts/sunray/fastlio_odom_alignment_adapter.py" \
    --fastlio-topic /Odometry \
    --local-topic /uav1/mavros/local_position/odom \
    --output-topic "${FASTLIO_ALIGNED_ODOM_TOPIC}" \
    --path-topic "${FASTLIO_ALIGNED_PATH_TOPIC}" \
    --z-source "${FASTLIO_ALIGNMENT_Z_SOURCE}" \
    --truth-topic "${FASTLIO_ALIGNMENT_TRUTH_TOPIC}" \
    --alignment-reference "${FASTLIO_ALIGNMENT_REFERENCE}" \
    --alignment-origin-xyz "${FASTLIO_ALIGNMENT_ORIGIN_XYZ}" \
    --alignment-origin-rpy "${FASTLIO_ALIGNMENT_ORIGIN_RPY}" \
    --output-frame "${PX4CTRL_PATH_FRAME}" \
    --child-frame "base_link" \
    --stamp-source "${FASTLIO_ALIGNMENT_STAMP_SOURCE}" \
    --input-pose-frame "${FASTLIO_ODOM_INPUT_POSE_FRAME}" \
    --mount-xyz "${FASTLIO_MOUNT_XYZ}" \
    --mount-rpy "${FASTLIO_MOUNT_RPY}" \
    "${republish_args[@]}" \
    > "${RESULT_DIR}/fastlio_odom_alignment_adapter.log" 2>&1 &
  PIDS+=("$!")

  if python3 "${PROJECT_ROOT}/Scripts/sunray/wait_for_topic_sample.py" \
    --topic "${FASTLIO_ALIGNED_ODOM_TOPIC}" \
    --timeout-s "${ODOM_BRIDGE_READY_TIMEOUT_S}" \
    --output "${RESULT_DIR}/fastlio_aligned_odom_first.txt"; then
    FASTLIO_ALIGNMENT_STARTED=true
  fi

  if [[ "${FASTLIO_ALIGNMENT_STARTED}" != "true" ]]; then
    local required="${FASTLIO_ALIGNMENT_REQUIRED}"
    if [[ "${required}" == "auto" ]]; then
      if [[ "${PX4CTRL_ODOM_SOURCE}" == "fastlio_aligned" || "${PX4CTRL_ENABLE_FASTLIO_EKF_FUSION}" == "true" ]]; then
        required=true
      else
        required=false
      fi
    fi
    if [[ "${required}" == "true" ]]; then
      echo "No aligned FAST-LIO odometry on ${FASTLIO_ALIGNED_ODOM_TOPIC}; refusing to start external_fusion." >&2
      exit 9
    fi
    echo "No aligned FAST-LIO odometry on ${FASTLIO_ALIGNED_ODOM_TOPIC}; continuing because FAST-LIO alignment is review-only for this run." \
      > "${RESULT_DIR}/fastlio_alignment_nonfatal_blocker.txt"
  fi
}

if [[ ! -d "${PX4CTRL_WS}/devel" ]]; then
  echo "PX4CTRL_WS devel missing: ${PX4CTRL_WS}/devel" >&2
  exit 2
fi

pkill -f "roslaunch .*sunray_sim_uav" >/dev/null 2>&1 || true
pkill -f "roslaunch .*sunray_uav_control" >/dev/null 2>&1 || true
pkill -f "mosim_mavros_pose_velocity_to_odom_bridge" >/dev/null 2>&1 || true
pkill -f "mosim_px4ctrl_pointcloud_review" >/dev/null 2>&1 || true
pkill -f "mosim_pointcloud2_to_livox_custom_msg" >/dev/null 2>&1 || true
pkill -f "fastlio_odom_alignment_adapter" >/dev/null 2>&1 || true
pkill -f "fastlio_uav_axes_marker_node" >/dev/null 2>&1 || true
pkill -f "laserMapping" >/dev/null 2>&1 || true
pkill -f "mapping_mosim_sunray_livox_custom" >/dev/null 2>&1 || true
pkill -f "mapping_mosim_sunray_pointcloud2" >/dev/null 2>&1 || true
pkill -f "px4ctrl_node" >/dev/null 2>&1 || true
pkill -f "rviz.*sunray_ros1_trajectory_review" >/dev/null 2>&1 || true
pkill -f "rviz.*sunray_ros1_mid360_cloud_review" >/dev/null 2>&1 || true
pkill -f "rviz.*sunray_ros1_fastlio_accumulated_map_review" >/dev/null 2>&1 || true
pkill -f "gzserver" >/dev/null 2>&1 || true
pkill -f "gzclient" >/dev/null 2>&1 || true
pkill -f "mavros_node" >/dev/null 2>&1 || true
pkill -f "/opt/mosim_work/sunray_px4.*/px4" >/dev/null 2>&1 || true
pkill -f "rosmaster" >/dev/null 2>&1 || true
pkill -f "rosout" >/dev/null 2>&1 || true
sleep 3

source_env
export SUNRAY_MID360_PLUGIN_DOWNSAMPLE
export SUNRAY_LIVOX_PLUGIN_FILENAME
export SUNRAY_MID360_CSV_FILE_NAME
export SUNRAY_MID360_GOAL5_CSV_STRIDE
{
  echo "ROS_ENV_SNAPSHOT"
  echo "SUNRAY_GAZEBO_LAUNCH_FILE=${SUNRAY_GAZEBO_LAUNCH_FILE}"
  echo "LIVOX_PLUGIN_WS=${LIVOX_PLUGIN_WS}"
  echo "SUNRAY_STRIP_PX4_MODEL_PATH=${SUNRAY_STRIP_PX4_MODEL_PATH}"
  echo "SUNRAY_MID360_PLUGIN_DOWNSAMPLE=${SUNRAY_MID360_PLUGIN_DOWNSAMPLE}"
  echo "SUNRAY_LIVOX_PLUGIN_FILENAME=${SUNRAY_LIVOX_PLUGIN_FILENAME}"
  env | grep -E '^(ROS_PACKAGE_PATH|PYTHONPATH|CMAKE_PREFIX_PATH|GAZEBO_MODEL_PATH|GAZEBO_RESOURCE_PATH|GAZEBO_PLUGIN_PATH|LD_LIBRARY_PATH)=' || true
  rospack profile || true
  for pkg in px4ctrl quadrotor_msgs sunray_msgs sunray_uav_control; do
    echo "rospack find ${pkg}"
    rospack find "${pkg}"
  done
  python3 -c "import sunray_msgs.msg, quadrotor_msgs.msg; print('python message imports ok')"
} > "${RESULT_DIR}/ros_env_snapshot.txt" 2>&1 || {
  echo "ROS environment missing required px4ctrl/Sunray packages; see ${RESULT_DIR}/ros_env_snapshot.txt" >&2
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

if [[ "${SUNRAY_GAZEBO_LAUNCH_FILE}" == *"factory_l2_sunray_px4_gazebo.launch" || "${SUNRAY_GAZEBO_LAUNCH_FILE}" == *"goal5_swarm_px4_gazebo.launch" ]]; then
  roslaunch "${SUNRAY_GAZEBO_LAUNCH_FILE}" \
    uav_num:=1 vehicle:="${VEHICLE}" gui:="${GUI}" world:="${WORLD_FILE}" use_sim_time:="${USE_SIM_TIME}" \
    uav1_init_x:="${SUNRAY_UAV_INIT_X}" uav1_init_y:="${SUNRAY_UAV_INIT_Y}" \
    uav1_init_z:="${SUNRAY_UAV_INIT_Z}" uav1_init_yaw:="${SUNRAY_UAV_INIT_YAW}" \
    > "${RESULT_DIR}/sunray_gazebo.log" 2>&1 &
else
  roslaunch "${SUNRAY_GAZEBO_LAUNCH_FILE}" \
    gui:="${GUI}" rviz_enable:=false world:="${WORLD_FILE}" use_sim_time:="${USE_SIM_TIME}" \
    uav_init_x:="${SUNRAY_UAV_INIT_X}" uav_init_y:="${SUNRAY_UAV_INIT_Y}" \
    uav_init_yaw:="${SUNRAY_UAV_INIT_YAW}" \
    > "${RESULT_DIR}/sunray_gazebo.log" 2>&1 &
fi
PIDS+=("$!")
echo "${PIDS[-1]}" > "${RESULT_DIR}/sunray_gazebo.pid"

if ! timeout "${MAVROS_READY_TIMEOUT_S}s" python3 - <<'PY' > "${RESULT_DIR}/mavros_state_first.txt" 2>&1
import sys
import rospy
from mavros_msgs.msg import State

connected_msg = None

def cb(msg):
    global connected_msg
    if msg.connected:
        connected_msg = msg
        rospy.signal_shutdown("connected")

rospy.init_node("mosim_wait_mavros_connected", anonymous=True)
rospy.Subscriber("/uav1/mavros/state", State, cb, queue_size=5)
rate = rospy.Rate(20)
while not rospy.is_shutdown() and connected_msg is None:
    rate.sleep()
if connected_msg is None:
    print("connected: False")
    sys.exit(1)
print(f"connected: {connected_msg.connected}")
print(f"armed: {connected_msg.armed}")
print(f"guided: {connected_msg.guided}")
print(f"mode: {connected_msg.mode}")
PY
then
  if ! kill -0 "${PIDS[0]}" >/dev/null 2>&1; then
    echo "sunray gazebo launch exited before MAVROS ready" >&2
    exit 3
  fi
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
      echo "set_stream_rate ${group}(${stream_id}) ${rate_hz}Hz"
      timeout 8s rosservice call /uav1/mavros/set_stream_rate "stream_id: ${stream_id}
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
        timeout 8s rosservice call /uav1/mavros/cmd/command "broadcast: false
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

apply_px4_int_param_override() {
  local param_id="$1"
  local value="$2"
  if [[ -z "${value}" ]]; then
    return 0
  fi
  {
    echo "PARAM_OVERRIDE ${param_id}=${value}"
    if [[ "${PX4CTRL_PARAM_PULL_BEFORE_OVERRIDE}" == "true" ]]; then
      echo "PARAM_PULL_BEFORE_OVERRIDE"
      timeout 15s rosservice call /uav1/mavros/param/pull "force_pull: true" || true
    fi
    echo "PARAM_SET_SERVICE ${param_id}=${value}"
    timeout 8s rosservice call /uav1/mavros/param/set "param_id: '${param_id}'
value:
  integer: ${value}
  real: 0.0" || true
    echo "PARAM_SET_MAVPARAM ${param_id}=${value}"
    timeout 12s rosrun mavros mavparam -n /uav1/mavros set "${param_id}" "${value}" || true
    echo "PARAM_VERIFY_SERVICE ${param_id}"
    timeout 5s rosservice call /uav1/mavros/param/get "param_id: '${param_id}'" || true
    echo "PARAM_VERIFY_MAVPARAM ${param_id}"
    timeout 8s rosrun mavros mavparam -n /uav1/mavros get "${param_id}" || true
  } >> "${RESULT_DIR}/px4_param_overrides.txt" 2>&1
}

apply_px4_param_override() {
  local param_id="$1"
  local value="$2"
  if [[ -z "${param_id}" || -z "${value}" ]]; then
    return 0
  fi
  local integer_value="0"
  local real_value="0.0"
  if [[ "${value}" =~ ^-?[0-9]+$ ]]; then
    integer_value="${value}"
  else
    real_value="${value}"
  fi
  {
    echo "PARAM_OVERRIDE ${param_id}=${value}"
    if [[ "${PX4CTRL_PARAM_PULL_BEFORE_OVERRIDE}" == "true" ]]; then
      echo "PARAM_PULL_BEFORE_OVERRIDE"
      timeout 15s rosservice call /uav1/mavros/param/pull "force_pull: true" || true
    fi
    echo "PARAM_SET_SERVICE ${param_id}=${value}"
    timeout 8s rosservice call /uav1/mavros/param/set "param_id: '${param_id}'
value:
  integer: ${integer_value}
  real: ${real_value}" || true
    echo "PARAM_SET_MAVPARAM ${param_id}=${value}"
    timeout 12s rosrun mavros mavparam -n /uav1/mavros set "${param_id}" "${value}" || true
    echo "PARAM_VERIFY_SERVICE ${param_id}"
    timeout 5s rosservice call /uav1/mavros/param/get "param_id: '${param_id}'" || true
    echo "PARAM_VERIFY_MAVPARAM ${param_id}"
    timeout 8s rosrun mavros mavparam -n /uav1/mavros get "${param_id}" || true
  } >> "${RESULT_DIR}/px4_param_overrides.txt" 2>&1
}

{
  echo "PX4CTRL_EKF2_EV_CTRL_OVERRIDE=${PX4CTRL_EKF2_EV_CTRL_OVERRIDE:-none}"
  echo "PX4CTRL_EKF2_HGT_REF_OVERRIDE=${PX4CTRL_EKF2_HGT_REF_OVERRIDE:-none}"
} > "${RESULT_DIR}/px4_param_overrides.txt"
apply_px4_int_param_override EKF2_EV_CTRL "${PX4CTRL_EKF2_EV_CTRL_OVERRIDE}" || true
apply_px4_int_param_override EKF2_HGT_REF "${PX4CTRL_EKF2_HGT_REF_OVERRIDE}" || true
if [[ -n "${PX4CTRL_EXTRA_PARAM_OVERRIDES}" ]]; then
  for param_pair in ${PX4CTRL_EXTRA_PARAM_OVERRIDES//,/ }; do
    if [[ "${param_pair}" != *=* ]]; then
      echo "Skipping malformed PX4CTRL_EXTRA_PARAM_OVERRIDES item: ${param_pair}" >> "${RESULT_DIR}/px4_param_overrides.txt"
      continue
    fi
    apply_px4_param_override "${param_pair%%=*}" "${param_pair#*=}" || true
  done
fi

if [[ "${FREQUENCY_AUDIT_DURATION_S}" != "0" ]]; then
  (
    sleep "${FREQUENCY_AUDIT_DELAY_S}"
    python3 "${PROJECT_ROOT}/Scripts/sunray/record_ros1_system_frequency_audit.py" \
      --duration-s "${FREQUENCY_AUDIT_DURATION_S}" \
      --out "${RESULT_DIR}/system_frequency_audit.json" \
      > "${RESULT_DIR}/system_frequency_audit_stdout.json" 2>&1 || true
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

if [[ "${PX4CTRL_ENABLE_FASTLIO_EKF_FUSION}" == "true" && "${GOAL3_FUSION_AUDIT_DURATION_S}" != "0" ]]; then
  python3 "${PROJECT_ROOT}/Scripts/sunray/record_fastlio_ekf_fusion_goal3.py" \
    --duration-s "${GOAL3_FUSION_AUDIT_DURATION_S}" \
    --out "${RESULT_DIR}/GOAL3_FASTLIO_EKF_FUSION_AUDIT.json" \
    > "${RESULT_DIR}/goal3_fusion_audit_stdout.json" 2>&1 &
  PIDS+=("$!")
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

{
  echo "PX4 PARAM SNAPSHOT"
  for param in \
    EKF2_HGT_REF EKF2_AID_MASK EKF2_EV_CTRL EKF2_EV_POS_X EKF2_EV_POS_Y EKF2_EV_POS_Z \
    EKF2_EV_DELAY EKF2_EV_NOISE EKF2_EV_NOISE_MD EKF2_EVP_NOISE EKF2_EVV_NOISE EKF2_EVA_NOISE EKF2_REQ_EPH EKF2_REQ_EPV \
    MPC_THR_HOVER MPC_XY_P MPC_Z_P MPC_XY_VEL_P_ACC MPC_XY_VEL_I_ACC MPC_Z_VEL_P_ACC MPC_Z_VEL_I_ACC
  do
    printf "%s\n" "${param}"
    timeout 5s rosservice call /uav1/mavros/param/get "param_id: '${param}'" 2>&1 || true
  done
} > "${RESULT_DIR}/px4_param_snapshot_before_mission.txt" 2>&1 &
PIDS+=("$!")

if [[ "${PX4CTRL_START_EXTERNAL_FUSION}" == "true" ]]; then
  EXTERNAL_FUSION_SOURCE_EFFECTIVE=2
  EXTERNAL_FUSION_POSITION_TOPIC_EFFECTIVE=/uav1/mavros/local_position/pose
  if [[ "${PX4CTRL_ENABLE_FASTLIO_EKF_FUSION}" == "true" ]]; then
    EXTERNAL_FUSION_SOURCE_EFFECTIVE=0
    EXTERNAL_FUSION_POSITION_TOPIC_EFFECTIVE="${FASTLIO_ALIGNED_ODOM_TOPIC}"
    start_mavros_local_odom_bridge
    start_fastlio_alignment_adapter
  fi
  external_fusion_node_bin="${SUNRAY_WS}/devel/lib/sunray_uav_control/external_fusion_node"
  if [[ ! -x "${external_fusion_node_bin}" ]]; then
    echo "external_fusion node missing or not executable: ${external_fusion_node_bin}" >&2
    exit 2
  fi
  "${external_fusion_node_bin}" \
    __name:=external_fusion \
    _uav_id:=1 \
    _uav_name:=uav \
    _external_source:="${EXTERNAL_FUSION_SOURCE_EFFECTIVE}" \
    _position_topic:="${EXTERNAL_FUSION_POSITION_TOPIC_EFFECTIVE}" \
    _use_vision_pose:="${PX4CTRL_EXTERNAL_FUSION_USE_VISION_POSE}" \
    > "${RESULT_DIR}/external_fusion.log" 2>&1 &
  PIDS+=("$!")
  sleep 3
  {
    echo "external_fusion_node_bin=${external_fusion_node_bin}"
    pgrep -af "external_fusion_node" || true
    for external_pid in $(pgrep -f "external_fusion_node" || true); do
      printf "external_fusion_exe[%s]=" "${external_pid}"
      readlink "/proc/${external_pid}/exe" || true
    done
  } > "${RESULT_DIR}/external_fusion_process.txt"
else
  echo "PX4CTRL_START_EXTERNAL_FUSION=false; external_fusion disabled for this px4ctrl diagnostic run" \
    > "${RESULT_DIR}/external_fusion.log"
fi

if [[ "${REVIEW_START_FASTLIO}" == "true" ]]; then
  start_fastlio_stack
fi

if [[ "${REVIEW_START_FASTLIO_ALIGNMENT}" == "true" ]]; then
  start_mavros_local_odom_bridge
  start_fastlio_alignment_adapter
fi

if [[ "${PX4CTRL_ODOM_SOURCE}" == "fastlio_aligned" || "${PX4CTRL_ENABLE_FASTLIO_EKF_FUSION}" == "true" ]]; then
  start_mavros_local_odom_bridge
  start_fastlio_alignment_adapter
  echo "PX4CTRL_ODOM_SOURCE=${PX4CTRL_ODOM_SOURCE}; PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=${PX4CTRL_ENABLE_FASTLIO_EKF_FUSION}; publishing aligned FAST-LIO odometry on ${FASTLIO_ALIGNED_ODOM_TOPIC}" \
    > "${RESULT_DIR}/odom_source.log"
elif [[ "${PX4CTRL_ODOM_SOURCE}" == "mavros_local" ]]; then
  start_mavros_local_odom_bridge
else
  echo "PX4CTRL_ODOM_SOURCE=${PX4CTRL_ODOM_SOURCE}; using existing odometry topic ${PX4CTRL_ODOM_TOPIC}" \
    > "${RESULT_DIR}/odom_bridge.log"
fi

PX4CTRL_ODOM_READY=false
if python3 "${PROJECT_ROOT}/Scripts/sunray/wait_for_topic_sample.py" \
  --topic "${PX4CTRL_ODOM_TOPIC}" \
  --timeout-s "${ODOM_BRIDGE_READY_TIMEOUT_S}" \
  --output "${RESULT_DIR}/odom_first.txt"; then
  PX4CTRL_ODOM_READY=true
fi

if [[ "${PX4CTRL_ODOM_READY}" != "true" ]]; then
  echo "No px4ctrl odometry on ${PX4CTRL_ODOM_TOPIC}" >&2
  exit 5
fi

PX4CTRL_LAUNCH="${RESULT_DIR}/px4ctrl_mosim.launch"
PX4CTRL_CONFIG="$(rospack find px4ctrl)/config/ctrl_param_fpv.yaml"
cat > "${PX4CTRL_LAUNCH}" <<EOF
<launch>
  <node pkg="px4ctrl" type="px4ctrl_node" name="px4ctrl" output="screen">
    <remap from="~odom" to="${PX4CTRL_ODOM_TOPIC}" />
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
    <param name="bodyrate_attitude/gain_x" value="${PX4CTRL_BODYRATE_ATTITUDE_GAIN_XY}" />
    <param name="bodyrate_attitude/gain_y" value="${PX4CTRL_BODYRATE_ATTITUDE_GAIN_XY}" />
    <param name="bodyrate_attitude/gain_z" value="${PX4CTRL_BODYRATE_ATTITUDE_GAIN_Z}" />
    <param name="dfbc_high_order/body_rate_limit_x" value="${PX4CTRL_HIGH_ORDER_BODY_RATE_LIMIT_XY}" />
    <param name="dfbc_high_order/body_rate_limit_y" value="${PX4CTRL_HIGH_ORDER_BODY_RATE_LIMIT_XY}" />
    <param name="dfbc_high_order/body_rate_limit_z" value="${PX4CTRL_HIGH_ORDER_BODY_RATE_LIMIT_Z}" />
    <param name="dfbc_robust/smooth_feedback_gain_x" value="${PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_GAIN_XY}" />
    <param name="dfbc_robust/smooth_feedback_gain_y" value="${PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_GAIN_XY}" />
    <param name="dfbc_robust/smooth_feedback_gain_z" value="${PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_GAIN_Z}" />
    <param name="dfbc_robust/smooth_feedback_bound_x" value="${PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_BOUND_XY}" />
    <param name="dfbc_robust/smooth_feedback_bound_y" value="${PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_BOUND_XY}" />
    <param name="dfbc_robust/smooth_feedback_bound_z" value="${PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_BOUND_Z}" />
    <param name="dfbc_robust/disturbance_observer_gain_x" value="${PX4CTRL_DFBC_ROBUST_DISTURBANCE_OBSERVER_GAIN_XY}" />
    <param name="dfbc_robust/disturbance_observer_gain_y" value="${PX4CTRL_DFBC_ROBUST_DISTURBANCE_OBSERVER_GAIN_XY}" />
    <param name="dfbc_robust/disturbance_observer_gain_z" value="${PX4CTRL_DFBC_ROBUST_DISTURBANCE_OBSERVER_GAIN_Z}" />
    <param name="dfbc_robust/disturbance_compensation_limit_x" value="${PX4CTRL_DFBC_ROBUST_DISTURBANCE_COMPENSATION_LIMIT_XY}" />
    <param name="dfbc_robust/disturbance_compensation_limit_y" value="${PX4CTRL_DFBC_ROBUST_DISTURBANCE_COMPENSATION_LIMIT_XY}" />
    <param name="dfbc_robust/disturbance_compensation_limit_z" value="${PX4CTRL_DFBC_ROBUST_DISTURBANCE_COMPENSATION_LIMIT_Z}" />
    <param name="l1_awff/model_decay" value="${PX4CTRL_L1_AWFF_MODEL_DECAY}" />
    <param name="l1_awff/filter_T" value="${PX4CTRL_L1_AWFF_FILTER_T}" />
    <param name="l1_awff/gain_x" value="${PX4CTRL_L1_AWFF_GAIN_XY}" />
    <param name="l1_awff/gain_y" value="${PX4CTRL_L1_AWFF_GAIN_XY}" />
    <param name="l1_awff/gain_z" value="${PX4CTRL_L1_AWFF_GAIN_Z}" />
    <param name="l1_awff/comp_limit_x" value="${PX4CTRL_L1_AWFF_COMP_LIMIT_XY}" />
    <param name="l1_awff/comp_limit_y" value="${PX4CTRL_L1_AWFF_COMP_LIMIT_XY}" />
    <param name="l1_awff/comp_limit_z" value="${PX4CTRL_L1_AWFF_COMP_LIMIT_Z}" />
    <param name="l1_awff/drag_feedforward_gain_x" value="${PX4CTRL_L1_AWFF_DRAG_FEEDFORWARD_GAIN_XY}" />
    <param name="l1_awff/drag_feedforward_gain_y" value="${PX4CTRL_L1_AWFF_DRAG_FEEDFORWARD_GAIN_XY}" />
    <param name="l1_awff/drag_feedforward_gain_z" value="${PX4CTRL_L1_AWFF_DRAG_FEEDFORWARD_GAIN_Z}" />
    <param name="safety_filter/accel_limit_x" value="${PX4CTRL_SAFETY_FILTER_ACCEL_LIMIT_XY}" />
    <param name="safety_filter/accel_limit_y" value="${PX4CTRL_SAFETY_FILTER_ACCEL_LIMIT_XY}" />
    <param name="safety_filter/accel_limit_z" value="${PX4CTRL_SAFETY_FILTER_ACCEL_LIMIT_Z}" />
    <param name="fault_allocation/rotor1_efficiency" value="${PX4CTRL_FAULT_ALLOCATION_ROTOR1_EFFICIENCY}" />
    <param name="fault_allocation/rotor2_efficiency" value="${PX4CTRL_FAULT_ALLOCATION_ROTOR2_EFFICIENCY}" />
    <param name="fault_allocation/rotor3_efficiency" value="${PX4CTRL_FAULT_ALLOCATION_ROTOR3_EFFICIENCY}" />
    <param name="fault_allocation/rotor4_efficiency" value="${PX4CTRL_FAULT_ALLOCATION_ROTOR4_EFFICIENCY}" />
    <param name="fault_allocation/blend" value="${PX4CTRL_FAULT_ALLOCATION_BLEND}" />
    <param name="fault_allocation/min_efficiency" value="${PX4CTRL_FAULT_ALLOCATION_MIN_EFFICIENCY}" />
    <param name="fault_allocation/thrust_comp_limit" value="${PX4CTRL_FAULT_ALLOCATION_THRUST_COMP_LIMIT}" />
    <param name="odom_velocity_frame" value="${PX4CTRL_ODOM_VELOCITY_FRAME}" />
    <param name="mosim_generated_core_mode" value="${PX4CTRL_CORE_PROFILE}" />
    <param name="auto_takeoff_land/enable" value="true" />
    <param name="auto_takeoff_land/enable_auto_arm" value="true" />
    <param name="auto_takeoff_land/no_RC" value="true" />
    <param name="auto_takeoff_land/takeoff_height" value="${PX4CTRL_TAKEOFF_HEIGHT}" />
    <param name="auto_takeoff_land/takeoff_land_speed" value="${PX4CTRL_TAKEOFF_LAND_SPEED}" />
    <param name="thrust_model/hover_percentage" value="${PX4CTRL_HOVER_PERCENTAGE}" />
    <param name="thrust_model/estimate_enable" value="${PX4CTRL_THRUST_ESTIMATE_ENABLE}" />
    <param name="gain/Kp0" value="${PX4CTRL_KP_XY}" />
    <param name="gain/Kp1" value="${PX4CTRL_KP_XY}" />
    <param name="gain/Kp2" value="${PX4CTRL_KP_Z}" />
    <param name="gain/Kv0" value="${PX4CTRL_KV_XY}" />
    <param name="gain/Kv1" value="${PX4CTRL_KV_XY}" />
    <param name="gain/Kv2" value="${PX4CTRL_KV_Z}" />
    <param name="gain/Kvi0" value="${PX4CTRL_KI_XY}" />
    <param name="gain/Kvi1" value="${PX4CTRL_KI_XY}" />
    <param name="gain/Kvi2" value="${PX4CTRL_KI_Z}" />
    <param name="smc/lambda_x" value="${PX4CTRL_SMC_LAMBDA_XY}" />
    <param name="smc/lambda_y" value="${PX4CTRL_SMC_LAMBDA_XY}" />
    <param name="smc/lambda_z" value="${PX4CTRL_SMC_LAMBDA_Z}" />
    <param name="smc/eta_x" value="${PX4CTRL_SMC_ETA_XY}" />
    <param name="smc/eta_y" value="${PX4CTRL_SMC_ETA_XY}" />
    <param name="smc/eta_z" value="${PX4CTRL_SMC_ETA_Z}" />
    <param name="smc/phi_x" value="${PX4CTRL_SMC_PHI_XY}" />
    <param name="smc/phi_y" value="${PX4CTRL_SMC_PHI_XY}" />
    <param name="smc/phi_z" value="${PX4CTRL_SMC_PHI_Z}" />
    <param name="smc/surface_limit_x" value="${PX4CTRL_SMC_SURFACE_LIMIT_XY}" />
    <param name="smc/surface_limit_y" value="${PX4CTRL_SMC_SURFACE_LIMIT_XY}" />
    <param name="smc/surface_limit_z" value="${PX4CTRL_SMC_SURFACE_LIMIT_Z}" />
    <param name="indi/gain_x" value="${PX4CTRL_INDI_GAIN_XY}" />
    <param name="indi/gain_y" value="${PX4CTRL_INDI_GAIN_XY}" />
    <param name="indi/gain_z" value="${PX4CTRL_INDI_GAIN_Z}" />
    <param name="indi/increment_limit_x" value="${PX4CTRL_INDI_INCREMENT_LIMIT_XY}" />
    <param name="indi/increment_limit_y" value="${PX4CTRL_INDI_INCREMENT_LIMIT_XY}" />
    <param name="indi/increment_limit_z" value="${PX4CTRL_INDI_INCREMENT_LIMIT_Z}" />
    <param name="indi/measured_accel_limit_x" value="${PX4CTRL_INDI_MEASURED_ACCEL_LIMIT_XY}" />
    <param name="indi/measured_accel_limit_y" value="${PX4CTRL_INDI_MEASURED_ACCEL_LIMIT_XY}" />
    <param name="indi/measured_accel_limit_z" value="${PX4CTRL_INDI_MEASURED_ACCEL_LIMIT_Z}" />
    <param name="indi/accel_lpf_alpha" value="${PX4CTRL_INDI_ACCEL_LPF_ALPHA}" />
    <param name="nmpc/horizon_s" value="${PX4CTRL_NMPC_HORIZON_S}" />
    <param name="nmpc/position_weight_x" value="${PX4CTRL_NMPC_POSITION_WEIGHT_XY}" />
    <param name="nmpc/position_weight_y" value="${PX4CTRL_NMPC_POSITION_WEIGHT_XY}" />
    <param name="nmpc/position_weight_z" value="${PX4CTRL_NMPC_POSITION_WEIGHT_Z}" />
    <param name="nmpc/velocity_weight_x" value="${PX4CTRL_NMPC_VELOCITY_WEIGHT_XY}" />
    <param name="nmpc/velocity_weight_y" value="${PX4CTRL_NMPC_VELOCITY_WEIGHT_XY}" />
    <param name="nmpc/velocity_weight_z" value="${PX4CTRL_NMPC_VELOCITY_WEIGHT_Z}" />
    <param name="nmpc/control_weight_x" value="${PX4CTRL_NMPC_CONTROL_WEIGHT_XY}" />
    <param name="nmpc/control_weight_y" value="${PX4CTRL_NMPC_CONTROL_WEIGHT_XY}" />
    <param name="nmpc/control_weight_z" value="${PX4CTRL_NMPC_CONTROL_WEIGHT_Z}" />
    <param name="nmpc/accel_limit_x" value="${PX4CTRL_NMPC_ACCEL_LIMIT_XY}" />
    <param name="nmpc/accel_limit_y" value="${PX4CTRL_NMPC_ACCEL_LIMIT_XY}" />
    <param name="nmpc/accel_limit_z" value="${PX4CTRL_NMPC_ACCEL_LIMIT_Z}" />
    <param name="nmpc/increment_limit_x" value="${PX4CTRL_NMPC_INCREMENT_LIMIT_XY}" />
    <param name="nmpc/increment_limit_y" value="${PX4CTRL_NMPC_INCREMENT_LIMIT_XY}" />
    <param name="nmpc/increment_limit_z" value="${PX4CTRL_NMPC_INCREMENT_LIMIT_Z}" />
  </node>
</launch>
EOF

roslaunch "${PX4CTRL_LAUNCH}" > "${RESULT_DIR}/px4ctrl.log" 2>&1 &
PIDS+=("$!")
sleep 5

if [[ "${REVIEW_START_CLOUD_NODE}" == "true" ]]; then
  python3 "${PROJECT_ROOT}/Scripts/sunray/px4ctrl_pointcloud_review_node.py" \
    --result-dir "${RESULT_DIR}" \
    > "${RESULT_DIR}/pointcloud_review.log" 2>&1 &
  PIDS+=("$!")
  (
    python3 "${PROJECT_ROOT}/Scripts/sunray/wait_for_topic_sample.py" \
      --topic /uav1/livox/lidar \
      --timeout-s 20 \
      --output "${RESULT_DIR}/livox_lidar_first.txt" || true
    timeout 10s rostopic hz -w 20 /uav1/livox/lidar \
      > "${RESULT_DIR}/uav1_livox_lidar_hz.txt" 2>&1 || true
  ) &
  PIDS+=("$!")
fi

if [[ "${REVIEW_OPEN_RVIZ}" == "true" ]]; then
  rviz -d "${REVIEW_CLOUD_RVIZ_CONFIG}" \
    > "${RESULT_DIR}/rviz_cloud.log" 2>&1 &
  PIDS+=("$!")
fi

if [[ "${REVIEW_PRESTART_HOLD_S}" != "0" && "${REVIEW_PRESTART_HOLD_S}" != "0.0" ]]; then
  {
    echo "REVIEW_PRESTART_HOLD_S=${REVIEW_PRESTART_HOLD_S}"
    echo "Waiting before mission start so Gazebo/RViz can paint live review windows."
    date --iso-8601=seconds
  } > "${RESULT_DIR}/review_prestart_hold.txt"
  sleep "${REVIEW_PRESTART_HOLD_S}"
fi

PX4CTRL_MISSION_EFFECTIVE_EXTRA_ARGS="${PX4CTRL_MISSION_EXTRA_ARGS}"
if [[ "${MISSION}" == "takeoff_hover_land" && -z "${PX4CTRL_MISSION_EXTRA_ARGS}" ]]; then
  PX4CTRL_MISSION_EFFECTIVE_EXTRA_ARGS="${PX4CTRL_TAKEOFF_HOVER_DEFAULT_ARGS}"
elif [[ "${MISSION}" != "takeoff_hover_land" && -z "${PX4CTRL_MISSION_EXTRA_ARGS}" ]]; then
  PX4CTRL_MISSION_EFFECTIVE_EXTRA_ARGS="${PX4CTRL_TRAJECTORY_DEFAULT_ARGS}"
fi
if [[ "${PX4CTRL_ODOM_SOURCE}" == "fastlio" || "${PX4CTRL_ODOM_SOURCE}" == "fastlio_aligned" ]]; then
  PX4CTRL_MISSION_EFFECTIVE_EXTRA_ARGS="${PX4CTRL_MISSION_EFFECTIVE_EXTRA_ARGS} --no-require-mavros-local-control-odom --no-require-truth-local-alignment"
fi

if [[ "${PX4CTRL_SKIP_MISSION}" == "true" ]]; then
  {
    echo "PX4CTRL_SKIP_MISSION=true"
    echo "Mission node not started; no arming or setpoints were published by this runner."
    date --iso-8601=seconds
  } > "${RESULT_DIR}/px4ctrl_basic_mission.log"
  if [[ "${NO_FLIGHT_DIAGNOSTIC_HOLD_S}" == "auto" ]]; then
    NO_FLIGHT_DIAGNOSTIC_HOLD_S=$(python3 - <<PY
values = [
    float("${CONTROL_DIAGNOSTICS_DURATION_S}") if "${CONTROL_DIAGNOSTICS_DURATION_S}" != "0" else 0.0,
    float("${TIME_TF_AUDIT_DURATION_S}") if "${TIME_TF_AUDIT_DURATION_S}" != "0" else 0.0,
    float("${GOAL3_FUSION_AUDIT_DURATION_S}") if "${GOAL3_FUSION_AUDIT_DURATION_S}" != "0" else 0.0,
    (float("${FREQUENCY_AUDIT_DELAY_S}") + float("${FREQUENCY_AUDIT_DURATION_S}")) if "${FREQUENCY_AUDIT_DURATION_S}" != "0" else 0.0,
]
print(max(values))
PY
)
  fi
  if [[ "${NO_FLIGHT_DIAGNOSTIC_HOLD_S}" != "0" && "${NO_FLIGHT_DIAGNOSTIC_HOLD_S}" != "0.0" ]]; then
    {
      echo "NO_FLIGHT_DIAGNOSTIC_HOLD_S=${NO_FLIGHT_DIAGNOSTIC_HOLD_S}"
      echo "Holding without mission so passive diagnostics can complete."
      date --iso-8601=seconds
    } > "${RESULT_DIR}/no_flight_diagnostic_hold.txt"
    sleep "${NO_FLIGHT_DIAGNOSTIC_HOLD_S}"
  fi
  MISSION_EXIT_CODE=0
else
  set +e
  timeout "${TOTAL_TIMEOUT_S}s" python3 "${PROJECT_ROOT}/Scripts/sunray/px4ctrl_basic_mission_node.py" \
    --result-dir "${RESULT_DIR}" \
    --mission "${MISSION}" \
    --control-odom-topic "${PX4CTRL_ODOM_TOPIC}" \
    --path-frame "${PX4CTRL_PATH_FRAME}" \
    ${PX4CTRL_MISSION_EFFECTIVE_EXTRA_ARGS} \
    > "${RESULT_DIR}/px4ctrl_basic_mission.log" 2>&1
  MISSION_EXIT_CODE=$?
  set -e
fi

if [[ "${POST_MISSION_DIAGNOSTIC_GRACE_S}" != "0" && "${POST_MISSION_DIAGNOSTIC_GRACE_S}" != "0.0" ]]; then
  sleep "${POST_MISSION_DIAGNOSTIC_GRACE_S}"
fi

if [[ "${PX4CTRL_ODOM_SOURCE}" == "fastlio" ]]; then
  MANIFEST_STATE_SOURCE="fastlio_direct"
  MANIFEST_FASTLIO_CONTROL_INPUT_ALLOWED=true
elif [[ "${PX4CTRL_ODOM_SOURCE}" == "fastlio_aligned" ]]; then
  MANIFEST_STATE_SOURCE="fastlio_aligned_to_mavros_local"
  MANIFEST_FASTLIO_CONTROL_INPUT_ALLOWED=true
else
  MANIFEST_STATE_SOURCE="px4_mavros_or_configured"
  MANIFEST_FASTLIO_CONTROL_INPUT_ALLOWED=false
fi

cat > "${RESULT_DIR}/RUN_MANIFEST.json" <<EOF
{
  "schema": "mosim.sunray_ros1.px4ctrl_basic_gate_manifest.v1",
  "mission": "${MISSION}",
  "result_dir": "${RESULT_DIR}",
  "controller": "References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl",
  "controller_core_profile": "${PX4CTRL_CORE_PROFILE}",
  "claim_boundary": "Fast-Drone-250 px4ctrl ROS wrapper through Sunray ROS1 PX4/Gazebo plant; PX4CTRL_CORE_PROFILE selects original LinearControl, MWORKS generated px4ctrl_core, or G9 ATTITUDE_THRUST controller backend; no Sunray uav_control_node",
  "gazebo": {
    "launch_file": "${SUNRAY_GAZEBO_LAUNCH_FILE}",
    "world_file": "$(printf '%s' "${WORLD_FILE}" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read())[1:-1])')",
    "vehicle": "${VEHICLE}",
    "max_step_size_s": ${SUNRAY_GAZEBO_MAX_STEP_SIZE_S},
    "real_time_update_rate_hz": ${SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ},
    "uav_init_x": ${SUNRAY_UAV_INIT_X},
    "uav_init_y": ${SUNRAY_UAV_INIT_Y},
    "uav_init_z": ${SUNRAY_UAV_INIT_Z},
    "uav_init_yaw": ${SUNRAY_UAV_INIT_YAW},
    "strip_px4_model_path": "${SUNRAY_STRIP_PX4_MODEL_PATH}",
    "livox_plugin_ws": "${LIVOX_PLUGIN_WS}",
    "livox_plugin_filename": "${SUNRAY_LIVOX_PLUGIN_FILENAME}",
    "mid360_plugin_downsample": "${SUNRAY_MID360_PLUGIN_DOWNSAMPLE}",
    "mid360_csv_stride": "${SUNRAY_MID360_GOAL5_CSV_STRIDE}"
  },
  "px4ctrl": {
    "mass": ${PX4CTRL_MASS},
    "hover_percentage": ${PX4CTRL_HOVER_PERCENTAGE},
    "thrust_estimate_enable": ${PX4CTRL_THRUST_ESTIMATE_ENABLE},
    "Kp_xy": ${PX4CTRL_KP_XY},
    "Kp_z": ${PX4CTRL_KP_Z},
    "Kv_xy": ${PX4CTRL_KV_XY},
    "Kv_z": ${PX4CTRL_KV_Z},
    "Ki_xy": ${PX4CTRL_KI_XY},
    "Ki_z": ${PX4CTRL_KI_Z},
    "ctrl_freq_max": ${PX4CTRL_CTRL_FREQ_MAX},
    "use_bodyrate_ctrl": ${PX4CTRL_USE_BODYRATE_CTRL},
    "bodyrate_attitude_gain_xy": ${PX4CTRL_BODYRATE_ATTITUDE_GAIN_XY},
    "bodyrate_attitude_gain_z": ${PX4CTRL_BODYRATE_ATTITUDE_GAIN_Z},
    "high_order_body_rate_limit_xy": ${PX4CTRL_HIGH_ORDER_BODY_RATE_LIMIT_XY},
    "high_order_body_rate_limit_z": ${PX4CTRL_HIGH_ORDER_BODY_RATE_LIMIT_Z},
    "dfbc_robust": {
      "smooth_feedback_gain_xy": ${PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_GAIN_XY},
      "smooth_feedback_gain_z": ${PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_GAIN_Z},
      "smooth_feedback_bound_xy": ${PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_BOUND_XY},
      "smooth_feedback_bound_z": ${PX4CTRL_DFBC_ROBUST_SMOOTH_FEEDBACK_BOUND_Z},
      "disturbance_observer_gain_xy": ${PX4CTRL_DFBC_ROBUST_DISTURBANCE_OBSERVER_GAIN_XY},
      "disturbance_observer_gain_z": ${PX4CTRL_DFBC_ROBUST_DISTURBANCE_OBSERVER_GAIN_Z},
      "disturbance_compensation_limit_xy": ${PX4CTRL_DFBC_ROBUST_DISTURBANCE_COMPENSATION_LIMIT_XY},
      "disturbance_compensation_limit_z": ${PX4CTRL_DFBC_ROBUST_DISTURBANCE_COMPENSATION_LIMIT_Z}
    },
    "l1_awff": {
      "model_decay": ${PX4CTRL_L1_AWFF_MODEL_DECAY},
      "filter_T": ${PX4CTRL_L1_AWFF_FILTER_T},
      "gain_xy": ${PX4CTRL_L1_AWFF_GAIN_XY},
      "gain_z": ${PX4CTRL_L1_AWFF_GAIN_Z},
      "comp_limit_xy": ${PX4CTRL_L1_AWFF_COMP_LIMIT_XY},
      "comp_limit_z": ${PX4CTRL_L1_AWFF_COMP_LIMIT_Z},
      "drag_feedforward_gain_xy": ${PX4CTRL_L1_AWFF_DRAG_FEEDFORWARD_GAIN_XY},
      "drag_feedforward_gain_z": ${PX4CTRL_L1_AWFF_DRAG_FEEDFORWARD_GAIN_Z}
    },
    "safety_filter": {
      "accel_limit_xy": ${PX4CTRL_SAFETY_FILTER_ACCEL_LIMIT_XY},
      "accel_limit_z": ${PX4CTRL_SAFETY_FILTER_ACCEL_LIMIT_Z}
    },
    "fault_allocation": {
      "rotor1_efficiency": ${PX4CTRL_FAULT_ALLOCATION_ROTOR1_EFFICIENCY},
      "rotor2_efficiency": ${PX4CTRL_FAULT_ALLOCATION_ROTOR2_EFFICIENCY},
      "rotor3_efficiency": ${PX4CTRL_FAULT_ALLOCATION_ROTOR3_EFFICIENCY},
      "rotor4_efficiency": ${PX4CTRL_FAULT_ALLOCATION_ROTOR4_EFFICIENCY},
      "blend": ${PX4CTRL_FAULT_ALLOCATION_BLEND},
      "min_efficiency": ${PX4CTRL_FAULT_ALLOCATION_MIN_EFFICIENCY},
      "thrust_comp_limit": ${PX4CTRL_FAULT_ALLOCATION_THRUST_COMP_LIMIT},
      "claim_boundary": "ATTITUDE_THRUST degraded thrust compensation only; not PX4-native motor-level control allocation."
    },
    "odom_velocity_frame": "${PX4CTRL_ODOM_VELOCITY_FRAME}",
    "auto_takeoff_height": ${PX4CTRL_TAKEOFF_HEIGHT},
    "auto_takeoff_land_speed": ${PX4CTRL_TAKEOFF_LAND_SPEED},
    "mission_extra_args": "$(printf '%s' "${PX4CTRL_MISSION_EXTRA_ARGS}" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read())[1:-1])')",
    "mission_effective_extra_args": "$(printf '%s' "${PX4CTRL_MISSION_EFFECTIVE_EXTRA_ARGS}" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read())[1:-1])')",
    "skip_mission": "${PX4CTRL_SKIP_MISSION}",
    "takeoff_hover_default_args": "$(printf '%s' "${PX4CTRL_TAKEOFF_HOVER_DEFAULT_ARGS}" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read())[1:-1])')",
    "trajectory_default_args": "$(printf '%s' "${PX4CTRL_TRAJECTORY_DEFAULT_ARGS}" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read())[1:-1])')",
    "core_profile": "${PX4CTRL_CORE_PROFILE}",
    "smc": {
      "lambda_xy": ${PX4CTRL_SMC_LAMBDA_XY},
      "lambda_z": ${PX4CTRL_SMC_LAMBDA_Z},
      "eta_xy": ${PX4CTRL_SMC_ETA_XY},
      "eta_z": ${PX4CTRL_SMC_ETA_Z},
      "phi_xy": ${PX4CTRL_SMC_PHI_XY},
      "phi_z": ${PX4CTRL_SMC_PHI_Z},
      "surface_limit_xy": ${PX4CTRL_SMC_SURFACE_LIMIT_XY},
      "surface_limit_z": ${PX4CTRL_SMC_SURFACE_LIMIT_Z}
    },
    "indi": {
      "gain_xy": ${PX4CTRL_INDI_GAIN_XY},
      "gain_z": ${PX4CTRL_INDI_GAIN_Z},
      "increment_limit_xy": ${PX4CTRL_INDI_INCREMENT_LIMIT_XY},
      "increment_limit_z": ${PX4CTRL_INDI_INCREMENT_LIMIT_Z},
      "measured_accel_limit_xy": ${PX4CTRL_INDI_MEASURED_ACCEL_LIMIT_XY},
      "measured_accel_limit_z": ${PX4CTRL_INDI_MEASURED_ACCEL_LIMIT_Z},
      "accel_lpf_alpha": ${PX4CTRL_INDI_ACCEL_LPF_ALPHA}
    },
    "nmpc": {
      "horizon_s": ${PX4CTRL_NMPC_HORIZON_S},
      "position_weight_xy": ${PX4CTRL_NMPC_POSITION_WEIGHT_XY},
      "position_weight_z": ${PX4CTRL_NMPC_POSITION_WEIGHT_Z},
      "velocity_weight_xy": ${PX4CTRL_NMPC_VELOCITY_WEIGHT_XY},
      "velocity_weight_z": ${PX4CTRL_NMPC_VELOCITY_WEIGHT_Z},
      "control_weight_xy": ${PX4CTRL_NMPC_CONTROL_WEIGHT_XY},
      "control_weight_z": ${PX4CTRL_NMPC_CONTROL_WEIGHT_Z},
      "accel_limit_xy": ${PX4CTRL_NMPC_ACCEL_LIMIT_XY},
      "accel_limit_z": ${PX4CTRL_NMPC_ACCEL_LIMIT_Z},
      "increment_limit_xy": ${PX4CTRL_NMPC_INCREMENT_LIMIT_XY},
      "increment_limit_z": ${PX4CTRL_NMPC_INCREMENT_LIMIT_Z}
    },
    "start_external_fusion": "${PX4CTRL_START_EXTERNAL_FUSION}",
    "external_fusion_use_vision_pose": "${PX4CTRL_EXTERNAL_FUSION_USE_VISION_POSE}",
    "odom_source": "${PX4CTRL_ODOM_SOURCE}",
    "state_source": "${MANIFEST_STATE_SOURCE}",
    "odom_topic": "${PX4CTRL_ODOM_TOPIC}",
    "odom_bridge": "/uav1/mavros/local_position/pose + /uav1/mavros/local_position/velocity_local -> /uav1/mavros/local_position/odom only when PX4CTRL_ODOM_SOURCE=mavros_local"
  },
  "diagnostics": {
    "frequency_audit_duration_s": "${FREQUENCY_AUDIT_DURATION_S}",
    "control_diagnostics_duration_s": "${CONTROL_DIAGNOSTICS_DURATION_S}",
    "time_tf_audit_duration_s": "${TIME_TF_AUDIT_DURATION_S}",
    "post_mission_diagnostic_grace_s": "${POST_MISSION_DIAGNOSTIC_GRACE_S}",
    "mavros_stream_rate_hz": "${MAVROS_STREAM_RATE_HZ}",
    "mavros_set_stream_groups": "${MAVROS_SET_STREAM_GROUPS}",
    "mavros_set_message_intervals": "${MAVROS_SET_MESSAGE_INTERVALS}",
    "mavros_set_message_ids": "${MAVROS_SET_MESSAGE_IDS}",
    "mission_exit_code": ${MISSION_EXIT_CODE},
    "mavros_odom_bridge_mode": "${MAVROS_ODOM_BRIDGE_MODE}",
    "review_start_fastlio": "${REVIEW_START_FASTLIO}",
    "fastlio_ws": "${FASTLIO_WS}",
    "fastlio_mode": "${FASTLIO_MODE}",
    "fastlio_scan_rate_hz": ${FASTLIO_SCAN_RATE_HZ},
    "path_frame": "${PX4CTRL_PATH_FRAME}",
    "fastlio_axes_marker_topic": "${FASTLIO_AXES_MARKER_TOPIC}",
    "fastlio_axes_path_topic": "${FASTLIO_AXES_PATH_TOPIC}",
    "fastlio_axes_odom_topic": "${FASTLIO_AXES_ODOM_TOPIC}",
    "fastlio_axes_input_pose_frame": "${FASTLIO_AXES_INPUT_POSE_FRAME}",
    "fastlio_odom_input_pose_frame": "${FASTLIO_ODOM_INPUT_POSE_FRAME}",
    "fastlio_aligned_odom_topic": "${FASTLIO_ALIGNED_ODOM_TOPIC}",
    "fastlio_aligned_path_topic": "${FASTLIO_ALIGNED_PATH_TOPIC}",
    "fastlio_alignment_z_source": "${FASTLIO_ALIGNMENT_Z_SOURCE}",
    "fastlio_alignment_truth_topic": "${FASTLIO_ALIGNMENT_TRUTH_TOPIC}",
    "fastlio_alignment_stamp_source": "${FASTLIO_ALIGNMENT_STAMP_SOURCE}",
    "fastlio_alignment_reference": "${FASTLIO_ALIGNMENT_REFERENCE}",
    "fastlio_alignment_origin_xyz": "${FASTLIO_ALIGNMENT_ORIGIN_XYZ}",
    "fastlio_alignment_origin_rpy": "${FASTLIO_ALIGNMENT_ORIGIN_RPY}",
    "fastlio_alignment_republish_latest": "${FASTLIO_ALIGNMENT_REPUBLISH_LATEST}",
    "px4_extra_param_overrides": "$(printf '%s' "${PX4CTRL_EXTRA_PARAM_OVERRIDES}" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read())[1:-1])')",
    "fastlio_ekf_fusion_enabled": "${PX4CTRL_ENABLE_FASTLIO_EKF_FUSION}",
    "external_fusion_source_effective": "${EXTERNAL_FUSION_SOURCE_EFFECTIVE:-none}",
    "external_fusion_position_topic_effective": "${EXTERNAL_FUSION_POSITION_TOPIC_EFFECTIVE:-none}",
    "fastlio_control_input_allowed": ${MANIFEST_FASTLIO_CONTROL_INPUT_ALLOWED},
    "px4_ekf_external_vision": ${PX4CTRL_ENABLE_FASTLIO_EKF_FUSION},
    "gazebo_truth_control_input_allowed": false
  }
}
EOF

echo "${RESULT_DIR}"
if [[ "${KEEP_ALIVE:-false}" == "true" ]]; then
  if [[ "${REVIEW_OPEN_RVIZ}" == "true" ]]; then
    python3 "${PROJECT_ROOT}/Scripts/sunray/px4ctrl_path_hold_from_csv.py" \
      --result-dir "${RESULT_DIR}" \
      --frame-id "${PX4CTRL_PATH_FRAME}" \
      > "${RESULT_DIR}/path_hold_from_csv.log" 2>&1 &
    PIDS+=("$!")
  fi
  echo "KEEP_ALIVE=true; holding ROS/Gazebo processes for visual review after mission exit ${MISSION_EXIT_CODE}" \
    > "${RESULT_DIR}/keep_alive_status.txt"
  while true; do
    alive=0
    for pid in "${PIDS[@]:-}"; do
      if kill -0 "${pid}" >/dev/null 2>&1; then
        alive=1
      fi
    done
    if [[ "${alive}" -eq 0 ]]; then
      echo "all child processes exited" >> "${RESULT_DIR}/keep_alive_status.txt"
      exit "${MISSION_EXIT_CODE}"
    fi
    sleep 5
  done
fi
exit "${MISSION_EXIT_CODE}"
