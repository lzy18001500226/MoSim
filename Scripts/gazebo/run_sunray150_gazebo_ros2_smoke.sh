#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
GAZEBO_ENV_SCRIPT="${GAZEBO_ENV_SCRIPT:-${PROJECT_ROOT}/Scripts/gazebo/setup_gazebo_wsl_env.sh}"
if [[ -f "${GAZEBO_ENV_SCRIPT}" ]]; then
  # shellcheck disable=SC1090
  source "${GAZEBO_ENV_SCRIPT}"
fi
SCENARIO="${SCENARIO:-Config/scenarios/system/sunray150_gazebo_ros2_smoke.yaml}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/sunray150_gazebo_ros2_smoke}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
ROS_LOG_DIR="${ROS_LOG_DIR:-${PROJECT_ROOT}/Results/tmp/ros_logs}"
DRY_RUN="${DRY_RUN:-0}"
RUN_GAZEBO="${RUN_GAZEBO:-0}"
RUN_ROS2_BRIDGE="${RUN_ROS2_BRIDGE:-0}"
RUN_LOCAL_MAP="${RUN_LOCAL_MAP:-0}"
RUN_MAP_REVIEW_CAPTURE="${RUN_MAP_REVIEW_CAPTURE:-0}"
RUN_TOPIC_CHECK="${RUN_TOPIC_CHECK:-0}"
RUN_RATE_CHECK="${RUN_RATE_CHECK:-0}"
RUN_HEADER_RATE_CHECK="${RUN_HEADER_RATE_CHECK:-${RUN_RATE_CHECK}}"
RUN_STATIC_TF="${RUN_STATIC_TF:-0}"
RUN_TF_CHECK="${RUN_TF_CHECK:-0}"
RUN_FASTLIO_PLANNER_INPUT_ADAPTER="${RUN_FASTLIO_PLANNER_INPUT_ADAPTER:-0}"
RUN_EGO_STYLE_PLANNER_OUTPUT="${RUN_EGO_STYLE_PLANNER_OUTPUT:-0}"
RUN_SPARK_FASTLIO="${RUN_SPARK_FASTLIO:-0}"
RUN_FASTLIO_TRUTH_EVAL="${RUN_FASTLIO_TRUTH_EVAL:-0}"
RUN_GAZEBO_TRUTH_POSE="${RUN_GAZEBO_TRUTH_POSE:-0}"
RUN_PLANT_RESPONSE_EVAL="${RUN_PLANT_RESPONSE_EVAL:-0}"
RUN_ACTUATOR_BRIDGE="${RUN_ACTUATOR_BRIDGE:-0}"
RUN_CONTROLLER_COMMAND="${RUN_CONTROLLER_COMMAND:-0}"
RUN_CONTROLLER_OUTPUT_NODE="${RUN_CONTROLLER_OUTPUT_NODE:-0}"
RUN_CONTROLLER_OUTPUT_FIXTURE="${RUN_CONTROLLER_OUTPUT_FIXTURE:-0}"
RUN_ACTUATOR_COMMAND_CHECK="${RUN_ACTUATOR_COMMAND_CHECK:-0}"
RUN_COMMAND_ACK_GUARD="${RUN_COMMAND_ACK_GUARD:-0}"
CONTROLLER_COMMAND_TYPE="${CONTROLLER_COMMAND_TYPE:-normalized_motor_speed}"
CONTROLLER_COMMAND_VALUES="${CONTROLLER_COMMAND_VALUES:-0.5 0.5 0.5 0.5}"
CONTROLLER_COMMAND_RATE_HZ="${CONTROLLER_COMMAND_RATE_HZ:-5}"
CONTROLLER_COMMAND_TIMES="${CONTROLLER_COMMAND_TIMES:-5}"
CONTROLLER_OUTPUT_NODE_MAX_MESSAGES="${CONTROLLER_OUTPUT_NODE_MAX_MESSAGES:-1}"
COMMAND_ACK_MAX_AGE_S="${COMMAND_ACK_MAX_AGE_S:-2.0}"
COMMAND_ACK_STALE_AGE_S="${COMMAND_ACK_STALE_AGE_S:-10.0}"
MOSIM_ROS2_WS="${MOSIM_ROS2_WS:-${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs}"
BUILD_MOSIM_ROS2_MSGS="${BUILD_MOSIM_ROS2_MSGS:-0}"
RUNTIME_GATE_PROFILE="${RUNTIME_GATE_PROFILE:-sensor_local_map}"
if [[ "${RUNTIME_GATE_PROFILE}" == "sensor_local_map" \
  && "${RUN_GAZEBO_TRUTH_POSE}" == "1" \
  && "${RUN_ROS2_BRIDGE}" != "1" \
  && "${RUN_LOCAL_MAP}" != "1" \
  && "${RUN_TOPIC_CHECK}" != "1" \
  && "${RUN_RATE_CHECK}" != "1" \
  && "${RUN_TF_CHECK}" != "1" \
  && "${RUN_PLANT_RESPONSE_EVAL}" != "1" \
  && "${RUN_FASTLIO_TRUTH_EVAL}" != "1" ]]; then
  RUNTIME_GATE_PROFILE="gazebo_truth_pose_only"
fi
if [[ "${RUN_LOCAL_MAP}" == "1" && "${RUN_MAP_REVIEW_CAPTURE}" != "1" ]]; then
  RUN_MAP_REVIEW_CAPTURE="1"
fi
if [[ "${RUN_LOCAL_MAP}" == "1" && "${RUN_STATIC_TF}" != "1" ]]; then
  RUN_STATIC_TF="1"
fi
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-15}"
GAZEBO_RENDER_ENGINE_SERVER="${GAZEBO_RENDER_ENGINE_SERVER:-ogre}"
START_GAZEBO_PAUSED="${START_GAZEBO_PAUSED:-0}"
UNPAUSE_GAZEBO_AFTER_CONTROLLER_COMMAND="${UNPAUSE_GAZEBO_AFTER_CONTROLLER_COMMAND:-0}"

# Default output names are supplied by the scenario YAML:
# RUN_MANIFEST.json and BLOCKER.json.

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_DIR}" "${ROS_LOG_DIR}"
export ROS_LOG_DIR

write_json() {
  local path="$1"
  local payload="$2"
  printf '%s\n' "${payload}" > "${path}"
}

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

ros2_topic_list_snapshot() {
  local output_file="$1"
  local attempts="${2:-5}"
  local delay_seconds="${3:-1}"
  local tmp_file="${output_file}.tmp"
  local log_file="${output_file}.attempts.log"
  : > "${log_file}"
  local attempt
  for attempt in $(seq 1 "${attempts}"); do
    if timeout 5 ros2 topic list > "${tmp_file}" 2>> "${log_file}"; then
      if [[ -s "${tmp_file}" ]]; then
        mv "${tmp_file}" "${output_file}"
        printf 'attempt=%s status=nonempty\n' "${attempt}" >> "${log_file}"
        return 0
      fi
      printf 'attempt=%s status=empty\n' "${attempt}" >> "${log_file}"
    else
      local rc="$?"
      printf 'attempt=%s status=failed rc=%s\n' "${attempt}" "${rc}" >> "${log_file}"
    fi
    sleep "${delay_seconds}"
  done
  rm -f "${tmp_file}"
  if [[ ! -e "${output_file}" ]]; then
    : > "${output_file}"
  fi
  return 1
}

ros2_topic_echo_once_retry() {
  local topic="$1"
  local message_type="$2"
  local qos_mode="$3"
  local output_file="$4"
  local stderr_file="$5"
  local rc_file="$6"
  local attempts="${7:-3}"
  local delay_seconds="${8:-1}"
  local tmp_output="${output_file}.tmp"
  local tmp_stderr="${stderr_file}.tmp"
  : > "${stderr_file}"
  local attempt
  local rc=1
  for attempt in $(seq 1 "${attempts}"); do
    local echo_args=(topic echo --once)
    if [[ "${qos_mode}" == "sensor_data" ]]; then
      echo_args+=(--qos-profile sensor_data)
    elif [[ "${qos_mode}" == "tf_static" ]]; then
      echo_args+=(--qos-profile services_default --qos-reliability reliable --qos-durability transient_local)
    fi
    echo_args+=("${topic}")
    if [[ -n "${message_type}" ]]; then
      echo_args+=("${message_type}")
    fi
    printf 'attempt=%s topic=%s type=%s qos=%s\n' "${attempt}" "${topic}" "${message_type}" "${qos_mode}" >> "${stderr_file}"
    rc=0
    if timeout "${TIMEOUT_SECONDS}" ros2 "${echo_args[@]}" > "${tmp_output}" 2> "${tmp_stderr}"; then
      if [[ -s "${tmp_output}" ]] && ! grep -Eq 'xmlrpc\.client\.Fault|!rclpy\.ok\(\)|Traceback' "${tmp_stderr}"; then
        mv "${tmp_output}" "${output_file}"
        cat "${tmp_stderr}" >> "${stderr_file}"
        rm -f "${tmp_stderr}"
        write_rc "${rc_file}" 0
        return 0
      fi
      rc=1
      cat "${tmp_stderr}" >> "${stderr_file}" 2>/dev/null || true
      printf 'attempt=%s status=empty_or_ros_graph_fault\n' "${attempt}" >> "${stderr_file}"
      sleep "${delay_seconds}"
      continue
    fi
    rc="$?"
    cat "${tmp_stderr}" >> "${stderr_file}" 2>/dev/null || true
    printf 'attempt=%s rc=%s\n' "${attempt}" "${rc}" >> "${stderr_file}"
    sleep "${delay_seconds}"
  done
  rm -f "${tmp_output}" "${tmp_stderr}"
  : > "${output_file}"
  write_rc "${rc_file}" "${rc}"
  return "${rc}"
}

write_gazebo_world_control_report() {
  local status="$1"
  local action="$2"
  local service="$3"
  local response_file="$4"
  local stderr_file="$5"
  python3 - <<PY
import json
from pathlib import Path

response_path = Path("${response_file}")
stderr_path = Path("${stderr_file}")
payload = {
    "schema": "mosim.gazebo_world_control.v1",
    "status": "${status}",
    "action": "${action}",
    "service": "${service}",
    "start_gazebo_paused": "${START_GAZEBO_PAUSED}" == "1",
    "unpause_after_controller_command": "${UNPAUSE_GAZEBO_AFTER_CONTROLLER_COMMAND}" == "1",
    "response_file": "${response_file}",
    "stderr_file": "${stderr_file}",
    "response_text": response_path.read_text(encoding="utf-8", errors="replace") if response_path.exists() else "",
    "stderr_text": stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.exists() else "",
    "claim_boundary": "world-control evidence only; this does not prove hover, closed_loop, planner_ready, or controller performance",
}
Path("${RESULT_DIR}/gazebo_world_control.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
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
    write_gazebo_world_control_report "unpaused" "pause_false" "${service}" "${response_file}" "${stderr_file}"
    return 0
  fi
  local rc="$?"
  write_rc "${RESULT_DIR}/gazebo_world_control_unpause.rc" "${rc}"
  write_gazebo_world_control_report "blocked" "pause_false" "${service}" "${response_file}" "${stderr_file}"
  return "${rc}"
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
    for child in $(pgrep -P "${pid}" 2>/dev/null || true); do
      terminate_process_tree "${child}" 1
    done
    kill -KILL "${pid}" >/dev/null 2>&1 || true
  fi
  wait "${pid}" 2>/dev/null || true
}

drain_stale_project_gazebo() {
  local world_path="$1"
  local drain_log="${RESULT_DIR}/stale_gazebo_drain.jsonl"
  local world_abs="${PROJECT_ROOT}/${world_path}"
  local pids
  pids="$(
    ps -eo pid=,args= | awk -v wrel="${world_path}" -v wabs="${world_abs}" '
      ($0 ~ /(ign|gz)[[:space:]]+(gazebo|sim)/ && (index($0, wrel) > 0 || index($0, wabs) > 0)) {print $1}
    '
  )"
  for pid in ${pids}; do
    if [[ "${pid}" == "$$" ]] || [[ "${pid}" == "${BASHPID}" ]]; then
      continue
    fi
    printf '{"schema":"mosim.stale_gazebo_drain.v1","action":"terminate","pid":%s,"world":"%s"}\n' \
      "${pid}" "${world_path}" >> "${drain_log}"
    terminate_process_tree "${pid}" 2
  done
}

scenario_json="$(python3 - <<PY
import json
from pathlib import Path
try:
    import yaml
except Exception as exc:
    raise SystemExit(f"PyYAML is required to read {Path('${SCENARIO}').as_posix()}: {exc}")

path = Path("${SCENARIO}")
data = yaml.safe_load(path.read_text(encoding="utf-8"))
print(json.dumps(data, ensure_ascii=False))
PY
)"

