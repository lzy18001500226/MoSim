#!/usr/bin/env python3
"""Build the pid_awff_linear_eso graphical Sysblock through Sysplorer APIs.

The model is a reviewable graphical counterpart of the active AWFF plus
linear-ESO equation core.  It deliberately creates only the controller-core
topology; it does not replace the whole-aircraft Adapter or FormalRunner.

Run this file inside an already connected Sysplorer process through
``call_code(mode=\"run_script\")``.  The script never clears the session or
changes Sysplorer's working directory.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
MODEL_NAME = "MoSim_PID_AWFF_LINEAR_ESO_GRAPHICAL_MIL"
SOURCE_EQUATION = (
    ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Control"
    / "Implementations"
    / "Sysblocks"
    / "AWFF_PidLinearEsoControllerEquation_Sysblock.mo"
)
EVIDENCE_DIR = ROOT / "Results" / "control_platform" / "pid_awff_linear_eso_graphical_20260802"
MODEL_DIR = EVIDENCE_DIR / ".sysplorer_tmp"
MODEL_LIBRARY_DIR = (
    ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Control"
    / "Implementations"
    / "Sysblocks"
)
CANONICAL_MODEL_PATH = MODEL_LIBRARY_DIR / f"{MODEL_NAME}.mo"
DIAGRAM_PATH = EVIDENCE_DIR / "screenshots" / f"{MODEL_NAME}.png"
MANIFEST_PATH = EVIDENCE_DIR / "PID_AWFF_LINEAR_ESO_GRAPHICAL_BUILD.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def promote_to_model_library(generated_model: Path) -> None:
    """Promote the native Sysplorer export into the active Sysblocks package."""
    text = generated_model.read_text(encoding="utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip(" \t") for line in text.split("\n"))
    within = "within MoSimQuadrotorModel.Control.Implementations.Sysblocks;\n"
    if not text.startswith(within):
        text = within + text.lstrip("\n")
    if not text.endswith("\n"):
        text += "\n"
    MODEL_LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    with CANONICAL_MODEL_PATH.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)


def add(model: str, type_name: str, name: str, x: float, y: float, width: float = 32, height: float = 24) -> None:
    if not ModelingPy.AddComponent(type_name, model, name, x, y, width, height):
        raise RuntimeError(f"AddComponent failed: {model}.{name} ({type_name})")


def set_param(name: str, parameter: str, value: object) -> None:
    encoded = f'"{value}"' if parameter == "inputs" else str(value)
    if not ModelingPy.SetParamValue(f"{name}.{parameter}", encoded):
        raise RuntimeError(f"SetParamValue failed: {name}.{parameter}={value}")


def connect(model: str, source_port: str, target_port: str) -> None:
    if not ModelingPy.ConnectPort(model, source_port, target_port):
        raise RuntimeError(f"ConnectPort failed: {model}: {source_port} -> {target_port}")


def source(model: str, name: str, x: float, y: float, description: str) -> str:
    add(model, "SysplorerEmbeddedCoder.Port.Inport", name, x, y)
    ModelingPy.SetComponentDescription(model, name, description)
    return name


def output(model: str, name: str, x: float, y: float, source_port: str, description: str) -> None:
    add(model, "SysplorerEmbeddedCoder.Port.Outport", name, x, y)
    ModelingPy.SetComponentDescription(model, name, description)
    connect(model, source_port, name)


def constant(model: str, name: str, value: float, x: float, y: float, description: str) -> str:
    add(model, "SysplorerEmbeddedCoder.Sources.Constant", name, x, y)
    set_param(name, "k", value)
    ModelingPy.SetComponentDescription(model, name, description)
    return f"{name}.y"


def gain(model: str, name: str, source_port: str, value: float, x: float, y: float, description: str) -> str:
    add(model, "SysplorerEmbeddedCoder.MathOperation.Gain", name, x, y)
    set_param(name, "k", value)
    ModelingPy.SetComponentDescription(model, name, description)
    connect(model, source_port, f"{name}.u")
    return f"{name}.y"


def sum_ports(model: str, name: str, ports: list[str], signs: str, x: float, y: float, description: str) -> str:
    if len(ports) != len(signs) or not ports:
        raise ValueError(f"{name}: port/sign shape mismatch")
    # This Sysplorer release is reliable with binary live Sum blocks.  Expand
    # multi-term equations into visible two-input stages instead of relying on
    # a variable-port block shape.
    result = ports[0]
    if signs[0] == "-":
        result = gain(model, f"{name}_negate_first", result, -1.0, x - 72, y, "sign inversion")
    for index, (port, sign) in enumerate(zip(ports[1:], signs[1:]), start=2):
        stage = name if index == len(ports) else f"{name}_stage_{index}"
        stage_x = x if index == len(ports) else x - (len(ports) - index) * 68
        add(model, "SysplorerEmbeddedCoder.MathOperation.Sum", stage, stage_x, y)
        if sign == "-":
            set_param(stage, "inputs", "+-")
        ModelingPy.SetComponentDescription(model, stage, description)
        connect(model, result, f"{stage}.u1")
        connect(model, port, f"{stage}.u2")
        result = f"{stage}.y"
    return result


def saturation(model: str, name: str, source_port: str, low: float, high: float, x: float, y: float, description: str) -> str:
    add(model, "SysplorerEmbeddedCoder.Discontinuities.Saturation", name, x, y)
    set_param(name, "lowLimit", low)
    set_param(name, "upLimit", high)
    ModelingPy.SetComponentDescription(model, name, description)
    connect(model, source_port, f"{name}.u")
    return f"{name}.y"


def unit_delay(model: str, name: str, x: float, y: float, description: str) -> str:
    add(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", name, x, y)
    set_param(name, "initCond", 0.0)
    ModelingPy.SetComponentDescription(model, name, description)
    return f"{name}.y"


def integrator(model: str, name: str, derivative_port: str, x: float, y: float, description: str) -> str:
    add(model, "SysplorerEmbeddedCoder.Continuous.Integrator", name, x, y)
    ModelingPy.SetComponentDescription(model, name, description)
    connect(model, derivative_port, f"{name}.u1")
    return f"{name}.y"


def awff_xy(model: str, axis: str, error: str, y: float) -> str:
    """Construct 0.1*(kp*e + kd*de/dt) for the horizontal AWFF branches."""
    kp = 1.65
    kd = 1.0
    p = gain(model, f"AWFF_{axis}_P", error, 0.1 * kp, -585, y + 32, f"AWFF {axis} proportional command")
    previous = unit_delay(model, f"AWFF_{axis}_previous_error", -585, y - 50, f"AWFF {axis} derivative memory")
    delta = sum_ports(model, f"AWFF_{axis}_error_delta", [error, previous], "+-", -495, y - 50, f"AWFF {axis} error difference")
    rate = gain(model, f"AWFF_{axis}_derivative_rate", delta, 100.0, -405, y - 50, f"AWFF {axis} derivative at 100 Hz")
    d = gain(model, f"AWFF_{axis}_D", rate, 0.1 * kd, -315, y - 50, f"AWFF {axis} derivative command")
    base = sum_ports(model, f"AWFF_{axis}_base", [p, d], "++", -225, y, f"AWFF {axis} nominal base command")
    connect(model, error, f"AWFF_{axis}_previous_error.u1")
    return base


def awff_z(model: str, error: str, z_ref_rate: str, y: float) -> str:
    """Construct the altitude PID plus feedforward base command."""
    p = gain(model, "AWFF_z_P", error, 8.0, -585, y + 68, "AWFF z proportional command")
    previous = unit_delay(model, "AWFF_z_previous_error", -585, y - 15, "AWFF z derivative memory")
    delta = sum_ports(model, "AWFF_z_error_delta", [error, previous], "+-", -495, y - 15, "AWFF z error difference")
    rate = gain(model, "AWFF_z_derivative_rate", delta, 100.0, -405, y - 15, "AWFF z derivative at 100 Hz")
    d = gain(model, "AWFF_z_D", rate, 4.0, -315, y - 15, "AWFF z derivative command")
    integral_state = unit_delay(model, "AWFF_z_integral_state", -405, y - 92, "AWFF z bounded integral memory")
    integral_increment = gain(model, "AWFF_z_integral_increment", error, 0.01, -315, y - 92, "AWFF z integral increment at 100 Hz")
    integral_next = sum_ports(model, "AWFF_z_integral_next", [integral_state, integral_increment], "++", -225, y - 92, "AWFF z integral update")
    integral_limited = saturation(model, "AWFF_z_integral_limit", integral_next, -2.5, 2.5, -135, y - 92, "AWFF z integral limit")
    i = gain(model, "AWFF_z_I", integral_state, 6.0, -135, y - 52, "AWFF z integral command")
    ff = gain(model, "AWFF_z_feedforward", z_ref_rate, 0.35, -315, y + 108, "AWFF z reference-rate feedforward")
    pi = sum_ports(model, "AWFF_z_PI", [p, i], "++", -45, y + 35, "AWFF z PI command")
    pid = sum_ports(model, "AWFF_z_PID", [pi, d], "++", 45, y + 15, "AWFF z PID command")
    base = sum_ports(model, "AWFF_z_base", [pid, ff], "++", 135, y, "AWFF z nominal base command")
    connect(model, error, "AWFF_z_previous_error.u1")
    connect(model, integral_limited, "AWFF_z_integral_state.u1")
    return base


def eso_axis(model: str, axis: str, error: str, base_command: str, y: float, bandwidth: float, limit: float) -> str:
    """Build the continuous third-order linear ESO and bounded compensation."""
    beta1 = 3.0 * bandwidth
    beta2 = 3.0 * bandwidth * bandwidth
    beta3 = bandwidth * bandwidth * bandwidth
    z1_placeholder_x = 40
    z2_placeholder_x = 175
    z3_placeholder_x = 310
    z1 = unit_delay(model, f"ESO_{axis}_z1_feedback", z1_placeholder_x, y + 105, f"ESO {axis} z1 feedback tap")
    # The feedback taps are replaced below by the true continuous states.  They
    # make the innovation loop explicit and retain graphical port visibility.
    innovation = sum_ports(model, f"ESO_{axis}_innovation", [error, z1], "+-", -80, y + 115, f"ESO {axis}: e - z1")
    beta1_term = gain(model, f"ESO_{axis}_beta1_innovation", innovation, beta1, -5, y + 155, f"ESO {axis}: 3*w_o innovation")
    z2 = unit_delay(model, f"ESO_{axis}_z2_feedback", z2_placeholder_x, y + 85, f"ESO {axis} z2 feedback tap")
    z1_dot = sum_ports(model, f"ESO_{axis}_z1_dot", [z2, beta1_term], "++", 70, y + 125, f"ESO {axis}: z2 + beta1 innovation")
    z1_state = integrator(model, f"ESO_{axis}_z1_state", z1_dot, 145, y + 125, f"ESO {axis} continuous state z1")
    z3 = unit_delay(model, f"ESO_{axis}_z3_feedback", z3_placeholder_x, y - 25, f"ESO {axis} z3 feedback tap")
    beta2_term = gain(model, f"ESO_{axis}_beta2_innovation", innovation, beta2, -5, y + 35, f"ESO {axis}: 3*w_o^2 innovation")
    z2_pre = sum_ports(model, f"ESO_{axis}_z2_plus_z3", [z3, base_command], "++", 70, y + 35, f"ESO {axis}: z3 + b0*u0")
    z2_dot = sum_ports(model, f"ESO_{axis}_z2_dot", [z2_pre, beta2_term], "++", 145, y + 35, f"ESO {axis}: z3 + b0*u0 + beta2 innovation")
    z2_state = integrator(model, f"ESO_{axis}_z2_state", z2_dot, 220, y + 35, f"ESO {axis} continuous state z2")
    beta3_term = gain(model, f"ESO_{axis}_beta3_innovation", innovation, beta3, 70, y - 100, f"ESO {axis}: w_o^3 innovation")
    z3_state = integrator(model, f"ESO_{axis}_z3_state", beta3_term, 145, y - 100, f"ESO {axis} continuous state z3")
    # Feed the visible delay taps from the continuous states.  A unit delay is
    # used solely as a graphical feedback break at 100 Hz, matching the model's
    # outer control sample group while retaining the three continuous ESO states.
    connect(model, z1_state, f"ESO_{axis}_z1_feedback.u1")
    connect(model, z2_state, f"ESO_{axis}_z2_feedback.u1")
    connect(model, z3_state, f"ESO_{axis}_z3_feedback.u1")
    scaled = gain(model, f"ESO_{axis}_disturbance_over_b0", z3_state, 1.0, 300, y - 100, f"ESO {axis}: z3 / b0")
    return saturation(model, f"ESO_{axis}_comp_limit", scaled, -limit, limit, 390, y - 100, f"ESO {axis} bounded disturbance compensation")


def build() -> dict[str, object]:
    if ModelingPy.ClassExist(MODEL_NAME):
        if not ModelingPy.EraseClasses((MODEL_NAME,)):
            raise RuntimeError(f"EraseClasses failed: {MODEL_NAME}")
    if not ModelingPy.NewModel(
        MODEL_NAME,
        "Sysblock",
        "AWFF base controller with x/y/z third-order linear ESO and rotor mixer",
    ):
        raise RuntimeError(f"NewModel failed: {MODEL_NAME}")
    if not ModelingPy.OpenModel(MODEL_NAME, "diagram"):
        raise RuntimeError(f"OpenModel failed: {MODEL_NAME}")

    x_error = source(MODEL_NAME, "x_position_error", -760, 330, "x position error")
    y_error = source(MODEL_NAME, "y_position_error", -760, 105, "y position error")
    z_error = source(MODEL_NAME, "z_position_error", -760, -175, "z position error")
    z_ref_rate = source(MODEL_NAME, "z_reference_rate", -760, -260, "z reference velocity feedforward")

    x_base = awff_xy(MODEL_NAME, "x", x_error, 330)
    y_base = awff_xy(MODEL_NAME, "y", y_error, 95)
    z_base = awff_z(MODEL_NAME, z_error, z_ref_rate, -175)

    x_comp = eso_axis(MODEL_NAME, "x", x_error, x_base, 300, 3.0, 0.06)
    y_comp = eso_axis(MODEL_NAME, "y", y_error, y_base, 45, 3.0, 0.06)
    z_comp = eso_axis(MODEL_NAME, "z", z_error, z_base, -215, 2.0, 1.0)

    pitch_raw = sum_ports(MODEL_NAME, "pitch_base_minus_eso", [x_base, x_comp], "+-", 485, 300, "pitch base command minus ESO compensation")
    roll_raw = sum_ports(MODEL_NAME, "roll_base_minus_eso", [y_base, y_comp], "+-", 485, 45, "roll base command minus ESO compensation")
    thrust_raw = sum_ports(MODEL_NAME, "thrust_base_minus_eso", [z_base, z_comp], "+-", 485, -215, "thrust base command minus ESO compensation")
    pitch = saturation(MODEL_NAME, "pitch_command_limit", pitch_raw, -12.0 / 57.3, 12.0 / 57.3, 575, 300, "pitch command limit")
    roll = saturation(MODEL_NAME, "roll_command_limit", roll_raw, -12.0 / 57.3, 12.0 / 57.3, 575, 45, "roll command limit")
    thrust = saturation(MODEL_NAME, "thrust_command_limit", thrust_raw, -20.0, 20.0, 575, -215, "collective thrust command limit")
    yaw_zero = constant(MODEL_NAME, "yaw_command_zero", 0.0, 575, -65, "zero yaw command for the displayed mixer path")

    rotor_1_raw = sum_ports(MODEL_NAME, "mixer_rotor_1", [thrust, roll, pitch, yaw_zero], "++--", 700, 240, "rotor 1: thrust + roll - pitch - yaw")
    rotor_2_inner = sum_ports(MODEL_NAME, "mixer_rotor_2_inner", [thrust, roll, pitch, yaw_zero], "+--+", 700, 120, "rotor 2 inner mixer")
    rotor_2_raw = gain(MODEL_NAME, "mixer_rotor_2_negate", rotor_2_inner, -1.0, 820, 120, "rotor 2 sign convention")
    rotor_3_raw = sum_ports(MODEL_NAME, "mixer_rotor_3", [thrust, roll, pitch, yaw_zero], "+-+-", 700, 0, "rotor 3: thrust - roll + pitch - yaw")
    rotor_4_inner = sum_ports(MODEL_NAME, "mixer_rotor_4_inner", [thrust, roll, pitch, yaw_zero], "++++", 700, -120, "rotor 4 inner mixer")
    rotor_4_raw = gain(MODEL_NAME, "mixer_rotor_4_negate", rotor_4_inner, -1.0, 820, -120, "rotor 4 sign convention")
    rotor_1 = saturation(MODEL_NAME, "rotor_1_limit", rotor_1_raw, -20.0, 20.0, 910, 240, "rotor 1 output limit")
    rotor_2 = saturation(MODEL_NAME, "rotor_2_limit", rotor_2_raw, -20.0, 20.0, 910, 120, "rotor 2 output limit")
    rotor_3 = saturation(MODEL_NAME, "rotor_3_limit", rotor_3_raw, -20.0, 20.0, 910, 0, "rotor 3 output limit")
    rotor_4 = saturation(MODEL_NAME, "rotor_4_limit", rotor_4_raw, -20.0, 20.0, 910, -120, "rotor 4 output limit")
    output(MODEL_NAME, "rotor_1", 1020, 240, rotor_1, "rotor 1 command")
    output(MODEL_NAME, "rotor_2", 1020, 120, rotor_2, "rotor 2 command")
    output(MODEL_NAME, "rotor_3", 1020, 0, rotor_3, "rotor 3 command")
    output(MODEL_NAME, "rotor_4", 1020, -120, rotor_4, "rotor 4 command")

    # Sysplorer exports a top-level class first. Promote that native export into
    # the active Sysblocks package, while keeping Results limited to evidence.
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.joinpath("screenshots").mkdir(parents=True, exist_ok=True)
    target_model = MODEL_DIR / f"{MODEL_NAME}.mo"
    target_model.unlink(missing_ok=True)
    if not ModelingPy.SaveModelAs(MODEL_NAME, str(MODEL_DIR), MODEL_NAME):
        raise RuntimeError(f"SaveModelAs failed: {target_model}")
    if not ModelingPy.CheckModel(MODEL_NAME):
        errors = list(ModelingPy.GetLastErrors())
        raise RuntimeError(f"CheckModel failed: {errors}")
    if not ModelingPy.ExportDiagram(MODEL_NAME, str(DIAGRAM_PATH), 3200, 1800):
        raise RuntimeError(f"ExportDiagram failed: {DIAGRAM_PATH}")
    promote_to_model_library(target_model)

    model_text = str(ModelingPy.GetModelText(MODEL_NAME))
    manifest = {
        "schema": "mosim.pid_awff_linear_eso_graphical_build.v1",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_name": MODEL_NAME,
        "model_source": str(CANONICAL_MODEL_PATH.relative_to(ROOT)).replace("\\", "/"),
        "model_source_sha256": sha256(CANONICAL_MODEL_PATH),
        "equation_source": str(SOURCE_EQUATION.relative_to(ROOT)).replace("\\", "/"),
        "equation_source_sha256": sha256(SOURCE_EQUATION),
        "diagram": str(DIAGRAM_PATH.relative_to(ROOT)).replace("\\", "/"),
        "diagram_sha256": sha256(DIAGRAM_PATH),
        "saved": True,
        "check_model": True,
        "component_count": len(list(ModelingPy.GetComponents(MODEL_NAME))),
        "connect_count": model_text.count("connect("),
        "line_annotation_count": model_text.count("annotation(Line"),
        "required_signal_chain": [
            "position error",
            "AWFF base control",
            "x/y/z third-order ESO",
            "bounded disturbance compensation",
            "base command minus compensation",
            "attitude/thrust command limits",
            "four-rotor mixer",
        ],
        "claim_boundary": (
            "This artifact is an independently CheckModel-passed graphical controller-core view of the active equation source. "
            "It does not modify the existing Adapter, FormalRunner, or retained 50 s numerical record."
        ),
    }
    with MANIFEST_PATH.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    target_model.unlink(missing_ok=True)
    try:
        MODEL_DIR.rmdir()
    except OSError:
        pass
    return manifest


RUN_SCRIPT_RESULT = build()
