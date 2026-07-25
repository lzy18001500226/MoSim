#!/usr/bin/env python3
"""Compile the P2 core and verify it against independent physical invariants."""

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
    resolved = path.resolve()
    return f"/mnt/{resolved.drive[0].lower()}/{resolved.relative_to(resolved.anchor).as_posix()}"


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def expected_acceleration(controller_id: int) -> tuple[list[float], list[float], float]:
    position = [0.2, -0.1, 0.7]
    velocity = [-0.3, 0.2, -0.1]
    reference_position = [1.0, 0.5, 1.2]
    reference_velocity = [0.1, -0.2, 0.0]
    reference_acceleration = [0.05, -0.04, 0.02]
    kp = [11.0, 11.0, 4.0]
    kv = [6.5, 6.5, 4.0]
    k1 = [4.0, 4.0, 2.0]
    k2 = [2.75, 2.75, 2.0]
    gamma = [0.03, 0.03, 0.04]
    disturbance = [0.0, 0.0, 0.0]
    acceleration = []
    storage = 0.0
    for axis in range(3):
        ep = reference_position[axis] - position[axis]
        ev = reference_velocity[axis] - velocity[axis]
        feedback = kp[axis] * ep + kv[axis] * ev
        if controller_id == 4:
            sliding = ev + k1[axis] * ep
            disturbance[axis] = gamma[axis] * sliding * 0.02
            feedback = k1[axis] * ev + k2[axis] * sliding + disturbance[axis]
        if controller_id == 3:
            storage += 0.5 * 1.0 * ev * ev + 0.5 * kp[axis] * ep * ep
        acceleration.append(reference_acceleration[axis] + feedback)
    acceleration[2] += 9.80665
    horizontal = math.hypot(acceleration[0], acceleration[1])
    horizontal_limit = max(0.0, acceleration[2]) * math.tan(math.pi / 6.0)
    if horizontal > horizontal_limit:
        scale = horizontal_limit / horizontal
        acceleration[0] *= scale
        acceleration[1] *= scale
    return acceleration, disturbance, storage


