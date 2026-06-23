#!/usr/bin/env bash
# run_sunray150_takeoff_hover_land_gate: bounded plant sanity gate.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
GAZEBO_ENV_SCRIPT="${GAZEBO_ENV_SCRIPT:-${PROJECT_ROOT}/Scripts/gazebo/setup_gazebo_wsl_env.sh}"
if [[ -f "${GAZEBO_ENV_SCRIPT}" ]]; then
  # shellcheck disable=SC1090
  source "${GAZEBO_ENV_SCRIPT}"
fi
SCENARIO="${SCENARIO:-Config/scenarios/system/sunray150_single_uav_competition_light.yaml}"
WORLD_OVERRIDE="${WORLD_OVERRIDE:-Config/gazebo/worlds/sunray150_takeoff_hover_land_plant_sanity.sdf}"
WORLD_NAME_OVERRIDE="${WORLD_NAME_OVERRIDE:-sunray150_takeoff_hover_land_plant_sanity}"
TRUTH_TOPIC_OVERRIDE="${TRUTH_TOPIC_OVERRIDE:-/world/sunray150_takeoff_hover_land_plant_sanity/dynamic_pose/info}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/sunray150_takeoff_hover_land_plant_sanity}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
ROS_LOG_DIR="${ROS_LOG_DIR:-${PROJECT_ROOT}/Results/tmp/ros_logs}"
MOSIM_ROS2_WS="${MOSIM_ROS2_WS:-${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs}"
BUILD_MOSIM_ROS2_MSGS="${BUILD_MOSIM_ROS2_MSGS:-0}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-35}"
GAZEBO_RENDER_ENGINE_SERVER="${GAZEBO_RENDER_ENGINE_SERVER:-ogre}"
GAZEBO_GUI_REVIEW="${GAZEBO_GUI_REVIEW:-0}"
GAZEBO_GUI_VERBOSE="${GAZEBO_GUI_VERBOSE:-2}"
GUI_CONFIG="${GUI_CONFIG:-}"
GAZEBO_CAMERA_FOLLOW_SCRIPT="${GAZEBO_CAMERA_FOLLOW_SCRIPT:-Scripts/gazebo/set_gazebo_camera_follow.py}"
GAZEBO_CAMERA_FOLLOW_TARGET="${GAZEBO_CAMERA_FOLLOW_TARGET:-sunray150_assembled}"
GAZEBO_CAMERA_FOLLOW_OFFSET_X_M="${GAZEBO_CAMERA_FOLLOW_OFFSET_X_M:--0.55}"
GAZEBO_CAMERA_FOLLOW_OFFSET_Y_M="${GAZEBO_CAMERA_FOLLOW_OFFSET_Y_M:-0.14}"
GAZEBO_CAMERA_FOLLOW_OFFSET_Z_M="${GAZEBO_CAMERA_FOLLOW_OFFSET_Z_M:-0.28}"
GAZEBO_CAMERA_FOLLOW_MIN_DIST_M="${GAZEBO_CAMERA_FOLLOW_MIN_DIST_M:-0.35}"
GAZEBO_CAMERA_FOLLOW_MAX_DIST_M="${GAZEBO_CAMERA_FOLLOW_MAX_DIST_M:-2.0}"
GAZEBO_CAMERA_FOLLOW_REPEAT="${GAZEBO_CAMERA_FOLLOW_REPEAT:-80}"
GAZEBO_CAMERA_FOLLOW_INTERVAL_S="${GAZEBO_CAMERA_FOLLOW_INTERVAL_S:-0.4}"
TRUTH_TIMEOUT_SECONDS="${TRUTH_TIMEOUT_SECONDS:-120}"
HOVER_ALTITUDE_M="${HOVER_ALTITUDE_M:-0.6}"
LANDED_ALTITUDE_M="${LANDED_ALTITUDE_M:-0.12}"
TAKEOFF_DURATION_S="${TAKEOFF_DURATION_S:-4.0}"
HOVER_DURATION_S="${HOVER_DURATION_S:-4.0}"
LAND_DURATION_S="${LAND_DURATION_S:-4.0}"
SETTLE_DURATION_S="${SETTLE_DURATION_S:-1.0}"
HOVER_COMMAND="${HOVER_COMMAND:-0.0556}"
COMMAND_MAX="${COMMAND_MAX:-0.0585}"
LAND_COMMAND_MAX="${LAND_COMMAND_MAX:-0.0554}"
STAGE_CONTROLLER_EXTRA_ARGS="${STAGE_CONTROLLER_EXTRA_ARGS:-}"
TRUTH_TARGET_SAMPLES="${TRUTH_TARGET_SAMPLES:-$(python3 - <<PY
import math
duration = (
    float("${TAKEOFF_DURATION_S}")
    + float("${HOVER_DURATION_S}")
    + float("${LAND_DURATION_S}")
    + float("${SETTLE_DURATION_S}")
)
print(max(520, int(math.ceil((duration + 2.0) * 45.0))))
PY
)}"

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_DIR}" "${ROS_LOG_DIR}"
export ROS_LOG_DIR

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
import json, sys
data=json.loads('''${scenario_json}''')
node=data
for part in sys.argv[1].split("."):
    node=node[part]
