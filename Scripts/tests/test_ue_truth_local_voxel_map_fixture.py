from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "quality" / "build_ue_truth_local_voxel_map_fixture.py"
OUTPUT = ROOT / "Results" / "gazebo_ros2" / "offline_ue_truth_local_voxel_map_fixture"
REPORT = OUTPUT / "UE_TRUTH_LOCAL_VOXEL_MAP_FIXTURE.json"


def run_builder() -> dict:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, text=True, capture_output=True)
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_fixture_builder_generates_two_scene_offline_reports() -> None:
    report = run_builder()

    assert report["schema"] == "mosim.offline_ue_truth_local_voxel_map_fixture.v1"
    assert report["ok"] is True
    assert report["status"] == "offline_ue_truth_local_voxel_fixture_ready"
    assert {scene["scene_id"] for scene in report["scenes"]} == {
        "factoryenvironmentcollect",
        "derelictcorridormegascans",
    }
    for scene in report["scenes"]:
        counts = scene["counts"]
        assert counts["frame_count"] > 0
        assert counts["frames_with_voxels"] == counts["frame_count"]
        assert counts["source_point_count_total"] > 0
        assert counts["voxel_count_min"] > 0
        assert Path(ROOT / scene["artifacts"]["fixture_frames_jsonl"]).is_file()


def test_fixture_claim_boundary_blocks_runtime_overclaim() -> None:
    report = run_builder()

    boundary = "\n".join(report["claim_boundary"])
    for required in [
        "does not start UE, MWORKS, ROS2, Gazebo",
        "does not prove PointCloud2 runtime evidence",
        "Live validation still requires Gazebo Sim plus ros_gz_bridge",
    ]:
        assert required in boundary
    assert report["coordinate_transform"].startswith("ue_world_m_z_up translated")
