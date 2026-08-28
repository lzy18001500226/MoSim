from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/mworks/check_official_pid_rt1_sysblock_shadow.py"
SPEC = importlib.util.spec_from_file_location("official_pid_rt1_sysblock_shadow", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_rt1_sysblock_shadow_uses_graphical_core_without_embedded_c_pid() -> None:
    summary = MODULE.run_checks()
    assert summary["status"] == "pass", summary["failures"]
    assert "Static source/wiring" in summary["claim_boundary"]
