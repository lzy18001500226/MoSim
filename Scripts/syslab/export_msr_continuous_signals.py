#!/usr/bin/env python
"""Export required formal-runner signals from a MWORKS MSR file.

MWORKS MSR files are HDF5 containers.  The continuous table is accompanied by
an index table whose second row identifies the source table and whose third
row identifies the one-based data column.  This tool exports the signal set
consumed by the Syslab comparison scripts without synthesizing values.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import h5py
import numpy as np


CONTINUOUS_TABLE_KIND = 3
FIELDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("x", ("controller.position_mea[1]",)),
    ("y", ("controller.position_mea[2]",)),
    ("z", ("controller.position_mea[3]",)),
    ("x_ref", ("controller.position_ref[1]",)),
    ("y_ref", ("controller.position_ref[2]",)),
    ("z_ref", ("controller.position_ref[3]",)),
    ("vx", ("controller.velocity_mea[1]",)),
    ("vy", ("controller.velocity_mea[2]",)),
    ("vz", ("controller.velocity_mea[3]",)),
    ("roll", ("controller.roll_mea", "controller.attitude_mea[1]")),
    ("pitch", ("controller.pitch_mea", "controller.attitude_mea[2]")),
    ("yaw", ("controller.yaw_mea", "controller.attitude_mea[3]")),
    (
        "u1",
        (
            "plant.physical.wrapper.motor_command[1]",
            "plant.physical.wrapper.dynamics.motor_command[1]",
        ),
    ),
    (
        "u2",
        (
            "plant.physical.wrapper.motor_command[2]",
            "plant.physical.wrapper.dynamics.motor_command[2]",
        ),
    ),
    (
        "u3",
        (
            "plant.physical.wrapper.motor_command[3]",
            "plant.physical.wrapper.dynamics.motor_command[3]",
        ),
    ),
    (
        "u4",
        (
            "plant.physical.wrapper.motor_command[4]",
            "plant.physical.wrapper.dynamics.motor_command[4]",
        ),
    ),
)


def relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_variable_names(dataset: h5py.Dataset) -> list[str]:
    raw = np.asarray(dataset[0], dtype=np.int8).tobytes()
    names = [item.decode("utf-8", "replace") for item in raw.split(b"\0") if item]
    if not names:
        raise ValueError("Variable Name Table is empty")
    return names


def build_variable_index(handle: h5py.File) -> dict[str, tuple[int, int]]:
    names = decode_variable_names(handle["Variable Name Table"])
    index_table = np.asarray(handle["Variable Index Table"])
    if index_table.ndim != 2 or index_table.shape[0] < 3:
        raise ValueError(f"unexpected Variable Index Table shape {index_table.shape}")
    if index_table.shape[1] != len(names):
        raise ValueError(
            "Variable Name Table / Variable Index Table length mismatch: "
            f"{len(names)} names, {index_table.shape[1]} index columns"
        )
    return {
        name: (int(index_table[1, column]), int(index_table[2, column]))
        for column, name in enumerate(names)
    }


def resolve_series(
    variable_index: dict[str, tuple[int, int]],
    continuous: np.ndarray,
    aliases: tuple[str, ...],
) -> tuple[np.ndarray, dict[str, Any]]:
    rejected: list[str] = []
    for name in aliases:
        entry = variable_index.get(name)
        if entry is None:
            continue
        table_kind, signed_column = entry
        if table_kind != CONTINUOUS_TABLE_KIND:
            rejected.append(f"{name}: table_kind={table_kind}")
            continue
        column = abs(signed_column) - 1
        if column < 0 or column >= continuous.shape[1]:
            rejected.append(f"{name}: column={signed_column} outside continuous table")
            continue
        return continuous[:, column], {
            "source_variable": name,
            "table_kind": table_kind,
            "continuous_column_one_based": column + 1,
            "index_table_signed_column": signed_column,
        }
    available = ", ".join(aliases)
    detail = "; ".join(rejected)
    raise ValueError(f"required continuous signal not found: {available}" + (f" ({detail})" if detail else ""))


def validate_time(time: np.ndarray) -> None:
    if len(time) < 2:
        raise ValueError("continuous result has fewer than two samples")
    if not np.isfinite(time).all():
        raise ValueError("time contains non-finite values")
    if np.any(np.diff(time) <= 0):
        raise ValueError("time is not strictly increasing")


def write_csv(path: Path, values: dict[str, np.ndarray], overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    header = ["time", *[field for field, _ in FIELDS], "position_error_norm"]
    row_count = len(values["time"])
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in range(row_count):
            position_error = math.sqrt(
                (values["x"][row] - values["x_ref"][row]) ** 2
                + (values["y"][row] - values["y_ref"][row]) ** 2
                + (values["z"][row] - values["z_ref"][row]) ** 2
            )
            writer.writerow(
                [f"{values['time'][row]:.9f}"]
                + [f"{values[field][row]:.9f}" for field, _ in FIELDS]
                + [f"{position_error:.9f}"]
            )
    temporary.replace(path)


def verify_against(exported_csv: Path, reference_csv: Path) -> dict[str, Any]:
    with exported_csv.open(newline="", encoding="utf-8") as handle:
        exported_rows = list(csv.DictReader(handle))
    with reference_csv.open(newline="", encoding="utf-8-sig") as handle:
        reference_rows = list(csv.DictReader(handle))
    if len(exported_rows) != len(reference_rows):
        return {
            "reference_csv": relative_path(reference_csv),
            "exported_row_count": len(exported_rows),
            "reference_row_count": len(reference_rows),
            "status": "failed",
            "error": (
                "verification row mismatch: "
                f"exported={len(exported_rows)}, reference={len(reference_rows)}"
            ),
        }
    common = sorted(set(exported_rows[0]).intersection(reference_rows[0])) if exported_rows else []
    differences: dict[str, float] = {}
    per_column: list[dict[str, Any]] = []
    for field in common:
        deltas = [
            abs(float(exported[field]) - float(reference[field]))
            for exported, reference in zip(exported_rows, reference_rows)
        ]
        peak_index = max(range(len(deltas)), key=deltas.__getitem__) if deltas else 0
        maximum = deltas[peak_index] if deltas else 0.0
        differences[field] = maximum
        if exported_rows:
            per_column.append(
                {
                    "column": field,
                    "maximum_absolute_difference": maximum,
                    "peak_row_index": peak_index,
                    "time_s": float(exported_rows[peak_index]["time"]),
                    "exported_value_at_peak": float(exported_rows[peak_index][field]),
                    "reference_value_at_peak": float(reference_rows[peak_index][field]),
                }
            )
    maximum_difference = max(differences.values(), default=0.0)
    threshold = 1.0e-8
    result: dict[str, Any] = {
        "reference_csv": relative_path(reference_csv),
        "exported_row_count": len(exported_rows),
        "reference_row_count": len(reference_rows),
        "shared_columns": common,
        "max_abs_difference_by_column": differences,
        "per_column": per_column,
        "max_abs_difference": maximum_difference,
        "threshold": threshold,
        "status": "passed" if maximum_difference <= threshold else "failed",
    }
    if maximum_difference > threshold:
        result["error"] = f"verification mismatch exceeds {threshold:g}: {maximum_difference}"
    return result


def export_one(entry: dict[str, Any], overwrite: bool) -> dict[str, Any]:
    source = Path(entry["msr_path"])
    output = Path(entry["csv_path"])
    result: dict[str, Any] = {
        "scheme_id": entry.get("scheme_id", source.parent.parent.name),
        "msr_path": relative_path(source),
        "csv_path": relative_path(output),
    }
    if not source.is_file():
        raise FileNotFoundError(f"MSR file not found: {source}")

    with h5py.File(source, "r") as handle:
        if "Continuous Data Table" not in handle:
            raise ValueError("MSR lacks Continuous Data Table")
        continuous = np.asarray(handle["Continuous Data Table"])
        if continuous.ndim != 2 or continuous.shape[1] == 0:
            raise ValueError(f"unexpected continuous table shape {continuous.shape}")
        variable_index = build_variable_index(handle)
        values: dict[str, np.ndarray] = {"time": continuous[:, 0]}
        bindings: dict[str, dict[str, Any]] = {"time": {"continuous_column_one_based": 1}}
        validate_time(values["time"])
        for field, aliases in FIELDS:
            series, binding = resolve_series(variable_index, continuous, aliases)
            if not np.isfinite(series).all():
                raise ValueError(f"{field} contains non-finite values")
            values[field] = series
            bindings[field] = binding

    write_csv(output, values, overwrite=overwrite)
    result.update(
        {
            "status": "valid",
            "source_sha256": sha256_file(source),
            "row_count": int(len(values["time"])),
            "column_count": 18,
            "time_range_s": [float(values["time"][0]), float(values["time"][-1])],
            "source_bindings": bindings,
            "csv_size_bytes": output.stat().st_size,
        }
    )
    reference = entry.get("verify_against")
    if reference:
        regression = verify_against(output, Path(reference))
        result["reference_regression"] = regression
        if regression["status"] != "passed":
            result["status"] = "failed"
            result["error"] = regression["error"]
    return result


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", dest="input_msr", type=Path, help="single Result.msr input")
    parser.add_argument("--output", dest="output_csv", type=Path, help="single CSV output")
    parser.add_argument("--scheme-id", default="unknown", help="scheme id for a single export")
    parser.add_argument("--verify-against", type=Path, help="reference CSV for a single-export regression")
    parser.add_argument("--manifest", type=Path, help="JSON list/object with scheme_id, msr_path, and csv_path")
    parser.add_argument("--summary", type=Path, required=True, help="JSON summary output")
    parser.add_argument("--overwrite", action="store_true", help="permit replacement of an existing CSV")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if bool(args.input_msr) == bool(args.manifest):
        raise ValueError("provide exactly one of --input or --manifest")
    if args.input_msr and not args.output_csv:
        raise ValueError("--output is required with --input")
    if args.manifest and args.output_csv:
        raise ValueError("--output is only valid with --input")

    if args.input_msr:
        entries = [
            {
                "scheme_id": args.scheme_id,
                "msr_path": str(args.input_msr),
                "csv_path": str(args.output_csv),
                **({"verify_against": str(args.verify_against)} if args.verify_against else {}),
            }
        ]
        manifest_path = None
    else:
        manifest_path = args.manifest
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = payload["controllers"] if isinstance(payload, dict) else payload
        if not isinstance(entries, list) or not entries:
            raise ValueError("manifest must contain a non-empty controller list")

    results: list[dict[str, Any]] = []
    for entry in entries:
        try:
            results.append(export_one(entry, overwrite=args.overwrite))
        except Exception as error:  # Preserve per-controller diagnostics for batch completion.
            results.append(
                {
                    "scheme_id": entry.get("scheme_id", "unknown"),
                    "msr_path": entry.get("msr_path"),
                    "csv_path": entry.get("csv_path"),
                    "status": "failed",
                    "error": str(error),
                }
            )

    summary = {
        "schema": "mosim.msr_continuous_signal_export.v1",
        "manifest": relative_path(manifest_path) if manifest_path else None,
        "total_controllers": len(results),
        "export_success": sum(item["status"] == "valid" for item in results),
        "export_failed": sum(item["status"] != "valid" for item in results),
        "controllers": results,
    }
    write_json(args.summary, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["export_failed"] == 0 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
