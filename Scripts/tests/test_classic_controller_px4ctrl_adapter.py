from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PX4CTRL = ROOT / "References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl"
BASIC_GATE = ROOT / "Scripts/sunray/run_px4ctrl_basic_gate.sh"


def test_cmake_declares_classic_generated_backend() -> None:
    text = (PX4CTRL / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "classic_controller_attitude_thrust"' in text
    assert "MOSIM_PX4CTRL_GENERATED_BACKEND_CLASSIC_CONTROLLER_ATTITUDE_THRUST" in text
    assert "classic_controller_closeout_20260717/mworks/codegen/MoSim_Classic_CFunction_Sysblock" in text


def test_adapter_maps_five_profiles_and_generated_ports() -> None:
    text = (PX4CTRL / "src/controller.cpp").read_text(encoding="utf-8")
    gate = BASIC_GATE.read_text(encoding="utf-8")
    for profile in ("pole_placement_luenberger", "mrac", "ndi", "fopid", "h2_state_feedback"):
        assert f'"{profile}"' in text
        assert profile in gate
    for token in (
        "#define MOSIM_ATTITUDE_THRUST_GB_IN blockGbIn",
        "MOSIM_ATTITUDE_THRUST_GB_IN.controller_id_in",
        "MOSIM_ATTITUDE_THRUST_GB_IN.reference_position_x_in",
        "MOSIM_ATTITUDE_THRUST_GB_IN.reference_acceleration_z_in",
        "MOSIM_ATTITUDE_THRUST_GB_OUT.normalized_thrust_out",
    ):
        assert token in text


def test_adapter_acknowledges_hash_and_fails_closed() -> None:
    text = (PX4CTRL / "src/controller.cpp").read_text(encoding="utf-8")
    assert "generated_source_sha256=0f44c05a4d36ed4a2040989ff48a47b9b1033f24ced152da1c5eb38428da7772" in text
    assert "Classic-controller ATTITUDE_THRUST generated backend returned invalid output" in text
    assert "u.thrust = 0.0" in text
