#!/usr/bin/env bash
# Run bounded P6 SafetySupervisor event probes against the ROS1 Gazebo plant.
# Ordinary mission success is not required for stop/hold/return events; the
# fail-closed provenance checker is the acceptance authority.

set -uo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_ROOT="${RESULT_ROOT:-${PROJECT_ROOT}/Results/control_platform/p6_safety_runtime_20260717}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
GENERATED_DIR="${PROJECT_ROOT}/Results/control_platform/p6_safety_mworks_20260717/generated_c/MoSim_P6_SafetySupervisor_CFunction_Sysblock"
BUILD_MANIFEST="${PROJECT_ROOT}/Results/control_platform/p6_safety_mworks_20260717/BUILD_MANIFEST.json"
SIL_REPORT="${PROJECT_ROOT}/Results/control_platform/p6_safety_mworks_20260717/sil/P6_GENERATED_SIL_EQUIVALENCE.json"
MODES_TEXT="${P6_SAFETY_MODES:-safety_filter cbf reference_governor geofence emergency_stop return_and_land failsafe_state_machine}"

mkdir -p "${RESULT_ROOT}"
: > "${RESULT_ROOT}/matrix_status.tsv"

for mode in ${MODES_TEXT}; do
  result_dir="${RESULT_ROOT}/${mode}"
  gate_rc=0
  checker_rc=0
  RUN_ID="p6_${mode}_runtime_20260717" \
  RESULT_DIR="${result_dir}" \
  PX4CTRL_CORE_PROFILE="${mode}" \
  PX4CTRL_SAFETY_TEST_EVENT=true \
  TOTAL_TIMEOUT_S="${P6_TOTAL_TIMEOUT_S:-55}" \
  CONTROL_DIAGNOSTICS_DURATION_S="${P6_DIAGNOSTICS_DURATION_S:-20}" \
  TIME_TF_AUDIT_DURATION_S="${P6_DIAGNOSTICS_DURATION_S:-20}" \
  FREQUENCY_AUDIT_DURATION_S="${P6_FREQUENCY_DURATION_S:-10}" \
  bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" takeoff_hover_land || gate_rc=$?

  python3 "${PROJECT_ROOT}/Scripts/sunray/check_safety_generated_runtime_provenance.py" \
    --px4ctrl-workspace "${PX4CTRL_WS}" \
    --generated-code-dir "${GENERATED_DIR}" \
    --build-manifest "${BUILD_MANIFEST}" \
    --sil-report "${SIL_REPORT}" \
    --controller-profile "${mode}" \
    --runtime-log "${result_dir}/px4ctrl.log" \
    --require-runtime-ack \
    --json-out "${result_dir}/SAFETY_GENERATED_RUNTIME_PROVENANCE.json" || checker_rc=$?

  printf '%s\t%s\t%s\n' "${mode}" "${gate_rc}" "${checker_rc}" >> "${RESULT_ROOT}/matrix_status.tsv"
  sleep 2
done

if awk -F '\t' '$3 != 0 {exit 1}' "${RESULT_ROOT}/matrix_status.tsv"; then
  exit 0
fi
exit 1
