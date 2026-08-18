#!/usr/bin/env bash
# Start the source-local QGC Plan Goal closure. QGC remains a separate operator
# surface; this wrapper owns the live ROS1/Gazebo/PX4/planner process set and
# exposes the run only after readiness. The legacy Diff mode is retained only
# for its explicit diagnostic profile; the published mode is QGC-focused.

set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
if [ "$#" -ne 1 ]; then
  echo "Usage: bash Scripts/sunray/run_qgc_diff_realtime_goal_gate.sh {rviz_qgc_display_phase1|qgc_realtime_goal|interactive_goal}" >&2
  exit 2
fi

case "$1" in
  rviz_qgc_display_phase1)
    RUN_MODE=rviz_qgc_display_phase1
    EXPECTED_PROFILE_ID=px4ctrl_graphical_c99_factory_rviz_qgc_display_phase1_v1
    EXPECTED_RUNTIME_PROFILE_ID=sunray_ros1_factory_l2_graphical_px4ctrl_c99_rviz_qgc_display_phase1_v1
    RUNTIME_STATUS_FILE_NAME=RVIZ_QGC_DISPLAY_PHASE1_RUNTIME_STATUS.json
    RUNTIME_STATUS_SCHEMA=mosim.rviz_qgc_display_phase1_runtime_status.v1
    ACCEPTANCE_FILE_NAME=RVIZ_QGC_DISPLAY_PHASE1_ACCEPTANCE.json
    ACCEPTANCE_SCHEMA=mosim.rviz_qgc_display_phase1_acceptance.v1
    COMMAND_FILE_NAME=RVIZ_QGC_DISPLAY_PHASE1_COMMAND.txt
    COMMAND_SCHEMA=mosim.rviz_qgc_display_phase1_command.v1
    READY_FILE_NAME=rviz_qgc_display_phase1_ready.txt
    MANUAL_PACKET_FILE_NAME=RVIZ_QGC_DISPLAY_PHASE1_MANUAL_TEST.json
    PLANNER_MAP_EXTENT_FILE_NAME=RVIZ_QGC_DISPLAY_PHASE1_PLANNER_MAP_EXTENT_GATE.json
    PLANNER_MAP_EXTENT_SCHEMA=mosim.rviz_qgc_display_phase1_planner_map_extent_gate.v1
    REASON_PREFIX=rviz_qgc_display_phase1
    TERMINAL_SOURCE=terminal_rviz_qgc_display_phase1_gate
    OPEN_RVIZ_FOR_PHASE=true
    DIFF_OPEN_SPLIT_RVIZ_FOR_PHASE=false
    EGO_VISUALIZATION_FORWARD_ONLY_FOR_PHASE=true
    RVIZ_CONFIG_RELATIVE=Config/rviz/sunray_ros1_goal4_diff_realtime_combined_review.rviz
    ;;
  qgc_realtime_goal)
    RUN_MODE=qgc_realtime_goal
    EXPECTED_PROFILE_ID=px4ctrl_graphical_c99_factory_qgc_realtime_goal_v1
    EXPECTED_RUNTIME_PROFILE_ID=sunray_ros1_factory_l2_graphical_px4ctrl_c99_qgc_realtime_goal_v1
    RUNTIME_STATUS_FILE_NAME=QGC_REALTIME_GOAL_RUNTIME_STATUS.json
    RUNTIME_STATUS_SCHEMA=mosim.qgc_realtime_goal_runtime_status.v1
    ACCEPTANCE_FILE_NAME=QGC_REALTIME_GOAL_ACCEPTANCE.json
    ACCEPTANCE_SCHEMA=mosim.qgc_realtime_goal_acceptance.v1
    COMMAND_FILE_NAME=QGC_REALTIME_GOAL_COMMAND.txt
    COMMAND_SCHEMA=mosim.qgc_realtime_goal_command.v1
    READY_FILE_NAME=qgc_realtime_goal_ready.txt
    PLANNER_MAP_EXTENT_FILE_NAME=QGC_REALTIME_GOAL_PLANNER_MAP_EXTENT_GATE.json
    PLANNER_MAP_EXTENT_SCHEMA=mosim.qgc_realtime_goal_planner_map_extent_gate.v1
    REASON_PREFIX=qgc_realtime_goal
    TERMINAL_SOURCE=terminal_qgc_realtime_goal_gate
    MANUAL_PACKET_FILE_NAME=
    OPEN_RVIZ_FOR_PHASE=false
    DIFF_OPEN_SPLIT_RVIZ_FOR_PHASE=false
    EGO_VISUALIZATION_FORWARD_ONLY_FOR_PHASE=true
    RVIZ_CONFIG_RELATIVE=
    ;;
  interactive_goal)
    RUN_MODE=diff_interactive_goal
    EXPECTED_PROFILE_ID=px4ctrl_graphical_c99_factory_diff_interactive_goal_v1
    EXPECTED_RUNTIME_PROFILE_ID=sunray_ros1_factory_l2_graphical_px4ctrl_c99_diff_interactive_goal_v1
    RUNTIME_STATUS_FILE_NAME=QGC_DIFF_REALTIME_GOAL_RUNTIME_STATUS.json
    RUNTIME_STATUS_SCHEMA=mosim.qgc_diff_realtime_goal_runtime_status.v1
    ACCEPTANCE_FILE_NAME=QGC_DIFF_REALTIME_GOAL_ACCEPTANCE.json
    ACCEPTANCE_SCHEMA=mosim.qgc_diff_realtime_goal_acceptance.v1
    COMMAND_FILE_NAME=QGC_DIFF_REALTIME_GOAL_COMMAND.txt
    COMMAND_SCHEMA=mosim.qgc_diff_realtime_goal_command.v1
    READY_FILE_NAME=qgc_diff_realtime_goal_ready.txt
    PLANNER_MAP_EXTENT_FILE_NAME=QGC_DIFF_PLANNER_MAP_EXTENT_GATE.json
    PLANNER_MAP_EXTENT_SCHEMA=mosim.qgc_diff_planner_map_extent_gate.v1
    REASON_PREFIX=qgc_diff_realtime_goal
    TERMINAL_SOURCE=terminal_qgc_diff_realtime_goal_gate
    MANUAL_PACKET_FILE_NAME=
    OPEN_RVIZ_FOR_PHASE=false
    DIFF_OPEN_SPLIT_RVIZ_FOR_PHASE=false
    EGO_VISUALIZATION_FORWARD_ONLY_FOR_PHASE=true
    RVIZ_CONFIG_RELATIVE=
    ;;
  *)
    echo "Usage: bash Scripts/sunray/run_qgc_diff_realtime_goal_gate.sh {rviz_qgc_display_phase1|qgc_realtime_goal|interactive_goal}" >&2
    exit 2
    ;;
esac
EXPECTED_PLANNER_PROFILE=diff_planner_interactive_goal4_v1

set +u
OPERATOR_RUN_ID=$MOSIM_OPERATOR_RUN_ID
OPERATOR_RUN_DIR=$MOSIM_OPERATOR_RUN_DIR
OPERATOR_RUN_MANIFEST=$MOSIM_OPERATOR_RUN_MANIFEST
set -u
if [ -z "$OPERATOR_RUN_ID" ] || [ -z "$OPERATOR_RUN_DIR" ] || [ -z "$OPERATOR_RUN_MANIFEST" ]; then
  echo "MOSIM_OPERATOR_RUN_ID, MOSIM_OPERATOR_RUN_DIR, and MOSIM_OPERATOR_RUN_MANIFEST are required" >&2
  exit 2
fi
RUN_ID=$OPERATOR_RUN_ID
RESULT_DIR=$PROJECT_ROOT/Results/sunray_ros1/$RUN_ID
RUNTIME_RESULT_DIR=$RESULT_DIR/runtime
RUNTIME_STATUS_FILE="$RESULT_DIR/$RUNTIME_STATUS_FILE_NAME"
ACCEPTANCE_FILE="$RESULT_DIR/$ACCEPTANCE_FILE_NAME"
COMMAND_FILE="$RESULT_DIR/$COMMAND_FILE_NAME"
READY_FILE="$RESULT_DIR/$READY_FILE_NAME"
MANUAL_TEST_PACKET_FILE=
if [ -n "$MANUAL_PACKET_FILE_NAME" ]; then
  MANUAL_TEST_PACKET_FILE="$RESULT_DIR/$MANUAL_PACKET_FILE_NAME"
fi
RVIZ_CONFIG_FOR_PHASE=
if [ -n "$RVIZ_CONFIG_RELATIVE" ]; then
  RVIZ_CONFIG_FOR_PHASE="$PROJECT_ROOT/$RVIZ_CONFIG_RELATIVE"
