#!/usr/bin/env python3
"""Compile the P3 sliding-mode core and compare it with an independent oracle."""

from __future__ import annotations

import argparse
import json
import math
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(__file__).resolve().parent
CONTROLLERS = {
    1: "integral_smc",
    2: "terminal_smc",
    3: "nonsingular_terminal_smc",
    4: "super_twisting_smc",
    5: "adaptive_smc",
    6: "fuzzy_smc",
}


def wsl_path(path: Path) -> str:
    resolved = path.resolve()
    return f"/mnt/{resolved.drive[0].lower()}/{resolved.relative_to(resolved.anchor).as_posix()}"


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def signed_power(value: float, exponent: float) -> float:
    return math.copysign(abs(value) ** exponent, value) if value else 0.0


def oracle(controller_id: int) -> dict[str, list[float]]:
    position = [0.2, -0.1, 0.7]
    velocity = [-0.3, 0.2, -0.1]
    reference_position = [1.0, 0.5, 1.2]
    reference_velocity = [0.1, -0.2, 0.0]
    reference_acceleration = [0.05, -0.04, 0.02]
    lam = [4.0, 4.0, 2.0]
    linear = [2.75, 2.75, 2.0]
    reaching = [0.08, 0.08, 0.08]
    boundary = [0.35, 0.35, 0.35]
    integral_gain = [0.08, 0.08, 0.08]
    alpha = [0.90, 0.90, 0.92]
    nonsingular = [0.10, 0.10, 0.10]
    st_k1 = [1.6, 1.6, 2.0]
    st_k2 = [1.2, 1.2, 1.5]
    adaptive_rate = [0.04, 0.04, 0.04]
    fuzzy_delta = [0.04, 0.04, 0.04]
    dt = 0.02
    acceleration, sliding, auxiliary, gains = [], [], [], []
    st_state, adaptive_state = [], []
    for axis in range(3):
        ep = reference_position[axis] - position[axis]
        ev = reference_velocity[axis] - velocity[axis]
        s = ev + lam[axis] * ep
        aux = 0.0
        gain = reaching[axis]
        if controller_id == 1:
            aux = ep * dt
            s += integral_gain[axis] * aux
        elif controller_id == 2:
            s = ev + lam[axis] * signed_power(ep, alpha[axis])
        elif controller_id == 3:
            s += nonsingular[axis] * signed_power(ep, 1.5)
        sign = clamp(s / boundary[axis], -1.0, 1.0)
        if controller_id == 4:
            aux = st_k2[axis] * sign * dt
            robust = st_k1[axis] * math.sqrt(abs(s)) * sign + aux
            gain = st_k1[axis]
        elif controller_id == 5:
            gain = clamp(reaching[axis] + adaptive_rate[axis] * (abs(s) - 0.05) * dt,
                         reaching[axis], [0.30, 0.30, 0.35][axis])
            robust = gain * sign
        elif controller_id == 6:
            normalized = clamp(abs(s) / (4.0 * boundary[axis]), 0.0, 1.0)
            gain += fuzzy_delta[axis] * normalized * (2.0 - normalized)
            robust = gain * sign
        else:
            robust = gain * sign
        acceleration.append(reference_acceleration[axis] + lam[axis] * ev + linear[axis] * s + robust)
        sliding.append(s)
        auxiliary.append(aux)
        gains.append(gain)
        st_state.append(aux if controller_id == 4 else 0.0)
        adaptive_state.append(gain if controller_id == 5 else reaching[axis])
    acceleration[2] += 9.80665
    horizontal = math.hypot(acceleration[0], acceleration[1])
    horizontal_limit = max(0.0, acceleration[2]) * math.tan(math.pi / 6.0)
    if horizontal > horizontal_limit:
        scale = horizontal_limit / horizontal
        acceleration[0] *= scale
        acceleration[1] *= scale
    return {
        "acceleration": acceleration,
        "sliding": sliding,
        "auxiliary": auxiliary,
        "gains": gains,
        "st_state": st_state,
        "adaptive_state": adaptive_state,
    }


