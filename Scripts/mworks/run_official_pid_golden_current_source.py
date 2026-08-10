#!/usr/bin/env python3
"""Run the current Golden PID and Formal reference on one explicit Sysplorer session."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import mworks.sysplorer as ModelingPy


ROOT = Path(__file__).resolve().parents[2]
ROOT_CLASS = "MoSimQuadrotorModel"
PACKAGE_FILE = ROOT / "Models" / ROOT_CLASS / "package.mo"
GOLDEN_MODEL = "MoSimQuadrotorModel.Experiment.Runners.Golden.OfficialPidSingleUavGoldenRunner"
FORMAL_MODEL = "MoSimQuadrotorModel.Experiment.Runners.Formal.OfficialPidFormalRunner"

SOURCE_FILES = (
    ROOT / "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/OfficialPidSingleUavGoldenRunner.mo",
    ROOT / "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/Modules/RotorCommandChannel.mo",
    ROOT / "Models/MoSimQuadrotorModel/Experiment/Runners/Formal/OfficialPidFormalRunner.mo",
    ROOT / "Models/MoSimQuadrotorModel/Control/Adapters/OfficialPIDGraphicalRotorAdapter.mo",
    ROOT / "Models/MoSimQuadrotorModel/Control/Adapters/OfficialPIDRotorAdapter.mo",
    ROOT / "Models/MoSimQuadrotorModel/Control/Allocation/OfficialPidRotorCommandMapper.mo",
    ROOT / "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID/OfficialPidCoreSysblock.mo",
    ROOT / "Models/MoSimQuadrotorModel/Vehicle/Sunray150Assembly.mo",
    ROOT / "Models/MoSimQuadrotorModel/Vehicle/Dynamics/PhysicalWrenchAdapter.mo",
    ROOT / "Models/MoSimQuadrotorModel/Vehicle/Dynamics/WrapperSurface.mo",
)

VARIABLES = {
    "time": "time",
    "position_error_norm": "position_error_norm",
    "position[1]": "position[1]",
    "position[2]": "position[2]",
    "position[3]": "position[3]",
    "attitude[1]": "attitude[1]",
    "attitude[2]": "attitude[2]",
    "attitude[3]": "attitude[3]",
    "rotor_command[1]": "rotor_command[1]",
    "rotor_command[2]": "rotor_command[2]",
    "rotor_command[3]": "rotor_command[3]",
    "rotor_command[4]": "rotor_command[4]",
    "rotor_speed[1]": "rotor_speed[1]",
    "rotor_speed[2]": "rotor_speed[2]",
    "rotor_speed[3]": "rotor_speed[3]",
    "rotor_speed[4]": "rotor_speed[4]",
}

DIAGRAMS = {
    "golden_top": GOLDEN_MODEL,
    "controller": "MoSimQuadrotorModel.Control.Adapters.OfficialPIDGraphicalRotorAdapter",
    "mapper": "MoSimQuadrotorModel.Control.Allocation.OfficialPidRotorCommandMapper",
    "plant": "MoSimQuadrotorModel.Vehicle.Sunray150Assembly",
}


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


def read_series() -> dict[str, list[float]]:
    values: dict[str, list[float]] = {"time": [float(value) for value in ModelingPy.GetVarTimes()]}
    if len(values["time"]) < 11:
        raise RuntimeError(f"Result has too few samples: {len(values['time'])}")
    for alias, variable in VARIABLES.items():
        if alias == "time":
            continue
        series = [float(value) for value in ModelingPy.GetVarValues(variable)]
        if not series:
            raise RuntimeError(f"Required result series is empty: {variable}")
        values[alias] = series
    row_count = len(values["time"])
    inconsistent = {name: len(series) for name, series in values.items() if len(series) != row_count}
    if inconsistent:
        raise RuntimeError(f"Result series lengths differ: {inconsistent}")
    non_finite = {
        name: sum(1 for value in series if not math.isfinite(value))
        for name, series in values.items()
    }
    non_finite = {name: count for name, count in non_finite.items() if count}
    if non_finite:
        raise RuntimeError(f"Result contains non-finite values: {non_finite}")
    return values


def write_csv(series: dict[str, list[float]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(VARIABLES)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(fields)
        for index in range(len(series["time"])):
            writer.writerow([series[field][index] for field in fields])


def metrics_for(series: dict[str, list[float]], *, model_name: str, interval_s: float, stop_time_s: float) -> dict[str, Any]:
    time_values = series["time"]
    error_values = series["position_error_norm"]
    duration_s = time_values[-1] - time_values[0]
    return {
        "schema_version": "mosim.official_pid_golden_current_source.metrics.v1",
        "generated_at": now_iso(),
        "source": "MWORKS_MCP",
        "model_name": model_name,
        "sample_count": len(time_values),
        "time_start_s": time_values[0],
        "time_end_s": time_values[-1],
        "duration_s": duration_s,
        "requested_stop_time_s": stop_time_s,
        "requested_interval_s": interval_s,
        "position_error_norm_rmse_m": math.sqrt(sum(value * value for value in error_values) / len(error_values)),
        "position_error_norm_max_m": max(error_values),
        "terminal_position_error_m": error_values[-1],
        "finite": True,
        "time_reaches_requested_stop": abs(time_values[-1] - stop_time_s) <= max(0.02, interval_s * 1.1),
    }


def refresh_current_root(port: int) -> dict[str, Any]:
    record: dict[str, Any] = {
        "existing_sysplorer_port": port,
        "connect_sysplorer_return": repr(ModelingPy.ConnectSysplorer(port=port)),
    }
    record["erase_root"] = bool(ModelingPy.EraseClasses((ROOT_CLASS,)))
    if not record["erase_root"]:
        raise RuntimeError(f"Targeted root unload failed: {last_errors()}")
    record["open_package_file"] = bool(ModelingPy.OpenModelFile(str(PACKAGE_FILE)))
    if not record["open_package_file"]:
        raise RuntimeError(f"OpenModelFile failed for {PACKAGE_FILE}: {last_errors()}")
    return record


def check_and_export_diagrams(output_dir: Path) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    diagram_dir = output_dir / "diagrams"
    diagram_dir.mkdir(parents=True, exist_ok=True)
    for name, model_name in DIAGRAMS.items():
        class_exists = bool(ModelingPy.ClassExist(model_name))
        if not class_exists:
            raise RuntimeError(f"Diagram model is absent after root reload: {model_name}: {last_errors()}")
        checks[name] = {
            "model_name": model_name,
            "class_exists": class_exists,
            "open_diagram": bool(ModelingPy.OpenModel(model_name, ModelingPy.ModelView.Diagram)),
        }
        output = diagram_dir / f"{name}_after_check.png"
        checks[name]["export_diagram"] = bool(ModelingPy.ExportDiagram(model_name, str(output), 3000, 1900))
        checks[name]["path"] = relative(output)
        if not checks[name]["export_diagram"] or not output.is_file():
            raise RuntimeError(f"ExportDiagram failed for {model_name}: {last_errors()}")
    return checks


def run_model(
    *,
    model_name: str,
    output_dir: Path,
    interval_s: float,
    stop_time_s: float,
) -> dict[str, Any]:
    label = "golden" if model_name == GOLDEN_MODEL else "formal"
    native_dir = output_dir / "native" / label
    raw_csv = output_dir / "raw" / f"{label}_current_result.csv"
    metrics_path = output_dir / "metrics" / f"{label}_current_metrics.json"
    native_dir.mkdir(parents=True, exist_ok=True)

    result: dict[str, Any] = {
        "model_name": model_name,
        "class_exists": bool(ModelingPy.ClassExist(model_name)),
        "requested_stop_time_s": stop_time_s,
        "requested_interval_s": interval_s,
    }
    if not result["class_exists"]:
        raise RuntimeError(f"{model_name} is absent after root reload: {last_errors()}")
    result["check_model"] = bool(ModelingPy.CheckModel(model_name))
    result["check_model_last_errors"] = last_errors()
    if not result["check_model"]:
        raise RuntimeError(f"CheckModel failed for {model_name}: {last_errors()}")

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
        raise RuntimeError(f"SimulateModel failed for {model_name}: {last_errors()}")

    series = read_series()
    if abs(series["time"][-1] - stop_time_s) > max(0.02, interval_s * 1.1):
        raise RuntimeError(
            f"{model_name} ended at {series['time'][-1]:.12g}s, expected {stop_time_s:.12g}s"
        )
    write_csv(series, raw_csv)
    metrics = metrics_for(series, model_name=model_name, interval_s=interval_s, stop_time_s=stop_time_s)
    write_json(metrics_path, metrics)
    native_result = find_native_result(native_dir)
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
        "schema_version": "mosim.official_pid_golden_current_source_acceptance.v2",
        "created_at": now_iso(),
        "status": "blocked",
        "source": "MWORKS_MCP",
        "tool_transport": "official ModelingPy bound to an explicit existing Sysplorer port",
        "entry_model": GOLDEN_MODEL,
        "formal_reference": FORMAL_MODEL,
        "existing_sysplorer_port": args.port,
        "simulation_contract": {
            "scenario": "nominal ClimbPath",
            "start_time_s": 0.0,
            "stop_time_s": args.stop_time,
            "golden_interval_s": args.golden_interval,
            "formal_interval_s": args.formal_interval,
        },
        "activation_sentinel": relative(args.activation_sentinel.resolve()),
        "will_not_click_activation_login": True,
        "live_mworks_touched": True,
        "source_hashes_before": source_hashes(),
        "claim_boundary": (
            "This accepts the current Modelica-backed graphical Golden PID loop against the preserved Formal PID "
            "reference. It does not claim native Sysblock/Modelica composition, ROS/PX4/Gazebo deployment, or flight acceptance."
        ),
        "artifact_refs": [],
    }
    try:
        record["session_refresh"] = refresh_current_root(args.port)
        record["diagrams_after_check"] = check_and_export_diagrams(output_dir)
        record["golden"] = run_model(
            model_name=GOLDEN_MODEL,
            output_dir=output_dir,
            interval_s=args.golden_interval,
            stop_time_s=args.stop_time,
        )
        record["formal"] = run_model(
            model_name=FORMAL_MODEL,
            output_dir=output_dir,
            interval_s=args.formal_interval,
            stop_time_s=args.stop_time,
        )

        mworks_scripts = ROOT / "Scripts" / "mworks"
        if str(mworks_scripts) not in sys.path:
            sys.path.insert(0, str(mworks_scripts))
        from verify_official_pid_golden_equivalence import run_comparison  # noqa: PLC0415

        comparison = run_comparison(
            output_dir / "raw" / "golden_current_result.csv",
            output_dir / "raw" / "formal_current_result.csv",
        )
        comparison_path = output_dir / "metrics" / "GOLDEN_FORMAL_EQUIVALENCE.json"
        write_json(comparison_path, comparison)
        record["equivalence"] = {
            "status": comparison["status"],
            "path": relative(comparison_path),
            "time_alignment_max_abs_s": comparison["time_alignment_max_abs_s"],
            "max_abs_difference": comparison["max_abs_difference"],
        }
        if comparison["status"] != "pass":
            raise RuntimeError(f"Golden/Formal equivalence failed: {comparison['failures']}")
        record["status"] = "pass"
    except Exception as exc:
        record["error"] = repr(exc)
        record["last_errors"] = last_errors()
    finally:
        record["source_hashes_after"] = source_hashes()
        record["source_hash_drift"] = record["source_hashes_before"] != record["source_hashes_after"]
        if record.get("status") == "pass" and record["source_hash_drift"]:
            record["status"] = "source_hash_drift"
        for path, role in (
            (args.activation_sentinel.resolve(), "activation_sentinel"),
            (output_dir / "raw" / "golden_current_result.csv", "raw"),
            (output_dir / "raw" / "formal_current_result.csv", "raw"),
            (output_dir / "metrics" / "golden_current_metrics.json", "metrics"),
            (output_dir / "metrics" / "formal_current_metrics.json", "metrics"),
            (output_dir / "metrics" / "GOLDEN_FORMAL_EQUIVALENCE.json", "metrics"),
            (output_dir / "diagrams" / "golden_top_after_check.png", "diagram"),
            (output_dir / "diagrams" / "controller_after_check.png", "diagram"),
            (output_dir / "diagrams" / "mapper_after_check.png", "diagram"),
            (output_dir / "diagrams" / "plant_after_check.png", "diagram"),
        ):
            reference = artifact(path, role)
            if reference:
                record["artifact_refs"].append(reference)
        for route in ("golden", "formal"):
            native_relative = record.get(route, {}).get("native_result")
            if isinstance(native_relative, str):
                reference = artifact(ROOT / native_relative, "native_result")
                if reference:
                    record["artifact_refs"].append(reference)
        record["completed_at"] = now_iso()
        write_json(output_dir / "CURRENT_SOURCE_ACCEPTANCE_PACKET.json", record)
    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, required=True, help="Existing Golden Sysplorer script port")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "Results/mworks_live_gate/official_pid_golden_20260805/current_source_replay",
    )
    parser.add_argument(
        "--activation-sentinel",
        type=Path,
        required=True,
        help="Current-turn read-only MWORKS window sentinel JSON",
    )
    parser.add_argument("--stop-time", type=float, default=50.0)
    parser.add_argument("--golden-interval", type=float, default=0.01)
    parser.add_argument("--formal-interval", type=float, default=0.002)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.port <= 0:
        raise ValueError("--port must be positive")
    if args.stop_time <= 0 or args.golden_interval <= 0 or args.formal_interval <= 0:
        raise ValueError("stop time and intervals must be positive")
    record = run(args)
    print(json.dumps({"status": record["status"], "packet": relative(args.output_dir / "CURRENT_SOURCE_ACCEPTANCE_PACKET.json")}, ensure_ascii=False))
    return 0 if record["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
