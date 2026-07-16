from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PX4CTRL = ROOT / "References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl"
BASIC_GATE = ROOT / "Scripts/sunray/run_px4ctrl_basic_gate.sh"


def test_cmake_declares_independent_pid_generated_backend() -> None:
    text = (PX4CTRL / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "pid_attitude_thrust"' in text
    assert "MOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST" in text
    assert "generated_c_v2/MoSim_PID_AttitudeThrust_CFunction_Sysblock" in text


def test_adapter_preserves_physical_parameter_contract() -> None:
    text = (PX4CTRL / "src/controller.cpp").read_text(encoding="utf-8")
    for token in (
        "mass_kg_in = param_.mass",
        "gravity_mps2_in = param_.gra",
        "max_tilt_rad_in",
        "min_collective_thrust_n_in = 0.0",
        "max_collective_thrust_n_in = full_collective_thrust_n",
        "desired_collective_thrust_n_out / full_collective_thrust_n",
    ):
        assert token in text
    assert "param_.mass * thr2acc_" in text


def test_adapter_maps_six_profiles_and_bounds_optional_inputs() -> None:
    text = (PX4CTRL / "src/controller.cpp").read_text(encoding="utf-8")
    for profile in (
        "cascade_pid",
        "gain_scheduled_pid",
        "fuzzy_pid",
        "neural_pid",
        "anti_windup",
        "feedforward_profile",
    ):
        assert f'"{profile}"' in text
    assert "clamp_double(std::abs(position_error(0)), 0.0, 1.0)" in text
    assert "clamp_double(position_error(0), -1.0, 1.0)" in text
    assert "neural_residual_x_in = 0.0" in text
    assert "neural_residual_source=zero_untrained" in text


def test_basic_runtime_gate_accepts_six_pid_profiles() -> None:
    text = BASIC_GATE.read_text(encoding="utf-8")
    for profile in (
        "cascade_pid",
        "gain_scheduled_pid",
        "fuzzy_pid",
        "neural_pid",
        "anti_windup",
        "feedforward_profile",
    ):
        assert profile in text


def test_adapter_fails_closed_on_generated_status_or_profile_mismatch() -> None:
    text = (PX4CTRL / "src/controller.cpp").read_text(encoding="utf-8")
    assert "status_code_out == 0.0" in text
    assert "algorithm_id_out_out" in text
    assert "PID ATTITUDE_THRUST generated backend returned invalid status or profile id" in text
    assert "u.thrust = 0.0" in text
