#!/usr/bin/env python3
"""Build the full PID ATTITUDE_THRUST CFunction bridge and six MIL fixtures."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = [
    "algorithm_id", "dt",
    "position_x", "position_y", "position_z",
    "velocity_x", "velocity_y", "velocity_z",
    "attitude_w", "attitude_x", "attitude_y", "attitude_z",
    "angular_velocity_x", "angular_velocity_y", "angular_velocity_z",
    "reference_position_x", "reference_position_y", "reference_position_z",
    "reference_velocity_x", "reference_velocity_y", "reference_velocity_z",
    "reference_acceleration_x", "reference_acceleration_y", "reference_acceleration_z",
    "reference_yaw",
    "mass_kg", "gravity_mps2", "max_tilt_rad",
    "min_collective_thrust_n", "max_collective_thrust_n",
    "schedule_x", "schedule_y", "schedule_z",
    "fuzzy_error_x", "fuzzy_error_y", "fuzzy_error_z",
    "neural_residual_x", "neural_residual_y", "neural_residual_z",
    "enable", "reset",
]
OUTPUTS = [
    "desired_attitude_w", "desired_attitude_x", "desired_attitude_y", "desired_attitude_z",
    "desired_collective_thrust_n",
    "desired_acceleration_x", "desired_acceleration_y", "desired_acceleration_z",
    "position_error_x", "position_error_y", "position_error_z",
    "velocity_error_x", "velocity_error_y", "velocity_error_z",
    "scheduled_gain_x", "scheduled_gain_y", "scheduled_gain_z",
    "saturated", "status_code", "algorithm_id_out",
]
VARIANTS = {
    1: "cascade_pid",
    2: "gain_scheduled_pid",
    3: "fuzzy_pid",
    4: "neural_pid",
    5: "anti_windup",
    6: "feedforward_profile",
}
BASE_INPUTS = {
    "dt": 0.01,
    "position_x": 0.0, "position_y": 0.0, "position_z": 0.0,
    "velocity_x": 0.0, "velocity_y": 0.0, "velocity_z": 0.0,
    "attitude_w": 1.0, "attitude_x": 0.0, "attitude_y": 0.0, "attitude_z": 0.0,
    "angular_velocity_x": 0.0, "angular_velocity_y": 0.0, "angular_velocity_z": 0.0,
    "reference_position_x": 1.0, "reference_position_y": -0.5, "reference_position_z": 0.8,
    "reference_velocity_x": 0.2, "reference_velocity_y": -0.1, "reference_velocity_z": 0.0,
    "reference_acceleration_x": 0.6, "reference_acceleration_y": -0.3, "reference_acceleration_z": 0.2,
    "reference_yaw": 0.3,
    "mass_kg": 1.0, "gravity_mps2": 9.80665, "max_tilt_rad": 0.5235987755982988,
    "min_collective_thrust_n": 0.0, "max_collective_thrust_n": 19.6133,
    "schedule_x": 0.5, "schedule_y": 0.4, "schedule_z": 0.3,
    "fuzzy_error_x": 0.4, "fuzzy_error_y": -0.3, "fuzzy_error_z": 0.2,
    "neural_residual_x": 0.1, "neural_residual_y": -0.2, "neural_residual_z": 0.3,
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
    pid_header = (core_dir / "pid_unified_core.h").read_text(encoding="utf-8")
    pid_source = (core_dir / "pid_unified_core.c").read_text(encoding="utf-8")
    attitude_header = (core_dir / "pid_attitude_thrust_core.h").read_text(encoding="utf-8")
    attitude_source = (core_dir / "pid_attitude_thrust_core.c").read_text(encoding="utf-8")
    pid_blob = builder.strip_c_for_modelica_include(pid_header, pid_source)
    attitude_source = attitude_source.replace("clamp_value", "attitude_clamp_value")
    attitude_blob = builder.strip_c_for_modelica_include(attitude_header, attitude_source)
    local_includes = {'#include "pid_unified_core.h"', '#include "pid_attitude_thrust_core.h"'}
    pid_blob = "\n".join(
        line for line in pid_blob.splitlines() if line.strip() not in local_includes
    )
    attitude_blob = "\n".join(
        line for line in attitude_blob.splitlines() if line.strip() not in local_includes
    )
    scalar_args = ",\n    ".join(f"double {name}" for name in INPUTS)
    output_args = ",\n    ".join(f"double *{name}" for name in OUTPUTS)
    wrapper = f'''
void MosimPidAttitudeThrustStepScalar(
    {scalar_args},
    {output_args})
{{
    static MosimPidAttitudeThrustState states[7];
    MosimPidAttitudeThrustParams params;
    MosimPidAttitudeThrustInput input;
    MosimPidAttitudeThrustOutput output;
    int id = (int)algorithm_id;
    memset(&input, 0, sizeof(input));
    input.algorithm_id = id;
    input.dt = dt;
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
    input.schedule = vec3(schedule_x, schedule_y, schedule_z);
    input.fuzzy_error = vec3(fuzzy_error_x, fuzzy_error_y, fuzzy_error_z);
    input.neural_residual = vec3(neural_residual_x, neural_residual_y, neural_residual_z);
    input.enable = enable != 0.0;
    input.reset = reset != 0.0;
    mosim_pid_attitude_thrust_default_params(id, &params);
    params.mass_kg = mass_kg;
    params.gravity_mps2 = gravity_mps2;
    params.max_tilt_rad = max_tilt_rad;
    params.min_collective_thrust_n = min_collective_thrust_n;
    params.max_collective_thrust_n = max_collective_thrust_n;
    if (id < 1 || id > 6 || mosim_pid_attitude_thrust_step(&params, &states[id], &input, &output) != 0) {{
        memset(&output, 0, sizeof(output));
        output.desired_attitude_enu_flu_wxyz.w = 1.0;
        output.status_code = -1;
    }}
    *desired_attitude_w = output.desired_attitude_enu_flu_wxyz.w;
    *desired_attitude_x = output.desired_attitude_enu_flu_wxyz.x;
    *desired_attitude_y = output.desired_attitude_enu_flu_wxyz.y;
    *desired_attitude_z = output.desired_attitude_enu_flu_wxyz.z;
    *desired_collective_thrust_n = output.desired_collective_thrust_n;
    *desired_acceleration_x = output.desired_acceleration_enu_mps2.x;
    *desired_acceleration_y = output.desired_acceleration_enu_mps2.y;
    *desired_acceleration_z = output.desired_acceleration_enu_mps2.z;
    *position_error_x = output.position_error_enu_m.x;
    *position_error_y = output.position_error_enu_m.y;
    *position_error_z = output.position_error_enu_m.z;
    *velocity_error_x = output.velocity_error_enu_mps.x;
    *velocity_error_y = output.velocity_error_enu_mps.y;
    *velocity_error_z = output.velocity_error_enu_mps.z;
    *scheduled_gain_x = output.scheduled_gain.x;
    *scheduled_gain_y = output.scheduled_gain.y;
    *scheduled_gain_z = output.scheduled_gain.z;
    *saturated = (double)output.saturated;
    *status_code = (double)output.status_code;
    *algorithm_id_out = (double)output.algorithm_id;
}}
'''
    return "\n".join([pid_blob.strip(), attitude_blob.strip(), wrapper.strip()]) + "\n"


def fixture_model(model_name: str, algorithm_id: int, bridge_name: str) -> str:
    values = {"algorithm_id": float(algorithm_id), **BASE_INPUTS}
    declarations: list[str] = []
    connections: list[str] = []
    for index, name in enumerate(INPUTS):
        y = 360 - index * 20
        declarations.append(
            f"  SysplorerEmbeddedCoder.Sources.Constant {name}_source(k={values[name]}) "
            f"annotation(Placement(transformation(origin={{{{-280,{y}}}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(f"  connect({name}_source.y, controller.{name}_in);")
    for index, name in enumerate(OUTPUTS):
        y = 260 - index * 24
        declarations.append(
            f"  SysplorerEmbeddedCoder.Port.Outport {name} "
            f"annotation(Placement(transformation(origin={{{{280,{y}}}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(f"  connect(controller.{name}_out, {name});")
    return f'''model {model_name}
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-340,-420}},{{340,420}}}},grid={{2,2}})));
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
    parser.add_argument("--result-dir", default="Results/control_platform/p1_pid_attitude_thrust_mworks_20260716")
    args = parser.parse_args()
    result_dir = (ROOT / args.result_dir).resolve()
    model_dir = result_dir / "models"
    codegen_dir = result_dir / "generated_c_v2"
    model_dir.mkdir(parents=True, exist_ok=True)
    codegen_dir.mkdir(parents=True, exist_ok=True)
    builder = load_generic_builder()
    bridge_name = "MoSim_PID_AttitudeThrust_CFunction_Sysblock"
    bridge = builder.build_model(bridge_name, codegen_dir, embedded_c(), real_as_float=False)
    bridge = bridge.replace("MosimPx4ctrlG9FamilyCStepScalar", "MosimPidAttitudeThrustStepScalar")
    bridge = "\n".join(line.rstrip() for line in bridge.splitlines()) + "\n"
    bridge_path = model_dir / f"{bridge_name}.mo"
    bridge_path.write_text(bridge, encoding="utf-8", newline="\n")
    fixtures: dict[str, str] = {}
    for algorithm_id, algorithm_name in VARIANTS.items():
        fixture_name = f"MoSim_PID_{algorithm_name.upper()}_ATTITUDE_THRUST_MIL"
        fixtures[algorithm_name] = fixture_name
        (model_dir / f"{fixture_name}.mo").write_text(
            fixture_model(fixture_name, algorithm_id, bridge_name),
            encoding="utf-8", newline="\n",
        )
    manifest = {
        "schema": "mosim.pid_attitude_thrust_mworks_build.v1",
        "bridge_model": bridge_name,
        "bridge_path": str(bridge_path),
        "fixtures": fixtures,
        "inputs": INPUTS,
        "outputs": OUTPUTS,
        "sample_time_s": 0.01,
        "stop_time_s": 0.2,
        "claim_boundary": "Full fixed-size ATTITUDE_THRUST CFunction equation bridge and six MIL fixtures. Existing six graphical PID models are the behavior-equivalent algorithm topology counterparts; live CheckModel, MIL, official codegen, and SIL are separate gates.",
    }
    manifest_path = result_dir / "BUILD_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
