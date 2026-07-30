from pathlib import Path


def test_operator_live_gate_preserves_the_frozen_fastlio_baseline_and_starts_read_only_displays() -> None:
    gate = Path("Scripts/sunray/run_px4ctrl_fastlio_operator_live_gate.sh").read_text(encoding="utf-8")
    mission = Path("Scripts/sunray/px4ctrl_basic_mission_node.py").read_text(encoding="utf-8")

    assert "run_px4ctrl_fastlio_hover_gate.sh" in gate
    assert "runtime_sidecar.py" in gate
    assert "--read-only" in gate
    assert "prepare_factory_live_operator_map.py" in gate
    assert "stream_ros1_state_to_ue_udp.py" in gate
    assert "/uav1/sunray/gazebo_pose" in gate
    assert "/mosim/px4ctrl/reference_path" in gate
    assert "--finalize-active" in gate
    assert 'FASTLIO_FILTER_SIZE_SURF="${FASTLIO_FILTER_SIZE_SURF:-0.5}"' in gate
    assert 'FASTLIO_FILTER_SIZE_MAP="${FASTLIO_FILTER_SIZE_MAP:-0.5}"' in gate
    assert 'REVIEW_START_OCCUPANCY_NODE="${REVIEW_START_OCCUPANCY_NODE:-true}"' in gate
    assert "MID360" not in gate
    assert "SUNRAY_GPS_SENSOR_MODE=" not in gate

    assert "self.publish_reference_path()\n        self.phase = \"takeoff\"" in mission
    assert "def observed_truth_takeoff_rise_m" in mission
    assert "physical_takeoff_observed" in mission
    assert "--operational-min-takeoff-rise-m" in mission


def test_independent_unreal_review_defaults_to_following_the_live_playback_actor() -> None:
    launcher = Path("Scripts/UE5/open_unreal_renderer.sh").read_text(encoding="utf-8")

    assert "-MoSimFollowPlaybackCamera" in launcher
    assert "-MoSimPlaybackBaseUdpPort=5005" in launcher
    assert "-MoSimNoReviewCollision" in launcher
