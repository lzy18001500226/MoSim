from __future__ import annotations

from pathlib import Path

from Scripts.ui.audit_qgc_variant_acceptance_matrix import build_matrix


ROOT = Path(__file__).resolve().parents[2]
QGC_RUN = ROOT / "Results" / "runs" / "qgc-20260807-101020-3dd44bf72f"
DIFF_REVIEW = (
    ROOT
    / "Results"
    / "sunray_ros1"
    / "factory_l2_c99_diff_single_and_swarm_review_20260806"
    / "FACTORY_L2_C99_DIFF_SINGLE_AND_SWARM_REVIEW.json"
)


def test_current_matrix_keeps_qgc_and_separate_runtime_evidence_distinct() -> None:
    matrix = build_matrix(qgc_run_dir=QGC_RUN, diff_review_path=DIFF_REVIEW)

    assert matrix["status"] == "blocked"
    variants = {item["variant_id"]: item for item in matrix["variants"]}

    single = variants["qgc_single_graphical_c99"]
    assert single["qgc_publication"]["publication_state"] == "enabled"
    assert single["evidence"]["realtime_transport_status"] == "observed"
    assert single["evidence"]["qgc_visual_evidence"]["status"] == "not_collected"
    assert single["acceptance_status"] == "blocked"

    multi = variants["qgc_three_uav_formation"]
    assert multi["qgc_publication"]["publication_state"] == "disabled"
    assert multi["acceptance_status"] == "not_published"

    diff = variants["qgc_diff_variants"]
    assert diff["external_runtime_evidence"]["review_status"] == "passed"
    assert diff["qgc_publication"]["publication_state"] == "source_present_requires_qgc_audit"
    assert "px4ctrl_graphical_c99_factory_diff_interactive_goal_v1" in diff["qgc_publication"]["operator_profiles"]
    assert diff["acceptance_status"] == "requires_qgc_specific_audit"
