from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_candidate_submission_manifest.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_candidate_submission_manifest", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_candidate_submission_manifest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checker(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(path)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_candidate_submission_manifest_passes() -> None:
    checker = load_checker()
    report = checker.validate(
        ROOT / "Results/static_audits/submission_evidence_manifest_20260610/candidate_submission_evidence_manifest.json"
    )
    assert report["ok"], report
    assert report["row_count"] >= 10


def test_rejects_needs_iteration_selection(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    source = ROOT / "Results/static_audits/mworks_control_evidence_map_20260610/evidence_map.json"
    source_data = json.loads(source.read_text(encoding="utf-8"))
    bad_row = source_data["needs_iteration_exclusions"][0]
    payload = {
        "status": "review_candidate_not_final_acceptance",
        "source_evidence_map": source.relative_to(ROOT).as_posix(),
        "selection_rule": "test",
        "row_count": 1,
        "global_exclusions": [
            "Not final PMO acceptance.",
            "Does not claim native Syslab report completion.",
            "Does not claim live MWORKS no-start attach success.",
            "Does not claim ROS2 planner_ready or closed_loop.",
            "Does not claim UE build/runtime/editor success.",
            "Does not include metrics-only rows or needs_iteration rows.",
        ],
        "candidate_rows": [
            {
                "claim_slot": "bad",
                "experiment_id": bad_row["experiment_id"],
                "priority": bad_row["priority"],
                "quality_status": "needs_iteration",
                "metrics_file": bad_row["metrics_file"],
                "raw_file": bad_row["raw_file"],
                "claim_ceiling": "candidate_report_evidence_only_not_final_pmo_acceptance",
            }
        ],
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    completed = run_checker(path)
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    joined = "\n".join(report["issues"])
    assert "needs_iteration" in joined
    assert "quality_status=pass" in joined


def test_rejects_final_acceptance_status(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    current = ROOT / "Results/static_audits/submission_evidence_manifest_20260610/candidate_submission_evidence_manifest.json"
    payload = json.loads(current.read_text(encoding="utf-8"))
    payload["status"] = "final_acceptance"
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    completed = run_checker(path)
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert any("status must be review_candidate_not_final_acceptance" in issue for issue in report["issues"])


def test_rejects_missing_raw_file(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    current = ROOT / "Results/static_audits/submission_evidence_manifest_20260610/candidate_submission_evidence_manifest.json"
    payload = json.loads(current.read_text(encoding="utf-8"))
    payload["candidate_rows"][0]["raw_file"] = "Results/does/not/exist.csv"
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    completed = run_checker(path)
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert any("candidate raw_file does not exist" in issue for issue in report["issues"])


def main() -> int:
    test_current_candidate_submission_manifest_passes()
    temp = ROOT / ".tmp" / "candidate_submission_manifest_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_rejects_needs_iteration_selection(temp / "needs")
        test_rejects_final_acceptance_status(temp / "final")
        test_rejects_missing_raw_file(temp / "missing_raw")
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
    print("[OK] candidate submission manifest tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
