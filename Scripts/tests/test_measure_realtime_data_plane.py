import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MEASUREMENT = ROOT / "Scripts" / "sunray" / "measure_realtime_data_plane.py"


def load_module():
    spec = importlib.util.spec_from_file_location("measure_realtime_data_plane", MEASUREMENT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_below_threshold_clock_rtf_blocks_overall_measurement() -> None:
    module = load_module()

    assert module.measurement_status(True, True, 0.318, 0.95) == "blocked"


def test_retained_data_plane_and_threshold_rtf_passes_measurement() -> None:
    module = load_module()

    assert module.measurement_status(True, True, 0.95, 0.95) == "passed"
