#!/usr/bin/env bash
# Prove the project-local GPS -> PX4 EKF -> MAVROS state chain without flight.

set -uo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-/opt/mosim_work/sunray_px4}"
RUN_ID="${RUN_ID:-sunray_ros1_gps_state_chain_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-$PROJECT_ROOT/Results/sunray_ros1/$RUN_ID}"
BOOT_HOLD_S="${BOOT_HOLD_S:-110}"
CAPTURE_DURATION_S="${CAPTURE_DURATION_S:-90}"
ROS_MASTER_TIMEOUT_S="${ROS_MASTER_TIMEOUT_S:-90}"
SUNRAY_RUNTIME_ROS_HOME="${SUNRAY_RUNTIME_ROS_HOME:-$RESULT_DIR/ros_home}"
PX4_ULOG_SEARCH_ROOT="${PX4_ULOG_SEARCH_ROOT:-$SUNRAY_RUNTIME_ROS_HOME}"

usage() {
  cat <<'EOF'
Usage: bash Scripts/sunray/run_sunray_gps_state_chain_gate.sh

Runs a bounded, unarmed GPS/EKF state-chain check on the declared ROS1 Sunray
runtime. It never starts px4ctrl, external fusion, an arming publisher, or a
mission node. The result directory contains raw ROS samples, a rosbag, MAVROS
parameter evidence, a PX4 ULog analysis, and GPS_STATE_CHAIN_STATUS.json.

If another Sunray/PX4/Gazebo run is already active, stop it with its owning
entrypoint before running this gate. This script never kills an unknown run.
EOF
}

if [[ "$#" -gt 0 ]]; then
  if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    usage
    exit 0
  fi
  echo "Unknown option: $1" >&2
  usage >&2
  exit 2
fi

mkdir -p "$RESULT_DIR" "$SUNRAY_RUNTIME_ROS_HOME"
BASE_PID=""
COLLECTOR_PID=""
BAG_PID=""

capture_mavros_effective_state() {
  (
    set +u
    source /opt/ros/noetic/setup.bash
    echo "# MAVROS effective state captured after passive GPS/EKF collection"
    echo "## plugin_blacklist"
    rosparam get /uav1/mavros/plugin_blacklist || true
    echo "## plugin_whitelist"
    rosparam get /uav1/mavros/plugin_whitelist || true
    echo "## mavros_node"
    rosnode info /uav1/mavros || true
    echo "## home_position_topic"
    rostopic info /uav1/mavros/home_position/home || true
  ) > "$RESULT_DIR/mavros_effective_state.txt" 2>&1 || true
}

stop_bag() {
  if [[ -n "$BAG_PID" ]] && kill -0 "$BAG_PID" >/dev/null 2>&1; then
    kill -INT "$BAG_PID" >/dev/null 2>&1 || true
    for _ in $(seq 1 30); do
      kill -0 "$BAG_PID" >/dev/null 2>&1 || break
      sleep 0.1
    done
    kill -TERM "$BAG_PID" >/dev/null 2>&1 || true
    wait "$BAG_PID" >/dev/null 2>&1 || true
  fi
  BAG_PID=""
}

