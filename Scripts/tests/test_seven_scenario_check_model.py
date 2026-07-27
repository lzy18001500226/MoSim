from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "mworks" / "check_seven_scenario_preflight.py"


def load_module():
    spec = importlib.util.spec_from_file_location("seven_scenario_check_model", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_check_only_inventory_covers_the_contract_surface() -> None:
    module = load_module()

    assert len(module.TRAJECTORY_MODELS) == 8
    assert len(module.SHARED_RUNNER_MODELS) == 4
    assert len(module.FORMAL_RUNNER_MODELS) == 8
    assert len(module.TARGETS) == 20
    assert module.TARGETS[0].endswith("ClimbPath")
    assert module.TARGETS[-1].endswith("Px4CtrlFormalRunner")
    assert module.ALLOWED_MCP_TOOLS == {"session_manager", "model_manager", "check_model"}


def test_check_only_script_has_no_solver_invocation() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "simulate_" not in source
    assert "result_manager" not in source
