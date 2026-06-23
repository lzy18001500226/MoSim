#!/usr/bin/env python3
"""Compare MWORKS Sysblock output with generated C runtime output.

This is the first SIL gate for generated controller code. The current probe is
intentionally narrow: it verifies the zero-input Sysblock demo against the
generated C runtime using the already-open MWORKS result variable.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def load_codegen_checker():
    path = ROOT / "Scripts" / "mworks" / "check_codegen_runtime.py"
    spec = importlib.util.spec_from_file_location("check_codegen_runtime", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_codegen_runtime.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def project_path(value: str | Path) -> Path:
    checker = load_codegen_checker()
    return checker.project_path(value)


def display_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def row_outputs(row: dict[str, Any]) -> dict[str, float]:
    if isinstance(row.get("outputs"), dict):
        return {str(key): float(value) for key, value in row["outputs"].items()}
    if "output" in row:
        return {"output": float(row["output"])}
    raise KeyError(f"row has no output or outputs field: {row}")


def align_output_aliases(
    runtime_outputs: dict[str, float],
    mworks_outputs: dict[str, float],
) -> tuple[dict[str, float], dict[str, float]]:
    if set(mworks_outputs) == {"output"} and len(runtime_outputs) == 1 and "output" not in runtime_outputs:
        field = next(iter(runtime_outputs))
        return runtime_outputs, {field: mworks_outputs["output"]}
    if set(runtime_outputs) == {"output"} and len(mworks_outputs) == 1 and "output" not in mworks_outputs:
        field = next(iter(mworks_outputs))
        return {field: runtime_outputs["output"]}, mworks_outputs
    return runtime_outputs, mworks_outputs


def compare_rows(
    runtime_rows: list[dict[str, Any]],
    mworks_rows: list[dict[str, Any]],
    tolerance: float,
    compare_time: bool = False,
) -> dict[str, Any]:
    comparisons: list[dict[str, Any]] = []
    max_abs_error = 0.0
    for runtime_row, mworks_row in zip(runtime_rows, mworks_rows):
        runtime_outputs = row_outputs(runtime_row)
        mworks_outputs = row_outputs(mworks_row)
        runtime_outputs, mworks_outputs = align_output_aliases(runtime_outputs, mworks_outputs)
        fields = list(runtime_outputs)
        missing_runtime = [field for field in mworks_outputs if field not in runtime_outputs]
        missing_mworks = [field for field in runtime_outputs if field not in mworks_outputs]
        field_comparisons: dict[str, Any] = {}
        row_pass = not missing_runtime and not missing_mworks
        for field in fields:
            if field not in mworks_outputs:
                continue
            runtime_output = runtime_outputs[field]
            mworks_output = mworks_outputs[field]
            abs_error = abs(runtime_output - mworks_output)
            max_abs_error = max(max_abs_error, abs_error)
            field_comparisons[field] = {
                "runtime_output": runtime_output,
                "mworks_output": mworks_output,
                "abs_error": abs_error,
                "pass": abs_error <= tolerance,
            }
            row_pass = row_pass and abs_error <= tolerance
        runtime_time = float(runtime_row["time_s"])
        mworks_time = float(mworks_row["time_s"])
        time_error = abs(runtime_time - mworks_time)
        row_pass = row_pass and (not compare_time or time_error <= tolerance)
        comparisons.append(
            {
                "index": int(runtime_row["index"]),
                "runtime_time_s": runtime_time,
                "mworks_time_s": mworks_time,
                "time_error_s": time_error,
                "fields": field_comparisons,
                "missing_runtime_outputs": missing_runtime,
                "missing_mworks_outputs": missing_mworks,
                "pass": row_pass,
            }
        )
    return {
        "comparisons": comparisons,
        "max_abs_error": max_abs_error,
        "pass": len(runtime_rows) == len(mworks_rows) and all(item["pass"] for item in comparisons),
    }


def offline_zero_reference(times: list[float]) -> list[dict[str, Any]]:
    return [{"time_s": time_s, "output": 0.0, "source": "offline_zero_input_reference"} for time_s in times]


def run_runtime(
    code_dir: Path,
    model_name: str,
    input_sequence: list[float],
    runtime_schema: dict[str, Any] | None,
) -> dict[str, Any]:
    checker = load_codegen_checker()
    summary = checker.summarize(
        code_dir,
        model_name,
        do_compile=True,
        do_run_smoke=True,
        input_sequence=input_sequence,
        runtime_schema=runtime_schema,
    )
    if not summary.get("ok"):
        raise RuntimeError(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def runtime_has_nonzero_input(runtime_rows: list[dict[str, Any]], tolerance: float = 0.0) -> bool:
    for row in runtime_rows:
        inputs = row.get("inputs")
        if isinstance(inputs, dict):
            for value in inputs.values():
                try:
                    if abs(float(value)) > tolerance:
                        return True
                except (TypeError, ValueError):
                    continue
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code-dir", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--input-sequence", default="0,0,0")
    parser.add_argument("--mworks-reference-json", default="")
    parser.add_argument("--runtime-schema-json", default="")
    parser.add_argument("--tolerance", type=float, default=1e-12)
    parser.add_argument("--json-out", default="")
    args = parser.parse_args(argv)

    code_dir = project_path(args.code_dir)
    input_sequence = [float(item.strip()) for item in args.input_sequence.split(",") if item.strip()]
    runtime_schema = None
    if args.runtime_schema_json:
        schema_path = project_path(args.runtime_schema_json)
        runtime_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    runtime = run_runtime(code_dir, args.model_name, input_sequence, runtime_schema)
    runtime_rows = runtime["runtime_smoke"]["rows"]
    times = [float(row["time_s"]) for row in runtime_rows]

    if args.mworks_reference_json:
        reference_path = project_path(args.mworks_reference_json)
        reference = json.loads(reference_path.read_text(encoding="utf-8"))
        mworks_rows = reference["rows"]
        reference_source = display_path(reference_path)
        reference_label = str(reference.get("source_label", "MWORKS_REFERENCE_JSON"))
        gate_type = "nonzero_input_sil_smoke" if runtime_has_nonzero_input(runtime_rows) or any(abs(value) > 0.0 for value in input_sequence) else "zero_input_sil_smoke"
        limitations = [
            "This gate compares the generated C runtime against a MWORKS/Sysblock reference by output order.",
            "MWORKS reports the first Sysblock output at t=0 for this reference model; generated C harness records after Step(), so timestamps may be shifted by one sample.",
        ]
    else:
        mworks_rows = offline_zero_reference(times)
        reference_source = "offline_zero_input_reference_from_model_structure"
        reference_label = "offline_script"
        gate_type = "zero_input_sil_smoke"
        limitations = [
            "This gate uses zero input only unless a MWORKS external-input injection reference is supplied.",
            "It proves the generated runtime can match the Sysblock zero-input path; nonzero SIL remains a required next gate.",
        ]

    comparison = compare_rows(runtime_rows, mworks_rows, args.tolerance, compare_time=False)
    payload = {
        "schema": "mosim.mworks_codegen_sil_equivalence.v1",
        "gate_type": gate_type,
        "model_name": args.model_name,
        "code_dir": display_path(code_dir),
        "source_label": f"{reference_label}_PLUS_GENERATED_C_RUNTIME",
        "mworks_reference_source": reference_source,
        "input_sequence": input_sequence,
        "runtime_schema_source": display_path(project_path(args.runtime_schema_json)) if args.runtime_schema_json else None,
        "runtime_adapter_shape": runtime["runtime_adapter_shape"],
        "sample_time_s": runtime["sample_time_s"],
        "tolerance": args.tolerance,
        "comparison": comparison,
        "ok": comparison["pass"],
        "limitations": limitations,
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.json_out:
        output_path = project_path(args.json_out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
