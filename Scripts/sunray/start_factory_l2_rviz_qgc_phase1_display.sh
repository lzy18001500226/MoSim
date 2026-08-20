#!/usr/bin/env bash
# Attach a visible Phase 1 display terminal. This may start in parallel with
# the backend and waits for the matching run to reach its display gate.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ACTIVE_POINTER="${PROJECT_ROOT}/Results/ui_platform/qgc_active_run.json"
REQUESTED_RUN_ID="${1:-}"
PROFILE_ID="px4ctrl_graphical_c99_factory_rviz_qgc_display_phase1_v1"
RUNTIME_PROFILE_ID="sunray_ros1_factory_l2_graphical_px4ctrl_c99_rviz_qgc_display_phase1_v1"
POINTCLOUD_RVIZ_CONFIG="${PROJECT_ROOT}/Config/rviz/sunray_ros1_goal4_diff_pointcloud_review.rviz"
GRID_RVIZ_CONFIG="${PROJECT_ROOT}/Config/rviz/sunray_ros1_goal4_diff_grid3d_review.rviz"
GOAL4_DIFF_PLANNER_WS="${GOAL4_DIFF_PLANNER_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/goal4_diff_planner_ws_px4msg}"
ROS_MASTER_URI="${ROS_MASTER_URI:-http://127.0.0.1:11311}"
DISPLAY_WAIT_TIMEOUT_S="${PHASE1_DISPLAY_WAIT_TIMEOUT_S:-900}"
export ROS_MASTER_URI

if [[ "$#" -gt 1 ]]; then
  echo "Usage: $0 [run-id]" >&2
  exit 2
fi
if [[ ! "$DISPLAY_WAIT_TIMEOUT_S" =~ ^[1-9][0-9]*$ ]]; then
  echo "PHASE1_DISPLAY_WAIT_TIMEOUT_S must be a positive integer" >&2
  exit 2
fi
if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
  echo "BLOCKER RViz GUI display is unavailable: DISPLAY and WAYLAND_DISPLAY are both unset." >&2
  exit 2
fi
for config in "$POINTCLOUD_RVIZ_CONFIG" "$GRID_RVIZ_CONFIG"; do
  if [[ ! -f "$config" ]]; then
    echo "BLOCKER RViz configuration is missing: $config" >&2
    exit 2
  fi
done

RUN_ID="$REQUESTED_RUN_ID"
resolve_run_id() {
  python3 - "$ACTIVE_POINTER" <<'PY'
import json
import pathlib
import sys

try:
    value = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    value = {}
run_id = value.get("run_id", "") if isinstance(value, dict) else ""
print(run_id if isinstance(run_id, str) else "")
PY
}

active_state() {
  python3 - "$ACTIVE_POINTER" <<'PY'
import json
import pathlib
import sys

try:
    value = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    value = {}
print(value.get("state", "") if isinstance(value, dict) else "")
PY
}

runtime_reason_for_run() {
  local run_id="$1"
  python3 - "${PROJECT_ROOT}/Results/sunray_ros1/${run_id}/RVIZ_QGC_DISPLAY_PHASE1_RUNTIME_STATUS.json" <<'PY'
import json
import pathlib
import sys

try:
    value = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    value = {}
print(value.get("reason_code", "") if isinstance(value, dict) else "")
PY
}

phase1_manifest_matches() {
  local run_id="$1"
  python3 - "${PROJECT_ROOT}/Results/runs/${run_id}/RUN_MANIFEST.json" "$run_id" <<'PY'
import json
import pathlib
import sys

path, run_id = sys.argv[1:]
try:
    payload = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    raise SystemExit(1)
raise SystemExit(
    0
    if payload.get("run_id") == run_id
    and payload.get("experiment_profile_id") == "px4ctrl_graphical_c99_factory_rviz_qgc_display_phase1_v1"
    and payload.get("runtime_profile_id")
    == "sunray_ros1_factory_l2_graphical_px4ctrl_c99_rviz_qgc_display_phase1_v1"
    else 1
)
PY
}

