#!/usr/bin/env python3
"""Export a compact CoAgent status bundle for human review."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results" / "coagent_status"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.context import context_pack, context_quality
from CoAgent.devops import git_handoff_packet
from CoAgent.doctor import coagent_doctor
from CoAgent.evidence import evidence_manifest
from CoAgent.evidence.refresh_commands import standard_refresh_commands
from CoAgent.hooks import preflight
from CoAgent.review_queue import review_queue
from CoAgent.runtime import mosim_agent_runtime as runtime
from CoAgent.task_health import task_health


def blocker_packet_command(task_id: str, *, record_metadata: bool = False) -> str:
    command = (
        f"python3 CoAgent/blocker_packet/blocker_packet.py --task-id {task_id} "
        f"--output Results/agent_packets/blockers/{task_id}.blocker.json "
        f"--markdown-output Results/agent_packets/blockers/{task_id}.blocker.md --json"
    )
    if record_metadata:
        command += " --record-metadata --claim-token <claim-token>"
    return command


def resume_task_health_summary(task_health_info: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(task_health_info, dict):
        return {}
    return {
        "enabled": task_health_info.get("enabled", False),
        "ok": task_health_info.get("ok", ""),
        "continue_allowed": task_health_info.get("continue_allowed", ""),
        "recommended_action": task_health_info.get("recommended_action", ""),
        "stop_reason": task_health_info.get("stop_reason", ""),
        "next_intervention": task_health_info.get("next_intervention", ""),
        "blocking_task_ids": task_health_info.get("blocking_task_ids", []),
        "watch_task_ids": task_health_info.get("watch_task_ids", []),
        "human_task_ids": task_health_info.get("human_task_ids", []),
        "review_task_ids": task_health_info.get("review_task_ids", []),
        "safety_task_ids": task_health_info.get("safety_task_ids", []),
        "decision": task_health_info.get("decision", {}),
        "warning_count": task_health_info.get("warning_count", ""),
        "fail_count": task_health_info.get("fail_count", ""),
        "tasks": task_health_info.get("tasks", []),
    }


def resume_evidence_manifest_summary(evidence_manifest_info: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(evidence_manifest_info, dict):
        return {}
    return {
        "enabled": evidence_manifest_info.get("enabled", False),
        "ok": evidence_manifest_info.get("ok", ""),
        "outputs": evidence_manifest_info.get("outputs", {}),
        "freshness_status": evidence_manifest_info.get("freshness_status", ""),
        "stale_refresh_recommended": evidence_manifest_info.get("stale_refresh_recommended", ""),
        "refresh_commands": evidence_manifest_info.get("refresh_commands", []),
        "evidence_count": evidence_manifest_info.get("evidence_count", ""),
        "missing_count": evidence_manifest_info.get("missing_count", ""),
        "stale_count": evidence_manifest_info.get("stale_count", ""),
        "critical_stale_count": evidence_manifest_info.get("critical_stale_count", ""),
        "archival_stale_count": evidence_manifest_info.get("archival_stale_count", ""),
        "unknown_freshness_count": evidence_manifest_info.get("unknown_freshness_count", ""),
        "by_kind": evidence_manifest_info.get("by_kind", {}),
        "missing": evidence_manifest_info.get("missing", []),
        "stale": evidence_manifest_info.get("stale", []),
    }


def evidence_refresh_commands(task_id: str) -> list[str]:
    return standard_refresh_commands(task_id)


def project_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    if not (resolved == ROOT.resolve() or ROOT.resolve() in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def doctor_summary() -> dict[str, Any]:
    report = coagent_doctor.collect(argparse.Namespace(output=None, json=True, mode="quick", skip_status_export=True))
    return {
        "overallStatus": report["overallStatus"],
        "mode": report.get("mode"),
        "elapsed_seconds": report.get("elapsed_seconds"),
        "counts": report["counts"],
        "warnings": [
            {"id": check["id"], "summary": check["summary"]}
            for check in report["checks"].values()
            if check["status"] == "warning"
        ],
        "failures": [
            {"id": check["id"], "summary": check["summary"]}
            for check in report["checks"].values()
            if check["status"] == "fail"
        ],
    }


def maybe_context_quality(args: argparse.Namespace) -> dict[str, Any]:
    if not args.include_context_quality:
        return {"enabled": False}
    context_output = project_path(args.context_output or (DEFAULT_OUTPUT_ROOT / f"{args.task_id}.context.md"))
    built = context_pack.build_context_pack(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            task_id=args.task_id,
            output=context_output,
            event_limit=args.event_limit,
            knowledge_query=[],
            decision=[],
            blocker=[],
            include_memory_context=False,
            memory_policy=None,
            memory_limit_per_query=None,
            memory_max_hits=None,
            memory_max_chars=None,
            warn_chars=args.warn_chars,
            fail_chars=args.fail_chars,
        )
    )
    quality = context_quality.check_file(argparse.Namespace(path=context_output, warn_chars=args.warn_chars, fail_chars=args.fail_chars, json=True))
    return {"enabled": True, "context_path": built["output"], "metrics": built["metrics"], "quality": quality}


def preflight_summary(args: argparse.Namespace) -> dict[str, Any]:
    if not args.include_preflight_summary:
        return {"enabled": False}
    data = preflight.collect(
        argparse.Namespace(
            path=[],
            write_path=[],
            command=[],
            result_packet=[],
            large_limit_mb=100,
            full_repo_large_scan=False,
            allow_destructive_command=False,
            allow_broad_git=False,
            staged_file_warning_threshold=args.staged_file_warning_threshold,
        )
    )
    git_state = data.get("git_workspace_state", {})
    runtime_ignore = data.get("runtime_output_ignore", {})
    return {
        "enabled": True,
        "ok": bool(data.get("ok")),
        "git_workspace_state": {
            "ok": bool(git_state.get("ok")),
            "staged_count": git_state.get("staged_count"),
            "staged_limit": git_state.get("staged_limit"),
            "staged_runtime_count": git_state.get("staged_runtime_count"),
            "staged_external_count": git_state.get("staged_external_count"),
            "index_lock_present": git_state.get("index_lock_present"),
            "findings": git_state.get("findings", []),
        },
        "runtime_output_ignore": {
            "ok": bool(runtime_ignore.get("ok")),
            "ignored_count": runtime_ignore.get("ignored_count"),
            "missing": runtime_ignore.get("missing", []),
        },
    }


def runtime_audit_summary(args: argparse.Namespace) -> dict[str, Any]:
    if not args.include_runtime_audit:
        return {"enabled": False}
    audit = runtime.audit_event_stream(argparse.Namespace(db=args.db, events=args.events))
    return {
        "enabled": True,
        "ok": audit.get("ok"),
        "task_count": audit.get("task_count"),
        "db_event_count": audit.get("db_event_count"),
        "jsonl_event_count": audit.get("jsonl_event_count"),
        "invalid_jsonl_count": audit.get("invalid_jsonl_count"),
        "missing_in_jsonl_count": audit.get("missing_in_jsonl_count"),
        "missing_in_db_count": audit.get("missing_in_db_count"),
        "sensitive_db_event_count": audit.get("sensitive_db_event_count"),
        "sensitive_jsonl_event_count": audit.get("sensitive_jsonl_event_count"),
        "warning_count": audit.get("warning_count"),
        "fail_count": audit.get("fail_count"),
        "findings": audit.get("findings", [])[:20],
    }


def task_health_summary(args: argparse.Namespace) -> dict[str, Any]:
    if not getattr(args, "include_task_health", True):
        return {"enabled": False}
    snapshot = task_health.build_snapshot(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            task_id=args.task_id,
            state="",
            active_only=True,
            stale_minutes=getattr(args, "stale_minutes", task_health.DEFAULT_STALE_MINUTES),
            staged_file_warning_threshold=getattr(args, "staged_file_warning_threshold", preflight.STAGED_BROAD_THRESHOLD),
            skip_preflight=False,
            skip_runtime_audit=False,
        )
    )
    return {
        "enabled": True,
        "ok": snapshot.get("ok"),
        "continue_allowed": snapshot.get("continue_allowed"),
        "recommended_action": snapshot.get("recommended_action", ""),
        "stop_reason": snapshot.get("stop_reason", ""),
        "next_intervention": snapshot.get("next_intervention", ""),
        "blocking_task_ids": snapshot.get("blocking_task_ids", []),
        "watch_task_ids": snapshot.get("watch_task_ids", []),
        "human_task_ids": snapshot.get("human_task_ids", []),
        "review_task_ids": snapshot.get("review_task_ids", []),
        "safety_task_ids": snapshot.get("safety_task_ids", []),
        "decision": snapshot.get("decision", {}),
        "task_count": snapshot.get("task_count"),
        "fail_count": snapshot.get("fail_count"),
        "warning_count": snapshot.get("warning_count"),
        "stale_minutes": snapshot.get("stale_minutes"),
        "tasks": [
            {
                "task_id": item.get("task_id", ""),
                "runtime_state": item.get("runtime_state", ""),
                "health_state": item.get("health_state", ""),
                "decision": item.get("decision", {}),
                "last_event_age_minutes": item.get("last_event_age_minutes", ""),
                "next_action": item.get("next_action", ""),
                "findings": item.get("findings", []),
            }
            for item in snapshot.get("tasks", [])[:10]
        ],
    }


def git_handoff_summary(args: argparse.Namespace) -> dict[str, Any]:
    if not getattr(args, "include_git_handoff", True):
        return {"enabled": False}
    packet = git_handoff_packet.build_packet(
        argparse.Namespace(
            task_id=args.task_id,
            staged_file_warning_threshold=getattr(args, "staged_file_warning_threshold", preflight.STAGED_BROAD_THRESHOLD),
        )
    )
    return {
        "enabled": True,
        "ok": packet.get("ok"),
        "totals": packet.get("totals", {}),
        "blockers": packet.get("blockers", []),
        "required_review_gates": packet.get("required_review_gates", []),
        "recommended_sequence": packet.get("recommended_sequence", []),
        "global_risks": [item for item in packet.get("global_risks", []) if item],
        "next_action": packet.get("next_action", ""),
    }


def evidence_manifest_summary(args: argparse.Namespace) -> dict[str, Any]:
    if not getattr(args, "include_evidence_manifest", True):
        return {"enabled": False}
    manifest_result = evidence_manifest.run_manifest(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            task_id=args.task_id,
            output=args.evidence_manifest_output
            or (DEFAULT_OUTPUT_ROOT / f"{args.task_id}.evidence_manifest.json"),
            markdown_output=args.evidence_manifest_markdown_output
            or (DEFAULT_OUTPUT_ROOT / f"{args.task_id}.evidence_manifest.md"),
            include_manifest=True,
            json=True,
        )
    )
    manifest = manifest_result.get("manifest", {})
    return {
        "enabled": True,
        "ok": manifest_result.get("ok"),
        "outputs": manifest_result.get("outputs", {}),
        "freshness_status": manifest.get("freshness_status", ""),
        "stale_refresh_recommended": manifest.get("stale_refresh_recommended", False),
        "refresh_commands": manifest.get("refresh_commands", []),
        "evidence_count": manifest.get("evidence_count", 0),
        "missing_count": manifest.get("missing_count", 0),
        "stale_count": manifest.get("stale_count", 0),
        "critical_stale_count": manifest.get("critical_stale_count", 0),
        "archival_stale_count": manifest.get("archival_stale_count", 0),
        "unknown_freshness_count": manifest.get("unknown_freshness_count", 0),
        "task_last_event_at": manifest.get("task_last_event_at", ""),
        "by_kind": manifest.get("by_kind", {}),
        "missing": [
            {"path": item.get("path", ""), "sources": item.get("sources", [])}
            for item in manifest.get("missing", [])[:20]
        ],
        "stale": [
            {
                "path": item.get("path", ""),
                "modified_at": item.get("modified_at", ""),
                "age_after_task_last_event_seconds": item.get("age_after_task_last_event_seconds", ""),
                "sources": item.get("sources", []),
            }
            for item in manifest.get("stale", [])[:20]
        ],
    }


def build_bundle(args: argparse.Namespace) -> dict[str, Any]:
    task = runtime.show_task(argparse.Namespace(db=args.db, events=args.events, task_id=args.task_id))
    active = runtime.status_board(argparse.Namespace(db=args.db, events=args.events, state=None, active_only=True))
    queue = review_queue.build_queue(
        argparse.Namespace(
            db=args.db,
            include_terminal=args.include_terminal_reviews,
            include_superseded=args.include_superseded_reviews,
            json=True,
        )
    )
    return {
        "task_id": args.task_id,
        "task": {
            "task_id": task["task_id"],
            "state": task["state"],
            "owner": task["owner"],
            "role": task["role"],
            "objective": task["objective"],
            "updated_at": task["updated_at"],
            "last_event_at": task["last_event_at"],
            "metadata": task["metadata"],
            "event_count": len(task.get("events", [])),
            "last_events": task.get("events", [])[-args.event_limit :],
        },
        "active_tasks": active,
        "review_queue": queue,
        "doctor": doctor_summary(),
        "context_quality": maybe_context_quality(args),
        "preflight": preflight_summary(args),
        "runtime_audit": runtime_audit_summary(args),
        "task_health": task_health_summary(args),
        "git_handoff": git_handoff_summary(args),
        "evidence_manifest": evidence_manifest_summary(args),
    }


def write_markdown(path: Path, bundle: dict[str, Any]) -> str:
    task = bundle["task"]
    doctor = bundle["doctor"]
    queue = bundle["review_queue"]
    context = bundle.get("context_quality", {})
    preflight_info = bundle.get("preflight", {})
    runtime_audit = bundle.get("runtime_audit", {})
    task_health_info = bundle.get("task_health", {})
    git_handoff_info = bundle.get("git_handoff", {})
    evidence_manifest_info = bundle.get("evidence_manifest", {})
    quality = context.get("quality", {}) if isinstance(context, dict) else {}
    metrics = context.get("metrics", {}) if isinstance(context, dict) else {}
    git_state = preflight_info.get("git_workspace_state", {}) if isinstance(preflight_info, dict) else {}
    runtime_ignore = preflight_info.get("runtime_output_ignore", {}) if isinstance(preflight_info, dict) else {}
    lines = [
        f"# CoAgent Status: {bundle['task_id']}",
        "",
        f"- state: `{task['state']}`",
        f"- owner: `{task['owner']}`",
        f"- role: `{task['role']}`",
        f"- updated_at: `{task['updated_at']}`",
        f"- doctor: `{doctor['overallStatus']}` mode={doctor.get('mode', '')} elapsed={doctor.get('elapsed_seconds', '')}s ok={doctor['counts']['ok']} warning={doctor['counts']['warning']} fail={doctor['counts']['fail']}",
        f"- review_queue_count: `{queue['count']}`",
        f"- suppressed_review_count: `{queue.get('suppressed_count', 0)}`",
        f"- context_quality: `{quality.get('ok', 'disabled')}`",
        f"- context_chars: `{metrics.get('char_count', quality.get('char_count', ''))}`",
        f"- context_estimated_tokens: `{metrics.get('estimated_tokens', '')}`",
        f"- preflight: `{preflight_info.get('ok', 'disabled')}`",
        f"- runtime_event_audit: `{runtime_audit.get('ok', 'disabled')}`",
        f"- runtime_db_event_count: `{runtime_audit.get('db_event_count', '')}`",
        f"- runtime_jsonl_event_count: `{runtime_audit.get('jsonl_event_count', '')}`",
        f"- runtime_sensitive_db_event_count: `{runtime_audit.get('sensitive_db_event_count', '')}`",
        f"- runtime_sensitive_jsonl_event_count: `{runtime_audit.get('sensitive_jsonl_event_count', '')}`",
        f"- task_health: `{task_health_info.get('ok', 'disabled')}`",
        f"- task_continue_allowed: `{task_health_info.get('continue_allowed', '')}`",
        f"- task_recommended_action: `{task_health_info.get('recommended_action', '')}`",
        f"- task_health_warning_count: `{task_health_info.get('warning_count', '')}`",
        f"- task_health_fail_count: `{task_health_info.get('fail_count', '')}`",
        f"- blocker_packet_needed: `{task_health_info.get('decision', {}).get('continue_allowed') is False if isinstance(task_health_info, dict) and task_health_info.get('enabled') else ''}`",
        f"- git_handoff: `{git_handoff_info.get('ok', 'disabled')}`",
        f"- git_handoff_batch_count: `{git_handoff_info.get('totals', {}).get('batch_count', '')}`",
        f"- git_handoff_overlap_count: `{git_handoff_info.get('totals', {}).get('staged_unstaged_overlap_count', '')}`",
        f"- evidence_manifest: `{evidence_manifest_info.get('ok', 'disabled')}`",
        f"- evidence_manifest_count: `{evidence_manifest_info.get('evidence_count', '')}`",
        f"- evidence_manifest_missing_count: `{evidence_manifest_info.get('missing_count', '')}`",
        f"- evidence_manifest_stale_count: `{evidence_manifest_info.get('stale_count', '')}`",
        f"- evidence_manifest_critical_stale_count: `{evidence_manifest_info.get('critical_stale_count', '')}`",
        f"- evidence_manifest_archival_stale_count: `{evidence_manifest_info.get('archival_stale_count', '')}`",
        f"- evidence_manifest_refresh_recommended: `{evidence_manifest_info.get('stale_refresh_recommended', '')}`",
        f"- git_index_lock_present: `{git_state.get('index_lock_present', '')}`",
        f"- git_staged_count: `{git_state.get('staged_count', '')}`",
        f"- git_staged_runtime_count: `{git_state.get('staged_runtime_count', '')}`",
        f"- git_staged_external_count: `{git_state.get('staged_external_count', '')}`",
        f"- runtime_output_ignore: `{runtime_ignore.get('ok', '')}`",
        "",
        "## Objective",
        "",
        task["objective"],
        "",
        "## Checkpoint",
        "",
        str(task["metadata"].get("checkpoint", "")),
        "",
        "## Next Action",
        "",
        str(task["metadata"].get("next_action", "")),
        "",
        "## Review Closeout",
        "",
        f"- review_status: `{task['metadata'].get('review_status', '')}`",
        f"- human_needed: `{task['metadata'].get('human_needed', '')}`",
        f"- review_decision_by: `{task['metadata'].get('review_decision_by', '')}`",
        f"- review_closeout_path: `{task['metadata'].get('review_closeout_path', '')}`",
        f"- blocker_packet_path: `{task['metadata'].get('blocker_packet_path', '')}`",
        f"- blocker_packet_markdown: `{task['metadata'].get('blocker_packet_markdown', '')}`",
        "",
        "## Review Queue",
        "",
    ]
    if queue["items"]:
        for item in queue["items"]:
            lines.append(
                f"- `{item['task_id']}` state={item['state']} review={item['review_status']} "
                f"next={item['next_action']} closeout={item.get('review_closeout_path', '')}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Doctor Issues", ""])
    issues = doctor["failures"] + doctor["warnings"]
    if issues:
        for item in issues:
            lines.append(f"- `{item['id']}` {item['summary']}")
    else:
        lines.append("- none")
    lines.extend(["", "## Context Quality", ""])
    if context.get("enabled"):
        lines.append(f"- context_path: `{context.get('context_path', '')}`")
        lines.append(f"- ok: `{quality.get('ok', '')}`")
        for key in ["char_count", "estimated_tokens", "event_count_included", "event_count_total", "warn_chars", "fail_chars"]:
            if key in metrics:
                lines.append(f"- {key}: `{metrics[key]}`")
        issues = quality.get("issues", []) if isinstance(quality, dict) else []
        if issues:
            for issue in issues:
                lines.append(f"- issue: `{issue}`")
        else:
            lines.append("- issues: none")
    else:
        lines.append("- disabled")
    lines.extend(["", "## Git And Runtime Preflight", ""])
    if preflight_info.get("enabled"):
        lines.append(f"- ok: `{preflight_info.get('ok')}`")
        lines.append(f"- index_lock_present: `{git_state.get('index_lock_present')}`")
        lines.append(f"- staged_count: `{git_state.get('staged_count')}`")
        lines.append(f"- staged_limit: `{git_state.get('staged_limit')}`")
        lines.append(f"- staged_runtime_count: `{git_state.get('staged_runtime_count')}`")
        lines.append(f"- staged_external_count: `{git_state.get('staged_external_count')}`")
        lines.append(f"- runtime_output_ignore_ok: `{runtime_ignore.get('ok')}`")
        lines.append(f"- runtime_output_ignore_missing: `{len(runtime_ignore.get('missing', []))}`")
        findings = git_state.get("findings", [])
        if findings:
            for finding in findings:
                lines.append(f"- finding: `{finding.get('severity')}` `{finding.get('reason')}` value=`{finding.get('value')}`")
        else:
            lines.append("- findings: none")
    else:
        lines.append("- disabled")
    lines.extend(["", "## Runtime Event Audit", ""])
    if runtime_audit.get("enabled"):
        lines.append(f"- ok: `{runtime_audit.get('ok')}`")
        lines.append(f"- task_count: `{runtime_audit.get('task_count')}`")
        lines.append(f"- db_event_count: `{runtime_audit.get('db_event_count')}`")
        lines.append(f"- jsonl_event_count: `{runtime_audit.get('jsonl_event_count')}`")
        lines.append(f"- invalid_jsonl_count: `{runtime_audit.get('invalid_jsonl_count')}`")
        lines.append(f"- missing_in_jsonl_count: `{runtime_audit.get('missing_in_jsonl_count')}`")
        lines.append(f"- missing_in_db_count: `{runtime_audit.get('missing_in_db_count')}`")
        lines.append(f"- sensitive_db_event_count: `{runtime_audit.get('sensitive_db_event_count')}`")
        lines.append(f"- sensitive_jsonl_event_count: `{runtime_audit.get('sensitive_jsonl_event_count')}`")
        findings = runtime_audit.get("findings", [])
        if findings:
            for finding in findings:
                lines.append(f"- finding: `{finding.get('severity')}` `{finding.get('reason')}`")
        else:
            lines.append("- findings: none")
    else:
        lines.append("- disabled")
    lines.extend(["", "## Task Health", ""])
    if task_health_info.get("enabled"):
        decision = task_health_info.get("decision", {})
        lines.append(f"- ok: `{task_health_info.get('ok')}`")
        lines.append(f"- continue_allowed: `{decision.get('continue_allowed', '')}`")
        lines.append(f"- recommended_action: `{decision.get('recommended_action', '')}`")
        lines.append(f"- blocking_task_ids: `{', '.join(decision.get('blocking_task_ids', [])) if decision.get('blocking_task_ids') else 'none'}`")
        lines.append(f"- blocker_packet_needed: `{decision.get('continue_allowed') is False}`")
        lines.append(f"- blocker_packet_command: `{blocker_packet_command(bundle['task_id'])}`")
        lines.append(f"- task_count: `{task_health_info.get('task_count')}`")
        lines.append(f"- warning_count: `{task_health_info.get('warning_count')}`")
        lines.append(f"- fail_count: `{task_health_info.get('fail_count')}`")
        for item in task_health_info.get("tasks", []):
            item_decision = item.get("decision", {})
            lines.append(
                f"- `{item.get('task_id', '')}` runtime={item.get('runtime_state', '')} "
                f"health={item.get('health_state', '')} continue={item_decision.get('continue_allowed', '')} "
                f"action={item_decision.get('recommended_action', '')} age_min={item.get('last_event_age_minutes', '')}"
            )
            if item_decision.get("stop_reason"):
                lines.append(f"  stop_reason: `{item_decision.get('stop_reason')}`")
            if item.get("next_action"):
                lines.append(f"  next: {item.get('next_action')}")
            for finding_item in item.get("findings", []):
                lines.append(
                    f"  finding: `{finding_item.get('severity', '')}` "
                    f"`{finding_item.get('reason', '')}` -> {finding_item.get('next_action', '')}"
                )
    else:
        lines.append("- disabled")
    lines.extend(["", "## Git Handoff", ""])
    if git_handoff_info.get("enabled"):
        totals = git_handoff_info.get("totals", {})
        lines.append(f"- ok: `{git_handoff_info.get('ok')}`")
        lines.append(f"- batch_count: `{totals.get('batch_count')}`")
        lines.append(f"- total_file_count: `{totals.get('total_file_count')}`")
        lines.append(f"- staged_file_count: `{totals.get('staged_file_count')}`")
        lines.append(f"- worktree_file_count: `{totals.get('worktree_file_count')}`")
        lines.append(f"- staged_unstaged_overlap_count: `{totals.get('staged_unstaged_overlap_count')}`")
        blockers = git_handoff_info.get("blockers", [])
        if blockers:
            for item in blockers:
                lines.append(f"- blocker: `{item.get('blocker', '')}` -> {item.get('action', '')}")
        else:
            lines.append("- blockers: none")
        risks = git_handoff_info.get("global_risks", [])
        lines.append(f"- global_risks: `{', '.join(risks) if risks else 'none'}`")
        lines.append(f"- recommended_sequence: `{', '.join(git_handoff_info.get('recommended_sequence', []))}`")
        lines.append(f"- next_action: {git_handoff_info.get('next_action', '')}")
    else:
        lines.append("- disabled")
    lines.extend(["", "## Evidence Manifest", ""])
    if evidence_manifest_info.get("enabled"):
        lines.append(f"- ok: `{evidence_manifest_info.get('ok')}`")
        for key, value in evidence_manifest_info.get("outputs", {}).items():
            lines.append(f"- {key}: `{value}`")
        lines.append(f"- evidence_count: `{evidence_manifest_info.get('evidence_count')}`")
        lines.append(f"- missing_count: `{evidence_manifest_info.get('missing_count')}`")
        lines.append(f"- stale_count: `{evidence_manifest_info.get('stale_count')}`")
        lines.append(f"- critical_stale_count: `{evidence_manifest_info.get('critical_stale_count')}`")
        lines.append(f"- archival_stale_count: `{evidence_manifest_info.get('archival_stale_count')}`")
        lines.append(f"- unknown_freshness_count: `{evidence_manifest_info.get('unknown_freshness_count')}`")
        lines.append(f"- freshness_status: `{evidence_manifest_info.get('freshness_status', '')}`")
        lines.append(f"- stale_refresh_recommended: `{evidence_manifest_info.get('stale_refresh_recommended', False)}`")
        for kind, count in sorted(evidence_manifest_info.get("by_kind", {}).items()):
            lines.append(f"- `{kind}`: `{count}`")
        missing = evidence_manifest_info.get("missing", [])
        if missing:
            for item in missing:
                lines.append(f"- missing: `{item.get('path', '')}` sources={','.join(item.get('sources', []))}")
        else:
            lines.append("- missing: none")
        stale = evidence_manifest_info.get("stale", [])
        if stale:
            for item in stale:
                lines.append(
                    f"- stale: `{item.get('path', '')}` modified={item.get('modified_at', '')} "
                    f"age_after_task_last_event_seconds={item.get('age_after_task_last_event_seconds', '')}"
                )
            lines.extend(["", "### Refresh Commands", ""])
            for command in evidence_manifest_info.get("refresh_commands", evidence_refresh_commands(bundle["task_id"])):
                lines.append(f"- `{command}`")
        else:
            lines.append("- stale: none")
    else:
        lines.append("- disabled")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rel(path)


def build_resume_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    task = bundle["task"]
    metadata = task.get("metadata", {})
    doctor = bundle.get("doctor", {})
    preflight_info = bundle.get("preflight", {})
    runtime_audit = bundle.get("runtime_audit", {})
    task_health_info = bundle.get("task_health", {})
    git_handoff_info = bundle.get("git_handoff", {})
    evidence_manifest_info = bundle.get("evidence_manifest", {})
    review_queue_data = bundle.get("review_queue", {})
    context = bundle.get("context_quality", {})
    quality = context.get("quality", {}) if isinstance(context, dict) else {}
    metrics = context.get("metrics", {}) if isinstance(context, dict) else {}
    git_state = preflight_info.get("git_workspace_state", {}) if isinstance(preflight_info, dict) else {}
    runtime_ignore = preflight_info.get("runtime_output_ignore", {}) if isinstance(preflight_info, dict) else {}
    resume_task_health = resume_task_health_summary(task_health_info)
    resume_evidence_manifest = resume_evidence_manifest_summary(evidence_manifest_info)
    return {
        "schema_type": "coagent_resume_bundle",
        "schema_version": 1,
        "task_id": bundle["task_id"],
        "state": task["state"],
        "owner": task["owner"],
        "role": task["role"],
        "objective": task["objective"],
        "updated_at": task["updated_at"],
        "last_event_at": task["last_event_at"],
        "checkpoint": metadata.get("checkpoint", ""),
        "next_action": metadata.get("next_action", ""),
        "continue_allowed": resume_task_health.get("continue_allowed", ""),
        "recommended_action": resume_task_health.get("recommended_action", ""),
        "stop_reason": resume_task_health.get("stop_reason", ""),
        "next_intervention": resume_task_health.get("next_intervention", ""),
        "blocking_task_ids": resume_task_health.get("blocking_task_ids", []),
        "watch_task_ids": resume_task_health.get("watch_task_ids", []),
        "human_task_ids": resume_task_health.get("human_task_ids", []),
        "review_task_ids": resume_task_health.get("review_task_ids", []),
        "safety_task_ids": resume_task_health.get("safety_task_ids", []),
        "task_health": resume_task_health,
        "evidence_manifest_summary": resume_evidence_manifest,
        "review": {
            "review_status": metadata.get("review_status", ""),
            "human_needed": metadata.get("human_needed", ""),
            "requires_human_review": metadata.get("requires_human_review", ""),
            "review_owner": metadata.get("review_owner", ""),
            "review_path": metadata.get("review_path", ""),
            "review_closeout_path": metadata.get("review_closeout_path", ""),
            "notification_packet_path": metadata.get("notification_packet_path", ""),
            "blocker_packet_path": metadata.get("blocker_packet_path", ""),
            "blocker_packet_markdown": metadata.get("blocker_packet_markdown", ""),
            "blocker_packet_needed": task_health_info.get("decision", {}).get("continue_allowed") is False
            if isinstance(task_health_info, dict) and task_health_info.get("enabled")
            else "",
            "blocker_packet_command": blocker_packet_command(bundle["task_id"]),
            "blocker_packet_record_command": blocker_packet_command(bundle["task_id"], record_metadata=True),
            "review_package_path": metadata.get("review_package_path", ""),
            "review_package_markdown": metadata.get("review_package_markdown", ""),
            "queue_count": review_queue_data.get("count", 0),
            "queue_items": [
                {
                    "task_id": item.get("task_id", ""),
                    "state": item.get("state", ""),
                    "review_status": item.get("review_status", ""),
                    "next_action": item.get("next_action", ""),
                    "reasons": item.get("reasons", []),
                }
                for item in review_queue_data.get("items", [])[:10]
            ],
        },
        "evidence": {
            "files_changed": metadata.get("files_changed", []),
            "commands_run": metadata.get("commands_run", []),
            "evidence_paths": metadata.get("evidence", []),
            "status_export_path": metadata.get("status_export_path", ""),
            "status_export_markdown": metadata.get("status_export_markdown", ""),
            "resume_bundle_path": metadata.get("resume_bundle_path", ""),
            "resume_bundle_markdown": metadata.get("resume_bundle_markdown", ""),
            "task_health_path": metadata.get("task_health_path", ""),
            "task_health_markdown": metadata.get("task_health_markdown", ""),
            "git_handoff_path": metadata.get("git_handoff_path", ""),
            "git_handoff_markdown": metadata.get("git_handoff_markdown", ""),
            "evidence_manifest_path": metadata.get("evidence_manifest_path", ""),
            "evidence_manifest_markdown": metadata.get("evidence_manifest_markdown", ""),
            "review_package_path": metadata.get("review_package_path", ""),
            "review_package_markdown": metadata.get("review_package_markdown", ""),
            "blocker_packet_path": metadata.get("blocker_packet_path", ""),
            "blocker_packet_markdown": metadata.get("blocker_packet_markdown", ""),
        },
        "health": {
            "doctor": {
                "overallStatus": doctor.get("overallStatus", ""),
                "mode": doctor.get("mode", ""),
                "elapsed_seconds": doctor.get("elapsed_seconds", ""),
                "counts": doctor.get("counts", {}),
                "warnings": doctor.get("warnings", []),
                "failures": doctor.get("failures", []),
            },
            "context_quality": {
                "enabled": context.get("enabled", False) if isinstance(context, dict) else False,
                "ok": quality.get("ok", ""),
                "context_path": context.get("context_path", "") if isinstance(context, dict) else "",
                "char_count": metrics.get("char_count", ""),
                "estimated_tokens": metrics.get("estimated_tokens", ""),
            },
            "preflight": {
                "ok": preflight_info.get("ok", "") if isinstance(preflight_info, dict) else "",
                "git_index_lock_present": git_state.get("index_lock_present", ""),
                "git_staged_count": git_state.get("staged_count", ""),
                "git_staged_runtime_count": git_state.get("staged_runtime_count", ""),
                "git_staged_external_count": git_state.get("staged_external_count", ""),
                "runtime_output_ignore_ok": runtime_ignore.get("ok", ""),
                "findings": git_state.get("findings", []),
            },
            "runtime_audit": {
                "ok": runtime_audit.get("ok", "") if isinstance(runtime_audit, dict) else "",
                "db_event_count": runtime_audit.get("db_event_count", ""),
                "jsonl_event_count": runtime_audit.get("jsonl_event_count", ""),
                "sensitive_db_event_count": runtime_audit.get("sensitive_db_event_count", ""),
                "sensitive_jsonl_event_count": runtime_audit.get("sensitive_jsonl_event_count", ""),
                "findings": runtime_audit.get("findings", []),
            },
            "task_health": resume_task_health,
            "git_handoff": {
                "enabled": git_handoff_info.get("enabled", False) if isinstance(git_handoff_info, dict) else False,
                "ok": git_handoff_info.get("ok", "") if isinstance(git_handoff_info, dict) else "",
                "totals": git_handoff_info.get("totals", {}) if isinstance(git_handoff_info, dict) else {},
                "blockers": git_handoff_info.get("blockers", []) if isinstance(git_handoff_info, dict) else [],
                "global_risks": git_handoff_info.get("global_risks", []) if isinstance(git_handoff_info, dict) else [],
                "recommended_sequence": git_handoff_info.get("recommended_sequence", []) if isinstance(git_handoff_info, dict) else [],
                "next_action": git_handoff_info.get("next_action", "") if isinstance(git_handoff_info, dict) else "",
            },
            "evidence_manifest": resume_evidence_manifest,
        },
        "operating_limits": {
            "allowed_actions": metadata.get("allowed_actions", []),
            "forbidden_actions": metadata.get("forbidden_actions", []),
            "required_checks": metadata.get("required_checks", []),
            "stop_condition": metadata.get("circuit_breaker", ""),
            "current_gate": [
                "stay inside project-local CoAgent implementation",
                "do not expand app-server transport, unattended automation, new permanent departments, broad hooks, MCP/tools, external credentials, or non-dry-run notifications without approval",
                "do not print claim tokens or other token-like fields",
                "do not do one broad Git commit for the current large staged set; use split plan or DevOps handoff",
            ],
        },
        "resume_commands": [
            "python3 CoAgent/runtime/mosim_agent_runtime.py status-board --active-only",
            "python3 CoAgent/review_queue/review_queue.py list --json",
            "python3 CoAgent/runtime/mosim_agent_runtime.py audit-events",
            f"python3 CoAgent/task_health/task_health.py --task-id {bundle['task_id']} --output Results/coagent_status/{bundle['task_id']}.task_health.json --markdown-output Results/coagent_status/{bundle['task_id']}.task_health.md --json",
            f"python3 CoAgent/devops/git_handoff_packet.py --task-id {bundle['task_id']} --output Results/coagent_status/{bundle['task_id']}.git_handoff.json --markdown-output Results/coagent_status/{bundle['task_id']}.git_handoff.md --json",
            f"python3 CoAgent/evidence/evidence_manifest.py --task-id {bundle['task_id']} --output Results/coagent_status/{bundle['task_id']}.evidence_manifest.json --markdown-output Results/coagent_status/{bundle['task_id']}.evidence_manifest.md --json",
            f"python3 CoAgent/review_package/review_package.py --task-id {bundle['task_id']} --output Results/coagent_status/{bundle['task_id']}.review_package.json --markdown-output Results/coagent_status/{bundle['task_id']}.review_package.md --json",
            blocker_packet_command(bundle["task_id"]),
            "python3 CoAgent/doctor/coagent_doctor.py --json --output Results/coagent_doctor/latest_gateway.json",
            f"python3 CoAgent/status_export/status_export.py --task-id {bundle['task_id']} --output Results/coagent_status/{bundle['task_id']}.status.json --markdown-output Results/coagent_status/{bundle['task_id']}.status.md --resume-output Results/coagent_status/{bundle['task_id']}.resume.json --resume-markdown-output Results/coagent_status/{bundle['task_id']}.resume.md --json",
        ],
        "last_events": task.get("last_events", []),
    }


def write_resume_markdown(path: Path, resume: dict[str, Any]) -> str:
    review = resume["review"]
    health = resume["health"]
    evidence = resume["evidence"]
    limits = resume["operating_limits"]
    lines = [
        f"# CoAgent Resume: {resume['task_id']}",
        "",
        f"- state: `{resume['state']}`",
        f"- owner: `{resume['owner']}`",
        f"- role: `{resume['role']}`",
        f"- updated_at: `{resume['updated_at']}`",
        f"- doctor: `{health['doctor']['overallStatus']}` mode={health['doctor']['mode']} ok={health['doctor'].get('counts', {}).get('ok', '')} warning={health['doctor'].get('counts', {}).get('warning', '')} fail={health['doctor'].get('counts', {}).get('fail', '')}",
        f"- runtime_audit: `{health['runtime_audit']['ok']}` db={health['runtime_audit']['db_event_count']} jsonl={health['runtime_audit']['jsonl_event_count']} sensitive_db={health['runtime_audit']['sensitive_db_event_count']} sensitive_jsonl={health['runtime_audit']['sensitive_jsonl_event_count']}",
        f"- task_health: `{health['task_health']['ok']}` warning={health['task_health']['warning_count']} fail={health['task_health']['fail_count']}",
        f"- task_continue_allowed: `{health['task_health'].get('continue_allowed', '')}`",
        f"- task_recommended_action: `{health['task_health'].get('recommended_action', '')}`",
        f"- git_handoff: `{health['git_handoff']['ok']}` batches={health['git_handoff'].get('totals', {}).get('batch_count', '')} overlap={health['git_handoff'].get('totals', {}).get('staged_unstaged_overlap_count', '')}",
        f"- evidence_manifest: `{health['evidence_manifest']['ok']}` evidence={health['evidence_manifest']['evidence_count']} missing={health['evidence_manifest']['missing_count']}",
        f"- evidence_stale_count: `{health['evidence_manifest'].get('stale_count', '')}`",
        f"- evidence_critical_stale_count: `{health['evidence_manifest'].get('critical_stale_count', '')}`",
        f"- evidence_archival_stale_count: `{health['evidence_manifest'].get('archival_stale_count', '')}`",
        f"- evidence_refresh_recommended: `{health['evidence_manifest'].get('stale_refresh_recommended', '')}`",
        f"- review_status: `{review['review_status']}`",
        f"- human_needed: `{review['human_needed']}`",
        f"- review_queue_count: `{review['queue_count']}`",
        f"- blocker_packet_needed: `{review['blocker_packet_needed']}`",
        f"- git_staged_count: `{health['preflight']['git_staged_count']}`",
        "",
        "## Objective",
        "",
        resume["objective"],
        "",
        "## Checkpoint",
        "",
        str(resume["checkpoint"]),
        "",
        "## Next Action",
        "",
        str(resume["next_action"]),
        "",
        "## Review State",
        "",
        f"- review_path: `{review['review_path']}`",
        f"- review_closeout_path: `{review['review_closeout_path']}`",
        f"- notification_packet_path: `{review['notification_packet_path']}`",
        f"- blocker_packet_path: `{review['blocker_packet_path']}`",
        f"- blocker_packet_markdown: `{review['blocker_packet_markdown']}`",
        f"- blocker_packet_command: `{review['blocker_packet_command']}`",
        f"- blocker_packet_record_command: `{review['blocker_packet_record_command']}`",
        f"- review_package_path: `{review['review_package_path']}`",
        f"- review_package_markdown: `{review['review_package_markdown']}`",
    ]
    if review["queue_items"]:
        for item in review["queue_items"]:
            lines.append(f"- queued: `{item['task_id']}` state={item['state']} review={item['review_status']} next={item['next_action']}")
    else:
        lines.append("- queued: none")
    lines.extend(["", "## Task Health", ""])
    task_decision = health.get("task_health", {}).get("decision", {})
    if task_decision:
        lines.append(f"- continue_allowed: `{task_decision.get('continue_allowed')}`")
        lines.append(f"- recommended_action: `{task_decision.get('recommended_action')}`")
        lines.append(f"- blocking_task_ids: `{', '.join(task_decision.get('blocking_task_ids', [])) if task_decision.get('blocking_task_ids') else 'none'}`")
        lines.append(f"- next_intervention: {task_decision.get('next_intervention', '')}")
    task_health_items = health.get("task_health", {}).get("tasks", [])
    if task_health_items:
        for item in task_health_items:
            item_decision = item.get("decision", {})
            lines.append(
                f"- `{item.get('task_id', '')}` health={item.get('health_state', '')} "
                f"continue={item_decision.get('continue_allowed', '')} action={item_decision.get('recommended_action', '')} "
                f"runtime={item.get('runtime_state', '')} age_min={item.get('last_event_age_minutes', '')}"
            )
            if item_decision.get("stop_reason"):
                lines.append(f"  stop_reason: `{item_decision.get('stop_reason')}`")
            if item.get("next_action"):
                lines.append(f"  next: {item.get('next_action')}")
            for finding_item in item.get("findings", []):
                lines.append(
                    f"  finding: `{finding_item.get('severity', '')}` "
                    f"`{finding_item.get('reason', '')}` -> {finding_item.get('next_action', '')}"
                )
    else:
        lines.append("- none")
    lines.extend(["", "## Git Handoff", ""])
    git_handoff = health.get("git_handoff", {})
    if git_handoff.get("enabled"):
        totals = git_handoff.get("totals", {})
        lines.append(f"- ok: `{git_handoff.get('ok')}`")
        lines.append(f"- batch_count: `{totals.get('batch_count')}`")
        lines.append(f"- staged_file_count: `{totals.get('staged_file_count')}`")
        lines.append(f"- worktree_file_count: `{totals.get('worktree_file_count')}`")
        lines.append(f"- staged_unstaged_overlap_count: `{totals.get('staged_unstaged_overlap_count')}`")
        lines.append(f"- global_risks: `{', '.join(git_handoff.get('global_risks', [])) if git_handoff.get('global_risks') else 'none'}`")
        lines.append(f"- recommended_sequence: `{', '.join(git_handoff.get('recommended_sequence', []))}`")
        lines.append(f"- next_action: {git_handoff.get('next_action', '')}")
    else:
        lines.append("- disabled")
    lines.extend(["", "## Evidence Manifest", ""])
    manifest = health.get("evidence_manifest", {})
    if manifest.get("enabled"):
        lines.append(f"- ok: `{manifest.get('ok')}`")
        lines.append(f"- evidence_count: `{manifest.get('evidence_count')}`")
        lines.append(f"- missing_count: `{manifest.get('missing_count')}`")
        lines.append(f"- stale_count: `{manifest.get('stale_count')}`")
        lines.append(f"- critical_stale_count: `{manifest.get('critical_stale_count')}`")
        lines.append(f"- archival_stale_count: `{manifest.get('archival_stale_count')}`")
        lines.append(f"- unknown_freshness_count: `{manifest.get('unknown_freshness_count')}`")
        lines.append(f"- freshness_status: `{manifest.get('freshness_status', '')}`")
        lines.append(f"- stale_refresh_recommended: `{manifest.get('stale_refresh_recommended', '')}`")
        for key, value in manifest.get("outputs", {}).items():
            lines.append(f"- {key}: `{value}`")
        if manifest.get("stale_refresh_recommended"):
            lines.extend(["", "### Evidence Refresh Commands", ""])
            for command in manifest.get("refresh_commands", evidence_refresh_commands(resume["task_id"])):
                lines.append(f"- `{command}`")
    else:
        lines.append("- disabled")
    lines.extend(["", "## Evidence", ""])
    for key in [
        "files_changed",
        "commands_run",
        "evidence_paths",
        "status_export_path",
        "resume_bundle_path",
        "task_health_path",
        "git_handoff_path",
        "evidence_manifest_path",
        "review_package_path",
        "blocker_packet_path",
    ]:
        values = evidence.get(key, [])
        if isinstance(values, str):
            values = [values] if values else []
        if values:
            lines.append(f"### {key}")
            for value in values:
                lines.append(f"- `{value}`")
        else:
            lines.append(f"- {key}: none")
    lines.extend(["", "## Operating Limits", ""])
    for value in limits.get("current_gate", []):
        lines.append(f"- {value}")
    lines.extend(["", "## Resume Commands", ""])
    for command in resume.get("resume_commands", []):
        lines.append(f"- `{command}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rel(path)


def export_status(args: argparse.Namespace) -> dict[str, Any]:
    bundle = build_bundle(args)
    outputs: dict[str, str] = {}
    if args.output:
        output = project_path(args.output)
    else:
        output = DEFAULT_OUTPUT_ROOT / f"{args.task_id}.status.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs["json"] = rel(output)
    if args.markdown_output:
        outputs["markdown"] = write_markdown(project_path(args.markdown_output), bundle)
    if args.resume_output or args.resume_markdown_output:
        resume = build_resume_bundle(bundle)
        if args.resume_output:
            resume_output = project_path(args.resume_output)
        else:
            resume_output = DEFAULT_OUTPUT_ROOT / f"{args.task_id}.resume.json"
        resume_output.parent.mkdir(parents=True, exist_ok=True)
        resume_output.write_text(json.dumps(resume, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        outputs["resume_json"] = rel(resume_output)
        if args.resume_markdown_output:
            outputs["resume_markdown"] = write_resume_markdown(project_path(args.resume_markdown_output), resume)
    if getattr(args, "include_evidence_manifest", True):
        # The manifest must be generated after this exporter writes the current
        # status/resume files; otherwise it can mark the files about to be
        # refreshed as stale and embed that stale summary into the resume bundle.
        bundle["evidence_manifest"] = evidence_manifest_summary(args)
        output.write_text(json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.markdown_output:
            outputs["markdown"] = write_markdown(project_path(args.markdown_output), bundle)
        if args.resume_output or args.resume_markdown_output:
            resume = build_resume_bundle(bundle)
            if args.resume_output:
                resume_output = project_path(args.resume_output)
            else:
                resume_output = DEFAULT_OUTPUT_ROOT / f"{args.task_id}.resume.json"
            resume_output.parent.mkdir(parents=True, exist_ok=True)
            resume_output.write_text(json.dumps(resume, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            outputs["resume_json"] = rel(resume_output)
            if args.resume_markdown_output:
                outputs["resume_markdown"] = write_resume_markdown(project_path(args.resume_markdown_output), resume)
    return {"ok": True, "task_id": args.task_id, "outputs": outputs, "bundle": bundle if args.include_bundle else {}}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=runtime.DEFAULT_DB)
    parser.add_argument("--events", type=Path, default=runtime.DEFAULT_EVENTS)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--resume-output", type=Path)
    parser.add_argument("--resume-markdown-output", type=Path)
    parser.add_argument("--include-bundle", action="store_true")
    parser.add_argument("--include-terminal-reviews", action="store_true")
    parser.add_argument("--include-superseded-reviews", action="store_true")
    parser.add_argument("--include-context-quality", action="store_true", default=True)
    parser.add_argument("--context-output", type=Path)
    parser.add_argument("--event-limit", type=int, default=8)
    parser.add_argument("--warn-chars", type=int, default=14000)
    parser.add_argument("--fail-chars", type=int, default=22000)
    parser.add_argument("--include-preflight-summary", action="store_true", default=True)
    parser.add_argument("--include-runtime-audit", action="store_true", default=True)
    parser.add_argument("--include-task-health", action="store_true", default=True)
    parser.add_argument("--include-git-handoff", action="store_true", default=True)
    parser.add_argument("--include-evidence-manifest", action="store_true", default=True)
    parser.add_argument("--evidence-manifest-output", type=Path)
    parser.add_argument("--evidence-manifest-markdown-output", type=Path)
    parser.add_argument("--stale-minutes", type=int, default=task_health.DEFAULT_STALE_MINUTES)
    parser.add_argument("--staged-file-warning-threshold", type=int, default=preflight.STAGED_BROAD_THRESHOLD)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = export_status(args)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status_export ok task_id={result['task_id']} json={result['outputs']['json']}")
        if "markdown" in result["outputs"]:
            print(f"markdown={result['outputs']['markdown']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
