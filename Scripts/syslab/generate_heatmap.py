#!/usr/bin/env python3
"""Generate a hand-written SVG RMSE heatmap for G3 accepted controllers."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from generate_status_matrix import FAMILY_ORDER, escape, load_accepted_rows, metric_float, row_metrics


RMSE_COLORS = {
    "lt_0_2": "#2ca02c",
    "lt_0_5": "#7fbc41",
    "lt_1_0": "#ffd92f",
    "lt_2_0": "#ff7f0e",
    "ge_2_0": "#d62728",
    "missing": "#cccccc",
}


def rmse_to_color(rmse: float) -> str:
    if not math.isfinite(rmse):
        return RMSE_COLORS["missing"]
    if rmse < 0.2:
        return RMSE_COLORS["lt_0_2"]
    if rmse < 0.5:
        return RMSE_COLORS["lt_0_5"]
    if rmse < 1.0:
        return RMSE_COLORS["lt_1_0"]
    if rmse < 2.0:
        return RMSE_COLORS["lt_2_0"]
    return RMSE_COLORS["ge_2_0"]


def render_heatmap(rows: list[dict[str, object]], output: Path) -> None:
    width, row_height, top, bottom = 900, 30, 94, 40
    group_breaks = sum(1 for index, row in enumerate(rows) if index and row["family"] != rows[index - 1]["family"])
    height = top + len(rows) * row_height + group_breaks * 6 + bottom
    name_x, family_x, cell_x, cell_width, colorbar_x = 30, 260, 460, 230, 750
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        'text { font-family: "Times New Roman"; fill: #1f2937; }',
        ".title { font-size: 16pt; font-weight: 700; }",
        ".header { font-size: 11pt; font-weight: 700; }",
        ".cell { font-size: 10pt; }",
        "</style>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width / 2}" y="30" text-anchor="middle" class="title">G3 Accepted Controller RMSE Heatmap</text>',
        f'<text x="{name_x}" y="72" class="header">Controller</text>',
        f'<text x="{family_x}" y="72" class="header">Family</text>',
        f'<text x="{cell_x + cell_width / 2}" y="72" text-anchor="middle" class="header">ClimbPath50s RMSE (m)</text>',
        '<line x1="24" y1="82" x2="716" y2="82" stroke="#6b7280" stroke-width="1.2"/>',
    ]
    y = top
    previous_family: str | None = None
    for index, row in enumerate(rows):
        family = str(row["family"])
        if previous_family is not None and family != previous_family:
            parts.append(f'<line x1="24" y1="{y + 3}" x2="716" y2="{y + 3}" stroke="#9ca3af" stroke-width="1.0"/>')
            y += 6
        metrics = row_metrics(row)
        rmse = metric_float(metrics, "position_rmse_m")
        fill = rmse_to_color(rmse)
        center_y = y + row_height / 2
        text_color = "#111827" if fill not in {RMSE_COLORS["ge_2_0"]} else "#ffffff"
        rmse_text = f"{rmse:.6f}" if math.isfinite(rmse) else "n/a"
        parts.append(f'<rect x="{cell_x}" y="{y}" width="{cell_width}" height="{row_height}" fill="{fill}"/>')
        parts.append(f'<rect x="{cell_x}" y="{y}" width="{cell_width}" height="{row_height}" fill="none" stroke="#ffffff" stroke-width="0.8"/>')
        parts.append(f'<text x="{name_x}" y="{center_y + 4:.1f}" class="cell">{escape(row["controller_id"])}</text>')
        parts.append(f'<text x="{family_x}" y="{center_y + 4:.1f}" class="cell">{escape(family)}</text>')
        parts.append(f'<text x="{cell_x + cell_width / 2}" y="{center_y + 4:.1f}" text-anchor="middle" font-family="Times New Roman" font-size="10pt" fill="{text_color}">{rmse_text}</text>')
        y += row_height
        previous_family = family

    bar_y, bar_height, segment_height = 110, 360, 72
    labels = [">=2.0", "1.0-2.0", "0.5-1.0", "0.2-0.5", "<0.2"]
    colors = [
        RMSE_COLORS["ge_2_0"],
        RMSE_COLORS["lt_2_0"],
        RMSE_COLORS["lt_1_0"],
        RMSE_COLORS["lt_0_5"],
        RMSE_COLORS["lt_0_2"],
    ]
    parts.append(f'<text x="{colorbar_x}" y="88" text-anchor="middle" class="header">RMSE Colorbar</text>')
    for index, (label, color) in enumerate(zip(labels, colors)):
        y0 = bar_y + index * segment_height
        parts.append(f'<rect x="{colorbar_x - 26}" y="{y0}" width="30" height="{segment_height}" fill="{color}"/>')
        parts.append(f'<text x="{colorbar_x + 12}" y="{y0 + segment_height / 2 + 4:.1f}" class="cell">{escape(label)} m</text>')
    parts.append(f'<rect x="{colorbar_x - 26}" y="{bar_y + bar_height + 18}" width="30" height="20" fill="{RMSE_COLORS["missing"]}"/>')
    parts.append(f'<text x="{colorbar_x + 12}" y="{bar_y + bar_height + 33}" class="cell">missing</text>')
    parts.append(f'<text x="24" y="{height - 14}" class="cell">Rows are ordered by controller family; colors encode position RMSE from each effective metrics.csv.</text>')
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
    print("[INFO] generate_heatmap.py - 开始执行")
    status_path = args.batch_dir / "g3_repair" / "G3_STATUS.json"
    rows = load_accepted_rows(status_path)
    render_heatmap(rows, args.output)
    print(f"[OK] 已生成: {args.output}")
    print(f"[DONE] generate_heatmap.py - 完成，共生成 1 个文件，包含 {len(rows)} 个 accepted 控制器")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(2)
