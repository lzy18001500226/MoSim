#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
OPERATION_ID="${1:-}"
RUN_ID="${2:-}"

if [[ ! "${RUN_ID}" =~ ^run-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$ ]]; then
  echo "invalid run_id" >&2
  exit 2
fi
source "${PROJECT_ROOT}/Scripts/sunray/resolve_local_ros1_runtime.sh"

ORCHESTRATOR_RUN_DIR="${PROJECT_ROOT}/Results/ui_platform/orchestrator_runs/${RUN_ID}"
mkdir -p -- "${ORCHESTRATOR_RUN_DIR}"
printf '%s\n' "$$" > "${ORCHESTRATOR_RUN_DIR}/runtime_linux_pid.txt"

SIDECAR_PID=""
OBSERVABILITY_PID=""
HOST_OBSERVABILITY_PID=""
RUNTIME_CHILD_PID=""
RT1_PID=""
source "${PROJECT_ROOT}/Scripts/sunray/sunray_ros1_runtime_lock.sh"
cleanup() {
  set +e
  if [[ -n "${SIDECAR_PID}" ]]; then
    kill -TERM "${SIDECAR_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${OBSERVABILITY_PID}" ]]; then
    kill -TERM "${OBSERVABILITY_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${HOST_OBSERVABILITY_PID}" ]]; then
    kill -TERM "${HOST_OBSERVABILITY_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${RUNTIME_CHILD_PID}" ]]; then
    kill -TERM "${RUNTIME_CHILD_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${RT1_PID}" ]]; then
    kill -TERM "${RT1_PID}" >/dev/null 2>&1 || true
  fi
  wait "${SIDECAR_PID}" >/dev/null 2>&1 || true
  wait "${OBSERVABILITY_PID}" >/dev/null 2>&1 || true
  wait "${HOST_OBSERVABILITY_PID}" >/dev/null 2>&1 || true
  wait "${RUNTIME_CHILD_PID}" >/dev/null 2>&1 || true
  wait "${RT1_PID}" >/dev/null 2>&1 || true
  sunray_ros1_runtime_lock_release
}
trap cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT

