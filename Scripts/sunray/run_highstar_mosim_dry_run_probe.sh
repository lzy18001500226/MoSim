#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
HIGHSTAR_WS="${HIGHSTAR_WS:-${PROJECT_ROOT}/Results/build/highstar_overlay_ws_20260708_try1}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/highstar_mosim_dry_run_probe_current}"
CLOUD_TOPIC="${CLOUD_TOPIC:-/uav1/livox/lidar}"
ODOM_TOPIC="${ODOM_TOPIC:-/uav1/mavros/local_position/odom}"
DEPTH_TOPIC="${DEPTH_TOPIC:-/mosim/highstar/depth}"
CAMERA_INFO_TOPIC="${CAMERA_INFO_TOPIC:-/mosim/highstar/camera_info}"
TRAJ_TOPIC="${TRAJ_TOPIC:-/Murder/Traj}"
ADAPTER_TIMEOUT_S="${ADAPTER_TIMEOUT_S:-20}"
TRAJ_TIMEOUT_S="${TRAJ_TIMEOUT_S:-45}"
ADAPTER_WIDTH="${ADAPTER_WIDTH:-320}"
ADAPTER_HEIGHT="${ADAPTER_HEIGHT:-180}"
ADAPTER_POINT_STRIDE="${ADAPTER_POINT_STRIDE:-2}"
HIGHSTAR_MAP_MIN_X="${HIGHSTAR_MAP_MIN_X:--35.0}"
HIGHSTAR_MAP_MIN_Y="${HIGHSTAR_MAP_MIN_Y:--45.0}"
HIGHSTAR_MAP_MIN_Z="${HIGHSTAR_MAP_MIN_Z:--0.1}"
HIGHSTAR_MAP_MAX_X="${HIGHSTAR_MAP_MAX_X:-25.0}"
HIGHSTAR_MAP_MAX_Y="${HIGHSTAR_MAP_MAX_Y:-15.0}"
HIGHSTAR_MAP_MAX_Z="${HIGHSTAR_MAP_MAX_Z:-8.0}"
HIGHSTAR_TRIGGER_REPEAT_S="${HIGHSTAR_TRIGGER_REPEAT_S:-8}"
HIGHSTAR_SHOW_FRONTIER="${HIGHSTAR_SHOW_FRONTIER:-false}"

mkdir -p "${RESULT_DIR}"

set +u
source /opt/ros/noetic/setup.bash
source "${HIGHSTAR_WS}/devel/setup.bash"
set -u

cleanup() {
  if [[ -n "${ADAPTER_PID:-}" ]]; then
    kill "${ADAPTER_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${LAUNCH_PID:-}" ]]; then
    kill "${LAUNCH_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

python3 "${PROJECT_ROOT}/Scripts/sunray/highstar_pointcloud_depth_adapter.py" \
  _cloud_topic:="${CLOUD_TOPIC}" \
  _depth_topic:="${DEPTH_TOPIC}" \
  _camera_info_topic:="${CAMERA_INFO_TOPIC}" \
  _max_range_m:=8.0 \
  _width:="${ADAPTER_WIDTH}" \
  _height:="${ADAPTER_HEIGHT}" \
  _point_stride:="${ADAPTER_POINT_STRIDE}" \
  > "${RESULT_DIR}/highstar_pointcloud_depth_adapter.log" 2>&1 &
ADAPTER_PID=$!

timeout "${ADAPTER_TIMEOUT_S}" rostopic echo -n 1 "${DEPTH_TOPIC}" \
  > "${RESULT_DIR}/depth_first.txt" 2>&1
timeout "${ADAPTER_TIMEOUT_S}" rostopic echo -n 1 "${CAMERA_INFO_TOPIC}" \
  > "${RESULT_DIR}/camera_info_first.txt" 2>&1

timeout "${ADAPTER_TIMEOUT_S}" rostopic echo -n 1 "${ODOM_TOPIC}" \
  > "${RESULT_DIR}/odom_first.txt" 2>&1

read -r CURRENT_X CURRENT_Y CURRENT_Z < <(
  python3 - "${ODOM_TOPIC}" <<'PY'
import sys

import rospy
from nav_msgs.msg import Odometry

topic = sys.argv[1]
rospy.init_node("highstar_probe_read_odom", anonymous=True, disable_signals=True)
msg = rospy.wait_for_message(topic, Odometry, timeout=10.0)
p = msg.pose.pose.position
print(f"{p.x:.6f} {p.y:.6f} {p.z:.6f}")
PY
)

