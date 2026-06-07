#!/usr/bin/env python3
"""Tests for sparse gateway email alert configuration handling."""

from __future__ import annotations

import importlib.util
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


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__]))
