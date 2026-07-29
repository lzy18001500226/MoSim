from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
G9_RUNNER = ROOT / "Scripts/sunray/run_g9_controller_final_acceptance.sh"
BASIC_GATE = ROOT / "Scripts/sunray/run_px4ctrl_basic_gate.sh"
ORCHESTRATED_RUNTIME = ROOT / "Scripts/ui/run_orchestrated_runtime.sh"


def test_px4_work_directory_is_per_run_and_exported_before_roslaunch() -> None:
    source = G9_RUNNER.read_text(encoding="utf-8")

    default = 'MOSIM_PX4_WORK_DIR="${MOSIM_PX4_WORK_DIR:-${RESULT_DIR}/px4_work}"'
    create = 'mkdir -p "${RESULT_DIR}" "${MOSIM_PX4_WORK_DIR}"'
    export = "export MOSIM_PX4_WORK_DIR"
    gate = 'bash "${PROJECT_ROOT}/Scripts/sunray/run_px4ctrl_basic_gate.sh"'

    assert default in source
    assert source.index(create) < source.index(export) < source.index(gate)


def test_g9_final_runner_freezes_backend_and_calibration_contract() -> None:
    source = G9_RUNNER.read_text(encoding="utf-8")

    assert "g9_single_uav_isolated_px4.launch" in source
    assert "check_g9_generated_runtime_provenance.py" in source
    assert "--require-runtime-ack" in source
    assert source.count("CAL_GYRO0_") == 3
    assert source.count("CAL_ACC0_") == 3
    assert "takeoff_hover_land|figure8" in source


def test_basic_gate_cleanup_is_bounded_before_force_kill() -> None:
    source = BASIC_GATE.read_text(encoding="utf-8")
    cleanup = source[source.index("cleanup() {"):source.index("trap cleanup EXIT")]

    first_term = cleanup.index('kill "${pid}"')
    deadline = cleanup.index("cleanup_deadline=$((SECONDS + 5))")
    force_kill = cleanup.index('kill -9 "${pid}"')
    reap = cleanup.index('wait "${pid}"')

    assert first_term < deadline < force_kill < reap
    assert cleanup.count('wait "${pid}"') == 1


def test_basic_gate_waits_for_estimator_attitude_to_settle_before_takeoff() -> None:
    source = BASIC_GATE.read_text(encoding="utf-8")

    assert source.count("--pre-takeoff-state-timeout-s 60") == 2
    assert source.count("--pre-takeoff-max-abs-roll-pitch-deg 0.5") == 2


def test_qgc_ground_standby_runs_until_managed_stop() -> None:
    runner = ORCHESTRATED_RUNTIME.read_text(encoding="utf-8")
    gate = BASIC_GATE.read_text(encoding="utf-8")

    assert 'QGC_GROUND_STANDBY_HOLD_S:-until_stopped' in runner
    assert 'NO_FLIGHT_DIAGNOSTIC_HOLD_S}" == "until_stopped' in gate
    assert "Ground standby remains active until the managed stop command" in gate


def test_fastlio_ekf_fusion_requires_a_boot_time_contract() -> None:
    gate = BASIC_GATE.read_text(encoding="utf-8")

    contract = (
        "PX4CTRL_FASTLIO_BOOT_PARAM_CONTRACT=\"EKF2_GPS_CTRL=0,"
        "EKF2_BARO_CTRL=0,EKF2_RNG_CTRL=0,EKF2_OF_CTRL=0,"
        "EKF2_EV_CTRL=15,EKF2_HGT_REF=3,EKF2_EV_DELAY=0,"
        "EKF2_EV_NOISE_MD=1,EKF2_EVP_NOISE=0.03,EKF2_EVA_NOISE=0.03\""
    )
    fusion_enable = gate.index('if [[ "${PX4CTRL_ENABLE_FASTLIO_EKF_FUSION}" == "true" ]]; then')
    resolve = gate.index("resolve_fastlio_px4_boot_contract", fusion_enable)
    overlay = gate.index("prepare_px4_ros1_runtime_overlay")

    assert contract in gate
    assert fusion_enable < resolve < overlay
    assert 'FASTLIO_ALIGNMENT_Z_SOURCE="fastlio"' in gate
    assert "Gazebo truth is evaluation-only." in gate
    assert "PX4CTRL_FASTLIO_BOOT_PARAM_CONTRACT_APPLIED" in gate
    assert "PX4CTRL_SUNRAY150_IMU_CALIBRATION_ENABLED" in gate
    assert "PX4CTRL_SUNRAY150_IMU_CALIBRATION_OVERRIDES" in gate
    assert "Sunray150 IMU calibration requires" in gate
    assert '"sunray150_imu_calibration_applied"' in gate


def test_sunray150_imu_calibration_applies_before_any_fastlio_branch() -> None:
    gate = BASIC_GATE.read_text(encoding="utf-8")

    calibration_call = gate.index("resolve_sunray150_imu_calibration_boot_contract\n\nif")
    fusion_enable = gate.index('if [[ "${PX4CTRL_ENABLE_FASTLIO_EKF_FUSION}" == "true" ]]; then')

    assert calibration_call < fusion_enable
    assert "CAL_GYRO0_PRIO=50" in gate
    assert "CAL_ACC0_PRIO=50" in gate
    assert "PX4CTRL_SUNRAY150_IMU_CALIBRATION_APPLIED=true" in gate


def test_basic_gate_enables_verified_mavlink_message_intervals_by_default() -> None:
    gate = BASIC_GATE.read_text(encoding="utf-8")

    assert 'MAVROS_SET_MESSAGE_INTERVALS="${MAVROS_SET_MESSAGE_INTERVALS:-true}"' in gate
    assert "command: 511" in gate
    assert "32:LOCAL_POSITION_NED" in gate
