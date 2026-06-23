#!/usr/bin/env python3
"""Summarize Sunray ROS1 control-mode sweep results."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


METRIC_KEYS = [
    "hover_xy_rmse_m",
    "hover_max_xy_m",
    "hover_z_rmse_m",
    "hover_max_abs_z_error_m",
    "landed_xy_span_m",
    "lidar_nonempty_samples",
]
FIGURE8_KEYS = [
    "rmse_xy_m",
    "max_xy_error_m",
    "time_sync_rmse_xy_m",
    "time_sync_max_xy_error_m",
    "span_x_m",
    "span_y_m",
    "center_crossings",
    "sample_count",
]


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(x):
        return None
    return x


def mode_from_dir(path: Path, mission: str) -> str:
    name = path.parent.name
    prefix = f"{mission}_"
    return name[len(prefix):] if name.startswith(prefix) else name


def score_record(record: dict[str, Any]) -> float:
    metrics = record.get("metrics", {})
    fig = metrics.get("figure8") if isinstance(metrics.get("figure8"), dict) else {}
    score = 0.0
    penalties = {
        "hover_xy_rmse_m": 2.0,
        "hover_z_rmse_m": 1.5,
        "landed_xy_span_m": 1.0,
    }
    for key, weight in penalties.items():
        value = as_float(metrics.get(key))
        if value is not None:
            score += weight * value
    for key, weight in {
        "rmse_xy_m": 4.0,
        "max_xy_error_m": 1.0,
        "time_sync_rmse_xy_m": 5.0,
        "time_sync_max_xy_error_m": 1.0,
    }.items():
        value = as_float(fig.get(key))
        if value is not None:
            score += weight * value
    if record.get("status") != "passed":
        score += 100.0
    return score


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--csv-out", required=True)
    args = parser.parse_args()

    root = Path(args.result_root)
    rows: list[dict[str, Any]] = []
    for gate in sorted(root.rglob("SUNRAY_ROS1_NATIVE_MISSION_GATE.json")):
        try:
            payload = json.loads(gate.read_text(encoding="utf-8"))
        except Exception as exc:
            rows.append({"path": str(gate), "status": "blocked_bad_json", "error": str(exc), "score": 999.0})
            continue
        mission = str(payload.get("mission", "unknown"))
        mode = mode_from_dir(gate, mission)
        metrics = payload.get("metrics", {}) if isinstance(payload.get("metrics"), dict) else {}
        fig = metrics.get("figure8") if isinstance(metrics.get("figure8"), dict) else {}
        row: dict[str, Any] = {
            "mission": mission,
            "mode": mode,
            "status": payload.get("status", "unknown"),
            "blockers": payload.get("blockers", []),
            "result_dir": str(gate.parent),
        }
        for key in METRIC_KEYS:
            row[key] = metrics.get(key)
        for key in FIGURE8_KEYS:
            row[f"figure8_{key}"] = fig.get(key)
        row["score"] = score_record({"status": row["status"], "metrics": metrics})
        rows.append(row)

    ranked = sorted(rows, key=lambda r: (str(r.get("mission")), float(r.get("score", 999.0))))
    summary = {
        "schema": "mosim.sunray_ros1_control_mode_sweep_summary.v1",
        "result_root": str(root),
        "records": ranked,
        "best_by_mission": {},
    }
    for mission in sorted({str(r.get("mission")) for r in ranked}):
        mission_rows = [r for r in ranked if r.get("mission") == mission]
        passed = [r for r in mission_rows if r.get("status") == "passed"]
        summary["best_by_mission"][mission] = passed[0] if passed else (mission_rows[0] if mission_rows else None)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    csv_out = Path(args.csv_out)
    fieldnames = [
        "mission", "mode", "status", "score",
        *METRIC_KEYS,
        *[f"figure8_{k}" for k in FIGURE8_KEYS],
        "blockers", "result_dir",
    ]
    with csv_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in ranked:
            flat = dict(row)
            flat["blockers"] = json.dumps(flat.get("blockers", []), ensure_ascii=False)
            writer.writerow(flat)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
