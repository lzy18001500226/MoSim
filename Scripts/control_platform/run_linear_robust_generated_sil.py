#!/usr/bin/env python3
"""Compile MWORKS-generated P2 C and compare it with the project source core."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "Scripts/control_platform"
INPUT_VALUES = {
    "dt": 0.02,
    "position_x": 0.2, "position_y": -0.1, "position_z": 0.7,
    "velocity_x": -0.3, "velocity_y": 0.2, "velocity_z": -0.1,
    "reference_position_x": 1.0, "reference_position_y": 0.5, "reference_position_z": 1.2,
    "reference_velocity_x": 0.1, "reference_velocity_y": -0.2, "reference_velocity_z": 0.0,
    "reference_acceleration_x": 0.05, "reference_acceleration_y": -0.04, "reference_acceleration_z": 0.02,
    "reference_yaw": 0.3,
    "mass_kg": 0.67, "gravity_mps2": 9.80665, "hover_percentage": 0.291,
    "max_tilt_rad": 0.5235987755982988,
    "min_collective_thrust_n": 0.0, "max_collective_thrust_n": 16.0,
    "enable": 1.0, "reset": 1.0,
}
OUTPUT_FIELDS = [
    "desired_acceleration_x", "desired_acceleration_y", "desired_acceleration_z",
    "desired_attitude_w", "desired_attitude_x", "desired_attitude_y", "desired_attitude_z",
    "normalized_thrust", "collective_thrust_n",
    "estimated_position_x", "estimated_position_y", "estimated_position_z",
    "estimated_velocity_x", "estimated_velocity_y", "estimated_velocity_z",
    "adaptive_disturbance_x", "adaptive_disturbance_y", "adaptive_disturbance_z",
    "storage_function", "saturated", "status_code",
]


def wsl_path(path: Path) -> str:
    resolved = path.resolve()
    return f"/mnt/{resolved.drive[0].lower()}/{resolved.relative_to(resolved.anchor).as_posix()}"


def run_wsl(command: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", " ".join(shlex.quote(part) for part in command)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def generated_harness(private_header: str, public_header: str) -> str:
    input_match = re.search(r"extern struct\s+\w+\s+(\w+);", public_header)
    output_match = re.search(r"extern struct\s+\w+\s+(\w+);", public_header[input_match.end():] if input_match else "")
    if input_match is None or output_match is None:
        raise RuntimeError("cannot resolve generated input/output globals")
    input_global = input_match.group(1)
    output_global = output_match.group(1)
    assignments = [f"    {input_global}.controller_id_in = (double)id;"]
    assignments.extend(f"    {input_global}.{name}_in = {value:.17g};" for name, value in INPUT_VALUES.items())
    output_args = ",\n        ".join(f"{output_global}.{name}_out" for name in OUTPUT_FIELDS)
    return f'''#include <stdio.h>
#include "MoSim_P2_LinearRobust_CFunction_Sysblock.h"
#include "MoSim_P2_LinearRobust_CFunction_Sysblock_private.h"

static void print_case(int id)
{{
{chr(10).join(assignments)}
    Init();
    Step();
    printf("%d,0,"
        "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
        "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
        "%.17g,%.17g,%.17g\\n",
        id,
        {output_args});
}}

int main(void)
{{
    print_case(1); print_case(2); print_case(3); print_case(4);
    return 0;
}}
'''


def parse_rows(stdout: str) -> dict[int, list[float]]:
    rows: dict[int, list[float]] = {}
    for line in stdout.splitlines():
        if not line.strip() or line.startswith("L,"):
            continue
        values = [float(item) for item in line.split(",")]
        rows[int(values[0])] = values[1:]
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--generated-dir",
        type=Path,
        default=ROOT / "Results/control_platform/p2_linear_robust_mworks_20260716/generated_c/MoSim_P2_LinearRobust_CFunction_Sysblock",
    )
    parser.add_argument(
        "--result-dir",
        type=Path,
        default=ROOT / "Results/control_platform/p2_linear_robust_mworks_20260716/sil",
    )
    args = parser.parse_args()
    generated_dir = args.generated_dir.resolve()
    result_dir = args.result_dir.resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    source_exe = result_dir / "source_gate"
    generated_exe = result_dir / "generated_gate"
    harness_path = result_dir / "generated_sil_harness.c"
    public_header = (generated_dir / "MoSim_P2_LinearRobust_CFunction_Sysblock.h").read_text(encoding="utf-8")
    private_header = (generated_dir / "MoSim_P2_LinearRobust_CFunction_Sysblock_private.h").read_text(encoding="utf-8")
    harness_path.write_text(generated_harness(private_header, public_header), encoding="utf-8", newline="\n")

    source_compile = run_wsl([
        "gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic",
        wsl_path(SOURCE_DIR / "linear_robust_attitude_thrust_core.c"),
        wsl_path(SOURCE_DIR / "linear_robust_attitude_thrust_gate.c"),
        "-I", wsl_path(SOURCE_DIR), "-lm", "-o", wsl_path(source_exe),
    ])
    generated_compile = run_wsl([
        "gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic",
        wsl_path(generated_dir / "MoSim_P2_LinearRobust_CFunction_Sysblock.c"),
        wsl_path(generated_dir / "MoSim_P2_LinearRobust_CFunction_Sysblock_data.c"),
        wsl_path(generated_dir / "extern_inc/momodel_extern_ince1.c"),
        wsl_path(harness_path),
        "-I", wsl_path(generated_dir), "-I", wsl_path(generated_dir / "extern_inc"),
        "-lm", "-o", wsl_path(generated_exe),
    ])
    (result_dir / "source_compile.stderr.txt").write_text(source_compile.stderr, encoding="utf-8")
    (result_dir / "generated_compile.stderr.txt").write_text(generated_compile.stderr, encoding="utf-8")
    if source_compile.returncode or generated_compile.returncode:
        report = {
            "schema": "mosim.control_platform.p2_generated_sil.v1",
            "status": "blocked",
            "stage": "compile",
            "source_return_code": source_compile.returncode,
            "generated_return_code": generated_compile.returncode,
        }
        (result_dir / "P2_GENERATED_SIL_EQUIVALENCE.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 1

    source_run = run_wsl([wsl_path(source_exe)])
    generated_run = run_wsl([wsl_path(generated_exe)])
    source_exe.unlink(missing_ok=True)
    generated_exe.unlink(missing_ok=True)
    source_rows = parse_rows(source_run.stdout)
    generated_rows = parse_rows(generated_run.stdout)
    tolerance = 1.0e-12
    failures: list[dict] = []
    max_difference = 0.0
    for controller_id in range(1, 5):
        source = source_rows.get(controller_id)
        generated = generated_rows.get(controller_id)
        if source is None or generated is None or len(source) != len(generated):
            failures.append({"controller_id": controller_id, "reason": "missing_or_mismatched_row"})
            continue
        for index, (expected, actual) in enumerate(zip(source, generated, strict=True)):
            difference = abs(expected - actual)
            max_difference = max(max_difference, difference)
            if difference > tolerance:
                failures.append({"controller_id": controller_id, "column": index, "expected": expected, "actual": actual, "difference": difference})
    report = {
        "schema": "mosim.control_platform.p2_generated_sil.v1",
        "status": "passed" if not failures and source_run.returncode == 0 and generated_run.returncode == 0 else "failed",
        "controllers": ["lqg", "feedback_linearization", "passivity_based_control", "adaptive_backstepping"],
        "controller_count": len(generated_rows),
        "compared_columns_per_controller": len(next(iter(generated_rows.values()), [])),
        "max_abs_difference": max_difference,
        "tolerance": tolerance,
        "official_codegen": "MWORKS GenerateModelCode",
        "failure_count": len(failures),
        "failures": failures[:30],
        "claim_ceiling": "Official MWORKS-generated C is numerically equivalent to the project source core for four deterministic controller cases; Gazebo runtime and graphical Sysblock equivalence remain separate gates.",
    }
    (result_dir / "P2_GENERATED_SIL_EQUIVALENCE.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
