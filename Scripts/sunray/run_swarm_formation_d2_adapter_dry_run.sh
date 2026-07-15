#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SWARM_FORMATION_WS="${SWARM_FORMATION_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/swarm_formation_ws_d1_20260701_173306}"
ROS_MASTER_PORT="${ROS_MASTER_PORT:-11333}"
ROS_MASTER_URI="${ROS_MASTER_URI:-http://127.0.0.1:${ROS_MASTER_PORT}}"
RUN_ID="${RUN_ID:-swarm_formation_d2_adapter_dry_run_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
STIMULUS_TIMEOUT_S="${STIMULUS_TIMEOUT_S:-125}"
STIMULUS_DURATION_S="${STIMULUS_DURATION_S:-90}"

export PROJECT_ROOT
export ROS_MASTER_URI

mkdir -p "${RESULT_DIR}"

fail() {
  local reason="$1"
  echo "SWARM_FORMATION_D2_ADAPTER_DRY_RUN=FAIL"
  echo "reason=${reason}"
  python3 - "$reason" "$RESULT_DIR" "$ROS_MASTER_URI" <<'PY'
import json
import sys

reason, result_dir, ros_master_uri = sys.argv[1:4]
with open(f"{result_dir}/RUN_MANIFEST.json", "w", encoding="utf-8") as f:
    json.dump(
        {
            "status": "failed",
            "reason": reason,
            "result_dir": result_dir,
            "ros_master_uri": ros_master_uri,
            "claim": "Swarm-Formation SF-D2 adapter dry-run attempted; no Gazebo/PX4/MAVROS/RViz claim",
        },
        f,
        indent=2,
        sort_keys=True,
    )
    f.write("\n")
PY
  exit 1
}

