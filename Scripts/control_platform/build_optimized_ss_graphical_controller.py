#!/usr/bin/env python3
"""Build the optimized controller core with official Sysplorer APIs.

The controller is intentionally a graphical Sysblock artifact.  Its six
dynamic control channels are explicit DiscreteStateSpace blocks; saturation,
feed-forward, error formation, and motor mixing remain visible blocks around
them.  Run this file through ``call_code(mode="run_script")`` in Sysplorer.
"""

from __future__ import annotations

import json
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
MODEL_NAME = "MoSim_OptimizedSSGraphicalController"
PACKAGE_NAME = "MoSimQuadrotorModel.Control.Implementations.Graphical.ProjectOwned"
SOURCE_DIR = ROOT / "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/ProjectOwned"
RESULT_DIR = ROOT / "Results/control_optimization_ss_graphical"
RESULT_MODEL_DIR = RESULT_DIR / "models/graphical"
SCREENSHOT_DIR = RESULT_DIR / "screenshots"
LOG_DIR = RESULT_DIR / "logs"


INPUTS = [
    ("x_error", -720, 270),
    ("y_error", -720, 220),
    ("z_error", -720, 170),
    ("z_ref_rate", -720, 120),
    ("roll_mea", -720, 45),
    ("pitch_mea", -720, 0),
    ("yaw_mea", -720, -45),
    ("yaw_ref", -720, -90),
]
OUTPUTS = [("y", 720, 190), ("y1", 720, 70), ("y2", 720, -50), ("y3", 720, -170)]


def add(type_name: str, block: str, x: float, y: float, width=42, height=30) -> None:
    if not ModelingPy.AddComponent(type_name, MODEL_NAME, block, x, y, width, height):
        raise RuntimeError(f"AddComponent failed: {block} ({type_name})")


def set_param(block: str, parameter: str, value: str) -> None:
    if not ModelingPy.SetParamValue(f"{block}.{parameter}", value):
        raise RuntimeError(f"SetParamValue failed: {block}.{parameter}={value}")


def connect(source: str, target: str) -> None:
    if not ModelingPy.ConnectPort(MODEL_NAME, source, target):
        raise RuntimeError(f"ConnectPort failed: {source} -> {target}")


def add_input_and_output_ports() -> None:
    for block, x, y in INPUTS:
        add("SysplorerEmbeddedCoder.Port.Inport", block, x, y)
    for block, x, y in OUTPUTS:
        add("SysplorerEmbeddedCoder.Port.Outport", block, x, y)


def add_ss_channel(
    block: str,
    x: float,
    y: float,
    input_signal: str,
    a: str,
    b: str,
    c: str,
    d: str,
    description: str,
) -> None:
    add("SysplorerEmbeddedCoder.Discrete.DiscreteStateSpace", block, x, y, 78, 46)
    set_param(block, "A", a)
    set_param(block, "B", b)
    set_param(block, "C", c)
    set_param(block, "D", d)
    if input_signal:
        connect(input_signal, f"{block}.u")
    ModelingPy.SetComponentDescription(MODEL_NAME, block, description)


def add_gain(block: str, x: float, y: float, gain: float) -> None:
    add("SysplorerEmbeddedCoder.MathOperation.Gain", block, x, y)
    set_param(block, "k", str(gain))


def add_sum(block: str, x: float, y: float, inputs: str) -> None:
    add("SysplorerEmbeddedCoder.MathOperation.Sum", block, x, y)
    set_param(block, "inputs", f'"{inputs}"')


def add_limit(block: str, x: float, y: float, lower: float, upper: float) -> None:
    add("SysplorerEmbeddedCoder.Discontinuities.Saturation", block, x, y)
    set_param(block, "upLimit", str(upper))
    set_param(block, "lowLimit", str(lower))


