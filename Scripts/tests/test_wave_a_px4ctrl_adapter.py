from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PX4CTRL = ROOT / "References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl"
BASIC_GATE = ROOT / "Scripts/sunray/run_px4ctrl_basic_gate.sh"
RUNNER = ROOT / "Scripts/sunray/run_wave_a_generated_gazebo_gate.sh"
PX4_LAUNCH = ROOT / "Scripts/sunray/g9_single_uav_isolated_px4.launch"


def test_cmake_declares_wave_a_generated_backend() -> None:
    text = (PX4CTRL / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "wave_a_attitude_thrust"' in text
    assert "MOSIM_PX4CTRL_GENERATED_BACKEND_WAVE_A_ATTITUDE_THRUST" in text
    assert "g5_mworks_closeout_20260716/wave_a/codegen/MoSim_WaveA_CFunction_Sysblock" in text


def test_adapter_maps_four_profiles_and_both_output_variants() -> None:
    text = (PX4CTRL / "src/controller.cpp").read_text(encoding="utf-8")
    gate = BASIC_GATE.read_text(encoding="utf-8")
    runner = RUNNER.read_text(encoding="utf-8")
    for profile in (
        "lqr_baseline",
        "lqi_baseline",
        "so3_attitude",
        "backstepping_baseline",
    ):
        assert f'"{profile}"' in text
        assert profile in gate
        assert profile in runner
    for token in (
        "#define MOSIM_ATTITUDE_THRUST_GB_IN ockGbIn",
        "MOSIM_ATTITUDE_THRUST_GB_IN.attitude_w_in",
        "MOSIM_ATTITUDE_THRUST_GB_IN.reference_attitude_w_in",
        "MOSIM_ATTITUDE_THRUST_GB_IN.collective_thrust_n_in",
        "MOSIM_ATTITUDE_THRUST_GB_OUT.desired_body_rate_x_out",
        "generated_family_controller_id_ == kWaveASo3",
    ):
        assert token in text


def test_adapter_acknowledges_hash_and_fails_closed() -> None:
    text = (PX4CTRL / "src/controller.cpp").read_text(encoding="utf-8")
    assert "generated_source_sha256=ec7dc5730b02bb4701c9f30ef78177b851a2ee8bc080575d8aedb5239fc492b7" in text
    assert "Wave A generated backend returned invalid output" in text
    assert "u.thrust = 0.0" in text


def test_runner_exports_run_local_px4_work_directory() -> None:
    runner = RUNNER.read_text(encoding="utf-8")
    assert 'MOSIM_PX4_WORK_DIR="${MOSIM_PX4_WORK_DIR:-${RESULT_DIR}/px4_work}"' in runner
    assert 'mkdir -p "${MOSIM_PX4_WORK_DIR}"' in runner
    assert "export MOSIM_PX4_WORK_DIR" in runner


def test_runner_uses_fail_closed_ram_dataman_startup_overlay() -> None:
    runner = RUNNER.read_text(encoding="utf-8")
    launch = PX4_LAUNCH.read_text(encoding="utf-8")
    assert "prepare_px4_ram_dataman_rcs.py" in runner
    assert "PX4_RAM_DATAMAN_RCS.json" in runner
    assert "export MOSIM_PX4_STARTUP_SCRIPT" in runner
    assert 'MAVROS_READY_TIMEOUT_S="${WAVE_A_MAVROS_READY_TIMEOUT_S:-120}"' in runner
    assert "$(optenv MOSIM_PX4_STARTUP_SCRIPT etc/init.d-posix/rcS)" in launch
