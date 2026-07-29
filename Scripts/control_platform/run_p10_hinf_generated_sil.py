#!/usr/bin/env python3
"""Compare the P10 H-infinity adapter source with official generated C."""

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
MODEL_NAME = "MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock"
DEFAULT_GENERATED_DIR = (
    ROOT / "Results/control_platform/p10_mworks_gap_closeout_20260718/"
    "hinf_hover_wrench/codegen" / MODEL_NAME
)
DEFAULT_RESULT_DIR = (
    ROOT / "Results/control_platform/p10_mworks_gap_closeout_20260718/"
    "hinf_hover_wrench/sil"
)


def load_builder():
    path = SOURCE_DIR / "build_p10_hinf_mworks_fixture.py"
    spec = importlib.util.spec_from_file_location("p10_hinf_builder", path)
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


def build_cases(constants: dict[str, float]) -> list[tuple[str, dict[str, float]]]:
    cases: list[tuple[str, dict[str, float]]] = []

    def add(name: str, **changes: float) -> None:
        values = dict(constants)
        values.update(changes)
        cases.append((name, values))

    add("nominal")
    add(
        "small_error",
        state_roll=-0.03, state_pitch=0.02, state_yaw=-0.04,
        reference_roll=0.01, reference_pitch=-0.015, reference_yaw=0.02,
        state_x=0.08, state_y=-0.06, state_z=0.04,
    )
    add(
        "positive_saturation",
        state_roll=-1.0, state_pitch=-1.0, state_yaw=-1.0,
        state_p=-4.0, state_q=-4.0, state_r=-4.0,
        state_x=-8.0, state_y=-8.0, state_z=-8.0,
        reference_roll=0.3, reference_pitch=0.3, reference_yaw=0.4,
    )
    add(
        "negative_saturation",
        state_roll=1.0, state_pitch=1.0, state_yaw=1.0,
        state_p=4.0, state_q=4.0, state_r=4.0,
        state_x=8.0, state_y=8.0, state_z=8.0,
        reference_roll=-0.3, reference_pitch=-0.3, reference_yaw=-0.4,
    )
    add("disabled", enable=0.0)
    add("reset", reset=1.0)
    add("invalid_mass", mass=0.0)
    add("invalid_stiffness", roll_stiffness_nm_per_rad=0.0)
    return cases


def discover_globals(public_header: str) -> tuple[str, str]:
    names = re.findall(r"^extern struct\s+\w+\s+(\w+)\s*;", public_header, re.MULTILINE)
    if len(names) < 2:
        raise RuntimeError(f"expected generated input/output globals, found {names}")
    return names[0], names[1]


def source_harness(inputs: list[str], outputs: list[str], cases: list[tuple[str, dict[str, float]]]) -> str:
    case_rows = ",\n".join(
        "    {" + ", ".join(f"{values[name]:.17g}" for name in inputs) + "}"
        for _, values in cases
    )
    output_declarations = "\n".join(f"        double {name} = 0.0;" for name in outputs)
    output_pointers = ",\n            ".join(f"&{name}" for name in outputs)
    output_values = ",\n            ".join(outputs)
    input_values = ",\n            ".join(f"cases[index][{position}]" for position in range(len(inputs)))
    fmt = "%d," + ",".join(["%.17g"] * len(outputs)) + "\\n"
    return f'''#include <stdio.h>
#include "p10_hinf_wrench_adapter_core.h"

static const double cases[{len(cases)}][{len(inputs)}] = {{
{case_rows}
}};

int main(void)
{{
    int index;
    for (index = 0; index < {len(cases)}; ++index) {{
{output_declarations}
        MosimP10HinfWrenchAdapterStepScalar(
            {input_values},
            {output_pointers});
        printf("{fmt}", index,
            {output_values});
    }}
    return 0;
}}
'''


def generated_harness(
    inputs: list[str], outputs: list[str], cases: list[tuple[str, dict[str, float]]],
    input_global: str, output_global: str,
) -> str:
    case_rows = ",\n".join(
        "    {" + ", ".join(f"{values[name]:.17g}" for name in inputs) + "}"
        for _, values in cases
    )
    assignments = "\n".join(
        f"        {input_global}.{name}_in = cases[index][{position}];"
        for position, name in enumerate(inputs)
    )
    output_values = ",\n            ".join(f"{output_global}.{name}_out" for name in outputs)
    fmt = "%d," + ",".join(["%.17g"] * len(outputs)) + "\\n"
    return f'''#include <stdio.h>
#include "{MODEL_NAME}.h"
#include "{MODEL_NAME}_private.h"

static const double cases[{len(cases)}][{len(inputs)}] = {{
{case_rows}
}};

int main(void)
{{
    int index;
    for (index = 0; index < {len(cases)}; ++index) {{
        Init();
{assignments}
        Step();
        printf("{fmt}", index,
            {output_values});
    }}
    return 0;
}}
'''


