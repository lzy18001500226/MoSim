#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="${1:-${ROOT_DIR}/Results/sunray_ros1/falcon_d3_node_smoke_${STAMP}}"
FALCON_WS="${FALCON_WS:-${ROOT_DIR}/Results/sunray_ros1/falcon_f1_minimal_build_probe_20260703_191928/ws}"
FALCON_LOCAL_DEPS_PREFIX="${FALCON_LOCAL_DEPS_PREFIX:-${ROOT_DIR}/Results/sunray_ros1/falcon_local_deps_combined_20260703_191853/prefix}"
ROS_MASTER_URI="${ROS_MASTER_URI:-http://127.0.0.1:11320}"
export ROS_MASTER_URI
export MOSIM_ROOT="${ROOT_DIR}"
export LD_LIBRARY_PATH="${FALCON_LOCAL_DEPS_PREFIX}/usr/lib/x86_64-linux-gnu:${FALCON_LOCAL_DEPS_PREFIX}/lib:${FALCON_LOCAL_DEPS_PREFIX}/lib64:${LD_LIBRARY_PATH:-}"

mkdir -p "${OUT_DIR}"

set +u
source /opt/ros/noetic/setup.bash
source "${FALCON_WS}/devel/setup.bash"
set -u

cleanup() {
  if [ -n "${stim_pid:-}" ]; then kill "${stim_pid}" >/dev/null 2>&1 || true; fi
  if [ -n "${launch_pid:-}" ]; then kill "${launch_pid}" >/dev/null 2>&1 || true; fi
  if [ -n "${bridge_pid:-}" ]; then kill "${bridge_pid}" >/dev/null 2>&1 || true; fi
  if [ -n "${roscore_pid:-}" ]; then kill "${roscore_pid}" >/dev/null 2>&1 || true; fi
}
trap cleanup EXIT

roscore -p "${ROS_MASTER_URI##*:}" > "${OUT_DIR}/roscore.log" 2>&1 &
roscore_pid=$!
sleep 3

python3 "${ROOT_DIR}/Scripts/sunray/falcon_mosim_topic_bridge.py" \
  --summary-json "${OUT_DIR}/bridge_summary.json" \
  > "${OUT_DIR}/bridge.log" 2>&1 &
bridge_pid=$!
sleep 1

roslaunch "${ROOT_DIR}/Scripts/sunray/falcon_mosim_exploration.launch" \
  > "${OUT_DIR}/falcon_launch.log" 2>&1 &
launch_pid=$!
sleep 5

if ! kill -0 "${launch_pid}" >/dev/null 2>&1; then
  echo "failed_launch_exited" > "${OUT_DIR}/status.txt"
else
  python3 "${ROOT_DIR}/Scripts/sunray/falcon_d2_synthetic_stimulus.py" \
    --duration-s "${FALCON_NODE_SMOKE_DURATION_S:-12}" \
    --summary-json "${OUT_DIR}/stimulus_summary.json" \
    > "${OUT_DIR}/stimulus.log" 2>&1 &
  stim_pid=$!
  wait "${stim_pid}" || true
  rostopic list > "${OUT_DIR}/rostopic_list.txt" 2>&1 || true
  timeout 5s rostopic hz /voxel_mapping/occupancy_grid_occupied \
    > "${OUT_DIR}/occupancy_grid_occupied_hz.txt" 2>&1 || true
  timeout 5s rostopic hz /planning/pos_cmd \
    > "${OUT_DIR}/planning_pos_cmd_hz.txt" 2>&1 || true
  echo "completed" > "${OUT_DIR}/status.txt"
fi

cleanup
trap - EXIT

python3 - "${OUT_DIR}" <<'PY'
import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
status = (out / "status.txt").read_text(errors="replace").strip() if (out / "status.txt").exists() else "missing_status"
launch = (out / "falcon_launch.log").read_text(errors="replace") if (out / "falcon_launch.log").exists() else ""
stim = (out / "stimulus.log").read_text(errors="replace") if (out / "stimulus.log").exists() else ""
topics = (out / "rostopic_list.txt").read_text(errors="replace").splitlines() if (out / "rostopic_list.txt").exists() else []
fatal_errors = [
    line for line in (launch + "\n" + stim).splitlines()
    if any(k in line.lower() for k in [
        "fatal", "exception", "traceback", "check failed", "error while loading shared libraries"
    ])
]
planner_errors = [
    line for line in (launch + "\n" + stim).splitlines()
    if "[ERROR]" in line and line not in fatal_errors
]
passed = status == "completed" and not fatal_errors
payload = {
    "schema": "mosim.falcon_d3_node_smoke.v1",
    "status": "passed_with_planner_warnings" if passed and planner_errors else ("passed" if passed else "failed"),
    "raw_status": status,
    "out_dir": str(out),
    "topic_count": len(topics),
    "selected_topics": [
        t for t in topics
        if t.startswith("/voxel_mapping") or t.startswith("/planning") or t in [
            "/odom_world", "/transformer/sensor_pose_topic"
        ]
    ][:80],
    "fatal_error_tail": fatal_errors[-40:],
    "planner_error_tail": planner_errors[-40:],
    "claim_boundary": "FALCON node smoke with synthetic inputs only; not Gazebo/PX4/MAVROS/RViz or full-coverage evidence.",
}
(out / "FALCON_D3_NODE_SMOKE.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
(out / "SUMMARY.md").write_text(
    "# FALCON D3 Node Smoke\n\n"
    f"Status: `{payload['status']}`\n\n"
    "This runs FALCON nodes with synthetic bridge inputs only. It is not Factory full-coverage evidence.\n",
    encoding="utf-8",
)
print(json.dumps(payload, ensure_ascii=False))
PY
