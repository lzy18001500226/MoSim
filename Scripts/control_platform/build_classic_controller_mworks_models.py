#!/usr/bin/env python3
"""Build graphical CFunction Sysblock and MIL fixtures for five classic controllers."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = [
    "controller_id", "dt",
    "position_x", "position_y", "position_z",
    "velocity_x", "velocity_y", "velocity_z",
    "reference_position_x", "reference_position_y", "reference_position_z",
    "reference_velocity_x", "reference_velocity_y", "reference_velocity_z",
    "reference_acceleration_x", "reference_acceleration_y", "reference_acceleration_z",
    "reference_yaw", "enable", "reset",
]
VECTOR_OUTPUTS = {
    "desired_acceleration": 3, "desired_attitude": 4,
    "observer_position": 3, "observer_velocity": 3,
    "reference_model_position": 3, "reference_model_velocity": 3,
    "adaptive_position_delta": 3, "adaptive_velocity_delta": 3,
    "fractional_integral": 3, "fractional_derivative": 3,
}
AXIS_NAMES = ["x", "y", "z"]
OUTPUTS = []
for prefix, size in VECTOR_OUTPUTS.items():
    suffixes = ["w", "x", "y", "z"] if size == 4 else AXIS_NAMES
    OUTPUTS.extend(f"{prefix}_{suffix}" for suffix in suffixes)
OUTPUTS.extend(["normalized_thrust", "collective_thrust_n", "saturated", "status_code"])
CONTROLLERS = {
    1: "pole_placement_luenberger", 2: "mrac", 3: "ndi", 4: "fopid", 5: "h2_state_feedback",
}
CONSTANTS = {
    "dt": 0.01,
    "position_x": 0.10, "position_y": -0.05, "position_z": 0.80,
    "velocity_x": 0.02, "velocity_y": -0.01, "velocity_z": 0.01,
    "reference_position_x": 0.25, "reference_position_y": 0.10, "reference_position_z": 1.00,
    "reference_velocity_x": 0.0, "reference_velocity_y": 0.0, "reference_velocity_z": 0.0,
    "reference_acceleration_x": 0.01, "reference_acceleration_y": -0.02, "reference_acceleration_z": 0.0,
    "reference_yaw": 0.15, "enable": 1.0, "reset": 0.0,
}


def load_generic_builder():
    path = ROOT / "Scripts/sunray/px4ctrl_golden_slice/build_g9_family_cfunction_sysblock.py"
    spec = importlib.util.spec_from_file_location("g9_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.INPUTS = INPUTS
    module.OUTPUTS = OUTPUTS
    return module


def embedded_c() -> str:
    header = (ROOT / "Scripts/control_platform/classic_controller_core.h").read_text(encoding="utf-8")
    source = (ROOT / "Scripts/control_platform/classic_controller_core.c").read_text(encoding="utf-8")
    guard_lines = {
        "#ifndef MOSIM_CLASSIC_CONTROLLER_CORE_H",
        "#define MOSIM_CLASSIC_CONTROLLER_CORE_H",
        "#endif",
    }
    header_lines = [
        line for line in header.splitlines()
        if line.strip() not in guard_lines
        and line.strip() not in {"#ifdef __cplusplus", "extern \"C\" {", "}"}
    ]
    source_lines = [
        line for line in source.splitlines()
        if line.strip() != '#include "classic_controller_core.h"'
    ]
    scalar_args = ",\n    ".join(f"double {name}" for name in INPUTS)
    output_args = ",\n    ".join(f"double *{name}" for name in OUTPUTS)
    assignments = [
        "    *desired_acceleration_x=out.desired_acceleration[0]; *desired_acceleration_y=out.desired_acceleration[1]; *desired_acceleration_z=out.desired_acceleration[2];",
        "    *desired_attitude_w=out.desired_attitude_wxyz[0]; *desired_attitude_x=out.desired_attitude_wxyz[1]; *desired_attitude_y=out.desired_attitude_wxyz[2]; *desired_attitude_z=out.desired_attitude_wxyz[3];",
        "    *normalized_thrust=out.normalized_thrust; *collective_thrust_n=out.collective_thrust_n;",
    ]
    for prefix in (
        "observer_position", "observer_velocity", "reference_model_position", "reference_model_velocity",
        "adaptive_position_delta", "adaptive_velocity_delta", "fractional_integral", "fractional_derivative",
    ):
        assignments.append(
            f"    *{prefix}_x=out.{prefix}[0]; *{prefix}_y=out.{prefix}[1]; *{prefix}_z=out.{prefix}[2];"
        )
    assignments.append("    *saturated=(double)out.saturated; *status_code=(double)out.status_code;")
    wrapper = f"""
