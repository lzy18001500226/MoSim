import importlib.util
import threading
import time
from pathlib import Path
from types import SimpleNamespace


def test_ros1_display_launcher_gates_real_d6_topics_and_frames() -> None:
    launcher = Path("Scripts/ui/launch_ros1_display.sh").read_text(encoding="utf-8")
    fastlio_runtime = Path("Scripts/sunray/run_px4ctrl_fastlio_hover_gate.sh").read_text(encoding="utf-8")
    pointcloud_config = Path("Config/rviz/sunray_ros1_fastlio_accumulated_map_review.rviz").read_text(
        encoding="utf-8"
    )
    grid_config = Path("Config/rviz/sunray_ros1_fastlio_grid3d_review.rviz").read_text(encoding="utf-8")

    assert 'export REVIEW_START_FASTLIO=true' in fastlio_runtime
    assert "/mosim/fastlio/laser_map_obstacles" in launcher
    assert "/mosim/fastlio/occupancy_object_review" in launcher
    assert "assert_topic_frame /mosim/fastlio/laser_map_obstacles camera_init" in launcher
    assert "assert_topic_frame /mosim/fastlio/occupancy_object_review camera_init" in launcher
    assert "sunray_ros1_ego_grid_trajectory_review.rviz" not in launcher
    assert "Topic: /mosim/px4ctrl/truth_path" in pointcloud_config
    assert "Topic: /mosim/px4ctrl/reference_path" in pointcloud_config
    assert "Size (m): 0.20" in grid_config
    assert "Fixed Frame: camera_init" in grid_config
    assert 'existing.get("status") == "ready" and status != "ready"' in launcher
    assert 'late_path = path + ".latest_attempt.json"' in launcher


def test_ue_live_bridge_has_single_sender_and_stale_source_guards() -> None:
    streamer = Path("Scripts/UE5/stream_ros1_state_to_ue_udp.py").read_text(encoding="utf-8")
    launcher = Path("Scripts/ui/launch_ros1_display.sh").read_text(encoding="utf-8")
    unreal_launcher = Path("Scripts/UE5/open_unreal_renderer.sh").read_text(encoding="utf-8")
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
    assert "mosim.gazebo_ue_sender_metrics.v1" in streamer
    assert "estimated_ipv4_udp_wire_bytes_per_s" in streamer
    assert '"run_id": self.args.run_id' in streamer
    assert "Sender-side measurement only" in streamer
    assert '"unreal_bridge", $hostAddress, $SessionId' in helper
    assert '"unreal_bridge_stop"' in helper
    assert "stop_project_ue_bridge 5005" in launcher
    assert launcher.index('unreal_bridge_stop)') < launcher.index('stop_project_ue_bridge "" "${owner_id}"')
    assert "require_ros_master()" in launcher
    assert launcher.index("case \"${display_kind}\" in") < launcher.index("require_ros_master\n", launcher.index("case \"${display_kind}\" in"))
    unreal_bridge_case = launcher.split("  unreal_bridge)", 1)[1].split("    ;;", 1)[0]
    assert "require_ros_master" not in unreal_bridge_case
    assert '--source-timeout-s 0.5' in launcher
    assert '--stream-id "${owner_id}"' in launcher
    assert '"/Game/Maps/Demonstration?game=/Script/MoSimSceneLibrary.MoSimSceneLibraryGameMode"' in unreal_launcher
    assert "StreamTakeoverTimeoutSeconds = 1.0" in receiver_header
    assert "rejected competing UDP stream" in receiver
    assert "rejected non-monotonic UDP frame" in receiver


def test_unreal_receiver_and_frame_metrics_are_run_scoped() -> None:
    receiver = Path("UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpReceiverComponent.cpp").read_text(encoding="utf-8")
    game_mode = Path("UE5/MoSimSceneLibrary/Source/MoSimSceneLibrary/MoSimSceneLibraryGameMode.cpp").read_text(encoding="utf-8")
    launcher = Path("Scripts/ui/attach_orchestrated_displays.ps1").read_text(encoding="utf-8-sig")
    assert "mosim.gazebo_ue_receiver_metrics.v1" in receiver
    assert "receiver_drop_rate" in receiver
    assert "mosim.unreal_frame_timing.v1" in game_mode
    assert "ue_fps" in game_mode
    assert "-MoSimObservabilityRunId=$RunId" in launcher


