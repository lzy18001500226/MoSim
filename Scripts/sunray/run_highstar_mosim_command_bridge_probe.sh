#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
HIGHSTAR_WS="${HIGHSTAR_WS:-${PROJECT_ROOT}/Results/build/highstar_overlay_ws_20260708_try1}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
PLANNER_CONTROL_COMPAT_WS="${PLANNER_CONTROL_COMPAT_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/goal4_diff_planner_ws_px4msg}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/highstar_mosim_command_bridge_probe_current}"
CLOUD_TOPIC="${CLOUD_TOPIC:-/uav1/livox/lidar}"
ODOM_TOPIC="${ODOM_TOPIC:-/uav1/mavros/local_position/odom}"
DEPTH_TOPIC="${DEPTH_TOPIC:-/mosim/highstar/depth}"
CAMERA_INFO_TOPIC="${CAMERA_INFO_TOPIC:-/mosim/highstar/camera_info}"
TRAJ_TOPIC="${TRAJ_TOPIC:-/Murder/Traj}"
RAW_CMD_TOPIC="${RAW_CMD_TOPIC:-/highstar/position_cmd_raw}"
SAFE_CMD_TOPIC="${SAFE_CMD_TOPIC:-/highstar/position_cmd_safe_probe}"
SAFE_ENABLE_TOPIC="${SAFE_ENABLE_TOPIC:-/highstar/position_cmd_adapter_enable}"
SAFE_MIN_Z="${SAFE_MIN_Z:-0.80}"
SAFE_MAX_Z="${SAFE_MAX_Z:-2.80}"
ADAPTER_TIMEOUT_S="${ADAPTER_TIMEOUT_S:-20}"
COMMAND_TIMEOUT_S="${COMMAND_TIMEOUT_S:-55}"
ADAPTER_WIDTH="${ADAPTER_WIDTH:-320}"
ADAPTER_HEIGHT="${ADAPTER_HEIGHT:-180}"
ADAPTER_POINT_STRIDE="${ADAPTER_POINT_STRIDE:-2}"
HIGHSTAR_MAP_MIN_X="${HIGHSTAR_MAP_MIN_X:--35.0}"
HIGHSTAR_MAP_MIN_Y="${HIGHSTAR_MAP_MIN_Y:--45.0}"
HIGHSTAR_MAP_MIN_Z="${HIGHSTAR_MAP_MIN_Z:--0.1}"
HIGHSTAR_MAP_MAX_X="${HIGHSTAR_MAP_MAX_X:-25.0}"
HIGHSTAR_MAP_MAX_Y="${HIGHSTAR_MAP_MAX_Y:-15.0}"
HIGHSTAR_MAP_MAX_Z="${HIGHSTAR_MAP_MAX_Z:-8.0}"
HIGHSTAR_SHOW_FRONTIER="${HIGHSTAR_SHOW_FRONTIER:-false}"
HIGHSTAR_TRIGGER_REPEAT_S="${HIGHSTAR_TRIGGER_REPEAT_S:-8}"

mkdir -p "${RESULT_DIR}"

set +u
source /opt/ros/noetic/setup.bash
if [[ -f "${PX4CTRL_WS}/devel/setup.bash" ]]; then
  source "${PX4CTRL_WS}/devel/setup.bash"
fi
if [[ -f "${PLANNER_CONTROL_COMPAT_WS}/devel/setup.bash" ]]; then
  source "${PLANNER_CONTROL_COMPAT_WS}/devel/setup.bash"