collect_runtime_snapshot() {
  set +e
  rostopic list >"${RESULT_DIR}/topics.txt" 2>"${RESULT_DIR}/rostopic_list.err"
  rosnode list >"${RESULT_DIR}/nodes.txt" 2>"${RESULT_DIR}/rosnode_list.err"
  for topic in \
    /drone_0_visual_slam/odom /drone_1_visual_slam/odom /drone_2_visual_slam/odom \
    /drone_0_pcl_render_node/cloud /drone_1_pcl_render_node/cloud /drone_2_pcl_render_node/cloud \
    /move_base_simple/goal \
    /drone_0_planning/trajectory /drone_1_planning/trajectory /drone_2_planning/trajectory \
    /drone_0_planning/pos_cmd /drone_1_planning/pos_cmd /drone_2_planning/pos_cmd \
    /drone_0_planning/start /drone_1_planning/start /drone_2_planning/start \
    /drone_0_planning/finish /drone_1_planning/finish /drone_2_planning/finish \
    /broadcast_traj_from_planner /broadcast_traj_to_planner; do
    timeout 2 rostopic info "${topic}" >"${RESULT_DIR}/topic_info_${topic//\//_}.txt" 2>&1
  done
  set -e
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

echo "SWARM_FORMATION_D2_ADAPTER_DRY_RUN=START"
echo "project_root=${PROJECT_ROOT}"
echo "swarm_formation_ws=${SWARM_FORMATION_WS}"
echo "ros_master_uri=${ROS_MASTER_URI}"
echo "result_dir=${RESULT_DIR}"

[[ -d "${PROJECT_ROOT}" ]] || fail "project_root_missing"
[[ -d "${SWARM_FORMATION_WS}" ]] || fail "swarm_formation_ws_missing_run_sf_d1_first"
[[ -f "${SWARM_FORMATION_WS}/devel/setup.bash" ]] || fail "swarm_formation_ws_devel_setup_missing"
[[ -x "${SWARM_FORMATION_WS}/devel/lib/ego_planner/ego_planner_node" ]] \
  || fail "ego_planner_node_not_executable"
[[ -x "${SWARM_FORMATION_WS}/devel/lib/ego_planner/traj_server" ]] \
  || fail "traj_server_not_executable"

set +u
source /opt/ros/noetic/setup.bash
source "${SWARM_FORMATION_WS}/devel/setup.bash"
set -u

cp "${PROJECT_ROOT}/Scripts/sunray/swarm_formation_d2_adapter_dry_run.launch" \
  "${RESULT_DIR}/swarm_formation_d2_adapter_dry_run.launch"

roslaunch "${PROJECT_ROOT}/Scripts/sunray/swarm_formation_d2_adapter_dry_run.launch" --nodes \
  >"${RESULT_DIR}/swarm_formation_d2_launch_nodes.txt" \
  2>"${RESULT_DIR}/swarm_formation_d2_launch_nodes.err" \
  || fail "swarm_formation_d2_launch_parse_failed"

roscore -p "${ROS_MASTER_PORT}" >"${RESULT_DIR}/roscore.log" 2>&1 &
ROSCORE_PID=$!
for _ in {1..20}; do
  if rosnode list >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done
rosnode list >/dev/null 2>&1 || fail "roscore_not_ready"

roslaunch --wait "${PROJECT_ROOT}/Scripts/sunray/swarm_formation_d2_adapter_dry_run.launch" \
  >"${RESULT_DIR}/swarm_formation_d2_roslaunch.log" 2>&1 &
ROSLAUNCH_PID=$!
sleep 8
if ! kill -0 "${ROSLAUNCH_PID}" >/dev/null 2>&1; then
  collect_runtime_snapshot
  fail "swarm_formation_roslaunch_exited_before_stimulus"
fi

set +e
timeout "${STIMULUS_TIMEOUT_S}" \
  python3 "${PROJECT_ROOT}/Scripts/sunray/swarm_formation_d2_synthetic_stimulus.py" \
    --duration-s "${STIMULUS_DURATION_S}" \
    --summary-file "${RESULT_DIR}/swarm_formation_d2_stimulus_summary.json" \
    >"${RESULT_DIR}/swarm_formation_d2_stimulus.log" 2>&1
stimulus_exit=$?
set -e

collect_runtime_snapshot

if [[ "${stimulus_exit}" -ne 0 ]]; then
  python3 - "$stimulus_exit" "$RESULT_DIR" "$ROS_MASTER_URI" <<'PY'
import json
import sys

stimulus_exit, result_dir, ros_master_uri = sys.argv[1:4]
with open(f"{result_dir}/RUN_MANIFEST.json", "w", encoding="utf-8") as f:
    json.dump(
        {
            "status": "failed",
            "reason": "stimulus_failed",
            "stimulus_exit": int(stimulus_exit),
            "result_dir": result_dir,
            "ros_master_uri": ros_master_uri,
            "claim": "Swarm-Formation SF-D2 adapter dry-run attempted; no Gazebo/PX4/MAVROS/RViz claim",
        },
        f,
        indent=2,
        sort_keys=True,
    )
    f.write("\n")
PY
  echo "SWARM_FORMATION_D2_ADAPTER_DRY_RUN=FAIL"
  echo "reason=stimulus_failed"
  echo "stimulus_exit=${stimulus_exit}"
  echo "result_dir=${RESULT_DIR}"
  exit "${stimulus_exit}"
fi

python3 - "${RESULT_DIR}/swarm_formation_d2_stimulus_summary.json" <<'PY'
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

python3 - "$RESULT_DIR" "$ROS_MASTER_URI" "$SWARM_FORMATION_WS" <<'PY'
import json
import sys

result_dir, ros_master_uri, workspace = sys.argv[1:4]
with open(f"{result_dir}/RUN_MANIFEST.json", "w", encoding="utf-8") as f:
    json.dump(
        {
            "status": "passed",
            "result_dir": result_dir,
            "ros_master_uri": ros_master_uri,
            "workspace": workspace,
            "claim": "Swarm-Formation SF-D2 adapter dry-run only; no Gazebo/PX4/MAVROS/RViz formation-flight claim",
        },
        f,
        indent=2,
        sort_keys=True,
    )
    f.write("\n")
PY

echo "SWARM_FORMATION_D2_ADAPTER_DRY_RUN=PASS"
echo "result_dir=${RESULT_DIR}"