def test_fuel_ue_smoothing_uses_arrival_timing_without_changing_runtime_truth() -> None:
    fuel_launcher = Path("Scripts/sunray/start_factory_fuel_single_exploration_review.ps1").read_text(
        encoding="utf-8"
    )
    playback_header = Path(
        "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksPlaybackComponent.h"
    ).read_text(encoding="utf-8")
    playback = Path(
        "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksPlaybackComponent.cpp"
    ).read_text(encoding="utf-8")
    gate = Path("Scripts/sunray/run_px4ctrl_ego_single_gate.sh").read_text(encoding="utf-8")

    assert '"-MoSimPlaybackInterpolate"' in fuel_launcher
    assert '"-MoSimPlaybackUseArrivalTiming"' in fuel_launcher
    assert '"-MoSimPlaybackNominalRateHz=$UnrealPlaybackNominalRateHz"' in fuel_launcher
    assert "bUseArrivalTimeForInterpolation" in playback_header
    assert "FMath::Max(NominalDurationSeconds, ArrivalDurationSeconds)" in playback
    assert "UE display smoothing only; Gazebo/MAVROS trajectories remain authoritative." in fuel_launcher
    assert '--metrics-output "${RESULT_DIR}/observability/gazebo_ue_sender.json"' in gate


def test_fuel_launcher_uses_nonoverflow_fastlio_localization_voxels() -> None:
    fuel_launcher = Path("Scripts/sunray/start_factory_fuel_single_exploration_review.ps1").read_text(
        encoding="utf-8"
    )

    assert "[double]$FastlioFilterSizeSurfM = 0.5" in fuel_launcher
    assert "[double]$FastlioFilterSizeMapM = 0.5" in fuel_launcher
    assert '"FASTLIO_FILTER_SIZE_SURF=$FastlioFilterSizeSurfM"' in fuel_launcher
    assert '"FASTLIO_FILTER_SIZE_MAP=$FastlioFilterSizeMapM"' in fuel_launcher


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


