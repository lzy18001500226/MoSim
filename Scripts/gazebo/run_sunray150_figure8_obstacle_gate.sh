#!/usr/bin/env bash
# Bounded single-UAV figure-8 + static-obstacle Gazebo/ROS2 pre-acceptance gate.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
GAZEBO_ENV_SCRIPT="${GAZEBO_ENV_SCRIPT:-${PROJECT_ROOT}/Scripts/gazebo/setup_gazebo_wsl_env.sh}"
if [[ -f "${GAZEBO_ENV_SCRIPT}" ]]; then
  # shellcheck disable=SC1090
  source "${GAZEBO_ENV_SCRIPT}"
fi
SCENARIO="${SCENARIO:-Config/scenarios/system/sunray150_single_uav_competition_light.yaml}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/sunray150_single_uav_figure8_static_obstacle_pre_acceptance}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
ROS_LOG_DIR="${ROS_LOG_DIR:-${PROJECT_ROOT}/Results/tmp/ros_logs}"
MOSIM_ROS2_WS="${MOSIM_ROS2_WS:-${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs}"
BUILD_MOSIM_ROS2_MSGS="${BUILD_MOSIM_ROS2_MSGS:-0}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-35}"
GAZEBO_RENDER_ENGINE_SERVER="${GAZEBO_RENDER_ENGINE_SERVER:-ogre}"
DRY_RUN="${DRY_RUN:-0}"
GAZEBO_GUI_REVIEW="${GAZEBO_GUI_REVIEW:-0}"
GAZEBO_GUI_START_PAUSED="${GAZEBO_GUI_START_PAUSED:-1}"
GAZEBO_GUI_VERBOSE="${GAZEBO_GUI_VERBOSE:-2}"
if [[ -z "${GAZEBO_GUI_TRAIL_MARKER+x}" ]]; then
  GAZEBO_GUI_TRAIL_MARKER="0"
fi
if [[ -z "${GAZEBO_GUI_CAMERA_FOLLOW+x}" ]]; then
  if [[ "${GAZEBO_GUI_REVIEW}" == "1" ]]; then
    GAZEBO_GUI_CAMERA_FOLLOW="1"
  else
    GAZEBO_GUI_CAMERA_FOLLOW="0"
  fi
fi
GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M="${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M:--0.233}"
GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M="${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M:--0.933}"
GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M="${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M:-0.467}"
GAZEBO_GUI_CAMERA_FOLLOW_MIN_DIST_M="${GAZEBO_GUI_CAMERA_FOLLOW_MIN_DIST_M:-0.35}"
GAZEBO_GUI_CAMERA_FOLLOW_MAX_DIST_M="${GAZEBO_GUI_CAMERA_FOLLOW_MAX_DIST_M:-2.0}"
GAZEBO_GUI_CAMERA_FOLLOW_REPEAT="${GAZEBO_GUI_CAMERA_FOLLOW_REPEAT:-120}"
GAZEBO_GUI_CAMERA_FOLLOW_INTERVAL_S="${GAZEBO_GUI_CAMERA_FOLLOW_INTERVAL_S:-0.4}"
GAZEBO_GUI_CAMERA_FOLLOW_START_DELAY_S="${GAZEBO_GUI_CAMERA_FOLLOW_START_DELAY_S:-0.5}"
if [[ -z "${GAZEBO_GUI_CAMERA_ORBIT+x}" ]]; then
  if [[ "${GAZEBO_GUI_REVIEW}" == "1" && "${GAZEBO_GUI_CAMERA_FOLLOW}" == "1" ]]; then
    GAZEBO_GUI_CAMERA_ORBIT="1"
  else
    GAZEBO_GUI_CAMERA_ORBIT="0"
  fi
fi
GAZEBO_GUI_CAMERA_ORBIT_SCRIPT="${GAZEBO_GUI_CAMERA_ORBIT_SCRIPT:-Scripts/gazebo/orbit_gazebo_camera_follow.py}"
GAZEBO_GUI_CAMERA_ORBIT_AZIMUTH_STEP_DEG="${GAZEBO_GUI_CAMERA_ORBIT_AZIMUTH_STEP_DEG:-8.0}"
GAZEBO_GUI_CAMERA_ORBIT_ELEVATION_STEP_DEG="${GAZEBO_GUI_CAMERA_ORBIT_ELEVATION_STEP_DEG:-5.0}"
if [[ -z "${GAZEBO_RVIZ_REVIEW_PATHS+x}" ]]; then
  if [[ "${GAZEBO_GUI_REVIEW}" == "1" ]]; then
    GAZEBO_RVIZ_REVIEW_PATHS="1"
  else
    GAZEBO_RVIZ_REVIEW_PATHS="0"
  fi
fi
REFERENCE_SYNC_TO_GAZEBO_TRUTH="${REFERENCE_SYNC_TO_GAZEBO_TRUTH_OVERRIDE:-1}"
REFERENCE_TRUTH_SYNC_EPOCH_S="${REFERENCE_TRUTH_SYNC_EPOCH_S_OVERRIDE:-0.0}"
RVIZ_REVIEW_PATHS_SCRIPT="${RVIZ_REVIEW_PATHS_SCRIPT:-Scripts/ros/publish_gazebo_review_paths.py}"
ROS_REVIEW_ACTUAL_PATH_TOPIC="${ROS_REVIEW_ACTUAL_PATH_TOPIC:-/mosim/review/actual_path}"
ROS_REVIEW_REFERENCE_PATH_TOPIC="${ROS_REVIEW_REFERENCE_PATH_TOPIC:-/mosim/review/reference_path}"
RVIZ_REVIEW_PATH_MAX_POINTS="${RVIZ_REVIEW_PATH_MAX_POINTS:-5000}"
GAZEBO_GUI_TRAIL_PUBLISH_RATE_HZ="${GAZEBO_GUI_TRAIL_PUBLISH_RATE_HZ:-1.0}"
GAZEBO_GUI_TRAIL_MAX_POINTS="${GAZEBO_GUI_TRAIL_MAX_POINTS:-5000}"
GAZEBO_GUI_TRAIL_PUBLISH_TIMEOUT_S="${GAZEBO_GUI_TRAIL_PUBLISH_TIMEOUT_S:-4.0}"
GAZEBO_GUI_TRAIL_LINE_SCALE_M="${GAZEBO_GUI_TRAIL_LINE_SCALE_M:-0.025}"
GAZEBO_GUI_TRAIL_ENTITY_SEGMENTS="${GAZEBO_GUI_TRAIL_ENTITY_SEGMENTS:-0}"
GAZEBO_GUI_TRAIL_ENTITY_RADIUS_M="${GAZEBO_GUI_TRAIL_ENTITY_RADIUS_M:-0.018}"
GAZEBO_GUI_TRAIL_ENTITY_MIN_DISTANCE_M="${GAZEBO_GUI_TRAIL_ENTITY_MIN_DISTANCE_M:-0.12}"
GAZEBO_GUI_TRAIL_ENTITY_SEGMENTS_PER_PUBLISH="${GAZEBO_GUI_TRAIL_ENTITY_SEGMENTS_PER_PUBLISH:-12}"
GUI_CONFIG="${GUI_CONFIG:-}"
ENABLE_SAME_RUN_MAP_REVIEW="${ENABLE_SAME_RUN_MAP_REVIEW:-0}"
MAP_REVIEW_DURATION_SECONDS_OVERRIDE="${MAP_REVIEW_DURATION_SECONDS_OVERRIDE:-}"
STATIC_OBSTACLE_SOURCE="${STATIC_OBSTACLE_SOURCE_OVERRIDE:-scenario}"
WORLD_CYLINDER_OBSTACLE_RADIUS_M="${WORLD_CYLINDER_OBSTACLE_RADIUS_M_OVERRIDE:-0.35}"

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_DIR}" "${ROS_LOG_DIR}"
export ROS_LOG_DIR

json_array_from_lines() {
  python3 -c 'import json,sys; print(json.dumps([line.rstrip("\n") for line in sys.stdin if line.rstrip("\n")], ensure_ascii=False))'
}

command_path() {
  local name="$1"
  if command -v "${name}" >/dev/null 2>&1; then
    command -v "${name}"
  else
    true
  fi
}

ros_pkg_prefix() {
  local name="$1"
  if command -v ros2 >/dev/null 2>&1; then
    ros2 pkg prefix "${name}" 2>/dev/null || true
  fi
}

ros_pkg_has_executable() {
  local package="$1"
  local executable="$2"
  if command -v ros2 >/dev/null 2>&1; then
    ros2 pkg executables "${package}" 2>/dev/null | awk '{print $2}' | grep -Fx "${executable}" >/dev/null 2>&1
  else
    return 1
  fi
}

topic_key() {
  local topic="$1"
  topic="${topic#/}"
  topic="${topic//\//_}"
  printf '%s' "${topic}" | sed -E 's/[^A-Za-z0-9_]+/_/g'
}

write_rc() {
  local path="$1"
  local code="$2"
  printf '%s\n' "${code}" > "${path}"
}

terminate_process_tree() {
  local pid="$1"
  local grace_seconds="${2:-2}"
  if [[ -z "${pid}" ]] || ! kill -0 "${pid}" >/dev/null 2>&1; then
    return 0
  fi
  local child
  for child in $(pgrep -P "${pid}" 2>/dev/null || true); do
    terminate_process_tree "${child}" "${grace_seconds}"
  done
  kill "${pid}" >/dev/null 2>&1 || true
  local waited=0
  while kill -0 "${pid}" >/dev/null 2>&1 && [[ "${waited}" -lt "${grace_seconds}" ]]; do
    sleep 1
    waited=$((waited + 1))
  done
  if kill -0 "${pid}" >/dev/null 2>&1; then
    kill -KILL "${pid}" >/dev/null 2>&1 || true
  fi
  wait "${pid}" 2>/dev/null || true
}

wait_for_gazebo_truth_sample() {
  local timeout_seconds="$1"
  local deadline
  deadline="$(python3 - <<PY
import time
print(time.monotonic() + float("${timeout_seconds}"))
PY
)"
  while python3 - <<PY
import sys, time
sys.exit(0 if time.monotonic() < float("${deadline}") else 1)
PY
  do
    if timeout 8s ign topic -e -t "${GAZEBO_TRUTH_TOPIC}" -n 1 \
      > "${RESULT_DIR}/gazebo_truth_topic_ready_sample.txt" \
      2> "${RESULT_DIR}/gazebo_truth_topic_ready_sample.stderr.log"; then
      if [[ -s "${RESULT_DIR}/gazebo_truth_topic_ready_sample.txt" ]]; then
        return 0
      fi
    fi
    sleep 1
  done
  return 1
}

scenario_json="$(python3 - <<PY
import json
from pathlib import Path
import yaml
data = yaml.safe_load(Path("${SCENARIO}").read_text(encoding="utf-8"))
print(json.dumps(data, ensure_ascii=False))
PY
)"

yaml_get() {
  python3 - "$1" <<PY
import json
import sys
data = json.loads('''${scenario_json}''')
node = data
for part in sys.argv[1].split("."):
    node = node[part]
print(node)
PY
}

yaml_get_or_default() {
  python3 - "$1" "$2" <<PY
import json
import sys
data = json.loads('''${scenario_json}''')
node = data
for part in sys.argv[1].split("."):
    if isinstance(node, dict) and part in node:
        node = node[part]
    else:
        print(sys.argv[2])
        raise SystemExit(0)
print(node)
PY
}

