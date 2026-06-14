from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_final_submission_refresh_order.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_final_submission_refresh_order", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_final_submission_refresh_order.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checker(output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--output-json",
            str((output_dir / "refresh_order.json").relative_to(ROOT)),
            "--output-md",
            str((output_dir / "refresh_order.md").relative_to(ROOT)),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_refresh_order_passes(tmp_path: Path) -> None:
    completed = run_checker(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["summary"]["node_count"] == 50
    assert report["summary"]["generates_final_outputs"] is False
    assert "Do not run source_edit_reviewer_summary before source_edit_application_plan." in report["serial_barriers"]
    assert "Do not run source_edit_application_audit_checklist before source_edit_reviewer_summary." in report[
        "serial_barriers"
    ]
    assert "Do not run source_output_readiness before source_edit_application_plan." in report["serial_barriers"]
    assert "Do not run human_action_checklist before dashboard." in report["serial_barriers"]
    assert "Do not run final_submission_reviewer_action_map before human_action_checklist." in report[
        "serial_barriers"
    ]
    assert "Do not run final_submission_human_review_decision_packet before reviewer_action_map." in report[
        "serial_barriers"
    ]
    assert "Do not run final_submission_human_review_guide before human_review_decision_packet." in report[
        "serial_barriers"
    ]
    assert "Do not run final_submission_static_audit_index before readiness_chain and refresh_order." in report[
        "serial_barriers"
    ]
    assert "Do not run final_submission_blocked_gate_triage_map before final_submission_static_audit_index." in report[
        "serial_barriers"
    ]
    assert (
        "Do not run final_submission_human_decision_diff_template before final_submission_blocked_gate_triage_map."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_reviewer_quickstart before final_submission_human_decision_diff_template."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_review_progress_snapshot before final_submission_reviewer_quickstart."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_post_review_rerun_matrix before final_submission_review_progress_snapshot."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_manual_review_answer_sheet before final_submission_post_review_rerun_matrix."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_answer_sheet_decision_consistency before final_submission_manual_review_answer_sheet."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_review_artifact_bundle_index before final_submission_answer_sheet_decision_consistency."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_reviewer_handoff_note before final_submission_review_artifact_bundle_index."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_manual_review_closure_checklist before final_submission_reviewer_handoff_note."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_post_review_state_transition_plan before final_submission_manual_review_closure_checklist."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_post_review_command_plan_coverage before final_submission_post_review_state_transition_plan."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_review_artifact_dependency_graph before final_submission_post_review_command_plan_coverage."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_review_aid_freshness before final_submission_review_artifact_dependency_graph."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_reviewer_packet_index before final_submission_review_aid_freshness."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_blocker_question_crosswalk before final_submission_reviewer_packet_index."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_post_review_command_grouping_index before final_submission_blocker_question_crosswalk."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_post_review_command_critical_path_index before final_submission_post_review_command_grouping_index."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_post_review_shared_tail_deduplication_note before final_submission_post_review_command_critical_path_index."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_post_review_reviewer_checklist before final_submission_post_review_shared_tail_deduplication_note."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_human_review_execution_gate_summary before final_submission_post_review_reviewer_checklist."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_execution_authorization_blocker_index before final_submission_human_review_execution_gate_summary."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_no_packet_action_escalation_note before final_submission_execution_authorization_blocker_index."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_forbidden_action_guard before final_submission_no_packet_action_escalation_note."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_reviewer_evidence_index before final_submission_forbidden_action_guard."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_reviewer_open_file_checksum_index before final_submission_reviewer_evidence_index."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_execution_blocker_owner_status_digest before final_submission_reviewer_open_file_checksum_index."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_manual_review_shortest_path_note before final_submission_execution_blocker_owner_status_digest."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_open_file_shortest_path_bundle before final_submission_manual_review_shortest_path_note."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_human_review_status_packet_skeleton before final_submission_open_file_shortest_path_bundle."
        in report["serial_barriers"]
    )
    assert (
        "Do not run final_submission_status_packet_dependency_summary before final_submission_human_review_status_packet_skeleton."
        in report["serial_barriers"]
    )


def test_rejects_reverse_dependency_order() -> None:
    checker = load_checker()
    nodes = [dict(node) for node in checker.NODES]
    dashboard_index = next(index for index, node in enumerate(nodes) if node["node_id"] == "final_submission_dashboard")
    checklist_index = next(
        index for index, node in enumerate(nodes) if node["node_id"] == "final_submission_human_action_checklist"
    )
    nodes[dashboard_index], nodes[checklist_index] = nodes[checklist_index], nodes[dashboard_index]
    report = checker.validate_order(nodes)
    assert report["ok"] is False
    assert any("appears before dependency" in issue for issue in report["issues"])


def test_rejects_unknown_dependency() -> None:
    checker = load_checker()
    nodes = [dict(node) for node in checker.NODES]
    nodes[0]["after"] = ["missing_node"]
    report = checker.validate_order(nodes)
    assert report["ok"] is False
    assert any("depends on unknown node" in issue for issue in report["issues"])


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_refresh_order_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_refresh_order_passes(temp / "current")
        test_rejects_reverse_dependency_order()
        test_rejects_unknown_dependency()
    finally:
        if temp.exists():
            for item in sorted(temp.glob("**/*"), key=lambda path: len(path.parts), reverse=True):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
            temp.rmdir()
        tmp_root = ROOT / ".tmp"
        if tmp_root.exists() and not any(tmp_root.iterdir()):
            tmp_root.rmdir()
    print("[OK] final submission refresh order tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
