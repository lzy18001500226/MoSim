from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts/control_platform/build_formation_control_mworks_models.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("p8_builder", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_builder_has_nine_fixed_size_graphical_fixtures():
    module = load_builder()
    assert len(module.VARIANTS) == 9
    assert len(module.INPUTS) == 33
    assert len(module.OUTPUTS) == 24
    model = module.fixture_model("Fixture", 8, "Bridge")
    assert model.count("SysplorerEmbeddedCoder.Sources.Constant") == 33
    assert model.count("SysplorerEmbeddedCoder.Port.Outport") == 24
    assert "connect(formation.safety_corrections_out, safety_corrections);" in model


def test_embedded_wrapper_calls_project_formation_core():
    module = load_builder()
    text = module.embedded_c()
    assert "MosimFormationControlStepScalar" in text
    assert "mosim_formation_step" in text
    assert "MOSIM_FORMATION_AGENTS = 3" in text
    assert "mosim_formation_isfinite(input->dt)" in text
    assert "!isfinite(" not in text


def test_bridge_and_fixture_use_the_same_50_hz_sample_time():
    module = load_builder()
    generic = module.load_p2_builder().load_generic_builder()
    bridge = generic.build_model("Bridge", ROOT / "generated", "void noop(void) {}", False)
    bridge = module.set_bridge_sample_time(bridge, module.BASE_INPUTS["dt"])
    fixture = module.fixture_model("Fixture", 1, "Bridge")
    assert 'SampleTime(auto=true,group="")=0.02,OutputInterval=0.02' in bridge
    assert 'SampleTime(group="D1")=0.01' not in bridge
    assert 'SampleTime(auto=true,group="")=0.02,OutputInterval=0.02' in fixture
