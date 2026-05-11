#!/usr/bin/env python3
"""Check generated official reference trajectory files."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


EXPECTED = {
    "official_example1": {
        "path": Path("results/official/example1_step/raw/reference_official_example1.csv"),
        "rows": 5001,
        "last_time": 50.0,
        "last_ref": (10.0, 10.0, 15.0),
    },
    "official_example2": {
        "path": Path("results/official/example2_helix/raw/reference_official_example2.csv"),
        "rows": 5001,
        "last_time": 50.0,
        "last_ref": (1.0, 0.0, 20.0 / 3.0),
    },
    "official_example3": {
        "path": Path("results/official/example3_figure8/raw/reference_official_example3.csv"),
        "rows": 12001,
        "last_time": 120.0,
        "last_ref": (
            10.0 * math.sin((0.02 * 110.0 + 1.0 / 360.0) * math.pi),
            10.0 * math.sin(0.04 * 110.0 * math.pi),
            10.0,
        ),
    },
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"time", "x_ref", "y_ref", "z_ref", "yaw_ref"}
        missing = sorted(required.difference(reader.fieldnames or []))
        if missing:
            raise ValueError(f"{path} missing columns: {', '.join(missing)}")
        return list(reader)


def assert_close(name: str, actual: float, expected: float, tolerance: float = 1e-9) -> None:
    if not math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance):
        raise AssertionError(f"{name}: expected {expected}, got {actual}")


def check_scene(scene_id: str, spec: dict[str, object]) -> None:
    path = spec["path"]
    assert isinstance(path, Path)
    rows = read_rows(path)
    expected_rows = int(spec["rows"])
    if len(rows) != expected_rows:
        raise AssertionError(f"{path}: expected {expected_rows} rows, got {len(rows)}")

    last = rows[-1]
    assert_close(f"{scene_id}.last_time", float(last["time"]), float(spec["last_time"]))
    expected_ref = spec["last_ref"]
    assert isinstance(expected_ref, tuple)
    for field, expected in zip(("x_ref", "y_ref", "z_ref"), expected_ref):
        assert_close(f"{scene_id}.{field}", float(last[field]), float(expected))
    assert_close(f"{scene_id}.yaw_ref", float(last["yaw_ref"]), 0.0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", choices=["all", *sorted(EXPECTED)], default="all")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scenes = sorted(EXPECTED) if args.scene == "all" else [args.scene]
    for scene_id in scenes:
        check_scene(scene_id, EXPECTED[scene_id])
        print(f"[OK] {scene_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
