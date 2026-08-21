#!/usr/bin/env python3
"""Launch OpenBlocks simulation with fresh A* planning before each run.

This launcher automates the workflow:
1. Run A* planning to generate fresh CSV trajectories
2. Update reference models with the new trajectories
3. Return path to the updated model ready for Sysplorer simulation

Usage:
    python Scripts/planning/launch_open_blocks_with_planning.py --controller px4ctrl
    python Scripts/planning/launch_open_blocks_with_planning.py --controller linear_mpc
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CONTROLLERS = {
    "px4ctrl": {
        "planning_script": ROOT / "Scripts/planning/plan_open_blocks_three_uav.py",
        "update_script": ROOT / "Scripts/planning/update_px4ctrl_references.py",
        "single_uav_model": "Models/MoSimQuadrotorModel/Guidance/Planning/Sunray150PlanningOpenBlocksPx4CtrlSysblockClosedLoop.mo",
        "three_uav_model": "Models/MoSimQuadrotorModel/Experiment/OpenBlocks/Px4Ctrl/Formation/ThreeUavPx4CtrlOpenBlocksRunner.mo",
    },
    "linear_mpc": {
        "planning_script": ROOT / "Scripts/planning/plan_open_blocks_three_uav.py",
        "update_script": ROOT / "Scripts/planning/update_planning_open_blocks_model.py",
        "single_uav_model": None,
        "three_uav_model": "Models/MoSimQuadrotorModel/Guidance/Planning/ThreeUavOpenBlocksReconfigurableFormationLinearMPC.mo",
    },
}


def run_planning(controller_name: str) -> int:
    """Run A* planning script to generate fresh CSV trajectories."""
    config = CONTROLLERS[controller_name]
    planning_script = config["planning_script"]

    print(f"\n=== Step 1: Running A* planning ===")
    print(f"Script: {planning_script.relative_to(ROOT)}")

    result = subprocess.run(
        [sys.executable, str(planning_script)],
        cwd=ROOT,
        capture_output=False,
    )

    if result.returncode != 0:
        print(f"ERROR: Planning failed with exit code {result.returncode}")
        return result.returncode

    print("Planning completed successfully")
    return 0


def update_models(controller_name: str) -> int:
    """Update Modelica reference models with fresh CSV data."""
    config = CONTROLLERS[controller_name]
    update_script = config["update_script"]

    print(f"\n=== Step 2: Updating reference models ===")
    print(f"Script: {update_script.relative_to(ROOT)}")

    result = subprocess.run(
        [sys.executable, str(update_script)],
        cwd=ROOT,
        capture_output=False,
    )

    if result.returncode != 0:
        print(f"ERROR: Model update failed with exit code {result.returncode}")
        return result.returncode

    print("Reference models updated successfully")
    return 0


def show_ready_models(controller_name: str):
    """Display the models ready for simulation."""
    config = CONTROLLERS[controller_name]

    print(f"\n=== Step 3: Models ready for simulation ===")
    print(f"Controller: {controller_name.upper()}")

    if config["single_uav_model"]:
        print(f"Single UAV: {config['single_uav_model']}")

    if config["three_uav_model"]:
        print(f"Three UAV: {config['three_uav_model']}")

    print("\nNext steps:")
    print("  1. Open the model in Sysplorer")
    print("  2. Load dependencies (if needed)")
    print("  3. Run CheckModel")
    print("  4. Click SimulateModel to start")
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--controller",
        choices=list(CONTROLLERS.keys()),
        default="px4ctrl",
        help="Controller type to use (default: px4ctrl)"
    )
    parser.add_argument(
        "--planning-only",
        action="store_true",
        help="Only run planning, skip model update"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print(f"OpenBlocks Simulation Launcher")
    print(f"Controller: {args.controller}")
    print(f"Working directory: {ROOT}")

    # Step 1: Run planning
    ret = run_planning(args.controller)
    if ret != 0:
        return ret

    # Step 2: Update models (unless planning-only)
    if not args.planning_only:
        ret = update_models(args.controller)
        if ret != 0:
            return ret

        # Step 3: Show ready models
        show_ready_models(args.controller)
    else:
        print("\nPlanning-only mode: skipping model update")

    return 0


if __name__ == "__main__":
    sys.exit(main())
