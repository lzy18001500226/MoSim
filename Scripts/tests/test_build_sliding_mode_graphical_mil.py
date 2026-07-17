from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEXT = (ROOT / "Scripts/control_platform/build_sliding_mode_graphical_mil.py").read_text(encoding="utf-8")


def test_graphical_gate_uses_native_state_and_nonlinear_blocks() -> None:
    assert '"SysplorerEmbeddedCoder.Discrete.UnitDelay"' in TEXT
    assert '"SysplorerEmbeddedCoder.MathOperation.MathFunction"' in TEXT
    assert '"SysplorerEmbeddedCoder.MathOperation.Abs"' in TEXT
    assert '"SysplorerEmbeddedCoder.Discontinuities.Saturation"' in TEXT
    assert "all_behavior_equivalent" in TEXT
    assert "len(expected) == len(actual) == 21" in TEXT
    assert "recover_completed_variant" in TEXT
    assert "p3_sliding_mode_graphical_mil.checkpoint.json" in TEXT
    for feature in ("integral_state_x", "terminal_shape_gain_x", "super_twisting_integral_x", "adaptive_reaching_gain_x", "fuzzy_membership_x"):
        assert feature in TEXT
