#!/usr/bin/env python3
"""Log the exact FUEL B-spline contract on both sides of the ROS message."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str, path: Path) -> str:
    if new in text:
        return text
    if text.count(old) != 1:
        raise SystemExit(f"{path}: expected one diagnostic anchor, found {text.count(old)}")
    return text.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    root = parser.parse_args().fuel_source_root.resolve()
    fsm = root / "exploration_manager/src/fast_exploration_fsm.cpp"
    server = root / "plan_manage/src/traj_server.cpp"

    text = fsm.read_text(encoding="utf-8")
    old = """    Eigen::VectorXd knots = info->position_traj_.getKnot();
    for (int i = 0; i < knots.rows(); ++i) {
      bspline.knots.push_back(knots(i));
    }
"""
    new = old + """    const Eigen::Vector3d wire_start = info->position_traj_.evaluateDeBoorT(0.0);
    const Eigen::Vector3d wire_end =
        info->position_traj_.evaluateDeBoorT(info->position_traj_.getTimeSum());
    ROS_WARN("[FUEL_BSPLINE_WIRE_TX] id=%d duration=%.9f knots=(%.9f,%.9f) "
             "start=(%.9f,%.9f,%.9f) end=(%.9f,%.9f,%.9f)",
        info->traj_id_, info->position_traj_.getTimeSum(), knots(0),
        knots(knots.rows() - 1), wire_start.x(), wire_start.y(), wire_start.z(),
        wire_end.x(), wire_end.y(), wire_end.z());
"""
    fsm.write_text(replace_once(text, old, new, fsm), encoding="utf-8")

    text = server.read_text(encoding="utf-8")
    old = """  traj_duration_ = traj_[0].getTimeSum();

  receive_traj_ = true;
"""
    new = """  traj_duration_ = traj_[0].getTimeSum();
  const Eigen::Vector3d wire_start = traj_[0].evaluateDeBoorT(0.0);
  const Eigen::Vector3d wire_end = traj_[0].evaluateDeBoorT(traj_duration_);
  ROS_WARN("[FUEL_BSPLINE_WIRE_RX] id=%d duration=%.9f knots=(%.9f,%.9f) "
           "start=(%.9f,%.9f,%.9f) end=(%.9f,%.9f,%.9f) "
           "msg_start=%.9f receive=%.9f effective_start=%.9f",
      traj_id_, traj_duration_, knots(0), knots(knots.rows() - 1),
      wire_start.x(), wire_start.y(), wire_start.z(), wire_end.x(), wire_end.y(),
      wire_end.z(), msg->start_time.toSec(), received_time.toSec(), start_time_.toSec());

  receive_traj_ = true;
"""
    server.write_text(replace_once(text, old, new, server), encoding="utf-8")
    print("Applied FUEL B-spline wire diagnostics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
