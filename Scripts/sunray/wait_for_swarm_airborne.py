#!/usr/bin/env python3

import argparse
import time

import rospy
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State


def parse_args():
    parser = argparse.ArgumentParser(description="Wait until every MAVROS UAV is connected, armed, and airborne.")
    parser.add_argument("--uav-num", type=int, default=3)
    parser.add_argument("--min-z", type=float, default=0.8)
    parser.add_argument("--timeout-s", type=float, default=300.0)
    parser.add_argument("--max-sample-age-s", type=float, default=1.0)
    return parser.parse_args(rospy.myargv()[1:])


def main():
    args = parse_args()
    rospy.init_node("mosim_wait_for_swarm_airborne", anonymous=True, disable_signals=True)

    states = {}
    poses = {}

    def state_callback(message, uav_id):
        states[uav_id] = (message, time.monotonic())

    def pose_callback(message, uav_id):
        poses[uav_id] = (message, time.monotonic())

    subscribers = []
    for uav_id in range(1, args.uav_num + 1):
        subscribers.append(
            rospy.Subscriber(
                f"/uav{uav_id}/mavros/state",
                State,
                state_callback,
                callback_args=uav_id,
                queue_size=1,
            )
        )
        subscribers.append(
            rospy.Subscriber(
                f"/uav{uav_id}/mavros/local_position/pose",
                PoseStamped,
                pose_callback,
                callback_args=uav_id,
                queue_size=1,
            )
        )

    deadline = time.monotonic() + args.timeout_s
    rate = rospy.Rate(10)
    while not rospy.is_shutdown() and time.monotonic() < deadline:
        now = time.monotonic()
        ready = True
        for uav_id in range(1, args.uav_num + 1):
            state_sample = states.get(uav_id)
            pose_sample = poses.get(uav_id)
            if state_sample is None or pose_sample is None:
                ready = False
                break
            state, state_time = state_sample
            pose, pose_time = pose_sample
            if now - state_time > args.max_sample_age_s or now - pose_time > args.max_sample_age_s:
                ready = False
                break
            if not state.connected or not state.armed or pose.pose.position.z <= args.min_z:
                ready = False
                break
        if ready:
            summary = ", ".join(
                f"uav{uav_id}:z={poses[uav_id][0].pose.position.z:.3f}"
                for uav_id in range(1, args.uav_num + 1)
            )
            rospy.loginfo("Swarm airborne gate passed: %s", summary)
            return 0
        rate.sleep()

    now = time.monotonic()
    diagnostics = []
    for uav_id in range(1, args.uav_num + 1):
        state_sample = states.get(uav_id)
        pose_sample = poses.get(uav_id)
        if state_sample is None:
            state_text = "state=missing"
        else:
            state, state_time = state_sample
            state_text = (
                f"connected={state.connected},armed={state.armed},"
                f"state_age={now - state_time:.2f}s"
            )
        if pose_sample is None:
            pose_text = "pose=missing"
        else:
            pose, pose_time = pose_sample
            pose_text = f"z={pose.pose.position.z:.3f},pose_age={now - pose_time:.2f}s"
        diagnostics.append(f"uav{uav_id}[{state_text},{pose_text}]")
    rospy.logerr(
        "Swarm airborne gate timed out after %.1fs (uav_num=%d, min_z=%.3f): %s",
        args.timeout_s,
        args.uav_num,
        args.min_z,
        "; ".join(diagnostics),
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
