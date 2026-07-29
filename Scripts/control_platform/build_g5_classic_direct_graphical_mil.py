#!/usr/bin/env python3
"""Build direct graphical G5 cores for the remaining classic wrappers.

The historical pole-placement, MRAC, NDI, FOPID, H2, and H-infinity routes
are CFunction wrappers.  This tool expands their existing source laws into
native Sysblock components through the official Sysplorer API.  The resulting
models are G5 topology-review artifacts only: they do not claim a whole-
aircraft simulation, numerical equivalence, code generation, or runtime
success.

Run with MWORKS' bundled Python against an existing Sysplorer API session:

    & 'D:\\Program Files\\MWORKS\\Sysplorer 2026a\\External\\python64\\python.exe' \
      Scripts\\control_platform\\build_g5_classic_direct_graphical_mil.py --replace
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
SOURCE_DIR = (
    ROOT
    / "Results"
    / "control_platform"
    / "g5_graphical_structure_review_20260722"
    / "direct_graphical_sources"
    / "classic"
)
MANIFEST_PATH = SOURCE_DIR / "CLASSIC_DIRECT_GRAPHICAL_BUILD.json"
CLASSIC_SOURCE = ROOT / "Scripts" / "control_platform" / "classic_controller_core.c"
HINF_SOURCE = (
    ROOT
    / "Results"
    / "control_platform"
    / "p10_mworks_gap_closeout_20260718"
    / "hinf_hover_wrench"
    / "models"
    / "MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock.mo"
)

AXES = ("x", "y", "z")
DT = 0.01
FOPID_MEMORY = 16

CLASSIC = {
    "pole_position_gain": (9.0, 9.0, 6.25),
    "pole_velocity_gain": (6.0, 6.0, 5.0),
    "observer_position_gain": (8.0, 8.0, 9.0),
    "observer_velocity_gain": (16.0, 16.0, 20.25),
    "mrac_reference_omega": (2.2, 2.2, 2.5),
    "mrac_reference_zeta": (0.85, 0.85, 0.90),
    "mrac_position_gain": (6.0, 6.0, 4.5),
    "mrac_velocity_gain": (4.5, 4.5, 4.0),
    "mrac_adaptation_gain": (0.08, 0.08, 0.10),
    "mrac_parameter_limit": (1.5, 1.5, 1.5),
    "ndi_position_gain": (8.0, 8.0, 5.0),
    "ndi_velocity_gain": (5.0, 5.0, 4.0),
    "ndi_linear_drag": (0.12, 0.12, 0.18),
    "fopid_kp": (6.5, 6.5, 4.5),
    "fopid_ki": (0.8, 0.8, 0.7),
    "fopid_kd": (1.2, 1.2, 1.0),
    "fopid_lambda": 0.85,
    "fopid_mu": 0.65,
    "h2_position_gain": (7.4, 7.4, 5.3),
    "h2_velocity_gain": (4.9, 4.9, 4.2),
    "mass": 1.0,
    "gravity": 9.80665,
    "hover_percentage": 0.37,
    "tilt_limit_rad": 0.5235987755982988,
    "min_collective_thrust_n": 0.0,
    "max_collective_thrust_n": 16.0,
}

HINF = {
    "gain": (
        (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 102.07465646871916, 0.0, 0.0, 160.7556564350713),
        (-521.4516779287975, 0.0, 0.0, -10.806018318480602, 0.0, 0.0, 0.0, -437.5189132603606, 0.0, 0.0, -1050.0326682458417, 0.0),
        (0.0, -521.451677928797, 0.0, 0.0, -10.806018318480536, 0.0, 437.51891326036105, 0.0, 0.0, 1050.0326682458376, 0.0, 0.0),
        (0.0, 0.0, -125.5903565899079, 0.0, 0.0, -25.26141057148942, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    ),
    "state_names": ("roll", "pitch", "yaw", "p", "q", "r", "u", "v", "w", "x", "y", "z"),
    "wrench_names": ("force", "tau_x", "tau_y", "tau_z"),
    "mass": 1.0,
    "gravity": 9.80665,
    "force_min_n": 0.0,
    "force_max_n": 25.0,
    "torque_limit_nm": 8.0,
    "attitude_stiffness": (30.0, 30.0, 40.0),
    "hover_percentage": 0.37,
    "tilt_limit_rad": 0.35,
    "yaw_correction_limit_rad": 0.20,
    "min_normalized_thrust": 0.0,
    "max_normalized_thrust": 0.62,
}

ALGORITHMS = {
    "pole_placement_luenberger": {
        "model": "MoSim_G5_POLE_PLACEMENT_LUENBERGER_DIRECT_GRAPHICAL_MIL",
        "label": "Pole-placement Luenberger direct graphical core",
        "law": "Luenberger position/velocity observer followed by pole-placement state feedback and attitude/thrust allocation.",
        "source": "classic",
    },
    "mrac": {
        "model": "MoSim_G5_MRAC_DIRECT_GRAPHICAL_MIL",
        "label": "MRAC direct graphical core",
        "law": "Second-order reference model, bounded adaptive gains, tracking feedback, and attitude/thrust allocation.",
        "source": "classic",
    },
    "ndi": {
        "model": "MoSim_G5_NDI_DIRECT_GRAPHICAL_MIL",
        "label": "NDI direct graphical core",
        "law": "Virtual acceleration feedback plus linear-drag inversion and attitude/thrust allocation.",
        "source": "classic",
    },
    "fopid": {
        "model": "MoSim_G5_FOPID_DIRECT_GRAPHICAL_MIL",
        "label": "FOPID direct graphical core",
        "law": "Sixteen-sample Grunwald-Letnikov fractional integral/derivative history with PID feedback and allocation.",
        "source": "classic",
    },
    "h2_state_feedback": {
        "model": "MoSim_G5_H2_STATE_FEEDBACK_DIRECT_GRAPHICAL_MIL",
        "label": "H2 state-feedback direct graphical core",
        "law": "H2 position/velocity state feedback with gravity, tilt, thrust, and allocation limits.",
        "source": "classic",
    },
    "hinf_hover_wrench": {
        "model": "MoSim_G5_HINF_HOVER_WRENCH_DIRECT_GRAPHICAL_MIL",
        "label": "H-infinity hover-wrench direct graphical core",
        "law": "Actual 4x12 H-infinity state-feedback wrench law with force/torque limits and attitude/thrust adapter.",
        "source": "hinf",
    },
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
        raise RuntimeError(f"SetParamValue failed: {name}.{parameter}={value}")


def connect(model: str, source_port: str, target_port: str) -> None:
    if not ModelingPy.ConnectPort(model, source_port, target_port):
        raise RuntimeError(f"ConnectPort failed: {model}: {source_port} -> {target_port}")


def source(model: str, name: str, x: float, y: float) -> str:
    add(model, "SysplorerEmbeddedCoder.Port.Inport", name, x, y)
    return name


def output(model: str, name: str, x: float, y: float, source_port: str) -> None:
    add(model, "SysplorerEmbeddedCoder.Port.Outport", name, x, y)
    connect(model, source_port, name)


def constant(model: str, name: str, value: float, x: float, y: float) -> str:
    add(model, "SysplorerEmbeddedCoder.Sources.Constant", name, x, y)
    set_param(name, "k", value)
    return f"{name}.y"


def gain(model: str, name: str, source_port: str, value: float, x: float, y: float) -> str:
    add(model, "SysplorerEmbeddedCoder.MathOperation.Gain", name, x, y)
    set_param(name, "k", value)
    connect(model, source_port, f"{name}.u")
    return f"{name}.y"


def product(model: str, name: str, left: str, right: str, x: float, y: float) -> str:
    add(model, "SysplorerEmbeddedCoder.MathOperation.Product", name, x, y)
    set_param(name, "inputs", "**")
    connect(model, left, f"{name}.u1")
    connect(model, right, f"{name}.u2")
    return f"{name}.y"


def sum_ports(model: str, name: str, ports: list[str], signs: str, x: float, y: float) -> str:
    if len(ports) != len(signs):
        raise ValueError(f"{name}: {len(ports)} ports do not match {signs!r}")
    if not ports:
        raise ValueError(f"{name}: at least one port is required")
    # The target Sysblock Sum accepts two live scalar ports.  Expand larger
    # algebraic sums into visible binary stages rather than relying on a
    # variadic port shape that fails CheckModel in this MWORKS release.
    result = ports[0]
    if signs[0] == "-":
        result = gain(model, f"{name}_negate_first", result, -1.0, x - 72, y)
    for index, (source_port, sign) in enumerate(zip(ports[1:], signs[1:]), start=2):
        stage_name = name if index == len(ports) else f"{name}_stage_{index}"
        stage_x = x if index == len(ports) else x - (len(ports) - index) * 68
        add(model, "SysplorerEmbeddedCoder.MathOperation.Sum", stage_name, stage_x, y)
        # A newly-created two-input Sum already has the ``++`` shape.  This
        # MWORKS build intermittently rejects an explicit re-write of that
        # default after several sequential Sum additions, so only override it
        # when the second operand is subtractive.
        if sign != "+":
            set_param(stage_name, "inputs", f"+{sign}")
        connect(model, result, f"{stage_name}.u1")
        connect(model, source_port, f"{stage_name}.u2")
        result = f"{stage_name}.y"
    if len(ports) == 1:
        return gain(model, name, result, 1.0, x, y)
    return result


def saturation(model: str, name: str, source_port: str, low: float, high: float, x: float, y: float) -> str:
    add(model, "SysplorerEmbeddedCoder.Discontinuities.Saturation", name, x, y)
    set_param(name, "lowLimit", low)
    set_param(name, "upLimit", high)
    connect(model, source_port, f"{name}.u")
    return f"{name}.y"


def delay_state(model: str, name: str, x: float, y: float, initial: float = 0.0) -> str:
    add(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", name, x, y)
    set_param(name, "initCond", initial)
    return f"{name}.y"


def enable_switch(model: str, name: str, source_port: str, enable: str, zero: str, x: float, y: float) -> str:
    add(model, "SysplorerEmbeddedCoder.SignalRouting.Switch", name, x, y)
    set_param(name, "threshold", 0.5)
    connect(model, source_port, f"{name}.u1")
    connect(model, enable, f"{name}.u2")
    connect(model, zero, f"{name}.u3")
    return f"{name}.y"


def reset_model(model: str, description: str, source_path: Path, replace: bool) -> None:
    if source_path.is_file() and not replace:
        raise RuntimeError(f"Refusing to overwrite existing direct source without --replace: {source_path}")
    if ModelingPy.ClassExist(model) and not ModelingPy.EraseClasses((model,)):
        raise RuntimeError(f"EraseClasses failed: {model}")
    if not ModelingPy.NewModel(model, "Sysblock", description):
        raise RuntimeError(f"NewModel failed: {model}")
    if not ModelingPy.OpenModel(model, "diagram"):
        raise RuntimeError(f"OpenModel failed: {model}")


def classic_inputs(model: str) -> tuple[dict[str, str], str, str, str]:
    ports: dict[str, str] = {}
    for row_index, row in enumerate(("position", "velocity", "reference_position", "reference_velocity", "reference_acceleration")):
        for axis_index, axis in enumerate(AXES):
            name = f"{row}_{axis}"
            ports[name] = source(model, name, -680, 350 - row_index * 112 - axis_index * 26)
    dt = source(model, "dt", -680, -245)
    enable = source(model, "enable", -680, -285)
    zero = constant(model, "disabled_command", 0.0, 500, -310)
    return ports, dt, enable, zero


def add_gated_outputs(model: str, ports: dict[str, str], enable: str, zero: str, *, x: float = 535, y: float = 360) -> None:
    for index, (name, source_port) in enumerate(ports.items()):
        row_y = y - index * 38
        gated = enable_switch(model, f"enable_{name}", source_port, enable, zero, x, row_y)
        output(model, f"{name}_out", x + 160, row_y, gated)


def add_classic_adapter(model: str, desired_acceleration: dict[str, str]) -> dict[str, str]:
    roll_raw = gain(
        model,
        "roll_from_lateral_acceleration",
        desired_acceleration["y"],
        -1.0 / CLASSIC["gravity"],
        230,
        75,
    )
    roll = saturation(
        model,
        "roll_tilt_limit",
        roll_raw,
        -CLASSIC["tilt_limit_rad"],
        CLASSIC["tilt_limit_rad"],
        320,
        75,
    )
    pitch_raw = gain(
        model,
        "pitch_from_lateral_acceleration",
        desired_acceleration["x"],
        1.0 / CLASSIC["gravity"],
        230,
        130,
    )
    pitch = saturation(
        model,
        "pitch_tilt_limit",
        pitch_raw,
        -CLASSIC["tilt_limit_rad"],
        CLASSIC["tilt_limit_rad"],
        320,
        130,
    )
    vertical_force = gain(
        model,
        "vertical_force_allocation",
        desired_acceleration["z"],
        CLASSIC["mass"],
        230,
        -45,
    )
    collective = saturation(
        model,
        "collective_thrust_limit",
        vertical_force,
        CLASSIC["min_collective_thrust_n"],
        CLASSIC["max_collective_thrust_n"],
        320,
        -45,
    )
    normalized_raw = gain(
        model,
        "normalized_thrust_from_collective",
        collective,
        CLASSIC["hover_percentage"] / (CLASSIC["mass"] * CLASSIC["gravity"]),
        410,
        -45,
    )
    normalized = saturation(model, "normalized_thrust_limit", normalized_raw, 0.0, 1.0, 500, -45)
    return {
        "desired_roll_rad": roll,
        "desired_pitch_rad": pitch,
        "collective_thrust_n": collective,
        "normalized_thrust": normalized,
    }


def finish_classic_axis_acceleration(
    model: str, axis: str, raw_acceleration: str, y: float
) -> str:
    if axis != "z":
        return gain(model, f"desired_acceleration_{axis}", raw_acceleration, 1.0, 140, y)
    gravity = constant(model, "gravity_compensation", CLASSIC["gravity"], 55, y + 72)
    return sum_ports(model, "desired_acceleration_z", [raw_acceleration, gravity], "++", 140, y)


def build_pole_placement(model: str) -> None:
    inputs, dt, enable, zero = classic_inputs(model)
    desired: dict[str, str] = {}
    outputs: dict[str, str] = {}
    for axis_index, axis in enumerate(AXES):
        y = 245 - axis_index * 225
        observer_position = delay_state(model, f"observer_position_state_{axis}", -410, y + 85)
        observer_velocity = delay_state(model, f"observer_velocity_state_{axis}", -410, y + 45)
        previous_virtual = delay_state(model, f"previous_virtual_acceleration_state_{axis}", -410, y - 145)
        residual = sum_ports(model, f"observer_residual_{axis}", [inputs[f"position_{axis}"], observer_position], "+-", -535, y + 85)
        position_correction = gain(model, f"observer_position_correction_{axis}", residual, CLASSIC["observer_position_gain"][axis_index], -300, y + 105)
        position_dot = sum_ports(model, f"observer_position_dot_{axis}", [observer_velocity, position_correction], "++", -190, y + 85)
        position_increment = product(model, f"observer_position_increment_{axis}", position_dot, dt, -90, y + 85)
        position_next = sum_ports(model, f"observer_position_next_{axis}", [observer_position, position_increment], "++", 10, y + 85)
        connect(model, position_next, f"observer_position_state_{axis}.u1")
        velocity_correction = gain(model, f"observer_velocity_correction_{axis}", residual, CLASSIC["observer_velocity_gain"][axis_index], -300, y + 35)
        velocity_dot = sum_ports(model, f"observer_velocity_dot_{axis}", [previous_virtual, velocity_correction], "++", -190, y + 45)
        velocity_increment = product(model, f"observer_velocity_increment_{axis}", velocity_dot, dt, -90, y + 45)
        velocity_next = sum_ports(model, f"observer_velocity_next_{axis}", [observer_velocity, velocity_increment], "++", 10, y + 45)
        connect(model, velocity_next, f"observer_velocity_state_{axis}.u1")
        position_error = sum_ports(model, f"pole_position_error_{axis}", [inputs[f"reference_position_{axis}"], observer_position], "+-", -300, y - 15)
        velocity_error = sum_ports(model, f"pole_velocity_error_{axis}", [inputs[f"reference_velocity_{axis}"], observer_velocity], "+-", -300, y - 55)
        position_feedback = gain(model, f"pole_position_feedback_{axis}", position_error, CLASSIC["pole_position_gain"][axis_index], -180, y - 15)
        velocity_feedback = gain(model, f"pole_velocity_feedback_{axis}", velocity_error, CLASSIC["pole_velocity_gain"][axis_index], -180, y - 55)
        feedback = sum_ports(model, f"pole_state_feedback_{axis}", [position_feedback, velocity_feedback], "++", -55, y - 35)
        pre_gravity = sum_ports(model, f"pole_virtual_acceleration_{axis}", [inputs[f"reference_acceleration_{axis}"], feedback], "++", 55, y - 35)
        connect(model, pre_gravity, f"previous_virtual_acceleration_state_{axis}.u1")
        desired[axis] = finish_classic_axis_acceleration(model, axis, pre_gravity, y - 35)
        outputs[f"observer_position_{axis}"] = observer_position
        outputs[f"observer_velocity_{axis}"] = observer_velocity
        outputs[f"position_error_{axis}"] = position_error
        outputs[f"velocity_error_{axis}"] = velocity_error
        outputs[f"desired_acceleration_{axis}"] = desired[axis]
    outputs.update(add_classic_adapter(model, desired))
    add_gated_outputs(model, outputs, enable, zero)


def build_mrac(model: str) -> None:
    inputs, dt, enable, zero = classic_inputs(model)
    desired: dict[str, str] = {}
    outputs: dict[str, str] = {}
    for axis_index, axis in enumerate(AXES):
        y = 245 - axis_index * 225
        reference_position = delay_state(model, f"reference_model_position_state_{axis}", -430, y + 95)
        reference_velocity = delay_state(model, f"reference_model_velocity_state_{axis}", -430, y + 55)
        adaptive_position = delay_state(model, f"adaptive_position_delta_state_{axis}", -160, y - 130)
        adaptive_velocity = delay_state(model, f"adaptive_velocity_delta_state_{axis}", -160, y - 172)
        model_position_error = sum_ports(model, f"reference_model_position_error_{axis}", [inputs[f"reference_position_{axis}"], reference_position], "+-", -555, y + 95)
        model_velocity_error = sum_ports(model, f"reference_model_velocity_error_{axis}", [reference_velocity, inputs[f"reference_velocity_{axis}"]], "+-", -555, y + 55)
        omega = CLASSIC["mrac_reference_omega"][axis_index]
        model_position_term = gain(model, f"reference_model_position_term_{axis}", model_position_error, omega * omega, -330, y + 105)
        model_velocity_term = gain(model, f"reference_model_damping_term_{axis}", model_velocity_error, -2.0 * CLASSIC["mrac_reference_zeta"][axis_index] * omega, -330, y + 55)
        model_acceleration = sum_ports(model, f"reference_model_acceleration_{axis}", [inputs[f"reference_acceleration_{axis}"], model_position_term, model_velocity_term], "+++", -180, y + 80)
        position_increment = product(model, f"reference_model_position_increment_{axis}", reference_velocity, dt, -70, y + 95)
        position_next = sum_ports(model, f"reference_model_position_next_{axis}", [reference_position, position_increment], "++", 30, y + 95)
        connect(model, position_next, f"reference_model_position_state_{axis}.u1")
        velocity_increment = product(model, f"reference_model_velocity_increment_{axis}", model_acceleration, dt, -70, y + 55)
        velocity_next = sum_ports(model, f"reference_model_velocity_next_{axis}", [reference_velocity, velocity_increment], "++", 30, y + 55)
        connect(model, velocity_next, f"reference_model_velocity_state_{axis}.u1")
        position_error = sum_ports(model, f"mrac_position_error_{axis}", [reference_position, inputs[f"position_{axis}"]], "+-", -330, y - 5)
        velocity_error = sum_ports(model, f"mrac_velocity_error_{axis}", [reference_velocity, inputs[f"velocity_{axis}"]], "+-", -330, y - 45)
        sliding_position = gain(model, f"mrac_sliding_position_component_{axis}", position_error, 0.5 * CLASSIC["mrac_position_gain"][axis_index], -205, y - 5)
        sliding = sum_ports(model, f"mrac_sliding_surface_{axis}", [velocity_error, sliding_position], "++", -80, y - 25)
        position_drive = product(model, f"mrac_position_adaptation_drive_{axis}", sliding, position_error, -40, y - 130)
        position_increment_drive = product(model, f"mrac_position_adaptation_dt_{axis}", position_drive, dt, 50, y - 130)
        position_increment_gain = gain(model, f"mrac_position_adaptation_gain_{axis}", position_increment_drive, CLASSIC["mrac_adaptation_gain"][axis_index], 140, y - 130)
        position_delta_pre = sum_ports(model, f"mrac_position_delta_pre_{axis}", [adaptive_position, position_increment_gain], "++", 235, y - 130)
        position_delta = saturation(model, f"mrac_position_delta_limit_{axis}", position_delta_pre, -CLASSIC["mrac_parameter_limit"][axis_index], CLASSIC["mrac_parameter_limit"][axis_index], 335, y - 130)
        connect(model, position_delta, f"adaptive_position_delta_state_{axis}.u1")
        velocity_drive = product(model, f"mrac_velocity_adaptation_drive_{axis}", sliding, velocity_error, -40, y - 172)
        velocity_increment_drive = product(model, f"mrac_velocity_adaptation_dt_{axis}", velocity_drive, dt, 50, y - 172)
        velocity_increment_gain = gain(model, f"mrac_velocity_adaptation_gain_{axis}", velocity_increment_drive, CLASSIC["mrac_adaptation_gain"][axis_index], 140, y - 172)
        velocity_delta_pre = sum_ports(model, f"mrac_velocity_delta_pre_{axis}", [adaptive_velocity, velocity_increment_gain], "++", 235, y - 172)
        velocity_delta = saturation(model, f"mrac_velocity_delta_limit_{axis}", velocity_delta_pre, -CLASSIC["mrac_parameter_limit"][axis_index], CLASSIC["mrac_parameter_limit"][axis_index], 335, y - 172)
        connect(model, velocity_delta, f"adaptive_velocity_delta_state_{axis}.u1")
        base_position_gain = constant(model, f"mrac_base_position_gain_{axis}", CLASSIC["mrac_position_gain"][axis_index], 20, y - 70)
        base_velocity_gain = constant(model, f"mrac_base_velocity_gain_{axis}", CLASSIC["mrac_velocity_gain"][axis_index], 20, y - 100)
        effective_position_gain = sum_ports(model, f"mrac_effective_position_gain_{axis}", [base_position_gain, adaptive_position], "++", 120, y - 70)
        effective_velocity_gain = sum_ports(model, f"mrac_effective_velocity_gain_{axis}", [base_velocity_gain, adaptive_velocity], "++", 120, y - 100)
        position_feedback = product(model, f"mrac_position_feedback_{axis}", effective_position_gain, position_error, 250, y - 70)
        velocity_feedback = product(model, f"mrac_velocity_feedback_{axis}", effective_velocity_gain, velocity_error, 250, y - 100)
        pre_gravity = sum_ports(model, f"mrac_desired_acceleration_pre_gravity_{axis}", [model_acceleration, position_feedback, velocity_feedback], "+++", 390, y - 80)
        desired[axis] = finish_classic_axis_acceleration(model, axis, pre_gravity, y - 80)
        outputs[f"reference_model_position_{axis}"] = reference_position
        outputs[f"reference_model_velocity_{axis}"] = reference_velocity
        outputs[f"adaptive_position_delta_{axis}"] = adaptive_position
        outputs[f"adaptive_velocity_delta_{axis}"] = adaptive_velocity
        outputs[f"sliding_surface_{axis}"] = sliding
        outputs[f"desired_acceleration_{axis}"] = desired[axis]
    outputs.update(add_classic_adapter(model, desired))
    add_gated_outputs(model, outputs, enable, zero, y=350)


def build_ndi_or_h2(model: str, scheme_id: str) -> None:
    inputs, _dt, enable, zero = classic_inputs(model)
    desired: dict[str, str] = {}
    outputs: dict[str, str] = {}
    if scheme_id == "ndi":
        position_gains = CLASSIC["ndi_position_gain"]
        velocity_gains = CLASSIC["ndi_velocity_gain"]
        prefix = "ndi"
    else:
        position_gains = CLASSIC["h2_position_gain"]
        velocity_gains = CLASSIC["h2_velocity_gain"]
        prefix = "h2"
    for axis_index, axis in enumerate(AXES):
        y = 235 - axis_index * 215
        position_error = sum_ports(model, f"{prefix}_position_error_{axis}", [inputs[f"reference_position_{axis}"], inputs[f"position_{axis}"]], "+-", -500, y + 42)
        velocity_error = sum_ports(model, f"{prefix}_velocity_error_{axis}", [inputs[f"reference_velocity_{axis}"], inputs[f"velocity_{axis}"]], "+-", -500, y - 42)
        position_feedback = gain(model, f"{prefix}_position_feedback_{axis}", position_error, position_gains[axis_index], -370, y + 42)
        velocity_feedback = gain(model, f"{prefix}_velocity_feedback_{axis}", velocity_error, velocity_gains[axis_index], -370, y - 42)
        virtual_acceleration = sum_ports(model, f"{prefix}_virtual_acceleration_{axis}", [inputs[f"reference_acceleration_{axis}"], position_feedback, velocity_feedback], "+++", -190, y)
        if scheme_id == "ndi":
            drag_inverse = gain(model, f"ndi_drag_inverse_{axis}", inputs[f"velocity_{axis}"], CLASSIC["ndi_linear_drag"][axis_index] / CLASSIC["mass"], -50, y - 78)
            pre_gravity = sum_ports(model, f"ndi_desired_acceleration_pre_gravity_{axis}", [virtual_acceleration, drag_inverse], "++", 65, y)
            outputs[f"drag_inverse_{axis}"] = drag_inverse
        else:
            pre_gravity = gain(model, f"h2_desired_acceleration_pre_gravity_{axis}", virtual_acceleration, 1.0, 65, y)
        desired[axis] = finish_classic_axis_acceleration(model, axis, pre_gravity, y)
        outputs[f"position_error_{axis}"] = position_error
        outputs[f"velocity_error_{axis}"] = velocity_error
        outputs[f"virtual_acceleration_{axis}"] = virtual_acceleration
        outputs[f"desired_acceleration_{axis}"] = desired[axis]
    outputs.update(add_classic_adapter(model, desired))
    add_gated_outputs(model, outputs, enable, zero)


def gl_coefficients(alpha: float) -> list[float]:
    coefficient = 1.0
    values: list[float] = []
    for index in range(FOPID_MEMORY):
        if index > 0:
            coefficient *= -((alpha - float(index) + 1.0) / float(index))
        values.append((DT ** (-alpha)) * coefficient)
    return values


def build_fopid(model: str) -> None:
    inputs, _dt, enable, zero = classic_inputs(model)
    desired: dict[str, str] = {}
    outputs: dict[str, str] = {}
    integral_weights = gl_coefficients(-CLASSIC["fopid_lambda"])
    derivative_weights = gl_coefficients(CLASSIC["fopid_mu"])
    for axis_index, axis in enumerate(AXES):
        y = 260 - axis_index * 235
        error = sum_ports(model, f"fopid_position_error_{axis}", [inputs[f"reference_position_{axis}"], inputs[f"position_{axis}"]], "+-", -590, y)
        history = [error]
        previous = error
        for sample_index in range(1, FOPID_MEMORY):
            state_name = f"fopid_history_{axis}_{sample_index:02d}"
            state = delay_state(model, state_name, -500 + sample_index * 42, y)
            connect(model, previous, f"{state_name}.u1")
            history.append(state)
            previous = state
        integral_terms = [
            gain(model, f"fopid_integral_weight_{axis}_{index:02d}", sample, integral_weights[index], -500 + index * 42, y - 58)
            for index, sample in enumerate(history)
        ]
        derivative_terms = [
            gain(model, f"fopid_derivative_weight_{axis}_{index:02d}", sample, derivative_weights[index], -500 + index * 42, y - 102)
            for index, sample in enumerate(history)
        ]
        fractional_integral = sum_ports(model, f"fopid_fractional_integral_{axis}", integral_terms, "+" * len(integral_terms), 165, y - 58)
        fractional_derivative = sum_ports(model, f"fopid_fractional_derivative_{axis}", derivative_terms, "+" * len(derivative_terms), 165, y - 102)
        proportional = gain(model, f"fopid_proportional_{axis}", error, CLASSIC["fopid_kp"][axis_index], -150, y + 40)
        integral = gain(model, f"fopid_integral_feedback_{axis}", fractional_integral, CLASSIC["fopid_ki"][axis_index], 265, y - 58)
        derivative = gain(model, f"fopid_derivative_feedback_{axis}", fractional_derivative, CLASSIC["fopid_kd"][axis_index], 265, y - 102)
        pre_gravity = sum_ports(model, f"fopid_desired_acceleration_pre_gravity_{axis}", [inputs[f"reference_acceleration_{axis}"], proportional, integral, derivative], "++++", 375, y)
        desired[axis] = finish_classic_axis_acceleration(model, axis, pre_gravity, y)
        outputs[f"position_error_{axis}"] = error
        outputs[f"fractional_integral_{axis}"] = fractional_integral
        outputs[f"fractional_derivative_{axis}"] = fractional_derivative
        outputs[f"desired_acceleration_{axis}"] = desired[axis]
    outputs.update(add_classic_adapter(model, desired))
    add_gated_outputs(model, outputs, enable, zero, y=345)


def build_hinf(model: str) -> None:
    state: dict[str, str] = {}
    reference: dict[str, str] = {}
    for index, name in enumerate(HINF["state_names"]):
        state[name] = source(model, f"state_{name}", -660, 365 - index * 56)
        reference[name] = source(model, f"reference_{name}", -570, 365 - index * 56)
    enable = source(model, "enable", -660, -355)
    zero = constant(model, "disabled_command", 0.0, 430, -310)
    errors: dict[str, str] = {}
    for index, name in enumerate(HINF["state_names"]):
        errors[name] = sum_ports(model, f"state_error_{name}", [state[name], reference[name]], "+-", -440, 365 - index * 56)
    wrench: dict[str, str] = {}
    for command_index, command_name in enumerate(HINF["wrench_names"]):
        terms: list[str] = []
        if command_index == 0:
            terms.append(constant(model, "hover_force_bias", HINF["mass"] * HINF["gravity"], -235, 160))
        for state_index, coefficient in enumerate(HINF["gain"][command_index]):
            if coefficient == 0.0:
                continue
            state_name = HINF["state_names"][state_index]
            terms.append(gain(model, f"hinf_{command_name}_gain_{state_name}", errors[state_name], coefficient, -250, 365 - state_index * 56))
        raw = sum_ports(model, f"hinf_{command_name}_raw", terms, "+" * len(terms), 35, 160 - command_index * 105)
        if command_index == 0:
            wrench[command_name] = saturation(model, "hinf_force_limit", raw, HINF["force_min_n"], HINF["force_max_n"], 145, 160)
        else:
            wrench[command_name] = saturation(model, f"hinf_{command_name}_limit", raw, -HINF["torque_limit_nm"], HINF["torque_limit_nm"], 145, 160 - command_index * 105)
    normalized_raw = gain(model, "hinf_normalized_thrust_from_force", wrench["force"], HINF["hover_percentage"] / (HINF["mass"] * HINF["gravity"]), 255, 160)
    normalized = saturation(model, "hinf_normalized_thrust_limit", normalized_raw, HINF["min_normalized_thrust"], HINF["max_normalized_thrust"], 355, 160)
    roll_correction = gain(model, "hinf_roll_wrench_to_angle", wrench["tau_x"], 1.0 / HINF["attitude_stiffness"][0], 255, 55)
    roll_pre = sum_ports(model, "hinf_roll_reference_plus_correction", [reference["roll"], roll_correction], "++", 355, 55)
    roll = saturation(model, "hinf_roll_tilt_limit", roll_pre, -HINF["tilt_limit_rad"], HINF["tilt_limit_rad"], 455, 55)
    pitch_correction = gain(model, "hinf_pitch_wrench_to_angle", wrench["tau_y"], 1.0 / HINF["attitude_stiffness"][1], 255, -50)
    pitch_pre = sum_ports(model, "hinf_pitch_reference_plus_correction", [reference["pitch"], pitch_correction], "++", 355, -50)
    pitch = saturation(model, "hinf_pitch_tilt_limit", pitch_pre, -HINF["tilt_limit_rad"], HINF["tilt_limit_rad"], 455, -50)
    yaw_correction_raw = gain(model, "hinf_yaw_wrench_to_angle", wrench["tau_z"], 1.0 / HINF["attitude_stiffness"][2], 255, -155)
    yaw_correction = saturation(model, "hinf_yaw_correction_limit", yaw_correction_raw, -HINF["yaw_correction_limit_rad"], HINF["yaw_correction_limit_rad"], 355, -155)
    yaw = sum_ports(model, "hinf_yaw_reference_plus_correction", [reference["yaw"], yaw_correction], "++", 455, -155)
    outputs = {
        "state_error_roll": errors["roll"],
        "state_error_pitch": errors["pitch"],
        "state_error_yaw": errors["yaw"],
        "wrench_force_n": wrench["force"],
        "wrench_tau_x_nm": wrench["tau_x"],
        "wrench_tau_y_nm": wrench["tau_y"],
        "wrench_tau_z_nm": wrench["tau_z"],
        "collective_thrust_n": wrench["force"],
        "normalized_thrust": normalized,
        "adapted_roll_rad": roll,
        "adapted_pitch_rad": pitch,
        "adapted_yaw_rad": yaw,
    }
    add_gated_outputs(model, outputs, enable, zero, x=560, y=330)


def build_variant(scheme_id: str, replace: bool) -> dict[str, Any]:
    spec = ALGORITHMS[scheme_id]
    model = str(spec["model"])
    target = SOURCE_DIR / f"{model}.mo"
    reset_model(model, str(spec["label"]), target, replace)
    if scheme_id == "pole_placement_luenberger":
        build_pole_placement(model)
    elif scheme_id == "mrac":
        build_mrac(model)
    elif scheme_id in {"ndi", "h2_state_feedback"}:
        build_ndi_or_h2(model, scheme_id)
    elif scheme_id == "fopid":
        build_fopid(model)
    elif scheme_id == "hinf_hover_wrench":
        build_hinf(model)
    else:
        raise ValueError(f"Unhandled scheme: {scheme_id}")
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    saved = ModelingPy.SaveModelAs(model, str(SOURCE_DIR), model)
    checked = ModelingPy.CheckModel(model)
    source_text = str(ModelingPy.GetModelText(model))
    source_file = HINF_SOURCE if spec["source"] == "hinf" else CLASSIC_SOURCE
    formula_reference = (
        f"{repo_path(HINF_SOURCE)}:343-399,455-538"
        if spec["source"] == "hinf"
        else f"{repo_path(CLASSIC_SOURCE)}:99-148,173-328"
    )
    return {
        "scheme_id": scheme_id,
        "model": model,
        "source_file": repo_path(target),
        "saved": bool(saved),
        "check_model": bool(checked),
        "component_count": len(list(ModelingPy.GetComponents(model))),
        "connect_count": source_text.count("connect("),
        "line_annotation_count": source_text.count("annotation(Line"),
        "law": spec["law"],
        "source_formula_reference": formula_reference,
        "source_formula_sha256": sha256(source_file),
        "claim_boundary": "Direct graphical control-law core only. It is not a whole-aircraft harness, simulation result, code-generation result, runtime result, or numerical-equivalence claim.",
        "ok": bool(saved and checked),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=49153)
    parser.add_argument("--scheme-id", action="append", choices=tuple(ALGORITHMS), help="Build only the named scheme; repeat for more than one.")
    parser.add_argument("--replace", action="store_true", help="Replace an existing direct source after rebuilding it through the official API.")
    args = parser.parse_args(argv)
    selected = args.scheme_id or list(ALGORITHMS)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "schema": "mosim.g5.classic_direct_graphical_build.v1",
        "scope": "Direct graphical replacements for historical classic and H-infinity CFunction wrappers. Old wrappers remain compatibility and formula-provenance artifacts.",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "classic_source": repo_path(CLASSIC_SOURCE),
        "classic_source_sha256": sha256(CLASSIC_SOURCE),
        "hinf_source": repo_path(HINF_SOURCE),
        "hinf_source_sha256": sha256(HINF_SOURCE),
        "port": args.port,
        "schemes": [],
    }
    try:
        ModelingPy.ConnectSysplorer("127.0.0.1", args.port)
        for scheme_id in selected:
            report["schemes"].append(build_variant(scheme_id, args.replace))
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
