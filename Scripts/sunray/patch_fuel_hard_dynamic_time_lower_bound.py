#!/usr/bin/env python3
"""Prevent FUEL MINTIME from shrinking exploration splines below physics."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str, path: Path) -> str:
    if new in text:
        return text
    if text.count(old) != 1:
        raise SystemExit(f"{path}: expected one time-bound anchor, found {text.count(old)}")
    return text.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    root = parser.parse_args().fuel_source_root.resolve()
    manager = root / "plan_manage/src/planner_manager.cpp"
    optimizer = root / "bspline_opt/src/bspline_optimizer.cpp"

    text = manager.read_text(encoding="utf-8")
    old = """  bspline_optimizers_[0]->setBoundaryStates(start, end);
  if (time_lb > 0) bspline_optimizers_[0]->setTimeLowerBound(time_lb);

  bspline_optimizers_[0]->optimize(ctrl_pts, dt, cost_func, 1, 1);
"""
    new = """  bspline_optimizers_[0]->setBoundaryStates(start, end);
  double path_length = 0.0;
  for (int i = 0; i < pt_num - 1; ++i)
    path_length += (tour[i + 1] - tour[i]).norm();
  const double accel_distance = pp_.max_vel_ * pp_.max_vel_ / pp_.max_acc_;
  const double dynamic_time_lb = path_length <= accel_distance
      ? 2.0 * sqrt(path_length / pp_.max_acc_)
      : 2.0 * pp_.max_vel_ / pp_.max_acc_ +
            (path_length - accel_distance) / pp_.max_vel_;
  const double effective_time_lb = std::max(time_lb, dynamic_time_lb);
  bspline_optimizers_[0]->setTimeLowerBound(effective_time_lb);
  const double hard_dt_lb = effective_time_lb / double(seg_num);
  if (dt < hard_dt_lb) {
    ROS_WARN("[FUEL_TIME_LB] raise_initial_dt %.6f->%.6f", dt, hard_dt_lb);
    dt = hard_dt_lb;
  }
  ROS_WARN("[FUEL_TIME_LB] path_length=%.6f caller_lb=%.6f dynamic_lb=%.6f "
           "effective_lb=%.6f initial_duration=%.6f initial_dt=%.6f segments=%d",
      path_length, time_lb, dynamic_time_lb, effective_time_lb, duration, dt, seg_num);

  bspline_optimizers_[0]->optimize(ctrl_pts, dt, cost_func, 1, 1);
"""
    prior = new.replace(
        "  const double hard_dt_lb = effective_time_lb / double(seg_num);\n"
        "  if (dt < hard_dt_lb) {\n"
        "    ROS_WARN(\"[FUEL_TIME_LB] raise_initial_dt %.6f->%.6f\", dt, hard_dt_lb);\n"
        "    dt = hard_dt_lb;\n"
        "  }\n",
        "",
    )
    if prior in text and new not in text:
        text = text.replace(prior, new, 1)
    else:
        text = replace_once(text, old, new, manager)
    manager.write_text(text, encoding="utf-8")

    text = optimizer.read_text(encoding="utf-8")
    old = """    if (optimize_time_) {
      lb[variable_num_ - 1] = 0.0;
      ub[variable_num_ - 1] = 5.0;
    }
"""
    new = """    if (optimize_time_) {
      const int segment_count = std::max(1, point_num_ - order_);
      const double hard_dt_lb = time_lb_ > 0.0
          ? time_lb_ / double(segment_count)
          : 1e-3;
      lb[variable_num_ - 1] = hard_dt_lb;
      ub[variable_num_ - 1] = std::max(5.0, hard_dt_lb);
    }
"""
    optimizer.write_text(replace_once(text, old, new, optimizer), encoding="utf-8")
    print("Applied FUEL hard dynamic time lower bound")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
