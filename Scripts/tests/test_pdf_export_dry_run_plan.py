from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_pdf_export_dry_run_plan.py"


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


def test_current_pdf_export_plan_is_dry_run_only(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["safe_to_run_pdf_export_now"] is False
    assert stdout["runs_pandoc_now"] is False
    assert stdout["generates_final_outputs"] is False

    plan = json.loads((tmp_path / "pdf_export_dry_run_plan.json").read_text(encoding="utf-8"))
    assert plan["status"] == "dry_run_pdf_export_plan_not_final_output"
    assert plan["summary"]["runs_pandoc_now"] is False
    assert plan["summary"]["creates_submission_dir_now"] is False
    assert plan["summary"]["generates_final_outputs"] is False
    assert plan["summary"]["final_acceptance"] is False
    assert set(plan["exports"]) == {"user_manual_pdf", "simulation_analysis_report_pdf"}
    assert all(item["dry_run_only"] is True for item in plan["exports"].values())
    assert all(item["runs_command_now"] is False for item in plan["exports"].values())
    assert all(item["creates_output_now"] is False for item in plan["exports"].values())
    blocker_ids = {blocker["blocker_id"] for blocker in plan["blockers"]}
    assert "report_source_edit_not_approved" in blocker_ids
    assert "final_artifacts_missing" in blocker_ids
    assert "It does not run Pandoc." in plan["claim_boundary"]


def main() -> int:
    temp = ROOT / ".tmp" / "pdf_export_dry_run_plan_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_pdf_export_plan_is_dry_run_only(temp / "current")
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
    print("[OK] PDF export dry-run plan tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
