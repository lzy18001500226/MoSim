import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "Scripts/sunray/check_enhancement_generated_runtime_provenance.py"
SPEC = importlib.util.spec_from_file_location("enhancement_provenance", PATH)
assert SPEC is not None and SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def test_checker_declares_six_profiles_and_generated_identity() -> None:
    assert CHECKER.BASE.CONTROLLERS == {
        "l1_adaptive": 1,
        "awff": 2,
        "complete_adrc": 3,
        "standardized_indi": 4,
        "parameter_scheduling": 5,
        "ilc": 6,
    }
    assert CHECKER.BASE.BACKEND == "enhancement_attitude_thrust"
    assert CHECKER.BASE.BACKEND_DEFINITION == "MOSIM_PX4CTRL_GENERATED_BACKEND_ENHANCEMENT_ATTITUDE_THRUST"
    assert CHECKER.BASE.BINARY_SYMBOL == "MosimEnhancementStepScalar"
