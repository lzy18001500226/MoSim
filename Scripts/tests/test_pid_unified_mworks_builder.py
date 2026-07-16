from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts/control_platform/build_pid_unified_mworks_models.py"


def module():
    spec = importlib.util.spec_from_file_location("pid_mworks_builder", BUILDER)
    assert spec and spec.loader
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def test_embedded_core_exposes_all_six_pid_scope_items() -> None:
    builder = module()
    code = builder.embedded_c()
    assert "MosimPidUnifiedStepScalar" in code
    assert "mosim_cascade_pid_step" in code
    assert "outer->schedule_gain = 0.4" in code
    assert "outer->fuzzy_gain = 0.3" in code
    assert "outer->neural_residual_limit = 0.25" in code
    assert "outer->anti_windup_gain = 1.0" in code
    assert "outer->feedforward_gain = 0.5" in code
    assert set(builder.VARIANTS.values()) == {
        "cascade_pid", "gain_scheduled_pid", "fuzzy_pid", "neural_pid",
        "anti_windup", "feedforward_profile",
    }


def test_fixture_is_executable_sysblock_model() -> None:
    builder = module()
    model = builder.fixture_model("Probe", 5, "MoSim_PID_Unified_CFunction_Sysblock")
    assert "SysplorerEmbeddedCoder.Sources.Constant setpoint_source(k=2.0)" in model
    assert 'IntegratorStep=0.01' in model
    assert 'StopTime=0.2' in model
    assert builder.BASE_CONSTANTS["dt"] == 0.01
    assert builder.BASE_CONSTANTS["setpoint"] == 0.5
    assert "connect(controller.command_out, command);" in model
    assert "connect(controller.status_code_out, status_code);" in model
