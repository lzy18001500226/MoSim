#!/usr/bin/env python3
"""Add an opt-in rosout isolation switch to FUEL's exploration node."""

from pathlib import Path
import sys


OLD = '  ros::init(argc, argv, "exploration_node");\n'
NEW = '''  const char* disable_rosout_env = std::getenv("FUEL_DISABLE_ROSOUT");
  const bool disable_rosout = disable_rosout_env != nullptr &&
      (std::string(disable_rosout_env) == "1" ||
       std::string(disable_rosout_env) == "true");
  ros::init(argc, argv, "exploration_node",
      disable_rosout ? ros::init_options::NoRosout : 0);
'''


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch_fuel_optional_no_rosout.py <fuel_planner_root>")
    path = Path(sys.argv[1]) / "exploration_manager/src/exploration_node.cpp"
    text = path.read_text()
    if NEW in text:
        print("Optional FUEL NoRosout patch already applied")
        return 0
    if text.count(OLD) != 1:
        raise SystemExit(f"{path}: expected exactly one ros::init anchor")
    text = text.replace("#include <ros/ros.h>\n", "#include <ros/ros.h>\n#include <cstdlib>\n#include <string>\n", 1)
    path.write_text(text.replace(OLD, NEW, 1))
    print("Applied optional FUEL NoRosout diagnostic switch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
