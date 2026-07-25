#!/usr/bin/env python3
"""Compile Wave B boundary-layer SMC and compare it with a Python oracle."""

from __future__ import annotations

import argparse
import json
import math
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(__file__).resolve().parent


def wsl_path(path: Path) -> str:
    path = path.resolve()
    return f"/mnt/{path.drive[0].lower()}/{path.relative_to(path.anchor).as_posix()}"


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def oracle() -> list[float]:
    position = [0.2, -0.1, 0.7]
    velocity = [-0.3, 0.2, -0.1]
    reference_position = [1.0, 0.5, 1.2]
    reference_velocity = [0.1, -0.2, 0.0]
    reference_acceleration = [0.05, -0.04, 0.02]
    lam = [1.2, 1.2, 1.4]
    sliding_gain = [2.2, 2.2, 2.8]
    linear_gain = [0.8, 0.8, 1.0]
    boundary = [0.12, 0.12, 0.15]
    acceleration = []
    for i in range(3):
        sliding = reference_velocity[i] - velocity[i] + lam[i] * (reference_position[i] - position[i])
        saturated = clamp(sliding / boundary[i], -1.0, 1.0)
        acceleration.append(reference_acceleration[i] + linear_gain[i] * sliding + sliding_gain[i] * saturated)
    acceleration[2] += 9.80665
    roll = clamp(-acceleration[1] / 9.80665, -math.pi / 6, math.pi / 6)
    pitch = clamp(acceleration[0] / 9.80665, -math.pi / 6, math.pi / 6)
    yaw = 0.3
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    quat = [cy * cp * cr + sy * sp * sr, cy * cp * sr - sy * sp * cr,
            sy * cp * sr + cy * sp * cr, sy * cp * cr - cy * sp * sr]
    normalized_thrust = clamp(acceleration[2] / (9.80665 / 0.37), 0.0, 1.0)
    return acceleration + quat + [normalized_thrust, 1.0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", default=str(ROOT / "Results" / "control_platform" / "g5_wave_b_smc_20260716"))
    args = parser.parse_args()
    result_dir = Path(args.result_dir).resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    exe = result_dir / "wave_b_smc_gate"
    compile_cmd = ["gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic",
                   wsl_path(SOURCE_DIR / "wave_a_controller_core.c"),
                   wsl_path(SOURCE_DIR / "wave_b_smc_core.c"),
                   wsl_path(SOURCE_DIR / "wave_b_smc_gate.c"), "-I", wsl_path(SOURCE_DIR),
                   "-lm", "-o", wsl_path(exe)]
    compile = subprocess.run(["wsl", "-d", "Ubuntu-20.04", "bash", "-lc",
                              " ".join(shlex.quote(part) for part in compile_cmd)],
                             capture_output=True, text=True)
    (result_dir / "compile.stdout.txt").write_text(compile.stdout, encoding="utf-8", newline="\n")
    (result_dir / "compile.stderr.txt").write_text(compile.stderr, encoding="utf-8", newline="\n")
    if compile.returncode:
        (result_dir / "G5_WAVE_B_SMC_GATE.json").write_text(json.dumps({"status": "blocked", "stage": "compile"}, indent=2) + "\n", encoding="utf-8", newline="\n")
        return 1
    run = subprocess.run(["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", shlex.quote(wsl_path(exe))], capture_output=True, text=True)
    exe.unlink(missing_ok=True)
    row = [float(value) for value in run.stdout.strip().split(",")]
    expected = oracle()
    failures = [{"index": i, "actual": got, "expected": want, "diff": abs(got - want)}
                for i, (got, want) in enumerate(zip(row, expected)) if abs(got - want) > 1.0e-12]
    report = {
        "schema": "mosim.control_platform.g5_wave_b_smc_gate.v1",
        "status": "passed" if run.returncode == 0 and not failures else "failed",
        "controller": "smc_boundary_layer",
        "case_count": 1,
        "scalar_comparison_count": len(expected),
        "failure_count": len(failures),
        "max_abs_diff": max((item["diff"] for item in failures), default=0.0),
        "runtime_started": False,
        "shared_gazebo_px4_touched": False,
        "claim_ceiling": "Project-owned fixed-size boundary-layer SMC matches an independent Python oracle offline; no fresh MWORKS, generated-C, or Gazebo/PX4 acceptance is claimed.",
        "failures": failures,
    }
    (result_dir / "G5_WAVE_B_SMC_GATE.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
