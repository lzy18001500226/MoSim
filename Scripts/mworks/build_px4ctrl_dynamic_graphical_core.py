#!/usr/bin/env python3
"""Rebuild the Px4Ctrl native Sysblock core with the full dynamic input contract.

The model is authored through ModelingPy so the saved ``.mo`` contains real
Sysblock components and graphical ``ConnectPort`` wires.  The only text
normalization below updates generated display metadata after the API build.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
MODEL_NAME = "MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlBaselineCore"
SHORT_NAME = "Px4CtrlBaselineCore"
TARGET = ROOT / "Models/MoSimQuadrotorModel/Control/Px4Ctrl/Px4CtrlBaselineCore.mo"
EVIDENCE_DIR = ROOT / "Results/model_checks/px4ctrl_dynamic_repair_20260816"
PACKAGE = "MoSimQuadrotorModel.Control.Px4Ctrl"

INPORT = "SysplorerEmbeddedCoder.Port.Inport"
OUTPORT = "SysplorerEmbeddedCoder.Port.Outport"
SUM = "SysplorerEmbeddedCoder.MathOperation.Sum"
GAIN = "SysplorerEmbeddedCoder.MathOperation.Gain"
DIFFERENCE = "SysplorerEmbeddedCoder.Discrete.Difference"
UNIT_DELAY = "SysplorerEmbeddedCoder.Discrete.UnitDelay"
SATURATION = "SysplorerEmbeddedCoder.Discontinuities.Saturation"
CONSTANT = "SysplorerEmbeddedCoder.Sources.Constant"
# Sysplorer registers the loaded outer-loop Sysblock under its package class.
OUTER_LOOP = "MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlOuterLoopGraphicalSysblock"

SAMPLE_TIME_S = 0.01
DERIVATIVE_DECAY = 0.368160727285504
GRAVITY = 9.80665

INPUTS = [
    "x_ref",
    "y_ref",
    "z_ref",
    "vx_ref",
    "vy_ref",
    "vz_ref",
    "ax_ref",
    "ay_ref",
    "az_ref",
    "x_mea",
    "y_mea",
    "z_mea",
    "vx_mea",
    "vy_mea",
    "vz_mea",
    "roll_mea",
    "pitch_mea",
    "yaw_mea",
]
OUTPUTS = ["y", "y1", "y2", "y3"]


def _add(
    model_name: str,
    type_name: str,
    component: str,
    x: float,
    y: float,
    width: float = 34,
    height: float = 26,
) -> None:
    if not ModelingPy.AddComponent(type_name, model_name, component, x, y, width, height):
        raise RuntimeError(f"AddComponent failed: {model_name}.{component} ({type_name})")


def _set_param(component: str, parameter: str, value: object) -> None:
    encoded = f'"{value}"' if parameter == "inputs" else str(value)
    if not ModelingPy.SetParamValue(f"{component}.{parameter}", encoded):
        raise RuntimeError(f"SetParamValue failed: {component}.{parameter}={encoded}")


def _wire(model_name: str, source: str, target: str) -> None:
    if not ModelingPy.ConnectPort(model_name, source, target):
        raise RuntimeError(f"ConnectPort failed: {source} -> {target}")


def _open_empty_core() -> str:
    if ModelingPy.ClassExist(MODEL_NAME):
        model_name = MODEL_NAME
    elif ModelingPy.ClassExist(SHORT_NAME):
        model_name = SHORT_NAME
    else:
        if not ModelingPy.NewModel(
            SHORT_NAME,
            "Sysblock",
            "Native graphical px4ctrl dynamic controller core",
        ):
            raise RuntimeError(f"NewModel failed: {SHORT_NAME}")
        model_name = SHORT_NAME
    if not ModelingPy.OpenModel(model_name, "diagram"):
        raise RuntimeError(f"OpenModel failed: {model_name}")
    for component in list(ModelingPy.GetComponents(model_name)):
        if not ModelingPy.RemoveComponent(model_name, component):
            raise RuntimeError(f"RemoveComponent failed: {model_name}.{component}")
    return model_name


def _add_filtered_derivative(model_name: str, axis: str, x: float, y: float) -> str:
    """Create the existing visible 100 Hz attitude-rate estimate."""

    difference = f"{axis}_derivative_difference"
    slope = f"{axis}_derivative_slope"
    increment = f"{axis}_derivative_increment"
    previous = f"{axis}_derivative_previous_state"
    decay = f"{axis}_derivative_decay"
    state = f"{axis}_derivative_state"
    gain = f"{axis}_derivative_gain"

    _add(model_name, DIFFERENCE, difference, x - 90, y)
    _add(model_name, GAIN, slope, x - 25, y)
    _set_param(slope, "k", 1.0 / SAMPLE_TIME_S)
    _add(model_name, GAIN, increment, x + 40, y - 35)
    _set_param(increment, "k", 1.0 - DERIVATIVE_DECAY)
    _add(model_name, UNIT_DELAY, previous, x + 40, y + 35)
    _set_param(previous, "initCond", 0.0)
    _add(model_name, GAIN, decay, x + 105, y + 35)
    _set_param(decay, "k", DERIVATIVE_DECAY)
    _add(model_name, SUM, state, x + 170, y)
    _add(model_name, GAIN, gain, x + 235, y)
    _set_param(gain, "k", 1.414)

    _wire(model_name, f"{difference}.y", f"{slope}.u")
    _wire(model_name, f"{slope}.y", f"{increment}.u")
    _wire(model_name, f"{increment}.y", f"{state}.u2")
    _wire(model_name, f"{previous}.y", f"{decay}.u")
    _wire(model_name, f"{decay}.y", f"{state}.u1")
    _wire(model_name, f"{state}.y", f"{previous}.u1")
    _wire(model_name, f"{state}.y", f"{gain}.u")
    return difference


def _normalize_generated_metadata(text: str) -> str:
    arrangement = "PortArrangement(Left(" + ", ".join(INPUTS) + "), Right(" + ", ".join(OUTPUTS) + "))"
    text = re.sub(
        r"PortArrangement\(Left\([^)]*\),\s*Right\([^)]*\)\)",
        arrangement,
        text,
    )
    text = re.sub(r"OutputInterval\s*=\s*0\.02", "OutputInterval=0.01", text)
    text = text.replace(
        "SampleTime(auto=true)",
        'SampleTime(auto=true,group="")=0.01',
    )
    text = text.replace(
        "experiment(Algorithm=Euler,Interval=-1)",
        "experiment(Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=50,StoreEventValue=0)",
    )
    text = re.sub(r"^\s*within\s+[^;]+;\s*", "", text, flags=re.MULTILINE)
    return text


def build() -> dict:
    model_name = _open_empty_core()
    current_directory = str(ModelingPy.GetDirectory())

    for index, name in enumerate(INPUTS):
        _add(model_name, INPORT, name, -690, 360 - index * 42, 28, 20)
    for index, name in enumerate(OUTPUTS):
        _add(model_name, OUTPORT, name, 560, 180 - index * 120, 28, 20)

    # This child is itself a native Sysblock. It preserves all P, D, and
    # acceleration-feed-forward paths visibly instead of recreating them in
    # Modelica equations at the runner boundary.
    _add(model_name, OUTER_LOOP, "outer_loop", -370, 20, 190, 280)
    for axis in ("x", "y", "z"):
        _wire(model_name, f"{axis}_ref", f"outer_loop.ref_p_{axis}")
        _wire(model_name, f"{axis}_mea", f"outer_loop.mea_p_{axis}")
        _wire(model_name, f"v{axis}_ref", f"outer_loop.ref_v_{axis}")
        _wire(model_name, f"v{axis}_mea", f"outer_loop.mea_v_{axis}")
        _wire(model_name, f"a{axis}_ref", f"outer_loop.ref_a_{axis}")

    _add(model_name, GAIN, "pitch_reference_scale", -120, 220)
    _set_param("pitch_reference_scale", "k", 1.0 / GRAVITY)
    _add(model_name, GAIN, "roll_reference_scale", -120, 130)
    _set_param("roll_reference_scale", "k", 1.0 / GRAVITY)
    _add(model_name, CONSTANT, "z_gravity_offset", -115, 20)
    _set_param("z_gravity_offset", "k", -GRAVITY)
    _add(model_name, SUM, "z_collective_delta", -35, 20)
    _wire(model_name, "outer_loop.desired_acc_x", "pitch_reference_scale.u")
    _wire(model_name, "outer_loop.desired_acc_y", "roll_reference_scale.u")
    _wire(model_name, "outer_loop.desired_acc_z", "z_collective_delta.u1")
    _wire(model_name, "z_gravity_offset.y", "z_collective_delta.u2")

    _add(model_name, SUM, "roll_error", 10, 155)
    _add(model_name, GAIN, "roll_measurement_sign", -75, 115)
    # The former "+-" Sum received a negated measurement.  A default binary
    # Sum plus this explicit gain preserves the same net roll convention.
    _set_param("roll_measurement_sign", "k", 1.0)
    _add(model_name, GAIN, "roll_attitude_gain", 95, 155)
    _set_param("roll_attitude_gain", "k", 14.142)
    _add(model_name, SUM, "roll_pd", 340, 155)
    _add(model_name, SATURATION, "roll_limit", 410, 155)
    _set_param("roll_limit", "upLimit", 7.0)
    _set_param("roll_limit", "lowLimit", -7.0)
    _add(model_name, GAIN, "roll_mix", 475, 155)
    _set_param("roll_mix", "k", 0.707)
    roll_derivative_input = _add_filtered_derivative(model_name, "roll", 105, 80)
    _wire(model_name, "roll_reference_scale.y", "roll_error.u1")
    _wire(model_name, "roll_mea", "roll_measurement_sign.u")
    _wire(model_name, "roll_measurement_sign.y", "roll_error.u2")
    _wire(model_name, "roll_error.y", "roll_attitude_gain.u")
    _wire(model_name, "roll_mea", f"{roll_derivative_input}.u")
    _wire(model_name, "roll_attitude_gain.y", "roll_pd.u1")
    _wire(model_name, "roll_derivative_gain.y", "roll_pd.u2")
    _wire(model_name, "roll_pd.y", "roll_limit.u")
    _wire(model_name, "roll_limit.y", "roll_mix.u")

    _add(model_name, SUM, "pitch_error", 10, 60)
    _add(model_name, GAIN, "pitch_measurement_sign", -75, 20)
    _set_param("pitch_measurement_sign", "k", -1.0)
    _add(model_name, GAIN, "pitch_attitude_gain", 95, 60)
    _set_param("pitch_attitude_gain", "k", 14.142)
    _add(model_name, SUM, "pitch_pd", 340, 60)
    _add(model_name, SATURATION, "pitch_limit", 410, 60)
    _set_param("pitch_limit", "upLimit", 7.0)
    _set_param("pitch_limit", "lowLimit", -7.0)
    _add(model_name, GAIN, "pitch_mix", 475, 60)
    _set_param("pitch_mix", "k", 0.707)
    pitch_derivative_input = _add_filtered_derivative(model_name, "pitch", 105, -20)
    _wire(model_name, "pitch_reference_scale.y", "pitch_error.u1")
    _wire(model_name, "pitch_mea", "pitch_measurement_sign.u")
    _wire(model_name, "pitch_measurement_sign.y", "pitch_error.u2")
    _wire(model_name, "pitch_mea", f"{pitch_derivative_input}.u")
    _wire(model_name, "pitch_error.y", "pitch_attitude_gain.u")
    _wire(model_name, "pitch_attitude_gain.y", "pitch_pd.u1")
    _wire(model_name, "pitch_derivative_gain.y", "pitch_pd.u2")
    _wire(model_name, "pitch_pd.y", "pitch_limit.u")
    _wire(model_name, "pitch_limit.y", "pitch_mix.u")

    _add(model_name, CONSTANT, "yaw_reference", -115, -130)
    _set_param("yaw_reference", "k", 0.0)
    _add(model_name, SUM, "yaw_error", 10, -130)
    _add(model_name, GAIN, "yaw_measurement_sign", -75, -170)
    _set_param("yaw_measurement_sign", "k", -1.0)
    _add(model_name, GAIN, "yaw_attitude_gain", 95, -130)
    _set_param("yaw_attitude_gain", "k", 5.0)
    _add(model_name, SATURATION, "yaw_limit", 230, -130)
    _set_param("yaw_limit", "upLimit", 7.0)
    _set_param("yaw_limit", "lowLimit", -7.0)
    _add(model_name, GAIN, "yaw_mix", 300, -130)
    _set_param("yaw_mix", "k", 0.707)
    _wire(model_name, "yaw_reference.y", "yaw_error.u1")
    _wire(model_name, "yaw_mea", "yaw_measurement_sign.u")
    _wire(model_name, "yaw_measurement_sign.y", "yaw_error.u2")
    _wire(model_name, "yaw_error.y", "yaw_attitude_gain.u")
    _wire(model_name, "yaw_attitude_gain.y", "yaw_limit.u")
    _wire(model_name, "yaw_limit.y", "yaw_mix.u")

    # Sum blocks created by the current official API expose two inputs. Build
    # the four-term mixer as an explicit binary tree so all signs and paths
    # remain visible and queryable in the final Sysblock diagram.
    mixer_signs = [
        (1.0, -1.0, -1.0),
        (-1.0, -1.0, 1.0),
        (-1.0, 1.0, -1.0),
        (1.0, 1.0, 1.0),
    ]
    for index, (roll_sign, pitch_sign, yaw_sign) in enumerate(mixer_signs, start=1):
        y = 180 - (index - 1) * 120
        first = f"mixer_{index}_first"
        second = f"mixer_{index}_second"
        mixer = f"mixer_{index}"
        limit = f"amplitude_limit_{index}"
        sign = f"rotor_{index}_sign"
        for axis, gain_value, source, offset in (
            ("roll", roll_sign, "roll_mix.y", 35),
            ("pitch", pitch_sign, "pitch_mix.y", 0),
            ("yaw", yaw_sign, "yaw_mix.y", -35),
        ):
            component = f"mixer_{index}_{axis}_sign"
            _add(model_name, GAIN, component, 560, y + offset)
            _set_param(component, "k", gain_value)
            _wire(model_name, source, f"{component}.u")
        _add(model_name, SUM, first, 640, y + 20)
        _add(model_name, SUM, second, 710, y)
        _add(model_name, SUM, mixer, 780, y)
        _add(model_name, SATURATION, limit, 855, y)
        _set_param(limit, "upLimit", 200.0)
        _set_param(limit, "lowLimit", -200.0)
        _add(model_name, GAIN, sign, 920, y)
        _set_param(sign, "k", 1.0 if index in (1, 3) else -1.0)
        _wire(model_name, f"mixer_{index}_roll_sign.y", f"{first}.u1")
        _wire(model_name, f"mixer_{index}_pitch_sign.y", f"{first}.u2")
        _wire(model_name, f"{first}.y", f"{second}.u1")
        _wire(model_name, f"mixer_{index}_yaw_sign.y", f"{second}.u2")
        _wire(model_name, f"{second}.y", f"{mixer}.u1")
        _wire(model_name, "z_collective_delta.y", f"{mixer}.u2")
        _wire(model_name, f"{mixer}.y", f"{limit}.u")
        _wire(model_name, f"{limit}.y", f"{sign}.u")
        _wire(model_name, f"{sign}.y", OUTPUTS[index - 1])

    checked = bool(ModelingPy.CheckModel(model_name))
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    diagram_path = EVIDENCE_DIR / "Px4CtrlBaselineCore_dynamic_api.png"
    exported = bool(ModelingPy.ExportDiagram(model_name, str(diagram_path), 2600, 1800))
    generated = _normalize_generated_metadata(str(ModelingPy.GetModelText(model_name)))
    target_source = f"within {PACKAGE};\n" + generated.lstrip()
    TARGET.write_text(target_source, encoding="utf-8")
    staging_dir = EVIDENCE_DIR / "api_generated_source"
    staging_dir.mkdir(parents=True, exist_ok=True)
    staging_path = staging_dir / "Px4CtrlBaselineCore.mo"
    staging_path.write_text(target_source, encoding="utf-8")

    components = list(ModelingPy.GetComponents(model_name))
    manifest = {
        "schema": "mosim.px4ctrl_dynamic_graphical_core_api_build.v1",
        "source": "official ModelingPy NewModel/AddComponent/SetParamValue/ConnectPort",
        "model_name": model_name,
        "model_path": str(TARGET),
        "staging_model_path": str(staging_path),
        "diagram_path": str(diagram_path),
        "check_model": checked,
        "exported": exported,
        "current_directory": current_directory,
        "input_contract": INPUTS,
        "output_contract": OUTPUTS,
        "required_graphical_components": [
            "outer_loop",
            "z_collective_delta",
            "roll_pd",
            "pitch_pd",
            "mixer_1",
            "mixer_2",
            "mixer_3",
            "mixer_4",
        ],
        "component_count": len(components),
        "connection_count": len(re.findall(r"\bconnect\s*\(", generated)),
        "line_annotation_count": len(re.findall(r"annotation\s*\(\s*Line\b", generated)),
        "claim_boundary": "API-authored graphical Sysblock topology; runner-level and closed-loop behavior evidence remain separate.",
    }
    (EVIDENCE_DIR / "Px4CtrlBaselineCore_dynamic_api_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


RUN_SCRIPT_RESULT = build()