assert_no_conflicting_runtime() {
  local conflicts=()
  pgrep -x gzserver >/dev/null 2>&1 && conflicts+=("gzserver")
  pgrep -f '[r]osmaster --core' >/dev/null 2>&1 && conflicts+=("rosmaster")
  pgrep -f '/bin/[p]x4 ' >/dev/null 2>&1 && conflicts+=("px4")
  pgrep -f '[m]avros/mavros_node' >/dev/null 2>&1 && conflicts+=("mavros")
  pgrep -f '[r]un_px4ctrl_(basic|ego_swarm)_gate\.sh' >/dev/null 2>&1 && conflicts+=("sunray_gate")
  if (( ${#conflicts[@]} > 0 )); then
    printf 'Sunray ROS1 runtime process conflict: %s\n' "$(IFS=,; echo "${conflicts[*]}")" >&2
    return 11
  fi
}

start_sidecar() {
  local vehicle_count="${1:-1}"
  local expected_path_topic="${2:-}"
  local future_marker_topic="${3:-}"
  local ready_timeout_s="${ORCHESTRATOR_RUNTIME_READY_TIMEOUT_S:-90}"
  local sidecar_readiness_args=()
  local sidecar_path_args=()
  local sidecar_coordinate_args=()
  if [[ "${ORCHESTRATOR_REQUIRE_CONTROLLER_COMMAND:-true}" == "false" ]]; then
    sidecar_readiness_args+=(--skip-controller-command-readiness)
  fi
  if [[ "${ORCHESTRATOR_REQUIRE_ACTUATOR_TELEMETRY:-true}" == "false" ]]; then
    sidecar_readiness_args+=(--skip-actuator-telemetry-readiness)
  fi
  if [[ -n "${expected_path_topic}" ]]; then
    sidecar_path_args+=(--expected-path-topic "${expected_path_topic}")
  fi
  if [[ -n "${future_marker_topic}" ]]; then
    sidecar_path_args+=(--future-marker-topic "${future_marker_topic}")
  fi
  if [[ -n "${ORCHESTRATOR_MAP_COORDINATE_EVIDENCE:-}" ]]; then
    sidecar_coordinate_args+=(--coordinate-evidence "${ORCHESTRATOR_MAP_COORDINATE_EVIDENCE}")
  fi
  set +u
  source /opt/ros/noetic/setup.bash
  [[ -f "${LOCAL_ROS1_WS}/devel/setup.bash" ]] && source "${LOCAL_ROS1_WS}/devel/setup.bash"
  set -u
  python3 -u "${PROJECT_ROOT}/Scripts/ui/runtime_sidecar.py" \
    --run-dir "${ORCHESTRATOR_RUN_DIR}" \
    --manifest "${ORCHESTRATOR_RUN_DIR}/RUN_MANIFEST.json" \
    --contract "${PROJECT_ROOT}/Config/control_platform/factory_injection_contract.json" \
    --vehicle-count "${vehicle_count}" \
    --body-name "uav1::base_link" \
    --ready-timeout-s "${ready_timeout_s}" \
    "${sidecar_readiness_args[@]}" \
    "${sidecar_path_args[@]}" \
    "${sidecar_coordinate_args[@]}" \
    > "${ORCHESTRATOR_RUN_DIR}/runtime_sidecar.log" 2>&1 &
  SIDECAR_PID="$!"
  printf '%s\n' "${SIDECAR_PID}" > "${ORCHESTRATOR_RUN_DIR}/runtime_sidecar_pid.txt"
  python3 -u "${PROJECT_ROOT}/Scripts/runtime/collect_ros1_observability.py" \
    --run-id "${RUN_ID}" \
    --output "${ORCHESTRATOR_RUN_DIR}/observability/ros1_topics.json" \
    > "${ORCHESTRATOR_RUN_DIR}/observability_ros1.log" 2>&1 &
  OBSERVABILITY_PID="$!"
  printf '%s\n' "${OBSERVABILITY_PID}" > "${ORCHESTRATOR_RUN_DIR}/observability_ros1_pid.txt"
  if command -v python.exe >/dev/null 2>&1; then
    local windows_project_root windows_run_dir
    windows_project_root="$(wslpath -w "${PROJECT_ROOT}")"
    windows_run_dir="$(wslpath -w "${ORCHESTRATOR_RUN_DIR}")"
    python.exe "${windows_project_root}\\Scripts\\runtime\\collect_runtime_observability.py" \
      --run-id "${RUN_ID}" \
      --run-dir "${windows_run_dir}" \
      > "${ORCHESTRATOR_RUN_DIR}/observability_host.log" 2>&1 &
    HOST_OBSERVABILITY_PID="$!"
    printf '%s\n' "${HOST_OBSERVABILITY_PID}" > "${ORCHESTRATOR_RUN_DIR}/observability_host_pid.txt"
  else
    printf '%s\n' "python.exe unavailable; host observability collector not started" \
      > "${ORCHESTRATOR_RUN_DIR}/observability_host.log"
  fi
}

wait_for_runtime_ready() {
  local timeout_s="${MWORKS_LIVE_RUNTIME_READY_TIMEOUT_S:-240}"
  local status_path="${ORCHESTRATOR_RUN_DIR}/RUNTIME_STATUS.json"
  local deadline=$((SECONDS + timeout_s))
  while (( SECONDS < deadline )); do
    if [[ -f "${status_path}" ]] && python3 - "${status_path}" <<'PY'
import json, sys
try:
    value = json.load(open(sys.argv[1], encoding="utf-8"))
except (OSError, ValueError, TypeError):
    raise SystemExit(1)
missing = set(value.get("missing_readiness") or [])
# The RT1 adapter owns the final attitude fallback publisher in MWORKS Live
# runs, so controller-command freshness can only clear after this gate opens.
allowed = {"uav1:controller_command_fresh"}
upstream_ready = bool(value.get("status") in {"starting", "running"} and missing <= allowed)
raise SystemExit(0 if upstream_ready else 1)
PY
    then
      python3 - "${ORCHESTRATOR_RUN_DIR}/observability/rt1_start_gate.json" "${RUN_ID}" "${timeout_s}" <<'PY'
import json, pathlib, sys, time
pathlib.Path(sys.argv[1]).write_text(json.dumps({
    "schema": "mosim.mworks_live.rt1_start_gate.v1",
    "run_id": sys.argv[2],
    "status": "passed",
    "reason_code": "runtime_ready_before_rt1_start",
    "timeout_s": int(sys.argv[3]),
    "updated_at_unix": time.time(),
}, indent=2) + "\n", encoding="utf-8")
PY
      return 0
    fi
    if [[ -n "${RUNTIME_CHILD_PID}" ]] && ! kill -0 "${RUNTIME_CHILD_PID}" >/dev/null 2>&1; then
      echo "runtime exited before MWORKS Live RT1 readiness" >&2
      return 13
    fi
    sleep 1
  done
  echo "runtime did not become ready before MWORKS Live RT1 timeout (${timeout_s}s)" >&2
  return 13
}

wait_for_mission_terminal_sync() {
  local timeout_s="${MISSION_STATUS_SYNC_TIMEOUT_S:-2}"
  local telemetry_path="${ORCHESTRATOR_RUN_DIR}/telemetry.json"
  local deadline=$((SECONDS + timeout_s))
  while (( SECONDS <= deadline )); do
    if [[ -f "${telemetry_path}" ]] && python3 - "${telemetry_path}" "${RUN_ID}" <<'PY'
import json, sys
try:
    payload = json.load(open(sys.argv[1], encoding="utf-8"))
except (OSError, ValueError, TypeError):
    raise SystemExit(1)
mission = payload.get("mission_status") or {}
matched = (
    payload.get("run_id") == sys.argv[2]
    and mission.get("run_id") == sys.argv[2]
    and mission.get("transport_state") == "terminal"
    and mission.get("terminal") is True
)
raise SystemExit(0 if matched else 1)
PY
    then
      return 0
    fi
    sleep 0.1
  done
  printf '%s\n' "mission terminal ACK was not mirrored before cleanup" \
    >> "${ORCHESTRATOR_RUN_DIR}/runtime_sidecar.log"
  return 0
}

run_basic_gate() {
  local controller_profile="$1"
  local mission="${2:-figure8}"
  local mworks_live="${3:-false}"
  local manual_control="false"
  if [[ -f "${ORCHESTRATOR_RUN_DIR}/RUN_MANIFEST.json" ]]; then
    manual_control="$(python3 - "${ORCHESTRATOR_RUN_DIR}/RUN_MANIFEST.json" <<'PY'
import json, sys
try:
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    print("true" if data.get("parameter_set", {}).get("manual_control") else "false")
except (OSError, ValueError, TypeError, IndexError):
    print("false")
PY
)"
    if [[ "${manual_control}" == "true" ]]; then
      mission="manual"
    fi
  fi
  sunray_ros1_runtime_lock_acquire
  assert_no_conflicting_runtime
  local generated_backend="legacy_px4ctrl"
  case "${controller_profile}" in
    cascade_pid|gain_scheduled_pid|fuzzy_pid|neural_pid|anti_windup|feedforward_profile)
      generated_backend="pid_attitude_thrust"
      ;;
  esac
  RESULT_DIR="${ORCHESTRATOR_RUN_DIR}/runtime_backend" \
    bash "${PROJECT_ROOT}/Scripts/sunray/ensure_px4ctrl_generated_backend.sh" "${generated_backend}"
  local plugin_ws="${FTC_PLUGIN_WS}"
  local plugin_library="${plugin_ws}/devel/lib/libmosim_gazebo_ftc_actuator_plugin.so"
  if [[ ! -f "${plugin_library}" ]]; then
    FTC_PLUGIN_WS="${plugin_ws}" bash "${PROJECT_ROOT}/Scripts/sunray/build_p7_ftc_actuator_plugin.sh" \
      > "${ORCHESTRATOR_RUN_DIR}/ftc_plugin_build.log" 2>&1
  fi
  export RUN_ID="${RUN_ID}"
  export RESULT_DIR="${ORCHESTRATOR_RUN_DIR}/runtime"
  export PX4CTRL_CORE_PROFILE="${controller_profile}"
  export GUI="false"
  export KEEP_ALIVE="false"
  export REVIEW_START_FASTLIO="${REVIEW_START_FASTLIO:-false}"
  export REVIEW_START_OCCUPANCY_NODE="${REVIEW_START_OCCUPANCY_NODE:-false}"
  export MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-180}"
  export ORCHESTRATOR_RUNTIME_READY_TIMEOUT_S="${ORCHESTRATOR_RUNTIME_READY_TIMEOUT_S:-210}"
  export TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-540}"
  export PX4CTRL_MANUAL_INPUT_FILE="${PROJECT_ROOT}/Results/ui_platform/manual_control/manual_control.json"
  export PX4CTRL_MANUAL_RUN_ID="${RUN_ID}"
  export PX4CTRL_MISSION_EXTRA_ARGS="${PX4CTRL_MISSION_EXTRA_ARGS:---force-disarm-after-land --force-disarm-timeout-s 30 --pre-takeoff-state-stable-s 3.0 --pre-takeoff-state-timeout-s 30 --pre-takeoff-max-abs-roll-pitch-deg 0.5 --takeoff-timeout-s 90 --wall-timeout-s 480}"
  export MOSIM_ENABLE_FTC_ACTUATOR_PLUGIN="true"
  export GAZEBO_PLUGIN_PATH="${plugin_ws}/devel/lib:${GAZEBO_PLUGIN_PATH:-}"
  export LD_LIBRARY_PATH="${plugin_ws}/devel/lib:${LD_LIBRARY_PATH:-}"
  if [[ "${mworks_live}" == "true" ]]; then
    # RT1 capability profiles declare the sparse controller-validation scene.
    # Factory/MID360/UE load is measured separately by the system-load gate.
    export VEHICLE="${MWORKS_LIVE_VEHICLE:-sunray150}"
    export WORLD_FILE="${MWORKS_LIVE_WORLD_FILE:-${SUNRAY_WS}/simulation/sunray_simulator/worlds/planning_test.world}"
    export SUNRAY_GAZEBO_LAUNCH_FILE="${MWORKS_LIVE_GAZEBO_LAUNCH_FILE:-${SUNRAY_WS}/simulation/sunray_simulator/launch_uav_demo/sunray_sim_uav_planning.launch}"
    export SUNRAY_UAV_INIT_X="0.0"
    export SUNRAY_UAV_INIT_Y="0.0"
    export SUNRAY_UAV_INIT_Z="0.2"
    # The lightweight sunray150 SDF includes model://gps from the PX4 model
    # tree. Keep that tree available for this gate; Factory/MID360 does not
    # use this override.
    export SUNRAY_STRIP_PX4_MODEL_PATH="false"
    export ORCHESTRATOR_REQUIRE_ACTUATOR_TELEMETRY="false"
    export REVIEW_START_FASTLIO="false"
    export REVIEW_START_OCCUPANCY_NODE="false"
    export PX4CTRL_ATTITUDE_OUTPUT_TOPIC="/mosim/mworks_live/px4ctrl_attitude_candidate"
    export PX4CTRL_PRE_MISSION_OWNER_TOPIC="/mosim/mworks_live/control_owner_state"
    export PX4CTRL_PRE_MISSION_OWNER_TIMEOUT_S="${MWORKS_LIVE_OWNER_TIMEOUT_S:-45}"
    if [[ "${MWORKS_LIVE_ACTIVE_TAKEOVER:-false}" == "true" ]]; then
      export PX4CTRL_PRE_MISSION_OWNER_STATE="ACTIVE"
    else
      export PX4CTRL_PRE_MISSION_OWNER_STATE="SHADOW"
      export PX4CTRL_SKIP_MISSION="true"
      export NO_FLIGHT_DIAGNOSTIC_HOLD_S="${MWORKS_LIVE_SHADOW_HOLD_S:-300}"
    fi
  fi
  start_sidecar 1 "/mosim/px4ctrl/reference_path"
  bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" "${mission}" &
  RUNTIME_CHILD_PID="$!"
  if [[ "${mworks_live}" == "true" ]]; then
    wait_for_runtime_ready
    start_mworks_live_rt1
  fi
  set +e
  wait "${RUNTIME_CHILD_PID}"
  local exit_code="$?"
  set -e
  RUNTIME_CHILD_PID=""
  wait_for_mission_terminal_sync
  return "${exit_code}"
}

