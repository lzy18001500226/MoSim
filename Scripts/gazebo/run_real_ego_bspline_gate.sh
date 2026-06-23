#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/sunray150_gazebo_ros2_real_ego_bspline_gate}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
MOSIM_MSGS_SETUP="${MOSIM_MSGS_SETUP:-${PROJECT_ROOT}/Results/tmp/ros2_ws_mosim_msgs_20260615_ego_gate/install/setup.bash}"
EGO_SETUP="${EGO_SETUP:-${PROJECT_ROOT}/Results/tmp/ego_planner_ros2_port_ws/install/setup.bash}"
GAZEBO_ENV_SCRIPT="${GAZEBO_ENV_SCRIPT:-${PROJECT_ROOT}/Scripts/gazebo/setup_gazebo_wsl_env.sh}"
WORLD="${WORLD:-Config/gazebo/worlds/yunzong_planning_test_sunray150_assembled.sdf}"
GAZEBO_MODEL_PATH="${GAZEBO_MODEL_PATH:-${PROJECT_ROOT}/Config/gazebo/models}"
EGO_LAUNCH="${EGO_LAUNCH:-mosim_gazebo_real_planner_gate.launch.py}"
ODOM_TOPIC="${ODOM_TOPIC:-/mosim/planner/odom}"
CLOUD_TOPIC="${CLOUD_TOPIC:-/mosim/planner/global_points}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-20}"
EGO_REVIEW_RECORD_SECONDS="${EGO_REVIEW_RECORD_SECONDS:-45}"

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_DIR}"

if [[ -f "${GAZEBO_ENV_SCRIPT}" ]]; then
  # shellcheck disable=SC1090
  source "${GAZEBO_ENV_SCRIPT}"
fi

set +u
# shellcheck disable=SC1090
source "${ROS_SETUP}"
# shellcheck disable=SC1090
source "${MOSIM_MSGS_SETUP}"
# shellcheck disable=SC1090
source "${EGO_SETUP}"
set -u

export ROS_LOG_DIR="${PROJECT_ROOT}/Results/tmp/ros_logs"
mkdir -p "${ROS_LOG_DIR}"
export GZ_SIM_RESOURCE_PATH="${GAZEBO_MODEL_PATH}"
export IGN_GAZEBO_RESOURCE_PATH="${GAZEBO_MODEL_PATH}"

