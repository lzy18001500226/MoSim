#!/usr/bin/env python3
"""Compile and exercise the fixed-size P7 fault-tolerant-control core."""

from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Scripts/control_platform"
RESULT = ROOT / "Results/control_platform/p7_ftc_source_20260717"
NAMES = [
    "fdi", "passive_ftc", "active_ftc", "fault_aware_control_allocation",
    "single_motor_safe_landing", "multi_fault_estimation_reconfiguration",
]


def wsl_path(path: Path) -> str:
    path = path.resolve()
    return f"/mnt/{path.drive[0].lower()}/{path.relative_to(path.anchor).as_posix()}"


def main() -> int:
    RESULT.mkdir(parents=True, exist_ok=True)
    executable = RESULT / "fault_tolerant_control_gate"
    command = [
        "gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
        wsl_path(SOURCE / "fault_tolerant_control_core.c"),
        wsl_path(SOURCE / "fault_tolerant_control_gate.c"),
        "-I", wsl_path(SOURCE), "-lm", "-o", wsl_path(executable),
    ]
    compiled = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", " ".join(map(shlex.quote, command))],
        text=True, capture_output=True, check=False,
    )
    run = None
    rows = []
    if compiled.returncode == 0:
        run = subprocess.run(
            ["wsl", "-d", "Ubuntu-20.04", wsl_path(executable)],
            text=True, capture_output=True, check=False,
        )
        for line in run.stdout.splitlines():
            values = line.split(",")
            if len(values) == 8:
                rows.append({
                    "mode_id": int(values[0]),
                    "mode": NAMES[int(values[0]) - 1],
                    "action": int(values[1]),
                    "isolated_mask": int(values[2]),
                    "fault_count": int(values[3]),
                    "eta_hat_1": float(values[4]),
                    "eta_hat_2": float(values[5]),
                    "motor_command_1": float(values[6]),
                    "achieved_total_thrust": float(values[7]),
                })
    passed = compiled.returncode == 0 and run is not None and run.returncode == 0 and len(rows) == 6
    report = {
        "schema": "mosim.control_platform.p7_ftc_source_gate.v1",
        "status": "passed" if passed else "failed",
        "modes": NAMES,
        "mode_count": len(rows),
        "fixed_size": True,
        "dynamic_allocation": False,
        "rows": rows,
        "compile_stderr": compiled.stderr[-4000:],
        "run_stderr": run.stderr[-4000:] if run else None,
        "reuse_basis": [
            "Models/QuadrotorControllerBlocks/AWFF_InnovationGraphicalControllers.mo",
            "Config/controllers/l1_multi_fault_isolation_sysblock/default.yaml",
        ],
        "claim_ceiling": "Deterministic source scenarios prove the unified FDI/isolation/reallocation contract only; MWORKS generated-C and Gazebo actuator evidence remain separate gates.",
    }
    (RESULT / "P7_FTC_SOURCE_GATE.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    executable.unlink(missing_ok=True)
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
