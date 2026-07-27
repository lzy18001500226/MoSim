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


def test_g5_queue_keeps_46_current_review_scope_inside_the_48_entry_ledger() -> None:
    module = load_module()
    queue = module.build_queue()

    assert module.validate_queue(queue) == []
    assert queue["summary"]["active_top_level_entry_count"] == 48
    assert queue["summary"]["current_mworks_review_scope_count"] == 46
    assert queue["summary"]["pending_live_internal_review_count"] == 46
    assert queue["summary"]["planned_profile_no_live_review_count"] == 1
    assert queue["summary"]["pending_mworks_equivalent_core_count"] == 1


def test_g5_queue_keeps_wrappers_and_blockers_honest() -> None:
    module = load_module()
    queue = module.build_queue()
    rows = {row["scheme_id"]: row for row in queue["schemes"]}

    assert rows["px4ctrl"]["review_disposition"] == "pending_mworks_equivalent_core"
    assert rows["pid_awff_linear_eso"]["review_disposition"] == "planned_profile_no_live_review"
    assert "mu_synthesis" not in rows
    assert "neural_smc" not in rows
    assert rows["fixed_awff_pid"]["review_target_kind"] == "native_flat_awff_graphical_controller_core"
    assert rows["fixed_awff_pid"]["review_target"]["model_file"].endswith(
        "AWFF_FullControllerFlatGraphical_Sysblock.mo"
    )
    assert rows["fixed_awff_pid"]["wrapper_static_indicators"]["model_file"].endswith("FixedAwffPid.mo")
    assert rows["fixed_awff_pid"]["source_wrapper_static_indicators"]["model_file"].endswith("Example1AWFFSysblockClosedLoop.mo")
