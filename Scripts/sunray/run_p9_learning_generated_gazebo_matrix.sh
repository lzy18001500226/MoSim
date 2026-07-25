#!/usr/bin/env bash
# Run the P9 baseline/neural/RL A/B matrix after the shared runtime is free.

set -uo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
RESULT_ROOT="${RESULT_ROOT:-${PROJECT_ROOT}/Results/control_platform/p9_learning_gazebo_20260717}"
PX4CTRL_WS="${PX4CTRL_WS:-${PROJECT_ROOT}/Results/sunray_ros1/px4ctrl_source_audit_20260621_172313/catkin_ws}"
GENERATED_DIR="${PROJECT_ROOT}/Results/control_platform/p9_learning_mworks_20260717/generated_c/MoSim_P9_Learning_AttitudeThrust_CFunction_Sysblock"
BUILD_MANIFEST="${PROJECT_ROOT}/Results/control_platform/p9_learning_mworks_20260717/BUILD_MANIFEST.json"
SIL_REPORT="${PROJECT_ROOT}/Results/control_platform/p9_learning_mworks_20260717/sil/P9_GENERATED_SIL_EQUIVALENCE.json"
PROFILES_TEXT="${P9_LEARNING_PROFILES:-cascade_pid trained_neural_residual rl_gain_scheduler}"
CONDITIONS_TEXT="${P9_LEARNING_CONDITIONS:-nominal wind parameter_mismatch}"

mkdir -p "${RESULT_ROOT}"
: > "${RESULT_ROOT}/matrix_status.tsv"

# Fail before any backend rebuild when another run owns the shared workspace.
source "${PROJECT_ROOT}/Scripts/sunray/sunray_ros1_runtime_lock.sh"
RUN_ID="p9_learning_matrix_preflight_20260717"
sunray_ros1_runtime_lock_acquire || exit $?
sunray_ros1_runtime_lock_release

set +u
source /opt/ros/noetic/setup.bash
[[ -f "${PX4CTRL_WS}/devel/setup.bash" ]] && source "${PX4CTRL_WS}/devel/setup.bash"
set -u

current_backend=""
for profile in ${PROFILES_TEXT}; do
  backend="learning_attitude_thrust"
  [[ "${profile}" == "cascade_pid" ]] && backend="pid_attitude_thrust"
  if [[ "${backend}" != "${current_backend}" ]]; then
    bash "${PROJECT_ROOT}/Scripts/sunray/ensure_p9_learning_px4ctrl_backend.sh" || exit $?
    current_backend="${backend}"
  fi

  for condition in ${CONDITIONS_TEXT}; do
    result_dir="${RESULT_ROOT}/${profile}_${condition}"
    mkdir -p "${result_dir}"
    gate_rc=0
    injector_rc=0
    checker_rc=0
    mass_kg="1.0"
    [[ "${condition}" == "parameter_mismatch" ]] && mass_kg="1.20"

    RUN_ID="p9_${profile}_${condition}_20260717" \
    RESULT_DIR="${result_dir}" \
    PX4CTRL_CORE_PROFILE="${profile}" \
    PX4CTRL_MASS="${mass_kg}" \
    TOTAL_TIMEOUT_S="${P9_TOTAL_TIMEOUT_S:-150}" \
    CONTROL_DIAGNOSTICS_DURATION_S="${P9_DIAGNOSTICS_DURATION_S:-60}" \
    TIME_TF_AUDIT_DURATION_S="${P9_DIAGNOSTICS_DURATION_S:-60}" \
    FREQUENCY_AUDIT_DURATION_S="${P9_FREQUENCY_DURATION_S:-20}" \
    GOAL3_FUSION_AUDIT_DURATION_S="${P9_DIAGNOSTICS_DURATION_S:-60}" \
    bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh" takeoff_hover_land &
    gate_pid="$!"

    if [[ "${condition}" == "wind" ]]; then
      python3 "${PROJECT_ROOT}/Scripts/sunray/apply_p9_learning_wind_wrench.py" \
        --result-dir "${result_dir}" \
        --force-n "${P9_WIND_FORCE_N:-0.9}" \
        --direction-deg "${P9_WIND_DIRECTION_DEG:-35}" \
        --duration-s "${P9_WIND_DURATION_S:-20}" || injector_rc=$?
    fi

    wait "${gate_pid}" || gate_rc=$?
    if [[ "${profile}" != "cascade_pid" ]]; then
      python3 "${PROJECT_ROOT}/Scripts/sunray/check_learning_generated_runtime_provenance.py" \
        --px4ctrl-workspace "${PX4CTRL_WS}" \
        --generated-code-dir "${GENERATED_DIR}" \
        --build-manifest "${BUILD_MANIFEST}" \
        --sil-report "${SIL_REPORT}" \
        --controller-profile "${profile}" \
        --runtime-log "${result_dir}/px4ctrl.log" \
        --require-runtime-ack \
        --json-out "${result_dir}/LEARNING_GENERATED_RUNTIME_PROVENANCE.json" || checker_rc=$?
    fi
    printf '%s\t%s\t%s\t%s\t%s\n' \
      "${profile}" "${condition}" "${gate_rc}" "${injector_rc}" "${checker_rc}" \
      >> "${RESULT_ROOT}/matrix_status.tsv"
    sleep 2
  done
done

python3 "${PROJECT_ROOT}/Scripts/sunray/summarize_p9_learning_gazebo_matrix.py" \
  --result-root "${RESULT_ROOT}" \
  --json-out "${RESULT_ROOT}/P9_LEARNING_GAZEBO_AB_MATRIX.json" \
  --csv-out "${RESULT_ROOT}/P9_LEARNING_GAZEBO_AB_MATRIX.csv"