fi
PLANNER_MAP_EXTENT_FILE="$RESULT_DIR/$PLANNER_MAP_EXTENT_FILE_NAME"
WORLD_RELATIVE=Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf
MODELS_RELATIVE=Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/models
LAUNCH_RELATIVE=Scripts/sunray/factory_l2_sunray_px4_gazebo.launch
QGC_DIFF_FASTLIO_WS="${QGC_DIFF_FASTLIO_WS:-$PROJECT_ROOT/build/ros1/qgc_diff_fastlio_ws}"
QGC_DIFF_FASTLIO_WS="$(readlink -m "$QGC_DIFF_FASTLIO_WS")"
case "$QGC_DIFF_FASTLIO_WS" in
  "$PROJECT_ROOT"/build/ros1/*) ;;
  *)
    echo "QGC_DIFF_FASTLIO_WS must remain below $PROJECT_ROOT/build/ros1" >&2
    exit 2
    ;;
esac
GOAL4_DIFF_PLANNER_WS="${GOAL4_DIFF_PLANNER_WS:-$PROJECT_ROOT/Results/sunray_ros1/workspaces/goal4_diff_planner_ws_px4msg}"
GOAL4_DIFF_PLANNER_WS="$(readlink -m "$GOAL4_DIFF_PLANNER_WS")"
PROJECT_DIFF_SRC="$(readlink -m "$PROJECT_ROOT/src/planning/diff_planner/src")"

ensure_goal4_diff_planner_overlay() {
  local package link expected
  local packages=(
    "plan_env:diff_planner/plan_env"
    "path_searching:diff_planner/path_searching"
    "traj_opt:diff_planner/traj_opt"
    "traj_utils:diff_planner/traj_utils"
    "diff_planner:diff_planner/plan_manage"
    "multipoint:user_command/multipoint"
  )

  if [[ -f "$GOAL4_DIFF_PLANNER_WS/devel/setup.bash" ]]; then
    for package in "${packages[@]}"; do
      link="${package%%:*}"
      expected="${PROJECT_DIFF_SRC}/${package#*:}"
      if [[ ! -L "$GOAL4_DIFF_PLANNER_WS/src/$link" || "$(readlink -m "$GOAL4_DIFF_PLANNER_WS/src/$link")" != "$expected" ]]; then
        break
      fi
    done
    if [[ "$package" == "${packages[-1]}" ]]; then
      return 0
    fi
  fi

  echo "Rebuilding Goal4 Diff-Planner overlay from project-owned source" >&2
  PROJECT_ROOT="$PROJECT_ROOT" DIFF_SRC="$PROJECT_DIFF_SRC" DIFF_WS="$GOAL4_DIFF_PLANNER_WS" \
    bash "$PROJECT_ROOT/Scripts/sunray/setup_goal4_diff_planner_overlay.sh"

  if [[ ! -f "$GOAL4_DIFF_PLANNER_WS/devel/setup.bash" ]]; then
    return 1
  fi
  for package in "${packages[@]}"; do
    link="${package%%:*}"
    expected="${PROJECT_DIFF_SRC}/${package#*:}"
    [[ -L "$GOAL4_DIFF_PLANNER_WS/src/$link" ]] || return 1
    [[ "$(readlink -m "$GOAL4_DIFF_PLANNER_WS/src/$link")" == "$expected" ]] || return 1
  done
}

if ! ensure_goal4_diff_planner_overlay; then
  echo "Goal4 Diff-Planner overlay could not be rebuilt from project-owned source" >&2
  exit 2
fi
QGC_REALTIME_MISSION_READY_TOPIC="${QGC_REALTIME_MISSION_READY_TOPIC:-/mosim/goal4/interactive_goal_ready}"
QGC_REALTIME_WAYPOINT_PLAN_SIZE_TOPIC="${QGC_REALTIME_WAYPOINT_PLAN_SIZE_TOPIC:-/mosim/goal4/interactive_goal_waypoint_count}"
QGC_REALTIME_WAYPOINT_PLAN_SIM_DURATION_S="${QGC_REALTIME_WAYPOINT_PLAN_SIM_DURATION_S:-600}"
QGC_REALTIME_WAYPOINT_PLAN_WALL_STALL_S="${QGC_REALTIME_WAYPOINT_PLAN_WALL_STALL_S:-120}"
if [ -z "$QGC_REALTIME_MISSION_READY_TOPIC" ] || [ -z "$QGC_REALTIME_WAYPOINT_PLAN_SIZE_TOPIC" ]; then
  echo "QGC realtime mission topics must be non-empty" >&2
  exit 2
fi
QGC_INTERACTIVE_REQUIRE_WAYPOINT_PLAN_SIZE=false
if [ "$RUN_MODE" = "qgc_realtime_goal" ]; then
  QGC_INTERACTIVE_REQUIRE_WAYPOINT_PLAN_SIZE=true
fi
WORLD_FILE=$PROJECT_ROOT/$WORLD_RELATIVE
BASE_GAZEBO_MODEL_PATH=$PROJECT_ROOT/$MODELS_RELATIVE
FACTORY_MODEL_PATH_FOR_PHASE=$BASE_GAZEBO_MODEL_PATH
QGC_DIFF_GAZEBO_MODEL_OVERLAY="${QGC_DIFF_GAZEBO_MODEL_OVERLAY:-}"
if [ -n "$QGC_DIFF_GAZEBO_MODEL_OVERLAY" ]; then
  QGC_DIFF_GAZEBO_MODEL_OVERLAY="$(readlink -m "$QGC_DIFF_GAZEBO_MODEL_OVERLAY")"
  case "$QGC_DIFF_GAZEBO_MODEL_OVERLAY" in
    "$PROJECT_ROOT"/Results/*) ;;
    *)
      echo "QGC_DIFF_GAZEBO_MODEL_OVERLAY must remain below $PROJECT_ROOT/Results" >&2
      exit 2
      ;;
  esac
  if [ ! -d "$QGC_DIFF_GAZEBO_MODEL_OVERLAY" ]; then
    echo "QGC_DIFF_GAZEBO_MODEL_OVERLAY is missing: $QGC_DIFF_GAZEBO_MODEL_OVERLAY" >&2
      exit 2
  fi
  FACTORY_MODEL_PATH_FOR_PHASE=$QGC_DIFF_GAZEBO_MODEL_OVERLAY
fi
GAZEBO_MODEL_PATH=$BASE_GAZEBO_MODEL_PATH
if [ -n "$QGC_DIFF_GAZEBO_MODEL_OVERLAY" ]; then
  GAZEBO_MODEL_PATH="$QGC_DIFF_GAZEBO_MODEL_OVERLAY:$GAZEBO_MODEL_PATH"
fi
SUNRAY_GAZEBO_LAUNCH_FILE=$PROJECT_ROOT/$LAUNCH_RELATIVE
SUNRAY_UAV_INIT_X=-10.575025
SUNRAY_UAV_INIT_Y=-19.36313
SUNRAY_UAV_INIT_Z=0.2
SUNRAY_UAV_INIT_YAW=0
# QGC targets and the Factory L2 cloud are in Gazebo world coordinates.  The
# bounded grid below covers the configured spawn and the controlled QGC probe
# target at (2, 0), without changing the PX4-local controller frame.
QGC_DIFF_MAP_SIZE_X=32.0
QGC_DIFF_MAP_SIZE_Y=44.0
QGC_DIFF_MAP_SIZE_Z=2.5
# Keep cold runtime bring-up separate from the interactive contract. A new
# Gazebo/PX4/MAVROS session can consume most of the bounded startup window
# before the planner has created its own topic graph.
STARTUP_TIMEOUT_S=300
READINESS_TIMEOUT_S=300
QGC_DIFF_PLANNER_PARAM_TIMEOUT_S=30
QGC_DIFF_FASTLIO_BUILD_TIMEOUT_S="${QGC_DIFF_FASTLIO_BUILD_TIMEOUT_S:-900}"
if [[ ! "$QGC_DIFF_FASTLIO_BUILD_TIMEOUT_S" =~ ^[1-9][0-9]*$ ]]; then
  echo "QGC_DIFF_FASTLIO_BUILD_TIMEOUT_S must be a positive integer" >&2
  exit 2
fi
QGC_DIFF_FASTLIO_START_TIMEOUT_S="${QGC_DIFF_FASTLIO_START_TIMEOUT_S:-150}"
if [[ ! "$QGC_DIFF_FASTLIO_START_TIMEOUT_S" =~ ^[1-9][0-9]*$ ]]; then
  echo "QGC_DIFF_FASTLIO_START_TIMEOUT_S must be a positive integer" >&2
  exit 2
fi
# The QGC entrypoint has a dedicated cold-start budget: the same source-local
# MID360 stack can require longer than the generic probe before its first pair
# of LiDAR/IMU samples is observable.
QGC_DIFF_FASTLIO_SENSOR_START_TIMEOUT_S="${QGC_DIFF_FASTLIO_SENSOR_START_TIMEOUT_S:-300}"
if [[ ! "$QGC_DIFF_FASTLIO_SENSOR_START_TIMEOUT_S" =~ ^[1-9][0-9]*$ ]]; then
  echo "QGC_DIFF_FASTLIO_SENSOR_START_TIMEOUT_S must be a positive integer" >&2
  exit 2
fi
PX4CTRL_CORE_PROFILE=graphical_c99
PX4CTRL_EXPECTED_BUILD_BACKEND=graphical_px4ctrl_c99
# The QGC interactive profile shares the accepted Factory L2 graphical-C99
# Diff hover map. Keep the generic FAST-LIO and Modelica/base-adapter values
# out of this source-local interactive runtime path.
PX4CTRL_HOVER_PERCENTAGE=0.294
# Factory L2's long-lived MID360 map exceeds PCL's voxel index range at the
# generic 0.02 m resolution. Keep this operator profile on the upstream
# mapping resolution so FAST-LIO remains a timely PX4 EKF input.
FASTLIO_FILTER_SIZE_SURF=0.5
FASTLIO_FILTER_SIZE_MAP=0.5
# Keep PX4 at the source-local real-time default while it completes arming and
# takeoff. A slower rate must be explicitly requested and verified for this
# interactive entrypoint.
QGC_DIFF_PX4_SIM_SPEED_FACTOR="${QGC_DIFF_PX4_SIM_SPEED_FACTOR:-1.0}"
if ! awk -v value="$QGC_DIFF_PX4_SIM_SPEED_FACTOR" 'BEGIN { exit !(value > 0 && value <= 1) }'; then
  echo "QGC_DIFF_PX4_SIM_SPEED_FACTOR must be in (0, 1]" >&2
  exit 2
fi
QGC_DIFF_TAKEOFF_TIMEOUT_S="${QGC_DIFF_TAKEOFF_TIMEOUT_S:-90}"
if ! awk -v value="$QGC_DIFF_TAKEOFF_TIMEOUT_S" 'BEGIN { exit !(value > 0) }'; then
  echo "QGC_DIFF_TAKEOFF_TIMEOUT_S must be positive" >&2
  exit 2
fi
QGC_DIFF_AUTO_PASS_GOAL_COUNT="${QGC_DIFF_AUTO_PASS_GOAL_COUNT:-1}"
if [[ ! "$QGC_DIFF_AUTO_PASS_GOAL_COUNT" =~ ^[1-9][0-9]*$ ]]; then
  echo "QGC_DIFF_AUTO_PASS_GOAL_COUNT must be a positive integer" >&2
  exit 2
fi
QGC_DIFF_FINAL_HOVER_HOLD_S="${QGC_DIFF_FINAL_HOVER_HOLD_S:-8.0}"
if [ "$RUN_MODE" = "rviz_qgc_display_phase1" ]; then
  QGC_DIFF_FINAL_HOVER_HOLD_S="${RVIZ_QGC_DISPLAY_PHASE1_OBSERVATION_HOLD_S:-45.0}"
fi
if ! awk -v value="$QGC_DIFF_FINAL_HOVER_HOLD_S" 'BEGIN { exit !(value > 0) }'; then
  echo "QGC_DIFF_FINAL_HOVER_HOLD_S must be positive" >&2
  exit 2
fi

INNER_PID=
SIDECAR_PID=
GOAL_BRIDGE_PID=
ROSCORE_PID=
INNER_EXIT_CODE=
FINALIZED=false
mkdir -p "$RESULT_DIR" "$RUNTIME_RESULT_DIR"

normalize_reason_code() {
  local value=$1
  printf '%s' "${value/qgc_diff_realtime_goal/$REASON_PREFIX}"
}

write_runtime_status() {
  local state=$1
  local reason_code
  reason_code=$(normalize_reason_code "$2")
  local inner_exit_code=
  if [ "$#" -ge 3 ]; then inner_exit_code=$3; fi
  python3 - "$RUNTIME_STATUS_FILE" "$RUN_ID" "$state" "$reason_code" "$inner_exit_code" "$OPERATOR_RUN_DIR" "$RUNTIME_STATUS_SCHEMA" "$RUN_MODE" "$QGC_REALTIME_MISSION_READY_TOPIC" "$QGC_REALTIME_WAYPOINT_PLAN_SIZE_TOPIC" <<'PY'
import json
import pathlib
import sys
import time

output, run_id, state, reason_code, inner_exit_code, run_dir, schema, run_mode, mission_ready_topic, waypoint_plan_size_topic = sys.argv[1:]
if run_mode == "rviz_qgc_display_phase1":
    transport = {
        "rviz_goal_topic": "/move_base_simple/goal",
        "planner_goal_topic": "/goal_with_id",
        "mission_ready_topic": mission_ready_topic,
        "operator_telemetry_path": f"{run_dir}/telemetry.json",
        "claim_boundary": (
            "This status records the Phase 1 RViz input and QGC display readiness surfaces. "
            "It does not prove that a human observed QGC, that QGC originated a goal, "
            "or that the controller or vehicle passed acceptance."
        ),
    }
else:
    transport = {
        "qgc_request_path": f"{run_dir}/operator_goal/REQUEST.json",
        "qgc_status_path": f"{run_dir}/operator_goal/STATUS.json",
        "goal_topic": "/move_base_simple/goal",
        "adapter_topic": "/goal_with_id",
        "mission_ready_topic": mission_ready_topic,
        "waypoint_plan_size_topic": waypoint_plan_size_topic,
        "claim_boundary": (
            "This status records the live runtime wrapper and transport surfaces. "
            "It does not prove that a user selected a QGC goal, that the planner "
            "accepted it, or that the controller/vehicle reached it."
        ),
    }
payload = {
    "schema": schema,
    "run_id": run_id,
    "state": state,
    "reason_code": reason_code,
    "updated_at_unix_s": time.time(),
    "operator_run_directory": run_dir,
    "transport": transport,
}
if inner_exit_code:
    try:
        payload["inner_exit_code"] = int(inner_exit_code)
    except ValueError:
        payload["inner_exit_code"] = inner_exit_code
path = pathlib.Path(output)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
}

verify_qgc_goal_acceptance() {
  python3 - \
    "$RUNTIME_RESULT_DIR/EGO_SINGLE_METRICS.json" \
    "$OPERATOR_RUN_DIR/operator_goal/REQUEST.json" \
    "$OPERATOR_RUN_DIR/operator_goal/STATUS.json" \
    "$OPERATOR_RUN_DIR/telemetry.json" \
    "$ACCEPTANCE_FILE" \
    "$RUN_ID" \
    "$ACCEPTANCE_SCHEMA" \
    "$REASON_PREFIX" <<'PY'
import json
import math
import pathlib
import sys

metrics_path, goal_request_path, goal_status_path, telemetry_path, output_path, run_id, schema, reason_prefix = sys.argv[1:]
metrics_path = pathlib.Path(metrics_path)
goal_request_path = pathlib.Path(goal_request_path)
goal_status_path = pathlib.Path(goal_status_path)
telemetry_path = pathlib.Path(telemetry_path)
output_path = pathlib.Path(output_path)
run_id = str(run_id)
blockers = []

def load_object(path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        blockers.append(f"unreadable_{path.name}:{exc.__class__.__name__}")
        return {}
    if not isinstance(value, dict):
        blockers.append(f"invalid_{path.name}_object")
        return {}
    return value

metrics = load_object(metrics_path)
goal_request = load_object(goal_request_path)
goal_status = load_object(goal_status_path)
telemetry = load_object(telemetry_path)

def nonnegative_int(value):
    try:
        count = int(value)
    except (TypeError, ValueError):
        return None
    return count if count >= 0 else None

request_id = goal_request.get("request_id")
request_kind = ""
expected_waypoint_count = None
if (
    goal_request.get("schema") == "mosim.qgc_realtime_goal_request.v2"
    and goal_request.get("source") == "qgc_mission_waypoint_plan"
):
    request_kind = "waypoint_plan"
    requested_waypoints = goal_request.get("waypoints")
    if not isinstance(requested_waypoints, list) or not requested_waypoints:
        blockers.append("qgc_waypoint_plan_request_items_invalid")
    else:
        expected_waypoint_count = len(requested_waypoints)
elif (
    goal_request.get("schema") == "mosim.qgc_realtime_goal_request.v1"
    and goal_request.get("source") == "qgc_plan_view"
    and isinstance(goal_request.get("goal"), dict)
):
    request_kind = "single_goal"
    expected_waypoint_count = 1
else:
    blockers.append("qgc_goal_request_identity_invalid")
if not isinstance(request_id, str) or not request_id:
    blockers.append("qgc_goal_request_id_missing")

if metrics.get("run_terminal_status") != "interactive_passed" or metrics.get("status") != "passed":
    blockers.append("interactive_mission_not_passed")
if metrics.get("blockers"):
    blockers.append("interactive_mission_has_blockers")
counts = metrics.get("counts") if isinstance(metrics.get("counts"), dict) else {}
forwarded_goal_count = nonnegative_int(metrics.get("forwarded_goal_count"))
if forwarded_goal_count is None or forwarded_goal_count < (expected_waypoint_count or 1):
    blockers.append("forwarded_goal_missing")
if int(counts.get("polytraj", 0) or 0) < 1:
    blockers.append("planner_future_polytraj_missing")
if int(counts.get("planner_position_cmd", 0) or 0) < 1:
    blockers.append("planner_position_command_missing")
handoffs = metrics.get("interactive_goal_handoffs")
if not isinstance(handoffs, list) or len(handoffs) < (expected_waypoint_count or 1):
    blockers.append("interactive_goal_handoff_missing")
final_hover = metrics.get("interactive_final_hover")
if not isinstance(final_hover, dict) or final_hover.get("reached") is not True:
    blockers.append("interactive_final_hover_not_reached")

if (
    goal_status.get("run_id") != run_id
    or goal_status.get("state") != "forwarded"
    or goal_status.get("request_id") != request_id
):
    blockers.append("qgc_goal_transport_not_forwarded")
details = goal_status.get("details") if isinstance(goal_status.get("details"), dict) else {}
if details.get("transport") != "live_ros1":
    blockers.append("qgc_goal_transport_not_live_ros1")
if details.get("request_kind") != request_kind:
    blockers.append("qgc_goal_request_kind_mismatch")
status_waypoint_count = nonnegative_int(details.get("waypoint_count"))
forwarded_waypoint_count = nonnegative_int(details.get("forwarded_waypoint_count"))
if expected_waypoint_count is None or status_waypoint_count != expected_waypoint_count:
    blockers.append("qgc_goal_waypoint_count_mismatch")
if expected_waypoint_count is None or forwarded_waypoint_count != expected_waypoint_count:
    blockers.append("qgc_waypoint_plan_not_fully_forwarded")
if request_kind == "waypoint_plan":
    interactive_plan = metrics.get("interactive_waypoint_plan")
    interactive_plan = interactive_plan if isinstance(interactive_plan, dict) else {}
    if interactive_plan.get("expected_goal_count") != expected_waypoint_count:
        blockers.append("qgc_waypoint_plan_completion_size_mismatch")
    if forwarded_goal_count is None or forwarded_goal_count < expected_waypoint_count:
        blockers.append("qgc_waypoint_plan_mission_goal_missing")
    if not isinstance(handoffs, list) or len(handoffs) < expected_waypoint_count:
        blockers.append("qgc_waypoint_plan_mission_handoff_missing")
goal = details.get("goal") if isinstance(details.get("goal"), dict) else {}
goal_position = goal.get("position") if isinstance(goal.get("position"), dict) else {}
if goal.get("frame_id") != "world" or not all(key in goal_position for key in ("x", "y")):
    blockers.append("qgc_goal_world_coordinate_missing")
if (
    goal.get("waypoint_count") != expected_waypoint_count
    or goal.get("waypoint_index") != (expected_waypoint_count - 1 if expected_waypoint_count else None)
):
    blockers.append("qgc_goal_final_waypoint_metadata_mismatch")

map_state = telemetry.get("map_state") if isinstance(telemetry.get("map_state"), dict) else {}
if telemetry.get("run_id") != run_id or map_state.get("run_id") != run_id:
    blockers.append("operator_map_run_identity_mismatch")
map_info = map_state.get("map") if isinstance(map_state.get("map"), dict) else {}
map_data_status = map_state.get("map_data_status") if isinstance(map_state.get("map_data_status"), dict) else {}
if map_info.get("coordinate_contract_status") != "verified":
    blockers.append("operator_map_coordinate_contract_unverified")
if map_data_status.get("state") != "accepted":
    blockers.append("operator_map_frame_not_accepted")
task_paths = map_state.get("task_paths") if isinstance(map_state.get("task_paths"), dict) else {}
expected = task_paths.get("expected") if isinstance(task_paths.get("expected"), dict) else {}
future = task_paths.get("future") if isinstance(task_paths.get("future"), dict) else {}
if expected.get("status") != "available" or len(expected.get("points", [])) < 2:
    blockers.append("operator_expected_path_missing")
if future.get("status") != "available" or len(future.get("points", [])) < 2:
    blockers.append("operator_future_path_missing")
if future.get("frame_id") != "mworks_world":
    blockers.append("operator_future_path_frame_mismatch")
forwarded_at = float(goal_status.get("updated_at_unix_s", 0.0) or 0.0)
if float(future.get("updated_at", 0.0) or 0.0) < forwarded_at:
    blockers.append("operator_future_path_not_updated_after_qgc_goal")
expected_points = expected.get("points") if isinstance(expected.get("points"), list) else []
if expected_points and goal_position:
    endpoint = expected_points[-1] if isinstance(expected_points[-1], dict) else {}
    try:
        endpoint_error = math.hypot(
            float(endpoint["x"]) - float(goal_position["x"]),
            float(endpoint["y"]) - float(goal_position["y"]),
        )
    except (KeyError, TypeError, ValueError):
        blockers.append("operator_expected_path_endpoint_invalid")
    else:
        if endpoint_error > 1.0e-3:
            blockers.append("operator_expected_path_goal_mismatch")
actual_tracks = map_state.get("actual_tracks") if isinstance(map_state.get("actual_tracks"), dict) else {}
actual_track = actual_tracks.get("uav1") if isinstance(actual_tracks.get("uav1"), dict) else {}
if actual_track.get("status") != "available" or len(actual_track.get("points", [])) < 2:
    blockers.append("operator_actual_track_missing")
if float(actual_track.get("updated_at", 0.0) or 0.0) < forwarded_at:
    blockers.append("operator_actual_track_not_updated_after_qgc_goal")

payload = {
    "schema": schema,
    "run_id": run_id,
    "status": "passed" if not blockers else "blocked",
    "reason_code": f"{reason_prefix}_acceptance_verified" if not blockers else f"{reason_prefix}_acceptance_unverified",
    "blockers": blockers,
    "evidence": {
        "mission_metrics": str(metrics_path),
        "qgc_goal_request": str(goal_request_path),
        "qgc_goal_status": str(goal_status_path),
        "operator_telemetry": str(telemetry_path),
        "requested_waypoint_count": expected_waypoint_count,
        "status_forwarded_waypoint_count": forwarded_waypoint_count,
        "forwarded_goal_count": metrics.get("forwarded_goal_count"),
        "planner_polytraj_count": counts.get("polytraj"),
        "planner_position_command_count": counts.get("planner_position_cmd"),
        "future_path_updated_at_unix_s": future.get("updated_at"),
        "actual_track_updated_at_unix_s": actual_track.get("updated_at"),
    },
    "claim_boundary": (
        "This validates the run-bound live ROS1 goal transport, planner output, mission stability, "
        "and operator-map telemetry. A separate native QGC screenshot is required to claim visual observation."
    ),
}
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
raise SystemExit(0 if not blockers else 1)
PY
}

write_phase1_manual_test_packet() {
  python3 "$PROJECT_ROOT/Scripts/sunray/rviz_qgc_display_phase1.py" manual-packet \
    --run-id "$RUN_ID" \
    --profile-id "$EXPECTED_PROFILE_ID" \
    --runtime-profile-id "$EXPECTED_RUNTIME_PROFILE_ID" \
    --rviz-config "$RVIZ_CONFIG_FOR_PHASE" \
    --result-directory "$RESULT_DIR" \
    --operator-run-directory "$OPERATOR_RUN_DIR" \
    --output "$MANUAL_TEST_PACKET_FILE"
}

verify_rviz_qgc_display_phase1_acceptance() {
  python3 "$PROJECT_ROOT/Scripts/sunray/rviz_qgc_display_phase1.py" evaluate \
    --run-id "$RUN_ID" \
    --metrics "$RUNTIME_RESULT_DIR/EGO_SINGLE_METRICS.json" \
    --adapter "$RUNTIME_RESULT_DIR/clicked_goal_adapter.json" \
    --telemetry "$OPERATOR_RUN_DIR/telemetry.json" \
    --output "$ACCEPTANCE_FILE" \
    --schema "$ACCEPTANCE_SCHEMA"
}

collect_process_tree() {
  local parent_pid=$1
  local child_pid
  while IFS= read -r child_pid; do
    [[ "${child_pid}" =~ ^[0-9]+$ ]] || continue
    collect_process_tree "${child_pid}"
    printf '%s\n' "${child_pid}"
  done < <(pgrep -P "${parent_pid}" 2>/dev/null || true)
}

stop_process() {
  local variable_name=$1
  local pid=
  local tree_pid
  local alive
  local -a process_tree=()
  case "$variable_name" in
    SIDECAR_PID) pid=$SIDECAR_PID ;;
    GOAL_BRIDGE_PID) pid=$GOAL_BRIDGE_PID ;;
    INNER_PID) pid=$INNER_PID ;;
    ROSCORE_PID) pid=$ROSCORE_PID ;;
    *) return 1 ;;
  esac
  if [ -z "$pid" ] || ! kill -0 "$pid" 2>/dev/null; then
    case "$variable_name" in
      SIDECAR_PID) SIDECAR_PID= ;;
      GOAL_BRIDGE_PID) GOAL_BRIDGE_PID= ;;
      INNER_PID) INNER_PID= ;;
      ROSCORE_PID) ROSCORE_PID= ;;
    esac
    return
  fi
  while IFS= read -r tree_pid; do
    [[ "${tree_pid}" =~ ^[0-9]+$ ]] || continue
    process_tree+=("${tree_pid}")
  done < <(collect_process_tree "${pid}")
  process_tree+=("${pid}")

  for tree_pid in "${process_tree[@]}"; do
    kill -INT "${tree_pid}" 2>/dev/null || true
  done
  for _ in $(seq 1 30); do
    alive=false
    for tree_pid in "${process_tree[@]}"; do
      if kill -0 "${tree_pid}" 2>/dev/null; then
        alive=true
        break
      fi
    done
    if [ "${alive}" = false ]; then break; fi
    sleep 0.25
  done
  for tree_pid in "${process_tree[@]}"; do
    if kill -0 "${tree_pid}" 2>/dev/null; then
      kill -TERM "${tree_pid}" 2>/dev/null || true
    fi
  done
  sleep 1
  for tree_pid in "${process_tree[@]}"; do
    if kill -0 "${tree_pid}" 2>/dev/null; then
      kill -KILL "${tree_pid}" 2>/dev/null || true
    fi
  done
  wait "$pid" 2>/dev/null || true
  case "$variable_name" in
    SIDECAR_PID) SIDECAR_PID= ;;
    GOAL_BRIDGE_PID) GOAL_BRIDGE_PID= ;;
    INNER_PID) INNER_PID= ;;
    ROSCORE_PID) ROSCORE_PID= ;;
  esac
}

finalize_operator_run() {
  local terminal_state=$1
  local reason_code
  reason_code=$(normalize_reason_code "$2")
  if [ "$FINALIZED" = true ]; then return; fi
  python3 "$PROJECT_ROOT/Scripts/ui/prepare_operator_run.py" \
    --finalize-active \
    --expected-run-id "$OPERATOR_RUN_ID" \
    --terminal-state "$terminal_state" \
    --reason-code "$reason_code" \
    --terminal-source "$TERMINAL_SOURCE" \
    > "$RESULT_DIR/qgc_operator_run_finalize.log" 2>&1 || true
  FINALIZED=true
}

cleanup() {
  local exit_code=$?
  set +e
  stop_process GOAL_BRIDGE_PID
  stop_process SIDECAR_PID
  stop_process INNER_PID
  stop_process ROSCORE_PID
  if [ "$FINALIZED" != true ]; then
    write_runtime_status blocked qgc_diff_realtime_goal_wrapper_stopped "$exit_code"
    finalize_operator_run blocked qgc_diff_realtime_goal_wrapper_stopped
  fi
  trap - EXIT
  exit "$exit_code"
}

# The visible Windows terminal can emit SIGHUP while the run is still valid.
# Keep the runtime process tree alive in that case; Ctrl+C and TERM remain
# explicit operator stop paths and still flow through cleanup.
trap '' HUP
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

python3 - "$PROJECT_ROOT" "$RUN_ID" "$OPERATOR_RUN_DIR" "$OPERATOR_RUN_MANIFEST" \
  "$EXPECTED_PROFILE_ID" "$EXPECTED_RUNTIME_PROFILE_ID" "$EXPECTED_PLANNER_PROFILE" <<'PY'
import json
import pathlib
import sys

root, run_id, run_dir_value, manifest_value, expected_profile_id, expected_runtime_profile_id, expected_planner_profile = sys.argv[1:]
root = pathlib.Path(root).resolve()
run_dir = pathlib.Path(run_dir_value).resolve()
manifest_path = pathlib.Path(manifest_value).resolve()
expected_dir = (root / "Results" / "runs" / run_id).resolve()
if run_dir != expected_dir or manifest_path != expected_dir / "RUN_MANIFEST.json":
    raise SystemExit("qgc_diff_realtime_goal_operator_path_mismatch")
try:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    raise SystemExit(f"qgc_diff_realtime_goal_manifest_unreadable:{exc}") from exc
if not isinstance(manifest, dict) or manifest.get("run_id") != run_id:
    raise SystemExit("qgc_diff_realtime_goal_manifest_identity_mismatch")
if manifest.get("experiment_profile_id") != expected_profile_id:
    raise SystemExit("qgc_diff_realtime_goal_profile_mismatch")
if manifest.get("runtime_profile_id") != expected_runtime_profile_id:
    raise SystemExit("qgc_diff_realtime_goal_runtime_profile_mismatch")
if manifest.get("planner_profile") != expected_planner_profile:
    raise SystemExit("qgc_diff_realtime_goal_planner_profile_mismatch")
if manifest.get("operator_map_snapshot", {}).get("map_id") != "factory_l2":
    raise SystemExit("qgc_diff_realtime_goal_factory_map_required")
PY

if [ ! -f "$WORLD_FILE" ] || [ ! -f "$SUNRAY_GAZEBO_LAUNCH_FILE" ] || [ ! -d "$BASE_GAZEBO_MODEL_PATH" ]; then
  echo "Factory L2 runtime source is incomplete" >&2
  write_runtime_status blocked qgc_diff_realtime_goal_factory_runtime_source_missing
  finalize_operator_run blocked qgc_diff_realtime_goal_factory_runtime_source_missing
  exit 3
fi

bash "$PROJECT_ROOT/Scripts/sunray/check_sunray_ros1_runtime_preflight.sh" \
  > "$RESULT_DIR/qgc_diff_runtime_preflight.log" 2>&1

python3 "$PROJECT_ROOT/Scripts/ui/prepare_factory_live_operator_map.py" \
  --run-dir "$OPERATOR_RUN_DIR" \
  --manifest "$OPERATOR_RUN_MANIFEST" \
  --world-file "$WORLD_FILE" \
  --gazebo-launch-file "$SUNRAY_GAZEBO_LAUNCH_FILE" \
  > "$RESULT_DIR/qgc_factory_map_prepare.log" 2>&1

RUNTIME_OVERLAY_WORKSPACE="$PROJECT_ROOT/build/ros1/runtime_overlays/$RUN_ID"
if ! bash "$PROJECT_ROOT/Scripts/sunray/prepare_local_ros1_runtime_overlay.sh" \
  --workspace "$RUNTIME_OVERLAY_WORKSPACE" \
  > "$RESULT_DIR/local_runtime_overlay.log" 2>&1; then
  write_runtime_status blocked qgc_diff_realtime_goal_runtime_overlay_prepare_failed
  finalize_operator_run blocked qgc_diff_realtime_goal_runtime_overlay_prepare_failed
  exit 3
fi
LOCAL_ROS1_DEVEL="$PROJECT_ROOT/build/ros1/local_source_ws/devel"
if [ ! -f "$LOCAL_ROS1_DEVEL/setup.bash" ]; then
  write_runtime_status blocked qgc_diff_realtime_goal_local_ros1_setup_missing
  finalize_operator_run blocked qgc_diff_realtime_goal_local_ros1_setup_missing
  exit 3
fi
if [ -L "$RUNTIME_OVERLAY_WORKSPACE/devel" ]; then
  if [ "$(readlink -f "$RUNTIME_OVERLAY_WORKSPACE/devel")" != "$(readlink -f "$LOCAL_ROS1_DEVEL")" ]; then
    write_runtime_status blocked qgc_diff_realtime_goal_runtime_overlay_devel_link_mismatch
    finalize_operator_run blocked qgc_diff_realtime_goal_runtime_overlay_devel_link_mismatch
    exit 3
  fi
elif [ ! -e "$RUNTIME_OVERLAY_WORKSPACE/devel" ]; then
  if ! ln -s "$LOCAL_ROS1_DEVEL" "$RUNTIME_OVERLAY_WORKSPACE/devel"; then
    write_runtime_status blocked qgc_diff_realtime_goal_runtime_overlay_devel_link_create_failed
    finalize_operator_run blocked qgc_diff_realtime_goal_runtime_overlay_devel_link_create_failed
    exit 3
  fi
else
  write_runtime_status blocked qgc_diff_realtime_goal_runtime_overlay_devel_path_invalid
  finalize_operator_run blocked qgc_diff_realtime_goal_runtime_overlay_devel_path_invalid
  exit 3
fi

set +u
source /opt/ros/noetic/setup.bash
source "$PROJECT_ROOT/Scripts/sunray/resolve_local_ros1_runtime.sh"
source "$LOCAL_ROS1_WS/devel/setup.bash"
set -u

prepare_qgc_fastlio_workspace() {
  local local_src="$LOCAL_ROS1_WS/src"
  local catkin_toplevel=/opt/ros/noetic/share/catkin/cmake/toplevel.cmake
  local catkin_link="$QGC_DIFF_FASTLIO_WS/src/CMakeLists.txt"
  local fastlio_link fastlio_source legacy_link legacy_path expected_source resolved_source

  [[ -d "$local_src" ]] || {
    echo "Local ROS1 source workspace is missing: $local_src" >&2
    return 1
  }
  {
    echo "LOCAL_ROS1_WS=$LOCAL_ROS1_WS"
    echo "QGC_DIFF_FASTLIO_WS=$QGC_DIFF_FASTLIO_WS"
    for legacy_link in FAST_LIO livox_ros_driver_compat; do
      legacy_path="$local_src/$legacy_link"
      case "$legacy_link" in
        FAST_LIO) expected_source="$PROJECT_ROOT/src/perception/fast_lio" ;;
        livox_ros_driver_compat) expected_source="$PROJECT_ROOT/src/perception/livox_ros_driver_compat" ;;
      esac
      if [[ -L "$legacy_path" ]]; then
        resolved_source="$(readlink -f "$legacy_path")"
        if [[ "$resolved_source" != "$expected_source" ]]; then
          echo "unexpected_stale_fastlio_link=$legacy_path->$resolved_source"
          return 1
        fi
        rm -f "$legacy_path"
        echo "removed_stale_local_fastlio_link=$legacy_path->$resolved_source"
      elif [[ -e "$legacy_path" ]]; then
        echo "unexpected_nonlink=$legacy_path"
        return 1
      else
        echo "no_stale_local_fastlio_link=$legacy_path"
      fi
    done

    [[ -f "$catkin_toplevel" ]] || {
      echo "catkin_toplevel_missing=$catkin_toplevel"
      return 1
    }
    mkdir -p "$QGC_DIFF_FASTLIO_WS/src"
    for legacy_link in FAST_LIO livox_ros_driver_compat; do
      case "$legacy_link" in
        FAST_LIO) fastlio_source="$PROJECT_ROOT/src/perception/fast_lio" ;;
        livox_ros_driver_compat) fastlio_source="$PROJECT_ROOT/src/perception/livox_ros_driver_compat" ;;
      esac
      fastlio_link="$QGC_DIFF_FASTLIO_WS/src/$legacy_link"
      [[ -d "$fastlio_source" ]] || {
        echo "fastlio_source_missing=$fastlio_source"
        return 1
      }
      if [[ -L "$fastlio_link" ]]; then
        resolved_source="$(readlink -f "$fastlio_link")"
        if [[ "$resolved_source" != "$fastlio_source" ]]; then
          echo "unexpected_fastlio_source_link=$fastlio_link->$resolved_source"
          return 1
        fi
        echo "reused_fastlio_source_link=$fastlio_link->$resolved_source"
      elif [[ -e "$fastlio_link" ]]; then
        echo "unexpected_fastlio_source_path=$fastlio_link"
        return 1
      else
        ln -s "$fastlio_source" "$fastlio_link"
        echo "created_fastlio_source_link=$fastlio_link->$fastlio_source"
      fi
    done
    if [[ -L "$catkin_link" ]]; then
      resolved_source="$(readlink -f "$catkin_link")"
      if [[ "$resolved_source" != "$catkin_toplevel" ]]; then
        echo "unexpected_fastlio_catkin_link=$catkin_link->$resolved_source"
        return 1
      fi
      echo "reused_fastlio_catkin_link=$catkin_link"
    elif [[ -e "$catkin_link" ]]; then
      echo "unexpected_fastlio_catkin_file=$catkin_link"
      return 1
    else
      ln -s "$catkin_toplevel" "$catkin_link"
      echo "created_fastlio_catkin_link=$catkin_link"
    fi
  } > "$RESULT_DIR/qgc_fastlio_workspace_guard.log"
}

if ! prepare_qgc_fastlio_workspace; then
  write_runtime_status blocked qgc_diff_realtime_goal_fastlio_workspace_guard_failed
  finalize_operator_run blocked qgc_diff_realtime_goal_fastlio_workspace_guard_failed
  exit 3
fi

if ! timeout "${QGC_DIFF_FASTLIO_BUILD_TIMEOUT_S}s" bash -c '
  set -euo pipefail
  source /opt/ros/noetic/setup.bash
  cd "$1"
  catkin_make --only-pkg-with-deps livox_ros_driver fast_lio
' bash "$QGC_DIFF_FASTLIO_WS" > "$RESULT_DIR/qgc_fastlio_prebuild.log" 2>&1; then
  write_runtime_status blocked qgc_diff_realtime_goal_fastlio_prebuild_failed
  finalize_operator_run blocked qgc_diff_realtime_goal_fastlio_prebuild_failed
  exit 3
fi

start_qgc_roscore() {
  local deadline=$((SECONDS + 30))
  local probe_log="$RUNTIME_RESULT_DIR/qgc_roscore_probe.log"

  mkdir -p "$RUNTIME_RESULT_DIR/ros_log"
  export ROS_LOG_DIR="$RUNTIME_RESULT_DIR/ros_log"
  if timeout 3s rosnode list > "$probe_log" 2>&1; then
    echo "qgc_diff_realtime_goal_existing_ros_master" >&2
    return 1
  fi
  roscore > "$RUNTIME_RESULT_DIR/qgc_roscore.log" 2>&1 &
  ROSCORE_PID=$!
  while (( SECONDS < deadline )); do
    if ! kill -0 "$ROSCORE_PID" 2>/dev/null; then
      wait "$ROSCORE_PID" 2>/dev/null || true
      ROSCORE_PID=
      return 1
    fi
    if timeout 3s rosnode list > "$probe_log" 2>&1; then
      printf 'roscore_pid=%s\n' "$ROSCORE_PID" > "$RUNTIME_RESULT_DIR/qgc_roscore_ready.txt"
      return 0
    fi
    sleep 0.5
  done
  return 1
}

if ! start_qgc_roscore; then
  write_runtime_status blocked qgc_diff_realtime_goal_roscore_start_failed
  finalize_operator_run blocked qgc_diff_realtime_goal_roscore_start_failed
  exit 3
fi

{
  echo "schema=$COMMAND_SCHEMA"
  echo "run_id=$RUN_ID"
  echo "operator_run_dir=$OPERATOR_RUN_DIR"
  echo "planner_variant=diff_planner"
  echo "fastlio_workspace=$QGC_DIFF_FASTLIO_WS"
  echo "fastlio_build_timeout_s=$QGC_DIFF_FASTLIO_BUILD_TIMEOUT_S"
  echo "fastlio_sensor_start_timeout_s=$QGC_DIFF_FASTLIO_SENSOR_START_TIMEOUT_S"
  echo "px4_sim_speed_factor=$QGC_DIFF_PX4_SIM_SPEED_FACTOR"
  echo "gazebo_model_overlay=${QGC_DIFF_GAZEBO_MODEL_OVERLAY:-none}"
  echo "factory_model_path=$FACTORY_MODEL_PATH_FOR_PHASE"
  echo "rviz_config=${RVIZ_CONFIG_FOR_PHASE:-none}"
  echo "takeoff_timeout_s=$QGC_DIFF_TAKEOFF_TIMEOUT_S"
  echo "publish_hover_during_takeoff=true"
  if [ "$RUN_MODE" = "rviz_qgc_display_phase1" ]; then
    echo "phase=phase_1_rviz_goal_to_qgc_display"
    echo "rviz_input_topic=/move_base_simple/goal"
    echo "qgc_input=display_only"
    echo "qgc_plan_goal=disabled_for_phase_1"
    echo "manual_test_packet=$MANUAL_TEST_PACKET_FILE"
  else
    echo "qgc_input_topic=/move_base_simple/goal"
    echo "qgc_goal_bridge=runtime_managed"
  fi
  echo "planner_input_topic=/goal_with_id"
  echo "replay_transport=disabled"
  echo "manual_stop=Ctrl+C in this visible terminal"
} > "$COMMAND_FILE"

run_inner_gate() {
  cd "$PROJECT_ROOT"
  RUN_ID="$RUN_ID" \
  RESULT_DIR="$RUNTIME_RESULT_DIR" \
  WORLD_FILE="$WORLD_FILE" \
  GAZEBO_MODEL_PATH="$GAZEBO_MODEL_PATH" \
  SUNRAY_GAZEBO_LAUNCH_FILE="$SUNRAY_GAZEBO_LAUNCH_FILE" \
  SUNRAY_UAV_INIT_X="$SUNRAY_UAV_INIT_X" \
  SUNRAY_UAV_INIT_Y="$SUNRAY_UAV_INIT_Y" \
  SUNRAY_UAV_INIT_Z="$SUNRAY_UAV_INIT_Z" \
  SUNRAY_UAV_INIT_YAW="$SUNRAY_UAV_INIT_YAW" \
  PX4CTRL_CORE_PROFILE="$PX4CTRL_CORE_PROFILE" \
  PX4CTRL_EXPECTED_BUILD_BACKEND="$PX4CTRL_EXPECTED_BUILD_BACKEND" \
  PX4CTRL_HOVER_PERCENTAGE="$PX4CTRL_HOVER_PERCENTAGE" \
  SUNRAY_GPS_SENSOR_MODE=removed \
  PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=true \
  PX4CTRL_EKF2_EV_CTRL_OVERRIDE=15 \
  PX4CTRL_EKF2_HGT_REF_OVERRIDE=3 \
  PX4CTRL_ODOM_SOURCE=mavros_local \
  GOAL4_DIFF_PLANNER_WS="$GOAL4_DIFF_PLANNER_WS" \
  PRESERVE_EXISTING_ROSCORE=true \
  FASTLIO_WS="$QGC_DIFF_FASTLIO_WS" \
  FASTLIO_FILTER_SIZE_SURF="$FASTLIO_FILTER_SIZE_SURF" \
  FASTLIO_FILTER_SIZE_MAP="$FASTLIO_FILTER_SIZE_MAP" \
  FASTLIO_ALIGNMENT_Z_SOURCE=truth \
  FASTLIO_ALIGNMENT_REFERENCE=config \
  FASTLIO_ALIGNMENT_REQUIRED=true \
  FASTLIO_SENSOR_START_TIMEOUT_S="$QGC_DIFF_FASTLIO_SENSOR_START_TIMEOUT_S" \
  FASTLIO_START_TIMEOUT_S="$QGC_DIFF_FASTLIO_START_TIMEOUT_S" \
  REVIEW_START_FASTLIO=true \
  PX4CTRL_SUNRAY150_IMU_CALIBRATION_ENABLED=false \
  PX4_SIM_SPEED_FACTOR="$QGC_DIFF_PX4_SIM_SPEED_FACTOR" \
  GOAL4_TAKEOFF_TIMEOUT_S="$QGC_DIFF_TAKEOFF_TIMEOUT_S" \
  PLANNER_VARIANT=diff_planner \
  DIFF_INTERACTIVE_CLICK_GOAL=true \
  DIFF_INTERACTIVE_GOAL_READY_TOPIC="$QGC_REALTIME_MISSION_READY_TOPIC" \
  DIFF_INTERACTIVE_WAYPOINT_PLAN_SIZE_TOPIC="$QGC_REALTIME_WAYPOINT_PLAN_SIZE_TOPIC" \
  DIFF_INTERACTIVE_REQUIRE_WAYPOINT_PLAN_SIZE="$QGC_INTERACTIVE_REQUIRE_WAYPOINT_PLAN_SIZE" \
  DIFF_AUTO_GOAL_IN_INTERACTIVE_REVIEW=false \
  DIFF_INTERACTIVE_REVIEW_HOLD_S=0 \
  DIFF_INTERACTIVE_AUTO_PASS_GOAL_COUNT="$QGC_DIFF_AUTO_PASS_GOAL_COUNT" \
  DIFF_INTERACTIVE_FINAL_HOVER_HOLD_S="$QGC_DIFF_FINAL_HOVER_HOLD_S" \
  DIFF_USE_MULTIPOINT=false \
  DIFF_CLICK_MAX_GOAL_DISTANCE_XY=0 \
  DIFF_CLICK_READY_Z_TOL=0.30 \
  DIFF_CLICK_STATIC_PATH_GUARD=false \
  DIFF_INTERACTIVE_YAW_SCAN_ENABLE=true \
  DIFF_INTERACTIVE_YAW_SCAN_AFTER_GOAL=true \
  DIFF_INTERACTIVE_YAW_SCAN_REENABLE_CMD_ADAPTER=false \
  DIFF_PUBLISH_HOVER_DURING_TAKEOFF=true \
  DIFF_PUBLISH_HOVER_DURING_TAKEOFF_DELAY_S=0.5 \
  DIFF_GOAL4_COMMON_WORLD_FRAME=true \
  DIFF_CMD_SMOOTH_ENABLE=true \
  DIFF_CMD_SMOOTH_MAX_SPEED_MPS=0.6 \
  DIFF_CMD_SMOOTH_MAX_STEP_M=0 \
  DIFF_CMD_SMOOTH_ZERO_DYNAMICS=true \
  DIFF_CMD_MOTION_TIME_BASIS=ros_sim_time \
  DIFF_CMD_RECOMPUTE_VELOCITY_FROM_POSITION=true \
  DIFF_CMD_MAX_VELOCITY_MPS=0.6 \
  DIFF_CMD_MAX_ACCELERATION_MPS2=0.8 \
  DIFF_CMD_MAX_LATERAL_ACCELERATION_MPS2=0.6 \
  DIFF_CMD_MAX_JERK_MPS3=2.0 \
  DIFF_CMD_ODOM_TARGET_GUARD_ENABLE=true \
  DIFF_CMD_ODOM_TARGET_GUARD_TOPIC=/uav1/mavros/local_position/odom \
  DIFF_CMD_ODOM_TARGET_GUARD_TIMEOUT_S=0.3 \
  DIFF_CMD_MAX_XY_TARGET_DISTANCE_FROM_ODOM_M=0.5 \
  DIFF_CMD_ODOM_DISTANCE_POLICY=project_toward_raw \
  DIFF_CMD_ODOM_GUARD_ZERO_DYNAMICS=true \
  DIFF_CMD_SEED_FROM_ODOM_ON_ENABLE=true \
  DIFF_EXECUTE_MAX_TRUTH_ODOM_Z_ERROR_M=0.35 \
  EGO_MAP_SIZE_X="$QGC_DIFF_MAP_SIZE_X" \
  EGO_MAP_SIZE_Y="$QGC_DIFF_MAP_SIZE_Y" \
  EGO_MAP_SIZE_Z="$QGC_DIFF_MAP_SIZE_Z" \
  EGO_MAX_VEL=0.6 \
  EGO_MAX_JERK=2.0 \
  EGO_VIRTUAL_CEIL_HEIGHT=1.6 \
  EGO_VISUALIZATION_FORWARD_ONLY="$EGO_VISUALIZATION_FORWARD_ONLY_FOR_PHASE" \
  ENABLE_POINTCLOUD_REVIEW_ACCUMULATION=false \
  ENABLE_OCCUPANCY_REVIEW_ACCUMULATION=false \
  FACTORY_MODEL_PATH="$FACTORY_MODEL_PATH_FOR_PHASE" \
  TARGET_X="$SUNRAY_UAV_INIT_X" \
  TARGET_Y="$SUNRAY_UAV_INIT_Y" \
  TARGET_Z=1.0 \
  TOTAL_TIMEOUT_S=0 \
  RECORD_ROSBAG=false \
  GUI=false \
  OPEN_RVIZ="$OPEN_RVIZ_FOR_PHASE" \
  DIFF_OPEN_SPLIT_RVIZ="$DIFF_OPEN_SPLIT_RVIZ_FOR_PHASE" \
  GRID_RVIZ_CONFIG="$RVIZ_CONFIG_FOR_PHASE" \
  KEEP_ALIVE=false \
  DIFF_ENABLE_WAYPOINT_AUDIT=false \
  DIFF_ENABLE_Z_AUDIT=false \
  bash "$PROJECT_ROOT/Scripts/sunray/run_px4ctrl_ego_single_gate.sh"
}

(
  # Preserve the parent's ignored SIGHUP disposition for the generic runner
  # and all of its ROS/Gazebo descendants.
  trap '' HUP
  run_inner_gate
) > "$RESULT_DIR/qgc_diff_inner_runtime.log" 2>&1 &
INNER_PID=$!

topic_has_subscriber() {
  local topic=$1
  local info
  info=$(timeout 5s rostopic info "$topic" 2>/dev/null || true)
  printf '%s\n' "$info" | sed -n '/^Subscribers:/,$p' | grep -Eq '^[[:space:]]*\*'
}

inner_runtime_running() {
  if [ -n "$INNER_PID" ] && kill -0 "$INNER_PID" 2>/dev/null; then
    return 0
  fi
  if [ -n "$INNER_PID" ]; then
    set +e
    wait "$INNER_PID"
    INNER_EXIT_CODE=$?
    set -e
    INNER_PID=
  fi
  return 1
}

planner_reports_started() {
  python3 - "$RUNTIME_RESULT_DIR/planner_launch_gate.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
try:
    payload = json.loads(path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    raise SystemExit(1)
raise SystemExit(0 if payload.get("status") == "started" else 1)
PY
}

verify_qgc_planner_map_extent() {
  python3 - "$PLANNER_MAP_EXTENT_FILE" \
    "$QGC_DIFF_MAP_SIZE_X" "$QGC_DIFF_MAP_SIZE_Y" "$QGC_DIFF_MAP_SIZE_Z" \
    "$QGC_DIFF_PLANNER_PARAM_TIMEOUT_S" "$PLANNER_MAP_EXTENT_SCHEMA" "$REASON_PREFIX" <<'PY'
import json
import math
import pathlib
import subprocess
import sys
import time

output_path, expected_x, expected_y, expected_z, timeout_s, schema, reason_prefix = sys.argv[1:]
expected = {
    "map_size_x": float(expected_x),
    "map_size_y": float(expected_y),
    "map_size_z": float(expected_z),
}
timeout_s = float(timeout_s)
parameter_paths = {
    key: f"/drone_0_ego_planner_node/grid_map/{key}"
    for key in expected
}
payload = {
    "schema": schema,
    "status": "blocked",
    "reason_code": f"{reason_prefix}_planner_map_extent_mismatch",
    "planner_backend": "diff_planner_interactive_goal4",
    "expected_ego_map_size_m": expected,
    "observed_from": "rosparam",
    "observed_parameter_paths": parameter_paths,
    "parameter_timeout_s": timeout_s,
}
try:
    deadline = time.monotonic() + timeout_s
    last_errors = {}
    while True:
        actual = {}
        last_errors = {}
        for key, param_path in parameter_paths.items():
            completed = subprocess.run(
                ["rosparam", "get", param_path],
                capture_output=True,
                check=False,
                text=True,
                timeout=5,
            )
            if completed.returncode != 0:
                last_errors[param_path] = completed.stderr.strip() or completed.stdout.strip()
                continue
            actual[key] = float(completed.stdout.strip())
        if not last_errors:
            break
        if time.monotonic() >= deadline:
            param_path, detail = next(iter(last_errors.items()))
            raise ValueError(
                f"{reason_prefix}_planner_map_param_timeout:"
                f"{param_path}:{detail}"
            )
        time.sleep(1)
    if not all(math.isfinite(value) and value > 0.0 for value in actual.values()):
        raise ValueError(f"{reason_prefix}_planner_map_param_invalid")
    payload["actual_ego_map_size_m"] = actual
    if any(abs(actual[key] - expected[key]) > 1.0e-9 for key in expected):
        raise ValueError(f"{reason_prefix}_planner_map_extent_mismatch")
except (OSError, subprocess.SubprocessError, ValueError, TypeError) as exc:
    payload["reason_code"] = str(exc)
else:
    payload["status"] = "passed"
    payload["reason_code"] = f"{reason_prefix}_planner_map_extent_verified"

output = pathlib.Path(output_path)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if payload["status"] == "passed" else 1)
PY
}

wait_for_planner_launch() {
  local deadline=$((SECONDS + STARTUP_TIMEOUT_S))
  local fastlio_sensor_phase_extended=false
  while (( SECONDS < deadline )); do
    if ! inner_runtime_running; then return 1; fi
    # The generic runner records this only after its source/CustomMsg audit and
    # immediately before its bounded raw LiDAR/IMU wait. Give that independent
    # runtime prerequisite its own startup window instead of truncating it.
    if [ "$fastlio_sensor_phase_extended" = false ] \
      && [ -f "$RUNTIME_RESULT_DIR/fastlio_package_audit.txt" ]; then
      deadline=$((SECONDS + STARTUP_TIMEOUT_S))
      fastlio_sensor_phase_extended=true
      printf 'fastlio_sensor_phase_start=%s\n' "$SECONDS" \
        > "$RESULT_DIR/qgc_fastlio_sensor_phase.txt"
    fi
    if planner_reports_started; then
      return 0
    fi
    sleep 1
  done
  return 1
}

mission_reports_ready() {
  local ready_output
  ready_output=$(timeout 5s rostopic echo -n 1 /mosim/goal4/interactive_goal_ready 2>/dev/null || true)
  printf '%s\n' "$ready_output" | grep -Eiq 'data:[[:space:]]*true'
}

wait_for_interactive_chain() {
  local deadline=$((SECONDS + READINESS_TIMEOUT_S))
  while (( SECONDS < deadline )); do
    if ! inner_runtime_running; then return 1; fi
    if topic_has_subscriber /move_base_simple/goal \
      && topic_has_subscriber /goal_with_id \
      && mission_reports_ready; then
      return 0
    fi
    sleep 1
  done
  return 1
}

start_qgc_realtime_goal_bridge() {
  if [ "$RUN_MODE" != "qgc_realtime_goal" ]; then
    return 0
  fi
  local status_file="$OPERATOR_RUN_DIR/operator_goal/STATUS.json"
  mkdir -p "$(dirname "$status_file")"
  (
    set +u
    source /opt/ros/noetic/setup.bash
    source "$GOAL4_DIFF_PLANNER_WS/devel/setup.bash"
    set -u
    exec python3 "$PROJECT_ROOT/Scripts/sunray/qgc_realtime_goal_bridge.py" \
      --run-dir "$OPERATOR_RUN_DIR" \
      --coordinate-evidence "$OPERATOR_RUN_DIR/OPERATOR_MAP_COORDINATE_EVIDENCE.json" \
      --active-pointer "$PROJECT_ROOT/Results/ui_platform/qgc_active_run.json" \
      --goal-topic /move_base_simple/goal \
      --goal-frame world \
      --mission-ready-topic "$QGC_REALTIME_MISSION_READY_TOPIC" \
      --waypoint-plan-size-topic "$QGC_REALTIME_WAYPOINT_PLAN_SIZE_TOPIC" \
      --max-waypoint-plan-duration-s "$QGC_REALTIME_WAYPOINT_PLAN_SIM_DURATION_S" \
      --max-waypoint-plan-wall-stall-s "$QGC_REALTIME_WAYPOINT_PLAN_WALL_STALL_S"
  ) > "$RESULT_DIR/qgc_realtime_goal_bridge.log" 2>&1 &
  GOAL_BRIDGE_PID=$!

  local deadline=$((SECONDS + 15))
  while (( SECONDS < deadline )); do
    if ! kill -0 "$GOAL_BRIDGE_PID" 2>/dev/null; then
      wait "$GOAL_BRIDGE_PID" 2>/dev/null || true
      GOAL_BRIDGE_PID=
      return 1
    fi
    if [ -s "$status_file" ]; then
      printf 'qgc_realtime_goal_bridge_pid=%s\n' "$GOAL_BRIDGE_PID" \
        > "$RUNTIME_RESULT_DIR/qgc_realtime_goal_bridge.pid"
      return 0
    fi
    sleep 0.2
  done
  return 1
}

if ! wait_for_planner_launch; then
  echo "QGC planning backend did not report started before startup timeout" >&2
  if [ -n "$INNER_EXIT_CODE" ]; then
    write_runtime_status blocked qgc_diff_realtime_goal_inner_runtime_exited "$INNER_EXIT_CODE"
    finalize_operator_run blocked qgc_diff_realtime_goal_inner_runtime_exited
  else
    write_runtime_status blocked qgc_diff_realtime_goal_planner_start_not_ready
    finalize_operator_run blocked qgc_diff_realtime_goal_planner_start_not_ready
  fi
  exit 4
fi

if ! verify_qgc_planner_map_extent; then
  echo "QGC planning backend map extent does not match the Factory L2 goal contract" >&2
  write_runtime_status blocked qgc_diff_realtime_goal_planner_map_extent_mismatch
  finalize_operator_run blocked qgc_diff_realtime_goal_planner_map_extent_mismatch
  exit 4
fi

if ! python3 "$PROJECT_ROOT/Scripts/ui/prepare_operator_run.py" \
  --activate-active \
  --expected-run-id "$OPERATOR_RUN_ID" \
  --activation-source "$TERMINAL_SOURCE" \
  > "$RESULT_DIR/qgc_operator_run_activate.log" 2>&1; then
  echo "QGC realtime-goal active-run pointer could not advance after planner startup" >&2
  write_runtime_status blocked qgc_diff_realtime_goal_active_pointer_activate_failed
  finalize_operator_run blocked qgc_diff_realtime_goal_active_pointer_activate_failed
  exit 5
fi

if ! start_qgc_realtime_goal_bridge; then
  echo "QGC realtime-goal bridge did not become ready" >&2
  write_runtime_status blocked qgc_realtime_goal_bridge_start_failed
  finalize_operator_run blocked qgc_realtime_goal_bridge_start_failed
  exit 5
fi

if ! wait_for_interactive_chain; then
  echo "QGC realtime-goal chain did not become ready" >&2
  if [ -n "$INNER_EXIT_CODE" ]; then
    write_runtime_status blocked qgc_diff_realtime_goal_inner_runtime_exited "$INNER_EXIT_CODE"
    finalize_operator_run blocked qgc_diff_realtime_goal_inner_runtime_exited
  else
    write_runtime_status blocked qgc_diff_realtime_goal_interactive_chain_not_ready
    finalize_operator_run blocked qgc_diff_realtime_goal_interactive_chain_not_ready
  fi
  exit 4
fi

(
  set +u
  source "$GOAL4_DIFF_PLANNER_WS/devel/setup.bash"
  set -u
  exec python3 "$PROJECT_ROOT/Scripts/ui/runtime_sidecar.py" \
  --run-dir "$OPERATOR_RUN_DIR" \
  --manifest "$OPERATOR_RUN_MANIFEST" \
  --contract "$PROJECT_ROOT/Config/control_platform/factory_injection_contract.json" \
  --vehicle-count 1 \
  --odom-topic /uav1/sunray/gazebo_pose \
  --expected-path-topic /mosim/goal4/target_path \
  --future-polytraj-topic /drone_0_planning/trajectory \
  --future-polytraj-frame-id world \
  --coordinate-evidence "$OPERATOR_RUN_DIR/OPERATOR_MAP_COORDINATE_EVIDENCE.json" \
  --skip-actuator-telemetry-readiness \
  --read-only
) \
  > "$RESULT_DIR/qgc_runtime_sidecar.log" 2>&1 &
SIDECAR_PID=$!
sleep 1
if ! kill -0 "$SIDECAR_PID" 2>/dev/null; then
  echo "QGC runtime sidecar exited during startup" >&2
  write_runtime_status blocked qgc_diff_realtime_goal_sidecar_start_failed
  finalize_operator_run blocked qgc_diff_realtime_goal_sidecar_start_failed
  exit 5
fi
if [ "$RUN_MODE" = "rviz_qgc_display_phase1" ]; then
  if ! write_phase1_manual_test_packet; then
    write_runtime_status blocked rviz_qgc_display_phase1_manual_packet_write_failed
    finalize_operator_run blocked rviz_qgc_display_phase1_manual_packet_write_failed
    exit 5
  fi
  write_runtime_status running rviz_qgc_display_phase1_ready_for_rviz_goal
  echo "Phase 1 RViz-to-QGC display test is ready. Use RViz 2D Nav Goal once, then observe the same run in QGC; Plan Goal is intentionally disabled." \
    | tee "$READY_FILE"
  echo "Manual test packet: $MANUAL_TEST_PACKET_FILE"
else
  write_runtime_status running qgc_diff_realtime_goal_interactive_chain_ready
  echo "QGC Plan Goal is now available. Select Plan Goal on the Factory L2 map." \
    | tee "$READY_FILE"
  echo "The runtime-owned bridge publishes only /move_base_simple/goal; planner and vehicle acceptance require separate runtime evidence."
fi

set +e
wait "$INNER_PID"
INNER_EXIT_CODE=$?
set -e
INNER_PID=
if [ "$RUN_MODE" = "rviz_qgc_display_phase1" ]; then
  if [ "$INNER_EXIT_CODE" -eq 0 ] && verify_rviz_qgc_display_phase1_acceptance; then
    write_runtime_status completed rviz_qgc_display_phase1_automated_evidence_ready
    finalize_operator_run completed rviz_qgc_display_phase1_automated_evidence_ready
    exit 0
  fi
  if [ "$INNER_EXIT_CODE" -eq 0 ]; then
    INNER_EXIT_CODE=6
    write_runtime_status blocked rviz_qgc_display_phase1_automated_evidence_unverified "$INNER_EXIT_CODE"
    finalize_operator_run blocked rviz_qgc_display_phase1_automated_evidence_unverified
    exit "$INNER_EXIT_CODE"
  fi
  write_runtime_status blocked rviz_qgc_display_phase1_review_ended_without_evidence "$INNER_EXIT_CODE"
  finalize_operator_run blocked rviz_qgc_display_phase1_review_ended_without_evidence
  exit "$INNER_EXIT_CODE"
fi
if [ "$INNER_EXIT_CODE" -eq 0 ] && verify_qgc_goal_acceptance; then
  write_runtime_status completed qgc_diff_realtime_goal_acceptance_verified
  finalize_operator_run completed qgc_diff_realtime_goal_acceptance_verified
  exit 0
fi
if [ "$INNER_EXIT_CODE" -eq 0 ]; then
  INNER_EXIT_CODE=6
  write_runtime_status blocked qgc_diff_realtime_goal_acceptance_unverified "$INNER_EXIT_CODE"
  finalize_operator_run blocked qgc_diff_realtime_goal_acceptance_unverified
  exit "$INNER_EXIT_CODE"
fi
write_runtime_status blocked qgc_diff_realtime_goal_review_ended_without_acceptance "$INNER_EXIT_CODE"
finalize_operator_run blocked qgc_diff_realtime_goal_review_ended_without_acceptance
exit "$INNER_EXIT_CODE"