PIDS=()
cleanup() {
  local pid
  for pid in "${PIDS[@]}"; do
    kill "${pid}" >/dev/null 2>&1 || true
  done
  sleep 1
  for pid in "${PIDS[@]}"; do
    kill -KILL "${pid}" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT

ign gazebo -s --headless-rendering --render-engine-server ogre -r "${WORLD}" \
  > "${RESULT_DIR}/gazebo.stdout.log" \
  2> "${RESULT_DIR}/gazebo.stderr.log" &
PIDS+=("$!")
sleep 4

ros2 run ros_gz_bridge parameter_bridge \
  /mosim/gazebo/imu@sensor_msgs/msg/Imu@gz.msgs.IMU \
  /mosim/gazebo/lidar_points/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked \
  > "${RESULT_DIR}/ros_gz_bridge.stdout.log" \
  2> "${RESULT_DIR}/ros_gz_bridge.stderr.log" &
PIDS+=("$!")

ros2 run tf2_ros static_transform_publisher \
  --x 0 --y 0 --z 1.2 --roll 0 --pitch 0 --yaw 0 \
  --frame-id map \
  --child-frame-id sunray150_assembled/base_link/mid360_lidar \
  > "${RESULT_DIR}/static_tf.stdout.log" \
  2> "${RESULT_DIR}/static_tf.stderr.log" &
PIDS+=("$!")
sleep 2

python3 Scripts/ros/gazebo_fastlio_imu_passthrough.py \
  --imu-input-topic /mosim/gazebo/imu \
  --fastlio-imu-topic /mosim/fastlio/livox/imu \
  --sunray-imu-topic /uav1/livox/imu \
  --imu-frame sunray150_assembled/base_link/forward_imu \
  --output-json "${RESULT_DIR}/fastlio_imu_passthrough.json" \
  --trace-jsonl "${RESULT_DIR}/fastlio_imu_passthrough.trace.jsonl" \
  > "${RESULT_DIR}/fastlio_imu_passthrough.stdout.log" \
  2> "${RESULT_DIR}/fastlio_imu_passthrough.stderr.log" &
PIDS+=("$!")

python3 Scripts/ros/gazebo_fastlio_planner_input_adapter.py \
  --lidar-input-topic /mosim/gazebo/lidar_points/points \
  --imu-input-topic /mosim/gazebo/imu \
  --fastlio-lidar-topic /mosim/fastlio/livox/lidar \
  --fastlio-imu-topic /mosim/fastlio/livox/imu \
  --spark-livox-custom-topic /mosim/spark_fastlio/livox/lidar \
  --sunray-lidar-topic /uav1/livox/lidar \
  --sunray-imu-topic /uav1/livox/imu \
  --planner-global-points-topic /uav1/global_points \
  --mosim-planner-global-points-topic "${CLOUD_TOPIC}" \
  --planner-odom-topic /uav1/sunray/gazebo_pose \
  --mosim-planner-odom-topic "${ODOM_TOPIC}" \
  --map-frame map \
  --global-frame map \
  --sensor-frame sunray150_assembled/base_link/mid360_lidar \
  --imu-frame sunray150_assembled/base_link/forward_imu \
  --odom-child-frame uav1/base_link \
  --tf-lookup-timeout-s 0.2 \
  --spark-livox-scan-lines 4 \
  --spark-livox-scan-rate-hz 10 \
  --odom-rate-hz 20 \
  --output-json "${RESULT_DIR}/fastlio_planner_input_adapter.json" \
  --trace-jsonl "${RESULT_DIR}/fastlio_planner_input_adapter.trace.jsonl" \
  --disable-spark-livox-custom-output \
  --disable-imu-output \
  > "${RESULT_DIR}/fastlio_planner_input_adapter.stdout.log" \
  2> "${RESULT_DIR}/fastlio_planner_input_adapter.stderr.log" &
PIDS+=("$!")

sleep 8

if timeout --kill-after=5s "${TIMEOUT_SECONDS}" ros2 topic echo --once "${CLOUD_TOPIC}" sensor_msgs/msg/PointCloud2 \
  > "${RESULT_DIR}/topic_mosim_planner_global_points_once.txt" \
  2> "${RESULT_DIR}/topic_mosim_planner_global_points_once.stderr.txt"; then
  printf '0\n' > "${RESULT_DIR}/topic_mosim_planner_global_points_once.rc"
else
  printf '%s\n' "$?" > "${RESULT_DIR}/topic_mosim_planner_global_points_once.rc"
fi

ros2 launch ego_planner "${EGO_LAUNCH}" \
  odom_topic:="${ODOM_TOPIC}" \
  cloud_topic:="${CLOUD_TOPIC}" \
  > "${RESULT_DIR}/ego_planner.stdout.log" \
  2> "${RESULT_DIR}/ego_planner.stderr.log" &
PIDS+=("$!")

timeout --kill-after=5s "${TIMEOUT_SECONDS}" ros2 topic echo --once /planning/bspline ego_planner_msgs/msg/Bspline \
  > "${RESULT_DIR}/topic_planning_bspline_once.txt" \
  2> "${RESULT_DIR}/topic_planning_bspline_once.stderr.txt" &
BSPLINE_ECHO_PID="$!"

python3 Scripts/ros/record_real_ego_rviz_review_topics.py \
  --output-json "${RESULT_DIR}/real_ego_topic_recorder.json" \
  --duration-seconds "${EGO_REVIEW_RECORD_SECONDS}" \
  --planner-cloud-topic "${CLOUD_TOPIC}" \
  --ego-inflate-topic /grid_map/occupancy_inflate \
  --max-points 250000 \
  > "${RESULT_DIR}/real_ego_topic_recorder.stdout.log" \
  2> "${RESULT_DIR}/real_ego_topic_recorder.stderr.log" &
RECORDER_PID="$!"

sleep 15

ros2 topic list > "${RESULT_DIR}/ros2_topic_list.txt" || true

if wait "${BSPLINE_ECHO_PID}"; then
  printf '0\n' > "${RESULT_DIR}/topic_planning_bspline_once.rc"
else
  printf '%s\n' "$?" > "${RESULT_DIR}/topic_planning_bspline_once.rc"
fi

if wait "${RECORDER_PID}"; then
  printf '0\n' > "${RESULT_DIR}/real_ego_topic_recorder.rc"
else
  printf '%s\n' "$?" > "${RESULT_DIR}/real_ego_topic_recorder.rc"
fi

sleep 5

if timeout --kill-after=5s 15 ros2 topic echo --once /grid_map/occupancy_inflate sensor_msgs/msg/PointCloud2 \
  > "${RESULT_DIR}/topic_grid_map_occupancy_inflate_once.txt" \
  2> "${RESULT_DIR}/topic_grid_map_occupancy_inflate_once.stderr.txt"; then
  printf '0\n' > "${RESULT_DIR}/topic_grid_map_occupancy_inflate_once.rc"
else
  printf '%s\n' "$?" > "${RESULT_DIR}/topic_grid_map_occupancy_inflate_once.rc"
fi

if timeout --kill-after=5s 10 ros2 topic hz /planning/bspline \
  > "${RESULT_DIR}/topic_planning_bspline_hz.txt" \
  2> "${RESULT_DIR}/topic_planning_bspline_hz.stderr.txt"; then
  printf '0\n' > "${RESULT_DIR}/topic_planning_bspline_hz.rc"
else
  printf '%s\n' "$?" > "${RESULT_DIR}/topic_planning_bspline_hz.rc"
fi

python3 - <<PY
import json
import re
from pathlib import Path

out = Path("${RESULT_DIR}")

def read(name: str) -> str:
    path = out / name
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""

bspline = read("topic_planning_bspline_once.txt")
planner_cloud = read("topic_mosim_planner_global_points_once.txt")
occupancy = read("topic_grid_map_occupancy_inflate_once.txt")
ego_log = read("ego_planner.stdout.log") + "\n" + read("ego_planner.stderr.log")
adapter = json.loads(read("fastlio_planner_input_adapter.json") or "{}")
recorder = json.loads(read("real_ego_topic_recorder.json") or "{}")
adapter_counts = adapter.get("counts", {}) if isinstance(adapter, dict) else {}
adapter_filter = adapter.get("planner_cloud_filter", {}) if isinstance(adapter, dict) else {}
recorder_samples = recorder.get("samples", {}) if isinstance(recorder, dict) else {}
rc = read("topic_planning_bspline_once.rc").strip()
planner_cloud_rc = read("topic_mosim_planner_global_points_once.rc").strip()
planner_cloud_width = int(re.search(r"^width:\s*(\d+)", planner_cloud, re.M).group(1)) if re.search(r"^width:\s*(\d+)", planner_cloud, re.M) else 0
occupancy_widths = [int(item) for item in re.findall(r"^width:\s*(\d+)", occupancy, re.M)]
occupancy_width = max(occupancy_widths) if occupancy_widths else 0
recorder_planner = recorder_samples.get("planner_cloud_map_frame", {}) if isinstance(recorder_samples, dict) else {}
recorder_inflate = recorder_samples.get("ego_occupancy_inflate", {}) if isinstance(recorder_samples, dict) else {}
recorder_planner_finite = int(recorder_planner.get("finite_point_count", 0) or 0)
recorder_inflate_finite = int(recorder_inflate.get("finite_point_count", 0) or 0)
bspline_ok = rc == "0" and "pos_pts:" in bspline and "knots:" in bspline
planner_cloud_ok = (
    int(adapter_counts.get("mosim_planner_global_points_published", 0) or 0) > 0
    and int(adapter_filter.get("last_stats", {}).get("finite_after_filter", 0) or 0) > 0
) or recorder_planner_finite > 0 or planner_cloud_width > 0
occupancy_ok = occupancy_width > 0 or recorder_inflate_finite > 0
gate_passed = bspline_ok and planner_cloud_ok and occupancy_ok
payload = {
    "schema": "mosim.real_ego_bspline_gate.v1",
    "status": "real_ego_bspline_with_map_passed" if gate_passed else "blocked",
    "gate_passed": gate_passed,
    "result_dir": "${RESULT_DIR}",
    "inputs": {"odom": "${ODOM_TOPIC}", "cloud": "${CLOUD_TOPIC}"},
    "outputs": {"bspline": "/planning/bspline", "occupancy_inflate": "/grid_map/occupancy_inflate"},
    "planner_cloud_sample_returncode": planner_cloud_rc,
    "planner_cloud_width": planner_cloud_width,
    "planner_cloud_recorder_finite_points": recorder_planner_finite,
    "adapter_counts": {
        "lidar_received": adapter_counts.get("lidar_received", 0),
        "mosim_planner_global_points_published": adapter_counts.get("mosim_planner_global_points_published", 0),
        "planner_odom_published": adapter_counts.get("planner_odom_published", 0),
        "tf_lookup_failures": adapter_counts.get("tf_lookup_failures", 0),
        "frame_mismatch_count": adapter_counts.get("frame_mismatch_count", 0),
    },
    "adapter_planner_cloud_last_stats": adapter_filter.get("last_stats", {}),
    "bspline_sample_returncode": rc,
    "bspline_pos_pts_tokens": len(re.findall(r"pos_pts:", bspline)),
    "bspline_knots_tokens": len(re.findall(r"knots:", bspline)),
    "occupancy_sample_recorded": bool(occupancy.strip()),
    "occupancy_inflate_width": occupancy_width,
    "occupancy_inflate_width_samples": occupancy_widths[:20],
    "occupancy_inflate_recorder_finite_points": recorder_inflate_finite,
    "topic_recorder_status": recorder.get("status"),
    "topic_recorder_message_counts": recorder.get("message_counts", {}),
    "topic_recorder_measured_rates_hz": recorder.get("measured_rates_hz", {}),
    "topic_recorder_blockers": recorder.get("blockers", []),
    "ego_log_markers": {
        "final_plan_success_true": "final_plan_success=1" in ego_log or "final_plan_success=true" in ego_log,
        "unable_global": "Unable to generate global trajectory" in ego_log,
        "wrong_target": "Wrong target_type" in ego_log,
    },
    "artifacts": [
        "${RESULT_DIR}/ego_planner.stdout.log",
        "${RESULT_DIR}/ego_planner.stderr.log",
        "${RESULT_DIR}/topic_mosim_planner_global_points_once.txt",
        "${RESULT_DIR}/topic_planning_bspline_once.txt",
        "${RESULT_DIR}/topic_planning_bspline_hz.txt",
        "${RESULT_DIR}/topic_grid_map_occupancy_inflate_once.txt",
        "${RESULT_DIR}/real_ego_topic_recorder.json",
        "${RESULT_DIR}/ros2_topic_list.txt",
        "${RESULT_DIR}/fastlio_planner_input_adapter.json",
        "${RESULT_DIR}/fastlio_imu_passthrough.json",
    ],
    "claim_boundary": [
        "Real ROS2 EGO planner port was launched against same-run Gazebo odom/global point cloud.",
        "This gate proves non-empty planner global point cloud input, non-empty /grid_map/occupancy_inflate output, and one /planning/bspline sample.",
        "No traj_server, /position_cmd, controller output, actuator command, closed_loop, controller performance, or multi-UAV readiness is claimed.",
    ],
}
(out / "REAL_EGO_BSPLINE_GATE.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(payload, ensure_ascii=False, indent=2))
PY
