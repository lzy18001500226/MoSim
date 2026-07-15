from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREPARE = ROOT / "Scripts" / "quality" / "prepare_experiment_run.py"
COMPUTE = ROOT / "Scripts" / "quality" / "compute_tracking_metrics.py"
THRESHOLDS = ROOT / "Scripts" / "quality" / "check_metric_thresholds.py"
VALID_PROFILE = ROOT / "Config" / "profiles" / "experiments" / "px4ctrl_takeoff_hover_land_v1.json"
FASTLIO_PROFILE = ROOT / "Config" / "profiles" / "experiments" / "fastlio_independent_eval_figure8_v1.json"


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


def write_tracking(path: Path, high_error: bool = False) -> None:
    truth_z = "1.200" if high_error else "0.995"
    path.write_text(
        "\n".join(
            [
                "time_s,phase,ref_x_m,ref_y_m,ref_z_m,truth_x_m,truth_y_m,truth_z_m,saturated",
                "0.00,takeoff,0,0,0.0,0.000,0.000,0.000,0",
                "0.01,takeoff,0,0,0.5,0.005,0.000,0.490,0",
                f"0.02,hover,0,0,1.0,0.004,0.003,{truth_z},0",
                f"0.03,hover,0,0,1.0,0.004,0.003,{truth_z},0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def make_metrics(tmp_path: Path, high_error: bool = False) -> Path:
    run_id = "pytest_threshold_px4ctrl"
    prepared = run_cmd(str(PREPARE), str(VALID_PROFILE), "--run-id", run_id, "--output-root", str(tmp_path))
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    run_dir = tmp_path / run_id
    write_tracking(run_dir / "tracking.csv", high_error=high_error)
    computed = run_cmd(
        str(COMPUTE),
        str(run_dir / "tracking.csv"),
        "--manifest",
        str(run_dir / "RUN_MANIFEST.json"),
        "--out",
        str(run_dir / "metrics.json"),
    )
    assert computed.returncode == 0, computed.stdout + computed.stderr
    return run_dir


def write_localization(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "stamp,seq,estimate_x,estimate_y,estimate_z,truth_x,truth_y,truth_z,estimate_vx,estimate_vy,estimate_vz,truth_vx,truth_vy,truth_vz,estimate_yaw_rad,truth_yaw_rad,delay_s",
                "0.00,10,0.001,0.000,0.000,0.000,0.000,0.000,0.01,0.00,0.00,0.00,0.00,0.00,0.001,0.000,0.010",
                "0.10,11,0.101,0.002,0.000,0.100,0.000,0.000,1.01,0.02,0.00,1.00,0.00,0.00,0.002,0.000,0.012",
                "0.20,12,0.201,0.002,0.000,0.200,0.000,0.000,1.01,0.01,0.00,1.00,0.00,0.00,0.003,0.000,0.011",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_map_summary(path: Path) -> None:
    path.write_text('{"map_completeness": 0.92}\n', encoding="utf-8")


def test_metric_threshold_gate_accepts_baseline_metrics(tmp_path: Path) -> None:
    run_dir = make_metrics(tmp_path)
    completed = run_cmd(str(THRESHOLDS), str(run_dir / "metrics.json"), "--manifest", str(run_dir / "RUN_MANIFEST.json"))
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["accepted"] is True
    assert all(item["passed"] for item in report["results"])


def test_metric_threshold_gate_rejects_high_error_metrics(tmp_path: Path) -> None:
    run_dir = make_metrics(tmp_path, high_error=True)
    completed = run_cmd(str(THRESHOLDS), str(run_dir / "metrics.json"), "--manifest", str(run_dir / "RUN_MANIFEST.json"))
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["accepted"] is False
    assert any(error["code"] == "T-FAIL-01" for error in report["errors"])


def test_metric_threshold_gate_accepts_fastlio_localization_metrics(tmp_path: Path) -> None:
    run_id = "pytest_threshold_fastlio_eval"
    prepared = run_cmd(str(PREPARE), str(FASTLIO_PROFILE), "--run-id", run_id, "--output-root", str(tmp_path))
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    run_dir = tmp_path / run_id
    localization = run_dir / "raw" / "localization.csv"
    map_summary = run_dir / "raw" / "map_summary.json"
    localization.parent.mkdir(parents=True, exist_ok=True)
    write_localization(localization)
    write_map_summary(map_summary)

    computed = run_cmd(
        str(COMPUTE),
        "--localization-csv",
        str(localization),
        "--map-summary-json",
        str(map_summary),
        "--manifest",
        str(run_dir / "RUN_MANIFEST.json"),
        "--out",
        str(run_dir / "metrics.json"),
    )
    assert computed.returncode == 0, computed.stdout + computed.stderr
    packet = json.loads(computed.stdout)
    assert set(packet["metrics"]) == {
        "ate",
        "rpe",
        "pose_error",
        "velocity_error",
        "delay",
        "drop_rate",
        "map_completeness",
    }

    completed = run_cmd(str(THRESHOLDS), str(run_dir / "metrics.json"), "--manifest", str(run_dir / "RUN_MANIFEST.json"))
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["accepted"] is True
