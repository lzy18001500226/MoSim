#!/usr/bin/env python3
"""Prevent RACER from republishing stale trajectories for reached viewpoints."""

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


def make_plan_explore_traj_fallible(header: Path, source: Path) -> bool:
    changed = False
    changed |= replace_once(
        header,
        "  void planExploreTraj(const vector<Eigen::Vector3d>& tour, const Eigen::Vector3d& cur_vel,\n",
        "  bool planExploreTraj(const vector<Eigen::Vector3d>& tour, const Eigen::Vector3d& cur_vel,\n",
        "bool planExploreTraj(",
    )

    text = source.read_text(encoding="utf-8")
    marker = "[RACER_TRAJ_GENERATION_FAILED]"
    if marker in text:
        return changed

    start_anchor = "void FastPlannerManager::planExploreTraj("
    end_anchor = "\n// !SECTION\n\n// SECTION topological replanning"
    start = text.find(start_anchor)
    end = text.find(end_anchor, start)
    if start < 0 or end < 0:
        raise RuntimeError(f"{source}: planExploreTraj function boundaries not found")

    function = text[start:end]
    function = function.replace(
        start_anchor, "bool FastPlannerManager::planExploreTraj(", 1
    )
    if "return;" not in function:
        raise RuntimeError(f"{source}: no fallible early returns found in planExploreTraj")
    function = function.replace("return;", "return false;")
    closing = "  updateTrajInfo();\n}"
    if closing not in function:
        raise RuntimeError(f"{source}: planExploreTraj closing anchor not found")
    function = function.replace(
        closing,
        '  updateTrajInfo();\n'
        '  ROS_DEBUG("[RACER_TRAJ_GENERATION_FAILED] status=success traj_id=%d",\n'
        "      local_data_.traj_id_);\n"
        "  return true;\n}",
        1,
    )
    source.write_text(text[:start] + function + text[end:], encoding="utf-8")
    return True


def patch_manager_callers(source: Path) -> bool:
    changed = False
    changed |= replace_once(
        source,
        "    planner_manager_->planExploreTraj(ed_->path_next_goal_, vel, acc, time_lb);\n"
        "    ed_->next_goal_ = next_pos;\n",
        "    if (!planner_manager_->planExploreTraj(\n"
        "            ed_->path_next_goal_, vel, acc, time_lb)) {\n"
        "      ROS_WARN(\"[RACER_TRAJ_GENERATION_FAILED] close viewpoint trajectory rejected\");\n"
        "      return FAIL;\n"
        "    }\n"
        "    ed_->next_goal_ = next_pos;\n",
        "close viewpoint trajectory rejected",
    )
    changed |= replace_once(
        source,
        "    ed_->next_goal_ = truncated_path.back();\n"
        "    planner_manager_->planExploreTraj(truncated_path, vel, acc, time_lb);\n",
        "    ed_->next_goal_ = truncated_path.back();\n"
        "    if (!planner_manager_->planExploreTraj(truncated_path, vel, acc, time_lb)) {\n"
        "      ROS_WARN(\"[RACER_TRAJ_GENERATION_FAILED] truncated trajectory rejected\");\n"
        "      return FAIL;\n"
        "    }\n",
        "truncated trajectory rejected",
    )
    return changed


