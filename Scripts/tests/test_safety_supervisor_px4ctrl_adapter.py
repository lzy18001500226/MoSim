from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PX4CTRL = ROOT / "References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl"
BASIC_GATE = ROOT / "Scripts/sunray/run_px4ctrl_basic_gate.sh"
CHECKER = ROOT / "Scripts/sunray/check_safety_generated_runtime_provenance.py"
MODES = (
    "safety_filter", "cbf", "reference_governor", "geofence",
    "emergency_stop", "return_and_land", "failsafe_state_machine",
)


def test_cmake_declares_safety_supervisor_backend() -> None:
    text = (PX4CTRL / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'MOSIM_PX4CTRL_GENERATED_BACKEND STREQUAL "safety_supervisor"' in text
    assert "MOSIM_PX4CTRL_GENERATED_BACKEND_SAFETY_SUPERVISOR" in text
    assert "generated_c/MoSim_P6_SafetySupervisor_CFunction_Sysblock" in text


def test_adapter_maps_modes_and_applies_fail_closed_action() -> None:
    controller = (PX4CTRL / "src/controller.cpp").read_text(encoding="utf-8")
    runner = BASIC_GATE.read_text(encoding="utf-8")
    checker = CHECKER.read_text(encoding="utf-8")
    for mode in MODES:
        assert f'"{mode}"' in controller
        assert mode in runner
        assert mode in checker
    for token in (
        "MOSIM_SAFETY_GB_IN.mode_id_in",
        "MOSIM_SAFETY_GB_OUT.status_code_out == 1.0",
        "MOSIM_SAFETY_GB_OUT.action_out) == 5",
        "u.thrust = 0.0",
        "[px4ctrl] safety_event",
        "mosim_safety_test_event",
        "[mosim_generated_runtime] backend=mworks_generated_c",
    ):
        assert token in controller
