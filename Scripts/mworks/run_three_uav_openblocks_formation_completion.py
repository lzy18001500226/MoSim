#!/usr/bin/env python3
"""Run the canonical three-UAV OpenBlocks formation model on one existing session.

The runner never starts, closes, or restarts Sysplorer.  It refreshes only the
project-owned MoSimQuadrotorModel root so the current map-display sources are
loaded, then records raw native MWORKS outputs and bounded formation metrics.
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


ROOT = Path(__file__).resolve().parents[2]
ROOT_CLASS = "MoSimQuadrotorModel"
MODEL_NAME = "MoSimQuadrotorModel.Guidance.Planning.ThreeUavOpenBlocksReconfigurableFormationLinearMPC"
PACKAGE_FILE = ROOT / "Models" / "MoSimQuadrotorModel" / "package.mo"
PLANNING_METRICS = (
    ROOT
    / "Results"
    / "planning"
    / "three_uav_open_blocks_mworks_20260720"
    / "metrics"
    / "three_uav_planning_metrics.json"
)
SMOKE_STOP_TIME_S = 15.0
FULL_STOP_TIME_S = 304.840532932
SMOKE_INTERVAL_S = 0.05
# The 1 Hz output cadence is a result-storage choice only. Dassl still solves
# the model continuously, and this matches the known historical full-run path.
FULL_INTERVAL_S = 1.0
MIN_PAIR_DISTANCE_M = 1.0
MIN_CLEARANCE_LOWER_BOUND_M = 0.0

VARIABLES = {
    "time_s": "time",
    "uav1_tracking_error_m": "vehicle1.tracking_error_m",
    "uav2_tracking_error_m": "vehicle2.tracking_error_m",
    "uav3_tracking_error_m": "vehicle3.tracking_error_m",
    "minimum_pair_distance_m": "min_inter_uav_distance_m",
    "formation_distance_error_m": "formation_distance_error_m",
    "clearance_lower_bound_m": "actual_clearance_lower_bound_m",
}
for _index in range(1, 4):
    for _axis in "xyz":
        _axis_index = "xyz".index(_axis) + 1
        VARIABLES[f"uav{_index}_{_axis}_m"] = f"vehicle{_index}.position[{_axis_index}]"
        VARIABLES[f"uav{_index}_ref_{_axis}_m"] = f"reference{_index}.position_command[{_axis_index}]"

SOURCE_FILES = (
    ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "ThreeUavOpenBlocksReconfigurableFormationLinearMPC.mo",
    ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "OpenBlocksMapTruthDisplay.mo",
    ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "PlanningNavigationDisplay.mo",
    ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "OpenBlocksLinearMPCVehicle.mo",
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
    except Exception as exc:  # pragma: no cover - native fallback
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
        except Exception as exc:  # pragma: no cover - version dependent
            values[name] = {"error": repr(exc)}
    return values


def refresh_and_check(record: dict[str, Any], port: int, refresh_root: bool, open_diagram: bool) -> None:
    record["connect_sysplorer_return"] = repr(ModelingPy.ConnectSysplorer("127.0.0.1", port))
    record["connect_sysplorer"] = True
    record["class_exists_before_refresh"] = bool(ModelingPy.ClassExist(MODEL_NAME))

    if refresh_root:
        record["targeted_root_unload"] = bool(ModelingPy.EraseClasses((ROOT_CLASS,)))
        if not record["targeted_root_unload"]:
            raise RuntimeError(f"Targeted unload of {ROOT_CLASS} failed: {last_errors()}")
        record["open_package_file"] = bool(ModelingPy.OpenModelFile(str(PACKAGE_FILE)))
        if not record["open_package_file"]:
            raise RuntimeError(f"OpenModelFile failed for {PACKAGE_FILE}: {last_errors()}")

    record["class_exists_before_check"] = bool(ModelingPy.ClassExist(MODEL_NAME))
    if not record["class_exists_before_check"]:
        raise RuntimeError(f"{MODEL_NAME} is absent from reusable session {port}: {last_errors()}")
    record["check_model"] = bool(ModelingPy.CheckModel(MODEL_NAME))
    record["check_model_diagnostics"] = last_errors()
    if not record["check_model"]:
        raise RuntimeError(f"CheckModel failed for {MODEL_NAME}: {last_errors()}")
    if open_diagram:
        record["open_model_diagram"] = bool(ModelingPy.OpenModel(MODEL_NAME, ModelingPy.ModelView.Diagram))


def collect_series() -> dict[str, list[float]]:
    series: dict[str, list[float]] = {"time_s": [float(value) for value in ModelingPy.GetVarTimes()]}
    if len(series["time_s"]) < 11:
        raise RuntimeError(f"Result has too few samples: {len(series['time_s'])}")
    for alias, variable in VARIABLES.items():
        if alias == "time_s":
            continue
        values = [float(value) for value in ModelingPy.GetVarValues(variable)]
        if not values:
            raise RuntimeError(f"Required result variable is empty: {variable}")
        series[alias] = values
    count = len(series["time_s"])
    mismatched = {name: len(values) for name, values in series.items() if len(values) != count}
    if mismatched:
        raise RuntimeError(f"Result variable length mismatch: {mismatched}")
    non_finite = {
        name: sum(1 for value in values if not math.isfinite(value))
        for name, values in series.items()
    }
    non_finite = {name: count for name, count in non_finite.items() if count}
    if non_finite:
        raise RuntimeError(f"Non-finite result values: {non_finite}")
    return series


def write_csv(series: dict[str, list[float]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(VARIABLES)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(fields)
        for index in range(len(series["time_s"])):
            writer.writerow([series[field][index] for field in fields])


def smoke_metrics(series: dict[str, list[float]], stop_time_s: float) -> dict[str, Any]:
    times = series["time_s"]
    tracking_max = {
        f"uav{index}_tracking_max_m": max(series[f"uav{index}_tracking_error_m"])
        for index in range(1, 4)
    }
    return {
        "schema": "mosim.mworks.three_uav_openblocks.smoke.v1",
        "generated_at": now_iso(),
        "source": "MWORKS_MCP",
        "model_name": MODEL_NAME,
        "claim_role": "dynamics_smoke_only",
        "sample_count": len(times),
        "time_start_s": times[0],
        "time_end_s": times[-1],
        "expected_stop_time_s": stop_time_s,
        "minimum_pair_distance_m": min(series["minimum_pair_distance_m"]),
        "minimum_clearance_lower_bound_m": min(series["clearance_lower_bound_m"]),
        "maximum_formation_distance_error_m": max(series["formation_distance_error_m"]),
        **tracking_max,
        "gates": {
            "reached_requested_stop_time": abs(times[-1] - stop_time_s) <= 0.02,
            "pair_separation": min(series["minimum_pair_distance_m"]) >= MIN_PAIR_DISTANCE_M,
            "clearance_lower_bound_nonnegative": min(series["clearance_lower_bound_m"]) >= MIN_CLEARANCE_LOWER_BOUND_M,
        },
        "claim_boundary": (
            "A bounded three-UAV MWORKS dynamics smoke test. The global wall layer is rendered and is part of the "
            "offline planning/map truth; this does not establish plant-coupled wall collision or obstacle-avoidance acceptance."
        ),
    }


def newest_result_file(native_dir: Path) -> Path:
    candidates = [candidate for candidate in native_dir.rglob("Result.msr") if candidate.is_file()]
    if not candidates:
        raise RuntimeError(f"No native Result.msr created under {native_dir}")
    return max(candidates, key=lambda candidate: candidate.stat().st_mtime)


def run_check(args: argparse.Namespace) -> int:
    output_dir = args.output_dir.resolve()
    record: dict[str, Any] = {
        "schema": "mosim.mworks.three_uav_openblocks.check.v1",
        "created_at": now_iso(),
        "model_name": MODEL_NAME,
        "existing_sysplorer_port": args.port,
        "activation_sentinel_before": args.activation_sentinel,
        "background_screenshot_before": args.background_manifest,
        "will_not_click_activation_login": True,
        "live_mworks_touched": True,
        "source_hashes_before": source_hashes(),
        "claim_boundary": "Native model integrity and diagram preparation only; no simulation or collision-avoidance acceptance claim.",
    }
    try:
        refresh_and_check(record, args.port, refresh_root=True, open_diagram=True)
        record["status"] = "completed"
    except Exception as exc:
        record["status"] = "blocked"
        record["error"] = repr(exc)
        record["last_errors"] = last_errors()
    record["source_hashes_after"] = source_hashes()
    record["source_hash_drift"] = record["source_hashes_before"] != record["source_hashes_after"]
    record["completed_at"] = now_iso()
    write_json(output_dir / "CHECK_PHASE.json", record)
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0 if record["status"] == "completed" else 1


def run_phase(args: argparse.Namespace, phase: str, stop_time_s: float, interval_s: float) -> int:
    output_dir = args.output_dir.resolve()
    stem = "mworks_smoke_15s" if phase == "smoke" else "mworks_full_304p84s"
    native_dir = output_dir / "native" / phase
    raw_csv = output_dir / "raw" / f"{stem}.csv"
    metrics_json = output_dir / "metrics" / f"{stem}.json"
    metrics_csv = output_dir / "metrics" / f"{stem}.csv"
    record_file = output_dir / ("SMOKE_RECORD.json" if phase == "smoke" else "RUN_RECORD.json")
    record: dict[str, Any] = {
        "schema": "mosim.mworks.three_uav_openblocks.run.v1",
        "created_at": now_iso(),
        "phase": phase,
        "source": "MWORKS_MCP",
        "tool_transport": "official ModelingPy connected explicitly to an existing Sysplorer port",
        "model_name": MODEL_NAME,
        "existing_sysplorer_port": args.port,
        "simulation_contract": {
            "start_time_s": 0.0,
            "stop_time_s": stop_time_s,
            "result_interval_s": interval_s,
            "solver": "Dassl",
        },
        "activation_sentinel_before": args.activation_sentinel,
        "background_screenshot_before": args.background_manifest,
        "will_not_click_activation_login": True,
        "live_mworks_touched": True,
        "source_hashes_before": source_hashes(),
        "claim_boundary": (
            "Three current MWORKS whole-aircraft Linear-MPC loops track the frozen OpenBlocks references. "
            "The static/global wall geometry remains a map/visual/planning constraint rather than a plant-coupled "
            "collision-contact assertion."
        ),
    }
    try:
        refresh_and_check(record, args.port, refresh_root=False, open_diagram=False)
        native_dir.mkdir(parents=True, exist_ok=True)
        record["simulate_model"] = bool(
            ModelingPy.SimulateModel(
                MODEL_NAME,
                startTime=0.0,
                stopTime=stop_time_s,
                interval=interval_s,
                simMode=0,
                path=str(native_dir),
            )
        )
        record["post_simulation_diagnostics"] = simulation_diagnostics()
        if not record["simulate_model"]:
            raise RuntimeError(f"SimulateModel failed for {MODEL_NAME}: {last_errors()}")

        series = collect_series()
        if abs(series["time_s"][-1] - stop_time_s) > 0.02:
            raise RuntimeError(
                f"Simulation ended at {series['time_s'][-1]:.12g}s, expected {stop_time_s:.12g}s"
            )
        write_csv(series, raw_csv)
        result_file = newest_result_file(native_dir)
        record.update({
            "sample_count": len(series["time_s"]),
            "time_start_s": series["time_s"][0],
            "time_end_s": series["time_s"][-1],
            "raw_csv": str(raw_csv),
            "native_result_file": str(result_file),
            "native_result_exists": result_file.is_file(),
        })

        if phase == "smoke":
            metrics = smoke_metrics(series, stop_time_s)
            write_json(metrics_json, metrics)
            with metrics_csv.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle, lineterminator="\n")
                writer.writerow(["metric", "value"])
                for key, value in metrics.items():
                    if not isinstance(value, (dict, list)):
                        writer.writerow([key, value])
            record["smoke_gates"] = metrics["gates"]
            if not all(metrics["gates"].values()):
                raise RuntimeError(f"Smoke gates failed: {metrics['gates']}")
        else:
            planning_dir = ROOT / "Scripts" / "planning"
            if str(planning_dir) not in sys.path:
                sys.path.insert(0, str(planning_dir))
            from audit_three_uav_mworks_result import audit, write_outputs  # noqa: PLC0415

            metrics = audit(raw_csv.resolve(), PLANNING_METRICS.resolve())
            write_outputs(metrics, metrics_json, metrics_csv)
            record["formation_tracking_gates"] = metrics["gates"]
            record["formation_tracking_status"] = metrics["status"]
            record["formation_tracking_accepted"] = metrics["accepted"]

            record["open_result"] = bool(ModelingPy.OpenResult(str(result_file)))
            if not record["open_result"]:
                raise RuntimeError(f"OpenResult failed for {result_file}: {last_errors()}")
            record["create_animation"] = bool(ModelingPy.CreateAnimation())
            if not record["create_animation"]:
                raise RuntimeError(f"CreateAnimation failed: {last_errors()}")
            record["animation_speed"] = bool(ModelingPy.AnimationSpeed(0.2))

        record["metrics_json"] = str(metrics_json)
        record["metrics_csv"] = str(metrics_csv)
        record["status"] = "completed"
    except Exception as exc:
        record["status"] = "blocked"
        record["error"] = repr(exc)
        record["last_errors"] = last_errors()
    record["source_hashes_after"] = source_hashes()
    record["source_hash_drift"] = record["source_hashes_before"] != record["source_hashes_after"]
    record["completed_at"] = now_iso()
    write_json(record_file, record)
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0 if record["status"] == "completed" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, required=True, help="Existing Sysplorer port; this runner never starts a session.")
    parser.add_argument("--mode", choices=("check", "smoke", "full"), required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "Results" / "planning" / "three_uav_openblocks_gray_completion_20260730",
    )
    parser.add_argument("--activation-sentinel", required=True)
    parser.add_argument("--background-manifest", required=True)
    args = parser.parse_args()
    if args.mode == "check":
        return run_check(args)
    if args.mode == "smoke":
        return run_phase(args, "smoke", SMOKE_STOP_TIME_S, SMOKE_INTERVAL_S)
    return run_phase(args, "full", FULL_STOP_TIME_S, FULL_INTERVAL_S)


if __name__ == "__main__":
    raise SystemExit(main())
