from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HEADER = (ROOT / "Scripts/control_platform/safety_supervisor_core.h").read_text(encoding="utf-8")
SOURCE = (ROOT / "Scripts/control_platform/safety_supervisor_core.c").read_text(encoding="utf-8")
RUNNER = (ROOT / "Scripts/control_platform/run_safety_supervisor_gate.py").read_text(encoding="utf-8")


def test_all_seven_safety_modes_are_declared() -> None:
    for token in (
        "MOSIM_SAFETY_FILTER", "MOSIM_SAFETY_CBF", "MOSIM_SAFETY_REFERENCE_GOVERNOR",
        "MOSIM_SAFETY_GEOFENCE", "MOSIM_SAFETY_EMERGENCY_STOP",
        "MOSIM_SAFETY_RETURN_AND_LAND", "MOSIM_SAFETY_FAILSAFE",
    ):
        assert token in HEADER
    for name in (
        "safety_filter", "cbf", "reference_governor", "geofence",
        "emergency_stop", "return_and_land", "failsafe_state_machine",
    ):
        assert f'"{name}"' in RUNNER


def test_supervisor_is_fixed_size_and_fail_closed() -> None:
    assert "malloc(" not in SOURCE
    assert "realloc(" not in SOURCE
    assert "output->status_code = -1" in SOURCE
    assert "MOSIM_SAFETY_ACTION_STOP" in SOURCE
    assert "CONSTRAINT_TIMEOUT" in SOURCE
