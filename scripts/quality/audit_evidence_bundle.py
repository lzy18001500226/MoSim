#!/usr/bin/env python3
"""Audit scenario evidence bundles for report-ready MWORKS results."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

try:
    from run_mworks_scenario import ROOT, default_result_base, read_yaml
except ImportError:  # pragma: no cover
    ROOT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(ROOT / "scripts" / "mworks"))
    from run_mworks_scenario import default_result_base, read_yaml  # type: ignore


def repo_path(value: Any) -> Path:
    path = Path(str(value))
    return path if path.is_absolute() else ROOT / path


def rel(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_read_error": str(exc)}
    return data if isinstance(data, dict) else {"_read_error": "JSON root is not an object"}


def as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def count_csv_rows(path: Path) -> int | None:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return sum(1 for _ in csv.DictReader(handle))
    except Exception:
        return None


def graphical_model_declared(model_file: Path, model_name: str) -> bool:
    if not model_file.exists():
        return False
    text = model_file.read_text(encoding="utf-8", errors="replace")
    short_name = model_name.rsplit(".", 1)[-1]
    if "." in model_name:
        return bool(re.search(rf"^\s*model\s+{re.escape(short_name)}\b", text, re.MULTILINE))
    return bool(re.search(rf"^model\s+{re.escape(short_name)}\b", text, re.MULTILINE))


def scenario_paths(config: dict[str, Any], scenario_path: Path) -> dict[str, Path | None]:
    experiment_id = str(config.get("experiment_id", scenario_path.stem))
    result = config.get("result", {})
    result = result if isinstance(result, dict) else {}
    default_base = ROOT / default_result_base(config, experiment_id)
    return {
        "raw_file": repo_path(result["raw_file"]) if result.get("raw_file") else default_base / "raw" / f"{experiment_id}.csv",
        "metrics_file": repo_path(result["metrics_file"]) if result.get("metrics_file") else default_base / "metrics" / f"{experiment_id}.json",
        "figure_dir": repo_path(result["figure_dir"]) if result.get("figure_dir") else default_base / "figures",
        "replay_file": repo_path(result["replay_file"]) if result.get("replay_file") else default_base / "replay" / f"{experiment_id}.json",
        "mcp_log": repo_path(result["mcp_log"]) if result.get("mcp_log") else None,
    }


def audit_one(scenario_path: Path) -> dict[str, Any]:
    config = read_yaml(scenario_path)
    experiment_id = str(config.get("experiment_id", scenario_path.stem))
    scene_id = str(config.get("scene_id", ""))
    controller_id = str(config.get("controller_id", ""))
    evidence_level = str(config.get("evidence_level", ""))
    priority = str(config.get("priority", ""))
    active = bool(config.get("active", True))
    paths = scenario_paths(config, scenario_path)
    issues: list[str] = []
    warnings: list[str] = []

    raw_file = paths["raw_file"]
    metrics_file = paths["metrics_file"]
    figure_dir = paths["figure_dir"]
    replay_file = paths["replay_file"]
    mcp_log = paths["mcp_log"]

    metrics: dict[str, Any] = {}
    if metrics_file and metrics_file.exists():
        metrics = read_json(metrics_file)
        if metrics.get("_read_error"):
            issues.append(f"metrics unreadable: {metrics['_read_error']}")
    else:
        issues.append("missing metrics_file")

    row_count = count_csv_rows(raw_file) if raw_file and raw_file.exists() else None
    if not raw_file or not raw_file.exists():
        issues.append("missing raw_file")
    elif row_count is None or row_count <= 10:
        issues.append(f"raw row_count too small: {row_count}")

    if not replay_file or not replay_file.exists():
        warnings.append("missing replay_file")

    figure_count = 0
    if figure_dir and figure_dir.exists():
        figure_count = len([p for p in figure_dir.iterdir() if p.is_file() and p.suffix.lower() in {".svg", ".png", ".jpg", ".jpeg"}])
    else:
        warnings.append("missing figure_dir")
    if figure_count < 3 and "smoke" not in evidence_level and "smoke" not in experiment_id:
        warnings.append(f"few report figures: {figure_count}")

    if mcp_log is None:
        warnings.append("missing mcp_log field")
    elif not mcp_log.exists():
        issues.append("missing mcp_log file")

    quality_status = str(metrics.get("quality_status", ""))
    role = "pass_evidence"
    if "smoke" not in evidence_level and "smoke" not in experiment_id:
        if quality_status == "needs_iteration":
            role = "boundary_or_negative_evidence"
            warnings.append("quality_status is needs_iteration; usable only as boundary/ablation evidence, not as completed controller claim")
        elif quality_status != "pass":
            issues.append(f"quality_status is not pass: {quality_status or '<missing>'}")
    elif quality_status not in {"smoke_only", "pass"}:
        warnings.append(f"unexpected smoke quality_status: {quality_status or '<missing>'}")

    valid = metrics.get("valid")
    if valid is not True and metrics:
        issues.append(f"metrics valid is not true: {valid}")

    source = str(metrics.get("source", ""))
    if metrics and source != "MWORKS_MCP":
        warnings.append(f"metrics source is not MWORKS_MCP: {source or '<missing>'}")

    controller = config.get("controller", {})
    if isinstance(controller, dict) and controller.get("sysblock_controller_file"):
        graphical_model = str(controller.get("graphical_sysblock_model", "") or "")
        graphical_file_value = controller.get("graphical_sysblock_file")
        if not graphical_model:
            issues.append("missing controller.graphical_sysblock_model")
        if not graphical_file_value:
            issues.append("missing controller.graphical_sysblock_file")
        else:
            graphical_file = repo_path(graphical_file_value)
            if not graphical_file.exists():
                issues.append(f"missing graphical_sysblock_file: {rel(graphical_file)}")
            elif graphical_model and not graphical_model_declared(graphical_file, graphical_model):
                issues.append(f"graphical_sysblock_model not declared in file: {graphical_model}")

    planning_acceptance = config.get("planning_acceptance", {})
    if isinstance(planning_acceptance, dict) and planning_acceptance:
        report_value = planning_acceptance.get("trackability_report")
        report_path = repo_path(report_value) if report_value else None
        report = read_json(report_path) if report_path and report_path.exists() else {}
        if not report_path or not report_path.exists():
            issues.append("missing planning_acceptance.trackability_report")
        elif report.get("_read_error"):
            issues.append(f"planning_acceptance report unreadable: {report['_read_error']}")
        else:
            if planning_acceptance.get("require_local_planning") and report.get("local_planning_enabled") is not True:
                issues.append("planning_acceptance local_planning_enabled is not true")
            if planning_acceptance.get("require_ego_optimizer"):
                if report.get("ego_planner_enabled") is not True:
                    issues.append("planning_acceptance ego_planner_enabled is not true")
                if report.get("ego_optimizer_accepted") is not True:
                    issues.append("planning_acceptance ego_optimizer_accepted is not true")
            if planning_acceptance.get("require_collision_free"):
                if as_int(report.get("collision_count")) not in {0, None}:
                    issues.append(f"planning_acceptance collision_count={report.get('collision_count')}")
                if as_int(report.get("inflated_collision_count")) not in {0, None}:
                    issues.append(f"planning_acceptance inflated_collision_count={report.get('inflated_collision_count')}")
            min_replans = as_int(planning_acceptance.get("min_replan_count"))
            actual_replans = as_int(report.get("local_replan_count"))
            if min_replans is not None and (actual_replans is None or actual_replans < min_replans):
                issues.append(f"planning_acceptance local_replan_count={actual_replans}, expected >= {min_replans}")
            min_truth = as_int(planning_acceptance.get("min_truth_obstacles"))
            actual_truth = as_int(report.get("truth_obstacle_count"))
            if min_truth is not None and (actual_truth is None or actual_truth < min_truth):
                issues.append(f"planning_acceptance truth_obstacle_count={actual_truth}, expected >= {min_truth}")
            min_known = as_int(planning_acceptance.get("min_known_obstacles_final"))
            actual_known = as_int(report.get("known_obstacle_count_final"))
            if min_known is not None and (actual_known is None or actual_known < min_known):
                issues.append(f"planning_acceptance known_obstacle_count_final={actual_known}, expected >= {min_known}")
            min_distance = as_float(planning_acceptance.get("min_obstacle_distance_m"))
            actual_distance = as_float(report.get("min_obstacle_distance_m"))
            if min_distance is not None and (actual_distance is None or actual_distance < min_distance):
                issues.append(f"planning_acceptance min_obstacle_distance_m={actual_distance}, expected >= {min_distance}")
            warnings.append(
                "planning_acceptance: "
                f"local_replan_count={report.get('local_replan_count', '<missing>')}, "
                f"known_obstacles={report.get('known_obstacle_count_final', '<missing>')}/"
                f"{report.get('truth_obstacle_count', '<missing>')}, "
                f"min_obstacle_distance_m={report.get('min_obstacle_distance_m', '<missing>')}"
            )

    return {
        "scenario": rel(scenario_path),
        "experiment_id": experiment_id,
        "scene_id": scene_id,
        "controller_id": controller_id,
        "priority": priority,
        "active": active,
        "role": role,
        "evidence_level": evidence_level,
        "quality_status": quality_status,
        "metrics_valid": valid,
        "raw_rows": row_count,
        "figure_count": figure_count,
        "paths": {key: rel(path) for key, path in paths.items()},
        "ok": not issues,
        "issues": issues,
        "warnings": warnings,
    }


def selected_scenarios(args: argparse.Namespace) -> list[Path]:
    if args.scenario:
        return [repo_path(path) for path in args.scenario]
    paths = sorted((ROOT / "config" / "scenarios").glob("**/*.yaml"))
    if args.include_smoke:
        return paths
    selected: list[Path] = []
    for path in paths:
        if "/smoke/" in path.as_posix():
            continue
        try:
            config = read_yaml(path)
        except Exception:
            selected.append(path)
            continue
        is_visual_review = str(config.get("priority", "")) == "visual-review"
        if config.get("active", True) is False and not args.include_inactive and not is_visual_review:
            continue
        selected.append(path)
    return selected


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Evidence Bundle Audit",
        "",
        f"- scenarios_checked: {summary['scenarios_checked']}",
        f"- pass_count: {summary['pass_count']}",
        f"- issue_count: {summary['issue_count']}",
        f"- warning_count: {summary['warning_count']}",
        "",
        "## Issues",
        "",
    ]
    issue_rows = [item for item in summary["results"] if item["issues"]]
    if not issue_rows:
        lines.append("No blocking issues.")
    else:
        lines.append("| Scenario | Quality | Issues |")
        lines.append("|---|---|---|")
        for item in issue_rows:
            lines.append(f"| `{item['scenario']}` | {item['quality_status']} | {'; '.join(item['issues'])} |")
    lines.extend(["", "## Warnings", ""])
    warning_rows = [item for item in summary["results"] if item["warnings"]]
    if not warning_rows:
        lines.append("No warnings.")
    else:
        lines.append("| Scenario | Warnings |")
        lines.append("|---|---|")
        for item in warning_rows[:80]:
            lines.append(f"| `{item['scenario']}` | {'; '.join(item['warnings'])} |")
        if len(warning_rows) > 80:
            lines.append(f"| ... | {len(warning_rows) - 80} more warning rows omitted from markdown; see JSON. |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def result_group(scene_id: str, scenario: str) -> str:
    if scenario.startswith("config/scenarios/official/") or scene_id.startswith("official_"):
        return "official"
    if scenario.startswith("config/scenarios/robustness/") or "rotor" in scene_id or "wind" in scene_id or "mass" in scene_id:
        return "robustness"
    if scenario.startswith("config/scenarios/planning/") or scene_id.startswith("planning_"):
        return "planning"
    if scenario.startswith("config/scenarios/system/") or scene_id.startswith("system_"):
        return "system"
    return "other"


def is_figure8_scene(item: dict[str, Any]) -> str:
    paths = item.get("paths", {})
    text = " ".join([
        str(item.get("scene_id", "")),
        str(item.get("experiment_id", "")),
        str(item.get("evidence_level", "")),
        str(paths.get("raw_file", "")),
        str(paths.get("metrics_file", "")),
        str(paths.get("figure_dir", "")),
    ]).lower()
    return "yes" if "figure8" in text or "figure_8" in text else "no"


def native_result_dir(paths: dict[str, str]) -> str:
    raw_file = paths.get("raw_file", "")
    if not raw_file:
        return ""
    raw_path = Path(raw_file)
    try:
        experiment_dir = raw_path.parents[1]
    except IndexError:
        return ""
    candidate = experiment_dir / "native_result"
    return candidate.as_posix()


def review_priority(item: dict[str, Any]) -> str:
    if item["role"] == "boundary_or_negative_evidence":
        return "medium"
    if is_figure8_scene(item) == "yes":
        return "high"
    if item["scenario"].startswith("config/scenarios/planning/") or item["scenario"].startswith("config/scenarios/system/"):
        return "high"
    if "rotor" in item["scene_id"] or "wind" in item["scene_id"] or "mass" in item["scene_id"]:
        return "high"
    return "medium"


def write_manual_review_csv(summary: dict[str, Any], path: Path) -> None:
    columns = [
        "review_status",
        "review_priority",
        "group",
        "scene",
        "is_figure8",
        "experiment_id",
        "controller_or_case",
        "quality_status",
        "evidence_role",
        "raw_exists",
        "metrics_exists",
        "figure_count",
        "native_result_exists",
        "raw_file",
        "metrics_file",
        "figure_dir",
        "native_result_dir",
        "notes",
        "auto_quality_status",
        "auto_quality_notes",
        "auto_quality_checked_at",
    ]
    today = date.today().isoformat()
    rows: list[dict[str, str]] = []
    for item in summary["results"]:
        paths = item.get("paths", {})
        native_dir = native_result_dir(paths)
        native_exists = bool(native_dir and (ROOT / native_dir).exists())
        issues = "; ".join(item.get("issues", []))
        warnings = "; ".join(item.get("warnings", []))
        notes = warnings or issues or "待人工审核 GUI 动画、曲线和图形化模型入口"
        rows.append({
            "review_status": "pending",
            "review_priority": review_priority(item),
            "group": result_group(item["scene_id"], item["scenario"]),
            "scene": item["scene_id"],
            "is_figure8": is_figure8_scene(item),
            "experiment_id": item["experiment_id"],
            "controller_or_case": item["controller_id"],
            "quality_status": item["quality_status"],
            "evidence_role": item["role"],
            "raw_exists": "yes" if item.get("raw_rows") else "no",
            "metrics_exists": "yes" if item.get("metrics_valid") is not None else "no",
            "figure_count": str(item.get("figure_count", 0)),
            "native_result_exists": "yes" if native_exists else "no",
            "raw_file": paths.get("raw_file", ""),
            "metrics_file": paths.get("metrics_file", ""),
            "figure_dir": paths.get("figure_dir", ""),
            "native_result_dir": native_dir,
            "notes": notes,
            "auto_quality_status": "pass" if item.get("ok") else "needs_attention",
            "auto_quality_notes": "ok" if item.get("ok") else issues,
            "auto_quality_checked_at": today,
        })
    rows.sort(key=lambda row: (
        {"high": 0, "medium": 1, "low": 2}.get(row["review_priority"], 9),
        row["group"],
        row["scene"],
        row["controller_or_case"],
    ))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", nargs="*", help="Optional scenario YAML paths. Defaults to all non-smoke scenarios.")
    parser.add_argument("--include-smoke", action="store_true", help="Include historical smoke scenarios if the directory exists")
    parser.add_argument("--include-inactive", action="store_true", help="Include active: false scenarios in the audit")
    parser.add_argument("--json-output", type=Path, default=ROOT / "results/test_reports/evidence_bundle_audit_20260512.json")
    parser.add_argument("--md-output", type=Path, default=ROOT / "results/test_reports/evidence_bundle_audit_20260512.md")
    parser.add_argument("--manual-review-csv", type=Path, default=ROOT / "results/人工审核清单.csv")
    args = parser.parse_args()

    results = [audit_one(path) for path in selected_scenarios(args)]
    summary = {
        "source": "project_evidence_bundle_audit",
        "scenarios_checked": len(results),
        "pass_count": sum(1 for item in results if item["ok"]),
        "issue_count": sum(len(item["issues"]) for item in results),
        "warning_count": sum(len(item["warnings"]) for item in results),
        "results": results,
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(summary, args.md_output)
    write_manual_review_csv(summary, args.manual_review_csv)
    print(json.dumps({key: summary[key] for key in ["scenarios_checked", "pass_count", "issue_count", "warning_count"]}, ensure_ascii=False))
    print(f"json: {args.json_output}")
    print(f"md: {args.md_output}")
    print(f"manual_review_csv: {args.manual_review_csv}")
    return 0 if summary["issue_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
