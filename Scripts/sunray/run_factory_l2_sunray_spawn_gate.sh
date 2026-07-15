#!/usr/bin/env bash
# Bounded Factory L2 -> Sunray ROS1/Gazebo spawn and sensor gate.

set -uo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/opt/mosim_work/sunray_ws/Sunray}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-/opt/mosim_work/sunray_px4}"
LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/sunray_livox_plugin_ws}"
RUN_ID="${RUN_ID:-factory_l2_sunray_spawn_gate_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
WORLD_FILE="${WORLD_FILE:-${PROJECT_ROOT}/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/worlds/factoryenvironmentcollect_l2_static_review.sdf}"
FACTORY_MODEL_PATH="${FACTORY_MODEL_PATH:-${PROJECT_ROOT}/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/models}"
UAV_NUM="${UAV_NUM:-1}"
GUI="${GUI:-false}"
VERBOSE="${VERBOSE:-true}"
TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-90}"
MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-60}"
LIDAR_READY_TIMEOUT_S="${LIDAR_READY_TIMEOUT_S:-60}"
CLEAN_START="${CLEAN_START:-true}"
LAUNCH_FILE="${LAUNCH_FILE:-${PROJECT_ROOT}/Scripts/sunray/factory_l2_sunray_px4_gazebo.launch}"
SUNRAY_STRIP_PX4_MODEL_PATH="${SUNRAY_STRIP_PX4_MODEL_PATH:-true}"
SUNRAY_MID360_PLUGIN_DOWNSAMPLE="${SUNRAY_MID360_PLUGIN_DOWNSAMPLE:-4}"
SUNRAY_LIVOX_PLUGIN_FILENAME="${SUNRAY_LIVOX_PLUGIN_FILENAME:-${LIVOX_PLUGIN_WS}/devel/lib/liblivox_laser_simulation.so}"
SUNRAY_MID360_CSV_FILE_NAME="${SUNRAY_MID360_CSV_FILE_NAME:-mid360-real-centr.csv}"
SUNRAY_MID360_GOAL5_CSV_STRIDE="${SUNRAY_MID360_GOAL5_CSV_STRIDE:-4}"
SUNRAY_GAZEBO_MAX_STEP_SIZE_S="${SUNRAY_GAZEBO_MAX_STEP_SIZE_S:-0.001}"
SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ="${SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ:-1000}"

mkdir -p "${RESULT_DIR}"

PIDS=()

cleanup() {
  set +e
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
  pkill -f "[r]oslaunch .*factory_l2_sunray_px4_gazebo.launch" >/dev/null 2>&1 || true
}
trap cleanup EXIT

source_env() {
  export PATH=/opt/ros/noetic/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib
  set +u
  # shellcheck disable=SC1091
  source /usr/share/gazebo/setup.sh
  # shellcheck disable=SC1091
  source /opt/ros/noetic/setup.bash
  # shellcheck disable=SC1091
  source "${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/setup_gazebo.bash" \
    "${SUNRAY_PX4_DIR}" \
    "${SUNRAY_PX4_DIR}/build/px4_sitl_default"
  # shellcheck disable=SC1091
  source "${SUNRAY_WS}/devel/setup.bash"
  if [[ -f "${LIVOX_PLUGIN_WS}/devel/setup.bash" ]]; then
    # shellcheck disable=SC1091
    source "${LIVOX_PLUGIN_WS}/devel/setup.bash"
  fi
  set -u

  local sunray_models="${SUNRAY_WS}/simulation/sunray_simulator/models"
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
  export ROS_PACKAGE_PATH="${SUNRAY_PX4_DIR}:${SUNRAY_WS}:/opt/ros/noetic/share:${ROS_PACKAGE_PATH:-}"
  export GAZEBO_MODEL_PATH="${FACTORY_MODEL_PATH}:${PROJECT_ROOT}/Config/gazebo/models:${sunray_models}/scence_models:${sunray_models}/drone_models:${sunray_models}/sensor_models:${sunray_models}/fake_models:${sunray_models}/ugv_models:${sunray_models}/aws_models:${sunray_models}/aws_vins_models:${GAZEBO_MODEL_PATH:-}"
  export GAZEBO_RESOURCE_PATH="${SUNRAY_WS}/simulation/sunray_simulator:${GAZEBO_RESOURCE_PATH:-}"
  export GAZEBO_PLUGIN_PATH="${LIVOX_PLUGIN_WS}/devel/lib:${SUNRAY_WS}/devel/lib:${GAZEBO_PLUGIN_PATH:-}"
  export LD_LIBRARY_PATH="${LIVOX_PLUGIN_WS}/devel/lib:${SUNRAY_WS}/devel/lib:/opt/ros/noetic/lib:${LD_LIBRARY_PATH:-}"
}

