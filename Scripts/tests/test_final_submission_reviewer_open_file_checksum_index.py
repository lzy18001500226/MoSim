from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_reviewer_open_file_checksum_index.py"
SOURCE_INDEX = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_reviewer_evidence_index_20260610"
    / "final_submission_reviewer_evidence_index.json"
)


def load_builder():
    spec = importlib.util.spec_from_file_location("build_final_submission_reviewer_open_file_checksum_index", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_final_submission_reviewer_open_file_checksum_index.py")
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
            "--ignore-previous-output",
            *extra_args,
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_checksum_index_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["source_status"] == "reviewer_evidence_index_not_execution"
    assert stdout["source_action_count"] == 6
    assert stdout["unique_open_file_count"] == 21
    assert stdout["total_open_file_reference_count"] > stdout["unique_open_file_count"]
    assert stdout["duplicate_open_file_reference_count"] > 0
    assert stdout["checksum_file_count"] == 21
    assert stdout["missing_open_file_count"] == 0
    assert stdout["unreadable_open_file_count"] == 0
    assert stdout["drift_from_previous_output_count"] == 0
    assert stdout["issue_count"] == 0
    assert stdout["opens_files_now"] is False
    assert stdout["runs_commands_now"] is False
    assert stdout["generates_final_outputs"] is False
    assert stdout["final_acceptance"] is False

    index = json.loads(
        (tmp_path / "final_submission_reviewer_open_file_checksum_index.json").read_text(encoding="utf-8")
    )
    assert len(index["open_files"]) == 21
    assert all(record["sha256"] for record in index["open_files"])
    assert all(record["readable"] is True for record in index["open_files"])
    assert "It does not run final-output commands." in index["claim_boundary"]

    markdown = (tmp_path / "final_submission_reviewer_open_file_checksum_index.md").read_text(encoding="utf-8")
    assert "## Open Files" in markdown
    assert "SHA256" in markdown


def test_rejects_missing_open_file(tmp_path: Path) -> None:
    builder = load_builder()
    broken = json.loads(SOURCE_INDEX.read_text(encoding="utf-8"))
    broken["review_actions"][0]["review_evidence_files"][0]["path"] = (
        "Results/static_audits/final_submission_missing_open_file.md"
    )
    broken_path = tmp_path / "broken_reviewer_evidence_index.json"
    broken_path.parent.mkdir(parents=True, exist_ok=True)
    broken_path.write_text(json.dumps(broken), encoding="utf-8")
    index = builder.build_index(broken_path, None)
    assert index["summary"]["missing_open_file_count"] == 1
    assert index["summary"]["issue_count"] == 1
    assert any("missing required open file" in issue for issue in index["issues"])


def test_detects_previous_output_drift(tmp_path: Path) -> None:
    builder = load_builder()
    output_path = tmp_path / "previous.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    first = builder.build_index(SOURCE_INDEX, None)
    output_path.write_text(json.dumps(first), encoding="utf-8")
    previous = json.loads(output_path.read_text(encoding="utf-8"))
    previous["open_files"][0]["sha256"] = "0" * 64
    output_path.write_text(json.dumps(previous), encoding="utf-8")
    second = builder.build_index(SOURCE_INDEX, output_path)
    assert second["summary"]["drift_from_previous_output_count"] >= 1
    assert second["summary"]["issue_count"] >= 1
    assert any("open file drift detected" in issue for issue in second["issues"])


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_reviewer_open_file_checksum_index_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_checksum_index_builds(temp / "current")
        test_rejects_missing_open_file(temp / "missing_file")
        test_detects_previous_output_drift(temp / "drift")
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
    print("[OK] final submission reviewer open-file checksum index tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
