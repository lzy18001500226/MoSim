#!/usr/bin/env python3
"""Keep FUEL command continuity when an in-flight replan attempt fails."""

from __future__ import annotations

import argparse
from pathlib import Path


OLD = '''      } else if (res == FAIL) {
        // Still in PLAN_TRAJ state, keep replanning
        ROS_WARN("plan fail");
        fd_->static_state_ = true;
      }
'''

NEW = '''      } else if (res == FAIL) {
        // Keep sampling the active command trajectory on an in-flight retry. Switching to
        // odometry here creates a discontinuity while traj_server still executes the old spline.
        ROS_WARN("plan fail; retrying from active trajectory state");
        if (planner_manager_->local_data_.traj_id_ <= 0) fd_->static_state_ = true;
      }
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    root = parser.parse_args().fuel_source_root.resolve()
    path = root / "exploration_manager/src/fast_exploration_fsm.cpp"
    text = path.read_text(encoding="utf-8")
    if NEW in text:
        print("FUEL failed-replan continuity patch already applied")
        return 0
    count = text.count(OLD)
    if count != 1:
        raise SystemExit(f"{path}: expected one failed-replan block, found {count}")
    path.write_text(text.replace(OLD, NEW), encoding="utf-8")
    print("Applied FUEL failed-replan continuity patch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
