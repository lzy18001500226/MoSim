#!/usr/bin/env python3
"""Retry FUEL exploration trajectory generation with a longer uniform time step."""

from __future__ import annotations

import argparse
from pathlib import Path


FUNCTION_START = "bool FastPlannerManager::planExploreTraj("
BLOCK_START = "  Eigen::MatrixXd ctrl_pts;\n"
BLOCK_END = "  local_data_.position_traj_ = position_traj;\n"

REPLACEMENT = r'''  Eigen::MatrixXd ctrl_pts;
  NonUniformBspline position_traj;
  bool dynamic_feasible = false;
  double candidate_dt = dt;
  const int retry_count = std::max(1, pp_.dynamic_feasibility_max_iterations_);
  for (int retry = 0; retry < retry_count && ros::ok(); ++retry) {
    NonUniformBspline::parameterizeToBspline(
        candidate_dt, points, boundary_deri, pp_.bspline_degree_, ctrl_pts);
    NonUniformBspline tmp_traj(ctrl_pts, pp_.bspline_degree_, candidate_dt);

    int cost_func = BsplineOptimizer::NORMAL_PHASE;
    // Let the first candidate use FUEL's minimum-time objective. Recovery
    // candidates must keep the requested longer time scale; otherwise the
    // optimizer shortens dt through its reference argument and defeats retry.
    if (pp_.min_time_ && retry == 0) cost_func |= BsplineOptimizer::MINTIME;

    vector<Vector3d> start, end;
    tmp_traj.getBoundaryStates(2, 0, start, end);
    ROS_WARN("[FUEL_EXPLORE_BOUNDARY] retry=%d candidate_to_request "
             "dp=%.6f dv=%.6f da=%.6f dt=%.6f",
        retry, (start[0] - tour.front()).norm(),
        (start[1] - cur_vel).norm(), (start[2] - cur_acc).norm(), candidate_dt);
    start[0] = tour.front();
    start[1] = cur_vel;
    start[2] = cur_acc;
    bspline_optimizers_[0]->setBoundaryStates(start, end);
    bspline_optimizers_[0]->setTimeLowerBound(effective_time_lb);
    const double requested_dt = candidate_dt;
    bspline_optimizers_[0]->optimize(ctrl_pts, candidate_dt, cost_func, 1, 1);

    const double optimized_dt = candidate_dt;
    const double dt2 = optimized_dt * optimized_dt;
    ctrl_pts.row(0) = start[0] - start[1] * optimized_dt + start[2] * dt2 / 3.0;
    ctrl_pts.row(1) = start[0] - start[2] * dt2 / 6.0;
    ctrl_pts.row(2) = start[0] + start[1] * optimized_dt + start[2] * dt2 / 3.0;
    position_traj.setUniformBspline(ctrl_pts, pp_.bspline_degree_, optimized_dt);
    if (enforceDynamicFeasibility(position_traj, "planExploreTraj")) {
      dynamic_feasible = true;
      break;
    }

    const double next_dt = candidate_dt * 1.15;
    ROS_WARN("[FUEL_EXPLORE_RETRY] retry=%d infeasible dt=%.6f next_dt=%.6f",
        retry, candidate_dt, next_dt);
    candidate_dt = requested_dt * 1.15;
  }
  if (!dynamic_feasible) {
    ROS_ERROR("[FUEL_DYN_FEAS] Rejecting exploration trajectory after %d regenerated candidates",
        retry_count);
    return false;
  }
  local_data_.position_traj_ = position_traj;
'''

CALLER_RETRY_MARKER = "    const bool caller_regenerates = std::string(source) == \"planExploreTraj\";\n"
CALLER_RETRY_INSERT = "    if (caller_regenerates) return false;\n"


def apply(root: Path) -> None:
    path = root / "plan_manage/src/planner_manager.cpp"
    text = path.read_text(encoding="utf-8")
    function = text.find(FUNCTION_START)
    if function < 0:
        raise SystemExit("planExploreTraj function not found")
    start = text.find(BLOCK_START, function)
    end = text.find(BLOCK_END, start)
    if start < 0 or end < 0:
        raise SystemExit("planExploreTraj candidate block not found")
    end += len(BLOCK_END)

    current = text[start:end]
    if "[FUEL_EXPLORE_RETRY]" not in current:
        text = text[:start] + REPLACEMENT + text[end:]

    # Keep the patch idempotent while allowing this corrective detail to be
    # applied to a workspace that already has the first retry implementation.
    text = text.replace(
        "    if (pp_.min_time_) cost_func |= BsplineOptimizer::MINTIME;\n\n    vector<Vector3d> start, end;",
        "    if (pp_.min_time_ && retry == 0) cost_func |= BsplineOptimizer::MINTIME;\n\n    vector<Vector3d> start, end;",
        1,
    )
    text = text.replace(
        "    bspline_optimizers_[0]->setTimeLowerBound(effective_time_lb);\n    bspline_optimizers_[0]->optimize(ctrl_pts, candidate_dt, cost_func, 1, 1);\n\n    const double dt2 = candidate_dt * candidate_dt;\n    ctrl_pts.row(0) = start[0] - start[1] * candidate_dt + start[2] * dt2 / 3.0;\n    ctrl_pts.row(1) = start[0] - start[2] * dt2 / 6.0;\n    ctrl_pts.row(2) = start[0] + start[1] * candidate_dt + start[2] * dt2 / 3.0;\n    position_traj.setUniformBspline(ctrl_pts, pp_.bspline_degree_, candidate_dt);",
        "    bspline_optimizers_[0]->setTimeLowerBound(effective_time_lb);\n    const double requested_dt = candidate_dt;\n    bspline_optimizers_[0]->optimize(ctrl_pts, candidate_dt, cost_func, 1, 1);\n\n    const double optimized_dt = candidate_dt;\n    const double dt2 = optimized_dt * optimized_dt;\n    ctrl_pts.row(0) = start[0] - start[1] * optimized_dt + start[2] * dt2 / 3.0;\n    ctrl_pts.row(1) = start[0] - start[2] * dt2 / 6.0;\n    ctrl_pts.row(2) = start[0] + start[1] * optimized_dt + start[2] * dt2 / 3.0;\n    position_traj.setUniformBspline(ctrl_pts, pp_.bspline_degree_, optimized_dt);",
        1,
    )
    text = text.replace("    candidate_dt = next_dt;\n", "    candidate_dt = requested_dt * 1.15;\n", 1)

    loop = "  for (int iteration = 0; iteration < max_iterations && ros::ok(); ++iteration) {\n"
    if CALLER_RETRY_MARKER not in text:
        if loop not in text:
            raise SystemExit("dynamic feasibility loop not found")
        text = text.replace(loop, CALLER_RETRY_MARKER + loop, 1)

    success = "      trajectory = candidate;\n      return true;\n    }\n"
    if CALLER_RETRY_INSERT not in text:
        if success not in text:
            raise SystemExit("dynamic feasibility success block not found")
        text = text.replace(success, success + CALLER_RETRY_INSERT, 1)

    path.write_text(text, encoding="utf-8")
    print(f"Applied regenerated-candidate exploration retry to {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    args = parser.parse_args()
    apply(args.fuel_source_root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
