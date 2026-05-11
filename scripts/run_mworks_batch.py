#!/usr/bin/env python3
"""Run multiple scenario YAML files through the MWORKS scenario runner."""

from __future__ import annotations

import argparse
import glob
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from run_mworks_scenario import ROOT, default_result_base, read_yaml
except ImportError:  # pragma: no cover
    ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ROOT / "scripts"))
    from run_mworks_scenario import default_result_base, read_yaml  # type: ignore


def expand_patterns(patterns: list[str]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern, recursive=True))
        if matches:
            paths.extend(Path(item) for item in matches)
        else:
            path = Path(pattern)
            if path.exists():
                paths.append(path)
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        normalized = path.as_posix()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(path)
    if not unique:
        raise FileNotFoundError(f"No scenario YAML files matched: {', '.join(patterns)}")
    return unique


def metrics_path_for(scenario_path: Path) -> Path:
    config: dict[str, Any] = read_yaml(scenario_path)
    result = config.get("result", {})
    if not isinstance(result, dict):
        raise ValueError(f"Scenario result field must be a mapping: {scenario_path}")
    metrics_file = str(result.get("metrics_file", ""))
    if not metrics_file:
        experiment_id = str(config.get("experiment_id", scenario_path.stem))
        metrics_file = (default_result_base(config, experiment_id) / "metrics" / f"{experiment_id}.json").as_posix()
    return ROOT / metrics_file


def scenario_command(scenario_path: Path, args: argparse.Namespace) -> list[str]:
    command = [sys.executable, "scripts/run_mworks_scenario.py", str(scenario_path)]
    if args.no_postprocess:
        command.append("--no-postprocess")
    if args.no_quality_gate:
        command.append("--no-quality-gate")
    if args.allow_needs_iteration:
        command.append("--allow-needs-iteration")
    command.extend(["--min-rmse-improvement-pct", f"{args.min_rmse_improvement_pct:g}"])
    if args.shutdown_session:
        command.append("--shutdown-session")
    return command


def quality_command(scenario_path: Path, args: argparse.Namespace) -> list[str]:
    return [
        sys.executable,
        "scripts/evaluate_result_quality.py",
        str(scenario_path),
        "--write-metrics",
        "--min-rmse-improvement-pct",
        f"{args.min_rmse_improvement_pct:g}",
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scenarios",
        nargs="*",
        default=["scenarios/official/*.yaml"],
        help="Scenario YAML paths or glob patterns. Default: scenarios/official/*.yaml",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print commands without running MCP simulations")
    parser.add_argument("--skip-existing", action="store_true", help="Skip scenarios whose metrics JSON already exists")
    parser.add_argument("--continue-on-failure", action="store_true", help="Continue after a failed scenario and report failures")
    parser.add_argument("--no-postprocess", action="store_true", help="Skip figure and replay generation")
    parser.add_argument("--no-quality-gate", action="store_true", help="Skip automatic result quality evaluation")
    parser.add_argument(
        "--allow-needs-iteration",
        action="store_true",
        help="Keep batch exit code 0 when a quality gate marks a scenario as needs_iteration",
    )
    parser.add_argument(
        "--min-rmse-improvement-pct",
        type=float,
        default=0.5,
        help="Minimum RMSE improvement required for scenarios with controller.baseline_experiment",
    )
    parser.add_argument("--shutdown-session", action="store_true", help="Request Sysplorer session shutdown after each scenario")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scenario_paths = expand_patterns(args.scenarios)
    failures: list[tuple[Path, int]] = []
    skipped: list[Path] = []

    for scenario_path in scenario_paths:
        metrics_path = metrics_path_for(scenario_path)
        if args.skip_existing and metrics_path.exists():
            skipped.append(scenario_path)
            print(f"[SKIP] {scenario_path} -> {metrics_path}")
            if not args.dry_run and not args.no_quality_gate:
                proc = subprocess.run(quality_command(scenario_path, args), cwd=ROOT)
                if proc.returncode != 0:
                    print(f"[ITERATE] skipped existing scenario failed quality gate: {scenario_path}", flush=True)
                    if not args.allow_needs_iteration:
                        failures.append((scenario_path, proc.returncode))
                    if not args.continue_on_failure and not args.allow_needs_iteration:
                        break
            continue

        command = scenario_command(scenario_path, args)
        print("[RUN]", " ".join(command), flush=True)
        if args.dry_run:
            continue

        proc = subprocess.run(command, cwd=ROOT)
        if proc.returncode != 0:
            failures.append((scenario_path, proc.returncode))
            print(f"[FAIL] {scenario_path}: returncode={proc.returncode}", flush=True)
            if not args.continue_on_failure:
                break

    print(f"Scenarios matched: {len(scenario_paths)}")
    print(f"Skipped existing: {len(skipped)}")
    print(f"Failures: {len(failures)}")
    for path, returncode in failures:
        print(f"- {path}: returncode={returncode}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
