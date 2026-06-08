#!/usr/bin/env python3
"""Focused static tests for the 073 live evidence bundle validator."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "Scripts" / "ros" / "validate_ros2_b1_live_evidence_bundle.py"
EVIDENCE = (
    ROOT
    / "Results"
    / "ros2_runtime"
    / "b1_live_evidence_bundle_checker_static_gate_20260608_073"
)
ACCEPTED_SAMPLE = EVIDENCE / "sample_live_evidence_bundle_candidate.json"
REJECTED_FAKE_TRANSFORM_SAMPLE = EVIDENCE / "sample_rejected_fake_transform_bundle.json"
REJECTED_FORBIDDEN_TOPIC_SAMPLE = EVIDENCE / "sample_rejected_forbidden_topic_bundle.json"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_ros2_b1_live_evidence_bundle", VALIDATOR_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_accepts_future_output_review_bundle_while_blocking_controller_handoff() -> None:
    validator = load_validator()
    summary = validator.validate_bundle(load_json(ACCEPTED_SAMPLE), strict=True)

    assert summary["ok"] is True
    assert summary["classification"] == "accepted_for_future_fastlio_output_review_controller_handoff_blocked"
    assert summary["error_count"] == 0
    boundary = "\n".join(summary["claim_boundary"])
    assert "static/file-only" in boundary
    assert "not live TF/RViz readiness" in boundary
    assert "Controller handoff remains blocked" in boundary


def test_rejects_arbitrary_camera_init_to_map_or_world_grounding() -> None:
    validator = load_validator()
    summary = validator.validate_bundle(load_json(REJECTED_FAKE_TRANSFORM_SAMPLE), strict=True)

    assert summary["ok"] is False
    assert summary["classification"] == "rejected_or_blocked_future_live_evidence_bundle"
    errors = "\n".join(summary["errors"])
    assert "fake/arbitrary/header rename" in errors
    assert "real grounding requires evidence_path" in errors


def test_rejects_forbidden_controller_topics_before_authorized_handoff() -> None:
    validator = load_validator()
    summary = validator.validate_bundle(load_json(REJECTED_FORBIDDEN_TOPIC_SAMPLE), strict=True)

    assert summary["ok"] is False
    errors = "\n".join(summary["errors"])
    assert "/position_cmd" in errors
    assert "published_goal_or_setpoint must be false" in errors


def test_requires_explicit_tf_static_edge_list_even_when_empty() -> None:
    validator = load_validator()
    bundle = load_json(ACCEPTED_SAMPLE)
    bundle = copy.deepcopy(bundle)
    del bundle["tf"]["static_edges"]

    summary = validator.validate_bundle(bundle, strict=True)

    assert summary["ok"] is False
    assert "tf.static_edges must be an explicit list" in "\n".join(summary["errors"])


def test_validator_source_is_static_file_only() -> None:
    source = VALIDATOR_PATH.read_text(encoding="utf-8")
    forbidden_runtime_markers = [
        "import rclpy",
        "import rosbag",
        "subprocess.",
        "os.system",
        "Popen(",
        "run(",
        "rviz2",
        "ros2 launch",
    ]
    for marker in forbidden_runtime_markers:
        assert marker not in source


def main() -> int:
    test_accepts_future_output_review_bundle_while_blocking_controller_handoff()
    test_rejects_arbitrary_camera_init_to_map_or_world_grounding()
    test_rejects_forbidden_controller_topics_before_authorized_handoff()
    test_requires_explicit_tf_static_edge_list_even_when_empty()
    test_validator_source_is_static_file_only()
    print("[OK] 073 live evidence bundle static checker")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