def parse_rows(stdout: str, output_count: int) -> dict[int, list[float]]:
    rows: dict[int, list[float]] = {}
    for line in stdout.splitlines():
        if not line.strip() or line.startswith("L,"):
            continue
        values = [float(value) for value in line.split(",")]
        if len(values) == output_count + 1:
            rows[int(values[0])] = values[1:]
    return rows


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def update_mworks_manifest(result_dir: Path, report: dict) -> None:
    manifest_path = result_dir.parent / "P10_HINF_MWORKS_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["status"] = "passed" if report["status"] == "passed" else "failed"
    manifest["evidence_ladder"]["generated_c_sil"] = report["status"]
    refs = manifest["artifact_refs"]
    for path in (
        result_dir / "P10_HINF_GENERATED_SIL.json",
        result_dir.parent / "screenshots/mil/capture_manifest.json",
    ):
        ref = relative(path)
        if ref not in refs:
            refs.append(ref)
    manifest["claim_boundary"] = (
        "Frozen-hover graphical MWORKS MIL, official code generation and zero-difference "
        "generated-C SIL are closed; generated-C Gazebo remains not_run."
    )
    write_json(manifest_path, manifest)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-dir", type=Path, default=DEFAULT_GENERATED_DIR)
    parser.add_argument("--result-dir", type=Path, default=DEFAULT_RESULT_DIR)
    args = parser.parse_args()
    generated_dir = args.generated_dir.resolve()
    result_dir = args.result_dir.resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    builder = load_builder()
    cases = build_cases(builder.CONSTANTS)
    public_header = (generated_dir / f"{MODEL_NAME}.h").read_text(encoding="utf-8")
    input_global, output_global = discover_globals(public_header)

    source_harness_path = result_dir / "source_sil_harness.c"
    generated_harness_path = result_dir / "generated_sil_harness.c"
    source_harness_path.write_text(
        source_harness(builder.INPUTS, builder.OUTPUTS, cases), encoding="utf-8", newline="\n"
    )
    generated_harness_path.write_text(
        generated_harness(builder.INPUTS, builder.OUTPUTS, cases, input_global, output_global),
        encoding="utf-8", newline="\n",
    )

    source_exe = result_dir / "source_sil"
    generated_exe = result_dir / "generated_sil"
    source_compile = run_wsl([
        "gcc", "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic",
        wsl_path(SOURCE_DIR / "wave_b_hinf_core.c"),
        wsl_path(SOURCE_DIR / "p10_hinf_wrench_adapter_core.c"),
        wsl_path(source_harness_path), "-I", wsl_path(SOURCE_DIR), "-lm", "-o", wsl_path(source_exe),
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
            "schema": "mosim.p10_hinf_wrench_adapter.generated_sil.v1", "status": "blocked",
            "stage": "compile", "source_return_code": source_compile.returncode,
            "generated_return_code": generated_compile.returncode,
        }
        write_json(result_dir / "P10_HINF_GENERATED_SIL.json", report)
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
    for index, (case_name, _) in enumerate(cases):
        expected = source_rows.get(index)
        actual = generated_rows.get(index)
        if expected is None or actual is None:
            failures.append({"case": case_name, "reason": "missing_row"})
            continue
        for column, (source_value, generated_value) in enumerate(zip(expected, actual, strict=True)):
            difference = abs(source_value - generated_value)
            maximum = max(maximum, difference)
            if difference > tolerance:
                failures.append({
                    "case": case_name, "output": builder.OUTPUTS[column],
                    "expected": source_value, "actual": generated_value, "difference": difference,
                })
    passed = not failures and source_run.returncode == 0 and generated_run.returncode == 0
    report = {
        "schema": "mosim.p10_hinf_wrench_adapter.generated_sil.v1",
        "status": "passed" if passed else "failed",
        "controller": "hinf_hover_wrench",
        "cases": [name for name, _ in cases],
        "case_count": len(cases),
        "compared_output_count": len(builder.OUTPUTS),
        "total_scalar_comparisons": len(cases) * len(builder.OUTPUTS),
        "max_abs_difference": maximum,
        "tolerance": tolerance,
        "input_global": input_global,
        "output_global": output_global,
        "official_codegen": "MWORKS GenerateModelCode",
        "failure_count": len(failures),
        "failures": failures[:40],
        "claim_ceiling": (
            "Official generated C is sample-wise equivalent to the frozen-hover WRENCH adapter "
            "source for nominal, bounded, saturated, disabled, reset and invalid-parameter cases; "
            "Gazebo remains a separate gate."
        ),
    }
    write_json(result_dir / "P10_HINF_GENERATED_SIL.json", report)
    update_mworks_manifest(result_dir, report)
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
