#!/usr/bin/env bash
# run_sunray150_hover_hold_closed_loop: bounded single-UAV hover-hold gate.
# Expected eval artifact: GAZEBO_HOVER_HOLD_CLOSED_LOOP_EVAL.json.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
GAZEBO_ENV_SCRIPT="${GAZEBO_ENV_SCRIPT:-${PROJECT_ROOT}/Scripts/gazebo/setup_gazebo_wsl_env.sh}"
if [[ -f "${GAZEBO_ENV_SCRIPT}" ]]; then
  # shellcheck disable=SC1090
  source "${GAZEBO_ENV_SCRIPT}"
fi
SCENARIO="${SCENARIO:-Config/scenarios/system/sunray150_single_uav_competition_light.yaml}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/sunray150_gazebo_ros2_hover_hold_closed_loop_pre_acceptance}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
ROS_LOG_DIR="${ROS_LOG_DIR:-${PROJECT_ROOT}/Results/tmp/ros_logs}"
MOSIM_ROS2_WS="${MOSIM_ROS2_WS:-${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs}"
BUILD_MOSIM_ROS2_MSGS="${BUILD_MOSIM_ROS2_MSGS:-0}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-25}"
GAZEBO_RENDER_ENGINE_SERVER="${GAZEBO_RENDER_ENGINE_SERVER:-ogre}"
DRY_RUN="${DRY_RUN:-0}"

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
    "claim_boundary": "world-control evidence only; this does not prove hover, final closed_loop acceptance, planner_ready, or controller performance",
}
Path("${RESULT_DIR}/gazebo_world_control.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
}

unpause_gazebo_world() {
  local service="/world/${GAZEBO_WORLD_NAME:-yunzong_planning_test_sunray150_assembled}/control"
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
GAZEBO_WORLD_NAME="$(python3 - <<PY
import json
import re
data=json.loads('''${scenario_json}''')
topic=data["ros2"].get("gazebo_truth_pose", {}).get("topic", "/world/yunzong_planning_test_sunray150_assembled/dynamic_pose/info")
match=re.match(r"^/world/([^/]+)/", topic)
print(match.group(1) if match else "yunzong_planning_test_sunray150_assembled")
PY
)"
GAZEBO_RESOURCE_PATHS="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
paths=data.get("gazebo", {}).get("resource_paths", ["Config/gazebo/models"])
if isinstance(paths, str):
    paths=[paths]
print(":".join(str(path).strip("/") for path in paths if str(path).strip()))
PY
)"
if declare -F mosim_gazebo_apply_resource_paths >/dev/null 2>&1; then
  mosim_gazebo_apply_resource_paths "${GAZEBO_RESOURCE_PATHS}"
else
  export GZ_SIM_RESOURCE_PATH="${PROJECT_ROOT}/Config/gazebo/models"
  export IGN_GAZEBO_RESOURCE_PATH="${PROJECT_ROOT}/Config/gazebo/models"
