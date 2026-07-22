#!/usr/bin/env python3
"""Build P7 fixed-size fault-tolerant-control Sysplorer fixtures."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = [
    "mode_id", "dt", "desired_thrust", "desired_roll", "desired_pitch", "desired_yaw",
    "response_1", "response_2", "response_3", "response_4",
    "airborne", "altitude", "enable", "reset",
]
OUTPUTS = [
    "motor_command_1", "motor_command_2", "motor_command_3", "motor_command_4",
    "eta_hat_1", "eta_hat_2", "eta_hat_3", "eta_hat_4",
    "achieved_thrust", "achieved_roll", "achieved_pitch", "achieved_yaw",
    "residual_norm", "isolated_mask", "fault_count", "action",
    "allocation_saturated", "status_code",
]
VARIANTS = {
    1: "fdi", 2: "passive_ftc", 3: "active_ftc",
    4: "fault_aware_control_allocation", 5: "single_motor_safe_landing",
    6: "multi_fault_estimation_reconfiguration",
}
BASE_INPUTS = {
    "dt": 0.01, "desired_thrust": 2.4, "desired_roll": 0.04,
    "desired_pitch": -0.03, "desired_yaw": 0.02,
    "response_1": 0.57, "response_2": 0.60,
    "response_3": 0.64, "response_4": 0.59,
    "airborne": 1.0, "altitude": 1.2, "enable": 1.0, "reset": 0.0,
}
SCENARIO_OVERRIDES = {
    1: {"response_1": 0.3135},
    2: {"response_1": 0.4275},
    3: {"response_2": 0.33},
    4: {"response_3": 0.352},
    5: {"response_4": 0.118},
    6: {"response_1": 0.3135, "response_3": 0.384},
}
EXPECTED_ACTIONS = {1: 1, 2: 2, 3: 2, 4: 2, 5: 3, 6: 2}


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
        "p2_mworks_builder_for_p7",
    )


def embedded_c() -> str:
    p2 = load_p2_builder()
    generic = p2.load_generic_builder()
    source_dir = ROOT / "Scripts/control_platform"
    header = (source_dir / "fault_tolerant_control_core.h").read_text(encoding="utf-8")
    source = (source_dir / "fault_tolerant_control_core.c").read_text(encoding="utf-8")
    blob = generic.strip_c_for_modelica_include(header, source)
    blob = "\n".join(
        line for line in blob.splitlines()
        if line.strip() != '#include "fault_tolerant_control_core.h"'
    )
    scalar_args = ",\n    ".join(f"double {name}" for name in INPUTS)
    output_args = ",\n    ".join(f"double *{name}" for name in OUTPUTS)
    wrapper = f'''
void MosimFaultTolerantControlStepScalar(
    {scalar_args},
    {output_args})
{{
    static MosimFtcState states[7];
    static int initialized[7];
    MosimFtcParams params;
    MosimFtcInput input;
    MosimFtcOutput output;
    int id = (int)mode_id;
    int result;
    memset(&input, 0, sizeof(input));
    input.dt = dt;
    input.desired_wrench[0] = desired_thrust; input.desired_wrench[1] = desired_roll;
    input.desired_wrench[2] = desired_pitch; input.desired_wrench[3] = desired_yaw;
    input.measured_motor_response[0] = response_1;
    input.measured_motor_response[1] = response_2;
    input.measured_motor_response[2] = response_3;
    input.measured_motor_response[3] = response_4;
    input.airborne = airborne != 0.0; input.altitude = altitude;
    input.enable = enable != 0.0; input.reset = reset != 0.0;
    mosim_ftc_default_params(&params);
    if (id < 1 || id > 6) id = 0;
    if (!initialized[id]) {{ mosim_ftc_reset(&states[id]); initialized[id] = 1; }}
    result = mosim_ftc_step(id, &params, &states[id], &input, &output);
    if (result != 0) {{ memset(&output, 0, sizeof(output)); output.status_code = result; }}
    *motor_command_1 = output.motor_command[0]; *motor_command_2 = output.motor_command[1];
    *motor_command_3 = output.motor_command[2]; *motor_command_4 = output.motor_command[3];
    *eta_hat_1 = output.effectiveness_estimate[0]; *eta_hat_2 = output.effectiveness_estimate[1];
    *eta_hat_3 = output.effectiveness_estimate[2]; *eta_hat_4 = output.effectiveness_estimate[3];
    *achieved_thrust = output.achieved_wrench[0]; *achieved_roll = output.achieved_wrench[1];
    *achieved_pitch = output.achieved_wrench[2]; *achieved_yaw = output.achieved_wrench[3];
    *residual_norm = output.residual_norm; *isolated_mask = (double)output.isolated_mask;
    *fault_count = (double)output.fault_count; *action = (double)output.action;
    *allocation_saturated = (double)output.allocation_saturated;
    *status_code = (double)output.status_code;
}}
'''
    return "\n".join([blob.strip(), wrapper.strip()]) + "\n"


def fixture_model(model_name: str, mode_id: int, bridge_name: str) -> str:
    values = {"mode_id": float(mode_id), **BASE_INPUTS, **SCENARIO_OVERRIDES[mode_id]}
    declarations = []
    connections = []
    for index, name in enumerate(INPUTS):
        y = 280 - index * 30
        declarations.append(
            f"  SysplorerEmbeddedCoder.Sources.Constant {name}_source(k={values[name]}) "
            f"annotation(Placement(transformation(origin={{{{-280,{y}}}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(f"  connect({name}_source.y, supervisor.{name}_in);")
    for index, name in enumerate(OUTPUTS):
        y = 280 - index * 28
        declarations.append(
            f"  SysplorerEmbeddedCoder.Port.Outport {name} "
            f"annotation(Placement(transformation(origin={{{{280,{y}}}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(f"  connect(supervisor.{name}_out, {name});")
    return f'''model {model_name}
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.25,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-340,-440}},{{340,440}}}},grid={{2,2}})));
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
    parser.add_argument("--result-dir", default="Results/control_platform/p7_ftc_mworks_20260717")
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
    bridge_name = "MoSim_P7_FaultTolerantControl_CFunction_Sysblock"
    bridge = generic.build_model(bridge_name, codegen_dir, embedded_c(), real_as_float=False)
    bridge = bridge.replace("MosimPx4ctrlG9FamilyCStepScalar", "MosimFaultTolerantControlStepScalar")
    bridge_path = model_dir / f"{bridge_name}.mo"
    bridge_path.write_text(bridge, encoding="utf-8", newline="\n")
    fixtures = {}
    for mode_id, mode in VARIANTS.items():
        fixture_name = f"MoSim_P7_{mode.upper()}_MIL"
        fixtures[mode] = fixture_name
        (model_dir / f"{fixture_name}.mo").write_text(
            fixture_model(fixture_name, mode_id, bridge_name), encoding="utf-8", newline="\n"
        )
    manifest = {
        "schema": "mosim.p7_ftc_mworks_build.v1",
        "bridge_model": bridge_name,
        "bridge_path": str(bridge_path),
        "fixtures": fixtures,
        "scenario_overrides": {VARIANTS[key]: value for key, value in SCENARIO_OVERRIDES.items()},
        "expected_actions": {VARIANTS[key]: value for key, value in EXPECTED_ACTIONS.items()},
        "inputs": INPUTS,
        "outputs": OUTPUTS,
        "sample_time_s": 0.01,
        "stop_time_s": 0.25,
        "fixed_size": True,
        "reuse_basis": [
            "Models/MoSimQuadrotorModel/Controllers/Sysblocks/AWFF_InnovationGraphicalControllers.mo",
            "Config/controllers/l1_multi_fault_isolation_sysblock/default.yaml",
        ],
        "claim_boundary": "Equation-bridge plus six persistent fault fixtures. Live CheckModel/MIL, official codegen/SIL and Gazebo actuator evidence are separate gates.",
    }
    (result_dir / "BUILD_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
