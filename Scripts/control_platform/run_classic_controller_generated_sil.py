#!/usr/bin/env python3
"""Compare project source with official MWORKS-generated C for five controllers."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "Scripts/control_platform"
MODEL_NAME = "MoSim_Classic_CFunction_Sysblock"
DEFAULT_GENERATED_DIR = (
    ROOT / "Results/control_platform/classic_controller_closeout_20260717/mworks/codegen" / MODEL_NAME
)
DEFAULT_RESULT_DIR = ROOT / "Results/control_platform/classic_controller_closeout_20260717/mworks/sil"


def load_builder():
    path = SOURCE_DIR / "build_classic_controller_mworks_models.py"
    spec = importlib.util.spec_from_file_location("classic_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def wsl_path(path: Path) -> str:
    resolved = path.resolve()
    return f"/mnt/{resolved.drive[0].lower()}/{resolved.relative_to(resolved.anchor).as_posix()}"


def run_wsl(command: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["wsl", "-d", "Ubuntu-20.04", "bash", "-lc", " ".join(shlex.quote(part) for part in command)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def output_expressions(prefix: str) -> list[str]:
    expressions: list[str] = []
    for name in ("desired_acceleration",):
        expressions.extend(f"{prefix}.{name}[{index}]" for index in range(3))
    expressions.extend(f"{prefix}.desired_attitude_wxyz[{index}]" for index in range(4))
    for name in (
        "observer_position", "observer_velocity", "reference_model_position",
        "reference_model_velocity", "adaptive_position_delta", "adaptive_velocity_delta",
        "fractional_integral", "fractional_derivative",
    ):
        expressions.extend(f"{prefix}.{name}[{index}]" for index in range(3))
    expressions.extend([
        f"{prefix}.normalized_thrust", f"{prefix}.collective_thrust_n",
        f"(double){prefix}.saturated", f"(double){prefix}.status_code",
    ])
    return expressions


def source_harness(constants: dict[str, float], output_count: int) -> str:
    assignments = [
        f"    in.{name}[{axis}] = {constants[f'{name}_{suffix}']:.17g};"
        for name in ("position", "velocity", "reference_position", "reference_velocity", "reference_acceleration")
        for axis, suffix in enumerate(("x", "y", "z"))
    ]
    assignments.extend([
        f"    in.dt = {constants['dt']:.17g};",
        f"    in.reference_yaw = {constants['reference_yaw']:.17g};",
        "    in.enable = 1;",
    ])
    expressions = output_expressions("out")
    assert len(expressions) == output_count
    fmt = "%d,%d," + ",".join(["%.17g"] * output_count) + "\\n"
    args = ",\n            ".join(expressions)
    return f'''#include <stdio.h>
#include <string.h>
#include "classic_controller_core.h"

int main(void)
{{
    MosimClassicParams params;
    int id;
    mosim_classic_default_params(&params);
    for (id = 1; id <= 5; ++id) {{
        MosimClassicState state;
        MosimClassicInput in;
        MosimClassicOutput out;
        int step;
        mosim_classic_reset(&state);
        memset(&in, 0, sizeof(in));
{chr(10).join(assignments)}
        for (step = 0; step < 4; ++step) {{
            in.reset = step == 0;
            if (mosim_classic_step(id, &params, &state, &in, &out) != 0) return 2;
            printf("{fmt}", id, step,
            {args});
        }}
    }}
    return 0;
}}
'''


def generated_harness(constants: dict[str, float], outputs: list[str], input_global: str, output_global: str) -> str:
    assignments = [f"    {input_global}.{name}_in = {value:.17g};" for name, value in constants.items() if name != "reset"]
    assignments.append(f"    {input_global}.enable_in = 1.0;")
    expressions = [f"{output_global}.{name}_out" for name in outputs]
    fmt = "%d,%d," + ",".join(["%.17g"] * len(outputs)) + "\\n"
    args = ",\n            ".join(expressions)
    return f'''#include <stdio.h>
#include "{MODEL_NAME}.h"
#include "{MODEL_NAME}_private.h"

int main(void)
{{
    int id;
    Init();
    for (id = 1; id <= 5; ++id) {{
        int step;
{chr(10).join(assignments)}
        {input_global}.controller_id_in = (double)id;
        for (step = 0; step < 4; ++step) {{
            {input_global}.reset_in = step == 0 ? 1.0 : 0.0;
            Step();
            printf("{fmt}", id, step,
            {args});
        }}
    }}
    return 0;
}}
'''


def discover_globals(public_header: str) -> tuple[str, str]:
    names = re.findall(r"^extern struct\s+\w+\s+(\w+)\s*;", public_header, re.MULTILINE)
    if len(names) < 2:
        raise RuntimeError("cannot discover generated input/output globals")
    return names[0], names[1]


def parse_rows(stdout: str, output_count: int) -> dict[tuple[int, int], list[float]]:
    rows: dict[tuple[int, int], list[float]] = {}
    for line in stdout.splitlines():
        if not line.strip() or line.startswith("L,"):
            continue
        values = [float(value) for value in line.split(",")]
        if len(values) != output_count + 2:
            continue
        rows[(int(values[0]), int(values[1]))] = values[2:]
    return rows


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-dir", type=Path, default=DEFAULT_GENERATED_DIR)
    parser.add_argument("--result-dir", type=Path, default=DEFAULT_RESULT_DIR)
    args = parser.parse_args()
    generated_dir = args.generated_dir.resolve()
    result_dir = args.result_dir.resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    builder = load_builder()

    public_header = (generated_dir / f"{MODEL_NAME}.h").read_text(encoding="utf-8")
    input_global, output_global = discover_globals(public_header)
    source_harness_path = result_dir / "source_sil_harness.c"
    generated_harness_path = result_dir / "generated_sil_harness.c"
    source_harness_path.write_text(
        source_harness(builder.CONSTANTS, len(builder.OUTPUTS)), encoding="utf-8", newline="\n"
    )
    generated_harness_path.write_text(
        generated_harness(builder.CONSTANTS, builder.OUTPUTS, input_global, output_global),
        encoding="utf-8", newline="\n",
    )

    source_exe = result_dir / "source_sil"
    generated_exe = result_dir / "generated_sil"
    source_compile = run_wsl([
        "gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic",
        wsl_path(SOURCE_DIR / "classic_controller_core.c"), wsl_path(source_harness_path),
        "-I", wsl_path(SOURCE_DIR), "-lm", "-o", wsl_path(source_exe),
    ])
    generated_compile = run_wsl([
        "gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic",
        wsl_path(generated_dir / f"{MODEL_NAME}.c"),
        wsl_path(generated_dir / f"{MODEL_NAME}_data.c"),
        wsl_path(generated_dir / "extern_inc/momodel_extern_ince1.c"),
        wsl_path(generated_harness_path),
        "-I", wsl_path(generated_dir), "-I", wsl_path(generated_dir / "extern_inc"),
        "-lm", "-o", wsl_path(generated_exe),
    ])
    (result_dir / "source_compile.stderr.txt").write_text(source_compile.stderr, encoding="utf-8", newline="\n")
    (result_dir / "generated_compile.stderr.txt").write_text(generated_compile.stderr, encoding="utf-8", newline="\n")
    if source_compile.returncode or generated_compile.returncode:
        report = {
            "schema": "mosim.classic_controller.generated_sil.v1", "status": "blocked", "stage": "compile",
            "source_return_code": source_compile.returncode,
            "generated_return_code": generated_compile.returncode,
        }
        write_json(result_dir / "CLASSIC_CONTROLLER_GENERATED_SIL.json", report)
        print(json.dumps(report, indent=2))
        return 1

    source_run = run_wsl([wsl_path(source_exe)])
    generated_run = run_wsl([wsl_path(generated_exe)])
    source_exe.unlink(missing_ok=True)
    generated_exe.unlink(missing_ok=True)
    (result_dir / "source_run.stdout.csv").write_text(source_run.stdout, encoding="utf-8", newline="\n")
    (result_dir / "generated_run.stdout.csv").write_text(generated_run.stdout, encoding="utf-8", newline="\n")
    source_rows = parse_rows(source_run.stdout, len(builder.OUTPUTS))
    generated_rows = parse_rows(generated_run.stdout, len(builder.OUTPUTS))
    tolerance = 1.0e-12
    failures: list[dict] = []
    maximum = 0.0
    for key in [(controller_id, step) for controller_id in range(1, 6) for step in range(4)]:
        source = source_rows.get(key)
        generated = generated_rows.get(key)
        if source is None or generated is None:
            failures.append({"controller_id": key[0], "step": key[1], "reason": "missing_row"})
            continue
        for index, (expected, actual) in enumerate(zip(source, generated, strict=True)):
            difference = abs(expected - actual)
            maximum = max(maximum, difference)
            if difference > tolerance:
                failures.append({
                    "controller_id": key[0], "step": key[1], "output": builder.OUTPUTS[index],
                    "expected": expected, "actual": actual, "difference": difference,
                })
    passed = not failures and source_run.returncode == 0 and generated_run.returncode == 0
    report = {
        "schema": "mosim.classic_controller.generated_sil.v1",
        "status": "passed" if passed else "failed",
        "controllers": list(builder.CONTROLLERS.values()),
        "controller_count": 5,
        "samples_per_controller": 4,
        "compared_output_count": len(builder.OUTPUTS),
        "total_scalar_comparisons": 5 * 4 * len(builder.OUTPUTS),
        "max_abs_difference": maximum,
        "tolerance": tolerance,
        "input_global": input_global,
        "output_global": output_global,
        "official_codegen": "MWORKS GenerateModelCode",
        "failure_count": len(failures),
        "failures": failures[:40],
        "claim_ceiling": "Official generated C is sample-wise equivalent to project source for five stateful fixed-input cases; px4ctrl and Gazebo remain separate gates.",
    }
    write_json(result_dir / "CLASSIC_CONTROLLER_GENERATED_SIL.json", report)
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
