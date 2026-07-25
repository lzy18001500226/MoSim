#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_DIR="${RESULT_DIR:?RESULT_DIR is required}"
RUN_ID="${RUN_ID:-synthetic-gazebo-step}"
ROS_MASTER_PORT="${ROS_MASTER_PORT:-11348}"
GAZEBO_MASTER_PORT="${GAZEBO_MASTER_PORT:-11349}"
mkdir -p "${RESULT_DIR}"

set +u
source /opt/ros/noetic/setup.bash
[[ -f /opt/mosim_work/sunray_ws/Sunray/devel/setup.bash ]] && source /opt/mosim_work/sunray_ws/Sunray/devel/setup.bash
[[ -f "${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash" ]] && \
  source "${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash"
set -u

export ROS_MASTER_URI="http://127.0.0.1:${ROS_MASTER_PORT}"
export GAZEBO_MASTER_URI="http://127.0.0.1:${GAZEBO_MASTER_PORT}"
pids=()
cleanup() {
  for pid in "${pids[@]}"; do kill "${pid}" 2>/dev/null || true; done
  for pid in "${pids[@]}"; do wait "${pid}" 2>/dev/null || true; done
}
trap cleanup EXIT

roscore -p "${ROS_MASTER_PORT}" >"${RESULT_DIR}/roscore.log" 2>&1 & pids+=("$!")
for _ in $(seq 1 100); do rosparam list >/dev/null 2>&1 && break; sleep 0.1; done
gzserver --pause -s libgazebo_ros_api_plugin.so /usr/share/gazebo-11/worlds/empty.world >"${RESULT_DIR}/gzserver.log" 2>&1 & pids+=("$!")
for _ in $(seq 1 100); do rostopic type /clock >/dev/null 2>&1 && break; sleep 0.1; done

rostopic pub -r 250 /uav1/mavros/local_position/odom nav_msgs/Odometry \
  '{header: {frame_id: world}, child_frame_id: base_link, pose: {pose: {orientation: {w: 1.0}}}}' \
  >"${RESULT_DIR}/odom.log" 2>&1 & pids+=("$!")
rostopic pub -r 250 /uav1/mavros/imu/data sensor_msgs/Imu \
  '{header: {frame_id: base_link}, orientation: {w: 1.0}}' \
  >"${RESULT_DIR}/imu.log" 2>&1 & pids+=("$!")
rostopic pub -r 20 /uav1/mavros/state mavros_msgs/State \
  '{connected: true, armed: false, mode: MANUAL}' \
  >"${RESULT_DIR}/state.log" 2>&1 & pids+=("$!")

python3 "${PROJECT_ROOT}/Scripts/mworks_live/run_rt1_synthetic_mworks_responder.py" \
  --duration-s 5 --stall-after-s 2 --stall-duration-s 0.3 \
  --output "${RESULT_DIR}/synthetic_responder.json" \
  >"${RESULT_DIR}/responder.log" 2>&1 & responder_pid="$!"; pids+=("${responder_pid}")

adapter="$(PROJECT_ROOT="${PROJECT_ROOT}" bash "${PROJECT_ROOT}/Scripts/mworks_live/build_ros1_rt1_adapter_cpp.sh")"
"${adapter}" --run-id "${RUN_ID}" --result-dir "${RESULT_DIR}" \
  --mworks-host 127.0.0.1 --mworks-port 49020 --rate-hz 200 \
  --status-rate-hz 5 --allow-ground-hold-reference \
  --time-mode gazebo_step --gazebo-steps-per-command 5 --gazebo-step-size-ns 1000000 \
  >"${RESULT_DIR}/adapter.log" 2>&1 & adapter_pid="$!"; pids+=("${adapter_pid}")

wait "${responder_pid}" || true
sleep 0.5
kill "${adapter_pid}" 2>/dev/null || true
wait "${adapter_pid}" 2>/dev/null || true
python3 "${PROJECT_ROOT}/Scripts/mworks_live/analyze_gazebo_step_synthetic_gate.py" \
  --result-dir "${RESULT_DIR}"
