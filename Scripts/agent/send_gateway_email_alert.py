#!/usr/bin/env python3
"""Send opt-in MoSim task or gateway alert email via SMTP.

Secrets are read only from environment variables. Do not put SMTP passwords or
QQ authorization codes in project files, command arguments, or chat messages.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import smtplib
import ssl
import sys
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(os.environ.get("MOSIM_EMAIL_ALERT_ROOT") or ROOT / "Results" / "coagent_gateway" / "email").expanduser()
DEFAULT_TO = "1062771286@qq.com"
DEFAULT_HOST = "smtp.qq.com"
DEFAULT_PORT = 465
DEFAULT_COOLDOWN_MINUTES = 240
TERMINAL_TASK_STATUSES = frozenset({"blocked", "complete", "completed"})
WIN_ENV_SOURCES = (
    ("windows_user_env", "HKEY_CURRENT_USER\\Environment"),
    (
        "windows_machine_env",
        "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
    ),
)


def now_local() -> datetime:
    return datetime.now().astimezone()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def read_windows_env(name: str) -> tuple[str, str]:
    if not sys.platform.startswith("win"):
        return "", ""
    try:
        import winreg
    except ImportError:
        return "", ""
    for source, key_path in WIN_ENV_SOURCES:
        hive_name, subkey = key_path.split("\\", 1)
        hive = winreg.HKEY_CURRENT_USER if hive_name == "HKEY_CURRENT_USER" else winreg.HKEY_LOCAL_MACHINE
        try:
            with winreg.OpenKey(hive, subkey) as key:
                value, _ = winreg.QueryValueEx(key, name)
        except OSError:
            continue
        if isinstance(value, str) and value:
            return value, source
    return "", ""


def get_config_value(name: str, default: str = "") -> tuple[str, str]:
    value = os.environ.get(name, "")
    if value:
        return value, "process_env"
    value, source = read_windows_env(name)
    if value:
        return value, source
    return default, "default" if default else ""


def env_config() -> dict[str, Any]:
    host, host_source = get_config_value("MOSIM_ALERT_SMTP_HOST", DEFAULT_HOST)
    port_text, port_source = get_config_value("MOSIM_ALERT_SMTP_PORT", str(DEFAULT_PORT))
    from_addr, from_source = get_config_value("MOSIM_ALERT_EMAIL_FROM")
    password, password_source = get_config_value("MOSIM_ALERT_EMAIL_PASSWORD")
    to_addr, to_source = get_config_value("MOSIM_ALERT_EMAIL_TO", DEFAULT_TO)
    try:
        port = int(port_text)
    except ValueError:
        port = DEFAULT_PORT
        port_source = "default_invalid_env"
    return {
        "host": host,
        "host_source": host_source,
        "port": port,
        "port_source": port_source,
        "from_addr": from_addr,
        "from_source": from_source,
        "password": password,
        "password_source": password_source,
        "password_present": bool(password),
        "to_addr": to_addr,
        "to_source": to_source,
    }


def missing_config(config: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    if not config["from_addr"]:
        missing.append("MOSIM_ALERT_EMAIL_FROM")
    if not config["password_present"]:
        missing.append("MOSIM_ALERT_EMAIL_PASSWORD")
    if not config["to_addr"]:
        missing.append("MOSIM_ALERT_EMAIL_TO")
    return missing


def cooldown_allows(key: str, cooldown_minutes: int) -> tuple[bool, str]:
    if cooldown_minutes <= 0:
        return True, "cooldown_disabled"
    state_path = OUT_DIR / "email_alert_cooldown.json"
    state = load_json(state_path)
    last_text = str(state.get(key, ""))
    if last_text:
        try:
            last = datetime.fromisoformat(last_text)
        except ValueError:
            last = None
        if last and now_local() - last < timedelta(minutes=cooldown_minutes):
            return False, f"cooldown_active_until={(last + timedelta(minutes=cooldown_minutes)).isoformat(timespec='seconds')}"
    state[key] = now_local().isoformat(timespec="seconds")
    write_json(state_path, state)
    return True, "cooldown_passed"


def send_email(subject: str, body: str, config: dict[str, Any], timeout: int) -> dict[str, Any]:
    message = EmailMessage()
    message["From"] = str(config["from_addr"])
    message["To"] = str(config["to_addr"])
    message["Subject"] = subject
    message_id = make_msgid(domain="mosim.local")
    message["Message-ID"] = message_id
    message.set_content(body)
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(str(config["host"]), int(config["port"]), timeout=timeout, context=context) as smtp:
            smtp.login(str(config["from_addr"]), str(config["password"]))
            refused = smtp.send_message(message)
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "message_id": message_id}
    return {"ok": True, "message_id": message_id, "refused_recipients": refused}


def status_label(value: str) -> str:
    labels = {
        "blocked": "已阻塞",
        "complete": "已完成",
        "completed": "已完成",
        "review_required": "等待审核",
        "unhealthy": "异常",
        "healthy": "正常",
    }
    return labels.get(value.lower(), value or "未知")


def display_path(value: str | Path) -> str:
    path = Path(value)
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except (OSError, ValueError):
        return str(path).replace("\\", "/")


def is_task_status(status_path: Path) -> bool:
    return bool(str(load_json(status_path).get("task") or "").strip())


def is_terminal_task_status(status_path: Path) -> bool:
    status = str(load_json(status_path).get("status") or "").strip().lower()
    return status in TERMINAL_TASK_STATUSES


def task_delivery_key(status_path: Path) -> str:
    payload = load_json(status_path)
    status = str(payload.get("status") or "").strip().lower()
    conversation_id = str(payload.get("conversation_id") or "").strip()
    if conversation_id:
        return f"conversation:{conversation_id}|{status}"
    try:
        identity = str(status_path.resolve())
    except OSError:
        identity = str(status_path)
    return f"{identity}|{status}"


def claim_task_delivery(key: str) -> tuple[bool, Path, dict[str, Any]]:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    claim_path = OUT_DIR / "task_delivery" / f"{digest}.json"
    claim = {"key": key, "state": "claiming", "claimed_at": now_local().isoformat(timespec="seconds")}
    claim_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with claim_path.open("x", encoding="utf-8") as handle:
            json.dump(claim, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
    except FileExistsError:
        return False, claim_path, load_json(claim_path)
    return True, claim_path, claim


def complete_task_delivery(claim_path: Path, key: str, result: dict[str, Any]) -> None:
    write_json(
        claim_path,
        {
            "key": key,
            "state": "sent",
            "sent_at": now_local().isoformat(timespec="seconds"),
            "message_id": str(result.get("message_id") or ""),
        },
    )


def release_task_delivery(claim_path: Path) -> None:
    try:
        claim_path.unlink()
    except FileNotFoundError:
        pass


def body_from_status(status_path: Path) -> tuple[str, str, str]:
    status = load_json(status_path)
    failure_kind = str(status.get("failure_kind") or "gateway_alert")
    status_text = str(status.get("status") or "unknown")
    minimal_action = str(status.get("minimal_user_action") or "")
    latest_snapshot = str(status.get("latest_snapshot") or status_path)
    task = str(status.get("task") or "").strip()
    observed_error = str(status.get("observed_error") or "").strip()
    is_task = bool(task)
    normalized_status = status_text.lower()
    if is_task:
        subject_label = {
            "blocked": "任务已阻塞",
            "complete": "任务已完成",
            "completed": "任务已完成",
        }.get(normalized_status, "任务通知")
    else:
        subject_label = "网关告警"
    detail_label = "原因" if normalized_status == "blocked" or not is_task else "摘要"
    subject = f"MoSim {subject_label}：{task or failure_kind}"
    body = "\n".join(
        [
            f"MoSim {'任务通知' if is_task else '网关告警'}",
            "",
            f"状态：{status_label(status_text)}",
            *( [f"任务：{task}"] if task else [] ),
            f"{detail_label}：{observed_error or failure_kind}",
            *( [f"处理：{minimal_action}"] if minimal_action else [] ),
            f"证据：{display_path(latest_snapshot)}",
            f"时间：{now_local().isoformat(timespec='seconds')}",
        ]
    )
    default_key = f"task:{task}:{failure_kind}" if is_task else f"gateway:{failure_kind}"
    return subject, body, default_key


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status-json", type=Path, help="task or gateway status JSON to summarize")
    notification_kind = parser.add_mutually_exclusive_group()
    notification_kind.add_argument(
        "--task-notification",
        action="store_true",
        help="allow delivery for a task status JSON after the current user explicitly requested notification",
    )
    notification_kind.add_argument(
        "--incident-alert",
        action="store_true",
        help="allow delivery for an automated gateway or watchdog incident",
    )
    parser.add_argument("--subject", default="")
    parser.add_argument("--body", default="")
    parser.add_argument("--cooldown-key", default="")
    parser.add_argument("--cooldown-minutes", type=int, default=DEFAULT_COOLDOWN_MINUTES)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    task_status = bool(args.status_json and is_task_status(args.status_json))
    conversation_id = str(load_json(args.status_json).get("conversation_id") or "").strip() if args.status_json else ""
    if args.status_json:
        subject, body, default_key = body_from_status(args.status_json)
    else:
        subject = args.subject or "MoSim gateway alert"
        body = args.body or "MoSim gateway alert"
        default_key = subject
    key = args.cooldown_key or default_key
    config = env_config()
    terminal_task_status = bool(args.status_json and is_terminal_task_status(args.status_json))
    stamp = now_local().strftime("%Y%m%d_%H%M%S_%f")
    audit_path = OUT_DIR / f"email_alert_{stamp}.json"

    record: dict[str, Any] = {
        "timestamp": now_local().isoformat(timespec="seconds"),
        "status_json": str(args.status_json) if args.status_json else "",
        "to": config["to_addr"],
        "from_configured": bool(config["from_addr"]),
        "password_configured": bool(config["password_present"]),
        "recipient_explicit": config["to_source"] != "default",
        "recipient_warning": "using_default_recipient" if config["to_source"] == "default" else "",
        "config_sources": {
            "host": config["host_source"],
            "port": config["port_source"],
            "from": config["from_source"],
            "password": config["password_source"],
            "to": config["to_source"],
        },
        "host": config["host"],
        "port": config["port"],
        "cooldown_key": key,
        "cooldown_allowed": None,
        "cooldown_reason": "not_checked",
        "task_status": task_status,
        "conversation_id": conversation_id,
        "terminal_task_status": terminal_task_status,
        "task_notification_opt_in": args.task_notification,
        "incident_alert_opt_in": args.incident_alert,
        "dry_run": args.dry_run,
    }

    if args.task_notification and not task_status:
        record.update({"ok": True, "skipped": True, "reason": "task_notification_requires_task_status_json"})
        write_json(audit_path, record)
        print(json.dumps({"ok": True, "path": str(audit_path), "skipped": True, "reason": record["reason"]}, ensure_ascii=False))
        return 0
    if args.task_notification and not terminal_task_status:
        record.update({"ok": True, "skipped": True, "reason": "task_notification_requires_terminal_status"})
        write_json(audit_path, record)
        print(json.dumps({"ok": True, "path": str(audit_path), "skipped": True, "reason": record["reason"]}, ensure_ascii=False))
        return 0
    if task_status and not args.task_notification:
        record.update({"ok": True, "skipped": True, "reason": "task_notification_requires_explicit_opt_in"})
        write_json(audit_path, record)
        print(json.dumps({"ok": True, "path": str(audit_path), "skipped": True, "reason": record["reason"]}, ensure_ascii=False))
        return 0
    if not args.task_notification and not args.incident_alert:
        record.update({"ok": True, "skipped": True, "reason": "notification_requires_explicit_opt_in"})
        write_json(audit_path, record)
        print(json.dumps({"ok": True, "path": str(audit_path), "skipped": True, "reason": record["reason"]}, ensure_ascii=False))
        return 0

    if args.dry_run:
        record.update({"ok": True, "skipped": True, "reason": "dry_run"})
        write_json(audit_path, record)
        print(json.dumps({"ok": True, "path": str(audit_path), "skipped": True, "reason": "dry_run"}, ensure_ascii=False))
        return 0

    missing = missing_config(config)
    if missing:
        record.update({"ok": False, "skipped": True, "reason": "missing_config", "missing_env": missing})
        write_json(audit_path, record)
        print(json.dumps({"ok": False, "path": str(audit_path), "reason": "missing_config", "missing_env": missing}, ensure_ascii=False))
        return 2

    claim_path: Path | None = None
    if args.task_notification:
        key = task_delivery_key(args.status_json)
        claimed, claim_path, existing_claim = claim_task_delivery(key)
        record.update(
            {
                "task_delivery_key": key,
                "task_delivery_state": str(existing_claim.get("state") or ""),
                "cooldown_key": "",
                "cooldown_reason": "task_delivery_deduplication",
            }
        )
        if not claimed:
            record.update({"ok": True, "skipped": True, "reason": "task_notification_already_claimed_or_sent"})
            write_json(audit_path, record)
            print(json.dumps({"ok": True, "path": str(audit_path), "skipped": True, "reason": record["reason"]}, ensure_ascii=False))
            return 0
    else:
        allowed, cooldown_reason = cooldown_allows(key, args.cooldown_minutes)
        record.update({"cooldown_allowed": allowed, "cooldown_reason": cooldown_reason})
        if not allowed:
            record.update({"ok": True, "skipped": True, "reason": cooldown_reason})
            write_json(audit_path, record)
            print(json.dumps({"ok": True, "path": str(audit_path), "skipped": True, "reason": cooldown_reason}, ensure_ascii=False))
            return 0

    result = send_email(subject, body, config, args.timeout)
    if claim_path:
        if result.get("ok"):
            complete_task_delivery(claim_path, key, result)
        else:
            release_task_delivery(claim_path)
    record.update(result)
    write_json(audit_path, record)
    print(json.dumps({"ok": bool(result.get("ok")), "path": str(audit_path)}, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
