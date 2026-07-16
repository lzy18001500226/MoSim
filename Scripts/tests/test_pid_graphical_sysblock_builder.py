from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/build_pid_graphical_sysblock.py"


def script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_builder_uses_official_graphical_topology_apis() -> None:
    text = script_text()
    assert "ModelingPy.NewModel" in text
    assert "ModelingPy.OpenModel" in text
    assert "ModelingPy.AddComponent" in text
    assert "ModelingPy.ConnectPort" in text
    assert "ModelingPy.SetParamValue" in text
    assert "ModelingPy.SaveModelAs" in text
    assert "ModelingPy.ExportDiagram" in text
    assert "SysplorerEmbeddedCoder.Discrete.Difference" in text
    assert "SysplorerEmbeddedCoder.Discrete.UnitDelay" in text
    assert "SysplorerEmbeddedCoder.Continuous.Derivative" not in text
    assert "SysplorerEmbeddedCoder.Continuous.Integrator" not in text
    assert "SetModelText" not in text
    assert "ClearAll" not in text
    assert "ChangeDirectory" not in text


def test_builder_exposes_required_pid_family_behaviors() -> None:
    text = script_text()
    for behavior in (
        '"gain_schedule"',
        '"fuzzy_residual"',
        '"neural_residual"',
        '"integral_limit"',
        '"anti_windup"',
        '"feedforward"',
        '"cascade"',
        '"mode_enable"',
    ):
        assert behavior in text
    assert '"structure_ok": structure_ok' in text
    assert '"behavior_equivalence_ok": False' in text
