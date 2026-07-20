#!/usr/bin/env bash
# Start and verify the Sunray ROS1/PX4/MAVROS/Gazebo/MID360 foundation without flight control.

set -uo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-/opt/mosim_work/sunray_ws/Sunray}"
SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR:-/opt/mosim_work/sunray_px4}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/sunray_livox_plugin_ws}"
RUN_ID="${RUN_ID:-sunray_ros1_foundation_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
MODE="${MODE:-check}"
GUI="${GUI:-false}"
AUTO_BUILD_LIVOX="${AUTO_BUILD_LIVOX:-true}"
CLEAN_EXISTING="${CLEAN_EXISTING:-false}"
MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-90}"
MID360_READY_TIMEOUT_S="${MID360_READY_TIMEOUT_S:-120}"
CHECK_HOLD_S="${CHECK_HOLD_S:-35}"
WORLD_FILE="${WORLD_FILE:-${SUNRAY_WS}/simulation/sunray_simulator/worlds/planning_test.world}"
FOUNDATION_LAUNCH_FILE="${FOUNDATION_LAUNCH_FILE:-${PROJECT_ROOT}/Scripts/sunray/sunray_sim_uav_planning_foundation.launch}"
VEHICLE="${VEHICLE:-sunray150_with_mid360}"
SUNRAY_UAV_INIT_X="${SUNRAY_UAV_INIT_X:-1.0}"
SUNRAY_UAV_INIT_Y="${SUNRAY_UAV_INIT_Y:-1.0}"
SUNRAY_UAV_INIT_Z="${SUNRAY_UAV_INIT_Z:-0.2}"
SUNRAY_UAV_INIT_YAW="${SUNRAY_UAV_INIT_YAW:-0.0}"

usage() {
  cat <<'EOF'
Usage: bash Scripts/sunray/run_sunray_ros1_foundation_gate.sh [options]

Starts only the Sunray ROS1/PX4 SITL/MAVROS/Gazebo/MID360 runtime. It never
starts px4ctrl, external fusion, or a mission node, and it never publishes
arming or trajectory setpoints.

Options:
  --review              Keep the verified ground runtime alive until Ctrl-C.
  --gui                 Open Gazebo Classic GUI (requires WSLg/X11 support).
  --headless            Run Gazebo without its GUI (default).
  --clean-existing      Explicitly stop a previous Sunray ROS1 runtime first.
  --no-build-livox      Fail if the project-local Livox plugin is missing.
  --help                Show this help.

Artifacts are written under Results/sunray_ros1/<run_id>/. Read STATUS.md
first; it links to the relevant log and compact MID360 evidence.
EOF
}

for arg in "$@"; do
  case "${arg}" in
    --review) MODE="review" ;;
    --gui) GUI="true" ;;
    --headless) GUI="false" ;;
    --clean-existing) CLEAN_EXISTING="true" ;;
    --no-build-livox) AUTO_BUILD_LIVOX="false" ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: ${arg}" >&2; usage >&2; exit 2 ;;
  esac
done

mkdir -p "${RESULT_DIR}"

write_status() {
  local status="$1"
  local classification="$2"
  local message="$3"
  python3 - "${RESULT_DIR}" "${RUN_ID}" "${MODE}" "${GUI}" "${status}" "${classification}" "${message}" <<'PY'
import json
import pathlib
import sys
from datetime import datetime, timezone

result_dir = pathlib.Path(sys.argv[1])
run_id, mode, gui, status, classification, message = sys.argv[2:]
payload = {
    "schema": "mosim.sunray_ros1_foundation_gate.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "run_id": run_id,
    "mode": mode,
    "gui": gui,
    "status": status,
    "classification": classification,
    "message": message,
    "result_dir": str(result_dir),
    "no_flight_contract": {
        "px4ctrl_started": False,
        "external_fusion_started": False,
        "mission_started": False,
        "arming_or_setpoint_publisher_started": False,
    },
    "artifacts": {
        "preflight": str(result_dir / "sunray_ros1_preflight.log"),
        "launcher": str(result_dir / "foundation_launcher.log"),
        "gazebo": str(result_dir / "sunray_gazebo.log"),
        "mavros_state": str(result_dir / "mavros_state_first.txt"),
        "mid360": str(result_dir / "mid360_lidar_ready.json"),
        "failure_excerpt": str(result_dir / "failure_excerpt.txt"),
    },
}
(result_dir / "FOUNDATION_STATUS.json").write_text(
    json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8"
)
(result_dir / "STATUS.md").write_text(
    "# Sunray ROS1 Foundation\n\n"
    f"- status: `{status}`\n"
    f"- classification: `{classification}`\n"
    f"- message: {message}\n"
    f"- run id: `{run_id}`\n"
    f"- mode: `{mode}`\n"
    f"- Gazebo GUI: `{gui}`\n"
    "- flight control: `disabled` (`px4ctrl`, external fusion, and mission publishing are off)\n"
    f"- preflight: `{result_dir / 'sunray_ros1_preflight.log'}`\n"
    f"- launcher: `{result_dir / 'foundation_launcher.log'}`\n"
    f"- Gazebo: `{result_dir / 'sunray_gazebo.log'}`\n"
    f"- MAVROS: `{result_dir / 'mavros_state_first.txt'}`\n"
    f"- MID360 evidence: `{result_dir / 'mid360_lidar_ready.json'}`\n"
    f"- error excerpt: `{result_dir / 'failure_excerpt.txt'}`\n",
    encoding="utf-8",
)
PY
}

