#!/usr/bin/env python3
"""Regression checks for MWORKS generated controller runtime artifacts."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
CODE_DIR = ROOT / "Results" / "codegen_probe" / "AWFF_PID_Sysblock_Demo_api" / "AWFF_PID_Sysblock_Demo"
MODEL_NAME = "AWFF_PID_Sysblock_Demo"


def load_checker():
    path = ROOT / "Scripts" / "mworks" / "check_codegen_runtime.py"
    spec = importlib.util.spec_from_file_location("check_codegen_runtime", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_codegen_runtime.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checker(*extra: str) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "Scripts" / "mworks" / "check_codegen_runtime.py"),
            "--code-dir",
            str(CODE_DIR.relative_to(ROOT)),
            "--model-name",
            MODEL_NAME,
            *extra,
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def test_codegen_runtime_summary_contract() -> None:
    payload = run_checker("--expect-sample-time", "0.01")
    if payload["schema"] != "mosim.mworks_codegen_runtime_check.v1":
        raise AssertionError(payload)
    if not payload["ok"]:
        raise AssertionError(payload)
    if payload["runtime_adapter_shape"] != "global_struct_input_output_init_step":
        raise AssertionError(payload)
    if payload["sample_time_s"] != 0.01:
        raise AssertionError(payload)
    if payload["functions"] != ["Step", "Init"]:
        raise AssertionError(payload)
    input_fields = next(iter(payload["input_globals"].values()))["fields"]
    output_fields = next(iter(payload["output_globals"].values()))["fields"]
    if input_fields != ["z_error"]:
        raise AssertionError(payload)
    if output_fields != ["thrust_cmd"]:
        raise AssertionError(payload)
    if not payload["sil_gate_required"]:
        raise AssertionError(payload)


def test_codegen_runtime_compile_gate() -> None:
    payload = run_checker("--compile", "--run-smoke", "--expect-sample-time", "0.01")
    if not payload["ok"]:
        raise AssertionError(payload)
    compile_result = payload["compile"]
    if not compile_result["available"]:
        raise AssertionError(payload)
    if not compile_result["ok"]:
        raise AssertionError(payload)
    if compile_result["returncode"] != 0:
        raise AssertionError(payload)
    if not compile_result["object_dir_removed"]:
        raise AssertionError(payload)
    runtime_smoke = payload["runtime_smoke"]
    if not runtime_smoke["ok"]:
        raise AssertionError(payload)
    if not runtime_smoke["temp_dir_removed"]:
        raise AssertionError(payload)
    if [row["time_s"] for row in runtime_smoke["rows"]] != [0.01, 0.02, 0.03]:
        raise AssertionError(payload)


def test_codegen_runtime_project_path_guard() -> None:
    checker = load_checker()
    try:
        checker.project_path("/mnt/c/Users/HP/Desktop/not_mosim/code")
    except SystemExit:
        return
    raise AssertionError("project_path accepted a path outside MoSim")


def main() -> int:
    test_codegen_runtime_summary_contract()
    test_codegen_runtime_compile_gate()
    test_codegen_runtime_project_path_guard()
    print("[OK] MWORKS codegen runtime regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
