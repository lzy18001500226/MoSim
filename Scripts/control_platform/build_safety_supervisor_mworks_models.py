#!/usr/bin/env python3
"""Build P6 fixed-size SafetySupervisor MWORKS fixtures."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = [
    "mode_id", "dt", "position_x", "position_y", "position_z",
    "velocity_x", "velocity_y", "velocity_z",
    "candidate_acceleration_x", "candidate_acceleration_y", "candidate_acceleration_z",
    "candidate_thrust", "candidate_tilt_rad",
    "reference_position_x", "reference_position_y", "reference_position_z",
    "home_position_x", "home_position_y", "home_position_z",
    "obstacle_distance", "command_age_s", "state_valid", "offboard_valid",
    "emergency_request", "return_request", "land_request", "enable", "reset",
]
OUTPUTS = [
    "safe_acceleration_x", "safe_acceleration_y", "safe_acceleration_z",
    "safe_thrust", "safe_reference_x", "safe_reference_y", "safe_reference_z",
    "action", "state", "active_constraints", "modified", "status_code",
]
VARIANTS = {
    1: "safety_filter", 2: "cbf", 3: "reference_governor", 4: "geofence",
    5: "emergency_stop", 6: "return_and_land", 7: "failsafe_state_machine",
}
BASE_INPUTS = {
    "dt": 0.01,
    "position_x": 0.0, "position_y": 0.0, "position_z": 1.0,
    "velocity_x": 0.0, "velocity_y": 0.0, "velocity_z": 0.0,
    "candidate_acceleration_x": 8.0, "candidate_acceleration_y": 0.0,
    "candidate_acceleration_z": 0.0, "candidate_thrust": 1.2,
    "candidate_tilt_rad": 0.8,
    "reference_position_x": 12.0, "reference_position_y": 0.0,
    "reference_position_z": 1.0,
    "home_position_x": 0.0, "home_position_y": 0.0, "home_position_z": 0.0,
    "obstacle_distance": 5.0, "command_age_s": 0.0,
    "state_valid": 1.0, "offboard_valid": 1.0,
    "emergency_request": 0.0, "return_request": 0.0, "land_request": 0.0,
    "enable": 1.0, "reset": 1.0,
}
SCENARIO_OVERRIDES = {
    1: {},
    2: {"obstacle_distance": 0.4},
    3: {},
    4: {},
    5: {"emergency_request": 1.0},
    6: {"return_request": 1.0},
    7: {"command_age_s": 1.0},
}
EXPECTED_ACTIONS = {1: 1, 2: 1, 3: 1, 4: 1, 5: 5, 6: 3, 7: 2}


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_p2_builder():
    return load_module(
        ROOT / "Scripts/control_platform/build_linear_robust_attitude_thrust_mworks_models.py",
        "p2_mworks_builder_for_p6",
    )


def embedded_c() -> str:
    p2 = load_p2_builder()
    generic = p2.load_generic_builder()
    source_dir = ROOT / "Scripts/control_platform"
    header = (source_dir / "safety_supervisor_core.h").read_text(encoding="utf-8")
    source = (source_dir / "safety_supervisor_core.c").read_text(encoding="utf-8")
    blob = generic.strip_c_for_modelica_include(header, source)
    blob = "\n".join(
        line for line in blob.splitlines()
        if line.strip() != '#include "safety_supervisor_core.h"'
    )
    scalar_args = ",\n    ".join(f"double {name}" for name in INPUTS)
    output_args = ",\n    ".join(f"double *{name}" for name in OUTPUTS)
    wrapper = f'''
void MosimSafetySupervisorStepScalar(
    {scalar_args},
    {output_args})
{{
    static MosimSafetyState states[8];
    MosimSafetyParams params;
    MosimSafetyInput input;
    MosimSafetyOutput output;
    int id = (int)mode_id;
    int result;
    memset(&input, 0, sizeof(input));
    input.dt = dt;
    input.position[0] = position_x; input.position[1] = position_y; input.position[2] = position_z;
    input.velocity[0] = velocity_x; input.velocity[1] = velocity_y; input.velocity[2] = velocity_z;
    input.candidate_acceleration[0] = candidate_acceleration_x;
    input.candidate_acceleration[1] = candidate_acceleration_y;
    input.candidate_acceleration[2] = candidate_acceleration_z;
    input.candidate_thrust = candidate_thrust; input.candidate_tilt_rad = candidate_tilt_rad;
    input.reference_position[0] = reference_position_x;
    input.reference_position[1] = reference_position_y;
    input.reference_position[2] = reference_position_z;
    input.home_position[0] = home_position_x; input.home_position[1] = home_position_y;
    input.home_position[2] = home_position_z;
    input.obstacle_distance = obstacle_distance; input.command_age_s = command_age_s;
    input.state_valid = state_valid != 0.0; input.offboard_valid = offboard_valid != 0.0;
    input.emergency_request = emergency_request != 0.0;
    input.return_request = return_request != 0.0; input.land_request = land_request != 0.0;
    input.enable = enable != 0.0; input.reset = reset != 0.0;
    mosim_safety_default_params(&params);
    if (id < 1 || id > 7) id = 0;
    result = mosim_safety_step(id, &params, &states[id], &input, &output);
    if (result != 0) {{ memset(&output, 0, sizeof(output)); output.status_code = result; }}
    *safe_acceleration_x = output.safe_acceleration[0];
    *safe_acceleration_y = output.safe_acceleration[1];
    *safe_acceleration_z = output.safe_acceleration[2];
    *safe_thrust = output.safe_thrust;
    *safe_reference_x = output.safe_reference[0];
    *safe_reference_y = output.safe_reference[1];
    *safe_reference_z = output.safe_reference[2];
    *action = (double)output.action; *state = (double)output.state;
    *active_constraints = (double)output.active_constraints;
    *modified = (double)output.modified; *status_code = (double)output.status_code;
}}
'''
    return "\n".join([blob.strip(), wrapper.strip()]) + "\n"


def fixture_model(model_name: str, mode_id: int, bridge_name: str) -> str:
    values = {"mode_id": float(mode_id), **BASE_INPUTS, **SCENARIO_OVERRIDES[mode_id]}
    declarations: list[str] = []
    connections: list[str] = []
    for index, name in enumerate(INPUTS):
        y = 300 - index * 22
        declarations.append(
            f"  SysplorerEmbeddedCoder.Sources.Constant {name}_source(k={values[name]}) "
            f"annotation(Placement(transformation(origin={{{{-280,{y}}}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(f"  connect({name}_source.y, supervisor.{name}_in);")
    for index, name in enumerate(OUTPUTS):
        y = 240 - index * 25
        declarations.append(
            f"  SysplorerEmbeddedCoder.Port.Outport {name} "
            f"annotation(Placement(transformation(origin={{{{280,{y}}}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(f"  connect(supervisor.{name}_out, {name});")
    return f'''model {model_name}
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-340,-360}},{{340,360}}}},grid={{2,2}})));
  {bridge_name} supervisor annotation(Placement(transformation(origin={{{{0,0}}}},extent={{{{-24,-24}},{{24,24}}}})));
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
    parser.add_argument("--result-dir", default="Results/control_platform/p6_safety_mworks_20260717")
    args = parser.parse_args()
    result_dir = (ROOT / args.result_dir).resolve()
    model_dir = result_dir / "models"
    codegen_dir = result_dir / "generated_c"
    model_dir.mkdir(parents=True, exist_ok=True)
    codegen_dir.mkdir(parents=True, exist_ok=True)
    p2 = load_p2_builder()
    p2.INPUTS = INPUTS
    p2.OUTPUTS = OUTPUTS
    p2.BASE_INPUTS = BASE_INPUTS
    generic = p2.load_generic_builder()
    bridge_name = "MoSim_P6_SafetySupervisor_CFunction_Sysblock"
    bridge = generic.build_model(bridge_name, codegen_dir, embedded_c(), real_as_float=False)
    bridge = bridge.replace("MosimPx4ctrlG9FamilyCStepScalar", "MosimSafetySupervisorStepScalar")
    bridge_path = model_dir / f"{bridge_name}.mo"
    bridge_path.write_text(bridge, encoding="utf-8", newline="\n")
    fixtures: dict[str, str] = {}
    for mode_id, mode in VARIANTS.items():
        fixture_name = f"MoSim_P6_{mode.upper()}_MIL"
        fixtures[mode] = fixture_name
        (model_dir / f"{fixture_name}.mo").write_text(
            fixture_model(fixture_name, mode_id, bridge_name), encoding="utf-8", newline="\n"
        )
    manifest = {
        "schema": "mosim.p6_safety_mworks_build.v1",
        "bridge_model": bridge_name,
        "bridge_path": str(bridge_path),
        "fixtures": fixtures,
        "scenario_overrides": {VARIANTS[key]: value for key, value in SCENARIO_OVERRIDES.items()},
        "expected_actions": {VARIANTS[key]: value for key, value in EXPECTED_ACTIONS.items()},
        "inputs": INPUTS,
        "outputs": OUTPUTS,
        "sample_time_s": 0.01,
        "stop_time_s": 0.2,
        "fixed_size": True,
        "claim_boundary": "Fixed-size SafetySupervisor bridge and seven trigger fixtures only. Live CheckModel/MIL, official codegen/SIL and event-driven Gazebo acceptance are separate gates.",
    }
    (result_dir / "BUILD_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
