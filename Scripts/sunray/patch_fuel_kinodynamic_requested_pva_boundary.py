#!/usr/bin/env python3
"""Keep kinodynamic FUEL replans anchored to the requested handoff PVA."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    root = parser.parse_args().fuel_source_root.resolve()
    path = root / "plan_manage/src/planner_manager.cpp"
    text = path.read_text(encoding="utf-8")

    old = """  vector<Eigen::Vector3d> start, end;
  init.getBoundaryStates(2, 0, start, end);
  bspline_optimizers_[0]->setBoundaryStates(start, end);
"""
    new = """  vector<Eigen::Vector3d> start, end;
  init.getBoundaryStates(2, 0, start, end);
  const Eigen::Vector3d candidate_start_pt = start[0];
  const Eigen::Vector3d candidate_start_vel = start[1];
  const Eigen::Vector3d candidate_start_acc = start[2];
  ROS_WARN("[FUEL_KINO_BOUNDARY] candidate_to_request dp=%.6f dv=%.6f da=%.6f",
      (candidate_start_pt - start_pt).norm(),
      (candidate_start_vel - start_vel).norm(),
      (candidate_start_acc - start_acc).norm());
  start[0] = start_pt;
  start[1] = start_vel;
  start[2] = start_acc;
  bspline_optimizers_[0]->setBoundaryStates(start, end);
"""

    if new in text:
        print("FUEL kinodynamic requested-PVA boundary patch already applied")
        return 0
    if text.count(old) != 1:
        raise SystemExit(f"{path}: expected exactly one kinodynamic boundary anchor")

    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print("Applied FUEL kinodynamic requested-PVA boundary patch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
