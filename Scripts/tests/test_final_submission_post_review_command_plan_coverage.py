from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_final_submission_post_review_command_plan_coverage.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_final_submission_post_review_command_plan_coverage", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_final_submission_post_review_command_plan_coverage.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checker(output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--output-json",
            str((output_dir / "coverage.json").relative_to(ROOT)),
            "--output-md",
            str((output_dir / "coverage.md").relative_to(ROOT)),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_post_review_command_plan_coverage_passes(tmp_path: Path) -> None:
    completed = run_checker(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["ok"] is True
    assert result["status"] == "post_review_command_plan_coverage_check_not_execution"
    assert result["summary"]["transition_count"] == 3
    assert result["summary"]["total_command_reference_count"] == 45
    assert result["summary"]["unique_command_count"] == 20
    assert result["summary"]["covered_unique_command_count"] == 20
    assert result["summary"]["runs_rerun_commands_now"] is False
    assert result["summary"]["applies_transitions_now"] is False
    assert result["summary"]["generates_final_outputs"] is False
    assert result["summary"]["final_acceptance"] is False
    assert all(record["covered"] is True for record in result["unique_commands"])
    assert all(
        transition["runs_rerun_commands_now"] is False
        for transition in result["transition_command_coverage"]
    )
    assert "It does not run listed rerun commands." in result["claim_boundary"]

    markdown = (tmp_path / "coverage.md").read_text(encoding="utf-8")
    assert "## Transition Coverage" in markdown
    assert "TRANSITION-A1-approve-or-reject-report-source-edits" in markdown


def test_rejects_missing_command_script() -> None:
    checker = load_checker()
    result = checker.command_record("python Scripts/quality/does_not_exist.py")
    assert result["covered"] is False
    assert "script_missing" in result["issues"]


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_post_review_command_plan_coverage_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_post_review_command_plan_coverage_passes(temp / "current")
        test_rejects_missing_command_script()
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
    print("[OK] final submission post-review command plan coverage tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
