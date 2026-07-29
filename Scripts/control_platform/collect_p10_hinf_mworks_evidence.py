#!/usr/bin/env python3
"""Collect live MWORKS MIL/codegen evidence for the P10 H-infinity adapter."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
RESULT = ROOT / "Results/control_platform/p10_mworks_gap_closeout_20260718/hinf_hover_wrench"
BUILD_MANIFEST = RESULT / "P10_HINF_BUILD_MANIFEST.json"
GRAPHICAL_REVIEW = ROOT / "Results/control_platform/p10_mworks_gap_closeout_20260718/graphical_review_20260718/P10_MWORKS_GRAPHICAL_REVIEW.json"


def load_builder():
    path = ROOT / "Scripts/control_platform/build_p10_hinf_mworks_fixture.py"
    module = ModuleType("p10_hinf_current_builder")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> dict:
    builder = load_builder()
    build = json.loads(BUILD_MANIFEST.read_text(encoding="utf-8"))
    graphical_review = json.loads(GRAPHICAL_REVIEW.read_text(encoding="utf-8"))
    if graphical_review.get("status") != "passed":
        raise RuntimeError("P10 graphical review is not passed")
    function_model = build["function_model"]
    fixture_model = build["fixture_model"]
    for model_name, path_key in (
        (function_model, "function_model_path"),
        (fixture_model, "fixture_model_path"),
    ):
        if not ModelingPy.ClassExist(model_name):
            if not ModelingPy.OpenModelFile(build[path_key]):
                raise RuntimeError(f"OpenModelFile failed for {build[path_key]}")
    function_check = bool(ModelingPy.CheckModel(function_model))
    fixture_check = bool(ModelingPy.CheckModel(fixture_model))
    if not function_check or not fixture_check:
        raise RuntimeError(f"CheckModel failed: {ModelingPy.GetLastErrors()}")
    simulate_ok = bool(ModelingPy.SimulateModel(fixture_model))
    if not simulate_ok:
        raise RuntimeError(f"SimulateModel failed: {ModelingPy.GetLastErrors()}")
    times = [float(value) for value in ModelingPy.GetVarTimes()]
    values = [[float(value) for value in column] for column in ModelingPy.GetVarsValues(builder.OUTPUTS)]
    lengths = {len(times), *(len(column) for column in values)}
    if lengths != {8}:
        raise RuntimeError(f"unexpected result lengths: {sorted(lengths)}")
    columns = dict(zip(builder.OUTPUTS, values, strict=True))
    quaternion_norms = [
        math.sqrt(w * w + x * x + y * y + z * z)
        for w, x, y, z in zip(
            columns["desired_attitude_w"], columns["desired_attitude_x"],
            columns["desired_attitude_y"], columns["desired_attitude_z"], strict=True,
        )
    ]
    checks = {
        "all_outputs_finite": all(math.isfinite(value) for column in values for value in column),
        "status_code_zero": all(value == 0.0 for value in columns["status_code"]),
        "source_variant_is_wrench": all(value == 3.0 for value in columns["source_command_variant"]),
        "adapted_variant_is_attitude_thrust": all(value == 1.0 for value in columns["adapted_command_variant"]),
        "unit_desired_quaternion": all(abs(value - 1.0) <= 1.0e-12 for value in quaternion_norms),
        "normalized_thrust_in_declared_range": all(0.0 <= value <= 0.62 for value in columns["normalized_thrust"]),
        "nonzero_wrench_torque": any(abs(value) > 1.0e-12 for name in (
            "wrench_tau_x_nm", "wrench_tau_y_nm", "wrench_tau_z_nm"
        ) for value in columns[name]),
        "nonzero_adapted_tilt": any(abs(value) > 1.0e-12 for name in (
            "adapted_roll_rad", "adapted_pitch_rad"
        ) for value in columns[name]),
    }
    raw_path = RESULT / "raw/hinf_hover_wrench_mil.csv"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    with raw_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["time_s", *builder.OUTPUTS])
        writer.writerows(zip(times, *values))
    metrics = {
        "schema": "mosim.p10_hinf_wrench_adapter.mworks_mil_metrics.v1",
        "status": "passed" if all(checks.values()) else "failed",
        "source": "MWORKS_MCP_LIVE",
        "controller": "hinf_hover_wrench",
        "model_name": fixture_model,
        "sample_count": len(times),
        "behavior_checks": checks,
        "first_outputs": {name: column[0] for name, column in columns.items()},
        "last_outputs": {name: column[-1] for name, column in columns.items()},
        "raw_csv": relative(raw_path),
        "raw_csv_sha256": sha256(raw_path),
        "claim_boundary": "Frozen-hover fixed-input WRENCH and quasi-static ATTITUDE_THRUST adapter MIL only.",
    }
    metrics_path = RESULT / "metrics/MIL_METRICS.json"
    write(metrics_path, metrics)
    codegen_ok = bool(ModelingPy.GenerateModelCode(function_model))
    if not codegen_ok:
        raise RuntimeError(f"GenerateModelCode failed: {ModelingPy.GetLastErrors()}")
    log = {
        "schema": "mosim.p10_hinf_wrench_adapter.mworks_tool_log.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "MWORKS_MCP_LIVE",
        "live_mworks_touched": True,
        "will_not_click_activation_login": True,
        "activation_state_observation": "usable_main_window_no_login_license_or_authorization_blocker_observed",
        "license_state": "task_local_sufficient_for_check_simulate_codegen",
        "steps": [
            {"step": "CheckModel", "model": function_model, "status": "passed"},
            {"step": "CheckModel", "model": fixture_model, "status": "passed"},
            {"step": "SimulateModel", "model": fixture_model, "status": "passed"},
            {"step": "GetVarTimes/GetVarsValues", "status": "passed", "sample_count": len(times)},
            {"step": "GenerateModelCode", "model": function_model, "status": "passed"},
        ],
    }
    log_path = RESULT / "logs/MWORKS_TOOL_LOG.json"
    write(log_path, log)
    manifest = {
        "schema": "mosim.p10_hinf_wrench_adapter.mworks_manifest.v1",
        "status": metrics["status"] if codegen_ok else "failed",
        "source": "MWORKS_MCP_LIVE",
        "controller": "hinf_hover_wrench",
        "graphical_review": relative(GRAPHICAL_REVIEW),
        "evidence_ladder": {
            "graphical_sysblock_fixture": "passed",
            "check_model": "passed",
            "simulate_model": "passed",
            "result_variables_and_metrics": metrics["status"],
            "official_generate_model_code": "passed",
            "generated_c_sil": "not_run",
            "generated_c_gazebo": "not_run",
        },
        "artifact_refs": [relative(BUILD_MANIFEST), relative(GRAPHICAL_REVIEW), relative(raw_path), relative(metrics_path), relative(log_path)],
        "claim_boundary": "MWORKS MIL and official code generation only; generated-C SIL and Gazebo remain open.",
    }
    manifest_path = RESULT / "P10_HINF_MWORKS_MANIFEST.json"
    write(manifest_path, manifest)
    return {"ok": manifest["status"] == "passed", "manifest": str(manifest_path), "last_outputs": metrics["last_outputs"]}


RUN_SCRIPT_RESULT = main()
