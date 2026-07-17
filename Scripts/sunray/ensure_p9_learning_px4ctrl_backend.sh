#!/usr/bin/env bash
set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_backend_ensure}"
BACKEND="learning_attitude_thrust"
DEFINITION="MOSIM_PX4CTRL_GENERATED_BACKEND_LEARNING_ATTITUDE_THRUST"
GENERATED_DIR="${PROJECT_ROOT}/Results/control_platform/p9_learning_mworks_20260717/generated_c/MoSim_P9_Learning_AttitudeThrust_CFunction_Sysblock"

mkdir -p "${RESULT_DIR}"
cache="${PX4CTRL_WS}/build/CMakeCache.txt"
flags="${PX4CTRL_WS}/build/px4ctrl/CMakeFiles/px4ctrl_node.dir/flags.make"
fingerprint_file="${PX4CTRL_WS}/build/.mosim_${BACKEND}_source_fingerprint"
source_fingerprint="$({
  sha256sum \
    "${PROJECT_ROOT}/References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl/CMakeLists.txt" \
    "${PROJECT_ROOT}/References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl/src/controller.cpp"
  find "${GENERATED_DIR}" -type f -print0 | sort -z | xargs -0 sha256sum
} | sha256sum | awk '{print $1}')"
current="$(sed -n 's/^MOSIM_PX4CTRL_GENERATED_BACKEND:[^=]*=//p' "${cache}" 2>/dev/null | tail -1)"
recorded_fingerprint="$(cat "${fingerprint_file}" 2>/dev/null || true)"

if [[ "${current}" == "${BACKEND}" && -x "${PX4CTRL_WS}/devel/lib/px4ctrl/px4ctrl_node" ]] && \
   grep -q "${DEFINITION}" "${flags}" 2>/dev/null && \
   [[ "${recorded_fingerprint}" == "${source_fingerprint}" ]]; then
  status="reused"
else
  source /opt/ros/noetic/setup.bash
  catkin_make --force-cmake -C "${PX4CTRL_WS}" \
    -DMOSIM_PX4CTRL_GENERATED_BACKEND="${BACKEND}" \
    -DMOSIM_PX4CTRL_LEARNING_ATTITUDE_THRUST_GENERATED_DIR="${GENERATED_DIR}" \
    -DCMAKE_BUILD_TYPE=Release \
    > "${RESULT_DIR}/px4ctrl_backend_build.log" 2>&1
  status="built"
  printf '%s\n' "${source_fingerprint}" > "${fingerprint_file}"
fi

current="$(sed -n 's/^MOSIM_PX4CTRL_GENERATED_BACKEND:[^=]*=//p' "${cache}" | tail -1)"
if [[ "${current}" != "${BACKEND}" ]] || ! grep -q "${DEFINITION}" "${flags}"; then
  echo "px4ctrl backend verification failed: current=${current}, expected=${BACKEND}" >&2
  exit 4
fi

python3 - "${RESULT_DIR}/PX4CTRL_BACKEND_ENSURE.json" "${status}" "${PX4CTRL_WS}" "${DEFINITION}" "${source_fingerprint}" <<'PY'
import hashlib
import json
import pathlib
import sys
import time

output, status, workspace, definition, source_fingerprint = sys.argv[1:]
binary = pathlib.Path(workspace) / "devel/lib/px4ctrl/px4ctrl_node"
payload = {
    "schema": "mosim.p9_learning.px4ctrl_backend_ensure.v1",
    "status": "passed",
    "action": status,
    "backend": "learning_attitude_thrust",
    "build_definition": definition,
    "workspace": workspace,
    "binary": str(binary),
    "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
    "source_fingerprint": source_fingerprint,
    "completed_at": time.time(),
    "claim_boundary": "Build selection evidence only; runtime acknowledgement is required separately.",
}
pathlib.Path(output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY
