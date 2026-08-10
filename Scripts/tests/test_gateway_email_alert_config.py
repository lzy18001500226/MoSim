#!/usr/bin/env python3
"""Tests for sparse gateway email alert configuration handling."""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "agent" / "send_gateway_email_alert.py"


def load_module():
    spec = importlib.util.spec_from_file_location("send_gateway_email_alert", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_windows_registry_env_fallback(monkeypatch):
    module = load_module()
    fake_values = {
        "MOSIM_ALERT_EMAIL_FROM": "sender@example.com",
        "MOSIM_ALERT_EMAIL_PASSWORD": "configured-value",
        "MOSIM_ALERT_EMAIL_TO": "target@example.com",
    }

    class FakeKey:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def query_value(_key, name):
        if name not in fake_values:
            raise FileNotFoundError(name)
        return fake_values[name], 1

    fake_winreg = types.SimpleNamespace(
        HKEY_CURRENT_USER=object(),
        HKEY_LOCAL_MACHINE=object(),
        OpenKey=lambda hive, subkey: FakeKey(),
        QueryValueEx=query_value,
    )
    monkeypatch.setitem(sys.modules, "winreg", fake_winreg)
    monkeypatch.setattr(module.sys, "platform", "win32")
    for key in fake_values:
        monkeypatch.delenv(key, raising=False)

    config = module.env_config()
    assert config["from_addr"] == "sender@example.com"
    assert config["password"] == "configured-value"
    assert config["to_addr"] == "target@example.com"
    assert config["from_source"] == "windows_user_env"
    assert config["password_source"] == "windows_user_env"
    assert module.missing_config(config) == []


def test_process_env_takes_precedence(monkeypatch):
    module = load_module()
    monkeypatch.setenv("MOSIM_ALERT_EMAIL_FROM", "process@example.com")
    monkeypatch.setenv("MOSIM_ALERT_EMAIL_PASSWORD", "configured-value")
    config = module.env_config()
    assert config["from_addr"] == "process@example.com"
    assert config["password"] == "configured-value"
    assert config["from_source"] == "process_env"
    assert config["password_source"] == "process_env"


def test_send_email_audit_metadata(monkeypatch):
    module = load_module()
    sent = {}

    class FakeSmtp:
        def __init__(self, host, port, timeout, context):
            sent["host"] = host
            sent["port"] = port

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def login(self, from_addr, password):
            sent["from"] = from_addr
            sent["password_seen"] = bool(password)

        def send_message(self, message):
            sent["message_id"] = message["Message-ID"]
            return {}

    monkeypatch.setattr(module.smtplib, "SMTP_SSL", FakeSmtp)
    result = module.send_email(
        "subject",
        "body",
        {
            "host": "smtp.example.com",
            "port": 465,
            "from_addr": "sender@example.com",
            "to_addr": "target@example.com",
            "password": "configured-value",
        },
        timeout=3,
    )
    assert result["ok"] is True
    assert result["message_id"] == sent["message_id"]
    assert result["refused_recipients"] == {}


def test_task_blocker_email_is_chinese_and_concise(tmp_path):
    module = load_module()
    status_path = tmp_path / "CHECKMODEL_BLOCKER.json"
    status_path.write_text(
        json.dumps(
            {
                "status": "blocked",
                "task": "OfficialPIDGraphicalRotorAdapter mapper port repair",
                "failure_kind": "mworks_compiler_internal_error_100",
                "observed_error": "MWORKS 编译器内部错误 (100)",
                "minimal_user_action": "恢复编译器状态后重新运行 CheckModel。",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    subject, body, key = module.body_from_status(status_path)

    assert subject.startswith("MoSim 任务已阻塞：")
    assert "状态：已阻塞" in body
    assert "任务：OfficialPIDGraphicalRotorAdapter mapper port repair" in body
    assert "原因：MWORKS 编译器内部错误 (100)" in body
    assert "处理：恢复编译器状态后重新运行 CheckModel。" in body
    assert "sparse fallback" not in body
    assert key == "task:OfficialPIDGraphicalRotorAdapter mapper port repair:mworks_compiler_internal_error_100"


def test_task_status_json_requires_explicit_opt_in(monkeypatch, tmp_path):
    module = load_module()
    status_path = tmp_path / "task_status.json"
    status_path.write_text(json.dumps({"status": "blocked", "task": "邮件通知门禁"}), encoding="utf-8")
    monkeypatch.setattr(module, "OUT_DIR", tmp_path / "email")
    monkeypatch.setattr(module.sys, "argv", [str(SCRIPT), "--status-json", str(status_path), "--incident-alert"])

    assert module.main() == 0
    audits = list((tmp_path / "email").glob("email_alert_*.json"))
    assert len(audits) == 1
    audit = json.loads(audits[0].read_text(encoding="utf-8"))
    assert audit["skipped"] is True
    assert audit["reason"] == "task_notification_requires_explicit_opt_in"
    assert audit["incident_alert_opt_in"] is True
    assert not (tmp_path / "email" / "email_alert_cooldown.json").exists()


def test_freeform_email_requires_explicit_notification_kind(monkeypatch, tmp_path):
    module = load_module()
    monkeypatch.setattr(module, "OUT_DIR", tmp_path / "email")
    monkeypatch.setattr(
        module.sys,
        "argv",
        [str(SCRIPT), "--subject", "任务终态", "--body", "未经授权的普通通知"],
    )

    assert module.main() == 0
    audits = list((tmp_path / "email").glob("email_alert_*.json"))
    assert len(audits) == 1
    audit = json.loads(audits[0].read_text(encoding="utf-8"))
    assert audit["skipped"] is True
    assert audit["reason"] == "notification_requires_explicit_opt_in"
    assert not (tmp_path / "email" / "email_alert_cooldown.json").exists()


def test_incident_alert_can_use_freeform_body(monkeypatch, tmp_path):
    module = load_module()
    monkeypatch.setattr(module, "OUT_DIR", tmp_path / "email")
    monkeypatch.setattr(
        module,
        "env_config",
        lambda: {
            "host": "smtp.example.com",
            "host_source": "test",
            "port": 465,
            "port_source": "test",
            "from_addr": "sender@example.com",
            "from_source": "test",
            "password": "configured-value",
            "password_source": "test",
            "password_present": True,
            "to_addr": "target@example.com",
            "to_source": "test",
        },
    )
    monkeypatch.setattr(
        module.sys,
        "argv",
        [
            str(SCRIPT),
            "--subject",
            "网关异常",
            "--body",
            "事件告警",
            "--incident-alert",
            "--dry-run",
        ],
    )

    assert module.main() == 0
    audit = json.loads(next((tmp_path / "email").glob("email_alert_*.json")).read_text(encoding="utf-8"))
    assert audit["skipped"] is True
    assert audit["reason"] == "dry_run"
    assert audit["incident_alert_opt_in"] is True


def test_gateway_status_requires_incident_alert_opt_in(monkeypatch, tmp_path):
    module = load_module()
    status_path = tmp_path / "gateway_unhealthy_latest.json"
    status_path.write_text(json.dumps({"status": "unhealthy", "failure_kind": "gateway_unreachable"}), encoding="utf-8")
    monkeypatch.setattr(module, "OUT_DIR", tmp_path / "email")
    monkeypatch.setattr(module.sys, "argv", [str(SCRIPT), "--status-json", str(status_path)])

    assert module.main() == 0
    audit = json.loads(next((tmp_path / "email").glob("email_alert_*.json")).read_text(encoding="utf-8"))
    assert audit["skipped"] is True
    assert audit["reason"] == "notification_requires_explicit_opt_in"
    assert not (tmp_path / "email" / "email_alert_cooldown.json").exists()


def test_task_notification_requires_terminal_status_json(monkeypatch, tmp_path):
    module = load_module()
    status_path = tmp_path / "task_running.json"
    status_path.write_text(json.dumps({"status": "running", "task": "未结束任务"}), encoding="utf-8")
    monkeypatch.setattr(module, "OUT_DIR", tmp_path / "email")
    monkeypatch.setattr(
        module.sys,
        "argv",
        [str(SCRIPT), "--status-json", str(status_path), "--task-notification", "--dry-run"],
    )

    assert module.main() == 0
    audit = json.loads(next((tmp_path / "email").glob("email_alert_*.json")).read_text(encoding="utf-8"))
    assert audit["skipped"] is True
    assert audit["reason"] == "task_notification_requires_terminal_status"
    assert not (tmp_path / "email" / "task_delivery").exists()


def test_task_notification_rejects_freeform_body(monkeypatch, tmp_path):
    module = load_module()
    monkeypatch.setattr(module, "OUT_DIR", tmp_path / "email")
    monkeypatch.setattr(
        module.sys,
        "argv",
        [str(SCRIPT), "--subject", "任务终态", "--body", "不能绕过状态文件", "--task-notification", "--dry-run"],
    )

    assert module.main() == 0
    audit = json.loads(next((tmp_path / "email").glob("email_alert_*.json")).read_text(encoding="utf-8"))
    assert audit["skipped"] is True
    assert audit["reason"] == "task_notification_requires_task_status_json"


def test_completed_task_notification_uses_completion_format(monkeypatch, tmp_path):
    module = load_module()
    status_path = tmp_path / "task_completed.json"
    status_path.write_text(
        json.dumps(
            {
                "status": "completed",
                "task": "邮件发送链路验证",
                "observed_error": "全部验证通过",
                "minimal_user_action": "无需处理。",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "OUT_DIR", tmp_path / "email")
    monkeypatch.setattr(
        module.sys,
        "argv",
        [str(SCRIPT), "--status-json", str(status_path), "--task-notification", "--dry-run"],
    )

    subject, body, _ = module.body_from_status(status_path)
    assert subject == "MoSim 任务已完成：邮件发送链路验证"
    assert "状态：已完成" in body
    assert "摘要：全部验证通过" in body

    assert module.main() == 0
    audit = json.loads(next((tmp_path / "email").glob("email_alert_*.json")).read_text(encoding="utf-8"))
    assert audit["reason"] == "dry_run"
    assert audit["terminal_task_status"] is True


def test_conversation_id_is_the_task_delivery_deduplication_key(tmp_path):
    module = load_module()
    first = tmp_path / "blocked_first.json"
    second = tmp_path / "blocked_second.json"
    completed = tmp_path / "completed.json"
    for path, status in ((first, "blocked"), (second, "blocked"), (completed, "completed")):
        path.write_text(
            json.dumps({"status": status, "task": "同一会话任务", "conversation_id": "conversation-123"}),
            encoding="utf-8",
        )

    assert module.task_delivery_key(first) == "conversation:conversation-123|blocked"
    assert module.task_delivery_key(second) == module.task_delivery_key(first)
    assert module.task_delivery_key(completed) == "conversation:conversation-123|completed"


def test_task_notification_delivers_rendered_terminal_email_once(monkeypatch, tmp_path):
    module = load_module()
    status_path = tmp_path / "CHECKMODEL_BLOCKER.json"
    status_path.write_text(
        json.dumps(
            {
                "status": "blocked",
                "task": "图形适配器端口修复",
                "failure_kind": "mworks_compiler_internal_error_100",
                "observed_error": "MWORKS 编译器内部错误 (100)",
                "minimal_user_action": "恢复编译器状态后重新运行 CheckModel。",
                "latest_snapshot": str(status_path),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "OUT_DIR", tmp_path / "email")
    monkeypatch.setattr(
        module,
        "env_config",
        lambda: {
            "host": "smtp.example.com",
            "host_source": "test",
            "port": 465,
            "port_source": "test",
            "from_addr": "sender@example.com",
            "from_source": "test",
            "password": "configured-value",
            "password_source": "test",
            "password_present": True,
            "to_addr": "target@example.com",
            "to_source": "test",
        },
    )
    messages = []

    class FakeSmtp:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def login(self, _from_addr, _password):
            pass

        def send_message(self, message):
            messages.append(message)
            return {}

    monkeypatch.setattr(module.smtplib, "SMTP_SSL", FakeSmtp)
    argv = [str(SCRIPT), "--status-json", str(status_path), "--task-notification"]
    monkeypatch.setattr(module.sys, "argv", argv)

    assert module.main() == 0
    assert len(messages) == 1
    assert messages[0]["Subject"] == "MoSim 任务已阻塞：图形适配器端口修复"
    body = messages[0].get_content()
    assert "状态：已阻塞" in body
    assert "原因：MWORKS 编译器内部错误 (100)" in body
    assert "处理：恢复编译器状态后重新运行 CheckModel。" in body
    assert "This is a sparse fallback email" not in body

    assert module.main() == 0
    assert len(messages) == 1
    audits = [json.loads(path.read_text(encoding="utf-8")) for path in (tmp_path / "email").glob("email_alert_*.json")]
    assert any(audit.get("reason") == "task_notification_already_claimed_or_sent" for audit in audits)


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__]))
