#!/usr/bin/env python3
"""Apply the reviewed FUEL hard dynamic-feasibility change to a ROS1 source tree."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one match, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def apply(root: Path) -> None:
    plan = root / "plan_manage"
    manager_h = plan / "include/plan_manage/planner_manager.h"
    container_h = plan / "include/plan_manage/plan_container.hpp"
    manager_cpp = plan / "src/planner_manager.cpp"
    exploration_cpp = root / "exploration_manager/src/fast_exploration_manager.cpp"

    replace_once(
        container_h,
        "  double accept_vel_, accept_acc_;\n",
        "  double accept_vel_, accept_acc_;\n"
        "  bool enforce_dynamic_feasibility_;\n"
        "  int dynamic_feasibility_max_iterations_;\n",
    )
    replace_once(
        manager_h,
        "  void planExploreTraj(const vector<Eigen::Vector3d>& tour, const Eigen::Vector3d& cur_vel,\n",
        "  bool planExploreTraj(const vector<Eigen::Vector3d>& tour, const Eigen::Vector3d& cur_vel,\n",
    )
    replace_once(
        manager_h,
        "  void updateTrajInfo();\n",
        "  void updateTrajInfo();\n"
        "  bool enforceDynamicFeasibility(NonUniformBspline& trajectory, const char* source);\n",
    )
    replace_once(
        manager_cpp,
        '  nh.param("manager/accept_acc", pp_.accept_acc_, pp_.max_acc_ + 0.5);\n',
        '  nh.param("manager/accept_acc", pp_.accept_acc_, pp_.max_acc_ + 0.5);\n'
        '  nh.param("manager/enforce_dynamic_feasibility", pp_.enforce_dynamic_feasibility_, true);\n'
        '  nh.param("manager/dynamic_feasibility_max_iterations", pp_.dynamic_feasibility_max_iterations_, 8);\n',
    )
    replace_once(
        manager_cpp,
        "  bspline_optimizers_[0]->optimize(ctrl_pts, ts, cost_function, 1, 1);\n"
        "  local_data_.position_traj_.setUniformBspline(ctrl_pts, pp_.bspline_degree_, ts);\n",
        "  bspline_optimizers_[0]->optimize(ctrl_pts, ts, cost_function, 1, 1);\n"
        "  NonUniformBspline position_traj(ctrl_pts, pp_.bspline_degree_, ts);\n"
        '  if (!enforceDynamicFeasibility(position_traj, "kinodynamicReplan")) {\n'
        '    ROS_ERROR("[FUEL_DYN_FEAS] Rejecting infeasible kinodynamic trajectory");\n'
        "    return false;\n"
        "  }\n"
        "  local_data_.position_traj_ = position_traj;\n",
    )
    replace_once(
        manager_cpp,
        "void FastPlannerManager::planExploreTraj(const vector<Eigen::Vector3d>& tour,\n",
        "bool FastPlannerManager::planExploreTraj(const vector<Eigen::Vector3d>& tour,\n",
    )
    replace_once(
        manager_cpp,
        '  if (tour.empty()) ROS_ERROR("Empty path to traj planner");\n',
        '  if (tour.size() < 2) {\n'
        '    ROS_ERROR("[FUEL_TRAJ_INPUT] Need at least two waypoints, got %zu", tour.size());\n'
        '    return false;\n'
        '  }\n',
    )
    replace_once(
        manager_cpp,
        "  bspline_optimizers_[0]->optimize(ctrl_pts, dt, cost_func, 1, 1);\n"
        "  local_data_.position_traj_.setUniformBspline(ctrl_pts, pp_.bspline_degree_, dt);\n"
        "\n"
        "  updateTrajInfo();\n"
        "}\n",
        "  bspline_optimizers_[0]->optimize(ctrl_pts, dt, cost_func, 1, 1);\n"
        "  NonUniformBspline position_traj(ctrl_pts, pp_.bspline_degree_, dt);\n"
        '  if (!enforceDynamicFeasibility(position_traj, "planExploreTraj")) {\n'
        '    ROS_ERROR("[FUEL_DYN_FEAS] Rejecting infeasible exploration trajectory");\n'
        "    return false;\n"
        "  }\n"
        "  local_data_.position_traj_ = position_traj;\n"
        "\n"
        "  updateTrajInfo();\n"
        "  return true;\n"
        "}\n\n"
        "bool FastPlannerManager::enforceDynamicFeasibility(\n"
        "    NonUniformBspline& trajectory, const char* source) {\n"
        "  if (!pp_.enforce_dynamic_feasibility_) return true;\n"
        "  if (pp_.max_vel_ <= 0.0 || pp_.max_acc_ <= 0.0) {\n"
        '    ROS_ERROR("[FUEL_DYN_FEAS] Invalid limits: max_vel=%.3f max_acc=%.3f",\n'
        "        pp_.max_vel_, pp_.max_acc_);\n"
        "    return false;\n"
        "  }\n\n"
        "  trajectory.setPhysicalLimits(pp_.max_vel_, pp_.max_acc_);\n"
        "  const double duration_before = trajectory.getTimeSum();\n"
        "  const double ratio_before = trajectory.checkRatio();\n"
        "  if (!std::isfinite(ratio_before) || ratio_before <= 0.0) {\n"
        '    ROS_ERROR("[FUEL_DYN_FEAS] %s produced invalid ratio %.6f", source, ratio_before);\n'
        "    return false;\n"
        "  }\n\n"
        "  if (ratio_before > 1.0) trajectory.lengthenTime(ratio_before * 1.01);\n"
        "  bool feasible = trajectory.checkFeasibility(false);\n"
        "  int iterations = 0;\n"
        "  const int max_iterations = std::max(0, pp_.dynamic_feasibility_max_iterations_);\n"
        "  while (!feasible && iterations < max_iterations && ros::ok()) {\n"
        "    trajectory.reallocateTime(false);\n"
        "    feasible = trajectory.checkFeasibility(false);\n"
        "    ++iterations;\n"
        "  }\n\n"
        "  const double ratio_after = trajectory.checkRatio();\n"
        "  const double duration_after = trajectory.getTimeSum();\n"
        '  ROS_WARN("[FUEL_DYN_FEAS] source=%s feasible=%d ratio_before=%.6f "\n'
        '           "ratio_after=%.6f duration_before=%.6f duration_after=%.6f iterations=%d",\n'
        "      source, feasible, ratio_before, ratio_after, duration_before, duration_after, iterations);\n"
        "  if (!feasible) trajectory.checkFeasibility(true);\n"
        "  return feasible;\n"
        "}\n",
    )
    replace_once(
        exploration_cpp,
        "    planner_manager_->planExploreTraj(ed_->path_next_goal_, vel, acc, time_lb);\n",
        "    if (!planner_manager_->planExploreTraj(ed_->path_next_goal_, vel, acc, time_lb))\n"
        "      return FAIL;\n",
    )
    replace_once(
        exploration_cpp,
        "    planner_manager_->planExploreTraj(truncated_path, vel, acc, time_lb);\n",
        "    if (!planner_manager_->planExploreTraj(truncated_path, vel, acc, time_lb))\n"
        "      return FAIL;\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    args = parser.parse_args()
    apply(args.fuel_source_root.resolve())
    print(f"Applied FUEL hard dynamic-feasibility patch to {args.fuel_source_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
