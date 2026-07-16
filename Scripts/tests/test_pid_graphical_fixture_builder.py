from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/build_pid_graphical_fixture.py"


def test_fixture_uses_official_graphical_and_result_apis() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for api in (
        "ModelingPy.NewModel",
        "ModelingPy.AddComponent",
        "ModelingPy.ConnectPort",
        "ModelingPy.CheckModel",
        "ModelingPy.SimulateModelEx",
        "ModelingPy.GetVarTimes",
        "ModelingPy.GetVarsValues",
    ):
        assert api in text
    assert "SetModelText" not in text
    assert "ClearAll" not in text
    assert "ChangeDirectory" not in text


def test_fixture_keeps_equivalence_claim_bounded() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "Six-variant CFunction equivalence remains a separate gate" in text
