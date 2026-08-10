from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "mworks" / "repair_official_pid_sysblock_visual_wiring.py"
SPEC = importlib.util.spec_from_file_location("official_pid_visual_wiring", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


SOURCES = (
    "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID/OfficialPidNativeSysblockCore.mo",
    "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID/OfficialPidSysblockCore.mo",
    "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID/OfficialPidSysblockAdapter.mo",
    "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID/OfficialPidSysblockMapper.mo",
    "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID/OfficialPidSysblockRunner.mo",
)


def test_visual_repair_only_changes_degenerate_line_metadata() -> None:
    source = """within Example;
model WiringFixture
  SysplorerEmbeddedCoder.Port.Inport source_port
    annotation(Placement(transformation(origin = {-40, 0}, extent = {{-10, -10}, {10, 10}})));
  SysplorerEmbeddedCoder.MathOperation.Gain gain
    annotation(Placement(transformation(origin = {0, 0}, extent = {{-10, -10}, {10, 10}})));
  SysplorerEmbeddedCoder.Port.Outport output_port
    annotation(Placement(transformation(origin = {40, 0}, extent = {{-10, -10}, {10, 10}})));
equation
  connect(source_port, gain.u);
  connect(gain.y, output_port)
    annotation(Line(points = {{0, 0}, {0, 0}}));
end WiringFixture;
"""

    before_connections = MODULE.connection_signature(source, source.index("equation"))
    before_placements = MODULE.placement_signature(source, source.index("equation"))
    repaired, summary = MODULE.repair_text(source)

    assert summary["ok"] is True
    assert summary["added_line_count"] == 1
    assert summary["repaired_line_count"] == 1
    assert MODULE.connection_signature(repaired, repaired.index("equation")) == before_connections
    assert MODULE.placement_signature(repaired, repaired.index("equation")) == before_placements


def test_official_pid_sysblock_tree_has_a_non_degenerate_line_for_every_connection() -> None:
    for relative_path in SOURCES:
        audit = MODULE.audit_text((ROOT / relative_path).read_text(encoding="utf-8"))
        assert audit["ok"], f"{relative_path}: {audit}"


def test_runner_wires_terminate_at_the_second_layer_core_and_mapper_ports() -> None:
    """The nested Sysblock port names are not diagram coordinates at the runner level."""

    source = (
        ROOT
        / "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID/"
        / "OfficialPidSysblockRunner.mo"
    ).read_text(encoding="utf-8")

    def line_for(connection: str) -> str:
        start = source.index(connection)
        return source[start : source.index(";", start)]

    core_inputs = {
        "x_ref": 260,
        "y_ref": 205,
        "z_ref": 150,
        "x_mea": 95,
        "y_mea": 40,
        "z_mea": -15,
        "roll_mea": -70,
        "pitch_mea": -125,
        "yaw_mea": -180,
    }
    for port, height in core_inputs.items():
        statement = line_for(f"connect({port}, controller_core.{port})")
        assert f"{{-255, {height}}}" in statement

    for port, height in {"y": 180, "y1": 60, "y2": -60, "y3": -180}.items():
        statement = line_for(f"connect(controller_core.{port},")
        assert f"{{-105, {height}}}" in statement

    for index, height in enumerate((180, 110, 40, -30), start=1):
        mapper_input = line_for(
            f"connect(output_{index}_sign.y, rotor_mapper.amplitude_{index})"
        )
        mapper_output = line_for(
            f"connect(rotor_mapper.rotor_command_{index}, rotor_command_{index})"
        )
        assert f"{{225, {height}}}" in mapper_input
        assert f"{{375, {height}}}" in mapper_output


def test_golden_runner_mapper_uses_second_layer_port_endpoints() -> None:
    source = (
        ROOT
        / "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/"
        / "OfficialPidSingleUavGoldenRunner.mo"
    ).read_text(encoding="utf-8")

    def line_for(connection: str) -> str:
        start = source.index(connection)
        return source[start : source.index(";", start)]

    mapper_inputs = {
        1: "{-105,238}",
        2: "{-105,203}",
        3: "{-105,168}",
        4: "{-105,133}",
    }
    mapper_outputs = {
        1: "{35,238}",
        2: "{36.8,203}",
        3: "{36.8,168}",
        4: "{36.8,133}",
    }
    for index in range(1, 5):
        input_line = line_for(
            f"connect(rotor_sign_{index}.y, mapper.amplitude_{index})"
        )
        output_line = line_for(
            f"connect(mapper.rotor_command_{index}, esc.motor_command_raw[{index}])"
        )
        assert mapper_inputs[index] in input_line
        assert mapper_outputs[index] in output_line


def test_official_pid_golden_runner_has_a_non_degenerate_line_for_every_connection() -> None:
    relative_path = "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/OfficialPidSingleUavGoldenRunner.mo"
    source = (ROOT / relative_path).read_text(encoding="utf-8")

    audit = MODULE.audit_text(source)

    assert audit["ok"], f"{relative_path}: {audit}"
    assert audit["connect_count"] >= 35
    assert "connect(telemetry_bus.vehicle_bus, system_telemetry.vehicle_bus)" in source
    assert "connect(telemetry_bus.autonomy_bus, system_telemetry.autonomy_bus)" in source
    assert "connect(esc.esc_health, system_telemetry.vehicle_bus[1:4])" not in source


def test_official_pid_golden_runner_exposes_native_core_ports_at_root() -> None:
    relative_path = "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/OfficialPidSingleUavGoldenRunner.mo"
    source = (ROOT / relative_path).read_text(encoding="utf-8")

    assert "OfficialPidSysblockCore core" in source
    assert "OfficialPidSysblockCoreAdapter core" not in source
    core_source = (ROOT / "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID/OfficialPidSysblockCore.mo").read_text(encoding="utf-8")
    assert 'textString="Official PID"' in core_source
    assert 'textString="SYSBLOCK CORE"' in core_source
    assert 'textString="9 IN | 4 OUT"' in core_source
    for connection in (
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
    ):
        assert connection in source


def test_official_pid_golden_runner_exposes_native_mapper_ports_at_root() -> None:
    relative_path = "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/OfficialPidSingleUavGoldenRunner.mo"
    source = (ROOT / relative_path).read_text(encoding="utf-8")

    assert "OfficialPidSysblockMapper mapper" in source
    assert "OfficialPidSysblockMapperAdapter mapper" not in source
    assert "OfficialPidSysblockMapperDiagnostics mapper_diagnostics" in source
    assert "rotor_command = esc.motor_command_raw;" in source
    assert "= mapper.rotor_command_" not in source
    mapper_source = (ROOT / "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID/OfficialPidSysblockMapper.mo").read_text(encoding="utf-8")
    assert 'textString="SYSBLOCK MAPPER"' in mapper_source
    assert 'textString="4 IN | 4 OUT"' in mapper_source
    for connection in (
        "connect(rotor_sign_1.y, mapper.amplitude_1)",
        "connect(rotor_sign_2.y, mapper.amplitude_2)",
        "connect(rotor_sign_3.y, mapper.amplitude_3)",
        "connect(rotor_sign_4.y, mapper.amplitude_4)",
        "connect(mapper.rotor_command_1, esc.motor_command_raw[1])",
        "connect(mapper.rotor_command_2, esc.motor_command_raw[2])",
        "connect(mapper.rotor_command_3, esc.motor_command_raw[3])",
        "connect(mapper.rotor_command_4, esc.motor_command_raw[4])",
        "connect(mapper_diagnostics.direct_control_bus, direct_control_telemetry.mapper_bus)",
    ):
        assert connection in source


def test_direct_telemetry_chain_uses_uniform_port_geometry_and_real_bus_wires() -> None:
    expected_ports = {
        "Models/MoSimQuadrotorModel/Guidance/Trajectories/PartialTrajectory.mo": (
            "iconTransformation(origin = {100, 60}, extent = {{-8, -8}, {8, 8}})",
            "iconTransformation(origin = {100, -75}, extent = {{-8, -8}, {8, 8}})",
        ),
        "Models/MoSimQuadrotorModel/Control/Allocation/OfficialPidRotorCommandMapper.mo": (
            "iconTransformation(origin = {-100, 0}, extent = {{-8, -8}, {8, 8}})",
            "iconTransformation(origin = {100, 43}, extent = {{-8, -8}, {8, 8}})",
            "iconTransformation(origin = {100, -60}, extent = {{-8, -8}, {8, 8}})",
        ),
        "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/Modules/DirectControlTelemetry.mo": (
            "iconTransformation(origin = {-100, 45}, extent = {{-8, -8}, {8, 8}})",
            "iconTransformation(origin = {-100, -45}, extent = {{-8, -8}, {8, 8}})",
        ),
        "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/Modules/RotorCommandChannel.mo": (
            "iconTransformation(origin = {-100, 35}, extent = {{-8, -8}, {8, 8}})",
            "iconTransformation(origin = {-100, -35}, extent = {{-8, -8}, {8, 8}})",
            "iconTransformation(origin = {100, 35}, extent = {{-8, -8}, {8, 8}})",
            "iconTransformation(origin = {100, -35}, extent = {{-8, -8}, {8, 8}})",
        ),
        "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/Modules/TelemetryBusAggregator.mo": (
            "iconTransformation(origin = {100, 60}, extent = {{-8, -8}, {8, 8}})",
            "iconTransformation(origin = {100, -60}, extent = {{-8, -8}, {8, 8}})",
        ),
        "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/Modules/SystemTelemetry.mo": (
            "iconTransformation(origin = {-100, 60}, extent = {{-8, -8}, {8, 8}})",
            "iconTransformation(origin = {-100, -60}, extent = {{-8, -8}, {8, 8}})",
        ),
    }

    for relative_path, ports in expected_ports.items():
        source = (ROOT / relative_path).read_text(encoding="utf-8")
        for port in ports:
            assert port in source, f"{relative_path} is missing standardized port geometry: {port}"

    runner = (ROOT / "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/OfficialPidSingleUavGoldenRunner.mo").read_text(encoding="utf-8")
    trajectory = (ROOT / "Models/MoSimQuadrotorModel/Guidance/Trajectories/PartialTrajectory.mo").read_text(encoding="utf-8")
    assert "connect(reference.direct_control_bus, direct_control_telemetry.trajectory_bus)" in runner
    assert "connect(mapper_diagnostics.direct_control_bus, direct_control_telemetry.mapper_bus)" in runner
    assert "__MWorks_Manhattanize" not in runner
    assert "transformation(origin={-460,135.25}," in runner
    assert "Multiplex2 direct_control_multiplex(n1 = 3, n2 = 3)" in trajectory
    assert "connect(velocity_command, direct_control_multiplex.u1)" in trajectory
    assert "connect(acceleration_command, direct_control_multiplex.u2)" in trajectory
    assert "connect(direct_control_multiplex.y, direct_control_bus)" in trajectory
    assert "direct_control_bus[1:3] =" not in trajectory
    assert "direct_control_bus[4:6] =" not in trajectory


def test_mapper_sum_wires_terminate_at_real_add_input_ports() -> None:
    relative_path = "Models/MoSimQuadrotorModel/Control/Allocation/OfficialPidRotorCommandMapper.mo"
    source = (ROOT / relative_path).read_text(encoding="utf-8")
    expected_lines = {
        "connect(mapped_sum_first3.y, mapped_sum.u1)": "{{93, -100}, {110, -100}, {110, -88}, {127, -88}}",
        "connect(amplitude_sum_first3.y, amplitude_sum.u1)": "{{93, -150}, {110, -150}, {110, -138}, {127, -138}}",
        "connect(amplitude_command[4], amplitude_sum.u2)": "{{-250, 0}, {-225, 0}, {-225, -175}, {110, -175}, {110, -162}, {127, -162}}",
    }

    for connection, points in expected_lines.items():
        statement = source[source.index(connection) : source.index(";", source.index(connection))]
        assert points in statement, f"{connection} must terminate at its Add input port"


def test_parent_bridge_and_golden_runner_include_indexed_interface_connections() -> None:
    sources = {
        "Models/MoSimQuadrotorModel/Control/Adapters/OfficialPidSysblockRotorAdapter.mo": 13,
        "Models/MoSimQuadrotorModel/Experiment/Runners/Golden/OfficialPidSysblockSingleUavRunner.mo": 30,
    }

    for relative_path, minimum_connect_count in sources.items():
        audit = MODULE.audit_text((ROOT / relative_path).read_text(encoding="utf-8"))
        assert audit["ok"], f"{relative_path}: {audit}"
        assert audit["connect_count"] >= minimum_connect_count


def test_indexed_inherited_boundary_port_with_a_line_is_auditable() -> None:
    source = """within Example;
model IndexedBoundaryFixture
  SysplorerEmbeddedCoder.Port.Inport local_port
    annotation(Placement(transformation(origin = {0, 0}, extent = {{-10, -10}, {10, 10}})));
equation
  connect(boundary_signal[1], local_port)
    annotation(Line(points = {{-20, 0}, {-10, 0}}));
end IndexedBoundaryFixture;
"""

    audit = MODULE.audit_text(source)

    assert audit["ok"] is True
    assert audit["connect_count"] == 1
    assert audit["boundary_endpoint_count"] == 1
