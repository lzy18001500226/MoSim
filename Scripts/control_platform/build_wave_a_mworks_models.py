#!/usr/bin/env python3
"""Build Wave A CFunction Sysblock and fixed-input MIL fixtures."""

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
    "attitude_w", "attitude_x", "attitude_y", "attitude_z",
    "reference_position_x", "reference_position_y", "reference_position_z",
    "reference_velocity_x", "reference_velocity_y", "reference_velocity_z",
    "reference_acceleration_x", "reference_acceleration_y", "reference_acceleration_z",
    "reference_attitude_w", "reference_attitude_x", "reference_attitude_y", "reference_attitude_z",
    "reference_body_rate_x", "reference_body_rate_y", "reference_body_rate_z",
    "reference_yaw", "collective_thrust_n", "enable", "reset",
]
OUTPUTS = [
    "desired_attitude_w", "desired_attitude_x", "desired_attitude_y", "desired_attitude_z",
    "desired_body_rate_x", "desired_body_rate_y", "desired_body_rate_z",
    "desired_acceleration_x", "desired_acceleration_y", "desired_acceleration_z",
    "normalized_thrust", "commanded_collective_thrust_n", "command_variant", "saturated", "status_code",
]
CONTROLLERS = {1: "lqr", 2: "lqi", 3: "so3", 4: "backstepping"}
CONSTANTS = {
    "dt": 0.01,
    "position_x": 0.1, "position_y": -0.2, "position_z": 0.3,
    "velocity_x": 0.05, "velocity_y": -0.04, "velocity_z": 0.02,
    "attitude_w": 1.0, "attitude_x": 0.0, "attitude_y": 0.0, "attitude_z": 0.0,
    "reference_position_x": 1.0, "reference_position_y": -0.5, "reference_position_z": 1.2,
    "reference_velocity_x": 0.1, "reference_velocity_y": 0.0, "reference_velocity_z": 0.05,
    "reference_acceleration_x": 0.0, "reference_acceleration_y": 0.0, "reference_acceleration_z": 0.0,
    "reference_attitude_w": 0.995004165278, "reference_attitude_x": 0.0,
    "reference_attitude_y": 0.0, "reference_attitude_z": 0.099833416647,
    "reference_body_rate_x": 0.1, "reference_body_rate_y": -0.2, "reference_body_rate_z": 0.05,
    "reference_yaw": 0.2, "collective_thrust_n": 6.57, "enable": 1.0, "reset": 0.0,
}


