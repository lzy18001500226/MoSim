#!/usr/bin/env python3
"""Build direct graphical Wave-A controller cores for G5 review.

The historical LQR, LQI, and backstepping route files are CFunction wrappers.
This builder keeps those files intact and creates separate Sysblock models that
expose the same outer-loop equations and the attitude/thrust adapter path.
The outputs are graphical-review artifacts only: they are not whole-aircraft
test harnesses and do not claim numerical equivalence until a later gate.

Run with MWORKS' bundled Python against an existing Sysplorer API session:

    & 'D:\\Program Files\\MWORKS\\Sysplorer 2026a\\External\\python64\\python.exe' \
      Scripts\\control_platform\\build_g5_wave_a_direct_graphical_mil.py
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
    / "wave_a"
)
MANIFEST_PATH = SOURCE_DIR / "WAVE_A_DIRECT_GRAPHICAL_BUILD.json"
SOURCE_CFUNCTION = (
    ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Controllers"
    / "GraphicalMIL"
    / "ClassicRobust"
    / "MoSim_WaveA_CFunction_Sysblock.mo"
)

DT = 0.01
AXES = ("x", "y", "z")
INPUT_VALUES = {
    "position": (0.1, -0.2, 0.3),
    "velocity": (0.05, -0.04, 0.02),
    "reference_position": (1.0, -0.5, 1.2),
    "reference_velocity": (0.1, 0.0, 0.05),
    "reference_acceleration": (0.0, 0.0, 0.0),
}
PARAMS = {
    "kp": (1.6, 1.6, 2.2),
    "kv": (1.8, 1.8, 2.0),
    "ki": (0.20, 0.20, 0.30),
    "integral_limit": (0.50, 0.50, 0.35),
    "backstepping_k1": (1.1, 1.1, 1.3),
    "backstepping_k2": (1.8, 1.8, 2.0),
    "mass": 1.0,
    "gravity": 9.80665,
    "hover_percentage": 0.37,
    "tilt_limit_rad": 0.5235987755982988,
}
ALGORITHMS = {
    "lqr_baseline": {
        "model": "MoSim_G5_LQR_DIRECT_GRAPHICAL_MIL",
        "label": "LQR outer-loop direct graphical core",
        "law": "a_ref + Kp * (p_ref - p) + Kv * (v_ref - v), with gravity and attitude/thrust limits",
    },
    "lqi_baseline": {
        "model": "MoSim_G5_LQI_DIRECT_GRAPHICAL_MIL",
        "label": "LQI outer-loop direct graphical core",
        "law": "LQR outer loop plus bounded discrete integral of position error",
    },
    "backstepping_baseline": {
        "model": "MoSim_G5_BACKSTEPPING_DIRECT_GRAPHICAL_MIL",
        "label": "Backstepping outer-loop direct graphical core",
        "law": "a_ref + k1 * ev + k2 * (ev + k1 * ep), with gravity and attitude/thrust limits",
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


def connect(model: str, source: str, target: str) -> None:
    if not ModelingPy.ConnectPort(model, source, target):
        raise RuntimeError(f"ConnectPort failed: {model}: {source} -> {target}")


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


def sum_ports(model: str, name: str, ports: list[str], signs: str, x: float, y: float) -> str:
    if len(ports) != len(signs):
        raise ValueError(f"{name}: {len(ports)} ports do not match {signs!r}")
    add(model, "SysplorerEmbeddedCoder.MathOperation.Sum", name, x, y)
    set_param(name, "inputs", signs)
    for index, source_port in enumerate(ports, start=1):
        connect(model, source_port, f"{name}.u{index}")
    return f"{name}.y"


def product(model: str, name: str, left: str, right: str, x: float, y: float) -> str:
    add(model, "SysplorerEmbeddedCoder.MathOperation.Product", name, x, y)
    set_param(name, "inputs", "**")
    connect(model, left, f"{name}.u1")
    connect(model, right, f"{name}.u2")
    return f"{name}.y"


def saturation(model: str, name: str, source_port: str, low: float, high: float, x: float, y: float) -> str:
    add(model, "SysplorerEmbeddedCoder.Discontinuities.Saturation", name, x, y)
    set_param(name, "lowLimit", low)
    set_param(name, "upLimit", high)
    connect(model, source_port, f"{name}.u")
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
    if ModelingPy.ClassExist(model):
        if not ModelingPy.EraseClasses((model,)):
            raise RuntimeError(f"EraseClasses failed: {model}")
    if not ModelingPy.NewModel(model, "Sysblock", description):
        raise RuntimeError(f"NewModel failed: {model}")
    if not ModelingPy.OpenModel(model, "diagram"):
        raise RuntimeError(f"OpenModel failed: {model}")


def build_variant(scheme_id: str, replace: bool) -> dict[str, Any]:
    spec = ALGORITHMS[scheme_id]
    model = str(spec["model"])
    target = SOURCE_DIR / f"{model}.mo"
    reset_model(model, str(spec["label"]), target, replace)

    input_ports: dict[str, str] = {}
    for row_index, row in enumerate(("position", "velocity", "reference_position", "reference_velocity", "reference_acceleration")):
        for axis_index, axis in enumerate(AXES):
            name = f"{row}_{axis}"
            input_ports[name] = source(model, name, -650, 350 - row_index * 110 - axis_index * 26)
    dt = source(model, "dt", -650, -245)
    enable = source(model, "enable", -650, -285)
    zero = constant(model, "disabled_command", 0.0, 510, -270)

    desired_acceleration: dict[str, str] = {}
    position_error: dict[str, str] = {}
    velocity_error: dict[str, str] = {}
    auxiliary_outputs: dict[str, str] = {}
    for axis_index, axis in enumerate(AXES):
        y = 255 - axis_index * 210
        ep = sum_ports(
            model,
            f"position_error_{axis}",
            [input_ports[f"reference_position_{axis}"], input_ports[f"position_{axis}"]],
            "+-",
            -510,
            y + 42,
        )
        ev = sum_ports(
            model,
            f"velocity_error_{axis}",
            [input_ports[f"reference_velocity_{axis}"], input_ports[f"velocity_{axis}"]],
            "+-",
            -510,
            y - 42,
        )
        position_error[axis] = ep
        velocity_error[axis] = ev

        if scheme_id == "backstepping_baseline":
            k1_ep = gain(model, f"backstep_k1_ep_{axis}", ep, PARAMS["backstepping_k1"][axis_index], -400, y + 55)
            virtual_velocity_error = sum_ports(model, f"virtual_velocity_error_{axis}", [ev, k1_ep], "++", -325, y + 25)
            k1_ev = gain(model, f"backstep_k1_ev_{axis}", ev, PARAMS["backstepping_k1"][axis_index], -400, y - 55)
            k2_virtual = gain(model, f"backstep_k2_virtual_{axis}", virtual_velocity_error, PARAMS["backstepping_k2"][axis_index], -245, y + 25)
            feedback = sum_ports(model, f"backstep_feedback_{axis}", [k1_ev, k2_virtual], "++", -165, y)
            auxiliary_outputs[f"virtual_velocity_error_{axis}"] = virtual_velocity_error
        else:
            p_term = gain(model, f"position_gain_{axis}", ep, PARAMS["kp"][axis_index], -400, y + 42)
            v_term = gain(model, f"velocity_gain_{axis}", ev, PARAMS["kv"][axis_index], -400, y - 42)
            feedback = sum_ports(model, f"pv_feedback_{axis}", [p_term, v_term], "++", -300, y)
            if scheme_id == "lqi_baseline":
                add(model, "SysplorerEmbeddedCoder.Discrete.UnitDelay", f"integral_state_{axis}", -410, y - 120)
                set_param(f"integral_state_{axis}", "initCond", 0.0)
                integral_drive = product(model, f"integral_drive_{axis}", ep, dt, -315, y - 120)
                integral_pre = sum_ports(model, f"integral_pre_{axis}", [f"integral_state_{axis}.y", integral_drive], "++", -230, y - 120)
                integral_limited = saturation(
                    model,
                    f"integral_limit_{axis}",
                    integral_pre,
                    -PARAMS["integral_limit"][axis_index],
                    PARAMS["integral_limit"][axis_index],
                    -145,
                    y - 120,
                )
                connect(model, integral_limited, f"integral_state_{axis}.u1")
                i_term = gain(model, f"integral_gain_{axis}", integral_limited, PARAMS["ki"][axis_index], -65, y - 120)
                feedback = sum_ports(model, f"lqi_feedback_{axis}", [feedback, i_term], "++", -65, y)
                auxiliary_outputs[f"integral_position_error_{axis}"] = integral_limited

        acceleration = sum_ports(
            model,
            f"desired_acceleration_pre_gravity_{axis}",
            [input_ports[f"reference_acceleration_{axis}"], feedback],
            "++",
            35,
            y,
        )
        if axis == "z":
            gravity = constant(model, "gravity_compensation", PARAMS["gravity"], 35, y + 70)
            acceleration = sum_ports(model, "desired_acceleration_z", [acceleration, gravity], "++", 125, y)
        else:
            acceleration = gain(model, f"desired_acceleration_{axis}", acceleration, 1.0, 125, y)
        desired_acceleration[axis] = acceleration

    roll_raw = gain(model, "roll_from_lateral_acceleration", desired_acceleration["y"], -1.0 / PARAMS["gravity"], 240, 55)
    roll = saturation(model, "roll_tilt_limit", roll_raw, -PARAMS["tilt_limit_rad"], PARAMS["tilt_limit_rad"], 325, 55)
    pitch_raw = gain(model, "pitch_from_lateral_acceleration", desired_acceleration["x"], 1.0 / PARAMS["gravity"], 240, 120)
    pitch = saturation(model, "pitch_tilt_limit", pitch_raw, -PARAMS["tilt_limit_rad"], PARAMS["tilt_limit_rad"], 325, 120)
    normalized_raw = gain(
        model,
        "normalized_thrust_pre_limit",
        desired_acceleration["z"],
        PARAMS["hover_percentage"] / PARAMS["gravity"],
        240,
        -55,
    )
    normalized = saturation(model, "normalized_thrust_limit", normalized_raw, 0.0, 1.0, 325, -55)
    collective = gain(
        model,
        "collective_thrust_from_normalized",
        normalized,
        PARAMS["mass"] * PARAMS["gravity"] / PARAMS["hover_percentage"],
        410,
        -55,
    )

    output_ports: dict[str, str] = {
        **{f"position_error_{axis}": position_error[axis] for axis in AXES},
        **{f"velocity_error_{axis}": velocity_error[axis] for axis in AXES},
        **{f"desired_acceleration_{axis}": desired_acceleration[axis] for axis in AXES},
        **auxiliary_outputs,
        "desired_roll_rad": roll,
        "desired_pitch_rad": pitch,
        "normalized_thrust": normalized,
        "collective_thrust_n": collective,
    }
    output_order = list(output_ports)
    for index, name in enumerate(output_order):
        gated = enable_switch(model, f"enable_{name}", output_ports[name], enable, zero, 525, 330 - index * 38)
        # Sysblock component names are unique within a model. Keep the named
        # internal law blocks visible and suffix only their outward review ports.
        output(model, f"{name}_out", 675, 330 - index * 38, gated)

    for component, description in {
        "roll_tilt_limit": "Attitude adapter roll limit from lateral acceleration",
        "pitch_tilt_limit": "Attitude adapter pitch limit from lateral acceleration",
        "normalized_thrust_limit": "Normalized thrust saturation [0, 1]",
        "collective_thrust_from_normalized": "Collective thrust allocation from normalized thrust",
    }.items():
        ModelingPy.SetComponentDescription(model, component, description)

    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    saved = ModelingPy.SaveModelAs(model, str(SOURCE_DIR), model)
    checked = ModelingPy.CheckModel(model)
    source_text = str(ModelingPy.GetModelText(model))
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
        "source_formula_reference": f"{repo_path(SOURCE_CFUNCTION)}:301-320,251-289,357-363",
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
        "schema": "mosim.g5.wave_a_direct_graphical_build.v1",
        "scope": "Direct graphical replacements for historical Wave-A CFunction wrappers. Old wrappers remain compatibility/reference artifacts.",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "source_cfunction": repo_path(SOURCE_CFUNCTION),
        "source_cfunction_sha256": sha256(SOURCE_CFUNCTION),
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
