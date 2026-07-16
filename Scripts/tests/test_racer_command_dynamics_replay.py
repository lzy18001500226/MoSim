import csv
import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "sunray/audit_racer_command_dynamics_replay.py"


def test_replay_reports_bounded_direction_reversal(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    fieldnames = ["t", "phase", "x", "y", "z", "vx", "vy", "vz", "ax", "ay", "az", "yaw"]
    for uid in range(1, 4):
        with (run_dir / f"uav{uid}_position_cmd.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for index, x in enumerate((0.0, 0.1, 0.2, -10.0, -10.1)):
                writer.writerow(
                    {
                        "t": 100.0 + index * 0.1,
                        "phase": "ego_execute",
                        "x": x,
                        "y": 0.0,
                        "z": 1.2,
                        "vx": 0.0,
                        "vy": 0.0,
                        "vz": 0.0,
                        "ax": 0.0,
                        "ay": 0.0,
                        "az": 0.0,
                        "yaw": 0.0,
                    }
                )

    output = tmp_path / "report.json"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), str(run_dir), "--output", str(output)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["status"] == "passed"
    for vehicle in report["vehicles"]:
        assert vehicle["maxima"]["velocity_mps"] <= 2.0 + 1e-6
        assert vehicle["maxima"]["acceleration_mps2"] <= 1.2 + 1e-6
        assert vehicle["maxima"]["jerk_mps3"] <= 6.0 + 1e-6
