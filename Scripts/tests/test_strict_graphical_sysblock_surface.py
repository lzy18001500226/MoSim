from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "mworks" / "check_strict_graphical_sysblock_surface.py"
SPEC = importlib.util.spec_from_file_location("strict_graphical_sysblock_surface", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_text_backed_modelica_inheritance_cannot_pass_as_strict_native_sysblock() -> None:
    errors: list[str] = []
    MODULE.check_core(
        "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID/OfficialPidCoreSysblock.mo",
        None,
        "OfficialPidCoreSysblock",
        errors,
    )

    assert any("extends ModelWorkspace" in error for error in errors)
    assert any("non-native Modelica controller base" in error for error in errors)


def test_native_official_pid_core_has_non_degenerate_visible_lines() -> None:
    errors: list[str] = []
    MODULE.check_core(
        "Models/MoSimQuadrotorModel/Control/Implementations/Graphical/PID/OfficialPidNativeSysblockCore.mo",
        None,
        "OfficialPidNativeSysblockCore",
        errors,
    )

    assert errors == []


def test_api_roundtrip_official_pid_core_is_rejected_for_zero_length_lines() -> None:
    errors: list[str] = []
    MODULE.check_core(
        "Results/mworks_live_gate/native_sysblock_modelica_embedding_20260805/api_roundtrip/OfficialPidNativeSysblockApiCore.mo",
        None,
        "OfficialPidNativeSysblockApiCore",
        errors,
    )

    assert any("degenerate visible Line" in error for error in errors)


def test_official_pid_adapter_cannot_hide_the_text_backed_core() -> None:
    errors: list[str] = []
    MODULE.check_adapter(
        "Models/MoSimQuadrotorModel/Control/Adapters/OfficialPIDGraphicalRotorAdapter.mo",
        errors,
    )

    assert any("text-backed controller core" in error for error in errors)


def test_indexed_connection_without_a_line_is_rejected() -> None:
    errors: list[str] = []
    source = """model IndexedFixture
  SysplorerEmbeddedCoder.Port.Inport input_port
    annotation(Placement(transformation(origin = {-20, 0}, extent = {{-10, -10}, {10, 10}})));
  SysplorerEmbeddedCoder.Port.Outport output_port
    annotation(Placement(transformation(origin = {20, 0}, extent = {{-10, -10}, {10, 10}})));
equation
  connect(input_port[1], output_port);
end IndexedFixture;
"""

    MODULE.check_graphical_surface(source, "indexed", errors)

    assert any("connection 1 has no visible Line annotation" in error for error in errors)
