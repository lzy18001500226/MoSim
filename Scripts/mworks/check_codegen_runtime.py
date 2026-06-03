#!/usr/bin/env python3
"""Check MWORKS generated C controller runtime artifacts.

This is a pre-SIL gate. It verifies that generated C sources expose a usable
runtime shape before they are wrapped by MoSim ControllerRuntime.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def project_path(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"path outside project boundary: {path}") from exc
    return path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def find_function_names(header_text: str) -> list[str]:
    names: list[str] = []
    for match in re.finditer(r"^\s*void\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*void\s*\)\s*;", header_text, re.MULTILINE):
        names.append(match.group(1))
    return names


def find_extern_structs(header_text: str) -> dict[str, str]:
    structs: dict[str, str] = {}
    pattern = re.compile(
        r"^\s*extern\s+struct\s+([A-Za-z_][A-Za-z0-9_]*)\s+([A-Za-z_][A-Za-z0-9_]*)\s*;",
        re.MULTILINE,
    )
    for match in pattern.finditer(header_text):
        structs[match.group(2)] = match.group(1)
    return structs


def parse_struct_fields(private_header_text: str) -> dict[str, list[str]]:
    structs: dict[str, list[str]] = {}
    pattern = re.compile(
        r"struct\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{(?P<body>.*?)\};",
        re.DOTALL,
    )
    field_pattern = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\s+([A-Za-z_][A-Za-z0-9_]*)\s*;")
    for match in pattern.finditer(private_header_text):
        body = match.group("body")
        structs[match.group(1)] = field_pattern.findall(body)
    return structs


def find_sample_time(source_text: str) -> float | None:
    match = re.search(r"m_stepSize\s*=\s*([0-9]+(?:\.[0-9]+)?(?:[eE][-+]?[0-9]+)?)\s*;", source_text)
    if not match:
        return None
    return float(match.group(1))


def compile_sources(code_dir: Path, sources: list[str]) -> dict[str, Any]:
    gcc = shutil.which("gcc")
    if not gcc:
        return {"available": False, "ok": False, "reason": "gcc not found"}

    temp_path: Path | None = None
    with tempfile.TemporaryDirectory(prefix="mworks_codegen_compile_", dir=str(ROOT / "Results" / "tmp")) as temp_dir:
        temp_path = Path(temp_dir)
        command = [gcc, "-std=c99", "-Wall", "-Wextra", "-pedantic", "-c"]
        command.extend(str(code_dir / source) for source in sources)
        command.extend(["-I", str(code_dir)])
        result = subprocess.run(
            command,
            cwd=temp_dir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
        )
    return {
        "available": True,
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "command": command,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "object_dir_removed": temp_path is not None and not temp_path.exists(),
    }


def c_string(value: str) -> str:
    return json.dumps(value)


def run_harness(
    code_dir: Path,
    model_name: str,
    input_global: str,
    input_field: str,
    output_global: str,
    output_field: str,
    input_sequence: list[float],
) -> dict[str, Any]:
    gcc = shutil.which("gcc")
    if not gcc:
        return {"available": False, "ok": False, "reason": "gcc not found"}

    temp_path: Path | None = None
    with tempfile.TemporaryDirectory(prefix="mworks_codegen_run_", dir=str(ROOT / "Results" / "tmp")) as temp_dir_text:
        temp_dir = Path(temp_dir_text)
        temp_path = temp_dir
        harness = temp_dir / "mosim_codegen_harness.c"
        values = ", ".join(f"{value:.17g}" for value in input_sequence)
        sequence_len = len(input_sequence)
        harness.write_text(
            f"""
#include <stdio.h>
#include "{model_name}.h"
#include "{model_name}_private.h"