write_failure_excerpt() {
  : > "${RESULT_DIR}/failure_excerpt.txt"
  for file in \
    "${RESULT_DIR}/sunray_ros1_preflight.log" \
    "${RESULT_DIR}/foundation_launcher.log" \
    "${RESULT_DIR}/sunray_gazebo.log" \
    "${RESULT_DIR}/mid360_lidar_ready.json"; do
    if [[ -f "${file}" ]]; then
      {
        echo "===== ${file##*/} ====="
        tail -n 80 "${file}"
        echo
      } >> "${RESULT_DIR}/failure_excerpt.txt"
    fi
  done
}

fail() {
  local classification="$1"
  local message="$2"
  write_failure_excerpt
  write_status "failed" "${classification}" "${message}"
  echo "SUNRAY_ROS1_FOUNDATION=FAILED ${classification}: ${message}" >&2
  echo "Read ${RESULT_DIR}/STATUS.md and ${RESULT_DIR}/failure_excerpt.txt" >&2
  exit 1
}

if [[ "${MODE}" != "check" && "${MODE}" != "review" ]]; then
  fail "argument_blocker" "MODE must be check or review, got ${MODE}"
fi
if [[ ! -d "${PROJECT_ROOT}" ]]; then
  fail "preflight_blocker" "PROJECT_ROOT is missing: ${PROJECT_ROOT}"
fi
if [[ ! -f "${FOUNDATION_LAUNCH_FILE}" ]]; then
  fail "preflight_blocker" "Foundation launch file is missing: ${FOUNDATION_LAUNCH_FILE}"
fi
if [[ ! -d "${PX4CTRL_WS}/devel" ]]; then
  fail "preflight_blocker" "PX4CTRL workspace devel directory is missing: ${PX4CTRL_WS}/devel"
fi

PREFLIGHT_ARGS=()
if [[ "${AUTO_BUILD_LIVOX}" == "true" ]]; then
  PREFLIGHT_ARGS+=(--build-livox)
fi
if ! PROJECT_ROOT="${PROJECT_ROOT}" \
  SUNRAY_WS="${SUNRAY_WS}" \
  SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR}" \
  LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS}" \
  bash "${PROJECT_ROOT}/Scripts/sunray/check_sunray_ros1_runtime_preflight.sh" "${PREFLIGHT_ARGS[@]}" \
  > "${RESULT_DIR}/sunray_ros1_preflight.log" 2>&1; then
  fail "preflight_blocker" "Runtime dependency preflight failed"
fi

active_runtime_processes() {
  # Match the executable column so this check cannot mistake its own matcher
  # command line for a live PX4 process.
  ps -eo pid=,ppid=,comm=,args= | awk '
    $3 ~ /^(rosmaster|rosout|gzserver|gzclient|mavros_node)$/ { print; next }
    $3 == "roslaunch" && $0 ~ /sunray/ { print; next }
    $3 == "px4" && $0 ~ /(sunray_px4|px4_ros1_runtime_overlay)/ { print; next }
  '
}