fi
ROS_CONTROLLER_OUTPUT_TOPIC="$(yaml_get ros2.controller_adapter.input_topic)"
ROS_ACTUATOR_TOPIC="$(yaml_get ros2.controller_adapter.ros_actuator_topic)"
GZ_ACTUATOR_TOPIC="$(yaml_get ros2.controller_adapter.gz_actuator_topic)"
CONTROLLER_NODE_SCRIPT="$(yaml_get ros2.controller_adapter.node_script)"
CONTROLLER_FIXTURE_SCRIPT="$(yaml_get ros2.controller_adapter.fixture_publisher_script)"
MOSIM_MSGS_PACKAGE="$(yaml_get ros2.controller_adapter.message_package)"
GAZEBO_TRUTH_TOPIC="$(yaml_get ros2.gazebo_truth_pose.topic)"
GAZEBO_TRUTH_MODEL_NAME="$(yaml_get ros2.gazebo_truth_pose.model_name)"
GAZEBO_TRUTH_FRAME_ID="$(yaml_get ros2.gazebo_truth_pose.frame_id)"
GAZEBO_TRUTH_RECORDER_SCRIPT="$(yaml_get ros2.gazebo_truth_pose.recorder_script)"
GAZEBO_TRUTH_RECORDER_TIMEOUT_SECONDS="$(python3 - <<PY
import json, math
data=json.loads('''${scenario_json}''')
pose=data["ros2"].get("gazebo_truth_pose", {})
default=int(math.ceil(float("${TIMEOUT_SECONDS}") + 2.0))
print(pose.get("recorder_timeout_seconds", default))
PY
)"
GAZEBO_TRUTH_SAMPLE_TIMEOUT_SECONDS="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
pose=data["ros2"].get("gazebo_truth_pose", {})
print(pose.get("sample_timeout_seconds", 25))
PY
)"
HOVER_CONTROLLER_SCRIPT="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.controller_script)"
HOVER_EVAL_SCRIPT="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.eval_script)"
HOVER_TARGET_ALTITUDE_M="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.target_altitude_m)"
HOVER_COMMAND="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.hover_command)"
HOVER_KP_Z="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.kp_z)"
HOVER_KD_Z="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.kd_z)"
HOVER_KI_Z="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.ki_z)"
HOVER_KP_ROLL="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.kp_roll)"
HOVER_KD_ROLL="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.kd_roll)"
HOVER_KP_PITCH="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.kp_pitch)"
HOVER_KD_PITCH="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.kd_pitch)"
HOVER_KP_YAW="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.kp_yaw)"
HOVER_KD_YAW="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.kd_yaw)"
HOVER_KP_X="$(yaml_get_or_default ros2.single_uav_hover_hold_closed_loop_pre_acceptance.kp_x 1.2e-4)"
HOVER_KD_X="$(yaml_get_or_default ros2.single_uav_hover_hold_closed_loop_pre_acceptance.kd_x 2.0e-4)"
HOVER_KP_Y="$(yaml_get_or_default ros2.single_uav_hover_hold_closed_loop_pre_acceptance.kp_y 1.2e-4)"
HOVER_KD_Y="$(yaml_get_or_default ros2.single_uav_hover_hold_closed_loop_pre_acceptance.kd_y 2.0e-4)"
HOVER_XY_CONTROL_SIGN="$(yaml_get_or_default ros2.single_uav_hover_hold_closed_loop_pre_acceptance.xy_control_sign -1.0)"
HOVER_ROLL_CONTROL_SIGN="$(yaml_get_or_default ros2.single_uav_hover_hold_closed_loop_pre_acceptance.roll_control_sign "${HOVER_XY_CONTROL_SIGN}")"
HOVER_PITCH_CONTROL_SIGN="$(yaml_get_or_default ros2.single_uav_hover_hold_closed_loop_pre_acceptance.pitch_control_sign "${HOVER_XY_CONTROL_SIGN}")"
HOVER_LOW_ALTITUDE_XY_SCALE_START_M="$(yaml_get_or_default ros2.single_uav_hover_hold_closed_loop_pre_acceptance.low_altitude_xy_scale_start_m 0.35)"
HOVER_LOW_ALTITUDE_XY_SCALE_FULL_M="$(yaml_get_or_default ros2.single_uav_hover_hold_closed_loop_pre_acceptance.low_altitude_xy_scale_full_m 0.85)"
HOVER_XY_ERROR_LIMIT_M="$(yaml_get_or_default ros2.single_uav_hover_hold_closed_loop_pre_acceptance.xy_error_limit_m 0.8)"
HOVER_XY_VELOCITY_ERROR_LIMIT_MPS="$(yaml_get_or_default ros2.single_uav_hover_hold_closed_loop_pre_acceptance.xy_velocity_error_limit_mps 0.5)"
HOVER_INTEGRAL_LIMIT_M_S="$(yaml_get_or_default ros2.single_uav_hover_hold_closed_loop_pre_acceptance.integral_limit_m_s 1.0)"
HOVER_ATTITUDE_COMMAND_LIMIT="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.attitude_command_limit)"
HOVER_COMMAND_MIN="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.command_min)"
HOVER_COMMAND_MAX="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.command_max)"
HOVER_DURATION_S="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.duration_s)"
HOVER_PUBLISH_HZ="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.publish_rate_hz)"
HOVER_TARGET_ALTITUDE_M="${HOVER_TARGET_ALTITUDE_M_OVERRIDE:-${HOVER_TARGET_ALTITUDE_M}}"
HOVER_COMMAND="${HOVER_COMMAND_OVERRIDE:-${HOVER_COMMAND}}"
HOVER_KP_Z="${HOVER_KP_Z_OVERRIDE:-${HOVER_KP_Z}}"
HOVER_KD_Z="${HOVER_KD_Z_OVERRIDE:-${HOVER_KD_Z}}"
HOVER_KI_Z="${HOVER_KI_Z_OVERRIDE:-${HOVER_KI_Z}}"
HOVER_KP_ROLL="${HOVER_KP_ROLL_OVERRIDE:-${HOVER_KP_ROLL}}"
HOVER_KD_ROLL="${HOVER_KD_ROLL_OVERRIDE:-${HOVER_KD_ROLL}}"
HOVER_KP_PITCH="${HOVER_KP_PITCH_OVERRIDE:-${HOVER_KP_PITCH}}"
HOVER_KD_PITCH="${HOVER_KD_PITCH_OVERRIDE:-${HOVER_KD_PITCH}}"
HOVER_KP_YAW="${HOVER_KP_YAW_OVERRIDE:-${HOVER_KP_YAW}}"
HOVER_KD_YAW="${HOVER_KD_YAW_OVERRIDE:-${HOVER_KD_YAW}}"
HOVER_ATTITUDE_COMMAND_LIMIT="${HOVER_ATTITUDE_COMMAND_LIMIT_OVERRIDE:-${HOVER_ATTITUDE_COMMAND_LIMIT}}"
HOVER_COMMAND_MIN="${HOVER_COMMAND_MIN_OVERRIDE:-${HOVER_COMMAND_MIN}}"
HOVER_COMMAND_MAX="${HOVER_COMMAND_MAX_OVERRIDE:-${HOVER_COMMAND_MAX}}"
HOVER_DURATION_S="${HOVER_DURATION_S_OVERRIDE:-${HOVER_DURATION_S}}"
HOVER_PUBLISH_HZ="${HOVER_PUBLISH_HZ_OVERRIDE:-${HOVER_PUBLISH_HZ}}"
HOVER_START_GAZEBO_PAUSED="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
cfg=data["ros2"]["single_uav_hover_hold_closed_loop_pre_acceptance"]
print("1" if cfg.get("start_gazebo_paused", False) else "0")
PY
)"
HOVER_UNPAUSE_AFTER_CONTROLLER_READY="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
cfg=data["ros2"]["single_uav_hover_hold_closed_loop_pre_acceptance"]
print("1" if cfg.get("unpause_after_controller_ready", False) else "0")
PY
)"
HOVER_EVAL_OUTPUT="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.output_json)"
HOVER_MIN_CONTROLLER_SAMPLES="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.evaluation_thresholds.min_controller_samples)"
HOVER_MIN_ADAPTER_SAMPLES="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.evaluation_thresholds.min_adapter_samples)"
HOVER_MIN_TRUTH_SAMPLES="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.evaluation_thresholds.min_truth_samples)"
HOVER_MIN_DURATION_S="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.evaluation_thresholds.min_duration_s)"
HOVER_MAX_FINAL_ABS_Z_ERROR_M="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.evaluation_thresholds.max_final_abs_z_error_m)"
HOVER_MAX_ABS_Z_ERROR_M="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.evaluation_thresholds.max_abs_z_error_m)"
HOVER_MIN_ALLOWED_Z_M="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.evaluation_thresholds.min_allowed_z_m)"
HOVER_MAX_ALLOWED_Z_M="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.evaluation_thresholds.max_allowed_z_m)"
HOVER_MAX_XY_DISTANCE_M="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.evaluation_thresholds.max_xy_distance_m)"
HOVER_MAX_TILT_RAD="$(yaml_get ros2.single_uav_hover_hold_closed_loop_pre_acceptance.evaluation_thresholds.max_tilt_rad)"

