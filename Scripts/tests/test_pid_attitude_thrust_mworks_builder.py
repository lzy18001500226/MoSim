from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/build_pid_attitude_thrust_mworks_models.py"
SPEC = importlib.util.spec_from_file_location("pid_attitude_thrust_mworks_builder", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_builder_declares_complete_typed_contract() -> None:
    assert len(MODULE.VARIANTS) == 6
    for name in (
        "position_x", "velocity_x", "attitude_w", "angular_velocity_x",
        "reference_position_x", "reference_velocity_x", "reference_acceleration_x",
        "reference_yaw", "mass_kg", "gravity_mps2", "max_tilt_rad",
        "min_collective_thrust_n", "max_collective_thrust_n",
        "schedule_x", "fuzzy_error_x", "neural_residual_x",
        "enable", "reset",
    ):
        assert name in MODULE.INPUTS
    for name in (
        "desired_attitude_w", "desired_collective_thrust_n", "desired_acceleration_x",
        "position_error_x", "velocity_error_x", "scheduled_gain_x", "status_code",
    ):
        assert name in MODULE.OUTPUTS
    assert "normalized_thrust" not in MODULE.OUTPUTS


def test_embedded_bridge_uses_project_core_without_backend_dependencies() -> None:
    text = MODULE.embedded_c()
    assert "MosimPidAttitudeThrustStepScalar" in text
    assert "mosim_pid_attitude_thrust_step" in text
    assert "static MosimPidAttitudeThrustState states[7]" in text
    assert "attitude_clamp_value" in text
    assert "params.mass_kg = mass_kg" in text
    assert "params.gravity_mps2 = gravity_mps2" in text
    assert "params.max_tilt_rad = max_tilt_rad" in text
    assert "params.min_collective_thrust_n = min_collective_thrust_n" in text
    assert "params.max_collective_thrust_n = max_collective_thrust_n" in text
    for forbidden in ('#include "pid_unified_core.h"', '#include "pid_attitude_thrust_core.h"', "mavros", "ros::", "uORB"):
        assert forbidden not in text


def test_builder_normalizes_generated_model_text() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'line.rstrip() for line in bridge.splitlines()' in source
    assert 'codegen_dir = result_dir / "generated_c_v2"' in source
