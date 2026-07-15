from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Scripts" / "control_platform" / "factory_injection_replay.py"


def load_module():
    spec = importlib.util.spec_from_file_location("factory_injection_replay", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def command(command_id: str, target: str, value: float, **extra) -> dict:
    return {
        "command_id": command_id,
        "run_id": "run-test",
        "profile_hash": "sha256:test",
        "target": target,
        "requested_at": 1.0,
        "apply_mode": "set",
        "value": value,
        "ramp_s": 0.2,
        "duration_s": 0.0,
        "restore_policy": "manual",
        "source": "pytest",
        **extra,
    }


def test_apply_reject_and_restore(tmp_path: Path) -> None:
    module = load_module()
    restore = command("restore-r2", "motor_effectiveness", 0.0, rotor_index=2)
    restore["apply_mode"] = "restore"
    commands = [
        command("wind", "wind_speed_mps", 5.5),
        command("r2", "motor_effectiveness", 0.65, rotor_index=2),
        command("bad", "motor_effectiveness", 0.5, rotor_index=5),
        restore,
    ]
    report = module.replay(commands, tmp_path)
    assert report["status"] == "passed"
    assert report["command_count"] == 4
    assert report["rejected_count"] == 1
    assert report["final_state"]["wind_speed_mps"] == 5.5
    assert report["final_state"]["motor_effectiveness"] == [1.0, 1.0, 1.0, 1.0]
    events = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    assert {event["event_state"] for event in events} == {"accepted", "applied", "rejected", "restored"}
    with (tmp_path / "curves.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert rows
    assert "safety_intervention" in rows[0]
