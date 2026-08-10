#!/usr/bin/env bash
# Start and retain the C99/Diff-Swarm runtime components for a separate mission stage.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/c99_diff_stage_contract.sh"

case "${1:-}" in
  "")
    ;;
  -h|--help)
    cat <<'EOF'
Usage: RESULT_DIR=/path/to/run bash Scripts/sunray/run_c99_diff_swarm_components.sh

Requires the completed prepare-stage c99_multiuav_contract.env in RESULT_DIR.
Starts Gazebo/PX4/MAVROS, px4ctrl, coordinate bridges, safety adapters and
Diff-Planner, then holds this runner in the foreground. Wait for
C99_DIFF_SWARM_COMPONENTS_READY.json before using the separate mission stage.
Use stop_c99_diff_swarm_components.sh for controlled cleanup.
EOF
    exit 0
    ;;
  *)
    c99_diff_stage_die "unexpected argument: $1"
    ;;
esac

RESULT_DIR="${RESULT_DIR:-}"
[[ -n "${RESULT_DIR}" ]] || c99_diff_stage_die "RESULT_DIR is required"
CONTRACT_FILE="${C99_DIFF_CONTRACT_FILE:-${RESULT_DIR}/c99_multiuav_contract.env}"
c99_diff_load_contract "${CONTRACT_FILE}"
c99_diff_require_json_status "${RESULT_DIR}/C99_DIFF_PREPARE_STATUS.json" "passed"

[[ "${PLANNER_VARIANT}" == "diff_planner" ]] \
  || c99_diff_stage_die "staged components require PLANNER_VARIANT=diff_planner, got ${PLANNER_VARIANT}"
[[ "${UAV_NUM}" == "2" || "${UAV_NUM}" == "3" ]] \
  || c99_diff_stage_die "staged components require UAV_NUM=2 or 3, got ${UAV_NUM}"
[[ ! -e "${RESULT_DIR}/C99_DIFF_SWARM_COMPONENTS_READY.json" ]] \
  || c99_diff_stage_die "components-ready status already exists; use a new RESULT_DIR to avoid mixing runs"

printf '%s\n' "$$" > "${RESULT_DIR}/c99_diff_swarm_components_runner.pid"
exec env \
  GOAL4_DIFF_PLANNER_WS="${GOAL4_DIFF_PLANNER_WS:-${PLANNER_WS}}" \
  GOAL5_STARTUP_ONLY=false \
  GOAL5_COMPONENTS_ONLY=true \
  GOAL5_STARTUP_ATTEMPTS="${GOAL5_STARTUP_ATTEMPTS:-2}" \
  MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-180}" \
  MAVROS_CONN_TIMEOUT_S="${MAVROS_CONN_TIMEOUT_S:-120}" \
  LIDAR_READY_TIMEOUT_S="${LIDAR_READY_TIMEOUT_S:-180}" \
  KEEP_ALIVE=true \
  bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh"