run_ground_standby() {
  local map_catalog="${PROJECT_ROOT}/Config/control_platform/operator_map_catalog.json"
  read -r PX4CTRL_EKF_ORIGIN_LAT PX4CTRL_EKF_ORIGIN_LON PX4CTRL_EKF_ORIGIN_ALT_M < <(
    python3 - "${map_catalog}" <<'PY'
import json
import sys

catalog = json.load(open(sys.argv[1], encoding="utf-8"))
factory = next(item for item in catalog["maps"] if item["map_id"] == "factory_l2")
anchor = factory["simulation_geodetic_anchor"]
print(anchor["latitude_deg"], anchor["longitude_deg"], anchor["altitude_m"])
PY
  )
  export PX4CTRL_SET_EKF_GLOBAL_ORIGIN="true"
  export PX4CTRL_EKF_ORIGIN_LAT
  export PX4CTRL_EKF_ORIGIN_LON
  export PX4CTRL_EKF_ORIGIN_ALT_M
  export PX4CTRL_SKIP_MISSION="true"
  export PX4CTRL_START_CONTROLLER="false"
  export ORCHESTRATOR_REQUIRE_CONTROLLER_COMMAND="false"
  export ORCHESTRATOR_REQUIRE_ACTUATOR_TELEMETRY="false"
  export NO_FLIGHT_DIAGNOSTIC_HOLD_S="${QGC_GROUND_STANDBY_HOLD_S:-until_stopped}"
  run_basic_gate original takeoff_hover_land false
}

