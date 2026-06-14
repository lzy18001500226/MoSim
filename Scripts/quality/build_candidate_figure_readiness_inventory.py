#!/usr/bin/env python3
"""Build a static figure-readiness inventory for candidate submission evidence.

This is a planning artifact, not final report acceptance. It verifies that each
candidate evidence row has the files a report writer normally needs nearby:
metrics, raw data, core SVG figures, a figure manifest, optional replay, and
logs. It does not run MWORKS/Sysplorer/Syslab, ROS2, or UE.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = (
    ROOT
    / "Results"
    / "static_audits"
    / "submission_evidence_manifest_20260610"
    / "candidate_submission_evidence_manifest.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "static_audits" / "candidate_figure_readiness_20260610"

CORE_FIGURE_PATTERNS = {
    "trajectory_xy": "trajectory_xy",
    "position_error": "position_error",
    "metrics_summary": "metrics_summary",
    "altitude_tracking": "altitude_tracking",
}
FIGURE_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".pdf"}


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def derive_experiment_root(row: dict[str, Any]) -> Path:
    metrics_path = repo_path(str(row.get("metrics_file", "")))
    raw_path = repo_path(str(row.get("raw_file", "")))
    if metrics_path.parent.name == "metrics":
        return metrics_path.parent.parent
    if raw_path.parent.name == "raw":
        return raw_path.parent.parent
    return metrics_path.parent


def list_files(path: Path, suffixes: set[str] | None = None) -> list[Path]:
    if not path.exists() or not path.is_dir():
        return []
    files = [item for item in path.iterdir() if item.is_file()]
    if suffixes is not None:
        files = [item for item in files if item.suffix.lower() in suffixes]
    return sorted(files, key=lambda item: item.name.lower())


def find_core_figures(figure_files: list[Path]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for key, token in CORE_FIGURE_PATTERNS.items():
        matches = [rel(path) for path in figure_files if token in path.name.lower()]
        found[key] = matches
    return found


def row_inventory(row: dict[str, Any]) -> dict[str, Any]:
    metrics_path = repo_path(str(row.get("metrics_file", "")))
    raw_path = repo_path(str(row.get("raw_file", "")))
    experiment_root = derive_experiment_root(row)
    figures_dir = experiment_root / "figures"
    replay_dir = experiment_root / "replay"
    logs_dir = experiment_root / "logs"

    figure_files = list_files(figures_dir, FIGURE_EXTENSIONS)
    figure_manifests = [
        item
        for item in list_files(figures_dir)
        if "figure_manifest" in item.name.lower() and item.suffix.lower() in {".md", ".json"}
    ]
    replay_files = list_files(replay_dir, {".json", ".csv", ".mp4", ".gif"})
    log_files = list_files(logs_dir, {".jsonl", ".log", ".txt", ".json"})
    core_figures = find_core_figures(figure_files)
    missing_core_figures = [key for key, matches in core_figures.items() if not matches]

    report_ready = (
        metrics_path.exists()
        and raw_path.exists()
        and figures_dir.exists()
        and bool(figure_files)
        and bool(figure_manifests)
        and not missing_core_figures
    )
    review_notes: list[str] = []
    if not replay_files:
        review_notes.append("no_replay_file_found")
    if not log_files:
        review_notes.append("no_log_file_found")
    if missing_core_figures:
        review_notes.append("missing_core_figures")

    return {
        "claim_slot": row.get("claim_slot", ""),
        "experiment_id": row.get("experiment_id", ""),
        "claim_family": row.get("claim_family", ""),
        "quality_status": row.get("quality_status", ""),
        "claim_ceiling": row.get("claim_ceiling", ""),
        "experiment_root": rel(experiment_root),
        "metrics_file": rel(metrics_path),
        "metrics_exists": metrics_path.exists(),
        "raw_file": rel(raw_path),
        "raw_exists": raw_path.exists(),
        "figures_dir": rel(figures_dir),
        "figures_dir_exists": figures_dir.exists(),
        "figure_count": len(figure_files),
        "figure_files": [rel(path) for path in figure_files],
        "figure_manifest_files": [rel(path) for path in figure_manifests],
        "core_figures": core_figures,
        "missing_core_figures": missing_core_figures,
        "replay_files": [rel(path) for path in replay_files],
        "log_files": [rel(path) for path in log_files],
        "report_figure_ready": report_ready,
        "review_notes": review_notes,
    }


def build_inventory(manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    rows = [row for row in manifest.get("candidate_rows", []) if isinstance(row, dict)]
    candidates = [row_inventory(row) for row in rows]
    not_ready = [row for row in candidates if not row["report_figure_ready"]]
    missing_replay = [row["claim_slot"] for row in candidates if not row["replay_files"]]
    missing_logs = [row["claim_slot"] for row in candidates if not row["log_files"]]
    return {
        "inventory_id": "candidate_figure_readiness_20260610",
        "status": "static_figure_inventory_not_final_report_acceptance",
        "source_manifest": rel(manifest_path),
        "source_manifest_status": manifest.get("status"),
        "summary": {
            "candidate_row_count": len(candidates),
            "report_figure_ready_count": len(candidates) - len(not_ready),
            "not_ready_count": len(not_ready),
            "missing_replay_count": len(missing_replay),
            "missing_log_count": len(missing_logs),
        },
        "claim_boundary": [
            "Report-figure readiness means local static files exist near candidate evidence.",
            "It is not final PMO acceptance and does not prove live MWORKS, ROS2, UE, or native Syslab completion.",
            "Replay and log absence is recorded as review context; it does not by itself invalidate figure readiness.",
        ],
        "candidate_rows": candidates,
        "not_ready_rows": not_ready,
        "missing_replay_claim_slots": missing_replay,
        "missing_log_claim_slots": missing_logs,
    }


def write_markdown(inventory: dict[str, Any], path: Path) -> None:
    summary = inventory["summary"]
    lines = [
        "# Candidate Figure Readiness Inventory, 2026-06-10",
        "",
        "Status: static figure inventory, not final report acceptance.",
        "",
        f"- Source manifest: `{inventory['source_manifest']}`",
        f"- Source manifest status: `{inventory['source_manifest_status']}`",
        f"- Candidate rows: `{summary['candidate_row_count']}`",
        f"- Report-figure ready rows: `{summary['report_figure_ready_count']}`",
        f"- Not-ready rows: `{summary['not_ready_count']}`",
        f"- Rows without replay files: `{summary['missing_replay_count']}`",
        f"- Rows without log files: `{summary['missing_log_count']}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in inventory["claim_boundary"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Candidate Rows", ""])
    lines.append("| Claim Slot | Family | Ready | Figures | Missing Core Figures | Replay | Logs |")
    lines.append("|---|---|---:|---:|---|---:|---:|")
    for row in inventory["candidate_rows"]:
        missing = ", ".join(row["missing_core_figures"]) if row["missing_core_figures"] else ""
        lines.append(
            "| {claim_slot} | {family} | {ready} | {figures} | {missing} | {replay} | {logs} |".format(
                claim_slot=row["claim_slot"],
                family=row["claim_family"],
                ready=row["report_figure_ready"],
                figures=row["figure_count"],
                missing=missing,
                replay=len(row["replay_files"]),
                logs=len(row["log_files"]),
            )
        )

    lines.extend(["", "## Not-Ready Rows", ""])
    if inventory["not_ready_rows"]:
        for row in inventory["not_ready_rows"]:
            lines.append(f"- `{row['claim_slot']}`: `{row['experiment_root']}`")
    else:
        lines.append("- None. All candidate rows have metrics/raw paths, figure manifests, and core figures.")

    lines.extend(["", "## Notes", ""])
    lines.append("- Replay/log presence is tracked to help report review and traceability.")
    lines.append("- Missing replay/log files should be reviewed before final report packaging.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    manifest_path = repo_path(args.manifest)
    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory(manifest_path)

    json_path = output_dir / "candidate_figure_readiness_inventory.json"
    md_path = output_dir / "candidate_figure_readiness_inventory.md"
    json_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(inventory, md_path)

    result = {
        "ok": inventory["summary"]["not_ready_count"] == 0,
        "inventory_json": rel(json_path),
        "inventory_markdown": rel(md_path),
        "candidate_row_count": inventory["summary"]["candidate_row_count"],
        "report_figure_ready_count": inventory["summary"]["report_figure_ready_count"],
        "not_ready_count": inventory["summary"]["not_ready_count"],
        "missing_replay_count": inventory["summary"]["missing_replay_count"],
        "missing_log_count": inventory["summary"]["missing_log_count"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
