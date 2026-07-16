from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/build_pid_variant_graphical_mil.py"


def test_builder_uses_official_graphical_and_runtime_apis() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for token in (
        "ModelingPy.NewModel",
        "ModelingPy.AddComponent",
        "ModelingPy.ConnectPort",
        "ModelingPy.SetParamValue",
        "ModelingPy.CheckModel",
        "ModelingPy.ExportDiagram",
        "ModelingPy.SimulateModelEx",
        "ModelingPy.GetVarsValues",
    ):
        assert token in text
    assert "SetModelText" not in text
    assert "ClearAll" not in text
    assert "ChangeDirectory" not in text


def test_builder_exposes_exact_discrete_pid_behaviors() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for token in (
        "TrigonometricFunction.TrigonometricType.tanh",
        'n("previous_error")',
        'n("filter_state")',
        'n("integral_state")',
        'n("saturation_error")',
        '"cascade_pid"',
        '"gain_scheduled_pid"',
        '"fuzzy_pid"',
        '"neural_pid"',
        '"anti_windup"',
        '"feedforward_profile"',
    ):
        assert token in text
    assert "fixed-input graphical MIL" in text
