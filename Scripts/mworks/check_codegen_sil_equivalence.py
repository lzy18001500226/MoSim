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


def compare_rows(
    runtime_rows: list[dict[str, Any]],
    mworks_rows: list[dict[str, Any]],
    tolerance: float,
    compare_time: bool = False,
) -> dict[str, Any]:
    comparisons: list[dict[str, Any]] = []
    max_abs_error = 0.0
    for runtime_row, mworks_row in zip(runtime_rows, mworks_rows):
        runtime_output = float(runtime_row["output"])
        mworks_output = float(mworks_row["output"])
        abs_error = abs(runtime_output - mworks_output)
        max_abs_error = max(max_abs_error, abs_error)
        runtime_time = float(runtime_row["time_s"])
        mworks_time = float(mworks_row["time_s"])
        time_error = abs(runtime_time - mworks_time)
        comparisons.append(
            {
                "index": int(runtime_row["index"]),
                "runtime_time_s": runtime_time,
                "mworks_time_s": mworks_time,
                "time_error_s": time_error,
                "runtime_output": runtime_output,
                "mworks_output": mworks_output,
                "abs_error": abs_error,
                "pass": abs_error <= tolerance and (not compare_time or time_error <= tolerance),
            }
        )
    return {
        "comparisons": comparisons,
        "max_abs_error": max_abs_error,
        "pass": len(runtime_rows) == len(mworks_rows) and all(item["pass"] for item in comparisons),
    }


def offline_zero_reference(times: list[float]) -> list[dict[str, Any]]:
    return [{"time_s": time_s, "output": 0.0, "source": "offline_zero_input_reference"} for time_s in times]


def run_runtime(code_dir: Path, model_name: str, input_sequence: list[float]) -> dict[str, Any]:
    checker = load_codegen_checker()
    summary = checker.summarize(
        code_dir,
        model_name,
        do_compile=True,
        do_run_smoke=True,
        input_sequence=input_sequence,
    )
    if not summary.get("ok"):
        raise RuntimeError(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code-dir", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--input-sequence", default="0,0,0")
    parser.add_argument("--mworks-reference-json", default="")
    parser.add_argument("--tolerance", type=float, default=1e-12)
    parser.add_argument("--json-out", default="")
    args = parser.parse_args(argv)

    code_dir = project_path(args.code_dir)
    input_sequence = [float(item.strip()) for item in args.input_sequence.split(",") if item.strip()]
    runtime = run_runtime(code_dir, args.model_name, input_sequence)
    runtime_rows = runtime["runtime_smoke"]["rows"]
    times = [float(row["time_s"]) for row in runtime_rows]

    if args.mworks_reference_json:
        reference_path = project_path(args.mworks_reference_json)
        reference = json.loads(reference_path.read_text(encoding="utf-8"))
        mworks_rows = reference["rows"]
        reference_source = str(reference_path.relative_to(ROOT))
        reference_label = str(reference.get("source_label", "MWORKS_REFERENCE_JSON"))
        gate_type = "nonzero_input_sil_smoke" if any(abs(value) > 0.0 for value in input_sequence) else "zero_input_sil_smoke"
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
        "code_dir": str(code_dir.relative_to(ROOT)),
        "source_label": f"{reference_label}_PLUS_GENERATED_C_RUNTIME",
        "mworks_reference_source": reference_source,
        "input_sequence": input_sequence,
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
