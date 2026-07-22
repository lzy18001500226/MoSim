from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "quality" / "build_g5_graphical_review_queue.py"


def load_module():
    spec = importlib.util.spec_from_file_location("g5_graphical_review_queue", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_g5_queue_keeps_46_current_review_scope_inside_the_49_route_ledger() -> None:
    module = load_module()
    queue = module.build_queue()

    assert module.validate_queue(queue) == []
    assert queue["summary"]["top_level_scheme_count"] == 49
    assert queue["summary"]["current_mworks_review_scope_count"] == 46
    assert queue["summary"]["pending_live_internal_review_count"] == 46
    assert queue["summary"]["blocked_before_live_review_count"] == 2
    assert queue["summary"]["not_applicable_runtime_baseline_count"] == 1


def test_g5_queue_keeps_wrappers_and_blockers_honest() -> None:
    module = load_module()
    queue = module.build_queue()
    rows = {row["scheme_id"]: row for row in queue["schemes"]}

    assert rows["px4ctrl"]["review_disposition"] == "not_applicable_runtime_baseline"
    assert rows["mu_synthesis"]["review_disposition"] == "blocked_before_live_review"
    assert rows["neural_smc"]["review_disposition"] == "blocked_before_live_review"
    assert rows["fixed_awff_pid"]["review_target_kind"] == "internal_controller_referenced_by_whole_aircraft_wrapper"
    assert rows["fixed_awff_pid"]["review_target"]["model_file"].endswith(
        "AWFF_FullControllerEquation_Sysblock.mo"
    )
    assert rows["fixed_awff_pid"]["wrapper_static_indicators"]["model_file"].endswith("FixedAwffPid.mo")
    assert rows["fixed_awff_pid"]["source_wrapper_static_indicators"]["model_file"].endswith("Example1AWFFSysblockClosedLoop.mo")
