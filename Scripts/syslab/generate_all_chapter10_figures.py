#!/usr/bin/env python3
"""Generate the complete Chapter 10 figure tree from frozen G3 ClimbPath evidence."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from generate_status_matrix import (
    CONTROLLER_FAMILY,
    PROJECT_ROOT,
    load_accepted_rows,
    metric_float,
    metrics_path_for_row,
    read_metrics_csv,
    resolve_project_path,
)


FIGURE_SCRIPT = PROJECT_ROOT / "Scripts" / "results" / "plot_results.py"
COMPARE_SCRIPT = PROJECT_ROOT / "Scripts" / "syslab" / "compare_controllers.jl"
STATUS_SCRIPT = PROJECT_ROOT / "Scripts" / "syslab" / "generate_status_matrix.py"
HEATMAP_SCRIPT = PROJECT_ROOT / "Scripts" / "syslab" / "generate_heatmap.py"
RADAR_SCRIPT = PROJECT_ROOT / "Scripts" / "syslab" / "generate_radar_chart.py"
COMPARISON_GROUPS = {
    "pid_family_comparison": "PID族",
    "linear_family_comparison": "线性/鲁棒族",
    "nonlinear_family_comparison": "非线性/自适应族",
    "smc_family_comparison": "滑模族",
    "mpc_family_comparison": "优化/预测族",
    "geometric_family_comparison": "几何/微分平坦族",
}
TEXT_ARTIFACT_SUFFIXES = {".csv", ".json", ".md", ".svg", ".txt"}


def project_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def raw_csv_for_row(row: dict[str, Any]) -> Path:
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


def run_command(command: list[str], log_lines: list[str]) -> None:
    rendered = " ".join(f'"{part}"' if " " in part else part for part in command)
    print(f"[INFO] {rendered}")
    environment = os.environ.copy()
    # Python children inherit UTF-8 so their Chinese status messages round-trip
    # through the captured output on Windows hosts whose console code page is GBK.
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
    )
    log_lines.extend([f"$ {rendered}", result.stdout.rstrip(), result.stderr.rstrip(), f"exit_code={result.returncode}", ""])
    if result.stdout:
        print(result.stdout.rstrip())
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {rendered}")


def write_analysis_report(output_dir: Path, rows: list[dict[str, Any]], all_row_count: int) -> Path:
    report_path = output_dir / "ANALYSIS_REPORT.md"
    lines = [
        "# Syslab分析汇总报告",
        "",
        f"生成时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## 控制器统计",
        "",
        f"- G3有效记录总数：{all_row_count} 个",
        f"- accepted（有效 pass）控制器：{len(rows)} 个",
        f"- 非 accepted 有效记录：{all_row_count - len(rows)} 个",
        "- 数据边界：本报告仅汇总 G3 的 ClimbPath50s 最小闭环证据，不构成七场景、部署或运行时性能结论。",
        "",
        "## 位置RMSE汇总表",
        "",
        "| 控制器 | 族 | RMSE (m) | 状态 |",
        "|---|---|---:|---|",
    ]
    for row in rows:
        metrics = read_metrics_csv(metrics_path_for_row(row))
        rmse = metric_float(metrics, "position_rmse_m")
        rmse_text = repr(rmse) if math.isfinite(rmse) else "n/a"
        lines.append(f"| {row['controller_id']} | {row['family']} | {rmse_text} | ✅ accepted |")
    lines.extend(["", "## 生成的图表清单", ""])
    for path in sorted(output_dir.rglob("*.svg")):
        lines.append(f"- `{path.relative_to(output_dir).as_posix()}`")
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return report_path


def write_directory_tree(output_dir: Path) -> Path:
    """Write a stable text snapshot of the generated Chapter 10 figure tree."""
    tree_path = output_dir / "DIRECTORY_TREE.txt"
    lines = [f"{output_dir.name}/"]
    for path in sorted(output_dir.rglob("*"), key=lambda value: value.as_posix()):
        relative = path.relative_to(output_dir)
        indent = "  " * (len(relative.parts) - 1)
        suffix = "/" if path.is_dir() else ""
        lines.append(f"{indent}{relative.name}{suffix}")
    tree_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return tree_path


def validate_chapter10_output(output_dir: Path, rows: list[dict[str, Any]], focus: list[str]) -> Path:
    """Validate the generated evidence tree without relying on a rendering library."""
    errors: list[str] = []
    focus_ids = set(focus)
    expected_comparison_figures = {
        "climbpath_rmse_bar.svg",
        "climbpath_trajectory_overlay.svg",
        "control_energy_bar.svg",
        "terminal_error_bar.svg",
    }
    for row in rows:
        controller_id = str(row["controller_id"])
        controller_dir = output_dir / controller_id
        expected = {"trajectory_xy.svg", "figure_manifest.json"}
        if controller_id in focus_ids:
            expected.update({"altitude_z.svg", "position_error.svg", "control_input.svg"})
        missing = sorted(name for name in expected if not (controller_dir / name).is_file())
        if missing:
            errors.append(f"{controller_id}: missing {', '.join(missing)}")
    for directory_name in COMPARISON_GROUPS:
        figures_dir = output_dir / directory_name / "figures"
        missing = sorted(name for name in expected_comparison_figures if not (figures_dir / name).is_file())
        if missing:
            errors.append(f"{directory_name}: missing {', '.join(missing)}")
    for filename in ("controller_status_matrix.svg", "rmse_heatmap.svg", "controller_radar_chart.svg", "ANALYSIS_REPORT.md"):
        if not (output_dir / filename).is_file():
            errors.append(f"top-level: missing {filename}")
    svg_paths = sorted(output_dir.rglob("*.svg"))
    for svg_path in svg_paths:
        try:
            ET.parse(svg_path)
        except ET.ParseError as exc:
            errors.append(f"invalid XML {project_path(svg_path)}: {exc}")
    report_path = output_dir / "ANALYSIS_REPORT.md"
    if report_path.is_file():
        report_text = report_path.read_text(encoding="utf-8")
        for row in rows:
            metrics = read_metrics_csv(metrics_path_for_row(row))
            rmse = metric_float(metrics, "position_rmse_m")
            expected_row = f"| {row['controller_id']} | {row['family']} | {repr(rmse) if math.isfinite(rmse) else 'n/a'} | ✅ accepted |"
            if expected_row not in report_text:
                errors.append(f"ANALYSIS_REPORT missing metric row for {row['controller_id']}")
    validation = {
        "schema": "mosim.syslab_chapter10_validation.v1",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "accepted_controller_count": len(rows),
        "focus_controllers": focus,
        "comparison_directory_count": len(COMPARISON_GROUPS),
        "svg_count": len(svg_paths),
        "svg_xml_well_formed": not any(message.startswith("invalid XML") for message in errors),
        "passed": not errors,
        "errors": errors,
    }
    validation_path = output_dir / "VALIDATION_REPORT.json"
    validation_path.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if errors:
        raise RuntimeError("Chapter 10 output validation failed: " + "; ".join(errors))
    return validation_path


def normalize_text_artifact_newlines(output_dir: Path) -> int:
    """Keep generated evidence text portable and clean under Git on Windows."""
    normalized = 0
    for path in output_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_ARTIFACT_SUFFIXES:
            continue
        contents = path.read_bytes()
        canonical = contents.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        if canonical != contents:
            path.write_bytes(canonical)
            normalized += 1
    return normalized


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--focus-controllers", default="official_pid,px4ctrl")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print("[INFO] generate_all_chapter10_figures.py - 开始执行")
    batch_dir = args.batch_dir if args.batch_dir.is_absolute() else PROJECT_ROOT / args.batch_dir
    output_dir = args.output_dir if args.output_dir.is_absolute() else PROJECT_ROOT / args.output_dir
    status_path = batch_dir / "g3_repair" / "G3_STATUS.json"
    payload = json.loads(status_path.read_text(encoding="utf-8"))
    all_rows = payload.get("rows", [])
    if not isinstance(all_rows, list):
        raise ValueError(f"Status JSON has no rows array: {status_path}")
    rows = load_accepted_rows(status_path)
    focus = [value.strip() for value in args.focus_controllers.split(",") if value.strip()]
    accepted_ids = {str(row["controller_id"]) for row in rows}
    unknown_focus = [controller_id for controller_id in focus if controller_id not in accepted_ids]
    if unknown_focus:
        raise ValueError(f"Focus controllers are not accepted G3 rows: {', '.join(unknown_focus)}")
    output_dir.mkdir(parents=True, exist_ok=True)
    log_lines = ["# Chapter 10 Figure Generation Log", ""]

    for row in rows:
        controller_id = str(row["controller_id"])
        command = [
            sys.executable,
            str(FIGURE_SCRIPT),
            str(raw_csv_for_row(row)),
            str(output_dir / controller_id),
            "--metrics",
            str(metrics_path_for_row(row)),
            "--controller-id",
            controller_id,
            "--scene-id",
            "climbpath50s",
        ]
        if controller_id not in focus:
            command.extend(["--figures", "trajectory_xy"])
        run_command(command, log_lines)

    julia = shutil.which("julia")
    if not julia:
        raise FileNotFoundError("Julia executable was not found; cannot generate required controller comparisons")
    for directory_name, family in COMPARISON_GROUPS.items():
        group_rows = [row for row in rows if row["family"] == family]
        if not group_rows:
            continue
        command = [julia, str(COMPARE_SCRIPT), "--climbpath"]
        command.extend(f"{row['controller_id']}={raw_csv_for_row(row)}" for row in group_rows)
        command.extend(["--output-dir", str(output_dir / directory_name)])
        run_command(command, log_lines)

    run_command([sys.executable, str(STATUS_SCRIPT), "--status-json", str(status_path), "--output", str(output_dir / "controller_status_matrix.svg")], log_lines)
    run_command([sys.executable, str(HEATMAP_SCRIPT), "--batch-dir", str(batch_dir), "--output", str(output_dir / "rmse_heatmap.svg")], log_lines)
    run_command([sys.executable, str(RADAR_SCRIPT), "--batch-dir", str(batch_dir), "--output", str(output_dir / "controller_radar_chart.svg")], log_lines)

    log_path = output_dir / "GENERATION_LOG.txt"
    log_path.write_text("\n".join(log_lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    report_path = write_analysis_report(output_dir, rows, len(all_rows))
    validation_path = validate_chapter10_output(output_dir, rows, focus)
    tree_path = write_directory_tree(output_dir)
    normalized_count = normalize_text_artifact_newlines(output_dir)
    if normalized_count:
        print(f"[INFO] 已规范 {normalized_count} 个文本产物的换行符为 LF")
    print(f"[OK] 已生成: {log_path}")
    print(f"[OK] 已生成: {report_path}")
    print(f"[OK] 已生成: {tree_path}")
    print(f"[OK] 已生成: {validation_path}")
    print(f"[DONE] generate_all_chapter10_figures.py - 完成，共生成 {len(rows)} 个控制器目录和 {len(COMPARISON_GROUPS)} 个族内对比目录")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(2)
