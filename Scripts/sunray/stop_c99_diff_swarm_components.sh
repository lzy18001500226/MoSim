#!/usr/bin/env bash
# Stop only the retained components-stage runner and let it clean up its children.

set -euo pipefail

case "${1:-}" in
  "")
    ;;
  -h|--help)
    cat <<'EOF'
Usage: RESULT_DIR=/path/to/run bash Scripts/sunray/stop_c99_diff_swarm_components.sh

Sends SIGINT only to the recorded C99/Diff-Swarm components runner. The runner
then executes its own owned-process cleanup. This script does not use broad
process matching or terminate unrelated ROS, Gazebo, PX4, QGC, or UE sessions.
EOF
    exit 0
    ;;
  *)
    printf 'BLOCKER unexpected argument: %s\n' "$1" >&2
    exit 2
    ;;
esac

RESULT_DIR="${RESULT_DIR:-}"
[[ -n "${RESULT_DIR}" ]] || {
  printf 'BLOCKER RESULT_DIR is required\n' >&2
  exit 2
}
pid_file="${RESULT_DIR}/c99_diff_swarm_components_runner.pid"
runner_pid="$(tr -d '[:space:]' < "${pid_file}" 2>/dev/null || true)"
[[ "${runner_pid}" =~ ^[0-9]+$ ]] || {
  printf 'BLOCKER components runner PID is missing or invalid: %s\n' "${pid_file}" >&2
  exit 2
}

if ! kill -0 "${runner_pid}" >/dev/null 2>&1; then
  printf 'BLOCKER components runner is not active: %s\n' "${runner_pid}" >&2
  exit 2
fi
runner_cmdline="$(tr '\0' ' ' < "/proc/${runner_pid}/cmdline" 2>/dev/null || true)"
[[ "${runner_cmdline}" == *"run_px4ctrl_ego_swarm_gate.sh"* ]] || {
  printf 'BLOCKER PID %s is not the expected swarm gate runner\n' "${runner_pid}" >&2
  exit 2
}

leaf_runner_pid="$(python3 - "${runner_pid}" <<'PY'
import os
import sys

root = int(sys.argv[1])
rows = []
for entry in os.listdir("/proc"):
    if not entry.isdigit():
        continue
    pid = int(entry)
    try:
        stat = open(f"/proc/{pid}/stat", encoding="utf-8").read().split()
        ppid = int(stat[3])
        cmdline = open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ").decode(
            "utf-8", errors="replace"
        )
    except (FileNotFoundError, PermissionError, IndexError, ValueError):
        continue
    rows.append((pid, ppid, cmdline))

children = {}
for pid, ppid, cmdline in rows:
    children.setdefault(ppid, []).append((pid, cmdline))

frontier = [(root, 0)]
matched = []
while frontier:
    parent, depth = frontier.pop()
    for pid, cmdline in children.get(parent, []):
        frontier.append((pid, depth + 1))
        if "run_px4ctrl_ego_swarm_gate.sh" in cmdline:
            matched.append((depth + 1, pid))

if not matched:
    print(root)
else:
    print(max(matched)[1])
PY
)"
[[ "${leaf_runner_pid}" =~ ^[0-9]+$ ]] || {
  printf 'BLOCKER unable to resolve a child swarm gate runner for PID %s\n' "${runner_pid}" >&2
  exit 2
}
leaf_cmdline="$(tr '\0' ' ' < "/proc/${leaf_runner_pid}/cmdline" 2>/dev/null || true)"
[[ "${leaf_cmdline}" == *"run_px4ctrl_ego_swarm_gate.sh"* ]] || {
  printf 'BLOCKER resolved PID %s is not the expected swarm gate runner\n' "${leaf_runner_pid}" >&2
  exit 2
}

kill -INT "${leaf_runner_pid}"
for _ in $(seq 1 45); do
  if ! kill -0 "${runner_pid}" >/dev/null 2>&1; then
    python3 - "${RESULT_DIR}/C99_DIFF_SWARM_COMPONENTS_STOP.json" "${runner_pid}" "${leaf_runner_pid}" <<'PY'
import json
import sys
from pathlib import Path

Path(sys.argv[1]).write_text(
    json.dumps(
        {
            "schema": "mosim.sunray_ros1.c99_diff_swarm_components_stop.v1",
            "status": "stopped",
            "runner_pid": int(sys.argv[2]),
            "active_runner_pid": int(sys.argv[3]),
            "claim_boundary": "SIGINT was limited to the verified deepest swarm-gate runner inside the recorded runner's process tree; cleanup is performed by that runner's owned-process handler.",
        },
        ensure_ascii=True,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
PY
    exit 0
  fi
  sleep 1
done

if [[ "${leaf_runner_pid}" != "${runner_pid}" ]] && kill -0 "${runner_pid}" >/dev/null 2>&1; then
  kill -INT "${runner_pid}"
  for _ in $(seq 1 15); do
    if ! kill -0 "${runner_pid}" >/dev/null 2>&1; then
      exit 0
    fi
    sleep 1
  done
fi

printf 'BLOCKER components runner did not exit after verified SIGINT: root=%s active=%s\n' \
  "${runner_pid}" "${leaf_runner_pid}" >&2
exit 1
