from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_packaging_gap_inventory.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_final_packaging_gap_inventory", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_final_packaging_gap_inventory.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def test_current_packaging_gap_inventory(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["source_inputs_ready"] is True
    assert report["missing_final_artifact_count"] == 4
    assert report["final_submission_ready"] is False

    inventory = json.loads((tmp_path / "final_packaging_gap_inventory.json").read_text(encoding="utf-8"))
    assert inventory["status"] == "final_packaging_gap_inventory_not_final_acceptance"
    assert inventory["missing_final_artifacts"] == [
        "user_manual_pdf",
        "simulation_analysis_report_pdf",
        "demo_video",
        "final_acceptance_packet",
    ]
    assert "not final acceptance" in (tmp_path / "final_packaging_gap_inventory.md").read_text(
        encoding="utf-8"
    )


def test_all_final_artifacts_present_can_be_ready(tmp_path: Path, monkeypatch=None) -> None:
    builder = load_builder()
    submission_dir = tmp_path / "Results" / "submission"
    packet_dir = tmp_path / "Results" / "agent_packets" / "returns"
    submission_dir.mkdir(parents=True)
    packet_dir.mkdir(parents=True)
    files = {
        "user_manual_pdf": submission_dir / "user_manual.pdf",
        "simulation_analysis_report_pdf": submission_dir / "simulation_analysis_report.pdf",
        "demo_video": submission_dir / "demo_video.mp4",
        "final_acceptance_packet": packet_dir / "PMO-FINAL-SUBMISSION-ACCEPTANCE.json",
    }
    for path in files.values():
        path.write_text("placeholder", encoding="utf-8")

    original = builder.FINAL_ARTIFACTS
    try:
        builder.FINAL_ARTIFACTS = {
            name: {**original[name], "path": str(path)}
            for name, path in files.items()
        }
        inventory = builder.build_inventory()
    finally:
        builder.FINAL_ARTIFACTS = original

    assert inventory["summary"]["source_inputs_ready"] is True
    assert inventory["summary"]["missing_final_artifact_count"] == 0
    assert inventory["summary"]["final_submission_ready"] is True


def main() -> int:
    temp = ROOT / ".tmp" / "final_packaging_gap_inventory_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_packaging_gap_inventory(temp / "current")
        test_all_final_artifacts_present_can_be_ready(temp / "complete")
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
    print("[OK] final packaging gap inventory tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
