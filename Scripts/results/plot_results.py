#!/usr/bin/env python3
"""Generate report-ready, dependency-free SVG figures for one result CSV."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


REQUIRED_COLUMNS = ["time", "x", "y", "z", "x_ref", "y_ref", "z_ref"]
CONTROL_COLUMNS = ["u1", "u2", "u3", "u4"]
ATTITUDE_COLUMNS = ["roll", "pitch", "yaw"]
COLORS = {
    "actual": "#1f77b4",
    "reference": "#222222",
    "error": "#d62728",
    "u1": "#1f77b4",
    "u2": "#ff7f0e",
    "u3": "#2ca02c",
    "u4": "#d62728",
    "roll": "#1f77b4",
    "pitch": "#ff7f0e",
    "yaw": "#2ca02c",
    "axis": "#2f3542",
    "grid": "#d7dde8",
    "text": "#1f2937",
}
WIDTH, HEIGHT = 1080, 720
MAX_POINTS = 1400
REPO_ROOT = Path(__file__).resolve().parents[2]


def parse_float(value: str, path: Path, row_number: int, column: str) -> float:
    token = value.strip()
    if token == "":
        return math.nan
    try:
        return float(token)
    except ValueError as exc:
        raise ValueError(f"{path}: row {row_number}, column {column} is not numeric: {value!r}") from exc


def read_csv(path: Path) -> dict[str, list[float]]:
    if not path.is_file():
        raise FileNotFoundError(f"CSV does not exist: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        missing = [name for name in REQUIRED_COLUMNS if name not in headers]
        if missing:
            raise ValueError(f"{path} missing required columns: {', '.join(missing)}")
        data = {name: [] for name in headers}
        for row_number, row in enumerate(reader, start=2):
            for name in headers:
                data[name].append(parse_float(row.get(name, ""), path, row_number, name))
    if not data["time"]:
        raise ValueError(f"CSV contains no data rows: {path}")
    return data


def read_metrics(path: Path | None) -> dict[str, float | str | bool]:
    if path is None:
        return {}
    if not path.is_file():
        raise FileNotFoundError(f"Metrics file does not exist: {path}")
    if path.suffix.lower() == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError(f"Metrics JSON must contain an object: {path}")
        return value
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "metric" not in reader.fieldnames or "value" not in reader.fieldnames:
            raise ValueError(f"Metrics CSV must contain metric,value columns: {path}")
        result: dict[str, float | str | bool] = {}
        for row in reader:
            name = (row.get("metric") or "").strip()
            if not name:
                continue
            raw_value = (row.get("value") or "").strip()
            if raw_value == "":
                result[name] = math.nan
                continue
            try:
                result[name] = float(raw_value)
            except ValueError:
                result[name] = raw_value
        return result


def finite(values: Iterable[float]) -> list[float]:
    return [value for value in values if math.isfinite(value)]


def bounds(*series: Iterable[float], pad_ratio: float = 0.08) -> tuple[float, float]:
    values: list[float] = []
    for item in series:
        values.extend(finite(item))
    if not values:
        return 0.0, 1.0
    low, high = min(values), max(values)
    if math.isclose(low, high):
        delta = max(1.0, abs(low) * 0.1)
        return low - delta, high + delta
    padding = (high - low) * pad_ratio
    return low - padding, high + padding


def scale(value: float, low: float, high: float, pixel_low: float, pixel_high: float) -> float:
    if math.isclose(low, high):
        return (pixel_low + pixel_high) / 2.0
    return pixel_low + (value - low) * (pixel_high - pixel_low) / (high - low)


def escape(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def sample_indices(length: int, maximum: int = MAX_POINTS) -> list[int]:
    if length <= maximum:
        return list(range(length))
    step = max(1, math.ceil((length - 1) / (maximum - 1)))
    indices = list(range(0, length, step))
    if indices[-1] != length - 1:
        indices.append(length - 1)
    return indices


def svg_header(title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        "<style>",
        'text { font-family: "Times New Roman"; fill: #1f2937; }',
        ".title { font-size: 14pt; font-weight: 700; }",
        ".label { font-size: 12pt; }",
        ".tick { font-size: 10pt; fill: #4b5563; }",
        ".legend { font-size: 12pt; }",
        "</style>",
        '<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{WIDTH / 2:.2f}" y="30" text-anchor="middle" class="title">{escape(title)}</text>',
    ]


def svg_footer(parts: list[str]) -> str:
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def axes(
    parts: list[str],
    left: float,
    right: float,
    top: float,
    bottom: float,
    x_label: str,
    y_label: str,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
) -> None:
    plot_right = WIDTH - right
    plot_bottom = HEIGHT - bottom
    parts.extend(
        [
            f'<line x1="{left}" y1="{plot_bottom}" x2="{plot_right}" y2="{plot_bottom}" stroke="{COLORS["axis"]}" stroke-width="1.2"/>',
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{plot_bottom}" stroke="{COLORS["axis"]}" stroke-width="1.2"/>',
        ]
    )
    for index in range(6):
        y = top + index * (plot_bottom - top) / 5
        value = y_max - index * (y_max - y_min) / 5
        parts.append(f'<line x1="{left}" y1="{y:.2f}" x2="{plot_right}" y2="{y:.2f}" stroke="{COLORS["grid"]}" stroke-width="0.8"/>')
        parts.append(f'<text x="{left - 10:.2f}" y="{y + 4:.2f}" text-anchor="end" class="tick">{value:.3g}</text>')
    for index in range(6):
        x = left + index * (plot_right - left) / 5
        value = x_min + index * (x_max - x_min) / 5
        parts.append(f'<text x="{x:.2f}" y="{plot_bottom + 22:.2f}" text-anchor="middle" class="tick">{value:.3g}</text>')
    parts.append(f'<text x="{(left + plot_right) / 2:.2f}" y="{HEIGHT - 18}" text-anchor="middle" class="label">{escape(x_label)}</text>')
    parts.append(f'<text x="22" y="{(top + plot_bottom) / 2:.2f}" text-anchor="middle" class="label" transform="rotate(-90 22 {(top + plot_bottom) / 2:.2f})">{escape(y_label)}</text>')


def polyline_points(
    x_values: list[float],
    y_values: list[float],
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    left: float,
    top: float,
    plot_width: float,
    plot_height: float,
) -> str:
    points: list[str] = []
    for index in sample_indices(min(len(x_values), len(y_values))):
        x, y = x_values[index], y_values[index]
        if not math.isfinite(x) or not math.isfinite(y):
            continue
        px = scale(x, x_min, x_max, left, left + plot_width)
        py = scale(y, y_min, y_max, top + plot_height, top)
        points.append(f"{px:.2f},{py:.2f}")
    return " ".join(points)


def line_chart(title: str, time: list[float], series: list[tuple[str, list[float], str, str | None]], y_label: str) -> str:
    left, right, top, bottom = 86.0, 42.0, 58.0, 78.0
    plot_width, plot_height = WIDTH - left - right, HEIGHT - top - bottom
    x_min, x_max = bounds(time, pad_ratio=0.02)
    y_min, y_max = bounds(*(values for _, values, _, _ in series), pad_ratio=0.12)
    parts = svg_header(title)
    axes(parts, left, right, top, bottom, "Time (s)", y_label, x_min, x_max, y_min, y_max)
    for label, values, color, dash in series:
        points = polyline_points(time, values, x_min, x_max, y_min, y_max, left, top, plot_width, plot_height)
        dash_attribute = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.0"{dash_attribute}/>')
    legend_x = WIDTH - right - min(260.0, 92.0 * len(series))
    legend_y = top - 22
    for index, (label, _, color, dash) in enumerate(series):
        x = legend_x + index * 92.0
        dash_attribute = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(f'<line x1="{x:.2f}" y1="{legend_y:.2f}" x2="{x + 24:.2f}" y2="{legend_y:.2f}" stroke="{color}" stroke-width="2.0"{dash_attribute}/>')
        parts.append(f'<text x="{x + 30:.2f}" y="{legend_y + 4:.2f}" class="legend">{escape(label)}</text>')
    return svg_footer(parts)


def trajectory_xy(title: str, data: dict[str, list[float]]) -> str:
    left, right, top, bottom = 86.0, 42.0, 58.0, 78.0
    plot_width, plot_height = WIDTH - left - right, HEIGHT - top - bottom
    x_min, x_max = bounds(data["x"], data["x_ref"], pad_ratio=0.08)
    y_min, y_max = bounds(data["y"], data["y_ref"], pad_ratio=0.08)
    parts = svg_header(title)
    axes(parts, left, right, top, bottom, "X Position (m)", "Y Position (m)", x_min, x_max, y_min, y_max)
    reference = polyline_points(data["x_ref"], data["y_ref"], x_min, x_max, y_min, y_max, left, top, plot_width, plot_height)
    actual = polyline_points(data["x"], data["y"], x_min, x_max, y_min, y_max, left, top, plot_width, plot_height)
    parts.append(f'<polyline points="{reference}" fill="none" stroke="{COLORS["reference"]}" stroke-width="1.5" stroke-dasharray="6,4"/>')
    parts.append(f'<polyline points="{actual}" fill="none" stroke="{COLORS["actual"]}" stroke-width="2.0"/>')
    legend_x = WIDTH - right - 190
    legend_y = top - 22
    for index, (label, color, dash) in enumerate((("Reference", COLORS["reference"], " stroke-dasharray=\"6,4\""), ("Actual", COLORS["actual"], ""))):
        x = legend_x + index * 92
        parts.append(f'<line x1="{x}" y1="{legend_y}" x2="{x + 24}" y2="{legend_y}" stroke="{color}" stroke-width="2.0"{dash}/>')
        parts.append(f'<text x="{x + 30}" y="{legend_y + 4}" class="legend">{label}</text>')
    return svg_footer(parts)


def position_error_chart(title: str, data: dict[str, list[float]]) -> str:
    error = [
        math.sqrt((x - xr) ** 2 + (y - yr) ** 2 + (z - zr) ** 2)
        if all(math.isfinite(value) for value in (x, y, z, xr, yr, zr))
        else math.nan
        for x, y, z, xr, yr, zr in zip(data["x"], data["y"], data["z"], data["x_ref"], data["y_ref"], data["z_ref"])
    ]
    return line_chart(title, data["time"], [("Position error", error, COLORS["error"], None)], "Error (m)")


def write_svg(output_path: Path | str, content: str) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return path


def generate_trajectory_xy(csv_data: dict[str, list[float]], output_path: Path | str, *, title: str = "Trajectory XY") -> Path:
    """Write the XY top-view trajectory SVG required by the Chapter 10 workflow."""
    return write_svg(output_path, trajectory_xy(title, csv_data))


def generate_altitude_z(csv_data: dict[str, list[float]], output_path: Path | str, *, title: str = "Altitude Tracking") -> Path:
    """Write the actual/reference altitude tracking SVG."""
    return write_svg(
        output_path,
        line_chart(
            title,
            csv_data["time"],
            [("z", csv_data["z"], COLORS["actual"], None), ("z_ref", csv_data["z_ref"], COLORS["reference"], "6,4")],
            "Position (m)",
        ),
    )


def generate_position_error(csv_data: dict[str, list[float]], output_path: Path | str, *, title: str = "Position Error") -> Path:
    """Write the Euclidean position-error SVG."""
    return write_svg(output_path, position_error_chart(title, csv_data))


def generate_control_input(csv_data: dict[str, list[float]], output_path: Path | str, *, title: str = "Control Input") -> Path:
    """Write the four-channel control-input SVG."""
    return write_svg(
        output_path,
        line_chart(title, csv_data["time"], [(name, csv_data[name], COLORS[name], None) for name in CONTROL_COLUMNS], "Command"),
    )


def metrics_summary(metrics: dict[str, float | str | bool]) -> dict[str, float | str | bool]:
    selected = {}
    for name in ("position_rmse_m", "terminal_position_error_m", "control_energy", "max_position_error_m", "duration_s"):
        if name in metrics:
            selected[name] = metrics[name]
    return selected


def project_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def write_manifest(output_dir: Path, raw_csv: Path, metrics_path: Path | None, controller_id: str, scene_id: str, figures: list[dict[str, str]], metrics: dict[str, float | str | bool]) -> None:
    manifest = {
        "schema": "mosim.plot_results.v1",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "controller_id": controller_id,
        "scene_id": scene_id,
        "raw_csv": project_path(raw_csv),
        "metrics_json": project_path(metrics_path) if metrics_path and metrics_path.suffix.lower() == ".json" else None,
        "metrics_csv": project_path(metrics_path) if metrics_path and metrics_path.suffix.lower() != ".json" else None,
        "figures": figures,
        "key_metrics": metrics_summary(metrics),
    }
    path = output_dir / "figure_manifest.json"
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"[OK] 已生成: {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_csv", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--metrics", type=Path, default=None)
    parser.add_argument("--controller-id", default=None)
    parser.add_argument("--scene-id", default="climbpath50s")
    parser.add_argument("--figures", default=None, help="Comma-separated subset, e.g. trajectory_xy")
    parser.add_argument("--title-prefix", default=None, help="Backward-compatible title prefix")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print("[INFO] plot_results.py - 开始执行")
    data = read_csv(args.raw_csv)
    metrics = read_metrics(args.metrics)
    controller_id = args.controller_id or args.raw_csv.parent.parent.parent.name
    title_prefix = args.title_prefix or f"{controller_id} {args.scene_id}"
    requested = {name.strip() for name in args.figures.split(",")} if args.figures else {"trajectory_xy", "altitude_z", "position_error", "control_input"}
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[dict[str, str]] = []

    builders = {
        "trajectory_xy": ("trajectory_xy.svg", lambda path: generate_trajectory_xy(data, path, title=f"{title_prefix} trajectory XY")),
        "altitude_z": ("altitude_z.svg", lambda path: generate_altitude_z(data, path, title=f"{title_prefix} altitude tracking")),
        "position_error": ("position_error.svg", lambda path: generate_position_error(data, path, title=f"{title_prefix} position error")),
        "control_input": ("control_input.svg", lambda path: generate_control_input(data, path, title=f"{title_prefix} control input")),
        "attitude": ("attitude.svg", lambda: line_chart(f"{title_prefix} attitude", data["time"], [(name, data[name], COLORS[name], None) for name in ATTITUDE_COLUMNS], "Angle (rad)")),
    }
    for figure_type in ("trajectory_xy", "altitude_z", "position_error", "control_input", "attitude"):
        if figure_type not in requested:
            continue
        if figure_type == "control_input" and not all(name in data for name in CONTROL_COLUMNS):
            print("[WARN] control_input.svg skipped: CSV does not contain u1,u2,u3,u4")
            continue
        if figure_type == "attitude" and not all(name in data for name in ATTITUDE_COLUMNS):
            print("[WARN] attitude.svg skipped: CSV does not contain roll,pitch,yaw")
            continue
        filename, builder = builders[figure_type]
        path = output_dir / filename
        if figure_type == "attitude":
            write_svg(path, builder())
        else:
            builder(path)
        print(f"[OK] 已生成: {path}")
        generated.append({"file": filename, "type": figure_type})

    write_manifest(output_dir, args.raw_csv, args.metrics, controller_id, args.scene_id, generated, metrics)
    print(f"[DONE] plot_results.py - 完成，共生成 {len(generated) + 1} 个文件")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(2)