WORLD="$(yaml_get gazebo.world)"
WORLD="${WORLD_OVERRIDE:-${WORLD}}"
MOSIM_MSGS_PACKAGE="$(yaml_get ros2.controller_adapter.message_package)"
MOSIM_SETPOINT_ADAPTER_PACKAGE="Scripts/ros/mosim_setpoint_adapter"
CONTROLLER_NODE_SCRIPT="$(yaml_get ros2.controller_adapter.node_script)"
CONTROLLER_FIXTURE_SCRIPT="$(yaml_get ros2.controller_adapter.fixture_publisher_script)"
LOCAL_MAP_SCRIPT="$(yaml_get ros2.local_map_adapter.script)"
MAP_REVIEW_RECORDER_SCRIPT="$(yaml_get_or_default ros2.map_review_capture.script Scripts/ros/record_gazebo_ros2_map_review.py)"
REFERENCE_SCRIPT="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.reference_script)"
TRACKER_SCRIPT="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker_script)"
EVAL_SCRIPT="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.eval_script)"
REFERENCE_SCRIPT="${REFERENCE_SCRIPT_OVERRIDE:-${REFERENCE_SCRIPT}}"
TRACKER_SCRIPT="${TRACKER_SCRIPT_OVERRIDE:-${TRACKER_SCRIPT}}"
EVAL_SCRIPT="${EVAL_SCRIPT_OVERRIDE:-${EVAL_SCRIPT}}"
GAZEBO_TRUTH_RECORDER_SCRIPT="$(yaml_get ros2.gazebo_truth_pose.recorder_script)"
TRAIL_MARKER_SCRIPT="${TRAIL_MARKER_SCRIPT:-Scripts/gazebo/publish_gazebo_truth_trail_marker.py}"
CAMERA_FOLLOW_SCRIPT="${CAMERA_FOLLOW_SCRIPT:-Scripts/gazebo/set_gazebo_camera_follow.py}"
GAZEBO_TRUTH_TOPIC="$(yaml_get ros2.gazebo_truth_pose.topic)"
GAZEBO_TRUTH_TOPIC="${GAZEBO_TRUTH_TOPIC_OVERRIDE:-${GAZEBO_TRUTH_TOPIC}}"
GAZEBO_TRUTH_MODEL_NAME="$(yaml_get ros2.gazebo_truth_pose.model_name)"
GAZEBO_TRUTH_FRAME_ID="$(yaml_get ros2.gazebo_truth_pose.frame_id)"
GAZEBO_WORLD_NAME="$(GAZEBO_TRUTH_TOPIC_FOR_WORLD_NAME="${GAZEBO_TRUTH_TOPIC}" python3 - <<PY
import os
import re
topic=os.environ.get("GAZEBO_TRUTH_TOPIC_FOR_WORLD_NAME", "/world/yunzong_planning_test_sunray150_assembled/dynamic_pose/info")
match=re.match(r"^/world/([^/]+)/", topic)
print(match.group(1) if match else "yunzong_planning_test_sunray150_assembled")
PY
)"
GAZEBO_WORLD_NAME="${WORLD_NAME_OVERRIDE:-${GAZEBO_WORLD_NAME}}"
ROS_CONTROLLER_OUTPUT_TOPIC="$(yaml_get ros2.controller_adapter.input_topic)"
ROS_ACTUATOR_TOPIC="$(yaml_get ros2.controller_adapter.ros_actuator_topic)"
GZ_ACTUATOR_TOPIC="$(yaml_get ros2.controller_adapter.gz_actuator_topic)"
ROS_IMU_TOPIC="$(yaml_get ros2.topics.imu)"
ROS_LIDAR_POINTS_TOPIC="$(yaml_get ros2.topics.lidar_points)"
ROS_LOCAL_VOXEL_TOPIC="$(yaml_get ros2.topics.local_occupancy_voxels)"
ROS_LOCAL_GRID_TOPIC="$(yaml_get ros2.topics.local_occupancy_grid)"
ROS_REFERENCE_POSITION_CMD_TOPIC="$(yaml_get ros2.topics.reference_position_cmd)"
ROS_MOSIM_PLANNER_POSITION_CMD_TOPIC="$(yaml_get ros2.topics.mosim_planner_position_cmd)"
ROS_PLANNER_SETPOINT_TOPIC="$(yaml_get ros2.topics.planner_setpoint)"
ROS_PLANNER_SETPOINT_STATUS_TOPIC="$(yaml_get ros2.topics.planner_setpoint_adapter_status)"
ROS_GAZEBO_TRUTH_POSE_TOPIC="${ROS_GAZEBO_TRUTH_POSE_TOPIC:-/mosim/gazebo/truth_pose}"
MAP_REVIEW_OUTPUT_DIR="$(yaml_get_or_default ros2.map_review_capture.output_dir map_review)"
MAP_REVIEW_DURATION_SECONDS="$(yaml_get_or_default ros2.map_review_capture.duration_seconds 8)"
MAP_REVIEW_DURATION_SECONDS="${MAP_REVIEW_DURATION_SECONDS_OVERRIDE:-${MAP_REVIEW_DURATION_SECONDS}}"
OUTPUT_JSON="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.output_json)"
REFERENCE_REPORT_JSON="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.reference_report_json)"
REFERENCE_TRACE_JSONL="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.reference_trace_jsonl)"
TRACKER_REPORT_JSON="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker_report_json)"
TRACKER_TRACE_JSONL="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker_trace_jsonl)"
FIGURE_FRAME_ID="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.frame_id)"
FIGURE_RATE_HZ="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.rate_hz)"
FIGURE_DURATION_S="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.duration_s)"
FIGURE_PERIOD_S="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.period_s)"
FIGURE_X_AMP="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.x_amplitude_m)"
FIGURE_Y_AMP="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.y_amplitude_m)"
FIGURE_X_OFFSET="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.x_offset_m 0.0)"
FIGURE_Y_OFFSET="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.y_offset_m 0.0)"
FIGURE_ALTITUDE="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.altitude_m)"
FIGURE_START_DELAY_S="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.start_delay_s)"
FIGURE_TAKEOFF_S="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.takeoff_s 0.0)"
FIGURE_HOLD_S="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.hold_s 0.0)"
FIGURE_POST_FIGURE8_HOLD_S="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.post_figure8_hold_s 0.0)"
FIGURE_LAND_S="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.land_s 0.0)"
FIGURE_FINAL_HOLD_S="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.final_hold_s 0.0)"
FIGURE_GROUND_ALTITUDE="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.ground_altitude_m 0.05)"
FIGURE_CENTER_REVISIT_RADIUS_M="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.trajectory.center_revisit_radius_m 0.02)"
TRACKER_DURATION_S="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.duration_s)"
TRACKER_CONFIG_TAKEOFF_XY_ENABLE_ALTITUDE_M="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.takeoff_xy_enable_altitude_m 0.9)"
TRACKER_CONFIG_TAKEOFF_STABLE_Z_ERROR_M="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.takeoff_stable_z_error_m 0.25)"
TRACKER_CONFIG_TAKEOFF_REFERENCE_READY_Z_M="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.takeoff_reference_ready_z_m 0.9)"
TRACKER_CONFIG_TAKEOFF_STABLE_MAX_VZ_MPS="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.takeoff_stable_max_vz_mps 0.35)"
TRACKER_CONFIG_TAKEOFF_STABLE_S="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.takeoff_stable_s 0.8)"
TRACKER_CONFIG_RECOVERY_XY_BRAKE_SCALE="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.recovery_xy_brake_scale 0.35)"
TRACKER_CONFIG_RECOVERY_RESET_ALTITUDE_M="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.recovery_reset_altitude_m 0.35)"
TRACKER_CONFIG_XY_ERROR_LIMIT_M="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.xy_error_limit_m 0.8)"
TRACKER_CONFIG_XY_VELOCITY_ERROR_LIMIT_MPS="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.xy_velocity_error_limit_mps 0.5)"
TRACKER_CONFIG_INTEGRAL_LIMIT_M_S="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.integral_limit_m_s 1.0)"
TRACKER_CONFIG_XY_CONTROL_SIGN="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.xy_control_sign -1.0)"
TRACKER_CONFIG_ROLL_CONTROL_SIGN="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.roll_control_sign "")"
TRACKER_CONFIG_PITCH_CONTROL_SIGN="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.pitch_control_sign "")"
TRACKER_CONFIG_GROUND_MOTOR_COMMAND="$(yaml_get_or_default ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.ground_motor_command 0.0)"
if [[ -n "${FIGURE_DURATION_S_OVERRIDE:-}" ]]; then FIGURE_DURATION_S="${FIGURE_DURATION_S_OVERRIDE}"; fi
if [[ -n "${FIGURE_PERIOD_S_OVERRIDE:-}" ]]; then FIGURE_PERIOD_S="${FIGURE_PERIOD_S_OVERRIDE}"; fi
if [[ -n "${FIGURE_X_AMP_OVERRIDE:-}" ]]; then FIGURE_X_AMP="${FIGURE_X_AMP_OVERRIDE}"; fi
if [[ -n "${FIGURE_Y_AMP_OVERRIDE:-}" ]]; then FIGURE_Y_AMP="${FIGURE_Y_AMP_OVERRIDE}"; fi
if [[ -n "${FIGURE_X_OFFSET_OVERRIDE:-}" ]]; then FIGURE_X_OFFSET="${FIGURE_X_OFFSET_OVERRIDE}"; fi
if [[ -n "${FIGURE_Y_OFFSET_OVERRIDE:-}" ]]; then FIGURE_Y_OFFSET="${FIGURE_Y_OFFSET_OVERRIDE}"; fi
if [[ -n "${FIGURE_ALTITUDE_M_OVERRIDE:-}" ]]; then FIGURE_ALTITUDE="${FIGURE_ALTITUDE_M_OVERRIDE}"; fi
if [[ -n "${FIGURE_ALTITUDE_OVERRIDE:-}" ]]; then FIGURE_ALTITUDE="${FIGURE_ALTITUDE_OVERRIDE}"; fi
if [[ -n "${FIGURE_START_DELAY_S_OVERRIDE:-}" ]]; then FIGURE_START_DELAY_S="${FIGURE_START_DELAY_S_OVERRIDE}"; fi
if [[ -n "${FIGURE_TAKEOFF_S_OVERRIDE:-}" ]]; then FIGURE_TAKEOFF_S="${FIGURE_TAKEOFF_S_OVERRIDE}"; fi
if [[ -n "${FIGURE_HOLD_S_OVERRIDE:-}" ]]; then FIGURE_HOLD_S="${FIGURE_HOLD_S_OVERRIDE}"; fi
if [[ -n "${FIGURE_POST_FIGURE8_HOLD_S_OVERRIDE:-}" ]]; then FIGURE_POST_FIGURE8_HOLD_S="${FIGURE_POST_FIGURE8_HOLD_S_OVERRIDE}"; fi
if [[ -n "${FIGURE_LAND_S_OVERRIDE:-}" ]]; then FIGURE_LAND_S="${FIGURE_LAND_S_OVERRIDE}"; fi
if [[ -n "${FIGURE_FINAL_HOLD_S_OVERRIDE:-}" ]]; then FIGURE_FINAL_HOLD_S="${FIGURE_FINAL_HOLD_S_OVERRIDE}"; fi
if [[ -n "${FIGURE_GROUND_ALTITUDE_M_OVERRIDE:-}" ]]; then FIGURE_GROUND_ALTITUDE="${FIGURE_GROUND_ALTITUDE_M_OVERRIDE}"; fi
if [[ -n "${FIGURE_GROUND_ALTITUDE_OVERRIDE:-}" ]]; then FIGURE_GROUND_ALTITUDE="${FIGURE_GROUND_ALTITUDE_OVERRIDE}"; fi
if [[ -n "${FIGURE_CENTER_REVISIT_RADIUS_M_OVERRIDE:-}" ]]; then FIGURE_CENTER_REVISIT_RADIUS_M="${FIGURE_CENTER_REVISIT_RADIUS_M_OVERRIDE}"; fi
if [[ -n "${TRACKER_DURATION_S_OVERRIDE:-}" ]]; then TRACKER_DURATION_S="${TRACKER_DURATION_S_OVERRIDE}"; fi
TRACKER_SETPOINT_TIMEOUT_S="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.setpoint_timeout_s)"
TRACKER_SETPOINT_TIMEOUT_S="${TRACKER_SETPOINT_TIMEOUT_S_OVERRIDE:-${TRACKER_SETPOINT_TIMEOUT_S}}"
TRACKER_MAX_PUBLISH_HZ="$(yaml_get ros2.single_uav_figure8_static_obstacle_pre_acceptance.tracker.max_publish_hz)"
TRACKER_SYNC_TRUTH_TO_WALL_TIME="${TRACKER_SYNC_TRUTH_TO_WALL_TIME_OVERRIDE:-1}"
TRACKER_TRUTH_WALL_TIME_FACTOR="${TRACKER_TRUTH_WALL_TIME_FACTOR_OVERRIDE:-1.0}"
TRACKER_TRUTH_INPUT_MODE="${TRACKER_TRUTH_INPUT_MODE_OVERRIDE:-stream}"
TRACKER_POLL_SAMPLE_TIMEOUT_S="${TRACKER_POLL_SAMPLE_TIMEOUT_S_OVERRIDE:-5.0}"
TRACKER_POLL_SLEEP_S="${TRACKER_POLL_SLEEP_S_OVERRIDE:-0.04}"
TRACKER_HOLD_LAST_SETPOINT_WHEN_TRUTH_BUFFERED="${TRACKER_HOLD_LAST_SETPOINT_WHEN_TRUTH_BUFFERED_OVERRIDE:-0}"
INDEPENDENT_TRUTH_RECORDER="${INDEPENDENT_TRUTH_RECORDER_OVERRIDE:-1}"
TRACKER_CONFIG_NODE="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
ros2=data.get("ros2", {})
print("gazebo_truth_position_controller" if "gazebo_truth_position_controller" in ros2 else "gazebo_truth_planner_setpoint_tracker")
PY
)"
TRACKER_HOVER_COMMAND="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.hover_command)"
TRACKER_KP_X="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.kp_x)"
TRACKER_KD_X="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.kd_x)"
TRACKER_KA_X="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.ka_x)"
TRACKER_KP_Y="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.kp_y)"
TRACKER_KD_Y="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.kd_y)"
TRACKER_KA_Y="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.ka_y)"
TRACKER_KP_Z="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.kp_z)"
TRACKER_KD_Z="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.kd_z)"
TRACKER_KI_Z="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.ki_z)"
TRACKER_KP_ROLL="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.kp_roll)"
TRACKER_KD_ROLL="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.kd_roll)"
TRACKER_KP_PITCH="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.kp_pitch)"
TRACKER_KD_PITCH="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.kd_pitch)"
TRACKER_KP_YAW="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.kp_yaw)"
TRACKER_KD_YAW="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.kd_yaw)"
TRACKER_ATTITUDE_COMMAND_LIMIT="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.attitude_command_limit)"
TRACKER_COMMAND_MIN="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.command_min)"
TRACKER_COMMAND_MAX="$(yaml_get ros2.${TRACKER_CONFIG_NODE}.command_max)"
TRACKER_HOVER_COMMAND="${TRACKER_HOVER_COMMAND_OVERRIDE:-${TRACKER_HOVER_COMMAND}}"
TRACKER_KP_X="${TRACKER_KP_X_OVERRIDE:-${TRACKER_KP_X}}"
TRACKER_KD_X="${TRACKER_KD_X_OVERRIDE:-${TRACKER_KD_X}}"
TRACKER_KA_X="${TRACKER_KA_X_OVERRIDE:-${TRACKER_KA_X}}"
TRACKER_KP_Y="${TRACKER_KP_Y_OVERRIDE:-${TRACKER_KP_Y}}"
TRACKER_KD_Y="${TRACKER_KD_Y_OVERRIDE:-${TRACKER_KD_Y}}"
TRACKER_KA_Y="${TRACKER_KA_Y_OVERRIDE:-${TRACKER_KA_Y}}"
TRACKER_KP_Z="${TRACKER_KP_Z_OVERRIDE:-${TRACKER_KP_Z}}"
TRACKER_KD_Z="${TRACKER_KD_Z_OVERRIDE:-${TRACKER_KD_Z}}"
TRACKER_KI_Z="${TRACKER_KI_Z_OVERRIDE:-${TRACKER_KI_Z}}"
TRACKER_KP_ROLL="${TRACKER_KP_ROLL_OVERRIDE:-${TRACKER_KP_ROLL}}"
TRACKER_KD_ROLL="${TRACKER_KD_ROLL_OVERRIDE:-${TRACKER_KD_ROLL}}"
TRACKER_KP_PITCH="${TRACKER_KP_PITCH_OVERRIDE:-${TRACKER_KP_PITCH}}"
TRACKER_KD_PITCH="${TRACKER_KD_PITCH_OVERRIDE:-${TRACKER_KD_PITCH}}"
TRACKER_ATTITUDE_COMMAND_LIMIT="${TRACKER_ATTITUDE_COMMAND_LIMIT_OVERRIDE:-${TRACKER_ATTITUDE_COMMAND_LIMIT}}"
TRACKER_COMMAND_MIN="${TRACKER_COMMAND_MIN_OVERRIDE:-${TRACKER_COMMAND_MIN}}"
TRACKER_COMMAND_MAX="${TRACKER_COMMAND_MAX_OVERRIDE:-${TRACKER_COMMAND_MAX}}"
TRACKER_GROUND_MOTOR_COMMAND="${TRACKER_GROUND_MOTOR_COMMAND_OVERRIDE:-${TRACKER_CONFIG_GROUND_MOTOR_COMMAND}}"
TRACKER_XY_CONTROL_SIGN="${TRACKER_XY_CONTROL_SIGN_OVERRIDE:-${TRACKER_CONFIG_XY_CONTROL_SIGN}}"
TRACKER_ROLL_CONTROL_SIGN="${TRACKER_ROLL_CONTROL_SIGN_OVERRIDE:-${TRACKER_CONFIG_ROLL_CONTROL_SIGN}}"
TRACKER_PITCH_CONTROL_SIGN="${TRACKER_PITCH_CONTROL_SIGN_OVERRIDE:-${TRACKER_CONFIG_PITCH_CONTROL_SIGN}}"
TRACKER_TAKEOFF_XY_ENABLE_ALTITUDE_M="${TRACKER_TAKEOFF_XY_ENABLE_ALTITUDE_M_OVERRIDE:-${TRACKER_CONFIG_TAKEOFF_XY_ENABLE_ALTITUDE_M}}"
TRACKER_TAKEOFF_STABLE_Z_ERROR_M="${TRACKER_TAKEOFF_STABLE_Z_ERROR_M_OVERRIDE:-${TRACKER_CONFIG_TAKEOFF_STABLE_Z_ERROR_M}}"
TRACKER_TAKEOFF_REFERENCE_READY_Z_M="${TRACKER_TAKEOFF_REFERENCE_READY_Z_M_OVERRIDE:-${TRACKER_CONFIG_TAKEOFF_REFERENCE_READY_Z_M}}"
TRACKER_TAKEOFF_STABLE_MAX_VZ_MPS="${TRACKER_TAKEOFF_STABLE_MAX_VZ_MPS_OVERRIDE:-${TRACKER_CONFIG_TAKEOFF_STABLE_MAX_VZ_MPS}}"
TRACKER_TAKEOFF_STABLE_S="${TRACKER_TAKEOFF_STABLE_S_OVERRIDE:-${TRACKER_CONFIG_TAKEOFF_STABLE_S}}"
TRACKER_RECOVERY_XY_BRAKE_SCALE="${TRACKER_RECOVERY_XY_BRAKE_SCALE_OVERRIDE:-${TRACKER_CONFIG_RECOVERY_XY_BRAKE_SCALE}}"
TRACKER_RECOVERY_RESET_ALTITUDE_M="${TRACKER_RECOVERY_RESET_ALTITUDE_M_OVERRIDE:-${TRACKER_CONFIG_RECOVERY_RESET_ALTITUDE_M}}"
TRACKER_XY_ERROR_LIMIT_M="${TRACKER_XY_ERROR_LIMIT_M_OVERRIDE:-${TRACKER_CONFIG_XY_ERROR_LIMIT_M}}"
TRACKER_XY_VELOCITY_ERROR_LIMIT_MPS="${TRACKER_XY_VELOCITY_ERROR_LIMIT_MPS_OVERRIDE:-${TRACKER_CONFIG_XY_VELOCITY_ERROR_LIMIT_MPS}}"
TRACKER_INTEGRAL_LIMIT_M_S="${TRACKER_INTEGRAL_LIMIT_M_S_OVERRIDE:-${TRACKER_CONFIG_INTEGRAL_LIMIT_M_S}}"

