from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts" / "sunray" / "run_diff_planner_single_core_fixture.sh"
PROBE = ROOT / "Scripts" / "sunray" / "probe_diff_planner_single_core_fixture.py"


def test_single_core_fixture_exercises_only_the_planner_interface() -> None:
    runner = RUNNER.read_text(encoding="utf-8")
    probe = PROBE.read_text(encoding="utf-8")

    assert "roscore -p" in runner
    assert "use_multipoint:=false" in runner
    assert "flight_type:=1" in runner
    assert "Gazebo, QGC, or UE" in runner
    assert "PointCloud2" in probe
    assert '"planner_heartbeat_missing"' in probe
    assert '"planner_trajectory_missing"' in probe
    assert '"traj_server_position_cmd_missing"' in probe
    assert "It does not prove FAST-LIO, MID360" in probe