start_mworks_live_rt1() {
  local manifest="${ORCHESTRATOR_RUN_DIR}/RUN_MANIFEST.json"
  local rt1_values=()
  local active_takeover="${MWORKS_LIVE_ACTIVE_TAKEOVER:-false}"
  local rt1_authority_args=()
  local rt1_backend="${MWORKS_LIVE_RT1_BACKEND:-auto}"
  local rt1_status_rate_hz="2"
  if [[ "${active_takeover}" != "true" && "${active_takeover}" != "false" ]]; then
    echo "MWORKS_LIVE_ACTIVE_TAKEOVER must be true or false" >&2
    return 12
  fi
  if [[ "${active_takeover}" == "true" ]]; then
    rt1_authority_args+=(--allow-active-takeover --auto-activate-ground)
  fi
  mapfile -t rt1_values < <(python3 - "${manifest}" <<'PY'
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
connection = value.get("mworks_live_connection") or {}
print(connection.get("target_host", ""))
print(connection.get("rt1_udp_port", ""))
print(connection.get("selected_rate_hz", ""))
PY
)
  local configured_host="${rt1_values[0]:-}"
  local rt1_port="${rt1_values[1]:-}"
  local rt1_rate="${rt1_values[2]:-}"
  if [[ -z "${configured_host}" || ! "${rt1_port}" =~ ^[0-9]+$ || ! "${rt1_rate}" =~ ^(50|200)$ ]]; then
    echo "MWORKS Live manifest endpoint invalid or rate not RT0-accepted" >&2
    return 12
  fi
  if [[ "${rt1_backend}" == "auto" ]]; then
    if [[ "${rt1_rate}" == "200" ]]; then
      rt1_backend="cpp_wall_clock_v1"
    else
      rt1_backend="python_wall_clock_v1"
    fi
  fi
  if [[ "${rt1_rate}" == "200" ]]; then
    local windows_project_root windows_priority_evidence
    windows_project_root="$(wslpath -w "${PROJECT_ROOT}")"
    windows_priority_evidence="$(wslpath -w "${ORCHESTRATOR_RUN_DIR}/observability/mwsolver_priority.json")"
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File \
      "${windows_project_root}\\Scripts\\mworks_live\\set_mwsolver_priority.ps1" \
      -RunId "${RUN_ID}" \
      -OutputPath "${windows_priority_evidence}" \
      -PriorityClass "${MWORKS_LIVE_MWSOLVER_PRIORITY:-High}" \
      > "${ORCHESTRATOR_RUN_DIR}/mwsolver_priority.log" 2>&1
  fi
  if [[ "${rt1_rate}" == "200" ]]; then
    rt1_status_rate_hz="0.5"
  fi
  if [[ "${rt1_backend}" != "cpp_wall_clock_v1" && "${rt1_backend}" != "cpp_gazebo_step_v1" && "${rt1_backend}" != "python_wall_clock_v1" ]]; then
    echo "unsupported MWORKS Live RT1 backend: ${rt1_backend}" >&2
    return 12
  fi
  local effective_host="${configured_host}"
  if [[ "${configured_host}" == "127.0.0.1" || "${configured_host}" == "localhost" || "${configured_host}" == "::1" ]]; then
    effective_host="$(ip route show default 2>/dev/null | awk 'NR==1 {print $3}')"
    effective_host="${effective_host:-${configured_host}}"
  fi
  mkdir -p "${ORCHESTRATOR_RUN_DIR}/observability"
  python3 - "${ORCHESTRATOR_RUN_DIR}/observability/mworks_ros_endpoint.json" \
    "${RUN_ID}" "${configured_host}" "${effective_host}" "${rt1_port}" "${rt1_rate}" "${active_takeover}" <<'PY'
import json, pathlib, sys, time
pathlib.Path(sys.argv[1]).write_text(json.dumps({
    "schema": "mosim.mworks_live.wsl_endpoint.v1",
    "run_id": sys.argv[2],
    "configured_windows_host": sys.argv[3],
    "effective_wsl_target_host": sys.argv[4],
    "rt1_udp_port": int(sys.argv[5]),
    "selected_rate_hz": int(sys.argv[6]),
    "authority_mode": "active_takeover_requested" if sys.argv[7] == "true" else "shadow_only",
    "updated_at_unix": time.time(),
}, indent=2) + "\n", encoding="utf-8")
PY
  set +u
  source /opt/ros/noetic/setup.bash
  [[ -f /opt/mosim_work/sunray_ws/Sunray/devel/setup.bash ]] && source /opt/mosim_work/sunray_ws/Sunray/devel/setup.bash
  [[ -f "${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash" ]] && \
    source "${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws/devel/setup.bash"
  set -u
  local rt1_command=(python3 -u "${PROJECT_ROOT}/Scripts/mworks_live/ros1_rt1_adapter.py")
  if [[ "${rt1_backend}" == "cpp_wall_clock_v1" || "${rt1_backend}" == "cpp_gazebo_step_v1" ]]; then
    local cpp_adapter
    cpp_adapter="$(PROJECT_ROOT="${PROJECT_ROOT}" bash "${PROJECT_ROOT}/Scripts/mworks_live/build_ros1_rt1_adapter_cpp.sh")"
    rt1_command=("${cpp_adapter}")
  fi
  printf '%s\n' "${rt1_backend}" > "${ORCHESTRATOR_RUN_DIR}/observability/rt1_adapter_backend.txt"
  local rt1_time_args=()
  if [[ "${rt1_backend}" == "cpp_gazebo_step_v1" ]]; then
    rt1_time_args+=(--time-mode gazebo_step --gazebo-steps-per-command 5 --gazebo-step-size-ns 1000000)
  fi
  "${rt1_command[@]}" \
    --run-id "${RUN_ID}" \
    --result-dir "${ORCHESTRATOR_RUN_DIR}/observability" \
    --mworks-host "${effective_host}" \
    --mworks-port "${rt1_port}" \
    --rate-hz "${rt1_rate}" \
    --status-rate-hz "${rt1_status_rate_hz}" \
    --deadline-ms 10 \
    --command-stale-ms 50 \
    --failsafe-escalation-ms 100 \
    --minimum-shadow-commands 50 \
    --allow-ground-hold-reference \
    "${rt1_time_args[@]}" \
    "${rt1_authority_args[@]}" \
    > "${ORCHESTRATOR_RUN_DIR}/rt1_adapter.log" 2>&1 &
  RT1_PID="$!"
  printf '%s\n' "${RT1_PID}" > "${ORCHESTRATOR_RUN_DIR}/rt1_adapter_pid.txt"
}

