from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PX4CTRL = ROOT / "References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl"
BASIC_GATE = ROOT / "Scripts/sunray/run_px4ctrl_basic_gate.sh"
CHECKER = ROOT / "Scripts/sunray/check_enhancement_generated_runtime_provenance.py"
PROFILES = (
    "l1_adaptive", "awff", "complete_adrc", "standardized_indi",
    "parameter_scheduling", "ilc",
)


def test_cmake_declares_enhancement_generated_backend() -> None:
    text = (PX4CTRL / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "enhancement_attitude_thrust"' in text
    assert "MOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST" in text
    assert "generated_c/MoSim_P5_Enhancement_CFunction_Sysblock" in text


def test_adapter_maps_all_profiles_and_fails_closed() -> None:
    controller = (PX4CTRL / "src/controller.cpp").read_text(encoding="utf-8")
    runner = BASIC_GATE.read_text(encoding="utf-8")
    checker = CHECKER.read_text(encoding="utf-8")
    for profile in PROFILES:
        assert f'"{profile}"' in controller
        assert profile in runner
        assert profile in checker
    for token in (
        "enhancement_measured_acceleration_",
        "raw_acceleration.cwiseMax(-8.0).cwiseMin(8.0)",
        "measured_acceleration_x_in = enhancement_measured_acceleration_(0)",
        "trajectory_phase_bin_in = 0.0",
        "repeat_complete_in = 0.0",
        "status_code_out == 1.0",
        "Enhancement ATTITUDE_THRUST generated backend returned invalid output",
        "u.thrust = 0.0",
    ):
        assert token in controller
