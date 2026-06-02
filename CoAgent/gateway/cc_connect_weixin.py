#!/usr/bin/env python3
"""Safe cc-connect Weixin notification adapter for CoAgent.

This module is intentionally narrow. It converts approved CoAgent blocker or
review packets into short human-action messages and sends them through an
already configured cc-connect runtime only when --send is explicit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "Results" / "tmp" / "cc-connect-weixin-smoke" / "config-wsl-runtime.toml"
DEFAULT_BIN = ROOT / "Results" / "tmp" / "cc-connect-node" / "node_modules" / "cc-connect" / "bin" / "cc-connect"
DEFAULT_DATA_DIR = Path("/home/linux/.cache/mosim/coagent/cc-connect-weixin/data")
DEFAULT_AUDIT = ROOT / "Results" / "coagent_gateway" / "weixin_notifications.jsonl"
DEFAULT_DEDUPE = ROOT / "Results" / "coagent_gateway" / "weixin_dedupe.json"
DEFAULT_RECOVERY_DIR = ROOT / "Results" / "coagent_gateway" / "recovery"
DEFAULT_PROJECT = "MoSim｜微信通知网关"

ALLOWED_CLASSES = {"auth_required", "approval_required", "manual_review_required", "incident_required"}
ALLOWED_REVIEW_DECISIONS = {"needs_review", "accepted_with_concerns", "needs_rework", "rejected"}
SECRET_PATTERNS = [
    re.compile(r"(?i)(token|bearer|authorization|api[_-]?key|password|secret|cookie|base_url)\s*[:=]\s*\S+"),
    re.compile(r"(?i)context[_-]?token\s*[:=]\s*\S+"),
    re.compile(r"(?i)(sk-[A-Za-z0-9_-]{12,})"),
    re.compile(r"(?i)BEGIN\s+(RSA|OPENSSH|DSA|EC)\s+PRIVATE\s+KEY"),
    re.compile(r"o9cq[A-Za-z0-9_.@-]+"),
    re.compile(r"[A-Za-z0-9_.+-]+@im\.(wechat|bot)"),
]


@dataclass(frozen=True)
class NotificationPlan:
    ok: bool
    packet_path: str
    packet_type: str
    task_id: str
    dedupe_key: str
    message: str
    blocked_reason: str = ""
    send_allowed: bool = False
    already_sent: bool = False


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_packet(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if stripped.startswith("{"):
        data = json.loads(text)
        if not isinstance(data, dict):
            raise SystemExit("packet JSON must be an object")
        return data
    # Minimal YAML-ish parser for current CoAgent templates. It is deliberately
    # conservative; complex packets should be passed as JSON.
    data: dict[str, Any] = {}
    for line in text.splitlines():
        if not line or line.startswith("#") or ": " not in line:
            continue
        key, value = line.split(": ", 1)
        value = value.strip()
        if value in {"[]", ""}:
            parsed: Any = [] if value == "[]" else ""
        elif value in {"true", "false"}:
            parsed = value == "true"
        elif value.startswith("[") or value.startswith("{"):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                parsed = value
        else:
            parsed = value.strip('"')
        data[key.strip()] = parsed
    return data


def redact(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("<redacted>", redacted)
    return redacted


def truncate(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 20)].rstrip() + "\n...[truncated]"


def as_list(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def packet_type_for(payload: dict[str, Any]) -> str:
    template = str(payload.get("template_type", ""))
    if template in {"blocker_notification", "review_packet"}:
        return template
    if "human_action_required" in payload or "blocked_surface" in payload:
        return "blocker_notification"
    if "decision" in payload and "review_id" in payload:
        return "review_packet"
    if str(payload.get("canonical_status", "")) in {"auth_required", "review_required", "blocked", "failed"}:
        return "result_packet"
    return "unknown"


def dedupe_key_for(payload: dict[str, Any], packet_type: str, message: str) -> str:
    explicit = str(payload.get("dedupe_key") or "")
    if explicit:
        return explicit
    task_id = str(payload.get("task_id") or "unknown")
    digest = hashlib.sha256(message.encode("utf-8")).hexdigest()[:16]
    return f"{packet_type}:{task_id}:{digest}"


def format_blocker(payload: dict[str, Any]) -> tuple[bool, str, str]:
    klass = str(payload.get("class") or payload.get("canonical_status") or "")
    if klass not in ALLOWED_CLASSES:
        return False, "", f"blocker class {klass!r} is not allowed for Weixin escalation"
    task_id = str(payload.get("task_id") or "unknown")
    severity = str(payload.get("severity") or "medium")
    surface = str(payload.get("blocked_surface") or "unknown surface")
    action = str(payload.get("human_action_required") or payload.get("next_recommended_action") or "")
    why = str(payload.get("why_now") or payload.get("summary") or "")
    evidence = as_list(payload.get("evidence_paths") or payload.get("evidence"))[:5]
    resume = str(payload.get("resume_packet_path") or "")
    lines = [
        "【MoSim CoAgent 人工审核】",
        f"任务: {task_id}",
        f"类型: {klass} / {severity}",
        f"阻塞面: {surface}",
        f"需要你处理: {action or '请查看主对话/证据包并确认下一步。'}",
    ]
    if why:
        lines.append(f"原因: {why}")
    if evidence:
        lines.append("证据: " + ", ".join(evidence))
    if resume:
        lines.append(f"恢复包: {resume}")
    lines.append("处理后请在主对话或微信回复审核结论。")
    return True, "\n".join(lines), ""


def format_review(payload: dict[str, Any]) -> tuple[bool, str, str]:
    decision = str(payload.get("decision") or payload.get("review_status") or "")
    if decision not in ALLOWED_REVIEW_DECISIONS:
        return False, "", f"review decision {decision!r} does not require Weixin escalation"
    task_id = str(payload.get("task_id") or "unknown")
    review_id = str(payload.get("review_id") or "review")
    summary = str(payload.get("summary") or "")
    evidence = as_list(payload.get("evidence_paths") or payload.get("evidence"))[:5]
    risks = as_list(payload.get("risks"))[:5]
    rework = as_list(payload.get("required_rework"))[:5]
    lines = [
        "【MoSim CoAgent 审核请求】",
        f"任务: {task_id}",
        f"审核: {review_id}",
        f"决策状态: {decision}",
    ]
    if summary:
        lines.append(f"摘要: {summary}")
    if evidence:
        lines.append("证据: " + ", ".join(evidence))
    if risks:
        lines.append("风险: " + "; ".join(risks))
    if rework:
        lines.append("需返工: " + "; ".join(rework))
    lines.append("请回复: accepted / accepted_with_concerns / needs_rework / rejected，并说明理由。")
    return True, "\n".join(lines), ""


def format_result(payload: dict[str, Any]) -> tuple[bool, str, str]:
    canonical = str(payload.get("canonical_status") or payload.get("status") or "")
    if canonical not in {"auth_required", "review_required", "blocked", "failed"}:
        return False, "", f"result canonical_status {canonical!r} does not require Weixin escalation"
    mapped = {
        "auth_required": "auth_required",
        "review_required": "manual_review_required",
        "blocked": "incident_required",
        "failed": "incident_required",
    }[canonical]
    blocker = {
        "task_id": payload.get("task_id", "unknown"),
        "class": mapped,
        "severity": "high" if canonical in {"auth_required", "failed"} else "medium",
        "blocked_surface": payload.get("checkpoint") or payload.get("summary") or "CoAgent task",
        "human_action_required": payload.get("next_recommended_action") or "请审核结果包并确认下一步。",
        "why_now": payload.get("summary", ""),
        "evidence_paths": payload.get("evidence", []),
    }
    return format_blocker(blocker)


def build_plan(packet_path: Path, *, max_chars: int = 1500) -> NotificationPlan:
    payload = read_packet(packet_path)
    packet_type = packet_type_for(payload)
    if packet_type == "blocker_notification":
        allowed, message, reason = format_blocker(payload)
    elif packet_type == "review_packet":
        allowed, message, reason = format_review(payload)
    elif packet_type == "result_packet":
        allowed, message, reason = format_result(payload)
    else:
        allowed, message, reason = False, "", "unsupported packet type"
    message = truncate(redact(message), max_chars) if message else ""
    dedupe = dedupe_key_for(payload, packet_type, message or reason)
    return NotificationPlan(
        ok=allowed,
        packet_path=rel(packet_path),
        packet_type=packet_type,
        task_id=str(payload.get("task_id") or "unknown"),
        dedupe_key=dedupe,
        message=message,
        blocked_reason=reason,
        send_allowed=allowed,
    )


def load_dedupe(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"sent": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"sent": {}}
    if not isinstance(data, dict):
        return {"sent": {}}
    data.setdefault("sent", {})
    return data


def save_dedupe(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_audit(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def send_message(
    message: str,
    *,
    cc_bin: Path,
    data_dir: Path,
    project: str,
    session: str,
    timeout: int,
) -> dict[str, Any]:
    command = [
        str(cc_bin),
        "send",
        "--data-dir",
        str(data_dir),
        "--project",
        project,
    ]
    if session:
        command.extend(["--session", session])
    command.append("--stdin")
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            input=message,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "timeout": True,
            "returncode": None,
            "stdout": redact(exc.stdout or "") if isinstance(exc.stdout, str) else "",
            "stderr": redact(exc.stderr or "") if isinstance(exc.stderr, str) else "",
            "command": command[:1] + ["send", "--data-dir", "<runtime>", "--project", project, "--session", "<redacted>", "--stdin"],
        }
    return {
        "ok": completed.returncode == 0,
        "timeout": False,
        "returncode": completed.returncode,
        "stdout": redact(completed.stdout.strip()),
        "stderr": redact(completed.stderr.strip()),
        "command": command[:1] + ["send", "--data-dir", "<runtime>", "--project", project, "--session", "<redacted>", "--stdin"],
    }


def classify_send_failure(result: dict[str, Any]) -> str:
    """Classify cc-connect/Weixin send failures without exposing secrets."""
    if result.get("ok"):
        return "ok"
    if result.get("timeout"):
        return "timeout"
    text = f"{result.get('stdout', '')}\n{result.get('stderr', '')}".lower()
    if "ret=-2" in text:
        return "weixin_ret_minus_2"
    if "missing context_token" in text or "context_token is required" in text:
        return "missing_context_token"
    if "no active session found" in text:
        return "no_active_session"
    if "connection refused" in text or "no such file or directory" in text or "api.sock" in text:
        return "internal_api_unavailable"
    return "other"


def inspect_gateway_state(*, data_dir: Path, project: str, session: str) -> dict[str, Any]:
    """Return non-secret runtime health facts for recovery/audit records."""
    sessions_dir = data_dir / "sessions"
    run_socket = data_dir / "run" / "api.sock"
    session_files = sorted(sessions_dir.glob(f"{project}_*.json")) if sessions_dir.exists() else []
    all_session_files = sorted(sessions_dir.glob("*.json")) if sessions_dir.exists() else []
    resolved = resolve_session_key(session, data_dir=data_dir, project=project)
    context_root = data_dir / "weixin" / project
    context_files = sorted(context_root.glob("*/context_tokens.json")) if context_root.exists() else []
    return {
        "data_dir_exists": data_dir.exists(),
        "api_socket_exists": run_socket.exists(),
        "project_session_files": len(session_files),
        "all_session_files": len(all_session_files),
        "session_resolved": bool(resolved),
        "session_key_type": "platform" if ":" in resolved else "alias_or_empty",
        "context_token_files": len(context_files),
    }


def restart_cc_connect(
    *,
    cc_bin: Path,
    config: Path,
    data_dir: Path,
    timeout: int,
) -> dict[str, Any]:
    """Restart the cc-connect runtime with --force and wait for its API socket.

    This is a bounded recovery action. It may refresh stale process/socket state,
    but it cannot fabricate a Weixin context_token when the ilink side requires
    a fresh inbound message or QR login.
    """
    if not cc_bin.exists():
        return {"ok": False, "reason": "cc_bin_missing", "cc_bin": str(cc_bin)}
    if not config.exists():
        return {"ok": False, "reason": "config_missing", "config": rel(config) if ROOT in config.resolve().parents else str(config)}

    recovery_root = ROOT / "Results" / "tmp" / "cc-connect-weixin-smoke"
    recovery_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = recovery_root / f"recover-{stamp}.log"
    command = [str(cc_bin), "--config", str(config), "--force"]
    with log_path.open("w", encoding="utf-8") as log_handle:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
        )

    socket_path = data_dir / "run" / "api.sock"
    deadline = time.monotonic() + max(1, timeout)
    while time.monotonic() < deadline:
        if socket_path.exists():
            return {
                "ok": True,
                "pid": process.pid,
                "log_path": rel(log_path),
                "api_socket_exists": True,
            }
        if process.poll() is not None:
            break
        time.sleep(0.5)

    tail = ""
    try:
        tail = log_path.read_text(encoding="utf-8", errors="replace")[-2000:]
    except OSError:
        pass
    return {
        "ok": False,
        "pid": process.pid,
        "returncode": process.poll(),
        "log_path": rel(log_path),
        "api_socket_exists": socket_path.exists(),
        "stderr_tail": redact(tail),
    }


def write_recovery_packet(
    *,
    directory: Path,
    task_id: str,
    failure_kind: str,
    send_result: dict[str, Any],
    state: dict[str, Any],
    recovery: dict[str, Any] | None,
) -> str:
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = directory / f"weixin_recovery_required_{stamp}.json"
    payload = {
        "template_type": "blocker_notification",
        "task_id": task_id,
        "class": "manual_review_required",
        "severity": "high",
        "blocked_surface": "CoAgent Weixin gateway outbound notification",
        "human_action_required": (
            "Weixin ilink outbound context is stale. If automatic restart/retry failed, "
            "open the MoSim WeChat gateway chat and send one plain text message; "
            "if the next send still fails, rerun cc-connect weixin setup QR login."
        ),
        "why_now": (
            "cc-connect can keep a process and context_tokens.json while the Weixin "
            "platform still rejects sendMessage; software can restart/retry once, "
            "but cannot synthesize a new ilink context_token without a valid inbound event."
        ),
        "evidence_paths": [
            "CoAgent/gateway/cc_connect_weixin.py",
            "CoAgent/docs/status/cc_connect_weixin_smoke_2026_05_31.md",
            "PROGRESS.md",
        ],
        "gateway_failure_kind": failure_kind,
        "gateway_state": state,
        "send_result": {k: v for k, v in send_result.items() if k != "command"},
        "recovery_result": recovery or {},
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return rel(path)


def resolve_session_key(session: str, *, data_dir: Path, project: str) -> str:
    """Resolve convenient session aliases to cc-connect platform session keys.

    cc-connect session files store internal conversation ids under `sessions`
    and the send API expects the platform key from `active_session`, such as a
    `weixin:dm:...` key. Passing `s1`, the project name, or a session JSON path
    directly can produce `no active session found`, even when the QR login is
    still valid.
    """
    session = session.strip()
    if ":" in session:
        return session

    sessions_dir = data_dir / "sessions"

    explicit_path: Path | None = None
    if session.endswith(".json"):
        maybe_path = Path(session)
        if maybe_path.is_absolute():
            explicit_path = maybe_path
        else:
            explicit_path = sessions_dir / maybe_path

    candidates: list[Path] = []
    if explicit_path is not None:
        candidates.append(explicit_path)
    candidates.extend(sorted(sessions_dir.glob(f"{project}_*.json")))
    candidates.extend(path for path in sorted(sessions_dir.glob("*.json")) if path not in candidates)

    for path in candidates:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        active = payload.get("active_session") or {}
        if not isinstance(active, dict):
            continue
        if not session or session == project or explicit_path is not None:
            for platform_key in active:
                return str(platform_key)
        for platform_key, internal_id in active.items():
            if str(platform_key) == session:
                return str(platform_key)
            if str(internal_id) == session:
                return str(platform_key)
    return session


def notify(args: argparse.Namespace) -> dict[str, Any]:
    packet = project_path(args.packet)
    plan = build_plan(packet, max_chars=args.max_chars)
    dedupe = load_dedupe(args.dedupe)
    already_sent = plan.dedupe_key in dedupe.get("sent", {})
    plan_dict = {
        "ok": plan.ok,
        "packet_path": plan.packet_path,
        "packet_type": plan.packet_type,
        "task_id": plan.task_id,
        "dedupe_key": plan.dedupe_key,
        "message": plan.message,
        "blocked_reason": plan.blocked_reason,
        "send_allowed": plan.send_allowed,
        "already_sent": already_sent,
    }
    record = {
        "timestamp": now_iso(),
        "mode": "send" if args.send else "dry_run",
        "plan": {**plan_dict, "message": "<omitted>" if args.omit_message_in_audit else plan.message},
    }
    if not plan.ok:
        record["send_result"] = {"ok": False, "skipped": True, "reason": plan.blocked_reason}
        append_audit(args.audit, record)
        return {"ok": False, **plan_dict, "send_result": record["send_result"]}
    if already_sent and not args.force:
        record["send_result"] = {"ok": True, "skipped": True, "reason": "dedupe_key_already_sent"}
        append_audit(args.audit, record)
        return {"ok": True, **plan_dict, "send_result": record["send_result"]}
    if not args.send:
        record["send_result"] = {"ok": True, "skipped": True, "reason": "dry_run"}
        append_audit(args.audit, record)
        return {"ok": True, **plan_dict, "send_result": record["send_result"]}
    resolved_session = resolve_session_key(args.session, data_dir=args.data_dir, project=args.project)
    state_before = inspect_gateway_state(data_dir=args.data_dir, project=args.project, session=args.session)
    result = send_message(
        plan.message,
        cc_bin=args.cc_bin,
        data_dir=args.data_dir,
        project=args.project,
        session=resolved_session,
        timeout=args.timeout,
    )
    recovery: dict[str, Any] | None = None
    failure_kind = classify_send_failure(result)
    if not result["ok"] and args.recover_on_failure and failure_kind in {
        "weixin_ret_minus_2",
        "missing_context_token",
        "no_active_session",
        "internal_api_unavailable",
        "timeout",
    }:
        restart = restart_cc_connect(
            cc_bin=args.cc_bin,
            config=args.config,
            data_dir=args.data_dir,
            timeout=args.recovery_timeout,
        )
        retry_result: dict[str, Any] | None = None
        if restart.get("ok"):
            retry_result = send_message(
                plan.message,
                cc_bin=args.cc_bin,
                data_dir=args.data_dir,
                project=args.project,
                session=resolve_session_key(args.session, data_dir=args.data_dir, project=args.project),
                timeout=args.timeout,
            )
            result = retry_result
        recovery = {
            "trigger": failure_kind,
            "state_before": state_before,
            "restart": restart,
            "retry": retry_result,
            "state_after": inspect_gateway_state(data_dir=args.data_dir, project=args.project, session=args.session),
        }
        record["recovery"] = recovery
        failure_kind = classify_send_failure(result)
    if not result["ok"]:
        record["recovery_packet"] = write_recovery_packet(
            directory=args.recovery_dir,
            task_id=plan.task_id,
            failure_kind=failure_kind,
            send_result=result,
            state=inspect_gateway_state(data_dir=args.data_dir, project=args.project, session=args.session),
            recovery=recovery,
        )
    record["send_result"] = result
    if result["ok"]:
        dedupe.setdefault("sent", {})[plan.dedupe_key] = {
            "timestamp": record["timestamp"],
            "packet_path": plan.packet_path,
            "task_id": plan.task_id,
            "packet_type": plan.packet_type,
        }
        save_dedupe(args.dedupe, dedupe)
    append_audit(args.audit, record)
    return {**plan_dict, "ok": result["ok"], "send_result": result}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    notify_parser = subparsers.add_parser("notify")
    notify_parser.add_argument("--packet", required=True, type=Path)
    notify_parser.add_argument("--project", default=DEFAULT_PROJECT)
    notify_parser.add_argument("--session", default="")
    notify_parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    notify_parser.add_argument("--cc-bin", type=Path, default=DEFAULT_BIN)
    notify_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    notify_parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    notify_parser.add_argument("--dedupe", type=Path, default=DEFAULT_DEDUPE)
    notify_parser.add_argument("--recovery-dir", type=Path, default=DEFAULT_RECOVERY_DIR)
    notify_parser.add_argument("--max-chars", type=int, default=1500)
    notify_parser.add_argument("--timeout", type=int, default=60)
    notify_parser.add_argument("--recovery-timeout", type=int, default=20)
    notify_parser.add_argument("--send", action="store_true")
    notify_parser.add_argument("--force", action="store_true")
    notify_parser.add_argument("--recover-on-failure", action=argparse.BooleanOptionalAction, default=True)
    notify_parser.add_argument("--omit-message-in-audit", action="store_true")
    notify_parser.set_defaults(func=notify)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
