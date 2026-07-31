from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "Scripts/sunray/run_px4ctrl_fastlio_wind_demo_gate.sh"


def test_graphical_c99_wind_demo_reuses_the_frozen_runtime_baseline() -> None:
    source = GATE.read_text(encoding="utf-8")

    assert "PX4CTRL_CORE_PROFILE=graphical_c99" in source
    assert "PX4CTRL_EXPECTED_BUILD_BACKEND=graphical_px4ctrl_c99" in source
    assert "run_px4ctrl_fastlio_hover_gate.sh" in source
    assert "resolve_local_ros1_runtime.sh" in source
    assert 'source "${LOCAL_ROS1_WS}/devel/setup.bash"' in source
    assert "FASTLIO_FILTER_SIZE_SURF=0.5" in source
    assert "FASTLIO_FILTER_SIZE_MAP=0.5" in source


def test_graphical_c99_wind_demo_waits_for_runtime_then_records_bounded_injection() -> None:
    source = GATE.read_text(encoding="utf-8")

    assert "ros_master_not_ready_before_wind_injection" in source
    assert "apply_p9_learning_wind_wrench.py" in source
    assert 'C99_WIND_FORCE_N:-0.8' in source
    assert 'C99_WIND_DIRECTION_DEG:-35' in source
    assert 'C99_WIND_DURATION_S:-8' in source
    assert "WIND_INJECTION_EVIDENCE.json" in source
    assert "DEMO_STATUS.json" in source
    assert "do not upgrade the formal controller-performance result" in source
