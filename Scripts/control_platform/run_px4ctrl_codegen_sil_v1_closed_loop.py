#!/usr/bin/env python3
"""Run the hash-bound 50 s MWORKS graphical-to-generated-C SIL comparison.

This script is executed inside an authorized Sysplorer session.  It calls
``SimulateModel`` without overrides so both runners use their own identical
``Px4CtrlFormalRunner`` experiment annotation: Dassl, 50 s, 1e-4 tolerance,
and 0.01 s output interval.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
RESULT_DIR = ROOT / "Results" / "control_platform" / "px4ctrl_codegen_sil_v1"
RAW_DIR = RESULT_DIR / "raw"
LOG_DIR = RESULT_DIR / "logs"

BASELINE = "MoSimQuadrotorModel.Experiment.Runners.Formal.Px4CtrlFormalRunner"
GENERATED = "Px4CtrlGeneratedCodeFormalRunner"
VARIABLES = [
    "position[1]", "position[2]", "position[3]",
    "attitude[1]", "attitude[2]", "attitude[3]",
    "rotor_command[1]", "rotor_command[2]", "rotor_command[3]", "rotor_command[4]",
]
SOURCE_PATHS = {
    "graphical_model": ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Implementations" / "Sysblocks" / "PX4CTRL_Original_OuterLoop_Graphical_Sysblock.mo",
    "equation_bridge": ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Implementations" / "Sysblocks" / "PX4CTRL_Core_AttitudeThrust_EquationBridge_Sysblock.mo",
    "baseline_adapter": ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Adapters" / "Px4CtrlAttitudeThrustAdapter.mo",
    "baseline_runner": ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "Runners" / "Formal" / "Px4CtrlFormalRunner.mo",
    "cfunction_model": RESULT_DIR / "models" / "PX4CTRL_Generated_CFunction_Sysblock.mo",
    "generated_adapter": RESULT_DIR / "models" / "Px4CtrlGeneratedCodeAttitudeThrustAdapter.mo",
    "generated_runner": RESULT_DIR / "models" / "Px4CtrlGeneratedCodeFormalRunner.mo",
    "generated_c_source": RESULT_DIR / "generated_c" / "MoSimQuadrotorModel.Control.Implementations.Sysblocks.PX4CTRL_Original_OuterLoop_Graphical_Sysblock" / "PX4CTRL_Original_OuterLoop_Graphical_Sysblock.c",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_model(model_name: str, label: str) -> dict[str, Any]:
    if not ModelingPy.ClassExist(model_name):
        raise RuntimeError(f"model is not loaded: {model_name}")
    checked = ModelingPy.CheckModel(model_name)
    if not checked:
        raise RuntimeError(f"CheckModel failed: {model_name}")
    simulated = ModelingPy.SimulateModel(model_name)
    if not simulated:
        raise RuntimeError(f"SimulateModel failed: {model_name}")
    times = [float(value) for value in ModelingPy.GetVarTimes()]
    columns = [[float(value) for value in values] for values in ModelingPy.GetVarsValues(VARIABLES)]
    lengths = {len(times), *(len(values) for values in columns)}
    if len(times) != 5001 or lengths != {5001}:
        raise RuntimeError(f"unexpected result length for {model_name}: {sorted(lengths)}")
    if abs(times[0]) > 1e-12 or abs(times[-1] - 50.0) > 1e-12:
        raise RuntimeError(f"unexpected result time range for {model_name}: {times[0]}, {times[-1]}")
    if not all(math.isfinite(value) for column in columns for value in column):
        raise RuntimeError(f"non-finite result value for {model_name}")
    csv_path = RAW_DIR / f"{label}_50s.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["time", *VARIABLES])
        writer.writerows(zip(times, *columns))
    return {
        "model": model_name,
        "check_model": bool(checked),
        "simulate_model": bool(simulated),
        "sample_count": len(times),
        "time_start": times[0],
        "time_end": times[-1],
        "times": times,
        "columns": {name: values for name, values in zip(VARIABLES, columns)},
        "raw_csv": str(csv_path),
        "raw_csv_sha256": sha256(csv_path),
    }


def error_metrics(baseline: dict[str, Any], generated: dict[str, Any], names: list[str]) -> dict[str, Any]:
    times_a = baseline["times"]
    times_b = generated["times"]
    time_error = max(abs(left - right) for left, right in zip(times_a, times_b))
    per_signal: dict[str, dict[str, float]] = {}
    all_differences: list[float] = []
    for name in names:
        deltas = [
            float(generated["columns"][name][index]) - float(baseline["columns"][name][index])
            for index in range(len(times_a))
        ]
        all_differences.extend(deltas)
        per_signal[name] = {
            "max_abs": max(abs(value) for value in deltas),
            "rmse": math.sqrt(sum(value * value for value in deltas) / len(deltas)),
            "terminal_abs": abs(deltas[-1]),
        }
    return {
        "time_max_abs_s": time_error,
        "per_signal": per_signal,
        "aggregate_rmse": math.sqrt(sum(value * value for value in all_differences) / len(all_differences)),
        "aggregate_max_abs": max(abs(value) for value in all_differences),
    }


def public_run_record(run: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in run.items() if key not in {"times", "columns"}}


def main() -> dict[str, Any]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    baseline = run_model(BASELINE, "baseline_equation_bridge")
    generated = run_model(GENERATED, "generated_cfunction")
    if baseline["times"] != generated["times"]:
        raise RuntimeError("baseline and generated runner time grids differ")
    position = error_metrics(baseline, generated, VARIABLES[0:3])
    attitude = error_metrics(baseline, generated, VARIABLES[3:6])
    rotor = error_metrics(baseline, generated, VARIABLES[6:10])
    thresholds = {
        "position_rmse_m": 1e-6,
        "attitude_max_abs_rad": 1e-8,
        "rotor_max_abs_rad_s": 1e-6,
    }
    passed = (
        position["aggregate_rmse"] < thresholds["position_rmse_m"]
        and attitude["aggregate_max_abs"] < thresholds["attitude_max_abs_rad"]
        and rotor["aggregate_max_abs"] < thresholds["rotor_max_abs_rad_s"]
    )
    payload = {
        "schema": "mosim.px4ctrl_codegen_sil_closed_loop.v1",
        "source": "MWORKS_MCP",
        "baseline": public_run_record(baseline),
        "generated_cfunction": public_run_record(generated),
        "solver_contract": {
            "api": "ModelingPy.SimulateModel",
            "baseline_annotation": "Dassl, StartTime=0, StopTime=50, Tolerance=0.0001, Interval=0.01",
            "generated_runner_origin": "verbatim Px4CtrlFormalRunner clone with controller type substituted only",
            "overrides": "none",
        },
        "thresholds": thresholds,
        "differences": {"position": position, "attitude": attitude, "rotor_command": rotor},
        "source_hashes": {label: sha256(path) for label, path in SOURCE_PATHS.items()},
        "pass": passed,
        "claim_boundary": "This is MWORKS-only whole-aircraft SIL evidence. It does not execute Gazebo, PX4, ROS, MAVROS, or flight hardware.",
    }
    (LOG_DIR / "CLOSED_LOOP_SIL_RESULT.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": passed, "result": str(LOG_DIR / "CLOSED_LOOP_SIL_RESULT.json"), "position_rmse": position["aggregate_rmse"], "attitude_max_abs": attitude["aggregate_max_abs"], "rotor_max_abs": rotor["aggregate_max_abs"]}


RUN_SCRIPT_RESULT = main()
