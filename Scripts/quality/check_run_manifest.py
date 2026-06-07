#!/usr/bin/env python3
"""Validate a MoSim P0 cross-layer RUN_MANIFEST.json.

The checker is intentionally small and dependency-free. It prevents slice
evidence such as FAST-LIO replay, UE visuals, or offline scripts from being
overclaimed as a full MWORKS/ROS2/UE closed loop.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PASS_QUALITY = {"pass", "smoke_only", "needs_iteration", "invalid"}
FORMAL_MWORKS_SOURCES = {"MWORKS_MCP", "MWORKS_GUI"}


def repo_path(value: Any) -> Path:
    path = Path(str(value))
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_float(value: Any) -> float:
    try:
        if value is None or value == "":
            return math.nan
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def is_true(value: Any) -> bool:
    return value is True or str(value).lower() == "true"


def path_exists(value: Any) -> bool:
    if value in {None, ""}:
        return False
    return repo_path(value).exists()


def has_claim(manifest: dict[str, Any], needle: str) -> bool:
    scope = manifest.get("claim_scope")
    if isinstance(scope, str):
        return needle in scope
    return any(needle in str(item) for item in as_list(scope))


def validate(manifest: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []

    required_top = [
        "schema_version",
        "run_id",
        "objective",
        "scene_id",
        "map_id",
        "vehicle_id",
        "controller_id",
        "planner_id",
        "quality_status",
        "evidence_level",
        "claim_scope",
        "sources",
        "mworks",
        "ros2",
        "planner",
        "ue",
        "gate_results",
    ]
    for key in required_top:
        if key not in manifest:
            issues.append(f"missing top-level field: {key}")

    if str(manifest.get("schema_version", "")) != "mosim.run_manifest.v1":
        issues.append("schema_version must be mosim.run_manifest.v1")

    quality_status = str(manifest.get("quality_status", ""))
    if quality_status not in PASS_QUALITY:
        issues.append(f"invalid quality_status: {quality_status or '<missing>'}")

    sources = as_mapping(manifest.get("sources"))
    mworks_source = str(sources.get("mworks_source", ""))
    if mworks_source not in FORMAL_MWORKS_SOURCES:
        issues.append(f"mworks_source must be MWORKS_MCP or MWORKS_GUI: {mworks_source or '<missing>'}")
    if str(sources.get("planner_input_source", "")) in {"UE_GLOBAL_TRUTH", "UE_COLLISION_TRUTH"}:
        issues.append("planner_input_source must not be UE global/collision truth")
    if str(sources.get("replay_source", "")) == "offline_script" and quality_status == "pass":
        warnings.append("offline_script replay can support visualization/debug only; verify formal MWORKS/ROS2 sources before report claims")

    mworks = as_mapping(manifest.get("mworks"))
    if str(mworks.get("check_model_status", "")) != "pass":
        issues.append("mworks.check_model_status must be pass")
    if str(mworks.get("simulate_status", "")) not in {"pass", "smoke_only"}:
        issues.append("mworks.simulate_status must be pass or smoke_only")
    if has_claim(manifest, "performance") and not path_exists(mworks.get("raw_csv")):
        issues.append("performance claim requires existing mworks.raw_csv")
    if has_claim(manifest, "performance") and not path_exists(mworks.get("metrics_json")):
        issues.append("performance claim requires existing mworks.metrics_json")

    ros2 = as_mapping(manifest.get("ros2"))
    if not is_true(ros2.get("timestamp_monotonic")):
        issues.append("ros2.timestamp_monotonic must be true")
    if str(ros2.get("tf_status", "")) != "pass":
        issues.append("ros2.tf_status must be pass")
    imu_rate = as_float(ros2.get("imu_rate_hz"))
    lidar_rate = as_float(ros2.get("lidar_rate_hz"))
    if math.isnan(imu_rate) or imu_rate < 180.0:
        issues.append(f"ros2.imu_rate_hz too low: {ros2.get('imu_rate_hz', '<missing>')}")
    if math.isnan(lidar_rate) or lidar_rate < 9.0:
        issues.append(f"ros2.lidar_rate_hz too low: {ros2.get('lidar_rate_hz', '<missing>')}")

    fast_lio = as_mapping(ros2.get("fast_lio_eval"))
    if has_claim(manifest, "fast_lio") or has_claim(manifest, "localization"):
        if str(fast_lio.get("status", "")) != "pass":
            issues.append("FAST-LIO/localization claim requires ros2.fast_lio_eval.status=pass")
        rmse = as_float(fast_lio.get("position_rmse_m"))
        max_error = as_float(fast_lio.get("max_error_m"))
        samples = as_float(fast_lio.get("aligned_samples"))
        if math.isnan(rmse) or rmse > 0.5:
            issues.append(f"FAST-LIO position_rmse_m too high: {fast_lio.get('position_rmse_m', '<missing>')}")
        if math.isnan(max_error) or max_error > 1.0:
            issues.append(f"FAST-LIO max_error_m too high: {fast_lio.get('max_error_m', '<missing>')}")
        if math.isnan(samples) or samples < 40:
            issues.append(f"FAST-LIO aligned_samples too low: {fast_lio.get('aligned_samples', '<missing>')}")

    planner = as_mapping(manifest.get("planner"))
    if is_true(planner.get("global_truth_used_as_input")):
        issues.append("planner.global_truth_used_as_input must be false")
    if has_claim(manifest, "planner") or has_claim(manifest, "closed_loop"):
        if str(planner.get("map_source", "")) in {"", "ue_global_truth", "offline_global_truth"}:
            issues.append("planner claim requires sensed/local map_source, not global truth")
        trace_source = str(planner.get("setpoint_trace_source", ""))
        if trace_source != "RUNTIME_20HZ_ADAPTER":
            issues.append(
                "planner claim requires planner.setpoint_trace_source=RUNTIME_20HZ_ADAPTER, "
                f"not {trace_source or '<missing>'}"
            )
        if str(planner.get("setpoint_adapter_status", "")) != "pass":
            issues.append("planner claim requires planner.setpoint_adapter_status=pass")
        stale_timeout = as_float(planner.get("stale_command_timeout_s"))
        if math.isnan(stale_timeout) or stale_timeout <= 0.0:
            issues.append(
                f"planner.stale_command_timeout_s must be positive: "
                f"{planner.get('stale_command_timeout_s', '<missing>')}"
            )
        setpoint_rate = as_float(planner.get("setpoint_rate_hz"))
        if math.isnan(setpoint_rate) or setpoint_rate < 19.0:
            issues.append(f"planner.setpoint_rate_hz too low: {planner.get('setpoint_rate_hz', '<missing>')}")
        if not path_exists(planner.get("setpoint_trace")):
            issues.append("planner claim requires existing planner.setpoint_trace")

    if has_claim(manifest, "closed_loop"):
        consumed_trace = str(mworks.get("consumed_setpoint_trace", ""))
        planner_trace = str(planner.get("setpoint_trace", ""))
        if str(mworks.get("setpoint_trace_consumption_status", "")) != "pass":
            issues.append("closed_loop claim requires mworks.setpoint_trace_consumption_status=pass")
        if not consumed_trace:
            issues.append("closed_loop claim requires mworks.consumed_setpoint_trace")
        elif not path_exists(consumed_trace):
            issues.append("closed_loop claim requires existing mworks.consumed_setpoint_trace")
        if consumed_trace and planner_trace and repo_path(consumed_trace).resolve() != repo_path(planner_trace).resolve():
            issues.append("closed_loop claim requires MWORKS consumed_setpoint_trace to match planner.setpoint_trace")
        if not str(mworks.get("trace_consumption_evidence", "")):
            issues.append("closed_loop claim requires mworks.trace_consumption_evidence")

    ue = as_mapping(manifest.get("ue"))
    if str(ue.get("no_pose_overwrite_status", "")) != "pass":
        issues.append("ue.no_pose_overwrite_status must be pass")
    if has_claim(manifest, "ue_visual") and not path_exists(ue.get("command_echo_log")):
        warnings.append("UE visual claim should include ue.command_echo_log")

    gate_results = as_mapping(manifest.get("gate_results"))
    failures = as_list(gate_results.get("failures"))
    if failures:
        issues.append(f"gate_results.failures is not empty: {len(failures)}")
    blockers = as_list(manifest.get("blockers"))
    if quality_status == "pass" and blockers:
        issues.append("quality_status=pass requires blockers to be empty")

    return {
        "ok": not issues,
        "quality_status": quality_status,
        "run_id": str(manifest.get("run_id", "")),
        "issues": issues,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="Path to RUN_MANIFEST.json")
    parser.add_argument("--output-json", help="Optional path for validation report")
    args = parser.parse_args()

    manifest_path = repo_path(args.manifest)
    report: dict[str, Any]
    try:
        manifest = read_json(manifest_path)
        report = validate(manifest)
    except Exception as exc:
        report = {"ok": False, "run_id": "", "quality_status": "", "issues": [str(exc)], "warnings": []}

    report["manifest"] = rel(manifest_path)
    if args.output_json:
        output = repo_path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