HIGHSTAR_TAKEOFF_X="${HIGHSTAR_TAKEOFF_X:-${CURRENT_X}}"
HIGHSTAR_TAKEOFF_Y="${HIGHSTAR_TAKEOFF_Y:-${CURRENT_Y}}"
HIGHSTAR_TAKEOFF_Z="${HIGHSTAR_TAKEOFF_Z:-${CURRENT_Z}}"

roslaunch "${PROJECT_ROOT}/Scripts/sunray/highstar_mosim_dry_run.launch" \
  depth_topic:="${DEPTH_TOPIC}" \
  camera_info_topic:="${CAMERA_INFO_TOPIC}" \
  odom_topic:="${ODOM_TOPIC}" \
  map_min_x:="${HIGHSTAR_MAP_MIN_X}" \
  map_min_y:="${HIGHSTAR_MAP_MIN_Y}" \
  map_min_z:="${HIGHSTAR_MAP_MIN_Z}" \
  map_max_x:="${HIGHSTAR_MAP_MAX_X}" \
  map_max_y:="${HIGHSTAR_MAP_MAX_Y}" \
  map_max_z:="${HIGHSTAR_MAP_MAX_Z}" \
  show_frontier:="${HIGHSTAR_SHOW_FRONTIER}" \
  takeoff_x:="${HIGHSTAR_TAKEOFF_X}" \
  takeoff_y:="${HIGHSTAR_TAKEOFF_Y}" \
  takeoff_z:="${HIGHSTAR_TAKEOFF_Z}" \
  > "${RESULT_DIR}/highstar_mosim_dry_run_roslaunch.log" 2>&1 &
LAUNCH_PID=$!

for _ in $(seq 1 40); do
  if rosnode ping -c 1 /murder_demo >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done
rosnode info /murder_demo > "${RESULT_DIR}/murder_node_info_before_trigger.txt" 2>&1 || true
rostopic info /start_trigger > "${RESULT_DIR}/start_trigger_info_before_pub.txt" 2>&1 || true
timeout "${HIGHSTAR_TRIGGER_REPEAT_S}" python3 - <<'PY' \
  > "${RESULT_DIR}/start_trigger_pub.txt" 2>&1 || true
import time

import rospy
from std_msgs.msg import Empty

rospy.init_node("highstar_probe_start_trigger", anonymous=True, disable_signals=True)
pub = rospy.Publisher("/start_trigger", Empty, queue_size=1)
deadline = time.time() + 5.0
while pub.get_num_connections() == 0 and time.time() < deadline:
    time.sleep(0.1)
print(f"connections_before_publish={pub.get_num_connections()}", flush=True)
for _ in range(20):
    pub.publish(Empty())
    time.sleep(0.1)
print(f"connections_after_publish={pub.get_num_connections()}", flush=True)
PY
rosnode info /murder_demo > "${RESULT_DIR}/murder_node_info_after_trigger.txt" 2>&1 || true
timeout 10 rostopic echo -n 1 /Murder/Show \
  > "${RESULT_DIR}/murder_show_first.txt" 2>&1 || true
timeout 10 rostopic echo -n 1 /murder_demo/block_map/voxvis \
  > "${RESULT_DIR}/block_map_voxvis_first.txt" 2>&1 || true
timeout 10 rostopic echo -n 1 /murder_demo/LowResMap/Nodes \
  > "${RESULT_DIR}/lowres_map_nodes_first.txt" 2>&1 || true
timeout 10 rostopic echo -n 1 /Frontier/grid \
  > "${RESULT_DIR}/frontier_grid_first.txt" 2>&1 || true
timeout 10 rostopic echo -n 1 /murder_demo/block_map/stat_v \
  > "${RESULT_DIR}/block_map_stat_first.txt" 2>&1 || true

set +e
timeout "${TRAJ_TIMEOUT_S}" rostopic echo -n 1 "${TRAJ_TOPIC}" \
  > "${RESULT_DIR}/murder_traj_first.txt" 2>&1
traj_rc=$?
set -e

python3 - "$RESULT_DIR" "$traj_rc" <<'PY'
import json
import pathlib
import sys

result_dir = pathlib.Path(sys.argv[1])
traj_rc = int(sys.argv[2])
summary = {
    "status": "passed_nonempty_swarmtraj" if traj_rc == 0 else "blocked_no_swarmtraj",
    "traj_topic": "/Murder/Traj",
    "traj_echo_exit_code": traj_rc,
    "claim_boundary": (
        "HighStar dry-run only: no RotorS, no traj_exc_node, no direct MAVROS "
        "setpoint authority, and no full Factory coverage claim."
    ),
}
(result_dir / "HIGHSTAR_MOSIM_DRY_RUN_PROBE.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print(json.dumps(summary, indent=2, ensure_ascii=False))
PY

exit "${traj_rc}"