clean_existing_runtime() {
  pkill -f 'roslaunch .*sunray_sim_uav' >/dev/null 2>&1 || true
  pkill -f 'roslaunch .*sunray_uav_control' >/dev/null 2>&1 || true
  pkill -f 'mosim_mavros_pose_velocity_to_odom_bridge' >/dev/null 2>&1 || true
  pkill -f 'px4ctrl_node' >/dev/null 2>&1 || true
  pkill -f 'gzserver' >/dev/null 2>&1 || true
  pkill -f 'gzclient' >/dev/null 2>&1 || true
  pkill -f 'mavros_node' >/dev/null 2>&1 || true
  pkill -f '/opt/mosim_work/sunray_px4.*/px4' >/dev/null 2>&1 || true
  pkill -f 'px4_ros1_runtime_overlay_.*px4' >/dev/null 2>&1 || true
  pkill -f 'rosmaster' >/dev/null 2>&1 || true
  pkill -f 'rosout' >/dev/null 2>&1 || true
  sleep 3
}

if [[ -n "$(active_runtime_processes)" ]]; then
  if [[ "${CLEAN_EXISTING}" == "true" ]]; then
    clean_existing_runtime
  else
    active_runtime_processes > "${RESULT_DIR}/active_runtime_processes.txt"
    fail "runtime_busy" "A Sunray ROS1/Gazebo/PX4 process is already active; rerun with --clean-existing only after confirming it is safe to stop"
  fi
fi
if [[ -n "$(active_runtime_processes)" ]]; then
  active_runtime_processes > "${RESULT_DIR}/active_runtime_processes.txt"
  fail "runtime_cleanup_blocker" "Existing Sunray ROS1/Gazebo/PX4 processes remained after requested cleanup"
fi

source "${PROJECT_ROOT}/Scripts/sunray/sunray_ros1_runtime_lock.sh"
if ! sunray_ros1_runtime_lock_acquire; then
  fail "runtime_busy" "The shared Sunray ROS1 runtime lock is held by another managed run"
fi

INNER_PID=""
SENSOR_GATE_PID=""
cleanup() {
  set +e
  if [[ -n "${SENSOR_GATE_PID}" ]] && kill -0 "${SENSOR_GATE_PID}" >/dev/null 2>&1; then
    kill "${SENSOR_GATE_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${INNER_PID}" ]] && kill -0 "${INNER_PID}" >/dev/null 2>&1; then
    kill "${INNER_PID}" >/dev/null 2>&1 || true
    wait "${INNER_PID}" >/dev/null 2>&1 || true
  fi
  sunray_ros1_runtime_lock_release
}

stop_review() {
  local reason="$1"
  if [[ "${MODE}" == "review" ]]; then
    write_status "stopped" "review_ended" "Ground runtime stopped (${reason})"
    exit 0
  fi
  exit 130
}

trap cleanup EXIT
trap 'stop_review "interrupt"' INT
trap 'stop_review "termination"' TERM

if [[ "${MODE}" == "review" ]]; then
  NO_FLIGHT_DIAGNOSTIC_HOLD_S="until_stopped"
else
  NO_FLIGHT_DIAGNOSTIC_HOLD_S="${CHECK_HOLD_S}"
fi

echo "Sunray ROS1 foundation starting: mode=${MODE}, gui=${GUI}, result_dir=${RESULT_DIR}"
echo "Safety contract: px4ctrl=false, external_fusion=false, mission=false."

(
  cd "${PROJECT_ROOT}"
  PROJECT_ROOT="${PROJECT_ROOT}" \
  SUNRAY_WS="${SUNRAY_WS}" \
  SUNRAY_PX4_DIR="${SUNRAY_PX4_DIR}" \
  PX4CTRL_WS="${PX4CTRL_WS}" \
  LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS}" \
  RUN_ID="${RUN_ID}" \
  RESULT_DIR="${RESULT_DIR}" \
  GUI="${GUI}" \
  WORLD_FILE="${WORLD_FILE}" \
  SUNRAY_GAZEBO_LAUNCH_FILE="${FOUNDATION_LAUNCH_FILE}" \
  VEHICLE="${VEHICLE}" \
  SUNRAY_UAV_INIT_X="${SUNRAY_UAV_INIT_X}" \
  SUNRAY_UAV_INIT_Y="${SUNRAY_UAV_INIT_Y}" \
  SUNRAY_UAV_INIT_Z="${SUNRAY_UAV_INIT_Z}" \
  SUNRAY_UAV_INIT_YAW="${SUNRAY_UAV_INIT_YAW}" \
  USE_SIM_TIME=true \
  PX4CTRL_START_CONTROLLER=false \
  PX4CTRL_START_EXTERNAL_FUSION=false \
  PX4CTRL_SKIP_MISSION=true \
  PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=false \
  REVIEW_START_FASTLIO=false \
  REVIEW_START_CLOUD_NODE=false \
  REVIEW_OPEN_RVIZ=false \
  REVIEW_START_OCCUPANCY_NODE=false \
  MAVROS_STREAM_RATE_HZ=0 \
  FREQUENCY_AUDIT_DURATION_S=0 \
  CONTROL_DIAGNOSTICS_DURATION_S=0 \
  TIME_TF_AUDIT_DURATION_S=0 \
  GOAL3_FUSION_AUDIT_DURATION_S=0 \
  POST_MISSION_DIAGNOSTIC_GRACE_S=0 \
  MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S}" \
  NO_FLIGHT_DIAGNOSTIC_HOLD_S="${NO_FLIGHT_DIAGNOSTIC_HOLD_S}" \
  KEEP_ALIVE=false \
  bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh"
) > "${RESULT_DIR}/foundation_launcher.log" 2>&1 &
INNER_PID="$!"

