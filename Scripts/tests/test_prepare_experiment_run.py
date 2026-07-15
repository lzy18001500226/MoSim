from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREPARE = ROOT / "Scripts" / "quality" / "prepare_experiment_run.py"
VALID_PROFILE = ROOT / "Config" / "profiles" / "experiments" / "px4ctrl_takeoff_hover_land_v1.json"


def run_prepare(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PREPARE), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_prepare_experiment_run_materializes_pre_run_packet(tmp_path: Path) -> None:
    run_id = "pytest_prepare_px4ctrl_takeoff"
    completed = run_prepare(
        str(VALID_PROFILE),
        "--run-id",
        run_id,
        "--output-root",
        str(tmp_path),
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["run_id"] == run_id
    assert report["runtime_started"] is False
    assert report["evidence_complete"] is False

    run_dir = tmp_path / run_id
    assert (run_dir / "LaunchPlan.json").is_file()
    assert (run_dir / "RUN_MANIFEST.json").is_file()
    assert (run_dir / "preflight.json").is_file()
    assert (run_dir / "source_hashes.json").is_file()
    assert (run_dir / "operator_checklist.md").is_file()
    assert (run_dir / "commands.md").is_file()
    assert (run_dir / "review.template.md").is_file()
    assert (run_dir / "screenshots").is_dir()
    assert (run_dir / "logs").is_dir()
    assert (run_dir / "raw").is_dir()

    assert not (run_dir / "tracking.csv").exists()
    assert not (run_dir / "metrics.json").exists()
    assert not (run_dir / "review.md").exists()
    assert not any((run_dir / "screenshots").iterdir())
    assert not any((run_dir / "logs").iterdir())

    launch_plan = json.loads((run_dir / "LaunchPlan.json").read_text(encoding="utf-8"))
    manifest = json.loads((run_dir / "RUN_MANIFEST.json").read_text(encoding="utf-8"))
    assert launch_plan["launch_plan"]["run_id"] == run_id
    assert manifest["run_manifest"]["run_id"] == run_id
    source_state = manifest["run_manifest"]["source_state"]
    assert source_state["git_commit"] != "<commit-or-dirty>"
    assert source_state["source_hashes"].endswith("source_hashes.json")
    assert source_state["source_hashes_sha256"]
    source_hashes = json.loads((run_dir / "source_hashes.json").read_text(encoding="utf-8"))
    assert source_hashes["run_id"] == run_id
    assert source_hashes["sources"]
    commands = (run_dir / "commands.md").read_text(encoding="utf-8")
    checklist = (run_dir / "operator_checklist.md").read_text(encoding="utf-8")
    assert "RuntimeExportProfile" in commands
    assert "RuntimeExportProfile" in checklist
    assert "px4ctrl_runtime_log_export_v1" in commands
    assert f"export_runtime_sources.py {run_dir}" in commands
    assert f"Results/runs/{run_id}" not in commands


def test_prepare_experiment_run_refuses_existing_run_without_force(tmp_path: Path) -> None:
    run_id = "pytest_prepare_existing"
    first = run_prepare(str(VALID_PROFILE), "--run-id", run_id, "--output-root", str(tmp_path))
    assert first.returncode == 0, first.stdout + first.stderr

    second = run_prepare(str(VALID_PROFILE), "--run-id", run_id, "--output-root", str(tmp_path))
    assert second.returncode == 1, second.stdout + second.stderr
    report = json.loads(second.stdout)
    assert report["ok"] is False
    assert any(error["code"] == "RUN-PREP-01" for error in report["errors"])
