#!/usr/bin/env python3
"""Smoke tests for the cc-connect Weixin notification adapter."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.gateway import cc_connect_weixin


def main() -> int:
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        blocker = tmp_root / "blocker.json"
        blocker.write_text(
            json.dumps(
                {
                    "template_type": "blocker_notification",
                    "task_id": "COAGENT-GATEWAY-SMOKE",
                    "severity": "high",
                    "class": "manual_review_required",
                    "dedupe_key": "gateway-smoke-review",
                    "blocked_surface": "CoAgent gateway smoke at Results/agent_packets/blockers/example.json",
                    "human_action_required": "Confirm the dry-run payload shape.",
                    "why_now": "token=SHOULD_NOT_APPEAR base_url=https://secret.example",
                    "evidence_paths": ["CoAgent/tests/test_gateway_weixin.py"],
                    "resume_packet_path": "Results/tmp/resume.md",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        plan = cc_connect_weixin.build_plan(blocker)
        assert plan.ok, plan
        assert plan.packet_type == "blocker_notification"
        assert plan.dedupe_key == "gateway-smoke-review"
        assert "!!! MoSim 需要人工介入 !!!" in plan.message
        assert "Results/agent_packets/blockers/example.json" not in plan.message
        assert "CoAgent/tests/test_gateway_weixin.py" not in plan.message
        assert "详见项目记录" in plan.message
        assert "SHOULD_NOT_APPEAR" not in plan.message
        assert "secret.example" not in plan.message
        assert "<redacted>" in plan.message

        audit = tmp_root / "audit.jsonl"
        dedupe = tmp_root / "dedupe.json"
        dry = cc_connect_weixin.notify(
            argparse.Namespace(
                packet=blocker,
                project="mosim-weixin-smoke",
                session="",
                data_dir=tmp_root / "data",
                cc_bin=tmp_root / "missing-cc-connect",
                config=tmp_root / "config.toml",
                audit=audit,
                dedupe=dedupe,
                recovery_dir=tmp_root / "recovery",
                max_chars=1500,
                timeout=1,
                recovery_timeout=1,
                send=False,
                force=False,
                recover_on_failure=True,
                omit_message_in_audit=False,
            )
        )
        assert dry["ok"], dry
        assert dry["send_result"]["reason"] == "dry_run"
        assert audit.exists()

        unsupported = tmp_root / "unsupported.json"
        unsupported.write_text(
            json.dumps(
                {
                    "template_type": "blocker_notification",
                    "task_id": "COAGENT-GATEWAY-SMOKE",
                    "class": "input_required",
                    "blocked_surface": "low risk question",
                    "human_action_required": "answer later",
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        blocked = cc_connect_weixin.build_plan(unsupported)
        assert not blocked.ok
        assert "not allowed" in blocked.blocked_reason

        review = tmp_root / "review.json"
        review.write_text(
            json.dumps(
                {
                    "template_type": "review_packet",
                    "review_id": "REVIEW-GATEWAY-SMOKE",
                    "task_id": "COAGENT-GATEWAY-SMOKE",
                    "decision": "needs_review",
                    "summary": "review me",
                    "evidence_paths": ["CoAgent/tests/test_gateway_weixin.py"],
                    "risks": ["risk one"],
                    "required_rework": ["none"],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        review_plan = cc_connect_weixin.build_plan(review)
        assert review_plan.ok, review_plan
        assert "需要人工审核" in review_plan.message
        assert "CoAgent/tests/test_gateway_weixin.py" not in review_plan.message

        completion = tmp_root / "completion.json"
        completion.write_text(
            json.dumps(
                {
                    "template_type": "completion_notification",
                    "task_id": "COAGENT-GATEWAY-SMOKE",
                    "canonical_status": "completed",
                    "summary": "completion message smoke",
                    "owner": "ProjectOwner",
                    "evidence_paths": ["CoAgent/tests/test_gateway_weixin.py"],
                    "next_recommended_action": "无需人工处理。",
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        completion_plan = cc_connect_weixin.build_plan(completion)
        assert completion_plan.ok, completion_plan
        assert completion_plan.packet_type == "completion_notification"
        assert "【MoSim 进度】" in completion_plan.message
        assert "completion message smoke" in completion_plan.message
        assert "CoAgent/tests/test_gateway_weixin.py" not in completion_plan.message

        data_dir = tmp_root / "data"
        sessions_dir = data_dir / "sessions"
        sessions_dir.mkdir(parents=True)
        session_file = sessions_dir / "MoSim｜微信通知网关_abc123.json"
        platform_key = "weixin:dm:user@im.wechat"
        session_file.write_text(
            json.dumps(
                {
                    "sessions": {"s1": {"id": "s1", "name": "default"}},
                    "active_session": {platform_key: "s1"},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        assert (
            cc_connect_weixin.resolve_session_key(
                "s1",
                data_dir=data_dir,
                project="MoSim｜微信通知网关",
            )
            == platform_key
        )
        assert (
            cc_connect_weixin.resolve_session_key(
                "MoSim｜微信通知网关",
                data_dir=data_dir,
                project="MoSim｜微信通知网关",
            )
            == platform_key
        )
        assert (
            cc_connect_weixin.resolve_session_key(
                "",
                data_dir=data_dir,
                project="MoSim｜微信通知网关",
            )
            == platform_key
        )
        assert (
            cc_connect_weixin.resolve_session_key(
                str(session_file),
                data_dir=data_dir,
                project="MoSim｜微信通知网关",
            )
            == platform_key
        )
        assert (
            cc_connect_weixin.resolve_session_key(
                platform_key,
                data_dir=data_dir,
                project="MoSim｜微信通知网关",
            )
            == platform_key
        )

        failures = [
            {"ok": False, "timeout": False, "stdout": "", "stderr": "Error: weixin: sendMessage: ret=-2 errcode=0"},
            {"ok": False, "timeout": False, "stdout": "", "stderr": "weixin: missing context_token for peer"},
            {"ok": False, "timeout": False, "stdout": "", "stderr": "Error: no active session found"},
            {"ok": False, "timeout": True, "stdout": "", "stderr": ""},
        ]
        assert [cc_connect_weixin.classify_send_failure(item) for item in failures] == [
            "weixin_ret_minus_2",
            "missing_context_token",
            "no_active_session",
            "timeout",
        ]

        original_send = cc_connect_weixin.send_message
        original_restart = cc_connect_weixin.restart_cc_connect
        try:
            calls = {"send": 0, "restart": 0}

            def fake_send(message, *, cc_bin, data_dir, project, session, timeout):
                calls["send"] += 1
                if calls["send"] == 1:
                    return {
                        "ok": False,
                        "timeout": False,
                        "returncode": 1,
                        "stdout": "",
                        "stderr": "Error: weixin: sendMessage: ret=-2 errcode=0",
                        "command": [],
                    }
                return {
                    "ok": True,
                    "timeout": False,
                    "returncode": 0,
                    "stdout": "Message sent successfully.",
                    "stderr": "",
                    "command": [],
                }

            def fake_restart(**kwargs):
                calls["restart"] += 1
                return {"ok": True, "api_socket_exists": True}

            cc_connect_weixin.send_message = fake_send
            cc_connect_weixin.restart_cc_connect = fake_restart
            ret_minus_2 = cc_connect_weixin.notify(
                argparse.Namespace(
                    packet=blocker,
                    project="MoSim｜微信通知网关",
                    session="s1",
                    data_dir=data_dir,
                    cc_bin=tmp_root / "cc-connect",
                    config=tmp_root / "config.toml",
                    audit=tmp_root / "recover_audit.jsonl",
                    dedupe=tmp_root / "recover_dedupe.json",
                    recovery_dir=tmp_root / "recovery",
                    max_chars=1500,
                    timeout=1,
                    recovery_timeout=1,
                    send=True,
                    force=True,
                    recover_on_failure=True,
                    omit_message_in_audit=True,
                )
            )
            assert not ret_minus_2["ok"], ret_minus_2
            assert calls == {"send": 1, "restart": 0}
            assert ret_minus_2["send_result"]["stderr"].endswith("ret=-2 errcode=0")

            def always_fail(message, *, cc_bin, data_dir, project, session, timeout):
                return {
                    "ok": False,
                    "timeout": False,
                    "returncode": 1,
                    "stdout": "",
                    "stderr": "Error: weixin: sendMessage: ret=-2 errcode=0",
                    "command": [],
                }

            cc_connect_weixin.send_message = always_fail
            failed = cc_connect_weixin.notify(
                argparse.Namespace(
                    packet=blocker,
                    project="MoSim｜微信通知网关",
                    session="s1",
                    data_dir=data_dir,
                    cc_bin=tmp_root / "cc-connect",
                    config=tmp_root / "config.toml",
                    audit=tmp_root / "failed_audit.jsonl",
                    dedupe=tmp_root / "failed_dedupe.json",
                    recovery_dir=tmp_root / "recovery",
                    max_chars=1500,
                    timeout=1,
                    recovery_timeout=1,
                    send=True,
                    force=True,
                    recover_on_failure=True,
                    omit_message_in_audit=True,
                )
            )
            assert not failed["ok"], failed
            recovery_packets = sorted((tmp_root / "recovery").glob("weixin_recovery_required_*.json"))
            assert recovery_packets, "expected recovery packet when retry still fails"
        finally:
            cc_connect_weixin.send_message = original_send
            cc_connect_weixin.restart_cc_connect = original_restart

    print("gateway_weixin_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