int main(void)
{{
    double inputs[{sequence_len}] = {{{values}}};
    Init();
    for (int i = 0; i < {sequence_len}; ++i) {{
        {input_global}.{input_field} = inputs[i];
        Step();
        printf("%d,%.17g,%.17g,%.17g\\n", i, inputs[i], {output_global}.{output_field}, {model_name.lower()}GbMd->m_curTime);
    }}
    return 0;
}}
""".lstrip(),
            encoding="utf-8",
        )
        exe = temp_dir / "mosim_codegen_harness"
        command = [
            gcc,
            "-std=c99",
            "-Wall",
            "-Wextra",
            "-pedantic",
            str(harness),
            str(code_dir / f"{model_name}.c"),
            str(code_dir / f"{model_name}_data.c"),
            "-I",
            str(code_dir),
            "-lm",
            "-o",
            str(exe),
        ]
        build = subprocess.run(command, cwd=temp_dir, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        if build.returncode != 0:
            return {
                "available": True,
                "ok": False,
                "phase": "build",
                "returncode": build.returncode,
                "command": command,
                "stdout": build.stdout,
                "stderr": build.stderr,
            }
        run = subprocess.run([str(exe)], cwd=temp_dir, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        rows: list[dict[str, float | int]] = []
        for line in run.stdout.splitlines():
            if not line.strip():
                continue
            index_text, input_text, output_text, time_text = line.split(",")
            rows.append(
                {
                    "index": int(index_text),
                    "input": float(input_text),
                    "output": float(output_text),
                    "time_s": float(time_text),
                }
            )
    return {
        "available": True,
        "ok": run.returncode == 0 and len(rows) == sequence_len,
        "phase": "run",
        "build_command": command,
        "returncode": run.returncode,
        "stdout": run.stdout,
        "stderr": run.stderr,
        "input_global": input_global,
        "input_field": input_field,
        "output_global": output_global,
        "output_field": output_field,
        "input_sequence": input_sequence,
        "rows": rows,
        "temp_dir_removed": temp_path is not None and not temp_path.exists(),
    }


def summarize(code_dir: Path, model_name: str, do_compile: bool, do_run_smoke: bool, input_sequence: list[float]) -> dict[str, Any]:
    header = code_dir / f"{model_name}.h"
    source = code_dir / f"{model_name}.c"
    private_header = code_dir / f"{model_name}_private.h"
    data_source = code_dir / f"{model_name}_data.c"
    main_source = code_dir / "mwb_main.c"

    required = [header, source, private_header, data_source, main_source, code_dir / "mwb_types.h", code_dir / "mwb_runtime.h"]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]

    payload: dict[str, Any] = {
        "schema": "mosim.mworks_codegen_runtime_check.v1",
        "model_name": model_name,
        "code_dir": str(code_dir.relative_to(ROOT)),
        "missing_required_files": missing,
        "files": sorted(path.name for path in code_dir.iterdir() if path.is_file()),
        "source_label": "MWORKS_GENERATED_CODE",
    }
    if missing:
        payload["ok"] = False
        payload["reason"] = "missing required generated files"
        return payload

    header_text = read_text(header)
    source_text = read_text(source)
    private_header_text = read_text(private_header)
    functions = find_function_names(header_text)
    externs = find_extern_structs(header_text)
    struct_fields = parse_struct_fields(private_header_text)

    input_globals = {
        name: {
            "struct": struct_name,
            "fields": struct_fields.get(struct_name, []),
        }
        for name, struct_name in externs.items()
        if struct_name.endswith("ExtU")
    }
    output_globals = {
        name: {
            "struct": struct_name,
            "fields": struct_fields.get(struct_name, []),
        }
        for name, struct_name in externs.items()
        if struct_name.endswith("ExtY")
    }
    sample_time = find_sample_time(source_text)

    payload.update(
        {
            "functions": functions,
            "has_init": "Init" in functions,
            "has_step": "Step" in functions,
            "input_globals": input_globals,
            "output_globals": output_globals,
            "sample_time_s": sample_time,
            "runtime_adapter_shape": "global_struct_input_output_init_step",
            "sil_gate_required": True,
        }
    )

    compile_payload: dict[str, Any] | None = None
    if do_compile:
        compile_payload = compile_sources(code_dir, [source.name, data_source.name, main_source.name])
        payload["compile"] = compile_payload

    run_payload: dict[str, Any] | None = None
    if do_run_smoke:
        if len(input_globals) != 1 or len(output_globals) != 1:
            run_payload = {
                "available": True,
                "ok": False,
                "reason": "runtime smoke currently requires exactly one input global and one output global",
            }
        else:
            input_global, input_info = next(iter(input_globals.items()))
            output_global, output_info = next(iter(output_globals.items()))
            input_fields = input_info["fields"]
            output_fields = output_info["fields"]
            if len(input_fields) != 1 or len(output_fields) != 1:
                run_payload = {
                    "available": True,
                    "ok": False,
                    "reason": "runtime smoke currently requires exactly one input field and one output field",
                }
            else:
                run_payload = run_harness(
                    code_dir,
                    model_name,
                    input_global,
                    input_fields[0],
                    output_global,
                    output_fields[0],
                    input_sequence,
                )
        payload["runtime_smoke"] = run_payload

    payload["ok"] = bool(
        payload["has_init"]
        and payload["has_step"]
        and input_globals
        and output_globals
        and sample_time is not None
        and (compile_payload is None or compile_payload.get("ok"))
        and (run_payload is None or run_payload.get("ok"))
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code-dir", required=True, help="Generated code directory, project-local")
    parser.add_argument("--model-name", required=True, help="Generated model basename")
    parser.add_argument("--compile", action="store_true", help="Compile generated C sources with gcc")
    parser.add_argument("--run-smoke", action="store_true", help="Build and run a temporary Init/Step harness")
    parser.add_argument("--input-sequence", default="0.1,0.2,-0.1", help="Comma-separated input values for --run-smoke")
    parser.add_argument("--expect-sample-time", type=float, default=None)
    parser.add_argument("--json-out", default=None, help="Optional project-local JSON output path")
    args = parser.parse_args(argv)

    code_dir = project_path(args.code_dir)
    input_sequence = [float(item.strip()) for item in args.input_sequence.split(",") if item.strip()]
    payload = summarize(code_dir, args.model_name, args.compile, args.run_smoke, input_sequence)
    if args.expect_sample_time is not None:
        actual = payload.get("sample_time_s")
        payload["expected_sample_time_s"] = args.expect_sample_time
        payload["sample_time_ok"] = actual is not None and abs(float(actual) - args.expect_sample_time) <= 1e-12
        payload["ok"] = bool(payload.get("ok") and payload["sample_time_ok"])

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.json_out:
        json_out = project_path(args.json_out)
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
