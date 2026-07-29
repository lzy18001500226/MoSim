#!/usr/bin/env bash
# Run one P10 generated controller through the bounded Sunray Gazebo gate.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
PROFILE="${1:-}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/control_platform/p10_generated_gazebo_20260718/${PROFILE}/takeoff_hover_land}"
bodyrate=false

case "${PROFILE}" in
  l1_awff_minimal)
    backend=p10_l1_awff
    generated_dir="${PROJECT_ROOT}/Results/control_platform/p10_mworks_gap_closeout_20260718/l1_awff_minimal/codegen/MoSim_P10_G10_BDE_CFunction_Sysblock"
    ;;
  hinf_hover_wrench)
    backend=p10_hinf_wrench
    generated_dir="${PROJECT_ROOT}/Results/control_platform/p10_mworks_gap_closeout_20260718/hinf_hover_wrench/codegen/MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock"
    ;;
  dfbc_high_order_attitude|dfbc_smooth_robust_attitude|dfbc_dob_eso_disabled|dfbc_dob_eso)
    backend=p10_dfbc_family
    generated_dir="${PROJECT_ROOT}/Results/control_platform/p10_mworks_gap_closeout_20260718/dfbc_family/codegen/MoSim_P10_DFBC_Family_CFunction_Sysblock"
    ;;
  dfbc_high_order_bodyrate|dfbc_smooth_robust_bodyrate)
    backend=p10_dfbc_family
    generated_dir="${PROJECT_ROOT}/Results/control_platform/p10_mworks_gap_closeout_20260718/dfbc_family/codegen/MoSim_P10_DFBC_Family_CFunction_Sysblock"
    bodyrate=true
    ;;
  *) echo "Unsupported P10 profile: ${PROFILE}" >&2; exit 2 ;;
esac

mkdir -p "${RESULT_DIR}"
MOSIM_PX4_WORK_DIR="${MOSIM_PX4_WORK_DIR:-${RESULT_DIR}/px4_work}"
mkdir -p "${MOSIM_PX4_WORK_DIR}"
export MOSIM_PX4_WORK_DIR
PX4_RCS_SOURCE="${PX4_RCS_SOURCE:-/opt/mosim_work/sunray_px4/build/px4_sitl_default/etc/init.d-posix/rcS}"
MOSIM_PX4_STARTUP_SCRIPT="${MOSIM_PX4_WORK_DIR}/mosim_rcS_ram_dataman"
python3 "${PROJECT_ROOT}/Scripts/sunray/prepare_px4_ram_dataman_rcs.py" \
  --source "${PX4_RCS_SOURCE}" --output "${MOSIM_PX4_STARTUP_SCRIPT}" \
  --manifest "${RESULT_DIR}/PX4_RAM_DATAMAN_RCS.json"
export MOSIM_PX4_STARTUP_SCRIPT

RESULT_DIR="${RESULT_DIR}/px4ctrl_build" \
  bash "${PROJECT_ROOT}/Scripts/sunray/ensure_px4ctrl_generated_backend.sh" "${backend}"

gate_rc=0
RUN_ID="p10_${PROFILE}_takeoff_hover_land_20260718" \
RESULT_DIR="${RESULT_DIR}" \
PX4CTRL_WS="${PX4CTRL_WS}" \
PX4CTRL_CORE_PROFILE="${PROFILE}" \
PX4CTRL_USE_BODYRATE_CTRL="${bodyrate}" \
SUNRAY_GAZEBO_LAUNCH_FILE="${PROJECT_ROOT}/Scripts/sunray/g9_single_uav_isolated_px4.launch" \
PX4CTRL_EXTRA_PARAM_OVERRIDES="CAL_GYRO0_XOFF=-0.001141657936386764,CAL_GYRO0_YOFF=-0.004853107035160065,CAL_GYRO0_ZOFF=-0.00022918041213415563,CAL_ACC0_XOFF=-0.19448795914649963,CAL_ACC0_YOFF=0.1512581706047058,CAL_ACC0_ZOFF=-0.0606503039598465" \
GUI=false REVIEW_OPEN_RVIZ=false REVIEW_START_FASTLIO=false PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=false \
MAVROS_READY_TIMEOUT_S="${P10_MAVROS_READY_TIMEOUT_S:-120}" \
TOTAL_TIMEOUT_S="${P10_TOTAL_TIMEOUT_S:-300}" \
bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" takeoff_hover_land || gate_rc=$?

provenance_rc=0
python3 "${PROJECT_ROOT}/Scripts/sunray/check_p10_generated_runtime_provenance.py" \
  --project-root "${PROJECT_ROOT}" --px4ctrl-workspace "${PX4CTRL_WS}" \
  --generated-code-dir "${generated_dir}" --controller-profile "${PROFILE}" \
  --runtime-log "${RESULT_DIR}/px4ctrl.log" \
  --json-out "${RESULT_DIR}/P10_GENERATED_RUNTIME_PROVENANCE.json" || provenance_rc=$?

if [[ "${gate_rc}" -ne 0 ]]; then exit "${gate_rc}"; fi
exit "${provenance_rc}"
