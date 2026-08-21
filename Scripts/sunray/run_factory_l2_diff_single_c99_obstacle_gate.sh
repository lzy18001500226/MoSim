#!/usr/bin/env bash
# Factory L2 graphical-C99 single-UAV obstacle-crossing gate.
#
# Static collision truth selects the end points and audits the recorded flight
# afterwards. The live planner still receives only MID360-derived world cloud
# and local occupancy data from the normal Diff/PX4/MAVROS/Gazebo route.

set -euo pipefail

case "${1:-}" in
  "")
    ;;
  -h|--help)
    cat <<'EOF'
Usage: bash Scripts/sunray/run_factory_l2_diff_single_c99_obstacle_gate.sh

Runs the Factory L2 graphical-C99 Diff single-UAV obstacle-crossing gate.
Set RUN_ID or RESULT_DIR before invoking it to choose the evidence location.
EOF
    exit 0
    ;;
  *)
    printf 'Unexpected argument: %s\n' "$1" >&2
    exit 2
    ;;
esac

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RUN_ID="${RUN_ID:-factory_l2_diff_single_c99_obstacle_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
SCENARIO_PATH="${SINGLE_UAV_SCENARIO_PATH:-${RESULT_DIR}/single_uav_obstacle_crossing.json}"
ROUTE_ALTITUDE_M="${ROUTE_ALTITUDE_M:-1.0}"
TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-1200}"
PX4CTRL_HOVER_PERCENTAGE="${PX4CTRL_HOVER_PERCENTAGE:-0.294}"
DIFF_FASTLIO_EKF_FUSION="${DIFF_FASTLIO_EKF_FUSION:-false}"
DIFF_FASTLIO_ALIGNMENT_Z_SOURCE="${DIFF_FASTLIO_ALIGNMENT_Z_SOURCE:-truth}"
# The Factory scenario's z target is absolute MAVROS local odom. Sunray's
# settled home odom is about 0.25 m, so this produces the 1.0 m route hold.
FACTORY_TAKEOFF_HEIGHT_M="${FACTORY_TAKEOFF_HEIGHT_M:-0.75}"
# A Factory launch needs enough wall time to settle at that hold before the
# required three-second simulation-time stability dwell can complete.
FACTORY_TAKEOFF_TIMEOUT_S="${FACTORY_TAKEOFF_TIMEOUT_S:-75}"

FACTORY_WORLD_FILE="${PROJECT_ROOT}/Config/gazebo/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf"
FACTORY_MODEL_PATH="${PROJECT_ROOT}/Config/gazebo/models"
FACTORY_GAZEBO_LAUNCH="${PROJECT_ROOT}/Scripts/sunray/factory_l2_sunray_px4_gazebo.launch"

mkdir -p "${RESULT_DIR}"
python3 "${PROJECT_ROOT}/Scripts/sunray/build_factory_l2_formation_obstacle_scenario.py" \
  --output "${SCENARIO_PATH}"

