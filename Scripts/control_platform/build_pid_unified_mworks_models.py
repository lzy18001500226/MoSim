#!/usr/bin/env python3
"""Build the unified PID CFunction bridge and fixed-input MWORKS fixtures."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = [
    "controller_id", "setpoint", "measurement", "inner_measurement",
    "feedforward", "schedule", "fuzzy_error", "neural_residual",
    "dt", "enable", "reset",
]
OUTPUTS = [
    "command", "outer_command", "unsaturated_command", "integral",
    "scheduled_gain", "saturated", "status_code",
]
VARIANTS = {
    1: "cascade_pid",
    2: "gain_scheduled_pid",
    3: "fuzzy_pid",
    4: "neural_pid",
    5: "anti_windup",
    6: "feedforward_profile",
}
BASE_CONSTANTS = {
    "setpoint": 0.5,
    "measurement": 0.1,
    "inner_measurement": 0.05,
    "feedforward": 0.3,
    "schedule": 0.5,
    "fuzzy_error": 0.4,
    "neural_residual": 0.1,
    "dt": 0.01,
    "enable": 1.0,
    "reset": 0.0,
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
    header = (ROOT / "Scripts/control_platform/pid_unified_core.h").read_text(encoding="utf-8")
    source = (ROOT / "Scripts/control_platform/pid_unified_core.c").read_text(encoding="utf-8")
    header_lines = [
        line for line in header.splitlines()
        if not line.strip().startswith(("#ifndef", "#define", "#endif"))
        and line.strip() not in {"#ifdef __cplusplus", 'extern "C" {', "}"}
    ]
    source_lines = [
        line for line in source.splitlines()
        if line.strip() != '#include "pid_unified_core.h"'
    ]
    scalar_args = ",\n    ".join(f"double {name}" for name in INPUTS)
    output_args = ",\n    ".join(f"double *{name}" for name in OUTPUTS)
    wrapper = f"""
static void MosimPidConfigure(int id, MosimPidConfig *outer, MosimPidConfig *inner)
{{
    mosim_pid_default_config(outer);
    mosim_pid_default_config(inner);
    outer->kp = 1.2; outer->ki = 0.8; outer->kd = 0.1;
    outer->output_min = -1.0; outer->output_max = 1.0;
    outer->integral_min = -0.5; outer->integral_max = 0.5;
    outer->anti_windup_gain = 0.4; outer->derivative_filter_tau = 0.05;
    inner->kp = 1.5; inner->ki = 0.4; inner->kd = 0.05;
    inner->output_min = -1.0; inner->output_max = 1.0;
    inner->integral_min = -0.5; inner->integral_max = 0.5;
    inner->anti_windup_gain = 0.4; inner->derivative_filter_tau = 0.03;
    if (id == 2) outer->schedule_gain = 0.4;
    if (id == 3) outer->fuzzy_gain = 0.3;
    if (id == 4) {{ outer->neural_gain = 0.2; outer->neural_residual_limit = 0.25; }}
    if (id == 5) outer->anti_windup_gain = 1.0;
    if (id == 6) outer->feedforward_gain = 0.5;
}}

