#!/usr/bin/env python3
"""Generate public Experiment review entries for the current graphical routes.

The generated runner boundary is intentionally a review boundary.  It keeps
the existing native Sysblock core as the controller center, adds visible
reference/state and output-adapter connections, and ends at the project plant
rotor-command interface.  It does not promote a route to APP execution or
claim closed-loop behavior equivalence.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MAP_PATH = ROOT / "Config" / "control_platform" / "current_model_entry_map.json"
CATALOG_PATH = ROOT / "Config" / "control_platform" / "control_scheme_catalog.json"
EXPERIMENT_ROOT = ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment"

FAMILY_DIRS = {
    "pid_family": "PidFamily",
    "linear_robust_state_feedback": "LinearRobustStateFeedback",
    "nonlinear_adaptive": "NonlinearAdaptive",
    "sliding_mode": "SlidingMode",
    "optimization_predictive": "OptimizationPredictive",
    "geometric_flatness": "GeometricFlatness",
    "learning": "Learning",
}

FAMILY_LABELS = {
    "pid_family": "PID family",
    "linear_robust_state_feedback": "linear robust state feedback family",
    "nonlinear_adaptive": "nonlinear adaptive family",
    "sliding_mode": "sliding-mode family",
    "optimization_predictive": "optimization predictive family",
    "geometric_flatness": "geometric flatness family",
    "learning": "learning family",
}

MODEL_RE = re.compile(r"^\s*model\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\b", re.MULTILINE)
WITHIN_RE = re.compile(r"^\s*within\s+(?P<name>[^;]+);", re.MULTILINE)
INPORT_RE = re.compile(r"SysplorerEmbeddedCoder\.Port\.Inport\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)")
OUTPORT_RE = re.compile(r"SysplorerEmbeddedCoder\.Port\.Outport\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)")


def pascal(value: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in value.split("_") if part)


def connect(src: str, dst: str, y: int) -> str:
    points = "{{-440,%d},{-120,%d}}" % (y, y + 18)
    return (
        f"  connect({src}, {dst}) annotation(Line(points={points}, "
        "color={0,0,127}));"
    )


def placement(
    class_name: str,
    instance: str,
    x: int,
    y: int,
    w: int = 70,
    h: int = 50,
    *,
    sec_instance: bool = True,
) -> str:
    metadata = ", __MWORKS(SECInstance = true)" if sec_instance else ""
    return (
        f"  {class_name} {instance}\n"
        f"    annotation(Placement(transformation(origin = {{{x}, {y}}}, "
        f"extent = {{{{-{w}, -{h}}}, {{{w}, {h}}}}})){metadata});"
    )


def source_class(text: str) -> tuple[str, str]:
    within = WITHIN_RE.search(text)
    model = MODEL_RE.search(text)
    if model is None:
        raise ValueError("model declaration missing")
    return (within.group("name") if within else "", model.group("name"))


def ports(path: Path) -> tuple[list[str], list[str]]:
    text = path.read_text(encoding="utf-8")
    return list(dict.fromkeys(INPORT_RE.findall(text))), list(dict.fromkeys(OUTPORT_RE.findall(text)))


def load_rows() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    current = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    catalog_by_id = {str(row["scheme_id"]): row for row in catalog["schemes"]}
    rows = {str(row["scheme_id"]): row for row in current["schemes"]}
    return rows, catalog_by_id


def input_source(port: str, needs_position_error: bool, needs_velocity_error: bool) -> str:
    axis = {"x": "1", "y": "2", "z": "3"}
    explicit_sources = {
        "state_x": "plant.position[1]",
        "state_y": "plant.position[2]",
        "state_z": "plant.position[3]",
        "state_u": "plant.VelMea[1]",
        "state_v": "plant.VelMea[2]",
        "state_w": "plant.VelMea[3]",
        "state_p": "plant.BodyRateMea[1]",
        "state_q": "plant.BodyRateMea[2]",
        "state_r": "plant.BodyRateMea[3]",
        "state_roll": "plant.attitude[1]",
        "state_pitch": "plant.attitude[2]",
        "state_yaw": "plant.attitude[3]",
        "reference_x": "reference.position_command[1]",
        "reference_y": "reference.position_command[2]",
        "reference_z": "reference.position_command[3]",
        "reference_u": "reference.velocity_command[1]",
        "reference_v": "reference.velocity_command[2]",
        "reference_w": "reference.velocity_command[3]",
    }
    if port in explicit_sources:
        return explicit_sources[port]
    if port in {"dt"}:
        return "dt.y"
    if port in {"enable"}:
        return "enable.y"
    if port == "position_error_in" and needs_position_error:
        return "position_error.y"
    if port == "velocity_error_in" and needs_velocity_error:
        return "velocity_error.y"
    if port == "auxiliary_in":
        return "zero.y"
    for prefix, source in (
        ("position_", "plant.position"),
        ("state_x", "plant.position"),
        ("state_y", "plant.position"),
        ("state_z", "plant.position"),
        ("velocity_", "plant.VelMea"),
        ("state_u", "plant.VelMea"),
        ("state_v", "plant.VelMea"),
        ("state_w", "plant.VelMea"),
        ("body_rate_", "plant.BodyRateMea"),
        ("state_p", "plant.BodyRateMea"),
        ("state_q", "plant.BodyRateMea"),
        ("state_r", "plant.BodyRateMea"),
        ("state_roll", "plant.attitude"),
        ("state_pitch", "plant.attitude"),
        ("state_yaw", "plant.attitude"),
    ):
        if port.startswith(prefix):
            suffix = port[len(prefix) :]
            index = axis.get(suffix, axis.get(suffix[-1:], "1"))
            return f"{source}[{index}]"
    for prefix, source in (
        ("reference_position_", "reference.position_command"),
        ("reference_velocity_", "reference.velocity_command"),
        ("reference_acceleration_", "reference.acceleration_command"),
        ("reference_x", "reference.position_command"),
        ("reference_y", "reference.position_command"),
        ("reference_z", "reference.position_command"),
        ("reference_u", "reference.velocity_command"),
        ("reference_v", "reference.velocity_command"),
        ("reference_w", "reference.velocity_command"),
    ):
        if port.startswith(prefix):
            suffix = port[len(prefix) :]
            index = axis.get(suffix, axis.get(suffix[-1:], "1"))
            return f"{source}[{index}]"
    if port in {"reference_roll", "reference_pitch", "reference_yaw", "yaw_ref"}:
        return "zero.y"
    return "zero.y"


def output_kind(outputs: list[str]) -> str:
    if any(name in outputs for name in ("desired_roll_rad_out", "adapted_roll_rad_out")):
        return "attitude"
    if any(name in outputs for name in ("desired_pitch_rad_out", "adapted_pitch_rad_out")):
        return "attitude"
    if any(name in outputs for name in ("desired_acceleration_x_out", "desired_acceleration_x")):
        return "acceleration"
    if any(name in outputs for name in ("normalized_thrust", "normalized_thrust_out")) and "command" not in outputs:
        return "scalar"
    return "scalar"


def pick(outputs: list[str], candidates: tuple[str, ...]) -> str | None:
    return next((name for name in candidates if name in outputs), None)


def output_connections(kind: str, outputs: list[str]) -> tuple[str, list[tuple[str, str]]]:
    if kind == "scalar":
        name = pick(outputs, ("command", "normalized_thrust", "normalized_thrust_out", "thrust_cmd"))
        return "GraphicalScalarRotorPreview", [(f"core.{name or outputs[0]}", "output_adapter.command")]
    if kind == "attitude":
        roll = pick(outputs, ("desired_roll_rad_out", "adapted_roll_rad_out", "roll_cmd"))
        pitch = pick(outputs, ("desired_pitch_rad_out", "adapted_pitch_rad_out", "pitch_cmd"))
        yaw = pick(outputs, ("adapted_yaw_rad_out", "yaw_cmd"))
        thrust = pick(outputs, ("collective_thrust_n_out", "normalized_thrust_out", "collective_thrust_n", "normalized_thrust"))
        return "GraphicalAttitudeThrustRotorPreview", [
            (f"core.{roll}", "output_adapter.roll_ref") if roll else ("zero.y", "output_adapter.roll_ref"),
            (f"core.{pitch}", "output_adapter.pitch_ref") if pitch else ("zero.y", "output_adapter.pitch_ref"),
            (f"core.{yaw}", "output_adapter.yaw_ref") if yaw else ("zero.y", "output_adapter.yaw_ref"),
            (f"core.{thrust}", "output_adapter.collective_thrust") if thrust else ("zero.y", "output_adapter.collective_thrust"),
        ]
    acceleration = [
        pick(outputs, ("desired_acceleration_x_out", "desired_acceleration_x")),
        pick(outputs, ("desired_acceleration_y_out", "desired_acceleration_y")),
        pick(outputs, ("desired_acceleration_z_out", "desired_acceleration_z")),
    ]
    thrust = pick(outputs, ("normalized_thrust_out", "collective_thrust_n_out", "normalized_thrust", "collective_thrust_n"))
    return "GraphicalAccelerationRotorPreview", [
        (f"core.{acceleration[0]}", "output_adapter.acceleration_x") if acceleration[0] else ("zero.y", "output_adapter.acceleration_x"),
        (f"core.{acceleration[1]}", "output_adapter.acceleration_y") if acceleration[1] else ("zero.y", "output_adapter.acceleration_y"),
        (f"core.{acceleration[2]}", "output_adapter.acceleration_z") if acceleration[2] else ("zero.y", "output_adapter.acceleration_z"),
        (f"core.{thrust}", "output_adapter.collective_thrust") if thrust else ("zero.y", "output_adapter.collective_thrust"),
    ]


def render_graphical_runner(scheme_id: str, category: str, path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    within, core_name = source_class(text)
    inports, outports = ports(path)
    family_dir = FAMILY_DIRS[category]
    package = f"MoSimQuadrotorModel.Experiment.{family_dir}"
    runner_name = pascal(scheme_id) + "GraphicalRunner"
    core_class = f"{within}.{core_name}" if within else core_name
    kind = output_kind(outports)
    adapter_class, out_wires = output_connections(kind, outports)
    needs_position_error = "position_error_in" in inports
    needs_velocity_error = "velocity_error_in" in inports

    lines = [
        f"within {package};",
        f"model {runner_name}",
        f"  \"{scheme_id} graphical Sysblock review runner with the common aircraft template\"",
        "",
        "  parameter Real gust_force[3](each unit = \"N\") = {0, 0, 0};",
        "  parameter Real gust_start_s(unit = \"s\") = 0;",
        "  parameter Real gust_duration_s(unit = \"s\") = 0;",
        "  parameter Real mass_scale(min = 0.01) = 1;",
        "  parameter Real inertia_scale[3](each min = 0.01) = {1, 1, 1};",
        "  parameter Real rotor_effectiveness[4](each min = 0, each max = 1) = {1, 1, 1, 1};",
        "  parameter Real fault_start_s(unit = \"s\") = 1e9;",
        "  parameter Integer fault_rotor_index(min = 1, max = 4) = 1;",
        "  parameter Real fault_rotor_effectiveness(min = 0, max = 1) = 1;",
        "  parameter Real nominal_esc_limit_abs(unit = \"rad/s\", min = 0) = 110;",
        "  parameter Integer scenario_mode(min = 0, max = 4) = 0;",
        "  Modelica.Blocks.Sources.Constant zero(k = 0)",
        "    annotation(Placement(transformation(origin = {-470, -180}, extent = {{-16, -16}, {16, 16}})));",
        "  Modelica.Blocks.Sources.Constant dt(k = 0.01)",
        "    annotation(Placement(transformation(origin = {-470, -220}, extent = {{-16, -16}, {16, 16}})));",
        "  Modelica.Blocks.Sources.Constant enable(k = 1)",
        "    annotation(Placement(transformation(origin = {-470, -260}, extent = {{-16, -16}, {16, 16}})));",
        "  MoSimQuadrotorModel.Guidance.Trajectories.MultiModeTrajectory reference(scenario_mode = scenario_mode)",
        "    annotation(Placement(transformation(origin = {-380, 185}, extent = {{-50, -65}, {50, 65}})));",
        placement(core_class, "core", -65, 185, 80, 65),
        placement(
            f"MoSimQuadrotorModel.Experiment.Adapters.{adapter_class}",
            "output_adapter",
            108,
            185,
            50,
            50,
            sec_instance=False,
        ),
        "  MoSimQuadrotorModel.Experiment.Baselines.ScheduledRotorEfficiencyCompensator fault_compensator(",
        "    rotor_effectiveness = rotor_effectiveness, fault_start_s = fault_start_s,",
        "    fault_rotor_index = fault_rotor_index, fault_rotor_effectiveness = fault_rotor_effectiveness)",
        "    annotation(Placement(transformation(origin = {320, 5}, extent = {{-50, -50}, {50, 50}})));",
        "  MoSimQuadrotorModel.Vehicle.BaseModules.ESCDrive esc(motor_limit_abs = nominal_esc_limit_abs)",
        "    annotation(Placement(transformation(origin = {190, 5}, extent = {{-50, -50}, {50, 50}})));",
        "  MoSimQuadrotorModel.Vehicle.BaseModules.BatteryPower battery(voltage_drop_per_second = 0)",
        "    annotation(Placement(transformation(origin = {55, 5}, extent = {{-50, -50}, {50, 50}})));",
        "  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor1(channel_index = 1)",
        "    annotation(Placement(transformation(origin = {465, 220}, extent = {{-28.75, -30}, {28.75, 30}})));",
        "  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor2(channel_index = 2)",
        "    annotation(Placement(transformation(origin = {465, 142}, extent = {{-28.75, -30}, {28.75, 30}})));",
        "  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor3(channel_index = 3)",
        "    annotation(Placement(transformation(origin = {465, 64}, extent = {{-28.75, -30}, {28.75, 30}})));",
        "  MoSimQuadrotorModel.Experiment.Telemetry.RotorCommandChannel motor4(channel_index = 4)",
        "    annotation(Placement(transformation(origin = {465, -14}, extent = {{-28.75, -30}, {28.75, 30}})));",
        "  MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant(",
        "    rotor_effectiveness = rotor_effectiveness, gust_force = gust_force,",
        "    gust_start_s = gust_start_s, gust_duration_s = gust_duration_s,",
        "    mass_scale = mass_scale, inertia_scale = inertia_scale,",
        "    fault_start_s = fault_start_s, fault_rotor_index = fault_rotor_index,",
        "    fault_rotor_effectiveness = fault_rotor_effectiveness)",
        "    annotation(Placement(transformation(origin = {650, 100}, extent = {{-127.5, -147.5}, {127.5, 147.5}})));",
        "  MoSimQuadrotorModel.Vehicle.BaseModules.PerceptionInterface perception",
        "    annotation(Placement(transformation(origin = {-380, 5}, extent = {{-50, -50}, {50, 50}})));",
        "  MoSimQuadrotorModel.Vehicle.BaseModules.FlightController flight_controller",
        "    annotation(Placement(transformation(origin = {-95, 5}, extent = {{-50, -50}, {50, 50}})));",
        "  MoSimQuadrotorModel.Vehicle.BaseModules.MissionComputer mission_computer",
        "    annotation(Placement(transformation(origin = {-235, 5}, extent = {{-50, -50}, {50, 50}})));",
    ]
    if needs_position_error:
        lines.append("  Modelica.Blocks.Math.Add position_error\n    annotation(Placement(transformation(origin = {-360, -90}, extent = {{-24, -18}, {24, 18}})));\n")
    if needs_velocity_error:
        lines.append("  Modelica.Blocks.Math.Add velocity_error\n    annotation(Placement(transformation(origin = {-360, -140}, extent = {{-24, -18}, {24, 18}})));\n")
    lines += [
        "",
        "  Real position_ref[3];",
        "  Real position[3];",
        "  Real attitude[3];",
        "  Real rotor_command[4];",
        "  Real esc_motor_command[4];",
        "  Real rotor_speed[4];",
        "  Real esc_health[4];",
        "  Real esc_saturation_ratio;",
        "  Real mission_reference_position[3];",
        "  Real position_error_norm;",
    ]
    lines += ["", "equation"]
    y = 240
    if needs_position_error:
        lines.append(connect("reference.position_command[1]", "position_error.u1", y))
        lines.append(connect("plant.position[1]", "position_error.u2", y + 12))
        y += 24
    if needs_velocity_error:
        lines.append(connect("reference.velocity_command[1]", "velocity_error.u1", y))
        lines.append(connect("plant.VelMea[1]", "velocity_error.u2", y + 12))
        y += 24
    for port in inports:
        lines.append(connect(input_source(port, needs_position_error, needs_velocity_error), f"core.{port}", y))
        y -= 14
    for source, target in out_wires:
        lines.append(connect(source, target, y))
        y -= 14
    for index in range(1, 5):
        lines.append(connect(f"output_adapter.rotor_command[{index}]", f"fault_compensator.command_in[{index}]", y))
        y -= 14
    for index in range(1, 5):
        lines.append(connect(f"fault_compensator.command_out[{index}]", f"esc.motor_command_raw[{index}]", y))
        y -= 14
    for index, motor in enumerate(("motor1", "motor2", "motor3", "motor4"), start=1):
        lines.append(connect(f"esc.motor_command[{index}]", f"{motor}.command", y))
        y -= 14
    for index, motor in enumerate(("motor1", "motor2", "motor3", "motor4"), start=1):
        lines.append(connect(f"{motor}.command_to_plant", f"plant.rotor_command[{index}]", y))
        y -= 14
    for index, motor in enumerate(("motor1", "motor2", "motor3", "motor4"), start=1):
        lines.append(connect(f"plant.rotor_speed[{index}]", f"{motor}.speed", y))
        y -= 14
    lines += [
        connect("battery.bus_voltage", "esc.bus_voltage", y),
        connect("battery.power_ok", "esc.power_ok", y - 14),
        connect("plant.position", "perception.position_raw", y - 28),
        connect("perception.gps_position", "flight_controller.gps_position", y - 42),
        connect("perception.gps_valid", "flight_controller.gps_valid", y - 56),
        connect("plant.attitude", "flight_controller.attitude_raw", y - 70),
        connect("plant.rotor_speed", "flight_controller.motor_speed_raw", y - 84),
        connect("perception.local_position", "mission_computer.local_position", y - 98),
        connect("flight_controller.position_est", "mission_computer.aircraft_position", y - 112),
        connect("perception.obstacle_margin", "mission_computer.obstacle_margin", y - 126),
        connect("flight_controller.estimator_quality", "mission_computer.estimator_quality", y - 140),
        "",
        "  position_ref = reference.position_command;",
        "  position = plant.position;",
        "  attitude = plant.attitude;",
        "  rotor_command = output_adapter.rotor_command;",
        "  esc_motor_command = esc.motor_command;",
        "  rotor_speed[1] = motor1.speed_telemetry;",
        "  rotor_speed[2] = motor2.speed_telemetry;",
        "  rotor_speed[3] = motor3.speed_telemetry;",
        "  rotor_speed[4] = motor4.speed_telemetry;",
        "  esc_health = esc.esc_health;",
        "  esc_saturation_ratio = esc.saturation_ratio_est;",
        "  mission_reference_position = mission_computer.reference_position;",
        "  position_error_norm = sqrt((position_ref[1] - position[1])^2 + (position_ref[2] - position[2])^2 + (position_ref[3] - position[3])^2);",
    ]
    lines += [
        "",
        "  annotation(",
        "    experiment(Algorithm = Dassl, StartTime = 0, StopTime = 50, Interval = 0.01),",
        "    Diagram(coordinateSystem(extent = {{-520, -400}, {830, 300}}, grid = {2, 2})),",
        '    __MWORKS(version = "26.3.0"));',
        f"end {runner_name};",
        "",
    ]
    return runner_name, "\n".join(lines).rstrip() + "\n"


def render_alias(package_dir: str, runner_name: str, source_class: str, description: str) -> str:
    package = f"MoSimQuadrotorModel.Experiment.{package_dir}"
    return (
        f"within {package};\n"
        f"model {runner_name}\n"
        f"  \"{description}\"\n"
        f"  extends {source_class};\n"
        '  annotation(__MWORKS(hide = false, version = "26.3.0"));\n'
        f"end {runner_name};\n"
    )


def render_package(package_dir: str, label: str) -> str:
    return (
        f"within MoSimQuadrotorModel.Experiment;\n"
        f"package {package_dir}\n"
        f"  \"{label} review runners\"\n"
        "  extends Modelica.Icons.Package;\n"
        '  annotation(__MWORKS(version = "26.3.0"));\n'
        f"end {package_dir};\n"
    )


def write_new(path: Path, text: str, *, force: bool) -> None:
    if path.exists() and not force:
        raise RuntimeError(f"refusing to overwrite existing path: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build(*, force: bool) -> dict[str, Any]:
    rows, catalog_by_id = load_rows()
    generated: list[dict[str, str]] = []
    family_models: dict[str, list[str]] = {name: [] for name in FAMILY_DIRS.values()}

    graphical_rows = [row for row in rows.values() if row.get("current_model_role") == "graphical_controller_core"]
    for row in sorted(graphical_rows, key=lambda item: str(item["scheme_id"])):
        scheme_id = str(row["scheme_id"])
        catalog = catalog_by_id[scheme_id]
        category = str(catalog["category"])
        package_dir = FAMILY_DIRS[category]
        if scheme_id == "official_pid":
            runner_name = "OfficialPidFamilyRunner"
            text = render_alias(
                package_dir,
                runner_name,
                "MoSimQuadrotorModel.Experiment.Baselines.OfficialPidRunner",
                "Official PID family entry reusing the reviewed Baselines template",
            )
        else:
            source = ROOT / str(row["current_model_file"])
            runner_name, text = render_graphical_runner(scheme_id, category, source)
        target = EXPERIMENT_ROOT / package_dir / f"{runner_name}.mo"
        write_new(target, text, force=force)
        family_models[package_dir].append(runner_name)
        generated.append({"scheme_id": scheme_id, "kind": "graphical", "runner_class": f"MoSimQuadrotorModel.Experiment.{package_dir}.{runner_name}", "runner_file": target.relative_to(ROOT).as_posix()})

    full_rows = [row for row in rows.values() if row.get("current_model_role") == "full_profile_whole_aircraft_closed_loop"]
    for row in sorted(full_rows, key=lambda item: str(item["scheme_id"])):
        scheme_id = str(row["scheme_id"])
        catalog = catalog_by_id[scheme_id]
        package_dir = FAMILY_DIRS[str(catalog["category"])]
        source = ROOT / str(row["current_model_file"])
        _, source_name = source_class(source.read_text(encoding="utf-8"))
        runner_name = pascal(scheme_id) + "FamilyRunner"
        text = render_alias(
            package_dir,
            runner_name,
            f"MoSimQuadrotorModel.Experiment.SingleUav.IntegratedChains.{source_name}",
            f"{scheme_id} family entry reusing the canonical integrated Sysblock chain",
        )
        target = EXPERIMENT_ROOT / package_dir / f"{runner_name}.mo"
        write_new(target, text, force=force)
        family_models[package_dir].append(runner_name)
        generated.append({"scheme_id": scheme_id, "kind": "full_profile", "runner_class": f"MoSimQuadrotorModel.Experiment.{package_dir}.{runner_name}", "runner_file": target.relative_to(ROOT).as_posix()})

    for package_dir, models in family_models.items():
        if not models:
            continue
        package_root = EXPERIMENT_ROOT / package_dir
        write_new(package_root / "package.mo", render_package(package_dir, next((key for key, value in FAMILY_DIRS.items() if value == package_dir), package_dir)), force=force)
        write_new(package_root / "package.order", "\n".join(sorted(models)) + "\n", force=force)

    experiment_order = EXPERIMENT_ROOT / "package.order"
    existing = [line.strip() for line in experiment_order.read_text(encoding="utf-8").splitlines() if line.strip()]
    for name in ["Adapters", *FAMILY_DIRS.values()]:
        if name not in existing:
            existing.append(name)
    experiment_order.write_text("\n".join(existing) + "\n", encoding="utf-8", newline="\n")
    return {"graphical_count": len(graphical_rows), "full_profile_count": len(full_rows), "generated_count": len(generated), "entries": generated}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    result = build(force=bool(args.force))
    if args.json_output:
        output = args.json_output if args.json_output.is_absolute() else ROOT / args.json_output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("graphical_count", "full_profile_count", "generated_count")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
