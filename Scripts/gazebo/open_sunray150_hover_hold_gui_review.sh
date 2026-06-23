#!/usr/bin/env bash
# Open a controlled Sunray150 hover-hold Gazebo GUI review window.
# This wrapper is for manual visual review only. Numeric gate evidence remains
# owned by run_sunray150_hover_hold_closed_loop.sh.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
WORLD="${WORLD:-Config/gazebo/worlds/sunray150_single_uav_competition_light.sdf}"
WORLD_NAME="${WORLD_NAME:-sunray150_single_uav_competition_light}"
MODEL_NAME="${MODEL_NAME:-sunray150_assembled}"
TRUTH_TOPIC="${TRUTH_TOPIC:-/world/${WORLD_NAME}/dynamic_pose/info}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
MOSIM_ROS2_SETUP="${MOSIM_ROS2_SETUP:-${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs/install/setup.bash}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_review/hover_hold_gui_$(date +%Y%m%d_%H%M%S)}"

ROS_CONTROLLER_OUTPUT_TOPIC="${ROS_CONTROLLER_OUTPUT_TOPIC:-/mosim/sunray150/controller_output}"
ROS_ACTUATOR_TOPIC="${ROS_ACTUATOR_TOPIC:-/sunray150/gazebo/command/motor_speed}"
HOVER_TARGET_ALTITUDE_M="${HOVER_TARGET_ALTITUDE_M:-1.2}"
HOVER_COMMAND="${HOVER_COMMAND:-0.05520}"
HOVER_COMMAND_MIN="${HOVER_COMMAND_MIN:-0.05350}"
HOVER_COMMAND_MAX="${HOVER_COMMAND_MAX:-0.05620}"
HOVER_KP_Z="${HOVER_KP_Z:-0.0010}"
HOVER_KD_Z="${HOVER_KD_Z:-0.0020}"
HOVER_KI_Z="${HOVER_KI_Z:-0.00035}"
HOVER_KP_X="${HOVER_KP_X:-1.2e-4}"
HOVER_KD_X="${HOVER_KD_X:-2.0e-4}"
HOVER_KP_Y="${HOVER_KP_Y:-1.2e-4}"
HOVER_KD_Y="${HOVER_KD_Y:-2.0e-4}"
HOVER_KP_ROLL="${HOVER_KP_ROLL:-0.010}"
HOVER_KD_ROLL="${HOVER_KD_ROLL:-0.002}"
HOVER_KP_PITCH="${HOVER_KP_PITCH:-0.010}"
HOVER_KD_PITCH="${HOVER_KD_PITCH:-0.002}"
HOVER_XY_CONTROL_SIGN="${HOVER_XY_CONTROL_SIGN:--1.0}"
HOVER_ROLL_CONTROL_SIGN="${HOVER_ROLL_CONTROL_SIGN:--1.0}"
HOVER_PITCH_CONTROL_SIGN="${HOVER_PITCH_CONTROL_SIGN:-1.0}"
HOVER_DURATION_S="${HOVER_DURATION_S:-1800}"
HOVER_PUBLISH_HZ="${HOVER_PUBLISH_HZ:-20}"

cd "${PROJECT_ROOT}"
source Scripts/gazebo/setup_gazebo_wsl_env.sh
mkdir -p "${RESULT_DIR}"

set +u
# shellcheck disable=SC1090
source "${ROS_SETUP}"
if [[ -f "${MOSIM_ROS2_SETUP}" ]]; then
  # shellcheck disable=SC1090
  source "${MOSIM_ROS2_SETUP}"
fi
set -u

cleanup() {
  for pid in "${controller_pid:-}" "${adapter_pid:-}" "${bridge_pid:-}" "${fixture_pid:-}" "${gazebo_pid:-}"; do
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      kill "${pid}" 2>/dev/null || true
    fi
  done
}
trap cleanup EXIT

ign gazebo --render-engine ogre "${WORLD}" \
  > "${RESULT_DIR}/gazebo.stdout.log" \
  2> "${RESULT_DIR}/gazebo.stderr.log" &
gazebo_pid="$!"
printf '%s\n' "${gazebo_pid}" > "${RESULT_DIR}/gazebo.pid"

sleep 5

ros2 run ros_gz_bridge parameter_bridge \
  "${ROS_ACTUATOR_TOPIC}@actuator_msgs/msg/Actuators@gz.msgs.Actuators" \
  > "${RESULT_DIR}/ros_gz_bridge.stdout.log" \
  2> "${RESULT_DIR}/ros_gz_bridge.stderr.log" &
bridge_pid="$!"
printf '%s\n' "${bridge_pid}" > "${RESULT_DIR}/ros_gz_bridge.pid"

sleep 3

python3 Scripts/ros/controller_output_to_gazebo_actuators_node.py \
  --input-topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" \
  --output-topic "${ROS_ACTUATOR_TOPIC}" \
  --vehicle-id sunray150 \
  --max-messages 0 \
  --max-command-age-s 2.0 \
  --output-json "${RESULT_DIR}/controller_output_adapter_node.json" \
  --trace-jsonl "${RESULT_DIR}/controller_output_adapter_node.trace.jsonl" \
  > "${RESULT_DIR}/controller_output_adapter_node.stdout.log" \
  2> "${RESULT_DIR}/controller_output_adapter_node.stderr.log" &
