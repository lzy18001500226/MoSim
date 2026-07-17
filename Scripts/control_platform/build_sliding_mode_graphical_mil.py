#!/usr/bin/env python3
"""Build six native P3 graphical sliding-mode cores and compare with CFunction MIL."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
RESULT_DIR = ROOT / "Results/control_platform/p3_sliding_mode_mworks_20260716"
MODEL_DIR = RESULT_DIR / "models/graphical_variants"
REFERENCE_DIR = RESULT_DIR / "raw/cfunction_variants"
GRAPHICAL_DIR = RESULT_DIR / "raw/graphical_variants"
SCREENSHOT_DIR = RESULT_DIR / "screenshots/graphical_variants"
LOG_DIR = RESULT_DIR / "logs"
DT = 0.01
AXES = ("x", "y", "z")
ALGORITHMS = {
    "integral_smc": "MoSim_P3_INTEGRAL_SMC_MIL",
    "terminal_smc": "MoSim_P3_TERMINAL_SMC_MIL",
    "nonsingular_terminal_smc": "MoSim_P3_NONSINGULAR_TERMINAL_SMC_MIL",
    "super_twisting_smc": "MoSim_P3_SUPER_TWISTING_SMC_MIL",
    "adaptive_smc": "MoSim_P3_ADAPTIVE_SMC_MIL",
    "fuzzy_smc": "MoSim_P3_FUZZY_SMC_MIL",
}
INPUT = {
    "position": (0.2, -0.1, 0.7), "velocity": (-0.3, 0.2, -0.1),
    "reference_position": (1.0, 0.5, 1.2), "reference_velocity": (0.1, -0.2, 0.0),
    "reference_acceleration": (0.05, -0.04, 0.02),
}
PARAMS = {
    "lambda": (1.2, 1.2, 1.4), "linear": (0.8, 0.8, 1.0),
    "reaching": (2.2, 2.2, 2.8), "boundary": (0.12, 0.12, 0.15),
    "integral_gain": (0.20, 0.20, 0.25), "integral_limit": (1.5, 1.5, 1.8),
    "terminal_alpha": (0.72, 0.72, 0.78), "nonsingular_gain": (0.35, 0.35, 0.40),
    "st_k1": (1.6, 1.6, 2.0), "st_k2": (1.2, 1.2, 1.5),
    "adaptive_rate": (0.8, 0.8, 1.0), "adaptive_limit": (5.0, 5.0, 6.0),
    "fuzzy_delta": (1.0, 1.0, 1.2), "gravity": 9.80665,
}
OUTPUTS = [
    *(f"desired_acceleration_{axis}" for axis in AXES),
    *(f"sliding_surface_{axis}" for axis in AXES),
    *(f"auxiliary_state_{axis}" for axis in AXES),
    *(f"effective_reaching_gain_{axis}" for axis in AXES),
]


def add(model: str, type_name: str, name: str, x: float, y: float) -> None:
    if not ModelingPy.AddComponent(type_name, model, name, x, y, 26, 20):
        raise RuntimeError(f"AddComponent failed: {model}.{name} ({type_name})")


def set_param(name: str, parameter: str, value: object) -> None:
    encoded = f'"{value}"' if parameter == "inputs" else str(value)
    if not ModelingPy.SetParamValue(f"{name}.{parameter}", encoded):
        raise RuntimeError(f"SetParamValue failed: {name}.{parameter}={encoded}")


def connect(model: str, source: str, target: str) -> None:
    if not ModelingPy.ConnectPort(model, source, target):
        raise RuntimeError(f"ConnectPort failed: {model}: {source} -> {target}")


def block(model: str, type_name: str, name: str, x: float, y: float, **params: object) -> str:
    add(model, type_name, name, x, y)
    for key, value in params.items():
        set_param(name, key, value)
    return name


def constant(model: str, name: str, value: float, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.Sources.Constant", name, x, y, k=value)
    return f"{name}.y"


def gain(model: str, name: str, source: str, value: float, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.MathOperation.Gain", name, x, y, k=value)
    connect(model, source, f"{name}.u")
    return f"{name}.y"


def sum_ports(model: str, name: str, sources: list[str], signs: str, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.MathOperation.Sum", name, x, y, inputs=signs)
    for index, source in enumerate(sources, start=1):
        connect(model, source, f"{name}.u{index}")
    return f"{name}.y"


def product(model: str, name: str, left: str, right: str, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.MathOperation.Product", name, x, y, inputs="**")
    connect(model, left, f"{name}.u1"); connect(model, right, f"{name}.u2")
    return f"{name}.y"


def saturation(model: str, name: str, source: str, low: float, high: float, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.Discontinuities.Saturation", name, x, y, lowLimit=low, upLimit=high)
    connect(model, source, f"{name}.u")
    return f"{name}.y"


def absolute(model: str, name: str, source: str, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.MathOperation.Abs", name, x, y)
    connect(model, source, f"{name}.u")
    return f"{name}.y"


def sign(model: str, name: str, source: str, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.MathOperation.Sign", name, x, y)
    connect(model, source, f"{name}.u")
    return f"{name}.y"


def power(model: str, name: str, source: str, exponent: float, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.MathOperation.MathFunction", name, x, y,
          operatorType="SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.pow")
    exponent_source = constant(model, f"{name}_exponent", exponent, x - 30, y - 30)
    connect(model, source, f"{name}.u1"); connect(model, exponent_source, f"{name}.u2")
    return f"{name}.y"


def prepare_model(model: str, description: str) -> None:
    if not ModelingPy.ClassExist(model) and not ModelingPy.NewModel(model, "Sysblock", description):
        raise RuntimeError(f"NewModel failed: {model}")
    if not ModelingPy.OpenModel(model, "diagram"):
        raise RuntimeError(f"OpenModel failed: {model}")
    for component in list(ModelingPy.GetComponents(model)):
        if not ModelingPy.RemoveComponent(model, component):
            raise RuntimeError(f"RemoveComponent failed: {model}.{component}")


def common_sources(model: str) -> dict[str, list[str]]:
    result = {}
    for row_index, row in enumerate(INPUT):
        result[row] = [constant(model, f"{row}_{axis}", INPUT[row][axis_index],
                                -700 + axis_index * 55, 420 - row_index * 55)
                       for axis_index, axis in enumerate(AXES)]
    return result


def axis_core(model: str, algorithm: str, sources: dict[str, list[str]], i: int, y: float) -> dict[str, str]:
    axis = AXES[i]
    ep = sum_ports(model, f"position_error_{axis}", [sources["reference_position"][i], sources["position"][i]], "+-", -530, y + 50)
    ev = sum_ports(model, f"velocity_error_{axis}", [sources["reference_velocity"][i], sources["velocity"][i]], "+-", -530, y - 50)
    lambda_ep = gain(model, f"lambda_position_{axis}", ep, PARAMS["lambda"][i], -445, y + 50)
    sliding = sum_ports(model, f"linear_sliding_surface_{axis}", [ev, lambda_ep], "++", -360, y)
    zero = constant(model, f"zero_{axis}", 0.0, 235, y + 95)
    auxiliary = zero
    effective_gain = constant(model, f"nominal_reaching_gain_{axis}", PARAMS["reaching"][i], -95, y + 130)

    if algorithm == "integral_smc":
        state_name = f"integral_state_{axis}"
        block(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", state_name, -360, y + 120, initCond=0.0)
        increment = gain(model, f"integral_increment_{axis}", ep, DT, -445, y + 120)
        next_raw = sum_ports(model, f"integral_next_raw_{axis}", [f"{state_name}.y", increment], "++", -275, y + 120)
        auxiliary = saturation(model, f"integral_limit_{axis}", next_raw, -PARAMS["integral_limit"][i], PARAMS["integral_limit"][i], -190, y + 120)
        connect(model, auxiliary, f"{state_name}.u1")
        integral_term = gain(model, f"integral_surface_term_{axis}", auxiliary, PARAMS["integral_gain"][i], -105, y + 65)
        sliding = sum_ports(model, f"integral_sliding_surface_{axis}", [sliding, integral_term], "++", -20, y + 45)
    elif algorithm in ("terminal_smc", "nonsingular_terminal_smc"):
        abs_ep = absolute(model, f"position_error_abs_{axis}", ep, -445, y + 130)
        exponent = PARAMS["terminal_alpha"][i] if algorithm == "terminal_smc" else 1.5
        ep_power = power(model, f"position_error_power_{axis}", abs_ep, exponent, -350, y + 130)
        ep_sign = sign(model, f"position_error_sign_{axis}", ep, -350, y + 185)
        signed_ep_power = product(model, f"signed_position_power_{axis}", ep_power, ep_sign, -255, y + 145)
        shape_gain = PARAMS["lambda"][i] if algorithm == "terminal_smc" else PARAMS["nonsingular_gain"][i]
        shape = gain(model, f"terminal_shape_gain_{axis}", signed_ep_power, shape_gain, -170, y + 145)
        sliding = sum_ports(model, f"terminal_sliding_surface_{axis}",
                            [ev, shape] if algorithm == "terminal_smc" else [sliding, shape], "++", -85, y + 100)

    boundary_input = gain(model, f"boundary_normalization_{axis}", sliding, 1.0 / PARAMS["boundary"][i], 5, y)
    boundary_sign = saturation(model, f"boundary_layer_{axis}", boundary_input, -1.0, 1.0, 90, y)

    if algorithm == "super_twisting_smc":
        state_name = f"super_twisting_integral_{axis}"
        block(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", state_name, 5, y + 135, initCond=0.0)
        increment = gain(model, f"super_twisting_increment_{axis}", boundary_sign, PARAMS["st_k2"][i] * DT, 90, y + 135)
        next_raw = sum_ports(model, f"super_twisting_next_raw_{axis}", [f"{state_name}.y", increment], "++", 175, y + 135)
        auxiliary = saturation(model, f"super_twisting_limit_{axis}", next_raw, -PARAMS["adaptive_limit"][i], PARAMS["adaptive_limit"][i], 260, y + 135)
        connect(model, auxiliary, f"{state_name}.u1")
        abs_sliding = absolute(model, f"sliding_abs_{axis}", sliding, 5, y - 95)
        sqrt_sliding = power(model, f"sliding_sqrt_{axis}", abs_sliding, 0.5, 90, y - 95)
        signed_root = product(model, f"signed_sliding_root_{axis}", sqrt_sliding, boundary_sign, 175, y - 75)
        root_term = gain(model, f"super_twisting_root_gain_{axis}", signed_root, PARAMS["st_k1"][i], 260, y - 75)
        robust = sum_ports(model, f"super_twisting_robust_{axis}", [root_term, auxiliary], "++", 345, y)
        effective_gain = constant(model, f"super_twisting_gain_{axis}", PARAMS["st_k1"][i], 345, y + 95)
    elif algorithm == "adaptive_smc":
        state_name = f"adaptive_reaching_gain_{axis}"
        block(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", state_name, 5, y + 135, initCond=0.0)
        abs_sliding = absolute(model, f"sliding_abs_{axis}", sliding, -80, y + 190)
        offset = constant(model, f"adaptive_threshold_{axis}", 0.05, -80, y + 235)
        excess = sum_ports(model, f"adaptive_excess_{axis}", [abs_sliding, offset], "+-", 5, y + 210)
        increment = gain(model, f"adaptive_increment_{axis}", excess, PARAMS["adaptive_rate"][i] * DT, 90, y + 210)
        next_raw = sum_ports(model, f"adaptive_next_raw_{axis}", [f"{state_name}.y", increment], "++", 175, y + 165)
        effective_gain = saturation(model, f"adaptive_gain_limit_{axis}", next_raw, PARAMS["reaching"][i], PARAMS["adaptive_limit"][i], 260, y + 165)
        connect(model, effective_gain, f"{state_name}.u1")
        robust = product(model, f"adaptive_robust_{axis}", effective_gain, boundary_sign, 345, y)
    elif algorithm == "fuzzy_smc":
        abs_sliding = absolute(model, f"sliding_abs_{axis}", sliding, -80, y + 170)
        normalized_raw = gain(model, f"fuzzy_normalization_{axis}", abs_sliding, 1.0 / (4.0 * PARAMS["boundary"][i]), 5, y + 170)
        normalized = saturation(model, f"fuzzy_membership_{axis}", normalized_raw, 0.0, 1.0, 90, y + 170)
        two = constant(model, f"fuzzy_two_{axis}", 2.0, 90, y + 225)
        complement = sum_ports(model, f"fuzzy_complement_{axis}", [two, normalized], "+-", 175, y + 200)
        shape = product(model, f"fuzzy_shape_{axis}", normalized, complement, 260, y + 170)
        delta = gain(model, f"fuzzy_gain_delta_{axis}", shape, PARAMS["fuzzy_delta"][i], 345, y + 170)
        effective_gain = sum_ports(model, f"fuzzy_reaching_gain_{axis}", [effective_gain, delta], "++", 430, y + 130)
        robust = product(model, f"fuzzy_robust_{axis}", effective_gain, boundary_sign, 430, y)
    else:
        robust = product(model, f"reaching_term_{axis}", effective_gain, boundary_sign, 175, y)

    velocity_term = gain(model, f"lambda_velocity_{axis}", ev, PARAMS["lambda"][i], 430, y - 120)
    linear_term = gain(model, f"linear_surface_gain_{axis}", sliding, PARAMS["linear"][i], 430, y - 70)
    feedforward = sum_ports(model, f"feedforward_velocity_sum_{axis}",
                            [sources["reference_acceleration"][i], velocity_term], "++", 500, y - 135)
    feedback = sum_ports(model, f"linear_robust_sum_{axis}",
                         [linear_term, robust], "++", 500, y - 65)
    acceleration = sum_ports(model, f"acceleration_sum_{axis}",
                             [feedforward, feedback], "++", 585, y - 95)
    if axis == "z":
        gravity = constant(model, "gravity", PARAMS["gravity"], 535, y + 45)
        acceleration = sum_ports(model, "gravity_compensation", [acceleration, gravity], "++", 620, y - 10)
    return {"acceleration": acceleration, "sliding": sliding, "auxiliary": auxiliary, "gain": effective_gain}


def write_csv(path: Path, times: list[float], columns: list[list[float]]) -> None:
    if not times or len({len(times), *(len(column) for column in columns)}) != 1:
        raise RuntimeError(f"inconsistent result lengths: {path}")
    if not all(math.isfinite(float(value)) for column in columns for value in column):
        raise RuntimeError(f"NaN/Inf in result: {path}")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["time", *OUTPUTS]); writer.writerows(zip(times, *columns))


def capture_reference(algorithm: str, fixture: str) -> Path:
    if not ModelingPy.ClassExist(fixture) or not ModelingPy.SimulateModelEx(fixture, {"stopTime": 0.2, "interval": DT}):
        raise RuntimeError(f"CFunction simulation failed: {fixture}")
    path = REFERENCE_DIR / f"{algorithm}.csv"
    write_csv(path, list(ModelingPy.GetVarTimes()), [list(v) for v in ModelingPy.GetVarsValues(OUTPUTS)])
    return path


def build_variant(algorithm: str) -> dict[str, object]:
    model = f"MoSim_P3_{algorithm.upper()}_GRAPHICAL_MIL"
    prepare_model(model, f"P3 native graphical sliding-mode controller core: {algorithm}")
    sources = common_sources(model)
    outputs = {}
    for i, axis in enumerate(AXES):
        axis_outputs = axis_core(model, algorithm, sources, i, 260 - i * 310)
        outputs[f"desired_acceleration_{axis}"] = axis_outputs["acceleration"]
        outputs[f"sliding_surface_{axis}"] = axis_outputs["sliding"]
        outputs[f"auxiliary_state_{axis}"] = axis_outputs["auxiliary"]
        outputs[f"effective_reaching_gain_{axis}"] = axis_outputs["gain"]
    for index, output in enumerate(OUTPUTS):
        add(model, "SysplorerEmbeddedCoder.Port.Outport", output, 720, 390 - index * 65)
        connect(model, outputs[output], output)
    feature = {
        "integral_smc": "integral_state_x", "terminal_smc": "terminal_shape_gain_x",
        "nonsingular_terminal_smc": "terminal_shape_gain_x", "super_twisting_smc": "super_twisting_integral_x",
        "adaptive_smc": "adaptive_reaching_gain_x", "fuzzy_smc": "fuzzy_membership_x",
    }[algorithm]
    ModelingPy.SetComponentDescription(model, feature, f"P3 distinguishing state or nonlinear surface for {algorithm}")
    target = MODEL_DIR / f"{model}.mo"
    saved = ModelingPy.SaveModel(model) if target.exists() else ModelingPy.SaveModelAs(model, str(MODEL_DIR), model)
    checked = ModelingPy.CheckModel(model)
    diagram = SCREENSHOT_DIR / f"{model}.png"
    exported = ModelingPy.ExportDiagram(model, str(diagram), 3000, 2000)
    simulated = ModelingPy.SimulateModelEx(model, {"stopTime": 0.2, "interval": DT})
    raw = GRAPHICAL_DIR / f"{algorithm}.csv"
    write_csv(raw, list(ModelingPy.GetVarTimes()), [list(v) for v in ModelingPy.GetVarsValues(OUTPUTS)])
    text = str(ModelingPy.GetModelText(model)); components = len(list(ModelingPy.GetComponents(model)))
    return {"model_name": model, "model_path": str(target), "diagram_path": str(diagram), "raw_csv": str(raw),
            "feature_component": feature, "saved": bool(saved), "check_model": bool(checked),
            "diagram_exported": bool(exported), "simulate_model": bool(simulated), "sample_count": len(list(ModelingPy.GetVarTimes())),
            "component_count": components, "connection_count": text.count("connect("),
            "structure_ok": bool(saved and checked and exported and simulated and components >= 55 and text.count("connect(") >= 55)}


def recover_completed_variant(algorithm: str) -> dict[str, object] | None:
    model = f"MoSim_P3_{algorithm.upper()}_GRAPHICAL_MIL"
    target = MODEL_DIR / f"{model}.mo"
    diagram = SCREENSHOT_DIR / f"{model}.png"
    raw = GRAPHICAL_DIR / f"{algorithm}.csv"
    if not (target.is_file() and diagram.is_file() and raw.is_file()):
        return None
    text = target.read_text(encoding="utf-8")
    sample_count = len(rows(raw))
    component_count = text.count("annotation (Placement(")
    connection_count = text.count("connect(")
    feature = {
        "integral_smc": "integral_state_x", "terminal_smc": "terminal_shape_gain_x",
        "nonsingular_terminal_smc": "terminal_shape_gain_x", "super_twisting_smc": "super_twisting_integral_x",
        "adaptive_smc": "adaptive_reaching_gain_x", "fuzzy_smc": "fuzzy_membership_x",
    }[algorithm]
    complete = sample_count == 21 and component_count >= 55 and connection_count >= 55 and diagram.stat().st_size > 10000
    if not complete:
        return None
    return {"model_name": model, "model_path": str(target), "diagram_path": str(diagram), "raw_csv": str(raw),
            "feature_component": feature, "saved": True, "check_model": True, "diagram_exported": True,
            "simulate_model": True, "sample_count": sample_count, "component_count": component_count,
            "connection_count": connection_count, "structure_ok": True, "recovered_from_complete_artifacts": True}


def rows(path: Path) -> list[dict[str, float]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return [{k: float(v) for k, v in row.items()} for row in csv.DictReader(stream)]


def compare(reference: Path, graphical: Path, tolerance: float = 1.0e-9) -> dict[str, object]:
    expected, actual = rows(reference), rows(graphical)
    sample_ok = len(expected) == len(actual) == 21
    errors = {output: float("inf") for output in OUTPUTS}
    time_error = float("inf")
    if sample_ok:
        time_error = max(abs(a["time"] - b["time"]) for a, b in zip(expected, actual))
        errors = {output: max(abs(a[output] - b[output]) for a, b in zip(expected, actual)) for output in OUTPUTS}
    return {"sample_count_ok": sample_ok, "max_abs_time_error": time_error, "max_abs_error": errors,
            "behavior_equivalence_ok": sample_ok and time_error <= tolerance and all(v <= tolerance for v in errors.values())}


def main() -> dict[str, object]:
    for folder in (MODEL_DIR, REFERENCE_DIR, GRAPHICAL_DIR, SCREENSHOT_DIR, LOG_DIR):
        folder.mkdir(parents=True, exist_ok=True)
    variants = {}
    for algorithm, fixture in ALGORITHMS.items():
        reference = capture_reference(algorithm, fixture)
        graphical = recover_completed_variant(algorithm)
        if graphical is not None:
            equivalence = compare(reference, Path(graphical["raw_csv"]))
            if not equivalence["behavior_equivalence_ok"]:
                graphical = None
        if graphical is None:
            graphical = build_variant(algorithm)
            equivalence = compare(reference, Path(graphical["raw_csv"]))
        variants[algorithm] = {**graphical, "reference_csv": str(reference), **equivalence}
        checkpoint = {"schema": "mosim.p3_sliding_mode_graphical_mil.checkpoint.v1", "variants": variants}
        (LOG_DIR / "p3_sliding_mode_graphical_mil.checkpoint.json").write_text(
            json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8")
    payload = {"schema": "mosim.p3_sliding_mode_graphical_mil.v1", "source_pair": ["MWORKS_CFUNCTION_MIL", "MWORKS_NATIVE_GRAPHICAL_MIL"],
               "sample_time_s": DT, "outputs": OUTPUTS, "variants": variants,
               "all_structure_ok": all(v["structure_ok"] for v in variants.values()),
               "all_behavior_equivalent": all(v["behavior_equivalence_ok"] for v in variants.values()),
               "claim_boundary": "Real MWORKS native graphical controller-core equivalence for six sliding-mode variants and 21 fixed-input samples. Full ATTITUDE_THRUST geometry, generated C/SIL, and Gazebo runtime are separate gates."}
    manifest = LOG_DIR / "p3_sliding_mode_graphical_mil.json"
    manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"ok": payload["all_structure_ok"] and payload["all_behavior_equivalent"], "manifest": str(manifest), "variants": variants}


RUN_SCRIPT_RESULT = main()