readarray -t OBSTACLE_ARGS < <(python3 - <<PY
import json
import re
import sys
from pathlib import Path
data=json.loads('''${scenario_json}''')
source = "${STATIC_OBSTACLE_SOURCE}"
items = []
if source == "scenario":
    items=data["ros2"]["single_uav_figure8_static_obstacle_pre_acceptance"].get("static_obstacles_xy_radius", [])
elif source == "world_cylinders":
    world_path = Path("${WORLD}")
    if not world_path.is_absolute():
        world_path = Path("${PROJECT_ROOT}") / world_path
    radius = float("${WORLD_CYLINDER_OBSTACLE_RADIUS_M}")
    import xml.etree.ElementTree as ET
    root = ET.parse(world_path).getroot()
    for include in root.findall(".//include"):
        uri = (include.findtext("uri") or "").strip()
        if "cylinder" not in uri:
            continue
        pose_text = (include.findtext("pose") or "").strip()
        parts = pose_text.split()
        if len(parts) >= 2:
            items.append([float(parts[0]), float(parts[1]), radius])
else:
    print(f"unsupported STATIC_OBSTACLE_SOURCE={source}", file=sys.stderr)
    raise SystemExit(2)
for item in items:
    print(f"--obstacle={float(item[0])},{float(item[1])},{float(item[2])}")
PY
)

readarray -t EVAL_THRESHOLD_ARGS < <(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
t=data["ros2"]["single_uav_figure8_static_obstacle_pre_acceptance"].get("evaluation_thresholds", {})
mapping = {
  "min_reference_samples": "--min-reference-samples",
  "min_truth_samples": "--min-truth-samples",
  "min_tracker_samples": "--min-tracker-samples",
  "min_xy_track_samples": "--min-xy-track-samples",
  "min_adapter_samples": "--min-adapter-samples",
  "min_duration_s": "--min-duration-s",
  "max_xy_rmse_m": "--max-xy-rmse-m",
  "max_xy_error_m": "--max-xy-error-m",
  "max_z_error_m": "--max-z-error-m",
  "max_xy_track_rmse_m": "--max-xy-track-rmse-m",
  "max_xy_track_error_m": "--max-xy-track-error-m",
  "min_figure8_phase_samples": "--min-figure8-phase-samples",
  "max_figure8_phase_xy_rmse_m": "--max-figure8-phase-xy-rmse-m",
  "max_figure8_phase_xy_error_m": "--max-figure8-phase-xy-error-m",
  "max_figure8_phase_z_error_m": "--max-figure8-phase-z-error-m",
  "expected_figure8_span_x_m": "--expected-figure8-span-x-m",
  "expected_figure8_span_y_m": "--expected-figure8-span-y-m",
  "min_truth_span_x_m": "--min-truth-span-x-m",
  "min_truth_span_y_m": "--min-truth-span-y-m",
  "min_truth_path_length_ratio": "--min-truth-path-length-ratio",
  "min_lobe_fraction": "--min-lobe-fraction",
  "min_center_crossings_x": "--min-center-crossings-x",
  "min_figure8_trajectory_time_span_s": "--min-figure8-trajectory-time-span-s",
  "min_center_revisit_entries": "--min-center-revisit-entries",
  "max_final_altitude_m": "--max-final-altitude-m",
  "max_landing_window_altitude_m": "--max-landing-window-altitude-m",
  "max_landing_window_xy_displacement_m": "--max-landing-window-xy-displacement-m",
  "min_reference_obstacle_clearance_m": "--min-reference-obstacle-clearance-m",
  "min_truth_obstacle_clearance_m": "--min-truth-obstacle-clearance-m",
}
for key, flag in mapping.items():
    if key in t:
        print(f"{flag}={t[key]}")
PY
)