adapter_pid="$!"
printf '%s\n' "${adapter_pid}" > "${RESULT_DIR}/controller_output_adapter_node.pid"

sleep 2

bash -lc "timeout '${HOVER_DURATION_S}' ign topic -e -t '${TRUTH_TOPIC}' | python3 Scripts/ros/gazebo_truth_hover_hold_controller.py --input-topic-name '${TRUTH_TOPIC}' --output-topic '${ROS_CONTROLLER_OUTPUT_TOPIC}' --vehicle-id sunray150 --model-name '${MODEL_NAME}' --frame-id world --target-altitude-m '${HOVER_TARGET_ALTITUDE_M}' --hover-command '${HOVER_COMMAND}' --kp-z '${HOVER_KP_Z}' --kd-z '${HOVER_KD_Z}' --ki-z '${HOVER_KI_Z}' --kp-x '${HOVER_KP_X}' --kd-x '${HOVER_KD_X}' --kp-y '${HOVER_KP_Y}' --kd-y '${HOVER_KD_Y}' --kp-roll '${HOVER_KP_ROLL}' --kd-roll '${HOVER_KD_ROLL}' --kp-pitch '${HOVER_KP_PITCH}' --kd-pitch '${HOVER_KD_PITCH}' --kp-yaw 0.0 --kd-yaw 0.0 --xy-control-sign '${HOVER_XY_CONTROL_SIGN}' --roll-control-sign '${HOVER_ROLL_CONTROL_SIGN}' --pitch-control-sign '${HOVER_PITCH_CONTROL_SIGN}' --attitude-command-limit 0.002 --command-min '${HOVER_COMMAND_MIN}' --command-max '${HOVER_COMMAND_MAX}' --max-publish-hz '${HOVER_PUBLISH_HZ}' --duration-s '${HOVER_DURATION_S}' --output-json '${RESULT_DIR}/hover_hold_controller.json' --trace-jsonl '${RESULT_DIR}/hover_hold_controller_trace.jsonl'" \
  > "${RESULT_DIR}/hover_hold_controller.stdout.log" \
  2> "${RESULT_DIR}/hover_hold_controller.stderr.log" &
controller_pid="$!"
printf '%s\n' "${controller_pid}" > "${RESULT_DIR}/hover_hold_controller.pid"

sleep 1

python3 Scripts/ros/publish_controller_output_fixture.py \
  --topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" \
  --vehicle-id sunray150 \
  --command-type normalized_motor_speed \
  --command "${HOVER_COMMAND}" "${HOVER_COMMAND}" "${HOVER_COMMAND}" "${HOVER_COMMAND}" \
  --rate-hz 20 \
  --times 60 \
  --backend pre_unpause_hover_fixture \
  --source-authority bounded_hover_hold_gui_review_startup_guard \
  --output-json "${RESULT_DIR}/pre_unpause_hover_fixture.json" \
  > "${RESULT_DIR}/pre_unpause_hover_fixture.stdout.log" \
  2> "${RESULT_DIR}/pre_unpause_hover_fixture.stderr.log" &
fixture_pid="$!"
printf '%s\n' "${fixture_pid}" > "${RESULT_DIR}/pre_unpause_hover_fixture.pid"

sleep 1

ign service \
  -s "/world/${WORLD_NAME}/control" \
  --reqtype ignition.msgs.WorldControl \
  --reptype ignition.msgs.Boolean \
  --timeout 2000 \
  --req "pause: false" \
  > "${RESULT_DIR}/unpause.stdout.log" \
  2> "${RESULT_DIR}/unpause.stderr.log" || true

cat > "${RESULT_DIR}/REVIEW_MANIFEST.json" <<JSON
{
  "schema": "mosim.gazebo_hover_hold_gui_review.v1",
  "status": "running_for_manual_review",
  "world": "${WORLD}",
  "world_name": "${WORLD_NAME}",
  "model_name": "${MODEL_NAME}",
  "truth_topic": "${TRUTH_TOPIC}",
  "render_engine": "ogre",
  "controller": "Scripts/ros/gazebo_truth_hover_hold_controller.py",
  "adapter": "Scripts/ros/controller_output_to_gazebo_actuators_node.py",
  "target_altitude_m": ${HOVER_TARGET_ALTITUDE_M},
  "hover_command": ${HOVER_COMMAND},
  "command_bounds": [${HOVER_COMMAND_MIN}, ${HOVER_COMMAND_MAX}],
  "roll_control_sign": ${HOVER_ROLL_CONTROL_SIGN},
  "pitch_control_sign": ${HOVER_PITCH_CONTROL_SIGN},
  "claim_boundary": [
    "manual GUI visual review only",
    "uses Gazebo truth-feedback hover-hold to avoid open-loop equal-motor flyaway",
    "does not prove competition controller performance, trajectory tracking, obstacle avoidance, point cloud, occupancy map, or multi-UAV readiness"
  ]
}
JSON

printf '%s\n' "${RESULT_DIR}"
wait "${gazebo_pid}"
