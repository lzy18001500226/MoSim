#!/usr/bin/env bash

set -euo pipefail

project_root="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
execute_s="${1:-120}"
result_dir="${2:?usage: run_factory_l2_fuel_full_map_gate.sh EXECUTE_S RESULT_DIR}"

# Canonical indoor wall/fence envelope from the accepted Factory L2 scene
# profile. Keep this separate from the fixed 64 x 64 m coverage gate.
export FUEL_MAP_SIZE_X=175.65987
export FUEL_MAP_SIZE_Y=63.99956
export FUEL_MAP_SIZE_Z=3
export FUEL_BOX_MIN_X=-98.40496
export FUEL_BOX_MIN_Y=-51.36291
export FUEL_BOX_MIN_Z=0.9
export FUEL_BOX_MAX_X=77.25491
export FUEL_BOX_MAX_Y=12.63665
export FUEL_BOX_MAX_Z=1.6

export FUEL_PERCEPTION_OMNI_HORIZONTAL=true
export FUEL_EXPLORATION_COVERAGE_EXPANSION_ENABLE=true
export FUEL_EXPLORATION_COVERAGE_EXPANSION_SCORE_COMMITTED_GOAL=true
export FUEL_EXPLORATION_COVERAGE_EXPANSION_GLOBAL_SELECTOR=true
# Full-map planning commonly takes about 1.9-2.0 simulation seconds. Predict
# the handoff far enough ahead that a valid trajectory is not discarded only
# because its planning cycle exceeded the 0.5 s small-map baseline.
export FUEL_REPLAN_TIME_S="${FUEL_REPLAN_TIME_S:-3.0}"
export PX4CTRL_EKF2_EV_CTRL_OVERRIDE=15

exec bash "${project_root}/Scripts/sunray/run_factory_l2_fuel_speed_gate.sh" \
  "${execute_s}" "${result_dir}"
