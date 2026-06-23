#!/usr/bin/env python3
"""Generate the px4ctrl_core scalar CFunction Sysblock model for G6."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


INPUTS = [
    "dt",
    "position_x",
    "position_y",
    "position_z",
    "velocity_x",
    "velocity_y",
    "velocity_z",
    "attitude_w",
    "attitude_x",
    "attitude_y",
    "attitude_z",
    "angular_velocity_x",
    "angular_velocity_y",
    "angular_velocity_z",
    "reference_position_x",
    "reference_position_y",
    "reference_position_z",
    "reference_velocity_x",
    "reference_velocity_y",
    "reference_velocity_z",
    "reference_acceleration_x",
    "reference_acceleration_y",
    "reference_acceleration_z",
    "reference_yaw",
    "reference_yaw_rate",
    "imu_attitude_w",
    "imu_attitude_x",
    "imu_attitude_y",
    "imu_attitude_z",
    "imu_angular_velocity_x",
    "imu_angular_velocity_y",
    "imu_angular_velocity_z",
    "enable",
    "reset",
    "kp_x",
    "kp_y",
    "kp_z",
    "kv_x",
    "kv_y",
    "kv_z",
    "mass",
    "gravity",
    "hover_percentage",
]


OUTPUTS = [
    "desired_attitude_w",
    "desired_attitude_x",
    "desired_attitude_y",
    "desired_attitude_z",
    "normalized_thrust",
    "collective_thrust_N",
    "position_error_x",
    "position_error_y",
    "position_error_z",
    "velocity_error_x",
    "velocity_error_y",
    "velocity_error_z",
    "desired_acceleration_x",
    "desired_acceleration_y",
    "desired_acceleration_z",
    "desired_force_N_x",
    "desired_force_N_y",
    "desired_force_N_z",
    "status_code",
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def strip_c_for_modelica_include(header: str, source: str) -> str:
    header_lines: list[str] = []
    skip_extern = False
    for line in header.splitlines():
        stripped = line.strip()
        if stripped == "#ifdef __cplusplus":
            skip_extern = True
            continue
        if skip_extern:
            if stripped == "#endif":
                skip_extern = False
            continue
        if stripped.startswith("#ifndef") or stripped.startswith("#define") or stripped.startswith("#endif"):
            continue
        header_lines.append(line)

    source_lines = []
    for line in source.splitlines():
        if line.strip() == '#include "px4ctrl_core_c.h"':
            continue
        source_lines.append(line)

    return "\n".join(header_lines + [""] + source_lines).strip() + "\n"


def modelica_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def port_arrangement(names: list[str]) -> str:
    return ", ".join(names)


def port_labels(names: list[str]) -> str:
    return ",".join(f'label(text="{name}",instance="{name}")' for name in names)


def inport_decl(name: str, index: int) -> str:
    y = 120 - index * 12
    return f'''  SysplorerEmbeddedCoder.Port.Inport {name}_in 
    annotation (Placement(transformation(origin={{-220,{y}}},extent={{{{-8,-8}},{{8,8}}}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));'''


def outport_decl(name: str, index: int) -> str:
    y = 90 - index * 12
    return f'''  SysplorerEmbeddedCoder.Port.Outport {name}_out 
    annotation (Placement(transformation(origin={{220,{y}}},extent={{{{-8,-8}},{{8,8}}}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));'''


def cfunction_port_decl(direction: str, name: str) -> str:
    port_type = "Inport" if direction == "input" else "Outport"
    return f'''    SysplorerEmbeddedCoder.Port.{port_type} {name} 
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={{0,0}},extent={{{{-10,-10}},{{10,10}}}})));'''


def function_arg_decl(direction: str, name: str) -> str:
    return f'''      {direction} SysplorerEmbeddedCoder.Types.Auto {name} annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));'''


def connect_line(src: str, dst: str, index: int) -> str:
    y = 120 - index * 8
    return f'''  connect({src}, {dst}) annotation(Line(origin={{0,0}},points={{{{-180,{y}}},{{-40,{y}}}}},color={{0,0,0}}));'''


def output_connect_line(src: str, dst: str, index: int) -> str:
    y = 90 - index * 8
    return f'''  connect({src}, {dst}) annotation(Line(origin={{0,0}},points={{{{40,{y}}},{{180,{y}}}}},color={{0,0,0}}));'''


def build_model(model_name: str, out_dir: Path, include_code: str) -> str:
    input_ports = INPUTS
    output_ports = OUTPUTS
    all_c_ports = input_ports + output_ports
    external_call = (
        "MosimPx4ctrlCoreCStepScalar("
        + ",".join(input_ports + output_ports)
        + ")"
    )

    return f'''model {model_name}
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(modelType=Control,PortArrangement(Left({port_arrangement([name + "_in" for name in input_ports])}), Right({port_arrangement([name + "_out" for name in output_ports])})),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",version="26.3.0",CodeGeneration(Config = {{"code_placement":{{"mode":"Compact"}},"code_replacement":{{"standard_c_library":"C99"}},"custom_code":{{"code":{{"function_declare":{{"head":"","item_head":"","item_tail":"","tail":""}},"function_define":{{"head":"","item_head":"","item_tail":"","tail":""}},"global_variable_declare":{{"head":"","item_head":"","item_tail":"","tail":""}},"global_variable_define":{{"head":"","item_head":"","item_tail":"","tail":""}},"include":{{"head":"","item_head":"","item_tail":"","tail":""}},"macro":{{"head":"","item_head":"","item_tail":"","tail":""}},"type":{{"head":"","item_head":"","item_tail":"","tail":""}}}},"code_protection":{{"integer_division_by_zero":false,"overflow":false}}}},"data_type":{{"real_as_float":true}},"experiment":{{"task_and_sample":{{"muti_task_mode":false,"whether_to_use_prefix":false}}}},"hardware_platform":{{"largest_atomic_size":{{"floating_point":"32","integer":"32"}}}},"identifier":{{"max_length":32,"style":{{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}}}},"interface":{{"function_name":{{"initialize":"Init","step":"Step"}}}},"is_expand":{{"is_expand":false}},"optimization":{{"array_loop_threshold":5,"logical_operator":"logical"}}}}, Sim_seting = {{"sim_seting":{{"output":"{modelica_escape(str(out_dir))}"}}}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision=false,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.03,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-260,-420}},{{260,160}}}},grid={{2,2}})));

  CFunction cFunction 
    annotation (Placement(transformation(origin={{0,0}}, extent={{{{-24,-18}},{{24,18}}}})),__MWORKS(BlockSystem(SampleTime(group="D1")=0.01)));
{chr(10).join(inport_decl(name, index) for index, name in enumerate(input_ports))}
{chr(10).join(outport_decl(name, index) for index, name in enumerate(output_ports))}

  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;

  block CFunction
    annotation(__MWORKS(PortArrangement(Left({port_arrangement(input_ports)}), Right({port_arrangement(output_ports)})),PortLabels(labelType="CustomType",labels({port_labels(all_c_ports)})),BlockSystem(blockKind=BlockKind.atomic,bltBlockKind=BltBlockKind.cfunction),independentInstance=true,sourceModel=SysplorerEmbeddedCoder.Utilities.CCaller,ExternalFunctionBlock,hide=true),
      Icon(coordinateSystem(extent={{{{-200,-100}},{{200,100}}}},preserveAspectRatio=false,initialScale=0.1,grid={{2,2}}),graphics={{Rectangle(origin={{0,0}},fillColor={{255,255,255}},fillPattern=FillPattern.Solid,extent={{{{-200,100}},{{200,-100}}}}),Text(origin={{0,0}},extent={{{{-100,20}},{{100,-20}}}},textString="C",verticalAlignment=TextAlignment.VCenter),Text(origin={{0,-120}},lineColor={{0,0,0}},extent={{{{-150,20}},{{150,-20}}}},textString="%name",fontSize=14,textColor={{0,0,0}},verticalAlignment=TextAlignment.Top)}}),
      Diagram(coordinateSystem(extent={{{{-100,-100}},{{100,100}}}},preserveAspectRatio=false,initialScale=0.1,grid={{2,2}})));

    function func_CFunction
{chr(10).join(function_arg_decl("input", name) for name in input_ports)}
{chr(10).join(function_arg_decl("output", name) for name in output_ports)}
    external "C" {external_call} 
      annotation (Include="{modelica_escape(include_code)}");
    end func_CFunction;

{chr(10).join(cfunction_port_decl("input", name) for name in input_ports)}
{chr(10).join(cfunction_port_decl("output", name) for name in output_ports)}
  equation
    ({", ".join(output_ports)}) = func_CFunction({", ".join(input_ports)});
  end CFunction;

equation
{chr(10).join(connect_line(name + "_in", "cFunction." + name, index) for index, name in enumerate(input_ports))}
{chr(10).join(output_connect_line("cFunction." + name, name + "_out", index) for index, name in enumerate(output_ports))}
end {model_name};
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", default="PX4CTRL_Core_CFunction_Sysblock")
    parser.add_argument("--model-dir", default="Results/sunray_ros1/px4ctrl_g6_codegen_20260622_001/px4ctrl_core_cfunction_model")
    parser.add_argument("--codegen-dir", default="Results/sunray_ros1/px4ctrl_g6_codegen_20260622_001/px4ctrl_core_cfunction_codegen")
    args = parser.parse_args()

    root = project_root()
    model_dir = (root / args.model_dir).resolve()
    codegen_dir = (root / args.codegen_dir).resolve()
    model_dir.mkdir(parents=True, exist_ok=True)
    codegen_dir.mkdir(parents=True, exist_ok=True)

    header = (root / "Scripts" / "sunray" / "px4ctrl_golden_slice" / "px4ctrl_core_c.h").read_text(encoding="utf-8")
    source = (root / "Scripts" / "sunray" / "px4ctrl_golden_slice" / "px4ctrl_core_c.c").read_text(encoding="utf-8")
    include_code = strip_c_for_modelica_include(header, source)
    model_text = build_model(args.model_name, codegen_dir, include_code)
    model_path = model_dir / f"{args.model_name}.mo"
    model_path.write_text(model_text, encoding="utf-8", newline="\n")

    manifest = {
        "schema": "mosim.px4ctrl_g6_cfunction_model_build.v1",
        "model_name": args.model_name,
        "model_path": str(model_path),
        "codegen_dir": str(codegen_dir),
        "input_count": len(INPUTS),
        "output_count": len(OUTPUTS),
        "interface": {
            "inputs": INPUTS,
            "outputs": OUTPUTS,
            "sample_time_s": 0.01,
            "external_c_function": "MosimPx4ctrlCoreCStepScalar",
        },
        "claim_boundary": "Generated .mo source only. CheckModel and GenerateModelCode are separate gates.",
    }
    (model_dir / "BUILD_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(model_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
