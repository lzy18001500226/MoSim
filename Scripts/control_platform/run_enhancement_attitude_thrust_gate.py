#!/usr/bin/env python3
"""Compile and run the fixed-size P5 enhancement controller gate."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(__file__).resolve().parent


def wsl_path(path: Path) -> str:
    resolved = path.resolve()
    return f"/mnt/{resolved.drive[0].lower()}/{resolved.relative_to(resolved.anchor).as_posix()}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--result-dir",
        default=str(ROOT / "Results/control_platform/p5_enhancement_source_20260717"),
    )
    args = parser.parse_args()
    result_dir = Path(args.result_dir).resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    executable = result_dir / "enhancement_gate"
    compile_command = [
        "gcc",
        "-std=c11",
        "-O2",
        "-Wall",
        "-Wextra",
        "-Werror",
        wsl_path(SOURCE_DIR / "enhancement_attitude_thrust_core.c"),
        wsl_path(SOURCE_DIR / "enhancement_attitude_thrust_gate.c"),
        "-I",
        wsl_path(SOURCE_DIR),
        "-lm",
        "-o",
        wsl_path(executable),
    ]
    compile_result = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", " ".join(shlex.quote(part) for part in compile_command)],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    (result_dir / "compile.stdout.txt").write_text(compile_result.stdout, encoding="utf-8")
    (result_dir / "compile.stderr.txt").write_text(compile_result.stderr, encoding="utf-8")
    if compile_result.returncode:
        report = {
            "schema": "mosim.control_platform.p5_enhancement_gate.v1",
            "status": "blocked",
            "stage": "compile",
        }
    else:
        run_result = subprocess.run(
            ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", shlex.quote(wsl_path(executable))],
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        try:
            gate_payload = json.loads(run_result.stdout)
        except json.JSONDecodeError:
            gate_payload = {"status": "failed", "failures": -1}
        report = {
            "schema": "mosim.control_platform.p5_enhancement_gate.v1",
            "status": "passed" if run_result.returncode == 0 and gate_payload.get("status") == "passed" else "failed",
            "controllers": [
                "l1_adaptive",
                "awff",
                "complete_adrc",
                "standardized_indi",
                "parameter_scheduling",
                "ilc",
            ],
            "controller_count": gate_payload.get("controller_count"),
            "failure_count": gate_payload.get("failures"),
            "fixed_size_state": {"ilc_phase_bins": 64, "axes": 3},
            "runtime_started": False,
            "external_gate_decisions": {
                "fuzzy_anfis_compensation": {
                    "decision": "deferred",
                    "reason": "No frozen ANFIS premise/consequent artifact, dataset hash, or held-out benchmark exists.",
                },
                "rbf_nn_disturbance_compensation": {
                    "decision": "deferred",
                    "reason": "No frozen RBF centers, widths, weights, dataset hash, or held-out disturbance benchmark exists.",
                },
                "rl_gain_scheduling_residual_policy": {
                    "decision": "deferred",
                    "reason": "No frozen policy artifact, training manifest, safety envelope, or independent fallback benchmark exists.",
                },
            },
            "claim_ceiling": (
                "Six deterministic fixed-size enhancement cores pass source and lifecycle checks. "
                "MWORKS MIL, generated C/SIL, and Gazebo runtime remain pending."
            ),
        }
        (result_dir / "gate.stdout.txt").write_text(run_result.stdout, encoding="utf-8")
        (result_dir / "gate.stderr.txt").write_text(run_result.stderr, encoding="utf-8")
    executable.unlink(missing_ok=True)
    report_path = result_dir / "P5_ENHANCEMENT_SOURCE_GATE.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
