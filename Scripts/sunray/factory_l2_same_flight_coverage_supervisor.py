#!/usr/bin/env python3
"""Same-flight coverage supervisor for Factory L2 FUEL probes.

The node does not publish position commands. It only republishes FUEL start
triggers, watches the actual odometry path, and records coverage progress. This
keeps trajectory generation inside FUEL/traj_server while making stalls visible.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from rospy.msg import AnyMsg


class CoverageGrid:
    def __init__(self, min_x: float, max_x: float, min_y: float, max_y: float, resolution: float, radius: float) -> None:
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.resolution = max(0.1, resolution)
        self.radius = max(0.0, radius)
        self.nx = max(1, int(math.ceil((self.max_x - self.min_x) / self.resolution)))
        self.ny = max(1, int(math.ceil((self.max_y - self.min_y) / self.resolution)))
        self.path_cells: set[tuple[int, int]] = set()
        self.sensor_cells: set[tuple[int, int]] = set()
        self.outside_rows = 0

    def add_pose(self, x: float, y: float) -> None:
        if x < self.min_x or x > self.max_x or y < self.min_y or y > self.max_y:
            self.outside_rows += 1
            return
        ix = min(max(int((x - self.min_x) / self.resolution), 0), self.nx - 1)
        iy = min(max(int((y - self.min_y) / self.resolution), 0), self.ny - 1)
        self.path_cells.add((ix, iy))
        radius_cells = max(0, int(math.ceil(self.radius / self.resolution)))
        for sx in range(ix - radius_cells, ix + radius_cells + 1):
            if sx < 0 or sx >= self.nx:
                continue
            cx = self.min_x + (sx + 0.5) * self.resolution
            for sy in range(iy - radius_cells, iy + radius_cells + 1):
                if sy < 0 or sy >= self.ny:
                    continue
                cy = self.min_y + (sy + 0.5) * self.resolution
                if math.hypot(cx - x, cy - y) <= self.radius:
                    self.sensor_cells.add((sx, sy))

    def summary(self) -> dict:
        total = self.nx * self.ny
        return {
            "grid_resolution_m": self.resolution,
            "sensor_radius_m": self.radius,
            "grid_shape": [self.nx, self.ny],
            "grid_cell_count": total,
            "path_cells": len(self.path_cells),
            "sensor_footprint_cells": len(self.sensor_cells),
            "path_coverage_ratio": len(self.path_cells) / total,
            "sensor_footprint_coverage_ratio": len(self.sensor_cells) / total,
            "outside_boundary_rows": self.outside_rows,
        }


class SameFlightCoverageSupervisor:
    def __init__(self) -> None:
        self.result_path = Path(rospy.get_param("~result_path", ""))
        self.trigger_topic = rospy.get_param("~trigger_topic", "/traj_start_trigger")
        self.odom_topic = rospy.get_param("~odom_topic", "/uav1/mavros/local_position/odom")
        self.bspline_topic = rospy.get_param("~bspline_topic", "/planning/bspline")
        self.position_cmd_topic = rospy.get_param("~position_cmd_topic", "/fuel/position_cmd_raw")
        self.frame_id = rospy.get_param("~frame_id", "world")
        self.target_z = float(rospy.get_param("~target_z", 1.2))
        self.min_x = float(rospy.get_param("~boundary_min_x", -10.0))
        self.max_x = float(rospy.get_param("~boundary_max_x", 10.0))
        self.min_y = float(rospy.get_param("~boundary_min_y", -10.0))
        self.max_y = float(rospy.get_param("~boundary_max_y", 10.0))
        self.coverage_resolution = float(rospy.get_param("~coverage_resolution_m", 2.0))
        self.sensor_radius = float(rospy.get_param("~sensor_radius_m", 8.0))
        self.min_required_ratio = float(rospy.get_param("~min_required_ratio", 0.80))
        self.initial_delay_s = max(0.0, float(rospy.get_param("~initial_delay_s", 35.0)))
        self.trigger_interval_s = max(1.0, float(rospy.get_param("~trigger_interval_s", 45.0)))
        self.stale_bspline_s = max(1.0, float(rospy.get_param("~stale_bspline_s", 20.0)))
        self.min_trigger_move_m = max(0.0, float(rospy.get_param("~min_trigger_move_m", 0.5)))
        self.max_runtime_s = max(0.0, float(rospy.get_param("~max_runtime_s", 0.0)))
        self.no_growth_timeout_s = max(0.0, float(rospy.get_param("~no_growth_timeout_s", 0.0)))
        self.min_growth_cells = max(1, int(rospy.get_param("~min_growth_cells", 1)))
        self.write_interval_s = max(1.0, float(rospy.get_param("~write_interval_s", 2.0)))
        self.time_basis = str(rospy.get_param("~time_basis", "wall")).strip().lower()
        self.trigger_require_target_z = bool(rospy.get_param("~trigger_require_target_z", True))
        self.trigger_z_tolerance_m = max(0.0, float(rospy.get_param("~trigger_z_tolerance_m", 0.3)))

        self.grid = CoverageGrid(self.min_x, self.max_x, self.min_y, self.max_y, self.coverage_resolution, self.sensor_radius)
        self.pub = rospy.Publisher(self.trigger_topic, PoseStamped, queue_size=3, latch=True)
        self.last_odom: Odometry | None = None
        self.last_odom_wall: float | None = None
        self.first_sim: float | None = None
        self.last_sim: float | None = None
        self.last_odom_sim: float | None = None
        self.first_wall = time.time()
        self.last_write_wall = 0.0
        self.last_trigger_wall: float | None = None
        self.last_trigger_elapsed_s: float | None = None
        self.first_trigger_elapsed_s: float | None = None
        self.last_trigger_xy: tuple[float, float] | None = None
        self.trigger_events: list[dict] = []
        self.trigger_wait_reason: str | None = "no_odom"
        self.odom_count = 0
        self.bspline_count = 0
        self.position_cmd_count = 0
        self.last_bspline_wall: float | None = None
        self.last_position_cmd_wall: float | None = None
        self.last_growth_wall = self.first_wall
        self.last_growth_sensor_cells = 0
        self.stop_reason: str | None = None

        rospy.Subscriber(self.odom_topic, Odometry, self.on_odom, queue_size=50)
        rospy.Subscriber(self.bspline_topic, AnyMsg, self.on_bspline, queue_size=20)
        rospy.Subscriber(self.position_cmd_topic, AnyMsg, self.on_position_cmd, queue_size=50)

    def update_sim_time(self, msg: Odometry | None = None) -> None:
        stamp = msg.header.stamp if msg is not None else rospy.Time.now()
        if stamp is None:
            return
        secs = stamp.to_sec()
        if secs <= 0.0:
            return
        if self.first_sim is None:
            self.first_sim = secs
        self.last_sim = secs
        if msg is not None:
            self.last_odom_sim = secs

    def elapsed_s(self) -> float:
        if self.time_basis in ("sim", "ros", "ros_sim_time", "sim_time") and self.first_sim is not None:
            now_sim = rospy.Time.now().to_sec()
            if now_sim > 0.0:
                self.last_sim = now_sim
            if self.last_sim is not None:
                return max(0.0, self.last_sim - self.first_sim)
        return time.time() - self.first_wall

    def on_odom(self, msg: Odometry) -> None:
        self.last_odom = msg
        self.last_odom_wall = time.time()
        self.update_sim_time(msg)
        self.odom_count += 1
        self.grid.add_pose(msg.pose.pose.position.x, msg.pose.pose.position.y)
        sensor_cells = len(self.grid.sensor_cells)
        if sensor_cells >= self.last_growth_sensor_cells + self.min_growth_cells:
            self.last_growth_sensor_cells = sensor_cells
            self.last_growth_wall = self.last_odom_wall

    def on_bspline(self, _msg: AnyMsg) -> None:
        self.bspline_count += 1
        self.last_bspline_wall = time.time()

    def on_position_cmd(self, _msg: AnyMsg) -> None:
        self.position_cmd_count += 1
        self.last_position_cmd_wall = time.time()

    def trigger_gate_ready(self) -> bool:
        if self.last_odom is None:
            self.trigger_wait_reason = "no_odom"
            return False
        z = self.last_odom.pose.pose.position.z
        if self.trigger_require_target_z and abs(z - self.target_z) > self.trigger_z_tolerance_m:
            self.trigger_wait_reason = "odom_z_not_ready"
            return False
        self.trigger_wait_reason = None
        return True

    def publish_trigger(self, reason: str) -> None:
        if self.last_odom is None:
            return
        msg = PoseStamped()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.frame_id
        msg.pose = self.last_odom.pose.pose
        msg.pose.position.z = self.target_z
        self.pub.publish(msg)
        now = time.time()
        self.last_trigger_wall = now
        self.last_trigger_elapsed_s = self.elapsed_s()
        if self.first_trigger_elapsed_s is None:
            self.first_trigger_elapsed_s = self.last_trigger_elapsed_s
        self.last_trigger_xy = (msg.pose.position.x, msg.pose.position.y)
        self.trigger_events.append(
            {
                "wall_elapsed_s": now - self.first_wall,
                "elapsed_s": self.last_trigger_elapsed_s,
                "time_basis": self.time_basis,
                "reason": reason,
                "xyz": [msg.pose.position.x, msg.pose.position.y, msg.pose.position.z],
                "odom_z_m": self.last_odom.pose.pose.position.z,
                "target_z_m": self.target_z,
                "trigger_z_tolerance_m": self.trigger_z_tolerance_m,
                "bspline_count": self.bspline_count,
                "position_cmd_count": self.position_cmd_count,
                "coverage": self.grid.summary(),
            }
        )

    def maybe_trigger(self) -> None:
        now = time.time()
        elapsed = self.elapsed_s()
        if self.last_odom is None:
            self.trigger_wait_reason = "no_odom"
            return
        if not self.trigger_gate_ready():
            return
        if self.last_trigger_wall is None:
            if elapsed >= self.initial_delay_s:
                self.publish_trigger("initial_supervisor_trigger")
            return
        last_elapsed = self.last_trigger_elapsed_s if self.last_trigger_elapsed_s is not None else now - self.first_wall
        if elapsed - last_elapsed < self.trigger_interval_s:
            return
        moved_enough = True
        if self.last_trigger_xy is not None:
            dx = self.last_odom.pose.pose.position.x - self.last_trigger_xy[0]
            dy = self.last_odom.pose.pose.position.y - self.last_trigger_xy[1]
            moved_enough = math.hypot(dx, dy) >= self.min_trigger_move_m
        stale = self.last_bspline_wall is None or now - self.last_bspline_wall >= self.stale_bspline_s
        if stale:
            self.publish_trigger("stale_bspline_retrigger")
        elif moved_enough:
            self.publish_trigger("periodic_progress_retrigger")

    def packet(self) -> dict:
        coverage = self.grid.summary()
        status = "running"
        blockers: list[str] = []
        if coverage["sensor_footprint_coverage_ratio"] >= self.min_required_ratio:
            status = "coverage_threshold_reached"
        elif self.stop_reason:
            status = "blocked"
            blockers.append(self.stop_reason)
        last_odom_xyz = None
        if self.last_odom is not None:
            p = self.last_odom.pose.pose.position
            last_odom_xyz = [p.x, p.y, p.z]
        return {
            "schema": "mosim.factory_l2.same_flight_coverage_supervisor.v2",
            "status": status,
            "blockers": blockers,
            "wall_elapsed_s": time.time() - self.first_wall,
            "elapsed_s": self.elapsed_s(),
            "time_basis": self.time_basis,
            "sim_time": {
                "first_sim_s": self.first_sim,
                "last_sim_s": self.last_sim,
                "last_odom_sim_s": self.last_odom_sim,
            },
            "topics": {
                "trigger_topic": self.trigger_topic,
                "odom_topic": self.odom_topic,
                "bspline_topic": self.bspline_topic,
                "position_cmd_topic": self.position_cmd_topic,
            },
            "boundary": {
                "min_x_m": self.min_x,
                "max_x_m": self.max_x,
                "min_y_m": self.min_y,
                "max_y_m": self.max_y,
            },
            "acceptance": {
                "min_required_ratio": self.min_required_ratio,
                "coverage": coverage,
            },
            "counts": {
                "odom": self.odom_count,
                "bspline": self.bspline_count,
                "position_cmd": self.position_cmd_count,
                "trigger_events": len(self.trigger_events),
            },
            "trigger_gate": {
                "require_target_z": self.trigger_require_target_z,
                "target_z_m": self.target_z,
                "z_tolerance_m": self.trigger_z_tolerance_m,
                "last_odom_xyz": last_odom_xyz,
                "last_wait_reason": self.trigger_wait_reason,
                "first_trigger_elapsed_s": self.first_trigger_elapsed_s,
                "last_trigger_elapsed_s": self.last_trigger_elapsed_s,
            },
            "last_seen_age_s": {
                "odom": None if self.last_odom_wall is None else time.time() - self.last_odom_wall,
                "bspline": None if self.last_bspline_wall is None else time.time() - self.last_bspline_wall,
                "position_cmd": None if self.last_position_cmd_wall is None else time.time() - self.last_position_cmd_wall,
                "coverage_growth": time.time() - self.last_growth_wall,
            },
            "stall_policy": {
                "no_growth_timeout_s": self.no_growth_timeout_s,
                "min_growth_cells": self.min_growth_cells,
                "last_growth_sensor_cells": self.last_growth_sensor_cells,
            },
            "trigger_events": self.trigger_events[-200:],
            "claim_boundary": [
                "This supervisor never publishes position_cmd or attitude commands.",
                "It can only trigger FUEL's existing exploration FSM and record same-flight coverage progress.",
                "If coverage stalls, the blocker is the current FUEL exploration/map strategy, not a direct-control failure proof.",
            ],
        }

    def write_packet(self) -> None:
        if not self.result_path:
            return
        self.result_path.parent.mkdir(parents=True, exist_ok=True)
        self.result_path.write_text(json.dumps(self.packet(), indent=2), encoding="utf-8")

    def spin(self) -> None:
        rate = rospy.Rate(5.0)
        while not rospy.is_shutdown():
            now = time.time()
            self.update_sim_time()
            elapsed = self.elapsed_s()
            budget_elapsed = None
            if self.first_trigger_elapsed_s is not None:
                budget_elapsed = elapsed - self.first_trigger_elapsed_s
            if self.max_runtime_s > 0 and budget_elapsed is not None and budget_elapsed >= self.max_runtime_s:
                self.stop_reason = "supervisor_runtime_budget_exhausted_before_full_coverage"
                self.write_packet()
                return
            if (
                self.no_growth_timeout_s > 0
                and self.bspline_count > 0
                and self.position_cmd_count > 0
                and now - self.last_growth_wall >= self.no_growth_timeout_s
            ):
                self.stop_reason = "coverage_stalled_before_full_boundary"
                self.write_packet()
                return
            self.maybe_trigger()
            coverage = self.grid.summary()
            if coverage["sensor_footprint_coverage_ratio"] >= self.min_required_ratio:
                self.write_packet()
                return
            if now - self.last_write_wall >= self.write_interval_s:
                self.last_write_wall = now
                self.write_packet()
            rate.sleep()
        self.stop_reason = "ros_shutdown_before_full_coverage"
        self.write_packet()


def main() -> None:
    rospy.init_node("mosim_factory_l2_same_flight_coverage_supervisor", anonymous=True)
    SameFlightCoverageSupervisor().spin()


if __name__ == "__main__":
    main()
