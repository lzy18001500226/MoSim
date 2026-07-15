#!/usr/bin/env python3
from pathlib import Path
import argparse


START = "bool FastPlannerManager::enforceDynamicFeasibility(\n"
END = "\n// !SECTION\n"

ZERO_TERMINAL_BLOCK = r'''  vector<Vector3d> start, end;
  tmp_traj.getBoundaryStates(2, 2, start, end);
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
  bspline_optimizers_[0]->optimize(ctrl_pts, dt, cost_func, 1, 1);
  vector<Eigen::Vector3d> pva_start, pva_end;
  tmp_traj.getBoundaryStates(2, 2, pva_start, pva_end);
  pva_start[0] = tour.front();
  pva_start[1] = cur_vel;
  pva_start[2] = cur_acc;
  pva_end[1].setZero();
  pva_end[2].setZero();
  enforceCubicPvaBoundary(ctrl_pts, dt, pva_start, pva_end);
'''

FREE_TERMINAL_BLOCK = r'''  vector<Vector3d> start, end;
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
'''

REPLACEMENT = r'''bool FastPlannerManager::enforceDynamicFeasibility(
    NonUniformBspline& trajectory, const char* source) {
  if (!pp_.enforce_dynamic_feasibility_) return true;
  if (pp_.max_vel_ <= 0.0 || pp_.max_acc_ <= 0.0) {
    ROS_ERROR("[FUEL_DYN_FEAS] Invalid limits: max_vel=%.3f max_acc=%.3f",
        pp_.max_vel_, pp_.max_acc_);
    return false;
  }

  NonUniformBspline candidate = trajectory;
  candidate.setPhysicalLimits(pp_.max_vel_, pp_.max_acc_);
  vector<Eigen::Vector3d> boundary_start, boundary_end;
  candidate.getBoundaryStates(2, 2, boundary_start, boundary_end);
  const double duration_before = trajectory.getTimeSum();
  const double ratio_before = candidate.checkRatio();
  if (!std::isfinite(ratio_before) || ratio_before <= 0.0) {
    ROS_ERROR("[FUEL_DYN_FEAS] %s produced invalid ratio %.6f", source, ratio_before);
    return false;
  }

  const int max_iterations = std::max(1, pp_.dynamic_feasibility_max_iterations_);
  for (int iteration = 0; iteration < max_iterations && ros::ok(); ++iteration) {
    const bool feasible = candidate.checkFeasibility(false);
    const double ratio = candidate.checkRatio();
    double mean_vel = 0.0, peak_vel = 0.0, mean_acc = 0.0, peak_acc = 0.0;
    candidate.getMeanAndMaxVel(mean_vel, peak_vel);
    candidate.getMeanAndMaxAcc(mean_acc, peak_acc);
    vector<Eigen::Vector3d> current_start, current_end;
    candidate.getBoundaryStates(2, 2, current_start, current_end);
    // getMeanAndMax*() advances in 10 ms increments and can miss the exact
    // endpoint when the duration is not a multiple of 10 ms. Include both
    // exact boundaries so an unchecked terminal acceleration cannot become
    // the next replan's immutable start state.
    peak_vel = std::max(peak_vel,
        std::max(current_start[1].norm(), current_end[1].norm()));
    peak_acc = std::max(peak_acc,
        std::max(current_start[2].norm(), current_end[2].norm()));
    const double start_pva_error = std::max(
        (current_start[0] - boundary_start[0]).norm(),
        std::max((current_start[1] - boundary_start[1]).norm(),
                 (current_start[2] - boundary_start[2]).norm()));
    const double end_pva_error =
        (current_end[0] - boundary_end[0]).norm();
    const bool boundary_preserved =
        start_pva_error <= 1e-6 && end_pva_error <= 1e-6;
    // FUEL's native feasibility test is component-wise.  A diagonal command
    // can therefore exceed the configured physical speed/acceleration norm
    // by sqrt(2) while every axis still passes.  The controller contract uses
    // vector magnitudes, so require both checks before committing a spline.
    // Both the search spline and the final exploration spline feed the next
    // planning boundary. Enforce the controller's vector-norm contract on
    // both so an over-limit intermediate state cannot poison the handoff.
    const bool require_norm_contract = true;
    const bool norm_feasible =
        !require_norm_contract ||
        (std::isfinite(peak_vel) && std::isfinite(peak_acc) &&
         peak_vel <= pp_.max_vel_ * 1.001 && peak_acc <= pp_.max_acc_ * 1.001);
    // checkFeasibility()/checkRatio() operate on derivative control points.
    // Their convex-hull bound is sufficient but can be far from necessary;
    // using that bound as a time scale made valid trajectories 3x slower.
    // The 10 ms norm sampling above is the controller-facing contract. Keep
    // the native component result as an audit signal, but allow a sampled,
    // boundary-preserving trajectory to pass when the conservative bound does
    // not.
    const bool tolerance_accepted =
        !feasible && boundary_preserved && norm_feasible;
    ROS_WARN("[FUEL_DYN_FEAS] source=%s iter=%d feasible=%d tolerance_accepted=%d "
             "ratio_before=%.6f ratio=%.6f duration=%.6f->%.6f "
             "sample_peak_vel=%.6f sample_peak_acc=%.6f boundary_error=(%.9f,%.9f)",
        source, iteration, feasible, tolerance_accepted, ratio_before, ratio,
        duration_before, candidate.getTimeSum(), peak_vel, peak_acc,
        start_pva_error, end_pva_error);
    if ((feasible || tolerance_accepted) && boundary_preserved && norm_feasible) {
      trajectory = candidate;
      return true;
    }
    double repair_ratio = 1.0;
    if (require_norm_contract && std::isfinite(peak_vel) && std::isfinite(peak_acc)) {
      repair_ratio = std::max(repair_ratio, peak_vel / pp_.max_vel_);
      repair_ratio = std::max(repair_ratio, sqrt(peak_acc / pp_.max_acc_));
    }
    if (!std::isfinite(repair_ratio) || repair_ratio <= 1.0) return false;
    // FUEL's lengthenTime() leaves endpoint knot spans unchanged. That keeps
    // endpoint derivatives intact, but it also means a violation near the
    // start can never converge. Rebuild a uniformly slower spline and restore
    // only the requested start PVA. FUEL constrains the terminal position, not
    // terminal velocity/acceleration; leaving the last controls unchanged
    // avoids turning every one-second replan into a braking trajectory.
    const double old_duration = candidate.getTimeSum();
    const double repaired_dt = candidate.getKnotSpan() * repair_ratio * 1.01;
    Eigen::MatrixXd repaired_ctrl_pts = candidate.getControlPoint();
    const double repaired_dt2 = repaired_dt * repaired_dt;
    repaired_ctrl_pts.row(0) = boundary_start[0] - boundary_start[1] * repaired_dt
        + boundary_start[2] * repaired_dt2 / 3.0;
    repaired_ctrl_pts.row(1) = boundary_start[0]
        - boundary_start[2] * repaired_dt2 / 6.0;
    repaired_ctrl_pts.row(2) = boundary_start[0] + boundary_start[1] * repaired_dt
        + boundary_start[2] * repaired_dt2 / 3.0;
    candidate.setUniformBspline(repaired_ctrl_pts, pp_.bspline_degree_, repaired_dt);
    candidate.setPhysicalLimits(pp_.max_vel_, pp_.max_acc_);
    if (candidate.getTimeSum() <= old_duration + 1e-9) {
      ROS_ERROR("[FUEL_DYN_FEAS] %s cannot increase uniform knot span", source);
      return false;
    }
  }

  ROS_ERROR("[FUEL_DYN_FEAS] %s could not produce a boundary-preserving feasible spline", source);
  return false;
}
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    root = parser.parse_args().fuel_source_root.resolve()
    path = root / "plan_manage/src/planner_manager.cpp"
    text = path.read_text(encoding="utf-8")
    original_text = text
    if ZERO_TERMINAL_BLOCK in text:
        text = text.replace(ZERO_TERMINAL_BLOCK, FREE_TERMINAL_BLOCK, 1)
    elif FREE_TERMINAL_BLOCK not in text:
        raise SystemExit("exploration terminal-boundary block not found")
    start = text.find(START)
    if start < 0:
        raise SystemExit("dynamic-feasibility function start not found")
    end = text.find(END, start)
    if end < 0:
        raise SystemExit("dynamic-feasibility function end not found")
    current = text[start:end]
    if current == REPLACEMENT.rstrip("\n"):
        if text != original_text:
            path.write_text(text, encoding="utf-8")
            print("Applied free-terminal exploration boundary")
        else:
            print("Boundary-preserving feasibility patch already applied")
        return 0
    path.write_text(text[:start] + REPLACEMENT.rstrip("\n") + text[end:], encoding="utf-8")
    print("Applied boundary-preserving FUEL dynamic feasibility")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
