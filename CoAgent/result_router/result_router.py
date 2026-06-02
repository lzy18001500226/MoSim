#!/usr/bin/env python3
"""Validate, archive, and import CoAgent result packets."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE_ROOT = ROOT / "Results" / "agent_packets" / "archive"
SUMMARY_ROOT = ROOT / "Results" / "agent_packets" / "summaries"
REVIEW_ROOT = ROOT / "Results" / "agent_packets" / "reviews"
NOTIFICATION_ROOT = ROOT / "Results" / "agent_packets" / "notifications"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.gateway import cc_connect_weixin
from CoAgent.runtime import mosim_agent_runtime as runtime


CANONICAL_STATUSES = {
    "planned",
    "ready",
    "working",
    "input_required",
    "auth_required",
    "review_required",
    "blocked",
    "failed",
    "completed",
    "canceled",
    "rejected",
    "superseded",
}
RUNTIME_STATUS_ALIASES = {"queued", "claimed", "running", "done", "done_with_concerns", "cancelled"}
VALID_STATUSES = CANONICAL_STATUSES | RUNTIME_STATUS_ALIASES
CANONICAL_TERMINAL_STATUSES = {"review_required", "blocked", "failed", "completed", "canceled", "rejected", "superseded"}
RUNTIME_TERMINAL_STATUSES = {"done", "done_with_concerns", "blocked", "failed", "cancelled"}
TERMINAL_STATUSES = CANONICAL_TERMINAL_STATUSES | RUNTIME_TERMINAL_STATUSES
STATUS_TO_CANONICAL = {
    "queued": "ready",
    "claimed": "working",
    "running": "working",
    "done": "completed",
    "done_with_concerns": "review_required",
    "cancelled": "canceled",
}


def canonical_status_for(status: str, payload: dict[str, Any] | None = None) -> str:
    if payload:
        explicit = str(payload.get("canonical_status") or "")
        if explicit in CANONICAL_STATUSES:
            return explicit
    return STATUS_TO_CANONICAL.get(status, status)


def now_stamp() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def project_path(path: Path) -> Path:
    path = Path(path)
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    if not (resolved == ROOT.resolve() or ROOT.resolve() in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "null", "None"}:
        return None
    if value.startswith("[") or value.startswith("{"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def parse_text_packet(text: str) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for line in text.splitlines():
        if not line or line.startswith("["):
            continue
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        payload[key] = parse_scalar(value)
    return payload


def parse_packet(path: Path) -> dict[str, Any]:
    resolved = project_path(path)
    text = resolved.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if stripped.startswith("{"):
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise SystemExit("result packet JSON must be an object")
    else:
        payload = parse_text_packet(text)
    payload["_source_packet"] = rel(resolved)
    return payload


def validate_packet(payload: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for field in ["task_id", "status", "summary"]:
        if not payload.get(field):
            findings.append({"severity": "fail", "field": field, "reason": "missing_required"})
    status = str(payload.get("status", ""))
    if status and status not in VALID_STATUSES:
        findings.append({"severity": "fail", "field": "status", "reason": "invalid_status", "value": status})
    explicit_canonical_status = str(payload.get("canonical_status", ""))
    if explicit_canonical_status and explicit_canonical_status not in CANONICAL_STATUSES:
        findings.append(
            {
                "severity": "fail",
                "field": "canonical_status",
                "reason": "invalid_canonical_status",
                "value": explicit_canonical_status,
            }
        )
    for field in ["read_scope", "write_scope", "events"]:
        value = payload.get(field, [])
        if value in (None, ""):
            payload[field] = []
        elif not isinstance(value, list):
            findings.append({"severity": "warning", "field": field, "reason": "not_list", "value_type": type(value).__name__})
    ok = not any(item["severity"] == "fail" for item in findings)
    return {"ok": ok, "findings": findings, "payload": payload}


def as_list(value: Any) -> list[Any]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return value
    return [value]


def review_packet(payload: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    status = str(payload.get("status", ""))
    canonical_status = canonical_status_for(status, payload)
    if not validation["ok"]:
        findings.append({"severity": "fail", "field": "validation", "reason": "schema_validation_failed"})
    if canonical_status == "review_required":
        findings.append({"severity": "warning", "field": "status", "reason": "completed_with_concerns"})
    if canonical_status in {"blocked", "failed", "canceled", "rejected", "superseded"}:
        findings.append({"severity": "warning", "field": "status", "reason": "terminal_non_success"})
    if canonical_status in CANONICAL_TERMINAL_STATUSES:
        evidence = as_list(payload.get("evidence"))
        if not evidence:
            findings.append({"severity": "warning", "field": "evidence", "reason": "missing_terminal_evidence"})
        next_action = payload.get("next_recommended_action") or payload.get("next_action")
        if not next_action:
            findings.append({"severity": "warning", "field": "next_recommended_action", "reason": "missing_next_action"})
    if canonical_status in {"blocked", "failed", "input_required", "auth_required"} and not as_list(payload.get("blockers")):
        findings.append({"severity": "warning", "field": "blockers", "reason": "missing_blocker_details"})
    if canonical_status == "completed" and as_list(payload.get("risks")):
        findings.append({"severity": "warning", "field": "risks", "reason": "done_with_unresolved_risks"})
    fail_count = sum(1 for item in findings if item["severity"] == "fail")
    warning_count = sum(1 for item in findings if item["severity"] == "warning")
    if fail_count:
        status_label = "rejected"
    elif warning_count:
        status_label = "needs_review"
    else:
        status_label = "accepted"
    return {
        "status": status_label,
        "canonical_status": canonical_status,
        "findings": findings,
        "fail_count": fail_count,
        "warning_count": warning_count,
        "requires_human_review": status_label != "accepted",
    }


def state_event_for_status(status: str) -> tuple[str, str]:
    canonical_status = canonical_status_for(status)
    event_map = {
        "completed": ("done", "task_completed"),
        "review_required": ("done_with_concerns", "task_completed"),
        "blocked": ("blocked", "task_blocked"),
        "failed": ("failed", "task_failed"),
        "canceled": ("cancelled", "task_cancelled"),
        "rejected": ("failed", "task_failed"),
        "superseded": ("cancelled", "task_cancelled"),
        "working": ("running", "checkpoint"),
        "ready": ("running", "checkpoint"),
        "planned": ("running", "checkpoint"),
        "input_required": ("blocked", "task_blocked"),
        "auth_required": ("blocked", "task_blocked"),
    }
    return event_map[canonical_status]


def archive_packet(packet_path: Path, payload: dict[str, Any]) -> dict[str, str]:
    task_id = str(payload.get("task_id") or "invalid")
    archive_dir = ARCHIVE_ROOT / task_id
    archive_dir.mkdir(parents=True, exist_ok=True)
    source = project_path(packet_path)
    archive_path = archive_dir / f"{now_stamp()}_{source.name}"
    shutil.copy2(source, archive_path)
    parsed_path = archive_dir / f"{archive_path.stem}.parsed.json"
    parsed_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"archive_path": rel(archive_path), "parsed_path": rel(parsed_path)}


def write_review(payload: dict[str, Any], review: dict[str, Any]) -> str:
    task_id = str(payload["task_id"])
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    review_path = REVIEW_ROOT / f"{task_id}.review.json"
    review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return rel(review_path)


def notification_class_for(payload: dict[str, Any], review: dict[str, Any]) -> str:
    canonical_status = str(review.get("canonical_status") or canonical_status_for(str(payload.get("status", "")), payload))
    if canonical_status == "auth_required":
        return "auth_required"
    if canonical_status == "review_required":
        return "manual_review_required"
    if canonical_status in {"blocked", "failed", "input_required"}:
        return "incident_required"
    return "manual_review_required"


def write_notification_packet(payload: dict[str, Any], review: dict[str, Any], review_path: str, summary_path: str) -> str:
    task_id = str(payload["task_id"])
    canonical_status = str(review.get("canonical_status") or canonical_status_for(str(payload.get("status", "")), payload))
    NOTIFICATION_ROOT.mkdir(parents=True, exist_ok=True)
    packet_path = NOTIFICATION_ROOT / f"{task_id}.weixin_notification.json"
    evidence = [str(item) for item in as_list(payload.get("evidence"))]
    if review_path:
        evidence.append(review_path)
    if summary_path:
        evidence.append(summary_path)
    packet = {
        "template_type": "blocker_notification",
        "task_id": task_id,
        "severity": "high" if canonical_status in {"auth_required", "failed"} else "medium",
        "class": notification_class_for(payload, review),
        "dedupe_key": f"result-router:{task_id}:{canonical_status}:{review.get('status', '')}",
        "blocked_surface": payload.get("checkpoint") or payload.get("summary") or "CoAgent result packet",
        "human_action_required": payload.get("next_recommended_action") or "请审核结果包并确认下一步。",
        "why_now": payload.get("summary") or "",
        "evidence_paths": evidence[:8],
        "resume_packet_path": summary_path,
        "review_status": review.get("status", ""),
        "canonical_status": canonical_status,
    }
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return rel(packet_path)


def maybe_notify_weixin(args: argparse.Namespace, payload: dict[str, Any], review: dict[str, Any], review_path: str, summary_path: str) -> dict[str, Any]:
    if not getattr(args, "notify_weixin", False):
        return {"enabled": False}
    if not review.get("requires_human_review"):
        return {"enabled": True, "skipped": True, "reason": "human_review_not_required"}
    packet_path = write_notification_packet(payload, review, review_path, summary_path)
    namespace = argparse.Namespace(
        packet=ROOT / packet_path,
        project=getattr(args, "weixin_project", cc_connect_weixin.DEFAULT_PROJECT),
        session=getattr(args, "weixin_session", ""),
        data_dir=getattr(args, "weixin_data_dir", cc_connect_weixin.DEFAULT_DATA_DIR),
        cc_bin=getattr(args, "weixin_cc_bin", cc_connect_weixin.DEFAULT_BIN),
        config=getattr(args, "weixin_config", cc_connect_weixin.DEFAULT_CONFIG),
        audit=getattr(args, "weixin_audit", cc_connect_weixin.DEFAULT_AUDIT),
        dedupe=getattr(args, "weixin_dedupe", cc_connect_weixin.DEFAULT_DEDUPE),
        max_chars=getattr(args, "weixin_max_chars", 1500),
        timeout=getattr(args, "weixin_timeout", 60),
        send=getattr(args, "send_weixin", False),
        force=getattr(args, "force_weixin", False),
        omit_message_in_audit=getattr(args, "omit_weixin_message_in_audit", False),
    )
    result = cc_connect_weixin.notify(namespace)
    return {"enabled": True, "packet_path": packet_path, "result": result}


def metadata_patch_for_import(
    payload: dict[str, Any],
    validation: dict[str, Any],
    review: dict[str, Any],
    archive: dict[str, str],
    review_path: str,
    summary_path: str,
    notification: dict[str, Any],
) -> dict[str, Any]:
    canonical_status = str(review.get("canonical_status") or canonical_status_for(str(payload.get("status", "")), payload))
    evidence = [str(item) for item in as_list(payload.get("evidence"))]
    for path in [review_path, summary_path, notification.get("packet_path", "")]:
        if path:
            evidence.append(str(path))
    patch: dict[str, Any] = {
        "result_packet_imported": True,
        "source_packet": payload.get("_source_packet", ""),
        "canonical_status": canonical_status,
        "review_status": review.get("status", ""),
        "requires_human_review": bool(review.get("requires_human_review")),
        "validation_ok": bool(validation.get("ok")),
        "review_path": review_path,
        "summary_path": summary_path,
        "archive_path": archive.get("archive_path", ""),
        "parsed_archive_path": archive.get("parsed_path", ""),
        "notification_packet_path": notification.get("packet_path", ""),
        "notification_enabled": bool(notification.get("enabled")),
        "notification_send_reason": str((notification.get("result") or {}).get("send_result", {}).get("reason", "")),
        "next_action": payload.get("next_recommended_action") or payload.get("next_action") or "review result packet",
        "evidence": evidence,
        "blockers": [str(item) for item in as_list(payload.get("blockers"))],
    }
    if review.get("requires_human_review"):
        patch["human_needed"] = "yes"
        patch["human_review_reason"] = review.get("status", "")
    else:
        patch["human_needed"] = ""
        patch["human_review_reason"] = ""
    return patch


def update_import_metadata(
    args: argparse.Namespace,
    payload: dict[str, Any],
    validation: dict[str, Any],
    review: dict[str, Any],
    archive: dict[str, str],
    review_path: str,
    summary_path: str,
    notification: dict[str, Any],
) -> dict[str, Any]:
    patch = metadata_patch_for_import(payload, validation, review, archive, review_path, summary_path, notification)
    namespace = argparse.Namespace(
        db=args.db,
        events=args.events,
        task_id=str(payload["task_id"]),
        actor=str(payload.get("owner") or payload.get("role") or "ImportedDepartment"),
        claim_token=args.claim_token or "",
        summary="updated result packet import metadata",
        metadata=json.dumps(patch, ensure_ascii=False, sort_keys=True),
    )
    return runtime.update_metadata(namespace)


def write_summary(
    payload: dict[str, Any],
    validation: dict[str, Any],
    imported: dict[str, Any] | None,
    archive: dict[str, str],
    review: dict[str, Any],
) -> str:
    task_id = str(payload["task_id"])
    SUMMARY_ROOT.mkdir(parents=True, exist_ok=True)
    summary_path = SUMMARY_ROOT / f"{task_id}.summary.md"
    lines = [
        f"# Result Packet Summary: {task_id}",
        "",
        f"- task_id: `{task_id}`",
        f"- status: `{payload.get('status', '')}`",
        f"- ok: `{validation['ok']}`",
        f"- source_packet: `{payload.get('_source_packet', '')}`",
        f"- archive_path: `{archive.get('archive_path', '')}`",
        f"- runtime_state: `{(imported or {}).get('state', '')}`",
        f"- review_status: `{review.get('status', '')}`",
        f"- requires_human_review: `{review.get('requires_human_review', False)}`",
        "",
        "## Summary",
        "",
        str(payload.get("summary", "")),
        "",
        "## Validation",
        "",
        "```json",
        json.dumps(validation["findings"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Review Gate",
        "",
        "```json",
        json.dumps(review, ensure_ascii=False, indent=2),
        "```",
    ]
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rel(summary_path)


def import_packet(args: argparse.Namespace) -> dict[str, Any]:
    payload = parse_packet(args.packet)
    validation = validate_packet(payload)
    review = review_packet(payload, validation)
    if not validation["ok"]:
        archive = archive_packet(args.packet, payload) if args.archive_invalid else {}
        review_path = write_review(payload, review) if payload.get("task_id") else ""
        summary = write_summary(payload, validation, None, archive, review) if payload.get("task_id") else ""
        notification = maybe_notify_weixin(args, payload, review, review_path, summary) if payload.get("task_id") else {"enabled": False}
        return {
            "ok": False,
            "validation": validation,
            "review": review,
            "review_path": review_path,
            "archive": archive,
            "summary_path": summary,
            "notification": notification,
        }
    task_id = str(payload["task_id"])
    status = str(payload["status"])
    mapped_state, event_type = state_event_for_status(status)
    canonical_status = canonical_status_for(status, payload)
    data = {
        "imported_result_packet": True,
        "source_packet": payload["_source_packet"],
        "status": status,
        "canonical_status": canonical_status,
        "review_status": review["status"],
        "acceptance_state": payload.get("acceptance_state", ""),
        "format": "coagent_result_router",
    }
    namespace = argparse.Namespace(
        db=args.db,
        events=args.events,
        task_id=task_id,
        actor=str(payload.get("owner") or payload.get("role") or "ImportedDepartment"),
        claim_token=args.claim_token or "",
        summary=str(payload.get("summary", "imported result packet")),
        data=json.dumps(data, ensure_ascii=False),
    )
    imported = runtime.update_task(namespace, state=mapped_state, event_type=event_type)
    archive = archive_packet(args.packet, payload) if args.archive else {}
    review_path = write_review(payload, review)
    summary = write_summary(payload, validation, imported, archive, review)
    notification = maybe_notify_weixin(args, payload, review, review_path, summary)
    metadata_state = update_import_metadata(args, payload, validation, review, archive, review_path, summary, notification)
    return {
        "ok": True,
        "task_id": task_id,
        "terminal": canonical_status in CANONICAL_TERMINAL_STATUSES,
        "validation": validation,
        "review": review,
        "review_path": review_path,
        "archive": archive,
        "summary_path": summary,
        "notification": notification,
        "metadata_state": metadata_state,
        "runtime_state": imported,
    }


def validate_command(args: argparse.Namespace) -> dict[str, Any]:
    payload = parse_packet(args.packet)
    validation = validate_packet(payload)
    review = review_packet(payload, validation)
    return {"ok": validation["ok"], "validation": validation, "review": review}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("--packet", type=Path, required=True)
    validate.set_defaults(func=validate_command)

    import_parser = subparsers.add_parser("import")
    runtime.add_common(import_parser)
    import_parser.add_argument("--packet", type=Path, required=True)
    import_parser.add_argument("--claim-token", default="")
    import_parser.add_argument("--archive", action="store_true", default=True)
    import_parser.add_argument("--no-archive", dest="archive", action="store_false")
    import_parser.add_argument("--archive-invalid", action="store_true")
    import_parser.add_argument("--notify-weixin", action="store_true", help="dry-run or send a Weixin review notification when human review is required")
    import_parser.add_argument("--send-weixin", action="store_true", help="actually send the Weixin notification; otherwise notification is a dry run")
    import_parser.add_argument("--weixin-session", default="", help="cc-connect session id or alias; omitted uses the first active session")
    import_parser.add_argument("--weixin-project", default=cc_connect_weixin.DEFAULT_PROJECT)
    import_parser.add_argument("--weixin-data-dir", type=Path, default=cc_connect_weixin.DEFAULT_DATA_DIR)
    import_parser.add_argument("--weixin-cc-bin", type=Path, default=cc_connect_weixin.DEFAULT_BIN)
    import_parser.add_argument("--weixin-config", type=Path, default=cc_connect_weixin.DEFAULT_CONFIG)
    import_parser.add_argument("--weixin-audit", type=Path, default=cc_connect_weixin.DEFAULT_AUDIT)
    import_parser.add_argument("--weixin-dedupe", type=Path, default=cc_connect_weixin.DEFAULT_DEDUPE)
    import_parser.add_argument("--weixin-max-chars", type=int, default=1500)
    import_parser.add_argument("--weixin-timeout", type=int, default=60)
    import_parser.add_argument("--force-weixin", action="store_true")
    import_parser.add_argument("--omit-weixin-message-in-audit", action="store_true")
    import_parser.set_defaults(func=import_packet)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
