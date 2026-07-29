from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ANALYZER = ROOT / "Scripts/sunray/analyze_swarm_formation_obstacle_clearance.py"


def write_truth(path: Path, points: list[tuple[float, float]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("t", "phase", "x", "y", "z"))
        writer.writeheader()
        for index, (x, y) in enumerate(points):
            writer.writerow({"t": index * 0.02, "phase": "ego_execute", "x": x, "y": y, "z": 1.2})


def write_fixture(run_dir: Path, direct: bool) -> tuple[Path, Path]:
    run_dir.mkdir()
    cargo = {"source_actor": "Cargo", "min_m": [1.5, -0.5, 0.7], "max_m": [2.5, 0.5, 1.7]}
    scene_truth = run_dir / "scene_truth.json"
    scene_truth.write_text(json.dumps({"collision_proxies": [cargo]}), encoding="utf-8")
    path_one = [(0.0, 0.0), (2.0, 0.0), (4.0, 0.0)] if direct else [(0.0, 0.0), (0.0, 1.0), (4.0, 1.0), (4.0, 0.0)]
    write_truth(run_dir / "uav1_truth.csv", path_one)
    write_truth(run_dir / "uav2_truth.csv", [(0.0, 2.0), (2.0, 2.0), (4.0, 2.0)])
    write_truth(run_dir / "uav3_truth.csv", [(0.0, -2.0), (2.0, -2.0), (4.0, -2.0)])
    scenario = {
        "source_truth": str(scene_truth),
        "formation": {
            "start_positions_xy_m": {"1": [0.0, 0.0], "2": [0.0, 2.0], "3": [0.0, -2.0]},
            "target_positions_xy_m": {"1": [4.0, 0.0], "2": [4.0, 2.0], "3": [4.0, -2.0]},
        },
        "obstacle_crossing_contract": {
            "direct_center_segment_blocked": True,
            "clearance_margin_m": 0.2,
            "member_intersecting_proxies": {"1": ["Cargo"], "2": [], "3": []},
        },
    }
    scenario_path = run_dir / "scenario.json"
    scenario_path.write_text(json.dumps(scenario), encoding="utf-8")
    return scenario_path, scene_truth


def run_analyzer(run_dir: Path, scenario_path: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
    completed = subprocess.run(
        [sys.executable, str(ANALYZER), "--run", str(run_dir), "--scenario", str(scenario_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    packet = json.loads((run_dir / "SWARM_FORMATION_OBSTACLE_CLEARANCE_GATE.json").read_text(encoding="utf-8"))
    return completed, packet


def test_obstacle_clearance_gate_accepts_a_real_detour(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    scenario, _ = write_fixture(run_dir, direct=False)
    completed, packet = run_analyzer(run_dir, scenario)

    assert completed.returncode == 0
    assert packet["status"] == "passed"
    assert packet["per_uav"]["1"]["detour_excess_m"] > 0.25
    assert packet["per_uav"]["1"]["expected_proxy_minimum_axis_linf_clearance_m"]["Cargo"] > 0.2
    assert packet["per_uav"]["1"]["expected_proxy_minimum_euclidean_clearance_m"]["Cargo"] > 0.2
    assert packet["per_uav"]["1"]["clearance_violation_count"] == 0


def test_obstacle_clearance_gate_rejects_a_direct_collision(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    scenario, _ = write_fixture(run_dir, direct=True)
    completed, packet = run_analyzer(run_dir, scenario)

    assert completed.returncode == 1
    assert packet["status"] == "blocked"
    assert "uav1_obstacle_clearance_violation" in packet["blockers"]
    assert "uav1_detour_not_observed" in packet["blockers"]


def test_obstacle_clearance_gate_uses_axis_linf_for_inflated_aabb_corners(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    scenario, _ = write_fixture(run_dir, direct=False)
    write_truth(
        run_dir / "uav1_truth.csv",
        [(0.0, 0.0), (1.35, -0.65), (2.65, -0.65), (4.0, 0.0)],
    )

    completed, packet = run_analyzer(run_dir, scenario)

    assert completed.returncode == 1
    assert packet["status"] == "blocked"
    violations = packet["per_uav"]["1"]["clearance_violations"]
    assert any(
        entry["axis_linf_clearance_m"] < 0.2
        and entry["euclidean_clearance_m"] > 0.2
        for entry in violations
    )
