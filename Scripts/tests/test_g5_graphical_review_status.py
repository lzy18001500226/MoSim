from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "quality" / "build_g5_graphical_review_status.py"


def load_module():
    spec = importlib.util.spec_from_file_location("g5_graphical_review_status", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_g5_status_tracks_current_packets_and_excludes_history_without_promoting_simulation() -> None:
    module = load_module()
    status = module.build_status()

    assert module.validate_status(status) == []
    assert status["summary"]["active_top_level_entry_count"] == 48
    assert status["summary"]["live_review_candidate_count"] == 46
    assert status["summary"]["pending_count"] == 46 - status["summary"]["reviewed_count"]
    assert "does not promote any route to simulation" in status["scope"]
    assert status["historical_packet_archive"]["excluded_from_current_status"] is True
    assert module.CURRENT_REVIEW_ROOT.name == "reviews"
    assert module.HISTORICAL_REVIEW_ROOT != module.CURRENT_REVIEW_ROOT
    assert status["families"]["pid_family"]["candidate_count"] == 9
    assert 0 <= status["families"]["pid_family"]["reviewed_count"] <= 9
