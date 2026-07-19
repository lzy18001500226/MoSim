import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/ui/build_factory_l2_2d_map.py"
SPEC = importlib.util.spec_from_file_location("build_factory_l2_2d_map", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def apply(matrix, x, y):
    return (
        matrix[0][0] * x + matrix[0][1] * y + matrix[0][2],
        matrix[1][0] * x + matrix[1][1] * y + matrix[1][2],
    )


def test_factory_map_build_and_round_trip(tmp_path):
    result = MODULE.build_map(MODULE.DEFAULT_TRUTH, MODULE.DEFAULT_ENVELOPE, MODULE.DEFAULT_MESH_DIR, tmp_path)

    assert result["map_id"] == "factory_l2"
    assert result["status"] == "full_factory_operator_map_candidate"
    assert result["feature_counts"]["mesh_section_segments"] > 1000
    assert (tmp_path / "floorplan.png").is_file()

    transform = json.loads((tmp_path / "world_to_pixel.json").read_text(encoding="utf-8"))
    forward = transform["world_to_pixel_3x3"]
    inverse = transform["pixel_to_world_3x3"]
    for world_x, world_y in ((-608.09999, -284.65), (587.89997, 246.35), (-10.575025, -19.36313)):
        pixel_x, pixel_y = apply(forward, world_x, world_y)
        recovered_x, recovered_y = apply(inverse, pixel_x, pixel_y)
        assert abs(recovered_x - world_x) < 1e-9
        assert abs(recovered_y - world_y) < 1e-9

    bounds = transform["bounds_m"]
    overlay = result["map_scope"]["indoor_task_overlay_bounds_m"]
    assert bounds["min_x_m"] <= overlay["min_x_m"] < overlay["max_x_m"] <= bounds["max_x_m"]
    assert bounds["min_y_m"] <= overlay["min_y_m"] < overlay["max_y_m"] <= bounds["max_y_m"]

    geojson = json.loads((tmp_path / "structure.geojson").read_text(encoding="utf-8"))
    task_features = [
        feature
        for feature in geojson["features"]
        if feature["properties"].get("semantic_type") == "task_boundary"
    ]
    assert len(task_features) == 1


def test_factory_map_is_deterministic(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    MODULE.build_map(MODULE.DEFAULT_TRUTH, MODULE.DEFAULT_ENVELOPE, MODULE.DEFAULT_MESH_DIR, first)
    MODULE.build_map(MODULE.DEFAULT_TRUTH, MODULE.DEFAULT_ENVELOPE, MODULE.DEFAULT_MESH_DIR, second)

    for name in ("floorplan.png", "structure.geojson", "world_to_pixel.json", "scene_map.json"):
        assert (first / name).read_bytes() == (second / name).read_bytes()
