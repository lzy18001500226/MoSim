#!/usr/bin/env bash
# run_mworks_controller_output_replay_gate: bounded MWORKS CSV ControllerOutput replay into Gazebo.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
GAZEBO_ENV_SCRIPT="${GAZEBO_ENV_SCRIPT:-${PROJECT_ROOT}/Scripts/gazebo/setup_gazebo_wsl_env.sh}"
if [[ -f "${GAZEBO_ENV_SCRIPT}" ]]; then
  # shellcheck disable=SC1090
  source "${GAZEBO_ENV_SCRIPT}"
fi

SCENARIO="${SCENARIO:-Config/scenarios/system/sunray150_single_uav_competition_light.yaml}"
WORLD="${WORLD:-Config/gazebo/worlds/sunray150_single_uav_competition_light.sdf}"
WORLD_NAME="${WORLD_NAME:-sunray150_single_uav_competition_light}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/mworks_controller_output_replay_gate_20260618}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
ROS_LOG_DIR="${ROS_LOG_DIR:-${PROJECT_ROOT}/Results/tmp/ros_logs}"
MOSIM_ROS2_WS="${MOSIM_ROS2_WS:-${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs}"
BUILD_MOSIM_ROS2_MSGS="${BUILD_MOSIM_ROS2_MSGS:-0}"
GAZEBO_RENDER_ENGINE_SERVER="${GAZEBO_RENDER_ENGINE_SERVER:-ogre}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-35}"

ROS_CONTROLLER_OUTPUT_TOPIC="${ROS_CONTROLLER_OUTPUT_TOPIC:-/mosim/sunray150/controller_output}"
ROS_ACTUATOR_TOPIC="${ROS_ACTUATOR_TOPIC:-/sunray150/gazebo/command/motor_speed}"
GZ_ACTUATOR_TOPIC="${GZ_ACTUATOR_TOPIC:-/sunray150/gazebo/command/motor_speed}"
GAZEBO_TRUTH_TOPIC="${GAZEBO_TRUTH_TOPIC:-/world/sunray150_single_uav_competition_light/dynamic_pose/info}"
GAZEBO_TRUTH_MODEL_NAME="${GAZEBO_TRUTH_MODEL_NAME:-sunray150_assembled}"
GAZEBO_TRUTH_FRAME_ID="${GAZEBO_TRUTH_FRAME_ID:-world}"

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_DIR}" "${ROS_LOG_DIR}"
export ROS_LOG_DIR
mosim_gazebo_apply_resource_paths "Config/gazebo/models"