(
  # ROS Noetic's setup fragments read optional variables before defining them.
  set +u
  source /opt/ros/noetic/setup.bash
  python3 "${PROJECT_ROOT}/Scripts/sunray/wait_for_nonempty_pointcloud2.py" \
    --topic /uav1/livox/lidar \
    --timeout-s "${MID360_READY_TIMEOUT_S}" \
    --output "${RESULT_DIR}/mid360_lidar_ready.json"
) > "${RESULT_DIR}/mid360_sensor_gate.log" 2>&1 &
SENSOR_GATE_PID="$!"

INNER_EXIT=""
SENSOR_EXIT=""
while :; do
  if [[ -z "${INNER_EXIT}" ]] && ! kill -0 "${INNER_PID}" >/dev/null 2>&1; then
    wait "${INNER_PID}"
    INNER_EXIT="$?"
  fi
  if [[ -z "${SENSOR_EXIT}" ]] && ! kill -0 "${SENSOR_GATE_PID}" >/dev/null 2>&1; then
    wait "${SENSOR_GATE_PID}"
    SENSOR_EXIT="$?"
  fi

  if [[ -n "${INNER_EXIT}" && -z "${SENSOR_EXIT}" ]]; then
    kill "${SENSOR_GATE_PID}" >/dev/null 2>&1 || true
    wait "${SENSOR_GATE_PID}" >/dev/null 2>&1 || true
    SENSOR_EXIT=143
  fi

  if [[ -n "${SENSOR_EXIT}" ]]; then
    break
  fi
  sleep 0.2
done

if [[ "${SENSOR_EXIT}" != "0" ]]; then
  if [[ -n "${INNER_EXIT}" && "${SENSOR_EXIT}" == "143" && "${INNER_EXIT}" != "143" ]]; then
    fail "runtime_exited" "Foundation launcher exited with code ${INNER_EXIT} before MID360 evidence was available"
  fi
  if [[ -z "${INNER_EXIT}" ]]; then
    kill "${INNER_PID}" >/dev/null 2>&1 || true
    wait "${INNER_PID}" >/dev/null 2>&1 || true
    INNER_EXIT=143
  fi
  fail "mid360_sensor_blocker" "MID360 topic /uav1/livox/lidar did not publish a nonempty PointCloud2 sample before ${MID360_READY_TIMEOUT_S}s"
fi

if [[ "${MODE}" == "review" ]]; then
  write_status "ready" "runtime_ready" "MAVROS and a nonempty MID360 PointCloud2 are live; press Ctrl-C in this terminal to stop the ground runtime"
  echo "SUNRAY_ROS1_FOUNDATION=READY"
  echo "MAVROS and MID360 are live. Press Ctrl-C here to stop all runtime processes."
  wait "${INNER_PID}"
  INNER_EXIT="$?"
  if [[ "${INNER_EXIT}" -eq 0 || "${INNER_EXIT}" -eq 130 || "${INNER_EXIT}" -eq 143 ]]; then
    write_status "stopped" "review_ended" "Ground runtime stopped"
    exit 0
  fi
  fail "runtime_exited" "Foundation launcher exited unexpectedly with code ${INNER_EXIT} after reaching ready state"
fi

if [[ -z "${INNER_EXIT}" ]]; then
  wait "${INNER_PID}"
  INNER_EXIT="$?"
fi
if [[ "${INNER_EXIT}" -ne 0 ]]; then
  fail "runtime_exited" "Foundation launcher exited with code ${INNER_EXIT} after MID360 became available"
fi

write_status "passed" "foundation_ready" "MAVROS and a nonempty MID360 PointCloud2 passed in a no-flight startup check"
echo "SUNRAY_ROS1_FOUNDATION=PASS"
echo "Read ${RESULT_DIR}/STATUS.md"
