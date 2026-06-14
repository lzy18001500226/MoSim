from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_final_submission_review_aid_freshness.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_final_submission_review_aid_freshness", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_final_submission_review_aid_freshness.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checker(output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--output-json",
            str((output_dir / "freshness.json").relative_to(ROOT)),
            "--output-md",
            str((output_dir / "freshness.md").relative_to(ROOT)),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def write_json(path: Path, status: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"status": status}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_current_review_aid_freshness_passes(tmp_path: Path) -> None:
    completed = run_checker(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["status"] == "review_aid_freshness_check_not_execution"
    assert report["summary"]["review_node_count"] == 13
    assert report["summary"]["dependency_edge_count"] == 12
    assert report["summary"]["missing_output_count"] == 0
    assert report["summary"]["status_mismatch_count"] == 0
    assert report["summary"]["stale_dependency_count"] == 0
    assert report["summary"]["refreshes_artifacts_now"] is False
    assert report["summary"]["runs_commands_now"] is False
    assert report["summary"]["updates_static_audit_index"] is False
    assert report["summary"]["generates_final_outputs"] is False
    assert report["summary"]["final_acceptance"] is False
    assert "It does not regenerate or refresh artifacts." in report["claim_boundary"]

    markdown = (tmp_path / "freshness.md").read_text(encoding="utf-8")
    assert "## Stale Dependencies" in markdown
    assert "Stale dependencies: `0`" in markdown


def test_detects_stale_dependency_with_synthetic_refresh_order(tmp_path: Path) -> None:
    checker = load_checker()
    upstream = tmp_path / "upstream.json"
    downstream = tmp_path / "downstream.json"
    write_json(upstream, checker.EXPECTED_STATUSES["final_submission_blocked_gate_triage_map"])
    write_json(downstream, checker.EXPECTED_STATUSES["final_submission_human_decision_diff_template"])
    os.utime(downstream, (100.0, 100.0))
    os.utime(upstream, (200.0, 200.0))
    refresh_order = tmp_path / "refresh_order.json"
    refresh_order.write_text(
        json.dumps(
            {
                "nodes": [
                    {
                        "node_id": "final_submission_blocked_gate_triage_map",
                        "command": "python Scripts/quality/build_final_submission_blocked_gate_triage_map.py",
                        "outputs": [str(upstream)],
                        "after": [],
                    },
                    {
                        "node_id": "final_submission_human_decision_diff_template",
                        "command": "python Scripts/quality/build_final_submission_human_decision_diff_template.py",
                        "outputs": [str(downstream)],
                        "after": ["final_submission_blocked_gate_triage_map"],
                    },
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    old_ids = checker.REVIEW_NODE_IDS
    try:
        checker.REVIEW_NODE_IDS = (
            "final_submission_blocked_gate_triage_map",
            "final_submission_human_decision_diff_template",
        )
        report = checker.build_freshness_check(refresh_order, grace_seconds=1.0)
    finally:
        checker.REVIEW_NODE_IDS = old_ids
    assert report["ok"] is False
    assert report["summary"]["stale_dependency_count"] == 1
    assert report["stale_dependencies"][0]["to"] == "final_submission_human_decision_diff_template"
    assert any("stale dependency" in issue for issue in report["issues"])


def test_detects_status_mismatch_with_synthetic_refresh_order(tmp_path: Path) -> None:
    checker = load_checker()
    output = tmp_path / "artifact.json"
    write_json(output, "wrong_status")
    refresh_order = tmp_path / "refresh_order.json"
    refresh_order.write_text(
        json.dumps(
            {
                "nodes": [
                    {
                        "node_id": "final_submission_reviewer_quickstart",
                        "command": "python Scripts/quality/build_final_submission_reviewer_quickstart.py",
                        "outputs": [str(output)],
                        "after": [],
                    }
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    old_ids = checker.REVIEW_NODE_IDS
    try:
        checker.REVIEW_NODE_IDS = ("final_submission_reviewer_quickstart",)
        report = checker.build_freshness_check(refresh_order, grace_seconds=1.0)
    finally:
        checker.REVIEW_NODE_IDS = old_ids
    assert report["ok"] is False
    assert report["summary"]["status_mismatch_count"] == 1
    assert report["status_mismatches"][0]["expected_status"] == "reviewer_quickstart_not_execution"


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_review_aid_freshness_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_review_aid_freshness_passes(temp / "current")
        test_detects_stale_dependency_with_synthetic_refresh_order(temp / "stale")
        test_detects_status_mismatch_with_synthetic_refresh_order(temp / "status")
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
    print("[OK] final submission review aid freshness tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
