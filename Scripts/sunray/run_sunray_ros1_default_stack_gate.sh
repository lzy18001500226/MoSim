#!/usr/bin/env bash
# Run the upstream Sunray ROS1 + PX4 + Gazebo Classic single-UAV stack.
#
# Scope:
# - Uses the upstream Sunray launch/demo path.
# - Does not run MoSim ROS2/GZ/x500 or hand-written controller substitutes.
# - Produces logs and a compact JSON result under Results/sunray_ros1.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/tmp/mosim_sunray_build_20260620_114615/Sunray}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-/opt/mosim_work/sunray_px4}"
RUN_ID="${RUN_ID:-sunray_ros1_default_stack_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
GUI="${GUI:-false}"
RUN_DEMO="${RUN_DEMO:-true}"
TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-95}"
STARTUP_TIMEOUT_S="${STARTUP_TIMEOUT_S:-35}"
EXTERNAL_FUSION_SOURCE="${EXTERNAL_FUSION_SOURCE:-2}"
EXTERNAL_FUSION_POSITION_TOPIC="${EXTERNAL_FUSION_POSITION_TOPIC:-/uav1/mavros/local_position/pose}"
EXTERNAL_FUSION_USE_VISION_POSE="${EXTERNAL_FUSION_USE_VISION_POSE:-true}"

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
}
trap cleanup EXIT