WORLD="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["gazebo"]["world"])
PY
)"
SCENE_ID="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data.get("scene_id", "factory_minimal"))
PY
)"
VEHICLE_ID="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data.get("vehicle_id", "sunray150"))
PY
)"
MAP_ID="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data.get("map_id", "factory_minimal_truth_voxels"))
PY
)"
MODEL="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["gazebo"]["model"])
PY
)"
CONTROLLER_ID="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["controller_id"])
PY
)"
LOCAL_MAP_SCRIPT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["local_map_adapter"]["script"])
PY
)"
MAP_REVIEW_RECORDER_SCRIPT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("map_review_capture", {}).get("script", "Scripts/ros/record_gazebo_ros2_map_review.py"))
PY
)"
FASTLIO_PLANNER_INPUT_SCRIPT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("fastlio_planner_input_adapter", {}).get("script", ""))
PY
)"
FASTLIO_IMU_PASSTHROUGH_SCRIPT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("fastlio_imu_passthrough", {}).get("script", ""))
PY
)"
EGO_STYLE_PLANNER_OUTPUT_SCRIPT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("ego_style_planner_output_without_actuation", {}).get("script", "Scripts/ros/ego_style_planner_output_node.py"))
PY
)"
EGO_STYLE_PLANNER_OUTPUT_JSON_NAME="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("ego_style_planner_output_without_actuation", {}).get("output_json", "EGO_STYLE_PLANNER_OUTPUT_GATE.json"))
PY
)"
EGO_STYLE_PLANNER_TRACE_JSONL_NAME="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("ego_style_planner_output_without_actuation", {}).get("trace_jsonl", "ego_style_planner_output.trace.jsonl"))
PY
)"
EGO_STYLE_PLANNER_OUTPUT_JSON="${RESULT_DIR}/${EGO_STYLE_PLANNER_OUTPUT_JSON_NAME}"
EGO_STYLE_PLANNER_TRACE_JSONL="${RESULT_DIR}/${EGO_STYLE_PLANNER_TRACE_JSONL_NAME}"
SPARK_FASTLIO_SETUP="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("spark_fastlio_runtime", {}).get("workspace_setup", ""))
PY
)"
SPARK_FASTLIO_LAUNCH_FILE="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("spark_fastlio_runtime", {}).get("launch_file", ""))
PY
)"
SPARK_FASTLIO_CONFIG_PATH="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("spark_fastlio_runtime", {}).get("config_path", ""))
PY
)"
SPARK_FASTLIO_RECORDER_SCRIPT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("spark_fastlio_runtime", {}).get("recorder_script", ""))
PY
)"
GAZEBO_TRUTH_RECORDER_SCRIPT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("gazebo_truth_pose", {}).get("recorder_script", "Scripts/gazebo/capture_gazebo_pose_truth_topic.py"))
PY
)"
GAZEBO_TRUTH_RECORDER_BASENAME="$(basename "${GAZEBO_TRUTH_RECORDER_SCRIPT}")"
FASTLIO_TRUTH_EVAL_SCRIPT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("fastlio_truth_error_eval", {}).get("script", "Scripts/quality/evaluate_fastlio_truth_error.py"))
PY
)"
TOPIC_HEADER_RATE_SCRIPT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("topic_header_rate_script", "Scripts/ros/record_topic_header_rate.py"))
PY
)"
SPARK_FASTLIO_OUTPUT_SUBDIR="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("spark_fastlio_runtime", {}).get("output_dir", "fastlio_runtime"))
PY
)"
SPARK_FASTLIO_OUTPUT_DIR="${RESULT_DIR}/${SPARK_FASTLIO_OUTPUT_SUBDIR}"
GAZEBO_TRUTH_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("gazebo_truth_pose", {}).get("topic", "/world/yunzong_planning_test_sunray150_assembled/dynamic_pose/info"))
PY
)"
GAZEBO_TRUTH_ROS_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
pose=data["ros2"].get("gazebo_truth_pose", {})
print(pose.get("ros_topic", pose.get("topic", "/world/yunzong_planning_test_sunray150_assembled/dynamic_pose/info")))
PY
)"
GAZEBO_TRUTH_ROS_MESSAGE="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("gazebo_truth_pose", {}).get("ros_message", "geometry_msgs/msg/PoseArray"))
PY
)"
GAZEBO_TRUTH_GZ_MESSAGE="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("gazebo_truth_pose", {}).get("gz_message", "gz.msgs.Pose_V"))
PY
)"
GAZEBO_WORLD_NAME="$(python3 - <<PY
import json, re
data=json.loads('''${scenario_json}''')
topic=data["ros2"].get("gazebo_truth_pose", {}).get("topic", "/world/yunzong_planning_test_sunray150_assembled/dynamic_pose/info")
match=re.match(r"^/world/([^/]+)/", topic)
print(match.group(1) if match else "yunzong_planning_test_sunray150_assembled")
PY
)"
GAZEBO_TRUTH_MODEL_NAME="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("gazebo_truth_pose", {}).get("model_name", "sunray150"))
PY
)"
GAZEBO_TRUTH_FRAME_ID="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("gazebo_truth_pose", {}).get("frame_id", "world"))
PY
)"
GAZEBO_TRUTH_EXPECTED_ENTITY_ID="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
value=data["ros2"].get("gazebo_truth_pose", {}).get("expected_entity_id", "")
print("" if value is None else value)
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
GAZEBO_TRUTH_POSE_JSONL="${RESULT_DIR}/gazebo_truth_pose.jsonl"
GAZEBO_TRUTH_POSE_SUMMARY_JSON="${RESULT_DIR}/GAZEBO_TRUTH_POSE_RECORDING.json"
FASTLIO_TRUTH_ERROR_EVAL_JSON="${RESULT_DIR}/FASTLIO_TRUTH_ERROR_EVAL.json"
GAZEBO_PLANT_RESPONSE_EVAL_JSON="${RESULT_DIR}/GAZEBO_PLANT_RESPONSE_EVAL.json"
PLANT_RESPONSE_EVAL_SCRIPT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("single_uav_plant_response_pre_acceptance", {}).get("script", "Scripts/quality/evaluate_gazebo_plant_response.py"))
PY
)"
SPARK_FASTLIO_RECORD_SECONDS="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("spark_fastlio_runtime", {}).get("record_duration_seconds", 10))
PY
)"
FASTLIO_TRUTH_MAX_TIME_DELTA_S="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("fastlio_truth_error_eval", {}).get("max_time_delta_s", 0.05))
PY
)"
FASTLIO_TRUTH_MIN_MATCHED_SAMPLES="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("fastlio_truth_error_eval", {}).get("min_matched_samples", 30))
PY
)"
FASTLIO_TRUTH_TIME_ALIGNMENT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("fastlio_truth_error_eval", {}).get("time_alignment", "relative_start"))
PY
)"
FASTLIO_TRUTH_RMSE_WARN_M="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("fastlio_truth_error_eval", {}).get("rmse_warn_m", 0.5))
PY
)"
FASTLIO_TRUTH_RMSE_BLOCK_M="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("fastlio_truth_error_eval", {}).get("rmse_block_m", 1.0))
PY
)"
FASTLIO_TRUTH_P95_BLOCK_M="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("fastlio_truth_error_eval", {}).get("p95_block_m", 1.5))
PY
)"
PLANT_RESPONSE_MIN_SAMPLES="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
gate=data["ros2"].get("single_uav_plant_response_pre_acceptance", {})
print(gate.get("min_samples", 20))
PY
)"
PLANT_RESPONSE_MIN_DURATION_S="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
gate=data["ros2"].get("single_uav_plant_response_pre_acceptance", {})
print(gate.get("min_duration_s", 2.0))
PY
)"
PLANT_RESPONSE_WINDOW_FRACTION="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
gate=data["ros2"].get("single_uav_plant_response_pre_acceptance", {})
print(gate.get("window_fraction", 0.2))
PY
)"
PLANT_RESPONSE_MIN_WINDOW_SAMPLES="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
gate=data["ros2"].get("single_uav_plant_response_pre_acceptance", {})
print(gate.get("min_window_samples", 5))
PY
)"
PLANT_RESPONSE_MIN_Z_DELTA_M="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
gate=data["ros2"].get("single_uav_plant_response_pre_acceptance", {})
print(gate.get("min_z_delta_m", 0.05))
PY
)"
PLANT_RESPONSE_MIN_3D_DELTA_M="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
gate=data["ros2"].get("single_uav_plant_response_pre_acceptance", {})
print(gate.get("min_3d_delta_m", 0.05))
PY
)"
PLANT_RESPONSE_MAX_EARLY_Z_RANGE_WARNING_M="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
gate=data["ros2"].get("single_uav_plant_response_pre_acceptance", {})
print(gate.get("max_early_z_range_warning_m", 0.02))
PY
)"
PLANT_RESPONSE_EXPECTED_ACTUATOR_COUNT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
gate=data["ros2"].get("single_uav_plant_response_pre_acceptance", {})
print(gate.get("expected_actuator_count", 4))
PY
)"
SPARK_FASTLIO_RECORDER_TIMEOUT_SECONDS="$(python3 - <<PY
import math
print(int(math.ceil(float("${TIMEOUT_SECONDS}") + float("${SPARK_FASTLIO_RECORD_SECONDS}") + 2.0)))
PY
)"
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
CONTROLLER_ADAPTER_SCRIPT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["controller_adapter"]["adapter_script"])
PY
)"
CONTROLLER_NODE_SCRIPT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["controller_adapter"].get("node_script", ""))
PY
)"
CONTROLLER_FIXTURE_SCRIPT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["controller_adapter"].get("fixture_publisher_script", ""))
PY
)"
MOSIM_MSGS_PACKAGE="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["controller_adapter"].get("message_package", "Scripts/ros/mosim_msgs"))
PY
)"
MOSIM_SETPOINT_ADAPTER_PACKAGE="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("ego_style_planner_output_without_actuation", {}).get("setpoint_adapter_package", "Scripts/ros/mosim_setpoint_adapter"))
PY
)"
ROS_CONTROLLER_OUTPUT_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["controller_adapter"]["input_topic"])
PY
)"
ROS_ACTUATOR_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["controller_adapter"]["ros_actuator_topic"])
PY
)"
GZ_ACTUATOR_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["controller_adapter"]["gz_actuator_topic"])
PY
)"
CONTROLLER_ACTUATOR_ROS_TYPE="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["controller_adapter"].get("ros_type", "actuator_msgs/msg/Actuators"))
PY
)"
CONTROLLER_ACTUATOR_GZ_TYPE="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["controller_adapter"].get("gz_type", "gz.msgs.Actuators"))
PY
)"
ROS_IMU_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"]["imu"])
PY
)"
ROS_LIDAR_POINTS_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"]["lidar_points"])
PY
)"
ROS_LOCAL_VOXEL_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"]["local_occupancy_voxels"])
PY
)"
ROS_LOCAL_GRID_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"]["local_occupancy_grid"])
PY
)"
MAP_REVIEW_OUTPUT_DIR="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("map_review_capture", {}).get("output_dir", "map_review"))
PY
)"
MAP_REVIEW_DURATION_SECONDS="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("map_review_capture", {}).get("duration_seconds", 8))
PY
)"
ROS_FASTLIO_LIDAR_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("fastlio_lidar", ""))
PY
)"
ROS_FASTLIO_IMU_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("fastlio_imu", ""))
PY
)"
ROS_SPARK_FASTLIO_LIVOX_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("spark_fastlio_livox", ""))
PY
)"
ROS_SUNRAY_FASTLIO_LIDAR_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("sunray_fastlio_lidar", ""))
PY
)"
ROS_SUNRAY_FASTLIO_IMU_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("sunray_fastlio_imu", ""))
PY
)"
ROS_PLANNER_GLOBAL_POINTS_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("planner_global_points", ""))
PY
)"
ROS_MOSIM_PLANNER_GLOBAL_POINTS_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("mosim_planner_global_points", ""))
PY
)"
ROS_PLANNER_ODOM_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("planner_odom", ""))
PY
)"
ROS_MOSIM_PLANNER_ODOM_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("mosim_planner_odom", ""))
PY
)"
ROS_REFERENCE_POSITION_CMD_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("reference_position_cmd", "/position_cmd"))
PY
)"
ROS_MOSIM_PLANNER_POSITION_CMD_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("mosim_planner_position_cmd", "/mosim/planner/position_cmd"))
PY
)"
ROS_PLANNER_SETPOINT_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("planner_setpoint", "/mosim/planner/setpoint"))
PY
)"
ROS_PLANNER_SETPOINT_STATUS_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("planner_setpoint_adapter_status", "/mosim/planner/setpoint_adapter_status"))
PY
)"
PLANNER_HANDOFF_FORBIDDEN_TOPIC_EVIDENCE="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
gate=data["ros2"].get("planner_handoff_without_setpoint_publication", {})
print(gate.get("forbidden_topic_evidence", "forbidden_topic_presence.json"))
PY
)"
EGO_STYLE_PLANNER_ARGS="$(python3 - <<PY
import json, shlex
data=json.loads('''${scenario_json}''')
topics=data["ros2"]["topics"]
gate=data["ros2"].get("ego_style_planner_output_without_actuation", {})
args = [
    "--odom-topic", topics.get("mosim_planner_odom", "/mosim/planner/odom"),
    "--global-points-topic", topics.get("mosim_planner_global_points", "/mosim/planner/global_points"),
    "--position-command-topic", topics.get("reference_position_cmd", "/position_cmd"),
    "--mosim-position-command-topic", topics.get("mosim_planner_position_cmd", "/mosim/planner/position_cmd"),
    "--report-json", "${EGO_STYLE_PLANNER_OUTPUT_JSON}",
    "--trace-jsonl", "${EGO_STYLE_PLANNER_TRACE_JSONL}",
    "--map-frame", gate.get("map_frame", "map"),
    "--planner-id", gate.get("planner_id", "mosim_ego_style_local_goal"),
    "--rate-hz", gate.get("output_rate_hz", 5.0),
    "--duration-s", gate.get("duration_s", 8.0),
    "--input-wait-s", gate.get("input_wait_s", 45.0),
    "--target-forward-m", gate.get("target_forward_m", 2.0),
    "--target-left-m", gate.get("target_left_m", 0.0),
    "--target-altitude-m", gate.get("target_altitude_m", 1.2),
    "--min-odom-samples", gate.get("min_odom_samples", 5),
    "--min-cloud-samples", gate.get("min_cloud_samples", 2),
    "--min-published-commands", gate.get("min_position_cmd_samples", 10),
]
print(" ".join(shlex.quote(str(item)) for item in args))
PY
)"
ROS_SPARK_FASTLIO_REGISTERED_CLOUD_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("spark_fastlio_registered_cloud", ""))
PY
)"
ROS_SPARK_FASTLIO_ODOMETRY_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("spark_fastlio_odometry", ""))
PY
)"
ROS_SPARK_FASTLIO_PATH_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"].get("spark_fastlio_path", ""))
PY
)"
ROS_TF_STATIC_TOPIC="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["topics"]["tf_static"])
PY
)"
LOCAL_MAP_MAP_FRAME="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"]["local_map_adapter"].get("map_frame", "map"))
PY
)"
LOCAL_MAP_EXPECTED_INPUT_FRAME="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
adapter=data["ros2"]["local_map_adapter"]
print(adapter.get("expected_input_frame", adapter.get("sensor_frame", adapter.get("map_frame", "map"))))
PY
)"
SENSOR_FRAGMENT="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["gazebo"]["sensor_fragment"])
PY
)"
SCENARIO_RUN_MANIFEST="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["outputs"]["run_manifest"])
PY
)"
RUN_MANIFEST="${RUN_MANIFEST:-${RESULT_DIR}/RUN_MANIFEST.json}"
SCENARIO_RUNTIME_STATUS_JSON="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["outputs"].get("runtime_status_json", "${RESULT_DIR}/RUNTIME_STATUS.json"))
PY
)"
RUNTIME_STATUS_JSON="${RUNTIME_STATUS_JSON:-${RESULT_DIR}/RUNTIME_STATUS.json}"
SCENARIO_BLOCKER="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["outputs"]["blocker"])
PY
)"
BLOCKER="${BLOCKER:-${RESULT_DIR}/BLOCKER.json}"
SCENARIO_PREFLIGHT_JSON="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["outputs"]["preflight_json"])
PY
)"
PREFLIGHT_JSON="${PREFLIGHT_JSON:-${RESULT_DIR}/PREFLIGHT.json}"
SCENARIO_TOPIC_CONTRACT_JSON="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["outputs"]["topic_contract_json"])
PY
)"
TOPIC_CONTRACT_JSON="${TOPIC_CONTRACT_JSON:-${RESULT_DIR}/TOPIC_CONTRACT.json}"
TOPIC_GATES_JSON="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(json.dumps(data["ros2"].get("topic_gates", {}), ensure_ascii=False, indent=2))
PY
)"
RATE_GATE_MIN_FRACTION="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(data["ros2"].get("rate_gate_min_fraction", 0.5))
PY
)"
LOCAL_MAP_FRAME_BOUNDARY_JSON="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
adapter=data["ros2"]["local_map_adapter"]
z_bounds = adapter.get("z_bounds_m", [-1.0, 5.0])
self_filter_z_bounds = adapter.get("self_filter_z_bounds_m", [None, None])
print(json.dumps({
  "map_frame": adapter.get("map_frame", "map"),
  "sensor_frame": adapter.get("sensor_frame", ""),
  "frame_assumption": adapter.get("frame_assumption", ""),
  "input_frame_policy": adapter.get("input_frame_policy", ""),
  "expected_input_frame": adapter.get("expected_input_frame", adapter.get("map_frame", "map")),
  "tf_lookup_timeout_s": adapter.get("tf_lookup_timeout_s", 0.2),
  "local_map_center_source": adapter.get("local_map_center_source", "map_origin"),
  "runtime_frame_gate": adapter.get("runtime_frame_gate", ""),
  "local_occupancy_filter": {
    "voxel_size_m": adapter.get("voxel_size_m", 0.2),
    "grid_resolution_m": adapter.get("grid_resolution_m", adapter.get("voxel_size_m", 0.2)),
    "local_radius_m": adapter.get("local_radius_m", 12.0),
    "z_bounds_m": z_bounds,
    "ground_min_z_m": adapter.get("ground_min_z_m"),
    "self_filter_radius_xy_m": adapter.get("self_filter_radius_xy_m", 0.0),
    "self_filter_z_bounds_m": self_filter_z_bounds,
    "filter_boundary": adapter.get("filter_boundary", "raw_lidar_unchanged_filters_apply_only_to_local_occupancy_outputs")
  }
}, ensure_ascii=False, indent=2))
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
FASTLIO_PLANNER_INPUT_ARGS="$(python3 - <<PY
import json, shlex
data=json.loads('''${scenario_json}''')
adapter=data["ros2"].get("fastlio_planner_input_adapter", {})
args = [
    "--lidar-input-topic", adapter.get("input_lidar_topic", data["ros2"]["topics"]["lidar_points"]),
    "--imu-input-topic", adapter.get("input_imu_topic", data["ros2"]["topics"]["imu"]),
    "--fastlio-lidar-topic", adapter.get("fastlio_lidar_topic", data["ros2"]["topics"].get("fastlio_lidar", "")),
    "--fastlio-imu-topic", adapter.get("fastlio_imu_topic", data["ros2"]["topics"].get("fastlio_imu", "")),
    "--spark-livox-custom-topic", adapter.get("spark_livox_custom_topic", data["ros2"]["topics"].get("spark_fastlio_livox", "")),
    "--sunray-lidar-topic", adapter.get("sunray_lidar_topic", data["ros2"]["topics"].get("sunray_fastlio_lidar", "")),
    "--sunray-imu-topic", adapter.get("sunray_imu_topic", data["ros2"]["topics"].get("sunray_fastlio_imu", "")),
    "--planner-global-points-topic", adapter.get("planner_global_points_topic", data["ros2"]["topics"].get("planner_global_points", "")),
    "--mosim-planner-global-points-topic", adapter.get("mosim_planner_global_points_topic", data["ros2"]["topics"].get("mosim_planner_global_points", "")),
    "--planner-odom-topic", adapter.get("planner_odom_topic", data["ros2"]["topics"].get("planner_odom", "")),
    "--mosim-planner-odom-topic", adapter.get("mosim_planner_odom_topic", data["ros2"]["topics"].get("mosim_planner_odom", "")),
    "--map-frame", adapter.get("map_frame", "map"),
    "--global-frame", adapter.get("global_frame", "map"),
    "--sensor-frame", adapter.get("sensor_frame", "sunray150/base_link/mid360_lidar"),
    "--imu-frame", adapter.get("imu_frame", "sunray150/base_link/forward_imu"),
    "--odom-child-frame", adapter.get("odom_child_frame", "uav1/base_link"),
    "--tf-lookup-timeout-s", adapter.get("tf_lookup_timeout_s", 0.2),
    "--spark-livox-scan-lines", adapter.get("spark_livox_scan_lines", 4),
    "--spark-livox-scan-rate-hz", adapter.get("spark_livox_scan_rate_hz", 10),
    "--odom-rate-hz", adapter.get("odom_rate_hz", 20),
    "--output-json", "${RESULT_DIR}/fastlio_planner_input_adapter.json",
    "--trace-jsonl", "${RESULT_DIR}/fastlio_planner_input_adapter.trace.jsonl",
]
if adapter.get("imu_output_policy") == "separate_high_rate_passthrough":
    args.append("--disable-imu-output")
