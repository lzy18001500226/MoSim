#!/usr/bin/env bash
# Real EGO -> PositionCommand -> ControllerOutput -> Gazebo plant gate.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/single_uav_real_ego_closed_loop_gate}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
MOSIM_MSGS_SETUP="${MOSIM_MSGS_SETUP:-${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs_20260615_ego_gate/install/setup.bash}"
EGO_SETUP="${EGO_SETUP:-${PROJECT_ROOT}/Results/tmp/ego_planner_ros2_port_ws/install/setup.bash}"
GAZEBO_ENV_SCRIPT="${GAZEBO_ENV_SCRIPT:-${PROJECT_ROOT}/Scripts/gazebo/setup_gazebo_wsl_env.sh}"
CONTROLLER_FIXTURE_SCRIPT="${CONTROLLER_FIXTURE_SCRIPT:-Scripts/ros/publish_controller_output_fixture.py}"
WORLD="${WORLD:-Config/gazebo/worlds/yunzong_planning_test_sunray150_assembled.sdf}"
GAZEBO_MODEL_PATH="${GAZEBO_MODEL_PATH:-${PROJECT_ROOT}/Config/gazebo/models}"
WORLD_NAME="${WORLD_NAME:-yunzong_planning_test_sunray150_assembled}"
GAZEBO_TRUTH_TOPIC="${GAZEBO_TRUTH_TOPIC:-/world/${WORLD_NAME}/dynamic_pose/info}"
GAZEBO_TRUTH_MODEL_NAME="${GAZEBO_TRUTH_MODEL_NAME:-sunray150_assembled}"
GAZEBO_TRUTH_FRAME_ID="${GAZEBO_TRUTH_FRAME_ID:-world}"
EGO_LAUNCH="${EGO_LAUNCH:-mosim_gazebo_real_planner_gate.launch.py}"
EGO_DEFAULT_CONFIG="${EGO_DEFAULT_CONFIG:-${PROJECT_ROOT}/Results/tmp/ego_planner_ros2_port_ws/src/plan_manage/config/mosim_gazebo_real_planner_gate.yaml}"
EGO_GOAL_X="${EGO_GOAL_X:-7.0}"
EGO_GOAL_Y="${EGO_GOAL_Y:-0.0}"
EGO_GOAL_Z="${EGO_GOAL_Z:-1.2}"
EGO_MANAGER_MAX_VEL="${EGO_MANAGER_MAX_VEL:-0.55}"
EGO_MANAGER_MAX_ACC="${EGO_MANAGER_MAX_ACC:-0.55}"
EGO_OPT_MAX_VEL="${EGO_OPT_MAX_VEL:-0.55}"
EGO_OPT_MAX_ACC="${EGO_OPT_MAX_ACC:-0.55}"
MISSION_START_X="${MISSION_START_X:-0.0}"
MISSION_START_Y="${MISSION_START_Y:-0.0}"
MISSION_START_Z="${MISSION_START_Z:-1.2}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-135}"
RECORD_SECONDS="${RECORD_SECONDS:-110}"
ODOM_TOPIC="${ODOM_TOPIC:-/mosim/planner/odom}"
CLOUD_TOPIC="${CLOUD_TOPIC:-/mosim/planner/global_points}"
ROS_IMU_TOPIC="${ROS_IMU_TOPIC:-/mosim/gazebo/imu}"
ROS_LIDAR_TOPIC="${ROS_LIDAR_TOPIC:-/mosim/gazebo/lidar_points/points}"
ROS_POSITION_CMD_TOPIC="${ROS_POSITION_CMD_TOPIC:-/position_cmd}"
ROS_MOSIM_POSITION_CMD_TOPIC="${ROS_MOSIM_POSITION_CMD_TOPIC:-/mosim/planner/position_cmd}"
ROS_PLANNER_SETPOINT_TOPIC="${ROS_PLANNER_SETPOINT_TOPIC:-/mosim/planner/setpoint}"
ROS_PLANNER_SETPOINT_STATUS_TOPIC="${ROS_PLANNER_SETPOINT_STATUS_TOPIC:-/mosim/planner/setpoint_adapter_status}"
ROS_CONTROLLER_OUTPUT_TOPIC="${ROS_CONTROLLER_OUTPUT_TOPIC:-/mosim/sunray150/controller_output}"
ROS_ACTUATOR_TOPIC="${ROS_ACTUATOR_TOPIC:-/sunray150/gazebo/command/motor_speed}"
REVIEW_ACTUAL_PATH_TOPIC="${REVIEW_ACTUAL_PATH_TOPIC:-/mosim/review/actual_path}"
REVIEW_REFERENCE_PATH_TOPIC="${REVIEW_REFERENCE_PATH_TOPIC:-/mosim/review/reference_path}"
POSITION_CMD_MIN_Z_M="${POSITION_CMD_MIN_Z_M:-${MISSION_START_Z}}"
TRACKER_HOVER_COMMAND="${TRACKER_HOVER_COMMAND:-0.0556055205}"
TRACKER_SETPOINT_TIMEOUT_S="${TRACKER_SETPOINT_TIMEOUT_S:-0.35}"
TRACKER_DURATION_S="${TRACKER_DURATION_S:-110}"
TRACKER_MAX_PUBLISH_HZ="${TRACKER_MAX_PUBLISH_HZ:-20}"
TRACKER_ROLL_CONTROL_SIGN="${TRACKER_ROLL_CONTROL_SIGN:--1.0}"
TRACKER_PITCH_CONTROL_SIGN="${TRACKER_PITCH_CONTROL_SIGN:-1.0}"
TRACKER_ATTITUDE_COMMAND_LIMIT="${TRACKER_ATTITUDE_COMMAND_LIMIT:-0.0035}"
TRACKER_KP_X="${TRACKER_KP_X:-0.0012}"
TRACKER_KD_X="${TRACKER_KD_X:-0.0022}"
TRACKER_KP_Y="${TRACKER_KP_Y:-0.0012}"
TRACKER_KD_Y="${TRACKER_KD_Y:-0.0022}"
TRACKER_KP_Z="${TRACKER_KP_Z:-0.0010}"
TRACKER_KD_Z="${TRACKER_KD_Z:-0.0020}"
TRACKER_KI_Z="${TRACKER_KI_Z:-0.00035}"
TRACKER_KP_ROLL="${TRACKER_KP_ROLL:-0.010}"
TRACKER_KD_ROLL="${TRACKER_KD_ROLL:-0.002}"
TRACKER_KP_PITCH="${TRACKER_KP_PITCH:-0.010}"
TRACKER_KD_PITCH="${TRACKER_KD_PITCH:-0.002}"
TRACKER_COMMAND_MIN="${TRACKER_COMMAND_MIN:-0.0525}"
TRACKER_COMMAND_MAX="${TRACKER_COMMAND_MAX:-0.0575}"
TRACKER_MISSION_GOAL_REFERENCE_RADIUS_M="${TRACKER_MISSION_GOAL_REFERENCE_RADIUS_M:-0.35}"
TRACKER_MISSION_GOAL_CAPTURE_RADIUS_M="${TRACKER_MISSION_GOAL_CAPTURE_RADIUS_M:-0.0}"
TRACKER_MISSION_GOAL_CAPTURE_MIN_ALTITUDE_M="${TRACKER_MISSION_GOAL_CAPTURE_MIN_ALTITUDE_M:-0.45}"
TRACKER_MISSION_GOAL_CAPTURE_XY_SCALE="${TRACKER_MISSION_GOAL_CAPTURE_XY_SCALE:-0.45}"
TRACKER_MISSION_GOAL_CAPTURE_Z_ERROR_M="${TRACKER_MISSION_GOAL_CAPTURE_Z_ERROR_M:-0.35}"
TRACKER_MISSION_GOAL_ACCEPT_RADIUS_M="${TRACKER_MISSION_GOAL_ACCEPT_RADIUS_M:-0.8}"
TRACKER_MISSION_GOAL_HOLD_S="${TRACKER_MISSION_GOAL_HOLD_S:-1.5}"
TRACKER_MISSION_LAND_LOCK="${TRACKER_MISSION_LAND_LOCK:-current}"
TRACKER_MISSION_LAND_Z_M="${TRACKER_MISSION_LAND_Z_M:-0.12}"
TRACKER_MISSION_LAND_RATE_MPS="${TRACKER_MISSION_LAND_RATE_MPS:-0.35}"
TRACKER_LOW_ALTITUDE_XY_SCALE_START_M="${TRACKER_LOW_ALTITUDE_XY_SCALE_START_M:-0.35}"
TRACKER_LOW_ALTITUDE_XY_SCALE_FULL_M="${TRACKER_LOW_ALTITUDE_XY_SCALE_FULL_M:-0.85}"
TRACKER_RECOVERY_XY_BRAKE_SCALE="${TRACKER_RECOVERY_XY_BRAKE_SCALE:-0.35}"
TRACKER_RECOVERY_RESET_ALTITUDE_M="${TRACKER_RECOVERY_RESET_ALTITUDE_M:-0.35}"
TRACKER_RECOVERY_EXIT_ALTITUDE_M="${TRACKER_RECOVERY_EXIT_ALTITUDE_M:-0.85}"
TRACKER_XY_TRACK_FAILSAFE_ERROR_M="${TRACKER_XY_TRACK_FAILSAFE_ERROR_M:-3.0}"
TRACKER_XY_TRACK_FAILSAFE_LAND_AFTER_COUNT="${TRACKER_XY_TRACK_FAILSAFE_LAND_AFTER_COUNT:-20}"
EGO_START_DELAY_S="${EGO_START_DELAY_S:-7}"
TRAJ_SERVER_TIME_SCALE="${TRAJ_SERVER_TIME_SCALE:-0.35}"
TRAJ_SERVER_PATH_FOLLOW_MODE="${TRAJ_SERVER_PATH_FOLLOW_MODE:-true}"
TRAJ_SERVER_PATH_FOLLOW_LOOKAHEAD_S="${TRAJ_SERVER_PATH_FOLLOW_LOOKAHEAD_S:-0.35}"
TRAJ_SERVER_PATH_FOLLOW_SEARCH_AHEAD_S="${TRAJ_SERVER_PATH_FOLLOW_SEARCH_AHEAD_S:-0.8}"
TRAJ_SERVER_PATH_FOLLOW_MAX_PROGRESS_PER_TICK_S="${TRAJ_SERVER_PATH_FOLLOW_MAX_PROGRESS_PER_TICK_S:-0.08}"
TRAJ_SERVER_OUTPUT_SHAPING_ENABLED="${TRAJ_SERVER_OUTPUT_SHAPING_ENABLED:-true}"
TRAJ_SERVER_OUTPUT_MAX_SPEED_MPS="${TRAJ_SERVER_OUTPUT_MAX_SPEED_MPS:-0.45}"
TRAJ_SERVER_OUTPUT_MAX_Z_SPEED_MPS="${TRAJ_SERVER_OUTPUT_MAX_Z_SPEED_MPS:-0.25}"
PLANNER_FILTER_GROUND_MIN_Z="${PLANNER_FILTER_GROUND_MIN_Z:-0.95}"
PLANNER_SELF_FILTER_RADIUS_XY="${PLANNER_SELF_FILTER_RADIUS_XY:-1.0}"
PLANNER_SELF_FILTER_Z_MIN="${PLANNER_SELF_FILTER_Z_MIN:--0.8}"
PLANNER_SELF_FILTER_Z_MAX="${PLANNER_SELF_FILTER_Z_MAX:-0.8}"
if [[ -z "${OBSTACLE_ARGS+x}" ]]; then
  OBSTACLE_ARGS="-4,0,0.2 4,0,0.2 8,0,0.2"
