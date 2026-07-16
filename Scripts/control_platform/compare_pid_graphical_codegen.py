#!/usr/bin/env python3
"""Compare live graphical MWORKS output with generated-C runtime output."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ["command", "outer_command", "unsaturated_command", "integral_state", "scheduled_gain"]


def project_path(value: str) -> Path:
    path = (ROOT / value).resolve() if not Path(value).is_absolute() else Path(value).resolve()
    path.relative_to(ROOT)
    return path


def compare(mworks_csv: Path, codegen_json: Path, tolerance: float) -> dict:
    with mworks_csv.open(encoding="utf-8", newline="") as stream:
        mworks_rows = list(csv.DictReader(stream))
    codegen = json.loads(codegen_json.read_text(encoding="utf-8"))
    codegen_rows = codegen.get("runtime_smoke", {}).get("rows", [])
    if len(mworks_rows) != len(codegen_rows):
        return {
            "ok": False,
            "reason": "sample count mismatch",
            "mworks_sample_count": len(mworks_rows),
            "codegen_sample_count": len(codegen_rows),
        }
    max_abs_error = {}
    for output in OUTPUTS:
        errors = [
            abs(float(mworks_row[output]) - float(codegen_row["outputs"][output]))
            for mworks_row, codegen_row in zip(mworks_rows, codegen_rows)
        ]
        max_abs_error[output] = max(errors, default=math.inf)
    return {
        "schema": "mosim.pid_graphical_codegen_equivalence.v1",
        "source_pair": ["MWORKS_MCP", "MWORKS_GENERATED_CODE"],
        "mworks_csv": str(mworks_csv),
        "codegen_runtime_json": str(codegen_json),
        "sample_count": len(mworks_rows),
        "outputs": OUTPUTS,
        "tolerance": tolerance,
        "max_abs_error": max_abs_error,
        "behavior_equivalence_ok": all(error <= tolerance for error in max_abs_error.values()),
        "claim_boundary": "Equivalence covers this fixed-input graphical fixture only; six PID variants remain separately gated.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mworks-csv", required=True)
    parser.add_argument("--codegen-json", required=True)
    parser.add_argument("--tolerance", type=float, default=1e-12)
    parser.add_argument("--json-out", required=True)
    args = parser.parse_args()
    payload = compare(project_path(args.mworks_csv), project_path(args.codegen_json), args.tolerance)
    payload["ok"] = bool(payload.get("behavior_equivalence_ok"))
    output = project_path(args.json_out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
