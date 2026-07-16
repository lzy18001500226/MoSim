from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/summarize_pid_p1_evidence.py"


def test_summary_preserves_unaccepted_claim_boundaries() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert '"selectable": False' in text
    assert '"six_variant_graphical_equivalence": False' in text
    assert '"full_attitude_thrust_contract": False' in text
    assert '"gazebo_px4_mavros_closed_loop": False' in text


def test_summary_indexes_required_evidence() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for name in (
        "mcp_evidence.json",
        "pid_graphical_build_manifest.json",
        "pid_codegen_manifest.json",
        "pid_codegen_runtime_check.json",
        "pid_graphical_codegen_equivalence.json",
        "screenshot_manifest.json",
    ):
        assert name in text
