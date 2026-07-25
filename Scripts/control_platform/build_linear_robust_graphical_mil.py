#!/usr/bin/env python3
"""Build and compare four fixed-input P2 graphical controller-core MIL models.

Run in Sysplorer through ``call_code(mode="run_script")``.  The diagrams expose
the observer, feedback, storage, and adaptive-state paths.  Attitude/thrust
geometry remains in the separately gated full-contract CFunction model.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
RESULT_DIR = ROOT / "Results/control_platform/p2_linear_robust_mworks_20260716"
MODEL_DIR = RESULT_DIR / "models/graphical_variants"
RAW_DIR = RESULT_DIR / "raw"
GRAPHICAL_RAW_DIR = RAW_DIR / "graphical_variants"
REFERENCE_RAW_DIR = RAW_DIR / "cfunction_variants"
SCREENSHOT_DIR = RESULT_DIR / "screenshots/graphical_variants"
LOG_DIR = RESULT_DIR / "logs"
DT = 0.01
AXES = ("x", "y", "z")
ALGORITHMS = {
    "lqg": "MoSim_P2_LQG_MIL",
    "feedback_linearization": "MoSim_P2_FEEDBACK_LINEARIZATION_MIL",
    "passivity_based_control": "MoSim_P2_PASSIVITY_BASED_CONTROL_MIL",
    "adaptive_backstepping": "MoSim_P2_ADAPTIVE_BACKSTEPPING_MIL",
}
INPUT = {
    "position": (0.2, -0.1, 0.7),
    "velocity": (-0.3, 0.2, -0.1),
    "reference_position": (1.0, 0.5, 1.2),
    "reference_velocity": (0.1, -0.2, 0.0),
    "reference_acceleration": (0.05, -0.04, 0.02),
}
PARAMS = {
    "position_gain": (1.6, 1.6, 2.2),
    "velocity_gain": (1.8, 1.8, 2.0),
    "observer_position_gain": (0.65, 0.65, 0.70),
    "observer_velocity_gain": (0.45, 0.45, 0.50),
    "backstepping_k1": (1.1, 1.1, 1.3),
    "backstepping_k2": (1.8, 1.8, 2.0),
    "adaptive_gain": (0.35, 0.35, 0.45),
    "adaptive_limit": (1.0, 1.0, 1.2),
    "mass_kg": 1.0,
    "gravity_mps2": 9.80665,
}
OUTPUTS = [
    *(f"desired_acceleration_{axis}" for axis in AXES),
    *(f"estimated_position_{axis}" for axis in AXES),
    *(f"estimated_velocity_{axis}" for axis in AXES),
    *(f"adaptive_disturbance_{axis}" for axis in AXES),
    "storage_function",
]


def add(model: str, type_name: str, name: str, x: float, y: float) -> None:
    if not ModelingPy.AddComponent(type_name, model, name, x, y, 28, 22):
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
    connect(model, left, f"{name}.u1")
    connect(model, right, f"{name}.u2")
    return f"{name}.y"


def delay(model: str, name: str, source: str, initial: float, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", name, x, y, initCond=initial)
    connect(model, source, f"{name}.u1")
    return f"{name}.y"


def prepare_model(model: str, description: str) -> None:
    if not ModelingPy.ClassExist(model):
        if not ModelingPy.NewModel(model, "Sysblock", description):
            raise RuntimeError(f"NewModel failed: {model}")
    if not ModelingPy.OpenModel(model, "diagram"):
        raise RuntimeError(f"OpenModel failed: {model}")
    for component in list(ModelingPy.GetComponents(model)):
        if not ModelingPy.RemoveComponent(model, component):
            raise RuntimeError(f"RemoveComponent failed: {model}.{component}")


def common_sources(model: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    rows = ("position", "velocity", "reference_position", "reference_velocity", "reference_acceleration")
    for row_index, row in enumerate(rows):
        result[row] = []
        for axis_index, axis in enumerate(AXES):
            result[row].append(constant(
                model, f"{row}_{axis}", INPUT[row][axis_index], -610 + axis_index * 55, 330 - row_index * 62,
            ))
    return result


def nominal_axis(model: str, sources: dict[str, list[str]], axis_index: int, y: float) -> tuple[str, str, str]:
    axis = AXES[axis_index]
    position_error = sum_ports(model, f"position_error_{axis}", [
        sources["reference_position"][axis_index], sources["position"][axis_index],
    ], "+-", -390, y + 35)
    velocity_error = sum_ports(model, f"velocity_error_{axis}", [
        sources["reference_velocity"][axis_index], sources["velocity"][axis_index],
    ], "+-", -390, y - 35)
    position_term = gain(model, f"position_feedback_{axis}", position_error, PARAMS["position_gain"][axis_index], -305, y + 35)
    velocity_term = gain(model, f"velocity_feedback_{axis}", velocity_error, PARAMS["velocity_gain"][axis_index], -305, y - 35)
    feedback = sum_ports(model, f"feedback_sum_{axis}", [position_term, velocity_term], "++", -220, y)
    acceleration = sum_ports(model, f"acceleration_sum_{axis}", [
        sources["reference_acceleration"][axis_index], feedback,
    ], "++", -135, y)
    if axis == "z":
        gravity = constant(model, "gravity", PARAMS["gravity_mps2"], -220, y + 85)
        acceleration = sum_ports(model, "gravity_compensation", [acceleration, gravity], "++", -50, y)
    return acceleration, position_error, velocity_error


def lqg_axis(model: str, sources: dict[str, list[str]], axis_index: int, y: float) -> dict[str, str]:
    axis = AXES[axis_index]
    # UnitDelay outputs are the current observer state. Their inputs compute the
    # corrected one-step prediction used at the next 10 ms sample.
    position_state_name = f"estimated_position_state_{axis}"
    velocity_state_name = f"estimated_velocity_state_{axis}"
    block(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", position_state_name, -285, y + 70,
          initCond=INPUT["position"][axis_index])
    block(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", velocity_state_name, -285, y - 70,
          initCond=INPUT["velocity"][axis_index])
    position_state = f"{position_state_name}.y"
    velocity_state = f"{velocity_state_name}.y"
    velocity_dt = gain(model, f"velocity_dt_{axis}", velocity_state, DT, -210, y + 105)
    predicted_position = sum_ports(model, f"predicted_position_{axis}", [position_state, velocity_dt], "++", -130, y + 85)
    position_innovation = sum_ports(model, f"position_innovation_{axis}", [
        sources["position"][axis_index], predicted_position,
    ], "+-", -50, y + 110)
    position_correction = gain(model, f"position_correction_{axis}", position_innovation,
                               PARAMS["observer_position_gain"][axis_index], 30, y + 110)
    next_position = sum_ports(model, f"next_position_{axis}", [predicted_position, position_correction], "++", 110, y + 85)
    connect(model, next_position, f"{position_state_name}.u1")

    position_error = sum_ports(model, f"estimated_position_error_{axis}", [
        sources["reference_position"][axis_index], position_state,
    ], "+-", -130, y + 20)
    velocity_error = sum_ports(model, f"estimated_velocity_error_{axis}", [
        sources["reference_velocity"][axis_index], velocity_state,
    ], "+-", -130, y - 20)
    position_feedback = gain(model, f"lqg_position_feedback_{axis}", position_error,
                             PARAMS["position_gain"][axis_index], -45, y + 20)
    velocity_feedback = gain(model, f"lqg_velocity_feedback_{axis}", velocity_error,
                             PARAMS["velocity_gain"][axis_index], -45, y - 20)
    feedback = sum_ports(model, f"lqg_feedback_{axis}", [position_feedback, velocity_feedback], "++", 40, y)
    acceleration_without_gravity = sum_ports(model, f"lqg_acceleration_without_gravity_{axis}", [
        sources["reference_acceleration"][axis_index], feedback,
    ], "++", 125, y)
    command_dt = gain(model, f"command_dt_{axis}", acceleration_without_gravity, DT, -210, y - 110)
    predicted_velocity = sum_ports(model, f"predicted_velocity_{axis}", [velocity_state, command_dt], "++", -130, y - 95)
    velocity_innovation = sum_ports(model, f"velocity_innovation_{axis}", [
        sources["velocity"][axis_index], predicted_velocity,
    ], "+-", -50, y - 115)
    velocity_correction = gain(model, f"velocity_correction_{axis}", velocity_innovation,
                               PARAMS["observer_velocity_gain"][axis_index], 30, y - 115)
    next_velocity = sum_ports(model, f"next_velocity_{axis}", [predicted_velocity, velocity_correction], "++", 110, y - 95)
    connect(model, next_velocity, f"{velocity_state_name}.u1")
    acceleration = acceleration_without_gravity
    if axis == "z":
        gravity = constant(model, "gravity", PARAMS["gravity_mps2"], 125, y + 55)
        acceleration = sum_ports(model, "lqg_gravity_compensation", [acceleration_without_gravity, gravity], "++", 210, y)
    return {"acceleration": acceleration, "estimated_position": position_state, "estimated_velocity": velocity_state}


def adaptive_axis(model: str, sources: dict[str, list[str]], axis_index: int, y: float) -> tuple[str, str]:
    axis = AXES[axis_index]
    position_error = sum_ports(model, f"position_error_{axis}", [
        sources["reference_position"][axis_index], sources["position"][axis_index],
    ], "+-", -390, y + 45)
    velocity_error = sum_ports(model, f"velocity_error_{axis}", [
        sources["reference_velocity"][axis_index], sources["velocity"][axis_index],
    ], "+-", -390, y - 45)
    k1_position = gain(model, f"k1_position_{axis}", position_error,
                       PARAMS["backstepping_k1"][axis_index], -305, y + 45)
    sliding = sum_ports(model, f"sliding_surface_{axis}", [velocity_error, k1_position], "++", -220, y)
    adaptive_increment = gain(model, f"adaptive_increment_{axis}", sliding,
                              PARAMS["adaptive_gain"][axis_index] * DT, -135, y + 70)
    adaptive_state_name = f"adaptive_state_{axis}"
    block(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", adaptive_state_name, -135, y + 115, initCond=0.0)
    adaptive_pre = sum_ports(model, f"adaptive_pre_{axis}", [
        f"{adaptive_state_name}.y", adaptive_increment,
    ], "++", -50, y + 90)
    adaptive_limit = PARAMS["adaptive_limit"][axis_index]
    block(model, "SysplorerEmbeddedCoder.Discontinuities.Saturation", f"adaptive_limit_{axis}", 35, y + 90,
          upLimit=adaptive_limit, lowLimit=-adaptive_limit)
    connect(model, adaptive_pre, f"adaptive_limit_{axis}.u")
    adaptive = f"adaptive_limit_{axis}.y"
    connect(model, adaptive, f"{adaptive_state_name}.u1")
    velocity_term = gain(model, f"backstepping_velocity_{axis}", velocity_error,
                         PARAMS["backstepping_k1"][axis_index], -50, y - 35)
    sliding_term = gain(model, f"backstepping_sliding_{axis}", sliding,
                        PARAMS["backstepping_k2"][axis_index], 35, y - 35)
    nominal_feedback = sum_ports(model, f"backstepping_nominal_feedback_{axis}", [
        velocity_term, sliding_term,
    ], "++", 120, y - 35)
    feedback = sum_ports(model, f"backstepping_feedback_{axis}", [
        nominal_feedback, adaptive,
    ], "+-", 120, y + 15)
    acceleration = sum_ports(model, f"acceleration_sum_{axis}", [
        sources["reference_acceleration"][axis_index], feedback,
    ], "++", 205, y)
    if axis == "z":
        gravity = constant(model, "gravity", PARAMS["gravity_mps2"], 120, y + 160)
        acceleration = sum_ports(model, "gravity_compensation", [acceleration, gravity], "++", 290, y)
    return acceleration, adaptive


def storage_axis(model: str, axis: str, axis_index: int, position_error: str, velocity_error: str, y: float) -> str:
    velocity_square = product(model, f"velocity_error_square_{axis}", velocity_error, velocity_error, 15, y - 55)
    position_square = product(model, f"position_error_square_{axis}", position_error, position_error, 15, y + 55)
    kinetic = gain(model, f"kinetic_storage_{axis}", velocity_square, 0.5 * PARAMS["mass_kg"], 95, y - 55)
    potential = gain(model, f"potential_storage_{axis}", position_square,
                     0.5 * PARAMS["position_gain"][axis_index], 95, y + 55)
    return sum_ports(model, f"storage_axis_{axis}", [kinetic, potential], "++", 175, y)


def write_csv(path: Path, times: list[float], columns: list[list[float]]) -> None:
    if not times or len({len(times), *(len(column) for column in columns)}) != 1:
        raise RuntimeError(f"inconsistent result lengths: {path}")
    if not all(math.isfinite(float(value)) for column in columns for value in column):
        raise RuntimeError(f"NaN/Inf in result: {path}")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["time", *OUTPUTS])
        writer.writerows(zip(times, *columns))


def capture_cfunction_reference(algorithm_id: str, fixture: str) -> Path:
    if not ModelingPy.ClassExist(fixture):
        raise RuntimeError(f"CFunction fixture is not loaded: {fixture}")
    if not ModelingPy.SimulateModelEx(fixture, {"stopTime": 0.2, "interval": DT}):
        raise RuntimeError(f"CFunction simulation failed: {fixture}")
    path = REFERENCE_RAW_DIR / f"{algorithm_id}.csv"
    write_csv(path, list(ModelingPy.GetVarTimes()), [list(v) for v in ModelingPy.GetVarsValues(OUTPUTS)])
    return path


def build_variant(algorithm_id: str) -> dict[str, object]:
    model = f"MoSim_P2_{algorithm_id.upper()}_GRAPHICAL_MIL"
    prepare_model(model, f"P2 fixed-input graphical controller core for {algorithm_id}")
    sources = common_sources(model)
    zero = constant(model, "zero", 0.0, 430, 340)
    outputs: dict[str, str] = {}
    storage_terms: list[str] = []
    for axis_index, axis in enumerate(AXES):
        y = 230 - axis_index * 230
        if algorithm_id == "lqg":
            axis_outputs = lqg_axis(model, sources, axis_index, y)
            acceleration = axis_outputs["acceleration"]
            outputs[f"estimated_position_{axis}"] = axis_outputs["estimated_position"]
            outputs[f"estimated_velocity_{axis}"] = axis_outputs["estimated_velocity"]
            outputs[f"adaptive_disturbance_{axis}"] = zero
        elif algorithm_id == "adaptive_backstepping":
            acceleration, adaptive = adaptive_axis(model, sources, axis_index, y)
            outputs[f"estimated_position_{axis}"] = zero
            outputs[f"estimated_velocity_{axis}"] = zero
            outputs[f"adaptive_disturbance_{axis}"] = adaptive
        else:
            acceleration, position_error, velocity_error = nominal_axis(model, sources, axis_index, y)
            outputs[f"estimated_position_{axis}"] = zero
            outputs[f"estimated_velocity_{axis}"] = zero
            outputs[f"adaptive_disturbance_{axis}"] = zero
            if algorithm_id == "passivity_based_control":
                storage_terms.append(storage_axis(model, axis, axis_index, position_error, velocity_error, y))
        outputs[f"desired_acceleration_{axis}"] = acceleration
    if storage_terms:
        storage_xy = sum_ports(model, "storage_xy", storage_terms[:2], "++", 270, 120)
        outputs["storage_function"] = sum_ports(model, "storage_total", [storage_xy, storage_terms[2]], "++", 350, 75)
    else:
        outputs["storage_function"] = zero

    for index, output in enumerate(OUTPUTS):
        add(model, "SysplorerEmbeddedCoder.Port.Outport", output, 520, 325 - index * 48)
        connect(model, outputs[output], output)
    for component, description in {
        "position_error_x": "Reference minus measured position",
        "estimated_position_state_x": "LQG observer position state",
        "storage_total": "Passivity storage function",
        "sliding_surface_x": "Adaptive backstepping sliding coordinate",
    }.items():
        if component in list(ModelingPy.GetComponents(model)):
            ModelingPy.SetComponentDescription(model, component, description)

    target = MODEL_DIR / f"{model}.mo"
    saved = ModelingPy.SaveModel(model) if target.exists() else ModelingPy.SaveModelAs(model, str(MODEL_DIR), model)
    checked = ModelingPy.CheckModel(model)
    diagram = SCREENSHOT_DIR / f"{model}.png"
    exported = ModelingPy.ExportDiagram(model, str(diagram), 2600, 1800)
    simulated = ModelingPy.SimulateModelEx(model, {"stopTime": 0.2, "interval": DT})
    raw_path = GRAPHICAL_RAW_DIR / f"{algorithm_id}.csv"
    write_csv(raw_path, list(ModelingPy.GetVarTimes()), [list(v) for v in ModelingPy.GetVarsValues(OUTPUTS)])
    model_text = str(ModelingPy.GetModelText(model))
    component_count = len(list(ModelingPy.GetComponents(model)))
    connection_count = model_text.count("connect(")
    return {
        "model_name": model,
        "model_path": str(target),
        "diagram_path": str(diagram),
        "raw_csv": str(raw_path),
        "saved": bool(saved),
        "check_model": bool(checked),
        "diagram_exported": bool(exported),
        "simulate_model": bool(simulated),
        "sample_count": len(list(ModelingPy.GetVarTimes())),
        "component_count": component_count,
        "connection_count": connection_count,
        "line_annotation_count": model_text.count("annotation(Line"),
        "structure_ok": bool(saved and checked and exported and simulated and component_count >= 35 and connection_count >= 35),
    }


def read_rows(path: Path) -> list[dict[str, float]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return [{key: float(value) for key, value in row.items()} for row in csv.DictReader(stream)]


def compare(reference: Path, graphical: Path, tolerance: float = 1.0e-9) -> dict[str, object]:
    expected = read_rows(reference)
    actual = read_rows(graphical)
    sample_count_ok = len(expected) == len(actual) and len(expected) == 21
    errors = {output: float("inf") for output in OUTPUTS}
    time_error = float("inf")
    if sample_count_ok:
        time_error = max(abs(a["time"] - b["time"]) for a, b in zip(expected, actual))
        errors = {output: max(abs(a[output] - b[output]) for a, b in zip(expected, actual)) for output in OUTPUTS}
    return {
        "sample_count": len(actual),
        "sample_count_ok": sample_count_ok,
        "max_abs_time_error": time_error,
        "max_abs_error": errors,
        "behavior_equivalence_ok": sample_count_ok and time_error <= tolerance and all(v <= tolerance for v in errors.values()),
    }


def main() -> dict[str, object]:
    for folder in (MODEL_DIR, GRAPHICAL_RAW_DIR, REFERENCE_RAW_DIR, SCREENSHOT_DIR, LOG_DIR):
        folder.mkdir(parents=True, exist_ok=True)
    variants: dict[str, object] = {}
    for algorithm_id, fixture in ALGORITHMS.items():
        reference = capture_cfunction_reference(algorithm_id, fixture)
        graphical = build_variant(algorithm_id)
        equivalence = compare(reference, Path(graphical["raw_csv"]))
        variants[algorithm_id] = {**graphical, "reference_csv": str(reference), **equivalence}
    payload = {
        "schema": "mosim.p2_linear_robust_graphical_mil.v1",
        "source_pair": ["MWORKS_CFUNCTION_MIL", "MWORKS_GRAPHICAL_MIL"],
        "sample_time_s": DT,
        "outputs": OUTPUTS,
        "variants": variants,
        "all_structure_ok": all(item["structure_ok"] for item in variants.values()),
        "all_behavior_equivalent": all(item["behavior_equivalence_ok"] for item in variants.values()),
        "claim_boundary": (
            "Real MWORKS graphical controller-core equivalence for 21 fixed-input samples. "
            "Full ATTITUDE_THRUST geometry, generated C/SIL, and Gazebo runtime are separate gates."
        ),
    }
    manifest = LOG_DIR / "p2_linear_robust_graphical_mil.json"
    manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"ok": payload["all_structure_ok"] and payload["all_behavior_equivalent"], "manifest": str(manifest), "variants": variants}


RUN_SCRIPT_RESULT = main()
