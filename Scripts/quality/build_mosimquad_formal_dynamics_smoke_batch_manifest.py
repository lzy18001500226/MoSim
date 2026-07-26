#!/usr/bin/env python3
"""Build the formal Dynamics smoke batch manifest.

This is a static manifest generator. It does not call MWORKS, Sysplorer, MCP,
check_model, SimulateModel, or any GUI/window surface.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCENARIO_CHECK = (
    ROOT
    / "Results"
    / "model_library_refactor"
    / "20260726_plant_runner_baseline"
    / "static_checks"
    / "static_validation_summary.json"
)
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "Results"
    / "model_library_refactor"
    / "20260726_plant_runner_baseline"
    / "static_checks"
    / "dynamics_smoke_batch_manifest"
)

sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
from run_mworks_batch import expand_patterns  # noqa: E402


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_manifest(scenario_check_path: Path) -> dict[str, Any]:
    scenario_check = read_json(scenario_check_path)
    findings: list[dict[str, Any]] = []
    if scenario_check.get("status") != "passed":
        findings.append(
            {
                "code": "scenario_check_not_passed",
                "message": "formal Dynamics smoke scenario binding check must pass before building the batch manifest",
            }
        )
    runner_support_status = str(scenario_check.get("runner_support_status", "unknown"))
    if runner_support_status != "minimal_dynamics_strategy_consumed":
        findings.append(
            {
                "code": "runner_does_not_consume_minimal_dynamics_strategy",
                "message": (
                    "scenario YAML declares minimal_dynamics_only, but the current runner command still uses the broad "
                    "top-level package load; treat the live batch as blocked until runner support or native MCP minimal loading is implemented"
                ),
            }
        )

    scenario_files = [ROOT / item["scenario_file"] for item in scenario_check.get("bindings", [])]
    expanded = expand_patterns([str(path) for path in scenario_files]) if scenario_files else []
    expanded_rel = [rel(path.resolve()) for path in expanded]
    expected_rel = [rel(path.resolve()) for path in scenario_files]
    if expanded_rel != expected_rel:
        findings.append(
            {
                "code": "scenario_expansion_drift",
                "message": "expanded scenario order does not match scenario binding summary order",
            }
        )

    command = [
        sys.executable,
        "Scripts/mworks/run_mworks_batch.py",
        "--no-gui-result-viewer",
        "--no-gui-open",
    ] + expected_rel

    dry_run_command = [
        sys.executable,
        "Scripts/mworks/run_mworks_batch.py",
        "--dry-run",
        "--no-gui-result-viewer",
        "--no-gui-open",
    ] + expected_rel

    return {
        "schema": "mosim.mworks.formal_dynamics_smoke_batch_manifest.v1",
        "status": "passed" if not findings else "failed",
        "static_only": True,
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "scenario_binding_check": rel(scenario_check_path),
        "scenario_count": len(expected_rel),
        "scenario_files": expected_rel,
        "runner_support_status": runner_support_status,
        "future_live_batch_command": command,
        "dry_run_batch_command": dry_run_command,
        "preconditions_for_future_live_run": [
            "User or PMO explicitly authorizes live MWORKS/Sysplorer/Syslab execution.",
            "PMO, legacy ops patrol, or the live task provides a current non-blocking MWORKS activation/window preflight.",
            "Stop before execution on demo, login, activation, authorization, GUI error-report, mixed license, visible unknown, unavailable, or unknown state.",
            "The runner must consume model.live_load_strategy=minimal_dynamics_only, or the task must use an explicitly reviewed native MCP minimal-loading sequence.",
            "All formal check_model targets in the 024 live-gate plan pass before treating SimulateModel outputs as evidence.",
        ],
        "claim_boundary": [
            "This manifest prepares a future live batch command only.",
            "It does not run or prove MWORKS load, check_model, SimulateModel, result variables, controller performance, mission success, or closed_loop.",
            "RotorEffectivenessSmoke remains a single-rotor effectiveness observability smoke, not controller robustness acceptance.",
        ],
        "findings": findings,
    }


def write_markdown(path: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# MoSimQuadrotorModel Formal Dynamics Smoke Batch Manifest",
        "",
        f"Status: `{manifest['status']}`",
        "",
        "Static-only manifest. It prepares the future live batch command but does not call MWORKS, Sysplorer, MCP, `check_model`, or `SimulateModel`.",
        "",
        "## Scenario Files",
        "",
    ]
    for scenario in manifest["scenario_files"]:
        lines.append(f"- `{scenario}`")
    lines.extend(
        [
            "",
            "## Future Live Command",
            "",
            "```powershell",
            " ".join(manifest["future_live_batch_command"]),
            "```",
            "",
            "## Dry Run Command",
            "",
            "```powershell",
            " ".join(manifest["dry_run_batch_command"]),
            "```",
            "",
            "## Preconditions",
            "",
        ]
    )
    for item in manifest["preconditions_for_future_live_run"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Claim Boundary", ""])
    for item in manifest["claim_boundary"]:
        lines.append(f"- {item}")
    write_text(path, "\n".join(lines) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario-check", type=Path, default=SCENARIO_CHECK)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    scenario_check = args.scenario_check if args.scenario_check.is_absolute() else ROOT / args.scenario_check
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    manifest = build_manifest(scenario_check)
    write_json(output_dir / "formal_dynamics_smoke_batch_manifest.json", manifest)
    write_markdown(output_dir / "formal_dynamics_smoke_batch_manifest.md", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if manifest["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
