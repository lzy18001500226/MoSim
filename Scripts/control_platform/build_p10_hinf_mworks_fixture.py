#!/usr/bin/env python3
"""Build the P10 frozen-hover H-infinity adapter Sysblock and MIL fixture."""

from __future__ import annotations

import json
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "Results/control_platform/p10_mworks_gap_closeout_20260718/hinf_hover_wrench"
MODEL_DIR = RESULT / "models"
CODEGEN_DIR = RESULT / "codegen"

INPUTS = [
    "state_roll", "state_pitch", "state_yaw", "state_p", "state_q", "state_r",
    "state_u", "state_v", "state_w", "state_x", "state_y", "state_z",
    "reference_roll", "reference_pitch", "reference_yaw", "reference_p", "reference_q", "reference_r",
    "reference_u", "reference_v", "reference_w", "reference_x", "reference_y", "reference_z",
    "enable", "reset", "mass", "gravity", "force_min_n", "force_max_n", "torque_limit_nm",
    "roll_stiffness_nm_per_rad", "pitch_stiffness_nm_per_rad", "yaw_stiffness_nm_per_rad",
    "hover_percentage", "tilt_limit_rad", "yaw_correction_limit_rad",
    "min_normalized_thrust", "max_normalized_thrust",
]

OUTPUTS = [
    "wrench_force_n", "wrench_tau_x_nm", "wrench_tau_y_nm", "wrench_tau_z_nm",
    "desired_attitude_w", "desired_attitude_x", "desired_attitude_y", "desired_attitude_z",
    "normalized_thrust", "collective_thrust_n", "adapted_roll_rad", "adapted_pitch_rad",
    "adapted_yaw_rad", "saturated", "status_code", "source_command_variant",
    "adapted_command_variant",
]

CONSTANTS = {
    "state_roll": 0.001, "state_pitch": -0.001, "state_yaw": 0.002,
    "state_p": 0.01, "state_q": -0.02, "state_r": 0.005,
    "state_u": 0.01, "state_v": -0.01, "state_w": 0.02,
    "state_x": 0.001, "state_y": -0.002, "state_z": 0.005,
    "reference_roll": 0.0, "reference_pitch": 0.0, "reference_yaw": 0.0,
    "reference_p": 0.0, "reference_q": 0.0, "reference_r": 0.0,
    "reference_u": 0.0, "reference_v": 0.0, "reference_w": 0.0,
    "reference_x": 0.0, "reference_y": 0.0, "reference_z": 0.0,
    "enable": 1.0, "reset": 0.0, "mass": 1.0, "gravity": 9.80665,
    "force_min_n": 0.0, "force_max_n": 25.0, "torque_limit_nm": 8.0,
    "roll_stiffness_nm_per_rad": 30.0, "pitch_stiffness_nm_per_rad": 30.0,
    "yaw_stiffness_nm_per_rad": 40.0, "hover_percentage": 0.37,
    "tilt_limit_rad": 0.35, "yaw_correction_limit_rad": 0.20,
    "min_normalized_thrust": 0.0, "max_normalized_thrust": 0.62,
}


def load_g9_builder():
    path = ROOT / "Scripts/sunray/px4ctrl_golden_slice/build_g9_family_cfunction_sysblock.py"
    module = ModuleType("p10_hinf_current_g9_builder")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def strip_header(text: str) -> str:
    output: list[str] = []
    skip_extern = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "#ifdef __cplusplus":
            skip_extern = True
            continue
        if skip_extern:
            if stripped == "#endif":
                skip_extern = False
            continue
        if stripped.startswith(("#ifndef", "#define", "#endif")):
            continue
        output.append(line)
    return "\n".join(output)


def strip_source(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines()
        if not line.strip().startswith('#include "')
    )


