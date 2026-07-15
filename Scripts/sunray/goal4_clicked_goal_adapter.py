#!/usr/bin/env python3
"""RViz goal adapter for Goal4 Diff-Planner review.

This review-only node converts RViz 2D Nav Goal input into the PoseStamped
target topic consumed by the current Diff-Planner overlay. It deliberately
keeps the planner and controller code unchanged.
"""

from __future__ import annotations

import json
import heapq
import math
import re
import time
from pathlib import Path
from xml.etree import ElementTree as ET

import rospy
from geometry_msgs.msg import PointStamped, PoseStamped
from nav_msgs.msg import Odometry, Path as RosPath
from std_msgs.msg import Bool, Header


class ClickedGoalAdapter:
    def __init__(self) -> None:
        self.clicked_point_topic = rospy.get_param("~clicked_point_topic", "/clicked_point")
        self.nav_goal_topic = rospy.get_param("~nav_goal_topic", "/move_base_simple/goal")
        self.output_goal_topic = rospy.get_param("~output_goal_topic", "/goal_with_id")
        self.target_path_topic = rospy.get_param("~target_path_topic", "/mosim/goal4/target_path")
        self.mission_ready_topic = rospy.get_param("~mission_ready_topic", "/mosim/goal4/interactive_goal_ready")
        self.require_mission_ready = bool(rospy.get_param("~require_mission_ready", True))
        self.odom_topic = rospy.get_param("~odom_topic", "/uav1/mavros/local_position/odom")
        self.frame_id = rospy.get_param("~frame_id", "world")
        self.target_z = float(rospy.get_param("~target_z", 1.0))
        self.use_clicked_z = bool(rospy.get_param("~use_clicked_z", False))
        self.enable_clicked_point = bool(rospy.get_param("~enable_clicked_point", False))
        self.ready_gate_enabled = bool(rospy.get_param("~ready_gate_enabled", True))
        self.ready_min_z = float(rospy.get_param("~ready_min_z", max(0.0, self.target_z - 0.15)))
        self.ready_z_tolerance = float(rospy.get_param("~ready_z_tolerance", 0.15))
        self.ready_max_speed_mps = float(rospy.get_param("~ready_max_speed_mps", 0.35))
        self.ready_max_vz_mps = float(rospy.get_param("~ready_max_vz_mps", 0.20))
        self.ready_max_roll_pitch_deg = float(rospy.get_param("~ready_max_roll_pitch_deg", 12.0))
        self.ready_required_stable_s = float(rospy.get_param("~ready_required_stable_s", 1.0))
        self.ready_odom_timeout_s = float(rospy.get_param("~ready_odom_timeout_s", 0.50))
        self.duplicate_goal_window_s = float(rospy.get_param("~duplicate_goal_window_s", 0.60))
        self.duplicate_goal_xy_tol_m = float(rospy.get_param("~duplicate_goal_xy_tol_m", 0.03))
        self.duplicate_goal_z_tol_m = float(rospy.get_param("~duplicate_goal_z_tol_m", 0.05))
        self.min_x = self.optional_float_param("~min_x")
        self.max_x = self.optional_float_param("~max_x")
        self.min_y = self.optional_float_param("~min_y")
        self.max_y = self.optional_float_param("~max_y")
        self.max_goal_distance_xy = self.optional_float_param("~max_goal_distance_xy")
        self.staged_goal_enabled = bool(rospy.get_param("~staged_goal_enabled", True))
        self.stage_reach_xy_radius_m = float(rospy.get_param("~stage_reach_xy_radius_m", 0.35))
        self.stage_reach_z_tol_m = float(rospy.get_param("~stage_reach_z_tol_m", self.ready_z_tolerance))
        self.stage_required_stable_s = float(rospy.get_param("~stage_required_stable_s", self.ready_required_stable_s))
        self.stage_max_count = int(rospy.get_param("~stage_max_count", 20))
        self.static_obstacle_guard_enabled = bool(rospy.get_param("~static_obstacle_guard_enabled", True))
        self.static_obstacle_world_file = str(rospy.get_param("~static_obstacle_world_file", ""))
        self.static_obstacle_default_radius_m = float(rospy.get_param("~static_obstacle_default_radius_m", 0.20))
        self.static_obstacle_inflation_m = float(rospy.get_param("~static_obstacle_inflation_m", 0.20))
        self.static_obstacle_extra_margin_m = float(rospy.get_param("~static_obstacle_extra_margin_m", 0.12))
        # Review adapter must not replace Diff-Planner with a coarse global A*.
        # Keep this disabled by default; enable only for explicit diagnostics.
        self.static_path_guard_enabled = bool(rospy.get_param("~static_path_guard_enabled", False))
        self.static_path_guard_grid_resolution_m = float(rospy.get_param("~static_path_guard_grid_resolution_m", 0.5))
        self.static_path_guard_bounds_padding_m = float(rospy.get_param("~static_path_guard_bounds_padding_m", 2.0))
        self.static_path_guard_max_waypoints = int(rospy.get_param("~static_path_guard_max_waypoints", 80))
        self.static_path_guard_max_nodes = int(rospy.get_param("~static_path_guard_max_nodes", 50000))
        self.diagnostics_path = rospy.get_param("~diagnostics_path", "")

        self.last_odom: Odometry | None = None
        self.last_odom_wall: float | None = None
        self.ready_stable_since_wall: float | None = None
        self.last_ready_snapshot: dict | None = None
        self.mission_ready = not self.require_mission_ready
        self.last_mission_ready_wall: float | None = None
        self.clicked_point_count = 0
        self.nav_goal_count = 0
        self.published_goal_count = 0
        self.rejected_goal_count = 0
        self.queued_goal_count = 0
        self.queue_release_count = 0
        self.duplicate_goal_ignored_count = 0
        self.clamped_count = 0
        self.staged_goal_count = 0
        self.stage_publish_count = 0
        self.stage_completion_count = 0
        self.stage_rejected_count = 0
        self.last_goal: dict | None = None
        self.last_published_request: dict | None = None
        self.last_published_request_wall: float | None = None
        self.queued_goal: dict | None = None
        self.last_rejected_goal: dict | None = None
        self.active_staged_goal: dict | None = None
        self.stage_stable_since_wall: float | None = None
        self.last_stage_snapshot: dict | None = None
        self.first_goal_wall: float | None = None
        self.last_goal_wall: float | None = None
        self.last_path_goal: tuple[float, float, float] | None = None
        self.last_path_guard_plan: dict | None = None
        self.static_obstacles = self.load_static_obstacles()

        self.goal_pub = rospy.Publisher(self.output_goal_topic, PoseStamped, queue_size=5, latch=True)
        self.path_pub = rospy.Publisher(self.target_path_topic, RosPath, queue_size=1, latch=True)
        if self.enable_clicked_point:
            rospy.Subscriber(self.clicked_point_topic, PointStamped, self.on_clicked_point, queue_size=10)
        rospy.Subscriber(self.nav_goal_topic, PoseStamped, self.on_nav_goal, queue_size=10)
        rospy.Subscriber(self.mission_ready_topic, Bool, self.on_mission_ready, queue_size=5)
        rospy.Subscriber(self.odom_topic, Odometry, self.on_odom, queue_size=20)

    @staticmethod
    def optional_float_param(name: str) -> float | None:
        if not rospy.has_param(name):
            return None
        value = rospy.get_param(name)
        if value in ("", None):
            return None
        return float(value)

    @staticmethod
    def clamp(value: float, lower: float | None, upper: float | None) -> tuple[float, bool]:
        clamped = False
        if lower is not None and value < lower:
            value = lower
            clamped = True
        if upper is not None and value > upper:
            value = upper
            clamped = True
        return value, clamped

    def on_odom(self, msg: Odometry) -> None:
        self.last_odom = msg
        self.last_odom_wall = time.time()
        snapshot = self.ready_snapshot()
        self.last_ready_snapshot = snapshot
        if snapshot["ready_now"]:
            if self.ready_stable_since_wall is None:
                self.ready_stable_since_wall = self.last_odom_wall
        else:
            self.ready_stable_since_wall = None
        self.try_release_queued_goal()

    def on_mission_ready(self, msg: Bool) -> None:
        self.mission_ready = bool(msg.data)
        self.last_mission_ready_wall = time.time()
        if self.mission_ready:
            self.try_release_queued_goal()

    def on_clicked_point(self, msg: PointStamped) -> None:
        self.clicked_point_count += 1
        z = float(msg.point.z) if self.use_clicked_z and math.isfinite(msg.point.z) else self.target_z
        self.publish_goal(float(msg.point.x), float(msg.point.y), z, source="clicked_point")

    def on_nav_goal(self, msg: PoseStamped) -> None:
        self.nav_goal_count += 1
        # RViz 2D Nav Goal lies on the ground plane; use a fixed flight height.
        self.publish_goal(float(msg.pose.position.x), float(msg.pose.position.y), self.target_z, source="nav_goal")

    @staticmethod
    def rpy_from_quat(x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
        roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
        pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
        yaw = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
        return roll, pitch, yaw

    def ready_snapshot(self) -> dict:
        if self.last_odom is None or self.last_odom_wall is None:
            return {"ready_now": False, "stable": False, "reasons": ["odom_missing"]}
        now_wall = time.time()
        age_s = now_wall - self.last_odom_wall
        p = self.last_odom.pose.pose.position
        q = self.last_odom.pose.pose.orientation
        v = self.last_odom.twist.twist.linear
        roll, pitch, _ = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        speed = math.sqrt(float(v.x) * float(v.x) + float(v.y) * float(v.y) + float(v.z) * float(v.z))
        abs_vz = abs(float(v.z))
        abs_roll_pitch_deg = math.degrees(max(abs(roll), abs(pitch)))
        reasons: list[str] = []
        if self.require_mission_ready and not self.mission_ready:
            reasons.append("mission_not_ready")
        if age_s > self.ready_odom_timeout_s:
            reasons.append("odom_timeout")
        if float(p.z) < self.ready_min_z:
            reasons.append("z_below_ready_min")
        if abs(float(p.z) - self.target_z) > self.ready_z_tolerance:
            reasons.append("z_outside_target_tolerance")
        if speed > self.ready_max_speed_mps:
            reasons.append("speed_above_ready_gate")
        if abs_vz > self.ready_max_vz_mps:
            reasons.append("vz_above_ready_gate")
        if abs_roll_pitch_deg > self.ready_max_roll_pitch_deg:
            reasons.append("attitude_above_ready_gate")
        stable_duration_s = 0.0
        ready_now = not reasons
        if ready_now and self.ready_stable_since_wall is not None:
            stable_duration_s = now_wall - self.ready_stable_since_wall
        return {
            "ready_now": ready_now,
            "stable": ready_now and stable_duration_s >= self.ready_required_stable_s,
            "stable_duration_s": stable_duration_s,
            "required_stable_s": self.ready_required_stable_s,
            "reasons": reasons,
            "mission_ready": self.mission_ready,
            "require_mission_ready": self.require_mission_ready,
            "mission_ready_topic": self.mission_ready_topic,
            "last_mission_ready_age_s": (
                None if self.last_mission_ready_wall is None else now_wall - self.last_mission_ready_wall
            ),
            "odom_age_s": age_s,
            "z": float(p.z),
            "target_z": self.target_z,
            "speed_mps": speed,
            "abs_vz_mps": abs_vz,
            "abs_roll_pitch_deg": abs_roll_pitch_deg,
        }

    def is_ready_to_forward_goal(self) -> bool:
        if not self.ready_gate_enabled:
            return True
        snapshot = self.ready_snapshot()
        self.last_ready_snapshot = snapshot
        return bool(snapshot.get("stable"))

    def is_duplicate_goal(self, requested: dict, source: str) -> bool:
        if self.last_published_request is None or self.last_published_request_wall is None:
            return False
        if time.time() - self.last_published_request_wall > self.duplicate_goal_window_s:
            return False
        if self.last_published_request.get("source") != source:
            return False
        dx = float(requested["x"]) - float(self.last_published_request["x"])
        dy = float(requested["y"]) - float(self.last_published_request["y"])
        dz = float(requested["z"]) - float(self.last_published_request["z"])
        return math.hypot(dx, dy) <= self.duplicate_goal_xy_tol_m and abs(dz) <= self.duplicate_goal_z_tol_m

    def queue_goal(self, requested: dict, source: str) -> None:
        self.queued_goal_count += 1
        now_wall = time.time()
        if self.first_goal_wall is None:
            self.first_goal_wall = now_wall
        self.last_goal_wall = now_wall
        self.queued_goal = {
            "source": source,
            "x": requested["x"],
            "y": requested["y"],
            "z": requested["z"],
            "requested": requested,
            "wall_time": now_wall,
            "ready_snapshot": self.last_ready_snapshot or self.ready_snapshot(),
            "mission_ready": self.mission_ready,
        }
        rospy.logwarn(
            "Queued Goal4 %s target %.3f %.3f %.3f until takeoff/hover readiness gate is stable",
            source,
            requested["x"],
            requested["y"],
            requested["z"],
        )
        self.write_diagnostics()

    def try_release_queued_goal(self) -> None:
        if self.queued_goal is None or not self.is_ready_to_forward_goal():
            return
        queued = self.queued_goal
        self.queued_goal = None
        self.queue_release_count += 1
        self.publish_goal(float(queued["x"]), float(queued["y"]), float(queued["z"]), str(queued["source"]), allow_queue=False)

    def staged_goal_should_be_used(self, distance_xy: float) -> bool:
        return bool(
            self.staged_goal_enabled
            and self.max_goal_distance_xy is not None
            and self.max_goal_distance_xy > 0.0
            and distance_xy > self.max_goal_distance_xy
        )

    def start_staged_goal(self, requested: dict, final_x: float, final_y: float, final_z: float, source: str) -> None:
        self.staged_goal_count += 1
        self.active_staged_goal = {
            "source": source,
            "requested": requested,
            "final": {"x": final_x, "y": final_y, "z": final_z},
            "stage_index": 0,
            "started_wall": time.time(),
            "last_stage_wall": None,
            "completed_wall": None,
            "failed": False,
            "failure_reason": None,
        }
        self.stage_stable_since_wall = None
        rospy.loginfo(
            "Started staged Goal4 %s target %.3f %.3f %.3f",
            source,
            final_x,
            final_y,
            final_z,
        )
        self.publish_next_staged_goal()

    def current_goal_distance_snapshot(self) -> dict:
        if self.last_odom is None or self.active_staged_goal is None:
            return {"active": self.active_staged_goal is not None, "ready": False, "reasons": ["missing_odom_or_goal"]}
        if self.last_goal is None:
            return {"active": True, "ready": False, "reasons": ["stage_goal_missing"]}
        p = self.last_odom.pose.pose.position
        goal = self.last_goal
        dx = float(goal["x"]) - float(p.x)
        dy = float(goal["y"]) - float(p.y)
        dz = float(p.z) - float(goal["z"])
        ready = self.ready_snapshot()
        reasons: list[str] = []
        distance_xy = math.hypot(dx, dy)
        if distance_xy > self.stage_reach_xy_radius_m:
            reasons.append("stage_xy_outside_radius")
        if abs(dz) > self.stage_reach_z_tol_m:
            reasons.append("stage_z_outside_tolerance")
        if not ready.get("ready_now", False):
            reasons.extend([f"ready:{reason}" for reason in ready.get("reasons", [])])
        return {
            "active": True,
            "ready": not reasons,
            "reasons": reasons,
            "stage_index": self.active_staged_goal.get("stage_index"),
            "stage_goal": {"x": goal["x"], "y": goal["y"], "z": goal["z"]},
            "final": self.active_staged_goal.get("final"),
            "distance_xy_m": distance_xy,
            "z_error_m": dz,
            "ready_snapshot": ready,
        }

    def try_advance_staged_goal(self) -> None:
        if self.active_staged_goal is None:
            return
        snapshot = self.current_goal_distance_snapshot()
        self.last_stage_snapshot = snapshot
        if not snapshot.get("ready", False):
            self.stage_stable_since_wall = None
            return
        now_wall = time.time()
        if self.stage_stable_since_wall is None:
            self.stage_stable_since_wall = now_wall
            return
        snapshot["stable_duration_s"] = now_wall - self.stage_stable_since_wall
        self.last_stage_snapshot = snapshot
        if now_wall - self.stage_stable_since_wall < self.stage_required_stable_s:
            return
        if self.last_goal is not None and self.last_goal.get("stage_meta", {}).get("final_stage"):
            self.active_staged_goal["completed_wall"] = now_wall
            self.stage_completion_count += 1
            rospy.loginfo("Completed staged Goal4 target after %d stages", self.active_staged_goal.get("stage_index", 0))
            self.active_staged_goal = None
            self.stage_stable_since_wall = None
            return
        self.stage_stable_since_wall = None
        self.publish_next_staged_goal()

    def publish_next_staged_goal(self) -> None:
        if self.active_staged_goal is None:
            return
        if self.last_odom is None:
            return
        stage_index = int(self.active_staged_goal.get("stage_index", 0)) + 1
        if stage_index > self.stage_max_count:
            self.active_staged_goal["failed"] = True
            self.active_staged_goal["failure_reason"] = "stage_max_count_exceeded"
            self.stage_rejected_count += 1
            rospy.logwarn("Rejected staged Goal4 target: stage_max_count_exceeded")
            self.write_diagnostics()
            return
        final = self.active_staged_goal["final"]
        path = self.active_staged_goal.get("path")
        if path:
            path_index = stage_index - 1
            if path_index >= len(path):
                self.active_staged_goal["completed_wall"] = time.time()
                self.stage_completion_count += 1
                rospy.loginfo("Completed staged Goal4 path target after %d stages", stage_index - 1)
                self.active_staged_goal = None
                self.stage_stable_since_wall = None
                return
            waypoint = path[path_index]
            stage_x = float(waypoint["x"])
            stage_y = float(waypoint["y"])
            distance_xy = math.hypot(stage_x - float(self.last_odom.pose.pose.position.x),
                                     stage_y - float(self.last_odom.pose.pose.position.y))
            final_stage = path_index == len(path) - 1
            max_step = None
        else:
            ox = float(self.last_odom.pose.pose.position.x)
            oy = float(self.last_odom.pose.pose.position.y)
            dx = float(final["x"]) - ox
            dy = float(final["y"]) - oy
            distance_xy = math.hypot(dx, dy)
            max_step = float(self.max_goal_distance_xy or distance_xy)
            final_stage = distance_xy <= max_step or max_step <= 0.0
            if final_stage:
                stage_x = float(final["x"])
                stage_y = float(final["y"])
            else:
                scale = max_step / distance_xy
                stage_x = ox + dx * scale
                stage_y = oy + dy * scale
        self.active_staged_goal["stage_index"] = stage_index
        self.active_staged_goal["last_stage_wall"] = time.time()
        stage_meta = {
            "staged": True,
            "stage_index": stage_index,
            "final_stage": final_stage,
            "final": final,
            "requested": self.active_staged_goal.get("requested"),
            "distance_xy_from_odom": distance_xy,
            "stage_step_xy_m": distance_xy if max_step is None else min(distance_xy, max_step),
            "max_goal_distance_xy": self.max_goal_distance_xy,
            "path": path,
        }
        self.stage_publish_count += 1
        self.publish_goal(
            stage_x,
            stage_y,
            float(final["z"]),
            str(self.active_staged_goal["source"]),
            allow_queue=False,
            allow_staging=False,
            stage_meta=stage_meta,
            update_duplicate_key=False,
        )

    def load_static_obstacles(self) -> list[dict]:
        if not self.static_obstacle_world_file:
            return []
        path = Path(self.static_obstacle_world_file)
        if not path.exists():
            rospy.logwarn("Goal static-obstacle guard world file not found: %s", path)
            return []
        try:
            root = ET.fromstring(path.read_text(encoding="utf-8", errors="ignore"))
        except ET.ParseError as exc:
            rospy.logwarn("Goal static-obstacle guard could not parse %s: %s", path, exc)
            return []

        obstacles: list[dict] = []
        for include in root.iter("include"):
            uri = (include.findtext("uri") or "").strip()
            if "cylinder" not in uri:
                continue
            pose_text = (include.findtext("pose") or "").strip()
            parts = pose_text.split()
            if len(parts) < 3:
                continue
            try:
                x, y, z = (float(parts[0]), float(parts[1]), float(parts[2]))
            except ValueError:
                continue
            name = (include.findtext("name") or uri).strip()
            obstacles.append(
                {
                    "name": name,
                    "uri": uri,
                    "x": x,
                    "y": y,
                    "z": z,
                    "radius_m": self.radius_from_uri(uri),
                }
            )
        rospy.loginfo("Goal static-obstacle guard loaded %d cylinder obstacles", len(obstacles))
        return obstacles

    def radius_from_uri(self, uri: str) -> float:
        match = re.search(r"cylinder_(\d+)cm", uri)
        if not match:
            return self.static_obstacle_default_radius_m
        return float(match.group(1)) / 100.0

    def nearest_static_obstacle(self, x: float, y: float) -> dict | None:
        if not self.static_obstacles:
            return None
        nearest = min(self.static_obstacles, key=lambda item: math.hypot(x - item["x"], y - item["y"]))
        distance_xy = math.hypot(x - nearest["x"], y - nearest["y"])
        clearance_m = distance_xy - float(nearest["radius_m"])
        threshold_m = (
            float(nearest["radius_m"])
            + self.static_obstacle_inflation_m
            + self.static_obstacle_extra_margin_m
        )
        return {
            "name": nearest["name"],
            "uri": nearest["uri"],
            "x": nearest["x"],
            "y": nearest["y"],
            "radius_m": nearest["radius_m"],
            "distance_xy_m": distance_xy,
            "clearance_m": clearance_m,
            "reject_threshold_distance_m": threshold_m,
            "reject": distance_xy <= threshold_m,
        }

    def static_collision_radius(self, obstacle: dict) -> float:
        return (
            float(obstacle["radius_m"])
            + self.static_obstacle_inflation_m
            + self.static_obstacle_extra_margin_m
        )

    @staticmethod
    def point_segment_distance_xy(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> tuple[float, float]:
        vx = bx - ax
        vy = by - ay
        wx = px - ax
        wy = py - ay
        denom = vx * vx + vy * vy
        ratio = 0.0 if denom <= 1e-9 else max(0.0, min(1.0, (wx * vx + wy * vy) / denom))
        qx = ax + ratio * vx
        qy = ay + ratio * vy
        return math.hypot(px - qx, py - qy), ratio

    def segment_static_obstacle_hits(self, ax: float, ay: float, bx: float, by: float) -> list[dict]:
        hits: list[dict] = []
        for obstacle in self.static_obstacles:
            distance, ratio = self.point_segment_distance_xy(
                float(obstacle["x"]), float(obstacle["y"]), ax, ay, bx, by
            )
            radius = self.static_collision_radius(obstacle)
            if distance <= radius:
                hits.append(
                    {
                        "name": obstacle["name"],
                        "x": obstacle["x"],
                        "y": obstacle["y"],
                        "distance_to_segment_m": distance,
                        "inflated_radius_m": radius,
                        "segment_ratio": ratio,
                    }
                )
        hits.sort(key=lambda item: float(item["distance_to_segment_m"]) - float(item["inflated_radius_m"]))
        return hits

    def point_is_static_free(self, x: float, y: float) -> bool:
        for obstacle in self.static_obstacles:
            if math.hypot(x - float(obstacle["x"]), y - float(obstacle["y"])) <= self.static_collision_radius(obstacle):
                return False
        return True

    def nearest_free_grid_cell(self, cell: tuple[int, int], to_xy, lower_x: float, lower_y: float, nx: int, ny: int) -> tuple[int, int] | None:
        if self.grid_cell_is_free(cell, lower_x, lower_y):
            return cell
        best: tuple[float, tuple[int, int]] | None = None
        max_radius = max(nx, ny)
        for radius in range(1, max_radius + 1):
            for ix in range(cell[0] - radius, cell[0] + radius + 1):
                for iy in (cell[1] - radius, cell[1] + radius):
                    candidate = (ix, iy)
                    if not (0 <= ix < nx and 0 <= iy < ny):
                        continue
                    if self.grid_cell_is_free(candidate, lower_x, lower_y):
                        score = math.hypot(self.grid_x(ix, lower_x) - to_xy[0], self.grid_y(iy, lower_y) - to_xy[1])
                        best = min(best, (score, candidate)) if best else (score, candidate)
            for iy in range(cell[1] - radius + 1, cell[1] + radius):
                for ix in (cell[0] - radius, cell[0] + radius):
                    candidate = (ix, iy)
                    if not (0 <= ix < nx and 0 <= iy < ny):
                        continue
                    if self.grid_cell_is_free(candidate, lower_x, lower_y):
                        score = math.hypot(self.grid_x(ix, lower_x) - to_xy[0], self.grid_y(iy, lower_y) - to_xy[1])
                        best = min(best, (score, candidate)) if best else (score, candidate)
            if best is not None:
                return best[1]
        return None

    def grid_x(self, ix: int, lower_x: float) -> float:
        return lower_x + ix * self.static_path_guard_grid_resolution_m

    def grid_y(self, iy: int, lower_y: float) -> float:
        return lower_y + iy * self.static_path_guard_grid_resolution_m

    def xy_to_grid_cell(self, x: float, y: float, lower_x: float, lower_y: float, nx: int, ny: int) -> tuple[int, int]:
        resolution = self.static_path_guard_grid_resolution_m
        ix = max(0, min(nx - 1, int(round((x - lower_x) / resolution))))
        iy = max(0, min(ny - 1, int(round((y - lower_y) / resolution))))
        return ix, iy

    def grid_cell_is_free(self, cell: tuple[int, int], lower_x: float, lower_y: float) -> bool:
        ix, iy = cell
        x = self.grid_x(ix, lower_x)
        y = self.grid_y(iy, lower_y)
        return self.point_is_static_free(x, y)

    def plan_static_obstacle_path(self, start_xy: tuple[float, float], goal_xy: tuple[float, float]) -> dict:
        if not self.static_obstacles:
            return {"status": "blocked", "reason": "static_obstacles_missing"}
        resolution = self.static_path_guard_grid_resolution_m
        if resolution <= 0:
            return {"status": "blocked", "reason": "invalid_grid_resolution"}

        xs = [start_xy[0], goal_xy[0]] + [float(obstacle["x"]) for obstacle in self.static_obstacles]
        ys = [start_xy[1], goal_xy[1]] + [float(obstacle["y"]) for obstacle in self.static_obstacles]
        padding = self.static_path_guard_bounds_padding_m
        lower_x = math.floor((min(xs) - padding) / resolution) * resolution
        upper_x = math.ceil((max(xs) + padding) / resolution) * resolution
        lower_y = math.floor((min(ys) - padding) / resolution) * resolution
        upper_y = math.ceil((max(ys) + padding) / resolution) * resolution
        nx = int(round((upper_x - lower_x) / resolution)) + 1
        ny = int(round((upper_y - lower_y) / resolution)) + 1
        if nx <= 1 or ny <= 1 or nx * ny > self.static_path_guard_max_nodes:
            return {"status": "blocked", "reason": "grid_too_large", "nx": nx, "ny": ny}

        start_cell = self.xy_to_grid_cell(start_xy[0], start_xy[1], lower_x, lower_y, nx, ny)
        goal_cell = self.xy_to_grid_cell(goal_xy[0], goal_xy[1], lower_x, lower_y, nx, ny)
        start_cell = self.nearest_free_grid_cell(start_cell, start_xy, lower_x, lower_y, nx, ny)
        goal_cell = self.nearest_free_grid_cell(goal_cell, goal_xy, lower_x, lower_y, nx, ny)
        if start_cell is None or goal_cell is None:
            return {"status": "blocked", "reason": "free_endpoint_missing"}

        neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        open_heap: list[tuple[float, float, tuple[int, int]]] = []
        heapq.heappush(open_heap, (0.0, 0.0, start_cell))
        came_from: dict[tuple[int, int], tuple[int, int]] = {}
        g_score = {start_cell: 0.0}
        visited = 0
        while open_heap:
            _, current_cost, current = heapq.heappop(open_heap)
            if current_cost > g_score.get(current, float("inf")) + 1e-9:
                continue
            visited += 1
            if visited > self.static_path_guard_max_nodes:
                return {"status": "blocked", "reason": "node_limit_exceeded", "visited": visited}
            if current == goal_cell:
                break
            for dx, dy in neighbors:
                nxt = (current[0] + dx, current[1] + dy)
                if not (0 <= nxt[0] < nx and 0 <= nxt[1] < ny):
                    continue
                if not self.grid_cell_is_free(nxt, lower_x, lower_y):
                    continue
                if self.segment_static_obstacle_hits(
                    self.grid_x(current[0], lower_x),
                    self.grid_y(current[1], lower_y),
                    self.grid_x(nxt[0], lower_x),
                    self.grid_y(nxt[1], lower_y),
                ):
                    continue
                step_cost = math.hypot(dx, dy) * resolution
                tentative = current_cost + step_cost
                if tentative >= g_score.get(nxt, float("inf")):
                    continue
                came_from[nxt] = current
                g_score[nxt] = tentative
                heuristic = math.hypot(nxt[0] - goal_cell[0], nxt[1] - goal_cell[1]) * resolution
                heapq.heappush(open_heap, (tentative + heuristic, tentative, nxt))

        if goal_cell not in g_score:
            return {"status": "blocked", "reason": "astar_no_path", "visited": visited}

        cells = [goal_cell]
        while cells[-1] != start_cell:
            cells.append(came_from[cells[-1]])
        cells.reverse()
        raw_points = [(self.grid_x(ix, lower_x), self.grid_y(iy, lower_y)) for ix, iy in cells]
        pruned = self.prune_static_path(raw_points)
        if pruned and math.hypot(pruned[0][0] - start_xy[0], pruned[0][1] - start_xy[1]) < resolution * 1.5:
            pruned = pruned[1:]
        pruned.append(goal_xy)
        compact: list[tuple[float, float]] = []
        for point in pruned:
            if compact and math.hypot(point[0] - compact[-1][0], point[1] - compact[-1][1]) < resolution * 0.5:
                compact[-1] = point
            else:
                compact.append(point)
        if len(compact) > self.static_path_guard_max_waypoints:
            return {
                "status": "blocked",
                "reason": "too_many_waypoints",
                "waypoint_count": len(compact),
                "max_waypoints": self.static_path_guard_max_waypoints,
            }
        return {
            "status": "planned",
            "grid_resolution_m": resolution,
            "bounds": {"lower_x": lower_x, "upper_x": upper_x, "lower_y": lower_y, "upper_y": upper_y, "nx": nx, "ny": ny},
            "visited": visited,
            "raw_cell_count": len(cells),
            "waypoint_count": len(compact),
            "waypoints_xy": compact,
        }

    def prune_static_path(self, points: list[tuple[float, float]]) -> list[tuple[float, float]]:
        if len(points) <= 2:
            return points[:]
        pruned = [points[0]]
        anchor = 0
        while anchor < len(points) - 1:
            best = anchor + 1
            for idx in range(len(points) - 1, anchor, -1):
                if not self.segment_static_obstacle_hits(points[anchor][0], points[anchor][1], points[idx][0], points[idx][1]):
                    best = idx
                    break
            pruned.append(points[best])
            anchor = best
        return pruned

    def maybe_start_static_path_goal(self, requested: dict, x: float, y: float, z: float, source: str) -> bool:
        if not self.static_path_guard_enabled or self.last_odom is None or not self.static_obstacles:
            return False
        ox = float(self.last_odom.pose.pose.position.x)
        oy = float(self.last_odom.pose.pose.position.y)
        hits = self.segment_static_obstacle_hits(ox, oy, x, y)
        if not hits:
            self.last_path_guard_plan = {
                "used": False,
                "reason": "direct_segment_clear",
                "start": {"x": ox, "y": oy},
                "goal": {"x": x, "y": y},
            }
            return False
        plan = self.plan_static_obstacle_path((ox, oy), (x, y))
        plan["used"] = plan.get("status") == "planned"
        plan["direct_segment_hits"] = hits[:8]
        plan["start"] = {"x": ox, "y": oy}
        plan["goal"] = {"x": x, "y": y}
        self.last_path_guard_plan = plan
        if plan.get("status") != "planned":
            self.reject_goal(requested, x, y, z, source, f"static_path_guard_{plan.get('reason', 'blocked')}", plan)
            return True
        waypoints = [{"x": wx, "y": wy, "z": z} for wx, wy in plan["waypoints_xy"]]
        if not waypoints:
            return False
        self.start_path_staged_goal(requested, x, y, z, source, waypoints, plan)
        return True

    def start_path_staged_goal(
        self,
        requested: dict,
        final_x: float,
        final_y: float,
        final_z: float,
        source: str,
        waypoints: list[dict],
        plan: dict,
    ) -> None:
        self.staged_goal_count += 1
        self.active_staged_goal = {
            "source": source,
            "requested": requested,
            "final": {"x": final_x, "y": final_y, "z": final_z},
            "path": waypoints,
            "path_plan": plan,
            "stage_index": 0,
            "started_wall": time.time(),
            "last_stage_wall": None,
            "completed_wall": None,
            "failed": False,
            "failure_reason": None,
        }
        self.stage_stable_since_wall = None
        self.stage_max_count = max(self.stage_max_count, len(waypoints) + 2)
        rospy.logwarn(
            "Started static-path guarded Goal4 target %.3f %.3f %.3f with %d staged waypoints",
            final_x,
            final_y,
            final_z,
            len(waypoints),
        )
        self.publish_next_staged_goal()

    def reject_goal(self, requested: dict, x: float, y: float, z: float, source: str, reason: str, detail: dict) -> None:
        self.rejected_goal_count += 1
        if self.active_staged_goal is not None:
            self.active_staged_goal["failed"] = True
            self.active_staged_goal["failure_reason"] = reason
            self.stage_rejected_count += 1
        now_wall = time.time()
        if self.first_goal_wall is None:
            self.first_goal_wall = now_wall
        self.last_goal_wall = now_wall
        self.last_rejected_goal = {
            "source": source,
            "reason": reason,
            "x": x,
            "y": y,
            "z": z,
            "requested": requested,
            "detail": detail,
            "wall_time": now_wall,
        }
        rospy.logwarn("Rejected Goal4 %s target %.3f %.3f %.3f: %s", source, x, y, z, reason)
        self.write_diagnostics()

    def publish_goal(
        self,
        x: float,
        y: float,
        z: float,
        source: str,
        allow_queue: bool = True,
        allow_staging: bool = True,
        stage_meta: dict | None = None,
        update_duplicate_key: bool = True,
    ) -> None:
        requested = {"x": x, "y": y, "z": z}
        if update_duplicate_key and self.is_duplicate_goal(requested, source):
            self.duplicate_goal_ignored_count += 1
            self.write_diagnostics()
            return
        if allow_queue and not self.is_ready_to_forward_goal():
            self.queue_goal(requested, source)
            return
        x, clamped_x = self.clamp(x, self.min_x, self.max_x)
        y, clamped_y = self.clamp(y, self.min_y, self.max_y)
        clamped_distance = False
        distance_xy = None
        if self.max_goal_distance_xy is not None and self.max_goal_distance_xy > 0 and self.last_odom is not None:
            ox = float(self.last_odom.pose.pose.position.x)
            oy = float(self.last_odom.pose.pose.position.y)
            dx = x - ox
            dy = y - oy
            distance_xy = math.hypot(dx, dy)
            if allow_staging and self.staged_goal_should_be_used(distance_xy):
                if clamped_x or clamped_y:
                    self.clamped_count += 1
                if update_duplicate_key:
                    self.last_published_request = {"source": source, **requested}
                    self.last_published_request_wall = time.time()
                self.start_staged_goal(requested, x, y, z, source)
                return
            if distance_xy > self.max_goal_distance_xy:
                scale = self.max_goal_distance_xy / distance_xy
                x = ox + dx * scale
                y = oy + dy * scale
                clamped_distance = True
        if clamped_x or clamped_y or clamped_distance:
            self.clamped_count += 1

        nearest_static_obstacle = self.nearest_static_obstacle(x, y)
        if (
            self.static_obstacle_guard_enabled
            and nearest_static_obstacle is not None
            and nearest_static_obstacle["reject"]
        ):
            self.reject_goal(
                requested,
                x,
                y,
                z,
                source,
                "inside_static_obstacle_inflation_guard",
                nearest_static_obstacle,
            )
            return

        if allow_staging and self.maybe_start_static_path_goal(requested, x, y, z, source):
            if update_duplicate_key:
                self.last_published_request = {"source": source, **requested}
                self.last_published_request_wall = time.time()
            return

        stamp = rospy.Time.now()
        goal = PoseStamped()
        goal.header = Header(stamp=stamp, frame_id=self.frame_id)
        goal.pose.position.x = x
        goal.pose.position.y = y
        goal.pose.position.z = z
        goal.pose.orientation.w = 1.0
        self.goal_pub.publish(goal)
        self.published_goal_count += 1

        now_wall = time.time()
        if self.first_goal_wall is None:
            self.first_goal_wall = now_wall
        self.last_goal_wall = now_wall
        self.last_goal = {
            "source": source,
            "x": x,
            "y": y,
            "z": z,
            "requested": requested,
            "nearest_static_obstacle": nearest_static_obstacle,
            "distance_xy_from_odom": distance_xy,
            "max_goal_distance_xy": self.max_goal_distance_xy,
            "stamp": stamp.to_sec(),
            "clamped": clamped_x or clamped_y or clamped_distance,
            "clamped_by_distance": clamped_distance,
            "stage_meta": stage_meta,
            "ready_snapshot": self.last_ready_snapshot or self.ready_snapshot(),
        }
        if update_duplicate_key:
            self.last_published_request = {"source": source, **requested}
            self.last_published_request_wall = now_wall
        self.publish_target_path(goal, stage_meta)
        self.write_diagnostics()

    def publish_target_path(self, goal: PoseStamped, stage_meta: dict | None = None) -> None:
        visual_goal = goal
        if stage_meta is not None and isinstance(stage_meta.get("final"), dict):
            final = stage_meta["final"]
            visual_goal = PoseStamped()
            visual_goal.header = goal.header
            visual_goal.pose.position.x = float(final["x"])
            visual_goal.pose.position.y = float(final["y"])
            visual_goal.pose.position.z = float(final["z"])
            visual_goal.pose.orientation = goal.pose.orientation

        path = RosPath()
        path.header = Header(stamp=visual_goal.header.stamp, frame_id=self.frame_id)
        if self.last_odom is not None:
            current = PoseStamped()
            current.header = path.header
            current.pose.position.x = self.last_odom.pose.pose.position.x
            current.pose.position.y = self.last_odom.pose.pose.position.y
            current.pose.position.z = self.last_odom.pose.pose.position.z
            current.pose.orientation = self.last_odom.pose.pose.orientation
            path.poses.append(current)
        if self.last_path_goal is not None:
            prev_x, prev_y, prev_z = self.last_path_goal
            jump = math.dist(
                (prev_x, prev_y, prev_z),
                (visual_goal.pose.position.x, visual_goal.pose.position.y, visual_goal.pose.position.z),
            )
            if jump > 1.5:
                # Break the visual trail between unrelated target clicks.
                path.poses = path.poses[:1]
        path.poses.append(visual_goal)
        self.path_pub.publish(path)
        self.last_path_goal = (
            visual_goal.pose.position.x,
            visual_goal.pose.position.y,
            visual_goal.pose.position.z,
        )

    def write_diagnostics(self) -> None:
        if not self.diagnostics_path:
            return
        path = Path(self.diagnostics_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema": "mosim.sunray_ros1.goal4_clicked_goal_adapter.v1",
            "clicked_point_topic": self.clicked_point_topic,
            "nav_goal_topic": self.nav_goal_topic,
            "output_goal_topic": self.output_goal_topic,
            "target_path_topic": self.target_path_topic,
            "mission_ready_topic": self.mission_ready_topic,
            "require_mission_ready": self.require_mission_ready,
            "mission_ready": self.mission_ready,
            "last_mission_ready_age_s": (
                None if self.last_mission_ready_wall is None else time.time() - self.last_mission_ready_wall
            ),
            "odom_topic": self.odom_topic,
            "frame_id": self.frame_id,
            "target_z": self.target_z,
            "use_clicked_z": self.use_clicked_z,
            "enable_clicked_point": self.enable_clicked_point,
            "ready_gate": {
                "enabled": self.ready_gate_enabled,
                "ready_min_z": self.ready_min_z,
                "ready_z_tolerance": self.ready_z_tolerance,
                "ready_max_speed_mps": self.ready_max_speed_mps,
                "ready_max_vz_mps": self.ready_max_vz_mps,
                "ready_max_roll_pitch_deg": self.ready_max_roll_pitch_deg,
                "ready_required_stable_s": self.ready_required_stable_s,
                "ready_odom_timeout_s": self.ready_odom_timeout_s,
                "last_snapshot": self.last_ready_snapshot or self.ready_snapshot(),
            },
            "clicked_point_count": self.clicked_point_count,
            "nav_goal_count": self.nav_goal_count,
            "published_goal_count": self.published_goal_count,
            "rejected_goal_count": self.rejected_goal_count,
            "queued_goal_count": self.queued_goal_count,
            "queue_release_count": self.queue_release_count,
            "duplicate_goal_ignored_count": self.duplicate_goal_ignored_count,
            "clamped_count": self.clamped_count,
            "staged_goal": {
                "enabled": self.staged_goal_enabled,
                "stage_reach_xy_radius_m": self.stage_reach_xy_radius_m,
                "stage_reach_z_tol_m": self.stage_reach_z_tol_m,
                "stage_required_stable_s": self.stage_required_stable_s,
                "stage_max_count": self.stage_max_count,
                "staged_goal_count": self.staged_goal_count,
                "stage_publish_count": self.stage_publish_count,
                "stage_completion_count": self.stage_completion_count,
                "stage_rejected_count": self.stage_rejected_count,
                "active": self.active_staged_goal,
                "last_stage_snapshot": self.last_stage_snapshot,
            },
            "first_goal_wall": self.first_goal_wall,
            "last_goal_wall": self.last_goal_wall,
            "last_goal": self.last_goal,
            "queued_goal": self.queued_goal,
            "last_rejected_goal": self.last_rejected_goal,
            "distance_clamp_enabled": bool(self.max_goal_distance_xy is not None and self.max_goal_distance_xy > 0),
            "static_obstacle_guard": {
                "enabled": self.static_obstacle_guard_enabled,
                "world_file": self.static_obstacle_world_file,
                "obstacle_count": len(self.static_obstacles),
                "default_radius_m": self.static_obstacle_default_radius_m,
                "inflation_m": self.static_obstacle_inflation_m,
                "extra_margin_m": self.static_obstacle_extra_margin_m,
            },
            "static_path_guard": {
                "enabled": self.static_path_guard_enabled,
                "grid_resolution_m": self.static_path_guard_grid_resolution_m,
                "bounds_padding_m": self.static_path_guard_bounds_padding_m,
                "max_waypoints": self.static_path_guard_max_waypoints,
                "max_nodes": self.static_path_guard_max_nodes,
                "last_plan": self.last_path_guard_plan,
            },
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def spin(self) -> None:
        rate = rospy.Rate(10.0)
        while not rospy.is_shutdown():
            self.try_release_queued_goal()
            self.try_advance_staged_goal()
            self.write_diagnostics()
            rate.sleep()
        self.write_diagnostics()


def main() -> None:
    rospy.init_node("mosim_goal4_clicked_goal_adapter")
    ClickedGoalAdapter().spin()


if __name__ == "__main__":
    main()
