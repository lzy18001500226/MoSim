from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_submission_source_output_readiness.py"


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


def test_current_submission_source_output_readiness_blocks_final_export(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["source_docs_ready"] is True
    assert report["pandoc_available"] is True
    assert report["safe_to_export_final_pdfs_now"] is False
    assert report["missing_final_output_count"] == 4
    assert report["final_submission_ready"] is False

    readiness = json.loads((tmp_path / "submission_source_output_readiness.json").read_text(encoding="utf-8"))
    assert readiness["status"] == "static_source_output_readiness_not_final_submission"
    assert readiness["summary"]["generates_final_outputs"] is False
    blocker_ids = {blocker["blocker_id"] for blocker in readiness["blockers"]}
    assert "report_source_edit_not_approved" in blocker_ids
    assert "final_outputs_missing" in blocker_ids
    assert "does not export PDFs" in " ".join(readiness["claim_boundary"])


def main() -> int:
    temp = ROOT / ".tmp" / "submission_source_output_readiness_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_submission_source_output_readiness_blocks_final_export(temp / "current")
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
    print("[OK] submission source output readiness tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
