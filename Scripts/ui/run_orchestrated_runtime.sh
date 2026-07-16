#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
OPERATION_ID="${1:-}"
RUN_ID="${2:-}"

if [[ ! "${RUN_ID}" =~ ^run-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$ ]]; then
  echo "invalid run_id" >&2
  exit 2
fi

ORCHESTRATOR_RUN_DIR="${PROJECT_ROOT}/Results/ui_platform/orchestrator_runs/${RUN_ID}"
mkdir -p -- "${ORCHESTRATOR_RUN_DIR}"
printf '%s\n' "$$" > "${ORCHESTRATOR_RUN_DIR}/runtime_linux_pid.txt"

case "${OPERATION_ID}" in
  px4ctrl_figure8_single)
    export RUN_ID="${RUN_ID}"
    export RESULT_DIR="${ORCHESTRATOR_RUN_DIR}/runtime"
    export PX4CTRL_CORE_PROFILE="original"
    export GUI="false"
    export KEEP_ALIVE="false"
    exec bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" figure8
    ;;
  *)
    echo "operation is not allowlisted: ${OPERATION_ID}" >&2
    exit 2
    ;;
esac
