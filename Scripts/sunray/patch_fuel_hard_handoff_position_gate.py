#!/usr/bin/env python3
"""Reject FUEL trajectories whose committed start misses the requested handoff."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    root = parser.parse_args().fuel_source_root.resolve()
    path = root / "exploration_manager/src/fast_exploration_fsm.cpp"
    text = path.read_text(encoding="utf-8")
    old = """    const Eigen::Vector3d new_p = info->position_traj_.evaluateDeBoorT(0.0);
    const Eigen::Vector3d new_v = info->velocity_traj_.evaluateDeBoorT(0.0);
    const Eigen::Vector3d new_a = info->acceleration_traj_.evaluateDeBoorT(0.0);
    ROS_WARN("[FUEL_HANDOFF] publish active_id=%d new_id=%d boundary_dp=%.6f "
"""
    position_only = """    const Eigen::Vector3d new_p = info->position_traj_.evaluateDeBoorT(0.0);
    const Eigen::Vector3d new_v = info->velocity_traj_.evaluateDeBoorT(0.0);
    const Eigen::Vector3d new_a = info->acceleration_traj_.evaluateDeBoorT(0.0);
    const double boundary_dp = (new_p - fd_->start_pt_).norm();
    if (!std::isfinite(boundary_dp) || boundary_dp > 0.05) {
      ROS_ERROR("[FUEL_HANDOFF_GATE] rejecting new_id=%d boundary_dp=%.6f limit=0.050000",
          info->traj_id_, boundary_dp);
      planner_manager_->local_data_ = active_traj;
      return FAIL;
    }
    ROS_WARN("[FUEL_HANDOFF] publish active_id=%d new_id=%d boundary_dp=%.6f "
"""
    new = """    const Eigen::Vector3d new_p = info->position_traj_.evaluateDeBoorT(0.0);
    const Eigen::Vector3d new_v = info->velocity_traj_.evaluateDeBoorT(0.0);
    const Eigen::Vector3d new_a = info->acceleration_traj_.evaluateDeBoorT(0.0);
    const double boundary_dp = (new_p - fd_->start_pt_).norm();
    const double boundary_dv = (new_v - fd_->start_vel_).norm();
    const double boundary_da = (new_a - fd_->start_acc_).norm();
    const double new_v_norm = new_v.norm();
    const double new_a_norm = new_a.norm();
    if (!std::isfinite(boundary_dp) || !std::isfinite(boundary_dv) ||
        !std::isfinite(boundary_da) || !std::isfinite(new_v_norm) ||
        !std::isfinite(new_a_norm) || boundary_dp > 0.05 ||
        boundary_dv > 0.05 || boundary_da > 0.05 ||
        new_v_norm > planner_manager_->pp_.max_vel_ * 1.001 ||
        new_a_norm > planner_manager_->pp_.max_acc_ * 1.001) {
      ROS_ERROR("[FUEL_HANDOFF_GATE] rejecting new_id=%d dp=%.6f dv=%.6f da=%.6f "
                "v_norm=%.6f/%.6f a_norm=%.6f/%.6f",
          info->traj_id_, boundary_dp, boundary_dv, boundary_da,
          new_v_norm, planner_manager_->pp_.max_vel_,
          new_a_norm, planner_manager_->pp_.max_acc_);
      planner_manager_->local_data_ = active_traj;
      return FAIL;
    }
    ROS_WARN("[FUEL_HANDOFF] publish active_id=%d new_id=%d boundary_dp=%.6f "
             "boundary_dv=%.6f boundary_da=%.6f "
"""
    if new in text:
        print("FUEL hard handoff PVA gate already applied")
        return 0
    if position_only in text:
        text = text.replace(position_only, new, 1)
    elif text.count(old) == 1:
        text = text.replace(old, new, 1)
    else:
        raise SystemExit(f"{path}: expected one handoff anchor")
    old_args = "active_traj.traj_id_, info->traj_id_, (new_p - fd_->start_pt_).norm(),"
    position_args = "active_traj.traj_id_, info->traj_id_, boundary_dp,"
    pva_args = "active_traj.traj_id_, info->traj_id_, boundary_dp, boundary_dv, boundary_da,"
    if old_args in text:
        text = text.replace(old_args, pva_args, 1)
    elif position_args in text:
        text = text.replace(position_args, pva_args, 1)
    path.write_text(text, encoding="utf-8")
    print("Applied FUEL hard handoff PVA gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
