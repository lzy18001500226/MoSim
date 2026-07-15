#!/usr/bin/env python3
"""Use one timestamp for FUEL's predicted handoff state and spline start."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str, path: Path) -> str:
    if new in text:
        return text
    if text.count(old) != 1:
        raise SystemExit(f"{path}: expected one patch anchor, found {text.count(old)}")
    return text.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    root = parser.parse_args().fuel_source_root.resolve()
    header = root / "exploration_manager/include/exploration_manager/fast_exploration_fsm.h"
    source = root / "exploration_manager/src/fast_exploration_fsm.cpp"

    h = header.read_text(encoding="utf-8")
    h = replace_once(
        h,
        "  bool classic_;\n",
        "  bool classic_;\n  ros::Time replan_start_time_;\n",
        header,
    )
    header.write_text(h, encoding="utf-8")

    s = source.read_text(encoding="utf-8")
    s = replace_once(
        s,
        "    case PLAN_TRAJ: {\n      if (fd_->static_state_) {\n",
        "    case PLAN_TRAJ: {\n"
        "      replan_start_time_ = ros::Time::now() + ros::Duration(fp_->replan_time_);\n"
        "      if (fd_->static_state_) {\n",
        source,
    )
    s = replace_once(
        s,
        "        double t_r = (ros::Time::now() - info->start_time_).toSec() + fp_->replan_time_;\n",
        "        double t_r = (replan_start_time_ - info->start_time_).toSec();\n",
        source,
    )
    s = replace_once(
        s,
        "int FastExplorationFSM::callExplorationPlanner() {\n  ros::Time time_r = ros::Time::now() + ros::Duration(fp_->replan_time_);\n",
        "int FastExplorationFSM::callExplorationPlanner() {\n"
        "  const ros::Time time_r = replan_start_time_;\n",
        source,
    )
    s = replace_once(
        s,
        "  int res = expl_manager_->planExploreMotion(fd_->start_pt_, fd_->start_vel_, fd_->start_acc_,\n"
        "                                             fd_->start_yaw_);\n"
        "  classic_ = false;\n",
        "  const LocalTrajData active_traj = planner_manager_->local_data_;\n"
        "  int res = expl_manager_->planExploreMotion(fd_->start_pt_, fd_->start_vel_, fd_->start_acc_,\n"
        "                                             fd_->start_yaw_);\n"
        "  classic_ = false;\n"
        "  if (res == SUCCEED && ros::Time::now() > time_r) {\n"
        "    const double overrun = (ros::Time::now() - time_r).toSec();\n"
        "    ROS_ERROR(\"[FUEL_REPLAN_TIME] Planning overran handoff by %.6f s; retaining active trajectory\",\n"
        "        overrun);\n"
        "    planner_manager_->local_data_ = active_traj;\n"
        "    return FAIL;\n"
        "  }\n",
        source,
    )
    source.write_text(s, encoding="utf-8")
    print("Applied single-timestamp FUEL replan start contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