cleanup() {
  set +e
  stop_bag
  if [[ -n "$COLLECTOR_PID" ]] && kill -0 "$COLLECTOR_PID" >/dev/null 2>&1; then
    kill -TERM "$COLLECTOR_PID" >/dev/null 2>&1 || true
    wait "$COLLECTOR_PID" >/dev/null 2>&1 || true
  fi
  if [[ -n "$BASE_PID" ]] && kill -0 "$BASE_PID" >/dev/null 2>&1; then
    kill -TERM "$BASE_PID" >/dev/null 2>&1 || true
    wait "$BASE_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

write_status() {
  local status="$1"
  local message="$2"
  local launcher_exit="${3:-null}"
  local collector_exit="${4:-null}"
  local ulog_exit="${5:-null}"
  local contract_exit="${6:-null}"
  python3 - "$RESULT_DIR" "$RUN_ID" "$status" "$message" "$launcher_exit" "$collector_exit" "$ulog_exit" "$contract_exit" "$SUNRAY_RUNTIME_ROS_HOME" "$PX4_ULOG_SEARCH_ROOT" <<'PY'
import json
import pathlib
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
run_id, status, message, launcher, collector, ulog, contract, ros_home, ulog_search_root = sys.argv[2:]

def parse_exit(value):
    return None if value == "null" else int(value)

payload = {
    "schema": "mosim.sunray_ros1.gps_state_chain_gate.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "run_id": run_id,
    "status": status,
    "message": message,
    "no_flight_contract": {
        "controller_started": False,
        "external_fusion_started": False,
        "mission_started": False,
        "arming_or_setpoint_publisher_started": False,
    },
    "frozen_boot_parameters": {
        "EKF2_GPS_CTRL": 7,
        "EKF2_HGT_REF": 1,
        "EKF2_EV_CTRL": 0,
    },
    "exit_codes": {
        "launcher": parse_exit(launcher),
        "collector": parse_exit(collector),
        "ulog_analysis": parse_exit(ulog),
        "manifest_contract": parse_exit(contract),
    },
    "runtime_paths": {
        "ros_home": ros_home,
        "px4_ulog_search_root": ulog_search_root,
    },
    "artifacts": {
        "preflight": str(result_dir / "sunray_ros1_preflight.log"),
        "launcher": str(result_dir / "gps_state_chain_launcher.log"),
        "capture": str(result_dir / "GPS_STATE_CHAIN_CAPTURE.json"),
        "samples": str(result_dir / "GPS_STATE_CHAIN_CAPTURE.jsonl"),
        "rosbag": str(result_dir / "gps_state_chain.bag"),
        "px4_parameters": str(result_dir / "px4_param_snapshot_before_mission.txt"),
        "mavros_effective_state": str(result_dir / "mavros_effective_state.txt"),
        "px4_ulog": str(result_dir / "PX4_GPS_STATE_CHAIN_ULOG.json"),
        "no_flight_manifest": str(result_dir / "NO_FLIGHT_CONTRACT.json"),
    },
}
(result_dir / "GPS_STATE_CHAIN_STATUS.json").write_text(
    json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8"
)
(result_dir / "STATUS.md").write_text(
    "# GPS/EKF State Chain Gate\n\n"
    f"- status: {status}\n"
    f"- message: {message}\n"
    f"- run id: {run_id}\n"
    "- flight control: disabled (no px4ctrl, external fusion, arming, or mission publisher)\n"
    f"- capture: {result_dir / 'GPS_STATE_CHAIN_CAPTURE.json'}\n"
    f"- PX4 ULog analysis: {result_dir / 'PX4_GPS_STATE_CHAIN_ULOG.json'}\n"
    f"- PX4 parameters: {result_dir / 'px4_param_snapshot_before_mission.txt'}\n"
    f"- no-flight contract: {result_dir / 'NO_FLIGHT_CONTRACT.json'}\n",
    encoding="utf-8",
)
PY
}

if ! PROJECT_ROOT="$PROJECT_ROOT" bash "$PROJECT_ROOT/Scripts/sunray/check_sunray_ros1_runtime_preflight.sh" > "$RESULT_DIR/sunray_ros1_preflight.log" 2>&1; then
  write_status "blocked" "Runtime dependency preflight failed"
  echo "GPS_STATE_CHAIN=BLOCKED preflight" >&2
  exit 2
fi
ULOG_MARKER="$RESULT_DIR/px4_ulog_start.marker"
touch "$ULOG_MARKER"

(
  cd "$PROJECT_ROOT"
  PROJECT_ROOT="$PROJECT_ROOT"   SUNRAY_PX4_DIR="$SUNRAY_PX4_DIR"   RUN_ID="$RUN_ID"   RESULT_DIR="$RESULT_DIR"   MOSIM_RUNTIME_ROS_HOME="$SUNRAY_RUNTIME_ROS_HOME"   GUI=false   SUNRAY_GPS_SENSOR_MODE=nested   SUNRAY_STRIP_PX4_MODEL_PATH=true   PX4CTRL_BOOT_PARAM_OVERRIDES="EKF2_GPS_CTRL=7,EKF2_HGT_REF=1,EKF2_EV_CTRL=0"   PX4CTRL_START_CONTROLLER=false   PX4CTRL_START_EXTERNAL_FUSION=false   PX4CTRL_SKIP_MISSION=true   PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=false   PX4CTRL_SET_EKF_GLOBAL_ORIGIN=false   PX4CTRL_ODOM_SOURCE=mavros_local   REVIEW_START_FASTLIO=false   REVIEW_START_CLOUD_NODE=false   REVIEW_OPEN_RVIZ=false   REVIEW_START_OCCUPANCY_NODE=false   FREQUENCY_AUDIT_DURATION_S=0   CONTROL_DIAGNOSTICS_DURATION_S=0   TIME_TF_AUDIT_DURATION_S=0   GOAL3_FUSION_AUDIT_DURATION_S=0   POST_MISSION_DIAGNOSTIC_GRACE_S=0   NO_FLIGHT_DIAGNOSTIC_HOLD_S="$BOOT_HOLD_S"   KEEP_ALIVE=false   bash "$PROJECT_ROOT/Scripts/sunray/run_px4ctrl_basic_gate.sh" takeoff_hover_land
) > "$RESULT_DIR/gps_state_chain_launcher.log" 2>&1 &
BASE_PID="$!"

ros_master_ready=false
deadline=$((SECONDS + ROS_MASTER_TIMEOUT_S))
while (( SECONDS < deadline )); do
  if ! kill -0 "$BASE_PID" >/dev/null 2>&1; then
    break
  fi
  if bash -lc 'source /opt/ros/noetic/setup.bash; rosnode list >/dev/null 2>&1'; then
    ros_master_ready=true
    break
  fi
  sleep 1
done

if [[ "$ros_master_ready" != "true" ]]; then
  wait "$BASE_PID"
  launcher_exit="$?"
  BASE_PID=""
  write_status "blocked" "ROS master did not become available before launcher exit or timeout" "$launcher_exit"
  echo "GPS_STATE_CHAIN=BLOCKED ROS master" >&2
  exit 18
fi

(
  set +u
  source /opt/ros/noetic/setup.bash
  python3 "$PROJECT_ROOT/Scripts/sunray/collect_sunray_gps_state_chain.py"     --output "$RESULT_DIR/GPS_STATE_CHAIN_CAPTURE.json"     --duration-s "$CAPTURE_DURATION_S"     --post-connect-settle-s 10
) > "$RESULT_DIR/gps_state_chain_collector.log" 2>&1 &
COLLECTOR_PID="$!"

(
  set +u
  source /opt/ros/noetic/setup.bash
  exec rosbag record --lz4 -O "$RESULT_DIR/gps_state_chain.bag"     /uav1/mavros/global_position/global     /uav1/mavros/home_position/home     /uav1/mavros/local_position/pose     /uav1/mavros/local_position/odom     /uav1/sunray/gazebo_pose     /uav1/mavros/state
) > "$RESULT_DIR/gps_state_chain_rosbag.log" 2>&1 &
BAG_PID="$!"

wait "$COLLECTOR_PID"
collector_exit="$?"
COLLECTOR_PID=""
capture_mavros_effective_state
stop_bag

wait "$BASE_PID"
launcher_exit="$?"
BASE_PID=""

mkdir -p "$RESULT_DIR/px4_ulog"
find "$PX4_ULOG_SEARCH_ROOT" -type f -name '*.ulg' -newer "$ULOG_MARKER" -print > "$RESULT_DIR/px4_ulog_candidates.txt" 2>/dev/null || true
ulog_exit=18
if [[ -s "$RESULT_DIR/px4_ulog_candidates.txt" ]]; then
  while IFS= read -r ulog_path; do
    cp -a "$ulog_path" "$RESULT_DIR/px4_ulog/"
  done < "$RESULT_DIR/px4_ulog_candidates.txt"
  newest_ulog="$(tail -n 1 "$RESULT_DIR/px4_ulog_candidates.txt")"
  python3 "$PROJECT_ROOT/Scripts/sunray/analyze_px4_gps_state_chain_ulog.py"     --ulog "$newest_ulog"     --output "$RESULT_DIR/PX4_GPS_STATE_CHAIN_ULOG.json"     --project-root "$PROJECT_ROOT"     > "$RESULT_DIR/px4_gps_state_chain_ulog.log" 2>&1
  ulog_exit="$?"
else
  python3 - "$RESULT_DIR/PX4_GPS_STATE_CHAIN_ULOG.json" <<'PY'
import json
import pathlib
import sys
path = pathlib.Path(sys.argv[1])
path.write_text(json.dumps({
    "schema": "mosim.sunray_ros1.px4_gps_state_chain_ulog.v1",
    "status": "blocked",
    "blockers": ["missing_new_px4_ulog"],
}, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
PY
fi

python3 - "$RESULT_DIR/RUN_MANIFEST.json" "$RESULT_DIR/NO_FLIGHT_CONTRACT.json" <<'PY'
import json
import pathlib
import sys

manifest_path = pathlib.Path(sys.argv[1])
output_path = pathlib.Path(sys.argv[2])
blockers = []
manifest = {}
if not manifest_path.is_file():
    blockers.append("missing_run_manifest")
else:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        blockers.append("run_manifest_parse_failed")
        manifest = {"error": repr(exc)}

px4ctrl = manifest.get("px4ctrl", {})
gazebo = manifest.get("gazebo", {})
if px4ctrl.get("controller_started") is not False:
    blockers.append("controller_started")
if str(px4ctrl.get("start_external_fusion")).lower() != "false":
    blockers.append("external_fusion_started")
if str(px4ctrl.get("skip_mission")).lower() != "true":
    blockers.append("mission_not_skipped")
if px4ctrl.get("gazebo_gps_sensor_mode") != "nested":
    blockers.append("gps_sensor_mode_not_nested")
boot = str(px4ctrl.get("px4_boot_param_overrides", ""))
for expected in ("EKF2_GPS_CTRL=7", "EKF2_HGT_REF=1", "EKF2_EV_CTRL=0"):
    if expected not in boot:
        blockers.append("missing_boot_override_" + expected.split("=", 1)[0])
if gazebo.get("strip_px4_model_path") != "true":
    blockers.append("px4_model_path_not_stripped")

payload = {
    "schema": "mosim.sunray_ros1.gps_state_chain_no_flight_contract.v1",
    "status": "passed" if not blockers else "blocked",
    "blockers": blockers,
    "manifest": str(manifest_path),
    "observed": {
        "controller_started": px4ctrl.get("controller_started"),
        "start_external_fusion": px4ctrl.get("start_external_fusion"),
        "skip_mission": px4ctrl.get("skip_mission"),
        "gps_sensor_mode": px4ctrl.get("gazebo_gps_sensor_mode"),
        "boot_param_overrides": boot,
        "strip_px4_model_path": gazebo.get("strip_px4_model_path"),
    },
}
output_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if not blockers else 18)
PY
contract_exit="$?"

if [[ "$launcher_exit" -eq 0 && "$collector_exit" -eq 0 && "$ulog_exit" -eq 0 && "$contract_exit" -eq 0 ]]; then
  write_status "passed" "Nested GPS, PX4 EKF, MAVROS, Gazebo truth, and ULog state-chain evidence passed"     "$launcher_exit" "$collector_exit" "$ulog_exit" "$contract_exit"
  echo "GPS_STATE_CHAIN=PASS"
  echo "Read $RESULT_DIR/GPS_STATE_CHAIN_STATUS.json"
  exit 0
fi

write_status "blocked" "One or more GPS/EKF state-chain evidence gates failed; inspect the per-artifact status"   "$launcher_exit" "$collector_exit" "$ulog_exit" "$contract_exit"
echo "GPS_STATE_CHAIN=BLOCKED" >&2
echo "Read $RESULT_DIR/GPS_STATE_CHAIN_STATUS.json and STATUS.md" >&2
exit 18