RUN_MANIFEST="${RESULT_DIR}/RUN_MANIFEST.json"
RUNTIME_STATUS_JSON="${RESULT_DIR}/RUNTIME_STATUS.json"
PREFLIGHT_JSON="${RESULT_DIR}/PREFLIGHT.json"
BLOCKER="${RESULT_DIR}/BLOCKER.json"
GAZEBO_TRUTH_POSE_JSONL="${RESULT_DIR}/gazebo_truth_pose.jsonl"
GAZEBO_TRUTH_POSE_SUMMARY_JSON="${RESULT_DIR}/GAZEBO_TRUTH_POSE_RECORDING.json"
HOVER_CONTROLLER_JSON="${RESULT_DIR}/hover_hold_controller.json"
HOVER_CONTROLLER_TRACE="${RESULT_DIR}/hover_hold_controller_trace.jsonl"
HOVER_EVAL_JSON="${RESULT_DIR}/${HOVER_EVAL_OUTPUT}"
HOVER_PREUNPAUSE_FIXTURE_JSON="${RESULT_DIR}/pre_unpause_hover_fixture.json"

missing_files=()
for path in "${SCENARIO}" "${WORLD}" "${CONTROLLER_NODE_SCRIPT}" "${CONTROLLER_FIXTURE_SCRIPT}" "${MOSIM_MSGS_PACKAGE}" "${GAZEBO_TRUTH_RECORDER_SCRIPT}" "${HOVER_CONTROLLER_SCRIPT}" "${HOVER_EVAL_SCRIPT}"; do
  if [[ "${path}" == "${MOSIM_MSGS_PACKAGE}" ]]; then
    [[ -d "${path}" ]] || missing_files+=("${path}")
  else
    [[ -f "${path}" ]] || missing_files+=("${path}")
  fi
