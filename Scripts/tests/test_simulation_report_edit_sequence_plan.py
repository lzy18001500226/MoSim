from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_simulation_report_edit_sequence_plan.py"


def run_builder(output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--output-dir",
            str(output_dir.relative_to(ROOT) if output_dir.is_relative_to(ROOT) else output_dir),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_simulation_report_edit_sequence_plan_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["action_count"] >= 7
    assert report["candidate_family_count"] == 3
    assert report["edits_report_source"] is False
    assert report["deletes_content"] is False
    assert report["final_acceptance"] is False

    plan = json.loads((tmp_path / "simulation_report_edit_sequence_plan.json").read_text(encoding="utf-8"))
    assert plan["status"] == "draft_edit_sequence_not_report_edit"
    action_ids = [action["action_id"] for action in plan["actions"]]
    assert action_ids[:2] == [
        "preserve_final_acceptance_boundary",
        "rewrite_formation_next_stage_boundary",
    ]
    assert {
        "insert_visual_trajectory_review_candidate_subsection",
        "insert_fault_tolerance_candidate_subsection",
        "insert_multi_uav_formation_candidate_subsection",
        "condense_smoke_and_legacy_sections",
        "renumber_l1_residual_subsection",
    }.issubset(set(action_ids))
    families = {action["claim_family"] for action in plan["actions"] if action["claim_family"]}
    assert families == {"fault_tolerance", "multi_uav_formation", "visual_trajectory_review"}
    assert all(action["edits_now"] is False for action in plan["actions"])
    assert all(action["requires_human_review_before_apply"] is True for action in plan["actions"])
    assert "does not edit Docs/报告/仿真分析报告_正文骨架.md" in " ".join(plan["claim_boundary"])


def main() -> int:
    temp = ROOT / ".tmp" / "simulation_report_edit_sequence_plan_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_simulation_report_edit_sequence_plan_builds(temp / "current")
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
    print("[OK] simulation report edit sequence plan tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
