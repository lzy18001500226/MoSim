#!/usr/bin/env bash
# Open assembled Sunray150 takeoff-hover-land Gazebo GUI review.
# Numeric acceptance remains owned by run_sunray150_takeoff_hover_land_gate.sh.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SCENARIO="${SCENARIO:-Config/scenarios/system/sunray150_single_uav_competition_light.yaml}"
WORLD="${WORLD:-Config/gazebo/worlds/sunray150_takeoff_hover_land_plant_sanity.sdf}"
WORLD_NAME="${WORLD_NAME:-sunray150_takeoff_hover_land_plant_sanity}"
TRUTH_TOPIC="${TRUTH_TOPIC:-/world/${WORLD_NAME}/dynamic_pose/info}"
MODEL_NAME="${MODEL_NAME:-sunray150_assembled}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
MOSIM_ROS2_SETUP="${MOSIM_ROS2_SETUP:-${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs/install/setup.bash}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_review/takeoff_hover_land_gui_$(date +%Y%m%d_%H%M%S)}"

ROS_CONTROLLER_OUTPUT_TOPIC="${ROS_CONTROLLER_OUTPUT_TOPIC:-/mosim/sunray150/controller_output}"
ROS_ACTUATOR_TOPIC="${ROS_ACTUATOR_TOPIC:-/sunray150/gazebo/command/motor_speed}"
HOVER_ALTITUDE_M="${HOVER_ALTITUDE_M:-0.6}"
LANDED_ALTITUDE_M="${LANDED_ALTITUDE_M:-0.12}"
TAKEOFF_DURATION_S="${TAKEOFF_DURATION_S:-4.0}"
HOVER_DURATION_S="${HOVER_DURATION_S:-4.0}"
LAND_DURATION_S="${LAND_DURATION_S:-4.0}"
SETTLE_DURATION_S="${SETTLE_DURATION_S:-1.0}"
HOVER_COMMAND="${HOVER_COMMAND:-0.0556}"
COMMAND_MAX="${COMMAND_MAX:-0.0585}"
LAND_COMMAND_MAX="${LAND_COMMAND_MAX:-0.0554}"
REVIEW_DURATION_S="${REVIEW_DURATION_S:-20}"

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

python3 Scripts/ros/publish_controller_output_fixture.py \
  --topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" \
  --vehicle-id sunray150 \
  --command-type normalized_motor_speed \
  --command "${HOVER_COMMAND}" "${HOVER_COMMAND}" "${HOVER_COMMAND}" "${HOVER_COMMAND}" \
  --rate-hz 20 \
  --times 40 \
  --mode pre_unpause_hover_guard \
  --backend pre_unpause_hover_guard \
  --source-authority bounded_takeoff_hover_land_gui_review_startup_guard \
  --output-json "${RESULT_DIR}/pre_unpause_hover_fixture.json" \
  > "${RESULT_DIR}/pre_unpause_hover_fixture.stdout.log" \
  2> "${RESULT_DIR}/pre_unpause_hover_fixture.stderr.log" &
fixture_pid="$!"
printf '%s\n' "${fixture_pid}" > "${RESULT_DIR}/pre_unpause_hover_fixture.pid"
sleep 1

bash -lc "timeout '${REVIEW_DURATION_S}' ign topic -e -t '${TRUTH_TOPIC}' | python3 Scripts/ros/gazebo_truth_takeoff_hover_land_controller.py --input-topic-name '${TRUTH_TOPIC}' --output-topic '${ROS_CONTROLLER_OUTPUT_TOPIC}' --vehicle-id sunray150 --model-name '${MODEL_NAME}' --frame-id world --hover-altitude-m '${HOVER_ALTITUDE_M}' --landed-altitude-m '${LANDED_ALTITUDE_M}' --takeoff-duration-s '${TAKEOFF_DURATION_S}' --hover-duration-s '${HOVER_DURATION_S}' --land-duration-s '${LAND_DURATION_S}' --settle-duration-s '${SETTLE_DURATION_S}' --hover-command '${HOVER_COMMAND}' --command-max '${COMMAND_MAX}' --land-command-max '${LAND_COMMAND_MAX}' --output-json '${RESULT_DIR}/takeoff_hover_land_controller.json' --trace-jsonl '${RESULT_DIR}/takeoff_hover_land_controller_trace.jsonl'" \
  > "${RESULT_DIR}/takeoff_hover_land_controller.stdout.log" \
  2> "${RESULT_DIR}/takeoff_hover_land_controller.stderr.log" &
controller_pid="$!"
printf '%s\n' "${controller_pid}" > "${RESULT_DIR}/takeoff_hover_land_controller.pid"
sleep 2

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
  "schema": "mosim.gazebo_takeoff_hover_land_gui_review.v1",
  "status": "running_for_manual_review",
  "world": "${WORLD}",
  "world_name": "${WORLD_NAME}",
  "model_name": "${MODEL_NAME}",
  "truth_topic": "${TRUTH_TOPIC}",
  "render_engine": "ogre",
  "controller": "Scripts/ros/gazebo_truth_takeoff_hover_land_controller.py",
  "adapter": "Scripts/ros/controller_output_to_gazebo_actuators_node.py",
  "profile": {
    "hover_altitude_m": ${HOVER_ALTITUDE_M},
    "landed_altitude_m": ${LANDED_ALTITUDE_M},
    "takeoff_duration_s": ${TAKEOFF_DURATION_S},
    "hover_duration_s": ${HOVER_DURATION_S},
    "land_duration_s": ${LAND_DURATION_S},
    "settle_duration_s": ${SETTLE_DURATION_S}
  },
  "claim_boundary": [
    "manual GUI visual review only",
    "uses same-run Gazebo truth-feedback takeoff-hover-land controller",
    "does not prove MWORKS controller deployment, competition controller performance, planner_ready, final closed_loop acceptance, or multi-UAV readiness"
  ]
}
JSON

printf '%s\n' "${RESULT_DIR}"
wait "${gazebo_pid}"
