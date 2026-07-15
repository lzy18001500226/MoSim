#!/usr/bin/env python3
"""Add odometry-grounded recovery when FUEL loses trajectory tracking."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKERS = {
    "exploration_manager/include/exploration_manager/expl_data.h": (
        "tracking_error_recovery_enabled_",
        "tracking_error_xy_limit_",
        "tracking_error_persistence_s_",
    ),
    "exploration_manager/include/exploration_manager/fast_exploration_fsm.h": (
        "tracking_error_exceeded_since_",
        "tracking_error_stop_pub_",
    ),
    "exploration_manager/src/fast_exploration_fsm.cpp": (
        "[FUEL_TRACKING_ERROR_WARN]",
        "[FUEL_TRACKING_ERROR_RECOVERY]",
        "/planning/tracking_error_stop",
    ),
    "plan_manage/src/traj_server.cpp": (
        "[FUEL_ODOM_HOLD]",
        "[FUEL_TRACKING_ERROR_HOLD]",
        "tracking_error_hold_active_",
        "planning/tracking_error_stop",
    ),
}


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if text.count(old) != 1:
        raise RuntimeError(f"{path}: expected exactly one patch anchor")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def check(root: Path) -> bool:
    missing: list[str] = []
    for relative, markers in MARKERS.items():
        path = root / relative
        if not path.is_file():
            missing.append(f"{relative}:missing_file")
            continue
        text = path.read_text(encoding="utf-8")
        missing.extend(f"{relative}:{marker}" for marker in markers if marker not in text)
    if missing:
        print("FUEL tracking-error recovery patch missing:")
        for item in missing:
            print(f"  {item}")
        return False
    print("FUEL tracking-error recovery patch is present")
    return True


def apply(root: Path) -> None:
    expl_data = root / "exploration_manager/include/exploration_manager/expl_data.h"
    fsm_h = root / "exploration_manager/include/exploration_manager/fast_exploration_fsm.h"
    fsm_cpp = root / "exploration_manager/src/fast_exploration_fsm.cpp"
    traj_server = root / "plan_manage/src/traj_server.cpp"

    replace_once(
        expl_data,
        "  double emergency_stop_margin_;\n",
        "  double emergency_stop_margin_;\n"
        "  bool tracking_error_recovery_enabled_;\n"
        "  double tracking_error_xy_limit_;\n"
        "  double tracking_error_persistence_s_;\n",
    )
    replace_once(
        fsm_h,
        "  ros::Time replan_start_time_;\n",
        "  ros::Time replan_start_time_;\n"
        "  ros::Time tracking_error_exceeded_since_;\n"
        "  unsigned int tracking_error_recovery_count_;\n",
    )
    replace_once(
        fsm_h,
        "  ros::Publisher replan_pub_, emergency_stop_pub_, new_pub_, bspline_pub_;\n",
        "  ros::Publisher replan_pub_, emergency_stop_pub_, tracking_error_stop_pub_, "
        "new_pub_, bspline_pub_;\n",
    )
    replace_once(
        fsm_cpp,
        "  nh.param(\"fsm/emergency_stop_margin\", fp_->emergency_stop_margin_, 0.35);\n",
        "  nh.param(\"fsm/emergency_stop_margin\", fp_->emergency_stop_margin_, 0.35);\n"
        "  nh.param(\"fsm/tracking_error_recovery_enabled\",\n"
        "      fp_->tracking_error_recovery_enabled_, true);\n"
        "  nh.param(\"fsm/tracking_error_xy_limit\", fp_->tracking_error_xy_limit_, 1.0);\n"
        "  nh.param(\"fsm/tracking_error_persistence_s\",\n"
        "      fp_->tracking_error_persistence_s_, 0.2);\n",
    )
    replace_once(
        fsm_cpp,
        "  fd_->trigger_ = false;\n",
        "  fd_->trigger_ = false;\n"
        "  tracking_error_exceeded_since_ = ros::Time(0);\n"
        "  tracking_error_recovery_count_ = 0;\n",
    )
    replace_once(
        fsm_cpp,
        "  emergency_stop_pub_ =\n"
        "      nh.advertise<std_msgs::Empty>(\"/planning/emergency_stop\", 10);\n",
        "  emergency_stop_pub_ =\n"
        "      nh.advertise<std_msgs::Empty>(\"/planning/emergency_stop\", 10);\n"
        "  tracking_error_stop_pub_ =\n"
        "      nh.advertise<std_msgs::Empty>(\"/planning/tracking_error_stop\", 10);\n",
    )

    old_safety = r'''void FastExplorationFSM::safetyCallback(const ros::TimerEvent& e) {
  if (state_ == EXPL_STATE::EXEC_TRAJ) {
    double dist;
    bool safe = planner_manager_->checkTrajCollision(dist);
    if (!safe) {
      const double speed = fd_->odom_vel_.norm();
      const double deceleration = std::max(0.1, fp_->emergency_stop_deceleration_);
      const double braking_distance =
          speed * speed / (2.0 * deceleration) + std::max(0.0, fp_->emergency_stop_margin_);
      if (fp_->emergency_stop_enabled_ && dist <= braking_distance) {
        ROS_ERROR("[FUEL_EMERGENCY_STOP] collision_distance=%.6f speed=%.6f "
                  "braking_distance=%.6f",
            dist, speed, braking_distance);
        emergency_stop_pub_.publish(std_msgs::Empty());
        fd_->static_state_ = true;
      } else {
        ROS_WARN("[FUEL_COLLISION_REPLAN] collision_distance=%.6f speed=%.6f "
                 "braking_distance=%.6f",
            dist, speed, braking_distance);
      }
      transitState(PLAN_TRAJ, "safetyCallback");
    }
  }
}
'''
    new_safety = r'''void FastExplorationFSM::safetyCallback(const ros::TimerEvent& e) {
  if (state_ != EXPL_STATE::EXEC_TRAJ) {
    tracking_error_exceeded_since_ = ros::Time(0);
    return;
  }

  if (fp_->tracking_error_recovery_enabled_) {
    LocalTrajData* info = &planner_manager_->local_data_;
    const ros::Time now = ros::Time::now();
    const double requested_t = (now - info->start_time_).toSec();
    const double sample_t = std::max(0.0, std::min(requested_t, info->duration_));
    const Eigen::Vector3d commanded = info->position_traj_.evaluateDeBoorT(sample_t);
    const double tracking_xy = (commanded.head<2>() - fd_->odom_pos_.head<2>()).norm();
    const double limit = std::max(0.1, fp_->tracking_error_xy_limit_);
    const double persistence = std::max(0.0, fp_->tracking_error_persistence_s_);

    if (!std::isfinite(tracking_xy) || tracking_xy > limit) {
      if (tracking_error_exceeded_since_.isZero()) tracking_error_exceeded_since_ = now;
      const double elapsed = (now - tracking_error_exceeded_since_).toSec();
      ROS_WARN_THROTTLE(0.5,
          "[FUEL_TRACKING_ERROR_WARN] active_id=%d xy=%.6f limit=%.6f elapsed=%.6f "
          "sample_t=%.6f speed=%.6f command=(%.6f,%.6f,%.6f) "
          "odom=(%.6f,%.6f,%.6f)",
          info->traj_id_, tracking_xy, limit, elapsed, sample_t, fd_->odom_vel_.norm(),
          commanded.x(), commanded.y(), commanded.z(), fd_->odom_pos_.x(),
          fd_->odom_pos_.y(), fd_->odom_pos_.z());
      if (!std::isfinite(tracking_xy) || elapsed >= persistence) {
        ++tracking_error_recovery_count_;
        ROS_ERROR("[FUEL_TRACKING_ERROR_RECOVERY] count=%u active_id=%d xy=%.6f "
                  "limit=%.6f persistence=%.6f speed=%.6f",
            tracking_error_recovery_count_, info->traj_id_, tracking_xy, limit,
            persistence, fd_->odom_vel_.norm());
        tracking_error_stop_pub_.publish(std_msgs::Empty());
        fd_->static_state_ = true;
        tracking_error_exceeded_since_ = ros::Time(0);
        transitState(PLAN_TRAJ, "trackingErrorRecovery");
        return;
      }
    } else {
      tracking_error_exceeded_since_ = ros::Time(0);
    }
  }

  double dist;
  bool safe = planner_manager_->checkTrajCollision(dist);
  if (!safe) {
    const double speed = fd_->odom_vel_.norm();
    const double deceleration = std::max(0.1, fp_->emergency_stop_deceleration_);
    const double braking_distance =
        speed * speed / (2.0 * deceleration) + std::max(0.0, fp_->emergency_stop_margin_);
    if (fp_->emergency_stop_enabled_ && dist <= braking_distance) {
      ROS_ERROR("[FUEL_EMERGENCY_STOP] collision_distance=%.6f speed=%.6f "
                "braking_distance=%.6f",
          dist, speed, braking_distance);
      emergency_stop_pub_.publish(std_msgs::Empty());
      fd_->static_state_ = true;
    } else {
      ROS_WARN("[FUEL_COLLISION_REPLAN] collision_distance=%.6f speed=%.6f "
               "braking_distance=%.6f",
          dist, speed, braking_distance);
    }
    transitState(PLAN_TRAJ, "safetyCallback");
  }
}
'''
    replace_once(fsm_cpp, old_safety, new_safety)

    replace_once(
        traj_server,
        "bool align_start_time_to_receive_;\n",
        "bool align_start_time_to_receive_;\n"
        "bool tracking_error_hold_active_ = false;\n"
        "Eigen::Vector3d tracking_error_hold_pos_;\n"
        "double tracking_error_hold_yaw_ = 0.0;\n",
    )
    replace_once(
        traj_server,
        "void replanCallback(std_msgs::Empty msg) {\n",
        r'''void trackingErrorStopCallback(std_msgs::Empty msg) {
  if (!receive_traj_) return;
  tracking_error_hold_pos_ = Eigen::Vector3d(
      odom.pose.pose.position.x, odom.pose.pose.position.y, odom.pose.pose.position.z);
  tracking_error_hold_yaw_ = cmd.yaw;
  tracking_error_hold_active_ = true;
  const Eigen::Vector3d previous_cmd(cmd.position.x, cmd.position.y, cmd.position.z);
  ROS_ERROR("[FUEL_TRACKING_ERROR_HOLD] active_id=%d command_to_odom=%.6f "
            "hold=(%.6f,%.6f,%.6f) yaw=%.6f",
      traj_id_, (previous_cmd - tracking_error_hold_pos_).norm(),
      tracking_error_hold_pos_.x(), tracking_error_hold_pos_.y(),
      tracking_error_hold_pos_.z(), tracking_error_hold_yaw_);
}

void replanCallback(std_msgs::Empty msg) {
''',
    )
    replace_once(
        traj_server,
        "  receive_traj_ = true;\n\n  // Record the start time of flight\n",
        "  if (tracking_error_hold_active_) {\n"
        "    ROS_WARN(\"[FUEL_TRACKING_ERROR_HOLD_RELEASE] new_id=%d\", traj_id_);\n"
        "  }\n"
        "  tracking_error_hold_active_ = false;\n"
        "  receive_traj_ = true;\n\n"
        "  // Record the start time of flight\n",
    )
    replace_once(
        traj_server,
        "  if (t_cur < traj_duration_ && t_cur >= 0.0) {\n",
        "  if (tracking_error_hold_active_) {\n"
        "    pos = tracking_error_hold_pos_;\n"
        "    vel.setZero();\n"
        "    acc.setZero();\n"
        "    jer.setZero();\n"
        "    yaw = tracking_error_hold_yaw_;\n"
        "    yawdot = 0.0;\n"
        "  } else if (t_cur < traj_duration_ && t_cur >= 0.0) {\n",
    )
    replace_once(
        traj_server,
        "  ros::Subscriber emergency_stop_sub =\n"
        "      node.subscribe(\"planning/emergency_stop\", 10, emergencyStopCallback);\n",
        "  ros::Subscriber emergency_stop_sub =\n"
        "      node.subscribe(\"planning/emergency_stop\", 10, emergencyStopCallback);\n"
        "  ros::Subscriber tracking_error_stop_sub =\n"
        "      node.subscribe(\"planning/tracking_error_stop\", 10, trackingErrorStopCallback);\n",
    )

    old_hold_callbacks = r'''void emergencyStopCallback(std_msgs::Empty msg) {
  if (!receive_traj_) return;
  const double t_now = (ros::Time::now() - start_time_).toSec();
  const double t_stop = std::max(0.0, std::min(t_now, traj_duration_));
  traj_duration_ = std::min(t_stop, traj_duration_);
  ROS_ERROR("[FUEL_TRAJ_SERVER_EMERGENCY_STOP] hold trajectory %d at t=%.6f",
      traj_id_, traj_duration_);
}

void trackingErrorStopCallback(std_msgs::Empty msg) {
  if (!receive_traj_) return;
  tracking_error_hold_pos_ = Eigen::Vector3d(
      odom.pose.pose.position.x, odom.pose.pose.position.y, odom.pose.pose.position.z);
  tracking_error_hold_yaw_ = cmd.yaw;
  tracking_error_hold_active_ = true;
  const Eigen::Vector3d previous_cmd(cmd.position.x, cmd.position.y, cmd.position.z);
  ROS_ERROR("[FUEL_TRACKING_ERROR_HOLD] active_id=%d command_to_odom=%.6f "
            "hold=(%.6f,%.6f,%.6f) yaw=%.6f",
      traj_id_, (previous_cmd - tracking_error_hold_pos_).norm(),
      tracking_error_hold_pos_.x(), tracking_error_hold_pos_.y(),
      tracking_error_hold_pos_.z(), tracking_error_hold_yaw_);
}
'''
    new_hold_callbacks = r'''void activateOdomHold(const char* reason) {
  if (!receive_traj_) return;
  tracking_error_hold_pos_ = Eigen::Vector3d(
      odom.pose.pose.position.x, odom.pose.pose.position.y, odom.pose.pose.position.z);
  tracking_error_hold_yaw_ = cmd.yaw;
  tracking_error_hold_active_ = true;
  const Eigen::Vector3d previous_cmd(cmd.position.x, cmd.position.y, cmd.position.z);
  ROS_ERROR("[FUEL_ODOM_HOLD] reason=%s active_id=%d command_to_odom=%.6f "
            "hold=(%.6f,%.6f,%.6f) yaw=%.6f",
      reason, traj_id_, (previous_cmd - tracking_error_hold_pos_).norm(),
      tracking_error_hold_pos_.x(), tracking_error_hold_pos_.y(),
      tracking_error_hold_pos_.z(), tracking_error_hold_yaw_);
}

void emergencyStopCallback(std_msgs::Empty msg) {
  activateOdomHold("emergency_stop");
}

void trackingErrorStopCallback(std_msgs::Empty msg) {
  activateOdomHold("tracking_error");
  ROS_ERROR("[FUEL_TRACKING_ERROR_HOLD] active_id=%d", traj_id_);
}
'''
    replace_once(traj_server, old_hold_callbacks, new_hold_callbacks)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.fuel_source_root.resolve()
    if args.check:
        return 0 if check(root) else 1
    apply(root)
    return 0 if check(root) else 1


if __name__ == "__main__":
    raise SystemExit(main())
