from pathlib import Path


TEXT = (Path(__file__).resolve().parents[1] / "control_platform/build_mpc_graphical_mil.py").read_text(encoding="utf-8")


def test_native_graphical_builder_uses_official_sysblock_api() -> None:
    for token in ("NewModel", "AddComponent", "ConnectPort", "SetParamValue", "CheckModel", "SimulateModelEx", "ExportDiagram"):
        assert f"ModelingPy.{token}" in TEXT
    assert "CFunction" not in TEXT.split("def build_variant", 1)[1].split("def rows", 1)[0]


def test_fixed_budget_and_stateful_paths_are_explicit() -> None:
    assert "range(1, 6)" in TEXT
    assert "(-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5)" in TEXT
    assert '"SysplorerEmbeddedCoder.Discrete.UnitDelay"' in TEXT
    assert 'initCond=1.0' in TEXT
    assert '"SysplorerEmbeddedCoder.MathOperation.Maxmin"' in TEXT
    assert '"SysplorerEmbeddedCoder.Discontinuities.Saturation"' in TEXT


def test_graphical_claim_is_bounded_to_controller_core() -> None:
    assert "controller-core equivalence" in TEXT
    assert "ATTITUDE_THRUST quaternion/thrust geometry" in TEXT
    assert "all_behavior_equivalent" in TEXT
