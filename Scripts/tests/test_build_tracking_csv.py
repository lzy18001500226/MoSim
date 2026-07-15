from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILD_TRACKING = ROOT / "Scripts" / "quality" / "build_tracking_csv.py"
TRACKING_PROFILE = "px4_mavros_fused_reference_state_csv_v1"


def run_build(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BUILD_TRACKING), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def write_reference(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "stamp,phase,rx,ry,rz",
                "0.00,takeoff,0,0,0.0",
                "0.10,hover,0,0,1.0",
                "0.20,hover,0,0,1.0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_profile_reference(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "stamp,phase,ref_x,ref_y,ref_z",
                "0.00,takeoff,0,0,0.0",
                "0.10,hover,0,0,1.0",
                "0.20,hover,0,0,1.0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_state(path: Path, gap: bool = False) -> None:
    first_time = "0.30" if gap else "0.01"
    path.write_text(
        "\n".join(
            [
                "stamp,x,y,z,sat",
                f"{first_time},0.001,0.000,0.000,0",
                "0.11,0.004,0.003,0.995,0",
                "0.19,0.003,0.002,0.998,0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_profile_state(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "stamp,x,y,z,saturated",
                "0.01,0.001,0.000,0.000,0",
                "0.11,0.004,0.003,0.995,0",
                "0.19,0.003,0.002,0.998,0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_build_tracking_csv_aligns_reference_and_state(tmp_path: Path) -> None:
    reference = tmp_path / "reference.csv"
    state = tmp_path / "state.csv"
    output = tmp_path / "tracking.csv"
    report_path = tmp_path / "report.json"
    write_reference(reference)
    write_state(state)

    completed = run_build(
        "--reference-csv",
        str(reference),
        "--state-csv",
        str(state),
        "--out",
        str(output),
        "--ref-time",
        "stamp",
        "--ref-x",
        "rx",
        "--ref-y",
        "ry",
        "--ref-z",
        "rz",
        "--state-time",
        "stamp",
        "--state-x",
        "x",
        "--state-y",
        "y",
        "--state-z",
        "z",
        "--phase-column",
        "phase",
        "--saturated-column",
        "sat",
        "--report",
        str(report_path),
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["alignment"]["aligned_rows"] == 3
    assert report["alignment"]["max_time_delta_s"] <= 0.01 + 1e-12

    with output.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[1]["phase"] == "hover"
    assert rows[1]["ref_z_m"] == "1.0"
    assert rows[1]["truth_z_m"] == "0.995"


def test_build_tracking_csv_accepts_tracking_source_profile(tmp_path: Path) -> None:
    reference = tmp_path / "reference.csv"
    state = tmp_path / "state.csv"
    output = tmp_path / "tracking.csv"
    report_path = tmp_path / "report.json"
    write_profile_reference(reference)
    write_profile_state(state)

    completed = run_build(
        "--reference-csv",
        str(reference),
        "--state-csv",
        str(state),
        "--out",
        str(output),
        "--tracking-source-profile",
        TRACKING_PROFILE,
        "--report",
        str(report_path),
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["tracking_source_profile"] == TRACKING_PROFILE
    assert report["columns"]["reference"]["x"] == "ref_x"
    assert report["columns"]["state"]["z"] == "z"
    assert report["alignment"]["max_allowed_time_delta_s"] == 0.05

    with output.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[2]["phase"] == "hover"
    assert rows[2]["saturated"] == "0"


def test_build_tracking_csv_rejects_unaligned_state_gap(tmp_path: Path) -> None:
    reference = tmp_path / "reference.csv"
    state = tmp_path / "state.csv"
    output = tmp_path / "tracking.csv"
    write_reference(reference)
    write_state(state, gap=True)

    completed = run_build(
        "--reference-csv",
        str(reference),
        "--state-csv",
        str(state),
        "--out",
        str(output),
        "--ref-time",
        "stamp",
        "--ref-x",
        "rx",
        "--ref-y",
        "ry",
        "--ref-z",
        "rz",
        "--state-time",
        "stamp",
        "--state-x",
        "x",
        "--state-y",
        "y",
        "--state-z",
        "z",
        "--max-time-delta-s",
        "0.05",
    )
    assert completed.returncode == 2
    assert "no state sample within" in completed.stderr