write_summary() {
  local status="$1"
  local classification="$2"
  local message="$3"
  python3 - "${RESULT_DIR}" "${status}" "${classification}" "${message}" <<'PY'
import json
import pathlib
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
status, classification, message = sys.argv[2:5]

def exists(name):
    return (result_dir / name).exists()

payload = {
    "schema": "mosim.factory_l2_sunray_spawn_gate.v1",
    "status": status,
    "classification": classification,
    "message": message,
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "result_dir": str(result_dir),
    "artifacts": {
        "env": exists("env.txt"),
        "roslaunch_log": exists("roslaunch_factory.log"),
        "mavros_connected_sample": exists("mavros_state_connected.txt"),
        "lidar_ready_sample": exists("livox_lidar_ready_sample.txt"),
        "model_states": exists("model_states_last.txt"),
        "topic_list": exists("topics_last.txt"),
    },
}
(result_dir / "FACTORY_SUNRAY_SPAWN_GATE.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
(result_dir / "SESSION.json").write_text(
    json.dumps(
        {
            "schema": "mosim.factory_l2_sunray_spawn_session.v1",
            "status": status,
            "classification": classification,
            "result_dir": str(result_dir),
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
PY
}

fail_gate() {
  local classification="$1"
  local message="$2"
  write_summary "failed" "${classification}" "${message}"
  echo "FACTORY_SUNRAY_SPAWN_GATE=FAILED ${classification}: ${message}" >&2
  exit 1
}

if [[ ! -d "${PROJECT_ROOT}" ]]; then
  fail_gate "preflight_blocker" "PROJECT_ROOT missing: ${PROJECT_ROOT}"
fi
if [[ ! -d "${SUNRAY_WS}" ]]; then
  fail_gate "preflight_blocker" "SUNRAY_WS missing: ${SUNRAY_WS}"
fi
if [[ ! -d "${SUNRAY_PX4_DIR}" ]]; then
  fail_gate "preflight_blocker" "SUNRAY_PX4_DIR missing: ${SUNRAY_PX4_DIR}"
fi
if [[ "${SUNRAY_LIVOX_PLUGIN_FILENAME}" == */* && ! -f "${SUNRAY_LIVOX_PLUGIN_FILENAME}" ]]; then
  fail_gate "plugin_overlay_blocker" "Livox plugin overlay missing: ${SUNRAY_LIVOX_PLUGIN_FILENAME}; run check_sunray_ros1_runtime_preflight.sh --build-livox first"
fi
if [[ ! -f "${WORLD_FILE}" ]]; then
  fail_gate "static_scene_blocker" "Factory world missing: ${WORLD_FILE}"
fi
if [[ ! -d "${FACTORY_MODEL_PATH}" ]]; then
  fail_gate "static_scene_blocker" "Factory model path missing: ${FACTORY_MODEL_PATH}"
fi

source_env

{
  echo "PROJECT_ROOT=${PROJECT_ROOT}"
  echo "SUNRAY_WS=${SUNRAY_WS}"
  echo "SUNRAY_PX4_DIR=${SUNRAY_PX4_DIR}"
  echo "LIVOX_PLUGIN_WS=${LIVOX_PLUGIN_WS}"
  echo "WORLD_FILE=${WORLD_FILE}"
  echo "FACTORY_MODEL_PATH=${FACTORY_MODEL_PATH}"
  echo "LAUNCH_FILE=${LAUNCH_FILE}"
  echo "SUNRAY_STRIP_PX4_MODEL_PATH=${SUNRAY_STRIP_PX4_MODEL_PATH}"
  echo "SUNRAY_MID360_PLUGIN_DOWNSAMPLE=${SUNRAY_MID360_PLUGIN_DOWNSAMPLE}"
  echo "SUNRAY_LIVOX_PLUGIN_FILENAME=${SUNRAY_LIVOX_PLUGIN_FILENAME}"
  echo "SUNRAY_MID360_CSV_FILE_NAME=${SUNRAY_MID360_CSV_FILE_NAME}"
  echo "SUNRAY_MID360_GOAL5_CSV_STRIDE=${SUNRAY_MID360_GOAL5_CSV_STRIDE}"
  echo "ROS_PACKAGE_PATH=${ROS_PACKAGE_PATH}"
  echo "GAZEBO_MODEL_PATH=${GAZEBO_MODEL_PATH}"
  echo "GAZEBO_RESOURCE_PATH=${GAZEBO_RESOURCE_PATH}"
  echo "GAZEBO_PLUGIN_PATH=${GAZEBO_PLUGIN_PATH}"
  echo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH}"
} > "${RESULT_DIR}/env.txt"

if [[ "${CLEAN_START}" == "true" ]]; then
  pkill -f "[r]oslaunch .*factory_l2_sunray_px4_gazebo.launch" >/dev/null 2>&1 || true
  pkill -f "[r]oslaunch .*sunray_sim_uav" >/dev/null 2>&1 || true
  pkill -x gzserver >/dev/null 2>&1 || true
  pkill -x gzclient >/dev/null 2>&1 || true
  pkill -x mavros_node >/dev/null 2>&1 || true
  pkill -x rosmaster >/dev/null 2>&1 || true
  pkill -x rosout >/dev/null 2>&1 || true
  sleep 2
fi

export SUNRAY_MID360_PLUGIN_DOWNSAMPLE
export SUNRAY_LIVOX_PLUGIN_FILENAME
export SUNRAY_MID360_CSV_FILE_NAME
export SUNRAY_GAZEBO_MAX_STEP_SIZE_S
export SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ

python3 "${PROJECT_ROOT}/Scripts/sunray/sync_assembled_model_into_sunray_ros1.py" \
  --project-root "${PROJECT_ROOT}" \
  --sunray-ws "${SUNRAY_WS}" \
  --manifest "${RESULT_DIR}/assembled_model_sync.json" \
  > "${RESULT_DIR}/assembled_model_sync.log" 2>&1 || \
  fail_gate "model_sync_blocker" "assembled Sunray model sync failed"

rm -f /tmp/px4-sock-0 /tmp/px4-sock-1 2>/dev/null || true

roslaunch "${LAUNCH_FILE}" \
  uav_num:="${UAV_NUM}" gui:="${GUI}" verbose:="${VERBOSE}" \
  world:="${WORLD_FILE}" factory_model_path:="${FACTORY_MODEL_PATH}" \
  > "${RESULT_DIR}/roslaunch_factory.log" 2>&1 &
PIDS+=("$!")
echo "${PIDS[-1]}" > "${RESULT_DIR}/roslaunch.pid"

deadline=$((SECONDS + TOTAL_TIMEOUT_S))
mavros_deadline=$((SECONDS + MAVROS_READY_TIMEOUT_S))
lidar_deadline=0
mavros_connected=false
lidar_ready=false
last_topics="${RESULT_DIR}/topics_last.txt"

while (( SECONDS < deadline )); do
  if ! kill -0 "${PIDS[0]}" >/dev/null 2>&1; then
    cp "${RESULT_DIR}/roslaunch_factory.log" "${RESULT_DIR}/roslaunch_factory_exited.log" 2>/dev/null || true
    fail_gate "runtime_startup_blocker" "Factory Sunray roslaunch exited before gate passed"
  fi

  rostopic list > "${last_topics}" 2>&1 || true

  if [[ "${mavros_connected}" == "false" ]]; then
    timeout 3s rostopic echo -n 1 /uav1/mavros/state > "${RESULT_DIR}/mavros_state_latest.txt" 2>/dev/null || true
    if grep -q "connected: True" "${RESULT_DIR}/mavros_state_latest.txt" 2>/dev/null; then
      cp "${RESULT_DIR}/mavros_state_latest.txt" "${RESULT_DIR}/mavros_state_connected.txt"
      mavros_connected=true
      lidar_deadline=$((SECONDS + LIDAR_READY_TIMEOUT_S))
    elif (( SECONDS > mavros_deadline )); then
      timeout 4s rostopic echo -n 1 /gazebo/model_states > "${RESULT_DIR}/model_states_last.txt" 2>&1 || true
      if grep -q " uav1" "${RESULT_DIR}/model_states_last.txt" 2>/dev/null || grep -q -- "- uav1" "${RESULT_DIR}/model_states_last.txt" 2>/dev/null; then
        fail_gate "gazebo_model_spawn_sensor_init_blocker" "MAVROS did not connect; uav1 appeared in Gazebo model states, so inspect spawn service return and MID360 sensor/plugin initialization first"
      fi
      fail_gate "mavros_connection_blocker" "MAVROS did not connect before timeout"
    fi
  fi

  if [[ "${mavros_connected}" == "true" && "${lidar_ready}" == "false" ]]; then
    timeout 5s rostopic echo -n 1 /uav1/livox/lidar > "${RESULT_DIR}/livox_lidar_latest.txt" 2>/dev/null || true
    if grep -q "width:" "${RESULT_DIR}/livox_lidar_latest.txt" 2>/dev/null && grep -q "data:" "${RESULT_DIR}/livox_lidar_latest.txt" 2>/dev/null; then
      cp "${RESULT_DIR}/livox_lidar_latest.txt" "${RESULT_DIR}/livox_lidar_ready_sample.txt"
      lidar_ready=true
      break
    elif (( SECONDS > lidar_deadline )); then
      timeout 4s rostopic echo -n 1 /gazebo/model_states > "${RESULT_DIR}/model_states_last.txt" 2>&1 || true
      fail_gate "mid360_sensor_blocker" "MID360 lidar topic did not publish a nonempty sample before timeout"
    fi
  fi

  sleep 1
done

timeout 4s rostopic echo -n 1 /gazebo/model_states > "${RESULT_DIR}/model_states_last.txt" 2>&1 || true

if [[ "${mavros_connected}" == "true" && "${lidar_ready}" == "true" ]]; then
  write_summary "passed" "spawn_sensor_pass" "Selected world supports one Sunray150+MID360 spawn, MAVROS connection, and MID360 lidar sample."
  cat "${RESULT_DIR}/FACTORY_SUNRAY_SPAWN_GATE.json"
  exit 0
fi

fail_gate "timeout_blocker" "Factory Sunray spawn gate timed out without required evidence"
