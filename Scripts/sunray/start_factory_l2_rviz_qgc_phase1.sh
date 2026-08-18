#!/usr/bin/env bash
# Start the published Factory L2 Phase 1 RViz-to-QGC display run from a visible WSL terminal.

set -euo pipefail

if [[ "$#" -gt 1 ]]; then
  echo "Usage: $0 [run-id]" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REQUESTED_RUN_ID="${1:-}"

# Fail before creating a RunManifest when another Gazebo Classic server owns
# the default Phase 1 master port. The full gate keeps a second guard later in
# startup, but this check prevents a stale active pointer on a known conflict.
GAZEBO_MASTER_URI="${GAZEBO_MASTER_URI:-http://127.0.0.1:11345}"
export GAZEBO_MASTER_URI
GAZEBO_MASTER_PORT="${GAZEBO_MASTER_URI##*:}"
GAZEBO_MASTER_PORT="${GAZEBO_MASTER_PORT%/}"
if [[ ! "${GAZEBO_MASTER_PORT}" =~ ^[1-9][0-9]{0,4}$ ]] || (( GAZEBO_MASTER_PORT > 65535 )); then
  echo "BLOCKER invalid GAZEBO_MASTER_URI: ${GAZEBO_MASTER_URI}" >&2
  exit 2
fi
if ! command -v ss >/dev/null 2>&1; then
  echo "BLOCKER Gazebo master port precheck requires ss in Ubuntu-20.04." >&2
  exit 2
fi
GAZEBO_LISTENERS="$(ss -ltnp 2>/dev/null | awk -v port=":${GAZEBO_MASTER_PORT}" '$4 ~ (port "$" )')"
if [[ -n "${GAZEBO_LISTENERS}" ]]; then
  echo "BLOCKER gazebo_master_port_in_use: ${GAZEBO_MASTER_PORT}" >&2
  printf '%s\n' "${GAZEBO_LISTENERS}" >&2
  echo "Stop the owning managed run, verify the port is free, then rerun this Phase 1 launcher." >&2
  exit 3
fi

prepare_args=(
  --profile-id "px4ctrl_graphical_c99_factory_rviz_qgc_display_phase1_v1"
  --runtime-profile-id "sunray_ros1_factory_l2_graphical_px4ctrl_c99_rviz_qgc_display_phase1_v1"
  --prepared-by "terminal_rviz_qgc_display_phase1"
  --print-run-id
)
if [[ -n "${REQUESTED_RUN_ID}" ]]; then
  prepare_args+=(--run-id "${REQUESTED_RUN_ID}")
fi

RUN_ID="$(python3 "${PROJECT_ROOT}/Scripts/ui/prepare_operator_run.py" "${prepare_args[@]}")"
export MOSIM_OPERATOR_RUN_ID="${RUN_ID}"
export MOSIM_OPERATOR_RUN_DIR="${PROJECT_ROOT}/Results/runs/${RUN_ID}"
export MOSIM_OPERATOR_RUN_MANIFEST="${MOSIM_OPERATOR_RUN_DIR}/RUN_MANIFEST.json"
export GUI=false

printf 'Prepared Factory L2 Phase 1 run: %s\n' "${RUN_ID}"
printf 'Run manifest: %s\n' "${MOSIM_OPERATOR_RUN_MANIFEST}"
exec bash "${PROJECT_ROOT}/Scripts/sunray/run_qgc_diff_realtime_goal_gate.sh" rviz_qgc_display_phase1