def load_generic_builder():
    path = ROOT / "Scripts" / "sunray" / "px4ctrl_golden_slice" / "build_g9_family_cfunction_sysblock.py"
    spec = importlib.util.spec_from_file_location("g9_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.INPUTS = INPUTS
    module.OUTPUTS = OUTPUTS
    return module


def embedded_c() -> str:
    header = (ROOT / "Scripts" / "control_platform" / "wave_a_controller_core.h").read_text(encoding="utf-8")
    source = (ROOT / "Scripts" / "control_platform" / "wave_a_controller_core.c").read_text(encoding="utf-8")
    header_lines = [
        line for line in header.splitlines()
        if not line.strip().startswith(("#ifndef", "#define", "#endif"))
        and line.strip() not in {"#ifdef __cplusplus", "extern \"C\" {", "}"}
    ]
    source_lines = [line for line in source.splitlines() if line.strip() != '#include "wave_a_controller_core.h"']
    scalar_args = ",\n    ".join(f"double {name}" for name in INPUTS)
    output_args = ",\n    ".join(f"double *{name}" for name in OUTPUTS)
    wrapper = f"""
void MosimWaveAStepScalar(
    {scalar_args},
    {output_args})
{{
    static MosimWaveAState states[5];
    static int initialized[5] = {{0}};
    MosimWaveAParams params;
    MosimWaveAInput input;
    MosimWaveAOutput output;
    int id = (int)controller_id;
    mosim_wave_a_default_params(&params);
    memset(&input, 0, sizeof(input));
    input.dt = dt;
    input.position[0] = position_x; input.position[1] = position_y; input.position[2] = position_z;
    input.velocity[0] = velocity_x; input.velocity[1] = velocity_y; input.velocity[2] = velocity_z;
    input.attitude_wxyz[0] = attitude_w; input.attitude_wxyz[1] = attitude_x;
    input.attitude_wxyz[2] = attitude_y; input.attitude_wxyz[3] = attitude_z;
    input.reference_position[0] = reference_position_x; input.reference_position[1] = reference_position_y;
    input.reference_position[2] = reference_position_z;
    input.reference_velocity[0] = reference_velocity_x; input.reference_velocity[1] = reference_velocity_y;
    input.reference_velocity[2] = reference_velocity_z;
    input.reference_acceleration[0] = reference_acceleration_x;
    input.reference_acceleration[1] = reference_acceleration_y;
    input.reference_acceleration[2] = reference_acceleration_z;
    input.reference_attitude_wxyz[0] = reference_attitude_w;
    input.reference_attitude_wxyz[1] = reference_attitude_x;
    input.reference_attitude_wxyz[2] = reference_attitude_y;
    input.reference_attitude_wxyz[3] = reference_attitude_z;
    input.reference_body_rate[0] = reference_body_rate_x;
    input.reference_body_rate[1] = reference_body_rate_y;
    input.reference_body_rate[2] = reference_body_rate_z;
    input.reference_yaw = reference_yaw;
    input.collective_thrust_n = collective_thrust_n;
    input.enable = enable != 0.0; input.reset = reset != 0.0;
    if (id < 1 || id > 4) id = 0;
    if (!initialized[id]) {{ mosim_wave_a_reset(&states[id]); initialized[id] = 1; }}
    mosim_wave_a_step(id, &params, &states[id], &input, &output);
    *desired_attitude_w = output.desired_attitude_wxyz[0];
    *desired_attitude_x = output.desired_attitude_wxyz[1];
    *desired_attitude_y = output.desired_attitude_wxyz[2];
    *desired_attitude_z = output.desired_attitude_wxyz[3];
    *desired_body_rate_x = output.desired_body_rate[0];
    *desired_body_rate_y = output.desired_body_rate[1];
    *desired_body_rate_z = output.desired_body_rate[2];
    *desired_acceleration_x = output.desired_acceleration[0];
    *desired_acceleration_y = output.desired_acceleration[1];
    *desired_acceleration_z = output.desired_acceleration[2];
    *normalized_thrust = output.normalized_thrust;
    *commanded_collective_thrust_n = output.collective_thrust_n;
    *command_variant = (double)output.command_variant;
    *saturated = (double)output.saturated;
    *status_code = (double)output.status_code;
}}
"""
    return "\n".join(header_lines + [""] + source_lines + [wrapper]).strip() + "\n"


def fixture_model(model_name: str, controller_id: int, controller_model: str) -> str:
    constants = {"controller_id": float(controller_id), **CONSTANTS}
    declarations = []
    connections = []
    for index, name in enumerate(INPUTS):
        value = constants[name]
        y = 260 - index * 12
        declarations.append(
            f"  SysplorerEmbeddedCoder.Sources.Constant {name}_source(k={value}) "
            f"annotation(Placement(transformation(origin={{-260,{y}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(f"  connect({name}_source.y, controller.{name}_in);")
    for index, name in enumerate(OUTPUTS):
        y = 180 - index * 18
        declarations.append(
            f"  SysplorerEmbeddedCoder.Port.Outport {name} "
            f"annotation(Placement(transformation(origin={{260,{y}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(f"  connect(controller.{name}_out, {name});")
    return f'''model {model_name}
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.03,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-320,-180}},{{320,300}}}},grid={{2,2}})));
  {controller_model} controller annotation(Placement(transformation(origin={{0,40}},extent={{{{-25,-25}},{{25,25}}}})));
{chr(10).join(declarations)}
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
{chr(10).join(connections)}
end {model_name};
'''


def runtime_schema(controller_name: str, controller_id: int, model_name: str) -> dict[str, object]:
    inputs = {"controller_id_in": float(controller_id)}
    inputs.update({f"{name}_in": float(value) for name, value in CONSTANTS.items()})
    return {
        "schema": "mosim.mworks_codegen_runtime_schema.v1",
        "model_name": model_name,
        "source_model_name": f"MoSim_WaveA_{controller_name.upper()}_MIL",
        "input_global": "ockGbIn",
        "output_global": "lockGbOut",
        "input_fields": [f"{name}_in" for name in INPUTS],
        "output_fields": [f"{name}_out" for name in OUTPUTS],
        "input_sequence": [dict(inputs) for _ in range(4)],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", default="Results/control_platform/g5_mworks_closeout_20260716/wave_a")
    args = parser.parse_args()
    result_dir = (ROOT / args.result_dir).resolve()
    model_dir = result_dir / "models"
    codegen_dir = result_dir / "codegen"
    sil_dir = result_dir / "sil"
    model_dir.mkdir(parents=True, exist_ok=True)
    codegen_dir.mkdir(parents=True, exist_ok=True)
    sil_dir.mkdir(parents=True, exist_ok=True)
    builder = load_generic_builder()
    model_name = "MoSim_WaveA_CFunction_Sysblock"
    model_text = builder.build_model(model_name, codegen_dir, embedded_c(), real_as_float=False)
    model_text = model_text.replace("MosimPx4ctrlG9FamilyCStepScalar", "MosimWaveAStepScalar")
    model_text = "\n".join(line.rstrip() for line in model_text.splitlines()) + "\n"
    (model_dir / f"{model_name}.mo").write_text(model_text, encoding="utf-8", newline="\n")
    fixture_names = {}
    for controller_id, controller_name in CONTROLLERS.items():
        fixture_name = f"MoSim_WaveA_{controller_name.upper()}_MIL"
        fixture_names[controller_name] = fixture_name
        (model_dir / f"{fixture_name}.mo").write_text(
            fixture_model(fixture_name, controller_id, model_name), encoding="utf-8", newline="\n"
        )
        controller_sil_dir = sil_dir / controller_name
        controller_sil_dir.mkdir(parents=True, exist_ok=True)
        (controller_sil_dir / "runtime_schema.json").write_text(
            json.dumps(runtime_schema(controller_name, controller_id, model_name), indent=2) + "\n",
            encoding="utf-8",
        )
    manifest = {
        "schema": "mosim.wave_a_mworks_model_build.v1",
        "model_name": model_name,
        "model_path": str(model_dir / f"{model_name}.mo"),
        "codegen_dir": str(codegen_dir),
        "inputs": INPUTS,
        "outputs": OUTPUTS,
        "fixtures": fixture_names,
        "sil_schema_root": str(sil_dir),
        "constants": CONSTANTS,
        "claim_boundary": "Generated Sysblock CFunction equation bridge and real MIL fixtures; CheckModel, simulation and GenerateModelCode are separate gates.",
    }
    (model_dir / "BUILD_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