def fixture_model(builder, model_name: str, function_model: str) -> str:
    declarations = []
    connections = []
    input_count = len(INPUTS)
    output_count = len(OUTPUTS)
    diagram_span = float(max(input_count - 1, output_count - 1, 25) * 24)
    diagram_half_height = diagram_span / 2.0 + 60.0
    block_half_height = diagram_span / 2.0
    diagram_bottom = -diagram_half_height
    block_bottom = -block_half_height
    diagram_extent = "{{-760," + f"{diagram_bottom:.2f}" + "},{760," + f"{diagram_half_height:.2f}" + "}}"
    block_extent = "{{-80," + f"{block_bottom:.2f}" + "},{80," + f"{block_half_height:.2f}" + "}}"
    for index, name in enumerate(INPUTS):
        x = -600
        y = builder.port_y(index, input_count, diagram_span)
        declarations.append(
            f"  SysplorerEmbeddedCoder.Sources.Constant {name}_source(k={CONSTANTS[name]}) "
            f"annotation(Placement(transformation(origin={{{x},{y:.2f}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(
            f"  connect({name}_source.y, controller.{name}_in) "
            f"annotation(Line(points={{{{{x + 8},{y:.2f}}},{{-80,{y:.2f}}}}},color={{0,0,127}}));"
        )
    for index, name in enumerate(OUTPUTS):
        x = 600
        y = builder.port_y(index, output_count, diagram_span)
        declarations.append(
            f"  SysplorerEmbeddedCoder.Port.Outport {name} "
            f"annotation(Placement(transformation(origin={{{x},{y:.2f}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(
            f"  connect(controller.{name}_out, {name}) "
            f"annotation(Line(points={{{{80,{y:.2f}}},{{{x - 8},{y:.2f}}}}},color={{0,0,127}}));"
        )
    return f'''model {model_name}
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.07,StoreEventValue=0),Diagram(coordinateSystem(extent={diagram_extent},grid={{2,2}})));
  {function_model} controller annotation(Placement(transformation(origin={{0,0}},extent={block_extent})));
{chr(10).join(declarations)}
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
{chr(10).join(connections)}
end {model_name};
'''


def main() -> int:
    builder = load_g9_builder()
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    CODEGEN_DIR.mkdir(parents=True, exist_ok=True)
    headers = [
        ROOT / "Scripts/control_platform/wave_b_hinf_core.h",
        ROOT / "Scripts/control_platform/p10_hinf_wrench_adapter_core.h",
    ]
    sources = [
        ROOT / "Scripts/control_platform/wave_b_hinf_core.c",
        ROOT / "Scripts/control_platform/p10_hinf_wrench_adapter_core.c",
    ]
    include_code = "\n\n".join(
        [strip_header(path.read_text(encoding="utf-8")) for path in headers]
        + [strip_source(path.read_text(encoding="utf-8")) for path in sources]
    ).strip() + "\n"
    builder.INPUTS = INPUTS
    builder.OUTPUTS = OUTPUTS
    function_model = "MoSim_P10_Hinf_WrenchAdapter_CFunction_Sysblock"
    fixture = "MoSim_P10_HINF_HOVER_WRENCH_MIL"
    function_path = MODEL_DIR / f"{function_model}.mo"
    function_path.write_text(
        builder.build_model(
            function_model,
            CODEGEN_DIR,
            include_code,
            real_as_float=False,
            external_function="MosimP10HinfWrenchAdapterStepScalar",
        ),
        encoding="utf-8",
        newline="\n",
    )
    fixture_path = MODEL_DIR / f"{fixture}.mo"
    fixture_path.write_text(fixture_model(builder, fixture, function_model), encoding="utf-8", newline="\n")
    manifest = {
        "schema": "mosim.p10_hinf_wrench_adapter_mworks_build.v1",
        "controller": "hinf_hover_wrench",
        "function_model": function_model,
        "function_model_path": str(function_path),
        "fixture_model": fixture,
        "fixture_model_path": str(fixture_path),
        "codegen_dir": str(CODEGEN_DIR),
        "inputs": INPUTS,
        "outputs": OUTPUTS,
        "constants": CONSTANTS,
        "adapter_contract": "Frozen-hover quasi-static WRENCH to ATTITUDE_THRUST using bounded virtual attitude stiffness.",
        "claim_boundary": "Graphical Sysblock source only. CheckModel, SimulateModel, official codegen, SIL and Gazebo are separate gates.",
    }
    (RESULT / "P10_HINF_BUILD_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