print(node)
PY
}

WORLD="${WORLD_OVERRIDE:-$(yaml_get gazebo.world)}"
GAZEBO_WORLD_NAME="$(python3 - <<PY
import json, re
data=json.loads('''${scenario_json}''')
topic=data["ros2"].get("gazebo_truth_pose", {}).get("topic", "/world/sunray150_single_uav_competition_light/dynamic_pose/info")
m=re.match(r"^/world/([^/]+)/", topic)
print("${WORLD_NAME_OVERRIDE}" or (m.group(1) if m else "sunray150_single_uav_competition_light"))
PY
)"
GAZEBO_RESOURCE_PATHS="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
paths=data.get("gazebo", {}).get("resource_paths", ["Config/gazebo/models"])
print(":".join(paths if isinstance(paths, list) else [paths]))
PY
)"
mosim_gazebo_apply_resource_paths "${GAZEBO_RESOURCE_PATHS}"

ROS_CONTROLLER_OUTPUT_TOPIC="$(yaml_get ros2.controller_adapter.input_topic)"
ROS_ACTUATOR_TOPIC="$(yaml_get ros2.controller_adapter.ros_actuator_topic)"
GZ_ACTUATOR_TOPIC="$(yaml_get ros2.controller_adapter.gz_actuator_topic)"
CONTROLLER_NODE_SCRIPT="$(yaml_get ros2.controller_adapter.node_script)"
MOSIM_MSGS_PACKAGE="$(yaml_get ros2.controller_adapter.message_package)"
GAZEBO_TRUTH_TOPIC="${TRUTH_TOPIC_OVERRIDE:-$(yaml_get ros2.gazebo_truth_pose.topic)}"
GAZEBO_TRUTH_MODEL_NAME="$(yaml_get ros2.gazebo_truth_pose.model_name)"
GAZEBO_TRUTH_FRAME_ID="$(yaml_get ros2.gazebo_truth_pose.frame_id)"
GAZEBO_TRUTH_RECORDER_SCRIPT="$(yaml_get ros2.gazebo_truth_pose.recorder_script)"
STAGE_CONTROLLER_SCRIPT="${STAGE_CONTROLLER_SCRIPT:-Scripts/ros/gazebo_truth_takeoff_hover_land_controller.py}"
EVAL_SCRIPT="Scripts/quality/evaluate_gazebo_takeoff_hover_land.py"

RUN_MANIFEST="${RESULT_DIR}/RUN_MANIFEST.json"
RUNTIME_STATUS_JSON="${RESULT_DIR}/RUNTIME_STATUS.json"
BLOCKER="${RESULT_DIR}/BLOCKER.json"
GAZEBO_TRUTH_POSE_JSONL="${RESULT_DIR}/gazebo_truth_pose.jsonl"
GAZEBO_TRUTH_POSE_SUMMARY_JSON="${RESULT_DIR}/GAZEBO_TRUTH_POSE_RECORDING.json"
CONTROLLER_JSON="${RESULT_DIR}/takeoff_hover_land_controller.json"
CONTROLLER_TRACE="${RESULT_DIR}/takeoff_hover_land_controller_trace.jsonl"
EVAL_JSON="${RESULT_DIR}/GAZEBO_TAKEOFF_HOVER_LAND_EVAL.json"

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
    if [[ ! -e "${msg_link}" ]]; then ln -s "${PROJECT_ROOT}/${MOSIM_MSGS_PACKAGE}" "${msg_link}"; fi
    (cd "${MOSIM_ROS2_WS}" && colcon build --packages-select mosim_msgs > "${RESULT_DIR}/mosim_msgs_colcon.stdout.log" 2> "${RESULT_DIR}/mosim_msgs_colcon.stderr.log")
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
controller_pid=""
pre_unpause_fixture_pid=""
camera_follow_pid=""
cleanup() {
  terminate_process_tree "${camera_follow_pid}" 2
  terminate_process_tree "${pre_unpause_fixture_pid}" 2
  terminate_process_tree "${controller_pid}" 2
  terminate_process_tree "${truth_recorder_pid}" 2
  terminate_process_tree "${adapter_pid}" 2
  terminate_process_tree "${bridge_pid}" 2
  terminate_process_tree "${gz_pid}" 3
}
trap cleanup EXIT

