"""Send one bounded terminal email per MoSim Codex conversation state."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EMAIL_SCRIPT = ROOT / "Scripts" / "agent" / "send_gateway_email_alert.py"
DEFAULT_ROOT = ROOT / "Results" / "coagent_gateway" / "task_notifications"
TERMINAL_STATUS = {"blocked": "blocked", "complete": "completed", "completed": "completed"}


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _session_id(payload: dict[str, Any]) -> str:
    for key in ("session_id", "sessionId", "thread_id", "threadId"):
        value = _text(payload.get(key)).strip()
        if value:
            return value
    return os.environ.get("CODEX_THREAD_ID", "").strip()


def _goal(payload: dict[str, Any]) -> dict[str, Any]:
    response = _mapping(payload.get("tool_response"))
    structured = _mapping(response.get("structuredContent"))
    for candidate in (response.get("goal"), structured.get("goal"), response, structured, payload.get("tool_input")):
        if isinstance(candidate, dict) and _text(candidate.get("objective")).strip():
            return candidate
    return {}


def _terminal_status(payload: dict[str, Any], goal: dict[str, Any]) -> str:
    for source in (goal, _mapping(payload.get("tool_input"))):
        value = _text(source.get("status")).strip().lower()
        if value in TERMINAL_STATUS:
            return TERMINAL_STATUS[value]
    return ""


def _notification_root() -> Path:
    override = os.environ.get("MOSIM_TASK_NOTIFICATION_ROOT", "").strip()
    return Path(override).expanduser() if override else DEFAULT_ROOT


def _safe_component(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return (cleaned or fallback)[:120]


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _task_label(objective: str) -> str:
    return " ".join(objective.split())[:180] or "未命名任务"


def _status_payload(conversation_id: str, terminal_status: str, objective: str, status_path: Path) -> dict[str, Any]:
    blocked = terminal_status == "blocked"
    return {
        "schema_version": "mosim.codex.task_terminal_notification.v1",
        "conversation_id": conversation_id,
        "status": terminal_status,
        "task": _task_label(objective),
        "failure_kind": "codex_goal_blocked" if blocked else "codex_goal_completed",
        "observed_error": "当前 Codex 对话任务已标记为阻塞。" if blocked else "当前 Codex 对话任务已完成。",
        "minimal_user_action": "请查看当前对话中的阻塞说明。" if blocked else "无需处理。",
        "latest_snapshot": str(status_path),
        "generated_at": _now(),
    }


def _parse_sender_output(text: str) -> dict[str, Any]:
    for line in reversed(text.splitlines()):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return {}


def emit_terminal_email(payload: dict[str, Any]) -> dict[str, Any]:
    """Deliver a terminal Goal status once for the current conversation."""

    if _text(payload.get("tool_name")) != "update_goal":
        return {"attempted": False, "reason": "not_update_goal"}

    conversation_id = _session_id(payload)
    goal = _goal(payload)
    objective = _text(goal.get("objective")).strip()
    terminal_status = _terminal_status(payload, goal)
    if not conversation_id or not objective or not terminal_status:
        return {
            "attempted": False,
            "reason": "missing_conversation_goal_or_terminal_status",
            "conversation_id_present": bool(conversation_id),
            "objective_present": bool(objective),
            "terminal_status": terminal_status,
        }

    directory = _notification_root() / _safe_component(conversation_id, "conversation")
    status_path = directory / f"{terminal_status}.json"
    delivery_path = directory / f"{terminal_status}.delivery.json"
    previous_delivery = _read_json(delivery_path)
    if previous_delivery.get("delivery_state") == "delivered":
        return {
            "attempted": False,
            "reason": "already_delivered",
            "conversation_id": conversation_id,
            "terminal_status": terminal_status,
            "status_path": str(status_path),
        }

    _write_json(status_path, _status_payload(conversation_id, terminal_status, objective, status_path))
    command = [
        sys.executable,
        str(EMAIL_SCRIPT),
        "--status-json",
        str(status_path),
        "--task-notification",
        "--timeout",
        "6",
    ]
    if os.environ.get("MOSIM_TASK_NOTIFICATION_DRY_RUN", "") == "1":
        command.append("--dry-run")
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
        sender = _parse_sender_output(completed.stdout or "")
        delivered = completed.returncode == 0 and bool(sender.get("ok")) and not bool(sender.get("skipped"))
        result: dict[str, Any] = {
            "attempted": True,
            "conversation_id": conversation_id,
            "terminal_status": terminal_status,
            "status_path": str(status_path),
            "returncode": completed.returncode,
            "sender": sender,
            "stderr_tail": (completed.stderr or "")[-1000:],
            "delivery_state": "delivered" if delivered else "not_delivered",
            "generated_at": _now(),
        }
    except Exception as exc:
        result = {
            "attempted": True,
            "conversation_id": conversation_id,
            "terminal_status": terminal_status,
            "status_path": str(status_path),
            "delivery_state": "not_delivered",
            "error": f"{type(exc).__name__}: {exc}",
            "generated_at": _now(),
        }
    _write_json(delivery_path, result)
    return result
