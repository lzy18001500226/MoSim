#!/usr/bin/env python3
"""Compare P9 project C with official MWORKS-generated C."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "Scripts/control_platform"
MODEL = "MoSim_P9_Learning_AttitudeThrust_CFunction_Sysblock"
ROUTES = ["trained_neural_residual", "rl_gain_scheduler"]
INPUT_VALUES = {
    "dt": 0.01,
    "position_x": 0.2, "position_y": -0.1, "position_z": 0.7,
    "velocity_x": -0.3, "velocity_y": 0.2, "velocity_z": -0.1,
    "attitude_w": 1.0, "attitude_x": 0.0, "attitude_y": 0.0, "attitude_z": 0.0,
    "angular_velocity_x": 0.0, "angular_velocity_y": 0.0, "angular_velocity_z": 0.0,
    "reference_position_x": 1.0, "reference_position_y": 0.5, "reference_position_z": 1.2,
    "reference_velocity_x": 0.1, "reference_velocity_y": -0.2, "reference_velocity_z": 0.0,
    "reference_acceleration_x": 0.05, "reference_acceleration_y": -0.04,
    "reference_acceleration_z": 0.02, "reference_yaw": 0.3,
    "mass_kg": 1.0, "gravity_mps2": 9.80665, "hover_percentage": 0.37,
    "max_tilt_rad": 0.5235987755982988,
    "min_collective_thrust_n": 0.0, "max_collective_thrust_n": 22.35,
    "enable": 1.0, "learning_enable": 1.0, "reset": 1.0,
}
OUTPUT_FIELDS = [
    "desired_attitude_w", "desired_attitude_x", "desired_attitude_y", "desired_attitude_z",
    "desired_collective_thrust_n",
    "normalized_thrust",
    "desired_acceleration_x", "desired_acceleration_y", "desired_acceleration_z",
    "learning_action_x", "learning_action_y", "learning_action_z",
    "scheduled_gain_x", "scheduled_gain_y", "scheduled_gain_z",
    "fallback_active", "status_code", "mode_out",
]


def wsl_path(path: Path) -> str:
    resolved = path.resolve()
    return f"/mnt/{resolved.drive[0].lower()}/{resolved.relative_to(resolved.anchor).as_posix()}"


def run_wsl(command: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", " ".join(shlex.quote(part) for part in command)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, check=False,
    )


def source_harness() -> str:
    outputs = [
        "out.control.desired_attitude_enu_flu_wxyz.w", "out.control.desired_attitude_enu_flu_wxyz.x",
        "out.control.desired_attitude_enu_flu_wxyz.y", "out.control.desired_attitude_enu_flu_wxyz.z",
        "out.control.desired_collective_thrust_n",
        "out.normalized_thrust",
        "out.control.desired_acceleration_enu_mps2.x", "out.control.desired_acceleration_enu_mps2.y",
        "out.control.desired_acceleration_enu_mps2.z",
        "out.learning.values[0]", "out.learning.values[1]", "out.learning.values[2]",
        "out.control.scheduled_gain.x", "out.control.scheduled_gain.y", "out.control.scheduled_gain.z",
        "(double)out.fallback_active", "(double)out.status_code", "(double)out.mode",
    ]
    return f'''#include <stdio.h>
#include <string.h>
#include "learning_attitude_thrust_core.h"
static void print_case(int mode) {{
    MosimLearningAttitudeThrustState state; MosimLearningAttitudeThrustInput in;
    MosimLearningAttitudeThrustOutput out; int result;
    memset(&state,0,sizeof(state)); memset(&in,0,sizeof(in));
    in.mode=mode; in.dt=0.01; in.enable=1; in.learning_enable=1; in.reset=1;
    in.mass_kg=1.0; in.gravity_mps2=9.80665; in.hover_percentage=0.37;
    in.max_tilt_rad=0.5235987755982988;
    in.min_collective_thrust_n=0.0; in.max_collective_thrust_n=22.35;
    in.position_enu_m.x=0.2; in.position_enu_m.y=-0.1; in.position_enu_m.z=0.7;
    in.velocity_enu_mps.x=-0.3; in.velocity_enu_mps.y=0.2; in.velocity_enu_mps.z=-0.1;
    in.attitude_enu_flu_wxyz.w=1.0;
    in.reference_position_enu_m.x=1.0; in.reference_position_enu_m.y=0.5; in.reference_position_enu_m.z=1.2;
    in.reference_velocity_enu_mps.x=0.1; in.reference_velocity_enu_mps.y=-0.2;
    in.reference_acceleration_enu_mps2.x=0.05; in.reference_acceleration_enu_mps2.y=-0.04;
    in.reference_acceleration_enu_mps2.z=0.02; in.reference_yaw_enu_rad=0.3;
    result=mosim_learning_attitude_thrust_step(&state,&in,&out);
    printf("%d,%d," "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
           "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\\n",
           mode,result,{','.join(outputs)});
}}
int main(void) {{ print_case(1); print_case(2); return 0; }}
'''


def generated_harness(public_header: str) -> str:
    globals_found = re.findall(r"extern struct\s+\w+\s+(\w+);", public_header)
    if len(globals_found) < 2:
        raise RuntimeError("cannot resolve generated input/output globals")
    input_global, output_global = globals_found[:2]
    assignments = [f"    {input_global}.mode_in=(double)mode;"]
    assignments.extend(f"    {input_global}.{name}_in={value:.17g};" for name, value in INPUT_VALUES.items())
    outputs = ",".join(f"{output_global}.{name}_out" for name in OUTPUT_FIELDS)
    return f'''#include <stdio.h>
#include "{MODEL}.h"
#include "{MODEL}_private.h"
static void print_case(int mode) {{
{chr(10).join(assignments)}
    Init(); Step();
    printf("%d,%d," "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
           "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\\n",
           mode,0,{outputs});
}}
int main(void) {{ print_case(1); print_case(2); return 0; }}
'''


def parse_rows(stdout: str) -> dict[int, list[float]]:
    rows: dict[int, list[float]] = {}
    for line in stdout.splitlines():
        if line.strip():
            values = [float(item) for item in line.split(",")]
            rows[int(values[0])] = values[1:]
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--generated-dir", type=Path,
        default=ROOT / f"Results/control_platform/p9_learning_mworks_20260717/generated_c/{MODEL}",
    )
    parser.add_argument(
        "--result-dir", type=Path,
        default=ROOT / "Results/control_platform/p9_learning_mworks_20260717/sil",
    )
    args = parser.parse_args()
    generated_dir = args.generated_dir.resolve()
    result_dir = args.result_dir.resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    source_path = result_dir / "source_sil_harness.c"
    generated_path = result_dir / "generated_sil_harness.c"
    source_path.write_text(source_harness(), encoding="utf-8", newline="\n")
    public_header = (generated_dir / f"{MODEL}.h").read_text(encoding="utf-8")
    generated_path.write_text(generated_harness(public_header), encoding="utf-8", newline="\n")
    source_exe, generated_exe = result_dir / "source_gate", result_dir / "generated_gate"
    source_compile = run_wsl([
        "gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
        wsl_path(SOURCE_DIR / "pid_unified_core.c"),
        wsl_path(SOURCE_DIR / "pid_attitude_thrust_core.c"),
        wsl_path(SOURCE_DIR / "learning_control_core.c"),
        wsl_path(SOURCE_DIR / "learning_attitude_thrust_core.c"), wsl_path(source_path),
        "-I", wsl_path(SOURCE_DIR), "-lm", "-o", wsl_path(source_exe),
    ])
    generated_compile = run_wsl([
        "gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
        wsl_path(generated_dir / f"{MODEL}.c"), wsl_path(generated_dir / f"{MODEL}_data.c"),
        wsl_path(generated_dir / "extern_inc/momodel_extern_ince1.c"), wsl_path(generated_path),
        "-I", wsl_path(generated_dir), "-I", wsl_path(generated_dir / "extern_inc"),
        "-lm", "-o", wsl_path(generated_exe),
    ])
    (result_dir / "source_compile.stderr.txt").write_text(source_compile.stderr, encoding="utf-8")
    (result_dir / "generated_compile.stderr.txt").write_text(generated_compile.stderr, encoding="utf-8")
    if source_compile.returncode or generated_compile.returncode:
        report = {
            "schema": "mosim.control_platform.p9_generated_sil.v1", "status": "blocked",
            "stage": "compile", "source_return_code": source_compile.returncode,
            "generated_return_code": generated_compile.returncode,
        }
    else:
        source_run, generated_run = run_wsl([wsl_path(source_exe)]), run_wsl([wsl_path(generated_exe)])
        (result_dir / "source_run.stdout.txt").write_text(source_run.stdout, encoding="utf-8")
        (result_dir / "generated_run.stdout.txt").write_text(generated_run.stdout, encoding="utf-8")
        source_rows, generated_rows = parse_rows(source_run.stdout), parse_rows(generated_run.stdout)
        failures: list[dict[str, object]] = []
        maximum, tolerance = 0.0, 1.0e-12
        for mode in (1, 2):
            expected, actual = source_rows.get(mode), generated_rows.get(mode)
            if expected is None or actual is None or len(expected) != len(actual):
                failures.append({"mode": mode, "reason": "missing_or_mismatched_row"})
                continue
            for index, (left, right) in enumerate(zip(expected, actual, strict=True)):
                difference = abs(left - right)
                maximum = max(maximum, difference)
                if difference > tolerance:
                    failures.append({"mode": mode, "column": index, "difference": difference})
        report = {
            "schema": "mosim.control_platform.p9_generated_sil.v1",
            "status": "passed" if not failures else "failed",
            "routes": ROUTES,
            "artifact_sha256": "4d480c6ad4738da75b4f7bfdf824658b7878ea511a52935ed2be4fff0d043e45",
            "route_count": len(generated_rows),
            "compared_columns_per_route": len(next(iter(generated_rows.values()), [])),
            "max_abs_difference": maximum,
            "tolerance": tolerance,
            "official_codegen": "MWORKS GenerateModelCode",
            "failure_count": len(failures),
            "failures": failures[:30],
            "claim_ceiling": "Official MWORKS-generated C equals project source for two frozen learning ATTITUDE_THRUST cases; Gazebo runtime remains separate.",
        }
    source_exe.unlink(missing_ok=True)
    generated_exe.unlink(missing_ok=True)
    (result_dir / "P9_GENERATED_SIL_EQUIVALENCE.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
