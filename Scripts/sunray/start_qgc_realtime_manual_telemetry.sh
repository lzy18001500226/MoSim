#!/usr/bin/env bash
# Run the QGC telemetry/map sidecar in its own visible terminal.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ACTIVE_POINTER="${PROJECT_ROOT}/Results/ui_platform/qgc_active_run.json"
RUN_ID="${1:-}"

resolve_run_id() {
  python3 - "${ACTIVE_POINTER}" <<'PY'
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

if [[ -z "${RUN_ID}" ]]; then
  deadline=$((SECONDS + 300))
  while (( SECONDS < deadline )); do
    RUN_ID="$(resolve_run_id)"
    if [[ "${RUN_ID}" =~ ^qgc-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$ ]]; then
      break
    fi
    sleep 1
  done
fi

if [[ ! "${RUN_ID}" =~ ^qgc-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$ ]]; then
  echo "No prepared QGC run appeared within 300 seconds." >&2
  exit 2
fi

RUN_DIR="${PROJECT_ROOT}/Results/runs/${RUN_ID}"
RESULT_DIR="${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}"
COORDINATE_EVIDENCE="${RUN_DIR}/OPERATOR_MAP_COORDINATE_EVIDENCE.json"
GOAL4_DIFF_PLANNER_WS="${GOAL4_DIFF_PLANNER_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/goal4_diff_planner_ws_px4msg}"

deadline=$((SECONDS + 300))
while (( SECONDS < deadline )); do
  state="$(python3 - "${ACTIVE_POINTER}" <<'PY'
import json
import pathlib
import sys

try:
    value = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    value = {}
print(value.get("state", "") if isinstance(value, dict) else "")
PY
)"
  if [[ "${state}" == "running" && -f "${RUN_DIR}/RUN_MANIFEST.json" && -f "${COORDINATE_EVIDENCE}" ]]; then
    break
  fi
  sleep 1
done

if [[ "${state:-}" != "running" ]]; then
  echo "QGC runtime backend did not reach running state for ${RUN_ID}." >&2
  exit 3
fi

mkdir -p "${RESULT_DIR}"
export MOSIM_OPERATOR_RUN_ID="${RUN_ID}"
export ROS_MASTER_URI="${ROS_MASTER_URI:-http://127.0.0.1:11311}"
cd "${PROJECT_ROOT}"
set +u
source /opt/ros/noetic/setup.bash
if [[ -f "${GOAL4_DIFF_PLANNER_WS}/devel/setup.bash" ]]; then
  source "${GOAL4_DIFF_PLANNER_WS}/devel/setup.bash"
fi
set -u

echo "QGC telemetry terminal attached to run ${RUN_ID}."
exec python3 "${PROJECT_ROOT}/Scripts/ui/runtime_sidecar.py" \
  --run-dir "${RUN_DIR}" \
  --manifest "${RUN_DIR}/RUN_MANIFEST.json" \
  --contract "${PROJECT_ROOT}/Config/control_platform/factory_injection_contract.json" \
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
  --coordinate-evidence "${COORDINATE_EVIDENCE}" \
  --skip-actuator-telemetry-readiness \
  --read-only
