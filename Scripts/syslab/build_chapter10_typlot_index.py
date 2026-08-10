#!/usr/bin/env python3
"""Build current catalog-48 indexes consumed by the Chapter 10 figures.

The immutable historical ``G3_STATUS.json`` snapshot remains available for
trace-back.  This report index uses the current catalog reconciliation instead:
30 ``pass`` rows are written to the accepted index and all 48 catalog rows are
written to the status index.  Metrics are read from existing run-record
artifacts; this script does not rerun simulations or recompute results.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

FAMILY_ORDER = [
    "PID族",
    "线性/鲁棒族",
    "非线性/自适应族",
    "滑模族",
    "优化/预测族",
    "几何/微分平坦族",
    "学习增强族",
    "工程基线",
]
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
CATEGORY_FAMILY = {
    "pid_family": "PID族",
    "linear_robust_state_feedback": "线性/鲁棒族",
    "nonlinear_adaptive": "非线性/自适应族",
    "sliding_mode": "滑模族",
    "optimization_predictive": "优化/预测族",
    "geometric_flatness": "几何/微分平坦族",
    "learning": "学习增强族",
    "engineering_deployment_baseline": "工程基线",
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


def resolve_project_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def status_class(value: object) -> str:
    raw = str(value).strip().lower()
    if raw in {"pass", "accepted"}:
        return "accepted"
    if raw in {"not_run", "pending", "skipped"}:
        return "not_run"
    return "executed_blocked"


def source_record_for_row(row: dict[str, object]) -> Path:
    locator = row.get("source_record") or row.get("effective_run_record")
    if not locator:
        raise ValueError(f"{row.get('controller_id', 'unknown')} has no source record")
    path = resolve_project_path(str(locator))
    if not path.is_file():
        raise FileNotFoundError(f"RUN_RECORD does not exist: {path}")
    return path


def source_payload_for_row(row: dict[str, object]) -> tuple[Path, dict[str, object]]:
    path = source_record_for_row(row)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"RUN_RECORD must contain an object: {path}")
    return path, payload


def nested_value(payload: dict[str, object], *keys: str) -> object | None:
    current: object = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def artifact_path(payload: dict[str, object], suffix: str) -> str | None:
    for artifact in payload.get("artifact_refs", []):
        if not isinstance(artifact, dict):
            continue
        candidate = str(artifact.get("path", ""))
        if candidate.replace("\\", "/").endswith(suffix):
            return candidate
    return None


def candidate_path(candidate: object | None) -> Path | None:
    if not candidate:
        return None
    path = resolve_project_path(str(candidate))
    return path if path.is_file() else None


def raw_csv_for_row(row: dict[str, object]) -> Path:
    record_path, payload = source_payload_for_row(row)
    candidates = [
        payload.get("raw_csv"),
        nested_value(payload, "post_run_export", "raw_csv"),
        artifact_path(payload, "/raw/result.csv"),
    ]
    for candidate in candidates:
        path = candidate_path(candidate)
        if path is not None:
            return path
    for fallback in (
        record_path.parent / "raw" / "result.csv",
        record_path.parent / "raw" / "climbpath50s.csv",
    ):
        if fallback.is_file():
            return fallback
    raise FileNotFoundError(f"Raw CSV not found for {row['controller_id']}: {record_path}")


def metrics_csv_for_row(row: dict[str, object]) -> Path | None:
    record_path, payload = source_payload_for_row(row)
    candidates = [
        nested_value(payload, "post_run_export", "metrics_csv"),
        payload.get("metrics_csv"),
        artifact_path(payload, "/metrics/metrics.csv"),
    ]
    for candidate in candidates:
        path = candidate_path(candidate)
        if path is not None:
            return path
    fallback = record_path.parent / "metrics" / "metrics.csv"
    return fallback if fallback.is_file() else None


def metrics_json_for_row(row: dict[str, object]) -> Path | None:
    _, payload = source_payload_for_row(row)
    for candidate in (
        nested_value(payload, "post_run_export", "metrics_json"),
        payload.get("metrics_json"),
    ):
        path = candidate_path(candidate)
        if path is not None:
            return path
    return None


def read_metrics_csv(path: Path) -> dict[str, float | str]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "metric" not in reader.fieldnames or "value" not in reader.fieldnames:
            raise ValueError(f"Metrics CSV must contain metric,value columns: {path}")
        metrics: dict[str, float | str] = {}
        for row in reader:
            name = (row.get("metric") or "").strip()
            raw_value = (row.get("value") or "").strip()
            if not name:
                continue
            try:
                metrics[name] = float(raw_value)
            except ValueError:
                metrics[name] = raw_value
        return metrics


def read_metrics_json(path: Path) -> dict[str, float | str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("metrics"), dict):
        payload = payload["metrics"]
    if not isinstance(payload, dict):
        raise ValueError(f"Metrics JSON must contain an object: {path}")
    return {
        str(key): value
        for key, value in payload.items()
        if isinstance(value, (int, float, str))
    }


def metrics_for_row(row: dict[str, object]) -> dict[str, float | str]:
    metrics_csv = metrics_csv_for_row(row)
    if metrics_csv is not None:
        return read_metrics_csv(metrics_csv)
    metrics_json = metrics_json_for_row(row)
    if metrics_json is not None:
        return read_metrics_json(metrics_json)
    _, payload = source_payload_for_row(row)
    for inline in (payload.get("metrics"), payload.get("metrics_summary")):
        if isinstance(inline, dict):
            return {
                str(key): value
                for key, value in inline.items()
                if isinstance(value, (int, float, str))
            }
    return {}


def metric_float(values: dict[str, object], name: str) -> float:
    value = values.get(name, math.nan)
    return float(value) if isinstance(value, (int, float)) else math.nan


def family_for_row(raw_row: dict[str, object], controller_id: str) -> str:
    category = str(raw_row.get("category", ""))
    if category in CATEGORY_FAMILY:
        return CATEGORY_FAMILY[category]
    # Compatibility for an explicitly supplied historical status file.
    legacy = {
        "official_pid": "PID族",
        "official_pid_yaw_authority_mapped": "PID族",
        "px4ctrl": "工程基线",
    }
    return legacy.get(controller_id, "工程基线")


def current_rows(status_path: Path) -> list[dict[str, object]]:
    payload = json.loads(status_path.read_text(encoding="utf-8"))
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError(f"Status JSON has no rows array: {status_path}")
    normalized: list[dict[str, object]] = []
    for raw_row in rows:
        if not isinstance(raw_row, dict):
            continue
        controller_id = str(raw_row.get("scheme_id") or raw_row.get("controller_id") or "")
        if not controller_id:
            raise ValueError(f"Status row has no scheme_id/controller_id: {status_path}")
        row = dict(raw_row)
        row["controller_id"] = controller_id
        row["family"] = family_for_row(row, controller_id)
        row["status_class"] = status_class(row.get("status"))
        normalized.append(row)
    return normalized


def build(status_path: Path, output: Path) -> dict[str, object]:
    rows = [row for row in current_rows(status_path) if row["status_class"] == "accepted"]
    records: list[dict[str, object]] = []
    for row in rows:
        controller_id = str(row["controller_id"])
        family = str(row["family"])
        metrics = metrics_for_row(row)
        record: dict[str, object] = {
            "controller_id": controller_id,
            "family": family,
            "family_slug": FAMILY_SLUG[family],
            "family_dir": FAMILY_DIR[family],
            "family_index": FAMILY_ORDER.index(family) + 1,
            "raw_csv": raw_csv_for_row(row).resolve().as_posix(),
        }
        for key in METRIC_KEYS:
            value = metric_float(metrics, key)
            if key == "terminal_position_error_m" and math.isnan(value):
                value = metric_float(metrics, "terminal_position_error_norm_m")
            if key == "max_position_error_m" and math.isnan(value):
                value = metric_float(metrics, "maximum_position_error_norm_m")
            if key == "position_rmse_m" and math.isnan(value):
                value = metric_float(row, "position_rmse_m")
            if key == "terminal_position_error_m" and math.isnan(value):
                value = metric_float(row, "terminal_position_error_norm_m")
            record[key] = "" if math.isnan(value) else repr(value)
        records.append(record)

    if not records:
        raise ValueError("Current catalog accepted index is empty")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    return {"controller_count": len(records), "index": output.resolve().as_posix()}


def build_status_index(status_path: Path, output: Path) -> dict[str, object]:
    rows = current_rows(status_path)
    records: list[dict[str, object]] = []
    for raw_row in rows:
        controller_id = str(raw_row["controller_id"])
        family = str(raw_row["family"])
        rmse = raw_row.get("position_rmse_m")
        terminal = raw_row.get("terminal_position_error_norm_m")
        records.append(
            {
                "controller_id": controller_id,
                "family": family,
                "family_slug": FAMILY_SLUG[family],
                "family_index": FAMILY_ORDER.index(family) + 1,
                "status": str(raw_row.get("status", "")),
                "status_class": str(raw_row["status_class"]),
                "failure_class": "" if raw_row.get("failure_class") in (None, "") else str(raw_row["failure_class"]),
                "effective_source": str(raw_row.get("source_record", "")),
                "position_rmse_m": "" if not isinstance(rmse, (int, float)) else repr(float(rmse)),
                "terminal_position_error_m": "" if not isinstance(terminal, (int, float)) else repr(float(terminal)),
            }
        )
    records.sort(key=lambda item: (int(item["family_index"]), str(item["controller_id"])))
    if not records:
        raise ValueError("Current catalog status index is empty")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    return {"row_count": len(records), "index": output.resolve().as_posix()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--status-json",
        type=Path,
        default=Path("Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_CATALOG_48_CURRENT_STATUS.json"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path(".tmp/chapter10_typlot"))
    args = parser.parse_args(argv)
    status_path = args.status_json if args.status_json.is_absolute() else PROJECT_ROOT / args.status_json
    output_dir = args.output_dir if args.output_dir.is_absolute() else PROJECT_ROOT / args.output_dir
    accepted = build(status_path, output_dir / "accepted_controller_index.csv")
    everything = build_status_index(status_path, output_dir / "g3_status_index.csv")
    print(f"[OK] current catalog accepted={accepted['controller_count']} -> {accepted['index']}")
    print(f"[OK] current catalog all_rows={everything['row_count']} -> {everything['index']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
