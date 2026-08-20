import importlib.util
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Scripts" / "sunray" / "materialize_gazebo_world_overlay.py"


def load_module():
    spec = importlib.util.spec_from_file_location("materialize_gazebo_world_overlay", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_materialize_world_overlay_changes_only_requested_ode_values(tmp_path: Path) -> None:
    module = load_module()
    source = tmp_path / "factory.sdf"
    source.write_text(
        """<?xml version=\"1.0\"?>
<sdf version=\"1.6\"><world name=\"factory\"><physics name=\"default\" type=\"ode\"><max_step_size>0.001</max_step_size><real_time_update_rate>1000</real_time_update_rate></physics><include><uri>model://factory_chunk</uri></include></world></sdf>
""",
        encoding="utf-8",
    )
    output = tmp_path / "Results" / "run" / "factory_overlay.sdf"
    manifest = tmp_path / "Results" / "run" / "factory_overlay.json"

    payload = module.materialize_world_overlay(tmp_path, source, output, manifest, 0.0025, 400.0)

    tree = ET.parse(output)
    physics = tree.getroot().find("world/physics")
    assert physics is not None
    assert physics.findtext("max_step_size") == "0.0025"
    assert physics.findtext("real_time_update_rate") == "400"
    assert tree.getroot().findtext("world/include/uri") == "model://factory_chunk"
    assert "0.001" in source.read_text(encoding="utf-8")
    assert payload["world"]["max_step_size_s"] == 0.0025
    assert json.loads(manifest.read_text(encoding="utf-8"))["status"] == "generated"


def test_project_path_rejects_overlay_output_outside_results(tmp_path: Path) -> None:
    module = load_module()

    try:
        module.project_path(tmp_path, str(tmp_path / "outside.sdf"), results_only=True)
    except ValueError as exc:
        assert "Results" in str(exc)
    else:
        raise AssertionError("output outside Results was accepted")
