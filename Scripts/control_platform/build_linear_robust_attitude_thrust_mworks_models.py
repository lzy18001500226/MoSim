#!/usr/bin/env python3
"""Build the P2 linear/robust ATTITUDE_THRUST CFunction bridge and MIL fixtures."""

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
    "reference_yaw", "mass_kg", "gravity_mps2", "hover_percentage",
    "max_tilt_rad", "min_collective_thrust_n", "max_collective_thrust_n",
    "enable", "reset",
]
OUTPUTS = [
    "desired_attitude_w", "desired_attitude_x", "desired_attitude_y", "desired_attitude_z",
    "normalized_thrust", "collective_thrust_n",
    "desired_acceleration_x", "desired_acceleration_y", "desired_acceleration_z",
    "estimated_position_x", "estimated_position_y", "estimated_position_z",
    "estimated_velocity_x", "estimated_velocity_y", "estimated_velocity_z",
    "adaptive_disturbance_x", "adaptive_disturbance_y", "adaptive_disturbance_z",
    "storage_function", "saturated", "status_code",
]
VARIANTS = {
    1: "lqg",
    2: "feedback_linearization",
    3: "passivity_based_control",
    4: "adaptive_backstepping",
}
BASE_INPUTS = {
    "dt": 0.01,
    "position_x": 0.2, "position_y": -0.1, "position_z": 0.7,
    "velocity_x": -0.3, "velocity_y": 0.2, "velocity_z": -0.1,
    "reference_position_x": 1.0, "reference_position_y": 0.5, "reference_position_z": 1.2,
    "reference_velocity_x": 0.1, "reference_velocity_y": -0.2, "reference_velocity_z": 0.0,
    "reference_acceleration_x": 0.05, "reference_acceleration_y": -0.04, "reference_acceleration_z": 0.02,
    "reference_yaw": 0.3,
    "mass_kg": 0.67, "gravity_mps2": 9.80665, "hover_percentage": 0.291,
    "max_tilt_rad": 0.5235987755982988,
    "min_collective_thrust_n": 0.0, "max_collective_thrust_n": 16.0,
    "enable": 1.0, "reset": 0.0,
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
    builder = load_generic_builder()
    core_dir = ROOT / "Scripts/control_platform"
    header = (core_dir / "linear_robust_attitude_thrust_core.h").read_text(encoding="utf-8")
    source = (core_dir / "linear_robust_attitude_thrust_core.c").read_text(encoding="utf-8")
    blob = builder.strip_c_for_modelica_include(header, source)
    blob = "\n".join(
        line for line in blob.splitlines()
        if line.strip() != '#include "linear_robust_attitude_thrust_core.h"'
    )
    scalar_args = ",\n    ".join(f"double {name}" for name in INPUTS)
    output_args = ",\n    ".join(f"double *{name}" for name in OUTPUTS)
    wrapper = f'''
void MosimLinearRobustStepScalar(
    {scalar_args},
    {output_args})
{{
    static MosimLinearRobustState states[5];
    MosimLinearRobustParams params;
    MosimLinearRobustInput input;
    MosimLinearRobustOutput output;
    int id = (int)controller_id;
    int result;
    memset(&input, 0, sizeof(input));
    input.dt = dt;
    input.position[0] = position_x; input.position[1] = position_y; input.position[2] = position_z;
    input.velocity[0] = velocity_x; input.velocity[1] = velocity_y; input.velocity[2] = velocity_z;
    input.reference_position[0] = reference_position_x;
    input.reference_position[1] = reference_position_y;
    input.reference_position[2] = reference_position_z;
    input.reference_velocity[0] = reference_velocity_x;
    input.reference_velocity[1] = reference_velocity_y;
    input.reference_velocity[2] = reference_velocity_z;
    input.reference_acceleration[0] = reference_acceleration_x;
    input.reference_acceleration[1] = reference_acceleration_y;
    input.reference_acceleration[2] = reference_acceleration_z;
    input.reference_yaw = reference_yaw;
    input.enable = enable != 0.0;
    input.reset = reset != 0.0;
    mosim_linear_robust_default_params(&params);
    params.mass_kg = mass_kg;
    params.gravity_mps2 = gravity_mps2;
    params.hover_percentage = hover_percentage;
    params.max_tilt_rad = max_tilt_rad;
    params.min_collective_thrust_n = min_collective_thrust_n;
    params.max_collective_thrust_n = max_collective_thrust_n;
    if (id < 1 || id > 4) id = 0;
    result = mosim_linear_robust_step(id, &params, &states[id], &input, &output);
    if (result != 0) {{
        memset(&output, 0, sizeof(output));
        output.desired_attitude_wxyz[0] = 1.0;
        output.status_code = result;
    }}
    *desired_attitude_w = output.desired_attitude_wxyz[0];
    *desired_attitude_x = output.desired_attitude_wxyz[1];
    *desired_attitude_y = output.desired_attitude_wxyz[2];
    *desired_attitude_z = output.desired_attitude_wxyz[3];
    *normalized_thrust = output.normalized_thrust;
    *collective_thrust_n = output.collective_thrust_n;
    *desired_acceleration_x = output.desired_acceleration[0];
    *desired_acceleration_y = output.desired_acceleration[1];
    *desired_acceleration_z = output.desired_acceleration[2];
    *estimated_position_x = output.estimated_position[0];
    *estimated_position_y = output.estimated_position[1];
    *estimated_position_z = output.estimated_position[2];
    *estimated_velocity_x = output.estimated_velocity[0];
    *estimated_velocity_y = output.estimated_velocity[1];
    *estimated_velocity_z = output.estimated_velocity[2];
    *adaptive_disturbance_x = output.adaptive_disturbance[0];
    *adaptive_disturbance_y = output.adaptive_disturbance[1];
    *adaptive_disturbance_z = output.adaptive_disturbance[2];
    *storage_function = output.storage_function;
    *saturated = (double)output.saturated;
    *status_code = (double)output.status_code;
}}
'''
    return "\n".join([blob.strip(), wrapper.strip()]) + "\n"


def fixture_model(model_name: str, controller_id: int, bridge_name: str) -> str:
    values = {"controller_id": float(controller_id), **BASE_INPUTS}
    declarations: list[str] = []
    connections: list[str] = []
    for index, name in enumerate(INPUTS):
        y = 300 - index * 22
        declarations.append(
            f"  SysplorerEmbeddedCoder.Sources.Constant {name}_source(k={values[name]}) "
            f"annotation(Placement(transformation(origin={{{{-280,{y}}}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(f"  connect({name}_source.y, controller.{name}_in);")
    for index, name in enumerate(OUTPUTS):
        y = 240 - index * 25
        declarations.append(
            f"  SysplorerEmbeddedCoder.Port.Outport {name} "
            f"annotation(Placement(transformation(origin={{{{280,{y}}}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(f"  connect(controller.{name}_out, {name});")
    return f'''model {model_name}
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-340,-360}},{{340,360}}}},grid={{2,2}})));
  {bridge_name} controller annotation(Placement(transformation(origin={{{{0,0}}}},extent={{{{-24,-24}},{{24,24}}}})));
{chr(10).join(declarations)}
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
{chr(10).join(connections)}
end {model_name};
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", default="Results/control_platform/p2_linear_robust_mworks_20260716")
    args = parser.parse_args()
    result_dir = (ROOT / args.result_dir).resolve()
    model_dir = result_dir / "models"
    codegen_dir = result_dir / "generated_c"
    model_dir.mkdir(parents=True, exist_ok=True)
    codegen_dir.mkdir(parents=True, exist_ok=True)
    builder = load_generic_builder()
    bridge_name = "MoSim_P2_LinearRobust_CFunction_Sysblock"
    bridge = builder.build_model(bridge_name, codegen_dir, embedded_c(), real_as_float=False)
    bridge = bridge.replace("MosimPx4ctrlG9FamilyCStepScalar", "MosimLinearRobustStepScalar")
    bridge_path = model_dir / f"{bridge_name}.mo"
    bridge_path.write_text(bridge, encoding="utf-8", newline="\n")
    fixtures: dict[str, str] = {}
    for controller_id, algorithm_name in VARIANTS.items():
        fixture_name = f"MoSim_P2_{algorithm_name.upper()}_MIL"
        fixtures[algorithm_name] = fixture_name
        (model_dir / f"{fixture_name}.mo").write_text(
            fixture_model(fixture_name, controller_id, bridge_name), encoding="utf-8", newline="\n"
        )
    manifest = {
        "schema": "mosim.p2_linear_robust_mworks_build.v1",
        "bridge_model": bridge_name,
        "bridge_path": str(bridge_path),
        "fixtures": fixtures,
        "inputs": INPUTS,
        "outputs": OUTPUTS,
        "sample_time_s": 0.01,
        "stop_time_s": 0.2,
        "claim_boundary": "Fixed-size CFunction equation bridge and four MIL fixtures only. Live CheckModel/MIL/codegen/SIL and behavior-equivalent graphical Sysblock models are separate gates.",
    }
    (result_dir / "BUILD_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
