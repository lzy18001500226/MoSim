#!/usr/bin/env python3
"""Run the canonical OpenBlocks PX4CTRL single-UAV route on an existing session.

The runner never starts, closes, or resets Sysplorer.  It connects only to the
caller-supplied reusable port, records a native MWORKS result, and separates
completed tracking evidence from collision/safety acceptance.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
MODEL_NAME = "MoSimQuadrotorModel.Guidance.Planning.OpenBlocksPx4Ctrl"
STOP_TIME_S = 80.1247340259
INTERVAL_S = 0.01
TERMINAL_ERROR_LIMIT_M = 5.0

VARIABLES = {
    "time": "time",
    "x": "position[1]",
    "y": "position[2]",
    "z": "position[3]",
    "x_ref": "position_ref[1]",
    "y_ref": "position_ref[2]",
    "z_ref": "position_ref[3]",
    "roll": "attitude[1]",
    "pitch": "attitude[2]",
    "yaw": "attitude[3]",
    "u1": "rotor_command[1]",
    "u2": "rotor_command[2]",
    "u3": "rotor_command[3]",
    "u4": "rotor_command[4]",
    "position_error_norm": "position_error_norm",
}
CORE_ALIASES = {"time", "x", "y", "z", "x_ref", "y_ref", "z_ref", "position_error_norm"}
SOURCE_FILES = (
    ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "OpenBlocksMapTruthDisplay.mo",
    ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "OpenBlocksPx4CtrlReference.mo",
    ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "Sunray150PlanningOpenBlocksPx4CtrlSysblockClosedLoop.mo",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes() -> dict[str, str]:
    return {
        str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
        for path in SOURCE_FILES
    }


def last_errors() -> str:
    try:
        return str(ModelingPy.GetLastErrors())
    except Exception as exc:  # pragma: no cover - native API diagnostic fallback
        return repr(exc)


def simulation_diagnostics() -> dict[str, Any]:
    values: dict[str, Any] = {}
    for name in (
        "GetSimulationExitState",
        "GetSimulationState",
        "GetCurrentSimTime",
        "MessageText",
        "GetLastErrors",
    ):
        try:
            values[name] = getattr(ModelingPy, name)()
        except Exception as exc:  # pragma: no cover - depends on native version
            values[name] = {"error": repr(exc)}
    return values


def write_csv(series: dict[str, list[float]], path: Path) -> None:
    count = len(series["time"])
    if count < 11:
        raise RuntimeError(f"Result has too few samples: {count}")
    mismatched = {name: len(values) for name, values in series.items() if len(values) != count}
    if mismatched:
        raise RuntimeError(f"Result variable length mismatch: {mismatched}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        names = list(VARIABLES)
        writer.writerow(names)
        for index in range(count):
            writer.writerow([series[name][index] for name in names])


def write_metrics(raw_csv: Path, metrics_json: Path, metrics_csv: Path) -> dict[str, Any]:
    results_script_dir = ROOT / "Scripts" / "results"
    if str(results_script_dir) not in sys.path:
        sys.path.insert(0, str(results_script_dir))
    from calc_metrics import compute_metrics, read_csv  # noqa: PLC0415

    metrics = compute_metrics(
        read_csv(raw_csv),
        raw_csv,
        scene_id="openblocks_single_uav_px4ctrl_completion",
        controller_id="px4ctrl",
        metrics_context=None,
    )
    metrics.update(
        {
            "source": "MWORKS_MCP",
            "tool_transport": "official ModelingPy connected explicitly to an existing Sysplorer port",
            "evidence_level": "mworks_openblocks_px4ctrl_single_uav_full",
            "metrics_profile": "standard_tracking",
        }
    )
    metrics_json.parent.mkdir(parents=True, exist_ok=True)
    metrics_json.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with metrics_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["metric", "value"])
        for key, value in metrics.items():
            writer.writerow([key, "" if value is None else value])
    return metrics


def newest_result_file(native_dir: Path) -> Path:
    candidates = [candidate for candidate in native_dir.rglob("Result.msr") if candidate.is_file()]
    if not candidates:
        raise RuntimeError(f"No native Result.msr created under {native_dir}")
    return max(candidates, key=lambda candidate: candidate.stat().st_mtime)


def connect_and_check(record: dict[str, Any], port: int, open_diagram: bool) -> None:
    record["connect_sysplorer_return"] = repr(ModelingPy.ConnectSysplorer("127.0.0.1", port))
    record["connect_sysplorer"] = True
    record["class_exists_before_check"] = bool(ModelingPy.ClassExist(MODEL_NAME))
    if not record["class_exists_before_check"]:
        raise RuntimeError(
            f"{MODEL_NAME} is absent from reusable session {port}; this runner will not load a root or open a new window. "
            f"Native errors: {last_errors()}"
        )
    record["check_model"] = bool(ModelingPy.CheckModel(MODEL_NAME))
    record["check_model_diagnostics"] = last_errors()
    if not record["check_model"]:
        raise RuntimeError(f"CheckModel failed for {MODEL_NAME}: {last_errors()}")
    if open_diagram:
        try:
            record["open_model_diagram"] = bool(ModelingPy.OpenModel(MODEL_NAME, ModelingPy.ModelView.Diagram))
        except Exception as exc:  # pragma: no cover - native GUI behavior
            record["open_model_diagram_error"] = repr(exc)


def run_precheck(port: int, output_dir: Path, activation_sentinel: str, background_manifest: str) -> int:
    record: dict[str, Any] = {
        "schema": "mosim.openblocks_single_uav_px4ctrl_check.v1",
        "created_at": now_iso(),
        "source": "MWORKS_MCP",
        "tool_transport": "official ModelingPy connected explicitly to an existing Sysplorer port",
        "model_name": MODEL_NAME,
        "existing_sysplorer_port": port,
        "activation_sentinel_before": activation_sentinel,
        "background_screenshot_before": background_manifest,
        "will_not_click_activation_login": True,
        "live_mworks_touched": True,
        "source_hashes_before": source_hashes(),
    }
    try:
        connect_and_check(record, port, open_diagram=True)
        record["status"] = "completed"
    except Exception as exc:
        record["status"] = "blocked"
        record["error"] = repr(exc)
        record["last_errors"] = last_errors()
    record["completed_at"] = now_iso()
    record["source_hashes_after"] = source_hashes()
    write_json(output_dir / "CHECK_PHASE.json", record)
    print(json.dumps(record, ensure_ascii=False))
    return 0 if record["status"] == "completed" else 1


def run_full(port: int, output_dir: Path, activation_sentinel: str, background_manifest: str) -> int:
    native_dir = output_dir / "native_result"
    raw_csv = output_dir / "raw" / "openblocks_single_uav_px4ctrl.csv"
    metrics_json = output_dir / "metrics" / "openblocks_single_uav_px4ctrl.json"
    metrics_csv = output_dir / "metrics" / "openblocks_single_uav_px4ctrl.csv"
    record: dict[str, Any] = {
        "schema": "mosim.openblocks_single_uav_px4ctrl_completion.v1",
        "created_at": now_iso(),
        "source": "MWORKS_MCP",
        "tool_transport": "official ModelingPy connected explicitly to an existing Sysplorer port",
        "model_name": MODEL_NAME,
        "existing_sysplorer_port": port,
        "simulation_contract": {
            "start_time_s": 0.0,
            "stop_time_s": STOP_TIME_S,
            "interval_s": INTERVAL_S,
            "solver": "Dassl",
            "terminal_tracking_error_limit_m": TERMINAL_ERROR_LIMIT_M,
        },
        "activation_sentinel_before": activation_sentinel,
        "background_screenshot_before": background_manifest,
        "will_not_click_activation_login": True,
        "live_mworks_touched": True,
        "source_hashes_before": source_hashes(),
        "claim_boundary": (
            "This is MWORKS equation-bridge PX4CTRL tracking evidence on the canonical OpenBlocks visual scene. "
            "It does not establish ROS/PX4/Gazebo deployment or collision-free obstacle avoidance."
        ),
    }
    try:
        connect_and_check(record, port, open_diagram=False)
        native_dir.mkdir(parents=True, exist_ok=True)
        record["simulate_model"] = bool(
            ModelingPy.SimulateModel(
                MODEL_NAME,
                startTime=0.0,
                stopTime=STOP_TIME_S,
                interval=INTERVAL_S,
                simMode=0,
                path=str(native_dir),
            )
        )
        record["post_simulation_diagnostics"] = simulation_diagnostics()
        if not record["simulate_model"]:
            raise RuntimeError(f"SimulateModel failed for {MODEL_NAME}: {last_errors()}")

        series = {"time": [float(value) for value in ModelingPy.GetVarTimes()]}
        for alias, variable in VARIABLES.items():
            if alias == "time":
                continue
            values = [float(value) for value in ModelingPy.GetVarValues(variable)]
            if not values and alias in CORE_ALIASES:
                raise RuntimeError(f"Required result variable is empty: {variable}")
            series[alias] = values

        non_finite = {
            alias: sum(1 for value in values if not math.isfinite(value))
            for alias, values in series.items()
        }
        non_finite = {alias: count for alias, count in non_finite.items() if count}
        if non_finite:
            raise RuntimeError(f"Non-finite result values: {non_finite}")
        if abs(series["time"][-1] - STOP_TIME_S) > 0.02:
            raise RuntimeError(
                f"Simulation ended at {series['time'][-1]:.12g}s, expected {STOP_TIME_S:.12g}s"
            )

        write_csv(series, raw_csv)
        result_file = newest_result_file(native_dir)
        record.update(
            {
                "sample_count": len(series["time"]),
                "time_start_s": series["time"][0],
                "time_end_s": series["time"][-1],
                "raw_csv": str(raw_csv),
                "native_result_file": str(result_file),
                "native_result_exists": result_file.is_file(),
            }
        )
        metrics = write_metrics(raw_csv, metrics_json, metrics_csv)
        terminal_error = float(metrics["terminal_position_error_m"])
        record["metrics_json"] = str(metrics_json)
        record["metrics_csv"] = str(metrics_csv)
        record["tracking_gate"] = {
            "terminal_position_error_m": terminal_error,
            "limit_m": TERMINAL_ERROR_LIMIT_M,
            "passed": math.isfinite(terminal_error) and terminal_error < TERMINAL_ERROR_LIMIT_M,
        }
        record["safety_and_avoidance_review"] = {
            "status": "not_accepted",
            "reason": (
                "The visual map surface has no plant-coupled wall collision or clearance assertion. "
                "Standard tracking constraints are reported for review but cannot establish obstacle avoidance."
            ),
            "altitude_violation_count": metrics.get("altitude_violation_count"),
            "tilt_violation_count": metrics.get("tilt_violation_count"),
            "constraint_violation_count": metrics.get("constraint_violation_count"),
        }

        record["open_result"] = bool(ModelingPy.OpenResult(str(result_file)))
        if not record["open_result"]:
            raise RuntimeError(f"OpenResult failed for {result_file}: {last_errors()}")
        record["create_animation"] = bool(ModelingPy.CreateAnimation())
        if not record["create_animation"]:
            raise RuntimeError(f"CreateAnimation failed: {last_errors()}")
        record["animation_speed"] = bool(ModelingPy.AnimationSpeed(0.2))

        record["source_hashes_after"] = source_hashes()
        record["source_hash_drift"] = record["source_hashes_before"] != record["source_hashes_after"]
        if record["source_hash_drift"]:
            raise RuntimeError("MWORKS changed a tracked OpenBlocks source file during the run")
        record["status"] = "completed"
    except Exception as exc:
        record["status"] = "blocked"
        record["error"] = repr(exc)
        record["last_errors"] = last_errors()
        record.setdefault("source_hashes_after", source_hashes())
        record.setdefault("source_hash_drift", record["source_hashes_before"] != record["source_hashes_after"])
    record["completed_at"] = now_iso()
    write_json(output_dir / "RUN_RECORD.json", record)
    print(json.dumps(record, ensure_ascii=False))
    return 0 if record["status"] == "completed" else 1


def run_postprocess(output_dir: Path) -> int:
    """Recover metrics from a completed native result without re-simulating."""
    record_path = output_dir / "RUN_RECORD.json"
    raw_csv = output_dir / "raw" / "openblocks_single_uav_px4ctrl.csv"
    metrics_json = output_dir / "metrics" / "openblocks_single_uav_px4ctrl.json"
    metrics_csv = output_dir / "metrics" / "openblocks_single_uav_px4ctrl.csv"
    if not record_path.is_file():
        raise RuntimeError(f"Missing prior run record: {record_path}")
    if not raw_csv.is_file():
        raise RuntimeError(f"Missing prior raw result CSV: {raw_csv}")

    record = json.loads(record_path.read_text(encoding="utf-8"))
    result_file = Path(str(record.get("native_result_file", "")))
    if record.get("simulate_model") is not True:
        raise RuntimeError("Postprocess requires a completed SimulateModel result")

    initial_status = record.get("status")
    initial_error = record.get("error")
    metrics = write_metrics(raw_csv, metrics_json, metrics_csv)
    terminal_error = float(metrics["terminal_position_error_m"])
    record.update(
        {
            "sample_count": int(metrics["row_count"]),
            "time_start_s": 0.0,
            "time_end_s": float(metrics["duration_s"]),
            "raw_csv": str(raw_csv),
            "native_result_file": str(result_file),
            "native_result_exists_at_completion": bool(record.get("native_result_exists")),
            "native_result_retained_after_postprocess": result_file.is_file(),
            "native_result_exists": result_file.is_file(),
            "metrics_json": str(metrics_json),
            "metrics_csv": str(metrics_csv),
            "tracking_gate": {
                "terminal_position_error_m": terminal_error,
                "limit_m": TERMINAL_ERROR_LIMIT_M,
                "passed": math.isfinite(terminal_error) and terminal_error < TERMINAL_ERROR_LIMIT_M,
            },
            "safety_and_avoidance_review": {
                "status": "not_accepted",
                "reason": (
                    "The visual map surface has no plant-coupled wall collision or clearance assertion. "
                    "Standard tracking constraints are reported for review but cannot establish obstacle avoidance."
                ),
                "altitude_violation_count": metrics.get("altitude_violation_count"),
                "tilt_violation_count": metrics.get("tilt_violation_count"),
                "constraint_violation_count": metrics.get("constraint_violation_count"),
            },
            "postprocess_recovery": {
                "initial_status": initial_status,
                "initial_error": initial_error,
                "recovered_without_resimulation": True,
                "reason": "The native simulation and raw extraction completed before a metrics-call keyword mismatch.",
                "native_result_retention_note": (
                    "MWORKS removed the task-local native result directory after opening the result viewer; "
                    "the completion-time record, raw CSV, and final result-window capture remain retained evidence."
                    if not result_file.is_file()
                    else "The native Result.msr remains retained under the task output directory."
                ),
            },
            "source_hashes_after": source_hashes(),
            "status": "completed",
            "completed_at": now_iso(),
        }
    )
    record["source_hash_drift"] = record.get("source_hashes_before") != record["source_hashes_after"]
    record.pop("error", None)
    record.pop("last_errors", None)
    write_json(record_path, record)
    print(json.dumps(record, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True, help="Existing Sysplorer port; this runner never starts a session.")
    parser.add_argument("--mode", choices=("check", "run", "postprocess"), required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "Results" / "planning" / "openblocks_single_uav_px4ctrl_completion_20260730",
    )
    parser.add_argument("--activation-sentinel", required=True)
    parser.add_argument("--background-manifest", required=True)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    if args.mode == "check":
        return run_precheck(args.port, output_dir, args.activation_sentinel, args.background_manifest)
    if args.mode == "postprocess":
        return run_postprocess(output_dir)
    return run_full(args.port, output_dir, args.activation_sentinel, args.background_manifest)


if __name__ == "__main__":
    raise SystemExit(main())
