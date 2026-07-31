#!/usr/bin/env python3
"""Resolve Chapter 10 accepted-controller artefacts into a flat index for TyPlot.

The index carries no derived statistics beyond what already exists in the frozen
metrics.csv files, so the Syslab/TyPlot plotting stage reads the same numbers the
G3 status matrix reports. Plotting itself stays entirely in TyPlot.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_status_matrix import (  # noqa: E402
    CONTROLLER_FAMILY,
    FAMILY_ORDER,
    PROJECT_ROOT,
    load_accepted_rows,
    metric_float,
    metrics_path_for_row,
    read_metrics_csv,
    resolve_project_path,
)

FAMILY_DIR = {
    "PID族": "pid_family_comparison",
    "线性/鲁棒族": "linear_family_comparison",
    "非线性/自适应族": "nonlinear_family_comparison",
    "滑模族": "smc_family_comparison",
    "优化/预测族": "mpc_family_comparison",
    "几何/微分平坦族": "geometric_family_comparison",
    "学习增强族": "",
    "工程基线": "",
}
FAMILY_SLUG = {
    "PID族": "pid",
    "线性/鲁棒族": "linear",
    "非线性/自适应族": "nonlinear",
    "滑模族": "sliding",
    "优化/预测族": "optimal",
    "几何/微分平坦族": "geometric",
    "学习增强族": "learning",
    "工程基线": "baseline",
}
METRIC_KEYS = [
    "position_rmse_m",
    "terminal_position_error_m",
    "control_energy",
    "max_position_error_m",
    "x_rmse_m",
    "y_rmse_m",
    "z_rmse_m",
    "steady_state_error_m",
    "settling_time_s",
    "sample_rate_hz",
    "row_count",
    "duration_s",
]


def raw_csv_for_row(row: dict[str, object]) -> Path:
    record_path = resolve_project_path(str(row["effective_run_record"]))
    payload = json.loads(record_path.read_text(encoding="utf-8"))
    for artifact in payload.get("artifact_refs", []):
        candidate = str(artifact.get("path", ""))
        if candidate.replace("\\", "/").endswith("/raw/result.csv"):
            path = resolve_project_path(candidate)
            if path.is_file():
                return path
    fallback = record_path.parent / "raw" / "result.csv"
    if fallback.is_file():
        return fallback
    raise FileNotFoundError(f"Raw CSV not found for {row['controller_id']}: {fallback}")


def build(status_path: Path, output: Path) -> dict[str, object]:
    rows = load_accepted_rows(status_path)
    records: list[dict[str, object]] = []
    for row in rows:
        controller_id = str(row["controller_id"])
        family = str(row["family"])
        metrics = read_metrics_csv(metrics_path_for_row(row))
        record: dict[str, object] = {
            "controller_id": controller_id,
            "family": family,
            "family_slug": FAMILY_SLUG.get(family, ""),
            "family_dir": FAMILY_DIR.get(family, ""),
            "family_index": FAMILY_ORDER.index(family) + 1,
            "raw_csv": raw_csv_for_row(row).resolve().as_posix(),
        }
        for key in METRIC_KEYS:
            value = metric_float(metrics, key)
            record[key] = "" if value != value else repr(value)
        records.append(record)

    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys())
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    return {"controller_count": len(records), "index": output.resolve().as_posix()}


def status_class(value: object) -> str:
    raw = str(value).strip().lower()
    if raw in {"pass", "accepted"}:
        return "accepted"
    if raw in {"not_run", "pending", "skipped"}:
        return "not_run"
    return "executed_blocked"


def build_status_index(status_path: Path, output: Path) -> dict[str, object]:
    """Flatten every G3 row (pass and fail) for the status matrix / heatmap."""
    payload = json.loads(status_path.read_text(encoding="utf-8"))
    records: list[dict[str, object]] = []
    for raw_row in payload.get("rows", []):
        controller_id = str(raw_row.get("controller_id", ""))
        family = CONTROLLER_FAMILY.get(controller_id, "工程基线")
        rmse = raw_row.get("position_rmse_m")
        terminal = raw_row.get("terminal_position_error_norm_m")
        records.append(
            {
                "controller_id": controller_id,
                "family": family,
                "family_slug": FAMILY_SLUG.get(family, ""),
                "family_index": FAMILY_ORDER.index(family) + 1 if family in FAMILY_ORDER else 99,
                "status": str(raw_row.get("status", "")),
                "status_class": status_class(raw_row.get("status")),
                "failure_class": "" if raw_row.get("failure_class") in (None, "") else str(raw_row["failure_class"]),
                "effective_source": str(raw_row.get("effective_source", "")),
                "position_rmse_m": "" if not isinstance(rmse, (int, float)) else repr(float(rmse)),
                "terminal_position_error_m": "" if not isinstance(terminal, (int, float)) else repr(float(terminal)),
            }
        )
    records.sort(key=lambda item: (item["family_index"], item["controller_id"]))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    return {"row_count": len(records), "index": output.resolve().as_posix()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--batch-dir",
        type=Path,
        default=Path("Results/control_platform/phase2_full_48_climbpath"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path(".tmp/chapter10_typlot"))
    args = parser.parse_args(argv)

    batch_dir = args.batch_dir if args.batch_dir.is_absolute() else PROJECT_ROOT / args.batch_dir
    output_dir = args.output_dir if args.output_dir.is_absolute() else PROJECT_ROOT / args.output_dir
    status_path = batch_dir / "g3_repair" / "G3_STATUS.json"

    accepted = build(status_path, output_dir / "accepted_controller_index.csv")
    everything = build_status_index(status_path, output_dir / "g3_status_index.csv")
    print(f"[OK] accepted={accepted['controller_count']} -> {accepted['index']}")
    print(f"[OK] all_rows={everything['row_count']} -> {everything['index']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
