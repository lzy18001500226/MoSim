#!/usr/bin/env python3
"""Install stable, review-oriented FUEL visualization layers.

The upstream FSM used to publish visualization from a detached thread while
replanning mutated the same containers. The current MoSim runtime calls
``visualize`` synchronously; this patch additionally deep-copies the planner
products before publishing and exposes the global/local tour semantics that
upstream FUEL already computes.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "FUEL_VISUALIZATION_SNAPSHOT_V1"

VISUALIZE = r'''void FastExplorationFSM::visualize() {
  // FUEL_VISUALIZATION_SNAPSHOT_V1: publish only deep-copied planner products.
  auto position_traj = planner_manager_->local_data_.position_traj_;
  const auto frontiers = expl_manager_->ed_->frontiers_;
  const auto global_points = expl_manager_->ed_->points_;
  const auto global_tour = expl_manager_->ed_->global_tour_;
  const auto refined_points = expl_manager_->ed_->refined_points_;
  const auto refined_tour = expl_manager_->ed_->refined_tour_;
  const auto path_next_goal = expl_manager_->ed_->path_next_goal_;
  const auto next_goal = expl_manager_->ed_->next_goal_;

  visualization_->drawFrontier(frontiers);

  visualization_->drawSpheres(
      global_points, 0.22, Vector4d(1.0, 0.75, 0.05, 0.95), "global_viewpoints", 0, 6);
  visualization_->drawLines(
      global_tour, 0.06, Vector4d(1.0, 0.55, 0.05, 0.95), "global_tour", 0, 6);

  visualization_->drawSpheres(
      refined_points, 0.24, Vector4d(0.15, 0.95, 0.35, 1.0), "local_viewpoints", 0, 6);
  visualization_->drawLines(
      refined_tour, 0.09, Vector4d(0.10, 1.0, 0.35, 1.0), "local_tour", 0, 6);
  visualization_->drawLines(
      path_next_goal, 0.05, Vector4d(0.20, 0.85, 1.0, 0.90), "next_goal_path", 0, 6);
  if (next_goal.allFinite()) {
    visualization_->drawSpheres(
        {next_goal}, 0.30, Vector4d(0.15, 0.95, 1.0, 1.0), "next_goal", 0, 6);
  }

  vector<Vector3d> trajectory_points;
  const double duration = position_traj.getTimeSum();
  if (std::isfinite(duration) && duration > 0.0) {
    const int sample_count = std::max(2, static_cast<int>(std::ceil(duration / 0.04)));
    trajectory_points.reserve(sample_count + 1);
    for (int i = 0; i <= sample_count; ++i) {
      trajectory_points.push_back(position_traj.evaluateDeBoorT(duration * i / sample_count));
    }
  }
  visualization_->drawLines(
      trajectory_points, 0.08, Vector4d(0.05, 0.90, 1.0, 1.0), "current_bspline", 0, 0);

  ROS_INFO("[FUEL_VIS_SNAPSHOT] frontiers=%zu global_points=%zu global_tour=%zu "
           "local_points=%zu local_tour=%zu bspline_samples=%zu",
      frontiers.size(), global_points.size(), global_tour.size(), refined_points.size(),
      refined_tour.size(), trajectory_points.size());
}
'''

CLEAR = r'''void FastExplorationFSM::clearVisMarker() {
  visualization_->drawFrontier({});
  visualization_->drawSpheres(
      {}, 0.22, Vector4d(0, 0, 0, 0), "global_viewpoints", 0, 6);
  visualization_->drawLines(
      {}, 0.06, Vector4d(0, 0, 0, 0), "global_tour", 0, 6);
  visualization_->drawSpheres(
      {}, 0.24, Vector4d(0, 0, 0, 0), "local_viewpoints", 0, 6);
  visualization_->drawLines(
      {}, 0.09, Vector4d(0, 0, 0, 0), "local_tour", 0, 6);
  visualization_->drawLines(
      {}, 0.05, Vector4d(0, 0, 0, 0), "next_goal_path", 0, 6);
  visualization_->drawSpheres(
      {}, 0.30, Vector4d(0, 0, 0, 0), "next_goal", 0, 6);
  visualization_->drawLines(
      {}, 0.08, Vector4d(0, 0, 0, 0), "current_bspline", 0, 0);
}
'''


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    begin = text.find(start)
    finish = text.find(end, begin + len(start))
    if begin < 0 or finish < 0:
        raise RuntimeError(f"cannot locate function range: {start!r} -> {end!r}")
    return text[:begin] + replacement + "\n" + text[finish:]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_root", type=Path)
    args = parser.parse_args()

    source = args.source_root / "exploration_manager/src/fast_exploration_fsm.cpp"
    text = source.read_text(encoding="utf-8")
    if MARKER in text:
        print(f"FUEL visualization patch already applied: {source}")
        return

    text = replace_between(
        text,
        "void FastExplorationFSM::visualize() {",
        "void FastExplorationFSM::clearVisMarker() {",
        VISUALIZE,
    )
    text = replace_between(
        text,
        "void FastExplorationFSM::clearVisMarker() {",
        "void FastExplorationFSM::frontierCallback(",
        CLEAR,
    )
    source.write_text(text, encoding="utf-8")
    print(f"Applied stable FUEL visualization layers: {source}")


if __name__ == "__main__":
    main()
