#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RACER_WS="${RACER_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/racer_ws_d1_optimized_20260701_084307}"
ROS_MASTER_PORT="${ROS_MASTER_PORT:-11332}"
ROS_MASTER_URI="${ROS_MASTER_URI:-http://127.0.0.1:${ROS_MASTER_PORT}}"
RUN_ID="${RUN_ID:-racer_d2_adapter_dry_run_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
STIMULUS_TIMEOUT_S="${STIMULUS_TIMEOUT_S:-110}"
STIMULUS_DURATION_S="${STIMULUS_DURATION_S:-75}"

export PROJECT_ROOT
export ROS_MASTER_URI

mkdir -p "${RESULT_DIR}"

fail() {
  local reason="$1"
  echo "RACER_D2_ADAPTER_DRY_RUN=FAIL"
  echo "reason=${reason}"
  printf '{"status":"failed","reason":"%s","result_dir":"%s"}\n' "${reason}" "${RESULT_DIR}" \
    >"${RESULT_DIR}/RUN_MANIFEST.json"
  exit 1
}

cleanup() {
  set +e
  for pid in ${ROSLAUNCH_PID:-} ${ROSCORE_PID:-}; do
    if [[ -n "${pid}" ]] && kill -0 "${pid}" >/dev/null 2>&1; then
      kill "${pid}" >/dev/null 2>&1
      wait "${pid}" >/dev/null 2>&1
    fi
  done
}
trap cleanup EXIT

echo "RACER_D2_ADAPTER_DRY_RUN=START"
echo "project_root=${PROJECT_ROOT}"
echo "racer_ws=${RACER_WS}"
echo "ros_master_uri=${ROS_MASTER_URI}"
echo "result_dir=${RESULT_DIR}"

[[ -d "${PROJECT_ROOT}" ]] || fail "project_root_missing"
[[ -d "${RACER_WS}" ]] || fail "racer_ws_missing_run_racer_d1_first"
[[ -f "${RACER_WS}/devel/setup.bash" ]] || fail "racer_ws_devel_setup_missing"
[[ -x "${RACER_WS}/devel/lib/exploration_manager/exploration_node" ]] \
  || fail "exploration_node_not_executable"
[[ -x "${RACER_WS}/devel/lib/plan_manage/traj_server" ]] \
  || fail "traj_server_not_executable"
[[ -x "${RACER_WS}/devel/lib/lkh_mtsp_solver/mtsp_node" ]] \
  || fail "mtsp_node_not_executable"

set +u
source /opt/ros/noetic/setup.bash
source "${RACER_WS}/devel/setup.bash"
set -u

cp "${PROJECT_ROOT}/Scripts/sunray/racer_d2_adapter_dry_run.launch" \
  "${RESULT_DIR}/racer_d2_adapter_dry_run.launch"

roslaunch "${PROJECT_ROOT}/Scripts/sunray/racer_d2_adapter_dry_run.launch" --nodes \
  >"${RESULT_DIR}/racer_d2_launch_nodes.txt" 2>"${RESULT_DIR}/racer_d2_launch_nodes.err" \
  || fail "racer_d2_launch_parse_failed"

roscore -p "${ROS_MASTER_PORT}" >"${RESULT_DIR}/roscore.log" 2>&1 &
ROSCORE_PID=$!
for _ in {1..20}; do
  if rosnode list >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done
rosnode list >/dev/null 2>&1 || fail "roscore_not_ready"

roslaunch --wait "${PROJECT_ROOT}/Scripts/sunray/racer_d2_adapter_dry_run.launch" \
  >"${RESULT_DIR}/racer_d2_roslaunch.log" 2>&1 &
ROSLAUNCH_PID=$!
sleep 8
if ! kill -0 "${ROSLAUNCH_PID}" >/dev/null 2>&1; then
  fail "racer_roslaunch_exited_before_stimulus"
fi

set +e
timeout "${STIMULUS_TIMEOUT_S}" \
  python3 "${PROJECT_ROOT}/Scripts/sunray/racer_d2_synthetic_stimulus.py" \
    --duration-s "${STIMULUS_DURATION_S}" \
    --summary-file "${RESULT_DIR}/racer_d2_stimulus_summary.json" \
    >"${RESULT_DIR}/racer_d2_stimulus.log" 2>&1
stimulus_exit=$?
set -e

if [[ "${stimulus_exit}" -ne 0 ]]; then
  rostopic list >"${RESULT_DIR}/topics.txt" 2>"${RESULT_DIR}/rostopic_list.err" || true
  rosnode list >"${RESULT_DIR}/nodes.txt" 2>"${RESULT_DIR}/rosnode_list.err" || true
  for topic in \
    /uav1/mosim/racer_d2/odom /uav2/mosim/racer_d2/odom /uav3/mosim/racer_d2/odom \
    /uav1/mosim/racer_d2/sensor_pose /uav2/mosim/racer_d2/sensor_pose /uav3/mosim/racer_d2/sensor_pose \
    /uav1/mosim/racer_d2/cloud /uav2/mosim/racer_d2/cloud /uav3/mosim/racer_d2/cloud \
    /planning/bspline_1 /planning/bspline_2 /planning/bspline_3 \
    /uav1/mosim/racer_d2/pos_cmd /uav2/mosim/racer_d2/pos_cmd /uav3/mosim/racer_d2/pos_cmd \
    /swarm_expl/drone_state /planning/swarm_traj /multi_map_manager/chunk_stamps; do
    timeout 2 rostopic info "${topic}" >"${RESULT_DIR}/topic_info_${topic//\//_}.txt" 2>&1 || true
  done
  printf '{"status":"failed","reason":"stimulus_failed","stimulus_exit":%s,"result_dir":"%s","claim":"RACER-D2 adapter dry-run attempted; no Gazebo/PX4/MAVROS/RViz claim"}\n' \
    "${stimulus_exit}" "${RESULT_DIR}" >"${RESULT_DIR}/RUN_MANIFEST.json"
  echo "RACER_D2_ADAPTER_DRY_RUN=FAIL"
  echo "reason=stimulus_failed"
  echo "stimulus_exit=${stimulus_exit}"
  echo "result_dir=${RESULT_DIR}"
  exit "${stimulus_exit}"
fi

python3 - "${RESULT_DIR}/racer_d2_stimulus_summary.json" <<'PY'
import json
import sys

summary_path = sys.argv[1]
with open(summary_path, "r", encoding="utf-8") as f:
    data = json.load(f)
if data.get("status") != "passed":
    raise SystemExit("stimulus_summary_not_passed")
if data.get("forbidden_topics"):
    raise SystemExit("forbidden_topics_in_stimulus_summary")
PY

printf '{"status":"passed","result_dir":"%s","ros_master_uri":"%s","claim":"RACER-D2 adapter dry-run only; no Gazebo/PX4/MAVROS/RViz or exploration-success claim"}\n' \
  "${RESULT_DIR}" "${ROS_MASTER_URI}" >"${RESULT_DIR}/RUN_MANIFEST.json"
echo "RACER_D2_ADAPTER_DRY_RUN=PASS"
echo "result_dir=${RESULT_DIR}"
