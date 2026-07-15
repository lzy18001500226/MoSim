#!/usr/bin/env python3
"""Compile the frozen-hover H-infinity core and compare with a JSON gain oracle."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(__file__).resolve().parent
GAIN_PATH = ROOT / "Config" / "control_platform" / "hinf_hover_frozen_gain.json"


def wsl_path(path: Path) -> str:
    path = path.resolve()
    return f"/mnt/{path.drive[0].lower()}/{path.relative_to(path.anchor).as_posix()}"


def clamp(value: float, lower: float, upper: float) -> tuple[float, bool]:
    bounded = max(lower, min(upper, value))
    return bounded, bounded != value


def expected_rows(gain_data: dict) -> list[list[float]]:
    cases = [
        ([0.0] * 12, [0.0] * 12, 1),
        ([0.001, -0.001, 0.002, 0.01, -0.02, 0.005,
          0.01, -0.01, 0.02, 0.001, -0.002, 0.005], [0.0] * 12, 1),
        ([0.1, -0.1, 0.2, 0.5, -0.5, 0.2,
          0.5, -0.5, 0.5, 0.2, -0.2, 0.3], [0.0] * 12, 1),
        ([0.0] * 12, [0.0] * 12, 0),
    ]
    rows: list[list[float]] = []
    for case_id, (state, reference, enabled) in enumerate(cases):
        if not enabled:
            rows.append([float(case_id), 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 3.0])
            continue
        wrench = [gain_data["mass_kg"] * gain_data["gravity_mps2"], 0.0, 0.0, 0.0]
        for command in range(4):
            wrench[command] += sum(
                gain_data["gain"][command][index] * (state[index] - reference[index])
                for index in range(12)
            )
        saturated = False
        wrench[0], clipped = clamp(wrench[0], *gain_data["force_limits_n"])
        saturated |= clipped
        for command in range(1, 4):
            wrench[command], clipped = clamp(
                wrench[command], -gain_data["torque_limit_nm"], gain_data["torque_limit_nm"]
            )
            saturated |= clipped
        rows.append([float(case_id), *wrench, float(saturated), 0.0, 3.0])
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", default=str(
        ROOT / "Results" / "control_platform" / "g5_wave_b_hinf_20260716"))
    args = parser.parse_args()
    result_dir = Path(args.result_dir).resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    exe = result_dir / "wave_b_hinf_gate"
    compile_cmd = [
        "gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic",
        wsl_path(SOURCE_DIR / "wave_b_hinf_core.c"),
        wsl_path(SOURCE_DIR / "wave_b_hinf_gate.c"),
        "-I", wsl_path(SOURCE_DIR), "-lm", "-o", wsl_path(exe),
    ]
    compile = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc",
         " ".join(shlex.quote(part) for part in compile_cmd)],
        capture_output=True, text=True,
    )
    (result_dir / "compile.stdout.txt").write_text(compile.stdout, encoding="utf-8", newline="\n")
    (result_dir / "compile.stderr.txt").write_text(compile.stderr, encoding="utf-8", newline="\n")
    report_path = result_dir / "G5_WAVE_B_HINF_GATE.json"
    if compile.returncode:
        report_path.write_text(json.dumps({"status": "blocked", "stage": "compile"}, indent=2) + "\n", encoding="utf-8")
        return 1
    run = subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", shlex.quote(wsl_path(exe))],
        capture_output=True, text=True,
    )
    exe.unlink(missing_ok=True)
    actual = [[float(value) for value in line.split(",")] for line in run.stdout.splitlines() if line.strip()]
    gain_data = json.loads(GAIN_PATH.read_text(encoding="utf-8"))
    expected = expected_rows(gain_data)
    failures = []
    for row_index, (got_row, expected_row) in enumerate(zip(actual, expected)):
        for column_index, (got, wanted) in enumerate(zip(got_row, expected_row)):
            if abs(got - wanted) > 1.0e-10:
                failures.append({"row": row_index, "column": column_index,
                                 "actual": got, "expected": wanted, "diff": abs(got - wanted)})
    if len(actual) != len(expected):
        failures.append({"row_count_actual": len(actual), "row_count_expected": len(expected)})
    report = {
        "schema": "mosim.control_platform.g5_wave_b_hinf_gate.v1",
        "status": "passed" if run.returncode == 0 and not failures else "failed",
        "controller": "hinf_hover_wrench",
        "upstream_commit": gain_data["upstream_commit"],
        "gamma": gain_data["gamma"],
        "riccati_residual": gain_data["riccati_residual"],
        "max_closed_loop_real_eigenvalue": gain_data["max_closed_loop_real_eigenvalue"],
        "case_count": len(expected),
        "scalar_comparison_count": len(expected) * len(expected[0]),
        "failure_count": len(failures),
        "runtime_started": False,
        "shared_gazebo_px4_touched": False,
        "selectable": False,
        "claim_ceiling": gain_data["claim_ceiling"],
        "failures": failures,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
