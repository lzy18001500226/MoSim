#!/usr/bin/env python3

import threading
import unittest
from collections import deque
from types import SimpleNamespace
from unittest.mock import Mock

from nav_msgs.msg import Odometry
from sensor_msgs import point_cloud2
from std_msgs.msg import Header

from fastlio_odom_alignment_adapter import FastlioOdomAlignmentAdapter
from fastlio_frame_transform import Pose3


def make_odom(stamp_s: float) -> Odometry:
    msg = Odometry()
    msg.header.stamp.secs = int(stamp_s)
    msg.header.stamp.nsecs = int(round((stamp_s - int(stamp_s)) * 1e9))
    return msg


class FastlioOdomAlignmentConcurrencyTest(unittest.TestCase):
    def test_local_history_snapshot_is_stable_during_callbacks(self):
        adapter = FastlioOdomAlignmentAdapter.__new__(FastlioOdomAlignmentAdapter)
        adapter.local_odom = None
        adapter.local_odom_history = deque(maxlen=500)
        adapter.local_odom_history_lock = threading.Lock()
        adapter.local_base0 = object()

        writer_done = threading.Event()

        def write_local_odom() -> None:
            for index in range(20000):
                adapter.on_local_odom(make_odom(index / 100.0))
            writer_done.set()

        writer = threading.Thread(target=write_local_odom)
        writer.start()
        snapshots = 0
        while not writer_done.is_set():
            latest, history = adapter.local_odom_snapshot()
            if latest is not None:
                self.assertGreater(len(history), 0)
                min(history, key=lambda msg: abs(msg.header.stamp.to_sec() - 100.0))
                snapshots += 1
        writer.join()

        self.assertGreater(snapshots, 0)


class FastlioCloudVerticalAlignmentTest(unittest.TestCase):
    @staticmethod
    def make_adapter(z_source: str) -> FastlioOdomAlignmentAdapter:
        adapter = FastlioOdomAlignmentAdapter.__new__(FastlioOdomAlignmentAdapter)
        adapter.args = SimpleNamespace(z_source=z_source, input_pose_frame="base")
        adapter.local_from_fast = Pose3((0.0, 0.0, 0.1), (0.0, 0.0, 0.0, 1.0))
        adapter.mount_pose = Pose3((0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0))
        adapter.fastlio_odom = make_odom(10.0)
        adapter.fastlio_odom.pose.pose.position.z = 0.5
        adapter.truth_odom = make_odom(10.0)
        adapter.truth_odom.pose.pose.position.z = 1.2
        adapter.truth_base0_z = 0.2
        adapter.local_base0 = Pose3((0.0, 0.0, 0.2), (0.0, 0.0, 0.0, 1.0))
        return adapter

    def test_truth_z_correction_keeps_cloud_and_planner_odom_consistent(self):
        adapter = self.make_adapter("truth")

        self.assertAlmostEqual(adapter.output_z(0.6), 1.2)
        self.assertAlmostEqual(adapter.current_cloud_z_correction(), 0.6)

    def test_fastlio_z_keeps_rigid_cloud_transform(self):
        adapter = self.make_adapter("fastlio")

        self.assertAlmostEqual(adapter.output_z(0.6), 0.6)
        self.assertAlmostEqual(adapter.current_cloud_z_correction(), 0.0)


class FastlioCloudSelfFilterTest(unittest.TestCase):
    @staticmethod
    def make_adapter(radius: float = 0.35) -> FastlioOdomAlignmentAdapter:
        adapter = FastlioOdomAlignmentAdapter.__new__(FastlioOdomAlignmentAdapter)
        adapter.args = SimpleNamespace(
            cloud_self_filter_radius_xy_m=radius,
            cloud_self_filter_z_min_m=-0.30,
            cloud_self_filter_z_max_m=0.30,
        )
        return adapter

    def test_filters_point_inside_airframe_cylinder(self):
        adapter = self.make_adapter()
        self.assertTrue(adapter.point_is_inside_self_filter((1.20, 2.10, 1.15), (1.0, 2.0, 1.0)))

    def test_keeps_point_outside_xy_radius(self):
        adapter = self.make_adapter()
        self.assertFalse(adapter.point_is_inside_self_filter((1.40, 2.0, 1.0), (1.0, 2.0, 1.0)))

    def test_keeps_point_outside_vertical_window(self):
        adapter = self.make_adapter()
        self.assertFalse(adapter.point_is_inside_self_filter((1.0, 2.0, 1.31), (1.0, 2.0, 1.0)))

    def test_zero_radius_disables_filter(self):
        adapter = self.make_adapter(radius=0.0)
        self.assertFalse(adapter.point_is_inside_self_filter((1.0, 2.0, 1.0), (1.0, 2.0, 1.0)))


