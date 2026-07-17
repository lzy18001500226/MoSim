from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (ROOT / "Scripts/control_platform/run_mpc_generated_sil.py").read_text(encoding="utf-8")


def test_sil_gate_covers_all_seven_controllers_and_public_outputs() -> None:
    assert "range(1, 8)" in SCRIPT
    assert '"steps_per_controller": 3' in SCRIPT
    assert '"MWORKS GenerateModelCode"' in SCRIPT
    assert '"solver_iterations"' in SCRIPT
    assert '"status_code"' in SCRIPT
