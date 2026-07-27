from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "quality" / "check_g5_graphical_review_packet.py"
QUEUE = ROOT / "Results" / "control_platform" / "g5_graphical_structure_review_20260722" / "G5_GRAPHICAL_REVIEW_QUEUE.json"


def load_module():
    spec = importlib.util.spec_from_file_location("g5_graphical_review_packet", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stale_cascade_packet(queue: dict[str, object]) -> dict[str, object]:
    rows = queue.get("schemes")
    assert isinstance(rows, list)
    planned = next(row for row in rows if isinstance(row, dict) and row.get("scheme_id") == "cascade_pid")
    target = dict(planned["review_target"])
    target["model_sha256"] = "0" * 64
    return {
        "schema": "mosim.g5_graphical_review_packet.v1",
        "scheme_id": "cascade_pid",
        "review_target": target,
        "verdict": "needs_relayout",
        "layout_observations": {
            "is_internal_control_law": True,
            "signal_flow_readable": False,
            "functional_groups_readable": False,
            "wires_traceable": False,
        },
        "live_mworks": {
            "live_mworks_touched": True,
            "will_not_click_activation_login": True,
            "model_check": {"status": "passed", "model_name": target["model_class"]},
        },
        "evidence": {},
        "claim_boundary": {
            "simulation": "not_run",
            "controller_behavior": "not_claimed",
            "code_generation": "not_run",
        },
        "next_action": "Re-review the current normalized model with native window evidence.",
    }


def test_pre_normalization_packet_is_not_accepted_as_current_review_evidence() -> None:
    module = load_module()
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    packet = stale_cascade_packet(queue)

    errors = module.validate_review_packet(packet, queue)
    assert any("model_sha256 differs" in error for error in errors)
    assert packet["verdict"] == "needs_relayout"
    assert packet["claim_boundary"]["simulation"] == "not_run"


def test_layout_passed_accepts_dense_but_verified_internal_topology() -> None:
    module = load_module()
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    dense = copy.deepcopy(stale_cascade_packet(queue))
    dense["verdict"] = "layout_passed"
    dense["layout_observations"].update(
        {
            "signal_flow_readable": True,
            "functional_groups_readable": True,
            "wires_traceable": True,
        }
    )

    errors = module.validate_review_packet(dense, queue)
    assert not any("layout_passed requires" in error for error in errors)


def test_layout_passed_rejects_a_wrapper_or_missing_internal_law() -> None:
    module = load_module()
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    invalid = copy.deepcopy(stale_cascade_packet(queue))
    invalid["verdict"] = "layout_passed"
    invalid["layout_observations"]["is_internal_control_law"] = False

    errors = module.validate_review_packet(invalid, queue)
    assert any("actual internal control-law topology" in error for error in errors)


def test_layout_passed_rejects_unreadable_signal_flow() -> None:
    module = load_module()
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    invalid = copy.deepcopy(stale_cascade_packet(queue))
    invalid["verdict"] = "layout_passed"

    errors = module.validate_review_packet(invalid, queue)
    assert any("readable functional groups and traceable signal wires" in error for error in errors)
