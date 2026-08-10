#!/usr/bin/env python3
"""Write the C99 Diff-Planner target-frame contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Translate three C99 Diff-Planner targets into the active MAVROS frame."
    )
    parser.add_argument("--source-frame", choices=("world", "local"), required=True)
    parser.add_argument(
        "--mavros-frame",
        choices=("local", "common_world"),
        default="local",
        help="Coordinate frame currently exposed by each MAVROS odometry stream.",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--starts", type=float, nargs=6, required=True, metavar=("U1_X", "U1_Y", "U2_X", "U2_Y", "U3_X", "U3_Y"))
    parser.add_argument(
        "--targets",
        type=float,
        nargs=9,
        required=True,
        metavar=("U1_X", "U1_Y", "U1_Z", "U2_X", "U2_Y", "U2_Z", "U3_X", "U3_Y", "U3_Z"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    starts = {
        "1": list(args.starts[0:2]),
        "2": list(args.starts[2:4]),
        "3": list(args.starts[4:6]),
    }
    source_targets = {
        "1": list(args.targets[0:3]),
        "2": list(args.targets[3:6]),
        "3": list(args.targets[6:9]),
    }
    planner_targets = {
        uid: (
            target[:]
            if args.source_frame == "world"
            else [target[0] + starts[uid][0], target[1] + starts[uid][1], target[2]]
        )
        for uid, target in source_targets.items()
    }
    if args.mavros_frame == "common_world":
        mission_targets = {uid: target[:] for uid, target in planner_targets.items()}
        transform = {
            "type": "identity_common_world",
            "formula": "mission_target_xyz = planner_target_xyz = source_target_world_xyz",
            "zero_yaw_spawn_contract": True,
        }
        runtime_bridge = {
            "planner_odom": "identity_common_world",
            "planner_goal": "identity_common_world",
            "planner_position_cmd": "identity_common_world",
        }
    else:
        mission_targets = {
            uid: (
                [target[0] - starts[uid][0], target[1] - starts[uid][1], target[2]]
                if args.source_frame == "world"
                else target[:]
            )
            for uid, target in source_targets.items()
        }
        transform = {
            "type": "translation_only",
            "formula": (
                "mission_target_xy = source_target_xy - uav_spawn_xy; planner_target_xy = source_target_xy"
                if args.source_frame == "world"
                else "mission_target_xy = source_target_xy; planner_target_xy = source_target_xy + uav_spawn_xy"
            ),
            "zero_yaw_spawn_contract": True,
        }
        runtime_bridge = {
            "planner_odom": "mavros_local_to_common_world",
            "planner_goal": "mission_local_to_common_world",
            "planner_position_cmd": "common_world_to_mavros_local",
        }
    contract = {
        "schema": "mosim.sunray_ros1.c99_diff_target_coordinate_contract.v1",
        "status": "passed",
        "source_frame": args.source_frame,
        "mavros_frame": args.mavros_frame,
        "mission_frame": "mavros_local" if args.mavros_frame == "local" else "common_world",
        "planner_frame": "common_world",
        "transform": transform,
        "spawn_xy_world_m": starts,
        "source_targets": source_targets,
        "mission_targets": mission_targets,
        "planner_targets": planner_targets,
        "runtime_bridge": runtime_bridge,
        "claim_boundary": (
            "This contract aligns mission acceptance targets and Diff-Planner inputs with the declared "
            "MAVROS frame; FAST-LIO, MID360, point-cloud and grid-map parameters are unchanged."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(contract, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(" ".join(f"{value:.12g}" for uid in ("1", "2", "3") for value in mission_targets[uid]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
