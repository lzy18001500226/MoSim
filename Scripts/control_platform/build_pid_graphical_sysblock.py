#!/usr/bin/env python3
"""Build the unified PID graphical counterpart with official Sysplorer APIs.

Run inside Sysplorer through ``call_code(mode="run_script")``.  The model is a
reviewable topology artifact; numerical equivalence is a separate gate.
"""

from __future__ import annotations

import json
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
RESULT_DIR = ROOT / "Results/control_platform/p1_pid_mworks_20260716"
MODEL_DIR = RESULT_DIR / "models/graphical"
SCREENSHOT_DIR = RESULT_DIR / "screenshots/graphical"
LOG_DIR = RESULT_DIR / "logs"
MODEL_NAME = "MoSim_PID_Unified_Graphical_Sysblock"


INPUTS = [
    ("setpoint", -310, 180),
    ("measurement", -310, 130),
    ("inner_measurement", -310, 80),
    ("feedforward", -310, 10),
    ("schedule", -310, -50),
    ("fuzzy_error", -310, -110),
    ("neural_residual", -310, -170),
    ("cascade_mode", -310, -230),
    ("enable", -310, -280),
]

OUTPUTS = [
    ("command", 350, 120),
    ("outer_command", 350, 55),
    ("unsaturated_command", 350, -10),
    ("integral_state", 350, -75),
    ("scheduled_gain", 350, -140),
]


def add(type_name: str, block: str, x: float, y: float, width=28, height=24) -> None:
    if not ModelingPy.AddComponent(type_name, MODEL_NAME, block, x, y, width, height):
        raise RuntimeError(f"AddComponent failed: {block} ({type_name})")


def set_param(block: str, param: str, value: str) -> None:
    encoded = f'"{value}"' if param == "inputs" else value
    if not ModelingPy.SetParamValue(f"{block}.{param}", encoded):
        raise RuntimeError(f"SetParamValue failed: {block}.{param}={encoded}")


def connect(source: str, target: str) -> None:
    if not ModelingPy.ConnectPort(MODEL_NAME, source, target):
        raise RuntimeError(f"ConnectPort failed: {source} -> {target}")


