#!/usr/bin/env bash
# Run one Wave A generated controller through the Sunray ROS1 Gazebo gate.

set -eo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
PROFILE="${1:-}"
MISSION="${2:-takeoff_hover_land}"
RESULT_DIR="${RESULT_DIR:-${PROJECT_ROOT}/Results/control_platform/wave_a_generated_gazebo_20260718/${PROFILE}/${MISSION}}"
GENERATED_CODE_DIR="${PROJECT_ROOT}/Results/control_platform/g5_mworks_closeout_20260716/wave_a/codegen/MoSim_WaveA_CFunction_Sysblock"
BUILD_MANIFEST="${PROJECT_ROOT}/Results/control_platform/g5_mworks_closeout_20260716/wave_a/models/BUILD_MANIFEST.json"
SIL_ROOT="${PROJECT_ROOT}/Results/control_platform/g5_mworks_closeout_20260716/wave_a/sil"

case "${PROFILE}" in
  lqr_baseline|lqi_baseline|so3_attitude|backstepping_baseline) ;;
  *) echo "Unsupported Wave A profile: ${PROFILE}" >&2; exit 2 ;;
esac
case "${MISSION}" in
  takeoff_hover_land|figure8) ;;
  *) echo "Unsupported Wave A mission: ${MISSION}" >&2; exit 2 ;;
esac

mkdir -p "${RESULT_DIR}"
MOSIM_PX4_WORK_DIR="${MOSIM_PX4_WORK_DIR:-${RESULT_DIR}/px4_work}"
mkdir -p "${MOSIM_PX4_WORK_DIR}"
export MOSIM_PX4_WORK_DIR
PX4_RCS_SOURCE="${PX4_RCS_SOURCE:-/opt/mosim_work/sunray_px4/build/px4_sitl_default/etc/init.d-posix/rcS}"
MOSIM_PX4_STARTUP_SCRIPT="${MOSIM_PX4_WORK_DIR}/mosim_rcS_ram_dataman"
python3 "${PROJECT_ROOT}/Scripts/sunray/prepare_px4_ram_dataman_rcs.py" \
  --source "${PX4_RCS_SOURCE}" \
  --output "${MOSIM_PX4_STARTUP_SCRIPT}" \
  --manifest "${RESULT_DIR}/PX4_RAM_DATAMAN_RCS.json"
export MOSIM_PX4_STARTUP_SCRIPT

RESULT_DIR="${RESULT_DIR}/px4ctrl_build" \
  bash "${PROJECT_ROOT}/Scripts/sunray/ensure_px4ctrl_generated_backend.sh" wave_a_attitude_thrust

bodyrate=false
if [[ "${PROFILE}" == "so3_attitude" ]]; then
  bodyrate=true
fi

gate_rc=0
RUN_ID="wave_a_${PROFILE}_${MISSION}_20260718" \
RESULT_DIR="${RESULT_DIR}" \
PX4CTRL_WS="${PX4CTRL_WS}" \
PX4CTRL_CORE_PROFILE="${PROFILE}" \
PX4CTRL_USE_BODYRATE_CTRL="${bodyrate}" \
SUNRAY_GAZEBO_LAUNCH_FILE="${PROJECT_ROOT}/Scripts/sunray/g9_single_uav_isolated_px4.launch" \
PX4CTRL_EXTRA_PARAM_OVERRIDES="CAL_GYRO0_XOFF=-0.001141657936386764,CAL_GYRO0_YOFF=-0.004853107035160065,CAL_GYRO0_ZOFF=-0.00022918041213415563,CAL_ACC0_XOFF=-0.19448795914649963,CAL_ACC0_YOFF=0.1512581706047058,CAL_ACC0_ZOFF=-0.0606503039598465" \
GUI=false \
REVIEW_OPEN_RVIZ=false \
REVIEW_START_FASTLIO=false \
PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=false \
MAVROS_READY_TIMEOUT_S="${WAVE_A_MAVROS_READY_TIMEOUT_S:-120}" \
TOTAL_TIMEOUT_S="${WAVE_A_TOTAL_TIMEOUT_S:-300}" \
bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" "${MISSION}" || gate_rc=$?

provenance_rc=0
python3 "${PROJECT_ROOT}/Scripts/sunray/check_wave_a_generated_runtime_provenance.py" \
  --px4ctrl-workspace "${PX4CTRL_WS}" \
  --generated-code-dir "${GENERATED_CODE_DIR}" \
  --build-manifest "${BUILD_MANIFEST}" \
  --sil-root "${SIL_ROOT}" \
  --px4-startup-manifest "${RESULT_DIR}/PX4_RAM_DATAMAN_RCS.json" \
  --controller-profile "${PROFILE}" \
  --runtime-log "${RESULT_DIR}/px4ctrl.log" \
  --require-runtime-ack \
  --json-out "${RESULT_DIR}/WAVE_A_GENERATED_RUNTIME_PROVENANCE.json" || provenance_rc=$?

if [[ "${gate_rc}" -ne 0 ]]; then
  exit "${gate_rc}"
fi
exit "${provenance_rc}"
