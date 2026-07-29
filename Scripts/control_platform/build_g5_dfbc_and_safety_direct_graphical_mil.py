#!/usr/bin/env python3
"""Build G5-readable DFBC and QP/NMPC safety graphical controller cores.

The source models are created only through the official Sysplorer ModelingPy
API. They make the actual control-law stages visible for G5 review; they are
not whole-aircraft harnesses, numerical-equivalence results, generated code,
or runtime claims. Historical CFunction and equation-shell implementations
remain intact as compatibility and formula-provenance artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import mworks.sysplorer as ModelingPy


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = (
    ROOT
    / "Results"
    / "control_platform"
    / "g5_graphical_structure_review_20260722"
    / "direct_graphical_sources"
)
DFBC_SOURCE_DIR = SOURCE_ROOT / "dfbc"
FIXED_CHAIN_SOURCE_DIR = SOURCE_ROOT / "fixed_chain"
MANIFEST_PATH = SOURCE_ROOT / "DFBC_AND_QPNMPC_DIRECT_GRAPHICAL_BUILD.json"
DT = 0.01
AXES = ("x", "y", "z")

DFBC_VARIANTS = {
    "dfbc_high_order_attitude": {
        "model": "MoSim_G5_DFBC_HIGH_ORDER_ATTITUDE_DIRECT_GRAPHICAL_MIL",
        "description": "Direct graphical high-order DFBC with attitude/thrust adapter",
        "law": "Position/velocity error surface, discrete surface-rate feedback, and attitude/thrust allocation.",
        "variant": "high_order",
        "output_mode": "attitude",
    },
    "dfbc_high_order_bodyrate": {
        "model": "MoSim_G5_DFBC_HIGH_ORDER_BODYRATE_DIRECT_GRAPHICAL_MIL",
        "description": "Direct graphical high-order DFBC with body-rate/thrust adapter",
        "law": "Position/velocity error surface, discrete surface-rate feedback, and body-rate/thrust allocation.",
        "variant": "high_order",
        "output_mode": "bodyrate",
    },
    "dfbc_smooth_robust_attitude": {
        "model": "MoSim_G5_DFBC_SMOOTH_ROBUST_ATTITUDE_DIRECT_GRAPHICAL_MIL",
        "description": "Direct graphical smooth-robust DFBC with attitude/thrust adapter",
        "law": "Smooth tanh robust feedback with bounded discrete disturbance observer and attitude/thrust allocation.",
        "variant": "smooth_robust",
        "output_mode": "attitude",
    },
    "dfbc_smooth_robust_bodyrate": {
        "model": "MoSim_G5_DFBC_SMOOTH_ROBUST_BODYRATE_DIRECT_GRAPHICAL_MIL",
        "description": "Direct graphical smooth-robust DFBC with body-rate/thrust adapter",
        "law": "Smooth tanh robust feedback with bounded discrete disturbance observer and body-rate/thrust allocation.",
        "variant": "smooth_robust",
        "output_mode": "bodyrate",
    },
}

QP_NMPC_VARIANT = {
    "model": "MoSim_G5_QPNMPC_SAFETY_DIRECT_GRAPHICAL_MIL",
    "description": "Direct graphical QP/NMPC safety projection core",
    "law": "NMPC tilt softening, two QP projection stages, output limits, and a safety event branch.",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def add(model: str, type_name: str, name: str, x: float, y: float, width: float = 28, height: float = 22) -> None:
    if not ModelingPy.AddComponent(type_name, model, name, x, y, width, height):
        raise RuntimeError(f"AddComponent failed: {model}.{name} ({type_name})")


def set_param(name: str, parameter: str, value: object) -> None:
    encoded = f'"{value}"' if parameter == "inputs" else str(value)
    if not ModelingPy.SetParamValue(f"{name}.{parameter}", encoded):
        raise RuntimeError(f"SetParamValue failed: {name}.{parameter}={encoded}")


def connect(model: str, source_port: str, target_port: str) -> None:
    if not ModelingPy.ConnectPort(model, source_port, target_port):
        raise RuntimeError(f"ConnectPort failed: {model}: {source_port} -> {target_port}")


def block(model: str, type_name: str, name: str, x: float, y: float, **params: object) -> str:
    add(model, type_name, name, x, y)
    for key, value in params.items():
        set_param(name, key, value)
    return name


def source(model: str, name: str, x: float, y: float) -> str:
    add(model, "SysplorerEmbeddedCoder.Port.Inport", name, x, y)
    return name


def output(model: str, name: str, source_port: str, x: float, y: float) -> None:
    add(model, "SysplorerEmbeddedCoder.Port.Outport", name, x, y)
    connect(model, source_port, name)


def constant(model: str, name: str, value: float, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.Sources.Constant", name, x, y, k=value)
    return f"{name}.y"


def gain(model: str, name: str, source_port: str, value: float, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.MathOperation.Gain", name, x, y, k=value)
    connect(model, source_port, f"{name}.u")
    return f"{name}.y"


def sum_ports(model: str, name: str, ports: list[str], signs: str, x: float, y: float) -> str:
    if len(ports) != len(signs) or len(ports) < 2:
        raise ValueError(f"{name}: matching two-or-more ports/signs are required")
    result = ports[0]
    first_sign = signs[0]
    if first_sign == "-":
        result = gain(model, f"{name}_negate_first", result, -1.0, x - 72, y)
    for index, (port, sign) in enumerate(zip(ports[1:], signs[1:]), start=2):
        stage = name if index == len(ports) else f"{name}_stage_{index}"
        stage_x = x if index == len(ports) else x - (len(ports) - index) * 58
        block(model, "SysplorerEmbeddedCoder.MathOperation.Sum", stage, stage_x, y)
        if sign != "+":
            set_param(stage, "inputs", f"+{sign}")
        connect(model, result, f"{stage}.u1")
        connect(model, port, f"{stage}.u2")
        result = f"{stage}.y"
    return result


def product(model: str, name: str, left: str, right: str, x: float, y: float, *, operators: str = "**") -> str:
    block(model, "SysplorerEmbeddedCoder.MathOperation.Product", name, x, y, inputs=operators)
    connect(model, left, f"{name}.u1")
    connect(model, right, f"{name}.u2")
    return f"{name}.y"


def saturation(model: str, name: str, source_port: str, low: float, high: float, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.Discontinuities.Saturation", name, x, y, lowLimit=low, upLimit=high)
    connect(model, source_port, f"{name}.u")
    return f"{name}.y"


def unit_delay(model: str, name: str, x: float, y: float, initial: float = 0.0) -> str:
    block(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", name, x, y, initCond=initial)
    return f"{name}.y"


def tanh_block(model: str, name: str, source_port: str, x: float, y: float) -> str:
    block(
        model,
        "SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction",
        name,
        x,
        y,
        operatorType="SysplorerEmbeddedCoder.MathOperation.TrigonometricFunction.TrigonometricType.tanh",
    )
    connect(model, source_port, f"{name}.u1")
    return f"{name}.y1"


def absolute(model: str, name: str, source_port: str, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.MathOperation.Abs", name, x, y)
    connect(model, source_port, f"{name}.u")
    return f"{name}.y"


def enable_switch(model: str, name: str, source_port: str, enable_port: str, zero_port: str, x: float, y: float) -> str:
    block(model, "SysplorerEmbeddedCoder.SignalRouting.Switch", name, x, y, threshold=0.5)
    connect(model, source_port, f"{name}.u1")
    connect(model, enable_port, f"{name}.u2")
    connect(model, zero_port, f"{name}.u3")
    return f"{name}.y"


def reset_model(model: str, description: str, target: Path, replace: bool) -> None:
    if target.is_file() and not replace:
        raise RuntimeError(f"Refusing to overwrite existing direct graphical source without --replace: {target}")
    if ModelingPy.ClassExist(model) and not ModelingPy.EraseClasses((model,)):
        raise RuntimeError(f"EraseClasses failed: {model}")
    if not ModelingPy.NewModel(model, "Sysblock", description):
        raise RuntimeError(f"NewModel failed: {model}")
    if not ModelingPy.OpenModel(model, "diagram"):
        raise RuntimeError(f"OpenModel failed: {model}")


def dfbc_inputs(model: str) -> tuple[dict[str, str], str, str, str]:
    ports: dict[str, str] = {}
    rows = ("position", "velocity", "reference_position", "reference_velocity", "reference_acceleration", "body_rate")
    for row_index, row in enumerate(rows):
        for axis_index, axis in enumerate(AXES):
            name = f"{row}_{axis}"
            ports[name] = source(model, name, -780, 500 - row_index * 122 - axis_index * 28)
    dt = source(model, "dt", -780, -310)
    enable = source(model, "enable", -780, -350)
    zero = constant(model, "disabled_command", 0.0, 660, -385)
    return ports, dt, enable, zero


def add_dfbc_axis(model: str, ports: dict[str, str], axis: str, index: int, variant: str, y: float) -> dict[str, str]:
    position_error = sum_ports(
        model,
        f"position_error_{axis}",
        [ports[f"reference_position_{axis}"], ports[f"position_{axis}"]],
        "+-",
        -650,
        y + 52,
    )
    velocity_error = sum_ports(
        model,
        f"velocity_error_{axis}",
        [ports[f"reference_velocity_{axis}"], ports[f"velocity_{axis}"]],
        "+-",
        -650,
        y - 52,
    )
    position_term = gain(model, f"position_feedback_{axis}", position_error, (1.7, 1.7, 2.1)[index], -510, y + 52)
    velocity_term = gain(model, f"velocity_feedback_{axis}", velocity_error, (1.2, 1.2, 1.55)[index], -510, y - 52)
    surface = sum_ports(model, f"sliding_surface_{axis}", [position_term, velocity_term], "++", -365, y)
    previous_surface = unit_delay(model, f"previous_surface_{axis}", -365, y - 85)
    connect(model, surface, f"previous_surface_{axis}.u1")
    surface_delta = sum_ports(model, f"surface_delta_{axis}", [surface, previous_surface], "+-", -220, y - 25)
    surface_rate = gain(model, f"surface_rate_{axis}", surface_delta, 1.0 / DT, -95, y - 25)

    if variant == "high_order":
        rate_term = gain(model, f"high_order_rate_feedback_{axis}", surface_rate, (0.045, 0.045, 0.060)[index], 25, y - 25)
        feedback = sum_ports(model, f"high_order_feedback_{axis}", [surface, rate_term], "++", 135, y)
        raw = sum_ports(model, f"high_order_desired_acceleration_{axis}", [ports[f"reference_acceleration_{axis}"], feedback], "++", 280, y)
        disturbance = constant(model, f"high_order_disturbance_path_{axis}", 0.0, 135, y - 110)
        command = saturation(model, f"high_order_acceleration_limit_{axis}", raw, (-4.0, -4.0, -3.0)[index], (4.0, 4.0, 3.0)[index], 410, y)
        return {
            "position_error": position_error,
            "velocity_error": velocity_error,
            "surface": surface,
            "surface_rate": surface_rate,
            "disturbance": disturbance,
            "command": command,
        }

    smooth_argument = gain(model, f"smooth_boundary_normalization_{axis}", surface, 1.0 / (0.45, 0.45, 0.35)[index], 25, y + 35)
    smooth_feedback = tanh_block(model, f"smooth_tanh_feedback_{axis}", smooth_argument, 135, y + 35)
    robust_term = gain(model, f"smooth_robust_gain_{axis}", smooth_feedback, -(0.75, 0.75, 0.95)[index], 250, y + 35)
    disturbance_state = unit_delay(model, f"disturbance_observer_state_{axis}", 25, y - 105)
    observer_innovation = sum_ports(model, f"disturbance_observer_innovation_{axis}", [surface, disturbance_state], "+-", 135, y - 105)
    observer_update = gain(model, f"disturbance_observer_gain_{axis}", observer_innovation, (0.18, 0.18, 0.14)[index], 250, y - 105)
    observer_next = sum_ports(model, f"disturbance_observer_next_{axis}", [disturbance_state, observer_update], "++", 370, y - 105)
    disturbance = saturation(model, f"disturbance_compensation_limit_{axis}", observer_next, (-1.0, -1.0, -0.8)[index], (1.0, 1.0, 0.8)[index], 485, y - 105)
    connect(model, disturbance, f"disturbance_observer_state_{axis}.u1")
    raw = sum_ports(
        model,
        f"smooth_robust_desired_acceleration_{axis}",
        [ports[f"reference_acceleration_{axis}"], surface, robust_term, disturbance],
        "+++-",
        485,
        y + 5,
    )
    command = saturation(model, f"smooth_robust_acceleration_limit_{axis}", raw, (-4.0, -4.0, -3.0)[index], (4.0, 4.0, 3.0)[index], 620, y + 5)
    return {
        "position_error": position_error,
        "velocity_error": velocity_error,
        "surface": surface,
        "surface_rate": surface_rate,
        "disturbance": disturbance,
        "command": command,
    }


def build_dfbc_variant(scheme_id: str, replace: bool) -> dict[str, Any]:
    spec = DFBC_VARIANTS[scheme_id]
    model = str(spec["model"])
    target = DFBC_SOURCE_DIR / f"{model}.mo"
    reset_model(model, str(spec["description"]), target, replace)
    ports, _, enable, zero = dfbc_inputs(model)
    axis_results = {
        axis: add_dfbc_axis(model, ports, axis, index, str(spec["variant"]), 260 - index * 285)
        for index, axis in enumerate(AXES)
    }

    outputs: dict[str, str] = {
        **{f"position_error_{axis}": axis_results[axis]["position_error"] for axis in AXES},
        **{f"velocity_error_{axis}": axis_results[axis]["velocity_error"] for axis in AXES},
        **{f"sliding_surface_{axis}": axis_results[axis]["surface"] for axis in AXES},
        **{f"surface_rate_{axis}": axis_results[axis]["surface_rate"] for axis in AXES},
        **{f"disturbance_estimate_{axis}": axis_results[axis]["disturbance"] for axis in AXES},
        **{f"desired_acceleration_{axis}": axis_results[axis]["command"] for axis in AXES},
    }
    if spec["output_mode"] == "attitude":
        desired_roll_raw = gain(model, "attitude_roll_from_lateral_acceleration", axis_results["y"]["command"], -1.0 / 9.80665, 745, 130)
        desired_pitch_raw = gain(model, "attitude_pitch_from_lateral_acceleration", axis_results["x"]["command"], 1.0 / 9.80665, 745, 75)
        outputs["desired_roll_rad"] = saturation(model, "attitude_roll_tilt_limit", desired_roll_raw, -0.52, 0.52, 855, 130)
        outputs["desired_pitch_rad"] = saturation(model, "attitude_pitch_tilt_limit", desired_pitch_raw, -0.52, 0.52, 855, 75)
    else:
        for index, axis in enumerate(AXES):
            body_rate_raw = gain(model, f"body_rate_from_acceleration_{axis}", axis_results[axis]["command"], (0.72, 0.72, 0.55)[index], 745, 155 - index * 72)
            outputs[f"desired_body_rate_{axis}"] = saturation(model, f"body_rate_limit_{axis}", body_rate_raw, (-6.0, -6.0, -3.0)[index], (6.0, 6.0, 3.0)[index], 855, 155 - index * 72)
    gravity = constant(model, "gravity_compensation", 9.80665, 745, -155)
    thrust_pre = sum_ports(model, "collective_thrust_pre_normalization", [axis_results["z"]["command"], gravity], "++", 855, -155)
    thrust_scaled = gain(model, "normalized_thrust_scaling", thrust_pre, 0.37 / 9.80665, 965, -155)
    outputs["normalized_thrust"] = saturation(model, "normalized_thrust_limit", thrust_scaled, 0.0, 1.0, 1075, -155)

    for index, (name, source_port) in enumerate(outputs.items()):
        y = 445 - index * 39
        gated = enable_switch(model, f"enable_{name}", source_port, enable, zero, 1185, y)
        output(model, f"{name}_out", gated, 1345, y)

    DFBC_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    saved = ModelingPy.SaveModelAs(model, str(DFBC_SOURCE_DIR), model)
    checked = ModelingPy.CheckModel(model)
    text = str(ModelingPy.GetModelText(model))
    return {
        "scheme_id": scheme_id,
        "model": model,
        "source_file": repo_path(target),
        "saved": bool(saved),
        "check_model": bool(checked),
        "component_count": len(list(ModelingPy.GetComponents(model))),
        "connect_count": text.count("connect("),
        "law": spec["law"],
        "formula_provenance": "Scripts/sunray/px4ctrl_golden_slice/px4ctrl_core.h:55-61,255-269",
        "claim_boundary": "Readable direct graphical DFBC control-law core only; no whole-aircraft, numerical-equivalence, generated-code, or runtime claim.",
        "ok": bool(saved and checked),
    }


def build_qp_nmpc_safety(replace: bool) -> dict[str, Any]:
    model = str(QP_NMPC_VARIANT["model"])
    target = FIXED_CHAIN_SOURCE_DIR / f"{model}.mo"
    reset_model(model, str(QP_NMPC_VARIANT["description"]), target, replace)
    inputs = {name: source(model, name, -700, 330 - index * 68) for index, name in enumerate((
        "x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref", "safety_override",
    ))}
    zero = constant(model, "zero", 0.0, 810, -320)
    one = constant(model, "one", 1.0, -525, -250)
    roll_square = product(model, "nmpc_roll_square", inputs["roll_mea"], inputs["roll_mea"], -525, -75)
    pitch_square = product(model, "nmpc_pitch_square", inputs["pitch_mea"], inputs["pitch_mea"], -525, -125)
    tilt_norm_square = sum_ports(model, "nmpc_tilt_norm_square", [roll_square, pitch_square], "++", -380, -100)
    tilt_softening = gain(model, "nmpc_tilt_softening", tilt_norm_square, 0.02, -240, -100)
    nmpc_denominator = sum_ports(model, "nmpc_softening_denominator", [one, tilt_softening], "++", -95, -100)
    nmpc_scale = product(model, "nmpc_scale", one, nmpc_denominator, 45, -100, operators="*/")
    altitude_cbf = saturation(model, "altitude_cbf_correction", gain(model, "altitude_cbf_gain", inputs["z_error"], 0.25, -240, 55), 0.0, 2.0, -95, 55)
    error_norm = sum_ports(
        model,
        "safety_error_norm_l1",
        [
            absolute(model, "safety_abs_x_error", inputs["x_error"], -525, -235),
            absolute(model, "safety_abs_y_error", inputs["y_error"], -425, -270),
            absolute(model, "safety_abs_z_error", inputs["z_error"], -325, -305),
        ],
        "+++",
        -185,
        -270,
    )
    safety_indicator = saturation(model, "safety_active_indicator", gain(model, "safety_threshold_normalization", error_norm, 1.0 / 0.75, -45, -270), 0.0, 1.0, 95, -270)
    combined_safety = saturation(model, "safety_event_selector", sum_ports(model, "safety_signal_combine", [safety_indicator, inputs["safety_override"]], "++", 245, -270), 0.0, 1.0, 390, -270)

    motor_outputs: dict[str, str] = {}
    motor_signs = ((1.0, -1.0, 1.0), (-1.0, -1.0, -1.0), (-1.0, 1.0, 1.0), (1.0, 1.0, -1.0))
    for motor_index, (roll_sign, pitch_sign, yaw_sign) in enumerate(motor_signs, start=1):
        y = 230 - (motor_index - 1) * 118
        z_term = gain(model, f"nmpc_motor{motor_index}_z_tracking", inputs["z_error"], 2.0, -385, y)
        roll_term = gain(model, f"nmpc_motor{motor_index}_roll_coupling", inputs["roll_mea"], 0.70 * roll_sign, -385, y - 28)
        pitch_term = gain(model, f"nmpc_motor{motor_index}_pitch_coupling", inputs["pitch_mea"], 0.70 * pitch_sign, -385, y - 56)
        yaw_term = gain(model, f"nmpc_motor{motor_index}_yaw_coupling", inputs["yaw_mea"], 0.10 * yaw_sign, -385, y - 84)
        nominal_raw = sum_ports(model, f"nmpc_motor{motor_index}_nominal_raw", [z_term, roll_term, pitch_term, yaw_term], "++++", -130, y - 26)
        scaled_nominal = product(model, f"nmpc_motor{motor_index}_tilt_softened_nominal", nmpc_scale, nominal_raw, 55, y - 26)
        cbf_term = gain(model, f"nmpc_motor{motor_index}_altitude_cbf_sign", altitude_cbf, 1.0 if motor_index in (1, 3) else -1.0, 170, y - 26)
        nominal_safe = sum_ports(model, f"nmpc_motor{motor_index}_nominal_with_cbf", [scaled_nominal, cbf_term], "++", 285, y - 26)
        qp_regularization = gain(model, f"qp_motor{motor_index}_regularization", nominal_safe, 0.50, 400, y - 56)
        qp_candidate = sum_ports(model, f"qp_motor{motor_index}_candidate", [nominal_safe, qp_regularization], "+-", 510, y - 26)
        qp_stage_one = saturation(model, f"qp_motor{motor_index}_projection_stage1", qp_candidate, -20.0, 20.0, 625, y - 26)
        qp_stage_two = saturation(model, f"qp_motor{motor_index}_projection_stage2", qp_stage_one, -20.0, 20.0, 735, y - 26)
        safe_descent = constant(model, f"safety_motor{motor_index}_fallback", -0.25, 735, y - 92)
        filtered = enable_switch(model, f"safety_motor{motor_index}_event_branch", qp_stage_two, combined_safety, safe_descent, 850, y - 26)
        motor_outputs[f"motor{motor_index}_command"] = filtered

    outputs = {"nmpc_scale": nmpc_scale, "safety_active": combined_safety, **motor_outputs}
    for index, (name, source_port) in enumerate(outputs.items()):
        output(model, f"{name}_out", source_port, 1015, 280 - index * 85)

    FIXED_CHAIN_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    saved = ModelingPy.SaveModelAs(model, str(FIXED_CHAIN_SOURCE_DIR), model)
    checked = ModelingPy.CheckModel(model)
    text = str(ModelingPy.GetModelText(model))
    return {
        "scheme_id": "fixed_qp_nmpc_l1_indi_cbf",
        "model": model,
        "source_file": repo_path(target),
        "saved": bool(saved),
        "check_model": bool(checked),
        "component_count": len(list(ModelingPy.GetComponents(model))),
        "connect_count": text.count("connect("),
        "law": str(QP_NMPC_VARIANT["law"]),
        "formula_provenance": "Models/MoSimQuadrotorModel/Control/Implementations/Sysblocks/AWFF_QPNMPCSafetyController_Sysblock.mo:86-117",
        "claim_boundary": "Readable direct graphical QP/NMPC safety control-law core only; no whole-aircraft, numerical-equivalence, generated-code, or runtime claim.",
        "ok": bool(saved and checked),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=49152)
    parser.add_argument("--scheme-id", action="append", choices=(*DFBC_VARIANTS, "fixed_qp_nmpc_l1_indi_cbf"))
    parser.add_argument("--replace", action="store_true", help="Replace an existing direct graphical source only after regenerating it through the official API.")
    args = parser.parse_args(argv)
    selected = args.scheme_id or [*DFBC_VARIANTS, "fixed_qp_nmpc_l1_indi_cbf"]
    SOURCE_ROOT.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "schema": "mosim.g5.dfbc_qp_nmpc_direct_graphical_build.v1",
        "scope": "Official Sysplorer API construction of readable G5 internal controller cores. No simulation, numerical-equivalence, code-generation, runtime, or whole-aircraft acceptance claim.",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "port": args.port,
        "schemes": [],
    }
    try:
        ModelingPy.ConnectSysplorer("127.0.0.1", args.port)
        for scheme_id in selected:
            row = build_qp_nmpc_safety(args.replace) if scheme_id == "fixed_qp_nmpc_l1_indi_cbf" else build_dfbc_variant(scheme_id, args.replace)
            report["schemes"].append(row)
        report["ok"] = all(bool(row["ok"]) for row in report["schemes"])
    except Exception as exc:
        report["ok"] = False
        report["error"] = str(exc)
        try:
            report["last_errors"] = [str(item) for item in ModelingPy.GetLastErrors()]
        except Exception as nested:
            report["last_errors"] = [f"GetLastErrors failed: {nested}"]
    MANIFEST_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
