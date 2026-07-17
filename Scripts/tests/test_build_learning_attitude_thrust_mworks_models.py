from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/build_learning_attitude_thrust_mworks_models.py"
SPEC = importlib.util.spec_from_file_location("p9_learning_mworks_builder", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_embedded_c_contains_frozen_learning_core_and_fallback() -> None:
    source = MODULE.embedded_c()
    assert "MOSIM_LEARNING_ARTIFACT_SHA256" in source
    assert "MosimLearningAttitudeThrustStepScalar" in source
    assert "mosim_neural_residual_step" in source
    assert "mosim_rl_gain_scheduler_step" in source
    assert "learning_enable" in source
    assert '#include "learning_control_weights.h"' not in source


def test_builder_emits_two_attitude_thrust_fixtures(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(MODULE, "ROOT", ROOT)
    result_dir = tmp_path / "p9"
    monkeypatch.setattr("sys.argv", [str(SCRIPT), "--result-dir", str(result_dir)])
    assert MODULE.main() == 0
    manifest = json.loads((result_dir / "BUILD_MANIFEST.json").read_text(encoding="utf-8"))
    assert set(manifest["fixtures"]) == {"trained_neural_residual", "rl_gain_scheduler"}
    assert len(manifest["artifact_sha256"]) == 64
    for model_name in manifest["fixtures"].values():
        text = (result_dir / "models" / f"{model_name}.mo").read_text(encoding="utf-8")
        assert "desired_collective_thrust_n" in text
        assert "normalized_thrust" in text
        assert "mass_kg" in text
        assert "hover_percentage" in text
        assert "learning_action_x" in text
        assert "fallback_active" in text
