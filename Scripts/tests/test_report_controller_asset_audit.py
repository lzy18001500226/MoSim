from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "quality" / "audit_report_controller_assets.py"


def load_module():
    spec = importlib.util.spec_from_file_location("report_controller_asset_audit", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_report_controller_asset_audit_preserves_asset_and_review_boundaries():
    module = load_module()
    audit = module.build_audit()
    summary = audit["summary"]
    rows = {row["controller"]: row for row in audit["rows"]}

    assert summary["controller_matrix_rows"] == 67
    assert summary["report_asset_pair_count"] == 65
    assert summary["missing_visual_asset_routes"] == ["mu_synthesis", "neural_smc"]
    assert summary["model_duplicate_replacement_count"] == 7
    assert summary["result_duplicate_replacement_count"] == 5
    assert summary["source_classification_counts"] == {
        "atomic_cfunction_wrapper": 17,
        "implementation_blocked": 2,
        "native_graphical_candidate": 47,
        "source_mapping_ambiguous": 1,
    }
    assert summary["source_mapping_ambiguous_routes"] == ["terminal_smc"]
    assert len(summary["atomic_cfunction_wrapper_routes"]) == 17
    assert {
        "mrac",
        "ndi",
        "fopid",
        "pole_placement_luenberger",
    }.issubset(summary["result_title_mismatch_routes"])
    assert rows["official_pid"]["report_use"] == "core_candidate_after_manual_review"
    assert rows["mu_synthesis"]["report_use"] == "blocked_route_not_in_body"
    assert rows["neural_smc"]["report_asset_present"] is False
    assert rows["official_pid"]["graphical_layout_status"].endswith("review_required")
    assert rows["lqr_baseline"]["source_classification"] == "atomic_cfunction_wrapper"
    assert rows["super_twisting_smc"]["source_classification"] == "native_graphical_candidate"
    assert (
        rows["terminal_smc"]["source_classification"]
        == "source_mapping_ambiguous"
    )
    assert (
        rows["mrac"]["result_report_use"]
        == "recapture_required_before_report_result_use"
    )
