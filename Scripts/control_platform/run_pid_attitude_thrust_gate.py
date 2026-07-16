#!/usr/bin/env python3
"""Compile and exercise the six PID ATTITUDE_THRUST contracts in WSL."""

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
    return r'''#include "pid_attitude_thrust_core.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

static void run_case(int algorithm, int dynamic) {
  MosimPidAttitudeThrustParams p;
  MosimPidAttitudeThrustState s = {0};
  MosimPidAttitudeThrustInput i = {0};
  MosimPidAttitudeThrustOutput o;
  mosim_pid_attitude_thrust_default_params(algorithm, &p);
  i.algorithm_id = algorithm; i.dt = 0.01; i.enable = 1; i.reset = 1;
  i.attitude_enu_flu_wxyz.w = 1.0;
  if (dynamic) {
    i.reference_position_enu_m.x = 1.0; i.reference_position_enu_m.y = -0.5; i.reference_position_enu_m.z = 0.8;
    i.reference_velocity_enu_mps.x = 0.2; i.reference_velocity_enu_mps.y = -0.1;
    i.reference_acceleration_enu_mps2.x = 0.6; i.reference_acceleration_enu_mps2.y = -0.3; i.reference_acceleration_enu_mps2.z = 0.2;
    i.reference_yaw_enu_rad = 0.3;
    i.schedule.x = 0.5; i.schedule.y = 0.4; i.schedule.z = 0.3;
    i.fuzzy_error.x = 0.4; i.fuzzy_error.y = -0.3; i.fuzzy_error.z = 0.2;
    i.neural_residual.x = 0.1; i.neural_residual.y = -0.2; i.neural_residual.z = 0.3;
  }
  mosim_pid_attitude_thrust_step(&p, &s, &i, &o);
  printf("case,%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d,%d,%.17g\n",
    algorithm, dynamic, o.desired_attitude_enu_flu_wxyz.w, o.desired_attitude_enu_flu_wxyz.x,
    o.desired_attitude_enu_flu_wxyz.y, o.desired_attitude_enu_flu_wxyz.z,
    o.desired_collective_thrust_n, o.desired_acceleration_enu_mps2.x,
    o.desired_acceleration_enu_mps2.y, o.desired_acceleration_enu_mps2.z,
    o.status_code, o.saturated, o.scheduled_gain.x);
}

int main(void) {
  int algorithm;
  MosimPidAttitudeThrustParams p;
  MosimPidAttitudeThrustState s = {0};
  MosimPidAttitudeThrustInput i = {0};
  MosimPidAttitudeThrustOutput first, second, reset, disabled, invalid, mismatch;
  for (algorithm = 1; algorithm <= 6; ++algorithm) { run_case(algorithm, 0); run_case(algorithm, 1); }
  mosim_pid_attitude_thrust_default_params(1, &p);
  i.algorithm_id=1; i.dt=0.01; i.enable=1; i.attitude_enu_flu_wxyz.w=1.0; i.reference_position_enu_m.x=1.0;
  mosim_pid_attitude_thrust_step(&p,&s,&i,&first);
  mosim_pid_attitude_thrust_step(&p,&s,&i,&second);
  i.reset=1; mosim_pid_attitude_thrust_step(&p,&s,&i,&reset);
  i.reset=0; i.enable=0; mosim_pid_attitude_thrust_step(&p,&s,&i,&disabled);
  i.enable=1; i.dt=0.0; mosim_pid_attitude_thrust_step(&p,&s,&i,&invalid);
  i.dt=0.01; p.algorithm_id=2; mosim_pid_attitude_thrust_step(&p,&s,&i,&mismatch);
  printf("lifecycle,%.17g,%.17g,%.17g,%d,%.17g,%d,%.17g,%d,%.17g\n", first.desired_collective_thrust_n,
    second.desired_collective_thrust_n, reset.desired_collective_thrust_n, disabled.status_code,
    disabled.desired_collective_thrust_n, invalid.status_code, invalid.desired_collective_thrust_n,
    mismatch.status_code, mismatch.desired_collective_thrust_n);
  return 0;
}
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", type=Path, default=ROOT / "Results/control_platform/p1_pid_attitude_thrust_20260716")
    args = parser.parse_args()
    result_dir = args.result_dir.resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    runner = result_dir / "pid_attitude_thrust_gate.c"
    binary = result_dir / "pid_attitude_thrust_gate"
    write_lf(runner, runner_source())
    compile_parts = [
        "gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-Werror", "-pedantic",
        wsl_path(runner), wsl_path(SOURCE_DIR / "pid_unified_core.c"),
        wsl_path(SOURCE_DIR / "pid_attitude_thrust_core.c"), "-I", wsl_path(SOURCE_DIR),
        "-lm", "-o", wsl_path(binary),
    ]
    compile_proc = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", " ".join(map(shlex.quote, compile_parts))],
        cwd=ROOT, capture_output=True, text=True,
    )
    write_lf(result_dir / "compile.stdout.txt", compile_proc.stdout)
    write_lf(result_dir / "compile.stderr.txt", compile_proc.stderr)
    if compile_proc.returncode:
        report = {"schema": "mosim.pid_attitude_thrust_gate.v1", "status": "blocked", "stage": "compile", "returncode": compile_proc.returncode}
        write_lf(result_dir / "PID_ATTITUDE_THRUST_GATE.json", json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return 1
    run_proc = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", shlex.quote(wsl_path(binary))],
        cwd=ROOT, capture_output=True, text=True,
    )
    write_lf(result_dir / "run.stdout.txt", run_proc.stdout)
    write_lf(result_dir / "run.stderr.txt", run_proc.stderr)
    binary.unlink(missing_ok=True)
    rows = [line.split(",") for line in run_proc.stdout.splitlines() if line]
    case_rows = [row for row in rows if row[0] == "case"]
    lifecycle = next((row for row in rows if row[0] == "lifecycle"), None)
    failures: list[str] = []
    hover_thrust_errors: list[float] = []
    max_quaternion_norm_error = 0.0
    dynamic_signatures: list[tuple[float, ...]] = []
    for row in case_rows:
        algorithm, dynamic = int(row[1]), int(row[2])
        q = tuple(float(value) for value in row[3:7])
        thrust = float(row[7])
        acceleration = tuple(float(value) for value in row[8:11])
        status, saturated = int(row[11]), int(row[12])
        gain = float(row[13])
        norm_error = abs(math.sqrt(sum(value * value for value in q)) - 1.0)
        max_quaternion_norm_error = max(max_quaternion_norm_error, norm_error)
        if status != 0 or not all(math.isfinite(value) for value in (*q, thrust, *acceleration, gain)):
            failures.append(f"algorithm {algorithm} dynamic={dynamic}: invalid finite/status contract")
        if dynamic == 0:
            hover_thrust_errors.append(abs(thrust - 9.80665))
            if max(abs(q[0] - 1.0), abs(q[1]), abs(q[2]), abs(q[3])) > 1e-12:
                failures.append(f"algorithm {algorithm}: hover attitude is not identity")
        else:
            dynamic_signatures.append((round(thrust, 12), round(acceleration[0], 12), round(acceleration[1], 12), round(gain, 12)))
            tilt = math.atan2(math.hypot(acceleration[0], acceleration[1]), acceleration[2])
            if tilt > math.radians(30.0) + 1e-12:
                failures.append(f"algorithm {algorithm}: tilt limit exceeded")
            if thrust < 0.0 or thrust > 19.6133 + 1e-12:
                failures.append(f"algorithm {algorithm}: physical thrust limit exceeded")
            if saturated not in (0, 1):
                failures.append(f"algorithm {algorithm}: invalid saturation flag")
    lifecycle_ok = False
    if lifecycle is not None:
        first, second, reset = map(float, lifecycle[1:4])
        disabled_status, disabled_thrust = int(lifecycle[4]), float(lifecycle[5])
        invalid_status, invalid_thrust = int(lifecycle[6]), float(lifecycle[7])
        mismatch_status, mismatch_thrust = int(lifecycle[8]), float(lifecycle[9])
        lifecycle_ok = (
            abs(first - reset) <= 1e-12
            and disabled_status == 1 and disabled_thrust == 0.0
            and invalid_status == -1 and invalid_thrust == 0.0
            and mismatch_status == -1 and mismatch_thrust == 0.0
        )
    if not lifecycle_ok:
        failures.append("reset/disable/invalid-input fail-closed contract failed")
    if len(set(dynamic_signatures)) < 4:
        failures.append("configured PID variants did not produce distinct bounded signatures")
    report = {
        "schema": "mosim.pid_attitude_thrust_gate.v1",
        "status": "passed" if run_proc.returncode == 0 and len(case_rows) == 12 and not failures else "failed",
        "algorithms": ["cascade_pid", "gain_scheduled_pid", "fuzzy_pid", "neural_pid", "anti_windup", "feedforward_profile"],
        "case_count": len(case_rows),
        "hover_max_collective_thrust_error_n": max(hover_thrust_errors, default=math.inf),
        "max_quaternion_norm_error": max_quaternion_norm_error,
        "distinct_dynamic_signature_count": len(set(dynamic_signatures)),
        "lifecycle_fail_closed": lifecycle_ok,
        "failure_count": len(failures),
        "failures": failures,
        "frame_contract": {"world": "ENU", "body": "FLU", "quaternion_order": "wxyz", "thrust_unit": "N"},
        "runtime_started": False,
        "shared_gazebo_px4_touched": False,
        "claim_ceiling": "Fixed-size project C core compile/runtime golden evidence for six ATTITUDE_THRUST contracts; no MWORKS full-contract codegen or Gazebo/PX4/MAVROS runtime is claimed.",
    }
    write_lf(result_dir / "PID_ATTITUDE_THRUST_GATE.json", json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
