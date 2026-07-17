#!/usr/bin/env python3
"""Compile and exercise all fixed-size SafetySupervisor modes."""

from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Scripts/control_platform"
RESULT = ROOT / "Results/control_platform/p6_safety_source_20260717"
NAMES = [
    "safety_filter", "cbf", "reference_governor", "geofence",
    "emergency_stop", "return_and_land", "failsafe_state_machine",
]


def wsl_path(path: Path) -> str:
    path = path.resolve()
    return f"/mnt/{path.drive[0].lower()}/{path.relative_to(path.anchor).as_posix()}"


def main() -> int:
    RESULT.mkdir(parents=True, exist_ok=True)
    executable = RESULT / "safety_supervisor_gate"
    command = [
        "gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
        wsl_path(SOURCE / "safety_supervisor_core.c"),
        wsl_path(SOURCE / "safety_supervisor_gate.c"),
        "-I", wsl_path(SOURCE), "-lm", "-o", wsl_path(executable),
    ]
    compile_result = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", " ".join(map(shlex.quote, command))],
        text=True, capture_output=True, check=False,
    )
    rows: list[dict[str, object]] = []
    run_result = None
    if compile_result.returncode == 0:
        run_result = subprocess.run(
            ["wsl", "-d", "Ubuntu-20.04", wsl_path(executable)],
            text=True, capture_output=True, check=False,
        )
        for line in run_result.stdout.splitlines():
            values = line.split(",")
            if len(values) == 8:
                rows.append({
                    "mode_id": int(values[0]), "mode": NAMES[int(values[0]) - 1],
                    "return_code": int(values[1]), "status_code": int(values[2]),
                    "action": int(values[3]), "active_constraints": int(values[4]),
                    "safe_acceleration_x": float(values[5]),
                    "safe_thrust": float(values[6]), "safe_reference_x": float(values[7]),
                })
    passed = compile_result.returncode == 0 and run_result is not None and run_result.returncode == 0 and len(rows) == 7
    report = {
        "schema": "mosim.control_platform.p6_safety_source_gate.v1",
        "status": "passed" if passed else "failed",
        "modes": NAMES,
        "mode_count": len(rows),
        "fixed_size": True,
        "dynamic_allocation": False,
        "rows": rows,
        "compile_stderr": compile_result.stderr[-4000:],
        "run_stderr": run_result.stderr[-4000:] if run_result else None,
        "claim_ceiling": "Deterministic source-level SafetySupervisor scenarios only; MWORKS, generated C and event-driven Gazebo gates remain separate.",
    }
    (RESULT / "P6_SAFETY_SOURCE_GATE.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    executable.unlink(missing_ok=True)
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
