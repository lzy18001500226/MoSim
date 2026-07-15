#!/usr/bin/env python3
"""Feed rejected FUEL trajectories back into autonomous frontier selection."""

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


def replace_if_present(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old in text:
        path.write_text(text.replace(old, new, 1), encoding="utf-8")


def apply(root: Path) -> None:
    manager_h = root / "plan_manage/include/plan_manage/planner_manager.h"
    manager_cpp = root / "plan_manage/src/planner_manager.cpp"
    expl_data = root / "exploration_manager/include/exploration_manager/expl_data.h"
    exploration_h = (
        root
        / "exploration_manager/include/exploration_manager/fast_exploration_manager.h"
    )
    exploration_cpp = root / "exploration_manager/src/fast_exploration_manager.cpp"

    legacy_accessor = (
        "  bool lastPlanRejectedForCollision() const {\n"
        "    return last_hard_collision_rejection_;\n"
        "  }\n\n"
    )
    collision_accessor = (
        "  bool lastPlanRejectedForCollision() const {\n"
        "    return last_hard_collision_rejection_;\n"
        "  }\n"
        "  double lastHardCollisionTime() const { return last_hard_collision_time_; }\n"
        "  double lastHardCollisionDuration() const { return last_hard_collision_duration_; }\n"
        "  double lastHardCollisionProgress() const {\n"
        "    return last_hard_collision_duration_ > 1e-9\n"
        "        ? last_hard_collision_time_ / last_hard_collision_duration_\n"
        "        : 0.0;\n"
        "  }\n"
        "  int lastHardCollisionRawOccupancy() const {\n"
        "    return last_hard_collision_raw_occupancy_;\n"
        "  }\n"
        "  double lastHardCollisionDistance() const { return last_hard_collision_distance_; }\n"
        "  const Eigen::Vector3d& lastHardCollisionPoint() const {\n"
        "    return last_hard_collision_point_;\n"
        "  }\n\n"
    )
    replace_if_present(manager_h, legacy_accessor, collision_accessor)
    replace_once(
        manager_h,
        "  PlanParameters pp_;\n",
        collision_accessor + "  PlanParameters pp_;\n",
    )
    legacy_fields = "  bool last_hard_collision_rejection_ = false;\n\n"
    collision_fields = (
        "  bool last_hard_collision_rejection_ = false;\n"
        "  double last_hard_collision_time_ = -1.0;\n"
        "  double last_hard_collision_duration_ = 0.0;\n"
        "  int last_hard_collision_raw_occupancy_ = -1;\n"
        "  double last_hard_collision_distance_ = -1.0;\n"
        "  Eigen::Vector3d last_hard_collision_point_ = Eigen::Vector3d::Zero();\n\n"
    )
    replace_if_present(manager_h, legacy_fields, collision_fields)
    replace_once(
        manager_h,
        "  /* main planning algorithms & modules */\n",
        collision_fields + "  /* main planning algorithms & modules */\n",
    )
    replace_once(
        manager_cpp,
        "bool FastPlannerManager::kinodynamicReplan(const Eigen::Vector3d& start_pt,\n"
        "    const Eigen::Vector3d& start_vel, const Eigen::Vector3d& start_acc,\n"
        "    const Eigen::Vector3d& end_pt, const Eigen::Vector3d& end_vel, const double& time_lb) {\n",
        "bool FastPlannerManager::kinodynamicReplan(const Eigen::Vector3d& start_pt,\n"
        "    const Eigen::Vector3d& start_vel, const Eigen::Vector3d& start_acc,\n"
        "    const Eigen::Vector3d& end_pt, const Eigen::Vector3d& end_vel, const double& time_lb) {\n"
        "  last_hard_collision_rejection_ = false;\n"
        "  last_hard_collision_time_ = -1.0;\n"
        "  last_hard_collision_duration_ = 0.0;\n"
        "  last_hard_collision_raw_occupancy_ = -1;\n"
        "  last_hard_collision_distance_ = -1.0;\n",
    )
    replace_once(
        manager_cpp,
        "bool FastPlannerManager::planExploreTraj(const vector<Eigen::Vector3d>& tour,\n"
        "    const Eigen::Vector3d& cur_vel, const Eigen::Vector3d& cur_acc, const double& time_lb) {\n",
        "bool FastPlannerManager::planExploreTraj(const vector<Eigen::Vector3d>& tour,\n"
        "    const Eigen::Vector3d& cur_vel, const Eigen::Vector3d& cur_acc, const double& time_lb) {\n"
        "  last_hard_collision_rejection_ = false;\n"
        "  last_hard_collision_time_ = -1.0;\n"
        "  last_hard_collision_duration_ = 0.0;\n"
        "  last_hard_collision_raw_occupancy_ = -1;\n"
        "  last_hard_collision_distance_ = -1.0;\n",
    )
    legacy_param_fields = (
        "  bool collision_recovery_enable_;\n"
        "  double collision_recovery_radius_;\n"
        "  double collision_recovery_duration_;\n"
        "  int collision_recovery_max_entries_;\n"
    )
    collision_param_fields = (
        legacy_param_fields
        + "  double collision_recovery_min_time_;\n"
        + "  double collision_recovery_min_progress_;\n"
    )
    replace_if_present(expl_data, legacy_param_fields, collision_param_fields)
    replace_once(
        expl_data,
        "  double near_frontier_escape_alternative_distance_;\n",
        "  double near_frontier_escape_alternative_distance_;\n" + collision_param_fields,
    )
    replace_once(
        exploration_h,
        "  shared_ptr<EDTEnvironment> edt_environment_;\n",
        "  struct CollisionBackoffTarget {\n"
        "    Vector3d point;\n"
        "    ros::Time expires_at;\n"
        "    int rejection_count;\n"
        "  };\n\n"
        "  vector<CollisionBackoffTarget> collision_backoff_targets_;\n"
        "  bool isCollisionBackoffTarget(const Vector3d& point) const;\n"
        "  void recordCollisionRejectedTarget(const Vector3d& point);\n"
        "  void applyCollisionBackoff(vector<int>& indices, const Vector3d& current_pos);\n\n"
        "  shared_ptr<EDTEnvironment> edt_environment_;\n",
    )
    legacy_param_load = (
        "  nh.param(\"exploration/collision_recovery_enable\",\n"
        "      ep_->collision_recovery_enable_, true);\n"
        "  nh.param(\"exploration/collision_recovery_radius\",\n"
        "      ep_->collision_recovery_radius_, 2.5);\n"
        "  nh.param(\"exploration/collision_recovery_duration\",\n"
        "      ep_->collision_recovery_duration_, 30.0);\n"
        "  nh.param(\"exploration/collision_recovery_max_entries\",\n"
        "      ep_->collision_recovery_max_entries_, 32);\n"
    )
    collision_param_load = (
        "  nh.param(\"exploration/collision_recovery_enable\",\n"
        "      ep_->collision_recovery_enable_, true);\n"
        "  nh.param(\"exploration/collision_recovery_radius\",\n"
        "      ep_->collision_recovery_radius_, 0.75);\n"
        "  nh.param(\"exploration/collision_recovery_duration\",\n"
        "      ep_->collision_recovery_duration_, 8.0);\n"
        "  nh.param(\"exploration/collision_recovery_max_entries\",\n"
        "      ep_->collision_recovery_max_entries_, 12);\n"
        "  nh.param(\"exploration/collision_recovery_min_time\",\n"
        "      ep_->collision_recovery_min_time_, 0.30);\n"
        "  nh.param(\"exploration/collision_recovery_min_progress\",\n"
        "      ep_->collision_recovery_min_progress_, 0.10);\n"
    )
    replace_if_present(exploration_cpp, legacy_param_load, collision_param_load)
    replace_once(
        exploration_cpp,
        "  nh.param(\n"
        "      \"exploration/near_frontier_escape_alternative_distance\",\n"
        "      ep_->near_frontier_escape_alternative_distance_, 2.0);\n",
        "  nh.param(\n"
        "      \"exploration/near_frontier_escape_alternative_distance\",\n"
        "      ep_->near_frontier_escape_alternative_distance_, 2.0);\n"
        + collision_param_load,
    )

    recovery_methods = r'''bool FastExplorationManager::isCollisionBackoffTarget(
    const Vector3d& point) const {
  if (!ep_->collision_recovery_enable_) return false;
  const ros::Time now = ros::Time::now();
  const double radius = std::max(0.1, ep_->collision_recovery_radius_);
  for (const auto& target : collision_backoff_targets_) {
    if (target.expires_at > now && (target.point - point).head<2>().norm() <= radius)
      return true;
  }
  return false;
}

void FastExplorationManager::recordCollisionRejectedTarget(const Vector3d& point) {
  if (!ep_->collision_recovery_enable_) return;
  const double collision_time = planner_manager_->lastHardCollisionTime();
  const double collision_progress = planner_manager_->lastHardCollisionProgress();
  if (collision_time < ep_->collision_recovery_min_time_ ||
      collision_progress < ep_->collision_recovery_min_progress_) {
    const Vector3d& collision_point = planner_manager_->lastHardCollisionPoint();
    ROS_WARN("[FUEL_COLLISION_RECOVERY_SKIP_SHARED_START] target=(%.3f, %.3f, %.3f) "
             "collision_t=%.3f progress=%.3f raw_occupancy=%d distance=%.3f "
             "collision_point=(%.3f, %.3f, %.3f)",
        point.x(), point.y(), point.z(), collision_time, collision_progress,
        planner_manager_->lastHardCollisionRawOccupancy(),
        planner_manager_->lastHardCollisionDistance(), collision_point.x(),
        collision_point.y(), collision_point.z());
    return;
  }
  const ros::Time now = ros::Time::now();
  const ros::Duration duration(std::max(1.0, ep_->collision_recovery_duration_));
  const double radius = std::max(0.1, ep_->collision_recovery_radius_);
  collision_backoff_targets_.erase(
      std::remove_if(collision_backoff_targets_.begin(), collision_backoff_targets_.end(),
          [&](const CollisionBackoffTarget& item) { return item.expires_at <= now; }),
      collision_backoff_targets_.end());

  for (auto& target : collision_backoff_targets_) {
    if ((target.point - point).head<2>().norm() <= radius) {
      target.rejection_count += 1;
      ROS_WARN("[FUEL_COLLISION_RECOVERY_RECORD] repeat point=(%.3f, %.3f, %.3f) "
               "count=%d active=%zu remaining=%.3f",
          target.point.x(), target.point.y(), target.point.z(), target.rejection_count,
          collision_backoff_targets_.size(), (target.expires_at - now).toSec());
      return;
    }
  }

  const int max_entries = std::max(1, ep_->collision_recovery_max_entries_);
  if (static_cast<int>(collision_backoff_targets_.size()) >= max_entries) {
    auto oldest = std::min_element(collision_backoff_targets_.begin(),
        collision_backoff_targets_.end(),
        [](const CollisionBackoffTarget& lhs, const CollisionBackoffTarget& rhs) {
          return lhs.expires_at < rhs.expires_at;
        });
    collision_backoff_targets_.erase(oldest);
  }
  collision_backoff_targets_.push_back({point, now + duration, 1});
  ROS_WARN("[FUEL_COLLISION_RECOVERY_RECORD] add point=(%.3f, %.3f, %.3f) "
           "active=%zu radius=%.3f duration=%.3f",
      point.x(), point.y(), point.z(), collision_backoff_targets_.size(), radius,
      duration.toSec());
}

void FastExplorationManager::applyCollisionBackoff(
    vector<int>& indices, const Vector3d& current_pos) {
  if (!ep_->collision_recovery_enable_ || indices.size() < 2) return;
  const ros::Time now = ros::Time::now();
  collision_backoff_targets_.erase(
      std::remove_if(collision_backoff_targets_.begin(), collision_backoff_targets_.end(),
          [&](const CollisionBackoffTarget& item) { return item.expires_at <= now; }),
      collision_backoff_targets_.end());
  if (collision_backoff_targets_.empty()) return;

  const int original_id = indices.front();
  if (original_id < 0 || original_id >= static_cast<int>(ed_->points_.size()) ||
      !isCollisionBackoffTarget(ed_->points_[original_id]))
    return;

  int alternative_rank = -1;
  for (int rank = 1; rank < static_cast<int>(indices.size()); ++rank) {
    const int id = indices[rank];
    if (id < 0 || id >= static_cast<int>(ed_->points_.size())) continue;
    if (!isCollisionBackoffTarget(ed_->points_[id])) {
      alternative_rank = rank;
      break;
    }
  }
  while (alternative_rank < 0 && !collision_backoff_targets_.empty()) {
    auto release = std::min_element(collision_backoff_targets_.begin(),
        collision_backoff_targets_.end(),
        [](const CollisionBackoffTarget& lhs, const CollisionBackoffTarget& rhs) {
          return lhs.expires_at < rhs.expires_at;
        });
    ROS_WARN("[FUEL_COLLISION_RECOVERY_RELEASE] point=(%.3f, %.3f, %.3f) "
             "count=%d active_before=%zu candidates=%zu",
        release->point.x(), release->point.y(), release->point.z(),
        release->rejection_count, collision_backoff_targets_.size(), indices.size());
    collision_backoff_targets_.erase(release);
    for (int rank = 0; rank < static_cast<int>(indices.size()); ++rank) {
      const int id = indices[rank];
      if (id < 0 || id >= static_cast<int>(ed_->points_.size())) continue;
      if (!isCollisionBackoffTarget(ed_->points_[id])) {
        alternative_rank = rank;
        break;
      }
    }
  }

  if (alternative_rank <= 0) return;

  const int alternative_id = indices[alternative_rank];
  indices.erase(indices.begin() + alternative_rank);
  indices.insert(indices.begin(), alternative_id);
  frontier_finder_->getPathForTour(current_pos, indices, ed_->global_tour_);
  ROS_WARN("[FUEL_COLLISION_RECOVERY_SELECT] original_id=%d original=(%.3f, %.3f, %.3f) "
           "alternative_rank=%d alternative_id=%d alternative=(%.3f, %.3f, %.3f) active=%zu",
      original_id, ed_->points_[original_id].x(), ed_->points_[original_id].y(),
      ed_->points_[original_id].z(), alternative_rank, alternative_id,
      ed_->points_[alternative_id].x(), ed_->points_[alternative_id].y(),
      ed_->points_[alternative_id].z(), collision_backoff_targets_.size());
}

'''
    current_text = exploration_cpp.read_text(encoding="utf-8")
    recovery_start = current_text.find("bool FastExplorationManager::isCollisionBackoffTarget(")
    recovery_end = current_text.find("int FastExplorationManager::planExploreMotion(", recovery_start)
    if recovery_start >= 0 and recovery_end > recovery_start and recovery_methods not in current_text:
        exploration_cpp.write_text(
            current_text[:recovery_start] + recovery_methods + current_text[recovery_end:],
            encoding="utf-8",
        )
    insert_before_once(
        exploration_cpp,
        "int FastExplorationManager::planExploreMotion(\n",
        recovery_methods,
        "[FUEL_COLLISION_RECOVERY_RECORD]",
    )
    insert_before_once(
        exploration_cpp,
        "    if (ep_->global_expansion_bias_enable_ && !indices.empty()) {\n",
        "    applyCollisionBackoff(indices, pos);\n\n",
        "applyCollisionBackoff(indices, pos);",
    )

    replace_once(
        exploration_cpp,
        "    if (!planner_manager_->planExploreTraj(ed_->path_next_goal_, vel, acc, time_lb)) return FAIL;\n",
        "    if (!planner_manager_->planExploreTraj(ed_->path_next_goal_, vel, acc, time_lb)) {\n"
        "      if (planner_manager_->lastPlanRejectedForCollision())\n"
        "        recordCollisionRejectedTarget(next_pos);\n"
        "      return FAIL;\n"
        "    }\n",
    )
    replace_once(
        exploration_cpp,
        "    if (!planner_manager_->planExploreTraj(truncated_path, vel, acc, time_lb)) return FAIL;\n",
        "    if (!planner_manager_->planExploreTraj(truncated_path, vel, acc, time_lb)) {\n"
        "      if (planner_manager_->lastPlanRejectedForCollision())\n"
        "        recordCollisionRejectedTarget(next_pos);\n"
        "      return FAIL;\n"
        "    }\n",
    )
    replace_once(
        exploration_cpp,
        "    if (!planner_manager_->kinodynamicReplan(\n"
        "            pos, vel, acc, ed_->next_goal_, Vector3d(0, 0, 0), time_lb))\n"
        "      return FAIL;\n",
        "    if (!planner_manager_->kinodynamicReplan(\n"
        "            pos, vel, acc, ed_->next_goal_, Vector3d(0, 0, 0), time_lb)) {\n"
        "      if (planner_manager_->lastPlanRejectedForCollision())\n"
        "        recordCollisionRejectedTarget(next_pos);\n"
        "      return FAIL;\n"
        "    }\n",
    )

    print(f"Applied FUEL collision recovery to {root}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    args = parser.parse_args()
    apply(args.fuel_source_root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
