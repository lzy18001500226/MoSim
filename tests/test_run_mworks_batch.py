#!/usr/bin/env python3
"""Regression checks for batch scenario command planning."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import re
import importlib.util


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "run_mworks_batch.py"
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("run_mworks_batch", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load run_mworks_batch.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_mworks_batch_dry_run_regression() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/run_mworks_batch.py",
            "--dry-run",
            "--skip-existing",
            "scenarios/smoke/*.yaml",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = proc.stdout
    if "example1_pid_mcp_smoke.yaml" not in output:
        raise AssertionError(output)
    match = re.search(r"Skipped existing: (\d+)", output)
    if not match or int(match.group(1)) < 1:
        raise AssertionError(output)
    if "Failures: 0" not in output:
        raise AssertionError(output)


def test_run_mworks_batch_dry_run_quality_args() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/run_mworks_batch.py",
            "--dry-run",
            "scenarios/smoke/example1_pid_mcp_smoke.yaml",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = proc.stdout
    if "--min-rmse-improvement-pct 0.5" not in output:
        raise AssertionError(output)


def test_run_mworks_batch_dry_run_reuse_mcp_arg() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/run_mworks_batch.py",
            "--dry-run",
            "--reuse-mcp-process",
            "scenarios/smoke/example1_pid_mcp_smoke.yaml",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = proc.stdout
    if "scripts/run_mworks_scenario.py scenarios/smoke/example1_pid_mcp_smoke.yaml" not in output:
        raise AssertionError(output)
    if "Failures: 0" not in output:
        raise AssertionError(output)


def test_reuse_mcp_smoke_args_translation() -> None:
    module = load_module()
    scenario_path = ROOT / "scenarios" / "smoke" / "example1_pid_mcp_smoke.yaml"
    config = module.read_yaml(scenario_path)
    args = module.parse_args(["--reuse-mcp-process", str(scenario_path)])
    smoke_args = module.smoke_args_for_scenario(scenario_path, args, config)
    if smoke_args.model_name != "QuadrotorModel.Examples.Example1":
        raise AssertionError(smoke_args)
    if smoke_args.target_time != "0,1":
        raise AssertionError(smoke_args)
    if not str(smoke_args.raw_output).endswith("mworks_mcp_example1_pid_smoke.csv"):
        raise AssertionError(smoke_args)


def main() -> int:
    test_run_mworks_batch_dry_run_regression()
    test_run_mworks_batch_dry_run_quality_args()
    test_run_mworks_batch_dry_run_reuse_mcp_arg()
    test_reuse_mcp_smoke_args_translation()
    print("[OK] run_mworks_batch dry-run regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
