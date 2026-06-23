#!/usr/bin/env bash
# Goal5 diagnostic: spawn two Sunray150+MID360 instances in a specified order
# and verify whether each Gazebo Livox plugin publishes a real PointCloud2.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/opt/mosim_work/sunray_ws/Sunray}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-/opt/mosim_work/sunray_px4}"
LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS:-/opt/mosim_work/sunray_livox_plugin_ws}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/goal5_probe_two_uav_livox_order_$(date +%Y%m%d_%H%M%S)}"
WORLD_FILE="${WORLD_FILE:-${SUNRAY_WS}/simulation/sunray_simulator/worlds/planning_test.world}"
SUNRAY_MID360_PLUGIN_DOWNSAMPLE="${SUNRAY_MID360_PLUGIN_DOWNSAMPLE:-4}"
SUNRAY_LIVOX_PLUGIN_FILENAME="${SUNRAY_LIVOX_PLUGIN_FILENAME:-${LIVOX_PLUGIN_WS}/devel/lib/liblivox_laser_simulation.so}"
SUNRAY_MID360_CSV_FILE_NAME="${SUNRAY_MID360_CSV_FILE_NAME:-mid360-real-centr.csv}"
SPAWN_ORDER="${SPAWN_ORDER:-2 1}"
FIRST_TIMEOUT_S="${FIRST_TIMEOUT_S:-70}"
SECOND_TIMEOUT_S="${SECOND_TIMEOUT_S:-90}"
SUNRAY_STRIP_PX4_MODEL_PATH="${SUNRAY_STRIP_PX4_MODEL_PATH:-true}"

mkdir -p "${RESULT_DIR}"

PIDS=()
cleanup() {
  set +e
  if [[ "${KEEP_ALIVE:-false}" == "true" ]]; then
    return
  fi
  for pid in "${PIDS[@]:-}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
  sleep 2
  for pid in "${PIDS[@]:-}"; do
    kill -9 "${pid}" >/dev/null 2>&1 || true
  done
  pkill -f "roslaunch .*sunray_px4_basic" >/dev/null 2>&1 || true
  pkill -f "roslaunch .*empty_world" >/dev/null 2>&1 || true
  pkill -f "gzserver" >/dev/null 2>&1 || true
  pkill -f "gzclient" >/dev/null 2>&1 || true
  pkill -f "mavros_node" >/dev/null 2>&1 || true
  pkill -f "/opt/mosim_work/sunray_px4.*/px4" >/dev/null 2>&1 || true
  pkill -f "rosmaster" >/dev/null 2>&1 || true
  pkill -f "rosout" >/dev/null 2>&1 || true
}
trap cleanup EXIT

source /usr/share/gazebo/setup.sh
source /opt/ros/noetic/setup.bash
source "${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/setup_gazebo.bash" \
  "${SUNRAY_PX4_DIR}" \
  "${SUNRAY_PX4_DIR}/build/px4_sitl_default"
source "${SUNRAY_WS}/devel/setup.bash"
source "${LIVOX_PLUGIN_WS}/devel/setup.bash"

strip_colon_path_entry() {
  local value="$1"
  local remove="$2"
  python3 - "$value" "$remove" <<'PY'
import sys
value, remove = sys.argv[1], sys.argv[2]
print(":".join(part for part in value.split(":") if part and part != remove))
PY
}

if [[ "${SUNRAY_STRIP_PX4_MODEL_PATH}" == "true" ]]; then
  PX4_GAZEBO_MODEL_PATH="${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/sitl_gazebo-classic/models"
  GAZEBO_MODEL_PATH="$(strip_colon_path_entry "${GAZEBO_MODEL_PATH:-}" "${PX4_GAZEBO_MODEL_PATH}")"
fi

export GAZEBO_MODEL_PATH="${SUNRAY_WS}/simulation/sunray_simulator/models/scence_models:${SUNRAY_WS}/simulation/sunray_simulator/models/drone_models:${SUNRAY_WS}/simulation/sunray_simulator/models/sensor_models:${SUNRAY_WS}/simulation/sunray_simulator/models/fake_models:${GAZEBO_MODEL_PATH:-}"
export GAZEBO_PLUGIN_PATH="${LIVOX_PLUGIN_WS}/devel/lib:${SUNRAY_WS}/devel/lib:${GAZEBO_PLUGIN_PATH:-}"
export LD_LIBRARY_PATH="${LIVOX_PLUGIN_WS}/devel/lib:${SUNRAY_WS}/devel/lib:/opt/ros/noetic/lib:${LD_LIBRARY_PATH:-}"
export ROS_PACKAGE_PATH="${SUNRAY_PX4_DIR}:${SUNRAY_WS}:/opt/ros/noetic/share:${ROS_PACKAGE_PATH:-}"
export SUNRAY_MID360_PLUGIN_DOWNSAMPLE
export SUNRAY_LIVOX_PLUGIN_FILENAME
export SUNRAY_MID360_CSV_FILE_NAME