def test_ue_rotors_remain_stopped_while_mavros_is_disarmed() -> None:
    path = Path("Scripts/UE5/stream_ros1_state_to_ue_udp.py")
    spec = importlib.util.spec_from_file_location("mosim_ue_streamer_motor_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    streamer = module.Ros1ToUeStreamer.__new__(module.Ros1ToUeStreamer)
    streamer.lock = threading.Lock()
    streamer.latest_motors = [900.0, 900.0, 900.0, 900.0]
    streamer.latest_motors_monotonic = time.monotonic()
    streamer.armed = False
    streamer.args = SimpleNamespace(motor_timeout_s=0.5, armed_visual_motor_command=0.65)

    assert streamer.motor_visual_state() == ([0.0, 0.0, 0.0, 0.0], "mavros_disarmed")


def test_ue_default_uav_pose_matches_gazebo_ground_spawn_height() -> None:
    game_mode = Path(
        "UE5/MoSimSceneLibrary/Source/MoSimSceneLibrary/MoSimSceneLibraryGameMode.h"
    ).read_text(encoding="utf-8")
    gazebo_launch = Path("Scripts/sunray/factory_l2_sunray_px4_gazebo.launch").read_text(
        encoding="utf-8"
    )

    assert "PlaybackActorLocation = FVector(0.0, 0.0, 20.0)" in game_mode
    assert '<arg name="uav1_init_z" default="0.2"/>' in gazebo_launch


def test_qgc_does_not_embed_or_control_the_unreal_window() -> None:
    qml = Path("apps/flight_console/mosim/custom/src/FlyViewCustomLayer.qml").read_text(encoding="utf-8")
    bridge = Path("apps/flight_console/mosim/custom/src/MoSimOrchestratorBridge.cc").read_text(
        encoding="utf-8"
    )

    assert "WindowContainer" not in qml
    assert "mosimOrchestrator.unrealWindow" not in qml
    assert "setUnrealPresentationSuppressed" not in qml
    assert "cycleUnrealView" not in qml
    assert "zoomUnrealIn" not in qml
    assert "zoomUnrealOut" not in qml
    assert "_autoAttachUnrealAfterStart" not in bridge
    assert "QTimer::singleShot(0, this, &MoSimOrchestratorBridge::refreshUnrealEmbedding)" not in bridge


def test_standalone_ue_releases_pointer_capture_by_default() -> None:
    input_config = Path("UE5/MoSimSceneLibrary/Config/DefaultInput.ini").read_text(encoding="utf-8")
    camera_source = Path(
        "UE5/MoSimSceneLibrary/Source/MoSimSceneLibrary/MworksReviewCameraPawn.cpp"
    ).read_text(encoding="utf-8")
    camera_header = Path(
        "UE5/MoSimSceneLibrary/Source/MoSimSceneLibrary/MworksReviewCameraPawn.h"
    ).read_text(encoding="utf-8")
    launcher = Path("Scripts/ui/attach_orchestrated_displays.ps1").read_text(encoding="utf-8-sig")

    assert "bCaptureMouseOnLaunch=False" in input_config
    assert "DefaultViewportMouseCaptureMode=NoCapture" in input_config
    assert "DefaultViewportMouseLockMode=DoNotLock" in input_config
    assert 'ActionName="MworksReviewReleasePointer"' in input_config and "Key=Escape" in input_config
    assert "MworksReviewReleasePointer" in camera_source
    assert "ReleaseReviewPointer" in camera_header
    assert "PlayerController->bShowMouseCursor = true;" in camera_source
    assert "FSlateApplication::Get().ReleaseAllPointerCapture();" in camera_source
    assert "InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);" in camera_source
    assert "FInputModeGameOnly InputMode;" not in camera_source
    assert "MoSimEmbeddedViewport" not in camera_source
    assert "WindowsHWrapper.h" not in camera_source
    assert "-MoSimEmbeddedViewport" not in launcher


def test_basic_runner_guards_ros1_mavlink_startup_from_uxrce_failure() -> None:
    runner = Path("Scripts/sunray/run_px4ctrl_basic_gate.sh").read_text(encoding="utf-8")

    assert 'PX4_ROS1_GUARD_UXRCE_DDS="${PX4_ROS1_GUARD_UXRCE_DDS:-true}"' in runner
    assert "prepare_px4_ros1_runtime_overlay()" in runner
    assert "continuing for MoSim ROS1/MAVROS gate" in runner
    assert 'PX4_GCS_REMOTE_HOST="${PX4_GCS_REMOTE_HOST:-auto}"' in runner
    assert 'PX4_GCS_REMOTE_PORT="${PX4_GCS_REMOTE_PORT:-14550}"' in runner
    assert "ip route show default" in runner
    assert 'new = f"{old} -t {host} -o {port}"' in runner
    assert '${PX4_ROS1_OVERLAY_PKG:+${PX4_ROS1_OVERLAY_PKG}:}${SUNRAY_PX4_DIR}' in runner
    assert runner.index("prepare_px4_ros1_runtime_overlay\nsource_env") < runner.index(
        'roslaunch "${SUNRAY_GAZEBO_LAUNCH_FILE}"'
    )


def test_ground_standby_readiness_does_not_require_a_controller_or_ftc_plugin() -> None:
    runtime = Path("Scripts/ui/run_orchestrated_runtime.sh").read_text(encoding="utf-8")
    runner = Path("Scripts/sunray/run_px4ctrl_basic_gate.sh").read_text(encoding="utf-8")
    sidecar = Path("Scripts/ui/runtime_sidecar.py").read_text(encoding="utf-8")

    standby = runtime.split("run_ground_standby() {", 1)[1].split(
        "start_mworks_live_rt1() {", 1
    )[0]
    assert 'operator_map_catalog.json' in standby
    assert 'PX4CTRL_SET_EKF_GLOBAL_ORIGIN="true"' in standby
    assert 'PX4CTRL_START_CONTROLLER="false"' in standby
    assert 'ORCHESTRATOR_REQUIRE_CONTROLLER_COMMAND="false"' in standby
    assert 'ORCHESTRATOR_REQUIRE_ACTUATOR_TELEMETRY="false"' in standby
    assert '"${PX4_CLIENT_BIN_DIR}/px4-commander" set_ekf_origin' in runner
    assert "pre_flight_checks_pass: True" in runner
    assert "global_position_invalid: False" in runner
    assert "home_position_invalid: False" in runner
    assert "--skip-controller-command-readiness" in sidecar


def test_orchestrated_runtime_term_exits_before_exit_cleanup() -> None:
    runtime = Path("Scripts/ui/run_orchestrated_runtime.sh").read_text(encoding="utf-8")
    runner = Path("Scripts/sunray/run_px4ctrl_basic_gate.sh").read_text(encoding="utf-8")
    stop_helper = Path("Scripts/ui/stop_orchestrated_runtime.sh").read_text(encoding="utf-8")

    assert "trap cleanup EXIT" in runtime
    assert "trap 'exit 143' TERM" in runtime
    assert "trap 'exit 130' INT" in runtime
    assert "trap cleanup EXIT TERM INT" not in runtime
    assert "trap cleanup EXIT" in runner
    assert "trap 'exit 143' TERM" in runner
    assert "trap 'exit 130' INT" in runner
    assert 'PGID="$(ps -o pgid= -p "${PID}"' in stop_helper
    assert 'kill -TERM -- "-${PGID}"' in stop_helper
