from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_execution_blocker_owner_status_digest.py"
AUTH_BLOCKERS = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_execution_authorization_blocker_20260610"
    / "final_submission_execution_authorization_blocker_index.json"
)


def load_builder():
    spec = importlib.util.spec_from_file_location("build_final_submission_execution_blocker_owner_status_digest", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_final_submission_execution_blocker_owner_status_digest.py")
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


def test_current_owner_status_digest_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["owner_count"] == 4
    assert stdout["action_count"] == 6
    assert stdout["execution_target_count"] == 4
    assert stdout["blocked_execution_target_count"] == 4
    assert stdout["target_action_reference_count"] == 16
    assert stdout["blocked_artifact_count"] == 17
    assert stdout["blocker_class_count"] == 10
    assert stdout["dashboard_blocking_gate_count"] == 7
    assert stdout["dashboard_blocker_count"] == 16
    assert stdout["reviewer_open_file_count"] == 21
    assert stdout["reviewer_open_file_drift_count"] == 0
    assert stdout["issue_count"] == 0
    assert stdout["runs_commands_now"] is False
    assert stdout["authorizes_execution_now"] is False
    assert stdout["generates_final_outputs"] is False
    assert stdout["final_acceptance"] is False

    digest = json.loads((tmp_path / "final_submission_execution_blocker_owner_status_digest.json").read_text(encoding="utf-8"))
    owners = {row["owner"]: row for row in digest["owner_groups"]}
    assert set(owners) == {"user_or_PMO", "local_environment_owner", "packaging_or_manual_operator", "operator"}
    assert owners["user_or_PMO"]["action_count"] == 3
    assert owners["local_environment_owner"]["action_ids"] == ["A2-provide-pdf-engine"]
    assert owners["packaging_or_manual_operator"]["action_ids"] == ["A4-create-reviewed-final-artifacts"]
    assert owners["operator"]["action_ids"] == ["A5-rerun-readiness-gates"]
    assert {row["action_id"] for row in digest["actions"]} == {
        "A1-approve-or-reject-report-source-edits",
        "A2-provide-pdf-engine",
        "A3-review-demo-storyboard",
        "A4-create-reviewed-final-artifacts",
        "A5-rerun-readiness-gates",
        "A6-review-final-output-execution-decision",
    }
    assert "It does not run commands." in digest["claim_boundary"]

    markdown = (tmp_path / "final_submission_execution_blocker_owner_status_digest.md").read_text(encoding="utf-8")
    assert "## Owner Groups" in markdown
    assert "user_or_PMO" in markdown


def test_rejects_unknown_required_action(tmp_path: Path) -> None:
    builder = load_builder()
    broken = json.loads(AUTH_BLOCKERS.read_text(encoding="utf-8"))
    broken["execution_target_authorization_blockers"][0]["required_action_ids"].append("A0-missing-action")
    broken_path = tmp_path / "broken_auth_blockers.json"
    broken_path.parent.mkdir(parents=True, exist_ok=True)
    broken_path.write_text(json.dumps(broken), encoding="utf-8")
    digest = builder.build_digest(
        builder.DEFAULT_ACTION_MAP,
        broken_path,
        builder.DEFAULT_TRIAGE_MAP,
        builder.DEFAULT_DASHBOARD,
        builder.DEFAULT_CHECKSUM_INDEX,
    )
    assert digest["summary"]["issue_count"] == 1
    assert any("unknown action" in issue for issue in digest["issues"])


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_execution_blocker_owner_status_digest_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_owner_status_digest_builds(temp / "current")
        test_rejects_unknown_required_action(temp / "unknown_action")
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
    print("[OK] final submission execution-blocker owner/status digest tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
