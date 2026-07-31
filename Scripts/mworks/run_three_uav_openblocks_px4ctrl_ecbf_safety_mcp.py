#!/usr/bin/env python3
"""Run the PX4CTRL pairwise-ECBF safety branch through one attached MCP session.

The process refuses to start a Sysplorer instance.  The caller must set
``SYSPLORER_API_PORT`` to the existing session port before invoking this script.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MODEL_NAME = (
    "MoSimQuadrotorModel.Guidance.Planning."
    "ThreeUavOpenBlocksReconfigurableFormationPx4CtrlEcbfSafety"
)
PACKAGE_FILE = ROOT / "Models" / "MoSimQuadrotorModel" / "package.mo"
PLANNING_METRICS = (
    ROOT
    / "Results"
    / "planning"
    / "three_uav_open_blocks_mworks_20260720"
    / "metrics"
    / "three_uav_planning_metrics.json"
)
DEFAULT_OUTPUT = ROOT / "Results" / "planning" / "three_uav_openblocks_px4ctrl_ecbf_safety_20260731"
NATIVE_RESULT_ROOT = ROOT / "Results" / "native_result_cache" / "three_uav_px4ctrl_ecbf_safety"
SMOKE_STOP_TIME_S = 15.0
FULL_STOP_TIME_S = 304.840532932
SMOKE_INTERVAL_S = 0.05
FULL_INTERVAL_S = 1.0
MIN_PAIR_DISTANCE_M = 1.0

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
        VARIABLES[f"uav{_index}_nominal_ref_{_axis}_m"] = f"reference{_index}.position_command[{_axis_index}]"
        VARIABLES[f"uav{_index}_safe_ref_{_axis}_m"] = f"safetySmoother.safe_position_{_index}[{_axis_index}]"
    VARIABLES[f"uav{_index}_pitch_argument"] = f"vehicle{_index}.controller.pitch_argument"
VARIABLES.update({
    "minimum_predicted_pair_distance_m": "safety_minimum_predicted_pair_distance_m",
    "safety_active_pair_count": "safety_active_pair_count",
    "safety_maximum_reference_offset_m": "safety_maximum_reference_offset_m",
    "safety_requested_reference_offset_m": "safety_requested_reference_offset_m",
    "safety_maximum_ecbf_residual_m2_s2": "safety_maximum_ecbf_residual_m2_s2",
    "safety_correction_saturated": "safety_correction_saturated",
    "nominal_formation_deviation_m": "nominal_formation_deviation_m",
})

SOURCE_FILES = (
    ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "ThreeUavOpenBlocksReconfigurableFormationPx4Ctrl.mo",
    ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "ThreeUavOpenBlocksReconfigurableFormationPx4CtrlEcbfSafety.mo",
    ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "ThreeUavPairwiseEcbfReferenceSafetyFilter.mo",
    ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "ThreeUavPairwiseEcbfReferenceSmoother.mo",
    ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "OpenBlocksMapTruthDisplay.mo",
    ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "PlanningNavigationDisplay.mo",
    ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "OpenBlocksPx4CtrlVehicle.mo",
    ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "PlannedQuinticPx4CtrlReference.mo",
    ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Adapters" / "Px4CtrlAttitudeThrustAdapter.mo",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_hashes() -> dict[str, str]:
    return {
        str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in SOURCE_FILES
    }


def load_mcp_helpers() -> Any:
    helper_path = ROOT / "Scripts" / "mworks" / "run_sysplorer_mcp_smoke.py"
    spec = importlib.util.spec_from_file_location("mosim_sysplorer_mcp_helpers", helper_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load MCP helpers from {helper_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def require_explicit_existing_port(port: int) -> None:
    configured = os.environ.get("SYSPLORER_API_PORT", "").strip()
    if configured != str(port):
        raise RuntimeError(
            "Refusing a potentially new Sysplorer session: set "
            f"SYSPLORER_API_PORT={port} before running this MCP runner (got {configured!r})."
        )


def start_attached_client(helper: Any, port: int, log_path: Path) -> tuple[Any, dict[str, Any]]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    client = helper.JsonlMcpClient(helper.wrapper_command(helper.resolve_wrapper(None)), log_path)
    try:
        health = helper.initialize_mcp_client(client)
        startup = health.get("sysplorer_startup", {})
        if not startup.get("already_running") or startup.get("dedicated_sysplorer_port") != port:
            raise RuntimeError(
                "MCP did not prove attachment to the requested existing Sysplorer port: "
                f"{startup}"
            )
        return client, health
    except Exception:
        client.close()
        raise


def check_model(client: Any, helper: Any) -> dict[str, Any]:
    result = client.call_tool(
        "check_model",
        {
            "model_name": MODEL_NAME,
            "reload_mo_path": helper.windows_path(PACKAGE_FILE),
            "stop_on_error": True,
        },
        timeout_s=240,
    )
    if not result.get("ok"):
        raise RuntimeError(f"MCP CheckModel failed: {result}")
    return result


def newest_result_file(native_dir: Path) -> Path:
    candidates = [candidate for candidate in native_dir.rglob("Result.msr") if candidate.is_file()]
    if not candidates:
        raise RuntimeError(f"No native Result.msr exists under {native_dir}")
    return max(candidates, key=lambda candidate: candidate.stat().st_mtime)


def write_csv(series: dict[str, list[float]], path: Path) -> None:
    if not series.get("time_s"):
        raise RuntimeError("MWORKS result export did not contain time_s samples")
    row_count = len(series["time_s"])
    missing = [name for name in VARIABLES if name not in series]
    mismatched = {name: len(values) for name, values in series.items() if len(values) != row_count}
    if missing or mismatched:
        raise RuntimeError(f"Invalid MWORKS result export; missing={missing}, mismatched={mismatched}")
    if any(not math.isfinite(value) for values in series.values() for value in values):
        raise RuntimeError("MWORKS result export contains NaN or Inf")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(VARIABLES)
        for index in range(row_count):
            writer.writerow([series[name][index] for name in VARIABLES])


def smoke_metrics(series: dict[str, list[float]], stop_time_s: float) -> dict[str, Any]:
    times = series["time_s"]
    return {
        "schema": "mosim.mworks.three_uav_openblocks_px4ctrl_ecbf_safety.smoke.v2",
        "generated_at": now_iso(),
        "source": "MWORKS_MCP",
        "model_name": MODEL_NAME,
        "claim_role": "dynamics_smoke_only",
        "sample_count": len(times),
        "time_start_s": times[0],
        "time_end_s": times[-1],
        "expected_stop_time_s": stop_time_s,
        "minimum_pair_distance_m": min(series["minimum_pair_distance_m"]),
        "minimum_predicted_pair_distance_m": min(series["minimum_predicted_pair_distance_m"]),
        "maximum_safety_active_pair_count": max(series["safety_active_pair_count"]),
        "maximum_safety_reference_offset_m": max(series["safety_maximum_reference_offset_m"]),
        "minimum_clearance_lower_bound_m": min(series["clearance_lower_bound_m"]),
        "maximum_formation_distance_error_m": max(series["formation_distance_error_m"]),
        "gates": {
            "reached_requested_stop_time": abs(times[-1] - stop_time_s) <= 0.02,
            "pair_separation": min(series["minimum_pair_distance_m"]) >= MIN_PAIR_DISTANCE_M,
            "finite_values": True,
        },
        "claim_boundary": "A bounded MWORKS smoke only; not static-obstacle collision acceptance or runtime evidence.",
    }


def run_check(args: argparse.Namespace) -> int:
    output_dir = args.output_dir.resolve()
    record: dict[str, Any] = {
        "schema": "mosim.mworks.three_uav_openblocks_px4ctrl_ecbf_safety.check_mcp.v1",
        "created_at": now_iso(),
        "model_name": MODEL_NAME,
        "existing_sysplorer_port": args.port,
        "activation_sentinel_before": args.activation_sentinel,
        "background_screenshot_before": args.background_manifest,
        "will_not_click_activation_login": True,
        "live_mworks_touched": True,
        "tool_transport": "official MCP wrapper attached through SYSPLORER_API_PORT",
        "source_hashes_before": source_hashes(),
    }
    client = None
    try:
        require_explicit_existing_port(args.port)
        helper = load_mcp_helpers()
        client, health = start_attached_client(helper, args.port, output_dir / "logs" / "check_mcp.jsonl")
        record["mcp_existing_session_health"] = health
        record["check_model"] = check_model(client, helper)
        record["status"] = "completed"
    except Exception as exc:
        record["status"] = "blocked"
        record["error"] = repr(exc)
    finally:
        if client is not None:
            client.close()
    record["source_hashes_after"] = source_hashes()
    record["source_hash_drift"] = record["source_hashes_before"] != record["source_hashes_after"]
    record["completed_at"] = now_iso()
    write_json(output_dir / "CHECK_PHASE_MCP.json", record)
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0 if record["status"] == "completed" else 1


def run_phase(args: argparse.Namespace, *, phase: str, stop_time_s: float, interval_s: float) -> int:
    output_dir = args.output_dir.resolve()
    stem = "mworks_px4ctrl_ecbf_safety_smoke_15s" if phase == "smoke" else "mworks_px4ctrl_ecbf_safety_full_304p84s"
    raw_csv = output_dir / "raw" / f"{stem}.csv"
    metrics_json = output_dir / "metrics" / f"{stem}.json"
    metrics_csv = output_dir / "metrics" / f"{stem}.csv"
    native_dir = NATIVE_RESULT_ROOT / phase
    record_path = output_dir / ("SMOKE_RECORD_MCP.json" if phase == "smoke" else "RUN_RECORD_MCP.json")
    record: dict[str, Any] = {
        "schema": "mosim.mworks.three_uav_openblocks_px4ctrl_ecbf_safety.run_mcp.v1",
        "created_at": now_iso(),
        "phase": phase,
        "source": "MWORKS_MCP",
        "tool_transport": "official MCP wrapper attached through SYSPLORER_API_PORT",
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
            "PX4CTRL tracks frozen OpenBlocks references through a pairwise ECBF reference governor. "
            "This assesses pairwise separation only, not online replanning or plant-coupled wall collision."
        ),
    }
    client = None
    try:
        require_explicit_existing_port(args.port)
        helper = load_mcp_helpers()
        client, health = start_attached_client(helper, args.port, output_dir / "logs" / f"{phase}_mcp.jsonl")
        record["mcp_existing_session_health"] = health
        record["check_model"] = check_model(client, helper)
        native_dir.mkdir(parents=True, exist_ok=True)
        simulation = helper.simulate_modelingpy(
            client,
            model_name=MODEL_NAME,
            target_time=[0.0, stop_time_s],
            native_result_dir=native_dir,
            verify_result_var="min_inter_uav_distance_m",
            interval=interval_s,
            timeout_s=args.simulation_timeout_s,
        )
        record["simulate_model"] = simulation
        if not simulation.get("ok"):
            raise RuntimeError(f"MCP simulation did not produce a readable result: {simulation}")
        series = helper.read_result_series(client, MODEL_NAME, VARIABLES)
        if abs(series["time_s"][-1] - stop_time_s) > 0.02:
            raise RuntimeError(f"Simulation ended at {series['time_s'][-1]:.12g}s, expected {stop_time_s:.12g}s")
        write_csv(series, raw_csv)
        native_result = newest_result_file(native_dir)
        record.update({
            "sample_count": len(series["time_s"]),
            "time_start_s": series["time_s"][0],
            "time_end_s": series["time_s"][-1],
            "raw_csv": str(raw_csv),
            "native_result_file": str(native_result),
            "native_result_exists": native_result.is_file(),
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
            sys.path.insert(0, str(planning_dir))
            from audit_three_uav_openblocks_px4ctrl_ecbf_safety_result import audit, write_outputs

            metrics = audit(raw_csv.resolve(), PLANNING_METRICS.resolve())
            write_outputs(metrics, metrics_json, metrics_csv)
            record["formation_tracking_status"] = metrics["status"]
            record["formation_tracking_accepted"] = metrics["accepted"]
            record["formation_tracking_gates"] = metrics["gates"]
            record["gui_result_review"] = helper.open_gui_result_viewer(
                client,
                native_result=native_result,
                model_name=MODEL_NAME,
                variables=VARIABLES,
                reset_windows=False,
            )
        record["metrics_json"] = str(metrics_json)
        record["metrics_csv"] = str(metrics_csv)
        record["status"] = "completed"
    except Exception as exc:
        record["status"] = "blocked"
        record["error"] = repr(exc)
    finally:
        if client is not None:
            client.close()
    record["source_hashes_after"] = source_hashes()
    record["source_hash_drift"] = record["source_hashes_before"] != record["source_hashes_after"]
    record["completed_at"] = now_iso()
    write_json(record_path, record)
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0 if record["status"] == "completed" else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True, type=int, help="Existing Sysplorer port only")
    parser.add_argument("--mode", required=True, choices=("check", "smoke", "full"))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--activation-sentinel", required=True)
    parser.add_argument("--background-manifest", required=True)
    parser.add_argument("--simulation-timeout-s", type=float, default=1500.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.mode == "check":
        return run_check(args)
    if args.mode == "smoke":
        return run_phase(args, phase="smoke", stop_time_s=SMOKE_STOP_TIME_S, interval_s=SMOKE_INTERVAL_S)
    return run_phase(args, phase="full", stop_time_s=FULL_STOP_TIME_S, interval_s=FULL_INTERVAL_S)


if __name__ == "__main__":
    raise SystemExit(main())