run_swarm_formation_gate() {
  local formation_values=()
  mapfile -t formation_values < <(python3 - "${ORCHESTRATOR_RUN_DIR}/RUN_MANIFEST.json" <<'PY'
import json, math, sys

manifest = json.load(open(sys.argv[1], encoding="utf-8"))
if manifest.get("experiment_profile_id") != "factory_l2_three_uav_swarm_formation_v1":
    raise SystemExit("formation manifest profile mismatch")
scenario = manifest.get("scenario_snapshot") or {}
formation = scenario.get("formation") or {}
obstacle = scenario.get("obstacle_crossing_contract") or {}
target = formation.get("target_center_xy_m") or []
values = [
    target[0] if len(target) == 2 else None,
    target[1] if len(target) == 2 else None,
    formation.get("z_m"),
    formation.get("scale"),
    obstacle.get("clearance_margin_m"),
]
if not all(isinstance(value, (int, float)) and math.isfinite(float(value)) for value in values):
    raise SystemExit("formation manifest contains invalid target parameters")
print("ok")
for value in values:
    print(value)
PY
  )
  if [[ "${formation_values[0]:-}" != "ok" || "${#formation_values[@]}" -ne 6 ]]; then
    echo "formation RunManifest is incomplete; refusing to launch" >&2
    return 12
  fi
  sunray_ros1_runtime_lock_acquire
  assert_no_conflicting_runtime
  local plugin_ws="${PROJECT_ROOT}/Results/control_platform/p7_ftc_gazebo_plugin_ws_v2"
  local plugin_library="${plugin_ws}/devel/lib/libmosim_gazebo_ftc_actuator_plugin.so"
  if [[ ! -f "${plugin_library}" ]]; then
    FTC_PLUGIN_WS="${plugin_ws}" bash "${PROJECT_ROOT}/Scripts/sunray/build_p7_ftc_actuator_plugin.sh" \
      > "${ORCHESTRATOR_RUN_DIR}/ftc_plugin_build.log" 2>&1
  fi
  local factory_root="${PROJECT_ROOT}/Config/gazebo"
  export RUN_ID="${RUN_ID}"
  export RESULT_DIR="${ORCHESTRATOR_RUN_DIR}/runtime"
  export PLANNER_VARIANT="swarm_formation"
  export UAV_NUM="3"
  export GUI="false"
  export KEEP_ALIVE="false"
  export WORLD_FILE="${factory_root}/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf"
  export GAZEBO_MODEL_PATH="${factory_root}/models:${GAZEBO_MODEL_PATH:-}"
  export MOSIM_ENABLE_FTC_ACTUATOR_PLUGIN="true"
  export GAZEBO_PLUGIN_PATH="${plugin_ws}/devel/lib:${GAZEBO_PLUGIN_PATH:-}"
  export LD_LIBRARY_PATH="${plugin_ws}/devel/lib:${LD_LIBRARY_PATH:-}"
  export TOTAL_TIMEOUT_S="600"
  export EGO_GATE_EGO_TAKEOVER_TIMEOUT_S="120"
  export EGO_GATE_EXECUTE_TIMEOUT_S="420"
  export SWARM_FORMATION_D3_CENTER_X="${formation_values[1]}"
  export SWARM_FORMATION_D3_CENTER_Y="${formation_values[2]}"
  export SWARM_FORMATION_D3_CENTER_Z="${formation_values[3]}"
  export SWARM_FORMATION_D3_SWARM_SCALE="${formation_values[4]}"
  export SWARM_FORMATION_D3_SWARM_CLEARANCE="${formation_values[5]}"
  export SWARM_FORMATION_D3_MIN_TRAJ_Z="0.90"
  export SWARM_FORMATION_D3_MAX_TRAJ_Z="1.60"
  export SWARM_FORMATION_D3_WEIGHT_HEIGHT="50000.0"
  export SWARM_FORMATION_D3_MAP_SIZE_X="64.0"
  export SWARM_FORMATION_D3_MAP_SIZE_Y="64.0"
  export SWARM_FORMATION_D3_MAP_SIZE_Z="3.0"
  export SWARM_FORMATION_D3_GRID_RESOLUTION="0.20"
  export SWARM_FORMATION_D3_OBSTACLES_INFLATION="0.20"
  export SWARM_FORMATION_D3_LOCAL_UPDATE_RANGE_XY="8.0"
  export SWARM_FORMATION_D3_LEADER_FOLLOWER_COMMANDS="true"
  start_sidecar 3 "/mosim/goal5/target_path"
  bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh" &
  RUNTIME_CHILD_PID="$!"
  set +e
  wait "${RUNTIME_CHILD_PID}"
  local exit_code="$?"
  set -e
  RUNTIME_CHILD_PID=""
  wait_for_mission_terminal_sync
  return "${exit_code}"
}

