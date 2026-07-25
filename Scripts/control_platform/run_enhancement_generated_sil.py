#!/usr/bin/env python3
"""Compare the P5 source core with official MWORKS-generated C."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "Scripts/control_platform"
MODEL = "MoSim_P5_Enhancement_CFunction_Sysblock"
CONTROLLERS = [
    "l1_adaptive", "awff", "complete_adrc", "standardized_indi",
    "parameter_scheduling", "ilc",
]
INPUT_VALUES = {
    "dt": 0.01,
    "position_x": 0.2, "position_y": -0.1, "position_z": 0.7,
    "velocity_x": -0.3, "velocity_y": 0.2, "velocity_z": -0.1,
    "measured_acceleration_x": 0.1, "measured_acceleration_y": -0.05,
    "measured_acceleration_z": 0.02,
    "reference_position_x": 1.0, "reference_position_y": 0.5, "reference_position_z": 1.2,
    "reference_velocity_x": 0.1, "reference_velocity_y": -0.2, "reference_velocity_z": 0.0,
    "reference_acceleration_x": 0.05, "reference_acceleration_y": -0.04,
    "reference_acceleration_z": 0.02, "reference_yaw": 0.3,
    "trajectory_phase_bin": 7.0, "repeat_complete": 0.0,
    "mass_kg": 1.0, "gravity_mps2": 9.80665, "hover_percentage": 0.37,
    "max_tilt_rad": 0.65, "min_collective_thrust_n": 0.0,
    "max_collective_thrust_n": 16.0, "enable": 1.0, "reset": 1.0,
}
OUTPUT_FIELDS = [
    "desired_attitude_w", "desired_attitude_x", "desired_attitude_y", "desired_attitude_z",
    "normalized_thrust", "collective_thrust_n",
    "desired_acceleration_x", "desired_acceleration_y", "desired_acceleration_z",
    "nominal_acceleration_x", "nominal_acceleration_y", "nominal_acceleration_z",
    "compensation_x", "compensation_y", "compensation_z",
    "observer_state_x", "observer_state_y", "observer_state_z",
    "effective_gain_scale", "saturated", "status_code",
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
        check=False,
    )


def source_harness() -> str:
    output_args = [
        "out.desired_attitude_wxyz[0]", "out.desired_attitude_wxyz[1]",
        "out.desired_attitude_wxyz[2]", "out.desired_attitude_wxyz[3]",
        "out.normalized_thrust", "out.collective_thrust_n",
        "out.desired_acceleration[0]", "out.desired_acceleration[1]", "out.desired_acceleration[2]",
        "out.nominal_acceleration[0]", "out.nominal_acceleration[1]", "out.nominal_acceleration[2]",
        "out.compensation[0]", "out.compensation[1]", "out.compensation[2]",
        "out.observer_state[0]", "out.observer_state[1]", "out.observer_state[2]",
        "out.effective_gain_scale", "(double)out.saturated", "(double)out.status_code",
    ]
    return f'''#include <stdio.h>
#include <string.h>
#include "enhancement_attitude_thrust_core.h"
static void print_case(int id) {{
    MosimEnhancementParams p; MosimEnhancementState s; MosimEnhancementInput in;
    MosimEnhancementOutput out; int i;
    memset(&in,0,sizeof(in)); mosim_enhancement_default_params(&p); mosim_enhancement_reset(&s);
    in.dt=0.01; in.position[0]=0.2; in.position[1]=-0.1; in.position[2]=0.7;
    in.velocity[0]=-0.3; in.velocity[1]=0.2; in.velocity[2]=-0.1;
    in.measured_acceleration[0]=0.1; in.measured_acceleration[1]=-0.05; in.measured_acceleration[2]=0.02;
    in.reference_position[0]=1.0; in.reference_position[1]=0.5; in.reference_position[2]=1.2;
    in.reference_velocity[0]=0.1; in.reference_velocity[1]=-0.2; in.reference_velocity[2]=0.0;
    in.reference_acceleration[0]=0.05; in.reference_acceleration[1]=-0.04; in.reference_acceleration[2]=0.02;
    in.reference_yaw=0.3; in.trajectory_phase_bin=7; in.enable=1; in.reset=1;
    p.max_collective_thrust_n=16.0;
    i=mosim_enhancement_step(id,&p,&s,&in,&out);
    printf("%d,%d," "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
           "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\\n",
           id,i,{','.join(output_args)});
}}
int main(void) {{ int id; for(id=1;id<=6;++id) print_case(id); return 0; }}
'''


def generated_harness(public_header: str) -> str:
    globals_found = re.findall(r"extern struct\s+\w+\s+(\w+);", public_header)
    if len(globals_found) < 2:
        raise RuntimeError("cannot resolve generated input/output globals")
    input_global, output_global = globals_found[:2]
    assignments = [f"    {input_global}.controller_id_in=(double)id;"]
    assignments.extend(f"    {input_global}.{name}_in={value:.17g};" for name, value in INPUT_VALUES.items())
    outputs = ",".join(f"{output_global}.{name}_out" for name in OUTPUT_FIELDS)
    return f'''#include <stdio.h>
#include "{MODEL}.h"
#include "{MODEL}_private.h"
static void print_case(int id) {{
{chr(10).join(assignments)}
    Init(); Step();
    printf("%d,%d," "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
           "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\\n",
           id,0,{outputs});
}}
int main(void) {{ int id; for(id=1;id<=6;++id) print_case(id); return 0; }}
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
        default=ROOT / f"Results/control_platform/p5_enhancement_mworks_20260717/generated_c/{MODEL}",
    )
    parser.add_argument(
        "--result-dir", type=Path,
        default=ROOT / "Results/control_platform/p5_enhancement_mworks_20260717/sil",
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
        wsl_path(SOURCE_DIR / "enhancement_attitude_thrust_core.c"), wsl_path(source_path),
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
            "schema": "mosim.control_platform.p5_generated_sil.v1", "status": "blocked",
            "stage": "compile", "source_return_code": source_compile.returncode,
            "generated_return_code": generated_compile.returncode,
        }
    else:
        source_run, generated_run = run_wsl([wsl_path(source_exe)]), run_wsl([wsl_path(generated_exe)])
        source_rows, generated_rows = parse_rows(source_run.stdout), parse_rows(generated_run.stdout)
        failures: list[dict[str, object]] = []
        maximum, tolerance = 0.0, 1.0e-12
        for controller_id in range(1, 7):
            expected, actual = source_rows.get(controller_id), generated_rows.get(controller_id)
            if expected is None or actual is None or len(expected) != len(actual):
                failures.append({"controller_id": controller_id, "reason": "missing_or_mismatched_row"})
                continue
            for index, (left, right) in enumerate(zip(expected, actual, strict=True)):
                difference = abs(left - right)
                maximum = max(maximum, difference)
                if difference > tolerance:
                    failures.append({"controller_id": controller_id, "column": index, "difference": difference})
        report = {
            "schema": "mosim.control_platform.p5_generated_sil.v1",
            "status": "passed" if not failures else "failed",
            "controllers": CONTROLLERS,
            "controller_count": len(generated_rows),
            "compared_columns_per_controller": len(next(iter(generated_rows.values()), [])),
            "max_abs_difference": maximum,
            "tolerance": tolerance,
            "official_codegen": "MWORKS GenerateModelCode",
            "failure_count": len(failures),
            "failures": failures[:30],
            "claim_ceiling": "Official MWORKS-generated C is numerically equivalent to the project source for six fixed-size enhancement cases; Gazebo runtime remains a separate gate.",
        }
    source_exe.unlink(missing_ok=True)
    generated_exe.unlink(missing_ok=True)
    (result_dir / "P5_GENERATED_SIL_EQUIVALENCE.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
