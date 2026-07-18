from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts/sunray/run_final_controller_ab_matrix.sh"
INJECTOR = ROOT / "Scripts/sunray/apply_motor_efficiency_fault.py"
SUMMARIZER = ROOT / "Scripts/sunray/summarize_final_controller_ab_matrix.py"
PROFILES = ("official_pid", "gain_scheduled_pid")
SCENARIOS = (
    "hover", "step", "figure8", "spiral", "wind",
    "parameter_mismatch", "motor_efficiency_fault",
)


def write_complete_matrix(root: Path, blocked: tuple[str, str] | None = None) -> None:
    for profile in PROFILES:
        for scenario in SCENARIOS:
            run_dir = root / f"{profile}_{scenario}"
            run_dir.mkdir()
            status = "blocked" if blocked == (profile, scenario) else "passed"
            mission = {"step": "step_x", "figure8": "figure8", "spiral": "spiral"}.get(
                scenario, "takeoff_hover_land"
            )
            (run_dir / "PX4CTRL_BASIC_MISSION_METRICS.json").write_text(json.dumps({
                "status": status,
                "reason": "threshold_failed" if status == "blocked" else None,
                "mission": mission,
                "steady_hover": {"xy_rmse_m": 0.01, "z_abs_rmse_m": 0.01},
                "trajectory": {"xyz_rmse_m": 0.03},
                "all_reference_tracking": {"xyz_rmse_m": 0.02},
                "landing_disarm": {"success": True},
            }), encoding="utf-8")
            provenance = (
                "G9_GENERATED_RUNTIME_PROVENANCE.json"
                if profile == "official_pid" else "PID_GENERATED_RUNTIME_PROVENANCE.json"
            )
            (run_dir / provenance).write_text(json.dumps({
                "status": "passed", "runtime_loaded_symbol": "generated::Step",
            }), encoding="utf-8")
            if scenario == "wind":
                (run_dir / "WIND_INJECTION_EVIDENCE.json").write_text(
                    json.dumps({"status": "passed"}), encoding="utf-8"
                )
            if scenario == "motor_efficiency_fault":
                (run_dir / "MOTOR_EFFICIENCY_INJECTION_EVIDENCE.json").write_text(
                    json.dumps({"status": "passed"}), encoding="utf-8"
                )


def run_summary(root: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
    output = root / "matrix.json"
    completed = subprocess.run([
        sys.executable, str(SUMMARIZER), "--result-root", str(root),
        "--json-out", str(output), "--csv-out", str(root / "matrix.csv"),
    ], cwd=ROOT, capture_output=True, text=True)
    return completed, json.loads(output.read_text(encoding="utf-8"))


def test_runner_declares_same_two_profiles_and_seven_scenarios() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "official_pid gain_scheduled_pid" in text
    assert "hover step figure8 spiral wind parameter_mismatch motor_efficiency_fault" in text
    assert "ensure_px4ctrl_generated_backend.sh" in text
    assert "prepare_px4_ram_dataman_rcs.py" in text
    assert "PX4_RAM_DATAMAN_RCS.json" in text
    assert "--pre-takeoff-state-timeout-s 120" in text
    assert "check_g9_generated_runtime_provenance.py" in text
    assert "check_pid_attitude_thrust_generated_runtime_provenance.py" in text


def test_motor_fault_injector_never_enables_override() -> None:
    text = INJECTOR.read_text(encoding="utf-8")
    assert "message.data = [0.0, *values" in text
    assert "controller_override_observed" in text
    assert "MOTOR_EFFICIENCY_INJECTION_EVIDENCE.json" in text


def test_summary_accepts_complete_fourteen_row_matrix(tmp_path: Path) -> None:
    write_complete_matrix(tmp_path)
    completed, payload = run_summary(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert payload["execution_status"] == "passed"
    assert payload["acceptance_status"] == "passed"
    assert payload["counts"] == {"accepted": 14, "executed_blocked": 0, "not_run": 0}


def test_summary_keeps_threshold_failure_as_executed_blocked(tmp_path: Path) -> None:
    write_complete_matrix(tmp_path, blocked=("gain_scheduled_pid", "wind"))
    completed, payload = run_summary(tmp_path)
    assert completed.returncode == 0
    assert payload["execution_status"] == "passed"
    assert payload["acceptance_status"] == "blocked"
    assert payload["counts"] == {"accepted": 13, "executed_blocked": 1, "not_run": 0}