if [[ "${GAZEBO_GUI_REVIEW}" == "1" ]]; then
  gazebo_gui_run_flags=()
  if [[ -n "${GUI_CONFIG}" ]]; then
    gazebo_gui_run_flags+=("--gui-config" "${GUI_CONFIG}")
  fi
  if command -v gz >/dev/null 2>&1; then
    gz sim --render-engine "${GAZEBO_RENDER_ENGINE_SERVER}" -v "${GAZEBO_GUI_VERBOSE}" "${gazebo_gui_run_flags[@]}" "${WORLD}" > "${RESULT_DIR}/gazebo.stdout.log" 2> "${RESULT_DIR}/gazebo.stderr.log" &
  else
    ign gazebo --render-engine "${GAZEBO_RENDER_ENGINE_SERVER}" -v "${GAZEBO_GUI_VERBOSE}" "${gazebo_gui_run_flags[@]}" "${WORLD}" > "${RESULT_DIR}/gazebo.stdout.log" 2> "${RESULT_DIR}/gazebo.stderr.log" &
  fi
else
  if command -v gz >/dev/null 2>&1; then
    gz sim -s --headless-rendering --render-engine-server "${GAZEBO_RENDER_ENGINE_SERVER}" "${WORLD}" > "${RESULT_DIR}/gazebo.stdout.log" 2> "${RESULT_DIR}/gazebo.stderr.log" &
  else
    ign gazebo -s --headless-rendering --render-engine-server "${GAZEBO_RENDER_ENGINE_SERVER}" "${WORLD}" > "${RESULT_DIR}/gazebo.stdout.log" 2> "${RESULT_DIR}/gazebo.stderr.log" &
  fi
fi
gz_pid="$!"
sleep 4

if [[ "${GAZEBO_GUI_REVIEW}" == "1" ]]; then
  python3 "${GAZEBO_CAMERA_FOLLOW_SCRIPT}" \
    --target "${GAZEBO_CAMERA_FOLLOW_TARGET}" \
    --offset-x-m "${GAZEBO_CAMERA_FOLLOW_OFFSET_X_M}" \
    --offset-y-m "${GAZEBO_CAMERA_FOLLOW_OFFSET_Y_M}" \
    --offset-z-m "${GAZEBO_CAMERA_FOLLOW_OFFSET_Z_M}" \
    --min-dist-m "${GAZEBO_CAMERA_FOLLOW_MIN_DIST_M}" \
    --max-dist-m "${GAZEBO_CAMERA_FOLLOW_MAX_DIST_M}" \
    --inherit-yaw \
    --use-model-frame \
    --start-delay-s 0 \
    --repeat "${GAZEBO_CAMERA_FOLLOW_REPEAT}" \
    --interval-s "${GAZEBO_CAMERA_FOLLOW_INTERVAL_S}" \
    --timeout-s 1.5 \
    --summary-json "${RESULT_DIR}/gazebo_camera_follow_request.json" \
    > "${RESULT_DIR}/gazebo_camera_follow.stdout.log" \
    2> "${RESULT_DIR}/gazebo_camera_follow.stderr.log" &
  camera_follow_pid="$!"
fi

ros2 run ros_gz_bridge parameter_bridge "${ROS_ACTUATOR_TOPIC}@actuator_msgs/msg/Actuators@gz.msgs.Actuators" > "${RESULT_DIR}/ros_gz_bridge.stdout.log" 2> "${RESULT_DIR}/ros_gz_bridge.stderr.log" &
bridge_pid="$!"
sleep 3

python3 "${CONTROLLER_NODE_SCRIPT}" --input-topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" --output-topic "${ROS_ACTUATOR_TOPIC}" --vehicle-id sunray150 --max-messages 0 --max-command-age-s 2.0 --output-json "${RESULT_DIR}/controller_output_adapter_node.json" --trace-jsonl "${RESULT_DIR}/controller_output_adapter_node.trace.jsonl" > "${RESULT_DIR}/controller_output_node.stdout.log" 2> "${RESULT_DIR}/controller_output_node.stderr.log" &
adapter_pid="$!"
sleep 2

python3 "$(yaml_get ros2.controller_adapter.fixture_publisher_script)" --topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" --vehicle-id sunray150 --command-type normalized_motor_speed --command "${HOVER_COMMAND}" "${HOVER_COMMAND}" "${HOVER_COMMAND}" "${HOVER_COMMAND}" --rate-hz 20 --times 40 --mode pre_unpause_hover_guard --backend pre_unpause_hover_guard --source-authority bounded_takeoff_hover_land_pre_unpause_guard --output-json "${RESULT_DIR}/pre_unpause_hover_fixture.json" > "${RESULT_DIR}/pre_unpause_hover_fixture.stdout.log" 2> "${RESULT_DIR}/pre_unpause_hover_fixture.stderr.log" &
pre_unpause_fixture_pid="$!"
sleep 1

truth_timeout="${TRUTH_TIMEOUT_SECONDS}"
python3 "${GAZEBO_TRUTH_RECORDER_SCRIPT}" --output-jsonl "${GAZEBO_TRUTH_POSE_JSONL}" --summary-json "${GAZEBO_TRUTH_POSE_SUMMARY_JSON}" --topic "${GAZEBO_TRUTH_TOPIC}" --model-name "${GAZEBO_TRUTH_MODEL_NAME}" --frame-id "${GAZEBO_TRUTH_FRAME_ID}" --timeout-seconds "${truth_timeout}" --target-samples "${TRUTH_TARGET_SAMPLES}" --startup-delay-seconds 0 --sample-timeout-seconds 25 --sleep-seconds 0.05 > "${RESULT_DIR}/gazebo_truth_pose_recorder.stdout.log" 2> "${RESULT_DIR}/gazebo_truth_pose_recorder.stderr.log" &
truth_recorder_pid="$!"
sleep 1

bash -lc "timeout '${truth_timeout}' ign topic -e -t '${GAZEBO_TRUTH_TOPIC}' | python3 '${STAGE_CONTROLLER_SCRIPT}' --input-topic-name '${GAZEBO_TRUTH_TOPIC}' --output-topic '${ROS_CONTROLLER_OUTPUT_TOPIC}' --vehicle-id sunray150 --model-name '${GAZEBO_TRUTH_MODEL_NAME}' --frame-id '${GAZEBO_TRUTH_FRAME_ID}' --hover-altitude-m '${HOVER_ALTITUDE_M}' --landed-altitude-m '${LANDED_ALTITUDE_M}' --takeoff-duration-s '${TAKEOFF_DURATION_S}' --hover-duration-s '${HOVER_DURATION_S}' --land-duration-s '${LAND_DURATION_S}' --settle-duration-s '${SETTLE_DURATION_S}' --hover-command '${HOVER_COMMAND}' --command-max '${COMMAND_MAX}' --land-command-max '${LAND_COMMAND_MAX}' --output-json '${CONTROLLER_JSON}' --trace-jsonl '${CONTROLLER_TRACE}' ${STAGE_CONTROLLER_EXTRA_ARGS}" > "${RESULT_DIR}/takeoff_hover_land_controller.stdout.log" 2> "${RESULT_DIR}/takeoff_hover_land_controller.stderr.log" &
controller_pid="$!"
sleep 2

ign service -s "/world/${GAZEBO_WORLD_NAME}/control" --reqtype ignition.msgs.WorldControl --reptype ignition.msgs.Boolean --timeout 2000 --req "pause: false" > "${RESULT_DIR}/gazebo_world_control_unpause_response.txt" 2> "${RESULT_DIR}/gazebo_world_control_unpause.stderr.txt" || true
if wait "${pre_unpause_fixture_pid}"; then write_rc "${RESULT_DIR}/pre_unpause_hover_fixture.rc" 0; else write_rc "${RESULT_DIR}/pre_unpause_hover_fixture.rc" "$?"; fi
pre_unpause_fixture_pid=""

if wait "${controller_pid}"; then write_rc "${RESULT_DIR}/takeoff_hover_land_controller.rc" 0; else write_rc "${RESULT_DIR}/takeoff_hover_land_controller.rc" "$?"; fi
controller_pid=""
if wait "${truth_recorder_pid}"; then write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" 0; else write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" "$?"; fi
truth_recorder_pid=""

eval_rc=0
python3 "${EVAL_SCRIPT}" --controller-report-json "${CONTROLLER_JSON}" --controller-trace-jsonl "${CONTROLLER_TRACE}" --adapter-trace-jsonl "${RESULT_DIR}/controller_output_adapter_node.trace.jsonl" --truth-pose-jsonl "${GAZEBO_TRUTH_POSE_JSONL}" --truth-summary-json "${GAZEBO_TRUTH_POSE_SUMMARY_JSON}" --output-json "${EVAL_JSON}" --hover-altitude-m "${HOVER_ALTITUDE_M}" --min-duration-s 10.0 --min-takeoff-peak-z-m 0.50 --max-hover-abs-z-error-m 0.30 --max-final-landed-z-m 0.35 > "${RESULT_DIR}/takeoff_hover_land_eval.stdout.log" 2> "${RESULT_DIR}/takeoff_hover_land_eval.stderr.log" || eval_rc="$?"
write_rc "${RESULT_DIR}/takeoff_hover_land_eval.rc" "${eval_rc}"

python3 - <<PY
import json
from pathlib import Path
result_dir=Path("${RESULT_DIR}")
eval_path=Path("${EVAL_JSON}")
eval_report=json.loads(eval_path.read_text(encoding="utf-8")) if eval_path.exists() else {}
passed=bool(eval_report.get("gate_passed"))
blockers=list(eval_report.get("blockers", []))
runtime={
  "schema":"mosim.gazebo_takeoff_hover_land_runtime_status.v1",
  "status":"runtime_passed" if passed else "runtime_blocked",
  "gate_passed":passed,
  "scenario":"${SCENARIO}",
  "result_dir":"${RESULT_DIR}",
  "controller":"takeoff_hover_land_controller.json",
  "controller_trace":"takeoff_hover_land_controller_trace.jsonl",
  "adapter_trace":"controller_output_adapter_node.trace.jsonl",
  "truth_recording":"GAZEBO_TRUTH_POSE_RECORDING.json",
  "eval":"GAZEBO_TAKEOFF_HOVER_LAND_EVAL.json",
  "blockers":blockers,
  "claim_boundary":[
    "bounded Gazebo plant sanity only: takeoff, hover, land",
    "no MWORKS controller deployment, competition controller performance, planner_ready, final closed_loop acceptance, or multi-UAV readiness is claimed"
  ]
}
Path("${RUNTIME_STATUS_JSON}").write_text(json.dumps(runtime, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
manifest={
  "schema_version":"mosim.run_manifest.v1",
  "run_id":"sunray150_takeoff_hover_land_plant_sanity",
  "objective":"prove accepted Gazebo plant can take off, hover, and land with a simple stable controller",
  "scene_id":"sunray150_single_uav_competition_light",
  "vehicle_id":"sunray150_assembled",
  "quality_status":"passed" if passed else "blocked",
  "artifacts":{"runtime_status":"${RUNTIME_STATUS_JSON}","eval":"${EVAL_JSON}","controller":"${CONTROLLER_JSON}","truth_summary":"${GAZEBO_TRUTH_POSE_SUMMARY_JSON}"},
  "blockers":blockers,
  "not_claimed":["MWORKS controller deployment","competition controller performance","planner_ready","final_closed_loop_acceptance","multi_uav_readiness"]
}
Path("${RUN_MANIFEST}").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
if passed:
    p=Path("${BLOCKER}")
    if p.exists(): p.unlink()
else:
    Path("${BLOCKER}").write_text(json.dumps({"schema":"mosim.gazebo_takeoff_hover_land_blocker.v1","status":"blocked","runtime_status":"${RUNTIME_STATUS_JSON}","blockers":blockers}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
PY

if [[ -f "${BLOCKER}" ]]; then
  echo "${BLOCKER}"
else
  echo "${RUN_MANIFEST}"
fi
