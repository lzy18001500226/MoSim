#!/usr/bin/env python3
"""Compile Wave A C and compare it with an independent Python oracle."""

from __future__ import annotations

import argparse
import json
import math
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(__file__).resolve().parent


def write_text_lf(path: Path, value: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(value)


def wsl_path(path: Path) -> str:
    path = path.resolve()
    return f"/mnt/{path.drive[0].lower()}/{path.relative_to(path.anchor).as_posix()}"


def clamp(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


def outer(controller_id: int, integral_scale: float = 1.0) -> list[float]:
    position = [0.2, -0.1, 0.7]
    velocity = [-0.3, 0.2, -0.1]
    rp = [1.0, 0.5, 1.2]
    rv = [0.1, -0.2, 0.0]
    ra = [0.05, -0.04, 0.02]
    kp = [1.6, 1.6, 2.2]
    kv = [1.8, 1.8, 2.0]
    ki = [0.20, 0.20, 0.30]
    k1 = [1.1, 1.1, 1.3]
    k2 = [1.8, 1.8, 2.0]
    acc = []
    for i in range(3):
        ep = rp[i] - position[i]
        ev = rv[i] - velocity[i]
        if controller_id == 4:
            feedback = k1[i] * ev + k2[i] * (ev + k1[i] * ep)
        else:
            feedback = kp[i] * ep + kv[i] * ev
            if controller_id == 2:
                feedback += ki[i] * ep * 0.02 * integral_scale
        acc.append(ra[i] + feedback)
    acc[2] += 9.80665
    roll = clamp(-acc[1] / 9.80665, math.pi / 6)
    pitch = clamp(acc[0] / 9.80665, math.pi / 6)
    yaw = 0.3
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    quat = [cy * cp * cr + sy * sp * sr, cy * cp * sr - sy * sp * cr,
            sy * cp * sr + cy * sp * cr, sy * cp * cr - cy * sp * sr]
    thrust = max(0.0, min(1.0, acc[2] / (9.80665 / 0.37)))
    return acc + quat + [0.0, 0.0, 0.0, thrust, thrust * 1.0 * 9.80665 / 0.37, 1.0, 0.0, 0.0]


def so3() -> list[float]:
    angle = 0.4
    qe = [math.cos(angle / 2), 0.0, math.sin(angle / 2), 0.0]
    rates = [0.1, -0.05 + 2 * 3.0 * qe[2], 0.02]
    thrust = 6.8 / (1.0 * 9.80665 / 0.37)
    return [0.0, 0.0, 0.0] + qe + rates + [thrust, 6.8, 2.0, 0.0, 0.0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", default=str(ROOT / "Results" / "control_platform" / "g5_wave_a_20260716"))
    args = parser.parse_args()
    result_dir = Path(args.result_dir).resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    exe = result_dir / "wave_a_controller_gate"
    compile_cmd = [
        "gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic",
        wsl_path(SOURCE_DIR / "wave_a_controller_core.c"),
        wsl_path(SOURCE_DIR / "wave_a_controller_gate.c"),
        "-I", wsl_path(SOURCE_DIR), "-lm", "-o", wsl_path(exe),
    ]
    shell_compile = " ".join(shlex.quote(part) for part in compile_cmd)
    compile_proc = subprocess.run(["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", shell_compile], capture_output=True, text=True)
    write_text_lf(result_dir / "compile.stdout.txt", compile_proc.stdout)
    write_text_lf(result_dir / "compile.stderr.txt", compile_proc.stderr)
    if compile_proc.returncode:
        report = {"schema": "mosim.control_platform.wave_a_gate.v1", "status": "blocked", "stage": "compile", "returncode": compile_proc.returncode}
        write_text_lf(result_dir / "G5_WAVE_A_GATE.json", json.dumps(report, indent=2) + "\n")
        return 1
    run_proc = subprocess.run(["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", shlex.quote(wsl_path(exe))], capture_output=True, text=True)
    exe.unlink(missing_ok=True)
    write_text_lf(result_dir / "run.stderr.txt", run_proc.stderr)
    rows = [[float(value) for value in line.split(",")] for line in run_proc.stdout.splitlines() if line.strip()]
    expected = [outer(1), outer(2, 1.0), outer(2, 2.0), so3(), outer(4)]
    failures = []
    max_diff = 0.0
    for row_index, (row, oracle) in enumerate(zip(rows, expected, strict=True)):
        actual = row[1:]
        for column, (got, want) in enumerate(zip(actual, oracle, strict=True)):
            diff = abs(got - want)
            max_diff = max(max_diff, diff)
            if diff > 1.0e-12:
                failures.append({"row": row_index, "column": column, "actual": got, "expected": want, "diff": diff})
    report = {
        "schema": "mosim.control_platform.wave_a_gate.v1",
        "status": "passed" if not failures and run_proc.returncode == 0 and len(rows) == 5 else "failed",
        "controllers": ["lqr", "lqi", "so3_attitude", "backstepping"],
        "case_count": len(rows),
        "scalar_comparison_count": sum(len(row) - 1 for row in rows),
        "failure_count": len(failures),
        "max_abs_diff": max_diff,
        "tolerance": 1.0e-12,
        "runtime_started": False,
        "shared_gazebo_px4_touched": False,
        "claim_ceiling": "Project-owned fixed-size C core matches an independent Python oracle offline; no fresh MWORKS, generated-C, or Gazebo/PX4 acceptance is claimed.",
        "failures": failures[:20],
    }
    write_text_lf(result_dir / "G5_WAVE_A_GATE.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
