#!/usr/bin/env python3
"""Extract project-standard CSV files from Sysplorer MCP JSONL logs.

This helper is intentionally narrow: it converts a known GetVarsValues result
saved by the Sysplorer MCP smoke workflow into the CSV schema consumed by
scripts/calc_metrics.jl. It lets the project keep reproducible P0 baseline
evidence even when the full MWORKS GUI is not running.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_COLUMNS = ["x_ref", "y_ref", "z_ref", "x", "y", "z"]


def load_inner_result(line: str) -> dict[str, Any] | None:
    outer = json.loads(line)
    result = outer.get("result", {})
    structured = result.get("structuredContent", {})
    raw = structured.get("result")
    if not raw:
        return None
    return json.loads(raw)


def find_series(jsonl_path: Path) -> list[list[float]]:
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        inner = load_inner_result(line)
        if not inner:
            continue
        if inner.get("api") != "GetVarsValues":
            continue
        data = inner.get("data")
        if not isinstance(data, list) or not data or not all(isinstance(item, list) for item in data):
            continue
        lengths = {len(item) for item in data}
        if len(lengths) != 1:
            raise ValueError(f"Inconsistent series lengths in {jsonl_path}: {sorted(lengths)}")
        return data
    raise ValueError(f"No GetVarsValues series found in {jsonl_path}")


def write_standard_csv(series: list[list[float]], output: Path, columns: list[str]) -> None:
    if len(series) < len(columns):
        raise ValueError(f"Expected at least {len(columns)} series, got {len(series)}")

    rows = len(series[0])
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["time", *columns])
        for index in range(rows):
            row = [index / (rows - 1) if rows > 1 else 0.0]
            row.extend(series[col_index][index] for col_index in range(len(columns)))
            writer.writerow(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path, help="Sysplorer MCP JSONL log")
    parser.add_argument("output", type=Path, help="Output CSV path")
    parser.add_argument(
        "--columns",
        default=",".join(DEFAULT_COLUMNS),
        help="Comma-separated names for series saved in GetVarsValues",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    columns = [item.strip() for item in args.columns.split(",") if item.strip()]
    series = find_series(args.jsonl)
    write_standard_csv(series, args.output, columns)
    print(f"Wrote {args.output} with {len(series[0])} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
