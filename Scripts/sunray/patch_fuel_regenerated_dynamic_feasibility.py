#!/usr/bin/env python3
"""Replace the non-convergent FUEL time repair with candidate regeneration."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "[FUEL_DYN_REGEN]"


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

    old_state_error = (
        '  std::cout << "State error: (" << (start2[0] - start[0]).norm() << ", "\n'
        '            << (start2[1] - start[1]).norm() << ", " << (start2[2] - start[2]).norm() << ")"\n'
        '            << std::endl;\n'
    )
    new_state_error = (
        '  std::cout << "State error: (" << (start2[0] - start_pt).norm() << ", "\n'
        '            << (start2[1] - start_vel).norm() << ", "\n'
        '            << (start2[2] - start_acc).norm() << ")" << std::endl;\n'
    )
    if old_state_error in manager_cpp.read_text(encoding="utf-8"):
        replace_once(manager_cpp, old_state_error, new_state_error)

    if MARKER in manager_cpp.read_text(encoding="utf-8"):
        print(f"Regenerated dynamic-feasibility patch already applied to {root}")
        return

    replace_once(
        container_h,
        "  bool enforce_dynamic_feasibility_;\n"
        "  int dynamic_feasibility_max_iterations_;\n",
        "  bool enforce_dynamic_feasibility_;\n"
        "  int dynamic_feasibility_max_iterations_;\n"
        "  double dynamic_feasibility_norm_tolerance_;\n"
        "  double dynamic_feasibility_max_time_scale_;\n",
    )
    replace_once(
        manager_h,
        "  bool enforceDynamicFeasibility(NonUniformBspline& trajectory, const char* source);\n",
        "  bool enforceDynamicFeasibility(NonUniformBspline& trajectory, const char* source,\n"
        "      double* required_time_scale);\n",
    )
    replace_once(
        manager_cpp,
        '  nh.param("manager/dynamic_feasibility_max_iterations", pp_.dynamic_feasibility_max_iterations_, 8);\n',
        '  nh.param("manager/dynamic_feasibility_max_iterations", pp_.dynamic_feasibility_max_iterations_, 8);\n'
        '  nh.param("manager/dynamic_feasibility_norm_tolerance",\n'
        '      pp_.dynamic_feasibility_norm_tolerance_, 0.01);\n'
        '  nh.param("manager/dynamic_feasibility_max_time_scale",\n'
        '      pp_.dynamic_feasibility_max_time_scale_, 2.0);\n',
    )
    replace_once(
        manager_cpp,
        "void enforceCubicPvaBoundary(Eigen::MatrixXd& ctrl_pts, const double dt,\n"
        "    const vector<Eigen::Vector3d>& start, const vector<Eigen::Vector3d>& end) {\n"
        "  if (ctrl_pts.rows() < 6 || start.size() < 3 || end.size() < 3 || dt <= 0.0) return;\n"
        "  const double dt2 = dt * dt;\n"
        "  ctrl_pts.row(0) = start[0] - start[1] * dt + start[2] * dt2 / 3.0;\n"
        "  ctrl_pts.row(1) = start[0] - start[2] * dt2 / 6.0;\n"
        "  ctrl_pts.row(2) = start[0] + start[1] * dt + start[2] * dt2 / 3.0;\n"
        "  const int n = ctrl_pts.rows();\n"
        "  ctrl_pts.row(n - 3) = end[0] - end[1] * dt + end[2] * dt2 / 3.0;\n"
        "  ctrl_pts.row(n - 2) = end[0] - end[2] * dt2 / 6.0;\n"
        "  ctrl_pts.row(n - 1) = end[0] + end[1] * dt + end[2] * dt2 / 3.0;\n"
        "}\n",
        "void enforceCubicPvaBoundary(Eigen::MatrixXd& ctrl_pts, const double dt,\n"
        "    const vector<Eigen::Vector3d>& start, const vector<Eigen::Vector3d>& end) {\n"
        "  if (ctrl_pts.rows() < 6 || start.size() < 3 || dt <= 0.0) return;\n"
        "  const double dt2 = dt * dt;\n"
        "  ctrl_pts.row(0) = start[0] - start[1] * dt + start[2] * dt2 / 3.0;\n"
        "  ctrl_pts.row(1) = start[0] - start[2] * dt2 / 6.0;\n"
        "  ctrl_pts.row(2) = start[0] + start[1] * dt + start[2] * dt2 / 3.0;\n"
        "  if (end.size() < 3) return;\n"
        "  const int n = ctrl_pts.rows();\n"
        "  ctrl_pts.row(n - 3) = end[0] - end[1] * dt + end[2] * dt2 / 3.0;\n"
        "  ctrl_pts.row(n - 2) = end[0] - end[2] * dt2 / 6.0;\n"
        "  ctrl_pts.row(n - 1) = end[0] + end[1] * dt + end[2] * dt2 / 3.0;\n"
        "}\n",
    )

    old_kino = r'''  Eigen::MatrixXd ctrl_pts;
  NonUniformBspline::parameterizeToBspline(
      ts, point_set, start_end_derivatives, pp_.bspline_degree_, ctrl_pts);
  NonUniformBspline init(ctrl_pts, pp_.bspline_degree_, ts);

  // B-spline-based optimization
  int cost_function = BsplineOptimizer::NORMAL_PHASE;
  if (pp_.min_time_) cost_function |= BsplineOptimizer::MINTIME;
  vector<Eigen::Vector3d> start, end;
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
  if (time_lb > 0) bspline_optimizers_[0]->setTimeLowerBound(time_lb);

  bspline_optimizers_[0]->optimize(ctrl_pts, ts, cost_function, 1, 1);
  enforceCubicPvaBoundary(ctrl_pts, ts, start, end);
  NonUniformBspline position_traj(ctrl_pts, pp_.bspline_degree_, ts);
  if (!enforceDynamicFeasibility(position_traj, "kinodynamicReplan")) {
    ROS_ERROR("[FUEL_DYN_FEAS] Rejecting infeasible kinodynamic trajectory");
    return false;
  }
  local_data_.position_traj_ = position_traj;
'''
    new_kino = r'''  // Regenerate from the same searched path when the controller-facing vector
  // norm is infeasible. Mutating one optimized spline's knots and first control
  // points caused non-monotonic acceleration and 10x-15x duration inflation.
  const int feasibility_attempts = std::max(1, pp_.dynamic_feasibility_max_iterations_);
  const double max_time_scale = std::max(1.0, pp_.dynamic_feasibility_max_time_scale_);
  double candidate_dt = ts;
  double cumulative_time_scale = 1.0;
  bool accepted = false;
  NonUniformBspline position_traj;
  int cost_function = BsplineOptimizer::NORMAL_PHASE;
  if (pp_.min_time_) cost_function |= BsplineOptimizer::MINTIME;
  for (int attempt = 0; attempt < feasibility_attempts && ros::ok(); ++attempt) {
    Eigen::MatrixXd ctrl_pts;
    NonUniformBspline::parameterizeToBspline(
        candidate_dt, point_set, start_end_derivatives, pp_.bspline_degree_, ctrl_pts);
    NonUniformBspline init(ctrl_pts, pp_.bspline_degree_, candidate_dt);
    vector<Eigen::Vector3d> start, end;
    init.getBoundaryStates(2, 0, start, end);
    ROS_WARN("[FUEL_KINO_BOUNDARY] attempt=%d candidate_to_request dp=%.6f dv=%.6f da=%.6f",
        attempt, (start[0] - start_pt).norm(), (start[1] - start_vel).norm(),
        (start[2] - start_acc).norm());
    start[0] = start_pt;
    start[1] = start_vel;
    start[2] = start_acc;
    bspline_optimizers_[0]->setBoundaryStates(start, end);
    bspline_optimizers_[0]->setTimeLowerBound(
        std::max(time_lb, candidate_dt * double(point_set.size() - 1)));
    bspline_optimizers_[0]->optimize(ctrl_pts, candidate_dt, cost_function, 1, 1);
    enforceCubicPvaBoundary(ctrl_pts, candidate_dt, start, end);
    NonUniformBspline candidate(ctrl_pts, pp_.bspline_degree_, candidate_dt);
    double required_time_scale = 1.0;
    if (enforceDynamicFeasibility(candidate, "kinodynamicReplan", &required_time_scale)) {
      position_traj = candidate;
      accepted = true;
      break;
    }
    if (!std::isfinite(required_time_scale) || required_time_scale <= 1.0) break;
    const double step_scale = required_time_scale * 1.01;
    cumulative_time_scale *= step_scale;
    ROS_WARN("[FUEL_DYN_REGEN] source=kinodynamicReplan attempt=%d dt=%.6f "
             "required_scale=%.6f cumulative_scale=%.6f",
        attempt, candidate_dt, step_scale, cumulative_time_scale);
    if (cumulative_time_scale > max_time_scale + 1e-9) break;
    candidate_dt *= step_scale;
  }
  if (!accepted) {
    ROS_ERROR("[FUEL_DYN_REGEN] Rejecting kinodynamic trajectory after regeneration");
    return false;
  }
  local_data_.position_traj_ = position_traj;
'''
    replace_once(manager_cpp, old_kino, new_kino)

    old_explore = r'''  Eigen::MatrixXd ctrl_pts;
  NonUniformBspline::parameterizeToBspline(
      dt, points, boundary_deri, pp_.bspline_degree_, ctrl_pts);
  NonUniformBspline tmp_traj(ctrl_pts, pp_.bspline_degree_, dt);

  int cost_func = BsplineOptimizer::NORMAL_PHASE;
  if (pp_.min_time_) cost_func |= BsplineOptimizer::MINTIME;

  vector<Vector3d> start, end;
  tmp_traj.getBoundaryStates(2, 0, start, end);
  ROS_WARN("[FUEL_EXPLORE_BOUNDARY] candidate_to_request dp=%.6f dv=%.6f da=%.6f",
      (start[0] - tour.front()).norm(),
      (start[1] - cur_vel).norm(),
      (start[2] - cur_acc).norm());
  start[0] = tour.front();
  start[1] = cur_vel;
  start[2] = cur_acc;
  bspline_optimizers_[0]->setBoundaryStates(start, end);
  bspline_optimizers_[0]->optimize(ctrl_pts, dt, cost_func, 1, 1);
  const double dt2 = dt * dt;
  ctrl_pts.row(0) = start[0] - start[1] * dt + start[2] * dt2 / 3.0;
  ctrl_pts.row(1) = start[0] - start[2] * dt2 / 6.0;
  ctrl_pts.row(2) = start[0] + start[1] * dt + start[2] * dt2 / 3.0;
  NonUniformBspline position_traj(ctrl_pts, pp_.bspline_degree_, dt);
  if (!enforceDynamicFeasibility(position_traj, "planExploreTraj")) {
    ROS_ERROR("[FUEL_DYN_FEAS] Rejecting infeasible exploration trajectory");
    return false;
  }
  local_data_.position_traj_ = position_traj;
'''
    new_explore = r'''  const int feasibility_attempts = std::max(1, pp_.dynamic_feasibility_max_iterations_);
  const double max_time_scale = std::max(1.0, pp_.dynamic_feasibility_max_time_scale_);
  double candidate_dt = dt;
  double cumulative_time_scale = 1.0;
  bool accepted = false;
  NonUniformBspline position_traj;
  int cost_func = BsplineOptimizer::NORMAL_PHASE;
  if (pp_.min_time_) cost_func |= BsplineOptimizer::MINTIME;
  for (int attempt = 0; attempt < feasibility_attempts && ros::ok(); ++attempt) {
    Eigen::MatrixXd ctrl_pts;
    NonUniformBspline::parameterizeToBspline(
        candidate_dt, points, boundary_deri, pp_.bspline_degree_, ctrl_pts);
    NonUniformBspline tmp_traj(ctrl_pts, pp_.bspline_degree_, candidate_dt);
    vector<Vector3d> start, end;
    tmp_traj.getBoundaryStates(2, 0, start, end);
    ROS_WARN("[FUEL_EXPLORE_BOUNDARY] attempt=%d candidate_to_request dp=%.6f dv=%.6f da=%.6f",
        attempt, (start[0] - tour.front()).norm(), (start[1] - cur_vel).norm(),
        (start[2] - cur_acc).norm());
    start[0] = tour.front();
    start[1] = cur_vel;
    start[2] = cur_acc;
    bspline_optimizers_[0]->setBoundaryStates(start, end);
    bspline_optimizers_[0]->setTimeLowerBound(
        std::max(effective_time_lb, candidate_dt * double(seg_num)));
    bspline_optimizers_[0]->optimize(ctrl_pts, candidate_dt, cost_func, 1, 1);
    enforceCubicPvaBoundary(ctrl_pts, candidate_dt, start, end);
    NonUniformBspline candidate(ctrl_pts, pp_.bspline_degree_, candidate_dt);
    double required_time_scale = 1.0;
    if (enforceDynamicFeasibility(candidate, "planExploreTraj", &required_time_scale)) {
      position_traj = candidate;
      accepted = true;
      break;
    }
    if (!std::isfinite(required_time_scale) || required_time_scale <= 1.0) break;
    const double step_scale = required_time_scale * 1.01;
    cumulative_time_scale *= step_scale;
    ROS_WARN("[FUEL_DYN_REGEN] source=planExploreTraj attempt=%d dt=%.6f "
             "required_scale=%.6f cumulative_scale=%.6f",
        attempt, candidate_dt, step_scale, cumulative_time_scale);
    if (cumulative_time_scale > max_time_scale + 1e-9) break;
    candidate_dt *= step_scale;
  }
  if (!accepted) {
    ROS_ERROR("[FUEL_DYN_REGEN] Rejecting exploration trajectory after regeneration");
    return false;
  }
  local_data_.position_traj_ = position_traj;
'''
    replace_once(manager_cpp, old_explore, new_explore)

    start = "bool FastPlannerManager::enforceDynamicFeasibility(\n"
    end = "\n// !SECTION\n"
    text = manager_cpp.read_text(encoding="utf-8")
    start_index = text.find(start)
    end_index = text.find(end, start_index)
    if start_index < 0 or end_index < 0:
        raise RuntimeError(f"{manager_cpp}: dynamic-feasibility function not found")
    replacement = r'''bool FastPlannerManager::enforceDynamicFeasibility(
    NonUniformBspline& trajectory, const char* source, double* required_time_scale) {
  if (required_time_scale != nullptr) *required_time_scale = 1.0;
  if (!pp_.enforce_dynamic_feasibility_) return true;
  if (pp_.max_vel_ <= 0.0 || pp_.max_acc_ <= 0.0) {
    ROS_ERROR("[FUEL_DYN_FEAS] Invalid limits: max_vel=%.3f max_acc=%.3f",
        pp_.max_vel_, pp_.max_acc_);
    return false;
  }

  trajectory.setPhysicalLimits(pp_.max_vel_, pp_.max_acc_);
  const bool native_feasible = trajectory.checkFeasibility(false);
  const double native_ratio = trajectory.checkRatio();
  double mean_vel = 0.0, peak_vel = 0.0, mean_acc = 0.0, peak_acc = 0.0;
  trajectory.getMeanAndMaxVel(mean_vel, peak_vel);
  trajectory.getMeanAndMaxAcc(mean_acc, peak_acc);
  vector<Eigen::Vector3d> start, end;
  trajectory.getBoundaryStates(2, 2, start, end);
  peak_vel = std::max(peak_vel, std::max(start[1].norm(), end[1].norm()));
  peak_acc = std::max(peak_acc, std::max(start[2].norm(), end[2].norm()));

  const double tolerance = std::max(0.0, pp_.dynamic_feasibility_norm_tolerance_);
  const double velocity_limit = pp_.max_vel_ * (1.0 + tolerance);
  const double acceleration_limit = pp_.max_acc_ * (1.0 + tolerance);
  double scale = 1.0;
  if (std::isfinite(peak_vel)) scale = std::max(scale, peak_vel / velocity_limit);
  if (std::isfinite(peak_acc))
    scale = std::max(scale, sqrt(peak_acc / acceleration_limit));
  const bool norm_feasible = std::isfinite(peak_vel) && std::isfinite(peak_acc) && scale <= 1.0;
  if (required_time_scale != nullptr) *required_time_scale = scale;
  ROS_WARN("[FUEL_DYN_FEAS] source=%s native_feasible=%d native_ratio=%.6f "
           "duration=%.6f sample_peak_vel=%.6f sample_peak_acc=%.6f "
           "norm_tolerance=%.6f required_scale=%.6f accepted=%d",
      source, native_feasible, native_ratio, trajectory.getTimeSum(), peak_vel,
      peak_acc, tolerance, scale, norm_feasible);
  return norm_feasible;
}
'''
    manager_cpp.write_text(
        text[:start_index] + replacement.rstrip("\n") + text[end_index:],
        encoding="utf-8",
    )
    print(f"Applied regenerated FUEL dynamic feasibility to {root}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    args = parser.parse_args()
    apply(args.fuel_source_root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
