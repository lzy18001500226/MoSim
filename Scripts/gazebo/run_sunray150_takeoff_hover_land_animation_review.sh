#!/usr/bin/env bash
# Open Gazebo GUI for the accepted takeoff-hover-land plant sanity animation.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/sunray150_takeoff_hover_land_animation_review_$(date +%Y%m%d_%H%M%S)}"

export PROJECT_ROOT
export RESULT_DIR
export GAZEBO_GUI_REVIEW=1
export WORLD_OVERRIDE="${WORLD_OVERRIDE:-Config/gazebo/worlds/sunray150_takeoff_hover_land_plant_sanity.sdf}"
export WORLD_NAME_OVERRIDE="${WORLD_NAME_OVERRIDE:-sunray150_takeoff_hover_land_plant_sanity}"
export TRUTH_TOPIC_OVERRIDE="${TRUTH_TOPIC_OVERRIDE:-/world/sunray150_takeoff_hover_land_plant_sanity/dynamic_pose/info}"
export HOVER_ALTITUDE_M="${HOVER_ALTITUDE_M:-0.6}"
export LANDED_ALTITUDE_M="${LANDED_ALTITUDE_M:-0.12}"
export TAKEOFF_DURATION_S="${TAKEOFF_DURATION_S:-4.0}"
export HOVER_DURATION_S="${HOVER_DURATION_S:-4.0}"
export LAND_DURATION_S="${LAND_DURATION_S:-4.0}"
export SETTLE_DURATION_S="${SETTLE_DURATION_S:-1.0}"
export HOVER_COMMAND="${HOVER_COMMAND:-0.0556}"
export COMMAND_MAX="${COMMAND_MAX:-0.0585}"
export LAND_COMMAND_MAX="${LAND_COMMAND_MAX:-0.0554}"

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_DIR}"

cat > "${RESULT_DIR}/ANIMATION_REVIEW_REQUEST.json" <<JSON
{
  "schema": "mosim.gazebo_takeoff_hover_land_animation_review_request.v1",
  "status": "starting",
  "purpose": "open Gazebo GUI for user review of takeoff-hover-land animation",
  "world": "${WORLD_OVERRIDE}",
  "world_name": "${WORLD_NAME_OVERRIDE}",
  "vehicle": "model://sunray150_assembled",
  "controller": "Scripts/ros/gazebo_truth_takeoff_hover_land_controller.py",
  "claim_boundary": [
    "visual review of stable Gazebo plant sanity takeoff-hover-land only",
    "not MWORKS AWFF controller deployment",
    "not planner_ready, final closed_loop acceptance, final competition controller performance, UE acceptance, or multi-UAV readiness"
  ]
}
JSON

"${PROJECT_ROOT}/Scripts/gazebo/run_sunray150_takeoff_hover_land_gate.sh"

python3 - <<PY
import json
from pathlib import Path
result_dir = Path("${PROJECT_ROOT}") / "${RESULT_DIR}"
request = json.loads((result_dir / "ANIMATION_REVIEW_REQUEST.json").read_text(encoding="utf-8"))
runtime_path = result_dir / "RUNTIME_STATUS.json"
runtime = json.loads(runtime_path.read_text(encoding="utf-8")) if runtime_path.exists() else {}
request.update({
    "status": "review_window_opened" if runtime.get("gate_passed") else "review_window_opened_with_runtime_blocker",
    "runtime_status": "${RESULT_DIR}/RUNTIME_STATUS.json",
    "gate_passed": bool(runtime.get("gate_passed")),
    "eval": "${RESULT_DIR}/GAZEBO_TAKEOFF_HOVER_LAND_EVAL.json",
})
(result_dir / "ANIMATION_REVIEW_REQUEST.json").write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
print("${RESULT_DIR}/ANIMATION_REVIEW_REQUEST.json")
PY
