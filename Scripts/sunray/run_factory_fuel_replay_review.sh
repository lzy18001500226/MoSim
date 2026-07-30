#!/usr/bin/env bash
# Replay an existing Factory FUEL bag on an isolated ROS master for display review.

source /opt/ros/noetic/setup.bash
set -eo pipefail

PROJECT_ROOT="/mnt/c/Users/HP/Desktop/MoSim"
DEFAULT_RUN_DIR="Results/sunray_ros1/sunray_ros1_p4_factory_fuel_replay_20260730_0945"
RUN_DIR="${DEFAULT_RUN_DIR}"
MASTER_PORT=11320
HOLD_S=8

usage() {
  cat <<'EOF'
Usage: run_factory_fuel_replay_review.sh [options]

Options:
  --run-dir PATH       P4 replay bundle directory, relative to the repository or absolute.
  --master-port PORT   Isolated ROS master port (default: 11320).
  --hold-s SECONDS     Keep RViz open after rosbag playback (default: 8).
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-dir)
      RUN_DIR="$2"
      shift 2
      ;;
    --master-port)
      MASTER_PORT="$2"
      shift 2
      ;;
    --hold-s)
      HOLD_S="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "${RUN_DIR}" != /* ]]; then
  RUN_DIR="${PROJECT_ROOT}/${RUN_DIR}"
fi
RUN_DIR="$(cd "${RUN_DIR}" && pwd)"
ROS_BAG="${RUN_DIR}/factory_fuel_review_clip.bag"
POINTCLOUD_CONFIG="${PROJECT_ROOT}/Config/rviz/sunray_ros1_factory_fuel_pointcloud_review.rviz"
GRID_CONFIG="${PROJECT_ROOT}/Config/rviz/sunray_ros1_factory_fuel_grid3d_review.rviz"
OUTPUT_DIR="${RUN_DIR}/rviz_replay"
STATUS_PATH="${OUTPUT_DIR}/RVIZ_REPLAY_STATUS.json"

for required_path in "${ROS_BAG}" "${POINTCLOUD_CONFIG}" "${GRID_CONFIG}"; do
  if [[ ! -f "${required_path}" ]]; then
    echo "Missing required replay input: ${required_path}" >&2
    exit 2
  fi
done
if ! [[ "${MASTER_PORT}" =~ ^[0-9]+$ ]] || (( MASTER_PORT < 1024 || MASTER_PORT > 65535 )); then
  echo "Invalid --master-port: ${MASTER_PORT}" >&2
  exit 2
fi
if ! [[ "${HOLD_S}" =~ ^[0-9]+$ ]]; then
  echo "Invalid --hold-s: ${HOLD_S}" >&2
  exit 2
fi

mkdir -p "${OUTPUT_DIR}"
export ROS_MASTER_URI="http://127.0.0.1:${MASTER_PORT}"
master_pid=""
pointcloud_pid=""
grid_pid=""
bag_pid=""
cloud_probe_pid=""
occupancy_probe_pid=""
truth_probe_pid=""

write_status() {
  local state="$1"
  local reason="$2"
  local bag_exit="${3:-null}"
  local cloud_exit="${4:-null}"
  local occupancy_exit="${5:-null}"
  local truth_exit="${6:-null}"
  printf '{\n  "schema": "mosim.sunray_p4_rviz_replay_status.v1",\n  "state": "%s",\n  "master_uri": "%s",\n  "rosbag": "%s",\n  "reason": "%s",\n  "bag_exit_code": %s,\n  "pointcloud_probe_exit_code": %s,\n  "occupancy_probe_exit_code": %s,\n  "truth_path_probe_exit_code": %s,\n  "claim_boundary": "Isolated display-only rosbag replay; no Gazebo, PX4, MAVROS, px4ctrl, planner, or command publisher was started by this script."\n}\n' \
    "${state}" "${ROS_MASTER_URI}" "${ROS_BAG}" "${reason}" "${bag_exit}" "${cloud_exit}" "${occupancy_exit}" "${truth_exit}" \
    > "${STATUS_PATH}"
}

cleanup() {
  for pid in "${bag_pid}" "${cloud_probe_pid}" "${occupancy_probe_pid}" "${truth_probe_pid}" "${pointcloud_pid}" "${grid_pid}" "${master_pid}"; do
    if [[ -n "${pid}" ]]; then
      kill -TERM "${pid}" 2>/dev/null || true
    fi
  done
}
trap cleanup EXIT INT TERM

if ss -ltn "sport = :${MASTER_PORT}" | grep -q LISTEN; then
  write_status "blocked" "isolated_master_port_in_use"
  echo "Isolated ROS master port already in use: ${MASTER_PORT}" >&2
  exit 3
fi

write_status "starting" "initializing"
roscore -p "${MASTER_PORT}" > "${OUTPUT_DIR}/roscore.log" 2>&1 &
master_pid=$!
for _ in $(seq 1 20); do
  if rostopic list >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
rostopic list >/dev/null
rosparam set use_sim_time true

rviz -d "${POINTCLOUD_CONFIG}" > "${OUTPUT_DIR}/rviz_pointcloud.log" 2>&1 &
pointcloud_pid=$!
rviz -d "${GRID_CONFIG}" > "${OUTPUT_DIR}/rviz_grid3d.log" 2>&1 &
grid_pid=$!

# These subscribers prove that the isolated master received recorded review data.
timeout 90 rostopic echo -n 1 /mosim/goal4/livox_world_accumulated > "${OUTPUT_DIR}/pointcloud_sample.yaml" 2>&1 &
cloud_probe_pid=$!
timeout 90 rostopic echo -n 1 /mosim/goal4/occupancy_accumulated > "${OUTPUT_DIR}/occupancy_sample.yaml" 2>&1 &
occupancy_probe_pid=$!
timeout 90 rostopic echo -n 1 /mosim/goal4/truth_path > "${OUTPUT_DIR}/truth_path_sample.yaml" 2>&1 &
truth_probe_pid=$!

sleep 8
write_status "playing" "rosbag_replay_started"
rosbag play --clock --delay=0.5 "${ROS_BAG}" > "${OUTPUT_DIR}/rosbag_play.log" 2>&1 &
bag_pid=$!
wait "${bag_pid}" || bag_exit=$?
bag_exit="${bag_exit:-0}"
wait "${cloud_probe_pid}" || cloud_exit=$?
cloud_exit="${cloud_exit:-0}"
wait "${occupancy_probe_pid}" || occupancy_exit=$?
occupancy_exit="${occupancy_exit:-0}"
wait "${truth_probe_pid}" || truth_exit=$?
truth_exit="${truth_exit:-0}"

if (( bag_exit != 0 || cloud_exit != 0 || occupancy_exit != 0 || truth_exit != 0 )); then
  write_status "blocked" "recorded_review_replay_or_topic_probe_failed" "${bag_exit}" "${cloud_exit}" "${occupancy_exit}" "${truth_exit}"
  exit 4
fi

write_status "completed" "recorded_review_topics_received" "${bag_exit}" "${cloud_exit}" "${occupancy_exit}" "${truth_exit}"
sleep "${HOLD_S}"
