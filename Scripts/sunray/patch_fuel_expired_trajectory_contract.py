#!/usr/bin/env python3
"""Make FUEL replanning transactional and consistent after trajectory expiry."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str, path: Path) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one patch anchor, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    root = parser.parse_args().fuel_source_root.resolve()
    source = root / "exploration_manager/src/fast_exploration_fsm.cpp"
    text = source.read_text(encoding="utf-8")

    text = replace_once(
        text,
        """        double t_r = (replan_start_time_ - info->start_time_).toSec();

        fd_->start_pt_ = info->position_traj_.evaluateDeBoorT(t_r);
        fd_->start_vel_ = info->velocity_traj_.evaluateDeBoorT(t_r);
        fd_->start_acc_ = info->acceleration_traj_.evaluateDeBoorT(t_r);
        fd_->start_yaw_(0) = info->yaw_traj_.evaluateDeBoorT(t_r)[0];
        fd_->start_yaw_(1) = info->yawdot_traj_.evaluateDeBoorT(t_r)[0];
        fd_->start_yaw_(2) = info->yawdotdot_traj_.evaluateDeBoorT(t_r)[0];
""",
        """        const double requested_t = (replan_start_time_ - info->start_time_).toSec();
        const bool expired = requested_t >= info->duration_;
        const double t_r = std::max(0.0, std::min(requested_t, info->duration_));

        fd_->start_pt_ = info->position_traj_.evaluateDeBoorT(t_r);
        fd_->start_vel_ = expired ? Eigen::Vector3d::Zero()
                                 : info->velocity_traj_.evaluateDeBoorT(t_r);
        fd_->start_acc_ = expired ? Eigen::Vector3d::Zero()
                                 : info->acceleration_traj_.evaluateDeBoorT(t_r);
        fd_->start_yaw_(0) = info->yaw_traj_.evaluateDeBoorT(t_r)[0];
        fd_->start_yaw_(1) = expired ? 0.0 : info->yawdot_traj_.evaluateDeBoorT(t_r)[0];
        fd_->start_yaw_(2) = expired ? 0.0 : info->yawdotdot_traj_.evaluateDeBoorT(t_r)[0];
        ROS_WARN("[FUEL_HANDOFF] active_id=%d requested_t=%.6f sample_t=%.6f duration=%.6f "
                 "expired=%d start_p=(%.6f,%.6f,%.6f) start_v=(%.6f,%.6f,%.6f) "
                 "start_a=(%.6f,%.6f,%.6f)",
            info->traj_id_, requested_t, t_r, info->duration_, expired,
            fd_->start_pt_.x(), fd_->start_pt_.y(), fd_->start_pt_.z(),
            fd_->start_vel_.x(), fd_->start_vel_.y(), fd_->start_vel_.z(),
            fd_->start_acc_.x(), fd_->start_acc_.y(), fd_->start_acc_.z());
""",
        source,
    )

    text = replace_once(
        text,
        """  classic_ = false;
  if (res == SUCCEED && ros::Time::now() > time_r) {
""",
        """  classic_ = false;
  if (res == FAIL) {
    ROS_WARN("[FUEL_HANDOFF] Planning failed; restoring active trajectory id=%d",
        active_traj.traj_id_);
    planner_manager_->local_data_ = active_traj;
    return FAIL;
  }
  if (res == SUCCEED && ros::Time::now() > time_r) {
""",
        source,
    )

    text = replace_once(
        text,
        """  if (res == SUCCEED) {
    auto info = &planner_manager_->local_data_;
    info->start_time_ = (ros::Time::now() - time_r).toSec() > 0 ? ros::Time::now() : time_r;

    bspline::Bspline bspline;
""",
        """  if (res == SUCCEED) {
    auto info = &planner_manager_->local_data_;
    info->start_time_ = (ros::Time::now() - time_r).toSec() > 0 ? ros::Time::now() : time_r;
    const Eigen::Vector3d new_p = info->position_traj_.evaluateDeBoorT(0.0);
    const Eigen::Vector3d new_v = info->velocity_traj_.evaluateDeBoorT(0.0);
    const Eigen::Vector3d new_a = info->acceleration_traj_.evaluateDeBoorT(0.0);
    ROS_WARN("[FUEL_HANDOFF] publish active_id=%d new_id=%d boundary_dp=%.6f "
             "new_p=(%.6f,%.6f,%.6f) new_v=(%.6f,%.6f,%.6f) "
             "new_a=(%.6f,%.6f,%.6f)",
        active_traj.traj_id_, info->traj_id_, (new_p - fd_->start_pt_).norm(),
        new_p.x(), new_p.y(), new_p.z(), new_v.x(), new_v.y(), new_v.z(),
        new_a.x(), new_a.y(), new_a.z());

    bspline::Bspline bspline;
""",
        source,
    )

    source.write_text(text, encoding="utf-8")
    print("Applied FUEL expired-trajectory transactional handoff contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
