#!/usr/bin/env python3
"""Build the P10 L1/AWFF MWORKS model and controller-specific MIL fixture.

The fixture deliberately uses the existing G9-family CFunction interface and
the controller ID 7 route. It is an executable model input, not an offline
replacement for the MWORKS evidence ladder.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "Results/control_platform/p10_mworks_gap_closeout_20260718/l1_awff_minimal"
GRAPHICAL_REVIEW = ROOT / "Results/control_platform/p10_mworks_gap_closeout_20260718/graphical_review_20260718/P10_MWORKS_GRAPHICAL_REVIEW.json"
MODEL_DIR = RESULT / "models"
CODEGEN_DIR = RESULT / "codegen"
SIL_DIR = RESULT / "sil"


def load_builder():
    path = ROOT / "Scripts/sunray/px4ctrl_golden_slice/build_g9_family_cfunction_sysblock.py"
    module = ModuleType("p10_l1_current_g9_builder")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def assert_port_surface(model_text: str, builder) -> None:
    missing_inputs = [name for name in builder.INPUTS if f" {name}_in\n" not in model_text]
    missing_outputs = [name for name in builder.OUTPUTS if f" {name}_out\n" not in model_text]
    if missing_inputs or missing_outputs:
        raise RuntimeError(
            "generated CFunction port surface is stale or incomplete: "
            f"missing_inputs={missing_inputs}, missing_outputs={missing_outputs}"
        )


def constants(builder) -> dict[str, float]:
    values = {name: 0.0 for name in builder.INPUTS}
    values.update(
        {
            "controller_id": 7.0,
            "dt": 0.01,
            "position_x": 0.0,
            "position_y": 0.0,
            "position_z": 0.2,
            "velocity_x": 0.0,
            "velocity_y": 0.0,
            "velocity_z": 0.0,
            "attitude_w": 1.0,
            "imu_attitude_w": 1.0,
            "reference_position_z": 1.0,
            "reference_velocity_x": 0.3,
            "reference_acceleration_z": 0.0,
            "measurement_stamp_s": 0.0,
            "measurement_stamp_valid": 0.0,
            "enable": 1.0,
            "reset": 0.0,
            "enable_disturbance_observer": 1.0,
            "kp_x": 2.0,
            "kp_y": 2.0,
            "kp_z": 4.0,
            "kv_x": 1.2,
            "kv_y": 1.2,
            "kv_z": 2.0,
            "ki_x": 0.05,
            "ki_y": 0.05,
            "ki_z": 0.1,
            "high_order_body_rate_limit_x": 2.0,
            "high_order_body_rate_limit_y": 2.0,
            "high_order_body_rate_limit_z": 1.0,
            "high_order_body_accel_limit_x": 20.0,
            "high_order_body_accel_limit_y": 20.0,
            "high_order_body_accel_limit_z": 8.0,
            "smooth_feedback_gain_x": 1.2,
            "smooth_feedback_gain_y": 1.2,
            "smooth_feedback_gain_z": 1.0,
            "smooth_feedback_bound_x": 0.8,
            "smooth_feedback_bound_y": 0.8,
            "smooth_feedback_bound_z": 0.7,
            "disturbance_observer_gain_x": 0.4,
            "disturbance_observer_gain_y": 0.4,
            "disturbance_observer_gain_z": 0.3,
            "disturbance_compensation_limit_x": 0.5,
            "disturbance_compensation_limit_y": 0.5,
            "disturbance_compensation_limit_z": 0.4,
            "l1_model_decay": 0.2,
            "l1_filter_T": 0.05,
            "l1_gain_x": 1.0,
            "l1_gain_y": 1.0,
            "l1_gain_z": 1.0,
            "l1_comp_limit_x": 2.0,
            "l1_comp_limit_y": 2.0,
            "l1_comp_limit_z": 2.0,
            "drag_feedforward_gain_x": 0.1,
            "drag_feedforward_gain_y": 0.1,
            "drag_feedforward_gain_z": 0.1,
            "safety_accel_limit_x": 8.0,
            "safety_accel_limit_y": 8.0,
            "safety_accel_limit_z": 8.0,
            "fault_rotor_efficiency_1": 1.0,
            "fault_rotor_efficiency_2": 1.0,
            "fault_rotor_efficiency_3": 1.0,
            "fault_rotor_efficiency_4": 1.0,
            "fault_allocation_blend": 0.0,
            "fault_min_efficiency": 0.05,
            "fault_thrust_comp_limit": 0.5,
            "mass": 1.0,
            "gravity": 9.80665,
            "hover_percentage": 0.5,
            "min_normalized_thrust": 0.0,
            "max_normalized_thrust": 1.0,
            "tilt_limit_rad": 0.6,
        }
    )
    return values


def fixture_model(builder, model_name: str, function_model: str, values: dict[str, float]) -> str:
    declarations: list[str] = []
    connections: list[str] = []
    input_count = len(builder.INPUTS)
    output_count = len(builder.OUTPUTS)
    diagram_span = float(max(input_count - 1, output_count - 1, 25) * 24)
    diagram_half_height = diagram_span / 2.0 + 60.0
    block_half_height = diagram_span / 2.0
    diagram_bottom = -diagram_half_height
    block_bottom = -block_half_height
    diagram_extent = "{{-760," + f"{diagram_bottom:.2f}" + "},{760," + f"{diagram_half_height:.2f}" + "}}"
    block_extent = "{{-80," + f"{block_bottom:.2f}" + "},{80," + f"{block_half_height:.2f}" + "}}"
    for index, name in enumerate(builder.INPUTS):
        x = -600
        y = builder.port_y(index, input_count, diagram_span)
        declarations.append(
            f"  SysplorerEmbeddedCoder.Sources.Constant {name}_source(k={values[name]}) "
            f"annotation(Placement(transformation(origin={{{x},{y:.2f}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(
            f"  connect({name}_source.y, controller.{name}_in) "
            f"annotation(Line(points={{{{{x + 8},{y:.2f}}},{{-80,{y:.2f}}}}},color={{0,0,127}}));"
        )
    for index, name in enumerate(builder.OUTPUTS):
        x = 600
        y = builder.port_y(index, output_count, diagram_span)
        declarations.append(
            f"  SysplorerEmbeddedCoder.Port.Outport {name} "
            f"annotation(Placement(transformation(origin={{{x},{y:.2f}}},extent={{{{-8,-8}},{{8,8}}}})));"
        )
        connections.append(
            f"  connect(controller.{name}_out, {name}) "
            f"annotation(Line(points={{{{80,{y:.2f}}},{{{x - 8},{y:.2f}}}}},color={{0,0,127}}));"
        )
    return f'''model {model_name}
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true,group="")=0.01,OutputInterval=0.01),SysblockVersion="1.0"),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.07,StoreEventValue=0),Diagram(coordinateSystem(extent={diagram_extent},grid={{2,2}})));
  {function_model} controller annotation(Placement(transformation(origin={{0,0}},extent={block_extent})));
{chr(10).join(declarations)}
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
{chr(10).join(connections)}
end {model_name};
'''


def main() -> int:
    builder = load_builder()
    values = constants(builder)
    for path in (MODEL_DIR, CODEGEN_DIR, SIL_DIR):
        path.mkdir(parents=True, exist_ok=True)

    header = (ROOT / "Scripts/sunray/px4ctrl_golden_slice/px4ctrl_g9_family_core_c.h").read_text(encoding="utf-8")
    source = (ROOT / "Scripts/sunray/px4ctrl_golden_slice/px4ctrl_g9_family_core_c.c").read_text(encoding="utf-8")
    include_code = builder.strip_c_for_modelica_include(header, source)
    function_name = "MoSim_P10_G10_BDE_CFunction_Sysblock"
    function_text = builder.build_model(function_name, CODEGEN_DIR, include_code, real_as_float=False)
    assert_port_surface(function_text, builder)
    function_path = MODEL_DIR / f"{function_name}.mo"
    function_path.write_text(function_text, encoding="utf-8", newline="\n")

    fixture_name = "MoSim_P10_L1_AWFF_Minimal_MIL"
    fixture_path = MODEL_DIR / f"{fixture_name}.mo"
    fixture_path.write_text(
        fixture_model(builder, fixture_name, function_name, values),
        encoding="utf-8",
        newline="\n",
    )

    input_sequence = []
    for index in range(8):
        row = {f"{name}_in": value for name, value in values.items()}
        row["measurement_stamp_s_in"] = index * values["dt"]
        input_sequence.append(row)
    manifest = {
        "schema": "mosim.p10_l1_awff_mworks_fixture.v1",
        "controller": "l1_awff_minimal",
        "controller_id": 7,
        "function_model": function_name,
        "function_model_path": str(function_path),
        "fixture_model": fixture_name,
        "fixture_model_path": str(fixture_path),
        "codegen_dir": str(CODEGEN_DIR),
        "inputs": builder.INPUTS,
        "outputs": builder.OUTPUTS,
        "constants": values,
        "sil_input_sequence": input_sequence,
        "claim_boundary": "Generated model and executable MIL fixture only; CheckModel, SimulateModel, GenerateModelCode and generated-C SIL remain separate evidence gates.",
        "graphical_review": str(GRAPHICAL_REVIEW),
        "graphical_review_scope": "Top-level visible wiring review; atomic CFunction internals are not claimed as primitive graphical expansion.",
    }
    (RESULT / "P10_L1_AWFF_BUILD_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
