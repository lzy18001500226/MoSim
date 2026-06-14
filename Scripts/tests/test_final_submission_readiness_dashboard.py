from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_readiness_dashboard.py"


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


def test_current_final_submission_dashboard_is_blocked(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["blocking_gate_count"] == 7
    assert stdout["final_submission_ready"] is False

    dashboard = json.loads((tmp_path / "final_submission_readiness_dashboard.json").read_text(encoding="utf-8"))
    assert dashboard["status"] == "static_dashboard_not_final_submission_acceptance"
    assert dashboard["summary"]["gate_count"] == 7
    assert dashboard["summary"]["ready_gate_count"] == 0
    assert dashboard["summary"]["blocking_gate_count"] == 7
    assert dashboard["summary"]["generates_final_outputs"] is False
    assert dashboard["summary"]["final_acceptance"] is False
    assert set(dashboard["blocking_gate_ids"]) == {
        "final_packaging_gap",
        "source_output_readiness",
        "final_artifact_manifest",
        "pdf_export_plan",
        "demo_video_storyboard",
        "final_acceptance_prereq",
        "final_output_execution_decision",
    }
    assert "It does not replace manual/PMO review." in dashboard["claim_boundary"]


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_readiness_dashboard_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_final_submission_dashboard_is_blocked(temp / "current")
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
    print("[OK] final submission readiness dashboard tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
