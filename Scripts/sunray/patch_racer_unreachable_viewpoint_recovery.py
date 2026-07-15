#!/usr/bin/env python3
"""Add bounded unreachable-viewpoint recovery to the RACER manager."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(path: Path, old: str, new: str, marker: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return False
    if old not in text:
        raise RuntimeError(f"{path}: expected patch anchor not found")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


def apply(root: Path) -> bool:
    manager_h = root / "exploration_manager/include/exploration_manager/fast_exploration_manager.h"
    manager_cpp = root / "exploration_manager/src/fast_exploration_manager.cpp"
    changed = False

    changed |= replace_once(
        manager_h,
        "  ros::ServiceClient tsp_client_, acvrp_client_;\n\n",
        "  ros::ServiceClient tsp_client_, acvrp_client_;\n\n"
        "  struct UnreachableViewpoint {\n"
        "    Vector3d point;\n"
        "    ros::Time expires_at;\n"
        "    int rejection_count;\n"
        "  };\n\n"
        "  vector<UnreachableViewpoint> unreachable_viewpoints_;\n"
        "  bool isUnreachableViewpoint(const Vector3d& point);\n"
        "  void recordUnreachableViewpoint(const Vector3d& point);\n\n",
        "struct UnreachableViewpoint",
    )

    changed |= replace_once(
        manager_cpp,
        "#include <thread>\n",
        "#include <thread>\n#include <algorithm>\n",
        "#include <algorithm>",
    )

    helper_methods = r'''bool FastExplorationManager::isUnreachableViewpoint(const Vector3d& point) {
  const ros::Time now = ros::Time::now();
  const double radius = 0.75;
  unreachable_viewpoints_.erase(
      std::remove_if(unreachable_viewpoints_.begin(), unreachable_viewpoints_.end(),
          [&](const UnreachableViewpoint& item) { return item.expires_at <= now; }),
      unreachable_viewpoints_.end());
  for (const auto& item : unreachable_viewpoints_) {
    if ((item.point - point).norm() <= radius) return true;
  }
  return false;
}

void FastExplorationManager::recordUnreachableViewpoint(const Vector3d& point) {
  const ros::Time now = ros::Time::now();
  const ros::Duration duration(8.0);
  const double radius = 0.75;
  for (auto& item : unreachable_viewpoints_) {
    if ((item.point - point).norm() <= radius) {
      item.expires_at = now + duration;
      item.rejection_count += 1;
      return;
    }
  }
  if (unreachable_viewpoints_.size() >= 12) {
    auto oldest = std::min_element(unreachable_viewpoints_.begin(), unreachable_viewpoints_.end(),
        [](const UnreachableViewpoint& lhs, const UnreachableViewpoint& rhs) {
          return lhs.expires_at < rhs.expires_at;
        });
    unreachable_viewpoints_.erase(oldest);
  }
  unreachable_viewpoints_.push_back({point, now + duration, 1});
}

'''
    changed |= replace_once(
        manager_cpp,
        "int FastExplorationManager::planExploreMotion(\n",
        helper_methods + "int FastExplorationManager::planExploreMotion(\n",
        "[RACER_UNREACHABLE_RETRY]",
    )

    old_selection = r'''  std::cout << "Next view: " << next_pos.transpose() << ", " << next_yaw << std::endl;
  ed_->next_pos_ = next_pos;
  ed_->next_yaw_ = next_yaw;

  if (planTrajToView(pos, vel, acc, yaw, next_pos, next_yaw) == FAIL) {
    return FAIL;
  }
'''
    new_selection = r'''  vector<pair<Vector3d, double>> candidates;
  auto append_candidate = [&](const Vector3d& point, const double candidate_yaw) {
    for (const auto& existing : candidates) {
      if ((existing.first - point).norm() <= 0.20) return;
    }
    candidates.push_back({point, candidate_yaw});
  };
  append_candidate(next_pos, next_yaw);

  for (int i = 0; i < static_cast<int>(ed_->refined_points_.size()); ++i) {
    double candidate_yaw = next_yaw;
    if (i < static_cast<int>(ed_->refined_views_.size())) {
      const Vector3d direction = ed_->refined_views_[i] - ed_->refined_points_[i];
      if (direction.head<2>().norm() > 1e-3)
        candidate_yaw = atan2(direction.y(), direction.x());
    }
    append_candidate(ed_->refined_points_[i], candidate_yaw);
  }

  for (int group = 0; group < static_cast<int>(ed_->n_points_.size()); ++group) {
    int frontier_id = group < static_cast<int>(ed_->refined_ids_.size())
                          ? ed_->refined_ids_[group]
                          : -1;
    for (const auto& point : ed_->n_points_[group]) {
      double candidate_yaw = next_yaw;
      if (frontier_id >= 0 && frontier_id < static_cast<int>(ed_->averages_.size())) {
        const Vector3d direction = ed_->averages_[frontier_id] - point;
        if (direction.head<2>().norm() > 1e-3)
          candidate_yaw = atan2(direction.y(), direction.x());
      }
      append_candidate(point, candidate_yaw);
    }
  }

  for (const int frontier_id : frontier_ids) {
    if (frontier_id < 0 || frontier_id >= static_cast<int>(ed_->points_.size())) continue;
    append_candidate(ed_->points_[frontier_id], ed_->yaws_[frontier_id]);
  }

  if (candidates.size() <= 1) {
    vector<pair<double, int>> nearest_frontiers;
    for (int frontier_id = 0; frontier_id < static_cast<int>(ed_->points_.size()); ++frontier_id) {
      nearest_frontiers.push_back({(ed_->points_[frontier_id] - pos).norm(), frontier_id});
    }
    std::sort(nearest_frontiers.begin(), nearest_frontiers.end());
    for (const auto& item : nearest_frontiers) {
      append_candidate(ed_->points_[item.second], ed_->yaws_[item.second]);
    }
    ROS_WARN("[RACER_ALL_FRONTIER_FALLBACK] drone=%d candidates=%zu",
        ep_->drone_id_, candidates.size());
  }

  const bool optimistic = ed_->plan_num_ < ep_->init_plan_num_;
  const int attempt_limit = 8;
  int attempted = 0;
  int skipped_backoff = 0;
  int selected_rank = -1;
  Eigen::Vector3d map_origin, map_size;
  sdf_map_->getRegion(map_origin, map_size);
  for (int rank = 0;
       rank < static_cast<int>(candidates.size()) && attempted < attempt_limit; ++rank) {
    const auto& candidate = candidates[rank];
    if (isUnreachableViewpoint(candidate.first)) {
      ++skipped_backoff;
      continue;
    }
    ++attempted;
    planner_manager_->path_finder_->reset();
    const int search_result =
        planner_manager_->path_finder_->search(pos, candidate.first, optimistic);
    if (search_result != Astar::REACH_END) {
      recordUnreachableViewpoint(candidate.first);
      ROS_WARN("[RACER_UNREACHABLE_RETRY] drone=%d rank=%d attempted=%d/%d "
               "start=(%.3f,%.3f,%.3f) target=(%.3f,%.3f,%.3f) distance=%.3f "
               "start_occ=%d target_occ=%d map_min=(%.3f,%.3f,%.3f) "
               "map_max=(%.3f,%.3f,%.3f) candidates=%zu",
          ep_->drone_id_, rank, attempted, attempt_limit, pos.x(), pos.y(), pos.z(),
          candidate.first.x(), candidate.first.y(), candidate.first.z(),
          (candidate.first - pos).norm(), static_cast<int>(sdf_map_->getOccupancy(pos)),
          static_cast<int>(sdf_map_->getOccupancy(candidate.first)), map_origin.x(),
          map_origin.y(), map_origin.z(), map_origin.x() + map_size.x(),
          map_origin.y() + map_size.y(), map_origin.z() + map_size.z(), candidates.size());
      continue;
    }
    next_pos = candidate.first;
    next_yaw = candidate.second;
    selected_rank = rank;
    break;
  }

  if (selected_rank < 0) {
    ROS_ERROR("No path to next viewpoint after bounded fallback: drone=%d attempted=%d "
              "skipped_backoff=%d candidates=%zu limit=%d",
        ep_->drone_id_, attempted, skipped_backoff, candidates.size(), attempt_limit);
    return FAIL;
  }
  if (selected_rank > 0 || skipped_backoff > 0) {
    ROS_WARN("[RACER_UNREACHABLE_SELECT] drone=%d rank=%d attempted=%d "
             "skipped_backoff=%d target=(%.3f,%.3f,%.3f) candidates=%zu",
        ep_->drone_id_, selected_rank, attempted, skipped_backoff, next_pos.x(),
        next_pos.y(), next_pos.z(), candidates.size());
  }

  std::cout << "Next view: " << next_pos.transpose() << ", " << next_yaw << std::endl;
  ed_->next_pos_ = next_pos;
  ed_->next_yaw_ = next_yaw;

  if (planTrajToView(pos, vel, acc, yaw, next_pos, next_yaw) == FAIL) {
    return FAIL;
  }
'''
    changed |= replace_once(
        manager_cpp,
        old_selection,
        new_selection,
        "[RACER_UNREACHABLE_SELECT]",
    )

    changed |= replace_once(
        manager_cpp,
        "  for (const int frontier_id : frontier_ids) {\n"
        "    if (frontier_id < 0 || frontier_id >= static_cast<int>(ed_->points_.size())) continue;\n"
        "    append_candidate(ed_->points_[frontier_id], ed_->yaws_[frontier_id]);\n"
        "  }\n\n"
        "  const bool optimistic = ed_->plan_num_ < ep_->init_plan_num_;\n",
        "  for (const int frontier_id : frontier_ids) {\n"
        "    if (frontier_id < 0 || frontier_id >= static_cast<int>(ed_->points_.size())) continue;\n"
        "    append_candidate(ed_->points_[frontier_id], ed_->yaws_[frontier_id]);\n"
        "  }\n\n"
        "  if (candidates.size() <= 1) {\n"
        "    vector<pair<double, int>> nearest_frontiers;\n"
        "    for (int frontier_id = 0; frontier_id < static_cast<int>(ed_->points_.size()); ++frontier_id) {\n"
        "      nearest_frontiers.push_back({(ed_->points_[frontier_id] - pos).norm(), frontier_id});\n"
        "    }\n"
        "    std::sort(nearest_frontiers.begin(), nearest_frontiers.end());\n"
        "    for (const auto& item : nearest_frontiers) {\n"
        "      append_candidate(ed_->points_[item.second], ed_->yaws_[item.second]);\n"
        "    }\n"
        "    ROS_WARN(\"[RACER_ALL_FRONTIER_FALLBACK] drone=%d candidates=%zu\",\n"
        "        ep_->drone_id_, candidates.size());\n"
        "  }\n\n"
        "  const bool optimistic = ed_->plan_num_ < ep_->init_plan_num_;\n",
        "[RACER_ALL_FRONTIER_FALLBACK]",
    )

    print(f"RACER unreachable-viewpoint recovery {'applied' if changed else 'already present'}: {root}")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("racer_source_root", type=Path)
    args = parser.parse_args()
    apply(args.racer_source_root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