run_fuel_fixed64_gate() {
  local fuel_values=()
  mapfile -t fuel_values < <(python3 - "${ORCHESTRATOR_RUN_DIR}/RUN_MANIFEST.json" <<'PY'
import json, math, sys

manifest = json.load(open(sys.argv[1], encoding="utf-8"))
if manifest.get("experiment_profile_id") != "factory_l2_fuel_fixed64_exploration_v1":
    raise SystemExit("FUEL manifest profile mismatch")
scenario = manifest.get("scenario_snapshot") or {}
spawn = scenario.get("spawn") or {}
boundary = scenario.get("exploration_boundary") or {}
mission = scenario.get("mission") or {}
numeric = [
    spawn.get("x_m"), spawn.get("y_m"), spawn.get("yaw_rad"),
    boundary.get("min_x_m"), boundary.get("max_x_m"),
    boundary.get("min_y_m"), boundary.get("max_y_m"),
    boundary.get("min_z_m"), boundary.get("max_z_m"),
    mission.get("duration_s"), mission.get("random_seed"),
    mission.get("max_velocity_mps"), mission.get("max_acceleration_mps2"),
]
if not all(isinstance(value, (int, float)) and math.isfinite(float(value)) for value in numeric):
    raise SystemExit("FUEL manifest contains invalid numeric parameters")
if not numeric[3] < numeric[4] or not numeric[5] < numeric[6] or not numeric[7] < numeric[8]:
    raise SystemExit("FUEL manifest boundary is invalid")
core_profile = mission.get("px4ctrl_core_profile")
if core_profile != "l1_awff":
    raise SystemExit("FUEL manifest controller core profile is not accepted")
print("ok")
for value in numeric:
    print(value)
print(core_profile)
PY
  )
  if [[ "${fuel_values[0]:-}" != "ok" || "${#fuel_values[@]}" -ne 15 ]]; then
    echo "FUEL RunManifest is incomplete; refusing to launch" >&2
    return 12
  fi
  sunray_ros1_runtime_lock_acquire
  assert_no_conflicting_runtime
  start_sidecar 1 "/mosim/goal4/target_path" "/planning_vis/trajectory"

  local windows_project_root
  local fuel_result_dir="${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}"
  windows_project_root="$(wslpath -w "${PROJECT_ROOT}")"
  mkdir -p "${ORCHESTRATOR_RUN_DIR}/runtime"

  powershell.exe -NoProfile -ExecutionPolicy Bypass -File \
    "${windows_project_root}\\Scripts\\sunray\\start_factory_fuel_single_exploration_review.ps1" \
    -RunId "${RUN_ID}" \
    -FuelRandomSeed "${fuel_values[11]}" \
    -ExplorationExecuteS "${fuel_values[10]}" \
    -ReviewHoldS 0 \
    -StartX "${fuel_values[1]}" \
    -StartY "${fuel_values[2]}" \
    -StartYaw "${fuel_values[3]}" \
    -FuelWindowXYM "$(python3 -c "print(float('${fuel_values[5]}') - float('${fuel_values[4]}'))")" \
    -FuelWindowYM "$(python3 -c "print(float('${fuel_values[7]}') - float('${fuel_values[6]}'))")" \
    -FuelBoxMinXOverride "${fuel_values[4]}" \
    -FuelBoxMaxXOverride "${fuel_values[5]}" \
    -FuelBoxMinYOverride "${fuel_values[6]}" \
    -FuelBoxMaxYOverride "${fuel_values[7]}" \
    -FuelBoxMinZM "${fuel_values[8]}" \
    -FuelBoxMaxZM "${fuel_values[9]}" \
    -FuelFrontierMinCandidateClearance 0.21 \
    -FuelCoverageExpansion \
    -FuelCoverageExpansionAxis -1 \
    -FuelCoverageExpansionScoreCommittedGoal \
    -FuelCoverageExpansionGlobalSelector \
    -ControllerCoreProfile "${fuel_values[14]}" \
    -FuelPlannerMaxVelMps "${fuel_values[12]}" \
    -FuelPlannerMaxAccMps2 "${fuel_values[13]}" \
    -FuelCmdSmoothMaxSpeedMps "${fuel_values[12]}" \
    -FuelCmdMaxVelocityMps "${fuel_values[12]}" \
    -FuelCmdMaxAccelerationMps2 "${fuel_values[13]}" \
    -NoRviz \
    -ReuseUnrealWindow \
    -NoKeepAlive \
    -Foreground &
  RUNTIME_CHILD_PID="$!"
  set +e
  wait "${RUNTIME_CHILD_PID}"
  local exit_code="$?"
  set -e
  RUNTIME_CHILD_PID=""
  wait_for_mission_terminal_sync

  if [[ -f "${fuel_result_dir}/RUN_MANIFEST.json" ]]; then
    cp "${fuel_result_dir}/RUN_MANIFEST.json" "${ORCHESTRATOR_RUN_DIR}/runtime/RUN_MANIFEST.json"
    printf '%s\n' "${fuel_result_dir}" > "${ORCHESTRATOR_RUN_DIR}/runtime/source_result_dir.txt"
  fi
  return "${exit_code}"
}

case "${OPERATION_ID}" in
  px4ctrl_ground_standby_single)
    run_ground_standby
    ;;
  px4ctrl_figure8_single)
    run_basic_gate original
    ;;
  cascade_pid_figure8_single)
    run_basic_gate cascade_pid
    ;;
  mworks_live_official_pid_hover_50hz)
    run_basic_gate original takeoff_hover_land true
    ;;
  mworks_live_official_pid_hover_200hz)
    run_basic_gate original takeoff_hover_land true
    ;;
  factory_l2_fuel_fixed64_exploration)
    run_fuel_fixed64_gate
    ;;
  factory_l2_three_uav_swarm_formation)
    run_swarm_formation_gate
    ;;
  *)
    echo "operation is not allowlisted: ${OPERATION_ID}" >&2
    exit 2
    ;;
esac
