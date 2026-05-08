#!/usr/bin/env python3
"""Generate lightweight SVG report figures from a project-standard CSV file."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


CORE_COLUMNS = ["time", "x", "y", "z", "x_ref", "y_ref", "z_ref"]
COLORS = {
    "actual": "#1f77b4",
    "reference": "#d62728",
    "error": "#2ca02c",
    "axis": "#2f3542",
    "grid": "#d7dde8",
    "text": "#1f2937",
}


def read_csv(path: Path) -> dict[str, list[float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [name for name in CORE_COLUMNS if name not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path} missing columns: {', '.join(missing)}")
        data = {name: [] for name in reader.fieldnames or []}
        for row in reader:
            for name in data:
                value = row.get(name, "")
                data[name].append(float(value) if value != "" else math.nan)
        return data


def read_metrics(path: Path | None) -> dict[str, float | str | bool]:
    if path is None or not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    return json.loads(text)


def finite(values: list[float]) -> list[float]:
    return [value for value in values if math.isfinite(value)]


def bounds(*series: list[float], pad_ratio: float = 0.08) -> tuple[float, float]:
    values: list[float] = []
    for item in series:
        values.extend(finite(item))
    if not values:
        return 0.0, 1.0
    low = min(values)
    high = max(values)
    if math.isclose(low, high):
        delta = max(1.0, abs(low) * 0.1)
        return low - delta, high + delta
    pad = (high - low) * pad_ratio
    return low - pad, high + pad


def scale(value: float, low: float, high: float, pixel_low: float, pixel_high: float) -> float:
    if math.isclose(low, high):
        return (pixel_low + pixel_high) / 2
    ratio = (value - low) / (high - low)
    return pixel_low + ratio * (pixel_high - pixel_low)


def escape(text: object) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def line_chart(
    title: str,
    x_values: list[float],
    series: list[tuple[str, list[float], str]],
    x_label: str,
    y_label: str,
) -> str:
    width, height = 920, 520
    left, right, top, bottom = 82, 28, 54, 76
    x_min, x_max = bounds(x_values, pad_ratio=0.02)
    y_min, y_max = bounds(*(values for _, values, _ in series), pad_ratio=0.12)

    def point(x: float, y: float) -> str:
        px = scale(x, x_min, x_max, left, width - right)
        py = scale(y, y_min, y_max, height - bottom, top)
        return f"{px:.2f},{py:.2f}"

    parts = svg_header(width, height, title)
    parts.append(axes(width, height, left, right, top, bottom, x_label, y_label, x_min, x_max, y_min, y_max))
    legend_x = left
    for label, values, color in series:
        points = " ".join(point(x, y) for x, y in zip(x_values, values) if math.isfinite(x) and math.isfinite(y))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.2"/>')
        parts.append(f'<line x1="{legend_x}" y1="30" x2="{legend_x + 28}" y2="30" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{legend_x + 36}" y="35" class="legend">{escape(label)}</text>')
        legend_x += 150
    parts.append(svg_footer())
    return "\n".join(parts)


def xy_chart(title: str, data: dict[str, list[float]]) -> str:
    width, height = 760, 640
    left, right, top, bottom = 82, 28, 58, 78
    x_min, x_max = bounds(data["x"], data["x_ref"])
    y_min, y_max = bounds(data["y"], data["y_ref"])

    def point(x: float, y: float) -> str:
        px = scale(x, x_min, x_max, left, width - right)
        py = scale(y, y_min, y_max, height - bottom, top)
        return f"{px:.2f},{py:.2f}"

    parts = svg_header(width, height, title)
    parts.append(axes(width, height, left, right, top, bottom, "x / m", "y / m", x_min, x_max, y_min, y_max))
    ref_points = " ".join(point(x, y) for x, y in zip(data["x_ref"], data["y_ref"]) if math.isfinite(x) and math.isfinite(y))
    actual_points = " ".join(point(x, y) for x, y in zip(data["x"], data["y"]) if math.isfinite(x) and math.isfinite(y))
    parts.append(f'<polyline points="{ref_points}" fill="none" stroke="{COLORS["reference"]}" stroke-width="2.2"/>')
    parts.append(f'<polyline points="{actual_points}" fill="none" stroke="{COLORS["actual"]}" stroke-width="2.2"/>')
    parts.append(f'<line x1="{left}" y1="32" x2="{left + 28}" y2="32" stroke="{COLORS["reference"]}" stroke-width="3"/>')
    parts.append(f'<text x="{left + 36}" y="37" class="legend">reference</text>')
    parts.append(f'<line x1="{left + 154}" y1="32" x2="{left + 182}" y2="32" stroke="{COLORS["actual"]}" stroke-width="3"/>')
    parts.append(f'<text x="{left + 190}" y="37" class="legend">actual</text>')
    parts.append(svg_footer())
    return "\n".join(parts)


def bar_chart(title: str, metrics: dict[str, float | str | bool]) -> str:
    items = [
        ("RMSE / m", float(metrics.get("position_rmse_m", math.nan))),
        ("Max error / m", float(metrics.get("max_position_error_m", math.nan))),
        ("Steady error / m", float(metrics.get("steady_state_error_m", math.nan))),
    ]
    width, height = 760, 480
    left, right, top, bottom = 92, 36, 64, 94
    max_value = max([value for _, value in items if math.isfinite(value)] or [1.0])
    y_min, y_max = 0.0, max_value * 1.2 if max_value > 0 else 1.0
    parts = svg_header(width, height, title)
    parts.append(axes(width, height, left, right, top, bottom, "metric", "value", 0.0, len(items), y_min, y_max, x_ticks=False))
    bar_gap = 34
    bar_width = (width - left - right - bar_gap * (len(items) + 1)) / len(items)
    for index, (label, value) in enumerate(items):
        x = left + bar_gap + index * (bar_width + bar_gap)
        y = scale(value if math.isfinite(value) else 0.0, y_min, y_max, height - bottom, top)
        bar_height = height - bottom - y
        parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}" fill="{COLORS["actual"]}"/>')
        parts.append(f'<text x="{x + bar_width / 2:.2f}" y="{height - 52}" text-anchor="middle" class="tick">{escape(label)}</text>')
        value_text = "n/a" if not math.isfinite(value) else f"{value:.4g}"
        parts.append(f'<text x="{x + bar_width / 2:.2f}" y="{y - 8:.2f}" text-anchor="middle" class="tick">{value_text}</text>')
    parts.append(svg_footer())
    return "\n".join(parts)


def axes(
    width: int,
    height: int,
    left: int,
    right: int,
    top: int,
    bottom: int,
    x_label: str,
    y_label: str,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    x_ticks: bool = True,
) -> str:
    plot_right = width - right
    plot_bottom = height - bottom
    parts = [
        f'<line x1="{left}" y1="{plot_bottom}" x2="{plot_right}" y2="{plot_bottom}" stroke="{COLORS["axis"]}" stroke-width="1.4"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{plot_bottom}" stroke="{COLORS["axis"]}" stroke-width="1.4"/>',
    ]
    for index in range(6):
        y = top + index * (plot_bottom - top) / 5
        value = y_max - index * (y_max - y_min) / 5
        parts.append(f'<line x1="{left}" y1="{y:.2f}" x2="{plot_right}" y2="{y:.2f}" stroke="{COLORS["grid"]}" stroke-width="0.8"/>')
        parts.append(f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" class="tick">{value:.3g}</text>')
    if x_ticks:
        for index in range(6):
            x = left + index * (plot_right - left) / 5
            value = x_min + index * (x_max - x_min) / 5
            parts.append(f'<text x="{x:.2f}" y="{plot_bottom + 22}" text-anchor="middle" class="tick">{value:.3g}</text>')
    parts.append(f'<text x="{(left + plot_right) / 2:.2f}" y="{height - 18}" text-anchor="middle" class="label">{escape(x_label)}</text>')
    parts.append(f'<text x="22" y="{(top + plot_bottom) / 2:.2f}" text-anchor="middle" class="label" transform="rotate(-90 22 {(top + plot_bottom) / 2:.2f})">{escape(y_label)}</text>')
    return "\n".join(parts)


def svg_header(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text { font-family: Arial, 'Microsoft YaHei', sans-serif; fill: #1f2937; }",
        ".title { font-size: 20px; font-weight: 700; }",
        ".label { font-size: 13px; }",
        ".tick { font-size: 12px; fill: #4b5563; }",
        ".legend { font-size: 13px; fill: #374151; }",
        "</style>",
        '<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width / 2:.2f}" y="26" text-anchor="middle" class="title">{escape(title)}</text>',
    ]


def svg_footer() -> str:
    return "</svg>"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content + "\n", encoding="utf-8")


def write_manifest(output_dir: Path, raw_csv: Path, metrics_path: Path | None, figures: list[str]) -> None:
    lines = [
        "# Figure Manifest",
        "",
        "- Generated by: `scripts/plot_results.py`",
        f"- Raw file: `{raw_csv}`",
        f"- Metrics file: `{metrics_path}`" if metrics_path else "- Metrics file: not provided",
        "- Status: `generated`",
        "",
        "Generated figures:",
        "",
    ]
    lines.extend(f"- `{name}`" for name in figures)
    write_text(output_dir / "figure_manifest.md", "\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_csv", type=Path)
    parser.add_argument("figure_dir", type=Path)
    parser.add_argument("--metrics", type=Path, default=None)
    parser.add_argument("--title-prefix", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = read_csv(args.raw_csv)
    metrics = read_metrics(args.metrics)
    title_prefix = args.title_prefix or args.raw_csv.stem
    position_error = [
        math.sqrt((x - xr) ** 2 + (y - yr) ** 2 + (z - zr) ** 2)
        for x, y, z, xr, yr, zr in zip(data["x"], data["y"], data["z"], data["x_ref"], data["y_ref"], data["z_ref"])
    ]

    figures = {
        "trajectory_xy.svg": xy_chart(f"{title_prefix} trajectory XY", data),
        "altitude_tracking.svg": line_chart(
            f"{title_prefix} altitude tracking",
            data["time"],
            [("z", data["z"], COLORS["actual"]), ("z_ref", data["z_ref"], COLORS["reference"])],
            "time / s",
            "z / m",
        ),
        "position_error.svg": line_chart(
            f"{title_prefix} position error",
            data["time"],
            [("position error", position_error, COLORS["error"])],
            "time / s",
            "error / m",
        ),
    }
    if metrics:
        figures["metrics_summary.svg"] = bar_chart(f"{title_prefix} metrics summary", metrics)

    for name, svg in figures.items():
        write_text(args.figure_dir / name, svg)
    write_manifest(args.figure_dir, args.raw_csv, args.metrics, sorted(figures))
    print(f"Wrote {len(figures)} figures to {args.figure_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
