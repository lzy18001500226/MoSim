#!/usr/bin/env python3
"""Build a compact evidence manifest for one CoAgent task."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results" / "coagent_status"
DEFAULT_TASK_ID = "COAGENT-IMPL-LONGRUN-20260531"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.runtime import mosim_agent_runtime as runtime
from CoAgent.evidence.refresh_commands import standard_refresh_commands


EVIDENCE_KEYS = (
    "status_export_path",
    "status_export_markdown",
    "resume_bundle_path",
    "resume_bundle_markdown",
    "task_health_path",
    "task_health_markdown",
    "git_handoff_path",
    "git_handoff_markdown",
    "evidence_manifest_path",
    "evidence_manifest_markdown",
    "review_package_path",
    "review_package_markdown",
    "doctor_quick_path",
    "doctor_full_path",
    "review_closeout_verification_path",
    "review_closeout_verification_markdown",
    "review_closeout_path",
    "notification_packet_path",
    "blocker_packet_path",
    "blocker_packet_markdown",
)

EVIDENCE_GLOBS = (
    "Results/coagent_status/{task_id}.*",
    "Results/coagent_doctor/latest_gateway*.json",
    "Results/agent_packets/reviews/{task_id}*.json",
    "Results/agent_packets/summaries/{task_id}*.md",
    "Results/agent_packets/closeouts/{task_id}*.json",
    "Results/agent_packets/notifications/{task_id}*.json",
    "Results/agent_packets/blockers/{task_id}*.json",
    "Results/agent_packets/blockers/{task_id}*.md",
)


CRITICAL_METADATA_SOURCES = {
    f"metadata:{key}"
    for key in EVIDENCE_KEYS
    if key not in {"evidence", "review_package_path", "review_package_markdown"}
}
DOWNSTREAM_METADATA_SOURCES = {"metadata:review_package_path", "metadata:review_package_markdown"}


def refresh_commands(task_id: str) -> list[str]:
    return standard_refresh_commands(task_id)


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def project_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    if not (resolved == ROOT.resolve() or ROOT.resolve() in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def parse_time(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def file_record(path: Path, *, source: str, task_last_event_at: str = "") -> dict[str, Any]:
    resolved = project_path(path)
    exists = resolved.exists()
    record: dict[str, Any] = {
        "path": rel(resolved) if exists else str(path).replace("\\", "/"),
        "source": source,
        "exists": exists,
    }
    if exists:
        stat = resolved.stat()
        modified = datetime.fromtimestamp(stat.st_mtime, timezone.utc).astimezone()
        task_last_event = parse_time(task_last_event_at)
        fresh_after_last_event = None
        age_after_last_event_seconds = None
        if task_last_event is not None:
            delta = modified - task_last_event.astimezone(modified.tzinfo)
            age_after_last_event_seconds = round(delta.total_seconds(), 3)
            fresh_after_last_event = age_after_last_event_seconds >= 0
        record.update(
            {
                "size_bytes": stat.st_size,
                "suffix": resolved.suffix,
                "modified_at": modified.isoformat(timespec="seconds"),
                "fresh_after_task_last_event": fresh_after_last_event,
                "age_after_task_last_event_seconds": age_after_last_event_seconds,
            }
        )
    return record


def add_record(records: dict[str, dict[str, Any]], path: str, *, source: str, task_last_event_at: str = "") -> None:
    if not path:
        return
    candidate = project_path(Path(path))
    key = rel(candidate) if candidate.exists() else str(Path(path)).replace("\\", "/")
    if key in records:
        records[key]["sources"] = sorted(set(records[key].get("sources", []) + [source]))
        return
    record = file_record(Path(path), source=source, task_last_event_at=task_last_event_at)
    record["sources"] = [source]
    records[key] = record


def classify(path: str, sources: list[str] | None = None) -> str:
    sources = sources or []
    if any(source in {"metadata:status_export_path", "metadata:status_export_markdown"} for source in sources):
        return "status_export"
    if any(source in {"metadata:resume_bundle_path", "metadata:resume_bundle_markdown"} for source in sources):
        return "resume"
    if any(source in {"metadata:task_health_path", "metadata:task_health_markdown"} for source in sources):
        return "task_health"
    if any(source in {"metadata:git_handoff_path", "metadata:git_handoff_markdown"} for source in sources):
        return "git_handoff"
    if any(source in {"metadata:evidence_manifest_path", "metadata:evidence_manifest_markdown"} for source in sources):
        return "evidence_manifest"
    if any(source in {"metadata:review_package_path", "metadata:review_package_markdown"} for source in sources):
        return "review_package"
    if any(source == "metadata:review_closeout_path" for source in sources):
        return "closeout"
    if any(source == "metadata:notification_packet_path" for source in sources):
        return "notification"
    if any(source in {"metadata:blocker_packet_path", "metadata:blocker_packet_markdown"} for source in sources):
        return "blocker"
    if "/doctor/" in path or path.startswith("Results/coagent_doctor/"):
        return "doctor"
    if path.endswith(".resume.json") or path.endswith(".resume.md"):
        return "resume"
    if path.endswith(".status.json") or path.endswith(".status.md"):
        return "status_export"
    if path.endswith(".task_health.json") or path.endswith(".task_health.md"):
        return "task_health"
    if path.endswith(".git_handoff.json") or path.endswith(".git_handoff.md"):
        return "git_handoff"
    if path.endswith(".evidence_manifest.json") or path.endswith(".evidence_manifest.md"):
        return "evidence_manifest"
    if path.endswith(".review_package.json") or path.endswith(".review_package.md"):
        return "review_package"
    if "/reviews/" in path:
        return "review"
    if "/summaries/" in path:
        return "summary"
    if "/closeouts/" in path:
        return "closeout"
    if "/notifications/" in path:
        return "notification"
    if "/blockers/" in path:
        return "blocker"
    return "other"


def freshness_role(sources: list[str] | None = None) -> str:
    sources = sources or []
    if any(source in DOWNSTREAM_METADATA_SOURCES for source in sources):
        return "downstream_package"
    if any(source in CRITICAL_METADATA_SOURCES for source in sources):
        return "recovery_current"
    return "archival_or_supporting"


def build_manifest(args: argparse.Namespace) -> dict[str, Any]:
    task = runtime.show_task(argparse.Namespace(db=args.db, events=args.events, task_id=args.task_id))
    metadata = task.get("metadata", {})
    task_last_event_at = str(task.get("last_event_at", ""))
    records: dict[str, dict[str, Any]] = {}
    for key in EVIDENCE_KEYS:
        value = metadata.get(key, "")
        if isinstance(value, str):
            add_record(records, value, source=f"metadata:{key}", task_last_event_at=task_last_event_at)
    for value in metadata.get("evidence", []) if isinstance(metadata.get("evidence", []), list) else []:
        if isinstance(value, str):
            add_record(records, value, source="metadata:evidence", task_last_event_at=task_last_event_at)
    for pattern in EVIDENCE_GLOBS:
        for path in sorted(ROOT.glob(pattern.format(task_id=args.task_id))):
            if path.is_file():
                add_record(records, rel(path), source=f"glob:{pattern}", task_last_event_at=task_last_event_at)
    items = sorted(records.values(), key=lambda item: (classify(item["path"], item.get("sources", [])), item["path"]))
    for item in items:
        item["kind"] = classify(item["path"], item.get("sources", []))
        item["freshness_role"] = freshness_role(item.get("sources", []))
        if item["freshness_role"] == "downstream_package":
            item["fresh_after_task_last_event"] = None
            item["age_after_task_last_event_seconds"] = None
            item["freshness_not_applicable_reason"] = "downstream package summarizes the manifest and is generated after it"
    missing = [item for item in items if not item.get("exists")]
    stale = [item for item in items if item.get("exists") and item.get("fresh_after_task_last_event") is False]
    critical_stale = [item for item in stale if item.get("freshness_role") == "recovery_current"]
    archival_stale = [item for item in stale if item.get("freshness_role") != "recovery_current"]
    unknown_freshness = [
        item
        for item in items
        if item.get("exists") and item.get("fresh_after_task_last_event") is None
    ]
    by_kind: dict[str, int] = {}
    for item in items:
        by_kind[item["kind"]] = by_kind.get(item["kind"], 0) + 1
    if missing:
        freshness_status = "missing"
    elif critical_stale:
        freshness_status = "critical_stale_warning"
    elif stale:
        freshness_status = "archival_stale"
    else:
        freshness_status = "fresh"
    return {
        "schema_type": "coagent_evidence_manifest",
        "schema_version": 1,
        "task_id": args.task_id,
        "ok": not missing,
        "freshness_status": freshness_status,
        "stale_refresh_recommended": bool(critical_stale),
        "refresh_commands": refresh_commands(args.task_id) if critical_stale else [],
        "task_state": task.get("state", ""),
        "task_last_event_at": task_last_event_at,
        "checkpoint": metadata.get("checkpoint", ""),
        "next_action": metadata.get("next_action", ""),
        "evidence_count": len(items),
        "missing_count": len(missing),
        "stale_count": len(stale),
        "critical_stale_count": len(critical_stale),
        "archival_stale_count": len(archival_stale),
        "unknown_freshness_count": len(unknown_freshness),
        "by_kind": by_kind,
        "items": items,
        "missing": missing,
        "stale": stale,
        "critical_stale": critical_stale,
        "archival_stale": archival_stale,
        "unknown_freshness": unknown_freshness,
    }


def write_markdown(path: Path, manifest: dict[str, Any]) -> str:
    lines = [
        "# CoAgent Evidence Manifest",
        "",
        f"- task_id: `{manifest['task_id']}`",
        f"- ok: `{manifest['ok']}`",
        f"- freshness_status: `{manifest.get('freshness_status', '')}`",
        f"- stale_refresh_recommended: `{manifest.get('stale_refresh_recommended', False)}`",
        f"- task_state: `{manifest['task_state']}`",
        f"- task_last_event_at: `{manifest.get('task_last_event_at', '')}`",
        f"- evidence_count: `{manifest['evidence_count']}`",
        f"- missing_count: `{manifest['missing_count']}`",
        f"- stale_count: `{manifest.get('stale_count', 0)}`",
        f"- critical_stale_count: `{manifest.get('critical_stale_count', 0)}`",
        f"- archival_stale_count: `{manifest.get('archival_stale_count', 0)}`",
        f"- unknown_freshness_count: `{manifest.get('unknown_freshness_count', 0)}`",
        "",
        "## Checkpoint",
        "",
        str(manifest.get("checkpoint", "")),
        "",
        "## Next Action",
        "",
        str(manifest.get("next_action", "")),
        "",
        "## Counts",
        "",
    ]
    for kind, count in sorted(manifest.get("by_kind", {}).items()):
        lines.append(f"- `{kind}`: `{count}`")
    lines.extend(["", "## Evidence", ""])
    current_kind = None
    for item in manifest["items"]:
        if item["kind"] != current_kind:
            current_kind = item["kind"]
            lines.extend(["", f"### {current_kind}", ""])
        lines.append(
            f"- `{item['path']}` exists={item['exists']} size={item.get('size_bytes', '')} "
            f"fresh={item.get('fresh_after_task_last_event', '')} modified={item.get('modified_at', '')} "
            f"role={item.get('freshness_role', '')} sources={','.join(item.get('sources', []))}"
        )
    if manifest["missing"]:
        lines.extend(["", "## Missing", ""])
        for item in manifest["missing"]:
            lines.append(f"- `{item['path']}` sources={','.join(item.get('sources', []))}")
    if manifest.get("stale"):
        lines.extend(["", "## Stale Compared With Task Last Event", ""])
        for item in manifest["stale"]:
            lines.append(
                f"- `{item['path']}` modified={item.get('modified_at', '')} "
                f"role={item.get('freshness_role', '')} "
                f"age_after_task_last_event_seconds={item.get('age_after_task_last_event_seconds', '')}"
            )
        if manifest.get("critical_stale"):
            lines.extend(["", "## Critical Stale Recovery Artifacts", ""])
            for item in manifest["critical_stale"]:
                lines.append(f"- `{item['path']}` kind={item.get('kind', '')}")
        if manifest.get("archival_stale"):
            lines.extend(["", "## Archival Or Supporting Stale Artifacts", ""])
            for item in manifest["archival_stale"]:
                lines.append(f"- `{item['path']}` kind={item.get('kind', '')}")
        if manifest.get("refresh_commands"):
            lines.extend(["", "## Refresh Commands", ""])
            for command in manifest.get("refresh_commands", []):
                lines.append(f"- `{command}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rel(path)


def run_manifest(args: argparse.Namespace) -> dict[str, Any]:
    manifest = build_manifest(args)
    outputs: dict[str, str] = {}
    if args.output:
        output = project_path(args.output)
    else:
        output = DEFAULT_OUTPUT_ROOT / f"{args.task_id}.evidence_manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs["json"] = rel(output)
    if args.markdown_output:
        outputs["markdown"] = write_markdown(project_path(args.markdown_output), manifest)
    return {"ok": manifest["ok"], "outputs": outputs, "manifest": manifest if args.include_manifest else {}}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=runtime.DEFAULT_DB)
    parser.add_argument("--events", type=Path, default=runtime.DEFAULT_EVENTS)
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--include-manifest", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_manifest(args)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"evidence_manifest ok={result['ok']} json={result['outputs']['json']}")
        if "markdown" in result["outputs"]:
            print(f"markdown={result['outputs']['markdown']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
