#!/usr/bin/env bash
# Stop only the project-owned Factory L2 Phase 1 QGC/RViz run for one run_id.

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
ACTIVE_POINTER="${PROJECT_ROOT}/Results/ui_platform/qgc_active_run.json"
RUN_ID="${1:-}"

if [[ -z "${RUN_ID}" && -f "${ACTIVE_POINTER}" ]]; then
  RUN_ID="$(python3 - "${ACTIVE_POINTER}" <<'PY'
import json
import sys

try:
    value = json.loads(open(sys.argv[1], encoding="utf-8").read()).get("run_id", "")
except (OSError, json.JSONDecodeError):
    value = ""
print(value)
PY
)"
fi

if [[ ! "${RUN_ID}" =~ ^qgc-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$ ]]; then
  echo "Usage: bash Scripts/sunray/stop_factory_l2_rviz_qgc_phase1.sh <qgc-run-id>" >&2
  exit 2
fi

if ! command -v ss >/dev/null 2>&1; then
  echo "BLOCKER Phase 1 stop requires ss in Ubuntu-20.04." >&2
  exit 2
fi

has_run_environment() {
  local pid="$1"
  [[ -r "/proc/${pid}/environ" ]] || return 1
  tr '\0' '\n' < "/proc/${pid}/environ" 2>/dev/null | grep -Fqx "MOSIM_OPERATOR_RUN_ID=${RUN_ID}"
}

phase1_gate_pids=()
owned_runtime_pids=()
while read -r pid args; do
  [[ "${pid}" =~ ^[0-9]+$ ]] || continue
  has_run_environment "${pid}" || continue
  if [[ "${args}" == *"run_qgc_diff_realtime_goal_gate.sh rviz_qgc_display_phase1"* ]]; then
    phase1_gate_pids+=("${pid}")
  fi
  case "${args}" in
    *gzserver*|*px4*|*roslaunch*|*mavros*|*rviz*|*roscore*|*fast_lio*|*px4ctrl*|*qgc_diff*|*run_px4ctrl_ego_single_gate*)
      owned_runtime_pids+=("${pid}")
      ;;
  esac
done < <(ps -eo pid=,args=)

target_pids=("${phase1_gate_pids[@]}")
if [[ "${#target_pids[@]}" -eq 0 ]]; then
  target_pids=("${owned_runtime_pids[@]}")
fi

if [[ "${#target_pids[@]}" -eq 0 ]]; then
  echo "No live Phase 1 process owned by ${RUN_ID} was found. Check 11345 before clearing the pointer." >&2
else
  printf 'Stopping Phase 1 process(es) for %s: %s\n' "${RUN_ID}" "${target_pids[*]}"
  for pid in "${target_pids[@]}"; do
    kill -INT "${pid}" 2>/dev/null || true
  done
  for _ in $(seq 1 20); do
    alive=false
    for pid in "${target_pids[@]}"; do
      if kill -0 "${pid}" 2>/dev/null; then
        alive=true
        break
      fi
    done
    [[ "${alive}" == false ]] && break
    sleep 1
  done
  for pid in "${target_pids[@]}"; do
    if kill -0 "${pid}" 2>/dev/null; then
      kill -TERM "${pid}" 2>/dev/null || true
    fi
  done
fi

for _ in $(seq 1 10); do
  listeners="$(ss -ltnp 2>/dev/null | awk -v port=':11345' '$4 ~ (port "$" )')"
  if [[ -z "${listeners}" ]]; then
    echo "Gazebo master port 11345 is free. Clear the Phase 1 pointer only after this check."
    exit 0
  fi
  sleep 1
done

echo "BLOCKER Gazebo master port 11345 is still in use after the owned stop request." >&2
printf '%s\n' "${listeners}" >&2
exit 1
