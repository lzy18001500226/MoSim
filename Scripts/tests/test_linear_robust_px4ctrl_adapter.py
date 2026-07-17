from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PX4CTRL = ROOT / "References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl"
BASIC_GATE = ROOT / "Scripts/sunray/run_px4ctrl_basic_gate.sh"


def test_cmake_declares_linear_robust_generated_backend() -> None:
    text = (PX4CTRL / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "linear_robust_attitude_thrust"' in text
    assert "MOSIM_PX4CTRL_GENERATED_BACKEND_LINEAR_ROBUST_ATTITUDE_THRUST" in text
    assert "p2_linear_robust_mworks_20260716/generated_c/MoSim_P2_LinearRobust_CFunction_Sysblock" in text


def test_adapter_maps_four_profiles_and_physical_contract() -> None:
    text = (PX4CTRL / "src/controller.cpp").read_text(encoding="utf-8")
    for profile in ("lqg", "feedback_linearization", "passivity_based_control", "adaptive_backstepping"):
        assert f'"{profile}"' in text
        assert profile in BASIC_GATE.read_text(encoding="utf-8")
    for token in (
        "mass_kg_in = param_.mass",
        "gravity_mps2_in = param_.gra",
        "hover_percentage_in = effective_hover_percentage",
        "max_tilt_rad_in",
        "min_collective_thrust_n_in = 0.0",
        "max_collective_thrust_n_in = full_collective_thrust_n",
    ):
        assert token in text


def test_adapter_fails_closed_on_invalid_generated_output() -> None:
    text = (PX4CTRL / "src/controller.cpp").read_text(encoding="utf-8")
    assert "ction_sysblockGbOut.status_code_out == 0.0" in text
    assert "Linear/robust ATTITUDE_THRUST generated backend returned invalid output" in text
    assert "u.thrust = 0.0" in text
