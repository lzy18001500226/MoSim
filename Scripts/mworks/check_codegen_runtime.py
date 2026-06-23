#!/usr/bin/env python3
"""Check MWORKS generated C controller runtime artifacts.

This is a pre-SIL gate. It verifies that generated C sources expose a usable
runtime shape before they are wrapped by MoSim ControllerRuntime.
"""

from __future__ import annotations

import argparse
import shlex
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


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


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


def find_model_data_global(header_text: str) -> str | None:
    match = re.search(
        r"^\s*extern\s+[A-Za-z_][A-Za-z0-9_]*\s*\*\s*const\s+([A-Za-z_][A-Za-z0-9_]*)\s*;",
        header_text,
        re.MULTILINE,
    )
    if not match:
        return None
    return match.group(1)


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


def require_c_identifier(name: str, role: str) -> str:
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        raise ValueError(f"invalid C identifier for {role}: {name!r}")
    return name


def find_sample_time(source_text: str) -> float | None:
    match = re.search(r"m_stepSize\s*=\s*([0-9]+(?:\.[0-9]+)?(?:[eE][-+]?[0-9]+)?)\s*;", source_text)
    if not match:
        return None
    return float(match.group(1))


def windows_path_to_wsl(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    if not drive:
        return resolved.as_posix()
    tail = resolved.relative_to(resolved.anchor).as_posix()
    return f"/mnt/{drive}/{tail}"


def run_command(command: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def run_wsl_command(command: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    shell_command = " ".join(shlex.quote(item) for item in command)
    return subprocess.run(
        ["wsl", "bash", "-lc", f"cd {shlex.quote(windows_path_to_wsl(cwd))} && {shell_command}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def available_compiler() -> dict[str, Any]:
    gcc = shutil.which("gcc")
    if gcc:
        return {"kind": "native", "path": gcc, "available": True}
    wsl = shutil.which("wsl")
    if wsl:
        probe = subprocess.run(
            [wsl, "bash", "-lc", "command -v gcc"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15,
        )
        if probe.returncode == 0 and probe.stdout.strip():
            return {"kind": "wsl", "path": probe.stdout.strip(), "available": True}
    return {"kind": "none", "available": False, "reason": "gcc not found in Windows PATH or WSL"}


def compiler_path(path: Path, compiler: dict[str, Any]) -> str:
    if compiler["kind"] == "wsl":
        return windows_path_to_wsl(path)
    return str(path)


def run_compiler(command: list[str], cwd: Path, compiler: dict[str, Any], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    if compiler["kind"] == "wsl":
        return run_wsl_command(command, cwd, timeout=timeout)
    return run_command(command, cwd, timeout=timeout)


def compile_sources(code_dir: Path, sources: list[str]) -> dict[str, Any]:
    compiler = available_compiler()
    if not compiler["available"]:
        return {"available": False, "ok": False, "reason": compiler["reason"]}

    temp_path: Path | None = None
    with tempfile.TemporaryDirectory(prefix="mworks_codegen_compile_", dir=str(ROOT / "Results" / "tmp")) as temp_dir:
        temp_path = Path(temp_dir)
        command = ["gcc", "-std=c99", "-Wall", "-Wextra", "-pedantic", "-c"]
        command.extend(compiler_path(code_dir / source, compiler) for source in sources)
        command.extend(["-I", compiler_path(code_dir, compiler)])
        result = run_compiler(command, Path(temp_dir), compiler, timeout=60)
    return {
        "available": True,
        "ok": result.returncode == 0,
        "compiler": compiler,
        "returncode": result.returncode,
        "command": command,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "object_dir_removed": temp_path is not None and not temp_path.exists(),
    }


def c_string(value: str) -> str:
    return json.dumps(value)


def normalize_runtime_schema(
    input_globals: dict[str, dict[str, Any]],
    output_globals: dict[str, dict[str, Any]],
    input_sequence: list[float],
    runtime_schema: dict[str, Any] | None,
) -> dict[str, Any]:
    if len(input_globals) != 1 or len(output_globals) != 1:
        if not runtime_schema:
            return {
                "ok": False,
                "reason": "multi-global runtime smoke requires --runtime-schema-json",
            }
        if not runtime_schema.get("input_global") or not runtime_schema.get("output_global"):
            return {
                "ok": False,
                "reason": "multi-global runtime schema must declare input_global and output_global",
            }

    input_global = runtime_schema.get("input_global") if runtime_schema else next(iter(input_globals))
    output_global = runtime_schema.get("output_global") if runtime_schema else next(iter(output_globals))
    if input_global not in input_globals:
        return {"ok": False, "reason": f"input_global not found: {input_global}"}
    if output_global not in output_globals:
        return {"ok": False, "reason": f"output_global not found: {output_global}"}

    available_inputs = list(input_globals[input_global]["fields"])
    available_outputs = list(output_globals[output_global]["fields"])
    input_fields = runtime_schema.get("input_fields") if runtime_schema else available_inputs
    output_fields = runtime_schema.get("output_fields") if runtime_schema else available_outputs
    if not input_fields:
        return {"ok": False, "reason": "runtime schema has no input_fields"}
    if not output_fields:
        return {"ok": False, "reason": "runtime schema has no output_fields"}
    missing_inputs = [field for field in input_fields if field not in available_inputs]
    missing_outputs = [field for field in output_fields if field not in available_outputs]
    if missing_inputs or missing_outputs:
        return {
            "ok": False,
            "reason": "runtime schema fields not found",
            "missing_inputs": missing_inputs,
            "missing_outputs": missing_outputs,
        }

    if runtime_schema and runtime_schema.get("input_sequence"):
        rows = runtime_schema["input_sequence"]
        if not isinstance(rows, list) or not rows:
            return {"ok": False, "reason": "runtime_schema.input_sequence must be a nonempty list"}
        normalized_rows: list[dict[str, float]] = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                return {"ok": False, "reason": f"input_sequence[{index}] must be an object"}
            normalized_rows.append({field: float(row.get(field, 0.0)) for field in input_fields})
    elif len(input_fields) == 1:
        normalized_rows = [{input_fields[0]: float(value)} for value in input_sequence]
    else:
        return {
            "ok": False,
            "reason": "multi-field runtime smoke requires runtime_schema.input_sequence",
        }

    for value in [input_global, output_global, *input_fields, *output_fields]:
        require_c_identifier(str(value), "runtime schema")

    return {
        "ok": True,
        "input_global": input_global,
        "output_global": output_global,
        "input_fields": input_fields,
        "output_fields": output_fields,
        "input_rows": normalized_rows,
    }


def run_harness(
    code_dir: Path,
    model_name: str,
    model_data_global: str,
    schema: dict[str, Any],
) -> dict[str, Any]:
    compiler = available_compiler()
    if not compiler["available"]:
        return {"available": False, "ok": False, "reason": compiler["reason"]}

    temp_path: Path | None = None
    with tempfile.TemporaryDirectory(prefix="mworks_codegen_run_", dir=str(ROOT / "Results" / "tmp")) as temp_dir_text:
        temp_dir = Path(temp_dir_text)
        temp_path = temp_dir
        harness = temp_dir / "mosim_codegen_harness.c"
        input_global = schema["input_global"]
        output_global = schema["output_global"]
        input_fields = list(schema["input_fields"])
        output_fields = list(schema["output_fields"])
        input_rows = list(schema["input_rows"])
        sequence_len = len(input_rows)
        field_arrays: list[str] = []
        for field in input_fields:
            values = ", ".join(f"{float(row[field]):.17g}" for row in input_rows)
            field_arrays.append(f"    double in_{field}[{sequence_len}] = {{{values}}};")
        input_assignments = "\n".join(f"        {input_global}.{field} = in_{field}[i];" for field in input_fields)
        printf_header = ",".join(["%d", *["%.17g" for _ in input_fields], *["%.17g" for _ in output_fields], "%.17g"])
        printf_values = ", ".join(
            [
                "i",
                *[f"in_{field}[i]" for field in input_fields],
                *[f"{output_global}.{field}" for field in output_fields],
                f"{model_data_global}->m_curTime",
            ]
        )
        harness.write_text(
            f"""
#include <stdio.h>
#include "{model_name}.h"
#include "{model_name}_private.h"

int main(void)
{{
{chr(10).join(field_arrays)}
    Init();
    for (int i = 0; i < {sequence_len}; ++i) {{
{input_assignments}
        Step();
        printf("{printf_header}\\n", {printf_values});
    }}
    return 0;
}}
""".lstrip(),
            encoding="utf-8",
        )
        exe = temp_dir / "mosim_codegen_harness"
        command = [
            "gcc",
            "-std=c99",
            "-Wall",
            "-Wextra",
            "-pedantic",
            compiler_path(harness, compiler),
            compiler_path(code_dir / f"{model_name}.c", compiler),
            compiler_path(code_dir / f"{model_name}_data.c", compiler),
            "-I",
            compiler_path(code_dir, compiler),
            "-lm",
            "-o",
            compiler_path(exe, compiler),
        ]
        build = run_compiler(command, temp_dir, compiler, timeout=60)
        if build.returncode != 0:
            return {
                "available": True,
                "ok": False,
                "phase": "build",
                "compiler": compiler,
                "returncode": build.returncode,
                "command": command,
                "stdout": build.stdout,
                "stderr": build.stderr,
            }
        run_command_line = [compiler_path(exe, compiler)]
        run = run_compiler(run_command_line, temp_dir, compiler, timeout=60)
        rows: list[dict[str, Any]] = []
        for line in run.stdout.splitlines():
            if not line.strip():
                continue
            parts = line.split(",")
            expected_parts = 1 + len(input_fields) + len(output_fields) + 1
            if len(parts) != expected_parts:
                return {
                    "available": True,
                    "ok": False,
                    "phase": "parse",
                    "compiler": compiler,
                    "line": line,
                    "expected_parts": expected_parts,
                    "stdout": run.stdout,
                    "stderr": run.stderr,
                }
            index_text = parts[0]
            input_values = parts[1 : 1 + len(input_fields)]
            output_values = parts[1 + len(input_fields) : 1 + len(input_fields) + len(output_fields)]
            time_text = parts[-1]
            rows.append(
                {
                    "index": int(index_text),
                    "inputs": {field: float(value) for field, value in zip(input_fields, input_values)},
                    "outputs": {field: float(value) for field, value in zip(output_fields, output_values)},
                    "input": float(input_values[0]) if len(input_values) == 1 else None,
                    "output": float(output_values[0]) if len(output_values) == 1 else None,
                    "time_s": float(time_text),
                }
            )
    return {
        "available": True,
        "ok": run.returncode == 0 and len(rows) == sequence_len,
        "phase": "run",
        "compiler": compiler,
        "build_command": command,
        "run_command": run_command_line,
        "returncode": run.returncode,
        "stdout": run.stdout,
        "stderr": run.stderr,
        "input_global": input_global,
        "input_fields": input_fields,
        "output_global": output_global,
        "output_fields": output_fields,
        "input_sequence": input_rows,
        "rows": rows,
        "temp_dir_removed": temp_path is not None and not temp_path.exists(),
    }


def summarize(
    code_dir: Path,
    model_name: str,
    do_compile: bool,
    do_run_smoke: bool,
    input_sequence: list[float],
    runtime_schema: dict[str, Any] | None = None,
) -> dict[str, Any]:
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
        "code_dir": display_path(code_dir),
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
    model_data_global = find_model_data_global(header_text)
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
            "model_data_global": model_data_global,
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
        schema = normalize_runtime_schema(input_globals, output_globals, input_sequence, runtime_schema)
        if not schema["ok"]:
            run_payload = {"available": True, "ok": False, **schema}
        elif not model_data_global:
            run_payload = {
                "available": True,
                "ok": False,
                "reason": "generated model data global not found",
            }
        else:
            run_payload = run_harness(code_dir, model_name, model_data_global, schema)
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
    parser.add_argument("--runtime-schema-json", default=None, help="Project-local JSON schema for multi-input/multi-output runtime smoke")
    parser.add_argument("--expect-sample-time", type=float, default=None)
    parser.add_argument("--json-out", default=None, help="Optional project-local JSON output path")
    args = parser.parse_args(argv)

    code_dir = project_path(args.code_dir)
    input_sequence = [float(item.strip()) for item in args.input_sequence.split(",") if item.strip()]
    runtime_schema = None
    if args.runtime_schema_json:
        schema_path = project_path(args.runtime_schema_json)
        runtime_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    payload = summarize(code_dir, args.model_name, args.compile, args.run_smoke, input_sequence, runtime_schema=runtime_schema)
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
