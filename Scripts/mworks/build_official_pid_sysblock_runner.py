#!/usr/bin/env python3
"""Build the native graphical Official PID Sysblock route through ModelingPy."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
MODEL_DIR = (
    ROOT
    / "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID"
)
EVIDENCE_DIR = (
    ROOT
    / "Results/mworks_live_gate/official_pid_sysblock_runner_20260805"
    / "resume_1625"
)

INPORT = "SysplorerEmbeddedCoder.Port.Inport"
OUTPORT = "SysplorerEmbeddedCoder.Port.Outport"
SUM = "SysplorerEmbeddedCoder.MathOperation.Sum"
GAIN = "SysplorerEmbeddedCoder.MathOperation.Gain"
DIFFERENCE = "SysplorerEmbeddedCoder.Discrete.Difference"
UNIT_DELAY = "SysplorerEmbeddedCoder.Discrete.UnitDelay"
INTEGRATOR = "SysplorerEmbeddedCoder.Continuous.Integrator"
SATURATION = "SysplorerEmbeddedCoder.Discontinuities.Saturation"
CONSTANT = "SysplorerEmbeddedCoder.Sources.Constant"

GRAPHICAL_PACKAGE = (
    "MoSimQuadrotorModel.Control.Implementations.Graphical.PID"
)
PROFILE_CONSTANTS = {
    "hover_speed_rad_s": 64.7923778389665,
    "legacy_hover_speed_rad_s": 13.985413115099604,
    "moment_constant_ratio_m": 0.06,
    "embedded_yaw_authority_reference_ratio": 0.016,
    "spin_command_sign": [1, -1, 1, -1],
    "yaw_pattern": [-1, 1, -1, 1],
}
SAMPLE_TIME_S = 0.01
DERIVATIVE_TIME_CONSTANT_S = 0.01
# The Formal runner's MWORKS sampled Derivative gives this effective decay at
# h=T=0.01 s; keep the calibration explicit instead of changing PID gains.
DERIVATIVE_DECAY = 0.368160727285504
DERIVATIVE_PROVENANCE = {
    "source": "MWORKS Formal Derivative(T=0.01) sampled at t=0.01",
    "evidence": "Results/mworks_live_gate/official_pid_sysblock_runner_20260805/resume_1625/current_continuation/behavior/formal_discrete_comparison",
    "sample_time_s": SAMPLE_TIME_S,
    "time_constant_s": DERIVATIVE_TIME_CONSTANT_S,
    "decay": DERIVATIVE_DECAY,
    "increment": 1.0 - DERIVATIVE_DECAY,
    "ideal_continuous_decay": math.exp(-SAMPLE_TIME_S / DERIVATIVE_TIME_CONSTANT_S),
}


def _normalize_generated_metadata(text: str) -> str:
    """Normalize API defaults without changing generated topology."""

    text = re.sub(r"OutputInterval\s*=\s*0\.02", "OutputInterval=0.01", text)
    text = text.replace(
        "SampleTime(auto=true)", 'SampleTime(auto=true,group="")=0.01'
    )
    text = text.replace(
        "experiment(Algorithm=Euler,Interval=-1)",
        "experiment(Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=50,StoreEventValue=0)",
    )
    return text


def _open_empty_model(model_name: str, description: str) -> str:
    full_name = f"{GRAPHICAL_PACKAGE}.{model_name}"
    actual_name = model_name
    if ModelingPy.ClassExist(full_name):
        actual_name = full_name
    elif not ModelingPy.ClassExist(model_name):
        created = ModelingPy.NewModel(model_name, "Sysblock", description)
        if not created:
            raise RuntimeError(f"NewModel failed: {model_name}")
    if not ModelingPy.OpenModel(actual_name, "diagram"):
        raise RuntimeError(f"OpenModel failed: {actual_name}")
    for component in list(ModelingPy.GetComponents(actual_name)):
        if not ModelingPy.RemoveComponent(actual_name, component):
            raise RuntimeError(f"RemoveComponent failed: {actual_name}.{component}")
    return actual_name


def _component_type(short_name: str) -> str:
    full_name = f"{GRAPHICAL_PACKAGE}.{short_name}"
    return full_name if ModelingPy.ClassExist(full_name) else short_name


def _add(
    model_name: str,
    type_name: str,
    component: str,
    x: float,
    y: float,
    width: float = 34,
    height: float = 26,
) -> None:
    if not ModelingPy.AddComponent(
        type_name, model_name, component, x, y, width, height
    ):
        raise RuntimeError(
            f"AddComponent failed: {model_name}.{component} ({type_name})"
        )


def _set_param(component: str, parameter: str, value: object) -> None:
    encoded = f'"{value}"' if parameter == "inputs" else str(value)
    if not ModelingPy.SetParamValue(f"{component}.{parameter}", encoded):
        raise RuntimeError(
            f"SetParamValue failed: {component}.{parameter}={encoded}"
        )


def _wire(model_name: str, source: str, target: str) -> None:
    if not ModelingPy.ConnectPort(model_name, source, target):
        raise RuntimeError(f"ConnectPort failed: {source} -> {target}")


def _add_filtered_derivative(
    model_name: str, component: str, x: float, y: float
) -> str:
    """Build a visible sampled high-pass derivative matching Formal Derivative."""

    # Sysblock TransferFcn currently evaluates this numerator/denominator pair
    # as an ideal sampled difference. Keep the filter state explicit so the
    # generated graph has the same first-order high-pass behavior as the
    # Modelica Derivative block used by the Formal reference.
    input_block = f"{component}_input"
    difference = f"{component}_difference"
    slope = f"{component}_slope"
    increment = f"{component}_filtered_increment"
    previous_state = f"{component}_previous_state"
    state_decay = f"{component}_state_decay"
    state_sum = f"{component}_state_sum"

    _add(model_name, GAIN, input_block, x - 80, y)
    _set_param(input_block, "k", 1.0)
    _add(model_name, DIFFERENCE, difference, x - 20, y)
    _add(model_name, GAIN, slope, x + 40, y)
    _set_param(slope, "k", 1.0 / SAMPLE_TIME_S)
    _add(model_name, GAIN, increment, x + 100, y - 30)
    _set_param(increment, "k", 1.0 - DERIVATIVE_DECAY)
    _add(model_name, UNIT_DELAY, previous_state, x + 100, y + 30)
    _set_param(previous_state, "initCond", 0.0)
    _add(model_name, GAIN, state_decay, x + 160, y + 30)
    _set_param(state_decay, "k", DERIVATIVE_DECAY)
    _add(model_name, SUM, state_sum, x + 220, y)
    _set_param(state_sum, "inputs", "++")
    _add(model_name, GAIN, component, x + 280, y)
    _set_param(component, "k", 1.0)

    _wire(model_name, f"{input_block}.y", f"{difference}.u")
    _wire(model_name, f"{difference}.y", f"{slope}.u")
    _wire(model_name, f"{slope}.y", f"{increment}.u")
    _wire(model_name, f"{increment}.y", f"{state_sum}.u2")
    _wire(model_name, f"{previous_state}.y", f"{state_decay}.u")
    _wire(model_name, f"{state_decay}.y", f"{state_sum}.u1")
    _wire(model_name, f"{state_sum}.y", f"{previous_state}.u1")
    _wire(model_name, f"{state_sum}.y", f"{component}.u")
    return input_block


def _save_and_evidence(
    model_name: str,
    model_dir: Path,
    evidence_dir: Path,
    within_package: str,
) -> dict:
    model_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    model_stem = model_name.rsplit(".", 1)[-1]
    target = model_dir / f"{model_stem}.mo"
    api_staging_dir = evidence_dir / "api_generated_source"
    api_staging_dir.mkdir(parents=True, exist_ok=True)
    api_staging_target = api_staging_dir / f"{model_stem}.mo"
    saved = (
        ModelingPy.SaveModel(model_name)
        if target.exists()
        else ModelingPy.SaveModelAs(
            model_name, str(api_staging_dir), model_stem
        )
    )
    if saved:
        generated_text = str(ModelingPy.GetModelText(model_name))
        # NewModel defaults to 0.02; align generated Sysblock output timing
        # with the Formal runner's 0.01-second comparison interval.
        generated_text = _normalize_generated_metadata(generated_text)
        api_staging_target.write_text(generated_text, encoding="utf-8")
        target.write_text(
            f"within {within_package};\n" + generated_text.lstrip(),
            encoding="utf-8",
        )
    diagram = evidence_dir / f"{model_name}.png"
    exported = ModelingPy.ExportDiagram(model_name, str(diagram), 2400, 1600)
    checked = ModelingPy.CheckModel(model_name)
    if saved:
        # CheckModel may refresh the generated source from the in-memory model.
        # Reapply this annotation-only normalization after the API gates.
        target.write_text(
            f"within {within_package};\n" + generated_text.lstrip(),
            encoding="utf-8",
        )
    components = list(ModelingPy.GetComponents(model_name))
    model_text = str(ModelingPy.GetModelText(model_name))
    ports = {
        component: list(ModelingPy.GetComponentPorts(model_name, component, 0))
        for component in components
    }
    manifest = {
        "schema": "mosim.official_pid_sysblock_api_build.v1",
        "source": (
            "official ModelingPy NewModel/AddComponent/SetParamValue/ConnectPort"
        ),
        "model_name": model_name,
        "model_path": str(target),
        "api_staging_model_path": str(api_staging_target),
        "diagram_path": str(diagram),
        "saved": bool(saved),
        "exported": bool(exported),
        "check_model": bool(checked),
        "component_count": len(components),
        "connection_count": len(re.findall(r"\bconnect\s*\(", model_text)),
        "line_annotation_count": len(
            re.findall(r"annotation\s*\(\s*Line\b", model_text)
        ),
        "ports": ports,
        "claim_boundary": (
            "API-generated Sysblock topology; reload and behavior gates are separate."
        ),
    }
    (evidence_dir / f"{model_name}_build_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def build_core() -> dict:
    model_name = _open_empty_model(
        "OfficialPidSysblockCore", "Official PID native graphical controller core"
    )

    for index, name in enumerate(
        [
            "x_ref",
            "y_ref",
            "z_ref",
            "x_mea",
            "y_mea",
            "z_mea",
            "roll_mea",
            "pitch_mea",
            "yaw_mea",
        ]
    ):
        _add(model_name, INPORT, name, -560, 260 - index * 58)
    for index, name in enumerate(["y", "y1", "y2", "y3"]):
        _add(model_name, OUTPORT, name, 430, 180 - index * 120)

    for axis, reference, measurement, y, attitude_axis in [
        ("x", "x_ref", "x_mea", 260, "pitch"),
        ("y", "y_ref", "y_mea", 120, "roll"),
    ]:
        _add(model_name, SUM, f"{axis}_error", -480, y)
        _set_param(f"{axis}_error", "inputs", "+-")
        _add(model_name, GAIN, f"{axis}_p", -400, y + 35)
        _set_param(f"{axis}_p", "k", 1.5)
        derivative_input = _add_filtered_derivative(
            model_name, f"{axis}_derivative", -400, y - 35
        )
        _add(model_name, GAIN, f"{axis}_d", -320, y - 35)
        _set_param(f"{axis}_d", "k", 1.0)
        _add(model_name, SUM, f"{axis}_pd", -240, y)
        _set_param(f"{axis}_pd", "inputs", "++")
        _add(model_name, GAIN, f"{attitude_axis}_ref_scale", -160, y)
        _set_param(f"{attitude_axis}_ref_scale", "k", 0.1)
        _add(model_name, SATURATION, f"{attitude_axis}_ref_limit", -80, y)
        _set_param(f"{attitude_axis}_ref_limit", "upLimit", 15.0 / 57.3)
        _set_param(f"{attitude_axis}_ref_limit", "lowLimit", -15.0 / 57.3)

        _wire(model_name, reference, f"{axis}_error.u1")
        _wire(model_name, measurement, f"{axis}_error.u2")
        _wire(model_name, f"{axis}_error.y", f"{axis}_p.u")
        _wire(model_name, f"{axis}_error.y", f"{derivative_input}.u")
        _wire(model_name, f"{axis}_derivative.y", f"{axis}_d.u")
        _wire(model_name, f"{axis}_p.y", f"{axis}_pd.u1")
        _wire(model_name, f"{axis}_d.y", f"{axis}_pd.u2")
        _wire(model_name, f"{axis}_pd.y", f"{attitude_axis}_ref_scale.u")
        _wire(
            model_name,
            f"{attitude_axis}_ref_scale.y",
            f"{attitude_axis}_ref_limit.u",
        )

    _add(model_name, SUM, "z_error", -480, -20)
    _set_param("z_error", "inputs", "+-")
    _add(model_name, GAIN, "z_p", -400, 25)
    _set_param("z_p", "k", 8.0)
    _add(model_name, INTEGRATOR, "z_integral", -400, -20)
    _add(model_name, GAIN, "z_i", -320, -20)
    _set_param("z_i", "k", 6.0)
    z_derivative_input = _add_filtered_derivative(
        model_name, "z_derivative", -400, -65
    )
    _add(model_name, GAIN, "z_d", -320, -65)
    _set_param("z_d", "k", 4.0)
    _add(model_name, SUM, "z_pi", -240, 0)
    _set_param("z_pi", "inputs", "++")
    _add(model_name, SUM, "thrust_command", -160, -15)
    _set_param("thrust_command", "inputs", "++")
    _wire(model_name, "z_ref", "z_error.u1")
    _wire(model_name, "z_mea", "z_error.u2")
    _wire(model_name, "z_error.y", "z_p.u")
    _wire(model_name, "z_error.y", "z_integral.u1")
    _wire(model_name, "z_error.y", f"{z_derivative_input}.u")
    _wire(model_name, "z_integral.y", "z_i.u")
    _wire(model_name, "z_derivative.y", "z_d.u")
    _wire(model_name, "z_p.y", "z_pi.u1")
    _wire(model_name, "z_i.y", "z_pi.u2")
    _wire(model_name, "z_pi.y", "thrust_command.u1")
    _wire(model_name, "z_d.y", "thrust_command.u2")

    _add(model_name, CONSTANT, "yaw_reference", -480, -370)
    _set_param("yaw_reference", "k", 0.0)
    for name, measurement, y, kp in [
        ("pitch", "pitch_mea", -130, 14.142),
        ("roll", "roll_mea", -250, 14.142),
        ("yaw", "yaw_mea", -370, 5.0),
    ]:
        measurement_port = measurement
        if name == "roll":
            _add(model_name, GAIN, "roll_mea_sign", -500, y)
            _set_param("roll_mea_sign", "k", -1)
            _wire(model_name, measurement, "roll_mea_sign.u")
            measurement_port = "roll_mea_sign.y"
        _add(model_name, SUM, f"{name}_error", -420, y)
        _set_param(f"{name}_error", "inputs", "+-")
        _add(model_name, GAIN, f"{name}_p", -340, y + 28)
        _set_param(f"{name}_p", "k", kp)
        if name != "yaw":
            derivative_input = _add_filtered_derivative(
                model_name, f"{name}_derivative", -340, y - 28
            )
            _add(model_name, GAIN, f"{name}_d", -260, y - 28)
            _set_param(f"{name}_d", "k", 1.414)
            _add(model_name, SUM, f"{name}_pd", -180, y)
            _set_param(f"{name}_pd", "inputs", "++")
            _wire(model_name, f"{name}_error.y", f"{derivative_input}.u")
            _wire(model_name, f"{name}_derivative.y", f"{name}_d.u")
            _wire(model_name, f"{name}_p.y", f"{name}_pd.u1")
            _wire(model_name, f"{name}_d.y", f"{name}_pd.u2")
            limit_source = f"{name}_pd.y"
        else:
            limit_source = f"{name}_p.y"
        _add(model_name, SATURATION, f"{name}_limit", -100, y)
        _set_param(f"{name}_limit", "upLimit", 7.0)
        _set_param(f"{name}_limit", "lowLimit", -7.0)
        _add(model_name, GAIN, f"{name}_mix", -20, y)
        _set_param(f"{name}_mix", "k", 0.707)
        _wire(model_name, f"{name}_error.y", f"{name}_p.u")
        _wire(model_name, limit_source, f"{name}_limit.u")
        _wire(model_name, f"{name}_limit.y", f"{name}_mix.u")
        if name == "pitch":
            _wire(model_name, "pitch_ref_limit.y", "pitch_error.u1")
        elif name == "roll":
            _wire(model_name, "roll_ref_limit.y", "roll_error.u1")
        else:
            _wire(model_name, "yaw_reference.y", "yaw_error.u1")
        _wire(model_name, measurement_port, f"{name}_error.u2")

    for index, (signs, y) in enumerate(
        [((-1, -1, 1), 180), ((1, -1, -1), 60), ((-1, 1, -1), -60), ((1, 1, 1), -180)],
        start=1,
    ):
        first_sum = f"mixer_{index}_first"
        mixer = f"mixer_{index}"
        rotor_sum = f"rotor_{index}_sum"
        sign = f"rotor_{index}_sign"
        for axis, source, gain_value, gain_y in [
            ("yaw", "yaw_mix.y", signs[0], y + 35),
            ("pitch", "pitch_mix.y", signs[1], y),
            ("roll", "roll_mix.y", signs[2], y - 35),
        ]:
            gain = f"mixer_{index}_{axis}_gain"
            _add(model_name, GAIN, gain, 55, gain_y)
            _set_param(gain, "k", gain_value)
            _wire(model_name, source, f"{gain}.u")
        _add(model_name, SUM, first_sum, 125, y + 18)
        _set_param(first_sum, "inputs", "++")
        _add(model_name, SUM, mixer, 185, y)
        _set_param(mixer, "inputs", "++")
        _add(model_name, SUM, rotor_sum, 255, y)
        _set_param(rotor_sum, "inputs", "++")
        _add(model_name, GAIN, sign, 335, y)
        _set_param(sign, "k", [1, -1, 1, -1][index - 1])
        _wire(model_name, f"mixer_{index}_yaw_gain.y", f"{first_sum}.u1")
        _wire(model_name, f"mixer_{index}_pitch_gain.y", f"{first_sum}.u2")
        _wire(model_name, f"{first_sum}.y", f"{mixer}.u1")
        _wire(model_name, f"mixer_{index}_roll_gain.y", f"{mixer}.u2")
        _wire(model_name, f"{mixer}.y", f"{rotor_sum}.u1")
        _wire(model_name, "thrust_command.y", f"{rotor_sum}.u2")
        _wire(model_name, f"{rotor_sum}.y", f"{sign}.u")
        _wire(model_name, f"{sign}.y", ["y", "y1", "y2", "y3"][index - 1])

    manifest = _save_and_evidence(
        model_name,
        MODEL_DIR,
        EVIDENCE_DIR / "core",
        GRAPHICAL_PACKAGE,
    )
    manifest["derivative_provenance"] = DERIVATIVE_PROVENANCE
    (EVIDENCE_DIR / "core" / f"{model_name}_build_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def build_adapter() -> dict:
    """Build the scalar sign adapter between the core and physical mapper."""

    model_name = _open_empty_model(
        "OfficialPidSysblockAdapter", "Official PID native graphical output adapter"
    )
    inputs = ["core_y", "core_y1", "core_y2", "core_y3"]
    outputs = ["amplitude_1", "amplitude_2", "amplitude_3", "amplitude_4"]
    for index, name in enumerate(inputs):
        _add(model_name, INPORT, name, -180, 90 - index * 60)
    for index, name in enumerate(outputs):
        _add(model_name, OUTPORT, name, 180, 90 - index * 60)
    for index, (source, target, sign) in enumerate(
        zip(inputs, outputs, PROFILE_CONSTANTS["spin_command_sign"]),
        start=1,
    ):
        gain = f"output_{index}_sign"
        _add(model_name, GAIN, gain, 0, 90 - (index - 1) * 60)
        _set_param(gain, "k", sign)
        _wire(model_name, source, f"{gain}.u")
        _wire(model_name, f"{gain}.y", target)
    return _save_and_evidence(
        model_name,
        MODEL_DIR,
        EVIDENCE_DIR / "adapter",
        GRAPHICAL_PACKAGE,
    )


def build_mapper() -> dict:
    """Build the visible yaw-authority and hover-speed mapper."""

    model_name = _open_empty_model(
        "OfficialPidSysblockMapper", "Official PID native graphical rotor command mapper"
    )
    inputs = ["amplitude_1", "amplitude_2", "amplitude_3", "amplitude_4"]
    outputs = [
        "rotor_command_1",
        "rotor_command_2",
        "rotor_command_3",
        "rotor_command_4",
    ]
    for index, name in enumerate(inputs):
        _add(model_name, INPORT, name, -520, 180 - index * 70)
    for index, name in enumerate(outputs):
        _add(model_name, OUTPORT, name, 520, 180 - index * 70)

    yaw_pattern = PROFILE_CONSTANTS["yaw_pattern"]
    yaw_authority_scale = (
        PROFILE_CONSTANTS["embedded_yaw_authority_reference_ratio"]
        / PROFILE_CONSTANTS["moment_constant_ratio_m"]
    )
    command_scale = (
        PROFILE_CONSTANTS["hover_speed_rad_s"]
        / PROFILE_CONSTANTS["legacy_hover_speed_rad_s"]
    )

    for index, source in enumerate(inputs, start=1):
        projection = f"yaw_projection_{index}"
        _add(model_name, GAIN, projection, -430, 330 - index * 45)
        _set_param(projection, "k", yaw_pattern[index - 1] / 4.0)
        _wire(model_name, source, f"{projection}.u")

    _add(model_name, SUM, "yaw_sum_12", -300, 305)
    _set_param("yaw_sum_12", "inputs", "++")
    _add(model_name, SUM, "yaw_sum_34", -300, 135)
    _set_param("yaw_sum_34", "inputs", "++")
    _add(model_name, SUM, "yaw_sum", -180, 220)
    _set_param("yaw_sum", "inputs", "++")
    _wire(model_name, "yaw_projection_1.y", "yaw_sum_12.u1")
    _wire(model_name, "yaw_projection_2.y", "yaw_sum_12.u2")
    _wire(model_name, "yaw_projection_3.y", "yaw_sum_34.u1")
    _wire(model_name, "yaw_projection_4.y", "yaw_sum_34.u2")
    _wire(model_name, "yaw_sum_12.y", "yaw_sum.u1")
    _wire(model_name, "yaw_sum_34.y", "yaw_sum.u2")

    for index, source in enumerate(inputs, start=1):
        row_y = 320 - index * 85
        yaw_component = f"yaw_component_{index}"
        non_yaw = f"non_yaw_{index}"
        yaw_authority = f"yaw_authority_{index}"
        mapped = f"mapped_{index}"
        command_gain = f"command_scale_{index}"
        hover = f"hover_{index}"
        hover_plus = f"hover_plus_{index}"
        spin_sign = f"spin_sign_{index}"

        _add(model_name, GAIN, yaw_component, -70, row_y + 35)
        _set_param(yaw_component, "k", yaw_pattern[index - 1])
        _wire(model_name, "yaw_sum.y", f"{yaw_component}.u")
        _add(model_name, SUM, non_yaw, 30, row_y + 35)
        _set_param(non_yaw, "inputs", "+-")
        _wire(model_name, source, f"{non_yaw}.u1")
        _wire(model_name, f"{yaw_component}.y", f"{non_yaw}.u2")
        _add(model_name, GAIN, yaw_authority, -70, row_y - 5)
        _set_param(
            yaw_authority,
            "k",
            yaw_pattern[index - 1] * yaw_authority_scale,
        )
        _wire(model_name, "yaw_sum.y", f"{yaw_authority}.u")
        _add(model_name, SUM, mapped, 145, row_y + 35)
        _set_param(mapped, "inputs", "++")
        _wire(model_name, f"{non_yaw}.y", f"{mapped}.u1")
        _wire(model_name, f"{yaw_authority}.y", f"{mapped}.u2")
        _add(model_name, GAIN, command_gain, 235, row_y + 35)
        _set_param(command_gain, "k", command_scale)
        _wire(model_name, f"{mapped}.y", f"{command_gain}.u")
        _add(model_name, CONSTANT, hover, 235, row_y - 5)
        _set_param(hover, "k", PROFILE_CONSTANTS["hover_speed_rad_s"])
        _add(model_name, SUM, hover_plus, 335, row_y + 35)
        _set_param(hover_plus, "inputs", "++")
        _wire(model_name, f"{command_gain}.y", f"{hover_plus}.u1")
        _wire(model_name, f"{hover}.y", f"{hover_plus}.u2")
        _add(model_name, GAIN, spin_sign, 430, row_y + 35)
        _set_param(spin_sign, "k", PROFILE_CONSTANTS["spin_command_sign"][index - 1])
        _wire(model_name, f"{hover_plus}.y", f"{spin_sign}.u")
        _wire(model_name, f"{spin_sign}.y", outputs[index - 1])

    manifest = _save_and_evidence(
        model_name,
        MODEL_DIR,
        EVIDENCE_DIR / "mapper",
        GRAPHICAL_PACKAGE,
    )
    manifest["parameter_provenance"] = {
        "source_file": "Models/MoSimQuadrotorModel/Parameters/Sunray150VirtualPx4Classic.mo",
        "source_kind": "project_profile_constants",
        "values": PROFILE_CONSTANTS,
    }
    (EVIDENCE_DIR / "mapper" / f"{model_name}_build_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def build_runner() -> dict:
    """Compose Core -> Adapter -> Mapper with a fixed scenario boundary."""

    model_name = _open_empty_model(
        "OfficialPidSysblockRunner", "Official PID native graphical controller runner"
    )
    input_names = [
        "x_ref",
        "y_ref",
        "z_ref",
        "x_mea",
        "y_mea",
        "z_mea",
        "roll_mea",
        "pitch_mea",
        "yaw_mea",
    ]
    output_names = [
        "rotor_command_1",
        "rotor_command_2",
        "rotor_command_3",
        "rotor_command_4",
    ]
    for index, name in enumerate(input_names):
        _add(model_name, INPORT, name, -520, 260 - index * 55)
    for index, name in enumerate(output_names):
        _add(model_name, OUTPORT, name, 520, 110 - index * 75)

    core_type = _component_type("OfficialPidSysblockCore")
    adapter_type = _component_type("OfficialPidSysblockAdapter")
    mapper_type = _component_type("OfficialPidSysblockMapper")
    _add(model_name, core_type, "controller_core", -180, 120, 150, 330)
    _add(model_name, adapter_type, "output_adapter", 60, 120, 130, 230)
    _add(model_name, mapper_type, "rotor_mapper", 300, 120, 150, 330)

    for name in input_names:
        _wire(model_name, name, f"controller_core.{name}")
    for index, core_output in enumerate(["y", "y1", "y2", "y3"], start=1):
        adapter_input = "core_y" if index == 1 else f"core_y{index - 1}"
        _wire(model_name, f"controller_core.{core_output}", f"output_adapter.{adapter_input}")
        _wire(model_name, f"output_adapter.amplitude_{index}", f"rotor_mapper.amplitude_{index}")
        _wire(model_name, f"rotor_mapper.rotor_command_{index}", output_names[index - 1])

    manifest = _save_and_evidence(
        model_name,
        MODEL_DIR,
        EVIDENCE_DIR / "runner",
        GRAPHICAL_PACKAGE,
    )
    manifest["composition"] = {
        "controller_core": core_type,
        "output_adapter": adapter_type,
        "rotor_mapper": mapper_type,
        "scenario_boundary": "fixed runner ports; scenario sources remain external",
    }
    (EVIDENCE_DIR / "runner" / f"{model_name}_build_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def build() -> dict:
    core = build_core()
    adapter = build_adapter()
    mapper = build_mapper()
    runner = build_runner()
    return {
        "core": core,
        "adapter": adapter,
        "mapper": mapper,
        "runner": runner,
    }


def _normalize_persisted_output_intervals() -> None:
    for model_stem, evidence_name in [
        ("OfficialPidSysblockCore", "core"),
        ("OfficialPidSysblockAdapter", "adapter"),
        ("OfficialPidSysblockMapper", "mapper"),
        ("OfficialPidSysblockRunner", "runner"),
    ]:
        staging = EVIDENCE_DIR / evidence_name / "api_generated_source" / f"{model_stem}.mo"
        target = MODEL_DIR / f"{model_stem}.mo"
        text = _normalize_generated_metadata(
            staging.read_text(encoding="utf-8")
        )
        staging.write_text(text, encoding="utf-8")
        target.write_text(
            f"within {GRAPHICAL_PACKAGE};\n" + text.lstrip(),
            encoding="utf-8",
        )


_BUILD_RESULT = build()
_normalize_persisted_output_intervals()
RUN_SCRIPT_RESULT = _BUILD_RESULT