def body_z_from_quaternion(q: list[float]) -> list[float]:
    w, x, y, z = q
    return [
        2.0 * (x * z + w * y),
        2.0 * (y * z - w * x),
        1.0 - 2.0 * (x * x + y * y),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--result-dir",
        default=str(ROOT / "Results/control_platform/p2_linear_robust_source_20260716"),
    )
    args = parser.parse_args()
    result_dir = Path(args.result_dir).resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    executable = result_dir / "linear_robust_gate"
    compile_command = [
        "gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic",
        wsl_path(SOURCE_DIR / "linear_robust_attitude_thrust_core.c"),
        wsl_path(SOURCE_DIR / "linear_robust_attitude_thrust_gate.c"),
        "-I", wsl_path(SOURCE_DIR), "-lm", "-o", wsl_path(executable),
    ]
    compile_process = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", " ".join(shlex.quote(part) for part in compile_command)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    (result_dir / "compile.stdout.txt").write_text(compile_process.stdout, encoding="utf-8")
    (result_dir / "compile.stderr.txt").write_text(compile_process.stderr, encoding="utf-8")
    if compile_process.returncode:
        report = {"schema": "mosim.control_platform.p2_linear_robust_gate.v1", "status": "blocked", "stage": "compile"}
        write_json(result_dir / "P2_LINEAR_ROBUST_SOURCE_GATE.json", report)
        return 1

    run_process = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", shlex.quote(wsl_path(executable))],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    executable.unlink(missing_ok=True)
    output_lines = [line for line in run_process.stdout.splitlines() if line.strip()]
    rows = [[float(value) for value in line.split(",")] for line in output_lines if not line.startswith("L,")]
    lifecycle_rows = [line.split(",") for line in output_lines if line.startswith("L,")]
    failures: list[dict] = []
    max_difference = 0.0
    for row in rows:
        controller_id = int(row[0])
        return_code = int(row[1])
        acceleration = row[2:5]
        quaternion = row[5:9]
        normalized_thrust, collective_thrust = row[9:11]
        estimated_position = row[11:14]
        estimated_velocity = row[14:17]
        adaptive_disturbance = row[17:20]
        storage_function = row[20]
        saturated = int(row[21])
        status_code = int(row[22])
        expected_accel, expected_disturbance, expected_storage = expected_acceleration(controller_id)
        checks = {
            "return_code": (return_code, 0.0),
            "status_code": (status_code, 0.0),
            "quaternion_norm": (math.sqrt(sum(value * value for value in quaternion)), 1.0),
            "collective_thrust": (collective_thrust, 1.0 * math.sqrt(sum(value * value for value in acceleration))),
            "normalized_thrust": (normalized_thrust, collective_thrust / (1.0 * 9.80665 / 0.37)),
            "storage_function": (storage_function, expected_storage),
        }
        for axis, (actual, expected) in enumerate(zip(acceleration, expected_accel, strict=True)):
            checks[f"acceleration_{axis}"] = (actual, expected)
        expected_estimated_position = [0.2, -0.1, 0.7] if controller_id == 1 else [0.0, 0.0, 0.0]
        expected_estimated_velocity = [-0.3, 0.2, -0.1] if controller_id == 1 else [0.0, 0.0, 0.0]
        for axis in range(3):
            checks[f"estimated_position_{axis}"] = (estimated_position[axis], expected_estimated_position[axis])
            checks[f"estimated_velocity_{axis}"] = (estimated_velocity[axis], expected_estimated_velocity[axis])
            checks[f"adaptive_disturbance_{axis}"] = (adaptive_disturbance[axis], expected_disturbance[axis])
        force_direction = [value / math.sqrt(sum(item * item for item in acceleration)) for value in acceleration]
        body_z = body_z_from_quaternion(quaternion)
        for axis in range(3):
            checks[f"body_z_{axis}"] = (body_z[axis], force_direction[axis])
        if saturated not in (0, 1):
            failures.append({"controller_id": controller_id, "field": "saturated", "actual": saturated})
        for field, (actual, expected) in checks.items():
            difference = abs(actual - expected)
            max_difference = max(max_difference, difference)
            if difference > 1.0e-10:
                failures.append({"controller_id": controller_id, "field": field, "actual": actual, "expected": expected, "difference": difference})

    lifecycle_expected = {
        "disabled": (0, 1, 0.0),
        "invalid_input": (-3, -3, 0.0),
        "unknown_controller": (-2, -2, 0.0),
        "invalid_params": (-5, -5, 0.0),
    }
    lifecycle_checks: dict[str, dict] = {}
    for row in lifecycle_rows:
        name, return_code, status_code, value = row[1], int(row[2]), int(row[3]), float(row[4])
        passed = False
        if name in lifecycle_expected:
            expected_return, expected_status, expected_value = lifecycle_expected[name]
            passed = (return_code, status_code) == (expected_return, expected_status) and abs(value - expected_value) <= 1.0e-12
        elif name == "tilt_limit":
            passed = return_code == 0 and status_code == 0 and value <= math.pi / 6.0 + 1.0e-12
        elif name == "adaptive_continuity":
            passed = return_code == 0 and status_code == 0 and value > 0.0
        elif name == "deterministic_reset":
            expected_once = 0.03 * (4.0 * 1.0) * 0.02
            passed = return_code == 0 and status_code == 0 and abs(value - expected_once) <= 1.0e-12
        lifecycle_checks[name] = {"passed": passed, "return_code": return_code, "status_code": status_code, "value": value}
        if not passed:
            failures.append({"lifecycle_case": name, "return_code": return_code, "status_code": status_code, "value": value})

    report = {
        "schema": "mosim.control_platform.p2_linear_robust_gate.v1",
        "status": "passed" if run_process.returncode == 0 and len(rows) == 4 and len(lifecycle_checks) == 7 and not failures else "failed",
        "controllers": ["lqg", "feedback_linearization", "passivity_based_control", "adaptive_backstepping"],
        "case_count": len(rows),
        "lifecycle_case_count": len(lifecycle_checks),
        "lifecycle_checks": lifecycle_checks,
        "failure_count": len(failures),
        "max_abs_difference": max_difference,
        "tolerance": 1.0e-10,
        "command_contract": "ATTITUDE_THRUST",
        "runtime_started": False,
        "claim_ceiling": "Fixed-size project C cores pass independent state, force, attitude, estimator, adaptive-state, and storage-function checks; MWORKS, generated C/SIL, and Gazebo runtime remain pending.",
        "failures": failures[:30],
    }
    write_json(result_dir / "P2_LINEAR_ROBUST_SOURCE_GATE.json", report)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
