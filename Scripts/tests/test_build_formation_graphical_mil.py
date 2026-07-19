from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts/control_platform/build_formation_graphical_mil.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_formation_graphical_mil", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load P8 graphical builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_all_nine_formation_modes_have_distinct_graphical_fixtures() -> None:
    module = load_builder()
    assert len(module.MODE_SPECS) == 9
    assert len({module.model_name(mode) for mode in module.MODE_SPECS}) == 9
    for mode, blocks in module.MODE_SPECS.items():
        source = module.build_model(mode)
        assert module.model_name(mode) in source
        for block in blocks:
            assert block in source
        assert source.count("connect(") == 9
        assert "Instance(u(u1,u2))" in source


def test_graphical_fixtures_expose_report_outputs() -> None:
    module = load_builder()
    for mode in module.MODE_SPECS:
        source = module.build_model(mode)
        for output in ("formation_command", "formation_error", "minimum_pair_distance"):
            assert f"Outport {output}" in source
        assert "StopTime=0.4" in source
