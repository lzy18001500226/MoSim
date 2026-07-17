import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts/control_platform/build_fault_tolerant_control_mworks_models.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("p7_ftc_builder", BUILDER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_builder_declares_six_persistent_fault_fixtures() -> None:
    module = load_builder()
    assert len(module.VARIANTS) == 6
    assert module.EXPECTED_ACTIONS[5] == 3
    assert module.SCENARIO_OVERRIDES[6]["response_1"] < module.BASE_INPUTS["response_1"]
    assert module.SCENARIO_OVERRIDES[6]["response_3"] < module.BASE_INPUTS["response_3"]


def test_embedded_wrapper_has_state_initialization_and_fixed_io() -> None:
    text = load_builder().embedded_c()
    assert "MosimFaultTolerantControlStepScalar" in text
    assert "static MosimFtcState states[7]" in text
    assert "static int initialized[7]" in text
    assert "malloc(" not in text
