#!/usr/bin/env python3
"""Build P8 fixed-size three-UAV formation-control Sysplorer fixtures."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = [
    "mode_id", "dt", "leader_x", "leader_y", "leader_z",
    "leader_vx", "leader_vy", "leader_vz", "leader_yaw",
    *[f"position_{agent}_{axis}" for agent in range(1, 4) for axis in "xyz"],
    *[f"velocity_{agent}_{axis}" for agent in range(1, 4) for axis in "xyz"],
    "healthy_1", "healthy_2", "healthy_3", "reconfigure", "enable", "reset",
]
OUTPUTS = [
    *[f"desired_position_{agent}_{axis}" for agent in range(1, 4) for axis in "xyz"],
    *[f"desired_velocity_{agent}_{axis}" for agent in range(1, 4) for axis in "xyz"],
    "minimum_pair_distance", "formation_rmse", "active_agents", "failed_mask",
    "safety_corrections", "status_code",
]
VARIANTS = {
    1: "leader_follower", 2: "virtual_structure", 3: "consensus",
    4: "containment", 5: "formation_tracking", 6: "formation_reconfiguration",
    7: "fault_tolerant_formation", 8: "formation_cbf",
    9: "distributed_mpc_formation",
}
BASE_INPUTS = {
    "dt": 0.02, "leader_x": 2.0, "leader_y": 1.0, "leader_z": 1.2,
    "leader_vx": 0.35, "leader_vy": 0.0, "leader_vz": 0.0,
    "leader_yaw": 0.4, "reconfigure": 1.0, "enable": 1.0, "reset": 0.0,
    "healthy_1": 1.0, "healthy_2": 1.0, "healthy_3": 1.0,
}
for agent in range(1, 4):
    for axis, value in zip("xyz", (0.15 * (agent - 1), -0.2 * (agent - 1), 1.0)):
        BASE_INPUTS[f"position_{agent}_{axis}"] = value
    for axis in "xyz":
        BASE_INPUTS[f"velocity_{agent}_{axis}"] = 0.0


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
        "p2_mworks_builder_for_p8",
    )


def embedded_c() -> str:
    p2 = load_p2_builder()
    generic = p2.load_generic_builder()
    source_dir = ROOT / "Scripts/control_platform"
    header = (source_dir / "formation_control_core.h").read_text(encoding="utf-8")
    source = (source_dir / "formation_control_core.c").read_text(encoding="utf-8")
    blob = generic.strip_c_for_modelica_include(header, source)
    blob = "\n".join(
        line for line in blob.splitlines()
        if line.strip() != '#include "formation_control_core.h"'
    )
    blob = blob.replace("isfinite(", "mosim_formation_isfinite(")
    embedded_compat = r'''
enum { MOSIM_FORMATION_AGENTS = 3, MOSIM_FORMATION_AXES = 3 };
static int mosim_formation_isfinite(double value) {
    return value == value &&
           value <= 1.7976931348623157e308 &&
           value >= -1.7976931348623157e308;
}
'''
    scalar_args = ",\n    ".join(f"double {name}" for name in INPUTS)
    output_args = ",\n    ".join(f"double *{name}" for name in OUTPUTS)
    assignments = []
    for agent in range(3):
        for axis, axis_name in enumerate("xyz"):
            assignments.append(
                f"    input.position[{agent}][{axis}] = position_{agent + 1}_{axis_name};"
            )
            assignments.append(
                f"    input.velocity[{agent}][{axis}] = velocity_{agent + 1}_{axis_name};"
            )
    output_assignments = []
    for agent in range(3):
        for axis, axis_name in enumerate("xyz"):
            output_assignments.append(
                f"    *desired_position_{agent + 1}_{axis_name} = output.desired_position[{agent}][{axis}];"
            )
            output_assignments.append(
                f"    *desired_velocity_{agent + 1}_{axis_name} = output.desired_velocity[{agent}][{axis}];"
            )
    wrapper = f'''
void MosimFormationControlStepScalar(
    {scalar_args},
    {output_args})
{{
    static MosimFormationState states[10];
    static int initialized[10];
    MosimFormationParams params;
    MosimFormationInput input;
    MosimFormationOutput output;
    int id = (int)mode_id;
    int result;
    memset(&input, 0, sizeof(input));
    input.dt = dt;
    input.leader_position[0] = leader_x; input.leader_position[1] = leader_y;
    input.leader_position[2] = leader_z; input.leader_velocity[0] = leader_vx;
    input.leader_velocity[1] = leader_vy; input.leader_velocity[2] = leader_vz;
    input.leader_yaw_rad = leader_yaw;
{chr(10).join(assignments)}
    input.healthy[0] = healthy_1 != 0.0; input.healthy[1] = healthy_2 != 0.0;
    input.healthy[2] = healthy_3 != 0.0; input.reconfigure = reconfigure != 0.0;
    input.enable = enable != 0.0; input.reset = reset != 0.0;
    mosim_formation_default_params(&params);
    if (id < 1 || id > 9) id = 0;
    if (!initialized[id]) {{ mosim_formation_reset(&states[id]); initialized[id] = 1; }}
    result = mosim_formation_step(id, &params, &states[id], &input, &output);
    if (result != 0) {{ memset(&output, 0, sizeof(output)); output.status_code = result; }}
{chr(10).join(output_assignments)}
    *minimum_pair_distance = output.minimum_pair_distance_m;
    *formation_rmse = output.formation_rmse_m;
    *active_agents = (double)output.active_agents;
    *failed_mask = (double)output.failed_mask;
    *safety_corrections = (double)output.safety_corrections;
    *status_code = (double)output.status_code;
}}
'''
    return "\n".join([embedded_compat.strip(), blob.strip(), wrapper.strip()]) + "\n"


def fixture_model(model_name: str, mode_id: int, bridge_name: str) -> str:
    values = {"mode_id": float(mode_id), **BASE_INPUTS}
    if mode_id == 7:
        values["healthy_2"] = 0.0
    declarations, connections = [], []
    for index, name in enumerate(INPUTS):
        column, row = index // 17, index % 17
        x, y = -310 + column * 90, 260 - row * 32
        declarations.append(
            f"  SysplorerEmbeddedCoder.Sources.Constant {name}_source(k={values[name]}) "
            f"annotation(Placement(transformation(origin={{{{{x},{y}}}}},extent={{{{-7,-7}},{{7,7}}}})));"
        )
        connections.append(f"  connect({name}_source.y, formation.{name}_in);")
    for index, name in enumerate(OUTPUTS):
        column, row = index // 13, index % 13
        x, y = 260 + column * 85, 250 - row * 38
        declarations.append(
            f"  SysplorerEmbeddedCoder.Port.Outport {name} "
            f"annotation(Placement(transformation(origin={{{{{x},{y}}}}},extent={{{{-7,-7}},{{7,7}}}})));"
        )
        connections.append(f"  connect(formation.{name}_out, {name});")
    return f'''model {model_name}
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.02,OutputInterval=0.02),SysblockVersion="1.0"),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.02,Interval=0.02,StartTime=0,StopTime=0.4,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-420,-340}},{{430,340}}}},grid={{2,2}})));
  {bridge_name} formation annotation(Placement(transformation(origin={{{{40,0}}}},extent={{{{-28,-28}},{{28,28}}}})));
{chr(10).join(declarations)}
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
{chr(10).join(connections)}
end {model_name};
'''


def set_bridge_sample_time(model_text: str, sample_time_s: float) -> str:
    """Align the generic 100 Hz bridge metadata with the 50 Hz formation lane."""
    sample = f"{sample_time_s:.2f}"
    replacements = {
        'SampleTime(auto=true,group="")=0.01,OutputInterval=0.01':
            f'SampleTime(auto=true,group="")={sample},OutputInterval={sample}',
        'IntegratorStep=0.01,Interval=0.01':
            f'IntegratorStep={sample},Interval={sample}',
        'SampleTime(group="D1")=0.01': f'SampleTime(group="D1")={sample}',
    }
    for old, new in replacements.items():
        model_text = model_text.replace(old, new)
    return model_text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", default="Results/control_platform/p8_formation_mworks_20260717")
    args = parser.parse_args()
    result_dir = (ROOT / args.result_dir).resolve()
    model_dir, codegen_dir = result_dir / "models", result_dir / "generated_c"
    model_dir.mkdir(parents=True, exist_ok=True)
    codegen_dir.mkdir(parents=True, exist_ok=True)
    p2 = load_p2_builder()
    p2.INPUTS, p2.OUTPUTS, p2.BASE_INPUTS = INPUTS, OUTPUTS, BASE_INPUTS
    generic = p2.load_generic_builder()
    bridge_name = "MoSim_P8_FormationControl_CFunction_Sysblock"
    bridge = generic.build_model(bridge_name, codegen_dir, embedded_c(), real_as_float=False)
    bridge = bridge.replace("MosimPx4ctrlG9FamilyCStepScalar", "MosimFormationControlStepScalar")
    bridge = set_bridge_sample_time(bridge, BASE_INPUTS["dt"])
    bridge_path = model_dir / f"{bridge_name}.mo"
    bridge_path.write_text(bridge, encoding="utf-8", newline="\n")
    fixtures = {}
    for mode_id, mode in VARIANTS.items():
        fixture_name = f"MoSim_P8_{mode.upper()}_MIL"
        fixtures[mode] = fixture_name
        (model_dir / f"{fixture_name}.mo").write_text(
            fixture_model(fixture_name, mode_id, bridge_name), encoding="utf-8", newline="\n")
    manifest = {
        "schema": "mosim.p8_formation_mworks_build.v1",
        "bridge_model": bridge_name,
        "bridge_path": str(bridge_path),
        "fixtures": fixtures,
        "inputs": INPUTS,
        "outputs": OUTPUTS,
        "sample_time_s": 0.02,
        "stop_time_s": 0.4,
        "fixed_agent_count": 3,
        "claim_boundary": "Equation bridge plus nine graphical fixed-size formation fixtures. Live MWORKS check/simulation and official codegen/SIL remain separate gates.",
    }
    (result_dir / "BUILD_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
