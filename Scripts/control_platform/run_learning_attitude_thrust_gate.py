#!/usr/bin/env python3
"""Compile and exercise the bounded learning ATTITUDE_THRUST controller core."""

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


def write_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)


def runner_source() -> str:
    return r'''#include "learning_attitude_thrust_core.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

static MosimLearningAttitudeThrustInput base_input(int mode) {
  MosimLearningAttitudeThrustInput input;
  memset(&input, 0, sizeof(input));
  input.mode = mode; input.dt = 0.01; input.enable = 1; input.learning_enable = 1;
  input.mass_kg = 0.67; input.gravity_mps2 = 9.80665; input.hover_percentage = 0.294;
  input.max_tilt_rad = 0.5235987755982988;
  input.min_collective_thrust_n = 0.0; input.max_collective_thrust_n = 22.35;
  input.attitude_enu_flu_wxyz.w = 1.0;
  input.position_enu_m.x = 0.2; input.position_enu_m.y = -0.1; input.position_enu_m.z = 0.7;
  input.velocity_enu_mps.x = -0.3; input.velocity_enu_mps.y = 0.2; input.velocity_enu_mps.z = -0.1;
  input.reference_position_enu_m.x = 1.0; input.reference_position_enu_m.y = 0.5; input.reference_position_enu_m.z = 1.2;
  input.reference_velocity_enu_mps.x = 0.1; input.reference_velocity_enu_mps.y = -0.2;
  input.reference_acceleration_enu_mps2.x = 0.05; input.reference_acceleration_enu_mps2.y = -0.04;
  input.reference_acceleration_enu_mps2.z = 0.02; input.reference_yaw_enu_rad = 0.3;
  return input;
}

static void print_case(const char *name, int result, const MosimLearningAttitudeThrustOutput *o) {
  printf("case,%s,%d,%d,%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
    name, result, o->status_code, o->fallback_active, o->mode,
    o->learning.values[0], o->learning.values[1], o->learning.values[2],
    o->control.desired_acceleration_enu_mps2.x, o->control.desired_acceleration_enu_mps2.y,
    o->control.desired_acceleration_enu_mps2.z, o->control.desired_collective_thrust_n,
    o->normalized_thrust, o->control.scheduled_gain.x);
}

int main(void) {
  MosimLearningAttitudeThrustState state = {0}, fresh = {0};
  MosimLearningAttitudeThrustInput input;
  MosimLearningAttitudeThrustOutput output;
  int result;
  input = base_input(MOSIM_LEARNING_NEURAL_RESIDUAL);
  result = mosim_learning_attitude_thrust_step(&state, &input, &output); print_case("neural", result, &output);
  input = base_input(MOSIM_LEARNING_RL_GAIN_SCHEDULER);
  result = mosim_learning_attitude_thrust_step(&state, &input, &output); print_case("rl", result, &output);
  input = base_input(MOSIM_LEARNING_NEURAL_RESIDUAL); input.learning_enable = 0;
  result = mosim_learning_attitude_thrust_step(&fresh, &input, &output); print_case("learning_disabled", result, &output);
  input = base_input(MOSIM_LEARNING_NEURAL_RESIDUAL); input.reset = 1;
  result = mosim_learning_attitude_thrust_step(&state, &input, &output); print_case("reset", result, &output);
  input = base_input(MOSIM_LEARNING_NEURAL_RESIDUAL); input.reference_position_enu_m.x = NAN;
  result = mosim_learning_attitude_thrust_step(&fresh, &input, &output); print_case("nan_fail_closed", result, &output);
  return 0;
}
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--result-dir",
        type=Path,
        default=ROOT / "Results/control_platform/p9_learning_attitude_thrust_gate_20260717",
    )
    args = parser.parse_args()
    result_dir = args.result_dir.resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    runner = result_dir / "learning_attitude_thrust_gate.c"
    binary = result_dir / "learning_attitude_thrust_gate"
    write_lf(runner, runner_source())
    sources = [
        runner,
        SOURCE_DIR / "pid_unified_core.c",
        SOURCE_DIR / "pid_attitude_thrust_core.c",
        SOURCE_DIR / "learning_control_core.c",
        SOURCE_DIR / "learning_attitude_thrust_core.c",
    ]
    compile_parts = [
        "gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-Werror", "-pedantic",
        *(wsl_path(path) for path in sources), "-I", wsl_path(SOURCE_DIR),
        "-lm", "-o", wsl_path(binary),
    ]
    compile_proc = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", " ".join(map(shlex.quote, compile_parts))],
        cwd=ROOT, capture_output=True, text=True,
    )
    write_lf(result_dir / "compile.stdout.txt", compile_proc.stdout)
    write_lf(result_dir / "compile.stderr.txt", compile_proc.stderr)
    if compile_proc.returncode:
        report = {"schema": "mosim.learning_attitude_thrust_gate.v1", "status": "blocked", "stage": "compile"}
        write_lf(result_dir / "P9_LEARNING_ATTITUDE_THRUST_GATE.json", json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return 1
    run_proc = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", shlex.quote(wsl_path(binary))],
        cwd=ROOT, capture_output=True, text=True,
    )
    write_lf(result_dir / "run.stdout.txt", run_proc.stdout)
    write_lf(result_dir / "run.stderr.txt", run_proc.stderr)
    binary.unlink(missing_ok=True)
    rows = {row[1]: row for row in (line.split(",") for line in run_proc.stdout.splitlines()) if row[0] == "case"}
    failures: list[str] = []
    required = {"neural", "rl", "learning_disabled", "reset", "nan_fail_closed"}
    if set(rows) != required:
        failures.append(f"case set mismatch: {sorted(rows)}")
    parsed: dict[str, dict[str, float | int]] = {}
    for name, row in rows.items():
        values = [float(value) for value in row[6:15]]
        parsed[name] = {
            "result": int(row[2]), "status_code": int(row[3]), "fallback_active": int(row[4]),
            "mode": int(row[5]), "action_x": values[0], "action_y": values[1], "action_z": values[2],
            "acceleration_x": values[3], "acceleration_y": values[4], "acceleration_z": values[5],
            "collective_thrust_n": values[6], "normalized_thrust": values[7],
            "scheduled_gain_x": values[8],
        }
        if not all(math.isfinite(value) for value in values):
            failures.append(f"{name}: non-finite output")
    if parsed:
        neural = parsed.get("neural", {})
        rl = parsed.get("rl", {})
        disabled = parsed.get("learning_disabled", {})
        reset = parsed.get("reset", {})
        nan_case = parsed.get("nan_fail_closed", {})
        if neural.get("result") != 0 or neural.get("fallback_active") != 0:
            failures.append("neural residual did not execute")
        if any(abs(float(neural.get(key, 99.0))) > 0.6 + 1e-12 for key in ("action_x", "action_y", "action_z")):
            failures.append("neural residual exceeded bound")
        if rl.get("result") != 0 or rl.get("fallback_active") != 0:
            failures.append("RL gain scheduler did not execute")
        if any(not 0.0 <= float(rl.get(key, -1.0)) <= 0.25 + 1e-12 for key in ("action_x", "action_y", "action_z")):
            failures.append("RL schedule exceeded [0, 0.25]")
        if disabled.get("result") != 0 or disabled.get("fallback_active") != 1:
            failures.append("learning-disable did not select Cascade PID fallback")
        if any(float(disabled.get(key, 1.0)) != 0.0 for key in ("action_x", "action_y", "action_z")):
            failures.append("learning-disable did not zero the enhancement")
        if reset.get("result") != 0 or reset.get("fallback_active") != 0:
            failures.append("reset did not preserve valid neural execution")
        if nan_case.get("result") != -1 or nan_case.get("fallback_active") != 1:
            failures.append("NaN input did not fail closed")
    report = {
        "schema": "mosim.learning_attitude_thrust_gate.v1",
        "status": "passed" if run_proc.returncode == 0 and not failures else "failed",
        "artifact_sha256": "4d480c6ad4738da75b4f7bfdf824658b7878ea511a52935ed2be4fff0d043e45",
        "cases": parsed,
        "failures": failures,
        "fallback_contract": "learning disabled -> active Cascade PID; invalid controller state -> fail closed",
        "runtime_started": False,
        "shared_gazebo_px4_touched": False,
        "claim_ceiling": "Compiled fixed-size C behavior gate only; no MWORKS or Gazebo runtime claim.",
    }
    write_lf(result_dir / "P9_LEARNING_ATTITUDE_THRUST_GATE.json", json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
