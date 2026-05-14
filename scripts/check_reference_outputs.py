#!/usr/bin/env python3
"""Check generated official reference trajectory files."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


EXPECTED = {
    "official_example1": {
        "path": Path("results/official/example1_step/reference_official_example1/raw/reference_official_example1.csv"),
        "rows": 5001,
        "last_time": 50.0,
        "last_ref": (10.0, 10.0, 15.0),
    },
    "official_example2": {
        "path": Path("results/official/example2_helix/reference_official_example2/raw/reference_official_example2.csv"),
        "rows": 5001,
        "last_time": 50.0,
        "last_ref": (1.0, 0.0, 20.0 / 3.0),
    },
    "official_example3": {
        "path": Path("results/official/example3_figure8/reference_official_example3/raw/reference_official_example3.csv"),
        "rows": 12001,
        "last_time": 120.0,
        "last_ref": (
            10.0 * math.sin((0.02 * 110.0 + 1.0 / 360.0) * math.pi),
            10.0 * math.sin(0.04 * 110.0 * math.pi),
            10.0,
        ),
    },
}

PLANNING_EXPECTED = {
    "single_obstacle_astar_awff": {
        "path": Path("results/planning/single_obstacle_astar_awff/raw/reference.csv"),
        "trackability": Path("results/planning/single_obstacle_astar_awff/metrics/trackability_report.json"),
        "min_rows": 20,
        "start_ref": (0.0, 0.0, 1.0),
        "last_ref": (6.0, 0.0, 1.0),
        "required_columns": {
            "time",
            "x_ref",
            "y_ref",
            "z_ref",
            "vx_ref",
            "vy_ref",
            "vz_ref",
            "ax_ref",
            "ay_ref",
            "az_ref",
            "jx_ref",
            "jy_ref",
            "jz_ref",
            "yaw_ref",
        },
    },
    "corridor_gate_astar_awff": {
        "path": Path("results/planning/corridor_gate_astar_awff/raw/reference.csv"),
        "trackability": Path("results/planning/corridor_gate_astar_awff/metrics/trackability_report.json"),
        "min_rows": 20,
        "start_ref": (0.0, 0.0, 1.0),
        "last_ref": (7.0, 0.0, 1.0),
        "required_columns": {
            "time",
            "x_ref",
            "y_ref",
            "z_ref",
            "vx_ref",
            "vy_ref",
            "vz_ref",
            "ax_ref",
            "ay_ref",
            "az_ref",
            "jx_ref",
            "jy_ref",
            "jz_ref",
            "yaw_ref",
        },
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


def check_planning_scene(scene_id: str, spec: dict[str, object]) -> None:
    path = spec["path"]
    assert isinstance(path, Path)
    rows = read_rows(path)
    required_columns = spec["required_columns"]
    assert isinstance(required_columns, set)
    missing = sorted(required_columns.difference(rows[0].keys() if rows else set()))
    if missing:
        raise AssertionError(f"{path} missing columns: {', '.join(missing)}")
    min_rows = int(spec["min_rows"])
    if len(rows) < min_rows:
        raise AssertionError(f"{path}: expected at least {min_rows} rows, got {len(rows)}")

    start_ref = spec["start_ref"]
    last_ref = spec["last_ref"]
    assert isinstance(start_ref, tuple)
    assert isinstance(last_ref, tuple)
    first = rows[0]
    last = rows[-1]
    for field, expected in zip(("x_ref", "y_ref", "z_ref"), start_ref):
        assert_close(f"{scene_id}.start.{field}", float(first[field]), float(expected), tolerance=1e-7)
    for field, expected in zip(("x_ref", "y_ref", "z_ref"), last_ref):
        assert_close(f"{scene_id}.last.{field}", float(last[field]), float(expected), tolerance=1e-7)

    trackability_path = spec["trackability"]
    assert isinstance(trackability_path, Path)
    import json

    trackability = json.loads(trackability_path.read_text(encoding="utf-8"))
    if trackability.get("accepted") is not True:
        raise AssertionError(f"{scene_id} trackability not accepted: {trackability}")
    if int(trackability.get("dynamic_violation_count", -1)) != 0:
        raise AssertionError(f"{scene_id} has dynamic violations: {trackability}")
    if float(trackability.get("min_obstacle_distance_m", 0.0)) < float(trackability.get("safety_margin_m", 0.0)):
        raise AssertionError(f"{scene_id} violates obstacle safety margin: {trackability}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", choices=["all", *sorted(EXPECTED), *sorted(PLANNING_EXPECTED)], default="all")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scenes = [*sorted(EXPECTED), *sorted(PLANNING_EXPECTED)] if args.scene == "all" else [args.scene]
    for scene_id in scenes:
        if scene_id in EXPECTED:
            check_scene(scene_id, EXPECTED[scene_id])
        else:
            check_planning_scene(scene_id, PLANNING_EXPECTED[scene_id])
        print(f"[OK] {scene_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
