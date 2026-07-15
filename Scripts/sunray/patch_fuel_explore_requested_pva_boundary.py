#!/usr/bin/env python3
"""Use the requested PVA as the FUEL exploration optimizer boundary."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    parser.add_argument("--revert", action="store_true")
    root = parser.parse_args().fuel_source_root.resolve()
    path = root / "plan_manage/src/planner_manager.cpp"
    text = path.read_text(encoding="utf-8")

    old_boundary = """  vector<Vector3d> start, end;
  tmp_traj.getBoundaryStates(2, 0, start, end);
  bspline_optimizers_[0]->setBoundaryStates(start, end);
  double path_length = 0.0;
"""
    new_boundary = """  vector<Vector3d> start, end;
  tmp_traj.getBoundaryStates(2, 0, start, end);
  ROS_WARN("[FUEL_EXPLORE_BOUNDARY] candidate_to_request dp=%.6f dv=%.6f da=%.6f",
      (start[0] - tour.front()).norm(),
      (start[1] - cur_vel).norm(),
      (start[2] - cur_acc).norm());
  start[0] = tour.front();
  start[1] = cur_vel;
  start[2] = cur_acc;
  end[1].setZero();
  end[2].setZero();
  bspline_optimizers_[0]->setBoundaryStates(start, end);
  double path_length = 0.0;
"""

    old_reconstruct = """  vector<Eigen::Vector3d> pva_start, pva_end;
  tmp_traj.getBoundaryStates(2, 2, pva_start, pva_end);
  pva_start[0] = tour.front();
  pva_start[1] = cur_vel;
  pva_start[2] = cur_acc;
  pva_end[1].setZero();
  pva_end[2].setZero();
  enforceCubicPvaBoundary(ctrl_pts, dt, pva_start, pva_end);
"""
    new_reconstruct = """  enforceCubicPvaBoundary(ctrl_pts, dt, start, end);
"""

    if parser.parse_args().revert:
        if new_boundary in text:
            text = text.replace(new_boundary, old_boundary, 1)
        if new_reconstruct in text:
            text = text.replace(new_reconstruct, old_reconstruct, 1)
        path.write_text(text, encoding="utf-8")
        print("Reverted FUEL exploration requested-PVA boundary experiment")
        return 0

    if new_boundary in text and new_reconstruct in text:
        print("FUEL exploration requested-PVA boundary patch already applied")
        return 0
    if text.count(old_boundary) != 1:
        raise SystemExit(f"{path}: expected exactly one exploration boundary anchor")
    if text.count(old_reconstruct) != 1:
        raise SystemExit(f"{path}: expected exactly one exploration reconstruction anchor")

    text = text.replace(old_boundary, new_boundary, 1)
    text = text.replace(old_reconstruct, new_reconstruct, 1)
    path.write_text(text, encoding="utf-8")
    print("Applied FUEL exploration requested-PVA boundary patch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
