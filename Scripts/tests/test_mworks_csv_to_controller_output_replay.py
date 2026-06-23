from __future__ import annotations

import csv
import json
import subprocess
import sys
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "ros" / "mworks_csv_to_controller_output_replay.py"


def local_tmp_dir() -> Path:
    path = ROOT / "Results" / "tmp" / "pytest_mworks_csv_to_controller_output_replay" / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_csv(path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["time", "u1", "u2", "u3", "u4"])
        writer.writeheader()
        writer.writerow({"time": "0.0", "u1": "0.0", "u2": "0.0", "u3": "0.0", "u4": "0.0"})
        writer.writerow({"time": "0.05", "u1": "1.0", "u2": "-1.0", "u3": "2.0", "u4": "-2.0"})
        writer.writerow({"time": "0.10", "u1": "2.0", "u2": "-2.0", "u3": "4.0", "u4": "-4.0"})


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_dry_run_declares_delta_hover_mapper(tmp_path: Path) -> None:
    work = local_tmp_dir()
    source = work / "mworks.csv"
    write_csv(source)
    completed = run_script("--input-csv", str(source), "--dry-run", "--max-rate-hz", "20")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["status"] == "ready"
    assert report["summary"]["sample_count"] == 3
    assert "signed_speed_i" in report["mapping"]["formula"]
    assert report["mapping"]["command_columns"] == ["u1", "u2", "u3", "u4"]
    assert "does not run Gazebo" in " ".join(report["claim_boundary"])


def test_writes_controller_output_jsonl_and_manifest(tmp_path: Path) -> None:
    work = local_tmp_dir()
    source = work / "mworks.csv"
    output = work / "controller_output.jsonl"
    manifest = work / "manifest.json"
    write_csv(source)

    completed = run_script(
        "--input-csv",
        str(source),
        "--output-jsonl",
        str(output),
        "--output-manifest",
        str(manifest),
        "--max-rate-hz",
        "20",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    samples = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert len(samples) == 3
    assert samples[0]["command_type"] == "normalized_motor_speed"
    assert samples[0]["command"] == [0.0552, 0.0552, 0.0552, 0.0552]
    assert samples[1]["mworks_source"]["controller_delta_command"] == [1.0, -1.0, 2.0, -2.0]
    assert all(0.0 <= value <= 1.0 for sample in samples for value in sample["command"])

    report = json.loads(manifest.read_text(encoding="utf-8"))
    assert report["output_jsonl"].endswith("controller_output.jsonl")
    assert report["summary"]["first_command"] == [0.0552, 0.0552, 0.0552, 0.0552]


def test_missing_command_column_blocks(tmp_path: Path) -> None:
    work = local_tmp_dir()
    source = work / "bad.csv"
    source.write_text("time,u1,u2,u3\n0,0,0,0\n", encoding="utf-8")
    completed = run_script("--input-csv", str(source), "--dry-run")
    assert completed.returncode != 0
    assert "missing required CSV columns" in (completed.stdout + completed.stderr)
