#!/usr/bin/env python3
"""Compare the P7 source FTC core with official MWORKS-generated C."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "Scripts/control_platform"
MODEL = "MoSim_P7_FaultTolerantControl_CFunction_Sysblock"
MODES = [
    "fdi", "passive_ftc", "active_ftc", "fault_aware_control_allocation",
    "single_motor_safe_landing", "multi_fault_estimation_reconfiguration",
]
INPUT_NAMES = [
    "dt", "desired_thrust", "desired_roll", "desired_pitch", "desired_yaw",
    "response_1", "response_2", "response_3", "response_4",
    "airborne", "altitude", "enable", "reset",
]
OUTPUT_FIELDS = [
    "motor_command_1", "motor_command_2", "motor_command_3", "motor_command_4",
    "eta_hat_1", "eta_hat_2", "eta_hat_3", "eta_hat_4",
    "achieved_thrust", "achieved_roll", "achieved_pitch", "achieved_yaw",
    "residual_norm", "isolated_mask", "fault_count", "action",
    "allocation_saturated", "status_code",
]
BASE_VALUES = {
    "dt": 0.01, "desired_thrust": 2.4, "desired_roll": 0.04,
    "desired_pitch": -0.03, "desired_yaw": 0.02,
    "response_1": 0.57, "response_2": 0.60,
    "response_3": 0.64, "response_4": 0.59,
    "airborne": 1.0, "altitude": 1.2, "enable": 1.0, "reset": 0.0,
}
OVERRIDES = {
    1: {"response_1": 0.3135}, 2: {"response_1": 0.4275},
    3: {"response_2": 0.33}, 4: {"response_3": 0.352},
    5: {"response_4": 0.118},
    6: {"response_1": 0.3135, "response_3": 0.384},
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
#include "fault_tolerant_control_core.h"
static void run_case(int id) {
    MosimFtcParams p; MosimFtcState s; MosimFtcInput in; MosimFtcOutput out;
    int step, rc=0; memset(&in,0,sizeof(in)); mosim_ftc_default_params(&p); mosim_ftc_reset(&s);
    in.dt=0.01; in.desired_wrench[0]=2.4; in.desired_wrench[1]=0.04;
    in.desired_wrench[2]=-0.03; in.desired_wrench[3]=0.02;
    in.measured_motor_response[0]=0.57; in.measured_motor_response[1]=0.60;
    in.measured_motor_response[2]=0.64; in.measured_motor_response[3]=0.59;
    in.airborne=1; in.altitude=1.2; in.enable=1;
    if(id==1) in.measured_motor_response[0]=0.3135;
    if(id==2) in.measured_motor_response[0]=0.4275;
    if(id==3) in.measured_motor_response[1]=0.33;
    if(id==4) in.measured_motor_response[2]=0.352;
    if(id==5) in.measured_motor_response[3]=0.118;
    if(id==6) { in.measured_motor_response[0]=0.3135; in.measured_motor_response[2]=0.384; }
    for(step=0;step<80;++step) rc=mosim_ftc_step(id,&p,&s,&in,&out);
    printf("%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%u,%d,%d,%d,%d\n",
      id,rc,out.motor_command[0],out.motor_command[1],out.motor_command[2],out.motor_command[3],
      out.effectiveness_estimate[0],out.effectiveness_estimate[1],out.effectiveness_estimate[2],out.effectiveness_estimate[3],
      out.achieved_wrench[0],out.achieved_wrench[1],out.achieved_wrench[2],out.achieved_wrench[3],out.residual_norm,
      out.isolated_mask,out.fault_count,out.action,out.allocation_saturated,out.status_code);
}
int main(void) { int id; for(id=1;id<=6;++id) run_case(id); return 0; }
'''


def generated_harness(public_header: str) -> str:
    globals_found = re.findall(r"extern struct\s+\w+\s+(\w+);", public_header)
    if len(globals_found) < 2:
        raise RuntimeError("cannot resolve generated input/output globals")
    input_global, output_global = globals_found[:2]
    cases = []
    for mode_id in range(1, 7):
        values = {**BASE_VALUES, **OVERRIDES[mode_id]}
        assignments = [f"    {input_global}.mode_id_in={float(mode_id):.17g};"]
        assignments.extend(
            f"    {input_global}.{name}_in={values[name]:.17g};" for name in INPUT_NAMES
        )
        cases.append(f"  if(id=={mode_id}) {{\n" + "\n".join(assignments) + "\n  }")
    outputs = ",".join(f"{output_global}.{name}_out" for name in OUTPUT_FIELDS)
    return f'''#include <stdio.h>
#include "{MODEL}.h"
#include "{MODEL}_private.h"
static void run_case(int id) {{
  int step;
{chr(10).join(cases)}
  Init(); for(step=0;step<80;++step) Step();
  printf("%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\\n",
    id,0,{outputs});
}}
int main(void) {{ int id; for(id=1;id<=6;++id) run_case(id); return 0; }}
'''


def parse_rows(stdout: str) -> dict[int, list[float]]:
    rows = {}
    for line in stdout.splitlines():
        if line.strip():
            values = [float(item) for item in line.split(",")]
            rows[int(values[0])] = values[1:]
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-dir", type=Path, default=ROOT / f"Results/control_platform/p7_ftc_mworks_20260717/generated_c/{MODEL}")
    parser.add_argument("--result-dir", type=Path, default=ROOT / "Results/control_platform/p7_ftc_mworks_20260717/sil")
    args = parser.parse_args()
    generated_dir, result_dir = args.generated_dir.resolve(), args.result_dir.resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    source_path = result_dir / "source_sil_harness.c"
    generated_path = result_dir / "generated_sil_harness.c"
    source_path.write_text(source_harness(), encoding="utf-8", newline="\n")
    public_header = (generated_dir / f"{MODEL}.h").read_text(encoding="utf-8")
    generated_path.write_text(generated_harness(public_header), encoding="utf-8", newline="\n")
    source_exe, generated_exe = result_dir / "source_gate", result_dir / "generated_gate"
    source_compile = run_wsl(["gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", wsl_path(SOURCE_DIR / "fault_tolerant_control_core.c"), wsl_path(source_path), "-I", wsl_path(SOURCE_DIR), "-lm", "-o", wsl_path(source_exe)])
    generated_compile = run_wsl(["gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", wsl_path(generated_dir / f"{MODEL}.c"), wsl_path(generated_dir / f"{MODEL}_data.c"), wsl_path(generated_dir / "extern_inc/momodel_extern_ince1.c"), wsl_path(generated_path), "-I", wsl_path(generated_dir), "-I", wsl_path(generated_dir / "extern_inc"), "-lm", "-o", wsl_path(generated_exe)])
    (result_dir / "source_compile.stderr.txt").write_text(source_compile.stderr, encoding="utf-8")
    (result_dir / "generated_compile.stderr.txt").write_text(generated_compile.stderr, encoding="utf-8")
    if source_compile.returncode or generated_compile.returncode:
        report = {"schema": "mosim.control_platform.p7_generated_sil.v1", "status": "blocked", "stage": "compile", "source_return_code": source_compile.returncode, "generated_return_code": generated_compile.returncode}
    else:
        source_run, generated_run = run_wsl([wsl_path(source_exe)]), run_wsl([wsl_path(generated_exe)])
        source_rows, generated_rows = parse_rows(source_run.stdout), parse_rows(generated_run.stdout)
        failures = []
        maximum, tolerance = 0.0, 1.0e-12
        for mode_id in range(1, 7):
            expected, actual = source_rows.get(mode_id), generated_rows.get(mode_id)
            if expected is None or actual is None or len(expected) != len(actual):
                failures.append({"mode_id": mode_id, "reason": "missing_or_mismatched_row"})
                continue
            for index, (left, right) in enumerate(zip(expected, actual, strict=True)):
                difference = abs(left - right)
                maximum = max(maximum, difference)
                if difference > tolerance:
                    failures.append({"mode_id": mode_id, "column": index, "difference": difference})
        report = {
            "schema": "mosim.control_platform.p7_generated_sil.v1",
            "status": "passed" if not failures else "failed",
            "modes": MODES, "mode_count": len(generated_rows),
            "compared_columns_per_mode": len(next(iter(generated_rows.values()), [])),
            "max_abs_difference": maximum, "tolerance": tolerance,
            "official_codegen": "MWORKS GenerateModelCode",
            "failure_count": len(failures), "failures": failures[:30],
            "claim_ceiling": "Official generated C is numerically equivalent for six persistent FTC fixtures; Gazebo motor injection and actuator telemetry remain separate.",
        }
    source_exe.unlink(missing_ok=True)
    generated_exe.unlink(missing_ok=True)
    (result_dir / "P7_GENERATED_SIL_EQUIVALENCE.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
