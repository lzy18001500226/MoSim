#!/usr/bin/env python3
"""Extract project-standard CSV files from Sysplorer MCP JSONL logs.

This helper is intentionally narrow: it converts a known GetVarsValues result
saved by the Sysplorer MCP smoke workflow into the CSV schema consumed by
scripts/results/calc_metrics.py / scripts/results/calc_metrics.jl. It lets the project keep
reproducible P0 baseline evidence even when the full MWORKS GUI is not running.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_COLUMNS = ["x", "y", "z", "x_ref", "y_ref", "z_ref"]


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


def build_time_axis(rows: int, start_time: float, stop_time: float | None, dt: float | None) -> list[float]:
    if rows <= 0:
        return []
    if dt is not None:
        return [start_time + index * dt for index in range(rows)]
    if stop_time is None:
        stop_time = 1.0
    if rows == 1:
        return [start_time]
    step = (stop_time - start_time) / (rows - 1)
    return [start_time + index * step for index in range(rows)]


def write_standard_csv(
    series: list[list[float]],
    output: Path,
    columns: list[str],
    start_time: float,
    stop_time: float | None,
    dt: float | None,
) -> None:
    if len(series) < len(columns):
        raise ValueError(f"Expected at least {len(columns)} series, got {len(series)}")

    rows = len(series[0])
    if columns and columns[0] == "time":
        time_values = series[0]
        data_columns = columns[1:]
        data_series_offset = 1
    else:
        time_values = build_time_axis(rows, start_time, stop_time, dt)
        data_columns = columns
        data_series_offset = 0

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["time", *data_columns])
        for index in range(rows):
            row = [time_values[index]]
            row.extend(series[col_index + data_series_offset][index] for col_index in range(len(data_columns)))
            writer.writerow(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path, help="Sysplorer MCP JSONL log")
    parser.add_argument("output", type=Path, help="Output CSV path")
    parser.add_argument(
        "--columns",
        default=",".join(DEFAULT_COLUMNS),
        help=(
            "Comma-separated output names for series saved in GetVarsValues. "
            "Use 'time,...' if the first series is an explicit time axis."
        ),
    )
    parser.add_argument("--start-time", type=float, default=0.0, help="Generated time-axis start when no time series is present")
    parser.add_argument("--stop-time", type=float, default=None, help="Generated time-axis stop when no time series is present")
    parser.add_argument("--dt", type=float, default=None, help="Generated time-axis fixed step when no time series is present")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    columns = [item.strip() for item in args.columns.split(",") if item.strip()]
    series = find_series(args.jsonl)
    write_standard_csv(series, args.output, columns, args.start_time, args.stop_time, args.dt)
    print(f"Wrote {args.output} with {len(series[0])} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