LOCAL_MAP_MAP_FRAME="$(yaml_get_or_default ros2.local_map_adapter.map_frame map)"
LOCAL_MAP_EXPECTED_INPUT_FRAME="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
adapter=data["ros2"]["local_map_adapter"]
print(adapter.get("expected_input_frame", adapter.get("sensor_frame", adapter.get("map_frame", "map"))))
PY
)"
LOCAL_MAP_FRAME_ARGS="$(python3 - <<PY
import json, shlex
data=json.loads('''${scenario_json}''')
adapter=data["ros2"]["local_map_adapter"]
z_bounds = adapter.get("z_bounds_m", [-1.0, 5.0])
self_filter_z_bounds = adapter.get("self_filter_z_bounds_m", [None, None])
args = [
    "--map-frame", adapter.get("map_frame", "map"),
    "--voxel-size-m", adapter.get("voxel_size_m", 0.2),
    "--grid-resolution-m", adapter.get("grid_resolution_m", adapter.get("voxel_size_m", 0.2)),
    "--local-radius-m", adapter.get("local_radius_m", 12.0),
    "--z-min-m", z_bounds[0],
    "--z-max-m", z_bounds[1],
    "--input-frame-policy", adapter.get("input_frame_policy", "require_input_frame_equals_map_frame"),
    "--expected-input-frame", adapter.get("expected_input_frame", adapter.get("map_frame", "map")),
    "--tf-lookup-timeout-s", adapter.get("tf_lookup_timeout_s", 0.2),
    "--local-map-center-source", adapter.get("local_map_center_source", "map_origin"),
]
if adapter.get("ground_min_z_m") is not None:
    args += ["--ground-min-z-m", adapter.get("ground_min_z_m")]
if adapter.get("self_filter_radius_xy_m", 0.0):
    args += ["--self-filter-radius-xy-m", adapter.get("self_filter_radius_xy_m", 0.0)]
if self_filter_z_bounds and self_filter_z_bounds[0] is not None:
    args += ["--self-filter-z-min-m", self_filter_z_bounds[0]]
if self_filter_z_bounds and len(self_filter_z_bounds) > 1 and self_filter_z_bounds[1] is not None:
    args += ["--self-filter-z-max-m", self_filter_z_bounds[1]]
print(" ".join(shlex.quote(str(item)) for item in args))
PY
)"

GAZEBO_RESOURCE_PATHS="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
paths=data.get("gazebo", {}).get("resource_paths", ["Config/gazebo/models"])
if isinstance(paths, str):
    paths=[paths]
print(":".join("${PROJECT_ROOT}/" + str(path).strip("/") for path in paths if str(path).strip()))
PY
)"
if declare -F mosim_gazebo_apply_resource_paths >/dev/null 2>&1; then
  mosim_gazebo_apply_resource_paths "${GAZEBO_RESOURCE_PATHS}"
else
  export GZ_SIM_RESOURCE_PATH="${GAZEBO_RESOURCE_PATHS}"
  export IGN_GAZEBO_RESOURCE_PATH="${GAZEBO_RESOURCE_PATHS}"
fi

RUN_MANIFEST="${RESULT_DIR}/RUN_MANIFEST.json"
RUNTIME_STATUS_JSON="${RESULT_DIR}/RUNTIME_STATUS.json"
PREFLIGHT_JSON="${RESULT_DIR}/PREFLIGHT.json"
BLOCKER="${RESULT_DIR}/BLOCKER.json"
GAZEBO_TRUTH_POSE_JSONL="${RESULT_DIR}/gazebo_truth_pose.jsonl"
GAZEBO_TRUTH_POSE_SUMMARY_JSON="${RESULT_DIR}/GAZEBO_TRUTH_POSE_RECORDING.json"
REFERENCE_REPORT_PATH="${RESULT_DIR}/${REFERENCE_REPORT_JSON}"
REFERENCE_TRACE_PATH="${RESULT_DIR}/${REFERENCE_TRACE_JSONL}"
TRACKER_REPORT_PATH="${RESULT_DIR}/${TRACKER_REPORT_JSON}"
TRACKER_TRACE_PATH="${RESULT_DIR}/${TRACKER_TRACE_JSONL}"
EVAL_JSON="${RESULT_DIR}/${OUTPUT_JSON}"

missing_files=()
for path in "${SCENARIO}" "${WORLD}" "${CONTROLLER_NODE_SCRIPT}" "${CONTROLLER_FIXTURE_SCRIPT}" "${REFERENCE_SCRIPT}" "${TRACKER_SCRIPT}" "${EVAL_SCRIPT}" "${GAZEBO_TRUTH_RECORDER_SCRIPT}"; do
  [[ -f "${path}" ]] || missing_files+=("${path}")
done
if [[ "${ENABLE_SAME_RUN_MAP_REVIEW}" == "1" ]]; then
  [[ -f "${LOCAL_MAP_SCRIPT}" ]] || missing_files+=("${LOCAL_MAP_SCRIPT}")
  [[ -f "${MAP_REVIEW_RECORDER_SCRIPT}" ]] || missing_files+=("${MAP_REVIEW_RECORDER_SCRIPT}")
fi
if [[ "${GAZEBO_GUI_REVIEW}" == "1" && "${GAZEBO_GUI_TRAIL_MARKER}" == "1" ]]; then
  [[ -f "${TRAIL_MARKER_SCRIPT}" ]] || missing_files+=("${TRAIL_MARKER_SCRIPT}")
fi
if [[ "${GAZEBO_RVIZ_REVIEW_PATHS}" == "1" ]]; then
  [[ -f "${RVIZ_REVIEW_PATHS_SCRIPT}" ]] || missing_files+=("${RVIZ_REVIEW_PATHS_SCRIPT}")
fi
[[ -d "${MOSIM_MSGS_PACKAGE}" ]] || missing_files+=("${MOSIM_MSGS_PACKAGE}")
[[ -d "${MOSIM_SETPOINT_ADAPTER_PACKAGE}" ]] || missing_files+=("${MOSIM_SETPOINT_ADAPTER_PACKAGE}")

if [[ -f "${ROS_SETUP}" ]]; then
  set +u
  # shellcheck disable=SC1090
  source "${ROS_SETUP}"
  set -u
fi

ensure_ros_overlay() {
  local setup_path="${MOSIM_ROS2_WS}/install/setup.bash"
  if [[ ! -f "${setup_path}" || "${BUILD_MOSIM_ROS2_MSGS}" == "1" ]]; then
    mkdir -p "${MOSIM_ROS2_WS}/src"
    local msg_link="${MOSIM_ROS2_WS}/src/mosim_msgs"
    local adapter_link="${MOSIM_ROS2_WS}/src/mosim_setpoint_adapter"
    if [[ -L "${msg_link}" || -f "${msg_link}" ]]; then rm -f "${msg_link}"; fi
    if [[ -L "${adapter_link}" || -f "${adapter_link}" ]]; then rm -f "${adapter_link}"; fi
    [[ -e "${msg_link}" ]] || ln -s "${PROJECT_ROOT}/${MOSIM_MSGS_PACKAGE}" "${msg_link}"
    [[ -e "${adapter_link}" ]] || ln -s "${PROJECT_ROOT}/${MOSIM_SETPOINT_ADAPTER_PACKAGE}" "${adapter_link}"
    (
      cd "${MOSIM_ROS2_WS}"
      colcon build --packages-select mosim_msgs mosim_setpoint_adapter \
        > "${RESULT_DIR}/mosim_ros2_overlay_colcon.stdout.log" \
        2> "${RESULT_DIR}/mosim_ros2_overlay_colcon.stderr.log"
    )
  fi
  set +u
  # shellcheck disable=SC1090
  source "${setup_path}"
  set -u
}

ros2_path="$(command_path ros2)"
colcon_path="$(command_path colcon)"
gz_path="$(command_path gz)"
ign_path="$(command_path ign)"
gazebo_sim_cli_path=""
gazebo_sim_cli_kind=""
if [[ -n "${gz_path}" ]]; then
  gazebo_sim_cli_path="${gz_path}"
  gazebo_sim_cli_kind="gz"
elif [[ -n "${ign_path}" ]]; then
  gazebo_sim_cli_path="${ign_path}"
  gazebo_sim_cli_kind="ign"
fi

blockers=()
[[ "${#missing_files[@]}" -eq 0 ]] || blockers+=("missing_project_files")
[[ -f "${ROS_SETUP}" ]] || blockers+=("missing_ros_setup:${ROS_SETUP}")
[[ -n "${ros2_path}" ]] || blockers+=("missing_command:ros2")
[[ -n "${colcon_path}" ]] || blockers+=("missing_command:colcon")
[[ -n "${ign_path}" ]] || blockers+=("missing_command:ign")
[[ -n "${gazebo_sim_cli_path}" ]] || blockers+=("missing_command:gazebo_sim_cli(gz_or_ign)")
[[ -n "$(ros_pkg_prefix ros_gz_bridge)" ]] || blockers+=("missing_ros2_package:ros_gz_bridge")
if ! ros_pkg_has_executable ros_gz_bridge parameter_bridge; then
  blockers+=("missing_ros2_executable:ros_gz_bridge/parameter_bridge")
fi

if [[ "${#blockers[@]}" -eq 0 ]]; then
  if ! ensure_ros_overlay; then
    blockers+=("mosim_ros2_overlay_build_or_source_failed")
  fi
fi
[[ -n "$(ros_pkg_prefix mosim_msgs)" ]] || blockers+=("missing_ros2_package:mosim_msgs")
[[ -n "$(ros_pkg_prefix mosim_setpoint_adapter)" ]] || blockers+=("missing_ros2_package:mosim_setpoint_adapter")

missing_files_json="$(printf '%s\n' "${missing_files[@]:-}" | json_array_from_lines)"
blockers_json="$(printf '%s\n' "${blockers[@]:-}" | json_array_from_lines)"

