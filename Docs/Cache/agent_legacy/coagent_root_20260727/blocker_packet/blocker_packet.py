#!/usr/bin/env python3
"""Generate CoAgent blocker-notification packets from task-health decisions."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results" / "agent_packets" / "blockers"
DEFAULT_TASK_ID = "COAGENT-IMPL-LONGRUN-20260531"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.hooks import preflight
from CoAgent.runtime import mosim_agent_runtime as runtime
from CoAgent.task_health import task_health


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def now_stamp() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def project_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def as_list(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def notification_class(decision: dict[str, Any], task_item: dict[str, Any]) -> str:
    stop_reason = str(decision.get("stop_reason") or "")
    if decision.get("required_human_action") and stop_reason == "auth_required":
        return "auth_required"
    if decision.get("required_human_action"):
        return "approval_required"
    if decision.get("required_safety_action"):
        return "incident_required"
    if decision.get("required_review_action"):
        return "manual_review_required"
    if task_item.get("health_state") in {"block_for_safety", "reject_completion"}:
        return "incident_required"
    return "manual_review_required"


def severity_for(decision: dict[str, Any], task_item: dict[str, Any]) -> str:
    if decision.get("required_safety_action") or task_item.get("health_state") == "block_for_safety":
        return "high"
    if task_item.get("health_state") in {"block_for_user", "reject_completion"}:
        return "high"
    return "medium"


def evidence_paths(metadata: dict[str, Any], task_item: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for key in [
        "summary_path",
        "review_path",
        "review_closeout_path",
        "notification_packet_path",
        "status_export_path",
        "resume_bundle_path",
        "task_health_path",
        "git_handoff_path",
        "evidence_manifest_path",
        "review_package_path",
        "doctor_full_path",
        "doctor_quick_path",
    ]:
        value = str(metadata.get(key) or "")
        if value:
            paths.append(value)
    paths.extend(as_list(metadata.get("evidence")))
    closeout = task_item.get("review_closeout", {})
    if isinstance(closeout, dict) and closeout.get("path"):
        paths.append(str(closeout["path"]))
    unique: list[str] = []
    for path in paths:
        if path and path not in unique:
            unique.append(path)
    return unique[:12]


def human_action(decision: dict[str, Any], task_item: dict[str, Any], metadata: dict[str, Any]) -> str:
    if decision.get("next_intervention"):
        return str(decision["next_intervention"])
    if metadata.get("next_action"):
        return str(metadata["next_action"])
    stop_reason = str(decision.get("stop_reason") or "")
    if stop_reason == "human_needed":
        return "请处理 runtime metadata 中记录的人工作业，然后通知主对话继续。"
    if stop_reason == "auth_required":
        return "请恢复所需登录、许可证或授权状态，然后通知主对话重新检查。"
    if decision.get("required_review_action"):
        return "请审核对应证据包，并回复 accepted / accepted_with_concerns / needs_rework / rejected。"
    if decision.get("required_safety_action"):
        return "请先处理安全阻塞项，确认后再允许继续自动化。"
    return "请查看阻塞包并确认下一步。"


def why_now(decision: dict[str, Any], task_item: dict[str, Any]) -> str:
    findings = task_item.get("findings", [])
    if findings:
        first = findings[0]
        return f"{first.get('reason', '')}: {first.get('evidence', '')}"
    return f"task health state is {task_item.get('health_state', '')}"


def build_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    return task_health.build_snapshot(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            task_id=args.task_id,
            state="",
            active_only=True,
            stale_minutes=args.stale_minutes,
            staged_file_warning_threshold=args.staged_file_warning_threshold,
            skip_preflight=args.skip_preflight,
            skip_runtime_audit=args.skip_runtime_audit,
        )
    )


def build_packet(args: argparse.Namespace) -> dict[str, Any]:
    snapshot = build_snapshot(args)
    decision = snapshot.get("decision", {})
    task_items = snapshot.get("tasks", [])
    blocking_ids = decision.get("blocking_task_ids", [])
    if blocking_ids:
        selected = next((item for item in task_items if item.get("task_id") == blocking_ids[0]), task_items[0])
    else:
        selected = task_items[0] if task_items else {}
    needed = bool(blocking_ids)
    if not needed and not args.write_when_clear:
        return {
            "needed": False,
            "snapshot_decision": decision,
            "packet": {},
            "snapshot": snapshot if args.include_snapshot else {},
        }

    task = runtime.show_task(argparse.Namespace(db=args.db, events=args.events, task_id=args.task_id))
    metadata = task.get("metadata", {})
    selected_decision = selected.get("decision", decision) if selected else decision
    klass = notification_class(selected_decision, selected)
    packet = {
        "template_type": "blocker_notification",
        "template_version": 1,
        "notification_id": f"BLOCKER-{now_stamp()}-{args.task_id}",
        "task_id": args.task_id,
        "parent_goal": metadata.get("parent_goal", metadata.get("project_goal", "")),
        "owner_conversation": metadata.get("owner_conversation", metadata.get("task_conversation", "")),
        "state": selected.get("runtime_state", task.get("state", "")),
        "severity": severity_for(selected_decision, selected),
        "class": klass,
        "dedupe_key": f"task-health:{args.task_id}:{selected.get('health_state', '')}:{selected_decision.get('stop_reason', '')}",
        "blocked_surface": selected_decision.get("stop_reason") or selected.get("health_state", "task_health"),
        "human_action_required": human_action(selected_decision, selected, metadata),
        "why_now": why_now(selected_decision, selected),
        "evidence_paths": evidence_paths(metadata, selected),
        "resume_packet_path": metadata.get("resume_bundle_markdown") or metadata.get("resume_bundle_path") or "",
        "retry_policy": {
            "max_retries_before_human": 1,
            "next_recheck_command": f"python3 CoAgent/task_health/task_health.py --task-id {args.task_id} --json",
            "expected_success_signal": "decision.continue_allowed=true",
        },
        "expires_or_recheck_after": "",
        "safe_to_continue_without_user": bool(selected_decision.get("continue_allowed")),
        "notification_level": "project_packet",
        "generated_at": now_iso(),
        "health_state": selected.get("health_state", ""),
        "recommended_action": selected_decision.get("recommended_action", decision.get("recommended_action", "")),
        "stop_reason": selected_decision.get("stop_reason", ""),
        "review_status": selected.get("review_status", ""),
        "human_needed": selected.get("human_needed", ""),
        "watch_reasons": selected_decision.get("watch_reasons", []),
        "task_health_decision": selected_decision,
    }
    return {
        "needed": needed,
        "snapshot_decision": decision,
        "packet": packet,
        "snapshot": snapshot if args.include_snapshot else {},
    }


def write_markdown(path: Path, result: dict[str, Any], output_json: str = "") -> str:
    packet = result.get("packet", {})
    decision = result.get("snapshot_decision", {})
    lines = [
        "# CoAgent Blocker Packet",
        "",
        f"- needed: `{result.get('needed')}`",
        f"- task_id: `{packet.get('task_id', '')}`",
        f"- class: `{packet.get('class', '')}`",
        f"- severity: `{packet.get('severity', '')}`",
        f"- health_state: `{packet.get('health_state', '')}`",
        f"- recommended_action: `{packet.get('recommended_action', decision.get('recommended_action', ''))}`",
        f"- stop_reason: `{packet.get('stop_reason', '')}`",
        f"- continue_allowed: `{packet.get('task_health_decision', {}).get('continue_allowed', decision.get('continue_allowed', ''))}`",
        f"- output_json: `{output_json}`",
        "",
        "## Human Action Required",
        "",
        str(packet.get("human_action_required", "")),
        "",
        "## Why Now",
        "",
        str(packet.get("why_now", "")),
        "",
        "## Evidence Paths",
        "",
    ]
    for evidence in packet.get("evidence_paths", []):
        lines.append(f"- `{evidence}`")
    if not packet.get("evidence_paths"):
        lines.append("- none")
    lines.extend(["", "## Resume", "", f"- resume_packet_path: `{packet.get('resume_packet_path', '')}`"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rel(path)


def run_packet(args: argparse.Namespace) -> dict[str, Any]:
    result = build_packet(args)
    outputs: dict[str, str] = {}
    metadata_recorded = False
    if result["needed"] or args.write_when_clear:
        output = project_path(args.output or (DEFAULT_OUTPUT_ROOT / f"{args.task_id}.blocker.json"))
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result["packet"], ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        outputs["json"] = rel(output)
        if args.markdown_output:
            outputs["markdown"] = write_markdown(project_path(args.markdown_output), result, outputs["json"])
    elif args.markdown_output:
        outputs["markdown"] = write_markdown(project_path(args.markdown_output), result, "")
    if getattr(args, "record_metadata", False):
        patch = {
            "blocker_packet_checked_at": now_iso(),
            "blocker_packet_needed": bool(result["needed"]),
            "blocker_packet_decision": result["snapshot_decision"],
        }
        if outputs.get("json"):
            patch["blocker_packet_path"] = outputs["json"]
        if outputs.get("markdown"):
            patch["blocker_packet_markdown"] = outputs["markdown"]
        runtime.update_metadata(
            argparse.Namespace(
                db=args.db,
                events=args.events,
                task_id=args.task_id,
                actor=getattr(args, "actor", "MainAgent"),
                claim_token=getattr(args, "claim_token", ""),
                summary=getattr(args, "summary", "record blocker packet status"),
                metadata=json.dumps(patch, ensure_ascii=False, sort_keys=True),
            )
        )
        metadata_recorded = True
    return {
        "ok": True,
        "needed": result["needed"],
        "outputs": outputs,
        "metadata_recorded": metadata_recorded,
        "decision": result["snapshot_decision"],
        "packet": result["packet"] if args.include_packet else {},
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=runtime.DEFAULT_DB)
    parser.add_argument("--events", type=Path, default=runtime.DEFAULT_EVENTS)
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--stale-minutes", type=int, default=task_health.DEFAULT_STALE_MINUTES)
    parser.add_argument("--staged-file-warning-threshold", type=int, default=preflight.STAGED_BROAD_THRESHOLD)
    parser.add_argument("--skip-preflight", action="store_true")
    parser.add_argument("--skip-runtime-audit", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--write-when-clear", action="store_true")
    parser.add_argument("--record-metadata", action="store_true")
    parser.add_argument("--claim-token", default="")
    parser.add_argument("--actor", default="MainAgent")
    parser.add_argument("--summary", default="record blocker packet status")
    parser.add_argument("--include-snapshot", action="store_true")
    parser.add_argument("--include-packet", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_packet(args)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"blocker_packet ok={result['ok']} needed={result['needed']}")
        for key, value in result["outputs"].items():
            print(f"{key}={value}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
