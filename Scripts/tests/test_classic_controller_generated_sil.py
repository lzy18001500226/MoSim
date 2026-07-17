from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/run_classic_controller_generated_sil.py"


def load_module():
    spec = importlib.util.spec_from_file_location("classic_sil", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sil_contract_covers_all_stateful_outputs() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for token in (
        "observer_position", "reference_model_position", "adaptive_position_delta",
        "fractional_integral", "fractional_derivative", "samples_per_controller",
        '"MWORKS GenerateModelCode"', "tolerance = 1.0e-12",
    ):
        assert token in text


def test_generated_global_discovery_matches_current_archive() -> None:
    module = load_module()
    header = (
        ROOT / "Results/control_platform/classic_controller_closeout_20260717/mworks/codegen"
        / "MoSim_Classic_CFunction_Sysblock/MoSim_Classic_CFunction_Sysblock.h"
    ).read_text(encoding="utf-8")
    assert module.discover_globals(header) == ("blockGbIn", "sblockGbOut")