cat > "${PREFLIGHT_JSON}" <<JSON
{
  "schema": "mosim.figure8_static_obstacle_preflight.v1",
  "scenario": "${SCENARIO}",
  "dry_run": $([[ "${DRY_RUN}" == "1" ]] && echo true || echo false),
  "gazebo_gui_review": $([[ "${GAZEBO_GUI_REVIEW}" == "1" ]] && echo true || echo false),
  "gazebo_gui_trail_marker": $([[ "${GAZEBO_GUI_TRAIL_MARKER}" == "1" ]] && echo true || echo false),
  "gazebo_rviz_review_paths": $([[ "${GAZEBO_RVIZ_REVIEW_PATHS}" == "1" ]] && echo true || echo false),
  "same_run_map_review_enabled": $([[ "${ENABLE_SAME_RUN_MAP_REVIEW}" == "1" ]] && echo true || echo false),
  "reference_sync_to_gazebo_truth": $([[ "${REFERENCE_SYNC_TO_GAZEBO_TRUTH}" == "1" ]] && echo true || echo false),
  "world": "${WORLD}",
  "result_dir": "${RESULT_DIR}",
  "gazebo_resource_paths": "${GAZEBO_RESOURCE_PATHS}",
  "position_cmd_topic": "${ROS_REFERENCE_POSITION_CMD_TOPIC}",
  "setpoint_topic": "${ROS_PLANNER_SETPOINT_TOPIC}",
  "controller_output_topic": "${ROS_CONTROLLER_OUTPUT_TOPIC}",
  "actuator_topic": "${ROS_ACTUATOR_TOPIC}",
  "truth_topic": "${GAZEBO_TRUTH_TOPIC}",
  "ros_truth_pose_topic": "${ROS_GAZEBO_TRUTH_POSE_TOPIC}",
  "review_actual_path_topic": "${ROS_REVIEW_ACTUAL_PATH_TOPIC}",
  "review_reference_path_topic": "${ROS_REVIEW_REFERENCE_PATH_TOPIC}",
  "lidar_topic": "${ROS_LIDAR_POINTS_TOPIC}",
  "local_occupancy_voxels_topic": "${ROS_LOCAL_VOXEL_TOPIC}",
  "local_occupancy_grid_topic": "${ROS_LOCAL_GRID_TOPIC}",
  "trajectory": {
    "frame_id": "${FIGURE_FRAME_ID}",
    "rate_hz": ${FIGURE_RATE_HZ},
    "duration_s": ${FIGURE_DURATION_S},
    "period_s": ${FIGURE_PERIOD_S},
    "x_amplitude_m": ${FIGURE_X_AMP},
    "y_amplitude_m": ${FIGURE_Y_AMP},
    "x_offset_m": ${FIGURE_X_OFFSET},
    "y_offset_m": ${FIGURE_Y_OFFSET},
    "altitude_m": ${FIGURE_ALTITUDE},
    "start_delay_s": ${FIGURE_START_DELAY_S},
    "takeoff_s": ${FIGURE_TAKEOFF_S},
    "hold_s": ${FIGURE_HOLD_S},
    "post_figure8_hold_s": ${FIGURE_POST_FIGURE8_HOLD_S},
    "land_s": ${FIGURE_LAND_S},
    "final_hold_s": ${FIGURE_FINAL_HOLD_S},
    "ground_altitude_m": ${FIGURE_GROUND_ALTITUDE},
    "center_revisit_radius_m": ${FIGURE_CENTER_REVISIT_RADIUS_M}
  },
  "static_obstacle_source": "${STATIC_OBSTACLE_SOURCE}",
  "world_cylinder_obstacle_radius_m": ${WORLD_CYLINDER_OBSTACLE_RADIUS_M},
  "tracker_reference_mode": "external_planner_setpoint",
  "missing_project_files": ${missing_files_json},
  "blockers": ${blockers_json},
  "claim_boundary": "preflight only; no trajectory tracking, planner_ready, final closed_loop, controller performance, or multi-UAV readiness is claimed"
}
JSON

if [[ "${DRY_RUN}" == "1" || "${#blockers[@]}" -gt 0 ]]; then
  cat > "${RUNTIME_STATUS_JSON}" <<JSON
{
  "schema": "mosim.figure8_static_obstacle_runtime_status.v1",
  "status": "preflight_blocked",
  "gate_passed": false,
  "preflight": "${PREFLIGHT_JSON}",
  "blockers": ${blockers_json}
}
JSON
  cat > "${BLOCKER}" <<JSON
{
  "schema": "mosim.figure8_static_obstacle_blocker.v1",
  "status": "blocked",
  "reason": "preflight_blocked",
  "preflight": "${PREFLIGHT_JSON}",
  "runtime_status": "${RUNTIME_STATUS_JSON}",
  "blockers": ${blockers_json}
}
JSON
  echo "${BLOCKER}"
  exit 0
fi

gz_pid=""
bridge_pid=""
static_tf_pid=""
local_map_pid=""
converter_pid=""
setpoint_adapter_pid=""
controller_adapter_pid=""
truth_recorder_pid=""
tracker_pid=""
reference_pid=""
trail_marker_pid=""
camera_follow_pid=""
camera_orbit_pid=""
rviz_review_paths_pid=""

write_world_control_report() {
  local status="$1"
  local service="$2"
  local response_file="${RESULT_DIR}/gazebo_world_control_unpause_response.txt"
  local stderr_file="${RESULT_DIR}/gazebo_world_control_unpause.stderr.txt"
  python3 - <<PY
import json
from pathlib import Path
response = Path("${response_file}")
stderr = Path("${stderr_file}")
payload = {
    "schema": "mosim.gazebo_world_control.v1",
    "status": "${status}",
    "action": "pause_false",
    "service": "${service}",
    "response_file": "${response_file}",
    "stderr_file": "${stderr_file}",
    "response_text": response.read_text(encoding="utf-8", errors="replace") if response.exists() else "",
    "stderr_text": stderr.read_text(encoding="utf-8", errors="replace") if stderr.exists() else "",
    "claim_boundary": "world-control evidence only; this does not prove figure-8 tracking, final closed_loop acceptance, planner_ready, or controller performance",
}
Path("${RESULT_DIR}/gazebo_world_control.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
}

unpause_gazebo_world() {
  local service="/world/${GAZEBO_WORLD_NAME}/control"
  local response_file="${RESULT_DIR}/gazebo_world_control_unpause_response.txt"
  local stderr_file="${RESULT_DIR}/gazebo_world_control_unpause.stderr.txt"
  if ign service \
    -s "${service}" \
    --reqtype ignition.msgs.WorldControl \
    --reptype ignition.msgs.Boolean \
    --timeout 2000 \
    --req "pause: false" \
    > "${response_file}" \
    2> "${stderr_file}"; then
    write_rc "${RESULT_DIR}/gazebo_world_control_unpause.rc" 0
    write_world_control_report "unpaused" "${service}"
    return 0
  fi
  local rc="$?"
  write_rc "${RESULT_DIR}/gazebo_world_control_unpause.rc" "${rc}"
  write_world_control_report "blocked" "${service}"
  return "${rc}"
}
cleanup() {
  terminate_process_tree "${reference_pid}" 1
  terminate_process_tree "${rviz_review_paths_pid}" 1
  terminate_process_tree "${camera_orbit_pid}" 1
  terminate_process_tree "${camera_follow_pid}" 1
  terminate_process_tree "${trail_marker_pid}" 1
  terminate_process_tree "${tracker_pid}" 2
  terminate_process_tree "${truth_recorder_pid}" 2
  terminate_process_tree "${controller_adapter_pid}" 2
  terminate_process_tree "${setpoint_adapter_pid}" 2
  terminate_process_tree "${converter_pid}" 2
  terminate_process_tree "${local_map_pid}" 2
  terminate_process_tree "${static_tf_pid}" 1
  terminate_process_tree "${bridge_pid}" 2
  terminate_process_tree "${gz_pid}" 3
}
trap cleanup EXIT

if [[ "${GAZEBO_GUI_REVIEW}" == "1" ]]; then
  gazebo_gui_run_flags=()
  if [[ "${GAZEBO_GUI_START_PAUSED}" != "1" ]]; then
    gazebo_gui_run_flags+=("-r")
  fi
  if [[ -n "${GUI_CONFIG}" ]]; then
    gazebo_gui_run_flags+=("--gui-config" "${GUI_CONFIG}")
  fi
  if [[ "${gazebo_sim_cli_kind}" == "gz" ]]; then
    "${gazebo_sim_cli_path}" sim --render-engine "${GAZEBO_RENDER_ENGINE_SERVER}" -v "${GAZEBO_GUI_VERBOSE}" "${gazebo_gui_run_flags[@]}" "${WORLD}" \
      > "${RESULT_DIR}/gazebo.stdout.log" \
      2> "${RESULT_DIR}/gazebo.stderr.log" &
  else
    "${gazebo_sim_cli_path}" gazebo --render-engine "${GAZEBO_RENDER_ENGINE_SERVER}" -v "${GAZEBO_GUI_VERBOSE}" "${gazebo_gui_run_flags[@]}" "${WORLD}" \
      > "${RESULT_DIR}/gazebo.stdout.log" \
      2> "${RESULT_DIR}/gazebo.stderr.log" &
  fi
else
  if [[ "${gazebo_sim_cli_kind}" == "gz" ]]; then
    "${gazebo_sim_cli_path}" sim -s --headless-rendering --render-engine-server "${GAZEBO_RENDER_ENGINE_SERVER}" "${WORLD}" \
      > "${RESULT_DIR}/gazebo.stdout.log" \
      2> "${RESULT_DIR}/gazebo.stderr.log" &
  else
    "${gazebo_sim_cli_path}" gazebo -s --headless-rendering --render-engine-server "${GAZEBO_RENDER_ENGINE_SERVER}" "${WORLD}" \
      > "${RESULT_DIR}/gazebo.stdout.log" \
      2> "${RESULT_DIR}/gazebo.stderr.log" &
  fi
fi
gz_pid="$!"
printf '%s\n' "${gz_pid}" > "${RESULT_DIR}/gazebo.pid"
sleep 4

bridge_args=("${ROS_ACTUATOR_TOPIC}@actuator_msgs/msg/Actuators@gz.msgs.Actuators")
if [[ "${ENABLE_SAME_RUN_MAP_REVIEW}" == "1" ]]; then
  bridge_args+=(
    "${ROS_GAZEBO_TRUTH_POSE_TOPIC}@geometry_msgs/msg/PoseArray@gz.msgs.Pose_V"
    "${ROS_IMU_TOPIC}@sensor_msgs/msg/Imu@gz.msgs.IMU"
    "${ROS_LIDAR_POINTS_TOPIC}@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked"
  )
fi
mapfile -t bridge_args < <(printf '%s\n' "${bridge_args[@]}" | awk '!seen[$0]++')
ros2 run ros_gz_bridge parameter_bridge "${bridge_args[@]}" \
  > "${RESULT_DIR}/ros_gz_bridge.stdout.log" \
  2> "${RESULT_DIR}/ros_gz_bridge.stderr.log" &
bridge_pid="$!"
sleep 2

if [[ "${ENABLE_SAME_RUN_MAP_REVIEW}" == "1" ]]; then
  ros2 run tf2_ros static_transform_publisher \
    --x 0 --y 0 --z 1.2 \
    --roll 0 --pitch 0 --yaw 0 \
    --frame-id "${LOCAL_MAP_MAP_FRAME}" \
    --child-frame-id "${LOCAL_MAP_EXPECTED_INPUT_FRAME}" \
    > "${RESULT_DIR}/static_tf.stdout.log" \
    2> "${RESULT_DIR}/static_tf.stderr.log" &
  static_tf_pid="$!"
  sleep 1

  python3 "${LOCAL_MAP_SCRIPT}" \
    --input-topic "${ROS_LIDAR_POINTS_TOPIC}" \
    --voxel-topic "${ROS_LOCAL_VOXEL_TOPIC}" \
    --grid-topic "${ROS_LOCAL_GRID_TOPIC}" \
    ${LOCAL_MAP_FRAME_ARGS} \
    > "${RESULT_DIR}/local_voxel_map.stdout.log" \
    2> "${RESULT_DIR}/local_voxel_map.stderr.log" &
  local_map_pid="$!"
  sleep 2
fi

ros2 run mosim_setpoint_adapter position_command_to_planner_setpoint_node \
  --ros-args \
  -p input_topic:="${ROS_REFERENCE_POSITION_CMD_TOPIC}" \
  -p output_topic:="${ROS_MOSIM_PLANNER_POSITION_CMD_TOPIC}" \
  -p expected_frame:="map" \
  -p source_frame_alias:="world" \
  -p planner_id:="mosim_figure8_static_obstacle_reference" \
  > "${RESULT_DIR}/position_command_converter.stdout.log" \
  2> "${RESULT_DIR}/position_command_converter.stderr.log" &
converter_pid="$!"
sleep 1

ros2 run mosim_setpoint_adapter planner_setpoint_adapter_node \
  --ros-args \
  -p input_topic:="${ROS_MOSIM_PLANNER_POSITION_CMD_TOPIC}" \
  -p output_topic:="${ROS_PLANNER_SETPOINT_TOPIC}" \
  -p status_topic:="${ROS_PLANNER_SETPOINT_STATUS_TOPIC}" \
  -p expected_frame:="map" \
  -p rate_hz:=20.0 \
  -p stale_timeout_s:="${TRACKER_SETPOINT_TIMEOUT_S}" \
  > "${RESULT_DIR}/planner_setpoint_adapter.stdout.log" \
  2> "${RESULT_DIR}/planner_setpoint_adapter.stderr.log" &
setpoint_adapter_pid="$!"
sleep 1

python3 "${CONTROLLER_NODE_SCRIPT}" \
  --input-topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" \
  --output-topic "${ROS_ACTUATOR_TOPIC}" \
  --vehicle-id "sunray150" \
  --max-messages 0 \
  --max-command-age-s 2.0 \
  --output-json "${RESULT_DIR}/controller_output_adapter_node.json" \
  --trace-jsonl "${RESULT_DIR}/controller_output_adapter_node.trace.jsonl" \
  > "${RESULT_DIR}/controller_output_node.stdout.log" \
  2> "${RESULT_DIR}/controller_output_node.stderr.log" &
controller_adapter_pid="$!"
sleep 2

python3 "${CONTROLLER_FIXTURE_SCRIPT}" \
  --topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" \
  --vehicle-id "sunray150" \
  --command-type "normalized_motor_speed" \
  --command "${TRACKER_HOVER_COMMAND}" "${TRACKER_HOVER_COMMAND}" "${TRACKER_HOVER_COMMAND}" "${TRACKER_HOVER_COMMAND}" \
  --rate-hz 20 \
  --times 40 \
  --backend "figure8_pre_unpause_hover_fixture" \
  --source-authority "bounded_figure8_pre_unpause_hover_startup_guard" \
  --output-json "${RESULT_DIR}/pre_unpause_hover_fixture.json" \
  > "${RESULT_DIR}/pre_unpause_hover_fixture.stdout.log" \
  2> "${RESULT_DIR}/pre_unpause_hover_fixture.stderr.log" || true

truth_timeout="$(python3 - <<PY
import math
print(int(math.ceil(float("${FIGURE_DURATION_S}") + 60.0)))
PY
)"
truth_target_samples="$(python3 - <<PY
import math
print(max(300, int(math.ceil(float("${FIGURE_DURATION_S}") * 5.0)) + 20))
PY
)"
truth_target_samples="${TRUTH_TARGET_SAMPLES_OVERRIDE:-${truth_target_samples}}"
if [[ "${INDEPENDENT_TRUTH_RECORDER}" == "1" ]]; then
  python3 "${GAZEBO_TRUTH_RECORDER_SCRIPT}" \
    --output-jsonl "${GAZEBO_TRUTH_POSE_JSONL}" \
    --summary-json "${GAZEBO_TRUTH_POSE_SUMMARY_JSON}" \
    --topic "${GAZEBO_TRUTH_TOPIC}" \
    --model-name "${GAZEBO_TRUTH_MODEL_NAME}" \
    --frame-id "${GAZEBO_TRUTH_FRAME_ID}" \
    --timeout-seconds "${truth_timeout}" \
    --target-samples "${truth_target_samples}" \
    > "${RESULT_DIR}/gazebo_truth_pose_recorder.stdout.log" \
    2> "${RESULT_DIR}/gazebo_truth_pose_recorder.stderr.log" &
  truth_recorder_pid="$!"
  sleep 1
