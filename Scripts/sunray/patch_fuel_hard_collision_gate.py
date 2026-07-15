#!/usr/bin/env python3
"""Add hard candidate collision validation and emergency braking to FUEL."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"{path}: expected patch anchor not found")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, addition: str, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    if anchor not in text:
        raise RuntimeError(f"{path}: expected insertion anchor not found")
    path.write_text(text.replace(anchor, addition + anchor, 1), encoding="utf-8")


def apply(root: Path) -> None:
    plan_container = root / "plan_manage/include/plan_manage/plan_container.hpp"
    manager_h = root / "plan_manage/include/plan_manage/planner_manager.h"
    manager_cpp = root / "plan_manage/src/planner_manager.cpp"
    expl_data = root / "exploration_manager/include/exploration_manager/expl_data.h"
    fsm_h = root / "exploration_manager/include/exploration_manager/fast_exploration_fsm.h"
    fsm_cpp = root / "exploration_manager/src/fast_exploration_fsm.cpp"
    traj_server = root / "plan_manage/src/traj_server.cpp"

    replace_once(
        plan_container,
        "  double dynamic_feasibility_max_time_scale_;\n",
        "  double dynamic_feasibility_max_time_scale_;\n"
        "  bool hard_collision_gate_enabled_;\n"
        "  double hard_collision_sample_dt_;\n",
    )
    replace_once(
        manager_h,
        "  void updateTrajInfo();\n",
        "  void updateTrajInfo();\n"
        "  bool validateTrajectoryCollisionFree(\n"
        "      const NonUniformBspline& trajectory, const char* source);\n",
    )
    replace_once(
        manager_h,
        "      const NonUniformBspline& trajectory, const char* source);\n",
        "      NonUniformBspline& trajectory, const char* source);\n",
    )
    replace_once(
        manager_cpp,
        "  nh.param(\"manager/dynamic_feasibility_max_time_scale\",\n"
        "      pp_.dynamic_feasibility_max_time_scale_, 2.0);\n",
        "  nh.param(\"manager/dynamic_feasibility_max_time_scale\",\n"
        "      pp_.dynamic_feasibility_max_time_scale_, 2.0);\n"
        "  nh.param(\"manager/hard_collision_gate_enabled\",\n"
        "      pp_.hard_collision_gate_enabled_, true);\n"
        "  nh.param(\"manager/hard_collision_sample_dt\",\n"
        "      pp_.hard_collision_sample_dt_, 0.02);\n",
    )

    validator = r'''bool FastPlannerManager::validateTrajectoryCollisionFree(
    const NonUniformBspline& trajectory, const char* source) {
  if (!pp_.hard_collision_gate_enabled_) return true;

  const double duration = trajectory.getTimeSum();
  const double sample_dt = std::max(0.005, pp_.hard_collision_sample_dt_);
  for (double t = 0.0; t <= duration + 1e-6; t += sample_dt) {
    const double sample_t = std::min(t, duration);
    Eigen::Vector3d point = trajectory.evaluateDeBoorT(sample_t);
    if (sdf_map_->getInflateOccupancy(point) == 1) {
      last_hard_collision_rejection_ = true;
      last_hard_collision_time_ = sample_t;
      last_hard_collision_duration_ = duration;
      last_hard_collision_point_ = point;
      last_hard_collision_raw_occupancy_ = sdf_map_->getOccupancy(point);
      last_hard_collision_distance_ = sdf_map_->getDistance(point);
      ROS_ERROR("[FUEL_HARD_COLLISION_GATE] source=%s rejected t=%.6f/%.6f "
                "progress=%.6f raw_occupancy=%d distance=%.6f "
                "point=(%.6f, %.6f, %.6f)",
          source, sample_t, duration, duration > 1e-9 ? sample_t / duration : 0.0,
          last_hard_collision_raw_occupancy_, last_hard_collision_distance_,
          point.x(), point.y(), point.z());
      return false;
    }
  }
  return true;
}

'''
    current_text = manager_cpp.read_text(encoding="utf-8")
    validator_start = current_text.find(
        "bool FastPlannerManager::validateTrajectoryCollisionFree("
    )
    validator_end = current_text.find(
        "bool FastPlannerManager::enforceDynamicFeasibility(", validator_start
    )
    if (
        validator_start >= 0
        and validator_end > validator_start
        and "progress=%.6f raw_occupancy=%d distance=%.6f" not in current_text
    ):
        manager_cpp.write_text(
            current_text[:validator_start] + validator + current_text[validator_end:],
            encoding="utf-8",
        )
    insert_before_once(
        manager_cpp,
        "bool FastPlannerManager::enforceDynamicFeasibility(\n",
        validator,
        "[FUEL_HARD_COLLISION_GATE]",
    )
    replace_once(
        manager_cpp,
        "    const NonUniformBspline& trajectory, const char* source) {\n",
        "    NonUniformBspline& trajectory, const char* source) {\n",
    )
    replace_once(
        manager_cpp,
        "    if (enforceDynamicFeasibility(candidate, \"kinodynamicReplan\", &required_time_scale)) {\n",
        "    if (enforceDynamicFeasibility(candidate, \"kinodynamicReplan\", &required_time_scale) &&\n"
        "        validateTrajectoryCollisionFree(candidate, \"kinodynamicReplan\")) {\n",
    )
    replace_once(
        manager_cpp,
        "    if (enforceDynamicFeasibility(candidate, \"planExploreTraj\", &required_time_scale)) {\n",
        "    if (enforceDynamicFeasibility(candidate, \"planExploreTraj\", &required_time_scale) &&\n"
        "        validateTrajectoryCollisionFree(candidate, \"planExploreTraj\")) {\n",
    )

    replace_once(
        expl_data,
        "  double replan_time_;  // second\n",
        "  double replan_time_;  // second\n"
        "  bool emergency_stop_enabled_;\n"
        "  double emergency_stop_deceleration_;\n"
        "  double emergency_stop_margin_;\n",
    )
    replace_once(
        fsm_h,
        "  ros::Publisher replan_pub_, new_pub_, bspline_pub_;\n",
        "  ros::Publisher replan_pub_, emergency_stop_pub_, new_pub_, bspline_pub_;\n",
    )
    replace_once(
        fsm_cpp,
        "  nh.param(\"fsm/replan_time\", fp_->replan_time_, -1.0);\n",
        "  nh.param(\"fsm/replan_time\", fp_->replan_time_, -1.0);\n"
        "  nh.param(\"fsm/emergency_stop_enabled\", fp_->emergency_stop_enabled_, true);\n"
        "  nh.param(\"fsm/emergency_stop_deceleration\",\n"
        "      fp_->emergency_stop_deceleration_, 1.5);\n"
        "  nh.param(\"fsm/emergency_stop_margin\", fp_->emergency_stop_margin_, 0.35);\n",
    )
    replace_once(
        fsm_cpp,
        "  replan_pub_ = nh.advertise<std_msgs::Empty>(\"/planning/replan\", 10);\n",
        "  replan_pub_ = nh.advertise<std_msgs::Empty>(\"/planning/replan\", 10);\n"
        "  emergency_stop_pub_ =\n"
        "      nh.advertise<std_msgs::Empty>(\"/planning/emergency_stop\", 10);\n",
    )
    old_safety = r'''void FastExplorationFSM::safetyCallback(const ros::TimerEvent& e) {
  if (state_ == EXPL_STATE::EXEC_TRAJ) {
    // Check safety and trigger replan if necessary
    double dist;
    bool safe = planner_manager_->checkTrajCollision(dist);
    if (!safe) {
      ROS_WARN("Replan: collision detected==================================");
      transitState(PLAN_TRAJ, "safetyCallback");
    }
  }
}
'''
    new_safety = r'''void FastExplorationFSM::safetyCallback(const ros::TimerEvent& e) {
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
    replace_once(fsm_cpp, old_safety, new_safety)

    emergency_callback = r'''void emergencyStopCallback(std_msgs::Empty msg) {
  if (!receive_traj_) return;
  const double t_now = (ros::Time::now() - start_time_).toSec();
  const double t_stop = std::max(0.0, std::min(t_now, traj_duration_));
  traj_duration_ = std::min(t_stop, traj_duration_);
  ROS_ERROR("[FUEL_TRAJ_SERVER_EMERGENCY_STOP] hold trajectory %d at t=%.6f",
      traj_id_, traj_duration_);
}

'''
    insert_before_once(
        traj_server,
        "void replanCallback(std_msgs::Empty msg) {\n",
        emergency_callback,
        "[FUEL_TRAJ_SERVER_EMERGENCY_STOP]",
    )
    replace_once(
        traj_server,
        "  ros::Subscriber replan_sub = node.subscribe(\"planning/replan\", 10, replanCallback);\n",
        "  ros::Subscriber replan_sub = node.subscribe(\"planning/replan\", 10, replanCallback);\n"
        "  ros::Subscriber emergency_stop_sub =\n"
        "      node.subscribe(\"planning/emergency_stop\", 10, emergencyStopCallback);\n",
    )

    # Normalize workspaces that were patched by the earlier const-signature
    # revision before the validator was changed to accept a mutable spline.
    manager_text = manager_h.read_text(encoding="utf-8")
    duplicate_validator = (
        "  bool validateTrajectoryCollisionFree(\n"
        "      const NonUniformBspline& trajectory, const char* source);\n"
        "  bool validateTrajectoryCollisionFree(\n"
        "      NonUniformBspline& trajectory, const char* source);\n"
    )
    if duplicate_validator in manager_text:
        manager_h.write_text(
            manager_text.replace(
                duplicate_validator,
                "  bool validateTrajectoryCollisionFree(\n"
                "      NonUniformBspline& trajectory, const char* source);\n",
                1,
            ),
            encoding="utf-8",
        )

    print(f"Applied FUEL hard collision gate to {root}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    args = parser.parse_args()
    apply(args.fuel_source_root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
