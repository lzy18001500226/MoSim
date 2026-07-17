#!/usr/bin/env python3
"""Compile and exercise the fixed-size P8 formation-control core."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Scripts" / "control_platform"
RESULT = ROOT / "Results" / "control_platform" / "p8_formation_source_20260717"


def wsl_path(path: Path) -> str:
    return "/mnt/" + path.drive[0].lower() + path.as_posix()[2:]


def main() -> int:
    RESULT.mkdir(parents=True, exist_ok=True)
    executable = RESULT / "formation_control_gate"
    compile_result = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "--", "gcc", "-std=c11", "-O2",
         "-Wall", "-Wextra", "-Werror", wsl_path(SOURCE / "formation_control_core.c"),
         wsl_path(SOURCE / "formation_control_gate.c"), "-I", wsl_path(SOURCE),
         "-lm", "-o", wsl_path(executable)], capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    (RESULT / "compile.stderr.txt").write_text(compile_result.stderr, encoding="utf-8")
    if compile_result.returncode:
        return compile_result.returncode
    run = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "--", wsl_path(executable)],
        check=True, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    rows = list(csv.DictReader(run.stdout.splitlines()))
    signatures = {round(float(row["signature"]), 6) for row in rows}
    failures = []
    if len(rows) != 9:
        failures.append(f"expected 9 modes, got {len(rows)}")
    if len(signatures) < 7:
        failures.append(f"formation modes are not sufficiently distinct: {len(signatures)} signatures")
    for row in rows:
        if int(row["status"]) != 1 or int(row["active"]) < 2:
            failures.append(f"mode {row['mode']} invalid status/active count")
    fault = next(row for row in rows if row["mode"] == "7")
    cbf = next(row for row in rows if row["mode"] == "8")
    containment = next(row for row in rows if row["mode"] == "4")
    if float(containment["desired_follower_distance"]) < 1.0:
        failures.append("containment desired follower separation is below the safety floor")
    if int(fault["failed_mask"]) != 2:
        failures.append("fault-tolerant mode did not isolate agent 2")
    if int(cbf["safety_corrections"]) < 1:
        failures.append("formation CBF did not activate on the close initial geometry")
    report = {
        "schema": "mosim.control_platform.p8_formation_source_gate.v1",
        "status": "passed" if not failures else "failed",
        "mode_count": len(rows),
        "distinct_signature_count": len(signatures),
        "failures": failures,
        "rows": rows,
        "claim_ceiling": "Deterministic fixed-size three-UAV formation reference and diagnostics only; MWORKS generated C and Gazebo runtime are separate gates.",
    }
    (RESULT / "P8_FORMATION_SOURCE_GATE.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
