#!/usr/bin/env python3
"""Compare the Golden and Formal Official PID result exports at matched times."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = ROOT / "Results/mworks_live_gate/official_pid_golden_20260803/live_attempt_20260803_1911"
DEFAULT_GOLDEN_CSV = DEFAULT_ROOT / "post_yaw_fix/raw/golden_result.csv"
DEFAULT_FORMAL_CSV = DEFAULT_ROOT / "formal_reference/raw/formal_result.csv"

POSITION_FIELDS = ["position_error_norm", "position[1]", "position[2]", "position[3]"]
ATTITUDE_FIELDS = ["attitude[1]", "attitude[2]", "attitude[3]"]
ROTOR_COMMAND_FIELDS = [f"rotor_command[{index}]" for index in range(1, 5)]
ROTOR_SPEED_FIELDS = [f"rotor_speed[{index}]" for index in range(1, 5)]
COMPARISON_FIELDS = POSITION_FIELDS + ATTITUDE_FIELDS + ROTOR_COMMAND_FIELDS + ROTOR_SPEED_FIELDS
FIELD_LIMITS = {
    **{field: 1e-3 for field in POSITION_FIELDS},
    **{field: 1e-3 for field in ATTITUDE_FIELDS},
    **{field: 2e-2 for field in ROTOR_COMMAND_FIELDS + ROTOR_SPEED_FIELDS},
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _finite_float(row: dict[str, str], field: str) -> float:
    value = float(row[field])
    if not math.isfinite(value):
        raise ValueError(f"{field} is not finite")
    return value


def run_comparison(golden_csv: Path, formal_csv: Path) -> dict[str, Any]:
    failures: list[str] = []
    golden_rows = _read_rows(golden_csv)
    formal_rows = _read_rows(formal_csv)

    if not golden_rows:
        failures.append("golden CSV has no data rows")
    if not formal_rows:
        failures.append("formal CSV has no data rows")

    fields_missing = {
        "golden": [field for field in ["time", *COMPARISON_FIELDS] if golden_rows and field not in golden_rows[0]],
        "formal": [field for field in ["time", *COMPARISON_FIELDS] if formal_rows and field not in formal_rows[0]],
    }
    for source, missing in fields_missing.items():
        if missing:
            failures.append(f"{source} CSV missing {', '.join(missing)}")

    sample_stride = None
    if golden_rows and formal_rows:
        if len(golden_rows) < 2 or len(formal_rows) < 2:
            failures.append("result exports need at least two data rows")
        elif (len(formal_rows) - 1) % (len(golden_rows) - 1) != 0:
            failures.append("formal/golden sample counts do not describe an aligned decimation")
        else:
            sample_stride = (len(formal_rows) - 1) // (len(golden_rows) - 1)
            if sample_stride < 1:
                failures.append("unable to derive a positive formal sample stride")

    max_time_error_s = 0.0
    max_abs_difference = {field: 0.0 for field in COMPARISON_FIELDS}
    terminal_abs_difference = {field: 0.0 for field in COMPARISON_FIELDS}
    if not failures and sample_stride is not None:
        for golden_index, golden_row in enumerate(golden_rows):
            formal_row = formal_rows[golden_index * sample_stride]
            try:
                max_time_error_s = max(
                    max_time_error_s,
                    abs(_finite_float(golden_row, "time") - _finite_float(formal_row, "time")),
                )
                for field in COMPARISON_FIELDS:
                    difference = abs(_finite_float(golden_row, field) - _finite_float(formal_row, field))
                    max_abs_difference[field] = max(max_abs_difference[field], difference)
                    if golden_index == len(golden_rows) - 1:
                        terminal_abs_difference[field] = difference
            except (KeyError, ValueError) as error:
                failures.append(f"row {golden_index}: {error}")
                break

    if max_time_error_s > 1e-12:
        failures.append(f"time axes differ by {max_time_error_s:.12g} s")
    for field, limit in FIELD_LIMITS.items():
        if max_abs_difference[field] > limit:
            failures.append(
                f"{field} max difference {max_abs_difference[field]:.12g} exceeds {limit:.12g}"
            )

    result = {
        "schema_version": "mosim.official_pid_golden_equivalence.v1",
        "source": "MWORKS_MCP_result_exports",
        "golden_model": "MoSimQuadrotorModel.Experiment.Runners.Golden.OfficialPidSingleUavGoldenRunner",
        "formal_model": "MoSimQuadrotorModel.Experiment.Runners.Formal.OfficialPidFormalRunner",
        "status": "pass" if not failures else "fail",
        "golden_csv": str(golden_csv),
        "formal_csv": str(formal_csv),
        "golden_sha256": _sha256(golden_csv),
        "formal_sha256": _sha256(formal_csv),
        "golden_sample_count": len(golden_rows),
        "formal_sample_count": len(formal_rows),
        "formal_decimation_stride": sample_stride,
        "time_alignment_max_abs_s": max_time_error_s,
        "max_abs_difference": max_abs_difference,
        "terminal_abs_difference": terminal_abs_difference,
        "limits": FIELD_LIMITS,
        "evidence_scope": (
            "Result-export comparison only. It does not replace a CheckModel run for the current source "
            "or a current-turn graphical screenshot review."
        ),
        "failures": failures,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--golden-csv", type=Path, default=DEFAULT_GOLDEN_CSV)
    parser.add_argument("--formal-csv", type=Path, default=DEFAULT_FORMAL_CSV)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    summary = run_comparison(args.golden_csv, args.formal_csv)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
