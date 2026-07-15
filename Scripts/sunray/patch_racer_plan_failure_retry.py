#!/usr/bin/env python3
"""Bound RACER full-plan retries after a temporary planning failure."""

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
    data_h = root / "exploration_manager/include/exploration_manager/expl_data.h"
    fsm_h = root / "exploration_manager/include/exploration_manager/fast_exploration_fsm.h"
    fsm_cpp = root / "exploration_manager/src/fast_exploration_fsm.cpp"
    manager_cpp = root / "exploration_manager/src/fast_exploration_manager.cpp"
    for path in (data_h, fsm_h, fsm_cpp, manager_cpp):
        if not path.is_file():
            raise FileNotFoundError(f"RACER source missing: {path}")

    changed = False
    changed |= replace_once(
        data_h,
        "  double attempt_interval_;   // Min interval of opt attempt\n",
        "  double attempt_interval_;   // Min interval of opt attempt\n"
        "  double plan_fail_retry_interval_;  // Min interval after a full-plan failure\n",
        "plan_fail_retry_interval_",
    )
    changed |= replace_once(
        fsm_h,
        "  ros::Timer exec_timer_, safety_timer_, vis_timer_, frontier_timer_;\n",
        "  ros::Timer exec_timer_, safety_timer_, vis_timer_, frontier_timer_;\n"
        "  ros::Time last_plan_fail_time_;\n",
        "last_plan_fail_time_",
    )
    changed |= replace_once(
        fsm_cpp,
        '  nh.param("fsm/attempt_interval", fp_->attempt_interval_, 0.2);\n',
        '  nh.param("fsm/attempt_interval", fp_->attempt_interval_, 0.2);\n'
        '  nh.param("fsm/plan_fail_retry_interval", fp_->plan_fail_retry_interval_, 0.4);\n',
        'nh.param("fsm/plan_fail_retry_interval"',
    )
    changed |= replace_once(
        fsm_cpp,
        "    case PLAN_TRAJ: {\n"
        "      if (fd_->static_state_) {\n",
        "    case PLAN_TRAJ: {\n"
        "      const ros::Time plan_now = ros::Time::now();\n"
        "      if (!last_plan_fail_time_.isZero() &&\n"
        "          (plan_now - last_plan_fail_time_).toSec() < fp_->plan_fail_retry_interval_) {\n"
        "        break;\n"
        "      }\n"
        "      if (fd_->static_state_) {\n",
        "(plan_now - last_plan_fail_time_).toSec()",
    )
    changed |= replace_once(
        fsm_cpp,
        "      if (res == SUCCEED) {\n"
        "        transitState(PUB_TRAJ, \"FSM\");\n"
        "      } else if (res == FAIL) {  // Keep trying to replan\n"
        "        fd_->static_state_ = true;\n"
        "        ROS_WARN(\"Plan fail\");\n",
        "      if (res == SUCCEED) {\n"
        "        last_plan_fail_time_ = ros::Time(0);\n"
        "        transitState(PUB_TRAJ, \"FSM\");\n"
        "      } else if (res == FAIL) {  // Keep trying to replan\n"
        "        fd_->static_state_ = true;\n"
        "        last_plan_fail_time_ = plan_now;\n"
        "        ROS_WARN_THROTTLE(1.0, \"Plan fail\");\n",
        "last_plan_fail_time_ = plan_now",
    )
    changed |= replace_once(
        manager_cpp,
        '    ROS_ERROR("No path to next viewpoint after bounded fallback: drone=%d attempted=%d "\n',
        '    ROS_ERROR_THROTTLE(1.0,\n'
        '        "No path to next viewpoint after bounded fallback: drone=%d attempted=%d "\n',
        "ROS_ERROR_THROTTLE(1.0",
    )

    print(
        "RACER plan-failure retry throttle "
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
