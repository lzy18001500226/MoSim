#!/usr/bin/env bash
# Run each P8 formation mode in an independent Gazebo/PX4 session.

set -uo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
P8_MODE_IDS="${P8_MODE_IDS:-2 3 4 5 6 7 8 9}"
P8_RESULT_SUFFIX="${P8_RESULT_SUFFIX:-gazebo_r1_20260717}"
RUNNER="${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh"
MISSION_NODE="${PROJECT_ROOT}/Scripts/sunray/p8_formation_generated_mission_node.py"
GENERATED_LIB="${PROJECT_ROOT}/Results/control_platform/p8_formation_generated_runtime_20260717/libmosim_p8_formation_generated.so"
WORLD_FILE="${PROJECT_ROOT}/Config/gazebo/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf"

for mode_id in ${P8_MODE_IDS}; do
  run_id="p8_formation_mode${mode_id}_${P8_RESULT_SUFFIX}"
  result_dir="${PROJECT_ROOT}/Results/control_platform/${run_id}"
  echo "P8_MODE_START mode=${mode_id} result_dir=${result_dir}"
  if ! env \
    RUN_ID="${run_id}" \
    RESULT_DIR="${result_dir}" \
    WORLD_FILE="${WORLD_FILE}" \
    SUNRAY_GAZEBO_LAUNCH_FILE="${PROJECT_ROOT}/Scripts/sunray/factory_l2_sunray_px4_gazebo.launch" \
    UAV_NUM=3 \
    PLANNER_VARIANT=swarm_formation \
    STAGGERED_SPAWN=true \
    STAGGERED_SPAWN_INTERVAL_S=12 \
    PRELOAD_GAZEBO_MODELS=false \
    GOAL5_STARTUP_ATTEMPTS=1 \
    MAVROS_READY_TIMEOUT_S=150 \
    TOTAL_TIMEOUT_S=600 \
    START1_X=-12.575025 START1_Y=-19.36313 \
    START2_X=-11.27595 START2_Y=-20.11313 \
    START3_X=-12.575025 START3_Y=-20.86313 \
    SWARM_BASELINE_ONLY=true \
    SWARM_BASELINE_MISSION_NODE="${MISSION_NODE}" \
    P8_FORMATION_MODE_ID="${mode_id}" \
    P8_FORMATION_GENERATED_LIB="${GENERATED_LIB}" \
    PX4CTRL_CORE_PROFILE=original \
    bash "${RUNNER}"; then
    echo "P8_MODE_BLOCKED mode=${mode_id} result_dir=${result_dir}" >&2
    exit "${mode_id}"
  fi
  python3 - "${result_dir}/PX4CTRL_SWARM_BASIC_METRICS.json" "${mode_id}" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
mode_id = int(sys.argv[2])
data = json.loads(path.read_text(encoding="utf-8"))
if data.get("status") != "passed" or data.get("formation_mode_id") != mode_id:
    raise SystemExit(
        f"P8 metrics rejected for mode {mode_id}: "
        f"status={data.get('status')} blockers={data.get('blockers')}"
    )
print(
    f"P8_MODE_PASSED mode={mode_id} generated_steps={data.get('generated_step_count')} "
    f"min_separation_m={data.get('min_inter_uav_distance_m')}"
)
PY
done

echo "P8_MATRIX_PASSED modes=${P8_MODE_IDS}"
