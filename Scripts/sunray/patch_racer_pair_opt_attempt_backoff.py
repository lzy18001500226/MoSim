#!/usr/bin/env python3
"""Apply RACER's attempt interval to failed pair-optimization attempts too."""

from __future__ import annotations

import argparse
from pathlib import Path


def apply(root: Path) -> bool:
    fsm_cpp = root / "exploration_manager/src/fast_exploration_fsm.cpp"
    if not fsm_cpp.is_file():
        raise FileNotFoundError(f"RACER source missing: {fsm_cpp}")

    text = fsm_cpp.read_text(encoding="utf-8")
    marker = "MoSim: throttle every pair-opt attempt, including rejected allocations."
    if marker in text:
        print(f"RACER pair-opt attempt backoff already present: {root}")
        return False

    anchor = (
        '  ROS_WARN("Pair opt %d & %d", getId(), select_id);\n'
        "\n"
        "  // Do pairwise optimization with selected drone, allocate the union of their domiance grids\n"
    )
    replacement = (
        '  ROS_WARN("Pair opt %d & %d", getId(), select_id);\n'
        "\n"
        "  // MoSim: throttle every pair-opt attempt, including rejected allocations.\n"
        "  state1.recent_attempt_time_ = tn;\n"
        "\n"
        "  // Do pairwise optimization with selected drone, allocate the union of their domiance grids\n"
    )
    if anchor not in text:
        raise RuntimeError(f"{fsm_cpp}: expected pair-opt anchor not found")

    text = text.replace(anchor, replacement, 1)
    trailing_assignment = (
        "  ed->pair_opt_stamp_ = opt.stamp;\n"
        "  ed->wait_response_ = true;\n"
        "  state1.recent_attempt_time_ = tn;\n"
    )
    if trailing_assignment not in text:
        raise RuntimeError(f"{fsm_cpp}: expected successful-attempt assignment not found")
    text = text.replace(
        trailing_assignment,
        "  ed->pair_opt_stamp_ = opt.stamp;\n  ed->wait_response_ = true;\n",
        1,
    )
    fsm_cpp.write_text(text, encoding="utf-8")
    print(f"RACER pair-opt attempt backoff applied: {root}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("racer_source_root", type=Path)
    args = parser.parse_args()
    apply(args.racer_source_root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
