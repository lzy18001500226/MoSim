from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MISSION_NODE = ROOT / "Scripts" / "sunray" / "px4ctrl_ego_single_mission_node.py"
RUNNER = ROOT / "Scripts" / "sunray" / "run_px4ctrl_ego_single_gate.sh"


def test_data_plane_observer_mode_is_opt_in_and_wired_to_the_mission_node() -> None:
    node = MISSION_NODE.read_text(encoding="utf-8")
    runner = RUNNER.read_text(encoding="utf-8")

    assert 'choices=["continuous", "startup_only"]' in node
    assert 'default="continuous"' in node
    assert "def data_plane_observation_ready" in node
    assert "def maybe_release_data_plane_observers" in node
    assert 'self.args.data_plane_observation_mode != "startup_only"' in node
    assert 'GOAL4_DATA_PLANE_OBSERVATION_MODE="${GOAL4_DATA_PLANE_OBSERVATION_MODE:-continuous}"' in runner
    assert '--data-plane-observation-mode "${GOAL4_DATA_PLANE_OBSERVATION_MODE}"' in runner
