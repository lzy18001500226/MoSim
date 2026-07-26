import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "quality" / "build_formal_closed_loop_harness_map.py"


def load_module():
    spec = importlib.util.spec_from_file_location("formal_closed_loop_harness_map", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_resolves_the_actual_unqualified_whole_aircraft_controller_type(tmp_path: Path) -> None:
    module = load_module()
    module.ROOT = tmp_path
    module.SYSBLOCK_DEFINITION_ROOT = tmp_path / "Models/MoSimQuadrotorModel/Control/Implementations/Sysblocks"

    source = tmp_path / "Models/MoSimQuadrotorModel/Experiment/Templates/Example.mo"
    source.parent.mkdir(parents=True)
    source.write_text(
        "within MoSimQuadrotorModel.Experiment.Templates;\n"
        "model Example\n"
        "  ActualController controller3_2;\n"
        "end Example;\n",
        encoding="utf-8",
    )
    definition = module.SYSBLOCK_DEFINITION_ROOT / "ActualController.mo"
    definition.parent.mkdir(parents=True)
    definition.write_text(
        "within MoSimQuadrotorModel.Control.Implementations.Sysblocks;\n"
        "model ActualController\n"
        "end ActualController;\n",
        encoding="utf-8",
    )

    alias = source.parent / "ActualController.mo"
    alias.write_text(
        "within MoSimQuadrotorModel.Experiment.Templates;\n"
        "model ActualController\n"
        "  extends MoSimQuadrotorModel.Control.Implementations.Sysblocks.ActualController;\n"
        "end ActualController;\n",
        encoding="utf-8",
    )

    prerequisites = module.whole_aircraft_sysblock_load_prerequisites(source, "fixed_example")

    assert prerequisites == [
        {
            "role": "embedded_sysblock_definition",
            "source_component": "controller3_2",
            "source_declared_type": "ActualController",
            "model_file": "Models/MoSimQuadrotorModel/Control/Implementations/Sysblocks/ActualController.mo",
            "model_class": "MoSimQuadrotorModel.Control.Implementations.Sysblocks.ActualController",
            "model_sha256": module.sha256_file(definition),
        },
        {
            "role": "namespace_compatibility_alias",
            "source_component": "controller3_2",
            "source_declared_type": "ActualController",
            "model_file": "Models/MoSimQuadrotorModel/Experiment/Templates/ActualController.mo",
            "model_class": "MoSimQuadrotorModel.Experiment.Templates.ActualController",
            "model_sha256": module.sha256_file(alias),
            "base_model_class": "MoSimQuadrotorModel.Control.Implementations.Sysblocks.ActualController",
        },
    ]