def body_z_from_quaternion(q: list[float]) -> list[float]:
    w, x, y, z = q
    return [2.0 * (x * z + w * y), 2.0 * (y * z - w * x), 1.0 - 2.0 * (x * x + y * y)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", default=str(ROOT / "Results/control_platform/p3_sliding_mode_source_20260716"))
    args = parser.parse_args()
    result_dir = Path(args.result_dir).resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    executable = result_dir / "sliding_mode_gate"
    command = [
        "gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic",
        wsl_path(SOURCE_DIR / "sliding_mode_attitude_thrust_core.c"),
        wsl_path(SOURCE_DIR / "sliding_mode_attitude_thrust_gate.c"),
        "-I", wsl_path(SOURCE_DIR), "-lm", "-o", wsl_path(executable),
    ]
    compile_process = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", " ".join(shlex.quote(part) for part in command)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    (result_dir / "compile.stdout.txt").write_text(compile_process.stdout, encoding="utf-8")
    (result_dir / "compile.stderr.txt").write_text(compile_process.stderr, encoding="utf-8")
    if compile_process.returncode:
        report = {"schema": "mosim.control_platform.p3_sliding_mode_gate.v1", "status": "blocked", "stage": "compile"}
        (result_dir / "P3_SLIDING_MODE_SOURCE_GATE.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 1
    run = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", shlex.quote(wsl_path(executable))],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    executable.unlink(missing_ok=True)
    lines = [line for line in run.stdout.splitlines() if line.strip()]
    rows = [[float(value) for value in line.split(",")] for line in lines if not line.startswith("L,")]
    lifecycle_rows = [line.split(",") for line in lines if line.startswith("L,")]
    failures: list[dict] = []
    max_difference = 0.0
    for row in rows:
        controller_id = int(row[0])
        expected = oracle(controller_id)
        actual_groups = {
            "acceleration": row[2:5], "sliding": row[5:8], "auxiliary": row[8:11], "gains": row[11:14]
        }
        for group, actual_values in actual_groups.items():
            for axis, (actual, wanted) in enumerate(zip(actual_values, expected[group], strict=True)):
                difference = abs(actual - wanted)
                max_difference = max(max_difference, difference)
                if difference > 1.0e-10:
                    failures.append({"controller_id": controller_id, "field": f"{group}_{axis}", "actual": actual, "expected": wanted})
        quaternion = row[14:18]
        acceleration = row[2:5]
        norm = math.sqrt(sum(value * value for value in acceleration))
        body_z = body_z_from_quaternion(quaternion)
        for axis in range(3):
            difference = abs(body_z[axis] - acceleration[axis] / norm)
            max_difference = max(max_difference, difference)
            if difference > 1.0e-10:
                failures.append({"controller_id": controller_id, "field": f"body_z_{axis}"})
        if int(row[1]) != 0 or int(row[23]) != 0:
            failures.append({"controller_id": controller_id, "field": "status"})
        if abs(row[20] - expected["st_state"][0]) > 1.0e-10:
            failures.append({"controller_id": controller_id, "field": "super_twisting_state"})
        if abs(row[21] - expected["adaptive_state"][0]) > 1.0e-10:
            failures.append({"controller_id": controller_id, "field": "adaptive_state"})
    lifecycle_expected = {
        "disabled": (0, 1, 0.0), "invalid_input": (-3, -3, 0.0),
        "unknown_controller": (-2, -2, 0.0), "invalid_params": (-5, -5, 0.0),
    }
    lifecycle_checks = {}
    for row in lifecycle_rows:
        name, rc, status, value = row[1], int(row[2]), int(row[3]), float(row[4])
        if name in lifecycle_expected:
            wanted = lifecycle_expected[name]
            passed = (rc, status) == wanted[:2] and abs(value - wanted[2]) <= 1.0e-12
        elif name == "super_twisting_continuity":
            passed = rc == 0 and status == 0 and value > 0.02
        else:
            passed = rc == 0 and status == 0 and abs(value - 0.024) <= 1.0e-12
        lifecycle_checks[name] = {"passed": passed, "return_code": rc, "status_code": status, "value": value}
        if not passed:
            failures.append({"lifecycle_case": name})
    report = {
        "schema": "mosim.control_platform.p3_sliding_mode_gate.v1",
        "status": "passed" if run.returncode == 0 and len(rows) == 6 and len(lifecycle_checks) == 6 and not failures else "failed",
        "controllers": list(CONTROLLERS.values()),
        "case_count": len(rows),
        "lifecycle_case_count": len(lifecycle_checks),
        "lifecycle_checks": lifecycle_checks,
        "neural_smc": {
            "decision": "deferred",
            "selectable": False,
            "reason": "No frozen training dataset, model artifact hash, or independently validated bounded inference weights exist.",
            "reopen_gate": "Frozen dataset and model hash, deterministic fixed-size inference, fallback tests, and an independent safety benchmark.",
        },
        "failure_count": len(failures),
        "max_abs_difference": max_difference,
        "command_contract": "ATTITUDE_THRUST",
        "runtime_started": False,
        "claim_ceiling": "Six fixed-size sliding-mode variants pass independent numerical and lifecycle checks. MWORKS, generated C/SIL, and Gazebo runtime remain pending; Neural-SMC is explicitly deferred rather than represented by an untrained zero residual.",
        "failures": failures[:30],
    }
    (result_dir / "P3_SLIDING_MODE_SOURCE_GATE.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
