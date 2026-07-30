#!/usr/bin/env python3
"""Generate the Chapter 10 accepted-controller status matrix as hand-written SVG."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTROLLER_FAMILY = {
    "official_pid": "PID族",
    "official_pid_yaw_authority_mapped": "PID族",
    "lqr_baseline": "线性/鲁棒族",
    "lqg": "线性/鲁棒族",
    "lqi": "线性/鲁棒族",
    "h_2_state_feedback": "线性/鲁棒族",
    "backstepping_baseline": "非线性/自适应族",
    "adaptive_backstepping": "非线性/自适应族",
    "feedback_linearization": "非线性/自适应族",
    "ndi": "非线性/自适应族",
    "passivity_based_control": "非线性/自适应族",
    "integral_smc": "滑模族",
    "terminal_smc": "滑模族",
    "nonsingular_terminal_smc": "滑模族",
    "adaptive_smc": "滑模族",
    "fuzzy_smc": "滑模族",
    "ilqr": "优化/预测族",
    "mppi": "优化/预测族",
    "explicit_gain_scheduled_mpc": "优化/预测族",
    "robust_mpc": "优化/预测族",
    "tube_mpc": "优化/预测族",
    "se_3_basic": "几何/微分平坦族",
    "dfbc_basic": "几何/微分平坦族",
    "dfbc_high_order": "几何/微分平坦族",
    "dfbc_high_order_body_rate": "几何/微分平坦族",
    "dfbc_smooth_robust": "几何/微分平坦族",
    "dfbc_smooth_robust_body_rate": "几何/微分平坦族",
    "px4ctrl": "工程基线",
}
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


def escape(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def resolve_project_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def family_for(controller_id: str) -> str:
    return CONTROLLER_FAMILY.get(controller_id, "未分类")


def family_sort_key(family: str) -> int:
    try:
        return FAMILY_ORDER.index(family)
    except ValueError:
        return len(FAMILY_ORDER)


def status_class(value: object) -> str:
    raw = str(value).strip().lower()
    if raw in {"pass", "accepted"}:
        return "accepted"
    if raw in {"not_run", "pending", "skipped"}:
        return "not_run"
    return "executed_blocked"


def load_accepted_rows(status_path: Path) -> list[dict[str, Any]]:
    if not status_path.is_file():
        raise FileNotFoundError(f"Status JSON does not exist: {status_path}")
    payload = json.loads(status_path.read_text(encoding="utf-8"))
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError(f"Status JSON has no rows array: {status_path}")
    accepted: list[dict[str, Any]] = []
    for raw_row in rows:
        if not isinstance(raw_row, dict) or status_class(raw_row.get("status")) != "accepted":
            continue
        row = dict(raw_row)
        controller_id = str(row.get("controller_id", ""))
        if not controller_id:
            raise ValueError(f"Accepted status row has no controller_id: {status_path}")
        row["family"] = family_for(controller_id)
        row["status_class"] = "accepted"
        accepted.append(row)
    return sorted(accepted, key=lambda row: (family_sort_key(str(row["family"])), str(row["controller_id"])))


def metrics_path_for_row(row: dict[str, Any]) -> Path:
    locator = row.get("effective_run_record")
    if not locator:
        raise ValueError(f"{row.get('controller_id', 'unknown')} has no effective_run_record")
    record_path = resolve_project_path(str(locator))
    if not record_path.is_file():
        raise FileNotFoundError(f"RUN_RECORD does not exist: {record_path}")
    payload = json.loads(record_path.read_text(encoding="utf-8"))
    for artifact in payload.get("artifact_refs", []):
        candidate = str(artifact.get("path", ""))
        if candidate.replace("\\", "/").endswith("/metrics/metrics.csv"):
            path = resolve_project_path(candidate)
            if path.is_file():
                return path
    fallback = record_path.parent / "metrics" / "metrics.csv"
    if fallback.is_file():
        return fallback
    raise FileNotFoundError(f"Metrics CSV not found for {row['controller_id']}: {fallback}")


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


def metric_float(metrics: dict[str, float | str], name: str) -> float:
    value = metrics.get(name, math.nan)
    return float(value) if isinstance(value, (int, float)) else math.nan


def row_metrics(row: dict[str, Any]) -> dict[str, float | str]:
    return read_metrics_csv(metrics_path_for_row(row))


def status_icon_svg(status: str, x: float, y: float) -> str:
    if status == "accepted":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#2ca02c"/>'
    if status == "not_run":
        return (
            f'<rect x="{x - 6:.1f}" y="{y - 7:.1f}" width="4" height="14" fill="#999999"/>'
            f'<rect x="{x + 2:.1f}" y="{y - 7:.1f}" width="4" height="14" fill="#999999"/>'
        )
    return (
        f'<path d="M{x - 6:.1f},{y - 6:.1f} L{x + 6:.1f},{y + 6:.1f} '
        f'M{x - 6:.1f},{y + 6:.1f} L{x + 6:.1f},{y - 6:.1f}" '
        'stroke="#d62728" stroke-width="2" fill="none"/>'
    )


def render_status_matrix(rows: list[dict[str, Any]], output: Path) -> None:
    width, row_height, header_height, bottom = 800, 40, 100, 36
    group_breaks = sum(1 for index, row in enumerate(rows) if index and row["family"] != rows[index - 1]["family"])
    height = header_height + len(rows) * row_height + group_breaks * 8 + bottom
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        'text { font-family: "Times New Roman"; fill: #1f2937; }',
        ".title { font-size: 16pt; font-weight: 700; }",
        ".header { font-size: 11pt; font-weight: 700; }",
        ".cell { font-size: 11pt; }",
        "</style>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width / 2}" y="30" text-anchor="middle" class="title">G3 Accepted Controller Status Matrix</text>',
        '<text x="34" y="76" class="header">No.</text>',
        '<text x="88" y="76" class="header">Controller</text>',
        '<text x="350" y="76" class="header">Family</text>',
        '<text x="585" y="76" class="header">Status</text>',
        '<text x="700" y="76" class="header">RMSE (m)</text>',
        '<line x1="24" y1="86" x2="776" y2="86" stroke="#6b7280" stroke-width="1.2"/>',
    ]
    y = header_height
    previous_family: str | None = None
    for index, row in enumerate(rows, start=1):
        family = str(row["family"])
        if previous_family is not None and family != previous_family:
            parts.append(f'<line x1="24" y1="{y + 4}" x2="776" y2="{y + 4}" stroke="#9ca3af" stroke-width="1.1"/>')
            y += 8
        center_y = y + row_height / 2
        fill = "#f8fafc" if index % 2 else "#ffffff"
        parts.append(f'<rect x="24" y="{y}" width="752" height="{row_height}" fill="{fill}"/>')
        rmse = row.get("position_rmse_m")
        rmse_value = float(rmse) if isinstance(rmse, (int, float)) and math.isfinite(float(rmse)) else math.nan
        rmse_text = f"{rmse_value:.6f}" if math.isfinite(rmse_value) else "n/a"
        parts.append(f'<text x="34" y="{center_y + 5:.1f}" class="cell">{index}</text>')
        parts.append(f'<text x="88" y="{center_y + 5:.1f}" class="cell">{escape(row["controller_id"])}</text>')
        parts.append(f'<text x="350" y="{center_y + 5:.1f}" class="cell">{escape(family)}</text>')
        parts.append(status_icon_svg(str(row["status_class"]), 610, center_y))
        parts.append(f'<text x="634" y="{center_y + 5:.1f}" class="cell">accepted</text>')
        parts.append(f'<text x="700" y="{center_y + 5:.1f}" class="cell">{rmse_text}</text>')
        y += row_height
        previous_family = family
    parts.extend(
        [
            f'<text x="24" y="{height - 12}" class="cell">Generated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}; accepted rows are G3 effective pass records.</text>',
            "</svg>",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status-json", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print("[INFO] generate_status_matrix.py - 开始执行")
    rows = load_accepted_rows(args.status_json)
    render_status_matrix(rows, args.output)
    print(f"[OK] 已生成: {args.output}")
    print(f"[DONE] generate_status_matrix.py - 完成，共生成 1 个文件，包含 {len(rows)} 个 accepted 控制器")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(2)
