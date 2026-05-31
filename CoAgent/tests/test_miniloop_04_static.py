#!/usr/bin/env python3
"""Static test for COAGENT-MINILOOP-04 candidate visible loop."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.doctor.check_miniloop_04 import check


def test_miniloop_04_candidate_visible_loop() -> None:
    result = check()
    assert result["ok"] is True
    assert result["state"] == "real_tui_thread_synced_awaiting_user_confirmation"
    assert result["thread_id"] == "019e7373-37f4-75e1-9780-e1519a489715"
    assert result["real_tui_thread_id"] == "019e73e5-d97d-75a3-ba72-b52e19d755b3"
