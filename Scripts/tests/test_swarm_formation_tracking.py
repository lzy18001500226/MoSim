from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ANALYZER = ROOT / "Scripts/sunray/analyze_swarm_formation_tracking.py"


def write_truth(path: Path, offset_x: float, attitude_deg: float = 5.0) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("t", "phase", "x", "y", "z"))
        writer.writeheader()
        for index in range(40):
            writer.writerow(
                {
                    "t": index * 0.02,
                    "phase": "ego_execute",
                    "x": offset_x + index * 0.01,
                    "y": 0.0,
                    "z": 1.2,
                }
            )


def write_fixture(run_dir: Path, min_distance: float = 2.0, attitude_deg: float = 5.0) -> Path:
    run_dir.mkdir()
    per_uav = {}
    for uid, x in ((1, 0.0), (2, 2.0), (3, 4.0)):
        write_truth(run_dir / f"uav{uid}_truth.csv", x, attitude_deg)
        per_uav[str(uid)] = {
            "target": {"x": x, "y": 0.0, "z": 1.2},
            "phase_peak_summary": {
                "truth": {"ego_execute": {"max_abs_roll_pitch_deg": attitude_deg}}
            },
        }
    metrics = {
        "status": "passed",
        "per_uav": per_uav,
        "min_inter_uav_distance_m": min_distance,
        "inter_uav_emergency_hold": {"trigger_count": 0},
    }
    (run_dir / "EGO_SWARM_METRICS.json").write_text(json.dumps(metrics), encoding="utf-8")
    scenario = run_dir / "scenario.json"
    scenario.write_text(
        json.dumps({"obstacle_crossing_contract": {"direct_center_segment_blocked": True}}),
        encoding="utf-8",
    )
    return scenario


def run_analyzer(run_dir: Path, scenario: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
    completed = subprocess.run(
        [sys.executable, str(ANALYZER), "--run", str(run_dir), "--scenario", str(scenario)],
        text=True,
        capture_output=True,
        check=False,
    )
    packet = json.loads((run_dir / "SWARM_FORMATION_TRACKING_GATE.json").read_text(encoding="utf-8"))
    return completed, packet


def test_tracking_gate_accepts_synchronized_safe_formation(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    scenario = write_fixture(run_dir)
    completed, packet = run_analyzer(run_dir, scenario)
    assert completed.returncode == 0
    assert packet["status"] == "passed"
    assert math.isclose(packet["formation_error"]["rmse_m"], 0.0, abs_tol=1e-12)


def test_tracking_gate_rejects_distance_attitude_and_emergency_hold(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    scenario = write_fixture(run_dir, min_distance=0.9, attitude_deg=46.0)
    metrics_path = run_dir / "EGO_SWARM_METRICS.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metrics["inter_uav_emergency_hold"]["trigger_count"] = 1
    metrics_path.write_text(json.dumps(metrics), encoding="utf-8")
    completed, packet = run_analyzer(run_dir, scenario)
    assert completed.returncode == 1
    assert "inter_uav_distance_below_gate" in packet["blockers"]
    assert "execute_truth_roll_pitch_above_gate" in packet["blockers"]
    assert "inter_uav_emergency_hold_triggered" in packet["blockers"]
