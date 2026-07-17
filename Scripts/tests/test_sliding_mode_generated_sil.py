from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (ROOT / "Scripts/control_platform/run_sliding_mode_generated_sil.py").read_text(encoding="utf-8")


def test_sil_gate_covers_all_six_controllers_and_public_outputs() -> None:
    assert "range(1, 7)" in SCRIPT
    assert '"controller_count"' in SCRIPT
    assert '"compared_columns_per_controller"' in SCRIPT
    assert '"MWORKS GenerateModelCode"' in SCRIPT
    assert '"sliding_surface_x"' in SCRIPT
    assert '"effective_reaching_gain_x"' in SCRIPT
    assert '"status_code"' in SCRIPT