class FastlioCloudPeerFilterTest(unittest.TestCase):
    @staticmethod
    def make_adapter() -> FastlioOdomAlignmentAdapter:
        adapter = FastlioOdomAlignmentAdapter.__new__(FastlioOdomAlignmentAdapter)
        adapter.args = SimpleNamespace(
            cloud_peer_odom_topic=["/uav2/odom", "/uav3/odom"],
            cloud_peer_odom_max_age_s=0.5,
            cloud_peer_filter_radius_xy_m=0.45,
            cloud_peer_filter_z_min_m=-0.30,
            cloud_peer_filter_z_max_m=0.30,
        )
        adapter.peer_odom_by_topic = {}
        adapter.peer_odom_lock = threading.Lock()
        return adapter

    def test_fresh_peer_odom_filters_only_peer_airframe(self):
        adapter = self.make_adapter()
        peer = make_odom(10.0)
        peer.pose.pose.position.x = 2.0
        peer.pose.pose.position.y = 1.0
        peer.pose.pose.position.z = 1.2
        adapter.on_peer_odom(peer, "/uav2/odom")

        centers, stale = adapter.peer_filter_centers(10.2)

        self.assertEqual(stale, 1)
        self.assertEqual(adapter.peer_filter_match((2.2, 1.0, 1.2), centers), "/uav2/odom")
        self.assertIsNone(adapter.peer_filter_match((2.6, 1.0, 1.2), centers))

    def test_stale_peer_odom_does_not_filter(self):
        adapter = self.make_adapter()
        peer = make_odom(9.0)
        peer.pose.pose.position.x = 2.0
        adapter.on_peer_odom(peer, "/uav2/odom")

        centers, stale = adapter.peer_filter_centers(10.0)

        self.assertEqual(centers, [])
        self.assertEqual(stale, 2)

    def test_peer_filter_keeps_points_outside_vertical_window(self):
        adapter = self.make_adapter()
        centers = [("/uav2/odom", (2.0, 1.0, 1.2), 0.1)]

        self.assertIsNone(adapter.peer_filter_match((2.0, 1.0, 1.51), centers))

    def test_cloud_callback_removes_peer_point_instead_of_writing_nan(self):
        adapter = self.make_adapter()
        adapter.args.cloud_self_filter_radius_xy_m = 0.0
        adapter.args.cloud_self_filter_z_min_m = -0.3
        adapter.args.cloud_self_filter_z_max_m = 0.3
        adapter.args.output_frame = "world"
        adapter.args.z_source = "fastlio"
        adapter.args.input_pose_frame = "base"
        adapter.args.cloud_diagnostics_path = ""
        adapter.local_from_fast = Pose3((0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0))
        adapter.mount_pose = Pose3((0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0))
        adapter.fastlio_odom = make_odom(10.0)
        adapter.fastlio_odom.pose.pose.orientation.w = 1.0
        peer = make_odom(10.0)
        peer.pose.pose.position.x = 2.0
        peer.pose.pose.position.y = 1.0
        peer.pose.pose.position.z = 1.2
        adapter.on_peer_odom(peer, "/uav2/odom")
        adapter.cloud_pub = Mock()
        adapter.cloud_received = 0
        adapter.cloud_published = 0
        adapter.cloud_dropped_before_alignment = 0
        adapter.cloud_finite_input_total = 0
        adapter.cloud_self_filtered_total = 0
        adapter.cloud_peer_filtered_total = 0
        adapter.cloud_peer_stale_samples_total = 0
        adapter.cloud_finite_output_total = 0
        adapter.cloud_peer_filtered_by_topic = {
            "/uav2/odom": 0,
            "/uav3/odom": 0,
        }
        adapter.last_cloud_diagnostics_wall = 0.0

        header = Header(stamp=make_odom(10.0).header.stamp, frame_id="world")
        cloud = point_cloud2.create_cloud_xyz32(
            header,
            [(2.1, 1.0, 1.2), (4.0, 1.0, 1.2)],
        )
        adapter.on_cloud(cloud)

        output = adapter.cloud_pub.publish.call_args.args[0]
        points = list(point_cloud2.read_points(output, field_names=("x", "y", "z")))
        self.assertEqual(len(points), 1)
        self.assertAlmostEqual(points[0][0], 4.0)
        self.assertEqual(adapter.cloud_peer_filtered_total, 1)


if __name__ == "__main__":
    unittest.main()
