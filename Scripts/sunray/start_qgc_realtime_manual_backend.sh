#!/usr/bin/env bash
# Prepare and hold the QGC manual-planning backend from one visible terminal.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PROFILE_ID="px4ctrl_graphical_c99_factory_qgc_realtime_goal_v1"
RUNTIME_PROFILE_ID="sunray_ros1_factory_l2_graphical_px4ctrl_c99_qgc_realtime_goal_v1"

RUN_ID="$(python3 "${PROJECT_ROOT}/Scripts/ui/prepare_operator_run.py" \
  --profile-id "${PROFILE_ID}" \
  --runtime-profile-id "${RUNTIME_PROFILE_ID}" \
  --prepared-by qgc_visible_terminal \
  --print-run-id)"

export MOSIM_OPERATOR_RUN_ID="${RUN_ID}"
export MOSIM_OPERATOR_RUN_DIR="${PROJECT_ROOT}/Results/runs/${RUN_ID}"
export MOSIM_OPERATOR_RUN_MANIFEST="${MOSIM_OPERATOR_RUN_DIR}/RUN_MANIFEST.json"
export GUI=false
export QGC_TERMINAL_ROLE=backend

echo "Prepared manual QGC run: ${RUN_ID}"
echo "This terminal owns runtime bring-up and takeoff/hover only."
exec bash "${PROJECT_ROOT}/Scripts/sunray/run_qgc_diff_realtime_goal_gate.sh" qgc_realtime_goal
