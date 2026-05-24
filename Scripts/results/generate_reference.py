#!/usr/bin/env python3
"""Generate reference trajectories matching the official QuadrotorModel examples."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


EXAMPLES = {
    "official_example1": {
        "model_name": "QuadrotorModel.Examples.Example1",
        "description": "阶梯爬升运动",
        "stop_time": 50.0,
        "dt": 0.01,
    },
    "official_example2": {
        "model_name": "QuadrotorModel.Examples.Example2",
        "description": "螺旋爬升运动",
        "stop_time": 50.0,
        "dt": 0.01,
    },
    "official_example3": {
        "model_name": "QuadrotorModel.Examples.Example3",
        "description": "8字形运动",
        "stop_time": 120.0,
        "dt": 0.01,
    },
}


def ramp(time: float, *, start: float, duration: float, height: float, offset: float = 0.0) -> float:
    if time <= start:
        return offset
    if time >= start + duration:
        return offset + height
    return offset + height * (time - start) / duration


def official_reference(scene_id: str, time: float) -> tuple[float, float, float]:
    if scene_id == "official_example1":
        x = ramp(time, start=20.0, duration=10.0, height=10.0)
        y = ramp(time, start=30.0, duration=10.0, height=10.0)
        z = ramp(time, start=0.0, duration=5.0, height=10.0) + ramp(time, start=10.0, duration=3.0, height=5.0)
        return x, y, z

    if scene_id == "official_example2":
        # Example2 overrides CirclePath defaults with ramp(height=20),
        # sine(f=0.05), and cosine(f=0.05, startTime=10, phase=0).
        z = ramp(time, start=0.0, duration=150.0, height=20.0)
        if time < 10.0:
            x = 0.0
            y = 0.0
        else:
            x = math.cos(2.0 * math.pi * 0.05 * (time - 10.0))
            y = math.sin(2.0 * math.pi * 0.05 * (time - 0.0))
        return x, y, z

    if scene_id == "official_example3":
        # EightPath uses delayed x/y expressions by 10 s and a 10 s altitude ramp.
        delayed_time = max(0.0, time - 10.0)
        x = 10.0 * math.sin((0.02 * delayed_time + 1.0 / 360.0) * math.pi) if time >= 10.0 else 0.0
        y = 10.0 * math.sin(0.04 * delayed_time * math.pi) if time >= 10.0 else 0.0
        z = ramp(time, start=0.0, duration=10.0, height=10.0)
        return x, y, z

    raise ValueError(f"Unknown scene_id: {scene_id}")


def generate_rows(scene_id: str, stop_time: float, dt: float) -> list[dict[str, float]]:
    steps = int(round(stop_time / dt))
    rows = []
    for index in range(steps + 1):
        time = round(index * dt, 10)
        x, y, z = official_reference(scene_id, time)
        rows.append(
            {
                "time": time,
                "x_ref": x,
                "y_ref": y,
                "z_ref": z,
                "yaw_ref": 0.0,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["time", "x_ref", "y_ref", "z_ref", "yaw_ref"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_replay(path: Path, scene_id: str, rows: list[dict[str, float]]) -> None:
    meta = EXAMPLES[scene_id]
    sample_stride = max(1, len(rows) // 600)
    frames = [
        {
            "time": row["time"],
            "uav": [{"id": "reference", "position": [row["x_ref"], row["y_ref"], row["z_ref"]], "yaw": row["yaw_ref"]}],
        }
        for row in rows[::sample_stride]
    ]
    payload = {
        "scene_id": scene_id,
        "model_name": meta["model_name"],
        "description": meta["description"],
        "source": "QuadrotorModel.PathPlanning reference equations",
        "frame_count": len(frames),
        "frames": frames,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", choices=["all", *sorted(EXAMPLES)], default="all")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--replay-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scenes = sorted(EXAMPLES) if args.scene == "all" else [args.scene]
    for scene_id in scenes:
        meta = EXAMPLES[scene_id]
        rows = generate_rows(scene_id, meta["stop_time"], meta["dt"])
        default_base = {
            "official_example1": Path("Results/official/example1_step/reference_official_example1"),
            "official_example2": Path("Results/official/example2_helix/reference_official_example2"),
            "official_example3": Path("Results/official/example3_figure8/reference_official_example3"),
        }[scene_id]
        csv_dir = args.output_dir or default_base / "raw"
        replay_dir = args.replay_dir or default_base / "replay"
        csv_path = csv_dir / f"reference_{scene_id}.csv"
        replay_path = replay_dir / f"reference_{scene_id}.json"
        write_csv(csv_path, rows)
        write_replay(replay_path, scene_id, rows)
        print(f"Wrote {csv_path} and {replay_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
