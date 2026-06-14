#!/usr/bin/env python3
"""Build a checksum index for final-submission reviewer-open files.

This guard reads the non-executing reviewer evidence index, aggregates the
unique files a human reviewer is expected to open, and records size, mtime, and
SHA256. If a prior output exists, it reports drift before overwriting the
output. It does not fill answers, edit decision artifacts, run final-output
commands, or authorize execution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REVIEWER_EVIDENCE_INDEX = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_reviewer_evidence_index_20260610"
    / "final_submission_reviewer_evidence_index.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_reviewer_open_file_checksum_index_20260610"


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_timestamp(seconds: float) -> str:
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat().replace("+00:00", "Z")


def collect_open_files(index: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    seen: dict[str, dict[str, Any]] = {}
    total_reference_count = 0
    for action in index.get("review_actions", []):
        if not isinstance(action, dict):
            continue
        action_id = str(action.get("action_id", ""))
        for item in action.get("review_evidence_files", []):
            if not isinstance(item, dict):
                continue
            path_value = str(item.get("path", "")).strip()
            if not path_value:
                continue
            total_reference_count += 1
            normalized = Path(path_value).as_posix()
            record = seen.setdefault(
                normalized,
                {
                    "path": normalized,
                    "required": bool(item.get("required", True)),
                    "sources": [],
                    "actions": [],
                },
            )
            source = str(item.get("source", "unknown"))
            if source not in record["sources"]:
                record["sources"].append(source)
            if action_id and action_id not in record["actions"]:
                record["actions"].append(action_id)
            record["required"] = bool(record["required"] or item.get("required", True))
    return list(seen.values()), total_reference_count


def file_record(item: dict[str, Any]) -> dict[str, Any]:
    path_value = str(item["path"])
    path = repo_path(path_value)
    record = {
        "path": path_value,
        "exists": path.exists(),
        "required": bool(item.get("required", True)),
        "sources": list(item.get("sources", [])),
        "actions": list(item.get("actions", [])),
        "action_reference_count": len(item.get("actions", [])),
        "size_bytes": None,
        "mtime_utc": "",
        "sha256": "",
        "readable": False,
        "issue": "",
    }
    if not path.exists():
        record["issue"] = "missing"
        return record
    try:
        stat = path.stat()
        record["size_bytes"] = stat.st_size
        record["mtime_utc"] = utc_timestamp(stat.st_mtime)
        record["sha256"] = sha256_file(path)
        record["readable"] = True
    except Exception as exc:
        record["issue"] = f"unreadable: {exc}"
    return record


def previous_records(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        data = read_json(path)
    except Exception:
        return {}
    records = data.get("open_files", [])
    if not isinstance(records, list):
        return {}
    return {
        str(record.get("path", "")): record
        for record in records
        if isinstance(record, dict) and record.get("path")
    }


def detect_drift(
    current_records: list[dict[str, Any]],
    old_records: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    drift: list[dict[str, Any]] = []
    if not old_records:
        return drift
    for record in current_records:
        old = old_records.get(str(record["path"]))
        if not old:
            drift.append(
                {
                    "path": record["path"],
                    "field": "path",
                    "previous": "missing_from_previous_index",
                    "current": "present",
                }
            )
            continue
        for field in ("sha256", "size_bytes"):
            if old.get(field) != record.get(field):
                drift.append(
                    {
                        "path": record["path"],
                        "field": field,
                        "previous": old.get(field),
                        "current": record.get(field),
                    }
                )
    current_paths = {str(record["path"]) for record in current_records}
    for path_value in sorted(set(old_records) - current_paths):
        drift.append(
            {
                "path": path_value,
                "field": "path",
                "previous": "present",
                "current": "missing_from_current_index",
            }
        )
    return drift


def build_index(input_path: Path, previous_output_path: Path | None = None) -> dict[str, Any]:
    source = read_json(input_path)
    source_summary = source.get("summary", {})
    if not isinstance(source_summary, dict):
        source_summary = {}
    open_file_specs, total_reference_count = collect_open_files(source)
    records = [file_record(item) for item in open_file_specs]

    missing = [record for record in records if record["required"] and not record["exists"]]
    unreadable = [record for record in records if record["exists"] and not record["readable"]]
    prior = previous_records(previous_output_path) if previous_output_path else {}
    drift = detect_drift(records, prior)
    issues = []
    issues.extend(f"missing required open file: {record['path']}" for record in missing)
    issues.extend(f"unreadable open file: {record['path']}" for record in unreadable)
    issues.extend(f"open file drift detected: {item['path']} {item['field']}" for item in drift)

    return {
        "index_id": "final_submission_reviewer_open_file_checksum_index_20260610",
        "status": "reviewer_open_file_checksum_index_not_execution",
        "source": rel(input_path),
        "summary": {
            "source_status": source.get("status", ""),
            "source_action_count": source_summary.get("action_count", 0),
            "unique_open_file_count": len(records),
            "total_open_file_reference_count": total_reference_count,
            "duplicate_open_file_reference_count": total_reference_count - len(records),
            "checksum_file_count": sum(1 for record in records if record["readable"]),
            "missing_open_file_count": len(missing),
            "unreadable_open_file_count": len(unreadable),
            "drift_from_previous_output_count": len(drift),
            "issue_count": len(issues),
            "automated_execution_allowed": False,
            "opens_files_now": False,
            "fills_answers_now": False,
            "copies_answers_now": False,
            "edits_decision_artifacts_now": False,
            "runs_commands_now": False,
            "authorizes_execution_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "open_files": records,
        "drift_from_previous_output": drift,
        "issues": issues,
        "claim_boundary": [
            "This checksum index is a static reviewer-open-file guard only.",
            "It does not open files in an editor or UI.",
            "It does not fill answers.",
            "It does not copy answers into decision artifacts.",
            "It does not edit decision templates.",
            "It does not approve decisions.",
            "It does not install PDF tooling.",
            "It does not create final artifacts.",
            "It does not run final-output commands.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
            "It does not run MWORKS, ROS2, UE, or visible-thread dispatch tools.",
        ],
    }


def write_markdown(index: dict[str, Any], path: Path) -> None:
    summary = index["summary"]
    lines = [
        "# Final Submission Reviewer Open-File Checksum Index, 2026-06-10",
        "",
        f"Status: `{index['status']}`",
        "",
        "## Summary",
        "",
        f"- Source status: `{summary['source_status']}`",
        f"- Source actions: `{summary['source_action_count']}`",
        f"- Unique open files: `{summary['unique_open_file_count']}`",
        f"- Total open-file references: `{summary['total_open_file_reference_count']}`",
        f"- Duplicate open-file references: `{summary['duplicate_open_file_reference_count']}`",
        f"- Checksum files: `{summary['checksum_file_count']}`",
        f"- Missing open files: `{summary['missing_open_file_count']}`",
        f"- Unreadable open files: `{summary['unreadable_open_file_count']}`",
        f"- Drift from previous output: `{summary['drift_from_previous_output_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- Opens files now: `{summary['opens_files_now']}`",
        f"- Runs commands now: `{summary['runs_commands_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Open Files",
        "",
    ]
    for record in index["open_files"]:
        lines.extend(
            [
                f"### {record['path']}",
                "",
                f"- Exists: `{record['exists']}`",
                f"- Readable: `{record['readable']}`",
                f"- Size bytes: `{record['size_bytes']}`",
                f"- Mtime UTC: `{record['mtime_utc']}`",
                f"- SHA256: `{record['sha256']}`",
                f"- Actions: `{', '.join(record['actions'])}`",
                "",
            ]
        )
    lines.extend(["## Drift From Previous Output", ""])
    if index["drift_from_previous_output"]:
        for item in index["drift_from_previous_output"]:
            lines.append(
                f"- `{item['path']}` `{item['field']}` changed from "
                f"`{item['previous']}` to `{item['current']}`"
            )
    else:
        lines.append("- None")
    lines.extend(["", "## Issues", ""])
    if index["issues"]:
        for item in index["issues"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in index["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-evidence-index", default=str(DEFAULT_REVIEWER_EVIDENCE_INDEX.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    parser.add_argument("--ignore-previous-output", action="store_true")
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "final_submission_reviewer_open_file_checksum_index.json"
    md_path = output_dir / "final_submission_reviewer_open_file_checksum_index.md"
    previous_output_path = None if args.ignore_previous_output else json_path
    index = build_index(repo_path(args.reviewer_evidence_index), previous_output_path)
    json_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(index, md_path)
    print(
        json.dumps(
            {
                "ok": not index["issues"],
                **index["summary"],
                "json": rel(json_path),
                "markdown": rel(md_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not index["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
