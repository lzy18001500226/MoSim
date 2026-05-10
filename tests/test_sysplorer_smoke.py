#!/usr/bin/env python3
"""Regression checks for Sysplorer MCP smoke-run helpers."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "run_sysplorer_mcp_smoke.py"
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("run_sysplorer_mcp_smoke", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load run_sysplorer_mcp_smoke.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_write_csv_rejects_empty_mcp_result(tmp_path: Path) -> None:
    module = load_module()
    output = tmp_path / "existing.csv"
    output.write_text("sentinel\n", encoding="utf-8")

    try:
        module.write_csv([[], []], {"time": "time", "z": "z"}, output)
    except ValueError as exc:
        if "empty" not in str(exc) and "zero rows" not in str(exc):
            raise AssertionError(f"Unexpected error message: {exc}") from exc
    else:
        raise AssertionError("Empty MCP result should fail")

    if output.read_text(encoding="utf-8") != "sentinel\n":
        raise AssertionError("Existing raw CSV was overwritten by an empty MCP result")


def main() -> int:
    temp_root = ROOT / ".tmp" / "sysplorer_smoke_test"
    temp_root.mkdir(parents=True, exist_ok=True)
    try:
        test_write_csv_rejects_empty_mcp_result(temp_root)
    finally:
        for item in sorted(temp_root.glob("*"), reverse=True):
            item.unlink()
        temp_root.rmdir()
        tmp_root = ROOT / ".tmp"
        if tmp_root.exists() and not any(tmp_root.iterdir()):
            tmp_root.rmdir()
    print("[OK] sysplorer smoke helpers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
