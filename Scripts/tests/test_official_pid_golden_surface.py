from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/mworks/check_official_pid_golden_surface.py"
SPEC = importlib.util.spec_from_file_location("official_pid_golden_surface", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_official_pid_golden_surface_contract() -> None:
    summary = MODULE.run_checks()
    assert summary["status"] == "pass", summary["failures"]
    assert summary["formal_runner_preserved"] is True
    assert summary["golden_connection_contract_ok"] is True
    assert summary["golden_interface_contract_ok"] is True
    assert summary["golden_interface_wiring_ok"] is True
    assert summary["mapper_topology_ok"] is True
    assert summary["physical_actuator_chain_ok"] is True
    assert summary["graphical_surface_ok"] is True
    assert summary["graphical_resources_ok"] is True
    assert summary["graphical_bitmap_aspect_ok"] is True
