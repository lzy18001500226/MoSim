#!/usr/bin/env python3
"""Regression tests for conversation-keyed terminal task notifications."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Scripts" / "hooks" / "task_terminal_email.py"


def load_module():
    spec = importlib.util.spec_from_file_location("task_terminal_email", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def terminal_payload(status: str) -> dict[str, object]:
    return {
        "cwd": str(ROOT),
        "hook_event_name": "PostToolUse",
        "session_id": "conversation-123",
        "turn_id": "assistant-turn",
        "tool_name": "update_goal",
        "tool_input": {"status": status},
        "tool_response": {"goal": {"objective": "修复邮件终态通知", "status": status}},
    }


def test_terminal_goal_emits_one_message_per_conversation_status(monkeypatch, tmp_path):
    module = load_module()
    monkeypatch.setenv("MOSIM_TASK_NOTIFICATION_ROOT", str(tmp_path / "notifications"))
    commands = []

    def fake_run(command, **_kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0, stdout='{"ok": true, "path": "audit.json"}\n', stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    blocked = module.emit_terminal_email(terminal_payload("blocked"))
    assert blocked["delivery_state"] == "delivered"
    assert "--task-notification" in commands[0]
    status_path = Path(blocked["status_path"])
    status = json.loads(status_path.read_text(encoding="utf-8"))
    assert status["conversation_id"] == "conversation-123"
    assert status["status"] == "blocked"
    assert status["task"] == "修复邮件终态通知"

    duplicate_blocked = module.emit_terminal_email(terminal_payload("blocked"))
    assert duplicate_blocked["reason"] == "already_delivered"
    assert len(commands) == 1

    completed = module.emit_terminal_email(terminal_payload("complete"))
    assert completed["delivery_state"] == "delivered"
    assert len(commands) == 2
    completed_status = json.loads(Path(completed["status_path"]).read_text(encoding="utf-8"))
    assert completed_status["status"] == "completed"


def test_terminal_email_ignores_nonterminal_goal_states(monkeypatch, tmp_path):
    module = load_module()
    monkeypatch.setenv("MOSIM_TASK_NOTIFICATION_ROOT", str(tmp_path / "notifications"))
    calls = []
    monkeypatch.setattr(module.subprocess, "run", lambda *args, **kwargs: calls.append((args, kwargs)))

    for status in ("active", "review_required"):
        result = module.emit_terminal_email(terminal_payload(status))
        assert result["attempted"] is False
        assert result["reason"] == "missing_conversation_goal_or_terminal_status"
    assert calls == []
    assert not (tmp_path / "notifications").exists()


def test_hook_routes_update_goal_to_terminal_notifier(monkeypatch, tmp_path):
    hook_path = ROOT / "Scripts" / "hooks" / "codex_native_hook.py"
    monkeypatch.syspath_prepend(str(hook_path.parent))
    spec = importlib.util.spec_from_file_location("mosim_terminal_hook", hook_path)
    assert spec and spec.loader
    hook = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook)
    monkeypatch.setenv("MOSIM_CONTEXT_PACK_ROOT", str(tmp_path / "context"))
    received = []
    monkeypatch.setattr(hook, "emit_terminal_email", lambda payload: received.append(payload))

    hook._posttool(terminal_payload("completed"))

    assert len(received) == 1
    assert received[0]["tool_name"] == "update_goal"


def test_native_hook_subprocess_invokes_sender_dry_run(tmp_path):
    hook = ROOT / "Scripts" / "hooks" / "codex_native_hook.py"
    environment = dict(os.environ)
    environment["MOSIM_CONTEXT_PACK_ROOT"] = str(tmp_path / "context")
    environment["MOSIM_TASK_NOTIFICATION_ROOT"] = str(tmp_path / "notifications")
    environment["MOSIM_EMAIL_ALERT_ROOT"] = str(tmp_path / "email_audits")
    environment["MOSIM_TASK_NOTIFICATION_DRY_RUN"] = "1"
    payload = json.dumps(terminal_payload("blocked"), ensure_ascii=False)

    completed = subprocess.run(
        [sys.executable, str(hook)],
        cwd=ROOT,
        input=payload,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
        check=False,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr
    status_path = tmp_path / "notifications" / "conversation-123" / "blocked.json"
    delivery_path = tmp_path / "notifications" / "conversation-123" / "blocked.delivery.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    delivery = json.loads(delivery_path.read_text(encoding="utf-8"))
    assert status["conversation_id"] == "conversation-123"
    assert status["status"] == "blocked"
    assert delivery["sender"]["reason"] == "dry_run"
