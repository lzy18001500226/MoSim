#!/usr/bin/env python3
"""Make FUEL's runtime random generators configurable and repeatable."""

from __future__ import annotations

import argparse
from pathlib import Path


TOPO_MARKER = "FUEL_DETERMINISTIC_TOPOLOGY_SEED_V1"
MAP_MARKER = "FUEL_DETERMINISTIC_MAP_SEED_V1"


def replace_once(path: Path, old: str, new: str, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print(f"FUEL deterministic seed patch already applied: {path}")
        return
    if text.count(old) != 1:
        raise RuntimeError(f"{path}: expected exactly one seed initialization block")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"Applied FUEL deterministic seed patch: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    args = parser.parse_args()
    root = args.fuel_source_root.resolve()

    topo_path = root / "path_searching/src/topo_prm.cpp"
    replace_once(
        topo_path,
        """  graph_.clear();
  eng_ = default_random_engine(rd_());
  rand_pos_ = uniform_real_distribution<double>(-1.0, 1.0);
""",
        """  graph_.clear();
  int random_seed = -1;
  nh.param("topo_prm/random_seed", random_seed, -1);
  if (random_seed >= 0) {
    // FUEL_DETERMINISTIC_TOPOLOGY_SEED_V1: repeat stochastic roadmap samples.
    eng_.seed(static_cast<unsigned int>(random_seed));
    ROS_INFO("FUEL TopologyPRM fixed random seed: %d", random_seed);
  } else {
    eng_.seed(rd_());
    ROS_INFO("FUEL TopologyPRM random_device seed enabled");
  }
  rand_pos_ = uniform_real_distribution<double>(-1.0, 1.0);
""",
        TOPO_MARKER,
    )

    map_path = root / "plan_env/src/map_ros.cpp"
    replace_once(
        map_path,
        """  rand_noise_ = normal_distribution<double>(0, 0.1);
  random_device rd;
  eng_ = default_random_engine(rd());
""",
        """  rand_noise_ = normal_distribution<double>(0, 0.1);
  int random_seed = -1;
  node_.param("map_ros/random_seed", random_seed, -1);
  if (random_seed >= 0) {
    // FUEL_DETERMINISTIC_MAP_SEED_V1: repeat optional depth-noise samples.
    eng_.seed(static_cast<unsigned int>(random_seed));
    ROS_INFO("FUEL MapROS fixed random seed: %d", random_seed);
  } else {
    random_device rd;
    eng_.seed(rd());
    ROS_INFO("FUEL MapROS random_device seed enabled");
  }
""",
        MAP_MARKER,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