SEEN_PHASE1_RUN_STATE=false
deadline=$((SECONDS + DISPLAY_WAIT_TIMEOUT_S))
while (( SECONDS < deadline )); do
  candidate_run_id="$REQUESTED_RUN_ID"
  if [[ -z "$candidate_run_id" ]]; then
    candidate_run_id="$(resolve_run_id)"
  fi
  if [[ ! "$candidate_run_id" =~ ^qgc-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$ ]]; then
    sleep 1
    continue
  fi
  if ! phase1_manifest_matches "$candidate_run_id"; then
    if [[ -n "$REQUESTED_RUN_ID" ]]; then
      echo "Requested run is not a Phase 1 runtime run: $candidate_run_id" >&2
      exit 3
    fi
    sleep 1
    continue
  fi
  if [[ "$RUN_ID" != "$candidate_run_id" ]]; then
    RUN_ID="$candidate_run_id"
    SEEN_PHASE1_RUN_STATE=false
  fi
  state="$(active_state)"
  reason="$(runtime_reason_for_run "$RUN_ID")"
  if [[ "$state" == "launch_prepared" || "$state" == "running" ]]; then
    SEEN_PHASE1_RUN_STATE=true
  fi
  if [[ "$state" == "running" && "$reason" == "rviz_qgc_display_phase1_runtime_ready_for_display" ]]; then
    break
  fi
  if [[ "$state" == "blocked" || "$state" == "failed" || "$state" == "completed" ]]; then
    if [[ -n "$REQUESTED_RUN_ID" || "$SEEN_PHASE1_RUN_STATE" == true ]]; then
      echo "Phase 1 runtime did not reach the display gate: state=$state reason=$reason" >&2
      exit 3
    fi
  fi
  sleep 1
done
if [[ ! "$RUN_ID" =~ ^qgc-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$ ]]; then
  echo "No Phase 1 runtime run appeared within ${DISPLAY_WAIT_TIMEOUT_S} seconds." >&2
  exit 2
fi
if [[ "$(active_state)" != "running" || "$(runtime_reason_for_run "$RUN_ID")" != "rviz_qgc_display_phase1_runtime_ready_for_display" ]]; then
  echo "Phase 1 runtime did not become ready for the Display/RViz terminal within ${DISPLAY_WAIT_TIMEOUT_S} seconds." >&2
  exit 3
fi

RUN_DIR="${PROJECT_ROOT}/Results/runs/${RUN_ID}"
RESULT_DIR="${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}"
RUNTIME_RESULT_DIR="${RESULT_DIR}/runtime"
RUNTIME_STATUS_FILE="${RESULT_DIR}/RVIZ_QGC_DISPLAY_PHASE1_RUNTIME_STATUS.json"
MANUAL_PACKET_FILE="${RESULT_DIR}/RVIZ_QGC_DISPLAY_PHASE1_MANUAL_TEST.json"
ACCEPTANCE_FILE="${RESULT_DIR}/RVIZ_QGC_DISPLAY_PHASE1_ACCEPTANCE.json"
COORDINATE_EVIDENCE="${RUN_DIR}/OPERATOR_MAP_COORDINATE_EVIDENCE.json"

write_runtime_status() {
  local state="$1"
  local reason_code="$2"
  python3 - "$RUNTIME_STATUS_FILE" "$RUN_ID" "$state" "$reason_code" "$RUN_DIR" <<'PY'
import json
import pathlib
import sys
import time

output, run_id, state, reason_code, run_dir = sys.argv[1:]
payload = {
    "schema": "mosim.rviz_qgc_display_phase1_runtime_status.v1",
    "run_id": run_id,
    "state": state,
    "reason_code": reason_code,
    "updated_at_unix_s": time.time(),
    "operator_run_directory": run_dir,
    "transport": {
        "rviz_goal_topic": "/move_base_simple/goal",
        "planner_goal_topic": "/goal_with_id",
        "mission_ready_topic": "/mosim/goal4/interactive_goal_ready",
        "operator_telemetry_path": f"{run_dir}/telemetry.json",
        "display_terminal": "separate_visible_terminal",
        "claim_boundary": (
            "This status records the Phase 1 RViz input and QGC display readiness surfaces. "
            "It does not prove human QGC observation, flight success, or controller acceptance."
        ),
    },
}
path = pathlib.Path(output)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
}

