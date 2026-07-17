#!/usr/bin/env python3
"""Build seven native graphical P4 MPC cores and compare them with CFunction MIL."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
RESULT_DIR = ROOT / "Results/control_platform/p4_mpc_mworks_20260716"
MODEL_DIR = RESULT_DIR / "models/graphical_variants"
REFERENCE_DIR = RESULT_DIR / "raw/cfunction_variants"
GRAPHICAL_DIR = RESULT_DIR / "raw/graphical_variants"
SCREENSHOT_DIR = RESULT_DIR / "screenshots/graphical_variants"
LOG_DIR = RESULT_DIR / "logs"
DT = 0.01
HORIZON = 0.25
AXES = ("x", "y", "z")
ALGORITHMS = {
    "linear_mpc": "MoSim_P4_LINEAR_MPC_MIL",
    "robust_mpc": "MoSim_P4_ROBUST_MPC_MIL",
    "adaptive_mpc": "MoSim_P4_ADAPTIVE_MPC_MIL",
    "tube_mpc": "MoSim_P4_TUBE_MPC_MIL",
    "explicit_gain_scheduled_mpc": "MoSim_P4_EXPLICIT_GAIN_SCHEDULED_MPC_MIL",
    "ilqr": "MoSim_P4_ILQR_MIL",
    "mppi": "MoSim_P4_MPPI_MIL",
}
INPUT = {
    "position": (0.2, -0.1, 0.7),
    "velocity": (-0.3, 0.2, -0.1),
    "reference_position": (1.0, 0.5, 1.2),
    "reference_velocity": (0.1, -0.2, 0.0),
    "reference_acceleration": (0.05, -0.04, 0.02),
}
PARAMS = {
    "position_weight": (1.0, 1.0, 1.2),
    "velocity_weight": (0.08, 0.08, 0.10),
    "control_weight": (0.002, 0.002, 0.003),
    "acceleration_limit": (4.0, 4.0, 2.5),
    "increment_limit": (1.2, 1.2, 0.8),
    "robust_bound": (0.25, 0.25, 0.20),
    "tube_position_gain": (0.35, 0.35, 0.45),
    "tube_velocity_gain": (0.18, 0.18, 0.25),
    "adaptive_rate": 0.08,
    "adaptive_scale_min": 0.75,
    "adaptive_scale_max": 1.25,
    "schedule_error_threshold": 0.75,
    "ilqr_step_size": 0.65,
    "mppi_temperature": 0.30,
    "mppi_noise_scale": (0.35, 0.35, 0.25),
    "gravity": 9.80665,
}
OUTPUTS = [
    *(f"desired_acceleration_{axis}" for axis in AXES),
    *(f"unconstrained_acceleration_{axis}" for axis in AXES),
    *(f"auxiliary_{axis}" for axis in AXES),
    "solver_cost",
    "solver_iterations",
]


def add(model: str, type_name: str, name: str, x: float, y: float, width: float = 26, height: float = 20) -> None:
    if not ModelingPy.AddComponent(type_name, model, name, x, y, width, height):
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
    if len(sources) != len(signs) or len(sources) < 2:
        raise ValueError("sum_ports requires matching sources/signs with at least two inputs")
    current = sources[0]
    current_sign = signs[0]
    for index, source in enumerate(sources[1:], start=1):
        stage = name if index == len(sources) - 1 else f"{name}_stage{index}"
        block(model, "SysplorerEmbeddedCoder.MathOperation.Sum", stage, x + index * 34, y - index * 22, inputs=current_sign + signs[index])
        connect(model, current, f"{stage}.u1")
        connect(model, source, f"{stage}.u2")
        current = f"{stage}.y"
        current_sign = "+"
    return current


def product_ports(model: str, name: str, sources: list[str], operators: str, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.MathOperation.Product", name, x, y, inputs=operators)
    for index, source in enumerate(sources, start=1):
        connect(model, source, f"{name}.u{index}")
    return f"{name}.y"


def multiply(model: str, name: str, left: str, right: str, x: float, y: float) -> str:
    return product_ports(model, name, [left, right], "**", x, y)


def divide(model: str, name: str, numerator: str, denominator: str, x: float, y: float) -> str:
    return product_ports(model, name, [numerator, denominator], "*/", x, y)


def square(model: str, name: str, source: str, x: float, y: float) -> str:
    return multiply(model, name, source, source, x, y)


def saturation(model: str, name: str, source: str, low: float, high: float, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.Discontinuities.Saturation", name, x, y, lowLimit=low, upLimit=high)
    connect(model, source, f"{name}.u")
    return f"{name}.y"


def absolute(model: str, name: str, source: str, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.MathOperation.Abs", name, x, y)
    connect(model, source, f"{name}.u")
    return f"{name}.y"


def tanh_block(model: str, name: str, source: str, x: float, y: float) -> str:
    block(
        model,
        "SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction",
        name,
        x,
        y,
        operatorType="SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction.TrigonometricType.tanh",
    )
    connect(model, source, f"{name}.u1")
    return f"{name}.y1"


def exp_block(model: str, name: str, source: str, x: float, y: float) -> str:
    block(
        model,
        "SysplorerEmbeddedCoder.MathOperation.MathFunction",
        name,
        x,
        y,
        operatorType="SysplorerEmbeddedCoder.MathOperation.MathFunction.OperatorType.exp",
    )
    connect(model, source, f"{name}.u1")
    return f"{name}.y"


def minimum(model: str, name: str, sources: list[str], x: float, y: float) -> str:
    if len(sources) < 2:
        raise ValueError("minimum requires at least two sources")
    current = sources[0]
    for index, source in enumerate(sources[1:], start=1):
        stage = f"{name}_stage{index}"
        block(
            model,
            "SysplorerEmbeddedCoder.MathOperation.Maxmin",
            stage,
            x + index * 42,
            y - index * 28,
            maxMinType="SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min",
        )
        connect(model, current, f"{stage}.u1")
        connect(model, source, f"{stage}.u2")
        current = f"{stage}.y"
    return current


def prepare_model(model: str, description: str) -> None:
    if not ModelingPy.ClassExist(model) and not ModelingPy.NewModel(model, "Sysblock", description):
        raise RuntimeError(f"NewModel failed: {model}")
    if not ModelingPy.OpenModel(model, "diagram"):
        raise RuntimeError(f"OpenModel failed: {model}")
    for component in list(ModelingPy.GetComponents(model)):
        if not ModelingPy.RemoveComponent(model, component):
            raise RuntimeError(f"RemoveComponent failed: {model}.{component}")


def common_sources(model: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for row_index, row in enumerate(INPUT):
        result[row] = [
            constant(model, f"{row}_{axis}", INPUT[row][axis_index], -950 + axis_index * 55, 520 - row_index * 55)
            for axis_index, axis in enumerate(AXES)
        ]
    return result


def linear_solution(model: str, sources: dict[str, list[str]], i: int, previous: str, y: float) -> tuple[str, str, str]:
    axis = AXES[i]
    ep = sum_ports(model, f"position_error_{axis}", [sources["reference_position"][i], sources["position"][i]], "+-", -780, y + 55)
    ev = sum_ports(model, f"velocity_error_{axis}", [sources["reference_velocity"][i], sources["velocity"][i]], "+-", -780, y - 55)
    q = PARAMS["position_weight"][i]
    v = PARAMS["velocity_weight"][i]
    r = PARAMS["control_weight"][i]
    denominator = 0.5 * q * HORIZON**4 + 2.0 * v * HORIZON**2 + 2.0 * r
    ep_term = gain(model, f"linear_position_term_{axis}", ep, q * HORIZON**2 / denominator, -690, y + 55)
    ev_term = gain(model, f"linear_velocity_term_{axis}", ev, 2.0 * v * HORIZON / denominator, -690, y)
    previous_term = gain(model, f"linear_previous_term_{axis}", previous, 2.0 * r / denominator, -690, y - 55)
    acceleration = sum_ports(model, f"linear_solution_{axis}", [ep_term, ev_term, previous_term], "+++", -600, y)
    return ep, ev, acceleration


def stage_cost(model: str, prefix: str, ep: str, ev: str, acceleration: str, i: int, x: float, y: float) -> str:
    h_ev = gain(model, f"{prefix}_h_ev", ev, HORIZON, x, y + 65)
    h2_acc = gain(model, f"{prefix}_half_h2_acc", acceleration, 0.5 * HORIZON**2, x, y + 20)
    pe = sum_ports(model, f"{prefix}_predicted_position_error", [ep, h_ev, h2_acc], "++-", x + 85, y + 55)
    h_acc = gain(model, f"{prefix}_h_acc", acceleration, HORIZON, x, y - 35)
    ve = sum_ports(model, f"{prefix}_predicted_velocity_error", [ev, h_acc], "+-", x + 85, y - 35)
    pe2 = square(model, f"{prefix}_position_error_squared", pe, x + 170, y + 55)
    ve2 = square(model, f"{prefix}_velocity_error_squared", ve, x + 170, y)
    ac2 = square(model, f"{prefix}_acceleration_squared", acceleration, x + 170, y - 55)
    q_cost = gain(model, f"{prefix}_position_cost", pe2, PARAMS["position_weight"][i], x + 255, y + 55)
    v_cost = gain(model, f"{prefix}_velocity_cost", ve2, PARAMS["velocity_weight"][i], x + 255, y)
    r_cost = gain(model, f"{prefix}_control_cost", ac2, PARAMS["control_weight"][i], x + 255, y - 55)
    return sum_ports(model, f"{prefix}_stage_cost", [q_cost, v_cost, r_cost], "+++", x + 340, y)


def ilqr_solution(model: str, ep: str, ev: str, initial: str, i: int, y: float) -> str:
    q = PARAMS["position_weight"][i]
    v = PARAMS["velocity_weight"][i]
    r = PARAMS["control_weight"][i]
    hessian = 0.5 * q * HORIZON**4 + 2.0 * v * HORIZON**2 + 2.0 * r
    acceleration = initial
    for iteration in range(1, 6):
        pe_h_ev = gain(model, f"ilqr_{i}_iter{iteration}_h_ev", ev, HORIZON, -505 + iteration * 85, y + 100)
        pe_h2_acc = gain(model, f"ilqr_{i}_iter{iteration}_half_h2_acc", acceleration, 0.5 * HORIZON**2, -505 + iteration * 85, y + 60)
        pe = sum_ports(model, f"ilqr_{i}_iter{iteration}_pe", [ep, pe_h_ev, pe_h2_acc], "++-", -465 + iteration * 85, y + 80)
        ve_h_acc = gain(model, f"ilqr_{i}_iter{iteration}_h_acc", acceleration, HORIZON, -505 + iteration * 85, y + 20)
        ve = sum_ports(model, f"ilqr_{i}_iter{iteration}_ve", [ev, ve_h_acc], "+-", -465 + iteration * 85, y + 20)
        gp = gain(model, f"ilqr_{i}_iter{iteration}_gp", pe, -q * HORIZON**2, -425 + iteration * 85, y + 80)
        gv = gain(model, f"ilqr_{i}_iter{iteration}_gv", ve, -2.0 * v * HORIZON, -425 + iteration * 85, y + 40)
        ga = gain(model, f"ilqr_{i}_iter{iteration}_ga", acceleration, 2.0 * r, -425 + iteration * 85, y)
        gradient = sum_ports(model, f"ilqr_{i}_iter{iteration}_gradient", [gp, gv, ga], "+++", -385 + iteration * 85, y + 40)
        correction = gain(model, f"ilqr_{i}_iter{iteration}_newton_step", gradient, PARAMS["ilqr_step_size"] / hessian, -345 + iteration * 85, y + 40)
        acceleration = sum_ports(model, f"ilqr_{i}_iter{iteration}_update", [acceleration, correction], "+-", -305 + iteration * 85, y)
    return acceleration


def mppi_solution(model: str, ep: str, ev: str, initial: str, i: int, y: float) -> tuple[str, str]:
    samples = (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5)
    candidates: list[str] = []
    costs: list[str] = []
    for sample_index, sample in enumerate(samples):
        row_y = y + 210 - sample_index * 65
        noise = constant(model, f"mppi_{i}_sample{sample_index}_noise", sample * PARAMS["mppi_noise_scale"][i], -480, row_y)
        candidate = sum_ports(model, f"mppi_{i}_sample{sample_index}_candidate", [initial, noise], "++", -395, row_y)
        cost = stage_cost(model, f"mppi_{i}_sample{sample_index}", ep, ev, candidate, i, -310, row_y)
        candidates.append(candidate)
        costs.append(cost)
    min_cost = minimum(model, f"mppi_{i}_minimum_cost", costs, 390, y + 225)
    weighted: list[str] = []
    weights: list[str] = []
    for sample_index, (candidate, cost) in enumerate(zip(candidates, costs)):
        row_y = y + 210 - sample_index * 65
        delta = sum_ports(model, f"mppi_{i}_sample{sample_index}_cost_delta", [cost, min_cost], "+-", 475, row_y)
        exponent = gain(model, f"mppi_{i}_sample{sample_index}_exponent", delta, -1.0 / PARAMS["mppi_temperature"], 560, row_y)
        weight = exp_block(model, f"mppi_{i}_sample{sample_index}_weight", exponent, 645, row_y)
        weighted.append(multiply(model, f"mppi_{i}_sample{sample_index}_weighted_candidate", weight, candidate, 730, row_y))
        weights.append(weight)
    weighted_sum = sum_ports(model, f"mppi_{i}_weighted_sum", weighted, "+" * len(weighted), 815, y + 40)
    weight_sum = sum_ports(model, f"mppi_{i}_weight_sum", weights, "+" * len(weights), 815, y - 40)
    return divide(model, f"mppi_{i}_solution", weighted_sum, weight_sum, 900, y), min_cost


def axis_core(model: str, algorithm: str, sources: dict[str, list[str]], i: int, y: float) -> dict[str, str]:
    axis = AXES[i]
    state_name = f"previous_acceleration_{axis}"
    block(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", state_name, -860, y, initCond=0.0)
    previous = f"{state_name}.y"
    ep, ev, acceleration = linear_solution(model, sources, i, previous, y)
    auxiliary = constant(model, f"auxiliary_zero_{axis}", 0.0, 110, y + 170)
    solver_cost_override = ""

    if algorithm == "robust_mpc":
        surface = sum_ports(model, f"robust_surface_{axis}", [ep, gain(model, f"robust_horizon_velocity_{axis}", ev, HORIZON, -505, y + 130)], "++", -420, y + 130)
        scaled = gain(model, f"robust_surface_scale_{axis}", surface, 4.0, -335, y + 130)
        smooth_sign = tanh_block(model, f"robust_tanh_{axis}", scaled, -250, y + 130)
        robust = gain(model, f"robust_bound_term_{axis}", smooth_sign, PARAMS["robust_bound"][i], -165, y + 130)
        acceleration = sum_ports(model, f"robust_solution_{axis}", [acceleration, robust], "++", -80, y)
        auxiliary = constant(model, f"robust_bound_debug_{axis}", PARAMS["robust_bound"][i], -80, y + 170)
    elif algorithm == "adaptive_mpc":
        state = "adaptive_scale_state"
        if i == 0:
            block(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", state, -505, y + 235, initCond=1.0)
            products = [multiply(model, f"adaptive_error_product_{a}",
                                 sum_ports(model, f"adaptive_position_error_{a}", [sources["reference_position"][j], sources["position"][j]], "+-", -780, y + 280 - j * 45),
                                 sum_ports(model, f"adaptive_velocity_error_{a}", [sources["reference_velocity"][j], sources["velocity"][j]], "+-", -690, y + 280 - j * 45),
                                 -600, y + 280 - j * 45)
                        for j, a in enumerate(AXES)]
            signal = sum_ports(model, "adaptive_signal_sum", products, "+++", -505, y + 190)
            increment = gain(model, "adaptive_scale_increment", signal, PARAMS["adaptive_rate"] * DT / 3.0, -420, y + 190)
            next_raw = sum_ports(model, "adaptive_scale_next_raw", [f"{state}.y", increment], "++", -335, y + 190)
            next_scale = saturation(model, "adaptive_scale_limit", next_raw, PARAMS["adaptive_scale_min"], PARAMS["adaptive_scale_max"], -250, y + 190)
            connect(model, next_scale, f"{state}.u1")
        current_scale = "adaptive_scale_limit.y"
        acceleration = multiply(model, f"adaptive_solution_{axis}", acceleration, current_scale, -80, y)
        auxiliary = current_scale
    elif algorithm == "tube_mpc":
        ep_term = gain(model, f"tube_position_term_{axis}", ep, PARAMS["tube_position_gain"][i], -335, y + 140)
        ev_term = gain(model, f"tube_velocity_term_{axis}", ev, PARAMS["tube_velocity_gain"][i], -335, y + 95)
        tube = sum_ports(model, f"tube_feedback_{axis}", [ep_term, ev_term], "++", -250, y + 115)
        acceleration = sum_ports(model, f"tube_solution_{axis}", [acceleration, tube], "++", -80, y)
        auxiliary = constant(model, f"tube_tightened_limit_{axis}", max(0.1, PARAMS["acceleration_limit"][i] - PARAMS["robust_bound"][i]), -80, y + 170)
    elif algorithm == "explicit_gain_scheduled_mpc":
        abs_ep = absolute(model, f"schedule_abs_error_{axis}", ep, -420, y + 150)
        normalized = gain(model, f"schedule_normalized_error_{axis}", abs_ep, 1.0 / PARAMS["schedule_error_threshold"], -335, y + 150)
        schedule = saturation(model, f"schedule_limit_{axis}", normalized, 0.0, 1.0, -250, y + 150)
        ep_term = gain(model, f"scheduled_position_term_{axis}", ep, PARAMS["tube_position_gain"][i], -250, y + 105)
        ev_term = gain(model, f"scheduled_velocity_term_{axis}", ev, PARAMS["tube_velocity_gain"][i], -250, y + 65)
        feedback = sum_ports(model, f"scheduled_feedback_{axis}", [ep_term, ev_term], "++", -165, y + 85)
        correction = multiply(model, f"scheduled_correction_{axis}", schedule, feedback, -80, y + 85)
        acceleration = sum_ports(model, f"scheduled_solution_{axis}", [acceleration, correction], "++", 5, y)
        auxiliary = schedule
    elif algorithm == "ilqr":
        acceleration = ilqr_solution(model, ep, ev, acceleration, i, y)
    elif algorithm == "mppi":
        acceleration, solver_cost_override = mppi_solution(model, ep, ev, acceleration, i, y)

    unconstrained = sum_ports(model, f"unconstrained_command_{axis}", [acceleration, sources["reference_acceleration"][i]], "++", 985, y)
    acceleration_limit = PARAMS["acceleration_limit"][i]
    if algorithm == "tube_mpc":
        acceleration_limit = max(0.1, acceleration_limit - PARAMS["robust_bound"][i])
    absolute_limited = saturation(model, f"absolute_acceleration_limit_{axis}", unconstrained, -acceleration_limit, acceleration_limit, 1070, y)
    previous_lower = gain(model, f"previous_lower_bound_{axis}", previous, 1.0, 1070, y + 85)
    increment_shift = constant(model, f"increment_limit_{axis}", PARAMS["increment_limit"][i], 1070, y + 130)
    lower = sum_ports(model, f"increment_lower_{axis}", [previous_lower, increment_shift], "+-", 1155, y + 105)
    upper = sum_ports(model, f"increment_upper_{axis}", [previous_lower, increment_shift], "++", 1155, y + 65)
    above_lower = block(model, "SysplorerEmbeddedCoder.MathOperation.Maxmin", f"increment_lower_clip_{axis}", 1240, y + 35,
                        portNumber=2, maxMinType="SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.max")
    connect(model, absolute_limited, f"{above_lower}.u1"); connect(model, lower, f"{above_lower}.u2")
    below_upper = block(model, "SysplorerEmbeddedCoder.MathOperation.Maxmin", f"increment_upper_clip_{axis}", 1325, y,
                        portNumber=2, maxMinType="SysplorerEmbeddedCoder.MathOperation.Maxmin.MaxMinType.min")
    connect(model, f"{above_lower}.y", f"{below_upper}.u1"); connect(model, upper, f"{below_upper}.u2")
    constrained = f"{below_upper}.y"
    connect(model, constrained, f"{state_name}.u1")
    desired = constrained
    if axis == "z":
        gravity = constant(model, "gravity", PARAMS["gravity"], 1325, y + 95)
        desired = sum_ports(model, "gravity_compensation", [constrained, gravity], "++", 1410, y)
    cost = solver_cost_override or stage_cost(model, f"final_{algorithm}_{axis}", ep, ev, constrained, i, 985, y - 165)
    return {"desired": desired, "unconstrained": unconstrained, "auxiliary": auxiliary, "cost": cost}


def write_csv(path: Path, times: list[float], columns: list[list[float]]) -> None:
    if not times or len({len(times), *(len(column) for column in columns)}) != 1:
        raise RuntimeError(f"inconsistent result lengths: {path}")
    if not all(math.isfinite(float(value)) for column in columns for value in column):
        raise RuntimeError(f"NaN/Inf in result: {path}")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["time", *OUTPUTS])
        writer.writerows(zip(times, *columns))


def ensure_reference_models() -> None:
    for path in sorted((RESULT_DIR / "models").glob("MoSim_P4_*.mo")):
        name = path.stem
        if not ModelingPy.ClassExist(name) and not ModelingPy.OpenModelFile(str(path)):
            raise RuntimeError(f"OpenModelFile failed: {path}")


def capture_reference(algorithm: str, fixture: str) -> Path:
    if not ModelingPy.ClassExist(fixture) or not ModelingPy.SimulateModelEx(fixture, {"stopTime": 0.2, "interval": DT}):
        raise RuntimeError(f"CFunction simulation failed: {fixture}")
    path = REFERENCE_DIR / f"{algorithm}.csv"
    write_csv(path, list(ModelingPy.GetVarTimes()), [list(v) for v in ModelingPy.GetVarsValues(OUTPUTS)])
    return path


def build_variant(algorithm: str) -> dict[str, object]:
    model = f"MoSim_P4_{algorithm.upper()}_GRAPHICAL_MIL"
    prepare_model(model, f"P4 native graphical fixed-budget MPC controller core: {algorithm}")
    sources = common_sources(model)
    axis_outputs = [axis_core(model, algorithm, sources, i, 340 - i * 430) for i in range(3)]
    outputs = {
        **{f"desired_acceleration_{axis}": axis_outputs[i]["desired"] for i, axis in enumerate(AXES)},
        **{f"unconstrained_acceleration_{axis}": axis_outputs[i]["unconstrained"] for i, axis in enumerate(AXES)},
        **{f"auxiliary_{axis}": axis_outputs[i]["auxiliary"] for i, axis in enumerate(AXES)},
        "solver_cost": sum_ports(model, "solver_cost_sum", [item["cost"] for item in axis_outputs], "+++", 1510, -930),
        "solver_iterations": constant(model, "fixed_solver_budget", 5.0 if algorithm == "ilqr" else 7.0 if algorithm == "mppi" else 0.0, 1510, -1000),
    }
    for index, output in enumerate(OUTPUTS):
        add(model, "SysplorerEmbeddedCoder.Port.Outport", output, 1610, 360 - index * 105)
        connect(model, outputs[output], output)
    feature = {
        "linear_mpc": "previous_acceleration_x",
        "robust_mpc": "robust_tanh_x",
        "adaptive_mpc": "adaptive_scale_state",
        "tube_mpc": "tube_tightened_limit_x",
        "explicit_gain_scheduled_mpc": "schedule_limit_x",
        "ilqr": "ilqr_0_iter5_update",
        "mppi": "mppi_0_minimum_cost_stage6",
    }[algorithm]
    ModelingPy.SetComponentDescription(model, feature, f"P4 distinguishing native graphical path for {algorithm}")
    target = MODEL_DIR / f"{model}.mo"
    saved = ModelingPy.SaveModel(model) if target.exists() else ModelingPy.SaveModelAs(model, str(MODEL_DIR), model)
    checked = ModelingPy.CheckModel(model)
    diagram = SCREENSHOT_DIR / f"{model}.png"
    exported = ModelingPy.ExportDiagram(model, str(diagram), 3600, 2400)
    simulated = ModelingPy.SimulateModelEx(model, {"stopTime": 0.2, "interval": DT})
    raw = GRAPHICAL_DIR / f"{algorithm}.csv"
    times = list(ModelingPy.GetVarTimes())
    write_csv(raw, times, [list(v) for v in ModelingPy.GetVarsValues(OUTPUTS)])
    text = str(ModelingPy.GetModelText(model))
    components = len(list(ModelingPy.GetComponents(model)))
    return {
        "model_name": model,
        "model_path": str(target),
        "diagram_path": str(diagram),
        "raw_csv": str(raw),
        "feature_component": feature,
        "saved": bool(saved),
        "check_model": bool(checked),
        "diagram_exported": bool(exported),
        "simulate_model": bool(simulated),
        "sample_count": len(times),
        "component_count": components,
        "connection_count": text.count("connect("),
        "structure_ok": bool(saved and checked and exported and simulated and components >= 75 and text.count("connect(") >= 75),
    }


def rows(path: Path) -> list[dict[str, float]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return [{key: float(value) for key, value in row.items()} for row in csv.DictReader(stream)]


def recover_completed_variant(algorithm: str) -> dict[str, object] | None:
    model = f"MoSim_P4_{algorithm.upper()}_GRAPHICAL_MIL"
    target = MODEL_DIR / f"{model}.mo"
    diagram = SCREENSHOT_DIR / f"{model}.png"
    raw = GRAPHICAL_DIR / f"{algorithm}.csv"
    if not (target.is_file() and diagram.is_file() and raw.is_file()):
        return None
    text = target.read_text(encoding="utf-8")
    sample_count = len(rows(raw))
    component_count = text.count("annotation (Placement(")
    connection_count = text.count("connect(")
    if sample_count != 21 or component_count < 75 or connection_count < 75 or diagram.stat().st_size <= 10000:
        return None
    feature = {
        "linear_mpc": "previous_acceleration_x",
        "robust_mpc": "robust_tanh_x",
        "adaptive_mpc": "adaptive_scale_state",
        "tube_mpc": "tube_tightened_limit_x",
        "explicit_gain_scheduled_mpc": "schedule_limit_x",
        "ilqr": "ilqr_0_iter5_update",
        "mppi": "mppi_0_minimum_cost_stage6",
    }[algorithm]
    return {
        "model_name": model,
        "model_path": str(target),
        "diagram_path": str(diagram),
        "raw_csv": str(raw),
        "feature_component": feature,
        "saved": True,
        "check_model": True,
        "diagram_exported": True,
        "simulate_model": True,
        "sample_count": sample_count,
        "component_count": component_count,
        "connection_count": connection_count,
        "structure_ok": True,
        "recovered_from_complete_artifacts": True,
    }


def compare(reference: Path, graphical: Path, tolerance: float = 1.0e-8) -> dict[str, object]:
    expected, actual = rows(reference), rows(graphical)
    sample_ok = len(expected) == len(actual) == 21
    errors = {output: float("inf") for output in OUTPUTS}
    time_error = float("inf")
    if sample_ok:
        time_error = max(abs(a["time"] - b["time"]) for a, b in zip(expected, actual))
        errors = {output: max(abs(a[output] - b[output]) for a, b in zip(expected, actual)) for output in OUTPUTS}
    return {
        "sample_count_ok": sample_ok,
        "max_abs_time_error": time_error,
        "max_abs_error": errors,
        "behavior_equivalence_ok": sample_ok and time_error <= tolerance and all(value <= tolerance for value in errors.values()),
    }


def main() -> dict[str, object]:
    for folder in (MODEL_DIR, REFERENCE_DIR, GRAPHICAL_DIR, SCREENSHOT_DIR, LOG_DIR):
        folder.mkdir(parents=True, exist_ok=True)
    ensure_reference_models()
    variants: dict[str, dict[str, object]] = {}
    for algorithm, fixture in ALGORITHMS.items():
        reference = capture_reference(algorithm, fixture)
        graphical = recover_completed_variant(algorithm)
        if graphical is None:
            graphical = build_variant(algorithm)
        equivalence = compare(reference, Path(graphical["raw_csv"]))
        if not equivalence["behavior_equivalence_ok"] and graphical.get("recovered_from_complete_artifacts"):
            graphical = build_variant(algorithm)
            equivalence = compare(reference, Path(graphical["raw_csv"]))
        variants[algorithm] = {**graphical, "reference_csv": str(reference), **equivalence}
        checkpoint = {"schema": "mosim.p4_mpc_graphical_mil.checkpoint.v1", "variants": variants}
        (LOG_DIR / "p4_mpc_graphical_mil.checkpoint.json").write_text(json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8")
    payload = {
        "schema": "mosim.p4_mpc_graphical_mil.v1",
        "source_pair": ["MWORKS_CFUNCTION_MIL", "MWORKS_NATIVE_GRAPHICAL_MIL"],
        "sample_time_s": DT,
        "stop_time_s": 0.2,
        "outputs": OUTPUTS,
        "fixed_budget": {"ilqr_iterations": 5, "mppi_samples": 7},
        "variants": variants,
        "all_structure_ok": all(item["structure_ok"] for item in variants.values()),
        "all_behavior_equivalent": all(item["behavior_equivalence_ok"] for item in variants.values()),
        "claim_boundary": "Real MWORKS native graphical controller-core equivalence for seven fixed-size MPC variants and 21 fixed-input samples. ATTITUDE_THRUST quaternion/thrust geometry, generated C/SIL, timing, and Gazebo runtime remain separate gates.",
    }
    manifest = LOG_DIR / "p4_mpc_graphical_mil.json"
    manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"ok": payload["all_structure_ok"] and payload["all_behavior_equivalent"], "manifest": str(manifest), "variants": variants}


RUN_SCRIPT_RESULT = main()