def patch_reached_viewpoint_skip(source: Path) -> bool:
    changed = False
    changed |= replace_once(
        source,
        "  const int attempt_limit = 8;\n"
        "  int attempted = 0;\n"
        "  int skipped_backoff = 0;\n",
        "  const int attempt_limit = 8;\n"
        "  constexpr double reached_viewpoint_radius = 0.45;\n"
        "  int attempted = 0;\n"
        "  int skipped_backoff = 0;\n"
        "  int skipped_reached = 0;\n",
        "reached_viewpoint_radius = 0.45",
    )
    changed |= replace_once(
        source,
        "    const auto& candidate = candidates[rank];\n"
        "    if (isUnreachableViewpoint(candidate.first)) {\n",
        "    const auto& candidate = candidates[rank];\n"
        "    const double candidate_distance = (candidate.first - pos).norm();\n"
        "    if (candidate_distance <= reached_viewpoint_radius) {\n"
        "      ++skipped_reached;\n"
        "      ROS_WARN_THROTTLE(1.0,\n"
        "          \"[RACER_REACHED_VIEWPOINT_SKIP] drone=%d rank=%d distance=%.3f \"\n"
        "          \"radius=%.3f target=(%.3f,%.3f,%.3f)\",\n"
        "          ep_->drone_id_, rank, candidate_distance, reached_viewpoint_radius,\n"
        "          candidate.first.x(), candidate.first.y(), candidate.first.z());\n"
        "      continue;\n"
        "    }\n"
        "    if (isUnreachableViewpoint(candidate.first)) {\n",
        "[RACER_REACHED_VIEWPOINT_SKIP]",
    )
    changed |= replace_once(
        source,
        "    ROS_ERROR(\"No path to next viewpoint after bounded fallback: drone=%d attempted=%d \"\n"
        "              \"skipped_backoff=%d candidates=%zu limit=%d\",\n"
        "        ep_->drone_id_, attempted, skipped_backoff, candidates.size(), attempt_limit);\n",
        "    ROS_ERROR(\"No path to next viewpoint after bounded fallback: drone=%d attempted=%d \"\n"
        "              \"skipped_backoff=%d skipped_reached=%d candidates=%zu limit=%d\",\n"
        "        ep_->drone_id_, attempted, skipped_backoff, skipped_reached,\n"
        "        candidates.size(), attempt_limit);\n",
        "skipped_backoff=%d skipped_reached=%d candidates=%zu limit=%d",
    )
    changed |= replace_once(
        source,
        "  if (selected_rank > 0 || skipped_backoff > 0) {\n"
        "    ROS_WARN(\"[RACER_UNREACHABLE_SELECT] drone=%d rank=%d attempted=%d \"\n"
        "             \"skipped_backoff=%d target=(%.3f,%.3f,%.3f) candidates=%zu\",\n"
        "        ep_->drone_id_, selected_rank, attempted, skipped_backoff, next_pos.x(),\n"
        "        next_pos.y(), next_pos.z(), candidates.size());\n",
        "  if (selected_rank > 0 || skipped_backoff > 0 || skipped_reached > 0) {\n"
        "    ROS_WARN(\"[RACER_UNREACHABLE_SELECT] drone=%d rank=%d attempted=%d \"\n"
        "             \"skipped_backoff=%d skipped_reached=%d target=(%.3f,%.3f,%.3f) \"\n"
        "             \"candidates=%zu\",\n"
        "        ep_->drone_id_, selected_rank, attempted, skipped_backoff, skipped_reached,\n"
        "        next_pos.x(), next_pos.y(), next_pos.z(), candidates.size());\n",
        "selected_rank > 0 || skipped_backoff > 0 || skipped_reached > 0",
    )
    return changed


def apply(root: Path) -> bool:
    planner_h = root / "plan_manage/include/plan_manage/planner_manager.h"
    planner_cpp = root / "plan_manage/src/planner_manager.cpp"
    manager_cpp = root / "exploration_manager/src/fast_exploration_manager.cpp"
    for path in (planner_h, planner_cpp, manager_cpp):
        if not path.is_file():
            raise FileNotFoundError(f"RACER source missing: {path}")

    changed = make_plan_explore_traj_fallible(planner_h, planner_cpp)
    changed |= patch_manager_callers(manager_cpp)
    changed |= patch_reached_viewpoint_skip(manager_cpp)
    print(
        "RACER degenerate-tour recovery "
        f"{'applied' if changed else 'already present'}: {root}"
    )
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("racer_source_root", type=Path)
    args = parser.parse_args()
    apply(args.racer_source_root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
