#!/usr/bin/env python3
"""Regression checks for the project-owned Sysplorer MCP wrapper location."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "mworks" / "run_sysplorer_mcp_smoke.py"
WRAPPER = (
    ROOT
    / "Docs"
    / "Skills"
    / "Mworks"
    / "mworks-mcp-operations"
    / "wrappers"
    / "sysplorer_mcp.cmd"
)


def load_module():
    spec = importlib.util.spec_from_file_location("run_sysplorer_mcp_smoke", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_project_windows_wrapper_is_mworks_skill_owned() -> None:
    module = load_module()
    assert WRAPPER.is_file()
    assert 'set "MOSIM_ROOT=%~dp0..\\..\\..\\..\\.."' in WRAPPER.read_text(encoding="utf-8")

    if module.os.name == "nt":
        candidates = {Path(candidate) for candidate in module.default_wrapper_candidates()}
        assert WRAPPER in candidates
        assert ROOT / "mcp-wrappers" / "sysplorer_mcp.cmd" not in candidates


def main() -> int:
    test_project_windows_wrapper_is_mworks_skill_owned()
    print("[OK] Sysplorer MCP wrapper location")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
