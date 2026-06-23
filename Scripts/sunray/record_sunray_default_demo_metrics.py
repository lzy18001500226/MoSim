#!/usr/bin/env python3
"""Record and score upstream Sunray takeoff-hover-land demo trajectory."""

import argparse
import csv
import json
import math
import time
from pathlib import Path

import rospy
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import PoseStamped


class Recorder:
    def __init__(self, target):
        self.target = target
        self.truth = []
        self.local_pose = []
        self.start_wall = time.time()

    def _stamp(self):
        now = rospy.Time.now()
        if now.to_sec() > 0:
            return now.to_sec()
        return time.time() - self.start_wall

    def on_model_states(self, msg):
        try:
            idx = list(msg.name).index("uav1")
        except ValueError:
            return
        pose = msg.pose[idx]
        twist = msg.twist[idx]
        self.truth.append(
            {
                "t": self._stamp(),
                "x": pose.position.x,
                "y": pose.position.y,
                "z": pose.position.z,
                "vx": twist.linear.x,
                "vy": twist.linear.y,
                "vz": twist.linear.z,
            }
        )

    def on_local_pose(self, msg):
        p = msg.pose.position
        self.local_pose.append({"t": self._stamp(), "x": p.x, "y": p.y, "z": p.z})

    def write_outputs(self, result_dir):
        result_dir.mkdir(parents=True, exist_ok=True)
        (result_dir / "gazebo_truth_uav1.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in self.truth),
            encoding="utf-8",
        )
        (result_dir / "mavros_local_position_pose.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in self.local_pose),
            encoding="utf-8",
        )

        with (result_dir / "gazebo_truth_uav1.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["t", "x", "y", "z", "vx", "vy", "vz"])
            writer.writeheader()
            writer.writerows(self.truth)

        metrics = self._metrics()
        (result_dir / "SUNRAY_DEFAULT_CONTROL_METRICS.json").write_text(
            json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        self._plot(result_dir, metrics)
        print(json.dumps(metrics, ensure_ascii=False, indent=2))

    def _metrics(self):
        samples = self.truth
        if not samples:
            return {
                "schema": "mosim.sunray_default_control_metrics.v1",
                "status": "blocked_no_truth_samples",
                "truth_samples": 0,
            }

        target_x, target_y, target_z = self.target
        zs = [r["z"] for r in samples]
        max_z = max(zs)
        airborne = [r for r in samples if r["z"] > 0.20]
        hover = [r for r in samples if r["z"] > 0.75]

        def rmse(rows, fn):
            if not rows:
                return None
            return math.sqrt(sum(fn(r) ** 2 for r in rows) / len(rows))

        def max_abs(rows, fn):
            if not rows:
                return None
            return max(abs(fn(r)) for r in rows)

        def max_norm_xy(rows):
            if not rows:
                return None
            return max(math.hypot(r["x"] - target_x, r["y"] - target_y) for r in rows)

        final = samples[-1]
        payload = {
            "schema": "mosim.sunray_default_control_metrics.v1",
            "status": "passed_recorded",
            "target": {"x": target_x, "y": target_y, "z": target_z},
            "truth_samples": len(samples),
            "local_pose_samples": len(self.local_pose),
            "duration_s": samples[-1]["t"] - samples[0]["t"] if len(samples) >= 2 else 0.0,
            "max_z_m": max_z,
            "final_position_m": {"x": final["x"], "y": final["y"], "z": final["z"]},
            "final_xy_error_m": math.hypot(final["x"] - target_x, final["y"] - target_y),
            "airborne_sample_count": len(airborne),
            "hover_sample_count": len(hover),
            "airborne_xy_rmse_m": rmse(
                airborne, lambda r: math.hypot(r["x"] - target_x, r["y"] - target_y)
            ),
            "airborne_max_xy_error_m": max_norm_xy(airborne),
            "hover_z_rmse_m": rmse(hover, lambda r: r["z"] - target_z),
            "hover_max_abs_z_error_m": max_abs(hover, lambda r: r["z"] - target_z),
            "hover_xy_rmse_m": rmse(
                hover, lambda r: math.hypot(r["x"] - target_x, r["y"] - target_y)
            ),
            "hover_max_xy_error_m": max_norm_xy(hover),
            "max_speed_xy_mps": max(
                math.hypot(r["vx"], r["vy"]) for r in samples if "vx" in r
            ),
            "claim_boundary": [
                "Metrics are for upstream Sunray ROS1/PX4 demo_id=1 takeoff-hover-land.",
                "The default sunray150 launch does not include MID360 PointCloud2 topics.",
            ],
        }
        return payload

    def _plot(self, result_dir, metrics):
        if not self.truth:
            return
        truth = list(self.truth)
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        xs = [r["x"] for r in truth]
        ys = [r["y"] for r in truth]
        zs = [r["z"] for r in truth]
        ts = [r["t"] - truth[0]["t"] for r in truth]

        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        axes[0].plot(xs, ys, label="Gazebo truth")
        axes[0].scatter([self.target[0]], [self.target[1]], s=30, label="target xy")
        axes[0].set_xlabel("x [m]")
        axes[0].set_ylabel("y [m]")
        axes[0].set_title("Sunray default demo XY trajectory")
        axes[0].axis("equal")
        axes[0].grid(True)
        axes[0].legend()

        axes[1].plot(ts, zs, label="z")
        axes[1].axhline(self.target[2], color="r", linestyle="--", label="target z")
        axes[1].set_xlabel("t [s]")
        axes[1].set_ylabel("z [m]")
        axes[1].set_title("Altitude")
        axes[1].grid(True)
        axes[1].legend()

        fig.suptitle(
            "hover z RMSE="
            + str(metrics.get("hover_z_rmse_m"))
            + ", hover XY RMSE="
            + str(metrics.get("hover_xy_rmse_m"))
        )
        fig.tight_layout()
        fig.savefig(result_dir / "sunray_default_demo_trajectory.png", dpi=160)
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--duration", type=float, default=45.0)
    parser.add_argument("--target-x", type=float, default=1.0)
    parser.add_argument("--target-y", type=float, default=1.0)
    parser.add_argument("--target-z", type=float, default=1.0)
    args = parser.parse_args()

    rospy.init_node("mosim_sunray_default_demo_metrics_recorder", anonymous=True)
    recorder = Recorder((args.target_x, args.target_y, args.target_z))
    rospy.Subscriber("/gazebo/model_states", ModelStates, recorder.on_model_states, queue_size=20)
    rospy.Subscriber(
        "/uav1/mavros/local_position/pose",
        PoseStamped,
        recorder.on_local_pose,
        queue_size=20,
    )
    deadline = time.time() + args.duration
    rate = rospy.Rate(20)
    while not rospy.is_shutdown() and time.time() < deadline:
        rate.sleep()
    recorder.write_outputs(Path(args.result_dir))


if __name__ == "__main__":
    main()
