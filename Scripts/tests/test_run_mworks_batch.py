#!/usr/bin/env python3
"""Regression checks for batch scenario command planning."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import re
import importlib.util


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "mworks" / "run_mworks_batch.py"
    sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
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
            "Scripts/mworks/run_mworks_batch.py",
            "--dry-run",
            "--skip-existing",
            "Config/scenarios/official/example1_pid_baseline.yaml",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = proc.stdout
    if "example1_pid_baseline.yaml" not in output:
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
            "Scripts/mworks/run_mworks_batch.py",
            "--dry-run",
            "Config/scenarios/official/example1_pid_baseline.yaml",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = proc.stdout
    if "--min-rmse-improvement-pct 0.5" not in output:
        raise AssertionError(output)


def test_run_mworks_batch_dry_run_wrapper_arg() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "Scripts/mworks/run_mworks_batch.py",
            "--dry-run",
            "--wrapper",
            r"C:\Users\HP\mcp-wrappers\sysplorer_mcp.cmd",
            "Config/scenarios/official/example1_pid_baseline.yaml",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = proc.stdout
    if r"--wrapper C:\Users\HP\mcp-wrappers\sysplorer_mcp.cmd" not in output:
        raise AssertionError(output)


def test_run_mworks_batch_dry_run_no_gui_result_viewer_arg() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "Scripts/mworks/run_mworks_batch.py",
            "--dry-run",
            "--no-gui-result-viewer",
            "Config/scenarios/official/example1_pid_baseline.yaml",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = proc.stdout
    if "--no-gui-result-viewer" not in output:
        raise AssertionError(output)


def test_inactive_official_scenarios_are_skipped_by_default() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "Scripts/mworks/run_mworks_batch.py",
            "--dry-run",
            "Config/scenarios/official/example2_awff_pid.yaml",
            "Config/scenarios/official/example2_awff_pid_helix_tuned.yaml",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = proc.stdout
    if "Skipped inactive: 1" not in output:
        raise AssertionError(output)
    if "example2_awff_pid_helix_tuned.yaml" not in output:
        raise AssertionError(output)
    if "Scripts/mworks/run_mworks_scenario.py Config/scenarios/official/example2_awff_pid.yaml" in output:
        raise AssertionError(output)


def test_include_inactive_official_scenarios() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "Scripts/mworks/run_mworks_batch.py",
            "--dry-run",
            "--include-inactive",
            "Config/scenarios/official/example2_awff_pid.yaml",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = proc.stdout
    if "Skipped inactive: 0" not in output:
        raise AssertionError(output)
    if "Scripts/mworks/run_mworks_scenario.py Config/scenarios/official/example2_awff_pid.yaml" not in output:
        raise AssertionError(output)


def main() -> int:
    test_run_mworks_batch_dry_run_regression()
    test_run_mworks_batch_dry_run_quality_args()
    test_run_mworks_batch_dry_run_wrapper_arg()
    test_run_mworks_batch_dry_run_no_gui_result_viewer_arg()
    test_inactive_official_scenarios_are_skipped_by_default()
    test_include_inactive_official_scenarios()
    print("[OK] run_mworks_batch dry-run regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