print(" ".join(shlex.quote(str(item)) for item in args))
PY
)"
FASTLIO_IMU_PASSTHROUGH_ARGS="$(python3 - <<PY
import json, shlex
data=json.loads('''${scenario_json}''')
adapter=data["ros2"].get("fastlio_imu_passthrough", {})
topics=data["ros2"].get("topics", {})
args = [
    "--imu-input-topic", adapter.get("input_imu_topic", topics.get("imu", "")),
    "--fastlio-imu-topic", adapter.get("fastlio_imu_topic", topics.get("fastlio_imu", "")),
    "--sunray-imu-topic", adapter.get("sunray_imu_topic", topics.get("sunray_fastlio_imu", "")),
    "--imu-frame", adapter.get("imu_frame", "sunray150/base_link/forward_imu"),
    "--output-json", "${RESULT_DIR}/fastlio_imu_passthrough.json",
    "--trace-jsonl", "${RESULT_DIR}/fastlio_imu_passthrough.trace.jsonl",
]
print(" ".join(shlex.quote(str(item)) for item in args))
PY
)"
SPARK_FASTLIO_ARGS="$(python3 - <<PY
import json, shlex
data=json.loads('''${scenario_json}''')
runtime=data["ros2"].get("spark_fastlio_runtime", {})
args = [
    "start_rviz:=false",
    "lidar_topic:=" + str(runtime.get("input_lidar_topic", data["ros2"]["topics"].get("fastlio_lidar", ""))),
    "imu_topic:=" + str(runtime.get("input_imu_topic", data["ros2"]["topics"].get("fastlio_imu", ""))),
    "map_frame:=" + str(runtime.get("map_frame", "map")),
    "base_frame:=" + str(runtime.get("base_frame", "sunray150/base_link")),
    "visualization_frame:=" + str(runtime.get("visualization_frame", "base")),
    "lidar_frame:=" + str(runtime.get("lidar_frame", "sunray150/base_link/mid360_lidar")),
    "imu_frame:=" + str(runtime.get("imu_frame", "sunray150/base_link/forward_imu")),
    "use_base_extrinsics:=" + str(runtime.get("use_base_extrinsics", True)).lower(),
    "config_path:=" + str(runtime.get("config_path", "Config/ros2/mosim_spark_fast_lio_mid360.yaml")),
]
print(" ".join(shlex.quote(str(item)) for item in args))
PY
)"

# A new preflight or failed runtime attempt must not leave a stale success
# manifest behind. The manifest is recreated only after the runtime gate passes.
rm -f "${RUN_MANIFEST}"
actuator_ros_key="$(topic_key "${ROS_ACTUATOR_TOPIC}")"
actuator_gz_key="$(topic_key "${GZ_ACTUATOR_TOPIC}")"
rm -f \
  "${RESULT_DIR}/stale_gazebo_drain.jsonl" \
  "${RESULT_DIR}/controller_actuator_command.json" \
  "${RESULT_DIR}/controller_adapter_runtime.stdout.log" \
  "${RESULT_DIR}/controller_adapter_runtime.stderr.log" \
  "${RESULT_DIR}/controller_output_adapter_node.json" \
  "${RESULT_DIR}/controller_output_adapter_node.trace.jsonl" \
  "${RESULT_DIR}/controller_output_node.stdout.log" \
  "${RESULT_DIR}/controller_output_node.stderr.log" \
  "${RESULT_DIR}/controller_output_fixture.json" \
  "${RESULT_DIR}/controller_output_fixture.stdout.log" \
  "${RESULT_DIR}/controller_output_fixture.stderr.log" \
  "${RESULT_DIR}/controller_output_fixture.rc" \
  "${RESULT_DIR}/command_ack_guard_report.json" \
  "${RESULT_DIR}/stale_controller_output.json" \
  "${RESULT_DIR}/stale_controller_output_report.json" \
  "${RESULT_DIR}/stale_controller_output.rc" \
  "${RESULT_DIR}/stale_controller_output.stdout.log" \
  "${RESULT_DIR}/stale_controller_output.stderr.log" \
  "${RESULT_DIR}/controller_output_node.rc" \
  "${RESULT_DIR}/${PLANNER_HANDOFF_FORBIDDEN_TOPIC_EVIDENCE}" \
  "${RESULT_DIR}/fastlio_planner_input_adapter.json" \
  "${RESULT_DIR}/fastlio_planner_input_adapter.trace.jsonl" \
  "${RESULT_DIR}/fastlio_planner_input_adapter.stdout.log" \
  "${RESULT_DIR}/fastlio_planner_input_adapter.stderr.log" \
  "${RESULT_DIR}/fastlio_imu_passthrough.json" \
  "${RESULT_DIR}/fastlio_imu_passthrough.trace.jsonl" \
  "${RESULT_DIR}/fastlio_imu_passthrough.stdout.log" \
  "${RESULT_DIR}/fastlio_imu_passthrough.stderr.log" \
  "${SPARK_FASTLIO_OUTPUT_DIR}/FASTLIO_RUNTIME_RECORDING.json" \
  "${SPARK_FASTLIO_OUTPUT_DIR}/fastlio_odometry.jsonl" \
  "${SPARK_FASTLIO_OUTPUT_DIR}/fastlio_path.jsonl" \
  "${SPARK_FASTLIO_OUTPUT_DIR}/fastlio_registered_cloud_summary.jsonl" \
  "${GAZEBO_TRUTH_POSE_JSONL}" \
  "${GAZEBO_TRUTH_POSE_SUMMARY_JSON}" \
  "${FASTLIO_TRUTH_ERROR_EVAL_JSON}" \
  "${GAZEBO_PLANT_RESPONSE_EVAL_JSON}" \
  "${RESULT_DIR}/gazebo_truth_pose_recorder.stdout.log" \
  "${RESULT_DIR}/gazebo_truth_pose_recorder.stderr.log" \
  "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" \
  "${RESULT_DIR}/fastlio_truth_error_eval.stdout.log" \
  "${RESULT_DIR}/fastlio_truth_error_eval.stderr.log" \
  "${RESULT_DIR}/fastlio_truth_error_eval.rc" \
  "${RESULT_DIR}/gazebo_plant_response_eval.stdout.log" \
  "${RESULT_DIR}/gazebo_plant_response_eval.stderr.log" \
  "${RESULT_DIR}/gazebo_plant_response_eval.rc" \
  "${RESULT_DIR}/spark_fastlio.stdout.log" \
  "${RESULT_DIR}/spark_fastlio.stderr.log" \
  "${RESULT_DIR}/spark_fastlio_recorder.stdout.log" \
  "${RESULT_DIR}/spark_fastlio_recorder.stderr.log" \
  "${RESULT_DIR}/spark_fastlio_recorder.rc" \
  "${RESULT_DIR}/topic_$(topic_key "${ROS_CONTROLLER_OUTPUT_TOPIC}")_once.rc" \
  "${RESULT_DIR}/topic_$(topic_key "${ROS_CONTROLLER_OUTPUT_TOPIC}")_once.txt" \
  "${RESULT_DIR}/topic_$(topic_key "${ROS_CONTROLLER_OUTPUT_TOPIC}")_once.stderr.txt" \
  "${RESULT_DIR}/controller_command.rc" \
  "${RESULT_DIR}/controller_command.stdout.txt" \
  "${RESULT_DIR}/controller_command.stderr.txt" \
  "${RESULT_DIR}/topic_${actuator_ros_key}_once.rc" \
  "${RESULT_DIR}/topic_${actuator_ros_key}_once.txt" \
  "${RESULT_DIR}/topic_${actuator_ros_key}_once.stderr.txt" \
  "${RESULT_DIR}/gz_topic_${actuator_gz_key}_once.rc" \
  "${RESULT_DIR}/gz_topic_${actuator_gz_key}_once.txt" \
  "${RESULT_DIR}/gz_topic_${actuator_gz_key}_once.stderr.txt"

missing_files=()
for path in "${SCENARIO}" "${WORLD}" "${MODEL}" "${SENSOR_FRAGMENT}" "${LOCAL_MAP_SCRIPT}"; do
  [[ -f "${path}" ]] || missing_files+=("${path}")
done
if [[ "${RUN_MAP_REVIEW_CAPTURE}" == "1" ]]; then
  [[ -f "${MAP_REVIEW_RECORDER_SCRIPT}" ]] || missing_files+=("${MAP_REVIEW_RECORDER_SCRIPT}")
fi
[[ -f "${CONTROLLER_ADAPTER_SCRIPT}" ]] || missing_files+=("${CONTROLLER_ADAPTER_SCRIPT}")
if [[ "${RUN_FASTLIO_PLANNER_INPUT_ADAPTER}" == "1" || "${RUNTIME_GATE_PROFILE}" == "fastlio_planner_input" ]]; then
  [[ -f "${FASTLIO_PLANNER_INPUT_SCRIPT}" ]] || missing_files+=("${FASTLIO_PLANNER_INPUT_SCRIPT}")
  [[ -f "${FASTLIO_IMU_PASSTHROUGH_SCRIPT}" ]] || missing_files+=("${FASTLIO_IMU_PASSTHROUGH_SCRIPT}")
fi
if [[ "${RUN_SPARK_FASTLIO}" == "1" || "${RUNTIME_GATE_PROFILE}" == "spark_fastlio_localization" ]]; then
  [[ -f "${SPARK_FASTLIO_SETUP}" ]] || missing_files+=("${SPARK_FASTLIO_SETUP}")
  [[ -f "${SPARK_FASTLIO_LAUNCH_FILE}" ]] || missing_files+=("${SPARK_FASTLIO_LAUNCH_FILE}")
  [[ -f "${SPARK_FASTLIO_CONFIG_PATH}" ]] || missing_files+=("${SPARK_FASTLIO_CONFIG_PATH}")
  [[ -f "${SPARK_FASTLIO_RECORDER_SCRIPT}" ]] || missing_files+=("${SPARK_FASTLIO_RECORDER_SCRIPT}")
fi
if [[ "${RUN_FASTLIO_TRUTH_EVAL}" == "1" || "${RUN_GAZEBO_TRUTH_POSE}" == "1" || "${RUN_PLANT_RESPONSE_EVAL}" == "1" || "${RUNTIME_GATE_PROFILE}" == "single_uav_plant_response_pre_acceptance" || "${RUNTIME_GATE_PROFILE}" == "single_uav_hover_command_bracket" ]]; then
  [[ -f "${GAZEBO_TRUTH_RECORDER_SCRIPT}" ]] || missing_files+=("${GAZEBO_TRUTH_RECORDER_SCRIPT}")
fi
if [[ "${RUN_HEADER_RATE_CHECK}" == "1" ]]; then
  [[ -f "${TOPIC_HEADER_RATE_SCRIPT}" ]] || missing_files+=("${TOPIC_HEADER_RATE_SCRIPT}")
fi
if [[ "${RUN_FASTLIO_TRUTH_EVAL}" == "1" ]]; then
  [[ -f "${FASTLIO_TRUTH_EVAL_SCRIPT}" ]] || missing_files+=("${FASTLIO_TRUTH_EVAL_SCRIPT}")
fi
if [[ "${RUN_PLANT_RESPONSE_EVAL}" == "1" || "${RUNTIME_GATE_PROFILE}" == "single_uav_plant_response_pre_acceptance" || "${RUNTIME_GATE_PROFILE}" == "single_uav_hover_command_bracket" ]]; then
  [[ -f "${PLANT_RESPONSE_EVAL_SCRIPT}" ]] || missing_files+=("${PLANT_RESPONSE_EVAL_SCRIPT}")
fi
if [[ "${RUN_CONTROLLER_OUTPUT_NODE}" == "1" || "${RUNTIME_GATE_PROFILE}" == "controller_output_node_handoff" || "${RUNTIME_GATE_PROFILE}" == "command_acknowledgement_without_closed_loop" || "${RUNTIME_GATE_PROFILE}" == "single_uav_plant_response_pre_acceptance" || "${RUNTIME_GATE_PROFILE}" == "single_uav_hover_command_bracket" ]]; then
  [[ -f "${CONTROLLER_NODE_SCRIPT}" ]] || missing_files+=("${CONTROLLER_NODE_SCRIPT}")
  [[ -f "${CONTROLLER_FIXTURE_SCRIPT}" ]] || missing_files+=("${CONTROLLER_FIXTURE_SCRIPT}")
  [[ -d "${MOSIM_MSGS_PACKAGE}" ]] || missing_files+=("${MOSIM_MSGS_PACKAGE}")
fi
if [[ "${RUN_EGO_STYLE_PLANNER_OUTPUT}" == "1" || "${RUNTIME_GATE_PROFILE}" == "ego_style_planner_output_without_actuation" ]]; then
  [[ -d "${MOSIM_MSGS_PACKAGE}" ]] || missing_files+=("${MOSIM_MSGS_PACKAGE}")
  [[ -d "${MOSIM_SETPOINT_ADAPTER_PACKAGE}" ]] || missing_files+=("${MOSIM_SETPOINT_ADAPTER_PACKAGE}")
fi

if [[ -f "${ROS_SETUP}" ]]; then
  # shellcheck disable=SC1090
  set +u
  source "${ROS_SETUP}"
  set -u
fi

if [[ "${RUN_FASTLIO_PLANNER_INPUT_ADAPTER}" == "1" || "${RUN_SPARK_FASTLIO}" == "1" || "${RUNTIME_GATE_PROFILE}" == "spark_fastlio_localization" ]]; then
  if [[ -f "${SPARK_FASTLIO_SETUP}" ]]; then
    # shellcheck disable=SC1090
    set +u
    source "${SPARK_FASTLIO_SETUP}"
    set -u
  fi
fi

