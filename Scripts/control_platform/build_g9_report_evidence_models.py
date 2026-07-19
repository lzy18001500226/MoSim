#!/usr/bin/env python3
"""Build route-specific G9 report fixtures around the frozen shared core.

The generated MIL fixtures expose a compact top-level signal chain while the
route adapter supplies the full scalar ABI expected by the existing G9
CFunction model. Separate small topology models provide readable report
diagrams; they are documentation fixtures, not numerical authorities.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE_MODEL = (
    ROOT
    / "Results/g9/controller_family_attitude_thrust_v1"
    / "g9_family_mworks_codegen_20260630_work/g9_family_cfunction_model"
    / "G9_Family_CFunction_Sysblock.mo"
)
OUTPUT_ROOT = (
    ROOT
    / "Results/control_platform/controller_document_evidence_20260720"
    / "G9_CORE_COMPARISON/g9_route_report_evidence"
)

ROUTES = {
    "se3_basic": (2, "SE3"),
    "dfbc_basic": (3, "DFBC"),
    "smc_boundary_layer": (4, "SMC_BOUNDARY_LAYER"),
    "pid_indi": (5, "PID_INDI"),
    "nmpc_outer": (6, "NMPC_OUTER"),
}

EXPOSED_INPUTS = [
    "dt",
    "position_x", "position_y", "position_z",
    "velocity_x", "velocity_y", "velocity_z",
    "reference_position_x", "reference_position_y", "reference_position_z",
    "reference_velocity_x", "reference_velocity_y", "reference_velocity_z",
    "reference_acceleration_x", "reference_acceleration_y", "reference_acceleration_z",
    "enable", "reset",
]

SELECTED_OUTPUTS = [
    "normalized_thrust",
    "desired_acceleration_x", "desired_acceleration_y", "desired_acceleration_z",
    "position_error_x", "position_error_y", "position_error_z",
    "sliding_surface_x", "sliding_surface_y", "sliding_surface_z",
    "status_code",
]

FIXTURE_VALUES = {
    "dt": 0.01,
    "position_x": 0.10, "position_y": -0.05, "position_z": 0.80,
    "velocity_x": 0.02, "velocity_y": -0.01, "velocity_z": 0.01,
    "reference_position_x": 0.25, "reference_position_y": 0.10,
    "reference_position_z": 1.00,
    "reference_velocity_x": 0.0, "reference_velocity_y": 0.0,
    "reference_velocity_z": 0.0,
    "reference_acceleration_x": 0.01, "reference_acceleration_y": -0.02,
    "reference_acceleration_z": 0.0,
    "enable": 1.0, "reset": 0.0,
}

DEFAULTS = {
    "controller_id": 0.0,
    "attitude_w": 1.0, "attitude_x": 0.0, "attitude_y": 0.0, "attitude_z": 0.0,
    "angular_velocity_x": 0.0, "angular_velocity_y": 0.0, "angular_velocity_z": 0.0,
    "reference_jerk_x": 0.0, "reference_jerk_y": 0.0, "reference_jerk_z": 0.0,
    "reference_snap_x": 0.0, "reference_snap_y": 0.0, "reference_snap_z": 0.0,
    "reference_yaw": 0.15, "reference_yaw_rate": 0.0,
    "reference_yaw_acceleration": 0.0, "measurement_stamp_s": 0.0,
    "imu_attitude_w": 1.0, "imu_attitude_x": 0.0,
    "imu_attitude_y": 0.0, "imu_attitude_z": 0.0,
    "imu_angular_velocity_x": 0.0, "imu_angular_velocity_y": 0.0,
    "imu_angular_velocity_z": 0.0, "measurement_stamp_valid": 0.0,
    "enable_disturbance_observer": 1.0,
    "kp_x": 1.5, "kp_y": 1.5, "kp_z": 1.5,
    "kv_x": 1.5, "kv_y": 1.5, "kv_z": 1.5,
    "ki_x": 0.0, "ki_y": 0.0, "ki_z": 0.0,
    "smc_lambda_x": 2.0, "smc_lambda_y": 2.0, "smc_lambda_z": 2.0,
    "smc_eta_x": 0.1, "smc_eta_y": 0.1, "smc_eta_z": 0.05,
    "smc_phi_x": 0.4, "smc_phi_y": 0.4, "smc_phi_z": 0.35,
    "smc_surface_limit_x": 3.0, "smc_surface_limit_y": 3.0,
    "smc_surface_limit_z": 2.5,
    "indi_gain_x": 0.12, "indi_gain_y": 0.12, "indi_gain_z": 0.08,
    "indi_increment_limit_x": 0.35, "indi_increment_limit_y": 0.35,
    "indi_increment_limit_z": 0.20,
    "indi_measured_accel_limit_x": 6.0, "indi_measured_accel_limit_y": 6.0,
    "indi_measured_accel_limit_z": 4.0, "indi_accel_lpf_alpha": 0.25,
    "nmpc_horizon_s": 0.25,
    "nmpc_position_weight_x": 1.0, "nmpc_position_weight_y": 1.0,
    "nmpc_position_weight_z": 1.0,
    "nmpc_velocity_weight_x": 0.05, "nmpc_velocity_weight_y": 0.05,
    "nmpc_velocity_weight_z": 0.05,
    "nmpc_control_weight_x": 0.001, "nmpc_control_weight_y": 0.001,
    "nmpc_control_weight_z": 0.001,
    "nmpc_accel_limit_x": 4.0, "nmpc_accel_limit_y": 4.0,
    "nmpc_accel_limit_z": 2.5,
    "nmpc_increment_limit_x": 4.0, "nmpc_increment_limit_y": 4.0,
    "nmpc_increment_limit_z": 2.5,
    "integral_limit_x": 0.5, "integral_limit_y": 0.5, "integral_limit_z": 0.3,
    "mass": 0.67, "gravity": 9.8, "hover_percentage": 0.37,
    "min_normalized_thrust": 0.0, "max_normalized_thrust": 1.0,
    "tilt_limit_rad": 0.5235987755982988,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def parse_ports() -> tuple[list[str], list[str]]:
    text = BASE_MODEL.read_text(encoding="utf-8")
    inputs = re.findall(
        r"^\s*SysplorerEmbeddedCoder\.Port\.Inport\s+([A-Za-z0-9_]+)_in\s*$",
        text,
        re.MULTILINE,
    )
    outputs = re.findall(
        r"^\s*SysplorerEmbeddedCoder\.Port\.Outport\s+([A-Za-z0-9_]+)_out\s*$",
        text,
        re.MULTILINE,
    )
    if not inputs or not outputs:
        raise RuntimeError("unable to parse G9 scalar ports")
    missing_defaults = sorted(set(inputs) - set(EXPOSED_INPUTS) - set(DEFAULTS))
    if missing_defaults:
        raise RuntimeError(f"missing defaults for G9 inputs: {missing_defaults}")
    missing_outputs = sorted(set(SELECTED_OUTPUTS) - set(outputs))
    if missing_outputs:
        raise RuntimeError(f"missing selected G9 outputs: {missing_outputs}")
    return inputs, outputs


def source_decl(name: str, value: float, x: int, y: int) -> str:
    return (
        f"  SysplorerEmbeddedCoder.Sources.Constant {name}_source(k={value}) "
        f"annotation(Placement(transformation(origin={{{x},{y}}},extent={{{{-14,-11}},{{14,11}}}})));"
    )


def adapter_text(
    adapter_name: str,
    controller_id: int,
    label: str,
    inputs: list[str],
) -> str:
    declarations: list[str] = []
    equations: list[str] = []
    for index, name in enumerate(EXPOSED_INPUTS):
        y = 300 - index * 35
        declarations.append(
            f"    SysplorerEmbeddedCoder.Port.Inport {name} "
            f"annotation(Placement(transformation(origin={{-300,{y}}},extent={{{{-9,-9}},{{9,9}}}})));"
        )
        equations.append(f"    connect({name}, core.{name}_in);")
    for name in inputs:
        if name in EXPOSED_INPUTS:
            continue
        value = float(controller_id) if name == "controller_id" else DEFAULTS[name]
        declarations.append(
            f"    SysplorerEmbeddedCoder.Sources.Constant {name}_default(k={value}) "
            "annotation(Placement(transformation(origin={0,0},extent={{-1,-1},{1,1}})));"
        )
        equations.append(f"    connect({name}_default.y, core.{name}_in);")
    for index, name in enumerate(SELECTED_OUTPUTS):
        y = 220 - index * 44
        declarations.append(
            f"    SysplorerEmbeddedCoder.Port.Outport {name} "
            f"annotation(Placement(transformation(origin={{300,{y}}},extent={{{{-9,-9}},{{9,9}}}})));"
        )
        equations.append(f"    connect(core.{name}_out, {name});")
    return f'''  model {adapter_name} "{label} shared G9 numerical adapter"
    extends ModelWorkspace;
    annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),
      Icon(coordinateSystem(extent={{{{-100,-100}},{{100,100}}}},preserveAspectRatio=false),graphics={{
        Rectangle(extent={{{{-100,100}},{{100,-100}}}},lineColor={{45,78,120}},fillColor={{234,242,250}},fillPattern=FillPattern.Solid,radius=6),
        Text(extent={{{{-92,22}},{{92,-22}}}},textString="{label}",fontSize=13,textColor={{25,48,80}})}}),
      Diagram(coordinateSystem(extent={{{{-340,-360}},{{340,340}}}},grid={{2,2}})));
    G9_Family_CFunction_Sysblock core annotation(Placement(transformation(origin={{0,0}},extent={{{{-85,-290}},{{85,290}}}})));
{chr(10).join(declarations)}
  equation
{chr(10).join(equations)}
  end {adapter_name};
'''


def fixture_text(route: str, controller_id: int, label: str, inputs: list[str]) -> str:
    model_name = f"MoSim_G9_{label}_REPORT_MIL"
    adapter_name = f"{label}RouteAdapter"
    declarations: list[str] = []
    equations: list[str] = []
    for index, name in enumerate(EXPOSED_INPUTS):
        column = index // 6
        row = index % 6
        x = -500 + column * 135
        y = 250 - row * 90
        declarations.append(source_decl(name, FIXTURE_VALUES[name], x, y))
        equations.append(f"  connect({name}_source.y, controller.{name});")
    for index, name in enumerate(SELECTED_OUTPUTS):
        y = 250 - index * 55
        declarations.append(
            f"  SysplorerEmbeddedCoder.Port.Outport {name} "
            f"annotation(Placement(transformation(origin={{520,{y}}},extent={{{{-12,-10}},{{12,10}}}})));"
        )
        equations.append(f"  connect(controller.{name}, {name});")
    return f'''model {model_name} "{label} fixed-input report MIL"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),experiment(DoublePrecision=true,Algorithm=Euler,IntegratorStep=0.01,Interval=0.01,StartTime=0,StopTime=0.20,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-580,-380}},{{580,330}}}},grid={{2,2}})));
  {adapter_name} controller annotation(Placement(transformation(origin={{110,-30}},extent={{{{-90,-190}},{{90,190}}}})));
{chr(10).join(declarations)}
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
{adapter_text(adapter_name, controller_id, label, inputs)}
equation
{chr(10).join(equations)}
end {model_name};
'''


def topology_text(route: str, label: str) -> str:
    def wire(connection: str, points: list[tuple[int, int]]) -> str:
        point_text = ",".join(f"{{{x},{y}}}" for x, y in points)
        return (
            f"  connect({connection}) annotation("
            f"Line(points={{{point_text}}},color={{0,90,160}},thickness=0.75));"
        )

    model_name = f"MoSim_G9_{label}_GRAPHICAL_OVERVIEW"
    if route == "smc_boundary_layer":
        blocks = [
            ("Gain", "lambda_position", "k=2.0", -220, 100),
            ("Sum", "sliding_surface", 'inputs="++"', -90, 50),
            ("Saturation", "boundary_layer", "lowLimit=-0.4,upLimit=0.4", 40, 50),
            ("Gain", "switching_gain", "k=0.1", 170, 50),
            ("Sum", "acceleration_sum", 'inputs="++"', 300, 0),
            ("Saturation", "acceleration_limit", "lowLimit=-4.0,upLimit=4.0", 430, 0),
        ]
    elif route == "pid_indi":
        blocks = [
            ("Gain", "pid_position", "k=1.5", -220, 100),
            ("Gain", "pid_velocity", "k=1.5", -220, 0),
            ("Sum", "pid_command", 'inputs="++"', -70, 50),
            ("Sum", "acceleration_residual", 'inputs="+-"', 70, -50),
            ("Gain", "indi_gain", "k=0.12", 190, -50),
            ("Saturation", "indi_increment_limit", "lowLimit=-0.35,upLimit=0.35", 310, -50),
            ("Sum", "augmented_command", 'inputs="++"', 430, 20),
        ]
    elif route == "nmpc_outer":
        blocks = [
            ("Gain", "position_prediction", "k=0.25", -220, 100),
            ("Gain", "velocity_prediction", "k=0.25", -220, 0),
            ("Sum", "horizon_state", 'inputs="++"', -70, 50),
            ("Gain", "quadratic_optimizer", "k=3.2", 80, 50),
            ("UnitDelay", "previous_command", "initCond=0.0", 80, -80),
            ("Sum", "command_increment", 'inputs="+-"', 220, 20),
            ("Saturation", "increment_limit", "lowLimit=-1.2,upLimit=1.2", 340, 20),
            ("Saturation", "acceleration_limit", "lowLimit=-4.0,upLimit=4.0", 460, 20),
        ]
    elif route == "dfbc_basic":
        blocks = [
            ("Gain", "position_feedback", "k=1.5", -220, 100),
            ("Gain", "velocity_feedback", "k=1.5", -220, 0),
            ("Sum", "nominal_force", 'inputs="++"', -70, 50),
            ("UnitDelay", "disturbance_state", "initCond=0.0", 70, -80),
            ("Gain", "disturbance_compensation", "k=-0.4", 200, -80),
            ("Sum", "robust_force", 'inputs="++"', 320, 20),
            ("Saturation", "tilt_force_limit", "lowLimit=-4.0,upLimit=4.0", 450, 20),
        ]
    else:
        blocks = [
            ("Gain", "geometric_position_error", "k=1.5", -220, 100),
            ("Gain", "geometric_velocity_error", "k=1.5", -220, 0),
            ("Sum", "desired_force", 'inputs="++"', -70, 50),
            ("Saturation", "tilt_limit", "lowLimit=-0.5236,upLimit=0.5236", 80, 50),
            ("Gain", "attitude_projection", "k=0.67", 220, 50),
            ("Saturation", "thrust_limit", "lowLimit=0.0,upLimit=1.0", 380, 50),
        ]

    declarations = [
        source_decl("position_error", 0.15, -480, 100),
        source_decl("velocity_error", -0.03, -480, 0),
    ]
    if route in {"dfbc_basic", "smc_boundary_layer", "pid_indi"}:
        declarations.append(source_decl("auxiliary", 0.02, -480, -100))
    names = []
    for kind, name, params, x, y in blocks:
        names.append(name)
        instance_annotation = ""
        if kind == "Gain":
            cls = "SysplorerEmbeddedCoder.MathOperation.Gain"
        elif kind == "Sum":
            cls = "SysplorerEmbeddedCoder.MathOperation.Sum"
            params = f"isSaturate=false,{params}"
            instance_annotation = (
                ",__MWORKS(BlockSystem(Instance("
                "u(u1(Type(ref=\"double\"),Dimension=1),"
                "u2(Type(ref=\"double\"),Dimension=1)),"
                "y(Type(ref=\"double\"),Dimension=1)),"
                "Type(overflowKind=SysplorerEmbeddedCoder.Types.OverflowKind.wrap),"
                "SampleTime(group=\"D1\")=0.01))"
            )
        elif kind == "UnitDelay":
            cls = "SysplorerEmbeddedCoder.Discrete.UnitDelay"
        else:
            cls = "SysplorerEmbeddedCoder.Discontinuities.Saturation"
        declarations.append(
            f"  {cls} {name}({params}) annotation(Placement(transformation(origin={{{x},{y}}},extent={{{{-22,-16}},{{22,16}}}})){instance_annotation});"
        )
    declarations.append(
        "  SysplorerEmbeddedCoder.Port.Outport command annotation(Placement(transformation(origin={520,20},extent={{-12,-10},{12,10}})));"
    )

    equations = [
        wire(f"position_error_source.y, {names[0]}.u", [(-466, 100), (-242, 100)]),
    ]
    if route != "smc_boundary_layer":
        equations.append(
            wire(f"velocity_error_source.y, {names[1]}.u", [(-466, 0), (-242, 0)])
        )
    # Route-specific wiring keeps every visible branch connected.
    if route == "smc_boundary_layer":
        equations += [
            wire("lambda_position.y, sliding_surface.u1", [(-198, 100), (-150, 100), (-150, 58), (-112, 58)]),
            wire("velocity_error_source.y, sliding_surface.u2", [(-466, 0), (-150, 0), (-150, 42), (-112, 42)]),
            wire("sliding_surface.y, boundary_layer.u", [(-68, 50), (18, 50)]),
            wire("boundary_layer.y, switching_gain.u", [(62, 50), (148, 50)]),
            wire("switching_gain.y, acceleration_sum.u1", [(192, 50), (240, 50), (240, 8), (278, 8)]),
            wire("auxiliary_source.y, acceleration_sum.u2", [(-466, -100), (240, -100), (240, -8), (278, -8)]),
            wire("acceleration_sum.y, acceleration_limit.u", [(322, 0), (408, 0)]),
            wire("acceleration_limit.y, command", [(452, 0), (480, 0), (480, 20), (508, 20)]),
        ]
    elif route == "pid_indi":
        equations += [
            wire("pid_position.y, pid_command.u1", [(-198, 100), (-130, 100), (-130, 58), (-92, 58)]),
            wire("pid_velocity.y, pid_command.u2", [(-198, 0), (-130, 0), (-130, 42), (-92, 42)]),
            wire("pid_command.y, acceleration_residual.u1", [(-48, 50), (0, 50), (0, -42), (48, -42)]),
            wire("auxiliary_source.y, acceleration_residual.u2", [(-466, -100), (0, -100), (0, -58), (48, -58)]),
            wire("acceleration_residual.y, indi_gain.u", [(92, -50), (168, -50)]),
            wire("indi_gain.y, indi_increment_limit.u", [(212, -50), (288, -50)]),
            wire("pid_command.y, augmented_command.u1", [(-48, 50), (370, 50), (370, 28), (408, 28)]),
            wire("indi_increment_limit.y, augmented_command.u2", [(332, -50), (370, -50), (370, 12), (408, 12)]),
            wire("augmented_command.y, command", [(452, 20), (508, 20)]),
        ]
    elif route == "nmpc_outer":
        equations += [
            wire("position_prediction.y, horizon_state.u1", [(-198, 100), (-130, 100), (-130, 58), (-92, 58)]),
            wire("velocity_prediction.y, horizon_state.u2", [(-198, 0), (-130, 0), (-130, 42), (-92, 42)]),
            wire("horizon_state.y, quadratic_optimizer.u", [(-48, 50), (58, 50)]),
            wire("previous_command.y, command_increment.u2", [(102, -80), (160, -80), (160, 12), (198, 12)]),
            wire("quadratic_optimizer.y, command_increment.u1", [(102, 50), (160, 50), (160, 28), (198, 28)]),
            wire("command_increment.y, increment_limit.u", [(242, 20), (318, 20)]),
            wire("increment_limit.y, previous_command.u1", [(362, 20), (380, 20), (380, -120), (40, -120), (40, -80), (58, -80)]),
            wire("increment_limit.y, acceleration_limit.u", [(362, 20), (438, 20)]),
            wire("acceleration_limit.y, command", [(482, 20), (508, 20)]),
        ]
    elif route == "dfbc_basic":
        equations += [
            wire("position_feedback.y, nominal_force.u1", [(-198, 100), (-130, 100), (-130, 58), (-92, 58)]),
            wire("velocity_feedback.y, nominal_force.u2", [(-198, 0), (-130, 0), (-130, 42), (-92, 42)]),
            wire("auxiliary_source.y, disturbance_state.u1", [(-466, -100), (20, -100), (20, -80), (48, -80)]),
            wire("disturbance_state.y, disturbance_compensation.u", [(92, -80), (178, -80)]),
            wire("nominal_force.y, robust_force.u1", [(-48, 50), (260, 50), (260, 28), (298, 28)]),
            wire("disturbance_compensation.y, robust_force.u2", [(222, -80), (260, -80), (260, 12), (298, 12)]),
            wire("robust_force.y, tilt_force_limit.u", [(342, 20), (428, 20)]),
            wire("tilt_force_limit.y, command", [(472, 20), (508, 20)]),
        ]
    else:
        equations += [
            wire("geometric_position_error.y, desired_force.u1", [(-198, 100), (-130, 100), (-130, 58), (-92, 58)]),
            wire("geometric_velocity_error.y, desired_force.u2", [(-198, 0), (-130, 0), (-130, 42), (-92, 42)]),
            wire("desired_force.y, tilt_limit.u", [(-48, 50), (58, 50)]),
            wire("tilt_limit.y, attitude_projection.u", [(102, 50), (198, 50)]),
            wire("attitude_projection.y, thrust_limit.u", [(242, 50), (358, 50)]),
            wire("thrust_limit.y, command", [(402, 50), (470, 50), (470, 20), (508, 20)]),
        ]
    return f'''model {model_name} "{label} readable algorithm topology"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.20,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-560,-180}},{{560,180}}}},grid={{2,2}})));
{chr(10).join(declarations)}
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
{chr(10).join(equations)}
end {model_name};
'''


def main() -> int:
    inputs, outputs = parse_ports()
    model_dir = OUTPUT_ROOT / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for route, (controller_id, label) in ROUTES.items():
        fixture_name = f"MoSim_G9_{label}_REPORT_MIL"
        overview_name = f"MoSim_G9_{label}_GRAPHICAL_OVERVIEW"
        fixture_path = model_dir / f"{fixture_name}.mo"
        overview_path = model_dir / f"{overview_name}.mo"
        fixture_path.write_text(
            fixture_text(route, controller_id, label, inputs),
            encoding="utf-8",
            newline="\n",
        )
        overview_path.write_text(
            topology_text(route, label), encoding="utf-8", newline="\n"
        )
        rows.append({
            "route": route,
            "controller_id": controller_id,
            "fixture_model": fixture_name,
            "fixture_path": rel(fixture_path),
            "fixture_sha256": sha256(fixture_path),
            "graphical_model": overview_name,
            "graphical_path": rel(overview_path),
            "graphical_sha256": sha256(overview_path),
        })
    manifest = {
        "schema": "mosim.g9_report_evidence_models.v1",
        "source_model": rel(BASE_MODEL),
        "source_model_sha256": sha256(BASE_MODEL),
        "input_count": len(inputs),
        "output_count": len(outputs),
        "routes": rows,
        "claim_boundary": [
            "Route MIL fixtures call the frozen shared G9 CFunction model and are the numerical MWORKS authority for this screenshot batch.",
            "Readable graphical overview models expose algorithm signal topology but are documentation fixtures, not generated-C equivalence authorities.",
            "Fixed-input 0.20 s MIL evidence is not seven-scenario performance acceptance.",
        ],
    }
    manifest_path = OUTPUT_ROOT / "MODEL_BUILD_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({"ok": True, "routes": len(rows), "manifest": rel(manifest_path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