verify_manifest() {
  python3 - "$RUN_DIR/RUN_MANIFEST.json" "$RUN_ID" <<'PY'
import json
import pathlib
import sys

path, run_id = sys.argv[1:]
payload = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
if payload.get("run_id") != run_id:
    raise SystemExit("phase1_display_run_id_mismatch")
if payload.get("experiment_profile_id") != "px4ctrl_graphical_c99_factory_rviz_qgc_display_phase1_v1":
    raise SystemExit("phase1_display_profile_mismatch")
if payload.get("runtime_profile_id") != "sunray_ros1_factory_l2_graphical_px4ctrl_c99_rviz_qgc_display_phase1_v1":
    raise SystemExit("phase1_display_runtime_profile_mismatch")
PY
}

verify_manifest
[[ -f "$COORDINATE_EVIDENCE" ]] || {
  echo "Phase 1 coordinate evidence is missing: $COORDINATE_EVIDENCE" >&2
  exit 3
}
mkdir -p "$RUNTIME_RESULT_DIR"

set +u
source /opt/ros/noetic/setup.bash
if [[ -f "${GOAL4_DIFF_PLANNER_WS}/devel/setup.bash" ]]; then
  source "${GOAL4_DIFF_PLANNER_WS}/devel/setup.bash"
fi
set -u

RVIZ_POINTCLOUD_PID=
RVIZ_GRID_PID=
SIDECAR_PID=
DISPLAY_ATTACHED=false

stop_pid() {
  local pid="$1"
  [[ "$pid" =~ ^[0-9]+$ ]] || return 0
  kill -0 "$pid" 2>/dev/null || return 0
  kill -INT "$pid" 2>/dev/null || true
  for _ in $(seq 1 20); do
    kill -0 "$pid" 2>/dev/null || return 0
    sleep 0.1
  done
  kill -TERM "$pid" 2>/dev/null || true
}

