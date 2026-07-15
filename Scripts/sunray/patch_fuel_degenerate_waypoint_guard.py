#!/usr/bin/env python3
from pathlib import Path
import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    root = parser.parse_args().fuel_source_root.resolve()
    path = root / "plan_manage/src/planner_manager.cpp"
    text = path.read_text(encoding="utf-8")
    old = '  if (tour.empty()) { ROS_ERROR("Empty path to traj planner"); return false; }\n'
    new = (
        '  if (tour.size() < 2) {\n'
        '    ROS_ERROR("[FUEL_TRAJ_INPUT] Need at least two waypoints, got %zu", tour.size());\n'
        '    return false;\n'
        '  }\n'
    )
    if text.count(new) == 1:
        print("Degenerate-waypoint guard already applied")
        return 0
    if text.count(old) != 1:
        raise SystemExit(f"expected one original guard, found {text.count(old)}")
    path.write_text(text.replace(old, new), encoding="utf-8")
    print("Applied degenerate-waypoint guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
