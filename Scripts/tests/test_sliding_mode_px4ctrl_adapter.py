from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CMAKE = (ROOT / "References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl/CMakeLists.txt").read_text(encoding="utf-8")
CONTROLLER = (ROOT / "References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl/src/controller.cpp").read_text(encoding="utf-8")
RUNNER = (ROOT / "Scripts/sunray/run_px4ctrl_basic_gate.sh").read_text(encoding="utf-8")
CHECKER = (ROOT / "Scripts/sunray/check_sliding_mode_generated_runtime_provenance.py").read_text(encoding="utf-8")


def test_sliding_backend_is_fail_closed_and_selectable() -> None:
    assert 'MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "sliding_mode_attitude_thrust"' in CMAKE
    assert "MOSIM_PX4CTRL_GENERATED_BACKEND_SLIDING_MODE_ATTITUDE_THRUST" in CONTROLLER
    assert "MoSim_P3_SlidingMode_CFunction_Sysblock::Step" in CONTROLLER
    assert "MOSIM_ATTITUDE_THRUST_GB_IN" in CONTROLLER
    assert "status_code_out == 0.0" in CONTROLLER
    for profile in ("integral_smc", "terminal_smc", "nonsingular_terminal_smc", "super_twisting_smc", "adaptive_smc", "fuzzy_smc"):
        assert profile in CONTROLLER
        assert profile in RUNNER
        assert profile in CHECKER