mapfile -t route_values < <(python3 - "${SCENARIO_PATH}" "${ROUTE_ALTITUDE_M}" <<'PY'
import json
import math
import sys
from pathlib import Path

scenario_path = Path(sys.argv[1])
route_altitude_m = float(sys.argv[2])
if not 0.95 <= route_altitude_m <= 1.15:
    raise SystemExit("ROUTE_ALTITUDE_M must stay inside the Diff command envelope [0.95, 1.15]")

scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
formation = scenario.get("formation") or {}
rigid_path = scenario.get("rigid_center_path_contract") or {}
if rigid_path.get("status") != "passed":
    raise SystemExit("Factory single-UAV route has no passed rigid_center_path_contract")

route = rigid_path.get("center_waypoints_xy_m") or []
start = formation.get("start_center_xy_m")
if len(route) < 2 or not isinstance(start, list) or len(start) < 2:
    raise SystemExit("Factory single-UAV route must contain a spawn point and a traversal waypoint")
if any(abs(float(route[0][axis]) - float(start[axis])) > 0.001 for axis in (0, 1)):
    raise SystemExit("Factory rigid center path does not start at the formation center")

traversal = route[1:]
clearance_m = float(rigid_path.get("clearance_margin_m") or 0.0)

if scenario.get("status") != "static_scenario_ready_runtime_pending":
    raise SystemExit("Factory single-UAV obstacle scenario was not generated successfully")
if len(traversal) < 1:
    raise SystemExit("Factory rigid center path has no traversal waypoint")
if clearance_m <= 0.0:
    raise SystemExit("Factory single-UAV route has no positive clearance contract")

goals = []
for point in traversal:
    if not isinstance(point, list) or len(point) < 2:
        raise SystemExit("Factory rigid center path contains an invalid traversal waypoint")
    x, y = float(point[0]), float(point[1])
    if not all(math.isfinite(value) for value in (x, y)):
        raise SystemExit("Factory single-UAV route coordinates must be finite")
    goals.append(f"{x:.12g},{y:.12g},{route_altitude_m:.12g}")

first_target = traversal[0]
values = [float(start[0]), float(start[1]), float(first_target[0]), float(first_target[1])]
if not all(math.isfinite(value) for value in values):
    raise SystemExit("Factory single-UAV route coordinates must be finite")

for value in (*values, route_altitude_m, clearance_m, ";".join(goals)):
    print(value)
PY
)

if [[ "${#route_values[@]}" -ne 7 ]]; then
  echo "Unable to resolve the Factory single-UAV obstacle route." >&2
  exit 2
fi

START_X="${route_values[0]}"
START_Y="${route_values[1]}"
TARGET_X="${route_values[2]}"
TARGET_Y="${route_values[3]}"
TARGET_Z="${route_values[4]}"
PLANNER_CLEARANCE_M="${route_values[5]}"
GOALS="${route_values[6]}"
GOAL_COUNT="$(awk -F';' '{count=0; for (i=1; i<=NF; i++) if ($i != "") count++; print count}' <<< "${GOALS}")"
RUNTIME_INFLATION_M="${RUNTIME_INFLATION_M:-0.20}"

set +e
env \
  PROJECT_ROOT="${PROJECT_ROOT}" \
  RUN_ID="${RUN_ID}" \
  RESULT_DIR="${RESULT_DIR}" \
  FACTORY_WORLD_MODE=clean \
  WORLD_FILE="${FACTORY_WORLD_FILE}" \
  FACTORY_MODEL_PATH="${FACTORY_MODEL_PATH}" \
  SUNRAY_GAZEBO_LAUNCH_FILE="${FACTORY_GAZEBO_LAUNCH}" \
  SUNRAY_UAV_INIT_X="${START_X}" \
  SUNRAY_UAV_INIT_Y="${START_Y}" \
  SUNRAY_UAV_INIT_Z=0.2 \
  SUNRAY_UAV_INIT_YAW=0.0 \
  GOALS="${GOALS}" \
  TARGET_X="${TARGET_X}" \
  TARGET_Y="${TARGET_Y}" \
  TARGET_Z="${TARGET_Z}" \
  DIFF_INTERACTIVE_AUTO_PASS_GOAL_COUNT="${GOAL_COUNT}" \
  DIFF_INTERACTIVE_TARGET_HOLD_S=5.0 \
  DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S=5.0 \
  DIFF_PUBLISH_HOVER_DURING_TAKEOFF=true \
  DIFF_FASTLIO_EKF_FUSION="${DIFF_FASTLIO_EKF_FUSION}" \
  DIFF_FASTLIO_ALIGNMENT_Z_SOURCE="${DIFF_FASTLIO_ALIGNMENT_Z_SOURCE}" \
  PX4CTRL_CORE_PROFILE=graphical_c99 \
  PX4CTRL_EXPECTED_BUILD_BACKEND=graphical_px4ctrl_c99 \
  PX4CTRL_HOVER_PERCENTAGE="${PX4CTRL_HOVER_PERCENTAGE}" \
  GOAL4_TAKEOFF_HEIGHT="${FACTORY_TAKEOFF_HEIGHT_M}" \
  PX4CTRL_AUTO_TAKEOFF_HEIGHT="${FACTORY_TAKEOFF_HEIGHT_M}" \
  GOAL4_TAKEOFF_TIMEOUT_S="${FACTORY_TAKEOFF_TIMEOUT_S}" \
  EGO_OBSTACLES_INFLATION="${RUNTIME_INFLATION_M}" \
  DIFF_CLICK_STATIC_OBSTACLE_GUARD=true \
  DIFF_CLICK_STATIC_PATH_GUARD=false \
  TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S}" \
  bash "${PROJECT_ROOT}/Scripts/sunray/run_diff_single_auto123_gate.sh"