void MosimClassicStepScalar(
    {scalar_args},
    {output_args})
{{
    static MosimClassicState states[6];
    static int initialized[6] = {{0}};
    MosimClassicParams params;
    MosimClassicInput in;
    MosimClassicOutput out;
    int id=(int)controller_id;
    mosim_classic_default_params(&params);
    memset(&in,0,sizeof(in));
    in.dt=dt;
    in.position[0]=position_x; in.position[1]=position_y; in.position[2]=position_z;
    in.velocity[0]=velocity_x; in.velocity[1]=velocity_y; in.velocity[2]=velocity_z;
    in.reference_position[0]=reference_position_x; in.reference_position[1]=reference_position_y; in.reference_position[2]=reference_position_z;
    in.reference_velocity[0]=reference_velocity_x; in.reference_velocity[1]=reference_velocity_y; in.reference_velocity[2]=reference_velocity_z;
    in.reference_acceleration[0]=reference_acceleration_x; in.reference_acceleration[1]=reference_acceleration_y; in.reference_acceleration[2]=reference_acceleration_z;
    in.reference_yaw=reference_yaw; in.enable=enable!=0.0; in.reset=reset!=0.0;
    if(id<1 || id>5) id=0;
    if(!initialized[id]) {{ mosim_classic_reset(&states[id]); initialized[id]=1; }}
    mosim_classic_step(id,&params,&states[id],&in,&out);
{chr(10).join(assignments)}
}}
"""
    return "\n".join(header_lines + [""] + source_lines + [wrapper]).strip() + "\n"


def layout_bridge_model(model_text: str) -> str:
    """Expand the generated bridge diagram so all scalar ports remain legible."""
    model_text = model_text.replace(
        "Diagram(coordinateSystem(extent={{-340,-620},{340,280}}",
        "Diagram(coordinateSystem(extent={{-620,-480},{620,480}}",
        1,
    )
    model_text = model_text.replace(
        "origin={0,0}, extent={{-28,-20},{28,20}}",
        "origin={0,0}, extent={{-110,-440},{110,440}}",
        1,
    )
    for index, name in enumerate(INPUTS):
        old_y = 250 - index * 7
        new_y = 420 - index * 44
        model_text = model_text.replace(
            f"origin={{-300,{old_y}}}", f"origin={{-500,{new_y}}}", 1
        )
        old_line_y = 250 - index * 6
        model_text = model_text.replace(
            f"points={{{{-250,{old_line_y}}},{{-50,{old_line_y}}}}}",
            f"points={{{{-450,{new_y}}},{{-110,{new_y}}}}}",
            1,
        )
    for index, name in enumerate(OUTPUTS):
        old_y = 160 - index * 9
        new_y = 420 - index * 24
        model_text = model_text.replace(
            f"origin={{300,{old_y}}}", f"origin={{500,{new_y}}}", 1
        )
        old_line_y = 160 - index * 7
        model_text = model_text.replace(
            f"points={{{{50,{old_line_y}}},{{250,{old_line_y}}}}}",
            f"points={{{{110,{new_y}}},{{450,{new_y}}}}}",
            1,
        )
    return model_text


def fixture_model(model_name: str, controller_id: int, controller_model: str) -> str:
    constants = {"controller_id": float(controller_id), **CONSTANTS}
    declarations: list[str] = []
    connections: list[str] = []
    for index, name in enumerate(INPUTS):
        y = 420 - index * 44
        declarations.append(
            f"  SysplorerEmbeddedCoder.Sources.Constant {name}_source(k={constants[name]}) "
            f"annotation(Placement(transformation(origin={{{{-500,{y}}}}},extent={{{{-10,-10}},{{10,10}}}})));"
        )
        connections.append(f"  connect({name}_source.y, controller.{name}_in);")
    for index, name in enumerate(OUTPUTS):
        y = 420 - index * 24
        declarations.append(
            f"  SysplorerEmbeddedCoder.Port.Outport {name} "
            f"annotation(Placement(transformation(origin={{{{500,{y}}}}},extent={{{{-10,-10}},{{10,10}}}})));"
        )
        connections.append(f"  connect(controller.{name}_out, {name});")
    return f'''model {model_name}
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.03,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-620,-480}},{{620,480}}}},grid={{2,2}})));
  {controller_model} controller annotation(Placement(transformation(origin={{0,0}},extent={{{{-110,-440}},{{110,440}}}})));
{chr(10).join(declarations)}
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
{chr(10).join(connections)}
end {model_name};
'''


def runtime_schema(controller_name: str, controller_id: int, model_name: str) -> dict[str, object]:
    first = {"controller_id_in": float(controller_id)}
    first.update({f"{name}_in": float(value) for name, value in CONSTANTS.items()})
    sequence = [dict(first) for _ in range(4)]
    sequence[0]["reset_in"] = 1.0
    return {
        "schema": "mosim.mworks_codegen_runtime_schema.v1",
        "model_name": model_name,
        "source_model_name": f"MoSim_Classic_{controller_name.upper()}_MIL",
        "input_global": "ockGbIn", "output_global": "lockGbOut",
        "input_fields": [f"{name}_in" for name in INPUTS],
        "output_fields": [f"{name}_out" for name in OUTPUTS],
        "input_sequence": sequence,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", default="Results/control_platform/classic_controller_closeout_20260717/mworks")
    args = parser.parse_args()
    result_dir = (ROOT / args.result_dir).resolve()
    model_dir, codegen_dir, sil_dir = result_dir / "models", result_dir / "codegen", result_dir / "sil"
    for path in (model_dir, codegen_dir, sil_dir):
        path.mkdir(parents=True, exist_ok=True)
    builder = load_generic_builder()
    model_name = "MoSim_Classic_CFunction_Sysblock"
    model_text = builder.build_model(model_name, codegen_dir, embedded_c(), real_as_float=False)
    model_text = model_text.replace("MosimPx4ctrlG9FamilyCStepScalar", "MosimClassicStepScalar")
    model_text = layout_bridge_model(model_text)
    model_text = model_text.replace(
        "Icon(coordinateSystem(preserveAspectRatio=false))",
        'Icon(coordinateSystem(extent={{-100,-100},{100,100}},preserveAspectRatio=false),graphics={'
        'Rectangle(fillColor={245,245,245},fillPattern=FillPattern.Solid,extent={{-100,100},{100,-100}}),'
        'Text(extent={{-86,18},{86,-18}},textString="Classic Controller",fontSize=12,'
        'textColor={0,0,0},verticalAlignment=TextAlignment.VCenter)})',
    )
    (model_dir / f"{model_name}.mo").write_text(model_text, encoding="utf-8", newline="\n")
    fixtures: dict[str, str] = {}
    for controller_id, controller_name in CONTROLLERS.items():
        fixture_name = f"MoSim_Classic_{controller_name.upper()}_MIL"
        fixtures[controller_name] = fixture_name
        (model_dir / f"{fixture_name}.mo").write_text(
            fixture_model(fixture_name, controller_id, model_name), encoding="utf-8", newline="\n"
        )
        target = sil_dir / controller_name
        target.mkdir(parents=True, exist_ok=True)
        (target / "runtime_schema.json").write_text(
            json.dumps(runtime_schema(controller_name, controller_id, model_name), indent=2) + "\n",
            encoding="utf-8", newline="\n",
        )
    manifest = {
        "schema": "mosim.classic_controller.mworks_model_build.v1",
        "model_name": model_name, "model_path": str(model_dir / f"{model_name}.mo"),
        "codegen_dir": str(codegen_dir), "inputs": INPUTS, "outputs": OUTPUTS,
        "fixtures": fixtures, "constants": CONSTANTS,
        "claim_boundary": "Graphical Sysblock source and fixed-input MIL fixtures only; live check, MIL, official codegen, SIL and Gazebo are separate gates.",
    }
    (model_dir / "BUILD_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
