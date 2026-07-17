#!/usr/bin/env bash
# Run one G9 controller gate and attach same-run generated-C provenance.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
PROFILE="${1:-}"
MISSION="${2:-takeoff_hover_land}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/control_platform/controller_family_final_acceptance_20260717/g9_core/${PROFILE}/${MISSION}}"
MOSIM_PX4_WORK_DIR="${MOSIM_PX4_WORK_DIR:-${RESULT_DIR}/px4_work}"
GENERATED_CODE_DIR="${PROJECT_ROOT}/Results/g9/controller_family_attitude_thrust_v1/g9_family_mworks_codegen_20260630_work/g9_family_cfunction_codegen_strict/G9_Family_CFunction_Sysblock"
CODEGEN_MANIFEST="${PROJECT_ROOT}/Results/g9/controller_family_attitude_thrust_v1/g9_family_mworks_codegen_20260630_work/generate_model_code_result.json"

case "${PROFILE}" in
  official_pid|se3_basic|dfbc_basic|smc_boundary_layer|pid_indi|nmpc_outer) ;;
  *) echo "Unsupported G9 profile: ${PROFILE}" >&2; exit 2 ;;
esac
case "${MISSION}" in
  takeoff_hover_land|figure8) ;;
  *) echo "Unsupported final-acceptance mission: ${MISSION}" >&2; exit 2 ;;
esac

mkdir -p "${RESULT_DIR}" "${MOSIM_PX4_WORK_DIR}"
export MOSIM_PX4_WORK_DIR

gate_rc=0
RUN_ID="g9_final_${PROFILE}_${MISSION}_20260717" \
RESULT_DIR="${RESULT_DIR}" \
PX4CTRL_WS="${PX4CTRL_WS}" \
PX4CTRL_CORE_PROFILE="${PROFILE}" \
SUNRAY_GAZEBO_LAUNCH_FILE="${PROJECT_ROOT}/Scripts/sunray/g9_single_uav_isolated_px4.launch" \
PX4CTRL_EXTRA_PARAM_OVERRIDES="CAL_GYRO0_XOFF=-0.001141657936386764,CAL_GYRO0_YOFF=-0.004853107035160065,CAL_GYRO0_ZOFF=-0.00022918041213415563,CAL_ACC0_XOFF=-0.19448795914649963,CAL_ACC0_YOFF=0.1512581706047058,CAL_ACC0_ZOFF=-0.0606503039598465" \
GUI=false \
REVIEW_OPEN_RVIZ=false \
REVIEW_START_FASTLIO=false \
PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=false \
TOTAL_TIMEOUT_S="${G9_FINAL_TOTAL_TIMEOUT_S:-300}" \
bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" "${MISSION}" || gate_rc=$?

provenance_rc=0
python3 "${PROJECT_ROOT}/Scripts/sunray/check_g9_generated_runtime_provenance.py" \
  --project-root "${PROJECT_ROOT}" \
  --px4ctrl-workspace "${PX4CTRL_WS}" \
  --generated-code-dir "${GENERATED_CODE_DIR}" \
  --codegen-manifest "${CODEGEN_MANIFEST}" \
  --controller-profile "${PROFILE}" \
  --runtime-log "${RESULT_DIR}/px4ctrl.log" \
  --require-runtime-ack \
  --json-out "${RESULT_DIR}/G9_GENERATED_RUNTIME_PROVENANCE.json" || provenance_rc=$?

if [[ "${gate_rc}" -ne 0 ]]; then
  exit "${gate_rc}"
fi
exit "${provenance_rc}"
