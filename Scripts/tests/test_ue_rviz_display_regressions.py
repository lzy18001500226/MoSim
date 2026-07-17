import importlib.util
import threading
import time
from pathlib import Path
from types import SimpleNamespace


def test_ros1_display_launcher_gates_real_d6_topics_and_frames() -> None:
    launcher = Path("Scripts/ui/launch_ros1_display.sh").read_text(encoding="utf-8")
    runtime = Path("Scripts/ui/run_orchestrated_runtime.sh").read_text(encoding="utf-8")
    pointcloud_config = Path("Config/rviz/sunray_ros1_fastlio_accumulated_map_review.rviz").read_text(
        encoding="utf-8"
    )
    grid_config = Path("Config/rviz/sunray_ros1_fastlio_grid3d_review.rviz").read_text(encoding="utf-8")

    assert 'export REVIEW_START_FASTLIO="true"' in runtime
    assert 'export REVIEW_START_OCCUPANCY_NODE="true"' in runtime
    assert "/mosim/fastlio/laser_map_obstacles" in launcher
    assert "/mosim/fastlio/occupancy_object_review" in launcher
    assert "assert_topic_frame /mosim/fastlio/laser_map_obstacles camera_init" in launcher
    assert "assert_topic_frame /mosim/fastlio/occupancy_object_review camera_init" in launcher
    assert "sunray_ros1_ego_grid_trajectory_review.rviz" not in launcher
    assert "Topic: /mosim/px4ctrl/truth_path" in pointcloud_config
    assert "Topic: /mosim/px4ctrl/reference_path" in pointcloud_config
    assert "Size (m): 0.20" in grid_config
    assert "Fixed Frame: camera_init" in grid_config


def test_ue_live_bridge_has_single_sender_and_stale_source_guards() -> None:
    streamer = Path("Scripts/UE5/stream_ros1_state_to_ue_udp.py").read_text(encoding="utf-8")
    launcher = Path("Scripts/ui/launch_ros1_display.sh").read_text(encoding="utf-8")
    helper = Path("Scripts/ui/attach_orchestrated_displays.ps1").read_text(encoding="utf-8")
    receiver = Path(
        "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpReceiverComponent.cpp"
    ).read_text(encoding="utf-8")
    receiver_header = Path(
        "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksUdpReceiverComponent.h"
    ).read_text(encoding="utf-8")

    assert "class UdpPortLease" in streamer
    assert "LOCK_EX | fcntl.LOCK_NB" in streamer
    assert "latest_state_monotonic" in streamer
    assert "source_timeout_s" in streamer
    assert '"stream_id": self.args.stream_id' in streamer
    assert '"unreal_bridge", $hostAddress, $SessionId' in helper
    assert '"unreal_bridge_stop"' in helper
    assert "stop_project_ue_bridge 5005" in launcher
    assert '--source-timeout-s 0.5' in launcher
    assert '--stream-id "${owner_id}"' in launcher
    assert "StreamTakeoverTimeoutSeconds = 1.0" in receiver_header
    assert "rejected competing UDP stream" in receiver
    assert "rejected non-monotonic UDP frame" in receiver


def test_ue_live_bridge_does_not_retransmit_stale_pose() -> None:
    path = Path("Scripts/UE5/stream_ros1_state_to_ue_udp.py")
    spec = importlib.util.spec_from_file_location("mosim_ue_streamer_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    streamer = module.Ros1ToUeStreamer.__new__(module.Ros1ToUeStreamer)
    streamer.lock = threading.Lock()
    streamer.latest_state = {"position": [1.0, 2.0, 3.0]}
    streamer.latest_state_monotonic = time.monotonic() - 1.0
    streamer.args = SimpleNamespace(source_timeout_s=0.5)

    assert streamer.make_frame() is None
