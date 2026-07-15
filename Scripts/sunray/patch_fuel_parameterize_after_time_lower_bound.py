#!/usr/bin/env python3
"""Move FUEL time-bound adjustment before B-spline parameterization."""
from __future__ import annotations
import argparse
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("fuel_source_root", type=Path)
    path = ap.parse_args().fuel_source_root.resolve() / "plan_manage/src/planner_manager.cpp"
    text = path.read_text(encoding="utf-8")
    if "[FUEL_TIME_LB] parameterization uses effective dt" in text:
        print("FUEL time-bound ordering patch already applied")
        return 0
    start = text.index('  std::cout << "duration: " << duration')
    loop = text.index('  for (double ts = 0.0', start)
    time_block = '''  double path_length = 0.0;
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

'''
    text = text[:loop] + '  ROS_WARN("[FUEL_TIME_LB] parameterization uses effective dt");\n' + time_block + text[loop:]
    block_start = text.index('  double path_length = 0.0;', loop + len(time_block) + 1)
    block_end = text.index('  bspline_optimizers_[0]->optimize', block_start)
    text = text[:block_start] + text[block_end:]
    path.write_text(text, encoding="utf-8")
    print("Applied FUEL time-bound ordering patch")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
