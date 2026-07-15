"""Normalize arbitrary tracking logs into MoSim standard tracking.csv.

The standard output is consumed by compute_tracking_metrics.py. This script is
offline and does not start ROS, Gazebo, PX4, MAVROS, RViz, UE, or MWORKS.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


STANDARD_COLUMNS = [
    "time_s",
    "phase",
    "ref_x_m",
    "ref_y_m",
    "ref_z_m",
    "truth_x_m",
    "truth_y_m",
    "truth_z_m",
    "saturated",
]
NUMERIC_COLUMNS = {
    "time_s",
    "ref_x_m",
    "ref_y_m",
    "ref_z_m",
    "truth_x_m",
    "truth_y_m",
    "truth_z_m",
    "saturated",
}
DEFAULT_VALUES = {
    "phase": "unknown",
    "saturated": "0",
}


def parse_assignments(values: list[str], kind: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"{kind} must use output=input syntax: {value}")
        left, right = value.split("=", 1)
        left = left.strip()
        right = right.strip()
        if not left or not right:
            raise ValueError(f"{kind} has an empty side: {value}")
        parsed[left] = right
    return parsed


def load_map_file(path: str | None) -> dict[str, str]:
    if not path:
        return {}
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("map file must be a JSON object")
    return {str(key): str(value) for key, value in payload.items()}


def load_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    if not fieldnames:
        raise ValueError(f"{path}: input CSV has no header")
    if not rows:
        raise ValueError(f"{path}: input CSV has no rows")
    return fieldnames, rows


def validate_mapping(
    input_columns: list[str],
    column_map: dict[str, str],
    defaults: dict[str, str],
) -> None:
    unknown_outputs = sorted(set(column_map) - set(STANDARD_COLUMNS))
    if unknown_outputs:
        raise ValueError("column map contains unknown standard columns: " + ", ".join(unknown_outputs))

    missing_outputs = [column for column in STANDARD_COLUMNS if column not in column_map and column not in defaults]
    if missing_outputs:
        raise ValueError("standard columns need --map or --default: " + ", ".join(missing_outputs))

    missing_inputs = sorted({source for source in column_map.values() if source not in input_columns})
    if missing_inputs:
        raise ValueError("input CSV is missing mapped columns: " + ", ".join(missing_inputs))


def normalize_rows(rows: list[dict[str, str]], column_map: dict[str, str], defaults: dict[str, str]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=2):
        output: dict[str, str] = {}
        for column in STANDARD_COLUMNS:
            if column in column_map:
                output[column] = row.get(column_map[column], "")
            else:
                output[column] = defaults[column]
        for column in NUMERIC_COLUMNS:
            try:
                float(output[column])
            except ValueError as exc:
                raise ValueError(f"row {index}: standard column {column} is not numeric: {output[column]!r}") from exc
        normalized.append(output)
    return normalized


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=STANDARD_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def build_report(input_path: Path, output_path: Path, row_count: int, column_map: dict[str, str], defaults: dict[str, str]) -> dict[str, Any]:
    return {
        "ok": True,
        "input_csv": str(input_path),
        "output_csv": str(output_path),
        "input_rows": row_count,
        "output_rows": row_count,
        "standard_columns": STANDARD_COLUMNS,
        "mapped_columns": column_map,
        "defaulted_columns": {key: defaults[key] for key in STANDARD_COLUMNS if key in defaults and key not in column_map},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", help="Raw CSV file to normalize")
    parser.add_argument("--out", required=True, help="Output tracking.csv path")
    parser.add_argument("--map", action="append", default=[], help="Column mapping in standard=input form")
    parser.add_argument("--map-file", help="Optional JSON object mapping standard columns to input columns")
    parser.add_argument("--default", action="append", default=[], help="Default value in standard=value form")
    parser.add_argument("--report", help="Optional JSON report output path")
    args = parser.parse_args(argv)

    try:
        input_path = Path(args.input_csv)
        output_path = Path(args.out)
        input_columns, rows = load_rows(input_path)
        column_map = {**load_map_file(args.map_file), **parse_assignments(args.map, "--map")}
        defaults = {**DEFAULT_VALUES, **parse_assignments(args.default, "--default")}
        validate_mapping(input_columns, column_map, defaults)
        normalized = normalize_rows(rows, column_map, defaults)
        write_csv(output_path, normalized)
        report = build_report(input_path, output_path, len(normalized), column_map, defaults)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