write_rc() {
  printf '%s\n' "$2" > "$1"
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

set +u
# shellcheck disable=SC1090
source "${ROS_SETUP}"
set -u

ensure_mosim_msgs_sourced() {
  local setup_path="${MOSIM_ROS2_WS}/install/setup.bash"
  if [[ ! -f "${setup_path}" || "${BUILD_MOSIM_ROS2_MSGS}" == "1" ]]; then
    mkdir -p "${MOSIM_ROS2_WS}/src"
    local msg_link="${MOSIM_ROS2_WS}/src/mosim_msgs"
    if [[ -L "${msg_link}" || -f "${msg_link}" ]]; then rm -f "${msg_link}"; fi
    if [[ ! -e "${msg_link}" ]]; then ln -s "${PROJECT_ROOT}/Scripts/ros/mosim_msgs" "${msg_link}"; fi
    (cd "${MOSIM_ROS2_WS}" && colcon build --packages-select mosim_msgs > "${PROJECT_ROOT}/${RESULT_DIR}/mosim_msgs_colcon.stdout.log" 2> "${PROJECT_ROOT}/${RESULT_DIR}/mosim_msgs_colcon.stderr.log")
  fi
  set +u
  # shellcheck disable=SC1090
  source "${setup_path}"
  set -u
}
ensure_mosim_msgs_sourced

gz_pid=""
bridge_pid=""
adapter_pid=""
truth_recorder_pid=""
replay_pid=""
cleanup() {
  terminate_process_tree "${replay_pid}" 2
  terminate_process_tree "${truth_recorder_pid}" 2
  terminate_process_tree "${adapter_pid}" 2
  terminate_process_tree "${bridge_pid}" 2
  terminate_process_tree "${gz_pid}" 3
}
trap cleanup EXIT

if command -v gz >/dev/null 2>&1; then
  gz sim -s --headless-rendering --render-engine-server "${GAZEBO_RENDER_ENGINE_SERVER}" "${WORLD}" > "${RESULT_DIR}/gazebo.stdout.log" 2> "${RESULT_DIR}/gazebo.stderr.log" &
else
  ign gazebo -s --headless-rendering --render-engine-server "${GAZEBO_RENDER_ENGINE_SERVER}" "${WORLD}" > "${RESULT_DIR}/gazebo.stdout.log" 2> "${RESULT_DIR}/gazebo.stderr.log" &
fi
gz_pid="$!"
sleep 4

ros2 run ros_gz_bridge parameter_bridge "${ROS_ACTUATOR_TOPIC}@actuator_msgs/msg/Actuators@gz.msgs.Actuators" > "${RESULT_DIR}/ros_gz_bridge.stdout.log" 2> "${RESULT_DIR}/ros_gz_bridge.stderr.log" &
bridge_pid="$!"
sleep 3

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
adapter_pid="$!"
sleep 2

ign service -s "/world/${WORLD_NAME}/control" --reqtype ignition.msgs.WorldControl --reptype ignition.msgs.Boolean --timeout 2000 --req "pause: false" > "${RESULT_DIR}/gazebo_world_control_unpause_response.txt" 2> "${RESULT_DIR}/gazebo_world_control_unpause.stderr.txt" || true
sleep 0.5

python3 Scripts/gazebo/capture_gazebo_pose_truth_topic.py \
  --output-jsonl "${RESULT_DIR}/gazebo_truth_pose.jsonl" \
  --summary-json "${RESULT_DIR}/GAZEBO_TRUTH_POSE_RECORDING.json" \
  --topic "${GAZEBO_TRUTH_TOPIC}" \
  --model-name "${GAZEBO_TRUTH_MODEL_NAME}" \
  --frame-id "${GAZEBO_TRUTH_FRAME_ID}" \
  --timeout-seconds 60 \
  --min-duration-seconds 2.0 \
  --target-samples 30 \
  --sample-timeout-seconds 2 \
  --sleep-seconds 0.05 \
  > "${RESULT_DIR}/gazebo_truth_pose_recorder.stdout.log" \
  2> "${RESULT_DIR}/gazebo_truth_pose_recorder.stderr.log" &
truth_recorder_pid="$!"
sleep 1

python3 Scripts/ros/mworks_csv_to_controller_output_replay.py \
  --output-jsonl "${RESULT_DIR}/controller_output_replay.jsonl" \
  --output-manifest "${RESULT_DIR}/MWORKS_CONTROLLER_OUTPUT_REPLAY_MANIFEST.json" \
  --publish \
  --publish-report-json "${RESULT_DIR}/mworks_controller_output_replay_publish.json" \
  --topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" \
  --publish-rate-hz 20 \
  --max-rate-hz 20 \
  > "${RESULT_DIR}/mworks_controller_output_replay.stdout.log" \
  2> "${RESULT_DIR}/mworks_controller_output_replay.stderr.log" &
replay_pid="$!"

if wait "${replay_pid}"; then write_rc "${RESULT_DIR}/mworks_controller_output_replay.rc" 0; else write_rc "${RESULT_DIR}/mworks_controller_output_replay.rc" "$?"; fi
replay_pid=""
if wait "${truth_recorder_pid}"; then write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" 0; else write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" "$?"; fi
truth_recorder_pid=""

eval_rc=0
python3 Scripts/quality/evaluate_gazebo_plant_response.py \
  --controller-report-json "${RESULT_DIR}/controller_output_adapter_node.json" \
  --fixture-report-json "${RESULT_DIR}/mworks_controller_output_replay_publish.json" \
  --truth-pose-jsonl "${RESULT_DIR}/gazebo_truth_pose.jsonl" \
  --truth-summary-json "${RESULT_DIR}/GAZEBO_TRUTH_POSE_RECORDING.json" \
  --output-json "${RESULT_DIR}/GAZEBO_MWORKS_REPLAY_PLANT_RESPONSE_EVAL.json" \
  --min-samples 20 \
  --min-duration-s 1.5 \
  --min-z-delta-m 0.02 \
  --min-3d-delta-m 0.02 \
  > "${RESULT_DIR}/mworks_replay_plant_response_eval.stdout.log" \
  2> "${RESULT_DIR}/mworks_replay_plant_response_eval.stderr.log" || eval_rc="$?"
write_rc "${RESULT_DIR}/mworks_replay_plant_response_eval.rc" "${eval_rc}"

python3 - <<PY
import json
from pathlib import Path
result_dir = Path("${RESULT_DIR}")
eval_path = result_dir / "GAZEBO_MWORKS_REPLAY_PLANT_RESPONSE_EVAL.json"
eval_report = json.loads(eval_path.read_text(encoding="utf-8")) if eval_path.exists() else {}
passed = bool(eval_report.get("gate_passed"))
blockers = list(eval_report.get("blockers", []))
runtime = {
  "schema": "mosim.gazebo_mworks_controller_output_replay_runtime_status.v1",
  "status": "runtime_passed" if passed else "runtime_blocked",
  "gate_passed": passed,
  "result_dir": "${RESULT_DIR}",
  "mworks_replay_manifest": "MWORKS_CONTROLLER_OUTPUT_REPLAY_MANIFEST.json",
  "publish_report": "mworks_controller_output_replay_publish.json",
  "adapter_trace": "controller_output_adapter_node.trace.jsonl",
  "truth_pose": "gazebo_truth_pose.jsonl",
  "truth_summary": "GAZEBO_TRUTH_POSE_RECORDING.json",
  "eval": "GAZEBO_MWORKS_REPLAY_PLANT_RESPONSE_EVAL.json",
  "blockers": blockers,
  "claim_boundary": [
    "bounded MWORKS CSV ControllerOutput replay into Gazebo actuator interface",
    "plant response only; not same-run MWORKS controller feedback in Gazebo",
    "no final controller performance, planner_ready, figure-8, obstacle avoidance, or multi-UAV readiness is claimed"
  ],
}
(result_dir / "RUNTIME_STATUS.json").write_text(json.dumps(runtime, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
manifest = {
  "schema_version": "mosim.run_manifest.v1",
  "run_id": "mworks_controller_output_replay_gate_20260618",
  "objective": "verify accepted MWORKS controller output CSV can be converted to ControllerOutput and drive Gazebo actuator/plant response",
  "quality_status": "passed" if passed else "blocked",
  "artifacts": {
    "runtime_status": "${RESULT_DIR}/RUNTIME_STATUS.json",
    "eval": "${RESULT_DIR}/GAZEBO_MWORKS_REPLAY_PLANT_RESPONSE_EVAL.json",
    "replay_manifest": "${RESULT_DIR}/MWORKS_CONTROLLER_OUTPUT_REPLAY_MANIFEST.json",
    "adapter_trace": "${RESULT_DIR}/controller_output_adapter_node.trace.jsonl",
    "truth_pose": "${RESULT_DIR}/gazebo_truth_pose.jsonl"
  },
  "blockers": blockers,
  "not_claimed": ["same_run_gazebo_feedback_controller", "competition_controller_performance", "planner_ready", "final_closed_loop_acceptance", "multi_uav_readiness"]
}
(result_dir / "RUN_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if not passed:
    (result_dir / "BLOCKER.json").write_text(json.dumps({"schema":"mosim.gazebo_mworks_controller_output_replay_blocker.v1","status":"blocked","runtime_status":"RUNTIME_STATUS.json","blockers":blockers}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
else:
    blocker = result_dir / "BLOCKER.json"
    if blocker.exists():
        blocker.unlink()
PY

if [[ -f "${RESULT_DIR}/BLOCKER.json" ]]; then
  echo "${RESULT_DIR}/BLOCKER.json"
else
  echo "${RESULT_DIR}/RUN_MANIFEST.json"
fi
