from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "control_platform" / "build_wave_a_mworks_models.py"


def module():
    spec = importlib.util.spec_from_file_location("wave_a_builder", BUILDER)
    assert spec and spec.loader
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def test_embedded_core_and_fixture_are_real_executable_models() -> None:
    builder = module()
    include = builder.embedded_c()
    assert "mosim_wave_a_step" in include
    assert "MosimWaveAStepScalar" in include
    assert "double *commanded_collective_thrust_n" in include
    fixture = builder.fixture_model("Probe", 1, "MoSim_WaveA_CFunction_Sysblock")
    assert "SysplorerEmbeddedCoder.Sources.Constant controller_id_source(k=1.0)" in fixture
    assert "origin={-260,260},extent={{-8,-8},{8,8}}" in fixture
    assert "connect(controller.desired_acceleration_x_out, desired_acceleration_x);" in fixture
    assert "connect(controller.commanded_collective_thrust_n_out, commanded_collective_thrust_n);" in fixture
    schema = builder.runtime_schema("lqr", 1, "MoSim_WaveA_CFunction_Sysblock")
    assert schema["input_global"] == "ockGbIn"
    assert schema["output_global"] == "lockGbOut"
    assert schema["input_sequence"][0]["controller_id_in"] == 1.0
    assert "commanded_collective_thrust_n_out" in schema["output_fields"]
