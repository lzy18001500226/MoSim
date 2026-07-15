#!/usr/bin/env python3
"""Publish a read-only Factory exploration coverage overlay for RViz.

This is a display-only sensor-footprint estimate derived from odometry. It is
not FUEL's occupancy state and never feeds the planner or controller.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import rospy
from geometry_msgs.msg import Point
from nav_msgs.msg import Odometry
from std_msgs.msg import ColorRGBA
from visualization_msgs.msg import Marker, MarkerArray


class CoverageOverlay:
    def __init__(self) -> None:
        self.frame_id = str(rospy.get_param("~frame_id", "world"))
        self.odom_topic = str(rospy.get_param("~odom_topic", "/uav1/mavros/local_position/odom"))
        self.output_topic = str(rospy.get_param("~output_topic", "/mosim/fuel/coverage_overlay"))
        self.min_x = float(rospy.get_param("~boundary_min_x"))
        self.max_x = float(rospy.get_param("~boundary_max_x"))
        self.min_y = float(rospy.get_param("~boundary_min_y"))
        self.max_y = float(rospy.get_param("~boundary_max_y"))
        self.resolution = max(0.25, float(rospy.get_param("~resolution_m", 2.0)))
        self.sensor_radius = max(0.0, float(rospy.get_param("~sensor_radius_m", 8.0)))
        self.plane_z = float(rospy.get_param("~plane_z_m", 0.08))
        self.publish_rate_hz = max(0.2, float(rospy.get_param("~publish_rate_hz", 1.0)))
        self.diagnostics_path = Path(str(rospy.get_param("~diagnostics_path", "")))

        if self.max_x <= self.min_x or self.max_y <= self.min_y:
            raise ValueError("coverage boundary must have positive X and Y spans")
        self.nx = max(1, int(math.ceil((self.max_x - self.min_x) / self.resolution)))
        self.ny = max(1, int(math.ceil((self.max_y - self.min_y) / self.resolution)))
        if self.nx * self.ny > 10000:
            raise ValueError("coverage overlay exceeds 10000 cells; increase ~resolution_m")

        self.explored: set[tuple[int, int]] = set()
        self.last_position: tuple[float, float, float] | None = None
        self.odom_count = 0
        self.first_wall = time.time()
        self.publisher = rospy.Publisher(self.output_topic, MarkerArray, queue_size=1, latch=True)
        rospy.Subscriber(self.odom_topic, Odometry, self.on_odom, queue_size=50)
        rospy.Timer(rospy.Duration(1.0 / self.publish_rate_hz), self.on_timer)

    def cell_center(self, ix: int, iy: int) -> Point:
        return Point(
            x=min(self.max_x, self.min_x + (ix + 0.5) * self.resolution),
            y=min(self.max_y, self.min_y + (iy + 0.5) * self.resolution),
            z=self.plane_z,
        )

    def on_odom(self, msg: Odometry) -> None:
        x = float(msg.pose.pose.position.x)
        y = float(msg.pose.pose.position.y)
        z = float(msg.pose.pose.position.z)
        self.last_position = (x, y, z)
        self.odom_count += 1
        if not (self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y):
            return
        ix = min(max(int((x - self.min_x) / self.resolution), 0), self.nx - 1)
        iy = min(max(int((y - self.min_y) / self.resolution), 0), self.ny - 1)
        radius_cells = int(math.ceil(self.sensor_radius / self.resolution))
        for sx in range(max(0, ix - radius_cells), min(self.nx, ix + radius_cells + 1)):
            for sy in range(max(0, iy - radius_cells), min(self.ny, iy + radius_cells + 1)):
                center = self.cell_center(sx, sy)
                if math.hypot(center.x - x, center.y - y) <= self.sensor_radius:
                    self.explored.add((sx, sy))

    def basic_marker(self, marker_id: int, namespace: str, marker_type: int) -> Marker:
        marker = Marker()
        marker.header.frame_id = self.frame_id
        marker.header.stamp = rospy.Time.now()
        marker.ns = namespace
        marker.id = marker_id
        marker.type = marker_type
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        return marker

    def build_markers(self) -> MarkerArray:
        boundary = self.basic_marker(0, "factory_boundary", Marker.LINE_STRIP)
        boundary.scale.x = 0.12
        boundary.color = ColorRGBA(0.95, 0.95, 0.95, 0.85)
        boundary.points = [
            Point(self.min_x, self.min_y, self.plane_z + 0.03),
            Point(self.max_x, self.min_y, self.plane_z + 0.03),
            Point(self.max_x, self.max_y, self.plane_z + 0.03),
            Point(self.min_x, self.max_y, self.plane_z + 0.03),
            Point(self.min_x, self.min_y, self.plane_z + 0.03),
        ]

        remaining = self.basic_marker(1, "remaining_coverage", Marker.CUBE_LIST)
        remaining.scale.x = self.resolution * 0.90
        remaining.scale.y = self.resolution * 0.90
        remaining.scale.z = 0.035
        remaining.color = ColorRGBA(0.35, 0.38, 0.42, 0.10)

        explored = self.basic_marker(2, "explored_sensor_footprint", Marker.CUBE_LIST)
        explored.scale.x = self.resolution * 0.92
        explored.scale.y = self.resolution * 0.92
        explored.scale.z = 0.055
        explored.color = ColorRGBA(0.10, 0.78, 0.35, 0.42)

        for ix in range(self.nx):
            for iy in range(self.ny):
                point = self.cell_center(ix, iy)
                if (ix, iy) in self.explored:
                    explored.points.append(point)
                else:
                    remaining.points.append(point)
        return MarkerArray(markers=[boundary, remaining, explored])

    def on_timer(self, _event: rospy.TimerEvent) -> None:
        self.publisher.publish(self.build_markers())
        self.write_diagnostics()

    def write_diagnostics(self) -> None:
        if not self.diagnostics_path:
            return
        self.diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
        total = self.nx * self.ny
        payload = {
            "schema": "mosim.fuel_coverage_visualization.v1",
            "scope": "review_only_sensor_footprint_estimate_not_planner_input",
            "topics": {"odom": self.odom_topic, "output": self.output_topic},
            "boundary": [self.min_x, self.max_x, self.min_y, self.max_y],
            "resolution_m": self.resolution,
            "sensor_radius_m": self.sensor_radius,
            "grid_shape": [self.nx, self.ny],
            "odom_count": self.odom_count,
            "explored_cells": len(self.explored),
            "remaining_cells": total - len(self.explored),
            "coverage_ratio": len(self.explored) / total,
            "last_position": self.last_position,
            "wall_elapsed_s": time.time() - self.first_wall,
        }
        self.diagnostics_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    rospy.init_node("mosim_fuel_coverage_visualization")
    CoverageOverlay()
    rospy.spin()


if __name__ == "__main__":
    main()
