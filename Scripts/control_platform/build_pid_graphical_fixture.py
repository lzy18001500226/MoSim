#!/usr/bin/env python3
"""Build and simulate a fixed-input fixture for the graphical PID model."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
RESULT_DIR = ROOT / "Results/control_platform/p1_pid_mworks_20260716"
MODEL_DIR = RESULT_DIR / "models/graphical"
RAW_DIR = RESULT_DIR / "raw"
LOG_DIR = RESULT_DIR / "logs"
CONTROLLER = "MoSim_PID_Unified_Graphical_Sysblock"
FIXTURE = "MoSim_PID_Unified_Graphical_Fixture"
INPUTS = {
    "setpoint": 0.5,
    "measurement": 0.1,
    "inner_measurement": 0.05,
    "feedforward": 0.3,
    "schedule": 0.0,
    "fuzzy_error": 0.0,
    "neural_residual": 0.0,
    "cascade_mode": 0.0,
    "enable": 1.0,
}
OUTPUTS = ["command", "outer_command", "unsaturated_command", "integral_state", "scheduled_gain"]


def add(type_name: str, block: str, x: float, y: float) -> None:
    if not ModelingPy.AddComponent(type_name, FIXTURE, block, x, y, 28, 24):
        raise RuntimeError(f"AddComponent failed: {block} ({type_name})")


def connect(source: str, target: str) -> None:
    if not ModelingPy.ConnectPort(FIXTURE, source, target):
        raise RuntimeError(f"ConnectPort failed: {source} -> {target}")


def build_and_run() -> dict:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not ModelingPy.ClassExist(CONTROLLER):
        raise RuntimeError(f"controller is not loaded: {CONTROLLER}")
    if not ModelingPy.ClassExist(FIXTURE):
        if not ModelingPy.NewModel(FIXTURE, "Sysblock", "Fixed-input graphical PID fixture"):
            raise RuntimeError(f"NewModel failed: {FIXTURE}")
    if not ModelingPy.OpenModel(FIXTURE, "diagram"):
        raise RuntimeError(f"OpenModel failed: {FIXTURE}")
    for component in list(ModelingPy.GetComponents(FIXTURE)):
        if not ModelingPy.RemoveComponent(FIXTURE, component):
            raise RuntimeError(f"RemoveComponent failed: {component}")

    for index, (name, value) in enumerate(INPUTS.items()):
        y = 160 - index * 38
        source = f"{name}_source"
        add("SysplorerEmbeddedCoder.Sources.Constant", source, -220, y)
        if not ModelingPy.SetParamValue(f"{source}.k", str(value)):
            raise RuntimeError(f"SetParamValue failed: {source}.k")
    add(CONTROLLER, "controller", 0, 0)
    for index, name in enumerate(OUTPUTS):
        add("SysplorerEmbeddedCoder.Port.Outport", name, 220, 120 - index * 52)
    for name in INPUTS:
        connect(f"{name}_source.y", f"controller.{name}")
    for name in OUTPUTS:
        connect(f"controller.{name}", name)

    target = MODEL_DIR / f"{FIXTURE}.mo"
    saved = ModelingPy.SaveModel(FIXTURE) if target.exists() else ModelingPy.SaveModelAs(FIXTURE, str(MODEL_DIR), FIXTURE)
    checked = ModelingPy.CheckModel(FIXTURE)
    simulated = ModelingPy.SimulateModelEx(FIXTURE, {"stopTime": 0.2, "interval": 0.02})
    times = list(ModelingPy.GetVarTimes())
    columns = [list(values) for values in ModelingPy.GetVarsValues(OUTPUTS)]
    if not times or len({len(times), *(len(column) for column in columns)}) != 1:
        raise RuntimeError("graphical fixture returned inconsistent result lengths")
    if not all(math.isfinite(float(value)) for column in columns for value in column):
        raise RuntimeError("graphical fixture returned NaN or Inf")
    raw_path = RAW_DIR / "graphical_pid_fixture.csv"
    with raw_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["time", *OUTPUTS])
        writer.writerows(zip(times, *columns))
    manifest = {
        "schema": "mosim.pid_graphical_fixture.v1",
        "source": "MWORKS_MCP",
        "controller": CONTROLLER,
        "fixture": FIXTURE,
        "fixture_path": str(target),
        "inputs": INPUTS,
        "outputs": OUTPUTS,
        "saved": bool(saved),
        "check_model": bool(checked),
        "simulate_model": bool(simulated),
        "sample_count": len(times),
        "time_start": float(times[0]),
        "time_end": float(times[-1]),
        "raw_csv": str(raw_path),
        "claim_boundary": "Real fixed-input MWORKS simulation of the graphical PID model. Six-variant CFunction equivalence remains a separate gate.",
    }
    manifest_path = LOG_DIR / "pid_graphical_fixture_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {"ok": bool(saved and checked and simulated), "manifest": str(manifest_path), "sample_count": len(times)}


RUN_SCRIPT_RESULT = build_and_run()