cleanup() {
  local exit_code=$?
  set +e
  stop_pid "$SIDECAR_PID"
  stop_pid "$RVIZ_POINTCLOUD_PID"
  stop_pid "$RVIZ_GRID_PID"
  if [[ "$exit_code" -ne 0 && "$DISPLAY_ATTACHED" == true ]]; then
    write_runtime_status blocked rviz_qgc_display_phase1_display_terminal_stopped
  fi
  trap - EXIT INT TERM
  exit "$exit_code"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

DISPLAY_ATTACHED=true
rviz -d "$POINTCLOUD_RVIZ_CONFIG" > "$RUNTIME_RESULT_DIR/rviz_phase1_pointcloud.log" 2>&1 &
RVIZ_POINTCLOUD_PID=$!
rviz -d "$GRID_RVIZ_CONFIG" > "$RUNTIME_RESULT_DIR/rviz_phase1_grid3d.log" 2>&1 &
RVIZ_GRID_PID=$!

(
  set +u
  source "$GOAL4_DIFF_PLANNER_WS/devel/setup.bash"
  set -u
  exec python3 "$PROJECT_ROOT/Scripts/ui/runtime_sidecar.py" \
    --run-dir "$RUN_DIR" \
    --manifest "$RUN_DIR/RUN_MANIFEST.json" \
    --contract "$PROJECT_ROOT/Config/control_platform/factory_injection_contract.json" \
    --vehicle-count 1 \
    --rate-hz 20 \
    --max-track-points 1200 \
    --odom-topic /uav1/mosim/diff_goal4/planner_odom_world \
    --expected-path-topic /mosim/goal4/target_path \
    --future-polytraj-topic /drone_0_planning/trajectory \
    --future-polytraj-frame-id world \
    --future-polytraj-sample-period-s 0.01 \
    --future-polytraj-max-points 2400 \
    --actual-track-min-distance-m 0.02 \
    --coordinate-evidence "$COORDINATE_EVIDENCE" \
    --skip-actuator-telemetry-readiness \
    --read-only
) > "$RESULT_DIR/qgc_runtime_sidecar.log" 2>&1 &
SIDECAR_PID=$!

for _ in $(seq 1 40); do
  if kill -0 "$RVIZ_POINTCLOUD_PID" 2>/dev/null \
    && kill -0 "$RVIZ_GRID_PID" 2>/dev/null \
    && kill -0 "$SIDECAR_PID" 2>/dev/null; then
    break
  fi
  sleep 0.5
done
if ! kill -0 "$RVIZ_POINTCLOUD_PID" 2>/dev/null || \
  ! kill -0 "$RVIZ_GRID_PID" 2>/dev/null || \
  ! kill -0 "$SIDECAR_PID" 2>/dev/null; then
  echo "Phase 1 Display/RViz startup failed; inspect runtime display logs." >&2
  exit 4
fi

python3 "$PROJECT_ROOT/Scripts/sunray/rviz_qgc_display_phase1.py" manual-packet \
  --run-id "$RUN_ID" \
  --profile-id "$PROFILE_ID" \
  --runtime-profile-id "$RUNTIME_PROFILE_ID" \
  --rviz-config "$GRID_RVIZ_CONFIG" \
  --rviz-pointcloud-config "$POINTCLOUD_RVIZ_CONFIG" \
  --result-directory "$RESULT_DIR" \
  --operator-run-directory "$RUN_DIR" \
  --output "$MANUAL_PACKET_FILE"
write_runtime_status running rviz_qgc_display_phase1_ready_for_rviz_goal
echo "Phase 1 Display/RViz terminal is ready. Use RViz 2D Nav Goal once, then observe the same run in QGC."
echo "RViz point-cloud log: $RUNTIME_RESULT_DIR/rviz_phase1_pointcloud.log"
echo "RViz grid3d log: $RUNTIME_RESULT_DIR/rviz_phase1_grid3d.log"

while true; do
  if ! kill -0 "$RVIZ_POINTCLOUD_PID" 2>/dev/null || \
    ! kill -0 "$RVIZ_GRID_PID" 2>/dev/null || \
    ! kill -0 "$SIDECAR_PID" 2>/dev/null; then
    echo "Phase 1 Display/RViz process exited before the backend run ended." >&2
    exit 5
  fi
  state="$(active_state)"
  if [[ "$state" == "completed" || "$state" == "blocked" || "$state" == "failed" ]]; then
    break
  fi
  sleep 2
done

if [[ -f "$RUNTIME_RESULT_DIR/EGO_SINGLE_METRICS.json" \
  && -f "$RUNTIME_RESULT_DIR/clicked_goal_adapter.json" \
  && -f "$RUN_DIR/telemetry.json" ]]; then
  python3 "$PROJECT_ROOT/Scripts/sunray/rviz_qgc_display_phase1.py" evaluate \
    --run-id "$RUN_ID" \
    --metrics "$RUNTIME_RESULT_DIR/EGO_SINGLE_METRICS.json" \
    --adapter "$RUNTIME_RESULT_DIR/clicked_goal_adapter.json" \
    --telemetry "$RUN_DIR/telemetry.json" \
    --output "$ACCEPTANCE_FILE" \
    --schema mosim.rviz_qgc_display_phase1_acceptance.v1 || true
fi
echo "Phase 1 backend ended; Display/RViz evidence was written for run $RUN_ID."
