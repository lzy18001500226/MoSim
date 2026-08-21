#!/usr/bin/env python3
"""Generate high-speed single-UAV OpenBlocks trajectory for testing."""

from pathlib import Path
import sys
import importlib.util
import yaml
import csv
import json

ROOT = Path(__file__).resolve().parents[2]
PLANNER_PATH = ROOT / "Scripts/planning/plan_astar_min_snap.py"
CONFIG_PATH = ROOT / "Config/planners/astar_min_snap/map_open_blocks.yaml"
OUTPUT_DIR = ROOT / "Results/planning/single_uav_openblocks_highspeed"

def load_planner():
    spec = importlib.util.spec_from_file_location("plan_astar_min_snap", PLANNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load planner: {PLANNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def main():
    planner = load_planner()

    # Load and expand config
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding='utf-8'))
    config = planner.expand_wall_groups(config)
    config = planner.expand_random_obstacles(config)

    # Disable random obstacles
    if "random_obstacles" in config["map"]:
        config["map"]["random_obstacles"]["enabled"] = False

    # Single UAV route: (-41, -26, 1) → (41, 26, 1)
    config["map"]["start"] = [-41.0, -26.0, 1.0]
    config["map"]["goal"] = [41.0, 26.0, 1.0]
    config["map"]["planning_safety_margin"] = 0.55

    # High-speed limits
    config["limits"].update({
        "velocity_reference_m_s": 3.0,
        "velocity_max_m_s": 5.0,
        "acceleration_max_m_s2": 5.0,
        "jerk_max_m_s3": 15.0,
        "tilt_max_rad": 0.60,
    })

    # Disable local planning
    config["local_planning"]["enabled"] = False

    print("Planning single-UAV high-speed OpenBlocks trajectory...")
    print(f"  Start: {config['map']['start']}")
    print(f"  Goal: {config['map']['goal']}")
    print(f"  Velocity reference: {config['limits']['velocity_reference_m_s']} m/s")
    print(f"  Velocity max: {config['limits']['velocity_max_m_s']} m/s")

    # Plan
    raw_path, path, rows, report = planner.plan_trackable(config)

    if not report.get("accepted", False):
        print(f"\nERROR: Planning failed!")
        print(f"  Duration: {report.get('duration_s', 0):.2f}s")
        print(f"  Max velocity: {report.get('max_velocity_m_s', 0):.2f} m/s")
        print(f"  Violations: {report.get('dynamic_violation_count', 0)}")
        print(f"  Min clearance: {report.get('min_obstacle_distance_m', 0):.3f} m")
        return 1

    print(f"\nPlanning succeeded!")
    print(f"  Duration: {report['duration_s']:.2f}s")
    print(f"  Max velocity: {report['max_velocity_m_s']:.2f} m/s")
    print(f"  Max acceleration: {report['max_acceleration_m_s2']:.2f} m/s^2")
    print(f"  Sample count: {report['sample_count']}")
    print(f"  Min clearance: {report['min_obstacle_distance_m']:.3f} m")

    # Export CSV
    raw_dir = OUTPUT_DIR / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    csv_path = raw_dir / "uav1_reference.csv"

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCSV saved: {csv_path}")

    # Export MAT
    try:
        import numpy as np
        from scipy.io import savemat

        mat_dir = OUTPUT_DIR / "mat"
        mat_dir.mkdir(parents=True, exist_ok=True)

        time = np.array([row['time'] for row in rows])
        x_ref = np.array([row['x_ref'] for row in rows])
        y_ref = np.array([row['y_ref'] for row in rows])
        z_ref = np.array([row['z_ref'] for row in rows])
        yaw_ref = np.array([row['yaw_ref'] for row in rows])

        table = np.column_stack([time, x_ref, y_ref, z_ref, yaw_ref])
        mat_path = mat_dir / "uav1_reference.mat"
        savemat(mat_path, {"uav1_ref": table}, oned_as='column')

        print(f"MAT saved: {mat_path}")
        print(f"\nUpdate OpenBlocksDynamicReference.matFilePath to:")
        print(f'  "{mat_path.as_posix()}"')
    except ImportError:
        print("\nWARNING: scipy not available, skipping MAT export")
        print("Run: python Scripts/planning/export_planning_to_mat.py")

    # Export report
    report_path = OUTPUT_DIR / "planning_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "config": {
                "start": config["map"]["start"],
                "goal": config["map"]["goal"],
                "velocity_reference_m_s": config["limits"]["velocity_reference_m_s"],
                "velocity_max_m_s": config["limits"]["velocity_max_m_s"],
            },
            "report": report,
        }, f, indent=2)

    print(f"Report saved: {report_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
