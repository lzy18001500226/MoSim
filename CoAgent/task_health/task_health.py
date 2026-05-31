#!/usr/bin/env python3
"""Read-only long-task health snapshot for CoAgent runtime tasks."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results" / "coagent_status"
DEFAULT_STALE_MINUTES = 120

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.hooks import preflight
from CoAgent.review_queue import review_queue
from CoAgent.runtime import mosim_agent_runtime as runtime


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
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def age_minutes(value: str, now: datetime) -> float | None:
    parsed = parse_time(value)
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return max(0.0, (now - parsed.astimezone(now.tzinfo)).total_seconds() / 60.0)


def severity_rank(state: str) -> int:
    ranks = {
        "block_for_safety": 10,
        "block_for_user": 20,
        "reject_completion": 30,
        "pause_for_context": 40,
        "pause_for_review": 50,
        "shrink_topology": 60,
        "continue_with_watch": 70,
        "close_ready": 80,
        "continue": 90,
    }
    return ranks.get(state, 100)


def state_from_findings(findings: list[dict[str, Any]], task: dict[str, Any]) -> str:
    reasons = {str(item.get("reason", "")) for item in findings}
    if any(str(item.get("severity")) == "fail" for item in findings):
        return "block_for_safety"
    if "human_needed" in reasons or "auth_required" in reasons:
        return "block_for_user"
    if "review_decision_blocks_progress" in reasons:
        return "reject_completion"
    if "review_required" in reasons or "runtime_event_audit_warning" in reasons:
        return "pause_for_review"
    if any(
        reason in reasons
        for reason in [
            "missing_review_closeout_artifact",
            "invalid_review_closeout_artifact",
            "review_closeout_decision_mismatch",
        ]
    ):
        return "pause_for_review"
    if (
        "stale_active_task" in reasons
        or "missing_recent_checkpoint" in reasons
        or "broad_git_surface" in reasons
        or "accepted_with_concerns_watch" in reasons
    ):
        return "continue_with_watch"
    if task["state"] in runtime.TERMINAL_STATES:
        return "close_ready"
    return "continue"


def decision_for_task(health_state: str, findings: list[dict[str, Any]], task: dict[str, Any]) -> dict[str, Any]:
    reasons = [str(item.get("reason", "")) for item in findings]
    stop_priority = [
        "runtime_event_audit_failed",
        "git_index_lock_present",
        "staged_runtime_outputs",
        "staged_external_references",
        "human_needed",
        "auth_required",
        "review_decision_blocks_progress",
        "completion_review_conflict",
        "missing_review_closeout_artifact",
        "invalid_review_closeout_artifact",
        "review_closeout_decision_mismatch",
        "review_required",
        "runtime_event_audit_warning",
    ]
    stop_finding = next((item for reason in stop_priority for item in findings if item.get("reason") == reason), None)
    if stop_finding is None:
        stop_finding = next((item for item in findings if item.get("severity") == "fail"), None)
    watch_findings = [
        item
        for item in findings
        if item.get("reason") in {"stale_active_task", "missing_recent_checkpoint", "broad_git_surface", "accepted_with_concerns_watch"}
    ]
    if health_state == "block_for_safety":
        recommended_action = "stop_and_repair_safety"
    elif health_state == "block_for_user":
        recommended_action = "ask_user_once"
    elif health_state == "pause_for_review":
        recommended_action = "route_review_or_closeout"
    elif health_state == "reject_completion":
        recommended_action = "rework_or_reject_completion"
    elif health_state == "close_ready":
        recommended_action = "close_task"
    elif health_state == "continue_with_watch":
        recommended_action = "continue_with_watch"
    else:
        recommended_action = "continue"
    continue_allowed = health_state in {"continue", "continue_with_watch"}
    return {
        "continue_allowed": continue_allowed,
        "recommended_action": recommended_action,
        "stop_reason": "" if continue_allowed else (str(stop_finding.get("reason", "")) if stop_finding else health_state),
        "required_human_action": bool(health_state == "block_for_user" or any(reason in {"human_needed", "auth_required"} for reason in reasons)),
        "required_review_action": bool(
            health_state in {"pause_for_review", "reject_completion"}
            or any(
                reason
                in {
                    "review_required",
                    "missing_review_closeout_artifact",
                    "invalid_review_closeout_artifact",
                    "review_closeout_decision_mismatch",
                    "review_decision_blocks_progress",
                    "completion_review_conflict",
                }
                for reason in reasons
            )
        ),
        "required_safety_action": health_state == "block_for_safety",
        "next_intervention": "" if stop_finding is None else str(stop_finding.get("next_action", "")),
        "watch_reasons": [str(item.get("reason", "")) for item in watch_findings],
        "owner": task.get("owner", ""),
    }


def finding(severity: str, reason: str, evidence: str, next_action: str, **extra: Any) -> dict[str, Any]:
    data = {
        "severity": severity,
        "reason": reason,
        "evidence": evidence,
        "next_action": next_action,
    }
    data.update(extra)
    return data


def load_runtime_task(args: argparse.Namespace, task_id: str) -> dict[str, Any]:
    return runtime.show_task(argparse.Namespace(db=args.db, events=args.events, task_id=task_id))


def selected_tasks(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.task_id:
        return [load_runtime_task(args, args.task_id)]
    listing = runtime.list_tasks(argparse.Namespace(db=args.db, events=args.events, state=args.state or ""))
    tasks = listing["tasks"]
    if args.active_only:
        tasks = [task for task in tasks if task["state"] not in runtime.TERMINAL_STATES]
    return tasks


def preflight_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    if args.skip_preflight:
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
    return {
        "enabled": True,
        "ok": bool(data.get("ok")),
        "git_workspace_state": {
            "ok": bool(git_state.get("ok")),
            "index_lock_present": bool(git_state.get("index_lock_present")),
            "staged_count": git_state.get("staged_count"),
            "staged_limit": git_state.get("staged_limit"),
            "staged_runtime_count": git_state.get("staged_runtime_count"),
            "staged_external_count": git_state.get("staged_external_count"),
            "findings": git_state.get("findings", []),
        },
    }


def audit_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    if args.skip_runtime_audit:
        return {"enabled": False}
    audit = runtime.audit_event_stream(argparse.Namespace(db=args.db, events=args.events))
    return {
        "enabled": True,
        "ok": bool(audit.get("ok")),
        "warning_count": audit.get("warning_count", 0),
        "fail_count": audit.get("fail_count", 0),
        "db_event_count": audit.get("db_event_count", 0),
        "jsonl_event_count": audit.get("jsonl_event_count", 0),
        "sensitive_db_event_count": audit.get("sensitive_db_event_count", 0),
        "sensitive_jsonl_event_count": audit.get("sensitive_jsonl_event_count", 0),
        "findings": audit.get("findings", [])[:20],
    }


def queue_items_by_task(args: argparse.Namespace) -> dict[str, dict[str, Any]]:
    queue = review_queue.build_queue(
        argparse.Namespace(
            db=args.db,
            include_terminal=True,
            include_superseded=False,
            json=True,
        )
    )
    return {str(item["task_id"]): item for item in queue.get("items", [])}


def load_closeout(metadata: dict[str, Any]) -> dict[str, Any]:
    path = str(metadata.get("review_closeout_path") or "")
    if not path:
        return {"exists": False, "path": ""}
    resolved = project_path(Path(path))
    if not resolved.exists():
        return {"exists": False, "path": path}
    try:
        data = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"exists": True, "path": rel(resolved), "error": str(exc)}
    if not isinstance(data, dict):
        return {"exists": True, "path": rel(resolved), "error": "closeout JSON is not an object"}
    return {
        "exists": True,
        "path": rel(resolved),
        "decision": data.get("decision", ""),
        "reason": data.get("reason", ""),
        "next_action": data.get("next_action", ""),
        "actor": data.get("actor", ""),
    }


def assess_task(
    task: dict[str, Any],
    *,
    now: datetime,
    args: argparse.Namespace,
    review_items: dict[str, dict[str, Any]],
    preflight_data: dict[str, Any],
    audit_data: dict[str, Any],
) -> dict[str, Any]:
    metadata = task.get("metadata", {})
    task_id = task["task_id"]
    minutes = age_minutes(task.get("last_event_at", ""), now)
    findings: list[dict[str, Any]] = []
    if minutes is None:
        findings.append(
            finding(
                "warning",
                "unknown_last_event_age",
                "runtime task last_event_at is missing or unparsable",
                "inspect runtime task row before resuming",
            )
        )
    elif task["state"] not in runtime.TERMINAL_STATES and minutes > args.stale_minutes:
        findings.append(
            finding(
                "warning",
                "stale_active_task",
                f"last_event_at={task.get('last_event_at', '')}",
                "write a checkpoint, rescope, or create a blocker packet before continuing",
                age_minutes=round(minutes, 2),
                stale_minutes=args.stale_minutes,
            )
        )
    review_item = review_items.get(task_id)
    if review_item:
        findings.append(
            finding(
                "warning",
                "review_required",
                review_item.get("review_path") or review_item.get("summary_path") or "review queue",
                "route to the review owner or record closeout before claiming completion",
                review_status=review_item.get("review_status", ""),
                reasons=review_item.get("reasons", []),
            )
        )
    if metadata.get("human_needed") == "yes":
        findings.append(
            finding(
                "warning",
                "human_needed",
                metadata.get("notification_packet_path", "") or metadata.get("summary_path", "") or "runtime metadata",
                "make exactly one PMO-facing ask and wait for the user's answer",
            )
        )
    if metadata.get("canonical_status") == "auth_required":
        findings.append(
            finding(
                "warning",
                "auth_required",
                metadata.get("summary_path", "") or "runtime metadata",
                "ask the user to restore the required login/license/auth state, then run the smallest resume check",
            )
        )
    review_status = str(metadata.get("review_status") or "")
    closeout = load_closeout(metadata)
    if review_status in {"accepted", "accepted_with_concerns", "needs_rework", "rejected"}:
        if not closeout.get("exists"):
            findings.append(
                finding(
                    "warning",
                    "missing_review_closeout_artifact",
                    str(metadata.get("review_closeout_path") or "runtime metadata"),
                    "write or recover the review closeout artifact before relying on this decision",
                    review_status=review_status,
                )
            )
        elif closeout.get("error"):
            findings.append(
                finding(
                    "warning",
                    "invalid_review_closeout_artifact",
                    str(closeout.get("path", "")),
                    "repair or regenerate the review closeout artifact",
                    review_status=review_status,
                    error=closeout.get("error", ""),
                )
            )
        elif str(closeout.get("decision") or "") != review_status:
            findings.append(
                finding(
                    "warning",
                    "review_closeout_decision_mismatch",
                    str(closeout.get("path", "")),
                    "inspect runtime metadata and closeout artifact before closing or resuming this task",
                    review_status=review_status,
                    closeout_decision=closeout.get("decision", ""),
                )
            )
    if review_status == "accepted_with_concerns":
        findings.append(
            finding(
                "warning",
                "accepted_with_concerns_watch",
                str(metadata.get("review_closeout_path") or "runtime metadata"),
                "continue only with the concern recorded in the next checkpoint and review package",
            )
        )
    if review_status in {"needs_rework", "rejected"}:
        findings.append(
            finding(
                "warning",
                "review_decision_blocks_progress",
                str(metadata.get("review_closeout_path") or "runtime metadata"),
                "do not continue this implementation path until the review decision is addressed",
                review_status=review_status,
            )
        )
    if audit_data.get("enabled") and not audit_data.get("ok"):
        findings.append(
            finding(
                "fail",
                "runtime_event_audit_failed",
                "runtime audit",
                "stop runtime mutation and repair DB/JSONL event drift first",
                fail_count=audit_data.get("fail_count"),
            )
        )
    elif audit_data.get("enabled") and audit_data.get("warning_count", 0):
        findings.append(
            finding(
                "warning",
                "runtime_event_audit_warning",
                "runtime audit",
                "inspect event drift before relying on status-board recovery",
                warning_count=audit_data.get("warning_count"),
            )
        )
    git_state = preflight_data.get("git_workspace_state", {}) if preflight_data.get("enabled") else {}
    if git_state.get("index_lock_present"):
        findings.append(
            finding(
                "fail",
                "git_index_lock_present",
                ".git/index.lock",
                "stop Git work, verify no active Git owner, then remove stale lock only if safe",
            )
        )
    if git_state.get("staged_runtime_count", 0):
        findings.append(
            finding(
                "fail",
                "staged_runtime_outputs",
                "preflight git workspace state",
                "unstage ignored runtime outputs before commit",
                count=git_state.get("staged_runtime_count"),
            )
        )
    if git_state.get("staged_external_count", 0):
        findings.append(
            finding(
                "fail",
                "staged_external_references",
                "preflight git workspace state",
                "do not commit broad external reference trees; split or ignore first",
                count=git_state.get("staged_external_count"),
            )
        )
    staged_count = git_state.get("staged_count")
    staged_limit = git_state.get("staged_limit")
    if isinstance(staged_count, int) and isinstance(staged_limit, int) and staged_count > staged_limit:
        findings.append(
            finding(
                "warning",
                "broad_git_surface",
                "preflight git workspace state",
                "route Git integration through split plan or DevOps handoff",
                staged_count=staged_count,
                staged_limit=staged_limit,
            )
        )
    if task["state"] == "done" and metadata.get("review_status") in {"needs_review", "rejected"}:
        findings.append(
            finding(
                "warning",
                "completion_review_conflict",
                "runtime metadata",
                "reject completion or record accepted closeout before marking this slice closed",
            )
        )
    state = state_from_findings(findings, task)
    decision = decision_for_task(state, findings, task)
    return {
        "task_id": task_id,
        "runtime_state": task["state"],
        "health_state": state,
        "decision": decision,
        "severity_rank": severity_rank(state),
        "owner": task["owner"],
        "role": task["role"],
        "last_event_at": task["last_event_at"],
        "last_event_age_minutes": None if minutes is None else round(minutes, 2),
        "checkpoint": metadata.get("checkpoint", ""),
        "next_action": metadata.get("next_action", ""),
        "review_status": metadata.get("review_status", ""),
        "human_needed": metadata.get("human_needed", ""),
        "review_closeout": closeout,
        "critical_path_owner": metadata.get("critical_path_owner", metadata.get("department", task["role"])),
        "findings": sorted(findings, key=lambda item: (0 if item["severity"] == "fail" else 1, item["reason"])),
    }


def build_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    now = datetime.now(timezone.utc).astimezone()
    tasks = selected_tasks(args)
    review_items = queue_items_by_task(args)
    preflight_data = preflight_snapshot(args)
    audit_data = audit_snapshot(args)
    task_health = [
        assess_task(
            task,
            now=now,
            args=args,
            review_items=review_items,
            preflight_data=preflight_data,
            audit_data=audit_data,
        )
        for task in tasks
    ]
    task_health.sort(key=lambda item: (item["severity_rank"], item["task_id"]))
    fail_count = sum(1 for item in task_health for finding_item in item["findings"] if finding_item["severity"] == "fail")
    warning_count = sum(1 for item in task_health for finding_item in item["findings"] if finding_item["severity"] == "warning")
    blocking_tasks = [item for item in task_health if not item.get("decision", {}).get("continue_allowed", False)]
    human_tasks = [item for item in task_health if item.get("decision", {}).get("required_human_action")]
    review_tasks = [item for item in task_health if item.get("decision", {}).get("required_review_action")]
    safety_tasks = [item for item in task_health if item.get("decision", {}).get("required_safety_action")]
    watch_tasks = [item for item in task_health if item.get("health_state") == "continue_with_watch"]
    continue_allowed = len(blocking_tasks) == 0
    if blocking_tasks:
        recommended_action = blocking_tasks[0]["decision"].get("recommended_action", "continue")
        stop_reason = blocking_tasks[0]["decision"].get("stop_reason", "")
        next_intervention = blocking_tasks[0]["decision"].get("next_intervention", "")
    elif watch_tasks:
        recommended_action = "continue_with_watch"
        stop_reason = ""
        next_intervention = ""
    else:
        recommended_action = "continue"
        stop_reason = ""
        next_intervention = ""
    return {
        "schema_type": "coagent_task_health_snapshot",
        "schema_version": 1,
        "generated_at": now.isoformat(timespec="seconds"),
        "ok": fail_count == 0,
        "continue_allowed": continue_allowed,
        "recommended_action": recommended_action,
        "stop_reason": stop_reason,
        "next_intervention": next_intervention,
        "blocking_task_ids": [item["task_id"] for item in blocking_tasks],
        "watch_task_ids": [item["task_id"] for item in watch_tasks],
        "human_task_ids": [item["task_id"] for item in human_tasks],
        "review_task_ids": [item["task_id"] for item in review_tasks],
        "safety_task_ids": [item["task_id"] for item in safety_tasks],
        "decision": {
            "continue_allowed": continue_allowed,
            "highest_priority_state": task_health[0]["health_state"] if task_health else "continue",
            "blocking_task_ids": [item["task_id"] for item in blocking_tasks],
            "watch_task_ids": [item["task_id"] for item in watch_tasks],
            "human_task_ids": [item["task_id"] for item in human_tasks],
            "review_task_ids": [item["task_id"] for item in review_tasks],
            "safety_task_ids": [item["task_id"] for item in safety_tasks],
            "next_intervention": next_intervention,
            "recommended_action": recommended_action,
            "stop_reason": stop_reason,
        },
        "task_count": len(task_health),
        "fail_count": fail_count,
        "warning_count": warning_count,
        "stale_minutes": args.stale_minutes,
        "preflight": preflight_data,
        "runtime_audit": audit_data,
        "tasks": task_health,
    }


def write_markdown(path: Path, snapshot: dict[str, Any]) -> str:
    decision = snapshot.get("decision", {})
    lines = [
        "# CoAgent Task Health",
        "",
        f"- generated_at: `{snapshot['generated_at']}`",
        f"- ok: `{snapshot['ok']}`",
        f"- continue_allowed: `{decision.get('continue_allowed', '')}`",
        f"- recommended_action: `{decision.get('recommended_action', '')}`",
        f"- highest_priority_state: `{decision.get('highest_priority_state', '')}`",
        f"- blocking_task_ids: `{', '.join(decision.get('blocking_task_ids', [])) or 'none'}`",
        f"- task_count: `{snapshot['task_count']}`",
        f"- fail_count: `{snapshot['fail_count']}`",
        f"- warning_count: `{snapshot['warning_count']}`",
        f"- stale_minutes: `{snapshot['stale_minutes']}`",
        "",
        "## Tasks",
        "",
    ]
    if not snapshot["tasks"]:
        lines.append("- none")
    for task in snapshot["tasks"]:
        task_decision = task.get("decision", {})
        lines.append(
            f"- `{task['task_id']}` state={task['runtime_state']} health={task['health_state']} "
            f"continue={task_decision.get('continue_allowed', '')} action={task_decision.get('recommended_action', '')} "
            f"age_min={task['last_event_age_minutes']} human={task['human_needed']} review={task['review_status']}"
        )
        if task.get("next_action"):
            lines.append(f"  next: {task['next_action']}")
        if task_decision.get("stop_reason"):
            lines.append(f"  stop_reason: `{task_decision.get('stop_reason')}`")
        if task_decision.get("next_intervention"):
            lines.append(f"  intervention: {task_decision.get('next_intervention')}")
        for item in task["findings"]:
            lines.append(f"  finding: `{item['severity']}` `{item['reason']}` -> {item['next_action']}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rel(path)


def run_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    snapshot = build_snapshot(args)
    outputs: dict[str, str] = {}
    if args.output:
        output = project_path(args.output)
    else:
        suffix = args.task_id or "active"
        output = DEFAULT_OUTPUT_ROOT / f"{suffix}.task_health.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs["json"] = rel(output)
    if args.markdown_output:
        outputs["markdown"] = write_markdown(project_path(args.markdown_output), snapshot)
    return {"ok": bool(snapshot["ok"]), "outputs": outputs, "snapshot": snapshot if args.include_snapshot else {}}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=runtime.DEFAULT_DB)
    parser.add_argument("--events", type=Path, default=runtime.DEFAULT_EVENTS)
    parser.add_argument("--task-id", default="")
    parser.add_argument("--state", choices=sorted(runtime.VALID_STATES), default="")
    parser.add_argument("--active-only", action="store_true", default=True)
    parser.add_argument("--include-terminal", dest="active_only", action="store_false")
    parser.add_argument("--stale-minutes", type=int, default=DEFAULT_STALE_MINUTES)
    parser.add_argument("--staged-file-warning-threshold", type=int, default=preflight.STAGED_BROAD_THRESHOLD)
    parser.add_argument("--skip-preflight", action="store_true")
    parser.add_argument("--skip-runtime-audit", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--include-snapshot", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_snapshot(args)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"task_health ok={result['ok']} json={result['outputs']['json']}")
        if "markdown" in result["outputs"]:
            print(f"markdown={result['outputs']['markdown']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
