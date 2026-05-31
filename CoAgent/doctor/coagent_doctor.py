#!/usr/bin/env python3
"""Project-local health report for CoAgent.

The doctor is intentionally read-mostly. It checks whether CoAgent has the
minimum recoverability surface needed before starting or resuming long-running
multi-conversation work.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "Results" / "coagent_doctor" / "latest.json"
MAX_STDOUT = 200000
MAX_STDERR = 20000
CODEX_HOME = Path("/home/linux/.codex")

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.knowledge import knowledge_indexer


@dataclass(frozen=True)
class CheckResult:
    id: str
    status: str
    summary: str
    detail: dict[str, Any]


def timed(check: CheckResult, started_at: float) -> CheckResult:
    detail = dict(check.detail)
    detail["elapsed_seconds"] = round(time.monotonic() - started_at, 3)
    return CheckResult(check.id, check.status, check.summary, detail)


def run_check(func) -> CheckResult:
    started_at = time.monotonic()
    try:
        return timed(func(), started_at)
    except Exception as exc:
        return timed(
            CheckResult(
                id=f"coagent.{getattr(func, '__name__', 'unknown_check')}",
                status="fail",
                summary="doctor check raised an exception",
                detail={"error": str(exc), "check": getattr(func, "__name__", "<unknown>")},
            ),
            started_at,
        )


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def run(command: list[str], timeout: int = 60) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "returncode": None,
            "timeout": True,
            "command": command,
            "stdout": (exc.stdout or "")[-MAX_STDOUT:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-MAX_STDERR:] if isinstance(exc.stderr, str) else "",
        }
    except OSError as exc:
        return {"ok": False, "command": command, "error": str(exc)}
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "command": command,
        "stdout": completed.stdout.strip()[-MAX_STDOUT:],
        "stderr": completed.stderr.strip()[-MAX_STDERR:],
    }


def parse_json_output(result: dict[str, Any]) -> Any:
    text = result.get("stdout", "")
    if not text:
        return None
    start = text.find("{")
    if start < 0:
        start = text.find("[")
    if start < 0:
        return None
    try:
        return json.loads(text[start:])
    except json.JSONDecodeError:
        return None


def check_required_paths() -> CheckResult:
    required = [
        "CoAgent/docs/architecture/ARCHITECTURE.md",
        "CoAgent/docs/architecture/COMPONENT_MAP.md",
        "CoAgent/docs/status/MIGRATION_STATUS.md",
        "CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md",
        "CoAgent/docs/research/LEARNING_STRATEGY.md",
        "CoAgent/runtime/mosim_agent_runtime.py",
        "CoAgent/dispatch/codex_transport.py",
        "CoAgent/dispatch/department_threads.json",
        "CoAgent/context/context_pack.py",
        "CoAgent/context/context_quality.py",
        "CoAgent/bootstrap/task_bootstrap.py",
        "CoAgent/bootstrap/README.md",
        "CoAgent/memory/memory_context.py",
        "CoAgent/memory/memory_policy.json",
        "CoAgent/knowledge/knowledge_indexer.py",
        "CoAgent/learning/learning_indexer.py",
        "CoAgent/hooks/preflight.py",
        "CoAgent/automation/automation_runner.py",
        "CoAgent/automation/guardrails.py",
        "CoAgent/automation/worker_policy.json",
        "CoAgent/transport/adapter.py",
        "CoAgent/transport/codex_exec.py",
        "CoAgent/result_router/result_router.py",
        "CoAgent/review_queue/review_queue.py",
        "CoAgent/status_export/status_export.py",
        "CoAgent/task_health/task_health.py",
        "CoAgent/blocker_packet/blocker_packet.py",
        "CoAgent/devops/git_batch_plan.py",
        "CoAgent/devops/git_handoff_packet.py",
        "CoAgent/devops/git_split_commit_apply.py",
        "CoAgent/devops/git_split_commit_dry_run.py",
        "CoAgent/devops/git_split_index_check.py",
        "CoAgent/evidence/evidence_manifest.py",
        "CoAgent/review_package/review_package.py",
        "CoAgent/doctor/goal_alignment.py",
        "CoAgent/tests/test_lifecycle_smoke.py",
        "CoAgent/tests/test_goal_alignment.py",
        "CoAgent/tests/test_runtime_update_metadata.py",
        "CoAgent/tests/test_task_bootstrap.py",
        "CoAgent/tests/test_task_health.py",
        "CoAgent/tests/test_blocker_packet.py",
        "CoAgent/tests/test_git_batch_plan.py",
        "CoAgent/tests/test_git_handoff_packet.py",
        "CoAgent/tests/test_git_split_commit_apply.py",
        "CoAgent/tests/test_git_split_commit_dry_run.py",
        "CoAgent/tests/test_git_split_index_check.py",
        "CoAgent/tests/test_evidence_refresh_commands.py",
        "CoAgent/tests/test_evidence_manifest.py",
        "CoAgent/tests/test_review_package.py",
        "CoAgent/protocol/task_packet_schema.json",
        "CoAgent/protocol/result_packet_schema.json",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    status = "ok" if not missing else "fail"
    return CheckResult(
        id="coagent.required_paths",
        status=status,
        summary="required CoAgent files are present" if status == "ok" else "required CoAgent files are missing",
        detail={"missing": missing},
    )


def check_department_registry() -> CheckResult:
    path = ROOT / "CoAgent" / "dispatch" / "department_threads.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return CheckResult(
            id="coagent.department_registry",
            status="fail",
            summary="department registry is unreadable",
            detail={"path": rel(path), "error": str(exc)},
        )
    threads = data.get("threads", [])
    departments = sorted(item.get("department", "") for item in threads if item.get("department"))
    required = {
        "MainAgent",
        "DispatchAgent",
        "ProductStrategyAgent",
        "RuntimePlatformAgent",
        "ContextMemoryAgent",
        "ToolchainMCPAgent",
        "KnowledgeSecretaryAgent",
        "VerificationAgent",
        "SafetyComplianceAgent",
        "DevOpsReleaseAgent",
        "ExternalIntelligenceAgent",
    }
    missing = sorted(required.difference(departments))
    status = "ok" if not missing else "warning"
    return CheckResult(
        id="coagent.department_registry",
        status=status,
        summary="department registry contains required departments" if status == "ok" else "department registry is incomplete",
        detail={"thread_count": len(threads), "departments": departments, "missing": missing},
    )


def check_command(check_id: str, summary_ok: str, summary_fail: str, command: list[str], timeout: int = 60) -> CheckResult:
    result = run(command, timeout=timeout)
    status = "ok" if result.get("ok") else "fail"
    return CheckResult(
        id=check_id,
        status=status,
        summary=summary_ok if status == "ok" else summary_fail,
        detail=result,
    )


def check_reference_index() -> CheckResult:
    return check_command(
        "coagent.reference_index",
        "reference index validates",
        "reference index validation failed",
        ["python3", "Scripts/reference/check_reference_index.py", "--strict"],
    )


def check_learning_index() -> CheckResult:
    return check_command(
        "coagent.learning_index",
        "learning audits validate",
        "learning audit validation failed",
        ["python3", "CoAgent/learning/learning_indexer.py", "validate", "--strict"],
    )


def check_learning_coverage() -> CheckResult:
    result = run(["python3", "CoAgent/learning/learning_indexer.py", "coverage", "--strict"])
    payload = parse_json_output(result)
    missing = payload.get("missing_required") if isinstance(payload, dict) else None
    ok = result.get("ok") and isinstance(payload, dict) and payload.get("ok") is True
    return CheckResult(
        id="coagent.learning_coverage",
        status="ok" if ok else "fail",
        summary="required learning source families are covered" if ok else "required learning source families are missing",
        detail={"missing_required": missing, "result": result},
    )


def check_preflight() -> CheckResult:
    return check_command(
        "coagent.preflight",
        "preflight checks pass",
        "preflight checks failed",
        ["python3", "CoAgent/hooks/preflight.py"],
    )


def check_active_queue() -> CheckResult:
    result = run(["python3", "CoAgent/runtime/mosim_agent_runtime.py", "status-board", "--active-only"])
    payload = parse_json_output(result)
    active_count = payload.get("count") if isinstance(payload, dict) else None
    tasks = payload.get("tasks", []) if isinstance(payload, dict) else []
    active_ids = sorted(item.get("task_id", "") for item in tasks if isinstance(item, dict))
    allowed_roots = {
        "COAGENT-IMPL-MINILOOP-01",
        "COAGENT-IMPL-LONGRUN-20260531",
        "COAGENT-IMPL-TRANSPORT-GIT-6H-20260531",
    }
    allowed_active: set[str] = set(allowed_roots)
    unexpected_active: list[str] = []
    for item in tasks:
        if not isinstance(item, dict):
            continue
        task_id = str(item.get("task_id", ""))
        metadata_parent = str(item.get("parent_task_id") or item.get("parent_goal_task_id") or "")
        parent_allowed = metadata_parent in allowed_roots
        id_child_allowed = any(task_id.startswith(f"{root}-") for root in allowed_roots)
        if task_id in allowed_roots or parent_allowed or id_child_allowed:
            allowed_active.add(task_id)
        else:
            unexpected_active.append(task_id)
    unexpected_active = sorted(set(unexpected_active))
    ok = result.get("ok") and (active_count == 0 or not unexpected_active)
    status = "ok" if ok else "warning" if result.get("ok") else "fail"
    if active_count == 0:
        summary = "runtime active queue is empty"
    elif ok:
        summary = "runtime active queue only contains approved implementation task(s)"
    else:
        summary = "runtime active queue needs review"
    detail = {
        "active_count": active_count,
        "active_ids": active_ids,
        "allowed_active": sorted(allowed_active),
        "unexpected_active": unexpected_active,
        "result": result,
    }
    return CheckResult("coagent.active_queue", status, summary, detail)


def check_runtime_event_audit() -> CheckResult:
    result = run(["python3", "CoAgent/runtime/mosim_agent_runtime.py", "audit-events"])
    payload = parse_json_output(result)
    ok = result.get("ok") and isinstance(payload, dict) and payload.get("ok") is True
    warning_count = payload.get("warning_count") if isinstance(payload, dict) else None
    status = "ok" if ok and not warning_count else "warning" if result.get("ok") and isinstance(payload, dict) else "fail"
    if status == "ok":
        summary = "runtime DB and JSONL event stream are consistent"
    elif status == "warning":
        summary = "runtime event stream has recoverable drift"
    else:
        summary = "runtime event stream audit failed"
    return CheckResult(
        id="coagent.runtime_event_audit",
        status=status,
        summary=summary,
        detail={"payload": payload, "result": result},
    )


def check_thread_graph_smoke() -> CheckResult:
    graph = check_command(
        "coagent.thread_graph",
        "runtime conversation graph smoke test passes",
        "runtime conversation graph smoke test failed",
        ["python3", "CoAgent/tests/test_runtime_thread_graph.py"],
    )
    transport = check_command(
        "coagent.transport_graph",
        "transport reconciliation closes conversation graph edges",
        "transport reconciliation graph smoke test failed",
        ["python3", "CoAgent/tests/test_transport_graph_reconcile.py"],
    )
    if graph.status == "ok" and transport.status == "ok":
        return CheckResult(
            id="coagent.thread_graph",
            status="ok",
            summary="runtime and transport conversation graph smoke tests pass",
            detail={"runtime_graph": graph.detail, "transport_graph": transport.detail},
        )
    return CheckResult(
        id="coagent.thread_graph",
        status="fail",
        summary="conversation graph smoke tests failed",
        detail={"runtime_graph": graph.detail, "transport_graph": transport.detail},
    )


def check_runtime_event_audit_smoke() -> CheckResult:
    return check_command(
        "coagent.runtime_event_audit_smoke",
        "runtime event stream audit smoke test passes",
        "runtime event stream audit smoke test failed",
        ["python3", "CoAgent/tests/test_runtime_event_audit.py"],
    )


def check_memory_context_smoke() -> CheckResult:
    return check_command(
        "coagent.memory_context",
        "fenced memory context smoke test passes",
        "fenced memory context smoke test failed",
        ["python3", "CoAgent/tests/test_memory_context.py"],
    )


def check_context_quality_smoke() -> CheckResult:
    return check_command(
        "coagent.context_quality",
        "context quality smoke test passes",
        "context quality smoke test failed",
        ["python3", "CoAgent/tests/test_context_quality.py"],
    )


def check_automation_guardrails_smoke() -> CheckResult:
    return check_command(
        "coagent.automation_guardrails",
        "automation guardrail smoke test passes",
        "automation guardrail smoke test failed",
        ["python3", "CoAgent/tests/test_automation_guardrails.py"],
    )


def check_preflight_policy_smoke() -> CheckResult:
    return check_command(
        "coagent.preflight_policy",
        "preflight policy smoke test passes",
        "preflight policy smoke test failed",
        ["python3", "CoAgent/tests/test_preflight_policy.py"],
    )


def check_transport_adapter_smoke() -> CheckResult:
    return check_command(
        "coagent.transport_adapter",
        "transport adapter smoke test passes",
        "transport adapter smoke test failed",
        ["python3", "CoAgent/tests/test_transport_adapter.py"],
    )


def check_result_router_smoke() -> CheckResult:
    return check_command(
        "coagent.result_router",
        "result router smoke test passes",
        "result router smoke test failed",
        ["python3", "CoAgent/tests/test_result_router.py"],
    )


def check_gateway_weixin_smoke() -> CheckResult:
    return check_command(
        "coagent.gateway_weixin",
        "cc-connect Weixin notification adapter smoke test passes",
        "cc-connect Weixin notification adapter smoke test failed",
        ["python3", "CoAgent/tests/test_gateway_weixin.py"],
    )


def check_review_notification_loop_smoke() -> CheckResult:
    return check_command(
        "coagent.review_notification_loop",
        "review-to-notification closed loop smoke test passes",
        "review-to-notification closed loop smoke test failed",
        ["python3", "CoAgent/tests/test_review_notification_loop.py"],
    )


def check_review_queue_smoke() -> CheckResult:
    return check_command(
        "coagent.review_queue",
        "human-review queue smoke test passes",
        "human-review queue smoke test failed",
        ["python3", "CoAgent/tests/test_review_queue.py"],
    )


def check_status_export_smoke() -> CheckResult:
    return check_command(
        "coagent.status_export",
        "compact status export smoke test passes",
        "compact status export smoke test failed",
        ["python3", "CoAgent/tests/test_status_export.py"],
    )


def check_task_health_smoke() -> CheckResult:
    return check_command(
        "coagent.task_health",
        "task-health snapshot smoke test passes",
        "task-health snapshot smoke test failed",
        ["python3", "CoAgent/tests/test_task_health.py"],
    )


def check_blocker_packet_smoke() -> CheckResult:
    return check_command(
        "coagent.blocker_packet",
        "blocker notification packet smoke test passes",
        "blocker notification packet smoke test failed",
        ["python3", "CoAgent/tests/test_blocker_packet.py"],
    )


def check_git_handoff_packet_smoke() -> CheckResult:
    return check_command(
        "coagent.git_handoff_packet",
        "Git handoff packet smoke test passes",
        "Git handoff packet smoke test failed",
        ["python3", "CoAgent/tests/test_git_handoff_packet.py"],
    )


def check_git_batch_plan_smoke() -> CheckResult:
    return check_command(
        "coagent.git_batch_plan",
        "Git batch plan smoke test passes",
        "Git batch plan smoke test failed",
        ["python3", "CoAgent/tests/test_git_batch_plan.py"],
    )


def check_git_split_index_smoke() -> CheckResult:
    return check_command(
        "coagent.git_split_index_check",
        "Git split-index smoke test passes",
        "Git split-index smoke test failed",
        ["python3", "CoAgent/tests/test_git_split_index_check.py"],
    )


def check_git_split_commit_dry_run_smoke() -> CheckResult:
    return check_command(
        "coagent.git_split_commit_dry_run",
        "Git split-commit dry-run smoke test passes",
        "Git split-commit dry-run smoke test failed",
        ["python3", "CoAgent/tests/test_git_split_commit_dry_run.py"],
    )


def check_git_split_commit_apply_smoke() -> CheckResult:
    return check_command(
        "coagent.git_split_commit_apply",
        "Git split-commit apply-plan smoke test passes",
        "Git split-commit apply-plan smoke test failed",
        ["python3", "CoAgent/tests/test_git_split_commit_apply.py"],
    )


def check_evidence_manifest_smoke() -> CheckResult:
    return check_command(
        "coagent.evidence_manifest",
        "evidence manifest smoke test passes",
        "evidence manifest smoke test failed",
        ["python3", "CoAgent/tests/test_evidence_manifest.py"],
    )


def check_evidence_refresh_commands_smoke() -> CheckResult:
    return check_command(
        "coagent.evidence_refresh_commands",
        "evidence refresh command plan smoke test passes",
        "evidence refresh command plan smoke test failed",
        ["python3", "CoAgent/tests/test_evidence_refresh_commands.py"],
    )


def check_review_package_smoke() -> CheckResult:
    return check_command(
        "coagent.review_package",
        "human-review package smoke test passes",
        "human-review package smoke test failed",
        ["python3", "CoAgent/tests/test_review_package.py"],
    )


def check_protocol_compliance_smoke() -> CheckResult:
    return check_command(
        "coagent.protocol_compliance",
        "protocol compliance smoke test passes",
        "protocol compliance smoke test failed",
        ["python3", "CoAgent/tests/test_protocol_compliance_smoke.py"],
    )


def check_goal_alignment_smoke() -> CheckResult:
    return check_command(
        "coagent.goal_alignment",
        "goal alignment smoke test passes",
        "goal alignment smoke test failed",
        ["python3", "CoAgent/tests/test_goal_alignment.py"],
    )


def check_lifecycle_smoke() -> CheckResult:
    return check_command(
        "coagent.lifecycle",
        "end-to-end task lifecycle smoke test passes",
        "end-to-end task lifecycle smoke test failed",
        ["python3", "CoAgent/tests/test_lifecycle_smoke.py"],
    )


def check_task_bootstrap_smoke() -> CheckResult:
    return check_command(
        "coagent.task_bootstrap",
        "long-task bootstrap and recovery smoke test passes",
        "long-task bootstrap and recovery smoke test failed",
        ["python3", "CoAgent/tests/test_task_bootstrap.py"],
    )


def check_automation_dispatch_plan_smoke() -> CheckResult:
    return check_command(
        "coagent.automation_dispatch_plan",
        "automation dispatch planning smoke test passes",
        "automation dispatch planning smoke test failed",
        ["python3", "CoAgent/tests/test_automation_dispatch_plan.py"],
    )


def check_automation_worker_status() -> CheckResult:
    result = run(["python3", "CoAgent/automation/automation_runner.py", "worker-status"])
    payload = parse_json_output(result)
    active_count = payload.get("active_count") if isinstance(payload, dict) else None
    stale_count = payload.get("stale_count") if isinstance(payload, dict) else None
    ok = result.get("ok") and isinstance(active_count, int) and isinstance(stale_count, int)
    return CheckResult(
        id="coagent.automation_worker_status",
        status="ok" if ok else "fail",
        summary="automation worker lock status is readable" if ok else "automation worker lock status failed",
        detail={"active_count": active_count, "stale_count": stale_count, "result": result},
    )


def check_automation_plan() -> CheckResult:
    tasks_path = ROOT / "CoAgent" / "automation" / "automation_tasks.json"
    threads_path = ROOT / "CoAgent" / "dispatch" / "department_threads.json"
    try:
        tasks = json.loads(tasks_path.read_text(encoding="utf-8")).get("tasks", [])
        threads = json.loads(threads_path.read_text(encoding="utf-8")).get("threads", [])
    except (OSError, json.JSONDecodeError) as exc:
        return CheckResult(
            id="coagent.automation_plan",
            status="fail",
            summary="automation registries are unreadable",
            detail={"error": str(exc)},
        )
    thread_by_department = {
        item.get("department"): item
        for item in threads
        if item.get("department") and item.get("thread_id")
    }
    daily_tasks = [task for task in tasks if task.get("cadence") == "daily"]
    missing_departments = sorted(
        {
            task.get("department", "")
            for task in daily_tasks
            if task.get("department") not in thread_by_department
        }
    )
    ok = bool(daily_tasks) and not missing_departments
    return CheckResult(
        id="coagent.automation_plan",
        status="ok" if ok else "warning",
        summary="daily automation can build dispatch plans" if ok else "daily automation dispatch plan needs review",
        detail={
            "daily_task_count": len(daily_tasks),
            "missing_departments": missing_departments,
            "departments": sorted(thread_by_department),
        },
    )


def check_knowledge_search() -> CheckResult:
    try:
        if knowledge_indexer.INDEX_JSON.exists():
            build = {"count": "existing", "index_path": rel(knowledge_indexer.INDEX_JSON)}
        else:
            build = knowledge_indexer.build_index()
        search = knowledge_indexer.search_index("worker policy stale lock concurrency", limit=20)
    except Exception as exc:
        return CheckResult(
            id="coagent.knowledge_search",
            status="fail",
            summary="knowledge index build/search failed",
            detail={"error": str(exc)},
        )
    count = search.get("count")
    hits = search.get("hits", [])
    worker_hit = any("CoAgent/automation" in item.get("path", "") for item in hits if isinstance(item, dict))
    ok = isinstance(count, int) and count > 0 and worker_hit
    return CheckResult(
        id="coagent.knowledge_search",
        status="ok" if ok else "fail",
        summary="knowledge index builds and searches" if ok else "knowledge index build/search failed",
        detail={"search_count": count, "worker_hit": worker_hit, "build": build, "search": search},
    )


def check_transport_readiness() -> CheckResult:
    path = ROOT / "CoAgent" / "dispatch" / "department_threads.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return CheckResult(
            id="coagent.transport_readiness",
            status="fail",
            summary="transport registry is unreadable",
            detail={"path": rel(path), "error": str(exc)},
        )
    missing = []
    for item in data.get("threads", []):
        if not item.get("thread_id"):
            missing.append(item.get("department", "<unknown>"))
    status = "ok" if not missing else "warning"
    return CheckResult(
        id="coagent.transport_readiness",
        status=status,
        summary="department threads have thread ids" if status == "ok" else "some department threads lack thread ids",
        detail={"missing_thread_id_departments": missing},
    )


def check_transport_session_files() -> CheckResult:
    path = ROOT / "CoAgent" / "dispatch" / "department_threads.json"
    sessions_root = CODEX_HOME / "sessions"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return CheckResult(
            id="coagent.transport_session_files",
            status="fail",
            summary="transport registry is unreadable",
            detail={"path": rel(path), "error": str(exc)},
        )
    if not sessions_root.exists():
        return CheckResult(
            id="coagent.transport_session_files",
            status="warning",
            summary="local Codex session root is missing",
            detail={"sessions_root": str(sessions_root)},
        )
    missing: list[dict[str, str]] = []
    found: list[dict[str, str]] = []
    for item in data.get("threads", []):
        thread_id = item.get("thread_id")
        department = item.get("department", "<unknown>")
        if not thread_id:
            continue
        matches = sorted(sessions_root.rglob(f"*{thread_id}*.jsonl"))
        if matches:
            found.append({"department": department, "thread_id": thread_id, "path": str(matches[0])})
        else:
            missing.append({"department": department, "thread_id": thread_id})
    status = "ok" if not missing else "warning"
    return CheckResult(
        id="coagent.transport_session_files",
        status=status,
        summary="department thread rollout files exist" if status == "ok" else "some department thread rollout files are missing",
        detail={"sessions_root": str(sessions_root), "found": found, "missing": missing},
    )


def check_plan(args: argparse.Namespace) -> list:
    quick_checks = [
        check_required_paths,
        check_department_registry,
        check_transport_readiness,
        check_transport_session_files,
        check_reference_index,
        check_learning_index,
        check_learning_coverage,
        check_preflight,
        check_automation_worker_status,
        check_active_queue,
        check_runtime_event_audit,
        check_automation_plan,
        check_knowledge_search,
    ]
    full_only_checks = [
        check_thread_graph_smoke,
        check_runtime_event_audit_smoke,
        check_memory_context_smoke,
        check_context_quality_smoke,
        check_preflight_policy_smoke,
        check_automation_guardrails_smoke,
        check_transport_adapter_smoke,
        check_result_router_smoke,
        check_gateway_weixin_smoke,
        check_review_notification_loop_smoke,
        check_review_queue_smoke,
        check_task_health_smoke,
        check_blocker_packet_smoke,
        check_git_batch_plan_smoke,
        check_git_handoff_packet_smoke,
        check_git_split_index_smoke,
        check_git_split_commit_dry_run_smoke,
        check_git_split_commit_apply_smoke,
        check_evidence_refresh_commands_smoke,
        check_evidence_manifest_smoke,
        check_review_package_smoke,
        check_protocol_compliance_smoke,
        check_goal_alignment_smoke,
        check_lifecycle_smoke,
        check_task_bootstrap_smoke,
        check_automation_dispatch_plan_smoke,
    ]
    checks = list(quick_checks)
    if args.mode == "full":
        checks.extend(full_only_checks)
    if not getattr(args, "skip_status_export", False):
        if args.mode == "full":
            checks.insert(20, check_status_export_smoke)
    return checks


def collect(args: argparse.Namespace) -> dict[str, Any]:
    started_at = time.monotonic()
    checks = [run_check(func) for func in check_plan(args)]
    fail_count = sum(1 for check in checks if check.status == "fail")
    warning_count = sum(1 for check in checks if check.status == "warning")
    overall = "fail" if fail_count else "warning" if warning_count else "ok"
    report = {
        "overallStatus": overall,
        "root": str(ROOT),
        "mode": args.mode,
        "elapsed_seconds": round(time.monotonic() - started_at, 3),
        "checks": {
            check.id: {
                "id": check.id,
                "status": check.status,
                "summary": check.summary,
                "detail": check.detail,
            }
            for check in checks
        },
        "counts": {
            "ok": sum(1 for check in checks if check.status == "ok"),
            "warning": warning_count,
            "fail": fail_count,
            "total": len(checks),
        },
    }
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        if not (output.resolve() == ROOT.resolve() or ROOT.resolve() in output.resolve().parents):
            raise SystemExit(f"output path is outside MoSim: {args.output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        report["output"] = rel(output)
    return report


def print_text(report: dict[str, Any]) -> None:
    for check in report["checks"].values():
        print(f"{check['status']:7} {check['id']} - {check['summary']}")
    print(f"overall={report['overallStatus']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument("--output", type=Path, help="write JSON report inside the project")
    parser.add_argument(
        "--mode",
        choices=["quick", "full"],
        default="quick",
        help="quick checks recoverability; full also runs all smoke tests",
    )
    parser.add_argument(
        "--skip-status-export",
        action="store_true",
        help="skip status-export smoke test when doctor is called from status export",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = collect(args)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text(report)
    return 0 if report["overallStatus"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