backend_exit=$?
set -e

clearance_exit=2
if [[ -f "${RESULT_DIR}/truth.csv" ]]; then
  set +e
  python3 "${PROJECT_ROOT}/Scripts/sunray/analyze_swarm_formation_obstacle_clearance.py" \
    --run "${RESULT_DIR}" \
    --scenario "${SCENARIO_PATH}" \
    --uav-ids 1 \
    --truth-file-template truth.csv \
    --execute-phases interactive_goal_review \
    --planner-clearance-m "${PLANNER_CLEARANCE_M}" \
    --output "${RESULT_DIR}/SINGLE_UAV_OBSTACLE_CLEARANCE_GATE.json"
  clearance_exit=$?
  set -e
fi

final_status=$(python3 - "${RESULT_DIR}" "${RUN_ID}" "${SCENARIO_PATH}" "${backend_exit}" "${clearance_exit}" <<'PY'
import json
import sys
from pathlib import Path

result_dir = Path(sys.argv[1])
run_id = sys.argv[2]
scenario_path = Path(sys.argv[3])
backend_exit = int(sys.argv[4])
clearance_exit = int(sys.argv[5])


def status(path: Path) -> str:
    try:
        return str(json.loads(path.read_text(encoding="utf-8")).get("status") or "missing")
    except (OSError, json.JSONDecodeError):
        return "missing"


metrics_path = result_dir / "EGO_SINGLE_METRICS.json"
probe_path = result_dir / "DIFF_INTERACTIVE_GOAL_SWITCH_CHAIN_PROBE.json"
clearance_path = result_dir / "SINGLE_UAV_OBSTACLE_CLEARANCE_GATE.json"
statuses = {
    "mission_metrics": status(metrics_path),
    "goal_switch_probe": status(probe_path),
    "obstacle_clearance": status(clearance_path),
}
passed = (
    backend_exit == 0
    and clearance_exit == 0
    and all(value == "passed" for value in statuses.values())
)
payload = {
    "schema": "mosim.sunray_ros1.factory_l2_diff_single_c99_obstacle_gate.v1",
    "status": "passed" if passed else "blocked",
    "run_id": run_id,
    "scenario": str(scenario_path),
    "controller_core_profile": "graphical_c99",
    "controller_build_backend": "graphical_px4ctrl_c99",
    "px4ctrl_odom_source": "/uav1/mavros/local_position/odom",
    "gazebo_truth_direct_px4ctrl_input_allowed": False,
    "exit_codes": {"backend": backend_exit, "obstacle_clearance": clearance_exit},
    "gate_results": statuses,
    "artifact_refs": [
        {"role": "scenario", "path": str(scenario_path)},
        {"role": "metrics", "path": str(metrics_path)},
        {"role": "raw", "path": str(result_dir / "truth.csv")},
        {"role": "clearance", "path": str(clearance_path)},
    ],
    "claim_boundary": (
        "This proves one Factory L2 graphical-C99 Diff fixed-target single-UAV "
        "obstacle-crossing run only when the live MID360/world-cloud/grid-map planner "
        "path, target hold, and post-flight collision-proxy clearance gate all pass. "
        "Static collision truth selects the route and is used after flight as an oracle; "
        "it is not provided to the live planner or controller."
    ),
}
(result_dir / "SINGLE_UAV_OBSTACLE_GATE.json").write_text(
    json.dumps(payload, indent=2) + "\n", encoding="utf-8"
)
print(payload["status"])
PY
)

if [[ "${final_status}" != "passed" ]]; then
  exit 1
fi
printf '%s\n' "${RESULT_DIR}"
