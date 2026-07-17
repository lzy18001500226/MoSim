#!/usr/bin/env python3
"""Compile the P4 fixed-size MPC family and compare it with a Python oracle."""

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
    1: "linear_mpc",
    2: "robust_mpc",
    3: "adaptive_mpc",
    4: "tube_mpc",
    5: "explicit_gain_scheduled_mpc",
    6: "ilqr",
    7: "mppi",
}


def wsl_path(path: Path) -> str:
    resolved = path.resolve()
    return f"/mnt/{resolved.drive[0].lower()}/{resolved.relative_to(resolved.anchor).as_posix()}"


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def stage_cost(ep: float, ev: float, acceleration: float, axis: int) -> float:
    h = 0.25
    wp = [1.0, 1.0, 1.2][axis]
    wv = [0.08, 0.08, 0.10][axis]
    wu = [0.002, 0.002, 0.003][axis]
    pe = ep + h * ev - 0.5 * h * h * acceleration
    ve = ev - h * acceleration
    return wp * pe * pe + wv * ve * ve + wu * acceleration * acceleration


def linear_solution(ep: float, ev: float, previous: float, axis: int) -> float:
    h = 0.25
    wp = [1.0, 1.0, 1.2][axis]
    wv = [0.08, 0.08, 0.10][axis]
    wu = [0.002, 0.002, 0.003][axis]
    numerator = wp * h * h * ep + 2.0 * wv * h * ev + 2.0 * wu * previous
    denominator = 0.5 * wp * h**4 + 2.0 * wv * h * h + 2.0 * wu
    return numerator / denominator


def ilqr_solution(ep: float, ev: float, initial: float, axis: int) -> float:
    h = 0.25
    wp = [1.0, 1.0, 1.2][axis]
    wv = [0.08, 0.08, 0.10][axis]
    wu = [0.002, 0.002, 0.003][axis]
    hessian = 0.5 * wp * h**4 + 2.0 * wv * h * h + 2.0 * wu
    acceleration = initial
    for _ in range(5):
        pe = ep + h * ev - 0.5 * h * h * acceleration
        ve = ev - h * acceleration
        gradient = -wp * h * h * pe - 2.0 * wv * h * ve + 2.0 * wu * acceleration
        acceleration -= 0.65 * gradient / hessian
    return acceleration


def mppi_solution(ep: float, ev: float, initial: float, axis: int) -> tuple[float, float]:
    samples = [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]
    noise = [0.35, 0.35, 0.25][axis]
    candidates = [initial + sample * noise for sample in samples]
    costs = [stage_cost(ep, ev, candidate, axis) for candidate in candidates]
    minimum = min(costs)
    weights = [math.exp(-(cost - minimum) / 0.30) for cost in costs]
    return sum(weight * candidate for weight, candidate in zip(weights, candidates, strict=True)) / sum(weights), minimum


def oracle(controller_id: int) -> dict[str, object]:
    ep = [0.8, 0.6, 0.5]
    ev = [0.4, -0.4, 0.1]
    reference_acceleration = [0.05, -0.04, 0.02]
    limits = [4.0, 4.0, 2.5]
    increments = [1.2, 1.2, 0.8]
    robust = [0.25, 0.25, 0.20]
    tube_p = [0.35, 0.35, 0.45]
    tube_v = [0.18, 0.18, 0.25]
    adaptive_scale = 1.0 + 0.08 * sum(p * v for p, v in zip(ep, ev, strict=True)) * 0.02 / 3.0
    unconstrained: list[float] = []
    constrained: list[float] = []
    auxiliary: list[float] = []
    solver_cost = 0.0
    solver_iterations = 0
    saturated = False
    for axis in range(3):
        acceleration = linear_solution(ep[axis], ev[axis], 0.0, axis)
        limit = limits[axis]
        aux = 0.0
        if controller_id == 2:
            acceleration += robust[axis] * math.tanh(4.0 * (ep[axis] + 0.25 * ev[axis]))
            aux = robust[axis]
        elif controller_id == 3:
            acceleration *= adaptive_scale
            aux = adaptive_scale
        elif controller_id == 4:
            acceleration += tube_p[axis] * ep[axis] + tube_v[axis] * ev[axis]
            limit -= robust[axis]
            aux = limit
        elif controller_id == 5:
            schedule = clamp(abs(ep[axis]) / 0.75, 0.0, 1.0)
            acceleration += schedule * (tube_p[axis] * ep[axis] + tube_v[axis] * ev[axis])
            aux = schedule
        elif controller_id == 6:
            acceleration = ilqr_solution(ep[axis], ev[axis], acceleration, axis)
            solver_iterations = 5
        elif controller_id == 7:
            acceleration, cost = mppi_solution(ep[axis], ev[axis], acceleration, axis)
            solver_cost += cost
            solver_iterations = 7
        acceleration += reference_acceleration[axis]
        unconstrained.append(acceleration)
        bounded = clamp(acceleration, -limit, limit)
        bounded = clamp(bounded, -increments[axis], increments[axis])
        saturated |= abs(bounded - acceleration) > 1.0e-12
        constrained.append(bounded)
        auxiliary.append(aux)
        if controller_id != 7:
            solver_cost += stage_cost(ep[axis], ev[axis], bounded, axis)
    desired = constrained.copy()
    desired[2] += 9.80665
    return {
        "desired": desired,
        "unconstrained": unconstrained,
        "auxiliary": auxiliary,
        "adaptive_scale": adaptive_scale if controller_id == 3 else 1.0,
        "solver_cost": solver_cost,
        "solver_iterations": solver_iterations,
        "saturated": int(saturated),
    }


