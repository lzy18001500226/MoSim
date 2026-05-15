#!/usr/bin/env python3
"""Summarize scenario configs and available metrics into CSV/Markdown reports."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - fallback keeps WSL/Windows lightweight
    yaml = None


SUMMARY_COLUMNS = [
    "experiment_id",
    "scene_id",
    "controller_id",
    "priority",
    "status",
    "raw_file",
    "metrics_file",
    "duration_s",
    "position_rmse_m",
    "max_position_error_m",
    "steady_state_error_m",
    "settling_time_s",
    "disturbance_peak_error_m",
    "disturbance_recovery_time_s",
    "overshoot_max_pct",
    "control_energy",
    "control_smoothness",
    "saturation_ratio",
    "constraint_violation_count",
    "total_health_score",
    "final_trackability_score",
    "formation_score",
    "baseline_experiment",
    "rmse_improvement_pct",
    "health_score_delta",
    "quality_status",
    "quality_pass",
    "source",
    "evidence_level",
    "notes",
]

def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return {}
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith("[") and value.endswith("]"):
        items = [item.strip() for item in value[1:-1].split(",") if item.strip()]
        return [parse_scalar(item) for item in items]
    try:
        if any(token in value for token in [".", "e", "E"]):
            return float(value)
        return int(value)
    except ValueError:
        return value.strip('"').strip("'")


def read_simple_yaml(path: Path) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip()
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if line.lstrip().startswith("- "):
                continue
            if ":" not in line:
                continue
            indent = len(line) - len(line.lstrip(" "))
            key, value = line.strip().split(":", 1)
            while stack and indent <= stack[-1][0]:
                stack.pop()
            parent = stack[-1][1]
            parsed = parse_scalar(value)
            parent[key] = parsed
            if isinstance(parsed, dict):
                stack.append((indent, parsed))
    if not root:
        raise ValueError(f"YAML root must be a mapping: {path}")
    return root


def read_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        return read_simple_yaml(path)
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def read_metrics(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Metrics root must be an object: {path}")
    return data


def is_active_scenario(config: dict[str, Any]) -> bool:
    if str(config.get("priority", "")) == "visual-review":
        return True
    return bool(config.get("active", True))


def as_float(value: Any) -> float:
    if value is None or value == "":
        return math.nan
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ""
        return f"{value:.6g}"
    return str(value)


def normalize_repo_path(root: Path, value: Any) -> Any:
    if not isinstance(value, str) or not value:
        return value
    path = Path(value)
    if not path.is_absolute():
        return value
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return value


def infer_evidence_level(row: dict[str, Any]) -> str:
    explicit = str(row.get("evidence_level", "") or "")
    if explicit:
        return explicit
    source = str(row.get("source", "") or "")
    metrics_file = str(row.get("metrics_file", "") or "")
    raw_file = str(row.get("raw_file", "") or "")
    if source == "MWORKS_MCP" or "mworks_mcp_" in metrics_file:
        return "real_sysplorer_mcp_smoke"
    if "/raw/reference_official_" in raw_file:
        return "official_reference_generation"
    return ""


def metrics_row(root: Path, metrics_path: Path, source: str) -> dict[str, Any]:
    metrics = read_metrics(metrics_path)
    if metrics is None:
        raise FileNotFoundError(metrics_path)
    row: dict[str, Any] = {key: "" for key in SUMMARY_COLUMNS}
    row.update({
        "experiment_id": metrics_path.stem,
        "scene_id": metrics.get("scene_id", ""),
        "controller_id": metrics.get("controller_id", ""),
        "priority": "",
        "status": "done" if metrics.get("valid", True) else "invalid",
        "raw_file": metrics.get("raw_file", ""),
        "metrics_file": str(metrics_path.relative_to(root)),
        "source": source,
        "evidence_level": metrics.get("evidence_level", ""),
        "notes": "metrics-only evidence",
    })
    for key in SUMMARY_COLUMNS:
        if key in metrics:
            row[key] = metrics[key]
    row["experiment_id"] = metrics_path.stem
    row["metrics_file"] = str(metrics_path.relative_to(root))
    row["source"] = source
    row["evidence_level"] = infer_evidence_level(row)
    row["notes"] = "metrics-only evidence"
    row["raw_file"] = normalize_repo_path(root, row.get("raw_file", ""))
    if "final_trackability_score" in metrics and "total_health_score" not in metrics:
        row["total_health_score"] = 100.0 * as_float(metrics["final_trackability_score"])
    if "formation_score" in metrics and "total_health_score" not in metrics:
        row["total_health_score"] = as_float(metrics["formation_score"])
    return row


def build_rows(
    root: Path,
    scenario_paths: list[Path],
    metrics_globs: list[str],
    *,
    include_inactive: bool = False,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    metrics_by_experiment: dict[str, dict[str, Any]] = {}
    used_metrics_files: set[Path] = set()

    for path in scenario_paths:
        config = read_yaml(path)
        if not include_inactive and not is_active_scenario(config):
            continue
        result = config.get("result", {})
        controller = config.get("controller", {})
        if not isinstance(result, dict):
            result = {}
        if not isinstance(controller, dict):
            controller = {}

        experiment_id = str(config.get("experiment_id", path.stem))
        metrics_rel = str(result.get("metrics_file", ""))
        metrics_path = root / metrics_rel if metrics_rel else Path()
        metrics = read_metrics(metrics_path) if metrics_rel else None

        row: dict[str, Any] = {
            "experiment_id": experiment_id,
            "scene_id": config.get("scene_id", ""),
            "controller_id": config.get("controller_id", ""),
            "priority": config.get("priority", ""),
            "status": "done" if metrics else "pending",
            "raw_file": result.get("raw_file", ""),
            "metrics_file": metrics_rel,
            "baseline_experiment": controller.get("baseline_experiment", ""),
            "source": str(path.relative_to(root)),
            "evidence_level": "",
            "notes": config.get("status_note", ""),
        }

        for key in SUMMARY_COLUMNS:
            if key not in row:
                row[key] = ""

        if metrics:
            for key in SUMMARY_COLUMNS:
                if key in metrics:
                    row[key] = metrics[key]
            row["raw_file"] = normalize_repo_path(root, row.get("raw_file", ""))
            row["metrics_file"] = metrics_rel
            if "final_trackability_score" in metrics and "total_health_score" not in metrics:
                row["total_health_score"] = 100.0 * as_float(metrics["final_trackability_score"])
            if "formation_score" in metrics and "total_health_score" not in metrics:
                row["total_health_score"] = as_float(metrics["formation_score"])
            if not metrics.get("valid", True):
                row["status"] = "invalid"
                row["notes"] = "metrics valid=false"
            row["evidence_level"] = infer_evidence_level(row)
            metrics_by_experiment[experiment_id] = metrics
            used_metrics_files.add(metrics_path.resolve())
        elif not row["notes"]:
            row["notes"] = "metrics missing"
        rows.append(row)

    for pattern in metrics_globs:
        for metrics_path in sorted(root.glob(pattern)):
            if metrics_path.resolve() in used_metrics_files:
                continue
            row = metrics_row(root, metrics_path, source=f"glob:{pattern}")
            rows.append(row)
            metrics_by_experiment[str(row["experiment_id"])] = read_metrics(metrics_path) or {}

    for row in rows:
        baseline_id = str(row.get("baseline_experiment", ""))
        baseline = metrics_by_experiment.get(baseline_id)
        if not baseline:
            continue
        rmse = as_float(row.get("position_rmse_m"))
        baseline_rmse = as_float(baseline.get("position_rmse_m"))
        if math.isfinite(rmse) and math.isfinite(baseline_rmse) and abs(baseline_rmse) > 1e-12:
            row["rmse_improvement_pct"] = 100.0 * (baseline_rmse - rmse) / baseline_rmse
        health = as_float(row.get("total_health_score"))
        baseline_health = as_float(baseline.get("total_health_score"))
        if math.isfinite(health) and math.isfinite(baseline_health):
            row["health_score_delta"] = health - baseline_health

    return sorted(rows, key=lambda item: (str(item["priority"]), str(item["scene_id"]), str(item["controller_id"])))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: format_value(row.get(key, "")) for key in SUMMARY_COLUMNS})


def write_markdown(path: Path, rows: list[dict[str, Any]], csv_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    done = [row for row in rows if row["status"] == "done"]
    pending = [row for row in rows if row["status"] == "pending"]
    invalid = [row for row in rows if row["status"] == "invalid"]
    best = sorted(done, key=lambda row: as_float(row.get("total_health_score")), reverse=True)

    lines = [
        "# Experiment Summary",
        "",
        f"- CSV: `{csv_path}`",
        f"- Total scenarios: `{len(rows)}`",
        f"- Done: `{len(done)}`",
        f"- Pending: `{len(pending)}`",
        f"- Invalid: `{len(invalid)}`",
        "",
        "## Available Results",
        "",
        "| Experiment | Scene | Controller | RMSE | Health | Quality | Status |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for row in best:
        lines.append(
            "| {experiment_id} | {scene_id} | {controller_id} | {rmse} | {health} | {quality} | {status} |".format(
                experiment_id=row["experiment_id"],
                scene_id=row["scene_id"],
                controller_id=row["controller_id"],
                rmse=format_value(row.get("position_rmse_m")),
                health=format_value(row.get("total_health_score")),
                quality=format_value(row.get("quality_status")),
                status=row["status"],
            )
        )

    attention = [
        row for row in rows
        if row["status"] == "done" and format_value(row.get("quality_status")) not in {"", "pass"}
    ]
    lines.extend([
        "",
        "## Needs Attention",
        "",
        "| Experiment | Scene | Controller | Quality | Notes |",
        "|---|---|---|---|---|",
    ])
    if not attention:
        lines.append("| - | - | - | - | No completed result currently needs iteration. |")
    else:
        for row in sorted(attention, key=lambda item: (str(item["scene_id"]), str(item["controller_id"]))):
            lines.append(
                "| {experiment_id} | {scene_id} | {controller_id} | {quality} | {notes} |".format(
                    experiment_id=row["experiment_id"],
                    scene_id=row["scene_id"],
                    controller_id=row["controller_id"],
                    quality=format_value(row.get("quality_status")),
                    notes=format_value(row.get("notes")),
                )
            )

    lines.extend([
        "",
        "## Evidence Levels",
        "",
        "| Experiment | Source | Evidence Level | Raw File |",
        "|---|---|---|---|",
    ])
    for row in sorted(done, key=lambda item: (str(item.get("source", "")), str(item.get("evidence_level", "")), str(item["experiment_id"]))):
        lines.append(
            "| {experiment_id} | {source} | {evidence_level} | `{raw_file}` |".format(
                experiment_id=row["experiment_id"],
                source=format_value(row.get("source")),
                evidence_level=format_value(row.get("evidence_level")),
                raw_file=format_value(row.get("raw_file")),
            )
        )

    lines.extend([
        "",
        "## Pending Results",
        "",
        "| Experiment | Scene | Controller | Metrics File | Notes |",
        "|---|---|---|---|---|",
    ])
    for row in pending:
        lines.append(
            f"| {row['experiment_id']} | {row['scene_id']} | {row['controller_id']} | `{row['metrics_file']}` | {row['notes']} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenarios-dir", type=Path, default=Path("scenarios"))
    parser.add_argument(
        "--include-metrics-glob",
        action="append",
        default=[],
        help="Include metrics JSON files not referenced by scenarios, e.g. results/robustness/**/*.json",
    )
    parser.add_argument("--csv", type=Path, default=Path("results/summaries/experiment_summary/experiment_summary.csv"))
    parser.add_argument("--markdown", type=Path, default=Path("results/summaries/experiment_summary/experiment_summary.md"))
    parser.add_argument(
        "--include-inactive",
        action="store_true",
        help="Include scenarios marked active: false. Default summaries focus on the current formal matrix.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path.cwd()
    scenario_root = root / args.scenarios_dir
    scenario_paths = sorted(scenario_root.glob("**/*.yaml"))
    if not scenario_paths:
        raise FileNotFoundError(f"No scenario YAML files found under {scenario_root}")
    rows = build_rows(root, scenario_paths, args.include_metrics_glob, include_inactive=args.include_inactive)
    write_csv(root / args.csv, rows)
    write_markdown(root / args.markdown, rows, args.csv)
    print(f"Summary CSV: {args.csv}")
    print(f"Summary Markdown: {args.markdown}")
    print(f"Scenarios: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
