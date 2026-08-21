#!/usr/bin/env python3
"""
Load all MoSimQuadrotorModel packages into Sysplorer
Workaround: Sysplorer doesn't recursively load sub-packages
"""
from pathlib import Path
import sys
sys.path.insert(0, r'D:\Program Files\MWORKS\Sysplorer 2026a\Bin')
import mworks.sysplorer as ModelingPy

BASE = Path('C:/Users/HP/Desktop/MoSim/Models/MoSimQuadrotorModel')

# Critical packages in load order
LOAD_ORDER = [
    # Top level
    BASE / 'package.mo',

    # Core infrastructure
    BASE / 'BaseModules/package.mo',
    BASE / 'Blocks/package.mo',
    BASE / 'Sources/package.mo',
    BASE / 'Vehicle/package.mo',
    BASE / 'Guidance/package.mo',
    BASE / 'Trajectories/package.mo',
    BASE / 'Telemetry/package.mo',

    # Control top-level
    BASE / 'Control/package.mo',
    BASE / 'Control/PidFamily/package.mo',
    BASE / 'Control/ClassicRobust/package.mo',
    BASE / 'Control/SlidingMode/package.mo',
    BASE / 'Control/Optimization/package.mo',
    BASE / 'Control/GeometricFlatness/package.mo',
    BASE / 'Control/Learning/package.mo',
    BASE / 'Control/IntegratedChains/package.mo',

    # Experiment top-level
    BASE / 'Experiment/package.mo',
    BASE / 'Experiment/PidFamily/package.mo',
]

print(f"Loading {len(LOAD_ORDER)} package files...")

success = 0
failed = []

for pkg_file in LOAD_ORDER:
    rel = pkg_file.relative_to(BASE.parent)
    try:
        result = ModelingPy.OpenModelFile(str(pkg_file))
        if result:
            success += 1
            print(f"[OK]   {rel}")
        else:
            errors = ModelingPy.GetLastErrors()
            failed.append((rel, errors))
            print(f"[FAIL] {rel}: {errors}")
    except Exception as e:
        failed.append((rel, str(e)))
        print(f"[ERR]  {rel}: {e}")

print(f"\n{'='*80}")
print(f"Success: {success}/{len(LOAD_ORDER)}")
if failed:
    print(f"\nFailed packages:")
    for rel, err in failed:
        print(f"  {rel}: {err}")
print(f"{'='*80}")

# Test if CascadePidGraphicalRunner is now visible
cascade_exists = ModelingPy.ClassExist('MoSimQuadrotorModel.Experiment.SingleUav.PidFamily.CascadePidGraphicalRunner')
print(f"\nCascadePidGraphicalRunner exists: {cascade_exists}")
