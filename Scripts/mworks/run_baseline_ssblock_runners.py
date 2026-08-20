#!/usr/bin/env python3
"""Run the two graphical-Sysblock baseline runners on one existing Sysplorer port."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import mworks.sysplorer as ModelingPy


ROOT = Path(__file__).resolve().parents[2]
ROOT_CLASS = "MoSimQuadrotorModel"
PACKAGE_FILE = ROOT / "Models" / ROOT_CLASS / "package.mo"
TERMINAL_ERROR_LIMIT_M = 5.0

CHECK_TARGETS = {
    "official_pid_core": "MoSimQuadrotorModel.Control.PID.OfficialPidGraphicalCore",
    "shared_mapper": "MoSimQuadrotorModel.Control.PID.BaselineRotorMapper",
    "px4ctrl_outer_loop": "MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlOuterLoopGraphicalSysblock",
    "px4ctrl_core": "MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlBaselineCore",
    "official_pid_runner": "MoSimQuadrotorModel.Experiment.Baselines.OfficialPidRunner",
    "px4ctrl_runner": "MoSimQuadrotorModel.Experiment.Px4Ctrl.Px4CtrlRunner",
}

DIAGRAM_TARGETS = {
    "official_pid_runner": CHECK_TARGETS["official_pid_runner"],
    "official_pid_core": CHECK_TARGETS["official_pid_core"],
    "shared_mapper": CHECK_TARGETS["shared_mapper"],
    "px4ctrl_outer_loop": CHECK_TARGETS["px4ctrl_outer_loop"],
    "px4ctrl_core": CHECK_TARGETS["px4ctrl_core"],
    "px4ctrl_runner": CHECK_TARGETS["px4ctrl_runner"],
}

RUNNERS = {
    "official_pid": CHECK_TARGETS["official_pid_runner"],
    "px4ctrl": CHECK_TARGETS["px4ctrl_runner"],
}

VARIABLES = {
    "time": "time",
    "position_error_norm": "position_error_norm",
    "position_x_m": "position[1]",
    "position_y_m": "position[2]",
    "position_z_m": "position[3]",
    "reference_x_m": "position_ref[1]",
    "reference_y_m": "position_ref[2]",
    "reference_z_m": "position_ref[3]",
    "roll_rad": "attitude[1]",
    "pitch_rad": "attitude[2]",
    "yaw_rad": "attitude[3]",
    "rotor_command_1": "rotor_command[1]",
    "rotor_command_2": "rotor_command[2]",
    "rotor_command_3": "rotor_command[3]",
    "rotor_command_4": "rotor_command[4]",
    "rotor_speed_1": "rotor_speed[1]",
    "rotor_speed_2": "rotor_speed[2]",
    "rotor_speed_3": "rotor_speed[3]",
    "rotor_speed_4": "rotor_speed[4]",
    "esc_saturation_ratio": "esc_saturation_ratio",
}

SOURCE_FILES = (
    ROOT / "Models/MoSimQuadrotorModel/Control/PID/OfficialPidGraphicalCore.mo",
    ROOT / "Models/MoSimQuadrotorModel/Control/PID/BaselineRotorMapper.mo",
    ROOT / "Models/MoSimQuadrotorModel/Control/Px4Ctrl/Px4CtrlOuterLoopGraphicalSysblock.mo",
    ROOT / "Models/MoSimQuadrotorModel/Control/Px4Ctrl/Px4CtrlBaselineCore.mo",
    ROOT / "Models/MoSimQuadrotorModel/Control/PID/package.mo",
    ROOT / "Models/MoSimQuadrotorModel/Control/PID/package.order",
    ROOT / "Models/MoSimQuadrotorModel/Control/Px4Ctrl/package.mo",
    ROOT / "Models/MoSimQuadrotorModel/Control/Px4Ctrl/package.order",
    ROOT / "Models/MoSimQuadrotorModel/Experiment/Baselines/OfficialPidRunner.mo",
    ROOT / "Models/MoSimQuadrotorModel/Experiment/Px4Ctrl/Px4CtrlRunner.mo",
    ROOT / "Models/MoSimQuadrotorModel/Experiment/Baselines/ScheduledRotorEfficiencyCompensator.mo",
    ROOT / "Models/MoSimQuadrotorModel/Experiment/Baselines/package.mo",
    ROOT / "Models/MoSimQuadrotorModel/Experiment/Baselines/package.order",
    ROOT / "Models/MoSimQuadrotorModel/Experiment/Px4Ctrl/package.mo",
    ROOT / "Models/MoSimQuadrotorModel/Experiment/Px4Ctrl/package.order",
)


def now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes() -> dict[str, str]:
    return {relative(path): sha256(path) for path in SOURCE_FILES}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def last_errors() -> str:
    try:
        return str(ModelingPy.GetLastErrors())
    except Exception as exc:  # pragma: no cover - native API fallback
        return repr(exc)


def artifact(path: Path, role: str) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return {
        "path": relative(path),
        "role": role,
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }


def find_native_result(native_dir: Path) -> Path:
    candidates = [path for path in native_dir.rglob("Result.msr") if path.is_file()]
    if not candidates:
        raise RuntimeError(f"No Result.msr was written below {native_dir}")
    return max(candidates, key=lambda path: path.stat().st_mtime_ns)


def refresh_current_root(port: int) -> dict[str, Any]:
    result = {
        "existing_sysplorer_port": port,
        "connect_sysplorer_return": repr(ModelingPy.ConnectSysplorer(port=port)),
    }
    result["root_present_before_refresh"] = bool(ModelingPy.ClassExist(ROOT_CLASS))
    if result["root_present_before_refresh"]:
        result["erase_root"] = bool(ModelingPy.EraseClasses((ROOT_CLASS,)))
        if not result["erase_root"]:
            raise RuntimeError(f"Targeted root unload failed: {last_errors()}")
    else:
        result["erase_root"] = None
    result["open_package_file"] = bool(ModelingPy.OpenModelFile(str(PACKAGE_FILE)))
    if not result["open_package_file"]:
        raise RuntimeError(f"OpenModelFile failed for {PACKAGE_FILE}: {last_errors()}")
    return result


def check_targets() -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for label, model_name in CHECK_TARGETS.items():
        exists = bool(ModelingPy.ClassExist(model_name))
        result = {
            "model_name": model_name,
            "class_exists": exists,
            "check_model": False,
            "last_errors": "",
        }
        if exists:
            result["check_model"] = bool(ModelingPy.CheckModel(model_name))
            result["last_errors"] = last_errors()
        results[label] = result
        if not exists or not result["check_model"]:
            raise RuntimeError(f"CheckModel failed for {model_name}: {result['last_errors']}")
    return results


def export_diagrams(output_dir: Path) -> dict[str, dict[str, Any]]:
    diagram_dir = output_dir / "diagrams"
    diagram_dir.mkdir(parents=True, exist_ok=True)
    exports: dict[str, dict[str, Any]] = {}
    for label, model_name in DIAGRAM_TARGETS.items():
        output = diagram_dir / f"{label}_after_check.png"
        open_ok = bool(ModelingPy.OpenModel(model_name, ModelingPy.ModelView.Diagram))
        export_ok = bool(ModelingPy.ExportDiagram(model_name, str(output), 3000, 1900))
        exports[label] = {
            "model_name": model_name,
            "open_diagram": open_ok,
            "export_diagram": export_ok,
            "path": relative(output),
            "last_errors": last_errors(),
        }
        if not open_ok or not export_ok or not output.is_file():
            raise RuntimeError(f"Diagram export failed for {model_name}: {last_errors()}")
    return exports


def read_series() -> dict[str, list[float]]:
    series: dict[str, list[float]] = {}
    for label, variable in VARIABLES.items():
        values = [float(value) for value in (ModelingPy.GetVarTimes() if label == "time" else ModelingPy.GetVarValues(variable))]
        if not values:
            raise RuntimeError(f"Required result series is empty: {variable}")
        series[label] = values
    row_count = len(series["time"])
    inconsistent = {label: len(values) for label, values in series.items() if len(values) != row_count}
    if inconsistent:
        raise RuntimeError(f"Result series lengths differ: {inconsistent}")
    non_finite = {
        label: sum(1 for value in values if not math.isfinite(value))
        for label, values in series.items()
    }
    non_finite = {label: count for label, count in non_finite.items() if count}
    if non_finite:
        raise RuntimeError(f"Result contains non-finite values: {non_finite}")
    return series


def write_csv(series: dict[str, list[float]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(VARIABLES)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(fields)
        for index in range(len(series["time"])):
            writer.writerow([series[field][index] for field in fields])


def metrics_for(series: dict[str, list[float]], *, model_name: str, stop_time_s: float, interval_s: float) -> dict[str, Any]:
    time_values = series["time"]
    errors = series["position_error_norm"]
    tail_start = max(time_values) - 5.0
    tail_errors = [error for time_value, error in zip(time_values, errors) if time_value >= tail_start]
    rotor_commands = [
        value
        for name in ("rotor_command_1", "rotor_command_2", "rotor_command_3", "rotor_command_4")
        for value in series[name]
    ]
    saturation = series["esc_saturation_ratio"]
    terminal_error = errors[-1]
    time_reaches_requested_stop = abs(time_values[-1] - stop_time_s) <= max(0.02, interval_s * 1.1)
    return {
        "schema_version": "mosim.baseline_ssblock_runner.metrics.v1",
        "generated_at": now_iso(),
        "source": "MWORKS_MCP",
        "tool_transport": "official ModelingPy bound to an explicit existing Sysplorer port",
        "model_name": model_name,
        "sample_count": len(time_values),
        "time_start_s": time_values[0],
        "time_end_s": time_values[-1],
        "requested_stop_time_s": stop_time_s,
        "requested_interval_s": interval_s,
        "position_error_norm_rmse_m": math.sqrt(sum(error * error for error in errors) / len(errors)),
        "position_error_norm_max_m": max(errors),
        "terminal_position_error_m": terminal_error,
        "tail_position_error_rmse_m": math.sqrt(sum(error * error for error in tail_errors) / len(tail_errors)),
        "max_abs_rotor_command": max(abs(value) for value in rotor_commands),
        "esc_saturation_ratio_max": max(saturation),
        "esc_saturation_ratio_final": saturation[-1],
        "finite": True,
        "completion_gates": {
            "more_than_ten_samples": len(time_values) > 10,
            "time_reaches_requested_stop": time_reaches_requested_stop,
            "terminal_position_error_lt_5m": terminal_error < TERMINAL_ERROR_LIMIT_M,
        },
    }


def run_runner(label: str, model_name: str, output_dir: Path, stop_time_s: float, interval_s: float) -> dict[str, Any]:
    native_dir = output_dir / "native" / label
    raw_csv = output_dir / "raw" / f"{label}_50s.csv"
    metrics_path = output_dir / "metrics" / f"{label}_50s.json"
    native_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "model_name": model_name,
        "class_exists": bool(ModelingPy.ClassExist(model_name)),
        "requested_stop_time_s": stop_time_s,
        "requested_interval_s": interval_s,
    }
    if not result["class_exists"]:
        raise RuntimeError(f"Runner is absent after root reload: {model_name}: {last_errors()}")
    result["check_model"] = bool(ModelingPy.CheckModel(model_name))
    result["check_model_last_errors"] = last_errors()
    if not result["check_model"]:
        raise RuntimeError(f"CheckModel failed for {model_name}: {result['check_model_last_errors']}")

    result["simulate_model"] = bool(
        ModelingPy.SimulateModel(
            model_name,
            startTime=0.0,
            stopTime=stop_time_s,
            interval=interval_s,
            simMode=0,
            path=str(native_dir),
        )
    )
    result["simulate_model_last_errors"] = last_errors()
    if not result["simulate_model"]:
        raise RuntimeError(f"SimulateModel failed for {model_name}: {result['simulate_model_last_errors']}")

    series = read_series()
    if abs(series["time"][-1] - stop_time_s) > max(0.02, interval_s * 1.1):
        raise RuntimeError(f"{model_name} ended at {series['time'][-1]:.12g}s, expected {stop_time_s:.12g}s")
    write_csv(series, raw_csv)
    metrics = metrics_for(series, model_name=model_name, stop_time_s=stop_time_s, interval_s=interval_s)
    write_json(metrics_path, metrics)
    native_result = find_native_result(native_dir)
    if not all(metrics["completion_gates"].values()):
        raise RuntimeError(f"{model_name} completed but failed result gates: {metrics['completion_gates']}")
    result.update(
        {
            "sample_count": len(series["time"]),
            "time_start_s": series["time"][0],
            "time_end_s": series["time"][-1],
            "raw_csv": relative(raw_csv),
            "metrics": relative(metrics_path),
            "native_result": relative(native_result),
            "terminal_position_error_m": metrics["terminal_position_error_m"],
            "position_error_norm_rmse_m": metrics["position_error_norm_rmse_m"],
        }
    )
    return result


def run(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = args.output_dir.resolve()
    record: dict[str, Any] = {
        "schema_version": "mosim.baseline_ssblock_runner.evidence.v1",
        "created_at": now_iso(),
        "status": "failed",
        "source": "MWORKS_MCP",
        "tool_transport": "official ModelingPy bound to an explicit existing Sysplorer port",
        "existing_sysplorer_port": args.port,
        "activation_sentinel_before": relative(args.activation_sentinel.resolve()),
        "will_not_click_activation_login": True,
        "live_mworks_touched": True,
        "fault_injection_boundary": "Both runners retain fault_start_s=1e9 by default; no motor-efficiency fault is injected in this run.",
        "source_hashes_before": source_hashes(),
        "artifact_refs": [],
    }
    try:
        record["session_refresh"] = refresh_current_root(args.port)
        record["check_model"] = check_targets()
        record["diagram_exports_after_check"] = export_diagrams(output_dir)
        for label, model_name in RUNNERS.items():
            record[label] = run_runner(label, model_name, output_dir, args.stop_time, args.interval)
        record["status"] = "pass"
    except Exception as exc:
        record["error"] = repr(exc)
        record["last_errors"] = last_errors()
    finally:
        record["source_hashes_after"] = source_hashes()
        record["source_hash_drift"] = record["source_hashes_before"] != record["source_hashes_after"]
        if record["status"] == "pass" and record["source_hash_drift"]:
            record["status"] = "source_hash_drift"
        artifact_paths = [(args.activation_sentinel.resolve(), "activation_sentinel")]
        artifact_paths.extend((output_dir / "diagrams" / f"{label}_after_check.png", "diagram") for label in DIAGRAM_TARGETS)
        for label in RUNNERS:
            artifact_paths.extend(
                (
                    (output_dir / "raw" / f"{label}_50s.csv", "raw"),
                    (output_dir / "metrics" / f"{label}_50s.json", "metrics"),
                )
            )
            native_relative = record.get(label, {}).get("native_result")
            if isinstance(native_relative, str):
                artifact_paths.append((ROOT / native_relative, "native_result"))
        for path, role in artifact_paths:
            reference = artifact(path, role)
            if reference:
                record["artifact_refs"].append(reference)
        record["completed_at"] = now_iso()
        write_json(output_dir / "BASELINE_SS_BLOCK_RUNNERS_EVIDENCE.json", record)
    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, required=True, help="Existing Sysplorer port to attach to")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--activation-sentinel", type=Path, required=True)
    parser.add_argument("--stop-time", type=float, default=50.0)
    parser.add_argument("--interval", type=float, default=0.01)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.port <= 0 or args.stop_time <= 0 or args.interval <= 0:
        raise ValueError("port, stop time, and interval must be positive")
    record = run(args)
    print(json.dumps({"status": record["status"], "packet": relative(args.output_dir / "BASELINE_SS_BLOCK_RUNNERS_EVIDENCE.json")}, ensure_ascii=False))
    return 0 if record["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
