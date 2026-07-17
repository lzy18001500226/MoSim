#!/usr/bin/env python3
"""Compare the P8 source formation core with official MWORKS-generated C."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "Scripts/control_platform"
MODEL = "MoSim_P8_FormationControl_CFunction_Sysblock"
MODES = [
    "leader_follower", "virtual_structure", "consensus", "containment",
    "formation_tracking", "formation_reconfiguration",
    "fault_tolerant_formation", "formation_cbf",
    "distributed_mpc_formation",
]
INPUT_NAMES = [
    "dt", "leader_x", "leader_y", "leader_z", "leader_vx", "leader_vy",
    "leader_vz", "leader_yaw",
    *[f"position_{agent}_{axis}" for agent in range(1, 4) for axis in "xyz"],
    *[f"velocity_{agent}_{axis}" for agent in range(1, 4) for axis in "xyz"],
    "healthy_1", "healthy_2", "healthy_3", "reconfigure", "enable", "reset",
]
OUTPUT_FIELDS = [
    *[f"desired_position_{agent}_{axis}" for agent in range(1, 4) for axis in "xyz"],
    *[f"desired_velocity_{agent}_{axis}" for agent in range(1, 4) for axis in "xyz"],
    "minimum_pair_distance", "formation_rmse", "active_agents", "failed_mask",
    "safety_corrections", "status_code",
]


def wsl_path(path: Path) -> str:
    resolved = path.resolve()
    return f"/mnt/{resolved.drive[0].lower()}/{resolved.relative_to(resolved.anchor).as_posix()}"


def run_wsl(command: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc",
         " ".join(shlex.quote(part) for part in command)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout, check=False,
    )


def source_harness() -> str:
    return r'''#include <stdio.h>
#include <string.h>
#include "formation_control_core.h"
static void run_case(int id) {
  MosimFormationParams p; MosimFormationState s; MosimFormationInput in; MosimFormationOutput out;
  int step,agent,axis,rc=0; memset(&in,0,sizeof(in));
  mosim_formation_default_params(&p); mosim_formation_reset(&s);
  in.dt=0.02; in.leader_position[0]=2.0; in.leader_position[1]=1.0; in.leader_position[2]=1.2;
  in.leader_velocity[0]=0.35; in.leader_yaw_rad=0.4; in.enable=1; in.reset=1; in.reconfigure=1;
  for(agent=0;agent<3;++agent) {
    in.healthy[agent]=1; in.position[agent][0]=0.15*agent;
    in.position[agent][1]=-0.20*agent; in.position[agent][2]=1.0;
    for(axis=0;axis<3;++axis) in.velocity[agent][axis]=0.0;
  }
  if(id==7) in.healthy[1]=0;
  for(step=0;step<20;++step) { rc=mosim_formation_step(id,&p,&s,&in,&out); in.reset=0; }
  printf("%d,%d",id,rc);
  for(agent=0;agent<3;++agent) for(axis=0;axis<3;++axis) printf(",%.17g",out.desired_position[agent][axis]);
  for(agent=0;agent<3;++agent) for(axis=0;axis<3;++axis) printf(",%.17g",out.desired_velocity[agent][axis]);
  printf(",%.17g,%.17g,%d,%u,%d,%d\n",out.minimum_pair_distance_m,out.formation_rmse_m,
    out.active_agents,out.failed_mask,out.safety_corrections,out.status_code);
}
int main(void) { int id; for(id=1;id<=9;++id) run_case(id); return 0; }
'''


def generated_harness(public_header: str) -> str:
    globals_found = re.findall(r"extern struct\s+\w+\s+(\w+);", public_header)
    if len(globals_found) < 2:
        raise RuntimeError("cannot resolve generated input/output globals")
    input_global, output_global = globals_found[:2]
    assignments = [
        f"  {input_global}.dt_in=0.02;",
        f"  {input_global}.leader_x_in=2.0;", f"  {input_global}.leader_y_in=1.0;",
        f"  {input_global}.leader_z_in=1.2;", f"  {input_global}.leader_vx_in=0.35;",
        f"  {input_global}.leader_vy_in=0.0;", f"  {input_global}.leader_vz_in=0.0;",
        f"  {input_global}.leader_yaw_in=0.4;",
    ]
    for agent in range(1, 4):
        assignments.extend([
            f"  {input_global}.position_{agent}_x_in={0.15 * (agent - 1):.17g};",
            f"  {input_global}.position_{agent}_y_in={-0.20 * (agent - 1):.17g};",
            f"  {input_global}.position_{agent}_z_in=1.0;",
            f"  {input_global}.velocity_{agent}_x_in=0.0;",
            f"  {input_global}.velocity_{agent}_y_in=0.0;",
            f"  {input_global}.velocity_{agent}_z_in=0.0;",
            f"  {input_global}.healthy_{agent}_in=1.0;",
        ])
    assignments.extend([
        f"  {input_global}.reconfigure_in=1.0;",
        f"  {input_global}.enable_in=1.0;",
        f"  {input_global}.reset_in=1.0;",
    ])
    outputs = ",".join(f"{output_global}.{name}_out" for name in OUTPUT_FIELDS)
    return f'''#include <stdio.h>
#include "{MODEL}.h"
#include "{MODEL}_private.h"
static void run_case(int id) {{
  int step;
  {input_global}.mode_id_in=(double)id;
{chr(10).join(assignments)}
  if(id==7) {input_global}.healthy_2_in=0.0;
  Init();
  for(step=0;step<20;++step) {{ Step(); {input_global}.reset_in=0.0; }}
  printf("%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\\n",id,0,{outputs});
}}
int main(void) {{ int id; for(id=1;id<=9;++id) run_case(id); return 0; }}
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
    parser.add_argument("--generated-dir", type=Path, default=ROOT / f"Results/control_platform/p8_formation_mworks_20260717/generated_c/{MODEL}")
    parser.add_argument("--result-dir", type=Path, default=ROOT / "Results/control_platform/p8_formation_mworks_20260717/sil")
    args = parser.parse_args()
    generated_dir, result_dir = args.generated_dir.resolve(), args.result_dir.resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    source_path = result_dir / "source_sil_harness.c"
    generated_path = result_dir / "generated_sil_harness.c"
    source_path.write_text(source_harness(), encoding="utf-8", newline="\n")
    public_header = (generated_dir / f"{MODEL}.h").read_text(encoding="utf-8")
    generated_path.write_text(generated_harness(public_header), encoding="utf-8", newline="\n")
    source_exe, generated_exe = result_dir / "source_gate", result_dir / "generated_gate"
    source_compile = run_wsl(["gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", wsl_path(SOURCE_DIR / "formation_control_core.c"), wsl_path(source_path), "-I", wsl_path(SOURCE_DIR), "-lm", "-o", wsl_path(source_exe)])
    generated_compile = run_wsl(["gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", wsl_path(generated_dir / f"{MODEL}.c"), wsl_path(generated_dir / f"{MODEL}_data.c"), wsl_path(generated_dir / "extern_inc/momodel_extern_ince1.c"), wsl_path(generated_path), "-I", wsl_path(generated_dir), "-I", wsl_path(generated_dir / "extern_inc"), "-lm", "-o", wsl_path(generated_exe)])
    (result_dir / "source_compile.stderr.txt").write_text(source_compile.stderr, encoding="utf-8")
    (result_dir / "generated_compile.stderr.txt").write_text(generated_compile.stderr, encoding="utf-8")
    if source_compile.returncode or generated_compile.returncode:
        report = {"schema": "mosim.control_platform.p8_generated_sil.v1", "status": "blocked", "stage": "compile", "source_return_code": source_compile.returncode, "generated_return_code": generated_compile.returncode}
    else:
        source_run, generated_run = run_wsl([wsl_path(source_exe)]), run_wsl([wsl_path(generated_exe)])
        source_rows, generated_rows = parse_rows(source_run.stdout), parse_rows(generated_run.stdout)
        failures, maximum, tolerance = [], 0.0, 1.0e-12
        for mode_id in range(1, 10):
            expected, actual = source_rows.get(mode_id), generated_rows.get(mode_id)
            if expected is None or actual is None or len(expected) != len(actual):
                failures.append({"mode_id": mode_id, "reason": "missing_or_mismatched_row"})
                continue
            for index, (left, right) in enumerate(zip(expected, actual, strict=True)):
                difference = abs(left - right); maximum = max(maximum, difference)
                if difference > tolerance:
                    failures.append({"mode_id": mode_id, "column": index, "difference": difference})
        report = {
            "schema": "mosim.control_platform.p8_generated_sil.v1",
            "status": "passed" if not failures else "failed", "modes": MODES,
            "mode_count": len(generated_rows),
            "compared_columns_per_mode": len(next(iter(generated_rows.values()), [])),
            "max_abs_difference": maximum, "tolerance": tolerance,
            "official_codegen": "MWORKS GenerateModelCode",
            "failure_count": len(failures), "failures": failures[:30],
            "claim_ceiling": "Official generated C is numerically equivalent for nine fixed-size three-UAV formation-reference modes; Gazebo multi-UAV acceptance remains separate.",
        }
    source_exe.unlink(missing_ok=True); generated_exe.unlink(missing_ok=True)
    (result_dir / "P8_GENERATED_SIL_EQUIVALENCE.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