ensure_mosim_msgs_sourced() {
  local setup_path="${MOSIM_ROS2_WS}/install/setup.bash"
  local result_dir_abs="${RESULT_DIR}"
  if [[ "${result_dir_abs}" != /* ]]; then
    result_dir_abs="${PROJECT_ROOT}/${result_dir_abs}"
  fi
  if [[ "${BUILD_MOSIM_ROS2_MSGS}" == "1" || "${RUN_CONTROLLER_OUTPUT_NODE}" == "1" || "${RUN_CONTROLLER_OUTPUT_FIXTURE}" == "1" || "${RUN_EGO_STYLE_PLANNER_OUTPUT}" == "1" || "${RUNTIME_GATE_PROFILE}" == "controller_output_node_handoff" || "${RUNTIME_GATE_PROFILE}" == "command_acknowledgement_without_closed_loop" || "${RUNTIME_GATE_PROFILE}" == "single_uav_hover_command_bracket" || "${RUNTIME_GATE_PROFILE}" == "ego_style_planner_output_without_actuation" ]]; then
    if [[ ! -f "${setup_path}" || "${BUILD_MOSIM_ROS2_MSGS}" == "1" ]]; then
      mkdir -p "${result_dir_abs}"
      mkdir -p "${MOSIM_ROS2_WS}/src"
      local msg_link="${MOSIM_ROS2_WS}/src/mosim_msgs"
      local adapter_link="${MOSIM_ROS2_WS}/src/mosim_setpoint_adapter"
      if [[ -L "${msg_link}" || -f "${msg_link}" ]]; then
        rm -f "${msg_link}"
      fi
      if [[ -L "${adapter_link}" || -f "${adapter_link}" ]]; then
        rm -f "${adapter_link}"
      fi
      if [[ ! -e "${msg_link}" ]]; then
        ln -s "${PROJECT_ROOT}/${MOSIM_MSGS_PACKAGE}" "${msg_link}"
      fi
      if [[ ! -e "${adapter_link}" ]]; then
        ln -s "${PROJECT_ROOT}/${MOSIM_SETPOINT_ADAPTER_PACKAGE}" "${adapter_link}"
      fi
      (
        cd "${MOSIM_ROS2_WS}"
        colcon build --packages-select mosim_msgs mosim_setpoint_adapter \
          > "${result_dir_abs}/mosim_msgs_colcon.stdout.log" \
          2> "${result_dir_abs}/mosim_msgs_colcon.stderr.log"
      )
    fi
    # shellcheck disable=SC1090
    set +u
    source "${setup_path}"
    set -u
  fi
}

ros2_path="$(command_path ros2)"
colcon_path="$(command_path colcon)"
gz_path="$(command_path gz)"
ign_path="$(command_path ign)"
ros_gz_bridge_prefix="$(ros_pkg_prefix ros_gz_bridge)"
tf2_ros_prefix="$(ros_pkg_prefix tf2_ros)"
spark_fastlio_prefix="$(ros_pkg_prefix spark_fast_lio)"
parameter_bridge_available="false"
if ros_pkg_has_executable ros_gz_bridge parameter_bridge; then
  parameter_bridge_available="true"
fi
static_transform_publisher_available="false"
if ros_pkg_has_executable tf2_ros static_transform_publisher; then
  static_transform_publisher_available="true"
fi
spark_fastlio_executable_available="false"
if ros_pkg_has_executable spark_fast_lio spark_lio_mapping; then
  spark_fastlio_executable_available="true"
fi
gazebo_sim_cli_path=""
gazebo_sim_cli_command=""
gazebo_sim_cli_kind=""
if [[ -n "${gz_path}" ]]; then
  gazebo_sim_cli_path="${gz_path}"
  gazebo_sim_cli_command="gz sim"
  gazebo_sim_cli_kind="gz"
elif [[ -n "${ign_path}" ]]; then
  gazebo_sim_cli_path="${ign_path}"
  gazebo_sim_cli_command="ign gazebo"
  gazebo_sim_cli_kind="ign"
fi

blockers=()
[[ "${#missing_files[@]}" -eq 0 ]] || blockers+=("missing_project_files")
[[ -f "${ROS_SETUP}" ]] || blockers+=("missing_ros_setup:${ROS_SETUP}")
[[ -n "${ros2_path}" ]] || blockers+=("missing_command:ros2")
[[ -n "${colcon_path}" ]] || blockers+=("missing_command:colcon")
[[ -n "${gazebo_sim_cli_path}" ]] || blockers+=("missing_command:gazebo_sim_cli(gz_or_ign)")
[[ -n "${ros_gz_bridge_prefix}" ]] || blockers+=("missing_ros2_package:ros_gz_bridge")
[[ "${parameter_bridge_available}" == "true" ]] || blockers+=("missing_ros2_executable:ros_gz_bridge/parameter_bridge")
if [[ "${RUN_STATIC_TF}" == "1" || "${RUN_TF_CHECK}" == "1" ]]; then
  [[ -n "${tf2_ros_prefix}" ]] || blockers+=("missing_ros2_package:tf2_ros")
  [[ "${static_transform_publisher_available}" == "true" ]] || blockers+=("missing_ros2_executable:tf2_ros/static_transform_publisher")
fi
if [[ "${RUN_SPARK_FASTLIO}" == "1" || "${RUNTIME_GATE_PROFILE}" == "spark_fastlio_localization" ]]; then
  [[ "${RUN_FASTLIO_PLANNER_INPUT_ADAPTER}" == "1" ]] || blockers+=("spark_fastlio_requires_fastlio_planner_input_adapter")
  [[ -n "${spark_fastlio_prefix}" ]] || blockers+=("missing_ros2_package:spark_fast_lio")
  [[ "${spark_fastlio_executable_available}" == "true" ]] || blockers+=("missing_ros2_executable:spark_fast_lio/spark_lio_mapping")
fi

if [[ "${#blockers[@]}" -eq 0 ]]; then
  if ! ensure_mosim_msgs_sourced; then
    blockers+=("mosim_msgs_colcon_build_or_source_failed")
  fi
fi
mosim_msgs_prefix="$(ros_pkg_prefix mosim_msgs)"
mosim_setpoint_adapter_prefix="$(ros_pkg_prefix mosim_setpoint_adapter)"
if [[ "${RUN_CONTROLLER_OUTPUT_NODE}" == "1" || "${RUN_CONTROLLER_OUTPUT_FIXTURE}" == "1" || "${RUN_EGO_STYLE_PLANNER_OUTPUT}" == "1" || "${RUNTIME_GATE_PROFILE}" == "controller_output_node_handoff" || "${RUNTIME_GATE_PROFILE}" == "command_acknowledgement_without_closed_loop" || "${RUNTIME_GATE_PROFILE}" == "single_uav_plant_response_pre_acceptance" || "${RUNTIME_GATE_PROFILE}" == "single_uav_hover_command_bracket" || "${RUNTIME_GATE_PROFILE}" == "ego_style_planner_output_without_actuation" ]]; then
  [[ -n "${mosim_msgs_prefix}" ]] || blockers+=("missing_ros2_package:mosim_msgs")
fi
if [[ "${RUN_EGO_STYLE_PLANNER_OUTPUT}" == "1" || "${RUNTIME_GATE_PROFILE}" == "ego_style_planner_output_without_actuation" ]]; then
  [[ -n "${mosim_setpoint_adapter_prefix}" ]] || blockers+=("missing_ros2_package:mosim_setpoint_adapter")
fi

required_topics_json="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
print(json.dumps(data["ros2"]["topics"], ensure_ascii=False, indent=2))
PY
)"

cat > "${TOPIC_CONTRACT_JSON}" <<JSON
{
  "schema": "mosim.gazebo_ros2_topic_contract.v1",
  "scenario": "${SCENARIO}",
  "topics": ${required_topics_json},
  "topic_gates": ${TOPIC_GATES_JSON},
  "local_map_frame_boundary": ${LOCAL_MAP_FRAME_BOUNDARY_JSON},
  "claim": "static topic contract only until a bounded Gazebo+ROS2 run records measured topics, rates, TF, and map outputs"
}
JSON

missing_files_json="$(printf '%s\n' "${missing_files[@]:-}" | json_array_from_lines)"
blockers_json="$(printf '%s\n' "${blockers[@]:-}" | json_array_from_lines)"

cat > "${PREFLIGHT_JSON}" <<JSON
{
  "schema": "mosim.gazebo_ros2_preflight.v1",
  "scenario": "${SCENARIO}",
  "dry_run": $([[ "${DRY_RUN}" == "1" ]] && echo true || echo false),
  "run_gazebo": $([[ "${RUN_GAZEBO}" == "1" ]] && echo true || echo false),
  "run_ros2_bridge": $([[ "${RUN_ROS2_BRIDGE}" == "1" ]] && echo true || echo false),
  "run_local_map": $([[ "${RUN_LOCAL_MAP}" == "1" ]] && echo true || echo false),
  "run_map_review_capture": $([[ "${RUN_MAP_REVIEW_CAPTURE}" == "1" ]] && echo true || echo false),
  "run_topic_check": $([[ "${RUN_TOPIC_CHECK}" == "1" ]] && echo true || echo false),
  "run_rate_check": $([[ "${RUN_RATE_CHECK}" == "1" ]] && echo true || echo false),
  "run_static_tf": $([[ "${RUN_STATIC_TF}" == "1" ]] && echo true || echo false),
  "run_tf_check": $([[ "${RUN_TF_CHECK}" == "1" ]] && echo true || echo false),
  "run_fastlio_planner_input_adapter": $([[ "${RUN_FASTLIO_PLANNER_INPUT_ADAPTER}" == "1" ]] && echo true || echo false),
  "run_spark_fastlio": $([[ "${RUN_SPARK_FASTLIO}" == "1" ]] && echo true || echo false),
  "run_gazebo_truth_pose": $([[ "${RUN_GAZEBO_TRUTH_POSE}" == "1" ]] && echo true || echo false),
  "run_plant_response_eval": $([[ "${RUN_PLANT_RESPONSE_EVAL}" == "1" ]] && echo true || echo false),
  "run_actuator_bridge": $([[ "${RUN_ACTUATOR_BRIDGE}" == "1" ]] && echo true || echo false),
  "run_controller_command": $([[ "${RUN_CONTROLLER_COMMAND}" == "1" ]] && echo true || echo false),
  "run_controller_output_node": $([[ "${RUN_CONTROLLER_OUTPUT_NODE}" == "1" ]] && echo true || echo false),
  "run_controller_output_fixture": $([[ "${RUN_CONTROLLER_OUTPUT_FIXTURE}" == "1" ]] && echo true || echo false),
  "run_actuator_command_check": $([[ "${RUN_ACTUATOR_COMMAND_CHECK}" == "1" ]] && echo true || echo false),
  "run_command_ack_guard": $([[ "${RUN_COMMAND_ACK_GUARD}" == "1" ]] && echo true || echo false),
  "runtime_gate_profile": "${RUNTIME_GATE_PROFILE}",
  "gazebo_render_engine_server": "${GAZEBO_RENDER_ENGINE_SERVER}",
  "gazebo_resource_paths": "${GAZEBO_RESOURCE_PATHS}",
  "gz_sim_resource_path": "${GZ_SIM_RESOURCE_PATH:-}",
  "ign_gazebo_resource_path": "${IGN_GAZEBO_RESOURCE_PATH:-}",
  "mesa_d3d12_default_adapter_name": "${MESA_D3D12_DEFAULT_ADAPTER_NAME:-}",
  "glx_vendor_library_name": "${__GLX_VENDOR_LIBRARY_NAME:-}",
  "libgl_always_software": "${LIBGL_ALWAYS_SOFTWARE:-}",
  "mosim_gazebo_inherit_resource_paths": "${MOSIM_GAZEBO_INHERIT_RESOURCE_PATHS:-0}",
  "start_gazebo_paused": "${START_GAZEBO_PAUSED}",
  "unpause_gazebo_after_controller_command": "${UNPAUSE_GAZEBO_AFTER_CONTROLLER_COMMAND}",
  "controller_command_type": "${CONTROLLER_COMMAND_TYPE}",
  "controller_command_values": "${CONTROLLER_COMMAND_VALUES}",
  "controller_command_rate_hz": "${CONTROLLER_COMMAND_RATE_HZ}",
  "controller_command_times": "${CONTROLLER_COMMAND_TIMES}",
  "controller_output_node_max_messages": "${CONTROLLER_OUTPUT_NODE_MAX_MESSAGES}",
  "command_ack_max_age_s": "${COMMAND_ACK_MAX_AGE_S}",
  "command_ack_stale_age_s": "${COMMAND_ACK_STALE_AGE_S}",
  "world": "${WORLD}",
  "model": "${MODEL}",
  "sensor_fragment": "${SENSOR_FRAGMENT}",
  "local_map_script": "${LOCAL_MAP_SCRIPT}",
  "fastlio_planner_input_script": "${FASTLIO_PLANNER_INPUT_SCRIPT}",
  "fastlio_imu_passthrough_script": "${FASTLIO_IMU_PASSTHROUGH_SCRIPT}",
  "spark_fastlio_setup": "${SPARK_FASTLIO_SETUP}",
  "spark_fastlio_prefix": "${spark_fastlio_prefix}",
  "spark_fastlio_executable_available": $([[ "${spark_fastlio_executable_available}" == "true" ]] && echo true || echo false),
  "spark_fastlio_launch_file": "${SPARK_FASTLIO_LAUNCH_FILE}",
  "spark_fastlio_config_path": "${SPARK_FASTLIO_CONFIG_PATH}",
  "spark_fastlio_recorder_script": "${SPARK_FASTLIO_RECORDER_SCRIPT}",
  "spark_fastlio_output_dir": "${SPARK_FASTLIO_OUTPUT_DIR}",
  "spark_fastlio_record_seconds": "${SPARK_FASTLIO_RECORD_SECONDS}",
  "gazebo_truth_recorder_script": "${GAZEBO_TRUTH_RECORDER_SCRIPT}",
  "gazebo_truth_pose_jsonl": "${GAZEBO_TRUTH_POSE_JSONL}",
  "gazebo_truth_pose_summary": "${GAZEBO_TRUTH_POSE_SUMMARY_JSON}",
  "gazebo_truth_recorder_timeout_seconds": "${GAZEBO_TRUTH_RECORDER_TIMEOUT_SECONDS}",
  "plant_response_eval_script": "${PLANT_RESPONSE_EVAL_SCRIPT}",
  "plant_response_eval_json": "${GAZEBO_PLANT_RESPONSE_EVAL_JSON}",
  "plant_response_min_samples": "${PLANT_RESPONSE_MIN_SAMPLES}",
  "plant_response_min_duration_s": "${PLANT_RESPONSE_MIN_DURATION_S}",
  "plant_response_min_z_delta_m": "${PLANT_RESPONSE_MIN_Z_DELTA_M}",
  "plant_response_min_3d_delta_m": "${PLANT_RESPONSE_MIN_3D_DELTA_M}",
  "controller_adapter_script": "${CONTROLLER_ADAPTER_SCRIPT}",
  "controller_node_script": "${CONTROLLER_NODE_SCRIPT}",
  "controller_fixture_script": "${CONTROLLER_FIXTURE_SCRIPT}",
  "mosim_msgs_package": "${MOSIM_MSGS_PACKAGE}",
  "mosim_ros2_ws": "${MOSIM_ROS2_WS}",
  "mosim_msgs_prefix": "${mosim_msgs_prefix}",
  "ros_controller_output_topic": "${ROS_CONTROLLER_OUTPUT_TOPIC}",
  "ros_imu_topic": "${ROS_IMU_TOPIC}",
  "ros_lidar_points_topic": "${ROS_LIDAR_POINTS_TOPIC}",
  "ros_local_voxel_topic": "${ROS_LOCAL_VOXEL_TOPIC}",
  "ros_local_grid_topic": "${ROS_LOCAL_GRID_TOPIC}",
  "ros_fastlio_lidar_topic": "${ROS_FASTLIO_LIDAR_TOPIC}",
  "ros_fastlio_imu_topic": "${ROS_FASTLIO_IMU_TOPIC}",
  "ros_spark_fastlio_livox_topic": "${ROS_SPARK_FASTLIO_LIVOX_TOPIC}",
  "ros_sunray_fastlio_lidar_topic": "${ROS_SUNRAY_FASTLIO_LIDAR_TOPIC}",
  "ros_sunray_fastlio_imu_topic": "${ROS_SUNRAY_FASTLIO_IMU_TOPIC}",
  "ros_planner_global_points_topic": "${ROS_PLANNER_GLOBAL_POINTS_TOPIC}",
  "ros_mosim_planner_global_points_topic": "${ROS_MOSIM_PLANNER_GLOBAL_POINTS_TOPIC}",
  "ros_planner_odom_topic": "${ROS_PLANNER_ODOM_TOPIC}",
  "ros_mosim_planner_odom_topic": "${ROS_MOSIM_PLANNER_ODOM_TOPIC}",
  "ros_spark_fastlio_registered_cloud_topic": "${ROS_SPARK_FASTLIO_REGISTERED_CLOUD_TOPIC}",
  "ros_spark_fastlio_odometry_topic": "${ROS_SPARK_FASTLIO_ODOMETRY_TOPIC}",
  "ros_spark_fastlio_path_topic": "${ROS_SPARK_FASTLIO_PATH_TOPIC}",
  "ros_tf_static_topic": "${ROS_TF_STATIC_TOPIC}",
  "local_map_map_frame": "${LOCAL_MAP_MAP_FRAME}",
  "local_map_expected_input_frame": "${LOCAL_MAP_EXPECTED_INPUT_FRAME}",
  "local_map_frame_boundary": ${LOCAL_MAP_FRAME_BOUNDARY_JSON},
  "ros_actuator_topic": "${ROS_ACTUATOR_TOPIC}",
  "gz_actuator_topic": "${GZ_ACTUATOR_TOPIC}",
  "controller_actuator_ros_type": "${CONTROLLER_ACTUATOR_ROS_TYPE}",
  "controller_actuator_gz_type": "${CONTROLLER_ACTUATOR_GZ_TYPE}",
  "scenario_outputs": {
    "run_manifest": "${SCENARIO_RUN_MANIFEST}",
    "runtime_status": "${SCENARIO_RUNTIME_STATUS_JSON}",
    "blocker": "${SCENARIO_BLOCKER}",
    "preflight": "${SCENARIO_PREFLIGHT_JSON}",
    "topic_contract": "${SCENARIO_TOPIC_CONTRACT_JSON}"
  },
  "ros_setup": "${ROS_SETUP}",
  "commands": {
    "ros2": "${ros2_path}",
    "colcon": "${colcon_path}",
    "gz": "${gz_path}",
    "ign": "${ign_path}",
    "gazebo_sim_cli_path": "${gazebo_sim_cli_path}",
    "gazebo_sim_cli_command": "${gazebo_sim_cli_command}",
    "gazebo_sim_cli_kind": "${gazebo_sim_cli_kind}",
    "ros_gz_bridge_prefix": "${ros_gz_bridge_prefix}",
    "parameter_bridge": "ros2 run ros_gz_bridge parameter_bridge",
    "parameter_bridge_available": ${parameter_bridge_available},
    "tf2_ros_prefix": "${tf2_ros_prefix}",
    "static_transform_publisher_available": ${static_transform_publisher_available}
  },
  "topic_gates": ${TOPIC_GATES_JSON},
  "rate_gate_min_fraction": ${RATE_GATE_MIN_FRACTION},
  "local_map_frame_boundary": ${LOCAL_MAP_FRAME_BOUNDARY_JSON},
  "missing_project_files": ${missing_files_json},
  "blockers": ${blockers_json},
  "claim_boundary": [
    "preflight does not prove Gazebo runtime",
    "dry-run does not prove ROS2 topics",
    "Gazebo+ROS2 validation cannot replace MWORKS/Syslab competition metric evidence"
  ]
}
JSON

if [[ "${DRY_RUN}" == "1" || "${#blockers[@]}" -gt 0 || "${RUN_GAZEBO}" != "1" ]]; then
  status="blocked"
  reason="preflight_only"
  if [[ "${#blockers[@]}" -gt 0 ]]; then
    reason="environment_or_file_blocker"
  fi
  if [[ "${DRY_RUN}" == "1" ]]; then
    reason="dry_run_only"
    if [[ "${#blockers[@]}" -gt 0 ]]; then
      reason="dry_run_only_with_dependency_blockers"
    fi
  fi
  cat > "${RUNTIME_STATUS_JSON}" <<JSON
{
  "schema": "mosim.gazebo_ros2_runtime_status.v1",
  "scenario": "${SCENARIO}",
  "result_dir": "${RESULT_DIR}",
  "status": "preflight_blocked",
  "gate_passed": false,
  "preflight": "${PREFLIGHT_JSON}",
  "topic_contract": "${TOPIC_CONTRACT_JSON}",
  "blockers": ${blockers_json},
  "warnings": [
    "${reason}"
  ],
  "requested_checks": {
    "run_gazebo": $([[ "${RUN_GAZEBO}" == "1" ]] && echo true || echo false),
    "run_ros2_bridge": $([[ "${RUN_ROS2_BRIDGE}" == "1" ]] && echo true || echo false),
    "run_local_map": $([[ "${RUN_LOCAL_MAP}" == "1" ]] && echo true || echo false),
    "run_topic_check": $([[ "${RUN_TOPIC_CHECK}" == "1" ]] && echo true || echo false),
    "run_rate_check": $([[ "${RUN_RATE_CHECK}" == "1" ]] && echo true || echo false),
    "run_tf_check": $([[ "${RUN_TF_CHECK}" == "1" ]] && echo true || echo false),
    "run_fastlio_planner_input_adapter": $([[ "${RUN_FASTLIO_PLANNER_INPUT_ADAPTER}" == "1" ]] && echo true || echo false),
    "run_ego_style_planner_output": $([[ "${RUN_EGO_STYLE_PLANNER_OUTPUT}" == "1" ]] && echo true || echo false),
    "run_spark_fastlio": $([[ "${RUN_SPARK_FASTLIO}" == "1" ]] && echo true || echo false),
    "run_gazebo_truth_pose": $([[ "${RUN_GAZEBO_TRUTH_POSE}" == "1" ]] && echo true || echo false),
    "run_plant_response_eval": $([[ "${RUN_PLANT_RESPONSE_EVAL}" == "1" ]] && echo true || echo false),
    "run_actuator_bridge": $([[ "${RUN_ACTUATOR_BRIDGE}" == "1" ]] && echo true || echo false),
    "run_controller_command": $([[ "${RUN_CONTROLLER_COMMAND}" == "1" ]] && echo true || echo false),
    "run_controller_output_node": $([[ "${RUN_CONTROLLER_OUTPUT_NODE}" == "1" ]] && echo true || echo false),
    "run_controller_output_fixture": $([[ "${RUN_CONTROLLER_OUTPUT_FIXTURE}" == "1" ]] && echo true || echo false),
    "run_actuator_command_check": $([[ "${RUN_ACTUATOR_COMMAND_CHECK}" == "1" ]] && echo true || echo false),
    "run_command_ack_guard": $([[ "${RUN_COMMAND_ACK_GUARD}" == "1" ]] && echo true || echo false)
  },
  "process_alive": {
    "gazebo": false,
    "ros2_bridge": false,
    "local_map_adapter": false
  },
  "topic_gates": ${TOPIC_GATES_JSON},
  "rate_gate_min_fraction": ${RATE_GATE_MIN_FRACTION},
  "local_map_frame_boundary": ${LOCAL_MAP_FRAME_BOUNDARY_JSON},
  "claim_boundary": [
    "preflight_blocked does not prove Gazebo runtime",
    "preflight_blocked does not prove ROS2 topic samples",
    "Gazebo+ROS2 validation cannot replace MWORKS/Syslab competition metric evidence"
  ]
}
JSON
  cat > "${BLOCKER}" <<JSON
{
  "schema": "mosim.gazebo_ros2_blocker.v1",
  "status": "${status}",
  "reason": "${reason}",
  "scenario": "${SCENARIO}",
  "preflight": "${PREFLIGHT_JSON}",
  "topic_contract": "${TOPIC_CONTRACT_JSON}",
  "blockers": ${blockers_json},
  "next_unblock": [
    "Run from WSL Ubuntu 22.04 with ROS2 Humble sourced.",
    "Install or source Gazebo Sim and ros_gz_bridge so 'gz sim' or Fortress 'ign gazebo' plus ros2 run ros_gz_bridge parameter_bridge are available.",
    "Rerun with RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_ACTUATOR_BRIDGE=1 RUN_CONTROLLER_COMMAND=1 RUN_ACTUATOR_COMMAND_CHECK=1 RUN_LOCAL_MAP=1 RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=1 RUN_STATIC_TF=1 RUN_TF_CHECK=1 after preflight blockers are clear.",
    "For the ControllerOutput node handoff, also set RUN_CONTROLLER_OUTPUT_NODE=1 RUN_CONTROLLER_OUTPUT_FIXTURE=1 BUILD_MOSIM_ROS2_MSGS=1 RUNTIME_GATE_PROFILE=controller_output_node_handoff.",
    "For a single hover-bracket sample, use RUNTIME_GATE_PROFILE=single_uav_hover_command_bracket with RUN_GAZEBO_TRUTH_POSE=1 RUN_PLANT_RESPONSE_EVAL=1 RUN_CONTROLLER_OUTPUT_NODE=1 RUN_CONTROLLER_OUTPUT_FIXTURE=1."
  ],
  "claim_boundary": "No Gazebo process, ROS2 graph, PointCloud2, voxel map, planner handoff, or closed-loop success is claimed."
}
JSON
  echo "${BLOCKER}"
  exit 0
fi

gz_pid=""
bridge_pid=""
local_map_pid=""
fastlio_planner_input_pid=""
fastlio_imu_passthrough_pid=""
ego_style_planner_pid=""
position_command_converter_pid=""
planner_setpoint_adapter_pid=""
spark_fastlio_pid=""
static_tf_pid=""
static_tf_lidar_pid=""
static_tf_imu_pid=""
controller_output_node_pid=""
controller_output_echo_pid=""
ros_actuator_echo_pid=""
gz_actuator_echo_pid=""
gazebo_truth_pose_recorder_pid=""
cleanup() {
  terminate_process_tree "${gazebo_truth_pose_recorder_pid}" 2
  terminate_process_tree "${gz_actuator_echo_pid}" 1
  terminate_process_tree "${ros_actuator_echo_pid}" 1
  terminate_process_tree "${controller_output_echo_pid}" 1
  terminate_process_tree "${static_tf_imu_pid}" 1
  terminate_process_tree "${static_tf_lidar_pid}" 1
  terminate_process_tree "${static_tf_pid}" 1
  terminate_process_tree "${controller_output_node_pid}" 2
  terminate_process_tree "${ego_style_planner_pid}" 2
  terminate_process_tree "${position_command_converter_pid}" 2
  terminate_process_tree "${planner_setpoint_adapter_pid}" 2
  terminate_process_tree "${local_map_pid}" 2
  terminate_process_tree "${fastlio_planner_input_pid}" 2
  terminate_process_tree "${fastlio_imu_passthrough_pid}" 2
  terminate_process_tree "${spark_fastlio_pid}" 2
  terminate_process_tree "${bridge_pid}" 2
  terminate_process_tree "${gz_pid}" 3
}
trap cleanup EXIT

drain_stale_project_gazebo "${WORLD}"

run_flag=()
if [[ "${START_GAZEBO_PAUSED}" != "1" ]]; then
  run_flag=(-r)
fi

if [[ "${gazebo_sim_cli_kind}" == "gz" ]]; then
  "${gazebo_sim_cli_path}" sim -s "${run_flag[@]}" --headless-rendering --render-engine-server "${GAZEBO_RENDER_ENGINE_SERVER}" "${WORLD}" > "${RESULT_DIR}/gazebo.stdout.log" 2> "${RESULT_DIR}/gazebo.stderr.log" &
else
  "${gazebo_sim_cli_path}" gazebo -s "${run_flag[@]}" --headless-rendering --render-engine-server "${GAZEBO_RENDER_ENGINE_SERVER}" "${WORLD}" > "${RESULT_DIR}/gazebo.stdout.log" 2> "${RESULT_DIR}/gazebo.stderr.log" &
fi
gz_pid="$!"
sleep 4

if [[ "${RUN_ROS2_BRIDGE}" == "1" ]]; then
  bridge_args=(
    "${ROS_IMU_TOPIC}@sensor_msgs/msg/Imu@gz.msgs.IMU"
    "${ROS_LIDAR_POINTS_TOPIC}@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked"
  )
  if [[ "${GAZEBO_TRUTH_RECORDER_BASENAME}" == "record_pose_array_truth.py" && ( "${RUN_GAZEBO_TRUTH_POSE}" == "1" || "${RUN_PLANT_RESPONSE_EVAL}" == "1" || "${RUN_FASTLIO_TRUTH_EVAL}" == "1" ) ]]; then
    bridge_args+=("${GAZEBO_TRUTH_ROS_TOPIC}@${GAZEBO_TRUTH_ROS_MESSAGE}[${GAZEBO_TRUTH_GZ_MESSAGE}")
  fi
  if [[ "${RUN_ACTUATOR_BRIDGE}" == "1" ]]; then
    bridge_args+=("${ROS_ACTUATOR_TOPIC}@actuator_msgs/msg/Actuators@gz.msgs.Actuators")
  fi
  ros2 run ros_gz_bridge parameter_bridge "${bridge_args[@]}" \
    > "${RESULT_DIR}/ros_gz_bridge.stdout.log" \
    2> "${RESULT_DIR}/ros_gz_bridge.stderr.log" &
  bridge_pid="$!"
  sleep 3
fi

if [[ "${RUN_STATIC_TF}" == "1" ]]; then
  static_tf_child_frame="${LOCAL_MAP_EXPECTED_INPUT_FRAME}"
  static_tf_lidar_child_frame=""
  static_tf_imu_child_frame=""
  if [[ "${RUN_SPARK_FASTLIO}" == "1" || "${RUNTIME_GATE_PROFILE}" == "spark_fastlio_localization" ]]; then
    static_tf_frames="$(python3 - <<PY
import json
data=json.loads('''${scenario_json}''')
runtime=data["ros2"].get("spark_fastlio_runtime", {})
print(
    runtime.get("base_frame", f"{data.get('vehicle_id', 'sunray150')}/base_link"),
    runtime.get("lidar_frame", ""),
    runtime.get("imu_frame", ""),
)
PY
)"
    read -r static_tf_child_frame static_tf_lidar_child_frame static_tf_imu_child_frame <<< "${static_tf_frames}"
  fi
  ros2 run tf2_ros static_transform_publisher \
    --x 0 --y 0 --z 1.2 \
    --roll 0 --pitch 0 --yaw 0 \
    --frame-id "${LOCAL_MAP_MAP_FRAME}" \
    --child-frame-id "${static_tf_child_frame}" \
    > "${RESULT_DIR}/static_tf.stdout.log" \
    2> "${RESULT_DIR}/static_tf.stderr.log" &
  static_tf_pid="$!"
  if [[ -n "${static_tf_lidar_child_frame}" && "${static_tf_lidar_child_frame}" != "${static_tf_child_frame}" ]]; then
    ros2 run tf2_ros static_transform_publisher \
      --x 0 --y 0 --z 0 \
      --roll 0 --pitch 0 --yaw 0 \
      --frame-id "${static_tf_child_frame}" \
      --child-frame-id "${static_tf_lidar_child_frame}" \
      >> "${RESULT_DIR}/static_tf.stdout.log" \
      2>> "${RESULT_DIR}/static_tf.stderr.log" &
    static_tf_lidar_pid="$!"
  fi
  if [[ -n "${static_tf_imu_child_frame}" && "${static_tf_imu_child_frame}" != "${static_tf_child_frame}" ]]; then
    ros2 run tf2_ros static_transform_publisher \
      --x 0 --y 0 --z 0 \
      --roll 0 --pitch 0 --yaw 0 \
      --frame-id "${static_tf_child_frame}" \
      --child-frame-id "${static_tf_imu_child_frame}" \
      >> "${RESULT_DIR}/static_tf.stdout.log" \
      2>> "${RESULT_DIR}/static_tf.stderr.log" &
    static_tf_imu_pid="$!"
  fi
  sleep 1
fi

if [[ "${RUN_GAZEBO_TRUTH_POSE}" == "1" || "${RUN_PLANT_RESPONSE_EVAL}" == "1" || "${RUN_FASTLIO_TRUTH_EVAL}" == "1" ]]; then
  gazebo_truth_record_topic="${GAZEBO_TRUTH_TOPIC}"
  if [[ "${GAZEBO_TRUTH_RECORDER_BASENAME}" == "record_pose_array_truth.py" ]]; then
    gazebo_truth_record_topic="${GAZEBO_TRUTH_ROS_TOPIC}"
  fi
  gazebo_truth_recorder_args=(
    --output-jsonl "${GAZEBO_TRUTH_POSE_JSONL}"
    --summary-json "${GAZEBO_TRUTH_POSE_SUMMARY_JSON}"
    --topic "${gazebo_truth_record_topic}"
    --model-name "${GAZEBO_TRUTH_MODEL_NAME}"
    --frame-id "${GAZEBO_TRUTH_FRAME_ID}"
    --timeout-seconds "${GAZEBO_TRUTH_RECORDER_TIMEOUT_SECONDS}"
  )
  if [[ "${GAZEBO_TRUTH_RECORDER_BASENAME}" == "capture_gazebo_pose_truth_topic.py" ]]; then
    gazebo_truth_recorder_args+=(--startup-delay-seconds 6 --sample-timeout-seconds "${GAZEBO_TRUTH_SAMPLE_TIMEOUT_SECONDS}")
  fi
  if [[ -n "${GAZEBO_TRUTH_EXPECTED_ENTITY_ID}" && "${GAZEBO_TRUTH_RECORDER_BASENAME}" == "capture_gazebo_state_truth_topic.py" ]]; then
    gazebo_truth_recorder_args+=(--expected-entity-id "${GAZEBO_TRUTH_EXPECTED_ENTITY_ID}")
  fi
  python3 "${GAZEBO_TRUTH_RECORDER_SCRIPT}" \
    "${gazebo_truth_recorder_args[@]}" \
    > "${RESULT_DIR}/gazebo_truth_pose_recorder.stdout.log" \
    2> "${RESULT_DIR}/gazebo_truth_pose_recorder.stderr.log" &
  gazebo_truth_pose_recorder_pid="$!"
  sleep 1
fi

if [[ "${RUN_LOCAL_MAP}" == "1" ]]; then
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

if [[ "${RUN_FASTLIO_PLANNER_INPUT_ADAPTER}" == "1" ]]; then
  python3 "${FASTLIO_IMU_PASSTHROUGH_SCRIPT}" \
    ${FASTLIO_IMU_PASSTHROUGH_ARGS} \
    > "${RESULT_DIR}/fastlio_imu_passthrough.stdout.log" \
    2> "${RESULT_DIR}/fastlio_imu_passthrough.stderr.log" &
  fastlio_imu_passthrough_pid="$!"
  sleep 1
  python3 "${FASTLIO_PLANNER_INPUT_SCRIPT}" \
    ${FASTLIO_PLANNER_INPUT_ARGS} \
    > "${RESULT_DIR}/fastlio_planner_input_adapter.stdout.log" \
    2> "${RESULT_DIR}/fastlio_planner_input_adapter.stderr.log" &
  fastlio_planner_input_pid="$!"
  sleep 2
fi

if [[ "${RUN_EGO_STYLE_PLANNER_OUTPUT}" == "1" ]]; then
  if [[ "${RUN_FASTLIO_PLANNER_INPUT_ADAPTER}" != "1" ]]; then
    echo "RUN_EGO_STYLE_PLANNER_OUTPUT requires RUN_FASTLIO_PLANNER_INPUT_ADAPTER=1" > "${RESULT_DIR}/ego_style_planner_output.stderr.log"
  else
    ros2 run mosim_setpoint_adapter position_command_to_planner_setpoint_node \
      --ros-args \
      -p input_topic:="${ROS_REFERENCE_POSITION_CMD_TOPIC}" \
      -p output_topic:="${ROS_MOSIM_PLANNER_POSITION_CMD_TOPIC}" \
      -p expected_frame:="map" \
      -p source_frame_alias:="world" \
      > "${RESULT_DIR}/position_command_converter.stdout.log" \
      2> "${RESULT_DIR}/position_command_converter.stderr.log" &
    position_command_converter_pid="$!"
    sleep 1
    ros2 run mosim_setpoint_adapter planner_setpoint_adapter_node \
      --ros-args \
      -p input_topic:="${ROS_MOSIM_PLANNER_POSITION_CMD_TOPIC}" \
      -p output_topic:="${ROS_PLANNER_SETPOINT_TOPIC}" \
      -p status_topic:="${ROS_PLANNER_SETPOINT_STATUS_TOPIC}" \
      -p expected_frame:="map" \
      > "${RESULT_DIR}/planner_setpoint_adapter.stdout.log" \
      2> "${RESULT_DIR}/planner_setpoint_adapter.stderr.log" &
    planner_setpoint_adapter_pid="$!"
    sleep 1
    python3 "${EGO_STYLE_PLANNER_OUTPUT_SCRIPT}" \
      ${EGO_STYLE_PLANNER_ARGS} \
      > "${RESULT_DIR}/ego_style_planner_output.stdout.log" \
      2> "${RESULT_DIR}/ego_style_planner_output.stderr.log" &
    ego_style_planner_pid="$!"
    sleep 2
  fi
fi

if [[ "${RUN_SPARK_FASTLIO}" == "1" ]]; then
  mkdir -p "${SPARK_FASTLIO_OUTPUT_DIR}"
  if [[ "${RUN_FASTLIO_TRUTH_EVAL}" == "1" && -z "${gazebo_truth_pose_recorder_pid}" ]]; then
    gazebo_truth_record_topic="${GAZEBO_TRUTH_TOPIC}"
    if [[ "${GAZEBO_TRUTH_RECORDER_BASENAME}" == "record_pose_array_truth.py" ]]; then
      gazebo_truth_record_topic="${GAZEBO_TRUTH_ROS_TOPIC}"
    fi
    gazebo_truth_recorder_args=(
      --output-jsonl "${GAZEBO_TRUTH_POSE_JSONL}"
      --summary-json "${GAZEBO_TRUTH_POSE_SUMMARY_JSON}"
      --topic "${gazebo_truth_record_topic}"
      --model-name "${GAZEBO_TRUTH_MODEL_NAME}"
      --frame-id "${GAZEBO_TRUTH_FRAME_ID}"
      --timeout-seconds "${SPARK_FASTLIO_RECORDER_TIMEOUT_SECONDS}"
    )
    if [[ "${GAZEBO_TRUTH_RECORDER_BASENAME}" == "capture_gazebo_pose_truth_topic.py" ]]; then
      gazebo_truth_recorder_args+=(--startup-delay-seconds 6 --sample-timeout-seconds "${GAZEBO_TRUTH_SAMPLE_TIMEOUT_SECONDS}")
    fi
    if [[ -n "${GAZEBO_TRUTH_EXPECTED_ENTITY_ID}" && "${GAZEBO_TRUTH_RECORDER_BASENAME}" == "capture_gazebo_state_truth_topic.py" ]]; then
      gazebo_truth_recorder_args+=(--expected-entity-id "${GAZEBO_TRUTH_EXPECTED_ENTITY_ID}")
    fi
    python3 "${GAZEBO_TRUTH_RECORDER_SCRIPT}" \
      "${gazebo_truth_recorder_args[@]}" \
      > "${RESULT_DIR}/gazebo_truth_pose_recorder.stdout.log" \
      2> "${RESULT_DIR}/gazebo_truth_pose_recorder.stderr.log" &
    gazebo_truth_pose_recorder_pid="$!"
    sleep 1
  fi
  ros2 launch "${SPARK_FASTLIO_LAUNCH_FILE}" \
    ${SPARK_FASTLIO_ARGS} \
    > "${RESULT_DIR}/spark_fastlio.stdout.log" \
    2> "${RESULT_DIR}/spark_fastlio.stderr.log" &
  spark_fastlio_pid="$!"
  sleep 4
fi

if [[ "${RUN_CONTROLLER_OUTPUT_NODE}" == "1" ]]; then
  python3 "${CONTROLLER_NODE_SCRIPT}" \
    --input-topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" \
    --output-topic "${ROS_ACTUATOR_TOPIC}" \
    --vehicle-id "sunray150" \
    --max-messages "${CONTROLLER_OUTPUT_NODE_MAX_MESSAGES}" \
    --max-command-age-s "${COMMAND_ACK_MAX_AGE_S}" \
    --output-json "${RESULT_DIR}/controller_output_adapter_node.json" \
    --trace-jsonl "${RESULT_DIR}/controller_output_adapter_node.trace.jsonl" \
    > "${RESULT_DIR}/controller_output_node.stdout.log" \
    2> "${RESULT_DIR}/controller_output_node.stderr.log" &
  controller_output_node_pid="$!"
  sleep 2
fi

topic_list_file="${RESULT_DIR}/ros2_topic_list.txt"
ros2_topic_list_snapshot "${topic_list_file}" 8 1 || true

write_forbidden_topic_presence() {
  local observed_file="$1"
  local output_file="$2"
  python3 - <<PY
import json
from pathlib import Path

scenario = json.loads('''${scenario_json}''')
gate = scenario["ros2"].get("planner_handoff_without_setpoint_publication", {})
forbidden = [str(item) for item in gate.get("forbidden_topics", []) if str(item)]
observed_path = Path("${observed_file}")
observed = []
if observed_path.exists():
    observed = [
        line.strip()
        for line in observed_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip()
    ]
present = [topic for topic in forbidden if topic in observed]
payload = {
    "schema": "mosim.planner_handoff_forbidden_topic_presence.v1",
    "gate_profile": "${RUNTIME_GATE_PROFILE}",
    "topic_list": "${observed_file}",
    "forbidden_topics": forbidden,
    "forbidden_present": present,
    "all_forbidden_absent": not present,
    "claim_boundary": "negative evidence only; absence from ros2 topic list does not prove planner readiness, setpoint authority, command acknowledgement, actuator control, or closed_loop",
}
Path("${output_file}").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
}

if [[ "${RUN_TOPIC_CHECK}" == "1" ]]; then
  topics=("${ROS_IMU_TOPIC}" "${ROS_LIDAR_POINTS_TOPIC}")
  if [[ "${RUN_LOCAL_MAP}" == "1" ]]; then
    topics+=("${ROS_LOCAL_VOXEL_TOPIC}" "${ROS_LOCAL_GRID_TOPIC}")
  fi
  if [[ "${RUN_FASTLIO_PLANNER_INPUT_ADAPTER}" == "1" ]]; then
    topics+=(
      "${ROS_FASTLIO_LIDAR_TOPIC}"
      "${ROS_FASTLIO_IMU_TOPIC}"
      "${ROS_SPARK_FASTLIO_LIVOX_TOPIC}"
      "${ROS_SUNRAY_FASTLIO_LIDAR_TOPIC}"
      "${ROS_SUNRAY_FASTLIO_IMU_TOPIC}"
    )
    if [[ "${RUNTIME_GATE_PROFILE}" != "spark_fastlio_localization" ]]; then
      topics+=(
        "${ROS_PLANNER_GLOBAL_POINTS_TOPIC}"
        "${ROS_MOSIM_PLANNER_GLOBAL_POINTS_TOPIC}"
        "${ROS_PLANNER_ODOM_TOPIC}"
        "${ROS_MOSIM_PLANNER_ODOM_TOPIC}"
      )
    fi
  fi
  if [[ "${RUN_EGO_STYLE_PLANNER_OUTPUT}" == "1" ]]; then
    topics+=(
      "${ROS_REFERENCE_POSITION_CMD_TOPIC}"
      "${ROS_MOSIM_PLANNER_POSITION_CMD_TOPIC}"
      "${ROS_PLANNER_SETPOINT_TOPIC}"
      "${ROS_PLANNER_SETPOINT_STATUS_TOPIC}"
    )
  fi
  if [[ "${RUN_SPARK_FASTLIO}" == "1" ]]; then
    topics+=(
      "${ROS_SPARK_FASTLIO_REGISTERED_CLOUD_TOPIC}"
      "${ROS_SPARK_FASTLIO_ODOMETRY_TOPIC}"
      "${ROS_SPARK_FASTLIO_PATH_TOPIC}"
    )
  fi
  if [[ "${RUN_TF_CHECK}" == "1" ]]; then
    topics+=("${ROS_TF_STATIC_TOPIC}")
  fi
  for topic in "${topics[@]}"; do
    key="$(topic_key "${topic}")"
    message_type=""
    qos_mode=""
    if [[ "${topic}" == "${ROS_IMU_TOPIC}" ]]; then
      message_type="sensor_msgs/msg/Imu"
      qos_mode="sensor_data"
    fi
    if [[ "${topic}" == "${ROS_LIDAR_POINTS_TOPIC}" ]]; then
      message_type="sensor_msgs/msg/PointCloud2"
      qos_mode="sensor_data"
    fi
    if [[ "${topic}" == "${ROS_LOCAL_VOXEL_TOPIC}" ]]; then
      message_type="sensor_msgs/msg/PointCloud2"
      qos_mode="sensor_data"
    fi
    if [[ "${topic}" == "${ROS_LOCAL_GRID_TOPIC}" ]]; then
      message_type="nav_msgs/msg/OccupancyGrid"
    fi
    if [[ "${topic}" == "${ROS_TF_STATIC_TOPIC}" ]]; then
      message_type="tf2_msgs/msg/TFMessage"
      qos_mode="tf_static"
    fi
    ros2_topic_echo_once_retry \
      "${topic}" \
      "${message_type}" \
      "${qos_mode}" \
      "${RESULT_DIR}/topic_${key}_once.txt" \
      "${RESULT_DIR}/topic_${key}_once.stderr.txt" \
      "${RESULT_DIR}/topic_${key}_once.rc" \
      3 \
      1 || true
  done
fi

if [[ "${RUN_MAP_REVIEW_CAPTURE}" == "1" ]]; then
  if timeout "${TIMEOUT_SECONDS}" python3 "${MAP_REVIEW_RECORDER_SCRIPT}" \
    --lidar-topic "${ROS_LIDAR_POINTS_TOPIC}" \
    --voxel-topic "${ROS_LOCAL_VOXEL_TOPIC}" \
    --grid-topic "${ROS_LOCAL_GRID_TOPIC}" \
    --output-dir "${RESULT_DIR}/${MAP_REVIEW_OUTPUT_DIR}" \
    --duration-seconds "${MAP_REVIEW_DURATION_SECONDS}" \
    --include-point-data \
    > "${RESULT_DIR}/map_review_capture.stdout.log" \
    2> "${RESULT_DIR}/map_review_capture.stderr.log"; then
    write_rc "${RESULT_DIR}/map_review_capture.rc" 0
  else
    rc="$?"
    write_rc "${RESULT_DIR}/map_review_capture.rc" "${rc}"
  fi
fi

if [[ "${RUNTIME_GATE_PROFILE}" == "planner_handoff_without_setpoint_publication" ]]; then
  ros2_topic_list_snapshot "${topic_list_file}" 5 1 || true
  write_forbidden_topic_presence "${topic_list_file}" "${RESULT_DIR}/${PLANNER_HANDOFF_FORBIDDEN_TOPIC_EVIDENCE}"
fi

if [[ "${RUN_ACTUATOR_COMMAND_CHECK}" == "1" || "${RUN_CONTROLLER_COMMAND}" == "1" ]]; then
  ros_key="$(topic_key "${ROS_ACTUATOR_TOPIC}")"
  gz_key="$(topic_key "${GZ_ACTUATOR_TOPIC}")"
  controller_output_key="$(topic_key "${ROS_CONTROLLER_OUTPUT_TOPIC}")"

  if [[ "${RUN_CONTROLLER_OUTPUT_FIXTURE}" == "1" ]]; then
    timeout "${TIMEOUT_SECONDS}" ros2 topic echo --once \
      "${ROS_CONTROLLER_OUTPUT_TOPIC}" \
      "mosim_msgs/msg/ControllerOutput" \
      > "${RESULT_DIR}/topic_${controller_output_key}_once.txt" \
      2> "${RESULT_DIR}/topic_${controller_output_key}_once.stderr.txt" &
    controller_output_echo_pid="$!"
  fi

  timeout "${TIMEOUT_SECONDS}" ros2 topic echo --once \
    "${ROS_ACTUATOR_TOPIC}" \
    "${CONTROLLER_ACTUATOR_ROS_TYPE}" \
    > "${RESULT_DIR}/topic_${ros_key}_once.txt" \
    2> "${RESULT_DIR}/topic_${ros_key}_once.stderr.txt" &
  ros_actuator_echo_pid="$!"

  timeout "${TIMEOUT_SECONDS}" ign topic -e \
    -t "${GZ_ACTUATOR_TOPIC}" \
    -n 1 \
    > "${RESULT_DIR}/gz_topic_${gz_key}_once.txt" \
    2> "${RESULT_DIR}/gz_topic_${gz_key}_once.stderr.txt" &
  gz_actuator_echo_pid="$!"

  sleep 1

  if [[ "${RUN_CONTROLLER_OUTPUT_FIXTURE}" == "1" ]]; then
    # shellcheck disable=SC2206
    controller_command_array=(${CONTROLLER_COMMAND_VALUES})
    if timeout "${TIMEOUT_SECONDS}" python3 "${CONTROLLER_FIXTURE_SCRIPT}" \
      --topic "${ROS_CONTROLLER_OUTPUT_TOPIC}" \
      --vehicle-id "sunray150" \
      --command-type "${CONTROLLER_COMMAND_TYPE}" \
      --command "${controller_command_array[@]}" \
      --rate-hz "${CONTROLLER_COMMAND_RATE_HZ}" \
      --times "${CONTROLLER_COMMAND_TIMES}" \
      --output-json "${RESULT_DIR}/controller_output_fixture.json" \
      > "${RESULT_DIR}/controller_output_fixture.stdout.log" \
      2> "${RESULT_DIR}/controller_output_fixture.stderr.log"; then
      write_rc "${RESULT_DIR}/controller_output_fixture.rc" 0
    else
      rc="$?"
      write_rc "${RESULT_DIR}/controller_output_fixture.rc" "${rc}"
    fi
    if [[ "${UNPAUSE_GAZEBO_AFTER_CONTROLLER_COMMAND}" == "1" ]]; then
      unpause_gazebo_world || true
    fi
  elif [[ "${RUN_CONTROLLER_COMMAND}" == "1" ]]; then
    if [[ "${RUN_ACTUATOR_BRIDGE}" != "1" ]]; then
      echo "RUN_CONTROLLER_COMMAND requires RUN_ACTUATOR_BRIDGE=1" > "${RESULT_DIR}/controller_command.stderr.txt"
      write_rc "${RESULT_DIR}/controller_command.rc" 2
    else
      # shellcheck disable=SC2206
      controller_command_array=(${CONTROLLER_COMMAND_VALUES})
      if python3 "${CONTROLLER_ADAPTER_SCRIPT}" \
        --command-type "${CONTROLLER_COMMAND_TYPE}" \
        --command "${controller_command_array[@]}" \
        --ros-topic "${ROS_ACTUATOR_TOPIC}" \
        --gz-topic "${GZ_ACTUATOR_TOPIC}" \
        --output-json "${RESULT_DIR}/controller_actuator_command.json" \
        > "${RESULT_DIR}/controller_adapter_runtime.stdout.log" \
        2> "${RESULT_DIR}/controller_adapter_runtime.stderr.log"; then
        controller_ros_yaml="$(python3 - <<PY
import json
from pathlib import Path
data=json.loads(Path("${RESULT_DIR}/controller_actuator_command.json").read_text(encoding="utf-8"))
print(data["ros_cli_yaml"])
PY
)"
        if timeout "${TIMEOUT_SECONDS}" ros2 topic pub \
          --rate "${CONTROLLER_COMMAND_RATE_HZ}" \
          --times "${CONTROLLER_COMMAND_TIMES}" \
          "${ROS_ACTUATOR_TOPIC}" \
          "${CONTROLLER_ACTUATOR_ROS_TYPE}" \
          "${controller_ros_yaml}" \
          > "${RESULT_DIR}/controller_command.stdout.txt" \
          2> "${RESULT_DIR}/controller_command.stderr.txt"; then
          write_rc "${RESULT_DIR}/controller_command.rc" 0
        else
          rc="$?"
          write_rc "${RESULT_DIR}/controller_command.rc" "${rc}"
        fi
        if [[ "${UNPAUSE_GAZEBO_AFTER_CONTROLLER_COMMAND}" == "1" ]]; then
          unpause_gazebo_world || true
        fi
      else
        rc="$?"
        write_rc "${RESULT_DIR}/controller_command.rc" "${rc}"
      fi
    fi
  fi

  if [[ "${RUN_CONTROLLER_OUTPUT_NODE}" == "1" ]]; then
    if wait "${controller_output_node_pid}"; then
      write_rc "${RESULT_DIR}/controller_output_node.rc" 0
    else
      rc="$?"
      write_rc "${RESULT_DIR}/controller_output_node.rc" "${rc}"
    fi
    controller_output_node_pid=""
  fi

  if [[ -n "${controller_output_echo_pid}" ]]; then
    if wait "${controller_output_echo_pid}"; then
      write_rc "${RESULT_DIR}/topic_${controller_output_key}_once.rc" 0
    else
      rc="$?"
      write_rc "${RESULT_DIR}/topic_${controller_output_key}_once.rc" "${rc}"
    fi
    controller_output_echo_pid=""
  fi

  if wait "${ros_actuator_echo_pid}"; then
    write_rc "${RESULT_DIR}/topic_${ros_key}_once.rc" 0
  else
    rc="$?"
    write_rc "${RESULT_DIR}/topic_${ros_key}_once.rc" "${rc}"
  fi
  if wait "${gz_actuator_echo_pid}"; then
    write_rc "${RESULT_DIR}/gz_topic_${gz_key}_once.rc" 0
  else
    rc="$?"
    write_rc "${RESULT_DIR}/gz_topic_${gz_key}_once.rc" "${rc}"
  fi
  ros2_topic_list_snapshot "${topic_list_file}" 5 1 || true
fi

if [[ "${RUN_PLANT_RESPONSE_EVAL}" == "1" || "${RUNTIME_GATE_PROFILE}" == "single_uav_plant_response_pre_acceptance" || "${RUNTIME_GATE_PROFILE}" == "single_uav_hover_command_bracket" ]]; then
  if [[ -n "${gazebo_truth_pose_recorder_pid}" ]]; then
    if wait "${gazebo_truth_pose_recorder_pid}"; then
      write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" 0
    else
      rc="$?"
      write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" "${rc}"
    fi
    gazebo_truth_pose_recorder_pid=""
  fi
  if python3 "${PLANT_RESPONSE_EVAL_SCRIPT}" \
    --truth-pose-jsonl "${GAZEBO_TRUTH_POSE_JSONL}" \
    --truth-summary-json "${GAZEBO_TRUTH_POSE_SUMMARY_JSON}" \
    --controller-report-json "${RESULT_DIR}/controller_output_adapter_node.json" \
    --fixture-report-json "${RESULT_DIR}/controller_output_fixture.json" \
    --output-json "${GAZEBO_PLANT_RESPONSE_EVAL_JSON}" \
    --min-samples "${PLANT_RESPONSE_MIN_SAMPLES}" \
    --min-duration-s "${PLANT_RESPONSE_MIN_DURATION_S}" \
    --window-fraction "${PLANT_RESPONSE_WINDOW_FRACTION}" \
    --min-window-samples "${PLANT_RESPONSE_MIN_WINDOW_SAMPLES}" \
    --min-z-delta-m "${PLANT_RESPONSE_MIN_Z_DELTA_M}" \
    --min-3d-delta-m "${PLANT_RESPONSE_MIN_3D_DELTA_M}" \
    --max-early-z-range-warning-m "${PLANT_RESPONSE_MAX_EARLY_Z_RANGE_WARNING_M}" \
    --expected-actuator-count "${PLANT_RESPONSE_EXPECTED_ACTUATOR_COUNT}" \
    > "${RESULT_DIR}/gazebo_plant_response_eval.stdout.log" \
    2> "${RESULT_DIR}/gazebo_plant_response_eval.stderr.log"; then
    write_rc "${RESULT_DIR}/gazebo_plant_response_eval.rc" 0
  else
    rc="$?"
    write_rc "${RESULT_DIR}/gazebo_plant_response_eval.rc" "${rc}"
  fi
fi

if [[ "${RUN_COMMAND_ACK_GUARD}" == "1" || "${RUNTIME_GATE_PROFILE}" == "command_acknowledgement_without_closed_loop" ]]; then
  stale_issued_at="$(python3 - <<PY
import time
print(f"{time.time() - float('${COMMAND_ACK_STALE_AGE_S}'):.6f}")
PY
)"
  python3 - <<PY
import json
from pathlib import Path

result_dir = Path("${RESULT_DIR}")
stale_path = result_dir / "stale_controller_output.json"
stale_path.write_text(json.dumps({
    "schema": "mosim.controller_output_fixture.v1",
    "sequence": 9001,
    "vehicle_id": "sunray150",
    "command_type": "${CONTROLLER_COMMAND_TYPE}",
    "command": [float(item) for item in "${CONTROLLER_COMMAND_VALUES}".split()],
    "command_frame": "body_motor_order_rotor_0_1_2_3",
    "mode": "normal",
    "status": "valid",
    "backend": "stale_guard_fixture",
    "source_authority": "bounded_stale_guard_no_flight_authority",
    "issued_at_unix": float("${stale_issued_at}"),
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
  if python3 "${CONTROLLER_ADAPTER_SCRIPT}" \
    --input-json "${RESULT_DIR}/stale_controller_output.json" \
    --expected-vehicle-id "sunray150" \
    --required-status "valid" \
    --max-command-age-s "${COMMAND_ACK_MAX_AGE_S}" \
    --now-unix "$(python3 - <<PY
import time
print(f"{time.time():.6f}")
PY
)" \
    --output-json "${RESULT_DIR}/stale_controller_output_report.json" \
    > "${RESULT_DIR}/stale_controller_output.stdout.log" \
    2> "${RESULT_DIR}/stale_controller_output.stderr.log"; then
    write_rc "${RESULT_DIR}/stale_controller_output.rc" 0
  else
    rc="$?"
    write_rc "${RESULT_DIR}/stale_controller_output.rc" "${rc}"
  fi
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

node = load("controller_output_adapter_node.json")
fixture = load("controller_output_fixture.json")
stale = load("stale_controller_output_report.json")
payload = {
    "schema": "mosim.command_ack_guard.v1",
    "gate_profile": "${RUNTIME_GATE_PROFILE}",
    "controller_output_topic": "${ROS_CONTROLLER_OUTPUT_TOPIC}",
    "actuator_topic": "${ROS_ACTUATOR_TOPIC}",
    "max_command_age_s": float("${COMMAND_ACK_MAX_AGE_S}"),
    "stale_age_s": float("${COMMAND_ACK_STALE_AGE_S}"),
    "positive_path": {
        "fixture_status": fixture.get("status"),
        "node_status": node.get("status"),
        "node_sequence": node.get("input_sequence"),
        "node_vehicle_id": node.get("input_vehicle_id"),
        "node_command_age_s": node.get("command_age_s"),
        "node_velocity": node.get("velocity"),
    },
    "stale_negative_path": {
        "report_status": stale.get("status"),
        "error": stale.get("error", ""),
        "blocked_as_expected": stale.get("status") == "blocked" and "exceeds max_command_age_s" in str(stale.get("error", "")),
        "report": "stale_controller_output_report.json",
    },
    "claim_boundary": [
        "command acknowledgement only covers ControllerOutput receipt, metadata guard, adapter conversion, actuator echo, and stale-command rejection",
        "no planner setpoint, hover, closed_loop, controller performance, or multi-UAV readiness is claimed"
    ],
}
Path("${RESULT_DIR}/command_ack_guard_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
fi

if [[ "${RUN_RATE_CHECK}" == "1" ]]; then
  topics=("${ROS_IMU_TOPIC}" "${ROS_LIDAR_POINTS_TOPIC}")
  if [[ "${RUN_LOCAL_MAP}" == "1" ]]; then
    topics+=("${ROS_LOCAL_VOXEL_TOPIC}")
  fi
  if [[ "${RUN_FASTLIO_PLANNER_INPUT_ADAPTER}" == "1" ]]; then
    topics+=(
      "${ROS_FASTLIO_LIDAR_TOPIC}"
      "${ROS_FASTLIO_IMU_TOPIC}"
      "${ROS_SPARK_FASTLIO_LIVOX_TOPIC}"
      "${ROS_PLANNER_GLOBAL_POINTS_TOPIC}"
      "${ROS_MOSIM_PLANNER_GLOBAL_POINTS_TOPIC}"
      "${ROS_PLANNER_ODOM_TOPIC}"
      "${ROS_MOSIM_PLANNER_ODOM_TOPIC}"
    )
  fi
  if [[ "${RUN_SPARK_FASTLIO}" == "1" ]]; then
    topics+=(
      "${ROS_SPARK_FASTLIO_REGISTERED_CLOUD_TOPIC}"
      "${ROS_SPARK_FASTLIO_ODOMETRY_TOPIC}"
      "${ROS_SPARK_FASTLIO_PATH_TOPIC}"
    )
  fi
  for topic in "${topics[@]}"; do
    key="$(topic_key "${topic}")"
    if timeout --kill-after=5s "${TIMEOUT_SECONDS}" ros2 topic hz "${topic}" > "${RESULT_DIR}/topic_${key}_hz.txt" 2> "${RESULT_DIR}/topic_${key}_hz.stderr.txt"; then
      write_rc "${RESULT_DIR}/topic_${key}_hz.rc" 0
    else
      rc="$?"
      write_rc "${RESULT_DIR}/topic_${key}_hz.rc" "${rc}"
    fi
  done
fi

if [[ "${RUN_HEADER_RATE_CHECK}" == "1" ]]; then
  declare -a header_rate_specs=(
    "imu|${ROS_IMU_TOPIC}|sensor_msgs/msg/Imu"
    "lidar_points|${ROS_LIDAR_POINTS_TOPIC}|sensor_msgs/msg/PointCloud2"
  )
  if [[ "${RUN_LOCAL_MAP}" == "1" ]]; then
    header_rate_specs+=("local_occupancy_voxels|${ROS_LOCAL_VOXEL_TOPIC}|sensor_msgs/msg/PointCloud2")
  fi
  for spec in "${header_rate_specs[@]}"; do
    IFS='|' read -r header_name header_topic header_type <<< "${spec}"
    header_key="$(topic_key "${header_topic}")"
    if timeout --kill-after=5s "${TIMEOUT_SECONDS}" python3 "${TOPIC_HEADER_RATE_SCRIPT}" \
      --topic "${header_topic}" \
      --type "${header_type}" \
      --output-json "${RESULT_DIR}/topic_${header_key}_header_rate.json" \
      --target-samples 40 \
      --timeout-seconds "${TIMEOUT_SECONDS}" \
      > "${RESULT_DIR}/topic_${header_key}_header_rate.stdout.log" \
      2> "${RESULT_DIR}/topic_${header_key}_header_rate.stderr.log"; then
      write_rc "${RESULT_DIR}/topic_${header_key}_header_rate.rc" 0
    else
      rc="$?"
      write_rc "${RESULT_DIR}/topic_${header_key}_header_rate.rc" "${rc}"
    fi
  done
fi

if [[ "${RUN_SPARK_FASTLIO}" == "1" ]]; then
  if timeout "${SPARK_FASTLIO_RECORDER_TIMEOUT_SECONDS}" python3 "${SPARK_FASTLIO_RECORDER_SCRIPT}" \
    --scene-id "sunray150_gazebo_ros2_spark_fastlio_localization" \
    --output-dir "${SPARK_FASTLIO_OUTPUT_DIR}" \
    --duration-seconds "${SPARK_FASTLIO_RECORD_SECONDS}" \
    --odom-topic "${ROS_SPARK_FASTLIO_ODOMETRY_TOPIC}" \
    --path-topic "${ROS_SPARK_FASTLIO_PATH_TOPIC}" \
    --cloud-topic "${ROS_SPARK_FASTLIO_REGISTERED_CLOUD_TOPIC}" \
    > "${RESULT_DIR}/spark_fastlio_recorder.stdout.log" \
    2> "${RESULT_DIR}/spark_fastlio_recorder.stderr.log"; then
    write_rc "${RESULT_DIR}/spark_fastlio_recorder.rc" 0
  else
    rc="$?"
    write_rc "${RESULT_DIR}/spark_fastlio_recorder.rc" "${rc}"
  fi
  if [[ "${RUN_FASTLIO_TRUTH_EVAL}" == "1" ]]; then
    if [[ -n "${gazebo_truth_pose_recorder_pid}" ]]; then
      if wait "${gazebo_truth_pose_recorder_pid}"; then
        write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" 0
      else
        rc="$?"
        write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" "${rc}"
      fi
      gazebo_truth_pose_recorder_pid=""
    fi
    if python3 "${FASTLIO_TRUTH_EVAL_SCRIPT}" \
      --spark-odometry-jsonl "${SPARK_FASTLIO_OUTPUT_DIR}/fastlio_odometry.jsonl" \
      --truth-pose-jsonl "${GAZEBO_TRUTH_POSE_JSONL}" \
      --output-json "${FASTLIO_TRUTH_ERROR_EVAL_JSON}" \
      --source-topic "${GAZEBO_TRUTH_TOPIC}" \
      --truth-source-kind "gazebo_transport_dynamic_pose_info" \
      --max-time-delta-s "${FASTLIO_TRUTH_MAX_TIME_DELTA_S}" \
      --min-matched-samples "${FASTLIO_TRUTH_MIN_MATCHED_SAMPLES}" \
      --time-alignment "${FASTLIO_TRUTH_TIME_ALIGNMENT}" \
      --rmse-warn-m "${FASTLIO_TRUTH_RMSE_WARN_M}" \
      --rmse-block-m "${FASTLIO_TRUTH_RMSE_BLOCK_M}" \
      --p95-block-m "${FASTLIO_TRUTH_P95_BLOCK_M}" \
      > "${RESULT_DIR}/fastlio_truth_error_eval.stdout.log" \
      2> "${RESULT_DIR}/fastlio_truth_error_eval.stderr.log"; then
      write_rc "${RESULT_DIR}/fastlio_truth_error_eval.rc" 0
    else
      rc="$?"
      write_rc "${RESULT_DIR}/fastlio_truth_error_eval.rc" "${rc}"
    fi
  fi
  ros2_topic_list_snapshot "${topic_list_file}" 5 1 || true
fi

if [[ "${RUN_GAZEBO_TRUTH_POSE}" == "1" \
  && "${RUN_PLANT_RESPONSE_EVAL}" != "1" \
  && "${RUN_FASTLIO_TRUTH_EVAL}" != "1" \
  && -n "${gazebo_truth_pose_recorder_pid}" ]]; then
  if wait "${gazebo_truth_pose_recorder_pid}"; then
    write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" 0
  else
    rc="$?"
    write_rc "${RESULT_DIR}/gazebo_truth_pose_recorder.rc" "${rc}"
  fi
  gazebo_truth_pose_recorder_pid=""
fi

if [[ "${RUNTIME_GATE_PROFILE}" == "planner_handoff_without_setpoint_publication" ]]; then
  ros2_topic_list_snapshot "${topic_list_file}" 5 1 || true
  write_forbidden_topic_presence "${topic_list_file}" "${RESULT_DIR}/${PLANNER_HANDOFF_FORBIDDEN_TOPIC_EVIDENCE}"
fi

gazebo_alive="false"
bridge_alive="false"
local_map_alive="false"
fastlio_planner_input_alive="false"
fastlio_imu_passthrough_alive="false"
ego_style_planner_alive="false"
position_command_converter_alive="false"
planner_setpoint_adapter_alive="false"
spark_fastlio_alive="false"
if [[ -n "${gz_pid}" ]] && kill -0 "${gz_pid}" >/dev/null 2>&1; then
  gazebo_alive="true"
fi
if [[ -n "${bridge_pid}" ]] && kill -0 "${bridge_pid}" >/dev/null 2>&1; then
  bridge_alive="true"
fi
if [[ -n "${local_map_pid}" ]] && kill -0 "${local_map_pid}" >/dev/null 2>&1; then
  local_map_alive="true"
fi
if [[ -n "${fastlio_planner_input_pid}" ]] && kill -0 "${fastlio_planner_input_pid}" >/dev/null 2>&1; then
  fastlio_planner_input_alive="true"
fi
if [[ -n "${fastlio_imu_passthrough_pid}" ]] && kill -0 "${fastlio_imu_passthrough_pid}" >/dev/null 2>&1; then
  fastlio_imu_passthrough_alive="true"
fi
if [[ -n "${ego_style_planner_pid}" ]] && kill -0 "${ego_style_planner_pid}" >/dev/null 2>&1; then
  ego_style_planner_alive="true"
fi
if [[ -n "${position_command_converter_pid}" ]] && kill -0 "${position_command_converter_pid}" >/dev/null 2>&1; then
  position_command_converter_alive="true"
fi
if [[ -n "${planner_setpoint_adapter_pid}" ]] && kill -0 "${planner_setpoint_adapter_pid}" >/dev/null 2>&1; then
  planner_setpoint_adapter_alive="true"
fi
if [[ -n "${spark_fastlio_pid}" ]] && kill -0 "${spark_fastlio_pid}" >/dev/null 2>&1; then
  spark_fastlio_alive="true"
fi

runtime_status_rc=0
python3 Scripts/quality/build_gazebo_ros2_runtime_status.py \
  --scenario "${SCENARIO}" \
  --result-dir "${RESULT_DIR}" \
  --output-json "${RUNTIME_STATUS_JSON}" \
  --run-gazebo "${RUN_GAZEBO}" \
  --run-ros2-bridge "${RUN_ROS2_BRIDGE}" \
  --run-local-map "${RUN_LOCAL_MAP}" \
  --run-topic-check "${RUN_TOPIC_CHECK}" \
  --run-rate-check "${RUN_RATE_CHECK}" \
  --run-tf-check "${RUN_TF_CHECK}" \
  --run-fastlio-planner-input-adapter "${RUN_FASTLIO_PLANNER_INPUT_ADAPTER}" \
  --run-ego-style-planner-output "${RUN_EGO_STYLE_PLANNER_OUTPUT}" \
  --run-spark-fastlio "${RUN_SPARK_FASTLIO}" \
  --run-fastlio-truth-eval "${RUN_FASTLIO_TRUTH_EVAL}" \
  --run-gazebo-truth-pose "${RUN_GAZEBO_TRUTH_POSE}" \
  --run-plant-response-eval "${RUN_PLANT_RESPONSE_EVAL}" \
  --run-actuator-command-check "${RUN_ACTUATOR_COMMAND_CHECK}" \
  --run-controller-output-node "${RUN_CONTROLLER_OUTPUT_NODE}" \
  --run-controller-output-fixture "${RUN_CONTROLLER_OUTPUT_FIXTURE}" \
  --run-command-ack-guard "${RUN_COMMAND_ACK_GUARD}" \
  --start-gazebo-paused "${START_GAZEBO_PAUSED}" \
  --unpause-gazebo-after-controller-command "${UNPAUSE_GAZEBO_AFTER_CONTROLLER_COMMAND}" \
  --gate-profile "${RUNTIME_GATE_PROFILE}" \
  --gazebo-alive "${gazebo_alive}" \
  --bridge-alive "${bridge_alive}" \
  --local-map-alive "${local_map_alive}" \
  --fastlio-planner-input-alive "${fastlio_planner_input_alive}" \
  --fastlio-imu-passthrough-alive "${fastlio_imu_passthrough_alive}" \
  --ego-style-planner-alive "${ego_style_planner_alive}" \
  --position-command-converter-alive "${position_command_converter_alive}" \
  --planner-setpoint-adapter-alive "${planner_setpoint_adapter_alive}" \
  --spark-fastlio-alive "${spark_fastlio_alive}" \
  > "${RESULT_DIR}/runtime_status.stdout.log" \
  2> "${RESULT_DIR}/runtime_status.stderr.log" || runtime_status_rc="$?"

if [[ "${runtime_status_rc}" -ne 0 ]]; then
  runtime_status_blockers="$(python3 - <<PY
import json
from pathlib import Path
path = Path("${RUNTIME_STATUS_JSON}")
data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"blockers": ["runtime_status_missing"]}
print(json.dumps(data.get("blockers", []), ensure_ascii=False))
PY
)"
  cat > "${BLOCKER}" <<JSON
{
  "schema": "mosim.gazebo_ros2_blocker.v1",
  "status": "blocked",
  "reason": "runtime_smoke_gate_failed",
  "scenario": "${SCENARIO}",
  "preflight": "${PREFLIGHT_JSON}",
  "topic_contract": "${TOPIC_CONTRACT_JSON}",
  "runtime_status": "${RUNTIME_STATUS_JSON}",
  "blockers": ${runtime_status_blockers},
  "claim_boundary": "Gazebo+ROS2 dependencies may have started, but the required topic/rate/TF/local-map runtime smoke gate did not pass. No PointCloud2, voxel map, planner handoff, or closed-loop success is claimed."
}
JSON
  echo "${BLOCKER}"
  exit 0
fi

rm -f "${BLOCKER}"

FAST_LIO_EVAL_MANIFEST_JSON="$(python3 - <<PY
import json
from pathlib import Path

run_truth_eval = "${RUN_FASTLIO_TRUTH_EVAL}" == "1"
payload = {"status": "not_in_scope"}
if run_truth_eval:
    eval_path = Path("${FASTLIO_TRUTH_ERROR_EVAL_JSON}")
    status = "missing"
    gate_passed = False
    metrics = {}
    warnings = []
    if eval_path.exists():
        try:
            data = json.loads(eval_path.read_text(encoding="utf-8"))
            status = str(data.get("status", "unknown"))
            gate_passed = bool(data.get("gate_passed", False))
            metrics = data.get("metrics", {}) if isinstance(data.get("metrics"), dict) else {}
            warnings = data.get("warnings", []) if isinstance(data.get("warnings"), list) else []
        except Exception as exc:
            status = f"invalid_json:{exc.__class__.__name__}"
    payload = {
        "status": status,
        "gate_passed": gate_passed,
        "truth_error_eval": "${FASTLIO_TRUTH_ERROR_EVAL_JSON}",
        "metrics": metrics,
        "warnings": warnings,
        "claim_boundary": "estimator_vs_gazebo_pose_only_no_planner_no_setpoint_no_closed_loop",
    }
print(json.dumps(payload, ensure_ascii=False))
PY
)"

if [[ "${RUNTIME_GATE_PROFILE}" == "planner_handoff_without_setpoint_publication" ]]; then
  manifest_blockers_json='["setpoint_publication_not_in_scope", "controller_output_not_in_scope", "actuator_command_not_in_scope", "closed_loop_not_in_scope"]'
  planner_handoff_status="planner_input_topics_checked_without_setpoint_publication"
  planner_forbidden_topic_evidence="${RESULT_DIR}/${PLANNER_HANDOFF_FORBIDDEN_TOPIC_EVIDENCE}"
elif [[ "${RUNTIME_GATE_PROFILE}" == "ego_style_planner_output_without_actuation" ]]; then
  manifest_blockers_json='["controller_output_not_in_scope", "actuator_command_not_in_scope", "closed_loop_not_in_scope", "trajectory_tracking_not_claimed"]'
  planner_handoff_status="ego_style_planner_output_checked_without_actuation"
  planner_forbidden_topic_evidence="see_runtime_status"
elif [[ "${RUNTIME_GATE_PROFILE}" == "single_uav_hover_command_bracket" ]]; then
  manifest_blockers_json='["planner_handoff_not_in_scope", "closed_loop_not_in_scope", "controller_performance_not_in_scope", "hover_success_not_claimed"]'
  planner_handoff_status="not_in_scope"
  planner_forbidden_topic_evidence="not_in_scope"
else
  manifest_blockers_json='["planner_handoff_not_in_scope", "closed_loop_not_in_scope"]'
  planner_handoff_status="not_in_scope"
  planner_forbidden_topic_evidence="not_in_scope"
fi

cat > "${RUN_MANIFEST}" <<JSON
{
  "schema_version": "mosim.run_manifest.v1",
  "run_id": "sunray150_gazebo_ros2_${RUNTIME_GATE_PROFILE}",
  "objective": "Gazebo+ROS2 single-UAV ${RUNTIME_GATE_PROFILE} validation gate",
  "scene_id": "${SCENE_ID}",
  "map_id": "${MAP_ID}",
  "vehicle_id": "${VEHICLE_ID}",
  "controller_id": "${CONTROLLER_ID}",
  "planner_id": "local_voxel_map_smoke",
  "quality_status": "${RUNTIME_GATE_PROFILE}_passed",
  "evidence_level": "gazebo_ros2_validation_smoke",
  "claim_scope": ["gazebo_ros2_preflight", "${RUNTIME_GATE_PROFILE}"],
  "blockers": ${manifest_blockers_json},
  "sources": {
    "mworks_source": "MWORKS_MCP",
    "ros2_source": "ROS2_REALSTACK",
    "ue_source": "UE_SENSOR_ORACLE",
    "planner_input_source": "LOCAL_SENSED_MAP",
    "replay_source": "gazebo_plant"
  },
  "mworks": {
    "model_name": "MoSimQuadrotorModel.Dynamics",
    "check_model_status": "pass",
    "simulate_status": "smoke_only",
    "raw_csv": "",
    "metrics_json": ""
  },
  "ros2": {
    "bag_or_summary": "${topic_list_file}",
    "runtime_status": "${RUNTIME_STATUS_JSON}",
    "controller_output_status": "see_runtime_status",
    "actuator_command_status": "see_runtime_status",
    "imu_rate_hz": "see_runtime_status",
    "lidar_rate_hz": "see_runtime_status",
    "tf_status": "see_runtime_status",
    "timestamp_monotonic": "not_evaluated_in_smoke",
    "fast_lio_eval": ${FAST_LIO_EVAL_MANIFEST_JSON}
  },
  "planner": {
    "map_source": "gazebo_sensor_point_cloud_to_local_voxel_adapter",
    "global_truth_used_as_input": false,
    "handoff_status": "${planner_handoff_status}",
    "forbidden_topic_evidence": "${planner_forbidden_topic_evidence}",
    "ego_style_planner_output": "${EGO_STYLE_PLANNER_OUTPUT_JSON}",
    "setpoint_trace_source": "${EGO_STYLE_PLANNER_TRACE_JSONL}",
    "setpoint_adapter_status": "see_runtime_status",
    "setpoint_rate_hz": "see_runtime_status",
    "stale_command_timeout_s": "see_runtime_status"
  },
  "ue": {
    "scene_registry_ref": "Results/unreal_scene_mapping/factoryenvironmentcollect/realstack_miniloop_gate_current.json",
    "sensor_oracle_log": "",
    "command_echo_log": "",
    "no_pose_overwrite_status": "pass"
  },
  "gate_results": {
    "required_checks": ["see_runtime_status_for_profile_specific_checks"],
    "warnings": ["manifest intentionally does not claim planner, closed_loop, or controller performance"],
    "failures": []
  }
}
JSON

echo "${RUN_MANIFEST}"