def build() -> dict:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    if not ModelingPy.ClassExist(MODEL_NAME):
        created = ModelingPy.NewModel(
            MODEL_NAME,
            "Sysblock",
            "Unified PID family graphical counterpart",
        )
        if not created:
            raise RuntimeError(f"NewModel failed: {MODEL_NAME}")
    if not ModelingPy.OpenModel(MODEL_NAME, "diagram"):
        raise RuntimeError(f"OpenModel failed: {MODEL_NAME}")
    if ModelingPy.ClassExist(MODEL_NAME):
        for component in list(ModelingPy.GetComponents(MODEL_NAME)):
            if not ModelingPy.RemoveComponent(MODEL_NAME, component):
                raise RuntimeError(f"RemoveComponent failed: {component}")

    for block, x, y in INPUTS:
        add("SysplorerEmbeddedCoder.Port.Inport", block, x, y)
    for block, x, y in OUTPUTS:
        add("SysplorerEmbeddedCoder.Port.Outport", block, x, y)

    # Effective-gain surface: 1 + schedule + fuzzy + bounded neural residual.
    add("SysplorerEmbeddedCoder.Sources.Constant", "gain_bias", -235, -215)
    add("SysplorerEmbeddedCoder.MathOperation.Gain", "schedule_gain", -235, -50)
    add("SysplorerEmbeddedCoder.MathOperation.Gain", "fuzzy_gain", -235, -110)
    add("SysplorerEmbeddedCoder.Discontinuities.Saturation", "neural_limit", -235, -170)
    add("SysplorerEmbeddedCoder.MathOperation.Gain", "neural_gain", -170, -170)
    add("SysplorerEmbeddedCoder.MathOperation.Sum", "gain_sum_schedule", -155, -70)
    add("SysplorerEmbeddedCoder.MathOperation.Sum", "gain_sum_fuzzy", -100, -95)
    add("SysplorerEmbeddedCoder.MathOperation.Sum", "gain_sum", -45, -120)
    add("SysplorerEmbeddedCoder.Discontinuities.Saturation", "gain_limit", -35, -100)
    set_param("gain_bias", "k", "1.0")
    set_param("schedule_gain", "k", "0.4")
    set_param("fuzzy_gain", "k", "0.3")
    set_param("neural_limit", "upLimit", "0.25")
    set_param("neural_limit", "lowLimit", "-0.25")
    set_param("neural_gain", "k", "0.2")
    set_param("gain_sum_schedule", "inputs", "++")
    set_param("gain_sum_fuzzy", "inputs", "++")
    set_param("gain_sum", "inputs", "++")
    set_param("gain_limit", "upLimit", "4.0")
    set_param("gain_limit", "lowLimit", "0.25")
    connect("schedule", "schedule_gain.u")
    connect("fuzzy_error", "fuzzy_gain.u")
    connect("neural_residual", "neural_limit.u")
    connect("neural_limit.y", "neural_gain.u")
    connect("gain_bias.y", "gain_sum_schedule.u1")
    connect("schedule_gain.y", "gain_sum_schedule.u2")
    connect("gain_sum_schedule.y", "gain_sum_fuzzy.u1")
    connect("fuzzy_gain.y", "gain_sum_fuzzy.u2")
    connect("gain_sum_fuzzy.y", "gain_sum.u1")
    connect("neural_gain.y", "gain_sum.u2")
    connect("gain_sum.y", "gain_limit.u")
    connect("gain_limit.y", "scheduled_gain")

    # Main PID branch uses code-generation-compatible discrete state blocks.
    add("SysplorerEmbeddedCoder.MathOperation.Sum", "error_sum", -225, 155)
    add("SysplorerEmbeddedCoder.MathOperation.Product", "effective_error", -155, 155)
    add("SysplorerEmbeddedCoder.MathOperation.Gain", "kp_gain", -85, 205)
    add("SysplorerEmbeddedCoder.MathOperation.Gain", "ki_drive", -85, 145)
    add("SysplorerEmbeddedCoder.Discrete.Difference", "derivative", -85, 85)
    add("SysplorerEmbeddedCoder.MathOperation.Gain", "kd_gain", -15, 85)
    add("SysplorerEmbeddedCoder.MathOperation.Sum", "integrator_drive", -15, 145)
    add("SysplorerEmbeddedCoder.MathOperation.Gain", "integral_dt", 25, 145)
    add("SysplorerEmbeddedCoder.MathOperation.Sum", "integral_update", 55, 145)
    add("SysplorerEmbeddedCoder.Discontinuities.Saturation", "integral_limit", 85, 145)
    add("SysplorerEmbeddedCoder.Discrete.UnitDelay", "integrator", 115, 145)
    add("SysplorerEmbeddedCoder.MathOperation.Gain", "ki_gain", 145, 145)
    add("SysplorerEmbeddedCoder.MathOperation.Gain", "feedforward_gain", -15, 10)
    add("SysplorerEmbeddedCoder.MathOperation.Sum", "pid_sum_pi", 135, 175)
    add("SysplorerEmbeddedCoder.MathOperation.Sum", "pid_sum_pid", 175, 145)
    add("SysplorerEmbeddedCoder.MathOperation.Sum", "pid_sum", 210, 115)
    add("SysplorerEmbeddedCoder.Discontinuities.Saturation", "output_limit", 235, 125)
    add("SysplorerEmbeddedCoder.MathOperation.Sum", "saturation_error", 235, 25)
    add("SysplorerEmbeddedCoder.MathOperation.Gain", "anti_windup_gain", 165, 25)
    set_param("error_sum", "inputs", "+-")
    set_param("effective_error", "inputs", "**")
    set_param("kp_gain", "k", "1.2")
    set_param("ki_drive", "k", "1.0")
    # Difference returns e[k]-e[k-1], so kd includes 1 / Ts for Ts=0.02 s.
    set_param("kd_gain", "k", "5.0")
    set_param("integrator_drive", "inputs", "++")
    set_param("integral_dt", "k", "0.02")
    set_param("integral_update", "inputs", "++")
    set_param("integral_limit", "upLimit", "0.5")
    set_param("integral_limit", "lowLimit", "-0.5")
    set_param("integrator", "initCond", "0.0")
    set_param("ki_gain", "k", "0.8")
    set_param("feedforward_gain", "k", "0.5")
    set_param("pid_sum_pi", "inputs", "++")
    set_param("pid_sum_pid", "inputs", "++")
    set_param("pid_sum", "inputs", "++")
    set_param("output_limit", "upLimit", "1.0")
    set_param("output_limit", "lowLimit", "-1.0")
    set_param("saturation_error", "inputs", "+-")
    set_param("anti_windup_gain", "k", "0.4")
    connect("setpoint", "error_sum.u1")
    connect("measurement", "error_sum.u2")
    connect("error_sum.y", "effective_error.u1")
    connect("gain_limit.y", "effective_error.u2")
    connect("effective_error.y", "kp_gain.u")
    connect("effective_error.y", "ki_drive.u")
    connect("error_sum.y", "derivative.u")
    connect("derivative.y", "kd_gain.u")
    connect("ki_drive.y", "integrator_drive.u1")
    connect("anti_windup_gain.y", "integrator_drive.u2")
    connect("integrator_drive.y", "integral_dt.u")
    connect("integral_dt.y", "integral_update.u1")
    connect("integrator.y", "integral_update.u2")
    connect("integral_update.y", "integral_limit.u")
    connect("integral_limit.y", "integrator.u1")
    connect("integrator.y", "ki_gain.u")
    connect("feedforward", "feedforward_gain.u")
    connect("kp_gain.y", "pid_sum_pi.u1")
    connect("ki_gain.y", "pid_sum_pi.u2")
    connect("pid_sum_pi.y", "pid_sum_pid.u1")
    connect("kd_gain.y", "pid_sum_pid.u2")
    connect("pid_sum_pid.y", "pid_sum.u1")
    connect("feedforward_gain.y", "pid_sum.u2")
    connect("pid_sum.y", "output_limit.u")
    connect("output_limit.y", "saturation_error.u1")
    connect("pid_sum.y", "saturation_error.u2")
    connect("saturation_error.y", "anti_windup_gain.u")
    connect("pid_sum.y", "unsaturated_command")
    connect("integrator.y", "integral_state")

    # Visible cascade branch. It remains separately gated for numerical equivalence.
    add("SysplorerEmbeddedCoder.MathOperation.Sum", "outer_error", -155, 270)
    add("SysplorerEmbeddedCoder.MathOperation.Gain", "outer_gain", -85, 270)
    add("SysplorerEmbeddedCoder.Discontinuities.Saturation", "outer_limit", -15, 270)
    add("SysplorerEmbeddedCoder.MathOperation.Sum", "inner_error", 55, 250)
    add("SysplorerEmbeddedCoder.MathOperation.Gain", "inner_gain", 125, 250)
    add("SysplorerEmbeddedCoder.Discontinuities.Saturation", "inner_limit", 190, 250)
    set_param("outer_error", "inputs", "+-")
    set_param("outer_gain", "k", "1.2")
    set_param("outer_limit", "upLimit", "1.0")
    set_param("outer_limit", "lowLimit", "-1.0")
    set_param("inner_error", "inputs", "+-")
    set_param("inner_gain", "k", "1.5")
    set_param("inner_limit", "upLimit", "1.0")
    set_param("inner_limit", "lowLimit", "-1.0")
    connect("setpoint", "outer_error.u1")
    connect("measurement", "outer_error.u2")
    connect("outer_error.y", "outer_gain.u")
    connect("outer_gain.y", "outer_limit.u")
    connect("outer_limit.y", "inner_error.u1")
    connect("inner_measurement", "inner_error.u2")
    connect("inner_error.y", "inner_gain.u")
    connect("inner_gain.y", "inner_limit.u")
    connect("outer_limit.y", "outer_command")

    # Mode and enable switches make the selected command path explicit.
    add("SysplorerEmbeddedCoder.SignalRouting.Switch", "cascade_switch", 270, 200)
    add("SysplorerEmbeddedCoder.Sources.Constant", "zero_source", 235, -45)
    add("SysplorerEmbeddedCoder.SignalRouting.Switch", "enable_switch", 305, 120)
    set_param("cascade_switch", "threshold", "0.5")
    set_param("zero_source", "k", "0.0")
    set_param("enable_switch", "threshold", "0.5")
    connect("inner_limit.y", "cascade_switch.u1")
    connect("cascade_mode", "cascade_switch.u2")
    connect("output_limit.y", "cascade_switch.u3")
    connect("cascade_switch.y", "enable_switch.u1")
    connect("enable", "enable_switch.u2")
    connect("zero_source.y", "enable_switch.u3")
    connect("enable_switch.y", "command")

    descriptions = {
        "gain_sum": "Gain scheduling + fuzzy + bounded neural residual",
        "integrator": "Bounded discrete integral state at Ts=0.02 s",
        "saturation_error": "Tracking anti-windup error: saturated - unsaturated",
        "outer_error": "Cascade outer-loop error",
        "inner_error": "Cascade inner-loop error",
        "cascade_switch": "Select cascade or single-loop PID",
    }
    for component, description in descriptions.items():
        ModelingPy.SetComponentDescription(MODEL_NAME, component, description)

    target_model_path = MODEL_DIR / f"{MODEL_NAME}.mo"
    model_saved = (
        ModelingPy.SaveModel(MODEL_NAME)
        if target_model_path.exists()
        else ModelingPy.SaveModelAs(MODEL_NAME, str(MODEL_DIR), MODEL_NAME)
    )
    diagram_path = SCREENSHOT_DIR / f"{MODEL_NAME}.png"
    diagram_exported = ModelingPy.ExportDiagram(MODEL_NAME, str(diagram_path), 1800, 1100)
    check_model_result = ModelingPy.CheckModel(MODEL_NAME)
    components = list(ModelingPy.GetComponents(MODEL_NAME))
    ports = {component: list(ModelingPy.GetComponentPorts(MODEL_NAME, component, 0)) for component in components}
    model_text = ModelingPy.GetModelText(MODEL_NAME)
    connection_count = str(model_text).count("connect(")
    line_annotation_count = str(model_text).count("annotation(Line")
    structure_ok = bool(
        model_saved
        and diagram_exported
        and check_model_result
        and len(components) == 51
        and connection_count >= 45
        and line_annotation_count == connection_count
    )
    manifest = {
        "schema": "mosim.pid_graphical_sysblock_build.v1",
        "source": "MWORKS_MCP",
        "model_name": MODEL_NAME,
        "model_path": str(target_model_path),
        "diagram_path": str(diagram_path),
        "model_saved": bool(model_saved),
        "diagram_exported": bool(diagram_exported),
        "check_model": bool(check_model_result),
        "connection_count": connection_count,
        "line_annotation_count": line_annotation_count,
        "components": components,
        "component_ports": ports,
        "required_behavior_blocks": {
            "gain_schedule": ["schedule_gain", "gain_sum_schedule", "gain_sum_fuzzy", "gain_sum", "gain_limit"],
            "fuzzy_residual": ["fuzzy_gain"],
            "neural_residual": ["neural_limit", "neural_gain"],
            "integral_limit": ["integral_dt", "integral_update", "integral_limit", "integrator"],
            "anti_windup": ["saturation_error", "anti_windup_gain", "integrator_drive"],
            "feedforward": ["feedforward_gain"],
            "cascade": ["outer_error", "outer_limit", "inner_error", "inner_limit"],
            "mode_enable": ["cascade_switch", "enable_switch"],
        },
        "structure_ok": structure_ok,
        "behavior_equivalence_ok": False,
        "claim_boundary": (
            "Built with official Sysplorer graphical APIs. structure_ok covers "
            "component, wiring, exported-diagram, and CheckModel gates only. "
            "Behavior remains open until equation-bridge comparison passes."
        ),
    }
    manifest_path = LOG_DIR / "pid_graphical_build_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": structure_ok,
        "manifest": str(manifest_path),
        "component_count": len(components),
        "connection_count": connection_count,
    }


RUN_SCRIPT_RESULT = build()
