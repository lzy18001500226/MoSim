from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NORMALIZE = ROOT / "Scripts" / "quality" / "normalize_tracking_csv.py"
COMPUTE = ROOT / "Scripts" / "quality" / "compute_tracking_metrics.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def write_raw_csv(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "stamp,rx,ry,rz,gx,gy,gz,is_sat",
                "0.00,0,0,0.0,0.000,0.000,0.000,0",
                "0.01,0,0,0.5,0.005,0.000,0.480,0",
                "0.02,0,0,1.0,0.010,0.000,0.990,0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_tracking_normalizer_maps_raw_csv_and_metrics_accept_it(tmp_path: Path) -> None:
    raw = tmp_path / "raw_tracking.csv"
    tracking = tmp_path / "tracking.csv"
    metrics = tmp_path / "metrics.json"
    write_raw_csv(raw)

    completed = run_cmd(
        str(NORMALIZE),
        str(raw),
        "--out",
        str(tracking),
        "--map",
        "time_s=stamp",
        "--map",
        "ref_x_m=rx",
        "--map",
        "ref_y_m=ry",
        "--map",
        "ref_z_m=rz",
        "--map",
        "truth_x_m=gx",
        "--map",
        "truth_y_m=gy",
        "--map",
        "truth_z_m=gz",
        "--map",
        "saturated=is_sat",
        "--default",
        "phase=hover",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["output_rows"] == 3

    with tracking.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["phase"] == "hover"
    assert rows[0]["truth_z_m"] == "0.000"

    computed = run_cmd(str(COMPUTE), str(tracking), "--out", str(metrics))
    assert computed.returncode == 0, computed.stdout + computed.stderr
    packet = json.loads(metrics.read_text(encoding="utf-8"))
    assert packet["metrics"]["rmse"]["unit"] == "m"
    assert packet["metrics"]["saturation_ratio"]["value"] == 0


def test_tracking_normalizer_rejects_missing_required_mapping(tmp_path: Path) -> None:
    raw = tmp_path / "raw_tracking.csv"
    tracking = tmp_path / "tracking.csv"
    write_raw_csv(raw)

    completed = run_cmd(
        str(NORMALIZE),
        str(raw),
        "--out",
        str(tracking),
        "--map",
        "time_s=stamp",
    )
    assert completed.returncode == 2
    assert "standard columns need --map or --default" in completed.stderr
    assert not tracking.exists()


def test_tracking_normalizer_rejects_missing_input_column(tmp_path: Path) -> None:
    raw = tmp_path / "raw_tracking.csv"
    tracking = tmp_path / "tracking.csv"
    write_raw_csv(raw)

    completed = run_cmd(
        str(NORMALIZE),
        str(raw),
        "--out",
        str(tracking),
        "--map",
        "time_s=missing_stamp",
        "--map",
        "ref_x_m=rx",
        "--map",
        "ref_y_m=ry",
        "--map",
        "ref_z_m=rz",
        "--map",
        "truth_x_m=gx",
        "--map",
        "truth_y_m=gy",
        "--map",
        "truth_z_m=gz",
    )
    assert completed.returncode == 2
    assert "input CSV is missing mapped columns" in completed.stderr
    assert not tracking.exists()