void MosimPidUnifiedStepScalar(
    {scalar_args},
    {output_args})
{{
    static MosimPidState states[7];
    static MosimCascadePidState cascade_states[7];
    MosimPidConfig outer, inner;
    MosimPidInput input;
    MosimPidOutput output;
    MosimCascadePidInput cascade_input;
    MosimCascadePidOutput cascade_output;
    int id = (int)controller_id;
    int result;
    if (id < 1 || id > 6) id = 0;
    MosimPidConfigure(id, &outer, &inner);
    memset(&input, 0, sizeof(input));
    input.setpoint=setpoint; input.measurement=measurement;
    input.feedforward=feedforward; input.schedule=schedule;
    input.fuzzy_error=fuzzy_error; input.neural_residual=neural_residual;
    input.dt=dt; input.enable=enable != 0.0; input.reset=reset != 0.0;
    *outer_command = 0.0;
    if (id == 1) {{
        memset(&cascade_input, 0, sizeof(cascade_input));
        cascade_input.outer_reference=setpoint;
        cascade_input.outer_measurement=measurement;
        cascade_input.inner_measurement=inner_measurement;
        cascade_input.feedforward=feedforward;
        cascade_input.schedule=schedule;
        cascade_input.fuzzy_error=fuzzy_error;
        cascade_input.neural_residual=neural_residual;
        cascade_input.dt=dt; cascade_input.enable=enable != 0.0;
        cascade_input.reset=reset != 0.0;
        result=mosim_cascade_pid_step(&outer,&inner,&cascade_states[id],&cascade_input,&cascade_output);
        *command=cascade_output.command; *outer_command=cascade_output.outer_command;
        *unsaturated_command=cascade_output.command; *integral=cascade_states[id].inner.integral;
        *scheduled_gain=1.0; *saturated=(double)cascade_output.saturated;
        *status_code=(double)(result != 0 ? result : cascade_output.status_code);
        return;
    }}
    result=mosim_pid_step(&outer,&states[id],&input,&output);
    *command=output.command; *unsaturated_command=output.unsaturated_command;
    *integral=output.integral; *scheduled_gain=output.scheduled_gain;
    *saturated=(double)output.saturated;
    *status_code=(double)(result != 0 ? result : output.status_code);
}}
"""
    return "\n".join(header_lines + [""] + source_lines + [wrapper]).strip() + "\n"


def fixture_model(model_name: str, controller_id: int, controller_model: str) -> str:
    constants = {"controller_id": float(controller_id), **BASE_CONSTANTS}
    if controller_id == 5:
        constants["setpoint"] = 2.0
    declarations: list[str] = []
    connections: list[str] = []
    for index, name in enumerate(INPUTS):
        y = 130 - index * 24
        declarations.append(
            f"  SysplorerEmbeddedCoder.Sources.Constant {name}_source(k={constants[name]}) "
            f"annotation(Placement(transformation(origin={{{{-210,{y}}}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(f"  connect({name}_source.y, controller.{name}_in);")
    for index, name in enumerate(OUTPUTS):
        y = 90 - index * 28
        declarations.append(
            f"  SysplorerEmbeddedCoder.Port.Outport {name} "
            f"annotation(Placement(transformation(origin={{{{210,{y}}}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(f"  connect(controller.{name}_out, {name});")
    return f'''model {model_name}
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-260,-180}},{{260,180}}}},grid={{2,2}})));
  {controller_model} controller annotation(Placement(transformation(origin={{{{0,0}}}},extent={{{{-24,-24}},{{24,24}}}})));
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
    parser.add_argument("--result-dir", default="Results/control_platform/p1_pid_mworks_20260716")
    args = parser.parse_args()
    result_dir = (ROOT / args.result_dir).resolve()
    model_dir = result_dir / "models"
    codegen_dir = result_dir / "codegen"
    model_dir.mkdir(parents=True, exist_ok=True)
    codegen_dir.mkdir(parents=True, exist_ok=True)
    builder = load_generic_builder()
    bridge_name = "MoSim_PID_Unified_CFunction_Sysblock"
    bridge = builder.build_model(bridge_name, codegen_dir, embedded_c(), real_as_float=False)
    bridge = bridge.replace("MosimPx4ctrlG9FamilyCStepScalar", "MosimPidUnifiedStepScalar")
    (model_dir / f"{bridge_name}.mo").write_text(bridge, encoding="utf-8", newline="\n")
    fixtures: dict[str, str] = {}
    for controller_id, algorithm_id in VARIANTS.items():
        fixture_name = f"MoSim_PID_{algorithm_id.upper()}_MIL"
        fixtures[algorithm_id] = fixture_name
        (model_dir / f"{fixture_name}.mo").write_text(
            fixture_model(fixture_name, controller_id, bridge_name), encoding="utf-8", newline="\n"
        )
    manifest = {
        "schema": "mosim.pid_unified_mworks_build.v1",
        "bridge_model": bridge_name,
        "bridge_path": str(model_dir / f"{bridge_name}.mo"),
        "fixtures": fixtures,
        "inputs": INPUTS,
        "outputs": OUTPUTS,
        "claim_boundary": "Generated CFunction equation bridge and fixed-input MIL fixtures only; live load/check/simulate and graphical counterparts are separate gates.",
    }
    (model_dir / "BUILD_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
