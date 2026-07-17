from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/synthesize_classic_h2_state_feedback.py"


def load_module():
    spec = importlib.util.spec_from_file_location("classic_h2_synthesis", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_h2_synthesis_reproduces_frozen_stable_gains() -> None:
    report = load_module().build_report()
    assert report["status"] == "passed"
    for axis in report["axes"].values():
        assert axis["stable"] is True
        assert axis["gain_max_abs_difference"] <= report["tolerance"]
        assert axis["care_residual_max_abs"] <= report["tolerance"]


def test_h2_generalized_plant_has_disturbance_and_performance_channels() -> None:
    report = load_module().build_report()
    plant = report["axes"]["x"]["generalized_plant"]
    assert len(plant["B1"][0]) == 2
    assert len(plant["C1"]) == 3
    assert plant["D12"][-1][0] == 1.0
