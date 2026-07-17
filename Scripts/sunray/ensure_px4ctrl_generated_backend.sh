#!/usr/bin/env bash
set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
BACKEND="${1:-}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_backend_ensure}"

case "${BACKEND}" in
  legacy_px4ctrl|g9_family|g10_bde_family|pid_attitude_thrust|linear_robust_attitude_thrust|classic_controller_attitude_thrust|sliding_mode_attitude_thrust|mpc_attitude_thrust|enhancement_attitude_thrust|learning_attitude_thrust|safety_supervisor)
    ;;
  *)
    echo "unsupported px4ctrl generated backend: ${BACKEND:-missing}" >&2
    exit 2
    ;;
esac

mkdir -p "${RESULT_DIR}"
cache="${PX4CTRL_WS}/build/CMakeCache.txt"
flags="${PX4CTRL_WS}/build/px4ctrl/CMakeFiles/px4ctrl_node.dir/flags.make"
current=""
if [[ -f "${cache}" ]]; then
  current="$(sed -n 's/^MOSIM_PX4CTRL_GENERATED_BACKEND:[^=]*=//p' "${cache}" | tail -1)"
fi

definition="MOSIM_PX4CTRL_GENERATED_BACKEND_$(printf '%s' "${BACKEND}" | tr '[:lower:]' '[:upper:]')"
fingerprint_file="${PX4CTRL_WS}/build/.mosim_${BACKEND}_source_fingerprint"
fingerprint_inputs=(
  "${PROJECT_ROOT}/References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl/CMakeLists.txt"
  "${PROJECT_ROOT}/References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl/src/controller.cpp"
)
if [[ "${BACKEND}" == "learning_attitude_thrust" ]]; then
  fingerprint_inputs+=(
    "${PROJECT_ROOT}/Results/control_platform/p9_learning_mworks_20260717/generated_c/MoSim_P9_Learning_AttitudeThrust_CFunction_Sysblock"
  )
fi
if [[ "${BACKEND}" == "classic_controller_attitude_thrust" ]]; then
  fingerprint_inputs+=(
    "${PROJECT_ROOT}/Results/control_platform/classic_controller_closeout_20260717/mworks/codegen/MoSim_Classic_CFunction_Sysblock"
  )
fi
source_fingerprint="$({
  for input in "${fingerprint_inputs[@]}"; do
    if [[ -d "${input}" ]]; then
      find "${input}" -type f -print0 | sort -z | xargs -0 sha256sum
    else
      sha256sum "${input}"
    fi
  done
} | sha256sum | awk '{print $1}')"
recorded_fingerprint="$(cat "${fingerprint_file}" 2>/dev/null || true)"
if [[ "${current}" == "${BACKEND}" && -x "${PX4CTRL_WS}/devel/lib/px4ctrl/px4ctrl_node" ]] && \
   grep -q "${definition}" "${flags}" 2>/dev/null && \
   [[ "${recorded_fingerprint}" == "${source_fingerprint}" ]]; then
  status="reused"
else
  source /opt/ros/noetic/setup.bash
  cmake_args=(
    -DMOSIM_PX4CTRL_GENERATED_BACKEND="${BACKEND}"
    -DCMAKE_BUILD_TYPE=Release
  )
  if [[ "${BACKEND}" == "pid_attitude_thrust" ]]; then
    cmake_args+=(
      -DMOSIM_PX4CTRL_PID_ATTITUDE_THRUST_GENERATED_DIR="${PROJECT_ROOT}/Results/control_platform/p1_pid_attitude_thrust_mworks_20260716/generated_c_v2/MoSim_PID_AttitudeThrust_CFunction_Sysblock"
    )
  fi
  catkin_make --force-cmake -C "${PX4CTRL_WS}" "${cmake_args[@]}" \
    > "${RESULT_DIR}/px4ctrl_backend_build.log" 2>&1
  status="built"
  printf '%s\n' "${source_fingerprint}" > "${fingerprint_file}"
fi

current="$(sed -n 's/^MOSIM_PX4CTRL_GENERATED_BACKEND:[^=]*=//p' "${cache}" | tail -1)"
if [[ "${current}" != "${BACKEND}" ]] || ! grep -q "${definition}" "${flags}"; then
  echo "px4ctrl backend verification failed: current=${current}, expected=${BACKEND}" >&2
  exit 4
fi

python3 - "${RESULT_DIR}/PX4CTRL_BACKEND_ENSURE.json" "${BACKEND}" "${status}" "${PX4CTRL_WS}" "${definition}" <<'PY'
import hashlib
import json
import pathlib
import sys
import time

output, backend, status, workspace, definition = sys.argv[1:]
binary = pathlib.Path(workspace) / "devel/lib/px4ctrl/px4ctrl_node"
payload = {
    "schema": "mosim.px4ctrl.generated_backend_ensure.v1",
    "status": "passed",
    "action": status,
    "backend": backend,
    "build_definition": definition,
    "workspace": workspace,
    "binary": str(binary),
    "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
    "completed_at": time.time(),
    "claim_boundary": "Build selection evidence only; runtime acknowledgement is required separately.",
}
pathlib.Path(output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY
