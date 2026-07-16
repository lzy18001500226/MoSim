from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/collect_pid_mworks_evidence.py"


def script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_collector_uses_live_mworks_result_api_for_all_fixtures() -> None:
    text = script_text()
    tree = ast.parse(text)
    assert tree is not None
    assert "ModelingPy.CheckModel(model_name)" in text
    assert "ModelingPy.SimulateModel(model_name)" in text
    assert "ModelingPy.GetVarTimes()" in text
    assert "ModelingPy.GetVarsValues(VAR_NAMES)" in text
    assert '"source": "MWORKS_MCP"' in text
    assert 'lengths != {21}' in text


def test_collector_keeps_claim_boundary_and_session_safety() -> None:
    text = script_text()
    assert "graphical equivalence" in text
    assert "Gazebo/PX4/MAVROS" in text
    assert "will_not_click_activation_login" in text
    assert "ClearAll" not in text
    assert "ChangeDirectory" not in text
