#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean up unused and duplicate files in MoSimQuadrotorModel.Guidance directory.

Action plan:
1. Delete 3 duplicate files from Planning/
2. Move 15 unused Planning/ files to archive
3. Move 11 unused Trajectories/ files to archive
4. Update package.order files

Archive location: E:/刘致远18001500226/MoSim_Archive/Guidance_Cleanup_20260821/
"""
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Set UTF-8 output for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Repo root
REPO_ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
GUIDANCE_ROOT = REPO_ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance"
ARCHIVE_ROOT = Path(r"E:\刘致远18001500226\MoSim_Archive\Guidance_Cleanup_20260821")

# Files to DELETE (duplicates)
DELETE_FILES = {
    "Planning": [
        "ThreeUavPairwiseEcbfReferenceSafetyFilter.mo",
        "ThreeUavPairwiseEcbfReferenceSmoother.mo",
        "OpenBlocksMapTruthDisplay.mo",
    ]
}

# Files to ARCHIVE (unused)
ARCHIVE_FILES = {
    "Planning": [
        # Closed-loop test models
        "Sunray150PlanningCorridorGateAWFFSysblockClosedLoop.mo",
        "Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop.mo",
        "Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop.mo",
        "Sunray150PlanningOpenBlocksPx4CtrlSysblockClosedLoop.mo",
        "Sunray150PlanningOpenBlocksPx4CtrlSysblockDynamicClosedLoop.mo",
        "ThreeUavOpenBlocksReconfigurableFormationPx4Ctrl.mo",
        "ThreeUavOpenBlocksReconfigurableFormationPx4CtrlDynamic.mo",
        "ThreeUavOpenBlocksReconfigurableFormationPx4CtrlEcbfSafety.mo",
        # Component files
        "OpenBlocksLinearMPCVehicle.mo",
        "OpenBlocksPx4CtrlReference.mo",
        "OpenBlocksPx4CtrlVehicle.mo",
        "PlannedQuinticPx4CtrlReference.mo",
        "PlannedQuinticReference.mo",
        "PlanningNavigationDisplay.mo",
    ],
    "Trajectories": [
        "ClimbTrajectory.mo",
        "Figure8.mo",
        "HoverHold.mo",
        "MotorFault.mo",
        "ParameterMismatch.mo",
        "PartialTrajectory.mo",
        "PlannedQuinticPx4CtrlReference.mo",
        "PlannedQuinticReference.mo",
        "SpiralAscent.mo",
        "StepResponse.mo",
        "WindDisturbance.mo",
    ]
}


def update_package_order(subdir: str, removed_files: list[str]):
    """Update package.order file to remove archived/deleted entries."""
    package_order_path = GUIDANCE_ROOT / subdir / "package.order"
    if not package_order_path.exists():
        print(f"  [WARN] package.order not found: {package_order_path}")
        return

    with open(package_order_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Remove entries (strip .mo extension from filenames)
    removed_names = {f.replace('.mo', '') for f in removed_files}
    new_lines = [line for line in lines if line.strip() not in removed_names]

    if len(new_lines) < len(lines):
        with open(package_order_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"  [OK] Updated package.order: removed {len(lines) - len(new_lines)} entries")
    else:
        print(f"  [SKIP] package.order unchanged")


def main():
    print("=" * 80)
    print("Guidance Directory Cleanup")
    print("=" * 80)

    # Create archive root
    ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"\n[OK] Archive directory: {ARCHIVE_ROOT}")

    # Phase 1: Delete duplicate files
    print("\n" + "-" * 80)
    print("PHASE 1: Delete duplicate files")
    print("-" * 80)
    deleted_count = 0
    for subdir, files in DELETE_FILES.items():
        subdir_path = GUIDANCE_ROOT / subdir
        print(f"\n[{subdir}/]")
        for filename in files:
            file_path = subdir_path / filename
            if file_path.exists():
                file_path.unlink()
                deleted_count += 1
                print(f"  [DELETE] {filename}")
            else:
                print(f"  [WARN] Not found: {filename}")

        # Update package.order
        update_package_order(subdir, files)

    print(f"\n[OK] Deleted {deleted_count} duplicate files")

    # Phase 2: Archive unused files
    print("\n" + "-" * 80)
    print("PHASE 2: Archive unused files")
    print("-" * 80)
    archived_count = 0
    for subdir, files in ARCHIVE_FILES.items():
        subdir_path = GUIDANCE_ROOT / subdir
        archive_subdir = ARCHIVE_ROOT / subdir
        archive_subdir.mkdir(parents=True, exist_ok=True)

        print(f"\n[{subdir}/]")
        for filename in files:
            src = subdir_path / filename
            dst = archive_subdir / filename
            if src.exists():
                shutil.move(str(src), str(dst))
                archived_count += 1
                print(f"  [ARCHIVE] {filename}")
            else:
                print(f"  [WARN] Not found: {filename}")

        # Update package.order
        update_package_order(subdir, files)

    print(f"\n[OK] Archived {archived_count} unused files")

    # Summary
    print("\n" + "=" * 80)
    print("CLEANUP SUMMARY")
    print("=" * 80)
    print(f"Deleted:  {deleted_count} duplicate files")
    print(f"Archived: {archived_count} unused files")
    print(f"Total:    {deleted_count + archived_count} files cleaned")
    print(f"\nArchive location: {ARCHIVE_ROOT}")
    print("\n[OK] Cleanup complete")


if __name__ == "__main__":
    main()
