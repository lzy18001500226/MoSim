from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/quality/qa_check.py"


def load_module():
    spec = importlib.util.spec_from_file_location("qa_check", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_diagnostics_schema_allows_missing_reference_only():
    module = load_module()
    config = {"model": {}, "simulation": {}, "result": {}}
    assert module.alternate_scenario_schema(config, Path("Config/scenarios/diagnostics/x.yaml"), ["reference"]) == "diagnostics_without_reference"
    assert module.alternate_scenario_schema(config, Path("Config/scenarios/diagnostics/x.yaml"), ["model"]) is None


def test_legacy_ros2_schema_requires_explicit_boundary():
    module = load_module()
    config = {"ros2": {}, "claim_boundary": {"not_claimed": ["closed_loop"]}, "evidence_level": "gazebo_ros2_validation_smoke"}
    path = Path("Config/scenarios/system/sunray150_gazebo_ros2_smoke.yaml")
    assert module.alternate_scenario_schema(config, path, ["model", "simulation", "reference", "result"]) == "legacy_ros2_runtime_smoke"
    config.pop("claim_boundary")
    assert module.alternate_scenario_schema(config, path, ["model", "simulation", "reference", "result"]) is None
