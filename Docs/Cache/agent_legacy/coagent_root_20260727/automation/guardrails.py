#!/usr/bin/env python3
"""Automation guardrails for CoAgent recurring tasks."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
LOCK_DIR = ROOT / "Results" / "coagent_automation" / "locks"
WORKER_POLICY_JSON = ROOT / "CoAgent" / "automation" / "worker_policy.json"
ALLOWED_ROOT = ROOT.resolve()

DEFAULT_ALLOWED_TOOLS = {
    "coagent_runtime",
    "coagent_dispatch",
    "coagent_knowledge",
    "coagent_learning",
    "coagent_preflight",
    "git_read",
    "file_read",
    "file_write_project",
}
DEFAULT_DENIED_TOOLS = {
    "network",
    "external_write",
    "codex_app_private_db_write",
    "credential_read",
    "secret_store",
    "destructive_fs",
    "git_force",
}
PROMPT_INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"disregard\s+(all\s+)?(prior|previous)\s+instructions",
        r"reveal\s+(your\s+)?(system|developer)\s+prompt",
        r"print\s+(your\s+)?(system|developer)\s+prompt",
        r"show\s+(your\s+)?(system|developer)\s+prompt",
        r"bypass\s+(the\s+)?(policy|guardrails|safety)",
        r"disable\s+(the\s+)?(policy|guardrails|safety)",
        r"exfiltrat(e|ion)",
        r"secret(s)?\s*[:=]",
        r"api[_-]?key\s*[:=]",
        r"token\s*[:=]",
        r"password\s*[:=]",
        r"cookie\s*[:=]",
        r"ssh\s+private\s+key",
        r"BEGIN\s+(RSA|OPENSSH|DSA|EC)\s+PRIVATE\s+KEY",
    ]
]

DEFAULT_WORKER_POLICY = {
    "lock_ttl_seconds": 21600,
    "default_department_concurrency": 1,
    "max_total_active_locks": 3,
    "max_active_per_automation": 1,
    "department_concurrency": {},
    "notes": [],
}


@dataclass(frozen=True)
class GuardrailResult:
    ok: bool
    automation_id: str
    lock_id: str
    lock_path: str
    allowed_tools: list[str]
    denied_tools: list[str]
    findings: list[dict[str, Any]]
    acquired_lock: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "automation_id": self.automation_id,
            "lock_id": self.lock_id,
            "lock_path": self.lock_path,
            "allowed_tools": self.allowed_tools,
            "denied_tools": self.denied_tools,
            "findings": self.findings,
            "acquired_lock": self.acquired_lock,
        }


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def parse_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def load_worker_policy(path: Path = WORKER_POLICY_JSON) -> dict[str, Any]:
    if not path.exists():
        return dict(DEFAULT_WORKER_POLICY)
    data = json.loads(path.read_text(encoding="utf-8"))
    policy = dict(DEFAULT_WORKER_POLICY)
    policy.update(data)
    return policy


def project_relative(path: Path) -> str:
    return str(path.resolve().relative_to(ALLOWED_ROOT)).replace("\\", "/")


def normalize_project_paths(values: list[str], *, field: str) -> tuple[list[str], list[dict[str, Any]]]:
    normalized: list[str] = []
    findings: list[dict[str, Any]] = []
    for raw in values:
        candidate = Path(raw)
        full = candidate if candidate.is_absolute() else ROOT / candidate
        try:
            resolved = full.resolve()
        except OSError as exc:
            findings.append({"severity": "fail", "field": field, "value": raw, "reason": str(exc)})
            continue
        if not (resolved == ALLOWED_ROOT or ALLOWED_ROOT in resolved.parents):
            findings.append({"severity": "fail", "field": field, "value": raw, "reason": "outside_project"})
            continue
        normalized.append(str(resolved.relative_to(ALLOWED_ROOT)).replace("\\", "/"))
    return sorted(dict.fromkeys(normalized)), findings


def text_fields(task: dict[str, Any]) -> list[tuple[str, str]]:
    fields: list[tuple[str, str]] = []
    for key in ["automation_id", "role", "department", "objective", "acceptance", "stop_condition"]:
        value = task.get(key)
        if value:
            fields.append((key, str(value)))
    for key in ["read_scope", "write_scope"]:
        for index, value in enumerate(task.get(key, [])):
            fields.append((f"{key}[{index}]", str(value)))
    return fields


def prompt_injection_findings(task: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for field, text in text_fields(task):
        for pattern in PROMPT_INJECTION_PATTERNS:
            match = pattern.search(text)
            if match:
                findings.append(
                    {
                        "severity": "fail",
                        "field": field,
                        "pattern": pattern.pattern,
                        "match": match.group(0),
                    }
                )
    return findings


def tool_scope(task: dict[str, Any]) -> tuple[list[str], list[str], list[dict[str, Any]]]:
    scope = task.get("tool_scope") or {}
    allowed = sorted(dict.fromkeys(scope.get("allowed", [])))
    denied = sorted(dict.fromkeys(scope.get("denied", [])))
    findings: list[dict[str, Any]] = []
    if not allowed:
        findings.append({"severity": "fail", "field": "tool_scope.allowed", "reason": "empty"})
    unknown_allowed = sorted(set(allowed).difference(DEFAULT_ALLOWED_TOOLS))
    unknown_denied = sorted(set(denied).difference(DEFAULT_DENIED_TOOLS))
    if unknown_allowed:
        findings.append({"severity": "fail", "field": "tool_scope.allowed", "reason": "unknown_tools", "tools": unknown_allowed})
    if unknown_denied:
        findings.append({"severity": "fail", "field": "tool_scope.denied", "reason": "unknown_tools", "tools": unknown_denied})
    overlap = sorted(set(allowed).intersection(denied))
    if overlap:
        findings.append({"severity": "fail", "field": "tool_scope", "reason": "allowed_and_denied", "tools": overlap})
    return allowed, denied, findings


def lock_path_for(lock_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", lock_id).strip("_")
    if not safe:
        raise SystemExit("empty automation lock id")
    return LOCK_DIR / f"{safe}.lock"


def read_lock(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"error": "unreadable_lock", "path": project_relative(path)}
    if isinstance(payload, dict):
        payload.setdefault("path", project_relative(path))
        return payload
    return {"error": "invalid_lock_payload", "path": project_relative(path)}


def active_locks(*, now: datetime | None = None, policy: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    now = now or datetime.now(timezone.utc).astimezone()
    policy = policy or load_worker_policy()
    ttl = int(policy.get("lock_ttl_seconds", DEFAULT_WORKER_POLICY["lock_ttl_seconds"]))
    locks: list[dict[str, Any]] = []
    if not LOCK_DIR.exists():
        return locks
    for path in sorted(LOCK_DIR.glob("*.lock")):
        payload = read_lock(path)
        acquired_at = parse_timestamp(str(payload.get("acquired_at", "")))
        age_seconds = int((now - acquired_at).total_seconds()) if acquired_at else None
        is_stale = age_seconds is None or age_seconds > ttl
        payload["path"] = project_relative(path)
        payload["age_seconds"] = age_seconds
        payload["stale"] = is_stale
        locks.append(payload)
    return locks


def concurrency_findings(task: dict[str, Any], *, policy: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    policy = policy or load_worker_policy()
    locks = active_locks(policy=policy)
    live_locks = [lock for lock in locks if not lock.get("stale")]
    stale_locks = [lock for lock in locks if lock.get("stale")]
    findings: list[dict[str, Any]] = []
    if stale_locks:
        findings.append(
            {
                "severity": "warning",
                "field": "locks",
                "reason": "stale_locks_present",
                "locks": stale_locks,
            }
        )
    max_total = int(policy.get("max_total_active_locks", DEFAULT_WORKER_POLICY["max_total_active_locks"]))
    if len(live_locks) >= max_total:
        findings.append(
            {
                "severity": "fail",
                "field": "worker_policy.max_total_active_locks",
                "reason": "concurrency_limit_reached",
                "limit": max_total,
                "active": len(live_locks),
            }
        )
    automation_id = str(task.get("automation_id", ""))
    max_per_automation = int(policy.get("max_active_per_automation", DEFAULT_WORKER_POLICY["max_active_per_automation"]))
    active_same_automation = [lock for lock in live_locks if lock.get("automation_id") == automation_id]
    if automation_id and len(active_same_automation) >= max_per_automation:
        findings.append(
            {
                "severity": "fail",
                "field": "worker_policy.max_active_per_automation",
                "reason": "automation_concurrency_limit_reached",
                "automation_id": automation_id,
                "limit": max_per_automation,
                "active": len(active_same_automation),
            }
        )
    department = str(task.get("department", ""))
    department_limits = policy.get("department_concurrency", {})
    department_limit = int(department_limits.get(department, policy.get("default_department_concurrency", 1)))
    active_same_department = [lock for lock in live_locks if lock.get("department") == department]
    if department and len(active_same_department) >= department_limit:
        findings.append(
            {
                "severity": "fail",
                "field": "worker_policy.department_concurrency",
                "reason": "department_concurrency_limit_reached",
                "department": department,
                "limit": department_limit,
                "active": len(active_same_department),
            }
        )
    return findings


def worker_status(policy_path: Path = WORKER_POLICY_JSON) -> dict[str, Any]:
    policy = load_worker_policy(policy_path)
    locks = active_locks(policy=policy)
    live = [lock for lock in locks if not lock.get("stale")]
    stale = [lock for lock in locks if lock.get("stale")]
    by_department: dict[str, int] = {}
    by_automation: dict[str, int] = {}
    for lock in live:
        department = str(lock.get("department", ""))
        automation_id = str(lock.get("automation_id", ""))
        if department:
            by_department[department] = by_department.get(department, 0) + 1
        if automation_id:
            by_automation[automation_id] = by_automation.get(automation_id, 0) + 1
    return {
        "ok": True,
        "policy": {
            "lock_ttl_seconds": int(policy.get("lock_ttl_seconds", DEFAULT_WORKER_POLICY["lock_ttl_seconds"])),
            "default_department_concurrency": int(policy.get("default_department_concurrency", 1)),
            "max_total_active_locks": int(policy.get("max_total_active_locks", DEFAULT_WORKER_POLICY["max_total_active_locks"])),
            "max_active_per_automation": int(policy.get("max_active_per_automation", DEFAULT_WORKER_POLICY["max_active_per_automation"])),
            "department_concurrency": policy.get("department_concurrency", {}),
        },
        "lock_count": len(locks),
        "active_count": len(live),
        "stale_count": len(stale),
        "active_by_department": by_department,
        "active_by_automation": by_automation,
        "locks": locks,
    }


def acquire_lock(lock_id: str, *, payload: dict[str, Any]) -> tuple[bool, dict[str, Any] | None, Path]:
    path = lock_path_for(lock_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = path.open("x", encoding="utf-8")
    except FileExistsError:
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {"error": "unreadable_lock", "path": project_relative(path)}
        return False, existing, path
    with handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return True, None, path


def release_lock(lock_id: str) -> dict[str, Any]:
    path = lock_path_for(lock_id)
    if path.exists():
        path.unlink()
        return {"released": True, "lock_path": project_relative(path)}
    return {"released": False, "lock_path": project_relative(path)}


def check_task(task: dict[str, Any], *, acquire: bool = False, run_id: str = "", reviewed: bool = False) -> GuardrailResult:
    automation_id = str(task.get("automation_id", ""))
    if not automation_id:
        raise SystemExit("automation task missing automation_id")
    findings: list[dict[str, Any]] = []
    read_scope, read_findings = normalize_project_paths(task.get("read_scope", []), field="read_scope")
    write_scope, write_findings = normalize_project_paths(task.get("write_scope", []), field="write_scope")
    findings.extend(read_findings)
    findings.extend(write_findings)
    allowed, denied, tool_findings = tool_scope(task)
    findings.extend(tool_findings)
    findings.extend(prompt_injection_findings(task))
    if acquire:
        findings.extend(concurrency_findings(task))
    requires_human_review = task.get("requires_human_review")
    if requires_human_review is None:
        findings.append({"severity": "warning", "field": "requires_human_review", "reason": "not_explicit"})
    elif acquire and requires_human_review and not reviewed:
        findings.append({"severity": "fail", "field": "requires_human_review", "reason": "review_not_confirmed"})
    lock_id = str(task.get("lock_id") or f"automation_{automation_id}")
    lock_path = lock_path_for(lock_id)
    if acquire and lock_path.exists():
        findings.append(
            {
                "severity": "fail",
                "field": "lock_id",
                "reason": "already_locked",
                "existing": read_lock(lock_path),
            }
        )
    acquired = False
    if acquire and not any(item["severity"] == "fail" for item in findings):
        payload = {
            "automation_id": automation_id,
            "lock_id": lock_id,
            "run_id": run_id,
            "department": task.get("department", ""),
            "cadence": task.get("cadence", ""),
            "read_scope": read_scope,
            "write_scope": write_scope,
            "allowed_tools": allowed,
            "acquired_at": now_iso(),
        }
        acquired, existing, lock_path = acquire_lock(lock_id, payload=payload)
        if not acquired:
            findings.append(
                {
                    "severity": "fail",
                    "field": "lock_id",
                    "reason": "already_locked",
                    "existing": existing,
                }
            )
    ok = not any(item["severity"] == "fail" for item in findings)
    return GuardrailResult(
        ok=ok,
        automation_id=automation_id,
        lock_id=lock_id,
        lock_path=project_relative(lock_path),
        allowed_tools=allowed,
        denied_tools=denied,
        findings=findings,
        acquired_lock=acquired,
    )


def check_registry(tasks: list[dict[str, Any]], *, acquire: bool = False, run_id: str = "", reviewed: bool = False) -> dict[str, Any]:
    results = [check_task(task, acquire=acquire, run_id=run_id, reviewed=reviewed).to_dict() for task in tasks]
    return {
        "ok": all(item["ok"] for item in results),
        "count": len(results),
        "results": results,
    }
