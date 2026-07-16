import csv
import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "sunray/analyze_racer_attitude_events.py"


def test_attitude_event_alignment_reports_tracking_and_controller_demand(tmp_path: Path) -> None:
    fields = {
        "truth": ["t", "phase", "x", "y", "z", "vx", "vy", "vz", "roll", "pitch", "yaw"],
        "odom": ["t", "phase", "x", "y", "z", "vx", "vy", "vz", "roll", "pitch", "yaw"],
        "position_cmd": ["t", "phase", "x", "y", "z", "vx", "vy", "vz", "ax", "ay", "az", "yaw"],
        "raw_position_cmd": ["t", "phase", "x", "y", "z", "vx", "vy", "vz", "ax", "ay", "az", "yaw"],
        "debug_px4ctrl": ["t", "phase", "des_thr", "des_a_x", "des_a_y", "des_a_z"],
    }
    rows = {
        "truth": [100.0, "ego_execute", 0, 0, 1, 1, 0, 0, 0.8, 0.1, 0],
        "odom": [100.01, "ego_execute", 0, 0, 1, 1, 0, 0, 0.8, 0.1, 0],
        "position_cmd": [100.01, "ego_execute", 0.6, 0, 1, 0, 0, 0, 1.2, 0, 0, 0],
        "raw_position_cmd": [100.01, "ego_execute", 1, 0, 1, -1, 0, 0, 0.5, 0, 0, 0],
        "debug_px4ctrl": [100.01, "ego_execute", 0.5, 10, 0, 9.8],
    }
    for uid in range(1, 4):
        for name, header in fields.items():
            with (tmp_path / f"uav{uid}_{name}.csv").open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(header)
                writer.writerow(rows[name])

    output = tmp_path / "report.json"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--output", str(output)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["status"] == "blocked"
    assert report["vehicles"][0]["aligned_tracking"]["position_error_xy_m"] == 0.6
    assert report["vehicles"][0]["aligned_tracking"]["velocity_error_xy_mps"] == 1.0
    assert report["vehicles"][0]["aligned_px4ctrl"]["desired_acceleration_xy_mps2"] == 10.0
