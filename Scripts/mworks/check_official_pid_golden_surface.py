#!/usr/bin/env python3
"""Static contract checks for the Official PID single-UAV golden entry."""

from __future__ import annotations

import argparse
import json
import re
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
_MODEL_RESOURCE_URI = re.compile(
    r"modelica://MoSimQuadrotorModel/([^\"'\s)]+)"
)
_NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
# The plant-position feedback crosses the root-level control and telemetry lanes.
_MAX_VISIBLE_LINE_TURNS = 6
_BITMAP_WITH_MODEL_RESOURCE = re.compile(
    rf"Bitmap\s*\(\s*.*?extent\s*=\s*\{{\{{\s*(?P<x1>{_NUMBER})\s*,\s*"
    rf"(?P<y1>{_NUMBER})\s*\}},\s*\{{\s*(?P<x2>{_NUMBER})\s*,\s*"
    rf"(?P<y2>{_NUMBER})\s*\}}\}}.*?fileName\s*=\s*\"modelica://"
    rf"MoSimQuadrotorModel/(?P<resource>[^\"'\s)]+)\".*?\)",
    re.DOTALL,
)
_GRAPHICAL_RESOURCE_SOURCES = [
    "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/Modules/RotorCommandChannel.mo",
    "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/Modules/DirectControlTelemetry.mo",
    "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/Modules/SystemTelemetry.mo",
    "Models/MoSimQuadrotorModel/Vehicle/Sunray150Assembly.mo",
    "Models/MoSimQuadrotorModel/Vehicle/Sunray150VisualShell.mo",
    "Models/MoSimQuadrotorModel/Vehicle/Dynamics/WrapperSurface.mo",
    "Models/MoSimQuadrotorModel/Experiment/Templates/Architecture/Sunray150CompleteSystemGraphical_Sysblock.mo",
]


def _read(relative_path: str) -> tuple[Path, str]:
    path = ROOT / relative_path
    return path, path.read_text(encoding="utf-8") if path.exists() else ""


def _require_tokens(
    relative_path: str,
    tokens: list[str],
    failures: list[str],
) -> dict[str, Any]:
    path, text = _read(relative_path)
    missing = [token for token in tokens if token not in text]
    if missing:
        failures.append(f"{relative_path}: missing {', '.join(missing)}")
    return {
        "path": relative_path,
        "exists": path.exists(),
        "missing": missing,
    }


def _missing_tokens(
    text: str,
    tokens: list[str],
) -> list[str]:
    return [token for token in tokens if token not in text]