else
  python3 - <<PY
import json
from pathlib import Path
Path("${GAZEBO_TRUTH_POSE_JSONL}").write_text("", encoding="utf-8")
Path("${GAZEBO_TRUTH_POSE_SUMMARY_JSON}").write_text(json.dumps({
    "schema": "mosim.gazebo_pose_truth_recording.v1",
    "status": "skipped",
    "reason": "independent_truth_recorder_disabled_for_control_priority_runtime_probe",
    "topic": "${GAZEBO_TRUTH_TOPIC}",
    "model_name": "${GAZEBO_TRUTH_MODEL_NAME}",
    "frame_id": "${GAZEBO_TRUTH_FRAME_ID}",
    "count": 0,
    "claim_boundary": [
        "Independent truth recorder is disabled so controller polling is not starved.",
        "Evaluation may use controller-observed truth trace only as pre-acceptance evidence."
    ],
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
  write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" 0
fi

if [[ "${GAZEBO_GUI_REVIEW}" == "1" && "${GAZEBO_GUI_TRAIL_MARKER}" == "1" ]]; then
  python3 "${TRAIL_MARKER_SCRIPT}" \
    --truth-topic "${GAZEBO_TRUTH_TOPIC}" \
    --model-name "${GAZEBO_TRUTH_MODEL_NAME}" \
    --frame-id "${GAZEBO_TRUTH_FRAME_ID}" \
    --transport-mode service \
    --duration-s "${TRACKER_DURATION_S}" \
    --center-x-m "${FIGURE_X_OFFSET}" \
    --center-y-m "${FIGURE_Y_OFFSET}" \
    --center-revisit-radius-m "${FIGURE_CENTER_REVISIT_RADIUS_M}" \
    --publish-rate-hz "${GAZEBO_GUI_TRAIL_PUBLISH_RATE_HZ}" \
    --max-points "${GAZEBO_GUI_TRAIL_MAX_POINTS}" \
    --line-scale-m "${GAZEBO_GUI_TRAIL_LINE_SCALE_M}" \
    --world-name "${GAZEBO_WORLD_NAME}" \
    --entity-segment-radius-m "${GAZEBO_GUI_TRAIL_ENTITY_RADIUS_M}" \
    --entity-segment-min-distance-m "${GAZEBO_GUI_TRAIL_ENTITY_MIN_DISTANCE_M}" \
    --entity-segments-per-publish "${GAZEBO_GUI_TRAIL_ENTITY_SEGMENTS_PER_PUBLISH}" \
    $([[ "${GAZEBO_GUI_TRAIL_ENTITY_SEGMENTS}" == "1" ]] && echo "--entity-trail" || echo "--no-entity-trail") \
    --publish-timeout-s "${GAZEBO_GUI_TRAIL_PUBLISH_TIMEOUT_S}" \
    --summary-json "${RESULT_DIR}/gazebo_truth_trail_marker.json" \
    --trace-jsonl "${RESULT_DIR}/gazebo_truth_trail_marker.trace.jsonl" \
    > "${RESULT_DIR}/gazebo_truth_trail_marker.stdout.log" \
    2> "${RESULT_DIR}/gazebo_truth_trail_marker.stderr.log" &
  trail_marker_pid="$!"
  sleep 1
fi

if [[ "${GAZEBO_GUI_REVIEW}" == "1" && "${GAZEBO_GUI_CAMERA_FOLLOW}" == "1" ]]; then
  python3 "${CAMERA_FOLLOW_SCRIPT}" \
    --target "${GAZEBO_TRUTH_MODEL_NAME}" \
    --offset-x-m "${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M}" \
    --offset-y-m "${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M}" \
    --offset-z-m "${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M}" \
    --min-dist-m "${GAZEBO_GUI_CAMERA_FOLLOW_MIN_DIST_M}" \
    --max-dist-m "${GAZEBO_GUI_CAMERA_FOLLOW_MAX_DIST_M}" \
    --inherit-yaw \
    --use-model-frame \
    --allow-service-fallback \
    --start-delay-s "${GAZEBO_GUI_CAMERA_FOLLOW_START_DELAY_S}" \
    --repeat "${GAZEBO_GUI_CAMERA_FOLLOW_REPEAT}" \
    --interval-s "${GAZEBO_GUI_CAMERA_FOLLOW_INTERVAL_S}" \
    --timeout-s 1.5 \
    --summary-json "${RESULT_DIR}/gazebo_camera_follow_request.json" \
    > "${RESULT_DIR}/gazebo_camera_follow.stdout.log" \
    2> "${RESULT_DIR}/gazebo_camera_follow.stderr.log" &
  camera_follow_pid="$!"
  sleep 1
fi

if [[ "${GAZEBO_GUI_REVIEW}" == "1" && "${GAZEBO_GUI_CAMERA_FOLLOW}" == "1" && "${GAZEBO_GUI_CAMERA_ORBIT}" == "1" ]]; then
  python3 "${GAZEBO_GUI_CAMERA_ORBIT_SCRIPT}" \
    --target "${GAZEBO_TRUTH_MODEL_NAME}" \
    --initial-offset-x-m "${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M}" \
    --initial-offset-y-m "${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M}" \
    --initial-offset-z-m "${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M}" \
    --azimuth-step-deg "${GAZEBO_GUI_CAMERA_ORBIT_AZIMUTH_STEP_DEG}" \
    --elevation-step-deg "${GAZEBO_GUI_CAMERA_ORBIT_ELEVATION_STEP_DEG}" \
    --duration-s "${TRACKER_DURATION_S}" \
    --summary-json "${RESULT_DIR}/gazebo_camera_orbit_request.json" \
    --trace-jsonl "${RESULT_DIR}/gazebo_camera_orbit.trace.jsonl" \
    > "${RESULT_DIR}/gazebo_camera_orbit.stdout.log" \
    2> "${RESULT_DIR}/gazebo_camera_orbit.stderr.log" &
  camera_orbit_pid="$!"
  sleep 1
fi

if [[ "${GAZEBO_RVIZ_REVIEW_PATHS}" == "1" ]]; then
  python3 "${RVIZ_REVIEW_PATHS_SCRIPT}" \
    --gz-truth-topic "${GAZEBO_TRUTH_TOPIC}" \
    --model-name "${GAZEBO_TRUTH_MODEL_NAME}" \
    --reference-topic "${ROS_REFERENCE_POSITION_CMD_TOPIC}" \
    --truth-path-topic "${ROS_REVIEW_ACTUAL_PATH_TOPIC}" \
    --reference-path-topic "${ROS_REVIEW_REFERENCE_PATH_TOPIC}" \
    --frame-id "${FIGURE_FRAME_ID}" \
    --max-points "${RVIZ_REVIEW_PATH_MAX_POINTS}" \
    --duration-s "${TRACKER_DURATION_S}" \
    --summary-json "${RESULT_DIR}/rviz_review_paths.json" \
    > "${RESULT_DIR}/rviz_review_paths.stdout.log" \
    2> "${RESULT_DIR}/rviz_review_paths.stderr.log" &
  rviz_review_paths_pid="$!"
  sleep 1
fi

reference_command=(python3 "${REFERENCE_SCRIPT}" \
  --topic "${ROS_REFERENCE_POSITION_CMD_TOPIC}" \
  --frame-id "${FIGURE_FRAME_ID}" \
  --rate-hz "${FIGURE_RATE_HZ}" \
  --duration-s "${FIGURE_DURATION_S}" \
  --period-s "${FIGURE_PERIOD_S}" \
  --x-amplitude-m "${FIGURE_X_AMP}" \
  --y-amplitude-m "${FIGURE_Y_AMP}" \
  --x-offset-m "${FIGURE_X_OFFSET}" \
  --y-offset-m "${FIGURE_Y_OFFSET}" \
  --altitude-m "${FIGURE_ALTITUDE}" \
  --start-delay-s "${FIGURE_START_DELAY_S}" \
  --takeoff-s "${FIGURE_TAKEOFF_S}" \
  --hold-s "${FIGURE_HOLD_S}" \
  --post-figure8-hold-s "${FIGURE_POST_FIGURE8_HOLD_S}" \
  --land-s "${FIGURE_LAND_S}" \
  --final-hold-s "${FIGURE_FINAL_HOLD_S}" \
  --ground-altitude-m "${FIGURE_GROUND_ALTITUDE}" \
  "${OBSTACLE_ARGS[@]}" \
  --report-json "${REFERENCE_REPORT_PATH}" \
  --trace-jsonl "${REFERENCE_TRACE_PATH}")
if [[ "${REFERENCE_SYNC_TO_GAZEBO_TRUTH}" == "1" ]]; then
  reference_command+=(--truth-sync-stdin --truth-sync-model-name "${GAZEBO_TRUTH_MODEL_NAME}" --truth-sync-topic "${GAZEBO_TRUTH_TOPIC}" --truth-sync-frame-id "${GAZEBO_TRUTH_FRAME_ID}" --truth-sync-epoch-s "${REFERENCE_TRUTH_SYNC_EPOCH_S}")
  timeout "${truth_timeout}" ign topic -e -t "${GAZEBO_TRUTH_TOPIC}" | "${reference_command[@]}" \
    > "${RESULT_DIR}/figure8_position_command.stdout.log" \
    2> "${RESULT_DIR}/figure8_position_command.stderr.log" &
else
  "${reference_command[@]}" \
    > "${RESULT_DIR}/figure8_position_command.stdout.log" \
    2> "${RESULT_DIR}/figure8_position_command.stderr.log" &
fi
reference_pid="$!"
sleep 1

tracker_command=(python3 "${TRACKER_SCRIPT}" \
  --input-topic-name "${GAZEBO_TRUTH_TOPIC}" \
  --model-name "${GAZEBO_TRUTH_MODEL_NAME}" \
  --truth-frame-id "${GAZEBO_TRUTH_FRAME_ID}" \
  --setpoint-topic "${ROS_PLANNER_SETPOINT_TOPIC}" \
  --output-topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" \
  --vehicle-id sunray150 \
  --expected-frame map \
  --hover-command "${TRACKER_HOVER_COMMAND}" \
  --kp-x "${TRACKER_KP_X}" \
  --kd-x "${TRACKER_KD_X}" \
  --ka-x "${TRACKER_KA_X}" \
  --kp-y "${TRACKER_KP_Y}" \
  --kd-y "${TRACKER_KD_Y}" \
  --ka-y "${TRACKER_KA_Y}" \
  --kp-z "${TRACKER_KP_Z}" \
  --kd-z "${TRACKER_KD_Z}" \
  --ki-z "${TRACKER_KI_Z}" \
  --kp-roll "${TRACKER_KP_ROLL}" \
  --kd-roll "${TRACKER_KD_ROLL}" \
  --kp-pitch "${TRACKER_KP_PITCH}" \
  --kd-pitch "${TRACKER_KD_PITCH}" \
  --kp-yaw "${TRACKER_KP_YAW}" \
  --kd-yaw "${TRACKER_KD_YAW}" \
  --attitude-command-limit "${TRACKER_ATTITUDE_COMMAND_LIMIT}" \
  --xy-control-sign "${TRACKER_XY_CONTROL_SIGN}" \
  --takeoff-xy-enable-altitude-m "${TRACKER_TAKEOFF_XY_ENABLE_ALTITUDE_M}" \
  --takeoff-stable-z-error-m "${TRACKER_TAKEOFF_STABLE_Z_ERROR_M}" \
  --takeoff-reference-ready-z-m "${TRACKER_TAKEOFF_REFERENCE_READY_Z_M}" \
  --takeoff-stable-max-vz-mps "${TRACKER_TAKEOFF_STABLE_MAX_VZ_MPS}" \
  --takeoff-stable-s "${TRACKER_TAKEOFF_STABLE_S}" \
  --recovery-xy-brake-scale "${TRACKER_RECOVERY_XY_BRAKE_SCALE}" \
  --recovery-reset-altitude-m "${TRACKER_RECOVERY_RESET_ALTITUDE_M}" \
  --xy-error-limit-m "${TRACKER_XY_ERROR_LIMIT_M}" \
  --xy-velocity-error-limit-mps "${TRACKER_XY_VELOCITY_ERROR_LIMIT_MPS}" \
  --integral-limit-m-s "${TRACKER_INTEGRAL_LIMIT_M_S}" \
  --command-min "${TRACKER_COMMAND_MIN}" \
  --command-max "${TRACKER_COMMAND_MAX}" \
  --ground-motor-command "${TRACKER_GROUND_MOTOR_COMMAND}" \
  --setpoint-timeout-s "${TRACKER_SETPOINT_TIMEOUT_S}" \
  --max-publish-hz "${TRACKER_MAX_PUBLISH_HZ}" \
  --duration-s "${TRACKER_DURATION_S}" \
  --truth-wall-time-factor "${TRACKER_TRUTH_WALL_TIME_FACTOR}" \
  --output-json "${TRACKER_REPORT_PATH}" \
  --trace-jsonl "${TRACKER_TRACE_PATH}")
if [[ -n "${TRACKER_ROLL_CONTROL_SIGN}" ]]; then
  tracker_command+=(--roll-control-sign "${TRACKER_ROLL_CONTROL_SIGN}")
fi
if [[ -n "${TRACKER_PITCH_CONTROL_SIGN}" ]]; then
  tracker_command+=(--pitch-control-sign "${TRACKER_PITCH_CONTROL_SIGN}")
fi
if [[ "${TRACKER_HOLD_LAST_SETPOINT_WHEN_TRUTH_BUFFERED}" == "1" ]]; then
  tracker_command+=(--hold-last-setpoint-when-truth-buffered)
fi
if [[ "${TRACKER_SYNC_TRUTH_TO_WALL_TIME}" == "1" ]]; then
  tracker_command+=(--sync-truth-to-wall-time)
fi
if [[ "${TRACKER_TRUTH_INPUT_MODE}" == "poll" ]]; then
  tracker_command+=(--poll-command ign --poll-sleep-s "${TRACKER_POLL_SLEEP_S}" --poll-sample-timeout-s "${TRACKER_POLL_SAMPLE_TIMEOUT_S}")
fi
if [[ "${TRACKER_TRUTH_INPUT_MODE}" == "poll" ]]; then
  timeout "${truth_timeout}" "${tracker_command[@]}" \
    > "${RESULT_DIR}/figure8_setpoint_tracker.stdout.log" \
    2> "${RESULT_DIR}/figure8_setpoint_tracker.stderr.log" &
else
  timeout "${truth_timeout}" ign topic -e -t "${GAZEBO_TRUTH_TOPIC}" | "${tracker_command[@]}" \
    > "${RESULT_DIR}/figure8_setpoint_tracker.stdout.log" \
    2> "${RESULT_DIR}/figure8_setpoint_tracker.stderr.log" &
fi
tracker_pid="$!"

# Keep the world paused until the reference publisher, setpoint adapter, and
# truth-feedback tracker are all live. Otherwise the vehicle can free-fall for
# several wall-clock seconds before the first fresh ControllerOutput reaches the
# Gazebo motor plugin, which looks like an unstable hover or falling-leaf flip
# in GUI review.
sleep 1
unpause_gazebo_world || true

if wait "${reference_pid}"; then
  write_rc "${RESULT_DIR}/figure8_position_command.rc" 0
else
  write_rc "${RESULT_DIR}/figure8_position_command.rc" "$?"
fi
reference_pid=""

if wait "${tracker_pid}"; then
  write_rc "${RESULT_DIR}/figure8_setpoint_tracker.rc" 0
else
  write_rc "${RESULT_DIR}/figure8_setpoint_tracker.rc" "$?"
fi
tracker_pid=""

if [[ -n "${truth_recorder_pid}" ]]; then
  if wait "${truth_recorder_pid}"; then
    write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" 0
  else
    write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" "$?"
  fi
fi
truth_recorder_pid=""

if [[ -n "${trail_marker_pid}" ]]; then
  if wait "${trail_marker_pid}"; then
    write_rc "${RESULT_DIR}/gazebo_truth_trail_marker.rc" 0
  else
    write_rc "${RESULT_DIR}/gazebo_truth_trail_marker.rc" "$?"
  fi
fi
trail_marker_pid=""

if [[ -n "${camera_follow_pid}" ]]; then
  if wait "${camera_follow_pid}"; then
    write_rc "${RESULT_DIR}/gazebo_camera_follow.rc" 0
  else
    write_rc "${RESULT_DIR}/gazebo_camera_follow.rc" "$?"
  fi
fi
camera_follow_pid=""

if [[ -n "${camera_orbit_pid}" ]]; then
  if wait "${camera_orbit_pid}"; then
    write_rc "${RESULT_DIR}/gazebo_camera_orbit.rc" 0
  else
    write_rc "${RESULT_DIR}/gazebo_camera_orbit.rc" "$?"
  fi
fi
camera_orbit_pid=""

if [[ -n "${rviz_review_paths_pid}" ]]; then
  if wait "${rviz_review_paths_pid}"; then
    write_rc "${RESULT_DIR}/rviz_review_paths.rc" 0
  else
    write_rc "${RESULT_DIR}/rviz_review_paths.rc" "$?"
  fi
fi
rviz_review_paths_pid=""

map_review_rc=0
if [[ "${ENABLE_SAME_RUN_MAP_REVIEW}" == "1" ]]; then
  if timeout "${TIMEOUT_SECONDS}" python3 "${MAP_REVIEW_RECORDER_SCRIPT}" \
    --lidar-topic "${ROS_LIDAR_POINTS_TOPIC}" \
    --voxel-topic "${ROS_LOCAL_VOXEL_TOPIC}" \
    --grid-topic "${ROS_LOCAL_GRID_TOPIC}" \
    --output-dir "${RESULT_DIR}/${MAP_REVIEW_OUTPUT_DIR}" \
    --duration-seconds "${MAP_REVIEW_DURATION_SECONDS}" \
    > "${RESULT_DIR}/map_review_capture.stdout.log" \
    2> "${RESULT_DIR}/map_review_capture.stderr.log"; then
    write_rc "${RESULT_DIR}/map_review_capture.rc" 0
  else
    map_review_rc="$?"
    write_rc "${RESULT_DIR}/map_review_capture.rc" "${map_review_rc}"
  fi
else
  python3 - <<PY
import json
from pathlib import Path
Path("${RESULT_DIR}/${MAP_REVIEW_OUTPUT_DIR}").mkdir(parents=True, exist_ok=True)
Path("${RESULT_DIR}/${MAP_REVIEW_OUTPUT_DIR}/GAZEBO_ROS2_MAP_REVIEW.json").write_text(json.dumps({
    "schema": "mosim.gazebo_ros2_map_review.v1",
    "status": "not_requested",
    "gate_passed": None,
    "reason": "ENABLE_SAME_RUN_MAP_REVIEW is not set",
    "claim_boundary": [
        "Figure-8/static-obstacle gate ran without same-run raw LiDAR/local-map review capture.",
        "No same-run point-cloud, voxel-map, or occupancy-grid evidence is claimed from this skipped report."
    ],
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
  write_rc "${RESULT_DIR}/map_review_capture.rc" 0
fi

eval_rc=0
python3 "${EVAL_SCRIPT}" \
  --reference-report-json "${REFERENCE_REPORT_PATH}" \
  --reference-trace-jsonl "${REFERENCE_TRACE_PATH}" \
  --tracker-report-json "${TRACKER_REPORT_PATH}" \
  --tracker-trace-jsonl "${TRACKER_TRACE_PATH}" \
  --adapter-trace-jsonl "${RESULT_DIR}/controller_output_adapter_node.trace.jsonl" \
  --truth-pose-jsonl "${GAZEBO_TRUTH_POSE_JSONL}" \
  --truth-summary-json "${GAZEBO_TRUTH_POSE_SUMMARY_JSON}" \
  --output-json "${EVAL_JSON}" \
  "${OBSTACLE_ARGS[@]}" \
  --center-revisit-radius-m "${FIGURE_CENTER_REVISIT_RADIUS_M}" \
  "${EVAL_THRESHOLD_ARGS[@]}" \
  > "${RESULT_DIR}/figure8_static_obstacle_eval.stdout.log" \
  2> "${RESULT_DIR}/figure8_static_obstacle_eval.stderr.log" || eval_rc="$?"
write_rc "${RESULT_DIR}/figure8_static_obstacle_eval.rc" "${eval_rc}"

timeout 5 ros2 topic list > "${RESULT_DIR}/ros2_topic_list.txt" 2> "${RESULT_DIR}/ros2_topic_list.stderr.txt" || true

python3 - <<PY
import json
from pathlib import Path

result_dir = Path("${RESULT_DIR}")
def load(name):
    path = Path(name)
    if not path.is_absolute():
        path = result_dir / name
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "invalid_json", "error": f"{exc.__class__.__name__}: {exc}"}

eval_report = load("${OUTPUT_JSON}")
reference = load("${REFERENCE_REPORT_JSON}")
tracker = load("${TRACKER_REPORT_JSON}")
adapter = load("controller_output_adapter_node.json")
map_review = load("${MAP_REVIEW_OUTPUT_DIR}/GAZEBO_ROS2_MAP_REVIEW.json")
trail_marker = load("gazebo_truth_trail_marker.json")
rviz_paths = load("rviz_review_paths.json")
blockers = []
if not reference.get("gate_passed"):
    blockers.append(f"reference_not_passed:{reference.get('status')}")
if tracker.get("status") != "completed":
    blockers.append(f"tracker_not_completed:{tracker.get('status')}")
if adapter.get("status") not in {"published", None}:
    blockers.append(f"adapter_status_not_published:{adapter.get('status')}")
if not eval_report.get("gate_passed"):
    blockers.append("figure8_static_obstacle_eval_failed")
    blockers.extend([f"eval:{item}" for item in eval_report.get("blockers", [])])
same_run_map_review_enabled = "${ENABLE_SAME_RUN_MAP_REVIEW}" == "1"
if same_run_map_review_enabled and not map_review.get("gate_passed"):
    blockers.append(f"same_run_map_review_not_passed:{map_review.get('status')}")
    blockers.extend([f"map_review:{item}" for item in map_review.get("blockers", [])])
gazebo_gui_review = "${GAZEBO_GUI_REVIEW}" == "1"
gazebo_gui_trail_marker_enabled = "${GAZEBO_GUI_TRAIL_MARKER}" == "1"
gazebo_rviz_review_paths_enabled = "${GAZEBO_RVIZ_REVIEW_PATHS}" == "1"
if gazebo_rviz_review_paths_enabled:
    if rviz_paths.get("status") not in {"running", "completed"}:
        blockers.append(f"rviz_review_paths_not_running:{rviz_paths.get('status', 'missing')}")
    if int(rviz_paths.get("truth_points") or 0) < 2:
        blockers.append("rviz_actual_path_insufficient_points")
    if int(rviz_paths.get("reference_points") or 0) < 2:
        blockers.append("rviz_reference_path_insufficient_points")
if gazebo_gui_review and gazebo_gui_trail_marker_enabled:
    if trail_marker.get("status") != "published":
        blockers.append(f"gazebo_gui_trail_marker_not_published:{trail_marker.get('status', 'missing')}")
    elif int(trail_marker.get("marker_publish_success") or 0) <= 0:
        blockers.append("gazebo_gui_trail_marker_no_successful_publish")
    elif int(trail_marker.get("point_count") or 0) < 2:
        blockers.append("gazebo_gui_trail_marker_insufficient_points")
gate_passed = not blockers
runtime = {
    "schema": "mosim.figure8_static_obstacle_runtime_status.v1",
    "status": "runtime_gate_passed" if gate_passed else "runtime_gate_blocked",
    "gate_passed": gate_passed,
    "scenario": "${SCENARIO}",
    "world": "${WORLD}",
    "world_name": "${GAZEBO_WORLD_NAME}",
    "static_obstacle_source": "${STATIC_OBSTACLE_SOURCE}",
    "world_cylinder_obstacle_radius_m": float("${WORLD_CYLINDER_OBSTACLE_RADIUS_M}"),
    "result_dir": "${RESULT_DIR}",
    "same_run_map_review_enabled": same_run_map_review_enabled,
    "gazebo_gui_review": gazebo_gui_review,
    "gazebo_gui_trail_marker": gazebo_gui_trail_marker_enabled,
    "gazebo_rviz_review_paths": gazebo_rviz_review_paths_enabled,
    "rviz_review_paths_status": rviz_paths.get("status", "missing"),
    "rviz_actual_path_topic": rviz_paths.get("truth_path_topic", "${ROS_REVIEW_ACTUAL_PATH_TOPIC}"),
    "rviz_reference_path_topic": rviz_paths.get("reference_path_topic", "${ROS_REVIEW_REFERENCE_PATH_TOPIC}"),
    "rviz_actual_path_point_count": rviz_paths.get("truth_points", 0),
    "rviz_reference_path_point_count": rviz_paths.get("reference_points", 0),
    "gazebo_gui_trail_marker_status": trail_marker.get("status", "missing"),
    "gazebo_gui_trail_marker_visual_mode": trail_marker.get("visual_mode", "missing"),
    "gazebo_gui_trail_marker_line_scale_m": trail_marker.get("line_scale_m"),
    "gazebo_gui_entity_trail_enabled": trail_marker.get("entity_trail_enabled", False),
    "gazebo_gui_entity_trail_success_count": trail_marker.get("entity_spawn_success", 0),
    "gazebo_gui_entity_trail_segment_count": trail_marker.get("entity_spawned_segment_count", 0),
    "gazebo_gui_trail_marker_success_count": trail_marker.get("marker_publish_success", 0),
    "gazebo_gui_trail_marker_point_count": trail_marker.get("point_count", 0),
    "gazebo_gui_trail_marker_revisit_highlight_point_count": trail_marker.get("revisit_highlight_point_count", 0),
    "gazebo_gui_camera_follow": "${GAZEBO_GUI_CAMERA_FOLLOW}" == "1",
    "gazebo_gui_camera_orbit": "${GAZEBO_GUI_CAMERA_ORBIT}" == "1",
    "gazebo_gui_camera_follow_offset_m": [float("${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M}"), float("${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M}"), float("${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M}")],
    "gazebo_gui_camera_orbit_report": "gazebo_camera_orbit_request.json",
    "preflight": "${PREFLIGHT_JSON}",
    "run_manifest": "${RUN_MANIFEST}",
    "reference_report": "${REFERENCE_REPORT_JSON}",
    "reference_trace": "${REFERENCE_TRACE_JSONL}",
    "tracker_report": "${TRACKER_REPORT_JSON}",
    "tracker_trace": "${TRACKER_TRACE_JSONL}",
    "adapter_trace": "controller_output_adapter_node.trace.jsonl",
    "truth_recording": "GAZEBO_TRUTH_POSE_RECORDING.json",
    "truth_pose": "gazebo_truth_pose.jsonl",
    "map_review": "${MAP_REVIEW_OUTPUT_DIR}/GAZEBO_ROS2_MAP_REVIEW.json",
    "map_review_status": map_review.get("status", "missing"),
    "map_review_artifacts": map_review.get("artifacts", {}),
    "rviz_review_paths": "rviz_review_paths.json",
    "eval": "${OUTPUT_JSON}",
    "blockers": blockers,
    "warnings": eval_report.get("warnings", []),
    "claim_boundary": [
        "bounded single-UAV Gazebo/ROS2 figure-8 plus static-obstacle pre-acceptance only",
        "truth-feedback tracker and current Gazebo plant limitations mean no final competition controller-performance claim",
        "no UE acceptance or multi-UAV readiness is claimed"
    ],
}
Path("${RUNTIME_STATUS_JSON}").write_text(json.dumps(runtime, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
manifest = {
    "schema_version": "mosim.run_manifest.v1",
    "run_id": "sunray150_figure8_static_obstacle_pre_acceptance",
    "objective": "bounded single-UAV figure-8 tracking plus static-obstacle clearance gate",
    "scene_id": "sunray150_single_uav_competition_light",
    "vehicle_id": "sunray150_assembled",
    "world": "${WORLD}",
    "world_name": "${GAZEBO_WORLD_NAME}",
    "static_obstacle_source": "${STATIC_OBSTACLE_SOURCE}",
    "world_cylinder_obstacle_radius_m": float("${WORLD_CYLINDER_OBSTACLE_RADIUS_M}"),
    "gazebo_gui_review": "${GAZEBO_GUI_REVIEW}" == "1",
    "gazebo_gui_config": "${GUI_CONFIG}",
    "gazebo_gui_trail_marker": "${GAZEBO_GUI_TRAIL_MARKER}" == "1",
    "gazebo_rviz_review_paths": "${GAZEBO_RVIZ_REVIEW_PATHS}" == "1",
    "rviz_actual_path_topic": "${ROS_REVIEW_ACTUAL_PATH_TOPIC}",
    "rviz_reference_path_topic": "${ROS_REVIEW_REFERENCE_PATH_TOPIC}",
    "gazebo_gui_camera_follow": "${GAZEBO_GUI_CAMERA_FOLLOW}" == "1",
    "gazebo_gui_camera_orbit": "${GAZEBO_GUI_CAMERA_ORBIT}" == "1",
    "gazebo_gui_camera_follow_offset_m": [float("${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_X_M}"), float("${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Y_M}"), float("${GAZEBO_GUI_CAMERA_FOLLOW_OFFSET_Z_M}")],
    "quality_status": "passed" if gate_passed else "blocked",
    "evidence_level": "gazebo_ros2_figure8_static_obstacle_pre_acceptance",
    "claim_scope": ["PositionCommand", "PlannerSetpoint", "ControllerOutput", "Gazebo truth", "static obstacle clearance"],
    "blockers": blockers,
    "artifacts": {
        "runtime_status": "${RUNTIME_STATUS_JSON}",
        "eval": "${EVAL_JSON}",
        "reference_report": "${REFERENCE_REPORT_PATH}",
        "reference_trace": "${REFERENCE_TRACE_PATH}",
        "tracker_report": "${TRACKER_REPORT_PATH}",
        "tracker_trace": "${TRACKER_TRACE_PATH}",
        "truth_pose": "${GAZEBO_TRUTH_POSE_JSONL}",
        "truth_summary": "${GAZEBO_TRUTH_POSE_SUMMARY_JSON}",
        "gazebo_camera_follow": "${RESULT_DIR}/gazebo_camera_follow_request.json",
        "gazebo_camera_orbit": "${RESULT_DIR}/gazebo_camera_orbit_request.json",
        "rviz_review_paths": "${RESULT_DIR}/rviz_review_paths.json",
        "map_review": "${RESULT_DIR}/${MAP_REVIEW_OUTPUT_DIR}/GAZEBO_ROS2_MAP_REVIEW.json",
        "map_review_figures_dir": "${RESULT_DIR}/${MAP_REVIEW_OUTPUT_DIR}/figures"
    },
    "not_claimed": [
        "competition_controller_performance",
        "final_closed_loop_acceptance",
        "planner_ready",
        "fast_lio_localization_success",
        "UE_acceptance",
        "multi_uav_readiness"
    ],
}
Path("${RUN_MANIFEST}").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if gate_passed:
    blocker = Path("${BLOCKER}")
    if blocker.exists():
        blocker.unlink()
else:
    Path("${BLOCKER}").write_text(json.dumps({
        "schema": "mosim.figure8_static_obstacle_blocker.v1",
        "status": "blocked",
        "reason": "figure8_static_obstacle_runtime_gate_failed",
        "runtime_status": "${RUNTIME_STATUS_JSON}",
        "blockers": blockers,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

if [[ -f "${BLOCKER}" ]]; then
  echo "${BLOCKER}"
else
  echo "${RUN_MANIFEST}"
fi
