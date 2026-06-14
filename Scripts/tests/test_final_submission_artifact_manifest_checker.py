from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_final_submission_artifact_manifest.py"


def run_checker(output_json: Path, allow_missing: bool = False) -> subprocess.CompletedProcess[str]:
    cmd = [
        sys.executable,
        str(CHECKER),
        "--output-json",
        str(output_json.relative_to(ROOT) if output_json.is_relative_to(ROOT) else output_json),
    ]
    if allow_missing:
        cmd.append("--allow-missing")
    return subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_final_submission_artifacts_are_blocked(tmp_path: Path) -> None:
    output_json = tmp_path / "artifact_check.json"
    completed = run_checker(output_json)
    assert completed.returncode == 1
    result = json.loads(output_json.read_text(encoding="utf-8"))
    assert result["status"] == "final_artifacts_missing_not_final_submission"
    assert result["summary"]["artifact_count"] == 4
    assert result["summary"]["missing_artifact_count"] == 4
    assert result["summary"]["final_submission_artifacts_ready"] is False
    assert set(result["missing_artifacts"]) == {
        "user_manual_pdf",
        "simulation_analysis_report_pdf",
        "demo_video",
        "final_acceptance_packet",
    }


def test_allow_missing_keeps_blocked_result_but_returns_zero(tmp_path: Path) -> None:
    output_json = tmp_path / "artifact_check_allow.json"
    completed = run_checker(output_json, allow_missing=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is False
    result = json.loads(output_json.read_text(encoding="utf-8"))
    assert result["summary"]["generates_final_outputs"] is False
    assert result["summary"]["final_acceptance"] is False


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_artifact_manifest_checker_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_final_submission_artifacts_are_blocked(temp / "current")
        test_allow_missing_keeps_blocked_result_but_returns_zero(temp / "allow")
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
    print("[OK] final submission artifact manifest checker tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
