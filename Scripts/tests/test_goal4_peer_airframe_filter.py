from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Scripts" / "sunray" / "peer_airframe_filter.py"
RUNNER_PATH = ROOT / "Scripts" / "sunray" / "run_px4ctrl_ego_swarm_gate.sh"
POINTCLOUD_NODE_PATH = ROOT / "Scripts" / "sunray" / "goal4_pointcloud_to_world_node.py"


def load_module():
    spec = importlib.util.spec_from_file_location("peer_airframe_filter", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_peer_filter_requires_fresh_peer_odom_before_removing_points() -> None:
    module = load_module()
    samples = {
        "/uav2/mavros/local_position/odom": module.PeerOdomSample(
            "/uav2/mavros/local_position/odom", (2.0, 3.0, 1.0), 10.02
        ),
        "/uav3/mavros/local_position/odom": module.PeerOdomSample(
            "/uav3/mavros/local_position/odom", (4.0, 5.0, 1.0), 8.0
        ),
    }

    centers, stale = module.select_fresh_peer_filter_centers(
        samples,
        ["/uav2/mavros/local_position/odom", "/uav3/mavros/local_position/odom"],
        cloud_stamp_s=10.0,
        max_age_s=0.10,
    )

    assert [center.topic for center in centers] == ["/uav2/mavros/local_position/odom"]
    assert stale == ["/uav3/mavros/local_position/odom"]
    assert module.match_peer_airframe((2.2, 3.1, 1.1), centers, 0.45, -0.30, 0.30) == \
        "/uav2/mavros/local_position/odom"
    assert module.match_peer_airframe((2.2, 3.1, 1.5), centers, 0.45, -0.30, 0.30) is None


def test_swarm_runner_wires_peer_filter_only_into_live_world_cloud_transform() -> None:
    runner = RUNNER_PATH.read_text(encoding="utf-8")
    node = POINTCLOUD_NODE_PATH.read_text(encoding="utf-8")

    assert "SWARM_POINTCLOUD_PEER_FILTER_RADIUS_XY_M" in runner
    assert "_peer_odom_topics:=" in runner
    assert "_peer_filter_radius_xy_m:=" in runner
    assert "_diagnostics_path:=" in runner
    assert "select_fresh_peer_filter_centers" in node
    assert "match_peer_airframe" in node
