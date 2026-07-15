#!/usr/bin/env python3
"""Add a bounded occupied-start escape to RACER's grid A* implementation."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(path: Path, old: str, new: str, marker: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return False
    if old not in text:
        raise RuntimeError(f"anchor not found in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


def apply(source_root: Path) -> bool:
    cpp = source_root / "path_searching/src/astar2.cpp"
    header = source_root / "path_searching/include/path_searching/astar2.h"
    if not cpp.is_file() or not header.is_file():
        raise FileNotFoundError(f"RACER astar2 source missing under {source_root}")

    changed = False
    changed |= replace_once(
        header,
        "  double max_search_time_;\n",
        "  double max_search_time_;\n  double start_clearance_radius_;\n",
        "start_clearance_radius_",
    )
    changed |= replace_once(
        cpp,
        '  nh.param("astar/max_search_time", max_search_time_, -1.0);\n',
        '  nh.param("astar/max_search_time", max_search_time_, -1.0);\n'
        '  nh.param("astar/start_clearance_radius", start_clearance_radius_, 0.0);\n',
        'nh.param("astar/start_clearance_radius"',
    )
    changed |= replace_once(
        cpp,
        "  const auto t1 = ros::Time::now();\n\n  /* ---------- search loop ---------- */\n",
        "  const auto t1 = ros::Time::now();\n"
        "  const bool start_clearance_active = start_clearance_radius_ > 0.0 &&\n"
        "      edt_env_->sdf_map_->getInflateOccupancy(start_pt) == 1;\n"
        "  const auto inside_start_clearance = [&](const Eigen::Vector3d& point) {\n"
        "    return start_clearance_active &&\n"
        "        (point - start_pt).norm() <= start_clearance_radius_ + 1e-6;\n"
        "  };\n"
        "  if (start_clearance_active) {\n"
        "    ROS_WARN_THROTTLE(1.0,\n"
        "        \"[RACER_ASTAR_START_CLEARANCE] radius=%.3f start=(%.3f,%.3f,%.3f)\",\n"
        "        start_clearance_radius_, start_pt.x(), start_pt.y(), start_pt.z());\n"
        "  }\n\n"
        "  /* ---------- search loop ---------- */\n",
        "[RACER_ASTAR_START_CLEARANCE]",
    )
    changed |= replace_once(
        cpp,
        "          if (edt_env_->sdf_map_->getInflateOccupancy(nbr_pos) == 1 ||\n"
        "              (!optimistic && edt_env_->sdf_map_->getOccupancy(nbr_pos) == SDFMap::UNKNOWN))\n"
        "            continue;\n",
        "          if ((!inside_start_clearance(nbr_pos) &&\n"
        "                  edt_env_->sdf_map_->getInflateOccupancy(nbr_pos) == 1) ||\n"
        "              (!optimistic && edt_env_->sdf_map_->getOccupancy(nbr_pos) == SDFMap::UNKNOWN))\n"
        "            continue;\n",
        "!inside_start_clearance(nbr_pos)",
    )
    changed |= replace_once(
        cpp,
        "            if (edt_env_->sdf_map_->getInflateOccupancy(ckpt) == 1 ||\n"
        "                (!optimistic && edt_env_->sdf_map_->getOccupancy(ckpt) == SDFMap::UNKNOWN)) {\n",
        "            if ((!inside_start_clearance(ckpt) &&\n"
        "                    edt_env_->sdf_map_->getInflateOccupancy(ckpt) == 1) ||\n"
        "                (!optimistic && edt_env_->sdf_map_->getOccupancy(ckpt) == SDFMap::UNKNOWN)) {\n",
        "!inside_start_clearance(ckpt)",
    )
    changed |= replace_once(
        cpp,
        "          if ((!inside_start_clearance(nbr_pos) &&\n"
        "                  edt_env_->sdf_map_->getInflateOccupancy(nbr_pos) == 1) ||\n"
        "              (!optimistic && edt_env_->sdf_map_->getOccupancy(nbr_pos) == SDFMap::UNKNOWN))\n"
        "            continue;\n",
        "          if ((!inside_start_clearance(nbr_pos) &&\n"
        "                  edt_env_->sdf_map_->getInflateOccupancy(nbr_pos) == 1) ||\n"
        "              (!inside_start_clearance(nbr_pos) && !optimistic &&\n"
        "                  edt_env_->sdf_map_->getOccupancy(nbr_pos) == SDFMap::UNKNOWN))\n"
        "            continue;\n",
        "!inside_start_clearance(nbr_pos) && !optimistic",
    )
    changed |= replace_once(
        cpp,
        "            if ((!inside_start_clearance(ckpt) &&\n"
        "                    edt_env_->sdf_map_->getInflateOccupancy(ckpt) == 1) ||\n"
        "                (!optimistic && edt_env_->sdf_map_->getOccupancy(ckpt) == SDFMap::UNKNOWN)) {\n",
        "            if ((!inside_start_clearance(ckpt) &&\n"
        "                    edt_env_->sdf_map_->getInflateOccupancy(ckpt) == 1) ||\n"
        "                (!inside_start_clearance(ckpt) && !optimistic &&\n"
        "                    edt_env_->sdf_map_->getOccupancy(ckpt) == SDFMap::UNKNOWN)) {\n",
        "!inside_start_clearance(ckpt) && !optimistic",
    )

    print(f"RACER A* start clearance {'applied' if changed else 'already present'}: {source_root}")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("racer_source_root", type=Path)
    args = parser.parse_args()
    apply(args.racer_source_root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
