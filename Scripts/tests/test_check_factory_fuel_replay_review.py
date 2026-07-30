from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "sunray" / "check_factory_fuel_replay_review.py"
    spec = importlib.util.spec_from_file_location("check_factory_fuel_replay_review", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def build_valid_bundle(run_dir: Path) -> None:
    run_id = "p4-fixture"
    write_json(
        run_dir / "P4_REPLAY_BUNDLE_STATUS.json",
        {
            "status": "prepared",
            "run_id": run_id,
            "display_pose_source": "/uav1/sunray/gazebo_pose",
            "display_state_kind": "gazebo_world_truth",
        },
    )
    write_json(run_dir / "RUN_MANIFEST.json", {"run_id": run_id})
    write_json(run_dir / "OPERATOR_MAP_COORDINATE_EVIDENCE.json", {"source_frame_id": "world", "target_frame_id": "mworks_world"})
    write_json(
        run_dir / "rviz_replay" / "RVIZ_REPLAY_STATUS.json",
        {"state": "completed", "bag_exit_code": 0, "pointcloud_probe_exit_code": 0, "occupancy_probe_exit_code": 0, "truth_path_probe_exit_code": 0},
    )
    write_json(
        run_dir / "OPERATOR_MAP_REPLAY_MANIFEST.json",
        {"source": {"odom_topics": {"uav1": "/uav1/sunray/gazebo_pose"}}},
    )
    write_json(run_dir / "OPERATOR_MAP_REPLAY_STATUS.json", {"state": "completed", "run_id": run_id, "sequence": 5})
    write_json(run_dir / "ue_render" / "UE_RENDER_STREAM_VALIDATION.json", {"status": "passed"})
    write_json(
        run_dir / "ue_render" / "ue_receiver_metrics.json",
        {"run_id": run_id, "receive_rate_hz": 20.0, "sequence_gap_count": 0},
    )
    write_json(run_dir / "ue_render" / "ue_frame_metrics.json", {"ue_fps": 60.0})


def test_factory_fuel_display_replay_binds_all_consumers_to_truth() -> None:
    module = load_module()
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as temporary_directory:
        run_dir = Path(temporary_directory) / "p4"
        build_valid_bundle(run_dir)
        report = module.evaluate(run_dir)

    assert report["status"] == "completed_with_rviz_window_capture_limitation"
    assert report["display_data_status"] == "passed"
    assert report["issues"] == []


def test_factory_fuel_display_replay_rejects_mavros_odom_as_truth() -> None:
    module = load_module()
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as temporary_directory:
        run_dir = Path(temporary_directory) / "p4"
        build_valid_bundle(run_dir)
        bundle_path = run_dir / "P4_REPLAY_BUNDLE_STATUS.json"
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        bundle["display_pose_source"] = "/uav1/mavros/local_position/odom"
        write_json(bundle_path, bundle)
        report = module.evaluate(run_dir)

    assert report["status"] == "blocked"
    assert any(issue["code"] == "p4_replay_display_truth_topic_wrong" for issue in report["issues"])