done

if [[ -f "${ROS_SETUP}" ]]; then
  set +u
  # shellcheck disable=SC1090
  source "${ROS_SETUP}"
  set -u
fi

ensure_mosim_msgs_sourced() {
  local setup_path="${MOSIM_ROS2_WS}/install/setup.bash"
  if [[ ! -f "${setup_path}" || "${BUILD_MOSIM_ROS2_MSGS}" == "1" ]]; then
    mkdir -p "${MOSIM_ROS2_WS}/src"
    local msg_link="${MOSIM_ROS2_WS}/src/mosim_msgs"
    if [[ -L "${msg_link}" || -f "${msg_link}" ]]; then
      rm -f "${msg_link}"
    fi
    if [[ ! -e "${msg_link}" ]]; then
      ln -s "${PROJECT_ROOT}/${MOSIM_MSGS_PACKAGE}" "${msg_link}"
    fi
    (
      cd "${MOSIM_ROS2_WS}"
      colcon build --packages-select mosim_msgs \
        > "${RESULT_DIR}/mosim_msgs_colcon.stdout.log" \
        2> "${RESULT_DIR}/mosim_msgs_colcon.stderr.log"
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
  if ! ensure_mosim_msgs_sourced; then
    blockers+=("mosim_msgs_colcon_build_or_source_failed")
  fi
fi
if [[ -z "$(ros_pkg_prefix mosim_msgs)" ]]; then
  blockers+=("missing_ros2_package:mosim_msgs")
fi

missing_files_json="$(printf '%s\n' "${missing_files[@]:-}" | json_array_from_lines)"
blockers_json="$(printf '%s\n' "${blockers[@]:-}" | json_array_from_lines)"

cat > "${PREFLIGHT_JSON}" <<JSON
{
  "schema": "mosim.gazebo_hover_hold_closed_loop_preflight.v1",
  "scenario": "${SCENARIO}",
  "dry_run": $([[ "${DRY_RUN}" == "1" ]] && echo true || echo false),
  "world": "${WORLD}",
  "result_dir": "${RESULT_DIR}",
  "gazebo_resource_paths": "${GAZEBO_RESOURCE_PATHS}",
  "gz_sim_resource_path": "${GZ_SIM_RESOURCE_PATH:-}",
  "ign_gazebo_resource_path": "${IGN_GAZEBO_RESOURCE_PATH:-}",
  "mesa_d3d12_default_adapter_name": "${MESA_D3D12_DEFAULT_ADAPTER_NAME:-}",
  "glx_vendor_library_name": "${__GLX_VENDOR_LIBRARY_NAME:-}",
  "libgl_always_software": "${LIBGL_ALWAYS_SOFTWARE:-}",
  "mosim_gazebo_inherit_resource_paths": "${MOSIM_GAZEBO_INHERIT_RESOURCE_PATHS:-0}",
  "controller_output_topic": "${ROS_CONTROLLER_OUTPUT_TOPIC}",
  "actuator_topic": "${ROS_ACTUATOR_TOPIC}",
  "gazebo_truth_topic": "${GAZEBO_TRUTH_TOPIC}",
  "target_altitude_m": ${HOVER_TARGET_ALTITUDE_M},
  "hover_command": ${HOVER_COMMAND},
  "command_bounds": [${HOVER_COMMAND_MIN}, ${HOVER_COMMAND_MAX}],
  "attitude_gains": {
    "kp_roll": ${HOVER_KP_ROLL},
    "kd_roll": ${HOVER_KD_ROLL},
    "kp_pitch": ${HOVER_KP_PITCH},
    "kd_pitch": ${HOVER_KD_PITCH},
    "kp_yaw": ${HOVER_KP_YAW},
    "kd_yaw": ${HOVER_KD_YAW},
    "attitude_command_limit": ${HOVER_ATTITUDE_COMMAND_LIMIT}
  },
  "duration_s": ${HOVER_DURATION_S},
  "start_gazebo_paused": "${HOVER_START_GAZEBO_PAUSED}",
  "unpause_after_controller_ready": "${HOVER_UNPAUSE_AFTER_CONTROLLER_READY}",
  "pre_unpause_hover_fixture": "enabled_when_start_paused",
  "missing_project_files": ${missing_files_json},
  "blockers": ${blockers_json},
  "claim_boundary": "preflight only; no hover, final closed_loop, planner_ready, controller performance, or multi-UAV readiness is claimed"
}
JSON

if [[ "${DRY_RUN}" == "1" || "${#blockers[@]}" -gt 0 ]]; then
  cat > "${RUNTIME_STATUS_JSON}" <<JSON
{
  "schema": "mosim.gazebo_hover_hold_closed_loop_runtime_status.v1",
  "status": "preflight_blocked",
  "gate_passed": false,
  "preflight": "${PREFLIGHT_JSON}",
  "blockers": ${blockers_json},
  "claim_boundary": "No Gazebo process, ROS2 graph, ControllerOutput feedback loop, actuator echo, or hover-hold evidence is claimed."
}
JSON
  cat > "${BLOCKER}" <<JSON
{
  "schema": "mosim.gazebo_hover_hold_closed_loop_blocker.v1",
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
adapter_pid=""
truth_recorder_pid=""
controller_pid=""
controller_echo_pid=""
ros_actuator_echo_pid=""
gz_actuator_echo_pid=""
cleanup() {
  terminate_process_tree "${gz_actuator_echo_pid}" 1
  terminate_process_tree "${ros_actuator_echo_pid}" 1
  terminate_process_tree "${controller_echo_pid}" 1
  terminate_process_tree "${controller_pid}" 2
  terminate_process_tree "${truth_recorder_pid}" 2
  terminate_process_tree "${adapter_pid}" 2
  terminate_process_tree "${bridge_pid}" 2
  terminate_process_tree "${gz_pid}" 3
}
trap cleanup EXIT

run_flag=()
if [[ "${HOVER_START_GAZEBO_PAUSED}" != "1" ]]; then
  run_flag=(-r)
fi

if [[ "${gazebo_sim_cli_kind}" == "gz" ]]; then
  "${gazebo_sim_cli_path}" sim -s "${run_flag[@]}" --headless-rendering --render-engine-server "${GAZEBO_RENDER_ENGINE_SERVER}" "${WORLD}" \
    > "${RESULT_DIR}/gazebo.stdout.log" \
    2> "${RESULT_DIR}/gazebo.stderr.log" &
else
  "${gazebo_sim_cli_path}" gazebo -s "${run_flag[@]}" --headless-rendering --render-engine-server "${GAZEBO_RENDER_ENGINE_SERVER}" "${WORLD}" \
    > "${RESULT_DIR}/gazebo.stdout.log" \
    2> "${RESULT_DIR}/gazebo.stderr.log" &
fi
gz_pid="$!"
sleep 4

ros2 run ros_gz_bridge parameter_bridge \
  "${ROS_ACTUATOR_TOPIC}@actuator_msgs/msg/Actuators@gz.msgs.Actuators" \
  > "${RESULT_DIR}/ros_gz_bridge.stdout.log" \
  2> "${RESULT_DIR}/ros_gz_bridge.stderr.log" &
bridge_pid="$!"
sleep 3

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
adapter_pid="$!"
sleep 2

truth_timeout="$(python3 - <<PY
import math
print(max(int(math.ceil(float("${HOVER_DURATION_S}") + 8.0)), int(float("${GAZEBO_TRUTH_RECORDER_TIMEOUT_SECONDS}"))))
PY
)"
truth_target_samples="$(python3 - <<PY
import math
print(max(120, int(math.ceil(float("${HOVER_DURATION_S}") * 12.0))))
PY
)"
python3 "${GAZEBO_TRUTH_RECORDER_SCRIPT}" \
  --output-jsonl "${GAZEBO_TRUTH_POSE_JSONL}" \
  --summary-json "${GAZEBO_TRUTH_POSE_SUMMARY_JSON}" \
  --topic "${GAZEBO_TRUTH_TOPIC}" \
  --model-name "${GAZEBO_TRUTH_MODEL_NAME}" \
  --frame-id "${GAZEBO_TRUTH_FRAME_ID}" \
  --timeout-seconds "${truth_timeout}" \
  --target-samples "${truth_target_samples}" \
  --startup-delay-seconds 0 \
  --sample-timeout-seconds "${GAZEBO_TRUTH_SAMPLE_TIMEOUT_SECONDS}" \
  --sleep-seconds 0.05 \
  > "${RESULT_DIR}/gazebo_truth_pose_recorder.stdout.log" \
  2> "${RESULT_DIR}/gazebo_truth_pose_recorder.stderr.log" &
truth_recorder_pid="$!"
sleep 1

bash -lc "timeout '${truth_timeout}' ign topic -e -t '${GAZEBO_TRUTH_TOPIC}' | python3 '${HOVER_CONTROLLER_SCRIPT}' --input-topic-name '${GAZEBO_TRUTH_TOPIC}' --output-topic '${ROS_CONTROLLER_OUTPUT_TOPIC}' --vehicle-id sunray150 --model-name '${GAZEBO_TRUTH_MODEL_NAME}' --frame-id '${GAZEBO_TRUTH_FRAME_ID}' --target-altitude-m '${HOVER_TARGET_ALTITUDE_M}' --hover-command '${HOVER_COMMAND}' --kp-z '${HOVER_KP_Z}' --kd-z '${HOVER_KD_Z}' --ki-z '${HOVER_KI_Z}' --kp-x '${HOVER_KP_X}' --kd-x '${HOVER_KD_X}' --kp-y '${HOVER_KP_Y}' --kd-y '${HOVER_KD_Y}' --kp-roll '${HOVER_KP_ROLL}' --kd-roll '${HOVER_KD_ROLL}' --kp-pitch '${HOVER_KP_PITCH}' --kd-pitch '${HOVER_KD_PITCH}' --kp-yaw '${HOVER_KP_YAW}' --kd-yaw '${HOVER_KD_YAW}' --xy-control-sign '${HOVER_XY_CONTROL_SIGN}' --roll-control-sign '${HOVER_ROLL_CONTROL_SIGN}' --pitch-control-sign '${HOVER_PITCH_CONTROL_SIGN}' --low-altitude-xy-scale-start-m '${HOVER_LOW_ALTITUDE_XY_SCALE_START_M}' --low-altitude-xy-scale-full-m '${HOVER_LOW_ALTITUDE_XY_SCALE_FULL_M}' --xy-error-limit-m '${HOVER_XY_ERROR_LIMIT_M}' --xy-velocity-error-limit-mps '${HOVER_XY_VELOCITY_ERROR_LIMIT_MPS}' --integral-limit-m-s '${HOVER_INTEGRAL_LIMIT_M_S}' --attitude-command-limit '${HOVER_ATTITUDE_COMMAND_LIMIT}' --command-min '${HOVER_COMMAND_MIN}' --command-max '${HOVER_COMMAND_MAX}' --max-publish-hz '${HOVER_PUBLISH_HZ}' --duration-s '${HOVER_DURATION_S}' --output-json '${HOVER_CONTROLLER_JSON}' --trace-jsonl '${HOVER_CONTROLLER_TRACE}'" \
  > "${RESULT_DIR}/hover_hold_controller.stdout.log" \
  2> "${RESULT_DIR}/hover_hold_controller.stderr.log" &
controller_pid="$!"
sleep 2

if [[ "${HOVER_START_GAZEBO_PAUSED}" == "1" ]]; then
  python3 "${CONTROLLER_FIXTURE_SCRIPT}" \
    --topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" \
    --vehicle-id "sunray150" \
    --command-type "normalized_motor_speed" \
    --command "${HOVER_COMMAND}" "${HOVER_COMMAND}" "${HOVER_COMMAND}" "${HOVER_COMMAND}" \
    --rate-hz 20 \
    --times 40 \
    --backend "pre_unpause_hover_fixture" \
    --source-authority "bounded_pre_unpause_hover_hold_startup_guard" \
    --output-json "${HOVER_PREUNPAUSE_FIXTURE_JSON}" \
    > "${RESULT_DIR}/pre_unpause_hover_fixture.stdout.log" \
    2> "${RESULT_DIR}/pre_unpause_hover_fixture.stderr.log" || true
fi

controller_key="$(topic_key "${ROS_CONTROLLER_OUTPUT_TOPIC}")"
ros_actuator_key="$(topic_key "${ROS_ACTUATOR_TOPIC}")"
gz_actuator_key="$(topic_key "${GZ_ACTUATOR_TOPIC}")"
timeout "${TIMEOUT_SECONDS}" ros2 topic echo --once "${ROS_CONTROLLER_OUTPUT_TOPIC}" "mosim_msgs/msg/ControllerOutput" \
  > "${RESULT_DIR}/topic_${controller_key}_once.txt" \
  2> "${RESULT_DIR}/topic_${controller_key}_once.stderr.txt" &
controller_echo_pid="$!"
timeout "${TIMEOUT_SECONDS}" ros2 topic echo --once "${ROS_ACTUATOR_TOPIC}" "actuator_msgs/msg/Actuators" \
  > "${RESULT_DIR}/topic_${ros_actuator_key}_once.txt" \
  2> "${RESULT_DIR}/topic_${ros_actuator_key}_once.stderr.txt" &
ros_actuator_echo_pid="$!"
timeout "${TIMEOUT_SECONDS}" ign topic -e -t "${GZ_ACTUATOR_TOPIC}" -n 1 \
  > "${RESULT_DIR}/gz_topic_${gz_actuator_key}_once.txt" \
  2> "${RESULT_DIR}/gz_topic_${gz_actuator_key}_once.stderr.txt" &
gz_actuator_echo_pid="$!"

if [[ "${HOVER_UNPAUSE_AFTER_CONTROLLER_READY}" == "1" ]]; then
  unpause_gazebo_world || true
fi

if wait "${controller_pid}"; then
  write_rc "${RESULT_DIR}/hover_hold_controller.rc" 0
else
  write_rc "${RESULT_DIR}/hover_hold_controller.rc" "$?"
fi
controller_pid=""

if wait "${truth_recorder_pid}"; then
  write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" 0
else
  write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" "$?"
fi
truth_recorder_pid=""

if wait "${controller_echo_pid}"; then
  write_rc "${RESULT_DIR}/topic_${controller_key}_once.rc" 0
else
  write_rc "${RESULT_DIR}/topic_${controller_key}_once.rc" "$?"
fi
controller_echo_pid=""
if wait "${ros_actuator_echo_pid}"; then
  write_rc "${RESULT_DIR}/topic_${ros_actuator_key}_once.rc" 0
else
  write_rc "${RESULT_DIR}/topic_${ros_actuator_key}_once.rc" "$?"
fi
ros_actuator_echo_pid=""
if wait "${gz_actuator_echo_pid}"; then
  write_rc "${RESULT_DIR}/gz_topic_${gz_actuator_key}_once.rc" 0
else
  write_rc "${RESULT_DIR}/gz_topic_${gz_actuator_key}_once.rc" "$?"
fi
gz_actuator_echo_pid=""

eval_rc=0
python3 "${HOVER_EVAL_SCRIPT}" \
  --controller-report-json "${HOVER_CONTROLLER_JSON}" \
  --controller-trace-jsonl "${HOVER_CONTROLLER_TRACE}" \
  --adapter-trace-jsonl "${RESULT_DIR}/controller_output_adapter_node.trace.jsonl" \
  --truth-pose-jsonl "${GAZEBO_TRUTH_POSE_JSONL}" \
  --truth-summary-json "${GAZEBO_TRUTH_POSE_SUMMARY_JSON}" \
  --output-json "${HOVER_EVAL_JSON}" \
  --target-altitude-m "${HOVER_TARGET_ALTITUDE_M}" \
  --command-min "${HOVER_COMMAND_MIN}" \
  --command-max "${HOVER_COMMAND_MAX}" \
  --min-controller-samples "${HOVER_MIN_CONTROLLER_SAMPLES}" \
  --min-adapter-samples "${HOVER_MIN_ADAPTER_SAMPLES}" \
  --min-truth-samples "${HOVER_MIN_TRUTH_SAMPLES}" \
  --min-duration-s "${HOVER_MIN_DURATION_S}" \
  --max-final-abs-z-error-m "${HOVER_MAX_FINAL_ABS_Z_ERROR_M}" \
  --max-abs-z-error-m "${HOVER_MAX_ABS_Z_ERROR_M}" \
  --min-allowed-z-m "${HOVER_MIN_ALLOWED_Z_M}" \
  --max-allowed-z-m "${HOVER_MAX_ALLOWED_Z_M}" \
  --max-xy-distance-m "${HOVER_MAX_XY_DISTANCE_M}" \
  --max-tilt-rad "${HOVER_MAX_TILT_RAD}" \
  > "${RESULT_DIR}/hover_hold_closed_loop_eval.stdout.log" \
  2> "${RESULT_DIR}/hover_hold_closed_loop_eval.stderr.log" || eval_rc="$?"
write_rc "${RESULT_DIR}/hover_hold_closed_loop_eval.rc" "${eval_rc}"

timeout 5 ros2 topic list > "${RESULT_DIR}/ros2_topic_list.txt" 2> "${RESULT_DIR}/ros2_topic_list.stderr.txt" || true

python3 - <<PY
import json
from pathlib import Path

result_dir = Path("${RESULT_DIR}")
def load(name):
    path = result_dir / name
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "invalid_json", "error": f"{exc.__class__.__name__}: {exc}"}

