#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RUN_ID="${1:-}"

if [[ ! "${RUN_ID}" =~ ^run-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$ ]]; then
  echo "invalid run_id" >&2
  exit 2
fi

PID_FILE="${PROJECT_ROOT}/Results/ui_platform/orchestrator_runs/${RUN_ID}/runtime_linux_pid.txt"
if [[ ! -f "${PID_FILE}" ]]; then
  echo "runtime pid file not found: ${PID_FILE}" >&2
  exit 3
fi

PID="$(<"${PID_FILE}")"
if [[ ! "${PID}" =~ ^[0-9]+$ ]]; then
  echo "invalid runtime pid" >&2
  exit 3
fi

if kill -0 "${PID}" 2>/dev/null; then
  kill -TERM "${PID}"
fi

for _ in $(seq 1 60); do
  if ! kill -0 "${PID}" 2>/dev/null; then
    exit 0
  fi
  sleep 1
done

echo "runtime did not exit after TERM: pid=${PID}" >&2
exit 4