def build() -> dict:
    for directory in (RESULT_MODEL_DIR, SCREENSHOT_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    if not ModelingPy.ClassExist(MODEL_NAME):
        if not ModelingPy.NewModel(MODEL_NAME, "Sysblock", "Optimized pure graphical ss controller"):
            raise RuntimeError(f"NewModel failed: {MODEL_NAME}")
    if not ModelingPy.OpenModel(MODEL_NAME, "diagram"):
        raise RuntimeError(f"OpenModel failed: {MODEL_NAME}")
    for component in list(ModelingPy.GetComponents(MODEL_NAME)):
        if not ModelingPy.RemoveComponent(MODEL_NAME, component):
            raise RuntimeError(f"RemoveComponent failed: {component}")

    add_input_and_output_ports()

    # Each channel is a second-order discrete state-space compensator.  The
    # first state is the low-pass tracking state; the second is a filtered
    # rate state.  This exposes the dynamic core without a hidden equation or
    # CFunction block.
    add_ss_channel(
        "x_outer_ss", -560, 260, "x_error",
        "{{0.82, 0}, {0, 0.55}}", "{{0.18}, {0.45}}", "{{0.08, 0.04}}", "{{0.06}}",
        "x-error to pitch-reference discrete ss compensator",
    )
    add_ss_channel(
        "y_outer_ss", -560, 210, "y_error",
        "{{0.82, 0}, {0, 0.55}}", "{{0.18}, {0.45}}", "{{0.08, 0.04}}", "{{0.06}}",
        "y-error to roll-reference discrete ss compensator",
    )
    add_ss_channel(
        "z_outer_ss", -560, 160, "z_error",
        "{{0.93, 0}, {0, 0.60}}", "{{0.07}, {0.40}}", "{{7.0, 2.0}}", "{{1.5}}",
        "z-error to collective-thrust discrete ss compensator",
    )
    add_ss_channel(
        "roll_inner_ss", -270, 70, "",
        "{{0.74, 0}, {0, 0.50}}", "{{0.26}, {0.50}}", "{{2.0, 1.2}}", "{{3.0}}",
        "roll-error attitude discrete ss compensator",
    )
    add_ss_channel(
        "pitch_inner_ss", -270, 15, "",
        "{{0.74, 0}, {0, 0.50}}", "{{0.26}, {0.50}}", "{{2.0, 1.2}}", "{{3.0}}",
        "pitch-error attitude discrete ss compensator",
    )
    add_ss_channel(
        "yaw_inner_ss", -270, -40, "",
        "{{0.70, 0}, {0, 0.45}}", "{{0.30}, {0.55}}", "{{1.0, 0.4}}", "{{3.6}}",
        "yaw-error attitude discrete ss compensator",
    )

    add_gain("z_feedforward", -560, 115, 0.35)
    add_sum("thrust_command_sum", -370, 145, "++")
    add_limit("pitch_ref_limit", -370, 260, -0.2617801047, 0.2617801047)
    add_limit("roll_ref_limit", -370, 210, -0.2617801047, 0.2617801047)
    connect("z_outer_ss.y", "thrust_command_sum.u1")
    connect("z_ref_rate", "z_feedforward.u")
    connect("z_feedforward.y", "thrust_command_sum.u2")

    add_sum("roll_error", -430, 70, "+-")
    add_sum("pitch_error", -430, 15, "+-")
    add_sum("yaw_error", -430, -40, "+-")
    connect("roll_ref_limit.y", "roll_error.u1")
    connect("roll_mea", "roll_error.u2")
    connect("pitch_ref_limit.y", "pitch_error.u1")
    connect("pitch_mea", "pitch_error.u2")
    connect("yaw_ref", "yaw_error.u1")
    connect("yaw_mea", "yaw_error.u2")
    connect("roll_error.y", "roll_inner_ss.u")
    connect("pitch_error.y", "pitch_inner_ss.u")
    connect("yaw_error.y", "yaw_inner_ss.u")

    add_limit("thrust_limit", -270, 145, -20.0, 20.0)
    add_limit("roll_limit", -80, 70, -6.5, 6.5)
    add_limit("pitch_limit", -80, 15, -6.5, 6.5)
    add_limit("yaw_limit", -80, -40, -6.5, 6.5)
    connect("x_outer_ss.y", "pitch_ref_limit.u")
    connect("y_outer_ss.y", "roll_ref_limit.u")
    connect("thrust_command_sum.y", "thrust_limit.u")
    connect("roll_inner_ss.y", "roll_limit.u")
    connect("pitch_inner_ss.y", "pitch_limit.u")
    connect("yaw_inner_ss.y", "yaw_limit.u")

    # Explicit X quadrotor mixer: thrust + signed roll/pitch/yaw authority.
    mixer_signs = {
        "m1": (1.0, 0.707, -0.707, -0.707, 190),
        "m2": (1.0, -0.707, -0.707, 0.707, 70),
        "m3": (1.0, -0.707, 0.707, -0.707, -50),
        "m4": (1.0, 0.707, 0.707, 0.707, -170),
    }
    for suffix, (thrust_gain, roll_gain, pitch_gain, yaw_gain, y) in mixer_signs.items():
        add_gain(f"{suffix}_roll_gain", 80, y + 20, roll_gain)
        add_gain(f"{suffix}_pitch_gain", 80, y, pitch_gain)
        add_gain(f"{suffix}_yaw_gain", 80, y - 20, yaw_gain)
        add_sum(f"{suffix}_thrust_roll_sum", 180, y + 12, "++")
        add_sum(f"{suffix}_pitch_yaw_sum", 180, y - 12, "++")
        add_sum(f"{suffix}_mix_sum", 260, y, "++")
        add_limit(f"{suffix}_limit", 360, y, -20.0, 20.0)
        connect("thrust_limit.y", f"{suffix}_thrust_roll_sum.u1")
        connect("roll_limit.y", f"{suffix}_roll_gain.u")
        connect(f"{suffix}_roll_gain.y", f"{suffix}_thrust_roll_sum.u2")
        connect("pitch_limit.y", f"{suffix}_pitch_gain.u")
        connect(f"{suffix}_pitch_gain.y", f"{suffix}_pitch_yaw_sum.u1")
        connect("yaw_limit.y", f"{suffix}_yaw_gain.u")
        connect(f"{suffix}_yaw_gain.y", f"{suffix}_pitch_yaw_sum.u2")
        connect(f"{suffix}_thrust_roll_sum.y", f"{suffix}_mix_sum.u1")
        connect(f"{suffix}_pitch_yaw_sum.y", f"{suffix}_mix_sum.u2")
        connect(f"{suffix}_mix_sum.y", f"{suffix}_limit.u")

    connect("m1_limit.y", "y")
    connect("m2_limit.y", "y1")
    connect("m3_limit.y", "y2")
    connect("m4_limit.y", "y3")

    descriptions = {
        "thrust_command_sum": "State-space collective channel plus explicit vertical feed-forward",
        "pitch_ref_limit": "Outer-loop pitch reference safety limit",
        "roll_ref_limit": "Outer-loop roll reference safety limit",
        "thrust_limit": "Collective command safety limit",
        "roll_limit": "Roll torque command safety limit",
        "pitch_limit": "Pitch torque command safety limit",
        "yaw_limit": "Yaw torque command safety limit",
    }
    for component, description in descriptions.items():
        ModelingPy.SetComponentDescription(MODEL_NAME, component, description)

    model_text = str(ModelingPy.GetModelText(MODEL_NAME))
    result_model_path = RESULT_MODEL_DIR / f"{MODEL_NAME}.mo"
    source_model_path = SOURCE_DIR / f"{MODEL_NAME}.mo"
    # SaveModelAs is the persistence operation; the package-qualified copy is
    # only a generated source export so the model can be loaded from the repo.
    if result_model_path.exists():
        # SaveModelAs refuses an existing target.  The topology has already
        # been persisted by the official API; refresh the generated export
        # from GetModelText below so reruns stay deterministic.
        saved_result = True
    else:
        saved_result = bool(ModelingPy.SaveModelAs(MODEL_NAME, str(RESULT_MODEL_DIR), MODEL_NAME))
    result_model_path.write_text(model_text, encoding="utf-8")
    source_model_path.write_text(
        f"within {PACKAGE_NAME};\n" + model_text,
        encoding="utf-8",
    )
    diagram_path = SCREENSHOT_DIR / f"{MODEL_NAME}.png"
    exported = bool(ModelingPy.ExportDiagram(MODEL_NAME, str(diagram_path), 2600, 1500))
    check_model = bool(ModelingPy.CheckModel(MODEL_NAME))
    components = list(ModelingPy.GetComponents(MODEL_NAME))
    connections = model_text.count("connect(")
    state_space_blocks = [
        component for component in components
        if component.endswith("_ss")
    ]
    manifest = {
        "schema": "mosim.optimized_ss_graphical_controller.v1",
        "source": "MWORKS_MCP",
        "build_method": "official_sysplorer_api",
        "model_name": MODEL_NAME,
        "package_name": PACKAGE_NAME,
        "source_model_path": str(source_model_path),
        "result_model_path": str(result_model_path),
        "diagram_path": str(diagram_path),
        "saved_result": saved_result,
        "diagram_exported": exported,
        "check_model": check_model,
        "component_count": len(components),
        "connection_count": connections,
        "state_space_blocks": state_space_blocks,
        "state_space_block_count": len(state_space_blocks),
        "core_is_pure_graphical_ss": bool(
            len(state_space_blocks) == 6
            and "SysplorerEmbeddedCoder.Utilities.CFunction" not in model_text
            and "Equation_Sysblock" not in model_text
            and "Modelica.Blocks" not in model_text
        ),
        "behavior_equivalence_ok": False,
        "claim_boundary": (
            "Graphical structure and CheckModel only. Quantitative plant tracking "
            "equivalence remains open until a fixed-input MIL comparison is run."
        ),
        "last_errors": str(ModelingPy.GetLastErrors()),
    }
    manifest_path = LOG_DIR / "optimized_ss_graphical_build_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


RUN_SCRIPT_RESULT = build()
