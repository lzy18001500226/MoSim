from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_simulation_report_source_edit_readiness_gate.py"


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


def test_current_source_edit_readiness_gate_blocks_apply(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["safe_to_apply_report_source_edits_now"] is False
    assert report["blocking_gate_count"] >= 1
    assert report["decision"] == "pending_review"
    assert report["approved_preview_count"] == 0
    assert report["decision_check_ok"] is True
    assert report["decision_authorizes_application"] is False
    assert report["edits_report_source"] is False
    assert report["final_acceptance"] is False

    readiness = json.loads((tmp_path / "simulation_report_source_edit_readiness_gate.json").read_text(encoding="utf-8"))
    assert readiness["status"] == "source_edit_application_blocked_pending_human_review"
    gates = {gate["gate_id"]: gate for gate in readiness["gates"]}
    assert gates["patch_preview_checker_ok"]["ok"] is True
    assert gates["patch_preview_is_non_applying"]["ok"] is True
    assert gates["human_pmo_apply_approval_present"]["ok"] is False
    assert "current decision=pending_review" in gates["human_pmo_apply_approval_present"]["blocking_reason"]
    assert gates["report_source_edit_decision_check_ok"]["ok"] is True
    assert gates["final_packaging_still_not_ready_boundary"]["ok"] is True
    assert readiness["summary"]["decision"] == "pending_review"
    assert readiness["summary"]["approved_preview_count"] == 0
    assert readiness["summary"]["decision_check_ok"] is True
    assert readiness["summary"]["decision_authorizes_application"] is False
    assert readiness["summary"]["safe_to_apply_report_source_edits_now"] is False
    assert "does not edit Docs/simulation_report.md" in " ".join(readiness["claim_boundary"])


def main() -> int:
    temp = ROOT / ".tmp" / "simulation_report_source_edit_readiness_gate_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_source_edit_readiness_gate_blocks_apply(temp / "current")
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
    print("[OK] simulation report source edit readiness gate tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
