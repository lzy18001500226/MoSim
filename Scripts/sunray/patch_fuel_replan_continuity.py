#!/usr/bin/env python3
from pathlib import Path
import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    parser.add_argument("--revert", action="store_true")
    args = parser.parse_args()
    path = (
        args.fuel_source_root.resolve()
        / "exploration_manager/src/fast_exploration_manager.cpp"
    )
    text = path.read_text(encoding="utf-8")
    old = (
        "  ed_->path_next_goal_ = planner_manager_->path_finder_->getPath();\n"
        "  shortenPath(ed_->path_next_goal_);\n"
    )
    new = old + (
        "  if (ed_->path_next_goal_.empty()) {\n"
        "    ROS_ERROR(\"[FUEL_REPLAN_CONTINUITY] A* returned an empty path after shortening\");\n"
        "    return FAIL;\n"
        "  }\n"
        "  const double start_gap = (ed_->path_next_goal_.front() - pos).norm();\n"
        "  if (start_gap > 1e-4) {\n"
        "    ROS_WARN(\"[FUEL_REPLAN_CONTINUITY] Prepending predicted start; A* gap=%.6f m\", start_gap);\n"
        "    ed_->path_next_goal_.insert(ed_->path_next_goal_.begin(), pos);\n"
        "  }\n"
    )
    source, target = (new, old) if args.revert else (old, new)
    if text.count(target) == 1 and text.count(source) == 0:
        print("Requested FUEL replan continuity state already present")
        return 0
    if text.count(source) != 1:
        raise SystemExit(f"expected one source block, found {text.count(source)}")
    path.write_text(text.replace(source, target), encoding="utf-8")
    print("Reverted" if args.revert else "Applied", "FUEL replan continuity patch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
