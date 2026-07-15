#!/usr/bin/env bash
# Run G-PX4CTRL-7B: original px4ctrl vs MWORKS generated-C core in Gazebo.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
MISSION="${1:-${MISSION:-takeoff_hover_land}}"
RUN_ID="${RUN_ID:-px4ctrl_g7b_gazebo_ab_${MISSION}_$(date +%Y%m%d_%H%M%S)}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/${RUN_ID}}"
ORIGINAL_PROFILE="${ORIGINAL_PROFILE:-original}"
GENERATED_PROFILE="${GENERATED_PROFILE:-mworks_generated_c}"
PRECHECK_ONLY="${PRECHECK_ONLY:-false}"
RUN_ORIGINAL="${RUN_ORIGINAL:-true}"
RUN_GENERATED="${RUN_GENERATED:-true}"
RUN_COMPARE="${RUN_COMPARE:-true}"
GUI="${GUI:-false}"
TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S:-180}"
POST_MISSION_DIAGNOSTIC_GRACE_S="${POST_MISSION_DIAGNOSTIC_GRACE_S:-3}"
G7B_HOVER_PERCENTAGE="${G7B_HOVER_PERCENTAGE:-${PX4CTRL_HOVER_PERCENTAGE:-0.294}}"
G7B_MAVROS_SET_MESSAGE_INTERVALS="${G7B_MAVROS_SET_MESSAGE_INTERVALS:-${MAVROS_SET_MESSAGE_INTERVALS:-false}}"
G7B_TAKEOFF_HOVER_DEFAULT_ARGS="${G7B_TAKEOFF_HOVER_DEFAULT_ARGS:-${PX4CTRL_TAKEOFF_HOVER_DEFAULT_ARGS:---initial-hover-s 20 --steady-hover-tail-s 8 --force-disarm-after-land --force-disarm-timeout-s 18 --command-x-bias-m -0.006 --command-y-bias-m -0.004 --command-z-bias-m 0.0}}"

G7B_BASIC_GATE="${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh"
G7B_COMPARE="${PROJECT_ROOT}/Scripts/sunray/px4ctrl_golden_slice/compare_px4ctrl_g7_ab_runs.py"
PREFLIGHT_SCRIPT="${PROJECT_ROOT}/Scripts/sunray/check_sunray_ros1_runtime_preflight.sh"
GENERATED_DIR="${GENERATED_DIR:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_mworks_goal5_m4a_cfunction_20260629_092411/px4ctrl_core_cfunction_codegen_strict/PX4CTRL_Core_CFunction_Sysblock}"

case "${MISSION}" in
  takeoff_hover_land|figure8|spiral|circle|step_x|step_y|step_z)
    ;;
  *)
    echo "Unsupported G7B mission=${MISSION}" >&2
    exit 2
    ;;
esac

case "${ORIGINAL_PROFILE}" in
  original)
    ;;
  *)
    echo "ORIGINAL_PROFILE must stay original for G7B A/B, got ${ORIGINAL_PROFILE}" >&2
    exit 2
    ;;
esac

case "${GENERATED_PROFILE}" in
  mworks_generated|generated_c|mworks_generated_c)
    ;;
  *)
    echo "Unsupported GENERATED_PROFILE=${GENERATED_PROFILE}" >&2
    exit 2
    ;;
esac

mkdir -p "${RESULT_DIR}"

mission_to_compare_scenario() {
  case "$1" in
    takeoff_hover_land) echo "hover" ;;
    *) echo "$1" ;;
  esac
}

json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read())[1:-1])'
}

