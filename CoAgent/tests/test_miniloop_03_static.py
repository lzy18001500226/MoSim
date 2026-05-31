#!/usr/bin/env python3
"""Static test for COAGENT-MINILOOP-03 rollout resume proof."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.doctor.check_miniloop_03 import check


def test_miniloop_03_visible_resume_proof() -> None:
    result = check()
    assert result["ok"] is True
    assert result["state"] == "superseded_not_visible"
    assert result["department"] == "TestOwner"
