from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_checker():
    path = ROOT / "Scripts" / "quality" / "check_evidence_map_claim_boundary.py"
    spec = importlib.util.spec_from_file_location("check_evidence_map_claim_boundary", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_evidence_map_claim_boundary.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def base_map() -> dict:
    return {
        "status": "static_audit_only",
        "row_counts": {
            "total_rows": 3,
            "metrics_only_rows_priority_empty": 1,
            "formal_rows_priority_nonempty": 2,
            "formal_pass_rows": 1,
            "formal_needs_iteration_rows": 1,
        },
        "claim_boundary": {
            "not_supported": [
                "Do not treat the priority-empty metrics-only rows as formal acceptance rows.",
                "Do not claim all robustness or fault cases pass; needs_iteration rows are excluded.",
                "Do not claim native Syslab report completion from these rows alone.",
                "Do not claim live MWORKS no-start attach success, ROS2 planner readiness, UE build/runtime success, or final closed-loop product acceptance from this static audit.",
            ],
        },
        "candidate_submission_evidence_rows": [
            {
                "experiment_id": "candidate_run",
                "priority": "P1",
                "quality_status": "pass",
                "notes": "",
                "metrics_file": "Results/candidate.json",
                "claim_family": "optimized_controller",
            }
        ],
        "needs_iteration_exclusions": [
            {
                "experiment_id": "iteration_run",
                "priority": "P1",
                "quality_status": "needs_iteration",
                "exclusion_reason": "quality_status=needs_iteration",
                "metrics_file": "Results/iteration.json",
                "claim_family": "fault_tolerance",
            }
        ],
    }


def test_current_evidence_map_and_design_doc_pass() -> None:
    checker = load_checker()
    report = checker.validate(
        ROOT / "Results/static_audits/mworks_control_evidence_map_20260610/evidence_map.json",
        ROOT / "Docs/Design/08_赛题闭环实现证据矩阵.md",
    )
    assert report["ok"], report
    assert report["row_counts"]["formal_pass_rows"] == 64
    assert report["row_counts"]["formal_needs_iteration_rows"] == 17


def test_rejects_metrics_only_candidate(tmp_path: Path) -> None:
    checker = load_checker()
    tmp_path.mkdir(parents=True, exist_ok=True)
    payload = base_map()
    payload["candidate_submission_evidence_rows"][0]["priority"] = ""
    payload["candidate_submission_evidence_rows"][0]["notes"] = "metrics-only evidence"
    path = tmp_path / "evidence_map.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    report = checker.validate(path)
    assert not report["ok"]
    joined = "\n".join(report["issues"])
    assert "empty priority" in joined
    assert "metrics-only" in joined


def test_rejects_needs_iteration_candidate(tmp_path: Path) -> None:
    checker = load_checker()
    tmp_path.mkdir(parents=True, exist_ok=True)
    payload = base_map()
    payload["candidate_submission_evidence_rows"][0]["quality_status"] = "needs_iteration"
    path = tmp_path / "evidence_map.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    report = checker.validate(path)
    assert not report["ok"]
    assert any("quality_status=pass" in issue for issue in report["issues"])


def test_rejects_missing_static_live_boundary(tmp_path: Path) -> None:
    checker = load_checker()
    tmp_path.mkdir(parents=True, exist_ok=True)
    payload = base_map()
    payload["claim_boundary"]["not_supported"] = ["Do not treat the priority-empty metrics-only rows as formal acceptance rows."]
    path = tmp_path / "evidence_map.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    report = checker.validate(path)
    assert not report["ok"]
    joined = "\n".join(report["issues"])
    assert "ROS2 planner readiness" in joined
    assert "UE build/runtime success" in joined


def main() -> int:
    test_current_evidence_map_and_design_doc_pass()
    temp = ROOT / ".tmp" / "evidence_map_claim_boundary_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_rejects_metrics_only_candidate(temp / "metrics")
        test_rejects_needs_iteration_candidate(temp / "needs")
        test_rejects_missing_static_live_boundary(temp / "boundary")
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
    print("[OK] evidence map claim boundary tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
