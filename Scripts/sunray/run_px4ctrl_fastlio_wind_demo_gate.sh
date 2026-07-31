#!/usr/bin/env bash
# Reproduce the source-local graphical-C99 wind-injection demonstration.

set -euo pipefail

if [[ "$#" -ne 0 ]]; then
  echo "Usage: $0" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
RUN_ID="${RUN_ID:-sunray_ros1_graphical_c99_wind_hover_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
FORCE_N="${C99_WIND_FORCE_N:-0.8}"
DIRECTION_DEG="${C99_WIND_DIRECTION_DEG:-35}"
DURATION_S="${C99_WIND_DURATION_S:-8}"
MINIMUM_ALTITUDE_M="${C99_WIND_MINIMUM_ALTITUDE_M:-0.95}"
AIRBORNE_TIMEOUT_S="${C99_WIND_AIRBORNE_TIMEOUT_S:-90}"
RUNTIME_LOCK_DIR="${PROJECT_ROOT}/Results/sunray_ros1/.sunray_ros1_runtime.lock"

mkdir -p "${RESULT_DIR}"

BASIC_PID=""

cleanup() {
  local exit_code=$?
  set +e
  if [[ -n "${BASIC_PID}" ]] && kill -0 "${BASIC_PID}" 2>/dev/null; then
    kill -INT "${BASIC_PID}" 2>/dev/null || true
    wait "${BASIC_PID}" 2>/dev/null || true
  fi
  return "${exit_code}"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

{
  echo "schema=mosim.sunray_ros1.graphical_c99_wind_demo_command.v1"
  echo "operation_selector=factory_l2_graphical_c99_wind_hover"
  echo "run_id=${RUN_ID}"
  echo "result_dir=${RESULT_DIR}"
  echo "controller_authority=px4ctrl_only"
  echo "controller_core_profile=graphical_c99"
  echo "controller_build_backend=graphical_px4ctrl_c99"
  echo "state_chain=fastlio_to_px4_ekf_to_mavros_local_odom"
  echo "wind_force_n=${FORCE_N}"
  echo "wind_direction_deg=${DIRECTION_DEG}"
  echo "wind_duration_s=${DURATION_S}"
  echo "fastlio_filter_size_surf_m=0.5"
  echo "fastlio_filter_size_map_m=0.5"
  echo "qgc_display_bridge=false"
  echo "ue_state_stream=false"
  echo "rviz=false"
} > "${RESULT_DIR}/DEMO_COMMAND.txt"

set +u
source /opt/ros/noetic/setup.bash
source "${PROJECT_ROOT}/Scripts/sunray/resolve_local_ros1_runtime.sh"
source "${LOCAL_ROS1_WS}/devel/setup.bash"
set -u

env \
  RUN_ID="${RUN_ID}" \
  RESULT_DIR="${RESULT_DIR}" \
  PX4CTRL_CORE_PROFILE=graphical_c99 \
  PX4CTRL_EXPECTED_BUILD_BACKEND=graphical_px4ctrl_c99 \
  FASTLIO_FILTER_SIZE_SURF=0.5 \
  FASTLIO_FILTER_SIZE_MAP=0.5 \
  GUI=false \
  REVIEW_OPEN_RVIZ=false \
  REVIEW_START_CLOUD_NODE=false \
  REVIEW_START_OCCUPANCY_NODE=false \
  MOSIM_UE_STATE_STREAM=false \
  bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_fastlio_hover_gate.sh" \
  > "${RESULT_DIR}/basic_gate_runner.log" 2>&1 &
BASIC_PID=$!

MASTER_READY=false
for _ in $(seq 1 360); do
  if ! kill -0 "${BASIC_PID}" 2>/dev/null; then
    break
  fi
  if [[ -f "${RUNTIME_LOCK_DIR}/run_id" && "$(<"${RUNTIME_LOCK_DIR}/run_id")" == "${RUN_ID}" ]] \
      && rosparam get /rosversion >/dev/null 2>&1; then
    MASTER_READY=true
    break
  fi
  sleep 0.5
done

if [[ "${MASTER_READY}" != "true" ]]; then
  set +e
  wait "${BASIC_PID}"
  BASIC_EXIT_CODE=$?
  set -e
  BASIC_PID=""
  python3 - "${RESULT_DIR}" "${RUN_ID}" "${BASIC_EXIT_CODE}" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
payload = {
    "schema": "mosim.sunray_ros1.graphical_c99_wind_demo_status.v1",
    "run_id": sys.argv[2],
    "status": "blocked",
    "reason": "ros_master_not_ready_before_wind_injection",
    "basic_gate_exit_code": int(sys.argv[3]),
    "claim_boundary": "No wind wrench was published because the source-local C99 runtime did not become ready.",
}
(root / "DEMO_STATUS.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY
  exit 4
fi

set +e
python3 "${PROJECT_ROOT}/Scripts/sunray/apply_p9_learning_wind_wrench.py" \
  --result-dir "${RESULT_DIR}" \
  --force-n "${FORCE_N}" \
  --direction-deg "${DIRECTION_DEG}" \
  --duration-s "${DURATION_S}" \
  --minimum-altitude-m "${MINIMUM_ALTITUDE_M}" \
  --airborne-timeout-s "${AIRBORNE_TIMEOUT_S}" \
  > "${RESULT_DIR}/wind_injector.log" 2>&1
INJECTOR_EXIT_CODE=$?
wait "${BASIC_PID}"
BASIC_EXIT_CODE=$?
set -e
BASIC_PID=""

python3 - "${RESULT_DIR}" "${RUN_ID}" "${BASIC_EXIT_CODE}" "${INJECTOR_EXIT_CODE}" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
run_id = sys.argv[2]
basic_exit_code = int(sys.argv[3])
injector_exit_code = int(sys.argv[4])

def read_json(name: str) -> dict:
    try:
        return json.loads((root / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

mission = read_json("PX4CTRL_BASIC_MISSION_METRICS.json")
wind = read_json("WIND_INJECTION_EVIDENCE.json")
lifecycle = mission.get("active_gate") or mission.get("operational_lifecycle_gate") or {}
mission_passed = basic_exit_code == 0 and mission.get("status") == "passed"
wind_passed = injector_exit_code == 0 and wind.get("status") == "passed"
payload = {
    "schema": "mosim.sunray_ros1.graphical_c99_wind_demo_status.v1",
    "run_id": run_id,
    "status": "passed" if mission_passed and wind_passed else "blocked",
    "reason": None if mission_passed and wind_passed else "mission_or_wind_injection_failed",
    "functional_lifecycle": lifecycle,
    "wind_injection": wind,
    "basic_gate_exit_code": basic_exit_code,
    "injector_exit_code": injector_exit_code,
    "quality_observation": {
        "formal_performance_gate": mission.get("formal_performance_gate"),
        "policy": "Lifecycle and injection acknowledgement do not upgrade the formal controller-performance result.",
    },
    "claim_boundary": "This gate proves a source-local graphical-C99 lifecycle and bounded Gazebo wind-wrench acknowledgement. It is not a strict same-parameter robustness comparison or a fault-tolerance claim.",
}
(root / "DEMO_STATUS.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY

if [[ "${BASIC_EXIT_CODE}" -ne 0 || "${INJECTOR_EXIT_CODE}" -ne 0 ]]; then
  exit 1
fi
