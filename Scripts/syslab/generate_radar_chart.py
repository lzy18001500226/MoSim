#!/usr/bin/env python3
"""Generate a hand-written SVG radar chart for the eight Chapter 10 controller families."""

from __future__ import annotations

import argparse
import math
import statistics
from pathlib import Path
from typing import Any

from generate_status_matrix import FAMILY_ORDER, load_accepted_rows, metric_float, row_metrics


FAMILY_COLORS = {
    "PID族": "#1f77b4",
    "线性/鲁棒族": "#d62728",
    "非线性/自适应族": "#2ca02c",
    "滑模族": "#9467bd",
    "优化/预测族": "#ff7f0e",
    "几何/微分平坦族": "#17becf",
    "学习增强族": "#7f7f7f",
    "工程基线": "#8c564b",
}
DIMENSIONS = [
    ("Position RMSE", "position_rmse_m", 2.0),
    ("Terminal Error", "terminal_position_error_m", 5.0),
    ("Control Energy", "control_energy", None),
    ("Max Error", "max_position_error_m", 10.0),
    ("Compute Efficiency", "compute_efficiency", None),
]


def point(cx: float, cy: float, radius: float, index: int, count: int = 5) -> tuple[float, float]:
    angle = -math.pi / 2 + index * 2 * math.pi / count
    return cx + radius * math.cos(angle), cy + radius * math.sin(angle)


def polygon_points(cx: float, cy: float, radius: float, values: list[float]) -> str:
    coordinates = [point(cx, cy, radius * max(0.0, min(1.0, value)), index) for index, value in enumerate(values)]
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in coordinates)


def finite_median(values: list[float]) -> float:
    finite = [value for value in values if math.isfinite(value)]
    return statistics.median(finite) if finite else math.nan


def lower_is_better(value: float, maximum: float) -> float:
    if not math.isfinite(value) or maximum <= 0:
        return 0.0
    return max(0.0, min(1.0, 1.0 - value / maximum))


def family_scores(rows: list[dict[str, Any]], official_energy: float) -> tuple[list[float], dict[str, float]]:
    if not rows:
        return [0.0] * len(DIMENSIONS), {}
    metrics = [row_metrics(row) for row in rows]
    aggregate = {
        "position_rmse_m": finite_median([metric_float(item, "position_rmse_m") for item in metrics]),
        "terminal_position_error_m": finite_median([metric_float(item, "terminal_position_error_m") for item in metrics]),
        "control_energy": finite_median([metric_float(item, "control_energy") for item in metrics]),
        "max_position_error_m": finite_median([metric_float(item, "max_position_error_m") for item in metrics]),
        "compute_efficiency": 1.0,
    }
    energy_score = lower_is_better(aggregate["control_energy"], official_energy) if math.isfinite(official_energy) else 0.0
    scores = [
        lower_is_better(aggregate["position_rmse_m"], 2.0),
        lower_is_better(aggregate["terminal_position_error_m"], 5.0),
        energy_score,
        lower_is_better(aggregate["max_position_error_m"], 10.0),
        1.0,
    ]
    return scores, aggregate


def render_radar(rows: list[dict[str, Any]], output: Path) -> None:
    width, height = 1600, 1200
    cell_width, cell_height = width / 4, (height - 52) / 2
    official_row = next((row for row in rows if row["controller_id"] == "official_pid"), None)
    official_energy = metric_float(row_metrics(official_row), "control_energy") if official_row else math.nan
    family_rows = {family: [row for row in rows if row["family"] == family] for family in FAMILY_ORDER}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        'text { font-family: "Times New Roman"; fill: #1f2937; }',
        ".title { font-size: 18pt; font-weight: 700; }",
        ".family { font-size: 13pt; font-weight: 700; }",
        ".axis { font-size: 10pt; }",
        ".note { font-size: 9pt; fill: #4b5563; }",
        "</style>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width / 2}" y="32" text-anchor="middle" class="title">G3 Accepted Controller Family Performance Radar</text>',
    ]
    for family_index, family in enumerate(FAMILY_ORDER):
        col, row_index = family_index % 4, family_index // 4
        cell_left, cell_top = col * cell_width, 52 + row_index * cell_height
        cx, cy, radius = cell_left + cell_width / 2, cell_top + 280, 160
        members = family_rows[family]
        scores, aggregate = family_scores(members, official_energy)
        color = FAMILY_COLORS[family]
        parts.append(f'<rect x="{cell_left + 8:.1f}" y="{cell_top + 8:.1f}" width="{cell_width - 16:.1f}" height="{cell_height - 16:.1f}" fill="#ffffff" stroke="#d1d5db"/>')
        parts.append(f'<text x="{cx:.1f}" y="{cell_top + 36:.1f}" text-anchor="middle" class="family">{family}</text>')
        for ring in (0.25, 0.5, 0.75, 1.0):
            parts.append(f'<polygon points="{polygon_points(cx, cy, radius * ring, [1.0] * 5)}" fill="none" stroke="#d1d5db" stroke-width="0.8"/>')
        for dimension_index, (label, _, _) in enumerate(DIMENSIONS):
            x, y = point(cx, cy, radius, dimension_index)
            label_x, label_y = point(cx, cy, radius + 34, dimension_index)
            parts.append(f'<line x1="{cx:.2f}" y1="{cy:.2f}" x2="{x:.2f}" y2="{y:.2f}" stroke="#9ca3af" stroke-width="0.8"/>')
            parts.append(f'<text x="{label_x:.2f}" y="{label_y + 4:.2f}" text-anchor="middle" class="axis">{label}</text>')
        if members:
            parts.append(f'<polygon points="{polygon_points(cx, cy, radius, scores)}" fill="{color}" fill-opacity="0.30" stroke="{color}" stroke-width="2.0"/>')
            stats = (
                f"n={len(members)}; median RMSE={aggregate['position_rmse_m']:.4f} m"
                if math.isfinite(aggregate.get("position_rmse_m", math.nan))
                else f"n={len(members)}; metrics unavailable"
            )
        else:
            parts.append(f'<polygon points="{polygon_points(cx, cy, radius, scores)}" fill="none" stroke="#9ca3af" stroke-width="2.0" stroke-dasharray="6,4"/>')
            stats = "No accepted controller in this family"
        parts.append(f'<text x="{cx:.1f}" y="{cell_top + cell_height - 38:.1f}" text-anchor="middle" class="note">{stats}</text>')
        parts.append(f'<text x="{cx:.1f}" y="{cell_top + cell_height - 20:.1f}" text-anchor="middle" class="note">Scores: higher is better; compute efficiency is a fixed 1.0 placeholder.</text>')
    parts.append('<text x="20" y="1184" class="note">Metrics use the median of accepted controllers per family. Energy is normalized against Official PID; no runtime or deployment claim is implied.</text>')
    parts.append("</svg>")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-dir", "--metrics-dir", dest="batch_dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print("[INFO] generate_radar_chart.py - 开始执行")
    rows = load_accepted_rows(args.batch_dir / "g3_repair" / "G3_STATUS.json")
    render_radar(rows, args.output)
    print(f"[OK] 已生成: {args.output}")
    print(f"[DONE] generate_radar_chart.py - 完成，共生成 1 个文件，包含 {len(rows)} 个 accepted 控制器")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(2)
