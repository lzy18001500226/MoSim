#!/usr/bin/env python3
"""Restore exact cubic B-spline P/V/A boundaries after FUEL optimization."""

from __future__ import annotations

import argparse
from pathlib import Path


HELPER_ANCHOR = "namespace fast_planner {\n"
OLD_HELPER = r'''namespace fast_planner {
namespace {
void enforceCubicPvaBoundary(Eigen::MatrixXd& ctrl_pts, const double dt,
    const vector<Eigen::Vector3d>& start, const vector<Eigen::Vector3d>& end) {
  if (ctrl_pts.rows() < 6 || start.size() < 3 || end.size() < 3 || dt <= 0.0) return;
  const double dt2 = dt * dt;
  ctrl_pts.row(0) = start[0] - start[1] * dt + start[2] * dt2 / 6.0;
  ctrl_pts.row(1) = start[0] - start[2] * dt2 / 3.0;
  ctrl_pts.row(2) = start[0] + start[1] * dt + start[2] * dt2 / 6.0;
  const int n = ctrl_pts.rows();
  ctrl_pts.row(n - 3) = end[0] - end[1] * dt + end[2] * dt2 / 6.0;
  ctrl_pts.row(n - 2) = end[0] - end[2] * dt2 / 3.0;
  ctrl_pts.row(n - 1) = end[0] + end[1] * dt + end[2] * dt2 / 6.0;
}
}  // namespace
'''
HELPER = r'''namespace fast_planner {
namespace {
void enforceCubicPvaBoundary(Eigen::MatrixXd& ctrl_pts, const double dt,
    const vector<Eigen::Vector3d>& start, const vector<Eigen::Vector3d>& end) {
  if (ctrl_pts.rows() < 6 || start.size() < 3 || end.size() < 3 || dt <= 0.0) return;
  const double dt2 = dt * dt;
  ctrl_pts.row(0) = start[0] - start[1] * dt + start[2] * dt2 / 3.0;
  ctrl_pts.row(1) = start[0] - start[2] * dt2 / 6.0;
  ctrl_pts.row(2) = start[0] + start[1] * dt + start[2] * dt2 / 3.0;
  const int n = ctrl_pts.rows();
  ctrl_pts.row(n - 3) = end[0] - end[1] * dt + end[2] * dt2 / 3.0;
  ctrl_pts.row(n - 2) = end[0] - end[2] * dt2 / 6.0;
  ctrl_pts.row(n - 1) = end[0] + end[1] * dt + end[2] * dt2 / 3.0;
}
}  // namespace
'''

CALLS = (
    (
        "  bspline_optimizers_[0]->optimize(ctrl_pts, ts, cost_function, 1, 1);\n"
        "  NonUniformBspline position_traj(ctrl_pts, pp_.bspline_degree_, ts);\n",
        "  bspline_optimizers_[0]->optimize(ctrl_pts, ts, cost_function, 1, 1);\n"
        "  enforceCubicPvaBoundary(ctrl_pts, ts, start, end);\n"
        "  NonUniformBspline position_traj(ctrl_pts, pp_.bspline_degree_, ts);\n",
    ),
    (
        "  bspline_optimizers_[0]->optimize(ctrl_pts, dt, cost_func, 1, 1);\n"
        "  NonUniformBspline position_traj(ctrl_pts, pp_.bspline_degree_, dt);\n",
        "  bspline_optimizers_[0]->optimize(ctrl_pts, dt, cost_func, 1, 1);\n"
        "  vector<Eigen::Vector3d> pva_start, pva_end;\n"
        "  tmp_traj.getBoundaryStates(2, 2, pva_start, pva_end);\n"
        "  pva_start[0] = tour.front();\n"
        "  pva_start[1] = cur_vel;\n"
        "  pva_start[2] = cur_acc;\n"
        "  pva_end[1].setZero();\n"
        "  pva_end[2].setZero();\n"
        "  enforceCubicPvaBoundary(ctrl_pts, dt, pva_start, pva_end);\n"
        "  NonUniformBspline position_traj(ctrl_pts, pp_.bspline_degree_, dt);\n",
    ),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    root = parser.parse_args().fuel_source_root.resolve()
    path = root / "plan_manage/src/planner_manager.cpp"
    text = path.read_text(encoding="utf-8")
    if OLD_HELPER in text:
        text = text.replace(OLD_HELPER, HELPER, 1)
    text = text.replace(
        "  vector<Eigen::Vector3d> exact_start = {cur_vel, cur_acc};\n"
        "  vector<Eigen::Vector3d> pva_start, pva_end;\n"
        "  tmp_traj.getBoundaryStates(2, 2, pva_start, pva_end);\n"
        "  pva_start[1] = exact_start[0];\n"
        "  pva_start[2] = exact_start[1];\n",
        "  vector<Eigen::Vector3d> pva_start, pva_end;\n"
        "  tmp_traj.getBoundaryStates(2, 2, pva_start, pva_end);\n"
        "  pva_start[0] = tour.front();\n"
        "  pva_start[1] = cur_vel;\n"
        "  pva_start[2] = cur_acc;\n"
        "  pva_end[1].setZero();\n"
        "  pva_end[2].setZero();\n",
    )
    if "void enforceCubicPvaBoundary" not in text:
        if text.count(HELPER_ANCHOR) != 1:
            raise SystemExit(f"{path}: namespace anchor is ambiguous")
        text = text.replace(HELPER_ANCHOR, HELPER, 1)
    for old, new in CALLS:
        if new in text:
            continue
        if text.count(old) != 1:
            raise SystemExit(f"{path}: expected one optimizer call, found {text.count(old)}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
    print("Applied exact cubic P/V/A boundary patch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
