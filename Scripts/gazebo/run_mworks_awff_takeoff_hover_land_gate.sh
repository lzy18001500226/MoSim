#!/usr/bin/env bash
# run_mworks_awff_takeoff_hover_land_gate: MWORKS AWFF behavior wrapper gate.
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_DIR="${RESULT_DIR:-Results/gazebo_ros2/mworks_awff_takeoff_hover_land_gate_$(date +%Y%m%d_%H%M%S)}"

export PROJECT_ROOT
export RESULT_DIR
export STAGE_CONTROLLER_SCRIPT="${STAGE_CONTROLLER_SCRIPT:-Scripts/ros/mworks_awff_takeoff_hover_land_controller.py}"
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
export LAND_COMMAND_MAX="${LAND_COMMAND_MAX:-0.0548}"
export STAGE_CONTROLLER_EXTRA_ARGS="${STAGE_CONTROLLER_EXTRA_ARGS:---mapping-mode gazebo_ref_adapter --enable-xy-hold --x-error-sign -1 --y-error-sign -1 --gazebo-roll-ref-sign 1 --gazebo-pitch-ref-sign -1 --gazebo-thrust-scale 0.000045 --gazebo-vz-damping-scale 0.0042 --ground-lock-altitude-m 0.5 --landing-attitude-disable-altitude-m 0.60 --landing-xy-disable-altitude-m 0.60}"

"${PROJECT_ROOT}/Scripts/gazebo/run_sunray150_takeoff_hover_land_gate.sh" "$@"

python3 - <<PY
import json
from pathlib import Path

result_dir = Path("${PROJECT_ROOT}") / "${RESULT_DIR}"
for name in ["RUNTIME_STATUS.json", "RUN_MANIFEST.json"]:
    path = result_dir / name
    if not path.exists():
        continue
    data = json.loads(path.read_text(encoding="utf-8"))
    data["controller_runtime"] = "mworks_awff_equation_behavior_wrapper"
    data["source_model"] = "Models/MoSimQuadrotorModel/Controllers/Sysblocks/AWFF_FullControllerEquation_Sysblock.mo"
    data["claim_boundary"] = [
        "MWORKS AWFF equation behavior wrapper drives Gazebo ControllerOutput in the same run",
        "hover trim and bounded delta scale are calibrated for the accepted Gazebo sunray150_assembled plant",
        "not generated C/C++ code and not final SIL equivalence evidence",
        "no planner_ready, final closed_loop acceptance, final competition controller performance, UE acceptance, or multi-UAV readiness is claimed"
    ]
    if name == "RUN_MANIFEST.json":
        data["run_id"] = "mworks_awff_takeoff_hover_land_gate"
        data["objective"] = "prove AWFF Sysblock-equation behavior wrapper can drive accepted Gazebo plant through takeoff, hover, and landing"
        data["not_claimed"] = [
            "generated C/C++ controller runtime",
            "SIL equivalence for this target controller",
            "planner_ready",
            "final_closed_loop_acceptance",
            "multi_uav_readiness"
        ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
PY
