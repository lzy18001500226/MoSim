from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts/sunray/run_p9_learning_generated_gazebo_matrix.sh"
INJECTOR = ROOT / "Scripts/sunray/apply_p9_learning_wind_wrench.py"
SUMMARIZER = ROOT / "Scripts/sunray/summarize_p9_learning_gazebo_matrix.py"


def test_matrix_runner_is_serial_and_lock_preserving() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "run_px4ctrl_basic_gate.sh" in text
    assert "ensure_p9_learning_px4ctrl_backend.sh" in text
    assert "wait \"${gate_pid}\"" in text
    assert "trained_neural_residual rl_gain_scheduler" in text
    assert "nominal wind parameter_mismatch" in text


def test_wind_injector_uses_bounded_gazebo_service() -> None:
    text = INJECTOR.read_text(encoding="utf-8")
    assert "ApplyBodyWrench" in text
    assert "minimum-altitude-m" in text
    assert "airborne-timeout-s" in text
    assert "WIND_INJECTION_EVIDENCE.json" in text


def test_summarizer_requires_all_nine_runtime_rows(tmp_path: Path) -> None:
    for profile in ("cascade_pid", "trained_neural_residual", "rl_gain_scheduler"):
        for condition in ("nominal", "wind", "parameter_mismatch"):
            run_dir = tmp_path / f"{profile}_{condition}"
            run_dir.mkdir()
            (run_dir / "PX4CTRL_BASIC_MISSION_METRICS.json").write_text(json.dumps({
                "status": "passed",
                "steady_hover": {"xy_rmse_m": 0.01, "z_abs_rmse_m": 0.01},
                "all_reference_tracking": {"xyz_rmse_m": 0.02},
                "landing_disarm": {"success": True},
            }), encoding="utf-8")
            if profile != "cascade_pid":
                (run_dir / "LEARNING_GENERATED_RUNTIME_PROVENANCE.json").write_text(json.dumps({
                    "status": "passed", "runtime_loaded_symbol": "model::Step",
                }), encoding="utf-8")
            if condition == "wind":
                (run_dir / "WIND_INJECTION_EVIDENCE.json").write_text(
                    json.dumps({"status": "passed"}), encoding="utf-8"
                )
    output = tmp_path / "matrix.json"
    completed = subprocess.run([
        sys.executable, str(SUMMARIZER), "--result-root", str(tmp_path),
        "--json-out", str(output), "--csv-out", str(tmp_path / "matrix.csv"),
    ], cwd=ROOT, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["status"] == "passed"
    assert payload["execution_status"] == "passed"
    assert payload["acceptance_status"] == "passed"
    assert len(payload["rows"]) == 9


def test_summarizer_does_not_accept_completed_but_blocked_missions(tmp_path: Path) -> None:
    for profile in ("cascade_pid", "trained_neural_residual", "rl_gain_scheduler"):
        for condition in ("nominal", "wind", "parameter_mismatch"):
            run_dir = tmp_path / f"{profile}_{condition}"
            run_dir.mkdir()
            mission_status = "blocked" if profile != "cascade_pid" else "passed"
            (run_dir / "PX4CTRL_BASIC_MISSION_METRICS.json").write_text(json.dumps({
                "status": mission_status,
                "reason": "takeoff_not_reached_altitude" if mission_status == "blocked" else None,
                "all_reference_tracking": {"xyz_rmse_m": 0.2},
                "landing_disarm": {"success": True},
            }), encoding="utf-8")
            if profile != "cascade_pid":
                (run_dir / "LEARNING_GENERATED_RUNTIME_PROVENANCE.json").write_text(json.dumps({
                    "status": "passed", "runtime_loaded_symbol": "model::Step",
                }), encoding="utf-8")
            if condition == "wind":
                (run_dir / "WIND_INJECTION_EVIDENCE.json").write_text(
                    json.dumps({"status": "passed"}), encoding="utf-8"
                )
    output = tmp_path / "matrix.json"
    completed = subprocess.run([
        sys.executable, str(SUMMARIZER), "--result-root", str(tmp_path),
        "--json-out", str(output), "--csv-out", str(tmp_path / "matrix.csv"),
    ], cwd=ROOT, capture_output=True, text=True)
    assert completed.returncode == 1
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["execution_status"] == "passed"
    assert payload["acceptance_status"] == "blocked"
    assert len(payload["acceptance_errors"]) == 6
