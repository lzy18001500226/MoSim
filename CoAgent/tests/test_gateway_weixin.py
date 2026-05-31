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
                    "blocked_surface": "CoAgent gateway smoke",
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
                max_chars=1500,
                timeout=1,
                send=False,
                force=False,
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
        assert "审核请求" in review_plan.message

    print("gateway_weixin_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