fi
GAZEBO_GUI_REVIEW="${GAZEBO_GUI_REVIEW:-0}"
PRE_UNPAUSE_HOVER_FIXTURE="${PRE_UNPAUSE_HOVER_FIXTURE:-1}"
PRE_UNPAUSE_HOVER_FIXTURE_RATE_HZ="${PRE_UNPAUSE_HOVER_FIXTURE_RATE_HZ:-20}"
PRE_UNPAUSE_HOVER_FIXTURE_TIMES="${PRE_UNPAUSE_HOVER_FIXTURE_TIMES:-40}"

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_DIR}" "${PROJECT_ROOT}/Results/tmp/ros_logs"
export ROS_LOG_DIR="${PROJECT_ROOT}/Results/tmp/ros_logs"
export GZ_SIM_RESOURCE_PATH="${GAZEBO_MODEL_PATH}"
export IGN_GAZEBO_RESOURCE_PATH="${GAZEBO_MODEL_PATH}"

if [[ -f "${GAZEBO_ENV_SCRIPT}" ]]; then
  # shellcheck disable=SC1090
  source "${GAZEBO_ENV_SCRIPT}"
fi

set +u
# shellcheck disable=SC1090
source "${ROS_SETUP}"
# shellcheck disable=SC1090
source "${MOSIM_MSGS_SETUP}"
# shellcheck disable=SC1090
source "${EGO_SETUP}"
set -u

