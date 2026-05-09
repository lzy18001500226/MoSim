#!/usr/bin/env python3
"""Generate replay JSON from a standard raw trajectory CSV."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


REQUIRED_COLUMNS = ["time", "x", "y", "z"]


def read_rows(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        missing = [name for name in REQUIRED_COLUMNS if name not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns in {path}: {', '.join(missing)}")
        rows = []
        for row in reader:
            parsed: dict[str, float] = {}
            for name in reader.fieldnames:
                value = row.get(name, "")
                parsed[name] = float(value) if value != "" else math.nan
            rows.append(parsed)
        return rows


def finite(value: float, fallback: float = 0.0) -> float:
    return value if not math.isnan(value) and not math.isinf(value) else fallback


def make_replay(
    rows: list[dict[str, float]],
    *,
    scene_id: str,
    model_name: str,
    description: str,
    source: str,
    max_frames: int,
) -> dict[str, object]:
    stride = max(1, len(rows) // max_frames)
    frames = []
    has_reference = all(name in rows[0] for name in ["x_ref", "y_ref", "z_ref"]) if rows else False
    for row in rows[::stride]:
        uav = [
            {
                "id": "actual",
                "position": [finite(row["x"]), finite(row["y"]), finite(row["z"])],
                "yaw": finite(row.get("yaw", 0.0)),
            }
        ]
        if has_reference:
            uav.append(
                {
                    "id": "reference",
                    "position": [finite(row["x_ref"]), finite(row["y_ref"]), finite(row["z_ref"])],
                    "yaw": 0.0,
                }
            )
        frames.append({"time": finite(row["time"]), "uav": uav})
    return {
        "scene_id": scene_id,
        "model_name": model_name,
        "description": description,
        "source": source,
        "frame_count": len(frames),
        "frames": frames,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_csv", type=Path)
    parser.add_argument("output_json", type=Path)
    parser.add_argument("--scene-id", default=None)
    parser.add_argument("--model-name", default="")
    parser.add_argument("--description", default="")
    parser.add_argument("--max-frames", type=int, default=900)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = read_rows(args.raw_csv)
    scene_id = args.scene_id or args.raw_csv.stem
    payload = make_replay(
        rows,
        scene_id=scene_id,
        model_name=args.model_name,
        description=args.description,
        source=str(args.raw_csv),
        max_frames=args.max_frames,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output_json}")
    print(f"Frames: {payload['frame_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