write_manifest() {
  local status="$1"
  local reason="$2"
  local original_dir="${3:-}"
  local generated_dir="${4:-}"
  local compare_dir="${5:-}"
  cat > "${RESULT_DIR}/RUN_MANIFEST.json" <<EOF
{
  "schema": "mosim.sunray_ros1.px4ctrl_g7b_gazebo_ab_gate_manifest.v1",
  "status": "${status}",
  "reason": "$(printf '%s' "${reason}" | json_escape)",
  "mission": "${MISSION}",
  "compare_scenario": "$(mission_to_compare_scenario "${MISSION}")",
  "result_dir": "${RESULT_DIR}",
  "project_root": "${PROJECT_ROOT}",
  "px4ctrl_ws": "${PX4CTRL_WS}",
  "generated_dir": "${GENERATED_DIR}",
  "original_profile": "${ORIGINAL_PROFILE}",
  "generated_profile": "${GENERATED_PROFILE}",
  "precheck_only": ${PRECHECK_ONLY},
  "gui": "${GUI}",
  "total_timeout_s": ${TOTAL_TIMEOUT_S},
  "post_mission_diagnostic_grace_s": ${POST_MISSION_DIAGNOSTIC_GRACE_S},
  "g7b_hover_percentage": "${G7B_HOVER_PERCENTAGE}",
  "g7b_mavros_set_message_intervals": "${G7B_MAVROS_SET_MESSAGE_INTERVALS}",
  "g7b_takeoff_hover_default_args": "$(printf '%s' "${G7B_TAKEOFF_HOVER_DEFAULT_ARGS}" | json_escape)",
  "original_run_dir": "${original_dir}",
  "generated_run_dir": "${generated_dir}",
  "compare_dir": "${compare_dir}",
  "claim_boundary": "G-PX4CTRL-7B compares original Fast-Drone-250 px4ctrl core against accepted MWORKS CFunction generated-C core inside the same Sunray ROS1/PX4/MAVROS/Gazebo wrapper. This is not advanced controller development or PX4-native uORB deployment."
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

run_precheck() {
  require_file "${PREFLIGHT_SCRIPT}"
  require_file "${G7B_BASIC_GATE}"
  require_file "${G7B_COMPARE}"
  require_dir "${PX4CTRL_WS}"
  require_file "${PX4CTRL_WS}/src/px4ctrl/CMakeLists.txt"
  require_file "${GENERATED_DIR}/PX4CTRL_Core_CFunction_Sysblock.c"
  require_file "${GENERATED_DIR}/PX4CTRL_Core_CFunction_Sysblock.h"
  require_file "${GENERATED_DIR}/PX4CTRL_Core_CFunction_Sysblock_data.c"
  require_file "${GENERATED_DIR}/PX4CTRL_Core_CFunction_Sysblock_private.h"
  require_file "${GENERATED_DIR}/extern_inc/momodel_extern_ince1.c"

  bash "${PREFLIGHT_SCRIPT}" > "${RESULT_DIR}/sunray_ros1_preflight.log" 2>&1

  # The Windows->WSL non-interactive entry may not inherit ROS tools in PATH.
  # Source Noetic explicitly before catkin_make so the build gate is reproducible.
  source /opt/ros/noetic/setup.bash

  (
    cd "${PROJECT_ROOT}"
    python3 -m py_compile "${G7B_COMPARE}"
  ) > "${RESULT_DIR}/compare_py_compile.log" 2>&1

  catkin_make -C "${PX4CTRL_WS}" > "${RESULT_DIR}/px4ctrl_catkin_make.log" 2>&1
}

run_one_profile() {
  local profile="$1"
  local label="$2"
  local run_id="${RUN_ID}_${label}"
  local run_dir="${RESULT_DIR}/${label}"
  mkdir -p "${run_dir}"
  (
    cd "${PROJECT_ROOT}"
    PROJECT_ROOT="${PROJECT_ROOT}" \
    PX4CTRL_WS="${PX4CTRL_WS}" \
    PX4CTRL_CORE_PROFILE="${profile}" \
    RUN_ID="${run_id}" \
    RESULT_DIR="${run_dir}" \
    GUI="${GUI}" \
    TOTAL_TIMEOUT_S="${TOTAL_TIMEOUT_S}" \
    POST_MISSION_DIAGNOSTIC_GRACE_S="${POST_MISSION_DIAGNOSTIC_GRACE_S}" \
    MAVROS_SET_MESSAGE_INTERVALS="${G7B_MAVROS_SET_MESSAGE_INTERVALS}" \
    PX4CTRL_HOVER_PERCENTAGE="${G7B_HOVER_PERCENTAGE}" \
    PX4CTRL_MISSION_EXTRA_ARGS="${PX4CTRL_MISSION_EXTRA_ARGS:-}" \
    PX4CTRL_TAKEOFF_HOVER_DEFAULT_ARGS="${G7B_TAKEOFF_HOVER_DEFAULT_ARGS}" \
    bash "${G7B_BASIC_GATE}" "${MISSION}"
  ) > "${RESULT_DIR}/${label}_run.log" 2>&1
  echo "${run_dir}"
}

write_manifest "running" "precheck" "" "" ""
run_precheck

if [[ "${PRECHECK_ONLY}" == "true" ]]; then
  write_manifest "passed" "precheck_only" "" "" ""
  cat > "${RESULT_DIR}/SUMMARY.md" <<EOF
# PX4CTRL G7B Gazebo A/B Gate

- status: \`passed\`
- mode: \`PRECHECK_ONLY\`
- mission: \`${MISSION}\`
- px4ctrl_ws: \`${PX4CTRL_WS}\`
- generated_dir: \`${GENERATED_DIR}\`
- preflight: \`${RESULT_DIR}/sunray_ros1_preflight.log\`
- build: \`${RESULT_DIR}/px4ctrl_catkin_make.log\`
EOF
  echo "${RESULT_DIR}"
  exit 0
fi

ORIGINAL_RUN_DIR=""
GENERATED_RUN_DIR=""
COMPARE_DIR="${RESULT_DIR}/compare"

if [[ "${RUN_ORIGINAL}" == "true" ]]; then
  ORIGINAL_RUN_DIR="$(run_one_profile "${ORIGINAL_PROFILE}" "original")"
fi

if [[ "${RUN_GENERATED}" == "true" ]]; then
  GENERATED_RUN_DIR="$(run_one_profile "${GENERATED_PROFILE}" "generated")"
fi

COMPARE_STATUS="skipped"
if [[ "${RUN_COMPARE}" == "true" ]]; then
  if [[ -z "${ORIGINAL_RUN_DIR}" || -z "${GENERATED_RUN_DIR}" ]]; then
    echo "RUN_COMPARE=true requires both original and generated runs in this invocation." >&2
    write_manifest "blocked" "compare_requested_without_both_runs" "${ORIGINAL_RUN_DIR}" "${GENERATED_RUN_DIR}" "${COMPARE_DIR}"
    exit 2
  fi
  mkdir -p "${COMPARE_DIR}"
  set +e
  python3 "${G7B_COMPARE}" \
    --original-run-dir "${ORIGINAL_RUN_DIR}" \
    --generated-run-dir "${GENERATED_RUN_DIR}" \
    --out-dir "${COMPARE_DIR}" \
    --scenario "$(mission_to_compare_scenario "${MISSION}")" \
    > "${RESULT_DIR}/compare.log" 2>&1
  COMPARE_EXIT=$?
  set -e
  if [[ "${COMPARE_EXIT}" -eq 0 ]]; then
    COMPARE_STATUS="passed"
  else
    COMPARE_STATUS="blocked"
  fi
fi

FINAL_STATUS="${COMPARE_STATUS}"
if [[ "${COMPARE_STATUS}" == "skipped" ]]; then
  FINAL_STATUS="passed"
fi
write_manifest "${FINAL_STATUS}" "g7b_${COMPARE_STATUS}" "${ORIGINAL_RUN_DIR}" "${GENERATED_RUN_DIR}" "${COMPARE_DIR}"

cat > "${RESULT_DIR}/SUMMARY.md" <<EOF
# PX4CTRL G7B Gazebo A/B Gate

- status: \`${FINAL_STATUS}\`
- mission: \`${MISSION}\`
- compare_scenario: \`$(mission_to_compare_scenario "${MISSION}")\`
- original: \`${ORIGINAL_RUN_DIR}\`
- generated: \`${GENERATED_RUN_DIR}\`
- compare: \`${COMPARE_DIR}\`
- preflight: \`${RESULT_DIR}/sunray_ros1_preflight.log\`
- build: \`${RESULT_DIR}/px4ctrl_catkin_make.log\`
EOF

echo "${RESULT_DIR}"
if [[ "${FINAL_STATUS}" == "passed" ]]; then
  exit 0
fi
exit 2
