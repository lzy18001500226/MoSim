from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_acceptance_packet_prereq_plan.py"


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


def test_current_final_acceptance_template_is_blocked(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["safe_to_write_final_acceptance_packet_now"] is False
    assert stdout["writes_canonical_acceptance_packet_now"] is False

    plan = json.loads((tmp_path / "final_acceptance_packet_prereq_plan.json").read_text(encoding="utf-8"))
    template = json.loads((tmp_path / "PMO-FINAL-SUBMISSION-ACCEPTANCE.draft-template.json").read_text(encoding="utf-8"))
    assert plan["status"] == "blocked_template_not_final_acceptance"
    assert plan["summary"]["missing_or_failing_final_artifact_count"] == 4
    assert plan["summary"]["safe_to_write_final_acceptance_packet_now"] is False
    assert plan["summary"]["writes_canonical_acceptance_packet_now"] is False
    assert plan["summary"]["final_acceptance"] is False
    assert template["status"] == "draft_template_not_final_acceptance"
    assert template["final_submission"]["accepted"] is False
    assert template["final_submission"]["canonical_packet_path"] == "Results/agent_packets/returns/PMO-FINAL-SUBMISSION-ACCEPTANCE.json"
    blocker_ids = {blocker["blocker_id"] for blocker in plan["blockers"]}
    assert "final_artifacts_not_ready" in blocker_ids
    assert "pdf_export_not_ready" in blocker_ids
    assert "demo_video_recording_not_approved" in blocker_ids
    assert "source_output_readiness_blocks_acceptance" in blocker_ids
    assert "It does not write the canonical PMO final acceptance packet." in plan["claim_boundary"]


def main() -> int:
    temp = ROOT / ".tmp" / "final_acceptance_packet_prereq_plan_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_final_acceptance_template_is_blocked(temp / "current")
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
    print("[OK] final acceptance packet prerequisite plan tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