fi
source "${HIGHSTAR_WS}/devel/setup.bash"
export CMAKE_PREFIX_PATH="${HIGHSTAR_WS}/devel:${PX4CTRL_WS}/devel:${PLANNER_CONTROL_COMPAT_WS}/devel:/opt/ros/noetic:${CMAKE_PREFIX_PATH:-}"
export ROS_PACKAGE_PATH="${HIGHSTAR_WS}/src:${PX4CTRL_WS}/src:${PLANNER_CONTROL_COMPAT_WS}/src:/opt/ros/noetic/share:${ROS_PACKAGE_PATH:-}"
export PYTHONPATH="${HIGHSTAR_WS}/devel/lib/python3/dist-packages:${PX4CTRL_WS}/devel/lib/python3/dist-packages:${PLANNER_CONTROL_COMPAT_WS}/devel/lib/python3/dist-packages:/opt/ros/noetic/lib/python3/dist-packages:${PYTHONPATH:-}"
export LD_LIBRARY_PATH="${HIGHSTAR_WS}/devel/lib:${PX4CTRL_WS}/devel/lib:${PLANNER_CONTROL_COMPAT_WS}/devel/lib:/opt/ros/noetic/lib:${LD_LIBRARY_PATH:-}"
set -u

cleanup() {
  for pid in "${SAFETY_PID:-}" "${BRIDGE_PID:-}" "${ADAPTER_PID:-}" "${LAUNCH_PID:-}"; do
    if [[ -n "${pid}" ]]; then
      kill "${pid}" >/dev/null 2>&1 || true
    fi
  done
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
rospy.init_node("highstar_command_bridge_probe_read_odom", anonymous=True, disable_signals=True)
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

python3 "${PROJECT_ROOT}/Scripts/sunray/highstar_swarmtraj_position_cmd_bridge.py" \
  _input_topic:="${TRAJ_TOPIC}" \
  _output_topic:="${RAW_CMD_TOPIC}" \
  _odom_topic:="${ODOM_TOPIC}" \
  _rate_hz:=50.0 \
  _max_v:=1.5 \
  _max_a:=1.5 \
  _retime_to_receive:=true \
  _start_delay_s:=0.10 \
  _diagnostics_path:="${RESULT_DIR}/highstar_swarmtraj_position_cmd_bridge.json" \
  > "${RESULT_DIR}/highstar_swarmtraj_position_cmd_bridge.log" 2>&1 &
BRIDGE_PID=$!

python3 "${PROJECT_ROOT}/Scripts/sunray/goal4_position_cmd_safety_adapter.py" \
  __name:=mosim_highstar_position_cmd_safety_probe \
  _input_topic:="${RAW_CMD_TOPIC}" \
  _output_topic:="${SAFE_CMD_TOPIC}" \
  _enable_topic:="${SAFE_ENABLE_TOPIC}" \
  _initial_enabled:=true \
  _odom_topic:="${ODOM_TOPIC}" \
  _odom_target_guard_enabled:=true \
  _max_xy_target_distance_from_odom_m:=4.0 \
  _max_target_distance_from_odom_m:=5.0 \
  _min_z:="${SAFE_MIN_Z}" \
  _max_z:="${SAFE_MAX_Z}" \
  _jump_guard_enabled:=true \
  _max_position_jump_speed_mps:=3.0 \
  _smoothing_enabled:=true \
  _smoothing_max_speed_mps:=1.2 \
  _diagnostics_path:="${RESULT_DIR}/highstar_position_cmd_safety_adapter.json" \
  > "${RESULT_DIR}/highstar_position_cmd_safety_adapter.log" 2>&1 &
SAFETY_PID=$!

for _ in $(seq 1 40); do
  if rosnode ping -c 1 /murder_demo >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

rosnode info /murder_demo > "${RESULT_DIR}/murder_node_info_before_trigger.txt" 2>&1 || true
rostopic info "${TRAJ_TOPIC}" > "${RESULT_DIR}/murder_traj_topic_info_before_trigger.txt" 2>&1 || true
rostopic info "${RAW_CMD_TOPIC}" > "${RESULT_DIR}/raw_cmd_topic_info_before_trigger.txt" 2>&1 || true
rostopic info "${SAFE_CMD_TOPIC}" > "${RESULT_DIR}/safe_cmd_topic_info_before_trigger.txt" 2>&1 || true

timeout "${HIGHSTAR_TRIGGER_REPEAT_S}" python3 - <<'PY' \
  > "${RESULT_DIR}/start_trigger_pub.txt" 2>&1 || true
import time

import rospy
from std_msgs.msg import Empty

rospy.init_node("highstar_command_bridge_probe_start_trigger", anonymous=True, disable_signals=True)
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

set +e
timeout "${COMMAND_TIMEOUT_S}" rostopic echo -n 1 "${TRAJ_TOPIC}" \
  > "${RESULT_DIR}/murder_traj_first.txt" 2>&1
traj_rc=$?
timeout "${COMMAND_TIMEOUT_S}" rostopic echo -n 1 "${RAW_CMD_TOPIC}" \
  > "${RESULT_DIR}/highstar_position_cmd_raw_first.txt" 2>&1
raw_rc=$?
timeout "${COMMAND_TIMEOUT_S}" rostopic echo -n 1 "${SAFE_CMD_TOPIC}" \
  > "${RESULT_DIR}/highstar_position_cmd_safe_first.txt" 2>&1
safe_rc=$?
set -e

python3 - "$RESULT_DIR" "$traj_rc" "$raw_rc" "$safe_rc" "$TRAJ_TOPIC" "$RAW_CMD_TOPIC" "$SAFE_CMD_TOPIC" <<'PY'
import json
import pathlib
import sys
import time

result_dir = pathlib.Path(sys.argv[1])
traj_rc = int(sys.argv[2])
raw_rc = int(sys.argv[3])
safe_rc = int(sys.argv[4])
traj_topic = sys.argv[5]
raw_topic = sys.argv[6]
safe_topic = sys.argv[7]

def load_json_with_retry(path: pathlib.Path) -> dict:
    for _ in range(10):
        if path.exists():
            text = path.read_text(encoding="utf-8").strip()
            if text:
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    pass
        time.sleep(0.1)
    return {}

bridge_diag = load_json_with_retry(result_dir / "highstar_swarmtraj_position_cmd_bridge.json")
safety_diag = load_json_with_retry(result_dir / "highstar_position_cmd_safety_adapter.json")

passed = traj_rc == 0 and raw_rc == 0 and safe_rc == 0
summary = {
    "status": "passed_command_bridge_probe" if passed else "blocked_command_bridge_probe",
    "traj_topic": traj_topic,
    "raw_cmd_topic": raw_topic,
    "safe_cmd_topic": safe_topic,
    "traj_echo_exit_code": traj_rc,
    "raw_cmd_echo_exit_code": raw_rc,
    "safe_cmd_echo_exit_code": safe_rc,
    "bridge_counts": {
        "input_count": bridge_diag.get("input_count"),
        "accepted_count": bridge_diag.get("accepted_count"),
        "rejected_count": bridge_diag.get("rejected_count"),
        "published_count": bridge_diag.get("published_count"),
        "last_reject_reason": bridge_diag.get("last_reject_reason"),
    },
    "safety_counts": {
        "raw_count": safety_diag.get("raw_count"),
        "published_count": safety_diag.get("published_count"),
        "jump_rejected_count": safety_diag.get("jump_rejected_count"),
        "odom_guard_applied_count": safety_diag.get("odom_guard_applied_count"),
        "last_reject_reason": safety_diag.get("last_reject_reason"),
    },
    "claim_boundary": (
        "HighStar command bridge smoke only. Safety adapter publishes to a "
        "probe topic, not the px4ctrl authority /position_cmd topic."
    ),
}
(result_dir / "HIGHSTAR_MOSIM_COMMAND_BRIDGE_PROBE.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print(json.dumps(summary, indent=2, ensure_ascii=False))
PY

if [[ "${traj_rc}" -eq 0 && "${raw_rc}" -eq 0 && "${safe_rc}" -eq 0 ]]; then
  exit 0
fi
exit 1