def body_z_from_quaternion(q: list[float]) -> list[float]:
    w, x, y, z = q
    return [2.0 * (x * z + w * y), 2.0 * (y * z - w * x), 1.0 - 2.0 * (x * x + y * y)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", default=str(ROOT / "Results/control_platform/p4_mpc_source_20260716"))
    args = parser.parse_args()
    result_dir = Path(args.result_dir).resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    executable = result_dir / "mpc_gate"
    command = [
        "gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic",
        wsl_path(SOURCE_DIR / "mpc_attitude_thrust_core.c"),
        wsl_path(SOURCE_DIR / "mpc_attitude_thrust_gate.c"),
        "-I", wsl_path(SOURCE_DIR), "-lm", "-o", wsl_path(executable),
    ]
    compile_process = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", " ".join(shlex.quote(part) for part in command)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    (result_dir / "compile.stdout.txt").write_text(compile_process.stdout, encoding="utf-8")
    (result_dir / "compile.stderr.txt").write_text(compile_process.stderr, encoding="utf-8")
    if compile_process.returncode:
        report = {"schema": "mosim.control_platform.p4_mpc_gate.v1", "status": "blocked", "stage": "compile"}
        (result_dir / "P4_MPC_SOURCE_GATE.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 1
    run = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", shlex.quote(wsl_path(executable))],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    executable.unlink(missing_ok=True)
    rows = [[float(value) for value in line.split(",")] for line in run.stdout.splitlines() if line and not line.startswith("L,")]
    lifecycle_rows = [line.split(",") for line in run.stdout.splitlines() if line.startswith("L,")]
    failures: list[dict[str, object]] = []
    maximum_difference = 0.0
    for row in rows:
        controller_id = int(row[0])
        expected = oracle(controller_id)
        actual_groups = {
            "desired": row[2:5], "unconstrained": row[5:8], "auxiliary": row[8:11],
        }
        for group, actual_values in actual_groups.items():
            for axis, (actual, wanted) in enumerate(zip(actual_values, expected[group], strict=True)):
                difference = abs(actual - wanted)
                maximum_difference = max(maximum_difference, difference)
                if difference > 1.0e-10:
                    failures.append({"controller_id": controller_id, "field": f"{group}_{axis}", "difference": difference})
        scalar_checks = {
            "solver_cost": (row[17], expected["solver_cost"]),
            "adaptive_scale": (row[18], expected["adaptive_scale"]),
        }
        for field, (actual, wanted) in scalar_checks.items():
            difference = abs(actual - wanted)
            maximum_difference = max(maximum_difference, difference)
            if difference > 1.0e-10:
                failures.append({"controller_id": controller_id, "field": field, "difference": difference})
        if int(row[19]) != expected["solver_iterations"] or int(row[20]) != expected["saturated"] or int(row[1]) != 0 or int(row[21]) != 0:
            failures.append({"controller_id": controller_id, "field": "status_or_diagnostics"})
        body_z = body_z_from_quaternion(row[11:15])
        desired = row[2:5]
        length = math.sqrt(sum(value * value for value in desired))
        for axis in range(3):
            difference = abs(body_z[axis] - desired[axis] / length)
            maximum_difference = max(maximum_difference, difference)
            if difference > 1.0e-10:
                failures.append({"controller_id": controller_id, "field": f"body_z_{axis}"})
    lifecycle_expected = {
        "disabled": (0, 1, 0.0), "invalid_input": (-3, -3, 0.0),
        "unknown_controller": (-2, -2, 0.0), "invalid_params": (-5, -5, 0.0),
    }
    lifecycle_checks: dict[str, dict[str, object]] = {}
    for row in lifecycle_rows:
        name, rc, status, value = row[1], int(row[2]), int(row[3]), float(row[4])
        if name in lifecycle_expected:
            wanted = lifecycle_expected[name]
            passed = (rc, status) == wanted[:2] and abs(value - wanted[2]) <= 1.0e-12
        elif name == "adaptive_continuity":
            passed = rc == 0 and status == 0 and 0.75 <= value <= 1.25
        else:
            passed = rc == 0 and status == 0 and abs(value - 1.0) <= 1.0e-12
        lifecycle_checks[name] = {"passed": passed, "return_code": rc, "status_code": status, "value": value}
        if not passed:
            failures.append({"lifecycle_case": name})
    report = {
        "schema": "mosim.control_platform.p4_mpc_gate.v1",
        "status": "passed" if run.returncode == 0 and len(rows) == 7 and len(lifecycle_checks) == 6 and not failures else "failed",
        "controllers": list(CONTROLLERS.values()),
        "case_count": len(rows),
        "lifecycle_case_count": len(lifecycle_checks),
        "lifecycle_checks": lifecycle_checks,
        "maximum_abs_difference": maximum_difference,
        "failure_count": len(failures),
        "failures": failures[:30],
        "command_contract": "ATTITUDE_THRUST",
        "runtime_started": False,
        "fixed_budget": {"ilqr_iterations": 5, "mppi_samples": 7},
        "external_gate_decisions": {
            "learning_mpc": {
                "decision": "deferred", "selectable": False,
                "reason": "No frozen learned dynamics or terminal-cost artifact, dataset hash, or independent safety benchmark exists.",
            },
            "distributed_mpc": {
                "decision": "deferred_external_gate", "selectable": False,
                "reason": "Meaningful acceptance requires synchronized multi-UAV state exchange and the shared formation runtime.",
            },
        },
        "claim_ceiling": "Seven fixed-size deterministic MPC-family cores pass independent numerical and lifecycle checks. MWORKS, generated C/SIL, timing, and Gazebo runtime remain pending.",
    }
    (result_dir / "P4_MPC_SOURCE_GATE.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
