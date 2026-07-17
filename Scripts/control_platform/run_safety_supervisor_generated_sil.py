#!/usr/bin/env python3
"""Compare the P6 source supervisor with official MWORKS-generated C."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "Scripts/control_platform"
MODEL = "MoSim_P6_SafetySupervisor_CFunction_Sysblock"
MODES = [
    "safety_filter", "cbf", "reference_governor", "geofence",
    "emergency_stop", "return_and_land", "failsafe_state_machine",
]
INPUT_NAMES = [
    "dt", "position_x", "position_y", "position_z",
    "velocity_x", "velocity_y", "velocity_z",
    "candidate_acceleration_x", "candidate_acceleration_y", "candidate_acceleration_z",
    "candidate_thrust", "candidate_tilt_rad",
    "reference_position_x", "reference_position_y", "reference_position_z",
    "home_position_x", "home_position_y", "home_position_z",
    "obstacle_distance", "command_age_s", "state_valid", "offboard_valid",
    "emergency_request", "return_request", "land_request", "enable", "reset",
]
OUTPUT_FIELDS = [
    "safe_acceleration_x", "safe_acceleration_y", "safe_acceleration_z",
    "safe_thrust", "safe_reference_x", "safe_reference_y", "safe_reference_z",
    "action", "state", "active_constraints", "modified", "status_code",
]
BASE_VALUES = {
    "dt": 0.01, "position_x": 0.0, "position_y": 0.0, "position_z": 1.0,
    "velocity_x": 0.0, "velocity_y": 0.0, "velocity_z": 0.0,
    "candidate_acceleration_x": 8.0, "candidate_acceleration_y": 0.0,
    "candidate_acceleration_z": 0.0, "candidate_thrust": 1.2,
    "candidate_tilt_rad": 0.8,
    "reference_position_x": 12.0, "reference_position_y": 0.0,
    "reference_position_z": 1.0,
    "home_position_x": 0.0, "home_position_y": 0.0, "home_position_z": 0.0,
    "obstacle_distance": 5.0, "command_age_s": 0.0,
    "state_valid": 1.0, "offboard_valid": 1.0,
    "emergency_request": 0.0, "return_request": 0.0, "land_request": 0.0,
    "enable": 1.0, "reset": 1.0,
}
OVERRIDES = {
    1: {}, 2: {"obstacle_distance": 0.4}, 3: {}, 4: {},
    5: {"emergency_request": 1.0}, 6: {"return_request": 1.0},
    7: {"command_age_s": 1.0},
}


def wsl_path(path: Path) -> str:
    resolved = path.resolve()
    return f"/mnt/{resolved.drive[0].lower()}/{resolved.relative_to(resolved.anchor).as_posix()}"


def run_wsl(command: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", " ".join(shlex.quote(part) for part in command)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout, check=False,
    )


def source_harness() -> str:
    return r'''#include <stdio.h>
#include <string.h>
#include "safety_supervisor_core.h"
static void run_case(int id) {
    MosimSafetyParams p; MosimSafetyState s; MosimSafetyInput in; MosimSafetyOutput out;
    int rc; memset(&in,0,sizeof(in)); mosim_safety_default_params(&p); mosim_safety_reset(&s);
    in.dt=0.01; in.position[2]=1.0; in.reference_position[0]=12.0; in.reference_position[2]=1.0;
    in.candidate_acceleration[0]=8.0; in.candidate_thrust=1.2; in.candidate_tilt_rad=0.8;
    in.obstacle_distance=5.0; in.state_valid=1; in.offboard_valid=1; in.enable=1; in.reset=1;
    if(id==2) in.obstacle_distance=0.4;
    if(id==5) in.emergency_request=1;
    if(id==6) in.return_request=1;
    if(id==7) in.command_age_s=1.0;
    rc=mosim_safety_step(id,&p,&s,&in,&out);
    printf("%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d,%d,%u,%d,%d\n",
      id,rc,out.safe_acceleration[0],out.safe_acceleration[1],out.safe_acceleration[2],
      out.safe_thrust,out.safe_reference[0],out.safe_reference[1],out.safe_reference[2],
      out.action,out.state,out.active_constraints,out.modified,out.status_code);
}
int main(void) { int id; for(id=1;id<=7;++id) run_case(id); return 0; }
'''


def generated_harness(public_header: str) -> str:
    globals_found = re.findall(r"extern struct\s+\w+\s+(\w+);", public_header)
    if len(globals_found) < 2:
        raise RuntimeError("cannot resolve generated input/output globals")
    input_global, output_global = globals_found[:2]
    cases: list[str] = []
    for mode_id in range(1, 8):
        values = {**BASE_VALUES, **OVERRIDES[mode_id]}
        assignments = [f"    {input_global}.mode_id_in={float(mode_id):.17g};"]
        assignments.extend(
            f"    {input_global}.{name}_in={values[name]:.17g};" for name in INPUT_NAMES
        )
        cases.append(
            f"  if(id=={mode_id}) {{\n" + "\n".join(assignments) + "\n  }"
        )
    outputs = ",".join(f"{output_global}.{name}_out" for name in OUTPUT_FIELDS)
    return f'''#include <stdio.h>
#include "{MODEL}.h"
#include "{MODEL}_private.h"
static void run_case(int id) {{
{chr(10).join(cases)}
  Init(); Step();
  printf("%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\\n",
    id,0,{outputs});
}}
int main(void) {{ int id; for(id=1;id<=7;++id) run_case(id); return 0; }}
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
    parser.add_argument("--generated-dir", type=Path, default=ROOT / f"Results/control_platform/p6_safety_mworks_20260717/generated_c/{MODEL}")
    parser.add_argument("--result-dir", type=Path, default=ROOT / "Results/control_platform/p6_safety_mworks_20260717/sil")
    args = parser.parse_args()
    generated_dir, result_dir = args.generated_dir.resolve(), args.result_dir.resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    source_path, generated_path = result_dir / "source_sil_harness.c", result_dir / "generated_sil_harness.c"
    source_path.write_text(source_harness(), encoding="utf-8", newline="\n")
    public_header = (generated_dir / f"{MODEL}.h").read_text(encoding="utf-8")
    generated_path.write_text(generated_harness(public_header), encoding="utf-8", newline="\n")
    source_exe, generated_exe = result_dir / "source_gate", result_dir / "generated_gate"
    source_compile = run_wsl(["gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", wsl_path(SOURCE_DIR / "safety_supervisor_core.c"), wsl_path(source_path), "-I", wsl_path(SOURCE_DIR), "-lm", "-o", wsl_path(source_exe)])
    generated_compile = run_wsl(["gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", wsl_path(generated_dir / f"{MODEL}.c"), wsl_path(generated_dir / f"{MODEL}_data.c"), wsl_path(generated_dir / "extern_inc/momodel_extern_ince1.c"), wsl_path(generated_path), "-I", wsl_path(generated_dir), "-I", wsl_path(generated_dir / "extern_inc"), "-lm", "-o", wsl_path(generated_exe)])
    (result_dir / "source_compile.stderr.txt").write_text(source_compile.stderr, encoding="utf-8")
    (result_dir / "generated_compile.stderr.txt").write_text(generated_compile.stderr, encoding="utf-8")
    report: dict[str, object]
    if source_compile.returncode or generated_compile.returncode:
        report = {"schema": "mosim.control_platform.p6_generated_sil.v1", "status": "blocked", "stage": "compile", "source_return_code": source_compile.returncode, "generated_return_code": generated_compile.returncode}
    else:
        source_run, generated_run = run_wsl([wsl_path(source_exe)]), run_wsl([wsl_path(generated_exe)])
        source_rows, generated_rows = parse_rows(source_run.stdout), parse_rows(generated_run.stdout)
        failures: list[dict[str, object]] = []
        maximum, tolerance = 0.0, 1.0e-12
        for mode_id in range(1, 8):
            expected, actual = source_rows.get(mode_id), generated_rows.get(mode_id)
            if expected is None or actual is None or len(expected) != len(actual):
                failures.append({"mode_id": mode_id, "reason": "missing_or_mismatched_row"})
                continue
            for index, (left, right) in enumerate(zip(expected, actual, strict=True)):
                difference = abs(left - right); maximum = max(maximum, difference)
                if difference > tolerance:
                    failures.append({"mode_id": mode_id, "column": index, "difference": difference})
        report = {"schema": "mosim.control_platform.p6_generated_sil.v1", "status": "passed" if not failures else "failed", "modes": MODES, "mode_count": len(generated_rows), "compared_columns_per_mode": len(next(iter(generated_rows.values()), [])), "max_abs_difference": maximum, "tolerance": tolerance, "official_codegen": "MWORKS GenerateModelCode", "failure_count": len(failures), "failures": failures[:30], "claim_ceiling": "Official MWORKS-generated C is numerically equivalent to source for seven isolated safety events; ROS1 Gazebo event evidence remains separate."}
    source_exe.unlink(missing_ok=True); generated_exe.unlink(missing_ok=True)
    (result_dir / "P6_GENERATED_SIL_EQUIVALENCE.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
