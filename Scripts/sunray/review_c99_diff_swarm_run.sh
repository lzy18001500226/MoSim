#!/usr/bin/env bash
# Audit the completed mission stage without changing the retained runtime.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/c99_diff_stage_contract.sh"

case "${1:-}" in
  "")
    ;;
  -h|--help)
    cat <<'EOF'
Usage: RESULT_DIR=/path/to/run bash Scripts/sunray/review_c99_diff_swarm_run.sh

Audits the planner log and writes C99_DIFF_SWARM_STAGE_REVIEW.json from the
prepare, components, coordinate-contract and mission artifacts. It does not
start, stop, or otherwise alter the retained runtime.
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
c99_diff_require_json_status "${RESULT_DIR}/C99_DIFF_PREPARE_STATUS.json" "passed"
c99_diff_require_json_status "${RESULT_DIR}/C99_DIFF_SWARM_COMPONENTS_READY.json" "passed"

set +e
python3 "${PROJECT_ROOT}/Scripts/sunray/audit_roslaunch_runtime_log.py" \
  --log "${RESULT_DIR}/planner_swarm_px4ctrl_goal5.log" \
  --output "${RESULT_DIR}/planner_runtime_log_audit.json" \
  --metrics-json "${RESULT_DIR}/EGO_SWARM_METRICS.json" \
  --blocker-prefix diff_planner \
  --planner-semantic-profile none \
  --missing-is-blocker \
  > "${RESULT_DIR}/planner_runtime_log_audit.log" 2>&1
audit_exit_code=$?
set -e

python3 "${PROJECT_ROOT}/Scripts/sunray/review_c99_diff_swarm_run.py" \
  --result-dir "${RESULT_DIR}" \
  --audit-exit-code "${audit_exit_code}"
