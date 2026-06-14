from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_open_file_shortest_path_bundle.py"
CHECKSUM_INDEX = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_reviewer_open_file_checksum_index_20260610"
    / "final_submission_reviewer_open_file_checksum_index.json"
)


def load_builder():
    spec = importlib.util.spec_from_file_location("build_final_submission_open_file_shortest_path_bundle", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_final_submission_open_file_shortest_path_bundle.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_builder(output_dir: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--output-dir",
            str(output_dir.relative_to(ROOT)),
            *extra_args,
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_open_file_shortest_path_bundle_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["path_step_count"] == 6
    assert stdout["unique_open_file_count"] == 21
    assert stdout["total_open_file_reference_count"] == 33
    assert stdout["new_open_file_count"] == 21
    assert stdout["reused_open_file_reference_count"] == 12
    assert stdout["checksum_file_count"] == 21
    assert stdout["missing_open_file_count"] == 0
    assert stdout["unreadable_open_file_count"] == 0
    assert stdout["drift_from_previous_output_count"] == 0
    assert stdout["issue_count"] == 0
    assert stdout["opens_files_now"] is False
    assert stdout["runs_commands_now"] is False
    assert stdout["authorizes_execution_now"] is False
    assert stdout["generates_final_outputs"] is False
    assert stdout["final_acceptance"] is False

    bundle = json.loads((tmp_path / "final_submission_open_file_shortest_path_bundle.json").read_text(encoding="utf-8"))
    assert bundle["status"] == "open_file_shortest_path_bundle_not_execution"
    assert [step["action_id"] for step in bundle["path_steps"]] == [
        "A1-approve-or-reject-report-source-edits",
        "A3-review-demo-storyboard",
        "A2-provide-pdf-engine",
        "A6-review-final-output-execution-decision",
        "A4-create-reviewed-final-artifacts",
        "A5-rerun-readiness-gates",
    ]
    assert sum(step["new_open_file_count"] for step in bundle["path_steps"]) == 21
    assert sum(step["reused_open_file_count"] for step in bundle["path_steps"]) == 12
    assert any(step["reused_open_file_count"] > 0 for step in bundle["path_steps"])
    assert "It does not open files in an editor or UI." in bundle["claim_boundary"]

    markdown = (tmp_path / "final_submission_open_file_shortest_path_bundle.md").read_text(encoding="utf-8")
    assert "## Path Steps" in markdown
    assert "Reused open files" in markdown


def test_reports_missing_checksum_file(tmp_path: Path) -> None:
    builder = load_builder()
    checksum = json.loads(CHECKSUM_INDEX.read_text(encoding="utf-8"))
    checksum["open_files"] = checksum["open_files"][1:]
    checksum_path = tmp_path / "broken_checksum.json"
    checksum_path.parent.mkdir(parents=True, exist_ok=True)
    checksum_path.write_text(json.dumps(checksum), encoding="utf-8")
    bundle = builder.build_bundle(
        builder.DEFAULT_SHORTEST_PATH,
        builder.DEFAULT_REVIEWER_EVIDENCE_INDEX,
        checksum_path,
    )
    assert bundle["summary"]["issue_count"] >= 1
    assert any("missing from checksum index" in issue for issue in bundle["issues"])


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_open_file_shortest_path_bundle_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_open_file_shortest_path_bundle_builds(temp / "current")
        test_reports_missing_checksum_file(temp / "missing_checksum")
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
    print("[OK] final submission open-file shortest-path bundle tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
