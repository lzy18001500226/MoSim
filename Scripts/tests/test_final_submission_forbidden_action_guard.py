from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_final_submission_forbidden_action_guard.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_final_submission_forbidden_action_guard", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_final_submission_forbidden_action_guard.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checker(output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--output-json",
            str((output_dir / "forbidden_action_guard.json").relative_to(ROOT)),
            "--output-md",
            str((output_dir / "forbidden_action_guard.md").relative_to(ROOT)),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def copy_artifacts(tmp_path: Path, checker) -> dict[str, str]:
    paths: dict[str, str] = {}
    for artifact_id, rel_path in checker.ARTIFACTS.items():
        source = ROOT / rel_path
        target = tmp_path / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        paths[artifact_id] = str(target.relative_to(ROOT))
    return paths


def test_current_forbidden_action_guard_passes(tmp_path: Path) -> None:
    completed = run_checker(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["summary"]["artifact_count"] == 16
    assert report["summary"]["issue_count"] == 0
    assert report["summary"]["pdf_export_still_forbidden"] is True
    assert report["summary"]["demo_recording_still_forbidden"] is True
    assert report["summary"]["final_acceptance_still_forbidden"] is True
    assert report["summary"]["live_tools_still_forbidden"] is True
    assert report["summary"]["visible_thread_dispatch_still_forbidden"] is True
    assert report["summary"]["generates_final_outputs"] is False
    assert report["summary"]["final_acceptance"] is False
    assert "human_review_execution_gate_summary.summary.runs_pandoc_now" in report["checked_false_flags"]
    assert "execution_authorization_blocker_index.summary.authorizes_execution_now" in report[
        "checked_false_flags"
    ]


def test_rejects_authorized_pdf_export(tmp_path: Path) -> None:
    checker = load_checker()
    paths = copy_artifacts(tmp_path, checker)
    decision_path = ROOT / paths["final_output_execution_decision"]
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    decision["summary"]["authorizes_pdf_export"] = True
    decision_path.write_text(json.dumps(decision), encoding="utf-8")
    report = checker.validate(paths)
    assert report["ok"] is False
    assert any("authorizes_pdf_export" in issue for issue in report["issues"])


def test_rejects_live_tool_command_reference(tmp_path: Path) -> None:
    checker = load_checker()
    paths = copy_artifacts(tmp_path, checker)
    grouping_path = ROOT / paths["post_review_command_grouping"]
    grouping = json.loads(grouping_path.read_text(encoding="utf-8"))
    grouping.setdefault("debug_commands", []).append({"command": "ros2 topic pub /setpoint"})
    grouping_path.write_text(json.dumps(grouping), encoding="utf-8")
    report = checker.validate(paths)
    assert report["ok"] is False
    assert any("forbidden command token 'ros2'" in issue for issue in report["issues"])


def test_rejects_visible_thread_dispatch_flag(tmp_path: Path) -> None:
    checker = load_checker()
    paths = copy_artifacts(tmp_path, checker)
    blocker_path = ROOT / paths["execution_authorization_blocker_index"]
    blocker = json.loads(blocker_path.read_text(encoding="utf-8"))
    blocker["summary"]["dispatches_visible_threads_now"] = True
    blocker_path.write_text(json.dumps(blocker), encoding="utf-8")
    report = checker.validate(paths)
    assert report["ok"] is False
    assert any("dispatches_visible_threads_now" in issue for issue in report["issues"])


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_forbidden_action_guard_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_forbidden_action_guard_passes(temp / "current")
        test_rejects_authorized_pdf_export(temp / "authorized_pdf")
        test_rejects_live_tool_command_reference(temp / "live_command")
        test_rejects_visible_thread_dispatch_flag(temp / "visible_dispatch")
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
    print("[OK] final submission forbidden action guard tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
