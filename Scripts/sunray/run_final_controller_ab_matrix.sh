#!/usr/bin/env bash
# Run official PID versus gain-scheduled PID under one seven-scenario contract.

set -uo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_ROOT="${RESULT_ROOT:-${PROJECT_ROOT}/Results/control_platform/final_controller_ab_20260718}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
PROFILES_TEXT="${FINAL_AB_PROFILES:-official_pid gain_scheduled_pid}"
SCENARIOS_TEXT="${FINAL_AB_SCENARIOS:-hover step figure8 spiral wind parameter_mismatch motor_efficiency_fault}"
G9_GENERATED_DIR="${PROJECT_ROOT}/Results/g9/controller_family_attitude_thrust_v1/g9_family_mworks_codegen_20260630_work/g9_family_cfunction_codegen_strict/G9_Family_CFunction_Sysblock"
G9_CODEGEN_MANIFEST="${PROJECT_ROOT}/Results/g9/controller_family_attitude_thrust_v1/g9_family_mworks_codegen_20260630_work/generate_model_code_result.json"
PID_GENERATED_DIR="${PROJECT_ROOT}/Results/control_platform/p1_pid_attitude_thrust_mworks_20260716/generated_c_v2/MoSim_PID_AttitudeThrust_CFunction_Sysblock"
PID_CODEGEN_MANIFEST="${PROJECT_ROOT}/Results/control_platform/p1_pid_attitude_thrust_mworks_20260716/generate_model_code_result_v2.json"
PID_RUNTIME_CHECK="${PROJECT_ROOT}/Results/control_platform/p1_pid_attitude_thrust_mworks_20260716/sil/codegen_runtime_check_v2.json"
PLUGIN_WS="${FTC_PLUGIN_WS:-${PROJECT_ROOT}/Results/control_platform/p7_ftc_gazebo_plugin_ws_v2}"

mkdir -p "${RESULT_ROOT}"
: > "${RESULT_ROOT}/matrix_status.tsv"

source "${PROJECT_ROOT}/Scripts/sunray/sunray_ros1_runtime_lock.sh"
RUN_ID="final_controller_ab_preflight_20260718"
sunray_ros1_runtime_lock_acquire || exit $?
sunray_ros1_runtime_lock_release

set +u
source /opt/ros/noetic/setup.bash
[[ -f "${PX4CTRL_WS}/devel/setup.bash" ]] && source "${PX4CTRL_WS}/devel/setup.bash"
set -u

if [[ " ${SCENARIOS_TEXT} " == *" motor_efficiency_fault "* ]]; then
  FTC_PLUGIN_WS="${PLUGIN_WS}" \
    bash "${PROJECT_ROOT}/Scripts/sunray/build_p7_ftc_actuator_plugin.sh" \
    > "${RESULT_ROOT}/ftc_plugin_build.log" 2>&1 || exit $?
fi

