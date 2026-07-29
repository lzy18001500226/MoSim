#!/usr/bin/env python3
"""Generate the G9 controller-family scalar CFunction Sysblock model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


INPUTS = [
    "controller_id",
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
    "reference_jerk_x",
    "reference_jerk_y",
    "reference_jerk_z",
    "reference_snap_x",
    "reference_snap_y",
    "reference_snap_z",
    "reference_yaw",
    "reference_yaw_rate",
    "reference_yaw_acceleration",
    "measurement_stamp_s",
    "imu_attitude_w",
    "imu_attitude_x",
    "imu_attitude_y",
    "imu_attitude_z",
    "imu_angular_velocity_x",
    "imu_angular_velocity_y",
    "imu_angular_velocity_z",
    "enable",
    "reset",
    "measurement_stamp_valid",
    "enable_disturbance_observer",
    "kp_x",
    "kp_y",
    "kp_z",
    "kv_x",
    "kv_y",
    "kv_z",
    "ki_x",
    "ki_y",
    "ki_z",
    "smc_lambda_x",
    "smc_lambda_y",
    "smc_lambda_z",
    "smc_eta_x",
    "smc_eta_y",
    "smc_eta_z",
    "smc_phi_x",
    "smc_phi_y",
    "smc_phi_z",
    "smc_surface_limit_x",
    "smc_surface_limit_y",
    "smc_surface_limit_z",
    "indi_gain_x",
    "indi_gain_y",
    "indi_gain_z",
    "indi_increment_limit_x",
    "indi_increment_limit_y",
    "indi_increment_limit_z",
    "indi_measured_accel_limit_x",
    "indi_measured_accel_limit_y",
    "indi_measured_accel_limit_z",
    "indi_accel_lpf_alpha",
    "nmpc_horizon_s",
    "nmpc_position_weight_x",
    "nmpc_position_weight_y",
    "nmpc_position_weight_z",
    "nmpc_velocity_weight_x",
    "nmpc_velocity_weight_y",
    "nmpc_velocity_weight_z",
    "nmpc_control_weight_x",
    "nmpc_control_weight_y",
    "nmpc_control_weight_z",
    "nmpc_accel_limit_x",
    "nmpc_accel_limit_y",
    "nmpc_accel_limit_z",
    "nmpc_increment_limit_x",
    "nmpc_increment_limit_y",
    "nmpc_increment_limit_z",
    "high_order_body_rate_limit_x",
    "high_order_body_rate_limit_y",
    "high_order_body_rate_limit_z",
    "high_order_body_accel_limit_x",
    "high_order_body_accel_limit_y",
    "high_order_body_accel_limit_z",
    "smooth_feedback_gain_x",
    "smooth_feedback_gain_y",
    "smooth_feedback_gain_z",
    "smooth_feedback_bound_x",
    "smooth_feedback_bound_y",
    "smooth_feedback_bound_z",
    "disturbance_observer_gain_x",
    "disturbance_observer_gain_y",
    "disturbance_observer_gain_z",
    "disturbance_compensation_limit_x",
    "disturbance_compensation_limit_y",
    "disturbance_compensation_limit_z",
    "l1_model_decay",
    "l1_filter_T",
    "l1_gain_x",
    "l1_gain_y",
    "l1_gain_z",
    "l1_comp_limit_x",
    "l1_comp_limit_y",
    "l1_comp_limit_z",
    "drag_feedforward_gain_x",
    "drag_feedforward_gain_y",
    "drag_feedforward_gain_z",
    "safety_accel_limit_x",
    "safety_accel_limit_y",
    "safety_accel_limit_z",
    "fault_rotor_efficiency_1",
    "fault_rotor_efficiency_2",
    "fault_rotor_efficiency_3",
    "fault_rotor_efficiency_4",
    "fault_allocation_blend",
    "fault_min_efficiency",
    "fault_thrust_comp_limit",
    "integral_limit_x",
    "integral_limit_y",
    "integral_limit_z",
    "mass",
    "gravity",
    "hover_percentage",
    "min_normalized_thrust",
    "max_normalized_thrust",
    "tilt_limit_rad",
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
    "sliding_surface_x",
    "sliding_surface_y",
    "sliding_surface_z",
    "desired_acceleration_x",
    "desired_acceleration_y",
    "desired_acceleration_z",
    "desired_body_rate_x",
    "desired_body_rate_y",
    "desired_body_rate_z",
    "desired_body_acceleration_x",
    "desired_body_acceleration_y",
    "desired_body_acceleration_z",
    "disturbance_estimate_x",
    "disturbance_estimate_y",
    "disturbance_estimate_z",
    "desired_force_N_x",
    "desired_force_N_y",
    "desired_force_N_z",
    "saturated",
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

    source_lines: list[str] = []
    for line in source.splitlines():
        if line.strip() == '#include "px4ctrl_g9_family_core_c.h"':
            continue
        source_lines.append(line)

    return "\n".join(header_lines + [""] + source_lines).strip() + "\n"


def modelica_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def port_arrangement(names: list[str]) -> str:
    return ", ".join(names)


def port_labels(names: list[str]) -> str:
    return ",".join(f'label(text="{name}",instance="{name}")' for name in names)


def port_y(index: int, count: int, span: float) -> float:
    return span / 2.0 - index * span / max(count - 1, 1)


def inport_decl(name: str, index: int, count: int, span: float) -> str:
    y = port_y(index, count, span)
    return f'''  SysplorerEmbeddedCoder.Port.Inport {name}_in
    annotation (Placement(transformation(origin={{-500,{y:.2f}}},extent={{{{-8,-8}},{{8,8}}}})),__MWORKS(BlockSystem(Type(inherit=InheritType.auto,ref="double"),Dimension(dimensionType=DimensionType.auto)=1,SampleTime(group="D1")=0.01)));'''


def outport_decl(name: str, index: int, count: int, span: float) -> str:
    y = port_y(index, count, span)
    return f'''  SysplorerEmbeddedCoder.Port.Outport {name}_out
    annotation (Placement(transformation(origin={{500,{y:.2f}}},extent={{{{-8,-8}},{{8,8}}}})),__MWORKS(BlockSystem(Type(ref="double"),Dimension=1,SampleTime(group="D1")=0.01)));'''


def cfunction_port_decl(direction: str, name: str) -> str:
    port_type = "Inport" if direction == "input" else "Outport"
    return f'''    SysplorerEmbeddedCoder.Port.{port_type} {name}
      annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)),Placement(transformation(origin={{0,0}},extent={{{{-10,-10}},{{10,10}}}})));'''


def function_arg_decl(direction: str, name: str) -> str:
    return f'''      {direction} SysplorerEmbeddedCoder.Types.Auto {name} annotation(__MWORKS(BlockSystem(Type(inherit=InheritType.none,ref="double"),Dimension(dimensionType=DimensionType.none)=1)));'''


def connect_line(src: str, dst: str, index: int, count: int, span: float) -> str:
    y = port_y(index, count, span)
    return f'''  connect({src}, {dst}) annotation(Line(points={{{{-492,{y:.2f}}},{{-80,{y:.2f}}}}},color={{0,0,127}}));'''


def output_connect_line(src: str, dst: str, index: int, count: int, span: float) -> str:
    y = port_y(index, count, span)
    return f'''  connect({src}, {dst}) annotation(Line(points={{{{80,{y:.2f}}},{{492,{y:.2f}}}}},color={{0,0,127}}));'''


def build_model(
    model_name: str,
    out_dir: Path,
    include_code: str,
    real_as_float: bool,
    external_function: str = "MosimPx4ctrlG9FamilyCStepScalar",
) -> str:
    input_ports = INPUTS
    output_ports = OUTPUTS
    diagram_span = float(max(len(input_ports) - 1, len(output_ports) - 1, 25) * 24)
    diagram_half_height = diagram_span / 2.0 + 60.0
    block_half_height = diagram_span / 2.0
    diagram_bottom = -diagram_half_height
    block_bottom = -block_half_height
    diagram_extent = "{{-620," + f"{diagram_bottom:.2f}" + "},{620," + f"{diagram_half_height:.2f}" + "}}"
    block_extent = "{{-80," + f"{block_bottom:.2f}" + "},{80," + f"{block_half_height:.2f}" + "}}"
    all_c_ports = input_ports + output_ports
    external_call = (
        external_function + "("
        + ",".join(input_ports + output_ports)
        + ")"
    )
    real_as_float_literal = "true" if real_as_float else "false"
    double_precision_literal = "false" if real_as_float else "true"
    floating_point_bits = "32" if real_as_float else "64"

    return f'''model {model_name}
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(modelType=Control,PortArrangement(Left({port_arrangement([name + "_in" for name in input_ports])}), Right({port_arrangement([name + "_out" for name in output_ports])})),BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0",version="26.3.0",CodeGeneration(Config = {{"code_placement":{{"mode":"Compact"}},"code_replacement":{{"standard_c_library":"C99"}},"custom_code":{{"code":{{"function_declare":{{"head":"","item_head":"","item_tail":"","tail":""}},"function_define":{{"head":"","item_head":"","item_tail":"","tail":""}},"global_variable_declare":{{"head":"","item_head":"","item_tail":"","tail":""}},"global_variable_define":{{"head":"","item_head":"","item_tail":"","tail":""}},"include":{{"head":"","item_head":"","item_tail":"","tail":""}},"macro":{{"head":"","item_head":"","item_tail":"","tail":""}},"type":{{"head":"","item_head":"","item_tail":"","tail":""}}}},"code_protection":{{"integer_division_by_zero":false,"overflow":false}}}},"data_type":{{"real_as_float":{real_as_float_literal}}},"experiment":{{"task_and_sample":{{"muti_task_mode":false,"whether_to_use_prefix":false}}}},"hardware_platform":{{"largest_atomic_size":{{"floating_point":"{floating_point_bits}","integer":"32"}}}},"identifier":{{"max_length":32,"style":{{"function":"camelCase","local_variable":"camelCase","macro":"camelCase","mem_var":"camelCase","type":"camelCase"}}}},"interface":{{"function_name":{{"initialize":"Init","step":"Step"}}}},"is_expand":{{"is_expand":false}},"optimization":{{"array_loop_threshold":5,"logical_operator":"logical"}}}}, Sim_seting = {{"sim_seting":{{"output":"{modelica_escape(str(out_dir))}"}}}})),Icon(coordinateSystem(preserveAspectRatio=false)),experiment(DoublePrecision={double_precision_literal},Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.03,StoreEventValue=0),Diagram(coordinateSystem(extent={diagram_extent},grid={{2,2}})));

  CFunction cFunction
    annotation (Placement(transformation(origin={{0,0}}, extent={block_extent})),__MWORKS(BlockSystem(SampleTime(group="D1")=0.01)));
{chr(10).join(inport_decl(name, index, len(input_ports), diagram_span) for index, name in enumerate(input_ports))}
{chr(10).join(outport_decl(name, index, len(output_ports), diagram_span) for index, name in enumerate(output_ports))}

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
{chr(10).join(connect_line(name + "_in", "cFunction." + name, index, len(input_ports), diagram_span) for index, name in enumerate(input_ports))}
{chr(10).join(output_connect_line("cFunction." + name, name + "_out", index, len(output_ports), diagram_span) for index, name in enumerate(output_ports))}
end {model_name};
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", default="G9_Family_CFunction_Sysblock")
    parser.add_argument("--result-dir", default="")
    parser.add_argument("--model-dir", default="")
    parser.add_argument("--codegen-dir", default="")
    parser.add_argument(
        "--double-precision-codegen",
        action="store_true",
        help="Generate the Sysblock model with real_as_float=false and DoublePrecision=true.",
    )
    args = parser.parse_args()

    root = project_root()
    result_dir = (
        Path(args.result_dir).resolve()
        if args.result_dir
        else root / "Results" / "g9" / "controller_family_attitude_thrust_v1" / "g9_family_mworks_codegen_work"
    )
    model_dir = (
        Path(args.model_dir).resolve()
        if args.model_dir
        else result_dir / "g9_family_cfunction_model"
    )
    codegen_dir = (
        Path(args.codegen_dir).resolve()
        if args.codegen_dir
        else result_dir / "g9_family_cfunction_codegen"
    )
    model_dir.mkdir(parents=True, exist_ok=True)
    codegen_dir.mkdir(parents=True, exist_ok=True)

    header = (root / "Scripts" / "sunray" / "px4ctrl_golden_slice" / "px4ctrl_g9_family_core_c.h").read_text(encoding="utf-8")
    source = (root / "Scripts" / "sunray" / "px4ctrl_golden_slice" / "px4ctrl_g9_family_core_c.c").read_text(encoding="utf-8")
    include_code = strip_c_for_modelica_include(header, source)
    real_as_float = not args.double_precision_codegen
    model_text = build_model(args.model_name, codegen_dir, include_code, real_as_float=real_as_float)
    model_path = model_dir / f"{args.model_name}.mo"
    model_path.write_text(model_text, encoding="utf-8", newline="\n")

    manifest = {
        "schema": "mosim.g9_family_cfunction_model_build.v1",
        "model_name": args.model_name,
        "model_path": str(model_path),
        "codegen_dir": str(codegen_dir),
        "codegen_precision": {
            "real_as_float": real_as_float,
            "double_precision_experiment": not real_as_float,
            "hardware_floating_point_bits": 32 if real_as_float else 64,
        },
        "input_count": len(INPUTS),
        "output_count": len(OUTPUTS),
        "interface": {
            "inputs": INPUTS,
            "outputs": OUTPUTS,
            "sample_time_s": 0.01,
            "external_c_function": "MosimPx4ctrlG9FamilyCStepScalar",
            "controller_ids": {
                "1": "official_pid",
                "2": "se3_basic",
                "3": "dfbc_basic",
                "4": "smc_boundary_layer",
                "5": "pid_indi",
                "6": "nmpc_outer",
                "7": "l1_awff",
                "8": "safety_filter",
                "9": "fault_allocation",
                "10": "dfbc_high_order",
                "11": "dfbc_smooth_robust",
            },
        },
        "claim_boundary": "Generated .mo source only. CheckModel and GenerateModelCode are separate gates.",
    }
    (model_dir / "BUILD_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(model_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
