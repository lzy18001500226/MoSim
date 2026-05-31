#!/usr/bin/env python3
"""Regression checks for MWORKS-vs-UE scene truth collision reporting."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "UE5" / "check_mworks_scene_truth_collision.py"
    spec = importlib.util.spec_from_file_location("check_mworks_scene_truth_collision", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_mworks_scene_truth_collision"] = module
    spec.loader.exec_module(module)
    return module


def write_fixture_scene(root: Path) -> Path:
    scene_dir = root / "fixture_scene"
    (scene_dir / "mworks_smoke" / "raw").mkdir(parents=True, exist_ok=True)
    (scene_dir / "mworks_smoke" / "metrics").mkdir(parents=True, exist_ok=True)
    (scene_dir / "occupancy_grid.json").write_text(
        json.dumps(
            {
                "schema": "mosim.ue_scene_occupancy.v1",
                "scene_id": "fixture_scene",
                "grid": {
                    "origin_xy_m": [0.0, 0.0],
                    "resolution_m": 1.0,
                    "size": [4, 4],
                    "occupied_cells_xy": [[2, 1]],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    raw_path = scene_dir / "mworks_smoke" / "raw" / "sunray150_ue_fixture_scene_linear_mpc_smoke.csv"
    with raw_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["time", "x", "y", "z", "x_ref", "y_ref", "z_ref"], lineterminator="\n")
        writer.writeheader()
        writer.writerow({"time": "0.0", "x": "1.0", "y": "1.0", "z": "1.0", "x_ref": "1.0", "y_ref": "1.0", "z_ref": "1.0"})
        writer.writerow({"time": "0.1", "x": "2.0", "y": "1.0", "z": "1.0", "x_ref": "1.0", "y_ref": "2.0", "z_ref": "1.0"})
    (scene_dir / "mworks_smoke" / "metrics" / "sunray150_ue_fixture_scene_linear_mpc_smoke.json").write_text(
        json.dumps({"source": "MWORKS_MCP", "evidence_level": "fixture"}, indent=2) + "\n",
        encoding="utf-8",
    )
    return scene_dir


def test_collision_report_flags_actual_trajectory_violation() -> None:
    module = load_module()
    temp_root = ROOT / "Results" / "tmp" / "mworks_scene_truth_collision_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    try:
        scene_dir = write_fixture_scene(temp_root)
        report = module.check_scene(scene_dir)
        if report["pass"]:
            raise AssertionError(report)
        if report["actual"]["occupied_sample_count"] != 1:
            raise AssertionError(report)
        if report["reference"]["occupied_sample_count"] != 0:
            raise AssertionError(report)
        output = scene_dir / "mworks_smoke" / "collision" / "mworks_scene_truth_collision.json"
        if not output.exists():
            raise AssertionError(output)
        module.write_status(temp_root, [report])
        status = (temp_root / "MWORKS_UE_SCENE_COLLISION_STATUS.md").read_text(encoding="utf-8")
        if "`fixture_scene`" not in status or "`false`" not in status:
            raise AssertionError(status)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    test_collision_report_flags_actual_trajectory_violation()
    print("[OK] MWORKS scene-truth collision regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
