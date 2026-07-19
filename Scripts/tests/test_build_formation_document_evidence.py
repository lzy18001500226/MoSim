from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts/control_platform/build_formation_document_evidence.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_formation_document_evidence", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load P8 evidence builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_p8_batch_binds_nine_distinct_routes_and_eighteen_images() -> None:
    batch = load_builder().build()
    assert batch["status"] == "passed_with_documented_boundaries"
    assert batch["route_count"] == 9
    assert len({route["mode"] for route in batch["routes"]}) == 9
    for route in batch["routes"]:
        assert (route["graphical_screenshot"]["width"], route["graphical_screenshot"]["height"]) == (1800, 1000)
        assert (route["result_screenshot"]["width"], route["result_screenshot"]["height"]) == (1708, 921)
        assert route["mworks_mil_summary"]["status_code"] == 1
    assert batch["native_result_msr"] is None
