#!/usr/bin/env python3
"""Build a compact human review package for one CoAgent task."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results" / "coagent_status"
DEFAULT_TASK_ID = "COAGENT-IMPL-LONGRUN-20260531"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.review_queue import review_queue
from CoAgent.runtime import mosim_agent_runtime as runtime
from CoAgent.task_health import task_health
from CoAgent.evidence.refresh_commands import standard_refresh_commands
from CoAgent.hooks import preflight


def blocker_packet_command(task_id: str, *, record_metadata: bool = False) -> str:
    command = (
        f"python3 CoAgent/blocker_packet/blocker_packet.py --task-id {task_id} "
        f"--output Results/agent_packets/blockers/{task_id}.blocker.json "
        f"--markdown-output Results/agent_packets/blockers/{task_id}.blocker.md --json"
    )
    if record_metadata:
        command += " --record-metadata --claim-token <claim-token>"
    return command


def evidence_refresh_commands(task_id: str) -> list[str]:
    return standard_refresh_commands(task_id)


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def project_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def read_json_file(path: str) -> dict[str, Any]:
    if not path:
        return {"exists": False}
    resolved = project_path(Path(path))
    if not resolved.exists():
        return {"exists": False, "path": str(path).replace("\\", "/")}
    try:
        data = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"exists": True, "path": rel(resolved), "error": str(exc)}
    return {"exists": True, "path": rel(resolved), "data": data}


def compact_file(path: str, *, max_items: int = 20) -> dict[str, Any]:
    payload = read_json_file(path)
    data = payload.get("data")
    if not isinstance(data, dict):
        return payload
    compact: dict[str, Any] = {"exists": True, "path": payload.get("path", str(path))}
    for key in [
        "schema_type",
        "task_id",
        "ok",
        "overallStatus",
        "state",
        "checkpoint",
        "next_action",
        "review",
        "counts",
        "totals",
        "evidence_count",
        "missing_count",
        "stale_count",
        "critical_stale_count",
        "archival_stale_count",
        "unknown_freshness_count",
        "freshness_status",
        "stale_refresh_recommended",
        "refresh_commands",
        "by_kind",
    ]:
        if key in data:
            compact[key] = data[key]
    if "checks" in data and isinstance(data["checks"], dict):
        compact["doctor_issues"] = [
            {"id": item.get("id"), "status": item.get("status"), "summary": item.get("summary")}
            for item in data["checks"].values()
            if isinstance(item, dict) and item.get("status") in {"warning", "fail"}
        ][:max_items]
        compact["doctor_count"] = len(data["checks"])
    if "tasks" in data and isinstance(data["tasks"], list):
        compact["tasks"] = data["tasks"][:max_items]
    if "items" in data and isinstance(data["items"], list):
        compact["items"] = data["items"][:max_items]
    if "missing" in data and isinstance(data["missing"], list):
        compact["missing"] = data["missing"][:max_items]
    return compact


def task_metadata_paths(metadata: dict[str, Any]) -> dict[str, str]:
    keys = [
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
        "doctor_quick_path",
        "doctor_full_path",
        "review_closeout_path",
        "notification_packet_path",
        "blocker_packet_path",
        "blocker_packet_markdown",
    ]
    return {key: str(metadata.get(key) or "") for key in keys if metadata.get(key)}


def review_queue_summary(args: argparse.Namespace) -> dict[str, Any]:
    queue = review_queue.build_queue(
        argparse.Namespace(
            db=args.db,
            include_terminal=args.include_terminal_reviews,
            include_superseded=args.include_superseded_reviews,
            json=True,
        )
    )
    return {
        "count": queue.get("count", 0),
        "suppressed_count": queue.get("suppressed_count", 0),
        "items": queue.get("items", [])[:20],
    }


def task_health_review_summary(args: argparse.Namespace) -> dict[str, Any]:
    snapshot = task_health.build_snapshot(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            task_id=args.task_id,
            state="",
            active_only=True,
            stale_minutes=task_health.DEFAULT_STALE_MINUTES,
            staged_file_warning_threshold=getattr(args, "staged_file_warning_threshold", preflight.STAGED_BROAD_THRESHOLD),
            skip_preflight=False,
            skip_runtime_audit=False,
        )
    )
    return {
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
        "warning_count": snapshot.get("warning_count"),
        "fail_count": snapshot.get("fail_count"),
        "tasks": [
            {
                "task_id": item.get("task_id", ""),
                "runtime_state": item.get("runtime_state", ""),
                "health_state": item.get("health_state", ""),
                "decision": item.get("decision", {}),
                "next_action": item.get("next_action", ""),
                "findings": item.get("findings", []),
            }
            for item in snapshot.get("tasks", [])[:10]
        ],
    }


def closeout_verification_summary(args: argparse.Namespace) -> dict[str, Any]:
    verification = review_queue.verify_closeout(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            task_id=args.task_id,
            include_superseded=args.include_superseded_reviews,
            stale_minutes=task_health.DEFAULT_STALE_MINUTES,
            skip_preflight=False,
            staged_file_warning_threshold=getattr(args, "staged_file_warning_threshold", preflight.STAGED_BROAD_THRESHOLD),
            output=None,
            markdown_output=None,
            json=True,
        )
    )
    return {
        "ok": verification.get("ok"),
        "closeout_required": verification.get("closeout_required"),
        "decision": verification.get("decision", ""),
        "review_status": verification.get("review_status", ""),
        "human_needed": verification.get("human_needed", ""),
        "artifact": verification.get("artifact", {}),
        "effect": verification.get("effect", {}),
        "findings": verification.get("findings", [])[:20],
        "closeout_command": verification.get("closeout_command", ""),
    }


def build_package(args: argparse.Namespace) -> dict[str, Any]:
    task = runtime.show_task(argparse.Namespace(db=args.db, events=args.events, task_id=args.task_id))
    metadata = task.get("metadata", {})
    paths = task_metadata_paths(metadata)
    artifacts: dict[str, Any] = {}
    for key, path in paths.items():
        if path.endswith(".json"):
            artifacts[key] = compact_file(path)
        else:
            exists = project_path(Path(path)).exists()
            artifacts[key] = {"exists": exists, "path": path}
    queue = review_queue_summary(args)
    health = task_health_review_summary(args)
    closeout_verification = closeout_verification_summary(args)
    audit = runtime.audit_event_stream(argparse.Namespace(db=args.db, events=args.events))
    health_decision = health.get("decision", {})
    evidence_artifact = artifacts.get("evidence_manifest_path", {})
    evidence_stale_count = int(evidence_artifact.get("stale_count", 0) or 0) if isinstance(evidence_artifact, dict) else 0
    critical_stale_count = int(evidence_artifact.get("critical_stale_count", 0) or 0) if isinstance(evidence_artifact, dict) else 0
    archival_stale_count = int(evidence_artifact.get("archival_stale_count", 0) or 0) if isinstance(evidence_artifact, dict) else 0
    evidence_refresh_recommended = bool(
        isinstance(evidence_artifact, dict)
        and (evidence_artifact.get("stale_refresh_recommended") or critical_stale_count > 0)
    )
    human_required = (
        bool(queue["count"])
        or metadata.get("human_needed") == "yes"
        or bool(health_decision.get("human_task_ids"))
        or closeout_verification.get("ok") is False
    )
    explicit_review = metadata.get("review_status", "")
    if explicit_review in {"needs_review", "manual_review_required", "rejected", "needs_rework"}:
        human_required = True
    return {
        "schema_type": "coagent_human_review_package",
        "schema_version": 1,
        "task_id": args.task_id,
        "ok": audit.get("ok") is True,
        "human_required": human_required,
        "task": {
            "state": task.get("state", ""),
            "owner": task.get("owner", ""),
            "role": task.get("role", ""),
            "objective": task.get("objective", ""),
            "updated_at": task.get("updated_at", ""),
            "last_event_at": task.get("last_event_at", ""),
            "event_count": len(task.get("events", [])),
        },
        "checkpoint": metadata.get("checkpoint", ""),
        "next_action": metadata.get("next_action", ""),
        "review_status": metadata.get("review_status", ""),
        "human_needed": metadata.get("human_needed", ""),
        "blocker_packet_needed": health_decision.get("continue_allowed") is False,
        "blocker_packet_command": blocker_packet_command(args.task_id),
        "blocker_packet_record_command": blocker_packet_command(args.task_id, record_metadata=True),
        "evidence_refresh": {
            "recommended": evidence_refresh_recommended,
            "stale_count": evidence_stale_count,
            "critical_stale_count": critical_stale_count,
            "archival_stale_count": archival_stale_count,
            "commands": evidence_artifact.get("refresh_commands") or evidence_refresh_commands(args.task_id)
            if evidence_refresh_recommended
            else [],
        },
        "artifacts": artifacts,
        "review_queue": queue,
        "task_health": health,
        "closeout_verification": closeout_verification,
        "runtime_audit": {
            "ok": audit.get("ok"),
            "task_count": audit.get("task_count"),
            "db_event_count": audit.get("db_event_count"),
            "jsonl_event_count": audit.get("jsonl_event_count"),
            "warning_count": audit.get("warning_count"),
            "fail_count": audit.get("fail_count"),
            "sensitive_db_event_count": audit.get("sensitive_db_event_count"),
            "sensitive_jsonl_event_count": audit.get("sensitive_jsonl_event_count"),
            "findings": audit.get("findings", [])[:20],
        },
        "review_questions": review_questions(metadata, queue),
        "resume_commands": [
            f"python3 CoAgent/status_export/status_export.py --task-id {args.task_id} --output Results/coagent_status/{args.task_id}.status.json --markdown-output Results/coagent_status/{args.task_id}.status.md --resume-output Results/coagent_status/{args.task_id}.resume.json --resume-markdown-output Results/coagent_status/{args.task_id}.resume.md --json",
            f"python3 CoAgent/review_package/review_package.py --task-id {args.task_id} --output Results/coagent_status/{args.task_id}.review_package.json --markdown-output Results/coagent_status/{args.task_id}.review_package.md --json",
            blocker_packet_command(args.task_id),
            *(
                evidence_artifact.get("refresh_commands") or evidence_refresh_commands(args.task_id)
                if evidence_refresh_recommended
                else []
            ),
            "python3 CoAgent/doctor/coagent_doctor.py --mode full --json --output Results/coagent_doctor/latest_gateway_full.json",
            "python3 CoAgent/runtime/mosim_agent_runtime.py audit-events",
        ],
    }


def review_questions(metadata: dict[str, Any], queue: dict[str, Any]) -> list[dict[str, str]]:
    questions: list[dict[str, str]] = []
    if queue.get("count", 0):
        questions.append(
            {
                "id": "review_queue_items",
                "question": "请逐项处理 review_queue 中的人工审核项，并给出 accepted / accepted_with_concerns / needs_rework / rejected。",
            }
        )
    if metadata.get("human_needed") == "yes":
        questions.append(
            {
                "id": "human_needed",
                "question": str(metadata.get("next_action") or "请确认该任务需要的人工作业是否已经完成。"),
            }
        )
    if metadata.get("review_status") in {"", "not_required", "accepted"} and not questions:
        questions.append(
            {
                "id": "progress_review",
                "question": "当前没有阻塞性人工审核项。请审核审查包中的 checkpoint、evidence、doctor/task_health/git_handoff 状态是否可以继续推进。",
            }
        )
    return questions


def write_markdown(path: Path, package: dict[str, Any]) -> str:
    health = package.get("task_health", {})
    health_decision = health.get("decision", {}) if isinstance(health, dict) else {}
    closeout_verification = package.get("closeout_verification", {})
    closeout_effect = closeout_verification.get("effect", {}) if isinstance(closeout_verification, dict) else {}
    evidence_refresh = package.get("evidence_refresh", {})
    lines = [
        "# CoAgent Human Review Package",
        "",
        f"- task_id: `{package['task_id']}`",
        f"- ok: `{package['ok']}`",
        f"- human_required: `{package['human_required']}`",
        f"- state: `{package['task']['state']}`",
        f"- owner: `{package['task']['owner']}`",
        f"- role: `{package['task']['role']}`",
        f"- updated_at: `{package['task']['updated_at']}`",
        f"- runtime_audit: `{package['runtime_audit']['ok']}` db={package['runtime_audit']['db_event_count']} jsonl={package['runtime_audit']['jsonl_event_count']} warning={package['runtime_audit']['warning_count']} fail={package['runtime_audit']['fail_count']}",
        f"- task_continue_allowed: `{health_decision.get('continue_allowed', '')}`",
        f"- task_recommended_action: `{health_decision.get('recommended_action', '')}`",
        f"- task_blocking_ids: `{', '.join(health_decision.get('blocking_task_ids', [])) if health_decision.get('blocking_task_ids') else 'none'}`",
        f"- review_queue_count: `{package['review_queue']['count']}`",
        f"- review_status: `{package['review_status']}`",
        f"- human_needed: `{package['human_needed']}`",
        f"- blocker_packet_needed: `{package['blocker_packet_needed']}`",
        f"- evidence_refresh_recommended: `{evidence_refresh.get('recommended', '')}`",
        f"- evidence_stale_count: `{evidence_refresh.get('stale_count', '')}`",
        f"- evidence_critical_stale_count: `{evidence_refresh.get('critical_stale_count', '')}`",
        f"- evidence_archival_stale_count: `{evidence_refresh.get('archival_stale_count', '')}`",
        f"- closeout_verification_ok: `{closeout_verification.get('ok', '')}`",
        "",
        "## Objective",
        "",
        package["task"]["objective"],
        "",
        "## Checkpoint",
        "",
        str(package.get("checkpoint", "")),
        "",
        "## Next Action",
        "",
        str(package.get("next_action", "")),
        "",
        "## Blocker Packet",
        "",
        f"- needed: `{package['blocker_packet_needed']}`",
        f"- generate: `{package['blocker_packet_command']}`",
        f"- generate_and_record: `{package['blocker_packet_record_command']}`",
        "",
        "## Review Questions",
        "",
    ]
    for item in package.get("review_questions", []):
        lines.append(f"- `{item['id']}`: {item['question']}")
    lines.extend(["", "## Artifacts", ""])
    for key, artifact in package.get("artifacts", {}).items():
        lines.append(f"- `{key}`: exists={artifact.get('exists')} path=`{artifact.get('path', '')}`")
        if "overallStatus" in artifact:
            counts = artifact.get("counts", {})
            lines.append(
                f"  doctor: `{artifact.get('overallStatus')}` ok={counts.get('ok', '')} warning={counts.get('warning', '')} fail={counts.get('fail', '')}"
            )
        if "evidence_count" in artifact:
            lines.append(
                f"  evidence: count={artifact.get('evidence_count')} missing={artifact.get('missing_count')} "
                f"stale={artifact.get('stale_count', '')} critical={artifact.get('critical_stale_count', '')} "
                f"archival={artifact.get('archival_stale_count', '')} kinds={artifact.get('by_kind', {})}"
            )
        if "totals" in artifact:
            totals = artifact.get("totals", {})
            lines.append(
                f"  git: batches={totals.get('batch_count', '')} staged={totals.get('staged_file_count', '')} overlap={totals.get('staged_unstaged_overlap_count', '')}"
            )
    lines.extend(["", "## Task Health", ""])
    if isinstance(health, dict):
        lines.append(f"- ok: `{health.get('ok')}`")
        lines.append(f"- continue_allowed: `{health_decision.get('continue_allowed', '')}`")
        lines.append(f"- recommended_action: `{health_decision.get('recommended_action', '')}`")
        lines.append(f"- next_intervention: {health_decision.get('next_intervention', '')}")
        for item in health.get("tasks", []):
            item_decision = item.get("decision", {})
            lines.append(
                f"- `{item.get('task_id', '')}` health={item.get('health_state', '')} "
                f"continue={item_decision.get('continue_allowed', '')} action={item_decision.get('recommended_action', '')}"
            )
            if item_decision.get("stop_reason"):
                lines.append(f"  stop_reason: `{item_decision.get('stop_reason')}`")
            for finding in item.get("findings", []):
                lines.append(f"  finding: `{finding.get('severity', '')}` `{finding.get('reason', '')}` -> {finding.get('next_action', '')}")
    else:
        lines.append("- disabled")
    lines.extend(["", "## Evidence Freshness", ""])
    lines.append(f"- refresh_recommended: `{evidence_refresh.get('recommended', False)}`")
    lines.append(f"- stale_count: `{evidence_refresh.get('stale_count', 0)}`")
    lines.append(f"- critical_stale_count: `{evidence_refresh.get('critical_stale_count', 0)}`")
    lines.append(f"- archival_stale_count: `{evidence_refresh.get('archival_stale_count', 0)}`")
    if evidence_refresh.get("recommended"):
        for command in evidence_refresh.get("commands", []):
            lines.append(f"- `{command}`")
    else:
        lines.append("- refresh_commands: none")
    lines.extend(["", "## Review Closeout Verification", ""])
    if isinstance(closeout_verification, dict):
        artifact = closeout_verification.get("artifact", {})
        lines.append(f"- ok: `{closeout_verification.get('ok')}`")
        lines.append(f"- closeout_required: `{closeout_verification.get('closeout_required')}`")
        lines.append(f"- decision: `{closeout_verification.get('decision', '')}`")
        lines.append(f"- artifact_exists: `{artifact.get('exists', '')}`")
        lines.append(f"- artifact_valid: `{artifact.get('valid', '')}`")
        lines.append(f"- artifact_path: `{artifact.get('path', '')}`")
        lines.append(f"- review_unblocked: `{closeout_effect.get('review_unblocked', '')}`")
        lines.append(f"- runtime_continuation: `{closeout_effect.get('runtime_continuation', '')}`")
        lines.append(f"- closeout_command: `{closeout_verification.get('closeout_command', '')}`")
        findings = closeout_verification.get("findings", [])
        if findings:
            for item in findings:
                lines.append(f"  finding: `{item.get('severity', '')}` `{item.get('reason', '')}` -> {item.get('next_action', '')}")
        else:
            lines.append("- findings: none")
    else:
        lines.append("- disabled")
    lines.extend(["", "## Review Queue", ""])
    if package["review_queue"]["items"]:
        for item in package["review_queue"]["items"]:
            lines.append(f"- `{item['task_id']}` state={item['state']} review={item['review_status']} next={item['next_action']}")
            for reason in item.get("reasons", []):
                lines.append(f"  reason: `{reason}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Runtime Audit Findings", ""])
    findings = package["runtime_audit"].get("findings", [])
    if findings:
        for item in findings:
            lines.append(f"- `{item.get('severity', '')}` `{item.get('reason', '')}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Resume Commands", ""])
    for command in package.get("resume_commands", []):
        lines.append(f"- `{command}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rel(path)


def run_package(args: argparse.Namespace) -> dict[str, Any]:
    package = build_package(args)
    outputs: dict[str, str] = {}
    output = project_path(args.output or (DEFAULT_OUTPUT_ROOT / f"{args.task_id}.review_package.json"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(package, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs["json"] = rel(output)
    if args.markdown_output:
        outputs["markdown"] = write_markdown(project_path(args.markdown_output), package)
    return {"ok": package["ok"], "outputs": outputs, "package": package if args.include_package else {}}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=runtime.DEFAULT_DB)
    parser.add_argument("--events", type=Path, default=runtime.DEFAULT_EVENTS)
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--include-terminal-reviews", action="store_true")
    parser.add_argument("--include-superseded-reviews", action="store_true")
    parser.add_argument("--staged-file-warning-threshold", type=int, default=preflight.STAGED_BROAD_THRESHOLD)
    parser.add_argument("--include-package", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_package(args)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"review_package ok={result['ok']} json={result['outputs']['json']}")
        if "markdown" in result["outputs"]:
            print(f"markdown={result['outputs']['markdown']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
