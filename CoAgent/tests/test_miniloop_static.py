#!/usr/bin/env python3
"""Static test for the CoAgent minimum closed-loop proof."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.doctor.check_miniloop import check_bundle


def test_miniloop_bundle_is_review_ready() -> None:
    result = check_bundle(ROOT / "Results" / "coagent_miniloop" / "COAGENT-MINILOOP-01")
    assert result["ok"] is True
    assert result["state"] in {"needs_user_review", "approved_with_next_gate"}
