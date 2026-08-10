#!/usr/bin/env bash
# Execute only the mission stage after run_c99_diff_swarm_components.sh is ready.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/c99_diff_stage_contract.sh"

case "${1:-}" in
  "")
    ;;
  -h|--help)
    cat <<'EOF'
Usage: RESULT_DIR=/path/to/run bash Scripts/sunray/run_c99_diff_swarm_mission.sh

Requires a live components-stage runner and its
C99_DIFF_SWARM_COMPONENTS_READY.json. Publishes the fixed targets, evaluates
the mission gates, lands the aircraft and writes EGO_SWARM_METRICS.json.
EOF
    exit 0
    ;;
  *)
    c99_diff_stage_die "unexpected argument: $1"
    ;;
esac

RESULT_DIR="${RESULT_DIR:-}"
[[ -n "${RESULT_DIR}" ]] || c99_diff_stage_die "RESULT_DIR is required"
c99_diff_load_contract "${C99_DIFF_CONTRACT_FILE:-${RESULT_DIR}/c99_multiuav_contract.env}"
c99_diff_load_contract "${RESULT_DIR}/c99_diff_swarm_component_contract.env"
c99_diff_require_json_status "${RESULT_DIR}/C99_DIFF_SWARM_COMPONENTS_READY.json" "passed"

runner_pid="$(tr -d '[:space:]' < "${RESULT_DIR}/c99_diff_swarm_components_runner.pid" 2>/dev/null || true)"
[[ "${runner_pid}" =~ ^[0-9]+$ ]] || c99_diff_stage_die "components runner PID is missing or invalid"
kill -0 "${runner_pid}" >/dev/null 2>&1 \
  || c99_diff_stage_die "components runner ${runner_pid} is not active"
runner_cmdline="$(tr '\0' ' ' < "/proc/${runner_pid}/cmdline" 2>/dev/null || true)"
[[ "${runner_cmdline}" == *"run_px4ctrl_ego_swarm_gate.sh"* ]] \
  || c99_diff_stage_die "components runner ${runner_pid} is not the expected swarm gate"
[[ ! -e "${RESULT_DIR}/EGO_SWARM_METRICS.json" ]] \
  || c99_diff_stage_die "mission metrics already exist; use a new RESULT_DIR to avoid mixing runs"

for setup in \
  /opt/ros/noetic/setup.bash \
  "${LOCAL_ROS1_WS}/devel/setup.bash" \
  "${PX4CTRL_WS}/devel/setup.bash" \
  "${PLANNER_WS}/devel/setup.bash"; do
  [[ -f "${setup}" ]] || c99_diff_stage_die "required ROS setup file is missing: ${setup}"
  set +u
  source "${setup}"
  set -u
done

exec bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_ego_swarm_mission_stage.sh"
