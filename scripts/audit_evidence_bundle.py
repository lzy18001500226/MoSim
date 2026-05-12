#!/usr/bin/env python3
"""Audit scenario evidence bundles for report-ready MWORKS results."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from run_mworks_scenario import ROOT, default_result_base, read_yaml
except ImportError:  # pragma: no cover
    ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ROOT / "scripts"))
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
    paths = sorted((ROOT / "scenarios").glob("**/*.yaml"))
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
        if config.get("active", True) is False and not args.include_inactive:
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", nargs="*", help="Optional scenario YAML paths. Defaults to all non-smoke scenarios.")
    parser.add_argument("--include-smoke", action="store_true", help="Include scenarios/smoke in the audit")
    parser.add_argument("--include-inactive", action="store_true", help="Include active: false scenarios in the audit")
    parser.add_argument("--json-output", type=Path, default=ROOT / "results/test_reports/evidence_bundle_audit_20260512.json")
    parser.add_argument("--md-output", type=Path, default=ROOT / "results/test_reports/evidence_bundle_audit_20260512.md")
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
    print(json.dumps({key: summary[key] for key in ["scenarios_checked", "pass_count", "issue_count", "warning_count"]}, ensure_ascii=False))
    print(f"json: {args.json_output}")
    print(f"md: {args.md_output}")
    return 0 if summary["issue_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
