from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Scripts" / "control_platform" / "offline_runtime_adapter.py"


def load_module():
    spec = importlib.util.spec_from_file_location("offline_runtime_adapter", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_offline_lifecycle_and_injection() -> None:
    module = load_module()
    platform = module.OfflineControlPlatform()
    validation = platform.validate_profile("Config/profiles/experiments/g9_official_pid_figure8_v1.json", "validate-1")
    assert validation["accepted"] is True
    assert validation["lifecycle_state"] == "ready"
    started = platform.start("start-1", "offline-test", validation["profile_hash"])
    assert started["accepted"] is True
    command = {
        "request_id": "inject-1",
        "command_id": "inject-1",
        "run_id": "offline-test",
        "profile_hash": validation["profile_hash"],
        "target": "motor_effectiveness",
        "requested_at": 1.0,
        "apply_mode": "set",
        "value": 0.65,
        "rotor_index": 2,
        "ramp_s": 0.0,
        "duration_s": 0.0,
        "restore_policy": "manual",
        "source": "pytest",
    }
    applied = platform.apply_injection(command)
    assert applied["accepted"] is True
    assert applied["injection_state"]["motor_effectiveness"][1] == 0.65
    stopped = platform.stop("stop-1")
    assert stopped["accepted"] is True
    assert stopped["runtime_started"] is False