PIDS=()
cleanup() {
  local pid
  for pid in "${PIDS[@]:-}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
  sleep 1
  for pid in "${PIDS[@]:-}"; do
    kill -KILL "${pid}" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT

write_rc() {
  printf '%s\n' "$2" > "$1"
}

unpause_world() {
  ign service \
    -s "/world/${WORLD_NAME}/control" \
    --reqtype ignition.msgs.WorldControl \
    --reptype ignition.msgs.Boolean \
    --timeout 2000 \
    --req "pause: false" \
    > "${RESULT_DIR}/gazebo_world_unpause_response.txt" \
    2> "${RESULT_DIR}/gazebo_world_unpause.stderr.txt" || true
}

EGO_CONFIG_TO_RUN="${RESULT_DIR}/ego_closed_loop_config.yaml"
python3 - "${EGO_DEFAULT_CONFIG}" "${EGO_CONFIG_TO_RUN}" "${EGO_GOAL_X}" "${EGO_GOAL_Y}" "${EGO_GOAL_Z}" "${EGO_MANAGER_MAX_VEL}" "${EGO_MANAGER_MAX_ACC}" "${EGO_OPT_MAX_VEL}" "${EGO_OPT_MAX_ACC}" <<'PY'
from pathlib import Path
import re
import sys

source = Path(sys.argv[1])
target = Path(sys.argv[2])
goal_x, goal_y, goal_z, manager_max_vel, manager_max_acc, opt_max_vel, opt_max_acc = sys.argv[3:10]
text = source.read_text(encoding="utf-8")
for pattern, replacement in {
    r"(\bfsm\.waypoint0_x:\s*)[-+0-9.eE]+": rf"\g<1>{goal_x}",
    r"(\bfsm\.waypoint0_y:\s*)[-+0-9.eE]+": rf"\g<1>{goal_y}",
    r"(\bfsm\.waypoint0_z:\s*)[-+0-9.eE]+": rf"\g<1>{goal_z}",
    r"(\bmanager\.max_vel:\s*)[-+0-9.eE]+": rf"\g<1>{manager_max_vel}",
    r"(\bmanager\.max_acc:\s*)[-+0-9.eE]+": rf"\g<1>{manager_max_acc}",
    r"(\boptimization\.max_vel:\s*)[-+0-9.eE]+": rf"\g<1>{opt_max_vel}",
    r"(\boptimization\.max_acc:\s*)[-+0-9.eE]+": rf"\g<1>{opt_max_acc}",
}.items():
    text, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise SystemExit(f"failed to patch {pattern}")
target.write_text(text, encoding="utf-8")
PY

if [[ "${GAZEBO_GUI_REVIEW}" == "1" ]]; then
  ign gazebo --render-engine ogre "${WORLD}" \
    > "${RESULT_DIR}/gazebo.stdout.log" \
    2> "${RESULT_DIR}/gazebo.stderr.log" &
else
  ign gazebo -s --headless-rendering --render-engine-server ogre "${WORLD}" \
    > "${RESULT_DIR}/gazebo.stdout.log" \
    2> "${RESULT_DIR}/gazebo.stderr.log" &
fi
PIDS+=("$!")
sleep 4

ros2 run ros_gz_bridge parameter_bridge \
  "${ROS_ACTUATOR_TOPIC}@actuator_msgs/msg/Actuators@gz.msgs.Actuators" \
  "${ROS_IMU_TOPIC}@sensor_msgs/msg/Imu@gz.msgs.IMU" \
  "${ROS_LIDAR_TOPIC}@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked" \
  > "${RESULT_DIR}/ros_gz_bridge.stdout.log" \
  2> "${RESULT_DIR}/ros_gz_bridge.stderr.log" &
PIDS+=("$!")
sleep 2

python3 Scripts/ros/gazebo_truth_to_planner_odom_tf.py \
  --gz-topic "${GAZEBO_TRUTH_TOPIC}" \
  --model-name "${GAZEBO_TRUTH_MODEL_NAME}" \
  --map-frame map \
  --body-frame sunray150_assembled/base_link \
  --sensor-frame sunray150_assembled/base_link/mid360_lidar \
  --planner-odom-topic /uav1/sunray/gazebo_pose \
  --mosim-planner-odom-topic "${ODOM_TOPIC}" \
  --sensor-offset 0.035,0,0.045 \
  --poll-timeout-s 0.5 \
  --poll-sleep-s 0.02 \
  --output-json "${RESULT_DIR}/gazebo_truth_to_planner_odom_tf.json" \
  > "${RESULT_DIR}/gazebo_truth_to_planner_odom_tf.stdout.log" \
  2> "${RESULT_DIR}/gazebo_truth_to_planner_odom_tf.stderr.log" &
PIDS+=("$!")
sleep 2

python3 Scripts/ros/gazebo_fastlio_planner_input_adapter.py \
  --lidar-input-topic "${ROS_LIDAR_TOPIC}" \
  --imu-input-topic "${ROS_IMU_TOPIC}" \
  --fastlio-lidar-topic /mosim/fastlio/livox/lidar \
  --fastlio-imu-topic /mosim/fastlio/livox/imu \
  --spark-livox-custom-topic /mosim/spark_fastlio/livox/lidar \
  --sunray-lidar-topic /uav1/livox/lidar \
  --sunray-imu-topic /uav1/livox/imu \
  --planner-global-points-topic /uav1/global_points \
  --mosim-planner-global-points-topic "${CLOUD_TOPIC}" \
  --review-map-cloud-topic /mosim/review/lidar_points_map \
  --review-accumulated-cloud-topic /mosim/review/lidar_points_map_accumulated \
  --review-accumulated-frames 10 \
  --review-accumulated-max-points 150000 \
  --review-accumulated-intensity-policy z \
  --planner-odom-topic /uav1/sunray/gazebo_pose \
  --mosim-planner-odom-topic "${ODOM_TOPIC}" \
  --map-frame map \
  --global-frame map \
  --sensor-frame sunray150_assembled/base_link/mid360_lidar \
  --imu-frame sunray150_assembled/base_link/forward_imu \
  --odom-child-frame uav1/base_link \
  --tf-lookup-timeout-s 0.2 \
  --spark-livox-scan-lines 4 \
  --spark-livox-scan-rate-hz 10 \
  --odom-rate-hz 20 \
  --planner-filter-ground-min-z "${PLANNER_FILTER_GROUND_MIN_Z}" \
  --planner-self-filter-radius-xy "${PLANNER_SELF_FILTER_RADIUS_XY}" \
  --planner-self-filter-z-min "${PLANNER_SELF_FILTER_Z_MIN}" \
  --planner-self-filter-z-max "${PLANNER_SELF_FILTER_Z_MAX}" \
  --output-json "${RESULT_DIR}/fastlio_planner_input_adapter.json" \
  --trace-jsonl "${RESULT_DIR}/fastlio_planner_input_adapter.trace.jsonl" \
  --disable-spark-livox-custom-output \
  --disable-imu-output \
  > "${RESULT_DIR}/fastlio_planner_input_adapter.stdout.log" \
  2> "${RESULT_DIR}/fastlio_planner_input_adapter.stderr.log" &
PIDS+=("$!")
sleep 2

ros2 run ego_planner traj_server_ros2_node \
  --ros-args \
  -p publish_enabled:=true \
  -p bspline_topic:=/planning/bspline \
  -p output_topic:="${ROS_POSITION_CMD_TOPIC}" \
  -p command_rate_hz:=20.0 \
  -p time_forward_s:=0.2 \
  -p trajectory_time_scale:="${TRAJ_SERVER_TIME_SCALE}" \
  -p path_follow_mode:="${TRAJ_SERVER_PATH_FOLLOW_MODE}" \
  -p odom_topic:="${ODOM_TOPIC}" \
  -p path_follow_lookahead_s:="${TRAJ_SERVER_PATH_FOLLOW_LOOKAHEAD_S}" \
  -p path_follow_search_ahead_s:="${TRAJ_SERVER_PATH_FOLLOW_SEARCH_AHEAD_S}" \
  -p path_follow_max_progress_per_tick_s:="${TRAJ_SERVER_PATH_FOLLOW_MAX_PROGRESS_PER_TICK_S}" \
  -p output_shaping_enabled:="${TRAJ_SERVER_OUTPUT_SHAPING_ENABLED}" \
  -p output_max_speed_mps:="${TRAJ_SERVER_OUTPUT_MAX_SPEED_MPS}" \
  -p output_max_z_speed_mps:="${TRAJ_SERVER_OUTPUT_MAX_Z_SPEED_MPS}" \
  > "${RESULT_DIR}/traj_server.stdout.log" \
  2> "${RESULT_DIR}/traj_server.stderr.log" &
PIDS+=("$!")
sleep 1

ros2 run mosim_setpoint_adapter position_command_to_planner_setpoint_node \
  --ros-args \
  -p input_topic:="${ROS_POSITION_CMD_TOPIC}" \
  -p output_topic:="${ROS_MOSIM_POSITION_CMD_TOPIC}" \
  -p expected_frame:=map \
  -p source_frame_alias:=world \
  -p planner_id:=real_ego_bspline \
  -p min_position_z_m:="${POSITION_CMD_MIN_Z_M}" \
  > "${RESULT_DIR}/position_command_converter.stdout.log" \
  2> "${RESULT_DIR}/position_command_converter.stderr.log" &
PIDS+=("$!")
sleep 1

ros2 run mosim_setpoint_adapter planner_setpoint_adapter_node \
  --ros-args \
  -p input_topic:="${ROS_MOSIM_POSITION_CMD_TOPIC}" \
  -p output_topic:="${ROS_PLANNER_SETPOINT_TOPIC}" \
  -p status_topic:="${ROS_PLANNER_SETPOINT_STATUS_TOPIC}" \
  -p expected_frame:=map \
  -p rate_hz:=20.0 \
  -p stale_timeout_s:="${TRACKER_SETPOINT_TIMEOUT_S}" \
  > "${RESULT_DIR}/planner_setpoint_adapter.stdout.log" \
  2> "${RESULT_DIR}/planner_setpoint_adapter.stderr.log" &
PIDS+=("$!")
sleep 1

python3 Scripts/ros/controller_output_to_gazebo_actuators_node.py \
  --input-topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" \
  --output-topic "${ROS_ACTUATOR_TOPIC}" \
  --vehicle-id sunray150 \
  --max-messages 0 \
  --max-command-age-s 2.0 \
  --output-json "${RESULT_DIR}/controller_output_adapter_node.json" \
  --trace-jsonl "${RESULT_DIR}/controller_output_adapter_node.trace.jsonl" \
  > "${RESULT_DIR}/controller_output_node.stdout.log" \
  2> "${RESULT_DIR}/controller_output_node.stderr.log" &
PIDS+=("$!")
sleep 1

if [[ "${PRE_UNPAUSE_HOVER_FIXTURE}" == "1" ]]; then
  python3 "${CONTROLLER_FIXTURE_SCRIPT}" \
    --topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" \
    --vehicle-id sunray150 \
    --command-type normalized_motor_speed \
    --command "${TRACKER_HOVER_COMMAND}" "${TRACKER_HOVER_COMMAND}" "${TRACKER_HOVER_COMMAND}" "${TRACKER_HOVER_COMMAND}" \
    --rate-hz "${PRE_UNPAUSE_HOVER_FIXTURE_RATE_HZ}" \
    --times "${PRE_UNPAUSE_HOVER_FIXTURE_TIMES}" \
    --backend real_ego_pre_unpause_hover_fixture \
    --source-authority bounded_real_ego_pre_unpause_hover_startup_guard \
    --output-json "${RESULT_DIR}/pre_unpause_hover_fixture.json" \
    > "${RESULT_DIR}/pre_unpause_hover_fixture.stdout.log" \
    2> "${RESULT_DIR}/pre_unpause_hover_fixture.stderr.log" || true
fi

python3 Scripts/ros/gazebo_truth_position_controller.py \
  --input-topic-name "${GAZEBO_TRUTH_TOPIC}" \
  --model-name "${GAZEBO_TRUTH_MODEL_NAME}" \
  --truth-frame-id "${GAZEBO_TRUTH_FRAME_ID}" \
  --setpoint-topic "${ROS_PLANNER_SETPOINT_TOPIC}" \
  --output-topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" \
  --vehicle-id sunray150 \
  --expected-frame map \
  --hover-command "${TRACKER_HOVER_COMMAND}" \
  --kp-x "${TRACKER_KP_X}" --kd-x "${TRACKER_KD_X}" --ka-x 0.0 \
  --kp-y "${TRACKER_KP_Y}" --kd-y "${TRACKER_KD_Y}" --ka-y 0.0 \
  --kp-z "${TRACKER_KP_Z}" --kd-z "${TRACKER_KD_Z}" --ki-z "${TRACKER_KI_Z}" \
  --kp-roll "${TRACKER_KP_ROLL}" --kd-roll "${TRACKER_KD_ROLL}" \
  --kp-pitch "${TRACKER_KP_PITCH}" --kd-pitch "${TRACKER_KD_PITCH}" \
  --kp-yaw 0.0 --kd-yaw 0.0 \
  --attitude-command-limit "${TRACKER_ATTITUDE_COMMAND_LIMIT}" \
  --xy-control-sign -1.0 \
  --roll-control-sign "${TRACKER_ROLL_CONTROL_SIGN}" \
  --pitch-control-sign "${TRACKER_PITCH_CONTROL_SIGN}" \
  --takeoff-xy-enable-altitude-m 0.9 \
  --takeoff-stable-z-error-m 0.25 \
  --takeoff-stable-max-vz-mps 0.35 \
  --takeoff-stable-s 0.8 \
  --low-altitude-xy-scale-start-m "${TRACKER_LOW_ALTITUDE_XY_SCALE_START_M}" \
  --low-altitude-xy-scale-full-m "${TRACKER_LOW_ALTITUDE_XY_SCALE_FULL_M}" \
  --mission-goal "${EGO_GOAL_X},${EGO_GOAL_Y},${EGO_GOAL_Z}" \
  --mission-goal-reference-radius-m "${TRACKER_MISSION_GOAL_REFERENCE_RADIUS_M}" \
  --mission-goal-capture-radius-m "${TRACKER_MISSION_GOAL_CAPTURE_RADIUS_M}" \
  --mission-goal-capture-min-altitude-m "${TRACKER_MISSION_GOAL_CAPTURE_MIN_ALTITUDE_M}" \
  --mission-goal-capture-xy-scale "${TRACKER_MISSION_GOAL_CAPTURE_XY_SCALE}" \
  --mission-goal-capture-z-error-m "${TRACKER_MISSION_GOAL_CAPTURE_Z_ERROR_M}" \
  --mission-goal-accept-radius-m "${TRACKER_MISSION_GOAL_ACCEPT_RADIUS_M}" \
  --mission-goal-hold-s "${TRACKER_MISSION_GOAL_HOLD_S}" \
  --mission-land-lock "${TRACKER_MISSION_LAND_LOCK}" \
  --mission-land-z-m "${TRACKER_MISSION_LAND_Z_M}" \
  --mission-land-rate-mps "${TRACKER_MISSION_LAND_RATE_MPS}" \
  --recovery-xy-brake-scale "${TRACKER_RECOVERY_XY_BRAKE_SCALE}" \
  --recovery-reset-altitude-m "${TRACKER_RECOVERY_RESET_ALTITUDE_M}" \
  --recovery-exit-altitude-m "${TRACKER_RECOVERY_EXIT_ALTITUDE_M}" \
  --xy-error-limit-m 1.5 \
  --xy-velocity-error-limit-mps 1.0 \
  --xy-track-failsafe-error-m "${TRACKER_XY_TRACK_FAILSAFE_ERROR_M}" \
  --xy-track-failsafe-land-after-count "${TRACKER_XY_TRACK_FAILSAFE_LAND_AFTER_COUNT}" \
  --integral-limit-m-s 1.0 \
  --command-min "${TRACKER_COMMAND_MIN}" \
  --command-max "${TRACKER_COMMAND_MAX}" \
  --setpoint-timeout-s "${TRACKER_SETPOINT_TIMEOUT_S}" \
  --max-publish-hz "${TRACKER_MAX_PUBLISH_HZ}" \
  --duration-s "${TRACKER_DURATION_S}" \
  --truth-wall-time-factor 1.0 \
  --sync-truth-to-wall-time \
  --output-json "${RESULT_DIR}/real_ego_setpoint_tracker.json" \
  --trace-jsonl "${RESULT_DIR}/real_ego_setpoint_tracker.trace.jsonl" \
  < <(timeout --kill-after=5s "${TIMEOUT_SECONDS}" ign topic -e -t "${GAZEBO_TRUTH_TOPIC}") \
  > "${RESULT_DIR}/real_ego_setpoint_tracker.stdout.log" \
  2> "${RESULT_DIR}/real_ego_setpoint_tracker.stderr.log" &
PIDS+=("$!")
sleep 1

timeout --kill-after=5s "${TIMEOUT_SECONDS}" ign topic -e -t "${GAZEBO_TRUTH_TOPIC}" | \
  python3 Scripts/gazebo/record_gazebo_pose_truth.py \
    --output-jsonl "${RESULT_DIR}/gazebo_truth_pose.jsonl" \
    --summary-json "${RESULT_DIR}/GAZEBO_TRUTH_POSE_RECORDING.json" \
    --topic "${GAZEBO_TRUTH_TOPIC}" \
    --model-name "${GAZEBO_TRUTH_MODEL_NAME}" \
    --frame-id "${GAZEBO_TRUTH_FRAME_ID}" \
  > "${RESULT_DIR}/gazebo_truth_pose_recorder.stdout.log" \
  2> "${RESULT_DIR}/gazebo_truth_pose_recorder.stderr.log" &
RECORDER_PID="$!"

python3 Scripts/ros/record_real_ego_rviz_review_topics.py \
  --output-json "${RESULT_DIR}/real_ego_topic_recorder.json" \
  --duration-seconds "${RECORD_SECONDS}" \
  --raw-lidar-topic "${ROS_LIDAR_TOPIC}" \
  --planner-cloud-topic "${CLOUD_TOPIC}" \
  --ego-inflate-topic /grid_map/occupancy_inflate \
  --actual-path-topic "${REVIEW_ACTUAL_PATH_TOPIC}" \
  --reference-path-topic "${REVIEW_REFERENCE_PATH_TOPIC}" \
  --position-command-topic "${ROS_POSITION_CMD_TOPIC}" \
  --planner-setpoint-topic "${ROS_PLANNER_SETPOINT_TOPIC}" \
  --controller-output-topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" \
  --position-command-trace-jsonl "${RESULT_DIR}/position_cmd.trace.jsonl" \
  --planner-setpoint-trace-jsonl "${RESULT_DIR}/planner_setpoint.trace.jsonl" \
  --controller-output-trace-jsonl "${RESULT_DIR}/controller_output.trace.jsonl" \
  --max-points 250000 \
  > "${RESULT_DIR}/real_ego_topic_recorder.stdout.log" \
  2> "${RESULT_DIR}/real_ego_topic_recorder.stderr.log" &
TOPIC_RECORDER_PID="$!"

unpause_world

sleep "${EGO_START_DELAY_S}"

ros2 launch ego_planner "${EGO_LAUNCH}" \
  config_file:="${EGO_CONFIG_TO_RUN}" \
  odom_topic:="${ODOM_TOPIC}" \
  cloud_topic:="${CLOUD_TOPIC}" \
  > "${RESULT_DIR}/ego_planner.stdout.log" \
  2> "${RESULT_DIR}/ego_planner.stderr.log" &
PIDS+=("$!")
sleep 2

if wait "${RECORDER_PID}"; then
  write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" 0
else
  write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" "$?"
fi
if wait "${TOPIC_RECORDER_PID}"; then
  write_rc "${RESULT_DIR}/real_ego_topic_recorder.rc" 0
else
  write_rc "${RESULT_DIR}/real_ego_topic_recorder.rc" "$?"
fi

timeout 5 ros2 topic list > "${RESULT_DIR}/ros2_topic_list.txt" 2> "${RESULT_DIR}/ros2_topic_list.stderr.txt" || true

obstacle_cli=()
for item in ${OBSTACLE_ARGS}; do
  obstacle_cli+=("--obstacle=${item}")
done

eval_rc=0
python3 Scripts/quality/evaluate_real_ego_closed_loop_gate.py \
  --truth-jsonl "${RESULT_DIR}/gazebo_truth_pose.jsonl" \
  --truth-summary-json "${RESULT_DIR}/GAZEBO_TRUTH_POSE_RECORDING.json" \
  --ego-topic-recorder-json "${RESULT_DIR}/real_ego_topic_recorder.json" \
  --traj-server-log "${RESULT_DIR}/traj_server.stdout.log" \
  --traj-server-stderr-log "${RESULT_DIR}/traj_server.stderr.log" \
  --controller-adapter-json "${RESULT_DIR}/controller_output_adapter_node.json" \
  --controller-adapter-trace-jsonl "${RESULT_DIR}/controller_output_adapter_node.trace.jsonl" \
  --start "${MISSION_START_X},${MISSION_START_Y},${MISSION_START_Z}" \
  --goal "${EGO_GOAL_X},${EGO_GOAL_Y},${EGO_GOAL_Z}" \
  "${obstacle_cli[@]}" \
  --output-json "${RESULT_DIR}/REAL_EGO_CLOSED_LOOP_GATE.json" \
  > "${RESULT_DIR}/real_ego_closed_loop_eval.stdout.log" \
  2> "${RESULT_DIR}/real_ego_closed_loop_eval.stderr.log" || eval_rc="$?"
write_rc "${RESULT_DIR}/real_ego_closed_loop_eval.rc" "${eval_rc}"

python3 - <<PY
import json
from pathlib import Path
out = Path("${RESULT_DIR}")
gate = json.loads((out / "REAL_EGO_CLOSED_LOOP_GATE.json").read_text(encoding="utf-8")) if (out / "REAL_EGO_CLOSED_LOOP_GATE.json").exists() else {}
runtime = {
    "schema": "mosim.real_ego_closed_loop_runtime_status.v1",
    "status": "runtime_gate_passed" if gate.get("gate_passed") else "runtime_gate_blocked",
    "gate_passed": bool(gate.get("gate_passed")),
    "result_dir": "${RESULT_DIR}",
    "world": "${WORLD}",
    "goal_m": [float("${EGO_GOAL_X}"), float("${EGO_GOAL_Y}"), float("${EGO_GOAL_Z}")],
    "eval": "REAL_EGO_CLOSED_LOOP_GATE.json",
    "blockers": gate.get("blockers", ["missing_eval"]),
    "claim_boundary": [
        "Real EGO bspline is connected to PositionCommand, PlannerSetpoint, truth-feedback tracker, ControllerOutput, Gazebo actuator topic, and Gazebo truth evaluation.",
        "This remains pre-acceptance and does not claim final MWORKS controller performance or multi-UAV readiness."
    ],
}
(out / "RUNTIME_STATUS.json").write_text(json.dumps(runtime, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
print(json.dumps(runtime, ensure_ascii=False, indent=2))
PY

cat "${RESULT_DIR}/RUNTIME_STATUS.json"
