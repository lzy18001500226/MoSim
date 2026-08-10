#!/usr/bin/env bash
# Prepare the C99/Diff-Swarm runtime contract without starting a simulator.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"

case "${1:-}" in
  "")
    ;;
  -h|--help)
    cat <<'EOF'
Usage: bash Scripts/sunray/prepare_c99_diff_swarm_runtime.sh

Runs the C99/Diff-Swarm runtime preflight and workspace preparation only.
Set RUN_ID or RESULT_DIR before invocation to select the output directory.
The output includes c99_multiuav_contract.env and C99_DIFF_PREPARE_STATUS.json.
EOF
    exit 0
    ;;
  *)
    printf 'Unexpected argument: %s\n' "$1" >&2
    exit 2
    ;;
esac

exec env \
  PROJECT_ROOT="${PROJECT_ROOT}" \
  PLANNER_VARIANT="${PLANNER_VARIANT:-diff_planner}" \
  C99_DIFF_PREPARE_ONLY=true \
  bash "${PROJECT_ROOT}/Scripts/sunray/run_c99_multiuav_planner_gate.sh"
