#!/usr/bin/env python3
"""Run a bounded fixed-input MIL smoke for the optimized ss controller."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
CONTROLLER = "MoSimQuadrotorModel.Control.Implementations.Graphical.ProjectOwned.MoSim_OptimizedSSGraphicalController"
FIXTURE = "MoSim_OptimizedSSGraphicalController_MIL"
PACKAGE_FILE = ROOT / "Models/MoSimQuadrotorModel/package.mo"
RESULT_DIR = ROOT / "Results/control_optimization_ss_graphical"
MODEL_DIR = RESULT_DIR / "models/mil"
RAW_DIR = RESULT_DIR / "raw"
LOG_DIR = RESULT_DIR / "logs"
INPUTS = {
    "x_error": 0.40,
    "y_error": -0.30,
    "z_error": 0.20,
    "z_ref_rate": 0.05,
    "roll_mea": 0.02,
    "pitch_mea": -0.03,
    "yaw_mea": 0.04,
    "yaw_ref": 0.15,
}
OUTPUTS = ["y", "y1", "y2", "y3"]


def add(type_name: str, block: str, x: float, y: float) -> None:
    if not ModelingPy.AddComponent(type_name, FIXTURE, block, x, y, 34, 26):
        raise RuntimeError(f"AddComponent failed: {block} ({type_name})")


def connect(source: str, target: str) -> None:
    if not ModelingPy.ConnectPort(FIXTURE, source, target):
        raise RuntimeError(f"ConnectPort failed: {source} -> {target}")


def build_and_run() -> dict:
    for directory in (MODEL_DIR, RAW_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    if not ModelingPy.OpenModelFile(str(PACKAGE_FILE)):
        raise RuntimeError(f"OpenModelFile failed: {PACKAGE_FILE}")
    if not ModelingPy.ClassExist(CONTROLLER):
        raise RuntimeError(f"controller is not loaded: {CONTROLLER}")
    if not ModelingPy.ClassExist(FIXTURE):
        if not ModelingPy.NewModel(FIXTURE, "Sysblock", "Fixed-input MIL smoke for optimized ss controller"):
            raise RuntimeError(f"NewModel failed: {FIXTURE}")
    if not ModelingPy.OpenModel(FIXTURE, "diagram"):
        raise RuntimeError(f"OpenModel failed: {FIXTURE}")
    for component in list(ModelingPy.GetComponents(FIXTURE)):
        if not ModelingPy.RemoveComponent(FIXTURE, component):
            raise RuntimeError(f"RemoveComponent failed: {component}")

    for index, (name, value) in enumerate(INPUTS.items()):
        source = f"{name}_source"
        add("SysplorerEmbeddedCoder.Sources.Constant", source, -420, 220 - index * 55)
        if not ModelingPy.SetParamValue(f"{source}.k", str(value)):
            raise RuntimeError(f"SetParamValue failed: {source}.k")
    add(CONTROLLER, "controller", 0, 0)
    for index, name in enumerate(OUTPUTS):
        add("SysplorerEmbeddedCoder.Port.Outport", name, 420, 135 - index * 90)
    for name in INPUTS:
        connect(f"{name}_source.y", f"controller.{name}")
    for name in OUTPUTS:
        connect(f"controller.{name}", name)

    target = MODEL_DIR / f"{FIXTURE}.mo"
    saved = ModelingPy.SaveModel(FIXTURE) if target.exists() else ModelingPy.SaveModelAs(FIXTURE, str(MODEL_DIR), FIXTURE)
    checked = bool(ModelingPy.CheckModel(FIXTURE))
    check_errors = str(ModelingPy.GetLastErrors())
    simulated = False
    simulation_errors = ""
    times: list[float] = []
    columns: list[list[float]] = []
    result_shape_ok = False
    finite_outputs = False
    nonzero_outputs = False
    raw_path = RAW_DIR / "optimized_ss_graphical_mil.csv"
    if checked:
        simulated = bool(ModelingPy.SimulateModelEx(FIXTURE, {"stopTime": 0.2, "interval": 0.01}))
        simulation_errors = str(ModelingPy.GetLastErrors())
        times = [float(value) for value in ModelingPy.GetVarTimes()]
        columns = [[float(value) for value in values] for values in ModelingPy.GetVarsValues(OUTPUTS)]
        result_shape_ok = bool(
            times
            and len(columns) == len(OUTPUTS)
            and all(len(column) == len(times) for column in columns)
        )
        if result_shape_ok:
            finite_outputs = all(math.isfinite(value) for column in columns for value in column)
            nonzero_outputs = any(abs(value) > 1e-9 for column in columns for value in column)
            if finite_outputs and nonzero_outputs:
                with raw_path.open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.writer(stream, lineterminator="\n")
                    writer.writerow(["time", *OUTPUTS])
                    writer.writerows(zip(times, *columns))

    manifest = {
        "schema": "mosim.optimized_ss_graphical_controller.mil.v1",
        "source": "MWORKS_MCP",
        "controller": CONTROLLER,
        "fixture": FIXTURE,
        "fixture_path": str(target),
        "inputs": INPUTS,
        "outputs": OUTPUTS,
        "saved": bool(saved),
        "check_model": checked,
        "simulate_model": bool(simulated),
        "check_model_errors": check_errors,
        "simulation_errors": simulation_errors,
        "sample_count": len(times),
        "time_start": times[0] if times else None,
        "time_end": times[-1] if times else None,
        "result_shape_ok": result_shape_ok,
        "finite_outputs": finite_outputs,
        "nonzero_outputs": nonzero_outputs,
        "raw_csv": str(raw_path) if result_shape_ok and finite_outputs and nonzero_outputs else None,
        "status": "pass" if checked and simulated and result_shape_ok and finite_outputs and nonzero_outputs else "blocked_mil_compile_or_results",
        "behavior_equivalence_ok": False,
        "claim_boundary": (
            "Fixed-input MWORKS MIL smoke for the pure graphical ss controller. "
            "No plant tracking, planner, closed-loop, or flight claim. Empty "
            "result series remain an execution blocker, not a pass."
        ),
    }
    manifest_path = LOG_DIR / "optimized_ss_graphical_mil_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": bool(saved and checked and simulated and result_shape_ok and finite_outputs and nonzero_outputs),
        "manifest": str(manifest_path),
        "sample_count": len(times),
    }


RUN_SCRIPT_RESULT = build_and_run()
