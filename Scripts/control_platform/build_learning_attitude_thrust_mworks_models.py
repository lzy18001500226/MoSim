#!/usr/bin/env python3
"""Build P9 bounded learning ATTITUDE_THRUST MWORKS fixtures."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = [
    "mode", "dt",
    "position_x", "position_y", "position_z",
    "velocity_x", "velocity_y", "velocity_z",
    "attitude_w", "attitude_x", "attitude_y", "attitude_z",
    "angular_velocity_x", "angular_velocity_y", "angular_velocity_z",
    "reference_position_x", "reference_position_y", "reference_position_z",
    "reference_velocity_x", "reference_velocity_y", "reference_velocity_z",
    "reference_acceleration_x", "reference_acceleration_y", "reference_acceleration_z",
    "reference_yaw", "mass_kg", "gravity_mps2", "hover_percentage", "max_tilt_rad",
    "min_collective_thrust_n", "max_collective_thrust_n",
    "enable", "learning_enable", "reset",
]
OUTPUTS = [
    "desired_attitude_w", "desired_attitude_x", "desired_attitude_y", "desired_attitude_z",
    "desired_collective_thrust_n",
    "normalized_thrust",
    "desired_acceleration_x", "desired_acceleration_y", "desired_acceleration_z",
    "learning_action_x", "learning_action_y", "learning_action_z",
    "scheduled_gain_x", "scheduled_gain_y", "scheduled_gain_z",
    "fallback_active", "status_code", "mode_out",
]
VARIANTS = {1: "trained_neural_residual", 2: "rl_gain_scheduler"}
BASE_INPUTS = {
    "dt": 0.01,
    "position_x": 0.2, "position_y": -0.1, "position_z": 0.7,
    "velocity_x": -0.3, "velocity_y": 0.2, "velocity_z": -0.1,
    "attitude_w": 1.0, "attitude_x": 0.0, "attitude_y": 0.0, "attitude_z": 0.0,
    "angular_velocity_x": 0.0, "angular_velocity_y": 0.0, "angular_velocity_z": 0.0,
    "reference_position_x": 1.0, "reference_position_y": 0.5, "reference_position_z": 1.2,
    "reference_velocity_x": 0.1, "reference_velocity_y": -0.2, "reference_velocity_z": 0.0,
    "reference_acceleration_x": 0.05, "reference_acceleration_y": -0.04,
    "reference_acceleration_z": 0.02, "reference_yaw": 0.3,
    "mass_kg": 0.67, "gravity_mps2": 9.80665, "hover_percentage": 0.294,
    "max_tilt_rad": 0.5235987755982988,
    "min_collective_thrust_n": 0.0, "max_collective_thrust_n": 22.35,
    "enable": 1.0, "learning_enable": 1.0, "reset": 0.0,
}


def load_generic_builder():
    path = ROOT / "Scripts/sunray/px4ctrl_golden_slice/build_g9_family_cfunction_sysblock.py"
    spec = importlib.util.spec_from_file_location("g9_builder_for_p9", path)
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
    files = [
        "pid_unified_core.h", "pid_unified_core.c",
        "pid_attitude_thrust_core.h", "pid_attitude_thrust_core.c",
        "learning_control_weights.h", "learning_control_core.h", "learning_control_core.c",
        "learning_attitude_thrust_core.h", "learning_attitude_thrust_core.c",
    ]
    blobs: list[str] = [
        "#define MOSIM_LEARNING_OBSERVATION_SIZE 12\n"
        "#define MOSIM_LEARNING_ACTION_SIZE 3\n"
        "#define MOSIM_NEURAL_HIDDEN_SIZE 12\n"
        "#define MOSIM_RL_HIDDEN_SIZE 16\n"
        "#define MOSIM_LEARNING_ARTIFACT_SHA256 "
        '"4d480c6ad4738da75b4f7bfdf824658b7878ea511a52935ed2be4fff0d043e45"'
    ]
    local_headers = {f'#include "{name}"' for name in files if name.endswith(".h")}
    for name in files:
        text = (core_dir / name).read_text(encoding="utf-8")
        if name.endswith(".h"):
            blob = builder.strip_c_for_modelica_include(text, "")
        else:
            blob = builder.strip_c_for_modelica_include("", text)
        blob = "\n".join(line for line in blob.splitlines() if line.strip() not in local_headers)
        if name == "pid_attitude_thrust_core.c":
            blob = blob.replace("clamp_value", "attitude_clamp_value")
        elif name == "learning_control_core.c":
            blob = blob.replace("clamp_value", "learning_clamp_value")
            blob = blob.replace("valid_input", "learning_valid_input")
        elif name == "learning_attitude_thrust_core.c":
            blob = blob.replace("component", "learning_component")
            blob = blob.replace("set_learning_component", "learning_set_component")
        blobs.append(blob.strip())
    scalar_args = ",\n    ".join(f"double {name}" for name in INPUTS)
    output_args = ",\n    ".join(f"double *{name}" for name in OUTPUTS)
    wrapper = f'''
void MosimLearningAttitudeThrustStepScalar(
    {scalar_args},
    {output_args})
{{
    static MosimLearningAttitudeThrustState states[3];
    MosimLearningAttitudeThrustInput input;
    MosimLearningAttitudeThrustOutput output;
    int id = (int)mode;
    int result;
    memset(&input, 0, sizeof(input));
    input.mode = id; input.dt = dt;
    input.position_enu_m = vec3(position_x, position_y, position_z);
    input.velocity_enu_mps = vec3(velocity_x, velocity_y, velocity_z);
    input.attitude_enu_flu_wxyz.w = attitude_w;
    input.attitude_enu_flu_wxyz.x = attitude_x;
    input.attitude_enu_flu_wxyz.y = attitude_y;
    input.attitude_enu_flu_wxyz.z = attitude_z;
    input.angular_velocity_flu_radps = vec3(angular_velocity_x, angular_velocity_y, angular_velocity_z);
    input.reference_position_enu_m = vec3(reference_position_x, reference_position_y, reference_position_z);
    input.reference_velocity_enu_mps = vec3(reference_velocity_x, reference_velocity_y, reference_velocity_z);
    input.reference_acceleration_enu_mps2 = vec3(reference_acceleration_x, reference_acceleration_y, reference_acceleration_z);
    input.reference_yaw_enu_rad = reference_yaw;
    input.mass_kg = mass_kg; input.gravity_mps2 = gravity_mps2;
    input.hover_percentage = hover_percentage; input.max_tilt_rad = max_tilt_rad;
    input.min_collective_thrust_n = min_collective_thrust_n;
    input.max_collective_thrust_n = max_collective_thrust_n;
    input.enable = enable != 0.0; input.learning_enable = learning_enable != 0.0;
    input.reset = reset != 0.0;
    if (id < 1 || id > 2) id = 0;
    result = mosim_learning_attitude_thrust_step(&states[id], &input, &output);
    if (result != 0) {{
        memset(&output, 0, sizeof(output));
        output.control.desired_attitude_enu_flu_wxyz.w = 1.0;
        output.fallback_active = 1; output.status_code = result; output.mode = id;
    }}
    *desired_attitude_w = output.control.desired_attitude_enu_flu_wxyz.w;
    *desired_attitude_x = output.control.desired_attitude_enu_flu_wxyz.x;
    *desired_attitude_y = output.control.desired_attitude_enu_flu_wxyz.y;
    *desired_attitude_z = output.control.desired_attitude_enu_flu_wxyz.z;
    *desired_collective_thrust_n = output.control.desired_collective_thrust_n;
    *normalized_thrust = output.normalized_thrust;
    *desired_acceleration_x = output.control.desired_acceleration_enu_mps2.x;
    *desired_acceleration_y = output.control.desired_acceleration_enu_mps2.y;
    *desired_acceleration_z = output.control.desired_acceleration_enu_mps2.z;
    *learning_action_x = output.learning.values[0];
    *learning_action_y = output.learning.values[1];
    *learning_action_z = output.learning.values[2];
    *scheduled_gain_x = output.control.scheduled_gain.x;
    *scheduled_gain_y = output.control.scheduled_gain.y;
    *scheduled_gain_z = output.control.scheduled_gain.z;
    *fallback_active = (double)output.fallback_active;
    *status_code = (double)output.status_code;
    *mode_out = (double)output.mode;
}}
'''
    return "\n".join([*blobs, wrapper.strip()]) + "\n"


def fixture_model(model_name: str, mode: int, bridge_name: str) -> str:
    values = {"mode": float(mode), **BASE_INPUTS}
    declarations: list[str] = []
    connections: list[str] = []
    for index, name in enumerate(INPUTS):
        y = 330 - index * 22
        declarations.append(
            f"  SysplorerEmbeddedCoder.Sources.Constant {name}_source(k={values[name]}) "
            f"annotation(Placement(transformation(origin={{{{-280,{y}}}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(f"  connect({name}_source.y, controller.{name}_in);")
    for index, name in enumerate(OUTPUTS):
        y = 250 - index * 28
        declarations.append(
            f"  SysplorerEmbeddedCoder.Port.Outport {name} "
            f"annotation(Placement(transformation(origin={{{{280,{y}}}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(f"  connect(controller.{name}_out, {name});")
    return f'''model {model_name}
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.5,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-340,-420}},{{340,420}}}},grid={{2,2}})));
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
    parser.add_argument("--result-dir", default="Results/control_platform/p9_learning_mworks_20260717")
    args = parser.parse_args()
    result_dir = (ROOT / args.result_dir).resolve()
    model_dir = result_dir / "models"
    codegen_dir = result_dir / "generated_c"
    model_dir.mkdir(parents=True, exist_ok=True)
    codegen_dir.mkdir(parents=True, exist_ok=True)
    builder = load_generic_builder()
    bridge_name = "MoSim_P9_Learning_AttitudeThrust_CFunction_Sysblock"
    bridge = builder.build_model(bridge_name, codegen_dir, embedded_c(), real_as_float=False)
    bridge = bridge.replace("MosimPx4ctrlG9FamilyCStepScalar", "MosimLearningAttitudeThrustStepScalar")
    bridge_path = model_dir / f"{bridge_name}.mo"
    bridge_path.write_text(bridge, encoding="utf-8", newline="\n")
    fixtures: dict[str, str] = {}
    for mode, route_name in VARIANTS.items():
        fixture_name = f"MoSim_P9_{route_name.upper()}_MIL"
        fixtures[route_name] = fixture_name
        (model_dir / f"{fixture_name}.mo").write_text(
            fixture_model(fixture_name, mode, bridge_name), encoding="utf-8", newline="\n"
        )
    manifest = {
        "schema": "mosim.p9_learning_mworks_build.v1",
        "artifact_sha256": "4d480c6ad4738da75b4f7bfdf824658b7878ea511a52935ed2be4fff0d043e45",
        "bridge_model": bridge_name,
        "bridge_path": str(bridge_path),
        "fixtures": fixtures,
        "inputs": INPUTS,
        "outputs": OUTPUTS,
        "sample_time_s": 0.01,
        "stop_time_s": 0.5,
        "claim_boundary": "Fixed-size frozen-policy CFunction bridge and two time-stepped MIL fixtures. Live CheckModel, MIL, official GenerateModelCode, generated-C SIL, and Gazebo A/B are separate gates.",
    }
    (result_dir / "BUILD_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
