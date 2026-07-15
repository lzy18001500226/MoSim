#!/usr/bin/env python3
"""Add bounded unreachable-frontier fallback to the patched FUEL manager."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(path: Path, old: str, new: str, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    if old not in text:
        raise RuntimeError(f"{path}: expected patch anchor not found")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_if_present(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old in text:
        path.write_text(text.replace(old, new, 1), encoding="utf-8")


def apply(root: Path) -> None:
    expl_data = root / "exploration_manager/include/exploration_manager/expl_data.h"
    manager_h = (
        root
        / "exploration_manager/include/exploration_manager/fast_exploration_manager.h"
    )
    manager_cpp = root / "exploration_manager/src/fast_exploration_manager.cpp"

    # Upgrade the first bounded-retry revision without requiring a clean source tree.
    replace_if_present(
        manager_cpp,
        "  const int retry_limit = std::min(\n"
        "      static_cast<int>(trajectory_candidate_positions.size()),\n"
        "      std::max(1, ep_->unreachable_recovery_retry_limit_));\n",
        "  const int retry_limit = std::max(1, ep_->unreachable_recovery_retry_limit_);\n",
    )
    replace_if_present(
        manager_cpp,
        "  for (int rank = 0; rank < retry_limit; ++rank) {\n",
        "  for (int rank = 0;\n"
        "       rank < static_cast<int>(trajectory_candidate_positions.size()) &&\n"
        "       attempted < retry_limit; ++rank) {\n",
    )

    replace_once(
        expl_data,
        "  double collision_recovery_min_progress_;\n",
        "  double collision_recovery_min_progress_;\n"
        "  bool unreachable_recovery_enable_;\n"
        "  double unreachable_recovery_radius_;\n"
        "  double unreachable_recovery_duration_;\n"
        "  int unreachable_recovery_max_entries_;\n"
        "  int unreachable_recovery_retry_limit_;\n",
        "unreachable_recovery_retry_limit_",
    )

    replace_once(
        manager_h,
        "  vector<CollisionBackoffTarget> collision_backoff_targets_;\n"
        "  bool isCollisionBackoffTarget(const Vector3d& point) const;\n"
        "  void recordCollisionRejectedTarget(const Vector3d& point);\n"
        "  void applyCollisionBackoff(vector<int>& indices, const Vector3d& current_pos);\n\n",
        "  vector<CollisionBackoffTarget> collision_backoff_targets_;\n"
        "  bool isCollisionBackoffTarget(const Vector3d& point) const;\n"
        "  void recordCollisionRejectedTarget(const Vector3d& point);\n"
        "  void applyCollisionBackoff(vector<int>& indices, const Vector3d& current_pos);\n\n"
        "  struct UnreachableBackoffTarget {\n"
        "    Vector3d point;\n"
        "    ros::Time expires_at;\n"
        "    int rejection_count;\n"
        "  };\n\n"
        "  vector<UnreachableBackoffTarget> unreachable_backoff_targets_;\n"
        "  bool isUnreachableBackoffTarget(const Vector3d& point) const;\n"
        "  void recordUnreachableTarget(const Vector3d& point);\n",
        "struct UnreachableBackoffTarget",
    )

    replace_once(
        manager_cpp,
        "  nh.param(\"exploration/collision_recovery_min_progress\",\n"
        "      ep_->collision_recovery_min_progress_, 0.10);\n",
        "  nh.param(\"exploration/collision_recovery_min_progress\",\n"
        "      ep_->collision_recovery_min_progress_, 0.10);\n"
        "  nh.param(\"exploration/unreachable_recovery_enable\",\n"
        "      ep_->unreachable_recovery_enable_, true);\n"
        "  nh.param(\"exploration/unreachable_recovery_radius\",\n"
        "      ep_->unreachable_recovery_radius_, 0.75);\n"
        "  nh.param(\"exploration/unreachable_recovery_duration\",\n"
        "      ep_->unreachable_recovery_duration_, 8.0);\n"
        "  nh.param(\"exploration/unreachable_recovery_max_entries\",\n"
        "      ep_->unreachable_recovery_max_entries_, 12);\n"
        "  nh.param(\"exploration/unreachable_recovery_retry_limit\",\n"
        "      ep_->unreachable_recovery_retry_limit_, 8);\n",
        '"exploration/unreachable_recovery_retry_limit"',
    )

    methods = r'''bool FastExplorationManager::isUnreachableBackoffTarget(
    const Vector3d& point) const {
  if (!ep_->unreachable_recovery_enable_) return false;
  const ros::Time now = ros::Time::now();
  const double radius = std::max(0.1, ep_->unreachable_recovery_radius_);
  for (const auto& target : unreachable_backoff_targets_) {
    if (target.expires_at > now && (target.point - point).head<2>().norm() <= radius)
      return true;
  }
  return false;
}

void FastExplorationManager::recordUnreachableTarget(const Vector3d& point) {
  if (!ep_->unreachable_recovery_enable_) return;
  const ros::Time now = ros::Time::now();
  const ros::Duration duration(std::max(1.0, ep_->unreachable_recovery_duration_));
  const double radius = std::max(0.1, ep_->unreachable_recovery_radius_);
  unreachable_backoff_targets_.erase(
      std::remove_if(unreachable_backoff_targets_.begin(), unreachable_backoff_targets_.end(),
          [&](const UnreachableBackoffTarget& item) { return item.expires_at <= now; }),
      unreachable_backoff_targets_.end());

  for (auto& target : unreachable_backoff_targets_) {
    if ((target.point - point).head<2>().norm() <= radius) {
      target.rejection_count += 1;
      target.expires_at = now + duration;
      ROS_WARN("[FUEL_UNREACHABLE_RECORD] repeat point=(%.3f, %.3f, %.3f) "
               "count=%d active=%zu duration=%.3f",
          target.point.x(), target.point.y(), target.point.z(), target.rejection_count,
          unreachable_backoff_targets_.size(), duration.toSec());
      return;
    }
  }

  const int max_entries = std::max(1, ep_->unreachable_recovery_max_entries_);
  if (static_cast<int>(unreachable_backoff_targets_.size()) >= max_entries) {
    auto oldest = std::min_element(unreachable_backoff_targets_.begin(),
        unreachable_backoff_targets_.end(),
        [](const UnreachableBackoffTarget& lhs, const UnreachableBackoffTarget& rhs) {
          return lhs.expires_at < rhs.expires_at;
        });
    unreachable_backoff_targets_.erase(oldest);
  }
  unreachable_backoff_targets_.push_back({point, now + duration, 1});
  ROS_WARN("[FUEL_UNREACHABLE_RECORD] add point=(%.3f, %.3f, %.3f) "
           "active=%zu radius=%.3f duration=%.3f",
      point.x(), point.y(), point.z(), unreachable_backoff_targets_.size(), radius,
      duration.toSec());
}

'''
    replace_once(
        manager_cpp,
        "int FastExplorationManager::planExploreMotion(\n",
        methods + "int FastExplorationManager::planExploreMotion(\n",
        "[FUEL_UNREACHABLE_RECORD]",
    )

    replace_once(
        manager_cpp,
        "  Vector3d next_pos;\n"
        "  double next_yaw;\n",
        "  Vector3d next_pos;\n"
        "  double next_yaw;\n"
        "  vector<int> fallback_frontier_indices;\n",
        "vector<int> fallback_frontier_indices;",
    )

    replace_once(
        manager_cpp,
        "    } else {\n"
        "      // Choose the next viewpoint from global tour\n"
        "      next_pos = ed_->points_[indices[0]];\n"
        "      next_yaw = ed_->yaws_[indices[0]];\n"
        "    }\n"
        "  } else if (ed_->points_.size() == 1) {\n",
        "    } else {\n"
        "      // Choose the next viewpoint from global tour\n"
        "      next_pos = ed_->points_[indices[0]];\n"
        "      next_yaw = ed_->yaws_[indices[0]];\n"
        "    }\n"
        "    fallback_frontier_indices = indices;\n"
        "  } else if (ed_->points_.size() == 1) {\n",
        "fallback_frontier_indices = indices;",
    )

    candidate_block = r'''  vector<Vector3d> trajectory_candidate_positions = {next_pos};
  vector<double> trajectory_candidate_yaws = {next_yaw};
  for (const int id : fallback_frontier_indices) {
    if (id < 0 || id >= static_cast<int>(ed_->points_.size())) continue;
    const Vector3d& candidate = ed_->points_[id];
    bool duplicate = false;
    for (const auto& existing : trajectory_candidate_positions) {
      if ((existing - candidate).norm() <= 1e-3) {
        duplicate = true;
        break;
      }
    }
    if (!duplicate) {
      trajectory_candidate_positions.push_back(candidate);
      trajectory_candidate_yaws.push_back(ed_->yaws_[id]);
    }
  }

'''
    replace_once(
        manager_cpp,
        "  std::cout << \"Next view: \" << next_pos.transpose() << \", \" << next_yaw << std::endl;\n",
        candidate_block
        + "  std::cout << \"Next view: \" << next_pos.transpose() << \", \" << next_yaw << std::endl;\n",
        "vector<Vector3d> trajectory_candidate_positions",
    )

    old_search = (
        "  planner_manager_->path_finder_->reset();\n"
        "  if (planner_manager_->path_finder_->search(pos, next_pos) != Astar::REACH_END) {\n"
        "    ROS_ERROR(\"No path to next viewpoint\");\n"
        "    return FAIL;\n"
        "  }\n"
        "  ed_->path_next_goal_ = planner_manager_->path_finder_->getPath();\n"
    )
    new_search = r'''  const int retry_limit = std::max(1, ep_->unreachable_recovery_retry_limit_);
  bool path_found = false;
  int attempted = 0;
  int skipped_backoff = 0;
  for (int rank = 0;
       rank < static_cast<int>(trajectory_candidate_positions.size()) &&
       attempted < retry_limit; ++rank) {
    const Vector3d& candidate = trajectory_candidate_positions[rank];
    if (retry_limit > 1 && isUnreachableBackoffTarget(candidate)) {
      ++skipped_backoff;
      ROS_WARN("[FUEL_UNREACHABLE_SKIP] rank=%d candidate=(%.3f, %.3f, %.3f)",
          rank, candidate.x(), candidate.y(), candidate.z());
      continue;
    }
    ++attempted;
    planner_manager_->path_finder_->reset();
    if (planner_manager_->path_finder_->search(pos, candidate) != Astar::REACH_END) {
      recordUnreachableTarget(candidate);
      ROS_WARN("[FUEL_UNREACHABLE_RETRY] failed rank=%d candidate=(%.3f, %.3f, %.3f) "
               "attempted=%d limit=%d",
          rank, candidate.x(), candidate.y(), candidate.z(), attempted, retry_limit);
      continue;
    }
    next_pos = candidate;
    next_yaw = trajectory_candidate_yaws[rank];
    ed_->path_next_goal_ = planner_manager_->path_finder_->getPath();
    path_found = true;
    if (rank > 0 || skipped_backoff > 0) {
      ROS_WARN("[FUEL_UNREACHABLE_SELECT] rank=%d candidate=(%.3f, %.3f, %.3f) "
               "attempted=%d skipped_backoff=%d limit=%d",
          rank, next_pos.x(), next_pos.y(), next_pos.z(), attempted, skipped_backoff,
          retry_limit);
    }
    break;
  }
  if (!path_found) {
    ROS_ERROR("No path to any bounded next-viewpoint candidate: attempted=%d "
              "skipped_backoff=%d candidates=%zu limit=%d",
        attempted, skipped_backoff, trajectory_candidate_positions.size(), retry_limit);
    return FAIL;
  }
  if (!ed_->refined_points_.empty()) ed_->refined_points_[0] = next_pos;
'''
    replace_once(
        manager_cpp,
        old_search,
        new_search,
        "[FUEL_UNREACHABLE_SELECT]",
    )

    print(f"Applied FUEL unreachable-frontier recovery to {root}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    args = parser.parse_args()
    apply(args.fuel_source_root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