{
  echo "SUNRAY_STRIP_PX4_MODEL_PATH=${SUNRAY_STRIP_PX4_MODEL_PATH}"
  echo "SUNRAY_PX4_DIR=${SUNRAY_PX4_DIR}"
  echo "PX4_GAZEBO_MODEL_PATH=${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/sitl_gazebo-classic/models"
  echo "GAZEBO_MODEL_PATH=${GAZEBO_MODEL_PATH:-}"
  echo "GAZEBO_PLUGIN_PATH=${GAZEBO_PLUGIN_PATH:-}"
  echo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH:-}"
  echo "ROS_PACKAGE_PATH=${ROS_PACKAGE_PATH:-}"
  if [[ "${GAZEBO_MODEL_PATH:-}" == *"${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/sitl_gazebo-classic/models"* ]]; then
    echo "PX4_MODEL_PATH_PRESENT=true"
  else
    echo "PX4_MODEL_PATH_PRESENT=false"
  fi
} > "${RESULT_DIR}/env.txt"

python3 "${PROJECT_ROOT}/Scripts/sunray/sync_assembled_model_into_sunray_ros1.py" \
  --project-root "${PROJECT_ROOT}" \
  --sunray-ws "${SUNRAY_WS}" \
  --manifest "${RESULT_DIR}/sync.json" \
  > "${RESULT_DIR}/sync.log" 2>&1

roslaunch gazebo_ros empty_world.launch \
  gui:=false world_name:="${WORLD_FILE}" use_sim_time:=true \
  > "${RESULT_DIR}/world.log" 2>&1 &
PIDS+=("$!")
sleep 8

wait_topic_sample() {
  local topic="$1"
  local output="$2"
  local timeout_s="$3"
  local deadline=$((SECONDS + timeout_s))
  while (( SECONDS < deadline )); do
    if timeout 2s rostopic echo -n 1 "${topic}" > "${output}" 2>/dev/null; then
      return 0
    fi
    sleep 1
  done
  return 1
}

spawn_uav() {
  local uid="$1"
  local y="$2"
  roslaunch sunray_simulator sunray_px4_basic.launch \
    uav_id:="${uid}" vehicle:=sunray150_with_mid360 \
    uav_init_x:=0 uav_init_y:="${y}" uav_init_z:=0.2 \
    > "${RESULT_DIR}/uav${uid}.log" 2>&1 &
  PIDS+=("$!")
  echo "${PIDS[-1]}" > "${RESULT_DIR}/uav${uid}.pid"
}

spawned=()
status=0
index=0
for uid in ${SPAWN_ORDER}; do
  index=$((index + 1))
  if [[ "${uid}" == "1" ]]; then
    spawn_uav 1 -1
  elif [[ "${uid}" == "2" ]]; then
    spawn_uav 2 1
  else
    echo "Unsupported uid in SPAWN_ORDER: ${uid}" >&2
    exit 2
  fi
  spawned+=("${uid}")
  timeout_s="${SECOND_TIMEOUT_S}"
  if [[ "${index}" == "1" ]]; then
    timeout_s="${FIRST_TIMEOUT_S}"
  fi
  if wait_topic_sample "/uav${uid}/livox/lidar" "${RESULT_DIR}/uav${uid}_lidar_after_spawn_${index}.txt" "${timeout_s}"; then
    echo "uav${uid}:lidar_pass_after_spawn_${index}" | tee -a "${RESULT_DIR}/summary.txt"
  else
    echo "uav${uid}:lidar_fail_after_spawn_${index}" | tee -a "${RESULT_DIR}/summary.txt"
    status=7
  fi
done

{
  echo "SPAWN_ORDER=${SPAWN_ORDER}"
  echo "RESULT_DIR=${RESULT_DIR}"
  echo "rostopic_list_livox:"
  rostopic list | grep -E '/uav[12]/livox' || true
} >> "${RESULT_DIR}/summary.txt" 2>&1

exit "${status}"
