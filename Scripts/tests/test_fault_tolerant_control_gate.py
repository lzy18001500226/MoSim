from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HEADER = (ROOT / "Scripts/control_platform/fault_tolerant_control_core.h").read_text(encoding="utf-8")
SOURCE = (ROOT / "Scripts/control_platform/fault_tolerant_control_core.c").read_text(encoding="utf-8")
RUNNER = (ROOT / "Scripts/control_platform/run_fault_tolerant_control_gate.py").read_text(encoding="utf-8")


def test_all_p7_modes_are_declared() -> None:
    for token in (
        "MOSIM_FTC_FDI", "MOSIM_FTC_PASSIVE", "MOSIM_FTC_ACTIVE",
        "MOSIM_FTC_FAULT_AWARE_ALLOCATION", "MOSIM_FTC_SINGLE_MOTOR_SAFE_LANDING",
        "MOSIM_FTC_MULTI_FAULT_RECONFIGURATION",
    ):
        assert token in HEADER


def test_core_is_fixed_size_and_fail_closed() -> None:
    assert "malloc(" not in SOURCE
    assert "calloc(" not in SOURCE
    assert "finite4" in SOURCE
    assert "detection_persistence_s" in SOURCE
    assert "bounded_allocation" in SOURCE
    assert "Ubuntu-20.04" in RUNNER
