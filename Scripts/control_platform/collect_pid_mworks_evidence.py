#!/usr/bin/env python3
"""Collect reproducible MWORKS MIL evidence for the unified PID fixtures.

Run this file inside Sysplorer through ``call_code(mode="run_script")``.
It intentionally uses the live result APIs and never reconstructs trajectories
offline.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
RESULT_DIR = ROOT / "Results/control_platform/p1_pid_mworks_20260716"
MODEL_DIR = RESULT_DIR / "models"
RAW_DIR = RESULT_DIR / "raw"
METRICS_DIR = RESULT_DIR / "metrics"
LOG_DIR = RESULT_DIR / "logs"

VAR_NAMES = [
    "setpoint_source.y",
    "measurement_source.y",
    "inner_measurement_source.y",
    "feedforward_source.y",
    "schedule_source.y",
    "fuzzy_error_source.y",
    "neural_residual_source.y",
    "command",
    "outer_command",
    "unsaturated_command",
    "integral",
    "scheduled_gain",
    "saturated",
    "status_code",
]

FIXTURES = {
    "cascade_pid": "MoSim_PID_CASCADE_PID_MIL",
    "gain_scheduled_pid": "MoSim_PID_GAIN_SCHEDULED_PID_MIL",
    "fuzzy_pid": "MoSim_PID_FUZZY_PID_MIL",
    "neural_pid": "MoSim_PID_NEURAL_PID_MIL",
    "anti_windup": "MoSim_PID_ANTI_WINDUP_MIL",
    "feedforward_profile": "MoSim_PID_FEEDFORWARD_PROFILE_MIL",
}


def _jsonable(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return str(value)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check_ok(result) -> bool:
    if isinstance(result, bool):
        return result
    if isinstance(result, (int, float)):
        return result == 0 or result == 1
    text = str(result).lower()
    return not any(marker in text for marker in ("error", "failed", "false"))


def main() -> dict:
    for directory in (RAW_DIR, METRICS_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(timezone.utc).isoformat()
    audit = {
        "schema": "mosim.pid_mworks_mil_evidence.v1",
        "source": "MWORKS_MCP",
        "started_at": started_at,
        "live_mworks_touched": True,
        "will_not_click_activation_login": True,
        "activation_reference": str(
            RESULT_DIR / "screenshots/activation/40544_0x11409CE_G9_Family_CFunction_Sysblock - Sysplorer _教育版_.png"
        ),
        "claim_boundary": (
            "Fixed-input scalar MIL evidence for the six unified PID variants. "
            "It does not establish ATTITUDE_THRUST, graphical equivalence, SIL, "
            "Gazebo/PX4/MAVROS, trained neural-network, or complete fuzzy-rule acceptance."
        ),
        "fixtures": {},
    }

    for algorithm_id, model_name in FIXTURES.items():
        model_path = MODEL_DIR / f"{model_name}.mo"
        if not ModelingPy.ClassExist(model_name):
            ModelingPy.OpenModel(str(model_path))

        check_result = ModelingPy.CheckModel(model_name)
        if not _check_ok(check_result):
            raise RuntimeError(f"CheckModel failed for {model_name}: {check_result}")
        simulate_result = ModelingPy.SimulateModel(model_name)
        if not _check_ok(simulate_result):
            raise RuntimeError(f"SimulateModel failed for {model_name}: {simulate_result}")

        times = list(ModelingPy.GetVarTimes())
        columns = [list(values) for values in ModelingPy.GetVarsValues(VAR_NAMES)]
        lengths = {len(times), *(len(values) for values in columns)}
        if lengths != {21}:
            raise RuntimeError(f"unexpected sample lengths for {model_name}: {sorted(lengths)}")
        if not all(math.isfinite(float(value)) for values in columns for value in values):
            raise RuntimeError(f"NaN or Inf found in {model_name}")

        csv_path = RAW_DIR / f"{algorithm_id}.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(["time", *VAR_NAMES])
            writer.writerows(zip(times, *columns))

        by_name = dict(zip(VAR_NAMES, columns))
        status_codes = [int(round(float(value))) for value in by_name["status_code"]]
        metrics = {
            "schema": "mosim.pid_mworks_mil_metrics.v1",
            "algorithm_id": algorithm_id,
            "model_name": model_name,
            "source": "MWORKS_MCP",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sample_count": len(times),
            "time_start": float(times[0]),
            "time_end": float(times[-1]),
            "command_start": float(by_name["command"][0]),
            "command_end": float(by_name["command"][-1]),
            "command_min": min(float(value) for value in by_name["command"]),
            "command_max": max(float(value) for value in by_name["command"]),
            "saturated_sample_count": sum(float(value) > 0.5 for value in by_name["saturated"]),
            "status_codes": sorted(set(status_codes)),
            "finite_values": True,
            "raw_csv": str(csv_path),
        }
        metrics_path = METRICS_DIR / f"{algorithm_id}.json"
        metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
        audit["fixtures"][algorithm_id] = {
            "model_name": model_name,
            "model_path": str(model_path),
            "check_model": _jsonable(check_result),
            "simulate_model": _jsonable(simulate_result),
            "sample_count": len(times),
            "status_codes": metrics["status_codes"],
            "raw_csv": str(csv_path),
            "raw_csv_sha256": _sha256(csv_path),
            "metrics": str(metrics_path),
            "metrics_sha256": _sha256(metrics_path),
        }

    audit["completed_at"] = datetime.now(timezone.utc).isoformat()
    audit_path = LOG_DIR / "mcp_evidence.json"
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "source": audit["source"],
        "fixture_count": len(audit["fixtures"]),
        "evidence_path": str(audit_path),
    }


RUN_SCRIPT_RESULT = main()
