from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRAINER = ROOT / "Scripts/control_platform/train_learning_controllers.py"
GATE = ROOT / "Scripts/control_platform/run_learning_control_gate.py"
ATTITUDE_THRUST_GATE = ROOT / "Scripts/control_platform/run_learning_attitude_thrust_gate.py"
CORE_H = ROOT / "Scripts/control_platform/learning_control_core.h"
CORE_C = ROOT / "Scripts/control_platform/learning_control_core.c"
WEIGHTS_H = ROOT / "Scripts/control_platform/learning_control_weights.h"
ARTIFACT = ROOT / "Config/control_platform/learning_control_artifact.json"


def test_learning_control_surface_is_fixed_size_and_fail_safe() -> None:
    header = CORE_H.read_text(encoding="utf-8")
    source = CORE_C.read_text(encoding="utf-8")
    assert "MOSIM_LEARNING_OBSERVATION_SIZE 12" in header
    assert "MOSIM_LEARNING_ACTION_SIZE 3" in header
    assert "mosim_neural_residual_step" in header
    assert "mosim_rl_gain_scheduler_step" in header
    assert "MOSIM_LEARNING_STATUS_FALLBACK" in header
    assert "isfinite" in source
    assert "mosim_learning_zero_output" in source
    assert "learning_control_weights.h" in source


def test_frozen_artifact_is_trained_and_hashed() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["schema"] == "mosim.learning_control_artifact.v1"
    assert artifact["status"] == "trained"
    assert artifact["neural_residual"]["trained"] is True
    assert artifact["rl_gain_scheduler"]["trained"] is True
    assert artifact["neural_residual"]["training_algorithm"] == "sklearn_mlp_regressor"
    assert artifact["rl_gain_scheduler"]["training_algorithm"] == "stable_baselines3_ppo"
    assert len(artifact["artifact_sha256"]) == 64
    assert len(artifact["dataset"]["manifest_sha256"]) == 64
    assert artifact["dataset"]["train_seed"] != artifact["dataset"]["evaluation_seed"]
    assert WEIGHTS_H.exists()


def test_learning_control_offline_gate(tmp_path: Path) -> None:
    subprocess.run(
        [sys.executable, str(GATE), "--result-dir", str(tmp_path)],
        cwd=ROOT,
        check=True,
    )
    report = json.loads((tmp_path / "P9_LEARNING_CONTROL_OFFLINE_GATE.json").read_text(encoding="utf-8"))
    assert report["status"] == "passed"
    assert report["compiled_c_equivalence"]["status"] == "passed"
    assert report["compiled_c_equivalence"]["max_abs_error"] <= 1.0e-12
    assert report["fallback_gate"]["status"] == "passed"
    assert report["neural_residual_ab"]["rmse_improvement_fraction"] > 0.05
    assert report["rl_gain_scheduler_ab"]["rmse_improvement_fraction"] > 0.02


def test_trainer_declares_reproducible_engines() -> None:
    text = TRAINER.read_text(encoding="utf-8")
    assert "MLPRegressor" in text
    assert "stable_baselines3" in text
    assert "PPO" in text
    assert "TRAIN_SEED = 20260717" in text
    assert "EVALUATION_SEED = 20260718" in text


def test_learning_attitude_thrust_gate(tmp_path: Path) -> None:
    completed = subprocess.run(
        [sys.executable, str(ATTITUDE_THRUST_GATE), "--result-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads((tmp_path / "P9_LEARNING_ATTITUDE_THRUST_GATE.json").read_text(encoding="utf-8"))
    assert report["status"] == "passed"
    assert report["cases"]["neural"]["fallback_active"] == 0
    assert report["cases"]["rl"]["fallback_active"] == 0
    assert report["cases"]["learning_disabled"]["fallback_active"] == 1
    assert report["cases"]["nan_fail_closed"]["result"] == -1
