from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_review_artifact_dependency_graph.py"


def run_builder(output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--output-dir",
            str(output_dir.relative_to(ROOT)),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_review_artifact_dependency_graph_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["review_node_count"] == 12
    assert stdout["dependency_edge_count"] == 11
    assert stdout["bundle_artifact_count"] == 7
    assert stdout["missing_output_count"] == 0
    assert stdout["updates_static_audit_index"] is False

    graph = json.loads((tmp_path / "final_submission_review_artifact_dependency_graph.json").read_text(encoding="utf-8"))
    assert graph["status"] == "review_artifact_dependency_graph_not_execution"
    assert graph["summary"]["runs_commands_now"] is False
    assert graph["summary"]["generates_final_outputs"] is False
    assert graph["summary"]["final_acceptance"] is False
    assert graph["nodes"][0]["node_id"] == "final_submission_blocked_gate_triage_map"
    assert graph["edges"][-1] == {
        "from": "final_submission_post_review_state_transition_plan",
        "to": "final_submission_post_review_command_plan_coverage",
        "type": "after",
    }
    assert len(graph["bundle_artifact_links"]) == 7
    assert "It does not change final_submission_static_audit_index.json." in graph["claim_boundary"]

    markdown = (tmp_path / "final_submission_review_artifact_dependency_graph.md").read_text(encoding="utf-8")
    assert "## Edges" in markdown
    assert "final_submission_reviewer_handoff_note" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_review_artifact_dependency_graph_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_review_artifact_dependency_graph_builds(temp / "current")
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
    print("[OK] final submission review artifact dependency graph tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