def _check_visible_orthogonal_connections(
    text: str,
    connections: list[str],
    failures: list[str],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for connection in connections:
        match = re.search(
            rf"{re.escape(connection)}\s*"
            r"annotation\(Line\((?P<line>.*?)\)\);",
            text,
            re.DOTALL,
        )
        check: dict[str, Any] = {
            "connection": connection,
            "annotation_found": match is not None,
            "visible": False,
            "orthogonal": False,
            "turn_count": None,
            "valid": False,
        }
        if match is None:
            failures.append(f"golden entry: missing Line annotation for {connection}")
            checks.append(check)
            continue

        line = match.group("line")
        check["visible"] = not bool(re.search(r"visible\s*=\s*false", line))
        points_match = re.search(r"\bpoints\s*=", line)
        point_source = line[points_match.end() :] if points_match else ""
        points = [
            (float(x), float(y))
            for x, y in re.findall(
                rf"\{{\s*({_NUMBER})\s*,\s*({_NUMBER})\s*\}}",
                point_source,
            )
        ]
        check["turn_count"] = max(0, len(points) - 2)
        check["orthogonal"] = len(points) >= 2 and all(
            x1 == x2 or y1 == y2
            for (x1, y1), (x2, y2) in zip(points, points[1:])
        )
        check["valid"] = (
            check["visible"]
            and check["orthogonal"]
            and check["turn_count"] <= _MAX_VISIBLE_LINE_TURNS
        )
        if not check["visible"]:
            failures.append(f"golden entry: hidden required connection {connection}")
        if not check["orthogonal"]:
            failures.append(f"golden entry: non-orthogonal route for {connection}")
        if check["turn_count"] > _MAX_VISIBLE_LINE_TURNS:
            failures.append(
                f"golden entry: route has too many turns ({check['turn_count']}) for {connection}"
            )
        checks.append(check)
    return checks


def _check_graphical_resources(failures: list[str]) -> list[dict[str, Any]]:
    resources: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source_relative_path in _GRAPHICAL_RESOURCE_SOURCES:
        _, source_text = _read(source_relative_path)
        for resource_relative_path in sorted(
            set(_MODEL_RESOURCE_URI.findall(source_text))
        ):
            if resource_relative_path in seen:
                continue
            seen.add(resource_relative_path)
            project_relative_path = (
                Path("Models") / "MoSimQuadrotorModel" / resource_relative_path
            )
            exists = (ROOT / project_relative_path).is_file()
            resources.append(
                {
                    "source": source_relative_path,
                    "uri": f"modelica://MoSimQuadrotorModel/{resource_relative_path}",
                    "path": project_relative_path.as_posix(),
                    "exists": exists,
                }
            )
            if not exists:
                failures.append(
                    f"{source_relative_path}: missing graphical resource "
                    f"{project_relative_path.as_posix()}"
                )
    return resources


def _png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("not a PNG with an IHDR header")
    return struct.unpack(">II", header[16:24])


def _check_graphical_bitmap_aspects(failures: list[str]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    tolerance = 2e-4
    for source_relative_path in _GRAPHICAL_RESOURCE_SOURCES:
        _, source_text = _read(source_relative_path)
        matches = list(_BITMAP_WITH_MODEL_RESOURCE.finditer(source_text))
        expected_count = source_text.count("Bitmap(")
        if len(matches) != expected_count:
            failures.append(
                f"{source_relative_path}: parsed {len(matches)} of {expected_count} Bitmap declarations"
            )
        for match in matches:
            resource_relative_path = match.group("resource")
            resource_path = ROOT / "Models" / "MoSimQuadrotorModel" / resource_relative_path
            x1, y1, x2, y2 = (
                float(match.group(name)) for name in ("x1", "y1", "x2", "y2")
            )
            display_width = abs(x2 - x1)
            display_height = abs(y2 - y1)
            check: dict[str, Any] = {
                "source": source_relative_path,
                "uri": f"modelica://MoSimQuadrotorModel/{resource_relative_path}",
                "path": resource_path.relative_to(ROOT).as_posix(),
                "display_width": display_width,
                "display_height": display_height,
                "valid": False,
            }
            if display_width == 0 or display_height == 0:
                failures.append(
                    f"{source_relative_path}: Bitmap {resource_relative_path} has zero display size"
                )
            elif not resource_path.is_file():
                failures.append(
                    f"{source_relative_path}: missing bitmap resource {resource_relative_path}"
                )
            else:
                try:
                    pixel_width, pixel_height = _png_dimensions(resource_path)
                except ValueError as error:
                    failures.append(
                        f"{source_relative_path}: cannot read {resource_relative_path}: {error}"
                    )
                else:
                    source_aspect = pixel_width / pixel_height
                    display_aspect = display_width / display_height
                    relative_error = abs(display_aspect / source_aspect - 1)
                    check.update(
                        {
                            "pixel_width": pixel_width,
                            "pixel_height": pixel_height,
                            "source_aspect": source_aspect,
                            "display_aspect": display_aspect,
                            "relative_error": relative_error,
                            "valid": relative_error <= tolerance,
                        }
                    )
                    if not check["valid"]:
                        failures.append(
                            f"{source_relative_path}: Bitmap {resource_relative_path} distorts its source aspect "
                            f"by {relative_error:.6g} (limit {tolerance:.6g})"
                        )
            checks.append(check)
    return checks


def run_checks() -> dict[str, Any]:
    failures: list[str] = []
    files: list[dict[str, Any]] = []

    files.append(
        _require_tokens(
            "Docs/Design/架构/01_控制器平台/Official_PID_单机黄金图形化闭环重构规划_20260803.md",
            [
                "OfficialPidSingleUavGoldenRunner",
                "OfficialPIDGraphicalRotorAdapter",
                "Sunray150Assembly",
                "CheckModel",
                "不修改 Official PID 控制律",
            ],
            failures,
        )
    )

    golden_path, golden = _read(
        "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/OfficialPidSingleUavGoldenRunner.mo"
    )
    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/OfficialPidSingleUavGoldenRunner.mo",
            [
                "model OfficialPidSingleUavGoldenRunner",
                "MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath reference",
                "Control.Implementations.Graphical.PID.OfficialPidSysblockCore core",
                "Modelica.Blocks.Math.Gain rotor_sign_1(k = 1)",
                "Modelica.Blocks.Math.Gain rotor_sign_2(k = -1)",
                "Modelica.Blocks.Math.Gain rotor_sign_3(k = 1)",
                "Modelica.Blocks.Math.Gain rotor_sign_4(k = -1)",
                "Control.Implementations.Graphical.PID.OfficialPidSysblockMapper mapper",
                "Control.Adapters.OfficialPidSysblockMapperDiagnostics mapper_diagnostics",
                "Templates.Modules.BatteryPower",
                "Templates.Modules.ESCDrive",
                "Golden.Modules.RotorCommandChannel motor1(channel_index = 1)",
                "Golden.Modules.RotorCommandChannel motor2(channel_index = 2)",
                "Golden.Modules.RotorCommandChannel motor3(channel_index = 3)",
                "Golden.Modules.RotorCommandChannel motor4(channel_index = 4)",
                "MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant(",
                "Templates.Modules.PerceptionInterface",
                "Templates.Modules.FlightController",
                "Templates.Modules.MissionComputer",
                "Templates.Modules.Supervisor",
                "Golden.Modules.DirectControlTelemetry direct_control_telemetry",
                "Golden.Modules.TelemetryBusAggregator telemetry_bus",
                "Golden.Modules.SystemTelemetry system_telemetry",
                "connect(reference.position_command[1], core.x_ref)",
                "connect(reference.position_command[2], core.y_ref)",
                "connect(reference.position_command[3], core.z_ref)",
                "connect(perception.local_position[1], core.x_mea)",
                "connect(perception.local_position[2], core.y_mea)",
                "connect(perception.local_position[3], core.z_mea)",
                "connect(plant.attitude[1], core.roll_mea)",
                "connect(plant.attitude[2], core.pitch_mea)",
                "connect(plant.attitude[3], core.yaw_mea)",
                "connect(core.y, rotor_sign_1.u)",
                "connect(core.y1, rotor_sign_2.u)",
                "connect(core.y2, rotor_sign_3.u)",
                "connect(core.y3, rotor_sign_4.u)",
                "connect(rotor_sign_1.y, mapper.amplitude_1)",
                "connect(rotor_sign_2.y, mapper.amplitude_2)",
                "connect(rotor_sign_3.y, mapper.amplitude_3)",
                "connect(rotor_sign_4.y, mapper.amplitude_4)",
                "connect(mapper.rotor_command_1, esc.motor_command_raw[1])",
                "connect(mapper.rotor_command_2, esc.motor_command_raw[2])",
                "connect(mapper.rotor_command_3, esc.motor_command_raw[3])",
                "connect(mapper.rotor_command_4, esc.motor_command_raw[4])",
                "connect(esc.motor_command[1], motor1.command)",
                "connect(esc.motor_command[2], motor2.command)",
                "connect(esc.motor_command[3], motor3.command)",
                "connect(esc.motor_command[4], motor4.command)",
                "connect(motor1.command_to_plant, plant.rotor_command[1])",
                "connect(motor2.command_to_plant, plant.rotor_command[2])",
                "connect(motor3.command_to_plant, plant.rotor_command[3])",
                "connect(motor4.command_to_plant, plant.rotor_command[4])",
                "connect(plant.position, perception.position_raw)",
                "rotor_command = esc.motor_command_raw;",
                "voltage_drop_per_second = 0",
                "nominal_esc_limit_abs(unit = \"rad/s\", min = 0) = 200",
                "StartTime = 0, StopTime = 50",
                "Interval = 0.01",
            ],
            failures,
        )
    )
    adapter_path, adapter = _read(
        "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/AdapterSingleUavGoldenRunner.mo"
    )
    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/AdapterSingleUavGoldenRunner.mo",
            [
                "model AdapterSingleUavGoldenRunner",
                "replaceable model Controller =",
                "MoSimQuadrotorModel.Control.Adapters.OfficialPIDGraphicalRotorAdapter",
                "replaceable model Trajectory =",
                "Controller controller",
                "Modelica.Blocks.Continuous.Derivative velocity_estimator[3]",
                "Golden.Modules.TelemetryBusAggregator telemetry_bus",
                "connect(reference.position_command, controller.position_ref)",
                "connect(reference.velocity_command, controller.velocity_ref)",
                "connect(reference.acceleration_command, controller.acceleration_ref)",
                "connect(perception.local_position, controller.position_mea)",
                "connect(perception.local_position, velocity_estimator.u)",
                "connect(velocity_estimator.y, controller.velocity_mea)",
                "connect(plant.attitude, controller.attitude_mea)",
                "connect(controller.rotor_command, esc.motor_command_raw)",
                "rotor_command = controller.rotor_command;",
            ],
            failures,
        )
    )
    golden_common_connection_tokens = [
        "connect(plant.position, perception.position_raw)",
    ]
    for index in range(1, 5):
        golden_common_connection_tokens.extend(
            [
                f"connect(esc.motor_command[{index}], motor{index}.command)",
                f"connect(motor{index}.command_to_plant, plant.rotor_command[{index}])",
                f"connect(plant.rotor_speed[{index}], motor{index}.speed)",
            ]
        )
    golden_direct_connection_tokens = [
        "connect(reference.position_command[1], core.x_ref)",
        "connect(reference.position_command[2], core.y_ref)",
        "connect(reference.position_command[3], core.z_ref)",
        "connect(perception.local_position[1], core.x_mea)",
        "connect(perception.local_position[2], core.y_mea)",
        "connect(perception.local_position[3], core.z_mea)",
        "connect(plant.attitude[1], core.roll_mea)",
        "connect(plant.attitude[2], core.pitch_mea)",
        "connect(plant.attitude[3], core.yaw_mea)",
        "connect(core.y, rotor_sign_1.u)",
        "connect(core.y1, rotor_sign_2.u)",
        "connect(core.y2, rotor_sign_3.u)",
        "connect(core.y3, rotor_sign_4.u)",
        "connect(rotor_sign_1.y, mapper.amplitude_1)",
        "connect(rotor_sign_2.y, mapper.amplitude_2)",
        "connect(rotor_sign_3.y, mapper.amplitude_3)",
        "connect(rotor_sign_4.y, mapper.amplitude_4)",
        "connect(mapper.rotor_command_1, esc.motor_command_raw[1])",
        "connect(mapper.rotor_command_2, esc.motor_command_raw[2])",
        "connect(mapper.rotor_command_3, esc.motor_command_raw[3])",
        "connect(mapper.rotor_command_4, esc.motor_command_raw[4])",
    ]
    golden_adapter_connection_tokens = [
        "connect(reference.position_command, controller.position_ref)",
        "connect(reference.velocity_command, controller.velocity_ref)",
        "connect(reference.acceleration_command, controller.acceleration_ref)",
        "connect(perception.local_position, controller.position_mea)",
        "connect(perception.local_position, velocity_estimator.u)",
        "connect(velocity_estimator.y, controller.velocity_mea)",
        "connect(plant.attitude, controller.attitude_mea)",
        "connect(controller.rotor_command, esc.motor_command_raw)",
    ]
    golden_connection_tokens = [
        *golden_common_connection_tokens,
        *golden_direct_connection_tokens,
    ]
    adapter_connection_tokens = [
        *golden_common_connection_tokens,
        *golden_adapter_connection_tokens,
    ]
    native_golden_connection_tokens = [
        "connect(reference.velocity_command, controller.velocity_ref)",
        "connect(reference.acceleration_command, controller.acceleration_ref)",
        "connect(plant.position, perception.position_raw)",
        "connect(perception.local_position, controller.position_mea)",
        "connect(perception.local_position, velocity_estimator.u)",
        "connect(velocity_estimator.y, controller.velocity_mea)",
        "connect(plant.attitude, controller.attitude_mea)",
    ]
    for index in range(1, 5):
        native_golden_connection_tokens.extend(
            [
                f"connect(esc.motor_command[{index}], motor{index}.command)",
                f"connect(motor{index}.command_to_plant, plant.rotor_command[{index}])",
                f"connect(plant.rotor_speed[{index}], motor{index}.speed)",
            ]
        )
    golden_connection_missing = _missing_tokens(golden, golden_connection_tokens)
    if golden_connection_missing:
        failures.append(
            "golden entry: missing closed-loop connection(s) "
            + ", ".join(golden_connection_missing)
        )
    adapter_connection_missing = _missing_tokens(adapter, adapter_connection_tokens)
    if adapter_connection_missing:
        failures.append(
            "adapter golden entry: missing closed-loop connection(s) "
            + ", ".join(adapter_connection_missing)
        )
    if "if use_adapter" in golden or "if not use_adapter" in golden:
        failures.append("golden entry must not use conditional graphical connect() paths")
    if "if use_adapter" in adapter or "if not use_adapter" in adapter:
        failures.append("adapter golden entry must not use conditional graphical connect() paths")
    golden_visible_wiring_connections = [
        "connect(reference.position_command[1], core.x_ref)",
        "connect(reference.position_command[2], core.y_ref)",
        "connect(reference.position_command[3], core.z_ref)",
        "connect(perception.local_position[1], core.x_mea)",
        "connect(perception.local_position[2], core.y_mea)",
        "connect(perception.local_position[3], core.z_mea)",
        "connect(plant.attitude[1], core.roll_mea)",
        "connect(plant.attitude[2], core.pitch_mea)",
        "connect(plant.attitude[3], core.yaw_mea)",
        "connect(plant.position, perception.position_raw)",
        "connect(battery.bus_voltage, esc.bus_voltage)",
        "connect(battery.power_ok, esc.power_ok)",
        "connect(perception.gps_position, flight_controller.gps_position)",
        "connect(plant.attitude, flight_controller.attitude_raw)",
        "connect(plant.rotor_speed, flight_controller.motor_speed_raw)",
        "connect(perception.gps_valid, flight_controller.gps_valid)",
        "connect(perception.local_position, mission_computer.local_position)",
        "connect(flight_controller.position_est, mission_computer.aircraft_position)",
        "connect(perception.obstacle_margin, mission_computer.obstacle_margin)",
        "connect(flight_controller.estimator_quality, mission_computer.estimator_quality)",
        "connect(battery.voltage_margin, system_supervisor.voltage_margin)",
    ]
    for index in range(1, 5):
        golden_visible_wiring_connections.extend(
            [
                f"connect(core.y{'' if index == 1 else index - 1}, rotor_sign_{index}.u)",
                f"connect(rotor_sign_{index}.y, mapper.amplitude_{index})",
                f"connect(mapper.rotor_command_{index}, esc.motor_command_raw[{index}])",
                f"connect(esc.motor_command[{index}], motor{index}.command)",
                f"connect(motor{index}.command_to_plant, plant.rotor_command[{index}])",
                f"connect(plant.rotor_speed[{index}], motor{index}.speed)",
            ]
        )
    golden_visible_wiring_checks = _check_visible_orthogonal_connections(
        golden,
        golden_visible_wiring_connections,
        failures,
    )
    golden_visible_wiring_ok = all(
        check["valid"] for check in golden_visible_wiring_checks
    )
    golden_interface_connections = [
        "connect(reference.direct_control_bus, direct_control_telemetry.trajectory_bus)",
        "connect(mapper_diagnostics.direct_control_bus, direct_control_telemetry.mapper_bus)",
        "connect(telemetry_bus.vehicle_bus, system_telemetry.vehicle_bus)",
        "connect(telemetry_bus.autonomy_bus, system_telemetry.autonomy_bus)",
    ]
    adapter_interface_connections = golden_interface_connections[2:]
    telemetry_binding_tokens = [
        "vehicle_values = {",
        "esc.esc_health[1]",
        "esc.esc_health[4]",
        "motor1.speed_telemetry",
        "motor4.speed_telemetry",
        "plant.VelMea[1]",
        "plant.VelMea[3]",
        "plant.QuatMea[1]",
        "plant.QuatMea[4]",
        "plant.rotor_thrust[1]",
        "plant.rotor_thrust[4]",
        "plant.rotor_yaw_reaction_moment[1]",
        "plant.rotor_yaw_reaction_moment[4]",
        "plant.applied_reaction_yaw_moment",
        "autonomy_values = {",
        "perception.health",
        "perception.mid360_valid",
        "flight_controller.attitude_est[1]",
        "flight_controller.attitude_est[3]",
        "flight_controller.motor_speed_est[1]",
        "flight_controller.motor_speed_est[4]",
        "mission_computer.reference_position[1]",
        "mission_computer.reference_position[3]",
        "mission_computer.reference_acceleration[1]",
        "mission_computer.reference_acceleration[3]",
        "mission_computer.obstacle_avoid_active",
        "system_supervisor.degraded_nav_active",
        "system_supervisor.geofence_breach_active})",
    ]
    golden_interface_missing = _missing_tokens(golden, golden_interface_connections)
    if golden_interface_missing:
        failures.append(
            "golden entry: missing interface-consumer connection(s) "
            + ", ".join(golden_interface_missing)
        )
    golden_interface_wiring_checks = _check_visible_orthogonal_connections(
        golden,
        golden_interface_connections,
        failures,
    )
    golden_interface_wiring_ok = all(
        check["valid"] for check in golden_interface_wiring_checks
    )
    adapter_interface_missing = _missing_tokens(adapter, adapter_interface_connections)
    adapter_telemetry_binding_missing = _missing_tokens(adapter, telemetry_binding_tokens)
    golden_telemetry_binding_missing = _missing_tokens(golden, telemetry_binding_tokens)
    if adapter_interface_missing or adapter_telemetry_binding_missing:
        failures.append(
            "adapter golden entry: incomplete aggregated telemetry wiring "
            + ", ".join(adapter_interface_missing + adapter_telemetry_binding_missing)
        )
    if golden_telemetry_binding_missing:
        failures.append(
            "golden entry: incomplete aggregated telemetry binding "
            + ", ".join(golden_telemetry_binding_missing)
        )
    if golden and "connect(controller.rotor_command, plant.rotor_command)" in golden:
        failures.append("golden entry bypasses the explicit battery/ESC/rotor chain")
    if golden and golden.count("Sunray150Assembly plant(") != 1:
        failures.append("golden entry must contain exactly one shared Sunray150Assembly")
    if golden_path.exists() and "Vehicle.Electricals.Actuator" in golden:
        failures.append("golden entry creates a second legacy actuator dynamics path")
    if adapter and "connect(controller.rotor_command, plant.rotor_command)" in adapter:
        failures.append("adapter golden entry bypasses the explicit battery/ESC/rotor chain")
    if adapter and adapter.count("Sunray150Assembly plant(") != 1:
        failures.append("adapter golden entry must contain exactly one shared Sunray150Assembly")
    files.append(
        {
            "path": "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/OfficialPidSingleUavGoldenRunner.mo",
            "connection_missing": golden_connection_missing,
            "connection_contract_ok": not golden_connection_missing,
            "visible_wiring_checks": golden_visible_wiring_checks,
            "visible_wiring_ok": golden_visible_wiring_ok,
            "interface_connection_missing": golden_interface_missing,
            "interface_wiring_checks": golden_interface_wiring_checks,
            "interface_wiring_ok": golden_interface_wiring_ok,
            "telemetry_binding_missing": golden_telemetry_binding_missing,
        }
    )
    files.append(
        {
            "path": "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/AdapterSingleUavGoldenRunner.mo",
            "exists": adapter_path.exists(),
            "connection_missing": adapter_connection_missing,
            "interface_connection_missing": adapter_interface_missing,
            "telemetry_binding_missing": adapter_telemetry_binding_missing,
            "connection_contract_ok": not adapter_connection_missing,
            "unconditional_graphical_paths": "if use_adapter" not in adapter
            and "if not use_adapter" not in adapter,
        }
    )
    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/Modules/DirectControlTelemetry.mo",
            [
                "block DirectControlTelemetry",
                "RealInput trajectory_bus[6]",
                "RealInput mapper_bus[10]",
                "trajectory_velocity_command = trajectory_bus[1:3];",
                "mapper_mapped_collective_amplitude_error = mapper_bus[10];",
            ],
            failures,
        )
    )
    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/Modules/SystemTelemetry.mo",
            [
                "block SystemTelemetry",
                "RealInput vehicle_bus[28]",
                "RealInput autonomy_bus[40]",
                "esc_health = vehicle_bus[1:4];",
                "mission_reference_position = autonomy_bus[12:14];",
                "supervisor_geofence_breach_active = autonomy_bus[40];",
            ],
            failures,
        )
    )
    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/Modules/TelemetryBusAggregator.mo",
            [
                "block TelemetryBusAggregator",
                "input Real vehicle_values[28]",
                "input Real autonomy_values[40]",
                "RealOutput vehicle_bus[28]",
                "RealOutput autonomy_bus[40]",
                "vehicle_bus = vehicle_values;",
                "autonomy_bus = autonomy_values;",
            ],
            failures,
        )
    )
    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Experiment/Runners/Graphical/AwffSingleUavGraphicalRunner.mo",
            [
                "extends MoSimQuadrotorModel.Experiment.Runners.Golden.AdapterSingleUavGoldenRunner(",
                "redeclare model Controller = MoSimQuadrotorModel.Control.Adapters.AWFFGraphicalRotorAdapter",
            ],
            failures,
        )
    )

    native_golden_path, native_golden = _read(
        "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/OfficialPidSysblockSingleUavRunner.mo"
    )
    native_golden_tokens = [
        "model OfficialPidSysblockSingleUavRunner",
        "MoSimQuadrotorModel.Control.Adapters.OfficialPidSysblockRotorAdapter controller",
        "replaceable model Trajectory = MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath",
        "Templates.Modules.BatteryPower",
        "Templates.Modules.ESCDrive",
        "Golden.Modules.RotorCommandChannel motor1(channel_index = 1)",
        "Golden.Modules.RotorCommandChannel motor2(channel_index = 2)",
        "Golden.Modules.RotorCommandChannel motor3(channel_index = 3)",
        "Golden.Modules.RotorCommandChannel motor4(channel_index = 4)",
        "MoSimQuadrotorModel.Vehicle.Sunray150Assembly plant(",
        "Templates.Modules.PerceptionInterface",
        "Templates.Modules.FlightController",
        "Templates.Modules.MissionComputer",
        "Templates.Modules.Supervisor",
        "origin = {-265, 5}",
        "{-370, -200}",
        "{-215, -215}",
        "{-230, -230}",
        "{-220, -245}",
        "extent = {{-390, -340}, {480, 210}}",
        "StartTime = 0, StopTime = 50",
        "Interval = 0.01",
        *native_golden_connection_tokens,
    ]
    native_golden_missing = _missing_tokens(native_golden, native_golden_tokens)
    if native_golden_missing:
        failures.append(
            "native Sysblock Golden entry: missing contract token(s) "
            + ", ".join(native_golden_missing)
        )
    if native_golden and "replaceable model Controller =" in native_golden:
        failures.append(
            "native Sysblock Golden entry must instantiate its controller concretely"
        )
    if native_golden and "connect(controller.rotor_command, plant.rotor_command)" in native_golden:
        failures.append(
            "native Sysblock Golden entry bypasses the explicit battery/ESC/rotor chain"
        )
    if native_golden and native_golden.count("Sunray150Assembly plant(") != 1:
        failures.append(
            "native Sysblock Golden entry must contain exactly one shared Sunray150Assembly"
        )
    files.append(
        {
            "path": "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/OfficialPidSysblockSingleUavRunner.mo",
            "exists": native_golden_path.exists(),
            "missing": native_golden_missing,
            "connection_contract_ok": not native_golden_missing,
            "controller_is_concrete": "replaceable model Controller =" not in native_golden,
        }
    )

    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Control/Adapters/OfficialPIDGraphicalRotorAdapter.mo",
            [
                "Control.Implementations.Graphical.PID.OfficialPidCoreSysblock core",
                "Control.Allocation.OfficialPidRotorCommandMapper mapper(",
                "profile = profile",
                "hover_speed = hover_speed",
                "command_scale = command_scale",
                "yaw_authority_scale = yaw_authority_scale",
                "yaw_pattern = yaw_pattern",
                "core_output_1_sign(k = 1)",
                "core_output_2_sign(k = -1)",
                "core_output_3_sign(k = 1)",
                "core_output_4_sign(k = -1)",
                "connect(core.y, core_output_1_sign.u)",
                "connect(core.y1, core_output_2_sign.u)",
                "connect(core.y2, core_output_3_sign.u)",
                "connect(core.y3, core_output_4_sign.u)",
                "connect(mapper.rotor_command, rotor_command)",
            ],
            failures,
        )
    )
    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Control/Adapters/OfficialPidSysblockRotorAdapter.mo",
            [
                "Control.Implementations.Graphical.PID.OfficialPidSysblockRunner",
                "connect(controller.rotor_command_1, rotor_command[1])",
                "connect(controller.rotor_command_2, rotor_command[2])",
                "connect(controller.rotor_command_3, rotor_command[3])",
                "connect(controller.rotor_command_4, rotor_command[4])",
                "__MWORKS(SECInstance = true)",
            ],
            failures,
        )
    )

    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Control/Allocation/OfficialPidRotorCommandMapper.mo",
            [
                "parameter Real hover_speed",
                "parameter Real command_scale",
                "parameter Real yaw_authority_scale",
                "parameter Real yaw_pattern[4]",
                "Modelica.Blocks.Math.Gain yaw_projection_1",
                "Modelica.Blocks.Math.Add non_yaw_1(k1 = 1, k2 = -1)",
                "Modelica.Blocks.Math.Gain yaw_authority_1(k = yaw_pattern[1] * yaw_authority_scale)",
                "Modelica.Blocks.Math.Gain yaw_authority_2(k = yaw_pattern[2] * yaw_authority_scale)",
                "Modelica.Blocks.Math.Gain yaw_authority_3(k = yaw_pattern[3] * yaw_authority_scale)",
                "Modelica.Blocks.Math.Gain yaw_authority_4(k = yaw_pattern[4] * yaw_authority_scale)",
                "Modelica.Blocks.Math.Add mapped_1(k1 = 1, k2 = 1)",
                "Modelica.Blocks.Sources.Constant hover_1",
                "Modelica.Blocks.Math.Gain spin_sign_1",
                "connect(spin_sign_1.y, rotor_command[1])",
                "connect(spin_sign_2.y, rotor_command[2])",
                "connect(spin_sign_3.y, rotor_command[3])",
                "connect(spin_sign_4.y, rotor_command[4])",
            ],
            failures,
        )
    )

    official_path, official = _read(
        "Models/MoSimQuadrotorModel/Control/Adapters/OfficialPIDRotorAdapter.mo"
    )
    official_mapping_tokens = [
        "amplitude_command[1] = core.y;",
        "amplitude_command[2] = -core.y1;",
        "amplitude_command[3] = core.y2;",
        "amplitude_command[4] = -core.y3;",
        "yaw_amplitude = sum({yaw_pattern[i] * amplitude_command[i] for i in 1:4}) / 4;",
        "non_yaw_amplitude[i] = amplitude_command[i] - yaw_pattern[i] * yaw_amplitude;",
        "mapped_amplitude[i] = non_yaw_amplitude[i]",
        "+ yaw_pattern[i] * yaw_authority_scale * yaw_amplitude;",
        "rotor_command[i] = profile.mworks_spin_command_sign[i]",
        "* (hover_speed + command_scale * mapped_amplitude[i]);",
    ]
    mapping_missing = [token for token in official_mapping_tokens if token not in official]
    if mapping_missing:
        failures.append(
            "OfficialPIDRotorAdapter.mo: missing preserved mapping formula "
            + ", ".join(mapping_missing)
        )
    files.append(
        {
            "path": "Models/MoSimQuadrotorModel/Control/Adapters/OfficialPIDRotorAdapter.mo",
            "exists": official_path.exists(),
            "missing": mapping_missing,
            "role": "unchanged_formal_mapping_reference",
        }
    )

    mapper_path, mapper = _read(
        "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID/OfficialPidSysblockMapper.mo"
    )
    mapper_topology_tokens = []
    for index in range(1, 5):
        mapper_topology_tokens.extend(
            [
                f"connect(amplitude_{index}, yaw_projection_{index}.u)",
                f"connect(amplitude_{index}, non_yaw_{index}.u1)",
                f"connect(yaw_component_{index}.y, non_yaw_{index}.u2)",
                f"connect(yaw_authority_{index}.y, mapped_{index}.u2)",
                f"connect(mapped_{index}.y, command_scale_{index}.u)",
                f"connect(spin_sign_{index}.y, rotor_command_{index})",
            ]
        )
    mapper_topology_missing = _missing_tokens(mapper, mapper_topology_tokens)
    if mapper_topology_missing:
        failures.append(
            "OfficialPidSysblockMapper.mo: incomplete native four-channel topology "
            + ", ".join(mapper_topology_missing)
        )
    files.append(
        {
            "path": "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID/OfficialPidSysblockMapper.mo",
            "exists": mapper_path.exists(),
            "missing": mapper_topology_missing,
            "role": "native_graphical_mapping_topology",
        }
    )

    plant_path, plant = _read("Models/MoSimQuadrotorModel/Vehicle/Sunray150Assembly.mo")
    plant_tokens = [
        "PhysicalWrenchAdapter physical(",
        "MoSimQuadrotorModel.Vehicle.Sensors.Sensors sensors",
        "Vehicle.Sunray150VisualShell visual_shell(profile = profile)",
        "annotation(Placement(transformation(origin = {-55, 10}",
        "annotation(Placement(transformation(origin = {105, 55}",
        "annotation(Placement(transformation(origin = {105, -45}",
        "annotation(Placement(transformation(origin = {-155, 100}",
        "connect(physical.body.frame_a, sensors.frame_a)",
        "connect(physical.body.frame_a, visual_shell.frame_a)",
        "rotor_speed[i] = physical.wrapper.dynamics.omega[i];",
        "position = sensors.PosMea;",
        "attitude = sensors.AngleMea;",
        "Diagram(coordinateSystem(extent = {{-240, -150}, {240, 145}}, grid = {2, 2}))",
    ]
    plant_missing = [token for token in plant_tokens if token not in plant]
    if plant_missing:
        failures.append(
            "Sunray150Assembly.mo: missing real plant/sensor binding "
            + ", ".join(plant_missing)
        )
    files.append(
        {
            "path": "Models/MoSimQuadrotorModel/Vehicle/Sunray150Assembly.mo",
            "exists": plant_path.exists(),
            "missing": plant_missing,
            "role": "shared_plant_reference",
        }
    )

    physical_path, physical = _read(
        "Models/MoSimQuadrotorModel/Vehicle/Dynamics/PhysicalWrenchAdapter.mo"
    )
    physical_actuator_tokens = [
        "WrapperSurface wrapper(",
        "wrapper.total_thrust",
        "forceAndTorque.force = applied_force_body",
        "forceAndTorque.torque = applied_torque_body",
    ]
    physical_actuator_missing = _missing_tokens(physical, physical_actuator_tokens)
    if physical_actuator_missing:
        failures.append(
            "PhysicalWrenchAdapter.mo: missing shared physical actuator chain "
            + ", ".join(physical_actuator_missing)
        )
    files.append(
        {
            "path": "Models/MoSimQuadrotorModel/Vehicle/Dynamics/PhysicalWrenchAdapter.mo",
            "exists": physical_path.exists(),
            "missing": physical_actuator_missing,
            "role": "shared_physical_actuator_chain",
        }
    )
    wrapper_path, wrapper = _read(
        "Models/MoSimQuadrotorModel/Vehicle/Dynamics/WrapperSurface.mo"
    )
    wrapper_actuator_tokens = [
        "RotorActuatorCore dynamics(profile = profile)",
        "dynamics.thrust",
        "dynamics.total_moment_body",
    ]
    wrapper_actuator_missing = _missing_tokens(wrapper, wrapper_actuator_tokens)
    if wrapper_actuator_missing:
        failures.append(
            "WrapperSurface.mo: missing RotorActuatorCore dynamics binding "
            + ", ".join(wrapper_actuator_missing)
        )
    files.append(
        {
            "path": "Models/MoSimQuadrotorModel/Vehicle/Dynamics/WrapperSurface.mo",
            "exists": wrapper_path.exists(),
            "missing": wrapper_actuator_missing,
            "role": "rotor_actuator_core_binding",
        }
    )

    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/Modules/RotorCommandChannel.mo",
            [
                "Modelica.Blocks.Math.Gain command_pass_through(k = 1)",
                "Modelica.Blocks.Math.Gain speed_pass_through(k = 1)",
                "connect(command_pass_through.y, command_to_plant)",
                "connect(speed_pass_through.y, speed_telemetry)",
            ],
            failures,
        )
    )
    channel_path, channel = _read(
        "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/Modules/RotorCommandChannel.mo"
    )
    if channel_path.exists() and "Vehicle.Electricals.Actuator" in channel:
        failures.append("RotorCommandChannel creates duplicate actuator dynamics")

    formal_path, formal = _read(
        "Models/MoSimQuadrotorModel/Experiment/Runners/Formal/OfficialPidFormalRunner.mo"
    )
    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Experiment/Runners/Formal/OfficialPidFormalRunner.mo",
            [
                "extends MoSimQuadrotorModel.Experiment.Runners.RotorCommandRunner(",
                "MoSimQuadrotorModel.Control.Adapters.OfficialPIDRotorAdapter",
            ],
            failures,
        )
    )
    if formal_path.exists() and "OfficialPIDGraphicalRotorAdapter" in formal:
        failures.append("Formal Official PID runner was redirected to the graphical adapter")

    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Experiment/Runners/package.order",
            ["Golden"],
            failures,
        )
    )
    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Control/Adapters/package.order",
            ["OfficialPIDGraphicalRotorAdapter", "OfficialPidSysblockMapperDiagnostics", "OfficialPidSysblockRotorAdapter"],
            failures,
        )
    )
    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Control/Allocation/package.order",
            ["OfficialPidRotorCommandMapper"],
            failures,
        )
    )
    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/package.order",
            [
                "Modules",
                "OfficialPidSingleUavGoldenRunner",
                "OfficialPidSysblockSingleUavRunner",
            ],
            failures,
        )
    )
    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/Modules/package.order",
            ["RotorCommandChannel", "DirectControlTelemetry", "SystemTelemetry", "TelemetryBusAggregator"],
            failures,
        )
    )
    files.append(
        _require_tokens(
            "Models/MoSimQuadrotorModel/Experiment/Templates/Modules/package.mo",
            [
                "block PerceptionInterface",
                "block FlightController",
                "block MissionComputer",
                "block Supervisor",
                "block BatteryPower",
                "block ESCDrive",
            ],
            failures,
        )
    )

    graphical_surface_checks = [
        (
            "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/OfficialPidSingleUavGoldenRunner.mo",
            [
                "origin={-460,225}",
                "origin={-285,185}",
                "origin={-35,185.5}",
                "origin={-35,75}",
                "origin={130,205}",
                "origin={280,220}",
                "origin={502.5,99.75}",
                "origin={-460,-4.25}",
                "origin={-302.5,-4.25}",
                "origin={130,-28.75}",
                "origin={130,42.5}",
                "extent={{-600,-340},{800,260}}",
            ],
        ),
        (
            "Models/MoSimQuadrotorModel/Vehicle/Dynamics/PhysicalWrenchAdapter.mo",
            [
                "WrapperSurface wrapper(",
                "Modelica.Mechanics.MultiBody.Parts.Body body(",
                "Modelica.Mechanics.MultiBody.Forces.WorldForceAndTorque forceAndTorque(",
                'textString = "Physical Wrench"',
                "__MWORKS(hide=false,version=\"26.3.0\")",
            ],
        ),
        (
            "Models/MoSimQuadrotorModel/Vehicle/Dynamics/WrapperSurface.mo",
            [
                "RotorActuatorCore dynamics(profile = profile)",
                'textString = "Rotor Actuation"',
                "Vehicle/Resources/Images/motor.png",
                "__MWORKS(hide=false,version=\"26.3.0\")",
            ],
        ),
        (
            "Models/MoSimQuadrotorModel/Vehicle/Sunray150VisualShell.mo",
            [
                "body_visual(",
                "propeller_front_right_visual(",
                "propeller_front_left_visual(",
                "propeller_back_left_visual(",
                "propeller_back_right_visual(",
                'textString = "Visual Shell"',
                "Vehicle/Resources/Images/Sunray150-Side.png",
                "__MWORKS(hide = false, version = \"26.3.0\")",
            ],
        ),
    ]
    graphical_surface_ok = True
    for relative_path, tokens in graphical_surface_checks:
        check = _require_tokens(relative_path, tokens, failures)
        files.append(check)
        graphical_surface_ok = graphical_surface_ok and not check["missing"]

    graphical_resources = _check_graphical_resources(failures)
    graphical_resources_ok = all(resource["exists"] for resource in graphical_resources)
    graphical_bitmap_aspects = _check_graphical_bitmap_aspects(failures)
    graphical_bitmap_aspect_ok = all(
        check["valid"] for check in graphical_bitmap_aspects
    )
    files.append(
        {
            "path": "Models/MoSimQuadrotorModel/Vehicle/Resources",
            "resources": graphical_resources,
            "role": "graphical_resource_bindings",
        }
    )
    files.append(
        {
            "path": "Models/MoSimQuadrotorModel/Vehicle/Resources/Images",
            "bitmap_aspects": graphical_bitmap_aspects,
            "role": "original_image_aspect_contract",
        }
    )

    return {
        "schema_version": "mosim.official_pid_golden_surface.v9",
        "source": "static_model_contract",
        "entry_model": "MoSimQuadrotorModel.Experiment.Runners.Golden.OfficialPidSingleUavGoldenRunner",
        "status": "pass" if not failures else "fail",
        "structure_ok": not failures,
        "formal_runner_preserved": formal_path.exists() and "OfficialPIDGraphicalRotorAdapter" not in formal,
        "official_pid_mapping_reference_ok": not mapping_missing,
        "golden_connection_contract_ok": not golden_connection_missing,
        "adapter_connection_contract_ok": not adapter_connection_missing,
        "golden_visible_wiring_ok": golden_visible_wiring_ok,
        "golden_interface_contract_ok": not golden_interface_missing,
        "golden_interface_wiring_ok": golden_interface_wiring_ok,
        "native_sysblock_golden_entry_ok": not native_golden_missing
        and "replaceable model Controller =" not in native_golden
        and "connect(controller.rotor_command, plant.rotor_command)" not in native_golden
        and native_golden.count("Sunray150Assembly plant(") == 1,
        "mapper_topology_ok": not mapper_topology_missing,
        "shared_plant_binding_ok": not plant_missing,
        "physical_actuator_chain_ok": not physical_actuator_missing and not wrapper_actuator_missing,
        "graphical_surface_ok": graphical_surface_ok,
        "graphical_resources_ok": graphical_resources_ok,
        "graphical_bitmap_aspect_ok": graphical_bitmap_aspect_ok,
        "failures": failures,
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    summary = run_checks()
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