current_backend=""
for profile in ${PROFILES_TEXT}; do
  case "${profile}" in
    official_pid) backend="g9_family" ;;
    gain_scheduled_pid) backend="pid_attitude_thrust" ;;
    *) echo "Unsupported final A/B profile: ${profile}" >&2; exit 2 ;;
  esac
  if [[ "${backend}" != "${current_backend}" ]]; then
    RESULT_DIR="${RESULT_ROOT}/backend_${backend}" \
      bash "${PROJECT_ROOT}/Scripts/sunray/ensure_px4ctrl_generated_backend.sh" "${backend}" || exit $?
    current_backend="${backend}"
  fi

  for scenario in ${SCENARIOS_TEXT}; do
    case "${scenario}" in
      hover|wind|parameter_mismatch|motor_efficiency_fault) mission="takeoff_hover_land" ;;
      step) mission="step_x" ;;
      figure8) mission="figure8" ;;
      spiral) mission="spiral" ;;
      *) echo "Unsupported final A/B scenario: ${scenario}" >&2; exit 2 ;;
    esac
    result_dir="${RESULT_ROOT}/${profile}_${scenario}"
    mkdir -p "${result_dir}"
    px4_work_dir="${result_dir}/px4_work"
    mkdir -p "${px4_work_dir}"
    px4_startup_script="${px4_work_dir}/mosim_rcS_ram_dataman"
    python3 "${PROJECT_ROOT}/Scripts/sunray/prepare_px4_ram_dataman_rcs.py" \
      --source "/opt/mosim_work/sunray_px4/build/px4_sitl_default/etc/init.d-posix/rcS" \
      --output "${px4_startup_script}" \
      --manifest "${result_dir}/PX4_RAM_DATAMAN_RCS.json" || exit $?
    gate_rc=0
    injector_rc=0
    provenance_rc=0
    mass_kg="1.0"
    [[ "${scenario}" == "parameter_mismatch" ]] && mass_kg="1.20"

    common_env=(
      RUN_ID="final_ab_${profile}_${scenario}_20260718"
      RESULT_DIR="${result_dir}"
      MOSIM_PX4_WORK_DIR="${px4_work_dir}"
      MOSIM_PX4_STARTUP_SCRIPT="${px4_startup_script}"
      PX4CTRL_CORE_PROFILE="${profile}"
      PX4CTRL_MASS="${mass_kg}"
      PX4CTRL_TAKEOFF_HOVER_DEFAULT_ARGS="--initial-hover-s 20 --steady-hover-tail-s 8 --land-wait-s 25 --force-disarm-after-land --force-disarm-timeout-s 18 --command-x-bias-m -0.006 --command-y-bias-m -0.004 --command-z-bias-m 0.0 --pre-takeoff-state-stable-s 3.0 --pre-takeoff-state-timeout-s 120 --pre-takeoff-max-abs-roll-pitch-deg 0.5"
      PX4CTRL_TRAJECTORY_DEFAULT_ARGS="--force-disarm-after-land --force-disarm-timeout-s 18 --pre-takeoff-state-stable-s 3.0 --pre-takeoff-state-timeout-s 120 --pre-takeoff-max-abs-roll-pitch-deg 0.5"
      PX4CTRL_EXTRA_PARAM_OVERRIDES="CAL_GYRO0_XOFF=-0.001141657936386764,CAL_GYRO0_YOFF=-0.004853107035160065,CAL_GYRO0_ZOFF=-0.00022918041213415563,CAL_ACC0_XOFF=-0.19448795914649963,CAL_ACC0_YOFF=0.1512581706047058,CAL_ACC0_ZOFF=-0.0606503039598465"
      SUNRAY_GAZEBO_LAUNCH_FILE="${PROJECT_ROOT}/Scripts/sunray/g9_single_uav_isolated_px4.launch"
      GUI=false
      REVIEW_OPEN_RVIZ=false
      REVIEW_START_FASTLIO=false
      PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=false
      MAVROS_READY_TIMEOUT_S="${FINAL_AB_MAVROS_READY_TIMEOUT_S:-120}"
      TOTAL_TIMEOUT_S="${FINAL_AB_TOTAL_TIMEOUT_S:-420}"
      CONTROL_DIAGNOSTICS_DURATION_S="${FINAL_AB_DIAGNOSTICS_DURATION_S:-90}"
      TIME_TF_AUDIT_DURATION_S="${FINAL_AB_DIAGNOSTICS_DURATION_S:-90}"
      FREQUENCY_AUDIT_DURATION_S="${FINAL_AB_FREQUENCY_DURATION_S:-20}"
    )

    if [[ "${scenario}" == "wind" ]]; then
      env "${common_env[@]}" \
        bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" "${mission}" &
      gate_pid="$!"
      python3 "${PROJECT_ROOT}/Scripts/sunray/apply_p9_learning_wind_wrench.py" \
        --result-dir "${result_dir}" --force-n "${FINAL_AB_WIND_FORCE_N:-0.9}" \
        --direction-deg "${FINAL_AB_WIND_DIRECTION_DEG:-35}" \
        --duration-s "${FINAL_AB_WIND_DURATION_S:-20}" \
        --airborne-timeout-s "${FINAL_AB_INJECTOR_AIRBORNE_TIMEOUT_S:-420}" || injector_rc=$?
      wait "${gate_pid}" || gate_rc=$?
    elif [[ "${scenario}" == "motor_efficiency_fault" ]]; then
      env "${common_env[@]}" \
        FTC_PLUGIN_WS="${PLUGIN_WS}" \
        MOSIM_ENABLE_FTC_ACTUATOR_PLUGIN=true \
        GAZEBO_PLUGIN_PATH="${PLUGIN_WS}/devel/lib:${GAZEBO_PLUGIN_PATH:-}" \
        LD_LIBRARY_PATH="${PLUGIN_WS}/devel/lib:${LD_LIBRARY_PATH:-}" \
        bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" "${mission}" &
      gate_pid="$!"
      python3 "${PROJECT_ROOT}/Scripts/sunray/apply_motor_efficiency_fault.py" \
        --result-dir "${result_dir}" --rotor-index 1 \
        --effectiveness "${FINAL_AB_MOTOR_EFFECTIVENESS:-0.65}" \
        --duration-s "${FINAL_AB_MOTOR_FAULT_DURATION_S:-20}" \
          --airborne-timeout-s "${FINAL_AB_INJECTOR_AIRBORNE_TIMEOUT_S:-420}" || injector_rc=$?
      wait "${gate_pid}" || gate_rc=$?
    else
      env "${common_env[@]}" \
        bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" "${mission}" || gate_rc=$?
    fi

    if [[ "${profile}" == "official_pid" ]]; then
      python3 "${PROJECT_ROOT}/Scripts/sunray/check_g9_generated_runtime_provenance.py" \
        --project-root "${PROJECT_ROOT}" --px4ctrl-workspace "${PX4CTRL_WS}" \
        --generated-code-dir "${G9_GENERATED_DIR}" --codegen-manifest "${G9_CODEGEN_MANIFEST}" \
        --controller-profile "${profile}" --runtime-log "${result_dir}/px4ctrl.log" \
        --require-runtime-ack --json-out "${result_dir}/G9_GENERATED_RUNTIME_PROVENANCE.json" \
        || provenance_rc=$?
    else
      python3 "${PROJECT_ROOT}/Scripts/sunray/check_pid_attitude_thrust_generated_runtime_provenance.py" \
        --px4ctrl-workspace "${PX4CTRL_WS}" --generated-code-dir "${PID_GENERATED_DIR}" \
        --codegen-manifest "${PID_CODEGEN_MANIFEST}" --runtime-check "${PID_RUNTIME_CHECK}" \
        --controller-profile "${profile}" --runtime-log "${result_dir}/px4ctrl.log" \
        --require-runtime-ack --json-out "${result_dir}/PID_GENERATED_RUNTIME_PROVENANCE.json" \
        || provenance_rc=$?
    fi
    printf '%s\t%s\t%s\t%s\t%s\n' \
      "${profile}" "${scenario}" "${gate_rc}" "${injector_rc}" "${provenance_rc}" \
      >> "${RESULT_ROOT}/matrix_status.tsv"
    sleep 2
  done
done

python3 "${PROJECT_ROOT}/Scripts/sunray/summarize_final_controller_ab_matrix.py" \
  --result-root "${RESULT_ROOT}" \
  --json-out "${RESULT_ROOT}/FINAL_CONTROLLER_SEVEN_SCENARIO_AB.json" \
  --csv-out "${RESULT_ROOT}/FINAL_CONTROLLER_SEVEN_SCENARIO_AB.csv"
