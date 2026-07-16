#!/usr/bin/env python3
"""Build and simulate six fixed-input PID-family graphical MIL models."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
RESULT_DIR = ROOT / "Results/control_platform/p1_pid_mworks_20260716"
MODEL_DIR = RESULT_DIR / "models/graphical_variants"
RAW_DIR = RESULT_DIR / "raw/graphical_variants"
SCREENSHOT_DIR = RESULT_DIR / "screenshots/graphical_variants"
LOG_DIR = RESULT_DIR / "logs"
DT = 0.01
OUTPUTS = ["command", "outer_command", "unsaturated_command", "integral", "scheduled_gain"]
BASE_INPUTS = {
    "setpoint": 0.5,
    "measurement": 0.1,
    "inner_measurement": 0.05,
    "feedforward": 0.3,
    "schedule": 0.5,
    "fuzzy_error": 0.4,
    "neural_residual": 0.1,
}
BASE_CONFIG = {
    "kp": 1.2,
    "ki": 0.8,
    "kd": 0.1,
    "feedforward_gain": 0.0,
    "output_min": -1.0,
    "output_max": 1.0,
    "integral_min": -0.5,
    "integral_max": 0.5,
    "anti_windup_gain": 0.4,
    "derivative_filter_tau": 0.05,
    "schedule_gain": 0.0,
    "fuzzy_gain": 0.0,
    "neural_gain": 0.0,
    "neural_residual_limit": 0.0,
}
INNER_CONFIG = {
    **BASE_CONFIG,
    "kp": 1.5,
    "ki": 0.4,
    "kd": 0.05,
    "derivative_filter_tau": 0.03,
}
VARIANTS = {
    "cascade_pid": {},
    "gain_scheduled_pid": {"schedule_gain": 0.4},
    "fuzzy_pid": {"fuzzy_gain": 0.3},
    "neural_pid": {"neural_gain": 0.2, "neural_residual_limit": 0.25},
    "anti_windup": {"anti_windup_gain": 1.0, "setpoint": 2.0},
    "feedforward_profile": {"feedforward_gain": 0.5},
}


def add(model: str, type_name: str, name: str, x: float, y: float) -> None:
    if not ModelingPy.AddComponent(type_name, model, name, x, y, 28, 22):
        raise RuntimeError(f"AddComponent failed: {model}.{name} ({type_name})")


def set_param(name: str, parameter: str, value: object) -> None:
    encoded = f'"{value}"' if parameter == "inputs" else str(value)
    if not ModelingPy.SetParamValue(f"{name}.{parameter}", encoded):
        raise RuntimeError(f"SetParamValue failed: {name}.{parameter}={value}")


def connect(model: str, source: str, target: str) -> None:
    if not ModelingPy.ConnectPort(model, source, target):
        raise RuntimeError(f"ConnectPort failed: {model}: {source} -> {target}")


def constant(model: str, name: str, value: float, x: float, y: float) -> str:
    add(model, "SysplorerEmbeddedCoder.Sources.Constant", name, x, y)
    set_param(name, "k", value)
    return f"{name}.y"


def configured(model: str, type_name: str, name: str, x: float, y: float, **parameters: object) -> str:
    add(model, type_name, name, x, y)
    for parameter, value in parameters.items():
        set_param(name, parameter, value)
    return name


def pid_chain(
    model: str,
    prefix: str,
    config: dict[str, float],
    sources: dict[str, str],
    initial_error: float,
    y_base: float,
) -> dict[str, str]:
    n = lambda name: f"{prefix}_{name}"

    configured(model, "SysplorerEmbeddedCoder.MathOperation.Sum", n("error"), -330, y_base, inputs="+-")
    connect(model, sources["setpoint"], f"{n('error')}.u1")
    connect(model, sources["measurement"], f"{n('error')}.u2")

    constant(model, n("gain_bias"), 1.0, -330, y_base + 190)
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Gain", n("schedule_term"), -255, y_base + 240, k=config["schedule_gain"])
    configured(model, "SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction", n("fuzzy_tanh"), -330, y_base + 285,
               operatorType="SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction.TrigonometricType.tanh")
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Gain", n("fuzzy_term"), -255, y_base + 285, k=config["fuzzy_gain"])
    configured(model, "SysplorerEmbeddedCoder.Discontinuities.Saturation", n("neural_limit"), -330, y_base + 335,
               upLimit=config["neural_residual_limit"], lowLimit=-config["neural_residual_limit"])
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Gain", n("neural_term"), -255, y_base + 335, k=config["neural_gain"])
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Sum", n("gain_sum_a"), -175, y_base + 225, inputs="++")
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Sum", n("gain_sum_b"), -100, y_base + 255, inputs="++")
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Sum", n("gain_sum_c"), -25, y_base + 285, inputs="++")
    configured(model, "SysplorerEmbeddedCoder.Discontinuities.Saturation", n("gain_limit"), 50, y_base + 285,
               upLimit=4.0, lowLimit=0.25)
    connect(model, sources["schedule"], f"{n('schedule_term')}.u")
    connect(model, sources["fuzzy_error"], f"{n('fuzzy_tanh')}.u1")
    connect(model, f"{n('fuzzy_tanh')}.y1", f"{n('fuzzy_term')}.u")
    connect(model, sources["neural_residual"], f"{n('neural_limit')}.u")
    connect(model, f"{n('neural_limit')}.y", f"{n('neural_term')}.u")
    connect(model, f"{n('gain_bias')}.y", f"{n('gain_sum_a')}.u1")
    connect(model, f"{n('schedule_term')}.y", f"{n('gain_sum_a')}.u2")
    connect(model, f"{n('gain_sum_a')}.y", f"{n('gain_sum_b')}.u1")
    connect(model, f"{n('fuzzy_term')}.y", f"{n('gain_sum_b')}.u2")
    connect(model, f"{n('gain_sum_b')}.y", f"{n('gain_sum_c')}.u1")
    connect(model, f"{n('neural_term')}.y", f"{n('gain_sum_c')}.u2")
    connect(model, f"{n('gain_sum_c')}.y", f"{n('gain_limit')}.u")

    configured(model, "SysplorerEmbeddedCoder.MathOperation.Product", n("gain_error"), -245, y_base + 45, inputs="**")
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Gain", n("p_term"), -165, y_base + 45, k=config["kp"])
    connect(model, f"{n('gain_limit')}.y", f"{n('gain_error')}.u1")
    connect(model, f"{n('error')}.y", f"{n('gain_error')}.u2")
    connect(model, f"{n('gain_error')}.y", f"{n('p_term')}.u")

    configured(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", n("previous_error"), -255, y_base - 65, initCond=initial_error)
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Sum", n("error_delta"), -175, y_base - 45, inputs="+-")
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Gain", n("derivative_rate"), -100, y_base - 45, k=1.0 / DT)
    configured(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", n("filter_state"), -100, y_base - 125, initCond=0.0)
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Sum", n("filter_delta"), -25, y_base - 65, inputs="+-")
    alpha = DT / (config["derivative_filter_tau"] + DT) if config["derivative_filter_tau"] > 0 else 1.0
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Gain", n("filter_alpha"), 50, y_base - 65, k=alpha)
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Sum", n("filter_update"), 125, y_base - 90, inputs="++")
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Product", n("gain_derivative"), 200, y_base - 70, inputs="**")
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Gain", n("d_term"), 275, y_base - 70, k=config["kd"])
    connect(model, f"{n('error')}.y", f"{n('previous_error')}.u1")
    connect(model, f"{n('error')}.y", f"{n('error_delta')}.u1")
    connect(model, f"{n('previous_error')}.y", f"{n('error_delta')}.u2")
    connect(model, f"{n('error_delta')}.y", f"{n('derivative_rate')}.u")
    connect(model, f"{n('derivative_rate')}.y", f"{n('filter_delta')}.u1")
    connect(model, f"{n('filter_state')}.y", f"{n('filter_delta')}.u2")
    connect(model, f"{n('filter_delta')}.y", f"{n('filter_alpha')}.u")
    connect(model, f"{n('filter_state')}.y", f"{n('filter_update')}.u1")
    connect(model, f"{n('filter_alpha')}.y", f"{n('filter_update')}.u2")
    connect(model, f"{n('filter_update')}.y", f"{n('filter_state')}.u1")
    connect(model, f"{n('gain_limit')}.y", f"{n('gain_derivative')}.u1")
    connect(model, f"{n('filter_update')}.y", f"{n('gain_derivative')}.u2")
    connect(model, f"{n('gain_derivative')}.y", f"{n('d_term')}.u")

    configured(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", n("integral_state"), -245, y_base - 190, initCond=0.0)
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Product", n("integral_drive"), -165, y_base - 165, inputs="**")
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Gain", n("integral_dt"), -90, y_base - 165, k=DT)
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Sum", n("integral_pre"), -15, y_base - 190, inputs="++")
    configured(model, "SysplorerEmbeddedCoder.Discontinuities.Saturation", n("integral_pre_limit"), 60, y_base - 190,
               upLimit=config["integral_max"], lowLimit=config["integral_min"])
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Gain", n("i_term"), 135, y_base - 180, k=config["ki"])
    connect(model, f"{n('gain_limit')}.y", f"{n('integral_drive')}.u1")
    connect(model, f"{n('error')}.y", f"{n('integral_drive')}.u2")
    connect(model, f"{n('integral_drive')}.y", f"{n('integral_dt')}.u")
    connect(model, f"{n('integral_state')}.y", f"{n('integral_pre')}.u1")
    connect(model, f"{n('integral_dt')}.y", f"{n('integral_pre')}.u2")
    connect(model, f"{n('integral_pre')}.y", f"{n('integral_pre_limit')}.u")
    connect(model, f"{n('integral_pre_limit')}.y", f"{n('i_term')}.u")

    configured(model, "SysplorerEmbeddedCoder.MathOperation.Gain", n("feedforward"), 135, y_base + 105, k=config["feedforward_gain"])
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Sum", n("pi_sum"), 215, y_base + 25, inputs="++")
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Sum", n("pid_sum"), 290, y_base, inputs="++")
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Sum", n("unsaturated"), 365, y_base + 30, inputs="++")
    configured(model, "SysplorerEmbeddedCoder.Discontinuities.Saturation", n("command_limit"), 440, y_base + 30,
               upLimit=config["output_max"], lowLimit=config["output_min"])
    connect(model, sources["feedforward"], f"{n('feedforward')}.u")
    connect(model, f"{n('p_term')}.y", f"{n('pi_sum')}.u1")
    connect(model, f"{n('i_term')}.y", f"{n('pi_sum')}.u2")
    connect(model, f"{n('pi_sum')}.y", f"{n('pid_sum')}.u1")
    connect(model, f"{n('d_term')}.y", f"{n('pid_sum')}.u2")
    connect(model, f"{n('pid_sum')}.y", f"{n('unsaturated')}.u1")
    connect(model, f"{n('feedforward')}.y", f"{n('unsaturated')}.u2")
    connect(model, f"{n('unsaturated')}.y", f"{n('command_limit')}.u")

    configured(model, "SysplorerEmbeddedCoder.MathOperation.Sum", n("saturation_error"), 365, y_base - 120, inputs="+-")
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Gain", n("aw_correction"), 440, y_base - 120,
               k=config["anti_windup_gain"] * DT)
    configured(model, "SysplorerEmbeddedCoder.MathOperation.Sum", n("integral_final"), 515, y_base - 165, inputs="++")
    configured(model, "SysplorerEmbeddedCoder.Discontinuities.Saturation", n("integral_final_limit"), 590, y_base - 165,
               upLimit=config["integral_max"], lowLimit=config["integral_min"])
    connect(model, f"{n('command_limit')}.y", f"{n('saturation_error')}.u1")
    connect(model, f"{n('unsaturated')}.y", f"{n('saturation_error')}.u2")
    connect(model, f"{n('saturation_error')}.y", f"{n('aw_correction')}.u")
    connect(model, f"{n('integral_pre_limit')}.y", f"{n('integral_final')}.u1")
    connect(model, f"{n('aw_correction')}.y", f"{n('integral_final')}.u2")
    connect(model, f"{n('integral_final')}.y", f"{n('integral_final_limit')}.u")
    connect(model, f"{n('integral_final_limit')}.y", f"{n('integral_state')}.u1")

    return {
        "command": f"{n('command_limit')}.y",
        "unsaturated": f"{n('unsaturated')}.y",
        "integral": f"{n('integral_final_limit')}.y",
        "scheduled_gain": f"{n('gain_limit')}.y",
    }


def build_variant(algorithm_id: str, overrides: dict[str, float]) -> dict[str, object]:
    model = f"MoSim_PID_{algorithm_id.upper()}_GRAPHICAL_MIL"
    inputs = dict(BASE_INPUTS)
    inputs["setpoint"] = float(overrides.get("setpoint", inputs["setpoint"]))
    config = {**BASE_CONFIG, **{k: v for k, v in overrides.items() if k in BASE_CONFIG}}
    if not ModelingPy.ClassExist(model):
        if not ModelingPy.NewModel(model, "Sysblock", f"Exact fixed-input graphical MIL for {algorithm_id}"):
            raise RuntimeError(f"NewModel failed: {model}")
    if not ModelingPy.OpenModel(model, "diagram"):
        raise RuntimeError(f"OpenModel failed: {model}")
    for component in list(ModelingPy.GetComponents(model)):
        if not ModelingPy.RemoveComponent(model, component):
            raise RuntimeError(f"RemoveComponent failed: {model}.{component}")

    source_ports: dict[str, str] = {}
    for index, (name, value) in enumerate(inputs.items()):
        source_ports[name] = constant(model, f"{name}_source", value, -510, 300 - index * 75)
    zero = constant(model, "zero_source", 0.0, 520, 300)
    one = constant(model, "one_source", 1.0, 520, 250)

    if algorithm_id == "cascade_pid":
        outer = pid_chain(model, "outer", config, {
            "setpoint": source_ports["setpoint"],
            "measurement": source_ports["measurement"],
            "feedforward": source_ports["feedforward"],
            "schedule": source_ports["schedule"],
            "fuzzy_error": source_ports["fuzzy_error"],
            "neural_residual": source_ports["neural_residual"],
        }, inputs["setpoint"] - inputs["measurement"], 280)
        first_outer_integral = (inputs["setpoint"] - inputs["measurement"]) * DT
        first_outer = max(config["output_min"], min(config["output_max"],
            config["kp"] * (inputs["setpoint"] - inputs["measurement"]) + config["ki"] * first_outer_integral))
        inner = pid_chain(model, "inner", INNER_CONFIG, {
            "setpoint": outer["command"],
            "measurement": source_ports["inner_measurement"],
            "feedforward": source_ports["feedforward"],
            "schedule": source_ports["schedule"],
            "fuzzy_error": source_ports["fuzzy_error"],
            "neural_residual": source_ports["neural_residual"],
        }, first_outer - inputs["inner_measurement"], -300)
        output_ports = {
            "command": inner["command"],
            "outer_command": outer["command"],
            "unsaturated_command": inner["command"],
            "integral": inner["integral"],
            "scheduled_gain": one,
        }
    else:
        chain = pid_chain(model, "pid", config, {
            "setpoint": source_ports["setpoint"],
            "measurement": source_ports["measurement"],
            "feedforward": source_ports["feedforward"],
            "schedule": source_ports["schedule"],
            "fuzzy_error": source_ports["fuzzy_error"],
            "neural_residual": source_ports["neural_residual"],
        }, inputs["setpoint"] - inputs["measurement"], 0)
        output_ports = {
            "command": chain["command"],
            "outer_command": zero,
            "unsaturated_command": chain["unsaturated"],
            "integral": chain["integral"],
            "scheduled_gain": chain["scheduled_gain"],
        }

    for index, name in enumerate(OUTPUTS):
        add(model, "SysplorerEmbeddedCoder.Port.Outport", name, 700, 130 - index * 70)
        connect(model, output_ports[name], name)

    target = MODEL_DIR / f"{model}.mo"
    saved = ModelingPy.SaveModel(model) if target.exists() else ModelingPy.SaveModelAs(model, str(MODEL_DIR), model)
    checked = ModelingPy.CheckModel(model)
    diagram = SCREENSHOT_DIR / f"{model}.png"
    exported = ModelingPy.ExportDiagram(model, str(diagram), 2600, 1800)
    simulated = ModelingPy.SimulateModelEx(model, {"stopTime": 0.2, "interval": DT})
    times = list(ModelingPy.GetVarTimes())
    columns = [list(values) for values in ModelingPy.GetVarsValues(OUTPUTS)]
    if not times or len({len(times), *(len(column) for column in columns)}) != 1:
        raise RuntimeError(f"inconsistent simulation lengths: {model}")
    if not all(math.isfinite(float(value)) for column in columns for value in column):
        raise RuntimeError(f"NaN/Inf in graphical MIL: {model}")
    raw_path = RAW_DIR / f"{algorithm_id}.csv"
    with raw_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["time", *OUTPUTS])
        writer.writerows(zip(times, *columns))
    model_text = str(ModelingPy.GetModelText(model))
    component_count = len(list(ModelingPy.GetComponents(model)))
    connection_count = model_text.count("connect(")
    return {
        "model_name": model,
        "model_path": str(target),
        "diagram_path": str(diagram),
        "raw_csv": str(raw_path),
        "raw_csv_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        "saved": bool(saved),
        "check_model": bool(checked),
        "diagram_exported": bool(exported),
        "simulate_model": bool(simulated),
        "sample_count": len(times),
        "component_count": component_count,
        "connection_count": connection_count,
        "line_annotation_count": model_text.count("annotation(Line"),
        "inputs": inputs,
        "config": config,
        "ok": bool(saved and checked and exported and simulated and len(times) == 21),
    }


def main() -> dict[str, object]:
    for folder in (MODEL_DIR, RAW_DIR, SCREENSHOT_DIR, LOG_DIR):
        folder.mkdir(parents=True, exist_ok=True)
    variants = {algorithm_id: build_variant(algorithm_id, overrides) for algorithm_id, overrides in VARIANTS.items()}
    payload = {
        "schema": "mosim.pid_graphical_variant_mil.v1",
        "source": "MWORKS_MCP",
        "sample_time_s": DT,
        "outputs": OUTPUTS,
        "variants": variants,
        "six_variant_graphical_mil_ok": all(item["ok"] for item in variants.values()),
        "claim_boundary": (
            "Six real fixed-input graphical MIL models. This gate covers the configured 21-sample trajectories only; "
            "dynamic reset/enable, ATTITUDE_THRUST, and Gazebo/PX4/MAVROS remain open."
        ),
    }
    manifest = LOG_DIR / "pid_graphical_variant_mil.json"
    manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"ok": payload["six_variant_graphical_mil_ok"], "manifest": str(manifest), "variants": variants}


RUN_SCRIPT_RESULT = main()
