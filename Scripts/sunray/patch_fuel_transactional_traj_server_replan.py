#!/usr/bin/env python3
"""Keep the accepted FUEL trajectory active until a replacement arrives."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    root = parser.parse_args().fuel_source_root.resolve()
    path = root / "plan_manage/src/traj_server.cpp"
    text = path.read_text(encoding="utf-8")

    old = """void replanCallback(std_msgs::Empty msg) {
  // Informed of new replan, end the current traj after some time
  const double time_out = 0.3;
  ros::Time time_now = ros::Time::now();
  double t_stop = (time_now - start_time_).toSec() + time_out + replan_time_;
  traj_duration_ = min(t_stop, traj_duration_);
}
"""
    new = """void replanCallback(std_msgs::Empty msg) {
  // A replan request is not a trajectory commit. Keep executing the accepted
  // spline until a validated replacement arrives through bsplineCallback().
  ROS_WARN_THROTTLE(1.0,
      "[FUEL_TRAJ_TXN] replan requested; retaining active trajectory id=%d duration=%.6f",
      traj_id_, traj_duration_);
}
"""
    if new in text:
        print("FUEL transactional traj_server replan patch already applied")
        return 0
    if text.count(old) != 1:
        raise SystemExit(f"{path}: expected one replan callback anchor, found {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("Applied FUEL transactional traj_server replan patch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
