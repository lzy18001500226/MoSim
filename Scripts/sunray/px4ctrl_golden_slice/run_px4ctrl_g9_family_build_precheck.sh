#!/usr/bin/env bash
# Build-only gate for the reversible px4ctrl generated-controller backend.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
BACKEND="${BACKEND:-g9_family}"
RUN_ID="${RUN_ID:-px4ctrl_${BACKEND}_build_precheck_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
PREFLIGHT_SCRIPT="${PROJECT_ROOT}/Scripts/sunray/check_sunray_ros1_runtime_preflight.sh"
FORCE_CMAKE="${FORCE_CMAKE:-true}"

case "${BACKEND}" in
  legacy_px4ctrl|g9_family|g10_bde_family)
    ;;
  *)
    echo "Unsupported BACKEND=${BACKEND}; expected legacy_px4ctrl, g9_family, or g10_bde_family" >&2
    exit 2
    ;;
esac

mkdir -p "${RESULT_DIR}"

json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read())[1:-1])'
}

write_manifest() {
  local status="$1"
  local reason="$2"
  cat > "${RESULT_DIR}/RUN_MANIFEST.json" <<EOF
{
  "schema": "mosim.sunray_ros1.px4ctrl_generated_backend_build_precheck.v1",
  "status": "${status}",
  "reason": "$(printf '%s' "${reason}" | json_escape)",
  "backend": "${BACKEND}",
  "result_dir": "${RESULT_DIR}",
  "project_root": "${PROJECT_ROOT}",
  "px4ctrl_ws": "${PX4CTRL_WS}",
  "force_cmake": "${FORCE_CMAKE}",
  "preflight_log": "${RESULT_DIR}/sunray_ros1_preflight.log",
  "catkin_make_log": "${RESULT_DIR}/px4ctrl_catkin_make_${BACKEND}.log",
  "claim_boundary": "Build/preflight only for the selected px4ctrl generated backend. This does not claim Gazebo runtime flight, Diff compatibility, or MWORKS controller performance."
}
EOF
}

require_file() {
  local path="$1"
  if [[ ! -f "${path}" ]]; then
    echo "Missing required file: ${path}" >&2
    return 1
  fi
}

require_dir() {
  local path="$1"
  if [[ ! -d "${path}" ]]; then
    echo "Missing required directory: ${path}" >&2
    return 1
  fi
}

write_manifest "running" "precheck_started"

require_file "${PREFLIGHT_SCRIPT}"
require_dir "${PX4CTRL_WS}"
require_file "${PX4CTRL_WS}/src/px4ctrl/CMakeLists.txt"

bash "${PREFLIGHT_SCRIPT}" > "${RESULT_DIR}/sunray_ros1_preflight.log" 2>&1

source /opt/ros/noetic/setup.bash

CATKIN_ARGS=(-C "${PX4CTRL_WS}" "-DMOSIM_PX4CTRL_GENERATED_BACKEND=${BACKEND}")
if [[ "${FORCE_CMAKE}" == "true" ]]; then
  CATKIN_ARGS=(--force-cmake "${CATKIN_ARGS[@]}")
fi

catkin_make "${CATKIN_ARGS[@]}" > "${RESULT_DIR}/px4ctrl_catkin_make_${BACKEND}.log" 2>&1

write_manifest "passed" "preflight_and_catkin_make_passed"

cat > "${RESULT_DIR}/SUMMARY.md" <<EOF
# PX4CTRL Generated Backend Build Precheck

- status: \`passed\`
- backend: \`${BACKEND}\`
- px4ctrl_ws: \`${PX4CTRL_WS}\`
- preflight: \`${RESULT_DIR}/sunray_ros1_preflight.log\`
- build: \`${RESULT_DIR}/px4ctrl_catkin_make_${BACKEND}.log\`
- claim boundary: build/preflight only; no Gazebo runtime flight.
EOF

echo "${RESULT_DIR}"