eval_report = load("${HOVER_EVAL_OUTPUT}")
controller = load("hover_hold_controller.json")
world = load("gazebo_world_control.json")
blockers = []
if world.get("status") != "unpaused":
    blockers.append(f"gazebo_world_control_not_unpaused:{world.get('status')}")
if controller.get("status") != "completed":
    blockers.append(f"hover_hold_controller_not_completed:{controller.get('status')}")
if not eval_report.get("gate_passed"):
    blockers.append("hover_hold_closed_loop_eval_failed")
    blockers.extend([f"eval:{item}" for item in eval_report.get("blockers", [])])

gate_passed = not blockers
runtime = {
    "schema": "mosim.gazebo_hover_hold_closed_loop_runtime_status.v1",
    "status": "runtime_smoke_passed" if gate_passed else "runtime_smoke_blocked",
    "gate_passed": gate_passed,
    "scenario": "${SCENARIO}",
    "result_dir": "${RESULT_DIR}",
    "preflight": "${PREFLIGHT_JSON}",
    "run_manifest": "${RUN_MANIFEST}",
    "controller": "hover_hold_controller.json",
    "controller_trace": "hover_hold_controller_trace.jsonl",
    "adapter_trace": "controller_output_adapter_node.trace.jsonl",
    "truth_recording": "GAZEBO_TRUTH_POSE_RECORDING.json",
    "truth_pose": "gazebo_truth_pose.jsonl",
    "eval": "${HOVER_EVAL_OUTPUT}",
    "world_control": "gazebo_world_control.json",
    "blockers": blockers,
    "warnings": eval_report.get("warnings", []),
    "claim_boundary": [
        "bounded single-UAV Gazebo truth-feedback hover-hold pre-acceptance only",
        "no planner setpoint, trajectory tracking, competition controller performance, final closed_loop acceptance, or multi-UAV readiness is claimed"
    ],
}
Path("${RUNTIME_STATUS_JSON}").write_text(json.dumps(runtime, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
manifest = {
    "schema_version": "mosim.run_manifest.v1",
    "run_id": "sunray150_gazebo_ros2_hover_hold_closed_loop_pre_acceptance",
    "objective": "bounded single-UAV Gazebo truth-feedback hover-hold pre-acceptance",
    "scene_id": "sunray150_single_uav_competition_light",
    "vehicle_id": "sunray150_assembled",
    "quality_status": "passed" if gate_passed else "blocked",
    "evidence_level": "gazebo_ros2_closed_loop_pre_acceptance",
    "claim_scope": ["gazebo_truth_feedback", "ControllerOutput", "actuator_echo", "hover_hold_pre_acceptance"],
    "blockers": blockers,
    "artifacts": {
        "runtime_status": "${RUNTIME_STATUS_JSON}",
        "eval": "${HOVER_EVAL_JSON}",
        "controller": "${HOVER_CONTROLLER_JSON}",
        "controller_trace": "${HOVER_CONTROLLER_TRACE}",
        "truth_pose": "${GAZEBO_TRUTH_POSE_JSONL}",
        "truth_summary": "${GAZEBO_TRUTH_POSE_SUMMARY_JSON}",
    },
    "not_claimed": [
        "planner_ready",
        "setpoint_publication",
        "trajectory_tracking",
        "competition_controller_performance",
        "final_closed_loop_acceptance",
        "multi_uav_readiness",
    ],
}
Path("${RUN_MANIFEST}").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if gate_passed:
    blocker = Path("${BLOCKER}")
    if blocker.exists():
        blocker.unlink()
else:
    Path("${BLOCKER}").write_text(json.dumps({
        "schema": "mosim.gazebo_hover_hold_closed_loop_blocker.v1",
        "status": "blocked",
        "reason": "hover_hold_closed_loop_runtime_gate_failed",
        "runtime_status": "${RUNTIME_STATUS_JSON}",
        "blockers": blockers,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

if [[ -f "${BLOCKER}" ]]; then
  echo "${BLOCKER}"
else
  echo "${RUN_MANIFEST}"
fi
