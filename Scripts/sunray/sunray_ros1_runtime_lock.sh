#!/usr/bin/env bash

# Cross-run guard for the shared ROS master, Gazebo, PX4, and MAVROS ports.

SUNRAY_ROS1_RUNTIME_LOCK_OWNED="${SUNRAY_ROS1_RUNTIME_LOCK_OWNED:-false}"

sunray_ros1_runtime_lock_release() {
  if [[ "${SUNRAY_ROS1_RUNTIME_LOCK_OWNED}" != "true" ]]; then
    return
  fi

  local lock_dir="${SUNRAY_ROS1_RUNTIME_LOCK_DIR}"
  local nonce_file="${lock_dir}/owner_nonce"
  local recorded_nonce=""
  if [[ -f "${nonce_file}" ]]; then
    recorded_nonce="$(<"${nonce_file}")"
  fi
  if [[ -n "${SUNRAY_ROS1_RUNTIME_LOCK_NONCE:-}" && "${recorded_nonce}" == "${SUNRAY_ROS1_RUNTIME_LOCK_NONCE}" ]]; then
    rm -f -- \
      "${lock_dir}/boot_id" \
      "${lock_dir}/owner_pid" \
      "${lock_dir}/run_id" \
      "${lock_dir}/owner_nonce"
    rmdir -- "${lock_dir}" 2>/dev/null || true
  fi
  SUNRAY_ROS1_RUNTIME_LOCK_OWNED=false
}

sunray_ros1_runtime_lock_acquire() {
  SUNRAY_ROS1_RUNTIME_LOCK_DIR="${SUNRAY_ROS1_RUNTIME_LOCK_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/.sunray_ros1_runtime.lock}"

  # Retry children inherit the top-level owner's nonce and must not self-deadlock.
  if [[ -n "${SUNRAY_ROS1_RUNTIME_LOCK_NONCE:-}" && -f "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/owner_nonce" ]]; then
    local inherited_nonce
    local inherited_owner_pid=""
    inherited_nonce="$(<"${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/owner_nonce")"
    [[ -f "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/owner_pid" ]] && inherited_owner_pid="$(<"${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/owner_pid")"
    if [[ "${inherited_nonce}" == "${SUNRAY_ROS1_RUNTIME_LOCK_NONCE}" ]]; then
      # exec preserves PID and ownership; retry children have a different PID.
      if [[ "${inherited_owner_pid}" == "$$" ]]; then
        SUNRAY_ROS1_RUNTIME_LOCK_OWNED=true
      else
        SUNRAY_ROS1_RUNTIME_LOCK_OWNED=false
      fi
      return 0
    fi
  fi

  mkdir -p -- "$(dirname "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}")"
  local current_boot_id
  current_boot_id="$(</proc/sys/kernel/random/boot_id)"

  local attempt
  for attempt in 1 2; do
    if mkdir -- "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}" 2>/dev/null; then
      SUNRAY_ROS1_RUNTIME_LOCK_NONCE="${RUN_ID:-unnamed}:$$:${RANDOM}:$(date +%s%N)"
      printf '%s\n' "${current_boot_id}" > "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/boot_id"
      printf '%s\n' "$$" > "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/owner_pid"
      printf '%s\n' "${RUN_ID:-unnamed}" > "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/run_id"
      printf '%s\n' "${SUNRAY_ROS1_RUNTIME_LOCK_NONCE}" > "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/owner_nonce"
      export SUNRAY_ROS1_RUNTIME_LOCK_DIR SUNRAY_ROS1_RUNTIME_LOCK_NONCE
      SUNRAY_ROS1_RUNTIME_LOCK_OWNED=true
      return 0
    fi

    local owner_boot_id=""
    local owner_pid=""
    local owner_run_id="unknown"
    [[ -f "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/boot_id" ]] && owner_boot_id="$(<"${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/boot_id")"
    [[ -f "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/owner_pid" ]] && owner_pid="$(<"${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/owner_pid")"
    [[ -f "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/run_id" ]] && owner_run_id="$(<"${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/run_id")"

    if [[ "${owner_boot_id}" == "${current_boot_id}" && "${owner_pid}" =~ ^[0-9]+$ ]] && kill -0 "${owner_pid}" 2>/dev/null; then
      echo "Sunray ROS1 runtime is busy: run_id=${owner_run_id}, pid=${owner_pid}, lock=${SUNRAY_ROS1_RUNTIME_LOCK_DIR}" >&2
      return 11
    fi

    if [[ "${attempt}" == "1" ]]; then
      rm -f -- \
        "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/boot_id" \
        "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/owner_pid" \
        "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/run_id" \
        "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}/owner_nonce"
      rmdir -- "${SUNRAY_ROS1_RUNTIME_LOCK_DIR}" 2>/dev/null || {
        echo "Sunray ROS1 runtime lock is invalid and could not be recovered: ${SUNRAY_ROS1_RUNTIME_LOCK_DIR}" >&2
        return 11
      }
    fi
  done

  echo "Sunray ROS1 runtime lock acquisition failed: ${SUNRAY_ROS1_RUNTIME_LOCK_DIR}" >&2
  return 11
}
