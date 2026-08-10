from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "sunray" / "analyze_fastlio_chain_offline.py"
    spec = importlib.util.spec_from_file_location("analyze_fastlio_chain_offline", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["analyze_fastlio_chain_offline"] = module
    spec.loader.exec_module(module)
    return module


def current_checks(**overrides):
    checks = {
        "external_odom_valid_last": True,
        "armed_fusion_sample_count": 100,
        "armed_fusion_success_seen": True,
        "armed_fusion_success_last": True,
        "armed_fusion_success_ratio": 1.0,
        "negative_header_gaps": {"fastlio_aligned_odom": 0},
    }
    checks.update(overrides)
    return checks


def current_goal3(**overrides):
    goal3 = {
        "status": "passed",
        "gate_pass": True,
        "checks": current_checks(),
        "comparisons": {"aligned_vs_truth_position_m": {"p95": 0.04}},
        "thresholds": {
            "min_armed_fusion_success_ratio": 0.99,
            "max_aligned_truth_position_p95_m": 0.15,
        },
    }
    goal3.update(overrides)
    return goal3


def test_goal3_contract_marks_old_observed_once_artifact_incomplete():
    module = load_module()
    legacy = {
        "status": "passed",
        "gate_pass": True,
        "checks": {
            "external_odom_valid_last": True,
            "fusion_success_seen": True,
            "fusion_success_ratio": 0.45,
            "fusion_success_last": False,
            "negative_header_gaps": {"fastlio_aligned_odom": 0},
        },
        "comparisons": {"aligned_vs_truth_position_m": {"p95": 0.04}},
    }

    summary = module.goal3_contract_summary(legacy)

    assert summary["status"] == "incomplete_legacy_contract"
    assert summary["current_contract_pass"] is False
    assert "armed_fusion_success_ratio" in summary["reason"]


def test_goal3_contract_accepts_only_a_current_continuous_fusion_pass():
    module = load_module()

    summary = module.goal3_contract_summary(current_goal3())

    assert summary["status"] == "verified_passed"
    assert summary["current_contract_pass"] is True


def test_goal3_contract_rejects_current_record_when_fusion_is_lost_while_armed():
    module = load_module()
    goal3 = current_goal3(
        checks=current_checks(
            armed_fusion_success_last=False,
            armed_fusion_success_ratio=0.45,
        )
    )

    summary = module.goal3_contract_summary(goal3)

    assert summary["status"] == "blocked"
    assert summary["current_contract_pass"] is False
    assert summary["evaluation"]["armed_fusion_success_last"] is False