write_json() {
  local status="$1"
  local reason="$2"
  python3 - "$RESULT_DIR" "$status" "$reason" <<'PY'
import json
import os
import sys
from pathlib import Path

result_dir = Path(sys.argv[1])
payload = {
    "schema": "mosim.sunray_ros1_default_stack_gate.v1",
    "status": sys.argv[2],
    "reason": sys.argv[3],
    "result_dir": str(result_dir),
    "logs": {
        "sunray_sim": str(result_dir / "sunray_sim.log"),
        "fmt_external_fusion": str(result_dir / "fmt_external_fusion.log"),
        "fmt_control": str(result_dir / "fmt_control.log"),
        "takeoff_hover_land_demo": str(result_dir / "takeoff_hover_land_demo.log"),
        "uav_state": str(result_dir / "uav_state.jsonl"),
        "model_states": str(result_dir / "model_states.jsonl"),
    },
    "external_fusion": {
        "source": os.environ.get("EXTERNAL_FUSION_SOURCE", "2"),
        "position_topic": os.environ.get("EXTERNAL_FUSION_POSITION_TOPIC", "/uav1/mavros/local_position/pose"),
        "use_vision_pose": os.environ.get("EXTERNAL_FUSION_USE_VISION_POSE", "true"),
    },
    "control_feedback_source": {
        "current_default": "Sunray uav_control consumes /uav1/sunray/px4_state from external_fusion_node.",
        "px4_state_fields": "external_fusion_node fills position/velocity/attitude from MAVROS local_position/velocity_local/imu topics.",
        "flight_controller_imu": "/imu -> PX4 SITL estimator -> /uav1/mavros/imu/data",
        "mid360_imu": "/uav1/livox/imu",
        "fastlio_feedback_into_control": "not proven by this default-stack gate",
    },
    "claim_boundary": [
        "This gate proves only the upstream Sunray ROS1/PX4/Gazebo single-UAV default stack and demo path.",
        "It does not prove MID360/FAST-LIO-backed control unless external_fusion/PX4 fusion of FAST-LIO odometry is separately proven.",
        "It does not prove MoSim/MWORKS controller deployment, ROS2/GZ/x500, EGO planning, or final competition performance.",
    ],
}
(result_dir / "SUNRAY_ROS1_DEFAULT_STACK_GATE.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(payload, ensure_ascii=False, indent=2))
PY
}

source_env() {
  export PATH=/opt/ros/noetic/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib
  source /opt/ros/noetic/setup.bash
  source "${SUNRAY_PX4_DIR}/Tools/simulation/gazebo-classic/setup_gazebo.bash" \
    "${SUNRAY_PX4_DIR}" \
    "${SUNRAY_PX4_DIR}/build/px4_sitl_default"
  source "${SUNRAY_WS}/devel/setup.bash"

  local sunray_models="${SUNRAY_WS}/simulation/sunray_simulator/models"
  export ROS_PACKAGE_PATH="${SUNRAY_PX4_DIR}:${SUNRAY_WS}:/opt/ros/noetic/share:${ROS_PACKAGE_PATH:-}"
  export GAZEBO_MODEL_PATH="${sunray_models}:${sunray_models}/drone_models:${sunray_models}/sensor_models:${sunray_models}/scence_models:${sunray_models}/fake_models:${GAZEBO_MODEL_PATH:-}"
  export GAZEBO_RESOURCE_PATH="${sunray_models}:${GAZEBO_RESOURCE_PATH:-}"
}

if [[ ! -d "${SUNRAY_WS}" ]]; then
  write_json "blocked_missing_sunray_ws" "SUNRAY_WS does not exist: ${SUNRAY_WS}"
  exit 2
fi
if [[ ! -d "${SUNRAY_PX4_DIR}" ]]; then
  write_json "blocked_missing_sunray_px4" "SUNRAY_PX4_DIR does not exist: ${SUNRAY_PX4_DIR}"
  exit 2
fi

source_env

# PX4/Gazebo Classic can leave a stale simulator socket owned by root after abort.
if [[ -S /tmp/px4-sock-0 || -e /tmp/px4-sock-0 ]]; then
  rm -f /tmp/px4-sock-0 2>/dev/null || printf "1\n" | sudo -S rm -f /tmp/px4-sock-0
fi
if [[ -S /tmp/px4-sock-1 || -e /tmp/px4-sock-1 ]]; then
  rm -f /tmp/px4-sock-1 2>/dev/null || printf "1\n" | sudo -S rm -f /tmp/px4-sock-1
fi

roslaunch sunray_simulator sunray_sim_1uav.launch gui:="${GUI}" \
  > "${RESULT_DIR}/sunray_sim.log" 2>&1 &
PIDS+=("$!")

deadline=$((SECONDS + STARTUP_TIMEOUT_S))
while (( SECONDS < deadline )); do
  if ! kill -0 "${PIDS[0]}" >/dev/null 2>&1; then
    write_json "blocked_sunray_sim_exited" "sunray_sim_1uav launch exited before MAVROS became ready"
    exit 3
  fi
  if timeout 2s rostopic echo -n 1 /uav1/mavros/state > "${RESULT_DIR}/mavros_state_first.txt" 2>/dev/null; then
    if grep -q "connected: True" "${RESULT_DIR}/mavros_state_first.txt"; then
      break
    fi
  fi
  sleep 1
done

if ! grep -q "connected: True" "${RESULT_DIR}/mavros_state_first.txt" 2>/dev/null; then
  write_json "blocked_mavros_no_heartbeat" "No connected MAVROS heartbeat on /uav1/mavros/state within startup timeout"
  exit 4
fi

roslaunch sunray_uav_control external_fusion.launch \
  uav_id:=1 uav_name:=uav external_source:="${EXTERNAL_FUSION_SOURCE}" position_topic:="${EXTERNAL_FUSION_POSITION_TOPIC}" use_vision_pose:="${EXTERNAL_FUSION_USE_VISION_POSE}" \
  > "${RESULT_DIR}/fmt_external_fusion.log" 2>&1 &
PIDS+=("$!")
sleep 2

roslaunch sunray_uav_control sunray_control_node.launch \
  uav_id:=1 uav_name:=uav Takeoff_height:=1.0 Land_speed:=0.25 \
  > "${RESULT_DIR}/fmt_control.log" 2>&1 &
PIDS+=("$!")
sleep 3

python3 - "${RESULT_DIR}" <<'PY' &
import json
import subprocess
import sys
import time
from pathlib import Path

result_dir = Path(sys.argv[1])
out = result_dir / "uav_state.jsonl"
end = time.time() + 80
while time.time() < end:
    try:
        text = subprocess.check_output(
            ["timeout", "2s", "rostopic", "echo", "-n", "1", "/uav1/sunray/uav_state"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        time.sleep(0.5)
        continue
    rec = {"wall_time": time.time(), "raw": text}
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    time.sleep(0.5)
PY
PIDS+=("$!")

python3 - "${RESULT_DIR}" <<'PY' &
import json
import subprocess
import sys
import time
from pathlib import Path

result_dir = Path(sys.argv[1])
out = result_dir / "model_states.jsonl"
end = time.time() + 80
while time.time() < end:
    try:
        text = subprocess.check_output(
            ["timeout", "2s", "rostopic", "echo", "-n", "1", "/gazebo/model_states"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        time.sleep(0.5)
        continue
    rec = {"wall_time": time.time(), "raw": text}
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    time.sleep(0.5)
PY
PIDS+=("$!")

if [[ "${RUN_DEMO}" == "true" ]]; then
  timeout "${TOTAL_TIMEOUT_S}s" roslaunch sunray_tutorial run_demo.launch demo_id:=1 uav_id:=1 uav_name:=uav \
    > "${RESULT_DIR}/takeoff_hover_land_demo.log" 2>&1 || true
else
  sleep "${TOTAL_TIMEOUT_S}"
fi

python3 - "${RESULT_DIR}" <<'PY'
import json
import re
import sys
from pathlib import Path

result_dir = Path(sys.argv[1])
demo = (result_dir / "takeoff_hover_land_demo.log").read_text(encoding="utf-8", errors="ignore") if (result_dir / "takeoff_hover_land_demo.log").exists() else ""
sim = (result_dir / "sunray_sim.log").read_text(encoding="utf-8", errors="ignore") if (result_dir / "sunray_sim.log").exists() else ""
fmt = (result_dir / "fmt_control.log").read_text(encoding="utf-8", errors="ignore") if (result_dir / "fmt_control.log").exists() else ""

uav_jsonl = result_dir / "uav_state.jsonl"
raws = []
if uav_jsonl.exists():
    for line in uav_jsonl.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            raws.append(json.loads(line)["raw"])
        except Exception:
            pass

z_values = []
armed_seen = False
landed_seen = False
for raw in raws:
    if "armed: True" in raw:
        armed_seen = True
    if re.search(r"landed_state:\s+1\b", raw):
        landed_seen = True
    m = re.search(r"position:\s*\n-\s*([-+0-9.eE]+)\s*\n-\s*([-+0-9.eE]+)\s*\n-\s*([-+0-9.eE]+)", raw)
    if not m:
        m = re.search(
            r"position:\s*\[\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*\]",
            raw,
        )
    if m:
        z_values.append(float(m.group(3)))

max_z = max(z_values) if z_values else None
final_z = z_values[-1] if z_values else None

spawn_ok = "SpawnModel: Successfully spawned entity" in sim
heartbeat_ok = "Got HEARTBEAT" in sim or (result_dir / "mavros_state_first.txt").read_text(encoding="utf-8", errors="ignore").find("connected: True") >= 0
demo_finished = "Demo finished" in demo or "Demo 结束" in demo
takeoff_logged = "Takeoff UAV successfully" in demo or "Takeoff UAV now" in demo or "Takeoff cmd received" in fmt
land_logged = "Land UAV successfully" in demo or "Land UAV now" in demo

status = "passed" if (spawn_ok and heartbeat_ok and takeoff_logged and land_logged and max_z is not None and max_z > 0.45 and final_z is not None and final_z < 0.35) else "blocked_or_incomplete"
reason = "upstream Sunray default stack takeoff-hover-land evidence collected" if status == "passed" else "missing one or more startup/flight/landing evidence checks"
payload = {
    "schema": "mosim.sunray_ros1_default_stack_gate.v1",
    "status": status,
    "reason": reason,
    "spawn_ok": spawn_ok,
    "heartbeat_ok": heartbeat_ok,
    "demo_finished": demo_finished,
    "takeoff_logged": takeoff_logged,
    "land_logged": land_logged,
    "armed_seen": armed_seen,
    "landed_seen": landed_seen,
    "max_z_m": max_z,
    "final_z_m": final_z,
    "sample_count_uav_state": len(raws),
    "result_dir": str(result_dir),
    "logs": {
        "sunray_sim": str(result_dir / "sunray_sim.log"),
        "fmt_external_fusion": str(result_dir / "fmt_external_fusion.log"),
        "fmt_control": str(result_dir / "fmt_control.log"),
        "takeoff_hover_land_demo": str(result_dir / "takeoff_hover_land_demo.log"),
        "uav_state": str(result_dir / "uav_state.jsonl"),
        "model_states": str(result_dir / "model_states.jsonl"),
    },
    "claim_boundary": [
        "This gate proves only the upstream Sunray ROS1/PX4/Gazebo single-UAV default stack and demo path.",
        "It does not prove MoSim/MWORKS controller deployment, ROS2/GZ/x500, EGO planning, or final competition performance.",
    ],
}
(result_dir / "SUNRAY_ROS1_DEFAULT_STACK_GATE.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False, indent=2))
PY
