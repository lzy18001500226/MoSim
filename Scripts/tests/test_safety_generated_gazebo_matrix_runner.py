from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts/sunray/run_safety_generated_gazebo_matrix.sh"


def test_matrix_runner_is_bounded_and_uses_fail_closed_checker() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    for mode in (
        "safety_filter", "cbf", "reference_governor", "geofence",
        "emergency_stop", "return_and_land", "failsafe_state_machine",
    ):
        assert mode in text
    assert "P6_TOTAL_TIMEOUT_S:-55" in text
    assert "check_safety_generated_runtime_provenance.py" in text
    assert "--require-runtime-ack" in text
    assert "matrix_status.tsv" in text
