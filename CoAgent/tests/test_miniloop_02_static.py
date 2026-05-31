#!/usr/bin/env python3
"""Static test for COAGENT-MINILOOP-02 communication proof."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.doctor.check_miniloop_02 import check


def test_miniloop_02_communication_proof() -> None:
    result = check()
    assert result["ok"] is True
    assert result["state"] == "accepted_with_concerns"
