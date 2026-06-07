#!/usr/bin/env python3
"""Send sparse MoSim gateway alert email via SMTP.

Secrets are read only from environment variables. Do not put SMTP passwords or
QQ authorization codes in project files, command arguments, or chat messages.
"""

from __future__ import annotations

import argparse
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
OUT_DIR = ROOT / "Results" / "coagent_gateway" / "email"
DEFAULT_TO = "1062771286@qq.com"
DEFAULT_HOST = "smtp.qq.com"
DEFAULT_PORT = 465
DEFAULT_COOLDOWN_MINUTES = 240
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


def body_from_status(status_path: Path) -> tuple[str, str, str]:
    status = load_json(status_path)
    failure_kind = str(status.get("failure_kind") or "gateway_alert")
    status_text = str(status.get("status") or "unknown")
    minimal_action = str(status.get("minimal_user_action") or "")
    latest_snapshot = str(status.get("latest_snapshot") or status_path)
    subject = f"MoSim gateway alert: {failure_kind}"
    body = "\n".join(
        [
            "MoSim gateway alert",
            "",
            f"status: {status_text}",
            f"failure_kind: {failure_kind}",
            f"minimal_action: {minimal_action}",
            f"status_file: {latest_snapshot}",
            f"generated_at: {now_local().isoformat(timespec='seconds')}",
            "",
            "This is a sparse fallback email. Check project files for details.",
        ]
    )
    return subject, body, failure_kind


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status-json", type=Path, help="gateway status JSON to summarize")
    parser.add_argument("--subject", default="")
    parser.add_argument("--body", default="")
    parser.add_argument("--cooldown-key", default="")
    parser.add_argument("--cooldown-minutes", type=int, default=DEFAULT_COOLDOWN_MINUTES)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.status_json:
        subject, body, default_key = body_from_status(args.status_json)
    else:
        subject = args.subject or "MoSim gateway alert"
        body = args.body or "MoSim gateway alert"
        default_key = subject
    key = args.cooldown_key or default_key
    config = env_config()
    stamp = now_local().strftime("%Y%m%d_%H%M%S")
    audit_path = OUT_DIR / f"email_alert_{stamp}.json"

    allowed, cooldown_reason = cooldown_allows(key, args.cooldown_minutes)
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
        "cooldown_allowed": allowed,
        "cooldown_reason": cooldown_reason,
        "dry_run": args.dry_run,
    }

    missing = missing_config(config)
    if missing:
        record.update({"ok": False, "skipped": True, "reason": "missing_config", "missing_env": missing})
        write_json(audit_path, record)
        print(json.dumps({"ok": False, "path": str(audit_path), "reason": "missing_config", "missing_env": missing}, ensure_ascii=False))
        return 2
    if not allowed:
        record.update({"ok": True, "skipped": True, "reason": cooldown_reason})
        write_json(audit_path, record)
        print(json.dumps({"ok": True, "path": str(audit_path), "skipped": True, "reason": cooldown_reason}, ensure_ascii=False))
        return 0
    if args.dry_run:
        record.update({"ok": True, "skipped": True, "reason": "dry_run"})
        write_json(audit_path, record)
        print(json.dumps({"ok": True, "path": str(audit_path), "skipped": True, "reason": "dry_run"}, ensure_ascii=False))
        return 0

    result = send_email(subject, body, config, args.timeout)
    record.update(result)
    write_json(audit_path, record)
    print(json.dumps({"ok": bool(result.get("ok")), "path": str(audit_path)}, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
