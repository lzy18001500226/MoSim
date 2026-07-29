#!/usr/bin/env bash
# Open Gazebo GUI for the MWORKS AWFF behavior-wrapper deployment review.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/mworks_awff_takeoff_hover_land_animation_review_$(date +%Y%m%d_%H%M%S)}"

export PROJECT_ROOT
export RESULT_DIR
export GAZEBO_GUI_REVIEW=1
export GAZEBO_GUI_VERBOSE="${GAZEBO_GUI_VERBOSE:-2}"
export GAZEBO_CAMERA_FOLLOW_TARGET="${GAZEBO_CAMERA_FOLLOW_TARGET:-sunray150_assembled}"
export GAZEBO_CAMERA_FOLLOW_OFFSET_X_M="${GAZEBO_CAMERA_FOLLOW_OFFSET_X_M:--0.55}"
export GAZEBO_CAMERA_FOLLOW_OFFSET_Y_M="${GAZEBO_CAMERA_FOLLOW_OFFSET_Y_M:-0.14}"
export GAZEBO_CAMERA_FOLLOW_OFFSET_Z_M="${GAZEBO_CAMERA_FOLLOW_OFFSET_Z_M:-0.28}"
export GAZEBO_CAMERA_FOLLOW_MIN_DIST_M="${GAZEBO_CAMERA_FOLLOW_MIN_DIST_M:-0.35}"
export GAZEBO_CAMERA_FOLLOW_MAX_DIST_M="${GAZEBO_CAMERA_FOLLOW_MAX_DIST_M:-2.0}"
export GAZEBO_CAMERA_FOLLOW_REPEAT="${GAZEBO_CAMERA_FOLLOW_REPEAT:-120}"
export GAZEBO_CAMERA_FOLLOW_INTERVAL_S="${GAZEBO_CAMERA_FOLLOW_INTERVAL_S:-0.35}"

cd "${PROJECT_ROOT}"
mkdir -p "${RESULT_DIR}"

cat > "${RESULT_DIR}/AWFF_ANIMATION_REVIEW_REQUEST.json" <<JSON
{
  "schema": "mosim.mworks_awff_gazebo_animation_review_request.v1",
  "status": "starting",
  "purpose": "open Gazebo GUI for user review of the MWORKS AWFF behavior-wrapper takeoff-hover-land deployment",
  "controller_runtime": "mworks_awff_equation_behavior_wrapper",
  "source_model": "Models/MoSimQuadrotorModel/Control/Implementations/Sysblocks/AWFF_FullControllerEquation_Sysblock.mo",
  "world": "Config/gazebo/worlds/sunray150_takeoff_hover_land_plant_sanity.sdf",
  "world_name": "sunray150_takeoff_hover_land_plant_sanity",
  "vehicle": "sunray150_assembled",
  "camera_follow": {
    "target": "${GAZEBO_CAMERA_FOLLOW_TARGET}",
    "offset_m": [${GAZEBO_CAMERA_FOLLOW_OFFSET_X_M}, ${GAZEBO_CAMERA_FOLLOW_OFFSET_Y_M}, ${GAZEBO_CAMERA_FOLLOW_OFFSET_Z_M}]
  },
  "claim_boundary": [
    "visual review of MWORKS AWFF behavior-wrapper Gazebo takeoff-hover-land only",
    "not generated C/C++ controller runtime",
    "not full SIL equivalence",
    "not planner_ready, final closed_loop acceptance, final competition controller performance, UE acceptance, or multi-UAV readiness"
  ]
}
JSON

"${PROJECT_ROOT}/Scripts/gazebo/run_mworks_awff_takeoff_hover_land_gate.sh"

python3 - <<PY
import json
from pathlib import Path

result_dir = Path("${PROJECT_ROOT}") / "${RESULT_DIR}"
request_path = result_dir / "AWFF_ANIMATION_REVIEW_REQUEST.json"
request = json.loads(request_path.read_text(encoding="utf-8"))
runtime_path = result_dir / "RUNTIME_STATUS.json"
runtime = json.loads(runtime_path.read_text(encoding="utf-8")) if runtime_path.exists() else {}
camera_path = result_dir / "gazebo_camera_follow_request.json"
camera = json.loads(camera_path.read_text(encoding="utf-8")) if camera_path.exists() else {}
stderr_path = result_dir / "gazebo.stderr.log"
stderr_tail = stderr_path.read_text(encoding="utf-8", errors="replace")[-2000:] if stderr_path.exists() else ""
request.update({
    "status": "review_run_completed" if runtime.get("gate_passed") else "review_run_blocked",
    "gate_passed": bool(runtime.get("gate_passed")),
    "runtime_status": "${RESULT_DIR}/RUNTIME_STATUS.json",
    "eval": "${RESULT_DIR}/GAZEBO_TAKEOFF_HOVER_LAND_EVAL.json",
    "camera_follow_status": camera.get("status", "missing"),
    "camera_follow_request": "${RESULT_DIR}/gazebo_camera_follow_request.json",
    "gazebo_ogre_shutdown_segfault_observed": "Segmentation fault" in stderr_tail,
    "interpretation": [
        "Numerical AWFF deployment gate is authoritative for control result.",
        "GUI animation acceptance still requires user visual review of the opened Gazebo window.",
        "Gazebo OGRE shutdown crash, if present, is tracked as GUI teardown risk rather than control failure."
    ],
})
request_path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
print("${RESULT_DIR}/AWFF_ANIMATION_REVIEW_REQUEST.json")
PY
