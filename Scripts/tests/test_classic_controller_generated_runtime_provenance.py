from __future__ import annotations

import importlib.util
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_checker():
    path = ROOT / "Scripts/sunray/check_classic_controller_generated_runtime_provenance.py"
    spec = importlib.util.spec_from_file_location("classic_runtime_provenance", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load provenance checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_constants_and_profiles() -> None:
    checker = load_checker()
    assert checker.BACKEND == "classic_controller_attitude_thrust"
    assert checker.BINARY_SYMBOL == "MosimClassicStepScalar"
    assert checker.CONTROLLERS == {
        "pole_placement_luenberger": 1,
        "mrac": 2,
        "ndi": 3,
        "fopid": 4,
        "h2_state_feedback": 5,
    }


def test_generated_bundle_matches_frozen_runtime_ack_hash() -> None:
    checker = load_checker()
    code_dir = ROOT / "Results/control_platform/classic_controller_closeout_20260717/mworks/codegen" / checker.MODEL
    bundle_hash, hashes, missing = checker.generated_bundle(code_dir)
    assert missing == []
    assert len(hashes) == len(checker.REQUIRED_GENERATED_FILES)
    assert bundle_hash == "0f44c05a4d36ed4a2040989ff48a47b9b1033f24ced152da1c5eb38428da7772"


def test_cache_and_path_helpers() -> None:
    checker = load_checker()
    text = "MOSIM_PX4CTRL_GENERATED_BACKEND:STRING=classic_controller_attitude_thrust\n"
    assert checker.cache_value(text, "MOSIM_PX4CTRL_GENERATED_BACKEND") == checker.BACKEND
    path = checker.normalized_path(r"C:\Users\HP\Desktop\MoSim\Results\control_platform")
    if os.name == "posix" and Path("/mnt/c").is_dir():
        assert str(path).startswith("/mnt/c/Users/HP/Desktop/MoSim/Results/control_platform")
    else:
        assert "C:/Users/HP/Desktop/MoSim/Results/control_platform" in str(path).replace("\\", "/")
