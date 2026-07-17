from __future__ import annotations

import importlib.util
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_checker():
    path = ROOT / "Scripts/sunray/check_wave_a_generated_runtime_provenance.py"
    spec = importlib.util.spec_from_file_location("wave_a_runtime_provenance", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load provenance checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_constants_and_profiles() -> None:
    checker = load_checker()
    assert checker.BACKEND == "wave_a_attitude_thrust"
    assert checker.BINARY_SYMBOL == "MosimWaveAStepScalar"
    assert checker.CONTROLLERS == {
        "lqr_baseline": (1, "lqr"),
        "lqi_baseline": (2, "lqi"),
        "so3_attitude": (3, "so3"),
        "backstepping_baseline": (4, "backstepping"),
    }
    assert "px4-startup-manifest" in (ROOT / "Scripts/sunray/check_wave_a_generated_runtime_provenance.py").read_text(encoding="utf-8")


def test_generated_bundle_matches_frozen_runtime_ack_hash() -> None:
    checker = load_checker()
    code_dir = (
        ROOT
        / "Results/control_platform/g5_mworks_closeout_20260716/wave_a/codegen"
        / checker.MODEL
    )
    bundle_hash, hashes, missing = checker.generated_bundle(code_dir)
    assert missing == []
    assert len(hashes) == len(checker.REQUIRED_GENERATED_FILES)
    assert bundle_hash == "ec7dc5730b02bb4701c9f30ef78177b851a2ee8bc080575d8aedb5239fc492b7"


def test_cache_and_path_helpers() -> None:
    checker = load_checker()
    text = "MOSIM_PX4CTRL_GENERATED_BACKEND:STRING=wave_a_attitude_thrust\n"
    assert checker.cache_value(text, "MOSIM_PX4CTRL_GENERATED_BACKEND") == checker.BACKEND
    path = checker.normalized_path(r"C:\Users\HP\Desktop\MoSim\Results\control_platform")
    if os.name == "posix" and Path("/mnt/c").is_dir():
        assert str(path).startswith("/mnt/c/Users/HP/Desktop/MoSim/Results/control_platform")
    else:
        assert "C:/Users/HP/Desktop/MoSim/Results/control_platform" in str(path).replace("\\", "/")
