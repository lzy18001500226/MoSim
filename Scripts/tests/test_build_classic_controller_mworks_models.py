from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/build_classic_controller_mworks_models.py"


def load_module():
    spec = importlib.util.spec_from_file_location("classic_mworks_builder", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fixture_has_real_block_topology_for_every_port() -> None:
    module = load_module()
    model = module.fixture_model("Fixture", 1, "Controller")
    assert model.count("Sources.Constant") == len(module.INPUTS)
    assert model.count("Port.Outport") == len(module.OUTPUTS)
    assert model.count("connect(") == len(module.INPUTS) + len(module.OUTPUTS)


def test_embedded_bridge_executes_project_core_and_persistent_state() -> None:
    source = load_module().embedded_c()
    assert "#define MOSIM_CLASSIC_FOPID_MEMORY 16" in source
    assert "mosim_classic_step" in source
    assert "static MosimClassicState states[6]" in source
    assert "MosimClassicStepScalar" in source


def test_fixture_layout_has_readable_port_spacing() -> None:
    model = load_module().fixture_model("Fixture", 1, "Controller")
    assert "origin={{-500,420}}" in model
    assert "origin={{-500,376}}" in model
    assert "origin={{500,420}}" in model
    assert "origin={{500,396}}" in model
    assert "extent={{-110,-440},{110,440}}" in model
    assert "extent={{-620,-480},{620,480}}" in model


def test_builder_adds_explicit_controller_icon() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'textString="Classic Controller"' in text
    assert "Rectangle(fillColor={245,245,245}" in text


def test_bridge_layout_expands_scalar_ports_and_connections() -> None:
    module = load_module()
    sample = (
        "Diagram(coordinateSystem(extent={{-340,-620},{340,280}} "
        "origin={0,0}, extent={{-28,-20},{28,20}} "
        "origin={-300,250} points={{-250,250},{-50,250}} "
        "origin={300,160} points={{50,160},{250,160}}"
    )
    result = module.layout_bridge_model(sample)
    assert "extent={{-620,-480},{620,480}}" in result
    assert "extent={{-110,-440},{110,440}}" in result
    assert "origin={-500,420}" in result
    assert "points={{-450,420},{-110,420}}" in result
    assert "origin={500,420}" in result
    assert "points={{110,420},{450,420}}" in result
