#!/usr/bin/env python3
"""Regression checks for UE navigation/control handoff artifacts."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[2]
SCENES = ("factoryenvironmentcollect", "derelictcorridormegascans")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_navigation_control_handoff_outputs() -> None:
    scene_pipeline = load_module(
        "scene_truth_pipeline",
        ROOT / "Scripts" / "UE5" / "scene_truth_pipeline.py",
    )
    fastlio = load_module(
        "prepare_fastlio_replay",
        ROOT / "Scripts" / "UE5" / "prepare_fastlio_replay.py",
    )
    navigation = load_module(
        "build_navigation_handoff",
        ROOT / "Scripts" / "UE5" / "build_navigation_handoff.py",
    )

    temp_root = ROOT / "Results" / "tmp" / "navigation_handoff_test"
    if temp_root.exists():
        shutil.rmtree(temp_root)
    output_root = temp_root / "scene_mapping"
    try:
        for scene_id in SCENES:
            truth_path = scene_pipeline.scene_truth_path(scene_id)
            truth = scene_pipeline.load_truth(truth_path)
            profile = scene_pipeline.default_profile(str(truth["scene_id"]), truth_path)
            scene_pipeline.run_scene(profile, output_root)
            fastlio.prepare_scene(output_root / scene_id)

        handoffs = [navigation.build_scene_handoff(output_root / scene_id) for scene_id in SCENES]
        navigation.write_summary(output_root, handoffs)

        status = (output_root / "NAVIGATION_HANDOFF_STATUS.md").read_text(encoding="utf-8")
        if "ready_for_mworks_controller_interface_smoke" not in status:
            raise AssertionError(status)
        if "global_truth_available_to_planner=false" not in status:
            raise AssertionError(status)

        for handoff in handoffs:
            scene_id = handoff["scene_id"]
            scene_dir = output_root / scene_id
            if handoff["truth_policy"]["global_truth_available_to_planner"]:
                raise AssertionError(handoff)
            if not handoff["truth_policy"]["collision_free_against_truth"]:
                raise AssertionError(handoff)
            if not handoff["truth_policy"]["buffered_collision_free_against_truth"]:
                raise AssertionError(handoff)
            if handoff["truth_policy"]["control_tracking_buffer_cells"] < 1:
                raise AssertionError(handoff)

            package = json.loads((scene_dir / "control_interface_package.json").read_text(encoding="utf-8"))
            if package["status"] != "ready_for_mworks_reference_model_integration":
                raise AssertionError(package)
            if "not a Sysplorer/MWORKS dynamics simulation result" not in " ".join(package["claim_boundary"]):
                raise AssertionError(package)

            params = json.loads((scene_dir / "planned_quintic_reference_params.json").read_text(encoding="utf-8"))
            if params["n_segments"] != len(handoff["waypoints"]) - 1:
                raise AssertionError(params)
            if len(params["p_x"]) != 91 or len(params["segment_duration"]) != 90:
                raise AssertionError(params)
            if params["n_segments"] > 90:
                raise AssertionError(params)

            with (scene_dir / "control_reference.csv").open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            if len(rows) < len(handoff["waypoints"]):
                raise AssertionError((scene_id, len(rows), len(handoff["waypoints"])))
            if {"time", "x_ref", "y_ref", "z_ref", "yaw_ref"} - set(rows[0]):
                raise AssertionError(rows[0])

            scenario = (scene_dir / "scenario_draft.yaml").read_text(encoding="utf-8")
            if "active: false" not in scenario:
                raise AssertionError(scenario)
            if "offline_ue_navigation_control_interface_package" not in scenario:
                raise AssertionError(scenario)
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root)


def main() -> int:
    test_navigation_control_handoff_outputs()
    print("[OK] UE navigation/control handoff regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
