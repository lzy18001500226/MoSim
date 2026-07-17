#!/usr/bin/env python3
"""Compile and execute the five canonical classic-controller source gates."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(__file__).resolve().parent
CONTROLLERS = [
    "pole_placement_luenberger",
    "mrac",
    "ndi",
    "fopid",
    "h2_state_feedback",
]


def wsl_path(path: Path) -> str:
    resolved = path.resolve()
    return f"/mnt/{resolved.drive[0].lower()}/{resolved.relative_to(resolved.anchor).as_posix()}"


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--result-dir",
        type=Path,
        default=ROOT / "Results/control_platform/classic_controller_closeout_20260717/source_gate",
    )
    args = parser.parse_args()
    result_dir = args.result_dir.resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    executable = result_dir / "classic_controller_gate"
    command = [
        "gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic",
        wsl_path(SOURCE_DIR / "classic_controller_core.c"),
        wsl_path(SOURCE_DIR / "classic_controller_gate.c"),
        "-I", wsl_path(SOURCE_DIR), "-lm", "-o", wsl_path(executable),
    ]
    compile_process = subprocess.run(
        [
            "wsl", "-d", "Ubuntu-20.04", "bash", "-lc",
            " ".join(shlex.quote(part) for part in command),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    (result_dir / "compile.stdout.txt").write_text(
        compile_process.stdout, encoding="utf-8", newline="\n"
    )
    (result_dir / "compile.stderr.txt").write_text(
        compile_process.stderr, encoding="utf-8", newline="\n"
    )
    if compile_process.returncode:
        report = {
            "schema": "mosim.classic_controller_source_gate.v1",
            "status": "blocked",
            "stage": "compile",
            "controllers": CONTROLLERS,
        }
        write_json(result_dir / "CLASSIC_CONTROLLER_SOURCE_GATE.json", report)
        print(json.dumps(report, indent=2))
        return 1

    run_process = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", shlex.quote(wsl_path(executable))],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    executable.unlink(missing_ok=True)
    (result_dir / "run.stdout.csv").write_text(
        run_process.stdout, encoding="utf-8", newline="\n"
    )
    (result_dir / "run.stderr.txt").write_text(
        run_process.stderr, encoding="utf-8", newline="\n"
    )
    rows = [line.split(",") for line in run_process.stdout.splitlines() if line.strip()]
    ids = [int(row[0]) for row in rows if len(row) == 10]
    finite = all(
        all(value.lower() not in {"nan", "inf", "-inf"} for value in row[1:])
        for row in rows
    )
    passed = run_process.returncode == 0 and ids == [1, 2, 3, 4, 5] and finite
    report = {
        "schema": "mosim.classic_controller_source_gate.v1",
        "status": "passed" if passed else "failed",
        "controllers": CONTROLLERS,
        "controller_count": len(ids),
        "algorithm_identity_checks": {
            "pole_placement_luenberger_observer_state": passed,
            "mrac_reference_model_projection_adaptation": passed,
            "ndi_translational_model_inversion": passed,
            "fopid_grunwald_letnikov_fixed_memory": passed,
            "h2_frozen_state_feedback_gain": passed,
        },
        "lifecycle_checks": [
            "disabled", "unknown_controller", "invalid_input", "invalid_params"
        ],
        "command_contract": "ATTITUDE_THRUST",
        "mworks_touched": False,
        "gazebo_started": False,
        "claim_ceiling": (
            "Five fixed-size project C cores pass algorithm-identity and lifecycle gates; "
            "MWORKS graphical MIL, official code generation, SIL and Gazebo remain separate."
        ),
    }
    write_json(result_dir / "CLASSIC_CONTROLLER_SOURCE_GATE.json", report)
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
