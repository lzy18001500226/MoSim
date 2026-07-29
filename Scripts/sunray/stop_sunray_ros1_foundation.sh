#!/usr/bin/env bash
# Stop only a managed no-flight Sunray foundation run. Other managed tasks own
# the shared ROS/Gazebo/PX4 runtime and are deliberately left untouched.

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
LOCK_DIR="${SUNRAY_ROS1_RUNTIME_LOCK_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/.sunray_ros1_runtime.lock}"

if [[ ! -d "${LOCK_DIR}" ]]; then
  echo "No managed Sunray ROS1 runtime lock is present. Nothing to stop."
  exit 0
fi

read_lock_value() {
  local path="$1"
  if [[ -f "${path}" ]]; then
    cat "${path}"
  fi
}

run_id="$(read_lock_value "${LOCK_DIR}/run_id")"
owner_pid="$(read_lock_value "${LOCK_DIR}/owner_pid")"
owner_boot_id="$(read_lock_value "${LOCK_DIR}/boot_id")"
current_boot_id="$(</proc/sys/kernel/random/boot_id)"

if [[ "${owner_boot_id}" != "${current_boot_id}" || ! "${owner_pid}" =~ ^[0-9]+$ ]] || ! kill -0 "${owner_pid}" 2>/dev/null; then
  echo "Foundation lock is stale or its owner is already gone. It will be reclaimed by the next launch."
  exit 0
fi

# A caller may supply a descriptive RunId, so the identifier alone is not an
# authority boundary. Only interrupt the actual no-flight foundation review
# owner; all other managed Sunray runs retain their own stop routes.
owner_args="$(ps -p "${owner_pid}" -o args= 2>/dev/null || true)"
if [[ "${owner_args}" != *"run_sunray_ros1_foundation_gate.sh --review"* ]]; then
  echo "Refusing to stop run_id=${run_id:-unknown}: owner pid ${owner_pid} is not a managed Sunray foundation review." >&2
  exit 2
fi

echo "Stopping managed foundation run: ${run_id} (owner pid ${owner_pid})"
kill -INT "${owner_pid}" 2>/dev/null || true

for _ in $(seq 1 20); do
  if ! kill -0 "${owner_pid}" 2>/dev/null; then
    echo "Foundation run stopped cleanly."
    exit 0
  fi
  sleep 1
done

echo "Foundation owner did not exit after SIGINT; sending SIGTERM." >&2
kill -TERM "${owner_pid}" 2>/dev/null || true
for _ in $(seq 1 10); do
  if ! kill -0 "${owner_pid}" 2>/dev/null; then
    echo "Foundation run stopped after SIGTERM."
    exit 0
  fi
  sleep 1
done

echo "Foundation owner is still alive. Do not start another task; inspect the active terminal and ${LOCK_DIR}." >&2
exit 1
