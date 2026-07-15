#!/usr/bin/env python3
"""Bridge uav_frontier exploration goals to MoSim PositionCommand.

The upstream frontier server publishes PoseStamped goals and expects a
point_reached Bool feedback. This bridge keeps that interface but sends the
goal through the existing MoSim PositionCommand safety adapter instead of
letting the upstream trajectory stack command px4ctrl directly.
"""

from __future__ import annotations

import argparse
import json
import math
import time

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from quadrotor_msgs.msg import PositionCommand
from std_msgs.msg import Bool
from std_srvs.srv import SetBool, SetBoolRequest


class UavFrontierGoalBridge:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.start_wall = time.time()
        self.current_goal: PoseStamped | None = None
        self.current_goal_seq = 0
        self.last_odom: Odometry | None = None
        self.reached_since: float | None = None
        self.reached_published_for_seq = 0
        self.exploration_enabled = False
        self.trigger_count = 0
        self.goal_count = 0
        self.cmd_count = 0
        self.point_reached_count = 0
        self.rejected_goal_count = 0
        self.last_reject_reason = ""

        self.cmd_pub = rospy.Publisher(args.raw_position_cmd_topic, PositionCommand, queue_size=20)
        self.point_reached_pub = rospy.Publisher(args.point_reached_topic, Bool, queue_size=5)
        rospy.Subscriber(args.goal_topic, PoseStamped, self.on_goal, queue_size=10)
        rospy.Subscriber(args.odom_topic, Odometry, self.on_odom, queue_size=50)
        rospy.Subscriber(args.trigger_topic, PoseStamped, self.on_trigger, queue_size=5)

    def on_trigger(self, _msg: PoseStamped) -> None:
        self.trigger_count += 1
        self.enable_exploration()

    def enable_exploration(self) -> None:
        if self.exploration_enabled:
            return
        try:
            rospy.wait_for_service(self.args.toggle_service, timeout=self.args.toggle_timeout_s)
            proxy = rospy.ServiceProxy(self.args.toggle_service, SetBool)
            resp = proxy(SetBoolRequest(data=True))
            self.exploration_enabled = bool(resp.success)
            if not resp.success:
                rospy.logwarn("uav_frontier toggle service returned success=false: %s", resp.message)
        except Exception as exc:  # noqa: BLE001 - ROS service exceptions vary.
            rospy.logwarn("Failed to enable uav_frontier exploration: %s", exc)

    def on_odom(self, msg: Odometry) -> None:
        self.last_odom = msg

    def on_goal(self, msg: PoseStamped) -> None:
        if not self.goal_inside_bounds(msg):
            self.rejected_goal_count += 1
            return
        self.current_goal = msg
        self.current_goal_seq += 1
        self.goal_count += 1
        self.reached_since = None

    def goal_inside_bounds(self, msg: PoseStamped) -> bool:
        p = msg.pose.position
        z = self.output_z(msg)
        checks = [
            (self.args.min_x <= p.x <= self.args.max_x, "x_out_of_bounds"),
            (self.args.min_y <= p.y <= self.args.max_y, "y_out_of_bounds"),
            (self.args.min_z <= z <= self.args.max_z, "z_out_of_bounds"),
        ]
        for ok, reason in checks:
            if not ok:
                self.last_reject_reason = reason
                rospy.logwarn("Rejecting uav_frontier goal: %s x=%.3f y=%.3f z=%.3f", reason, p.x, p.y, z)
                return False
        self.last_reject_reason = ""
        return True

    def output_z(self, msg: PoseStamped) -> float:
        if self.args.fixed_z > 0.0:
            return self.args.fixed_z
        return max(self.args.min_z, min(self.args.max_z, float(msg.pose.position.z)))

    def goal_error(self) -> tuple[float, float, float] | None:
        if self.current_goal is None or self.last_odom is None:
            return None
        gp = self.current_goal.pose.position
        op = self.last_odom.pose.pose.position
        dz = float(op.z) - self.output_z(self.current_goal)
        dxy = math.hypot(float(op.x) - float(gp.x), float(op.y) - float(gp.y))
        dxyz = math.sqrt(dxy * dxy + dz * dz)
        return dxy, abs(dz), dxyz

    def publish_cmd(self) -> None:
        if self.current_goal is None:
            return
        p = self.current_goal.pose.position
        msg = PositionCommand()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.args.frame_id
        msg.trajectory_flag = PositionCommand.TRAJECTORY_STATUS_READY
        msg.trajectory_id = self.current_goal_seq
        msg.position.x = float(p.x)
        msg.position.y = float(p.y)
        msg.position.z = self.output_z(self.current_goal)
        msg.velocity.x = 0.0
        msg.velocity.y = 0.0
        msg.velocity.z = 0.0
        msg.acceleration.x = 0.0
        msg.acceleration.y = 0.0
        msg.acceleration.z = 0.0
        msg.jerk.x = 0.0
        msg.jerk.y = 0.0
        msg.jerk.z = 0.0
        msg.yaw = 0.0
        msg.yaw_dot = 0.0
        msg.kx = [self.args.kx_xy, self.args.kx_xy, self.args.kx_z]
        msg.kv = [self.args.kv_xy, self.args.kv_xy, self.args.kv_z]
        self.cmd_pub.publish(msg)
        self.cmd_count += 1

    def update_reached(self) -> None:
        err = self.goal_error()
        if err is None or self.current_goal_seq == self.reached_published_for_seq:
            return
        dxy, dz, _dxyz = err
        if dxy <= self.args.reached_xy_m and dz <= self.args.reached_z_m:
            if self.reached_since is None:
                self.reached_since = time.time()
            if time.time() - self.reached_since >= self.args.reached_hold_s:
                self.point_reached_pub.publish(Bool(data=True))
                self.point_reached_count += 1
                self.reached_published_for_seq = self.current_goal_seq
                self.reached_since = None
        else:
            self.reached_since = None

    def write_summary(self) -> None:
        if not self.args.summary_json:
            return
        payload = {
            "schema": "mosim.uav_frontier_goal_bridge_summary.v1",
            "duration_wall_s": round(time.time() - self.start_wall, 3),
            "topics": {
                "goal_topic": self.args.goal_topic,
                "raw_position_cmd_topic": self.args.raw_position_cmd_topic,
                "point_reached_topic": self.args.point_reached_topic,
                "odom_topic": self.args.odom_topic,
                "toggle_service": self.args.toggle_service,
            },
            "counts": {
                "trigger": self.trigger_count,
                "goal": self.goal_count,
                "cmd": self.cmd_count,
                "point_reached": self.point_reached_count,
                "rejected_goal": self.rejected_goal_count,
            },
            "exploration_enabled": self.exploration_enabled,
            "last_reject_reason": self.last_reject_reason,
            "current_goal_seq": self.current_goal_seq,
        }
        with open(self.args.summary_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def spin(self) -> None:
        rate = rospy.Rate(self.args.rate_hz)
        try:
            while not rospy.is_shutdown():
                if self.args.auto_enable and not self.exploration_enabled:
                    self.enable_exploration()
                self.publish_cmd()
                self.update_reached()
                rate.sleep()
        finally:
            self.write_summary()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal-topic", default="/uav_frontier/exploration/goal")
    parser.add_argument("--raw-position-cmd-topic", default="/uav_frontier/position_cmd_raw")
    parser.add_argument("--point-reached-topic", default="/uav_frontier/exploration/point_reached")
    parser.add_argument("--odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--trigger-topic", default="/traj_start_trigger")
    parser.add_argument("--toggle-service", default="/uav_frontier/exploration/toggle")
    parser.add_argument("--toggle-timeout-s", type=float, default=2.0)
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--rate-hz", type=float, default=30.0)
    parser.add_argument("--fixed-z", type=float, default=1.2)
    parser.add_argument("--min-z", type=float, default=0.9)
    parser.add_argument("--max-z", type=float, default=1.6)
    parser.add_argument("--min-x", type=float, default=-98.40496)
    parser.add_argument("--max-x", type=float, default=77.25491)
    parser.add_argument("--min-y", type=float, default=-51.36291)
    parser.add_argument("--max-y", type=float, default=12.63665)
    parser.add_argument("--reached-xy-m", type=float, default=0.8)
    parser.add_argument("--reached-z-m", type=float, default=0.2)
    parser.add_argument("--reached-hold-s", type=float, default=0.8)
    parser.add_argument("--kx-xy", type=float, default=5.7)
    parser.add_argument("--kx-z", type=float, default=6.2)
    parser.add_argument("--kv-xy", type=float, default=3.4)
    parser.add_argument("--kv-z", type=float, default=4.0)
    parser.add_argument("--auto-enable", action="store_true")
    parser.add_argument("--summary-json", default="")
    return parser.parse_args(rospy.myargv()[1:])


def main() -> None:
    args = parse_args()
    rospy.init_node("uav_frontier_goal_bridge", anonymous=False)
    UavFrontierGoalBridge(args).spin()


if __name__ == "__main__":
    main()
